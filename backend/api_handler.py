from flask import Flask, jsonify, request, make_response
from flask_cors import CORS, cross_origin
import mysql.connector
from mysql.connector import pooling
import random
import string
import jwt
import json
import datetime
import requests
from dotenv import load_dotenv
import os
import re
from time import time
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging

load_dotenv()

app = Flask(__name__)
CORS(app)
limiter = Limiter(key_func=get_remote_address)
limiter.init_app(app)

# Configure MySQL connection
db_config = {
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'host': os.environ.get('DB_HOST'),
    'database': os.environ.get('DB_NAME')
}

connection_pool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, **db_config)

otp_storage = {}
otp_attempts = {}
otp_resend_attempts = {}
otp_blocked = {}
otp_resend_blocked = {}
otp_expiry = {}
MAX_OTP_ATTEMPTS = 5
BLOCK_TIME = 7200 # 2 hours = 7200 seconds
OTP_VALIDITY_PERIOD = 10 * 60  # 10 minutes
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')

#SMS API data

sms_url="https://api.sms4free.co.il/ApiSMS/v2/SendSMS"
sms_api_key=os.environ.get('SMS_API_KEY')
sms_root_phone=os.environ.get('SMS_ROOT_PHONE')
sms_root_password=os.environ.get('SMS_ROOT_PASSWORD')
sms_sender=os.environ.get('SMS_SENDER')

# Set a connection to the database.
def get_db_connection():
    try:
        conn = connection_pool.get_connection()
        return conn
    except mysql.connector.Error as err:
        app.logger.error("Error: Could not connect to MySQL database.")
        app.logger.error(err)
        return None

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def send_otp(phone_number, otp):
    try:
        data={}
        data["key"]=sms_api_key
        data["user"]=sms_root_phone
        data["sender"]=sms_sender
        data["pass"]=sms_root_password
        data["recipient"]= phone_number
        data["msg"]="Hi, your one-time code is: " + otp
        response=requests.post(sms_url, json=data)
        print(response.text)

        return response.text
    except Exception as e:
        print(e)
        return None 
    
def validate_token(token):
    if not token:
        return None, {'Error': 'Forbidden'}, 403

    try:
        decoded_token = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None, {'Error': 'Token has expired'}, 111
    except jwt.InvalidTokenError:
        return None, {'Error': 'Invalid token'}, 403

    return decoded_token, None, None

def get_client_data(client_id):
    if not re.match(r'^\d+$', client_id):
        return None
    
    conn = get_db_connection()
    if conn is None:
        return None
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Client WHERE client_id = %s", (client_id,))
    client_data = cursor.fetchone()
    cursor.close()
    conn.close()
    return client_data

def fetch_client_representative(rep_id):
    if not re.match(r'^\d+$', rep_id):
        
        return None, "Invalid representative ID format"

    conn = get_db_connection()
    if conn is None:
        return None, "Could not connect to the database"

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ClientRepresentative WHERE rep_id = %s", (rep_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result, None

def fetch_appointments_by_month_and_year(month, year):
    conn = get_db_connection()
    if conn is None:
        return None, "Could not connect to the database"

    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM Appointment WHERE MONTH(apt_date) = %s AND YEAR(apt_date) = %s", (month, year))
    result = cur.fetchall()
    cur.close()
    conn.close()

    return result, None

def check_client_blocked(client_id):
    current_time = time()

    # Check if the client is blocked and if the block period has expired
    if client_id in otp_resend_blocked:
        if current_time < otp_resend_blocked[client_id]:
            return True
        else:
            # Unblock the client after the block period has expired
            del otp_resend_blocked[client_id]
            otp_resend_attempts[client_id] = 0
    
    return False
    
@app.route('/requestClientAuth', methods=['POST'])
@limiter.limit("5 per minute")
def request_client_auth():
    data = request.get_json()
    client_id = data.get('client_id')

    if not re.match(r'^\d+$', client_id):
       return jsonify({"error": "Invalid client ID format"}), 400

    current_time = time()

    # Check if the client is blocked from resending OTPs.
    if check_client_blocked(client_id):
      return jsonify({"error": "Maximum OTP attempts exceeded. Please try again later."}), 403

    try:
        client_data = get_client_data(client_id)
        if not client_data:
            return jsonify({"error": "Client not found"}), 404
        
        rep_data, error = fetch_client_representative(client_data['client_rep']) 
        if error:
            return jsonify({"error": error}), 500
        
        rep_phone = rep_data['rep_phone']

        if client_id in otp_storage:
            otp_resend_attempts[client_id] += 1

            if current_time < otp_expiry.get(client_id, 0):
                otp = otp_storage[client_id]
            else:
                otp = generate_otp()
                otp_storage[client_id] = otp
                otp_expiry[client_id] = current_time + OTP_VALIDITY_PERIOD
                otp_attempts[client_id] = 0
        else:
            otp = generate_otp()
            otp_storage[client_id] = otp
            otp_resend_attempts[client_id] = 1
            otp_attempts[client_id] = 0
            otp_expiry[client_id] = current_time + OTP_VALIDITY_PERIOD

        # Check if attempts exceed the maximum allowed
        if otp_resend_attempts[client_id] > MAX_OTP_ATTEMPTS:
            otp_resend_blocked[client_id] = current_time + BLOCK_TIME
            return jsonify({"error": "Maximum OTP attempts exceeded. Please try again later."}), 403

        response = send_otp(rep_phone, otp)
        
        return jsonify({"message": "OTP sent successfully " + response}), 200
    except Exception as e:
        return jsonify({"error": "Internal server error: " + e}), 500

@app.route('/clientAuth', methods=['POST'])
@limiter.limit("5 per minute")
def client_auth():
    data = request.get_json()
    client_id = data.get('client_id')
    otp = data.get('otp')

    if not re.match(r'^\d+$', client_id):
        return jsonify({"error": "Invalid client ID format"}), 400
    
    if client_id not in otp_storage or client_id not in otp_attempts:
        return jsonify({"error": "OTP not requested or expired"}), 400
    
    if client_id in otp_blocked and time() < otp_blocked[client_id]:
        return jsonify({"error": "Maximum OTP attempts exceeded. Please try again later."}), 403

    if time() > otp_expiry.get(client_id, 0):
        otp_storage.pop(client_id, None)
        otp_attempts.pop(client_id, None)
        otp_expiry.pop(client_id, None)
        return jsonify({"error": "OTP expired. Please request a new OTP."}), 400

    if otp_storage[client_id] == otp:

        otp_storage.pop(client_id, None)
        otp_attempts.pop(client_id, None)
        otp_resend_attempts.pop(client_id, None)
        otp_expiry.pop(client_id, None)
        otp_blocked.pop(client_id, None)
        otp_resend_blocked.pop(client_id, None)
        client_data = get_client_data(client_id)

        token = jwt.encode({
            'client_id': client_id,
            'rep_id': client_data['client_rep'],
            'role': 'client',
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, JWT_SECRET_KEY, algorithm='HS256')
        
        return jsonify({"token": token}), 200
    else:
        otp_attempts[client_id] += 1
        if otp_attempts[client_id] >= MAX_OTP_ATTEMPTS:
            otp_blocked[client_id] = time() + BLOCK_TIME
            otp_storage.pop(client_id, None)
            otp_attempts.pop(client_id, None)
            otp_expiry.pop(client_id, None)
            return jsonify({"error": "Maximum OTP attempts exceeded. Please try again later."}), 403
        
        return jsonify({"error": f"Invalid OTP. {MAX_OTP_ATTEMPTS - otp_attempts[client_id]} attempts left"}), 401

@app.route('/clientRepresentative', methods=['GET'])
def get_client_representative():
    rep_id = request.args.get('id', '')

    if not re.match(r'^\d+$', rep_id):
        return jsonify({'error': 'Invalid representative ID format'}), 400

    if rep_id:
        result, error = fetch_client_representative(rep_id)
        if error:
            return jsonify({"error": "Internal server error"}), 500
        if result:
            return jsonify(result)
        else:
            return jsonify({'error': 'No client representative found with the given ID'}), 404
    else:
        return jsonify({'error': 'Client representative ID is required'}), 400
    
@app.route('/repName', methods=['GET'])
def get_rep_name():
    token = request.args.get('token', '')

    decoded_token, error_response, status_code = validate_token(token)
    if error_response:
        return jsonify(error_response), status_code
    
    rep_id = decoded_token.get('rep_id')

    conn = get_db_connection()
    if conn is None:
        return jsonify({'Error':'Could not connect to the database.'}), 500

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT rep_firstname, rep_lastname FROM ClientRepresentative WHERE rep_id = %s", (rep_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    return jsonify(result)


@app.route('/lastAppointment', methods=['GET'])
def get_last_appointment():
    token = request.args.get('token', '')

    decoded_token, error_response, status_code = validate_token(token)
    if error_response:
        return jsonify(error_response), status_code
    
    client_id = decoded_token.get('client_id')

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM Appointment WHERE apt_client = %s AND apt_date < CURDATE() AND apt_status = 'closed' ORDER BY apt_date DESC LIMIT 1", (client_id,))
    appointment = cur.fetchone()
    cur.close()
    conn.close()

    if appointment:
        return jsonify(appointment), 200 
    else: 
        return jsonify({"error": "No appointment found for the specified client"}), 404

@app.route('/nextAppointment', methods=['GET'])
def get_next_appointment():
    token = request.args.get('token', '')

    decoded_token, error_response, status_code = validate_token(token)
    if error_response:
        return jsonify(error_response), status_code
    
    client_id = decoded_token.get('client_id')

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT Appointment.*, Employee.emp_firstname, Employee.emp_lastname, Client.client_city, Client.client_street, Client.client_street_number FROM Appointment LEFT JOIN Employee ON Appointment.apt_emp_executive = Employee.emp_ID JOIN Client ON Appointment.apt_client = Client.client_id WHERE apt_client = %s AND apt_date >= CURDATE() ORDER BY apt_date LIMIT 1", (client_id,))
    appointment = cur.fetchone()
    cur.close()
    conn.close()

    if appointment:
        return jsonify(appointment), 200 
    else: 
        return jsonify({"error": "No upcoming appointment found for the specified client"}), 404

# GET /allAppointmentsInMonthAndYear
@app.route('/allAppointmentsInMonthAndYear', methods=['GET'])
def get_appointments_in_month():
    month = request.args.get('month')
    year = request.args.get('year')

    if not month or not year:
        return jsonify({"error": "Month and year are required query parameters."}), 400

    try:
        month = int(month)
        year = int(year)
        if month < 1 or month > 12:
            raise ValueError
    except ValueError:
        return jsonify({"error": "Month must be an integer between 1 and 12 and year must be a valid integer"}), 400

    appointments, error = fetch_appointments_by_month_and_year(month, year)

    if error:
        return jsonify({"error": error}), 500

    if not appointments:
        return jsonify({"error": "No appointments found for the provided month and year."}), 404

    return jsonify(appointments), 200

@app.route('/appointmentsCount', methods=['GET'])
def get_appointments_count_by_month_and_year():
    month = request.args.get('month')
    year = request.args.get('year')

    if not month or not year:
        return jsonify({"error": "Month and year are required query parameters."}), 400

    try:
        month = int(month)
        year = int(year)
        if month < 1 or month > 12:
            raise ValueError
    except ValueError:
        return jsonify({"error": "Month must be an integer between 1 and 12 and year must be a valid integer"}), 400

    appointments, error = fetch_appointments_by_month_and_year(month, year)

    if error:
        return jsonify({"error": error}), 500

    appointments_count_by_date = {}
    for appointment in appointments:
        date = appointment['apt_date'].strftime('%Y-%m-%d')
        if date in appointments_count_by_date:
            appointments_count_by_date[date] += 1
        else:
            appointments_count_by_date[date] = 1

    return jsonify(appointments_count_by_date)

# PUT /changeAppointment
@app.route('/changeAppointment', methods=['PUT'])
def change_appointment():
    data = request.get_json()
    token = data.get('token')
    apt_date = data.get('apt_date')
    new_apt_date = data.get('new_apt_date')

    decoded_token, error_response, status_code = validate_token(token)
    if error_response:
        return jsonify(error_response), status_code
    
    apt_client = decoded_token.get('client_id')

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE Appointment SET apt_date = %s WHERE apt_date = %s AND apt_client = %s",
            (new_apt_date, apt_date, apt_client)
        )
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        app.logger.error("Error: Could not execute UPDATE statement.")
        app.logger.error(err)
        cur.close()
        conn.close()
        return jsonify({"error": "Database error occurred"}), 500

    cur.close()
    conn.close()
    return jsonify({'message': 'Appointment updated successfully'}), 200


# PUT /changeClientAppointment
@app.route('/changeClientAppointment', methods=['PUT'])
def change_client_appointment():
    data = request.get_json()
    apt_client = data.get('apt_client')
    apt_date = data.get('apt_date')
    new_apt_date = data.get('new_apt_date')

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE Appointment SET apt_date = %s WHERE apt_date = %s AND apt_client = %s",
            (new_apt_date, apt_date, apt_client)
        )
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        app.logger.error("Error: Could not execute UPDATE statement.")
        app.logger.error(err)
        cur.close()
        conn.close()
        return jsonify({"error": "Database error occurred"}), 500

    cur.close()
    conn.close()
    return jsonify({'message': 'Appointment updated successfully'}), 200

# POST /makeAppointment
@app.route('/makeAppointment', methods=['POST'])
def make_appointment():
    data = request.get_json()
    token = data.get('token')
    apt_date = data.get('apt_date')

    decoded_token, error_response, status_code = validate_token(token)
    if error_response:
        return jsonify(error_response), status_code
    
    apt_client = decoded_token.get('client_id')

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO Appointment (apt_date, apt_client, apt_emp_executive, apt_status) VALUES (%s, %s, %s, %s)",
            (apt_date, apt_client, None, 'open')
        )
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        app.logger.error("Error: Could not execute INSERT statement.")
        app.logger.error(err)
        cur.close()
        conn.close()
        return jsonify({"error": "Database error occurred"}), 500

    cur.close()
    conn.close()
    return jsonify({'message': 'Appointment added successfully'}), 200

# GET /appointmentsInDate
@app.route('/appointmentsInDate', methods=['GET'])
def get_appointments_in_date():
    """Fetch all appointments for a specific date."""
    date = request.args.get('date')  # Get the date from the query parameters
    if not date:
        return jsonify({"error": "Date parameter is required"}), 400

    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Database connection failed")
        
        cur = conn.cursor(dictionary=True)
        cur.execute("""SELECT a.apt_date, 
                        a.apt_client, 
                        a.apt_emp_executive, 
                        e.emp_firstname, 
                        e.emp_lastname, 
                        c.client_name, 
                        c.client_city, 
                        c.client_street, 
                        c.client_street_number
                    FROM Appointment a 
                    LEFT JOIN Employee e ON a.apt_emp_executive = e.emp_ID 
                    LEFT JOIN Client c ON a.apt_client = c.client_id  
                    WHERE a.apt_date = %s AND a.apt_status = 'open'""", (date,))
        results = cur.fetchall()

        return jsonify(results), 200 
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# GET /unassignedAppointmentsInDate
@app.route('/unassignedAppointmentsInDate', methods=['GET'])
def get_unassigned_appointments_in_date():
    """Fetch all appointments for a specific date."""
    date = request.args.get('date')  # Get the date from the query parameters
    if not date:
        return jsonify({"error": "Date parameter is required"}), 400

    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Database connection failed")
        
        cur = conn.cursor(dictionary=True)
        cur.execute("""SELECT a.apt_date, 
                        a.apt_client,  
                        c.client_name, 
                        c.client_city, 
                        c.client_street, 
                        c.client_street_number, 
                        cr.rep_phone 
                    FROM Appointment a 
                    LEFT JOIN Client c ON a.apt_client = c.client_id 
                    LEFT JOIN ClientRepresentative cr ON c.client_rep = cr.rep_id 
                    WHERE a.apt_date = %s AND a.apt_status = 'open' AND a.apt_emp_executive is NULL""", (date,))
        results = cur.fetchall()

        return jsonify(results), 200 
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# GET /allEmployees
@app.route('/allEmployees', methods=['GET'])
def get_all_employees():
    """Fetch all employees from the Employee table."""
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT emp_ID, emp_firstname, emp_lastname, emp_role, emp_phone, emp_user 
        FROM Employee
    """)
    results = cur.fetchall()
    cur.close()
    conn.close()
    if results:
        return jsonify(results) 
    else:
        return jsonify({"error": "No employees found"}), 404

# PUT /assignExecutiveEmployee
@app.route('/assignExecutiveEmployee', methods=['PUT'])
def assign_executive_employee():
    """Assign executive employees to appointments."""
    try:
        data = request.get_json()
        appointments = data.get('appointments')  # Get the JSON data from the request body

        if not isinstance(appointments, list):
            response = make_response(jsonify({"error": "Invalid data format, expected a list of objects"}), 400)
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response

        conn = get_db_connection()
        if conn is None:
            response = make_response(jsonify({"error": "Database connection failed"}), 500)
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response

        cur = conn.cursor()
        for appointment in appointments:
            apt_date = appointment.get('apt_date')  # Get the date from the JSON object
            apt_client = appointment.get('apt_client')  # Get the client_id from the JSON object
            apt_emp_executive = appointment.get('apt_emp_executive')  # Get the executive ID from the JSON object

            if not apt_date or not apt_client:
                conn.rollback()
                cur.close()
                conn.close()
                response = make_response(jsonify({"error": "Missing required parameters in one of the objects"}), 400)
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response

            cur.execute("""
                UPDATE Appointment 
                SET apt_emp_executive = %s 
                WHERE apt_date = %s AND apt_client = %s
            """, (apt_emp_executive, apt_date, apt_client))
            
            if cur.rowcount == 0:
                conn.rollback()
                cur.close()
                conn.close()
                response = make_response(jsonify({"error": f"No matching appointment found for date: {apt_date}, client_id: {apt_client}"}), 404)
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response

        conn.commit()
        cur.close()
        conn.close()
        response = make_response(jsonify({"message": "Executive employees assigned successfully"}), 200)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
    except Exception as e:
        app.logger.error(f"Error: {e}")
        response = make_response(jsonify({"error": str(e)}), 500)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Use 'adhoc' for testing; in production, use a proper SSL certificate