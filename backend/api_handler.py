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

connection_pool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=10, **db_config)

otp_storage = {}
otp_attempts = {}
otp_resend_attempts = {}
otp_blocked = {}
otp_resend_blocked = {}
otp_expiry = {}
employee_login_attempts = {}
employee_login_blocked = {}
MAX_OTP_ATTEMPTS = 5
MAX_LOGIN_ATTEMPTS = 5
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
        data["recipient"]=phone_number
        data["msg"]="Hi, your one-time code is: " + otp
        response=requests.post(sms_url, json=data)
        print(response.text)

        return response.text
    except Exception as e:
        print(e)
        return None 
    
def validate_token(token):
    if not token:
        return None, {'Error': 'Forbidden! Invalid token.', 'type': 'TokenError'}, 403

    try:
        decoded_token = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None, {'Error': 'Token has expired', 'type': 'TokenError'}, 401
    except jwt.InvalidTokenError:
        return None, {'Error': 'Forbidden! Invalid token.', 'type': 'TokenError'}, 403

    return decoded_token, None, None

def fetch_client_data(client_id):
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

def check_blocked(blocked_dict, dict_key):
    current_time = time()

    # Check if the client is blocked and if the block period has expired
    if dict_key in blocked_dict:
        if current_time < blocked_dict[dict_key]:
            return True
        else:
            # Unblock the client after the block period has expired
            del blocked_dict[dict_key]
    
    return False

def get_optimal_trip(start_lat, start_lon, clients):
    # Define the OSRM API endpoint
    osrm_url = 'http://router.project-osrm.org/trip/v1/driving/'

    # Extract the waypoints coordinates from the clients array
    waypoints = [(client['client_lat'], client['client_long']) for client in clients]

    # Combine starting point and waypoints into a single list
    coordinates = [(start_lon, start_lat)] + [(lon, lat) for lat, lon in waypoints]

    # Format coordinates for the OSRM API
    coordinates_str = ';'.join([f'{lon},{lat}' for lon, lat in coordinates])

    # Define the OSRM trip endpoint with the coordinates
    trip_url = f'{osrm_url}{coordinates_str}?source=first&roundtrip=false'

    # Send request to the OSRM API
    response = requests.get(trip_url)
    data = response.json()

    # Extract the route information
    if data['code'] == 'Ok':
        # Extract the waypoints order from the waypoints array
        waypoints_info = data['waypoints']

        # The order is determined by the 'trips' array in the legs
        waypoint_order = [waypoint['waypoint_index'] for waypoint in waypoints_info]

        # Create an ordered list of clients based on the waypoints order
        ordered_clients = [clients[i - 1] for i in waypoint_order[1:]]  # Skip the first element as it is the start point

        return ordered_clients, None
    else:
        return None, data['message']

def fetch_client_equipment_reports_in_date(date, client_id):
    conn = get_db_connection()
    if conn is None:
        return None, "Could not connect to the database"

    cur = conn.cursor(dictionary=True)
    cur.execute("""
                SELECT 
                    ReportedEquipment.*,
                    Equipment.eqp_name,
                    Equipment.eqp_type,
                    Equipment.eqp_manufacturer
                FROM 
                    ReportedEquipment
                LEFT JOIN 
                    Equipment 
                ON 
                    ReportedEquipment.reqp_details = Equipment.eqp_cat_number
                WHERE 
                    ReportedEquipment.reqp_date = %s 
                    AND ReportedEquipment.reqp_client = %s
                """, (date, client_id))
    result = cur.fetchall()
    cur.close()
    conn.close()

    return result, None

def fetch_client_cabinet_reports_in_date(date, client_id):
    conn = get_db_connection()
    if conn is None:
        return None, "Could not connect to the database"

    cur = conn.cursor(dictionary=True)
    cur.execute("""
                SELECT * FROM ReportedCabinet 
                WHERE rcab_date = %s AND rcab_client = %s
                """, (date, client_id))
    result = cur.fetchall()
    cur.close()
    conn.close()

    return result, None

def fetch_last_client_equipment_reports(client_id):
    conn = get_db_connection()
    if conn is None:
        return None, "Could not connect to the database"

    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT MAX(reqp_date) as latest_date 
        FROM ReportedEquipment 
        WHERE reqp_client = %s AND reqp_in_use = 1
    """, (client_id,))
    latest_date_result = cur.fetchone()

    if latest_date_result is None:
        cur.close()
        conn.close()
        return None, None
    
    latest_date = latest_date_result['latest_date']
    cur.execute("""
        SELECT * FROM ReportedEquipment 
        WHERE reqp_date = %s AND reqp_client = %s AND reqp_in_use = 1
    """, (latest_date, client_id))
    result = cur.fetchall()
    
    cur.close()
    conn.close()

    return result, None

def fetch_last_client_cabinet_reports(client_id):
    conn = get_db_connection()
    if conn is None:
        return None, "Could not connect to the database"

    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT MAX(rcab_date) as latest_date 
        FROM ReportedCabinet 
        WHERE rcab_client = %s
    """, (client_id,))
    latest_date_result = cur.fetchone()

    if latest_date_result is None:
        cur.close()
        conn.close()
        return None, None
    
    latest_date = latest_date_result['latest_date']
    cur.execute("""
        SELECT * FROM ReportedCabinet 
        WHERE rcab_date = %s AND rcab_client = %s
    """, (latest_date, client_id))
    result = cur.fetchall()
    
    cur.close()
    conn.close()

    return result, None
    
@app.route('/requestClientAuth', methods=['POST'])
@limiter.limit("5 per minute")

def request_client_auth():
    data = request.get_json()
    client_id = data.get('client_id')

    if not re.match(r'^\d+$', client_id):
       return jsonify({"error": "Invalid client ID format"}), 400

    current_time = time()

    # Check if the client is blocked from resending OTPs.
    if check_blocked(otp_resend_blocked, client_id):
      return jsonify({"error": "Maximum OTP attempts exceeded. Please try again later."}), 403

    try:
        client_data = fetch_client_data(client_id)
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
    
    if check_blocked(otp_blocked, client_id):
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
        client_data = fetch_client_data(client_id)

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

@app.route('/employeeAuth', methods=['POST'])
@limiter.limit("5 per minute")
def employee_auth():
    data = request.get_json()
    username = data.get('emp_user')
    password = data.get('emp_password')

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    if check_blocked(employee_login_blocked, username):
        return jsonify({"error":"Maximum login attempts exceeded. Please try again later."}), 403
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute('SELECT emp_user, emp_password, emp_role, emp_ID FROM Employee WHERE emp_user = %s', (username,))
        user = cursor.fetchone()
    except mysql.connector.Error as err:
        app.logger.error("Database query failed.")
        app.logger.error(err)
        cursor.close()
        conn.close()
        return jsonify({'error': 'Database query failed'}), 500

    if user is None:
        return jsonify({"error": "Incorrect username or password"}), 401
    else:
        if user['emp_password'] == password:
            employee_login_attempts.pop(username, None)
            employee_login_blocked.pop(username, None)
            
            token = jwt.encode({
                'emp_ID': user['emp_ID'],
                'role': user['emp_role'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24) }
                ,JWT_SECRET_KEY, algorithm='HS256')
        
            return jsonify({"token": token}), 200
        else:
            if username not in employee_login_attempts:
                employee_login_attempts[username] = 1
            else:
                employee_login_attempts[username] += 1

            if employee_login_attempts[username] >= MAX_LOGIN_ATTEMPTS:
                employee_login_blocked[username] = time() + BLOCK_TIME
                return jsonify({"error":"Maximum login attempts exceeded. Please try again later."}), 403
                
            return jsonify({"error":f"username or password are incorrect {MAX_LOGIN_ATTEMPTS - employee_login_attempts[username]} attempts left"}), 401

@app.route('/userRole', methods=['GET'])
def get_user_role():
    token = request.args.get('token', '')
    decoded_token, error_response, status_code = validate_token(token)

    if error_response:
        return jsonify(error_response), status_code
    
    return jsonify(decoded_token.get('role')), 200

@app.route('/clientRepresentative', methods=['GET'])
def get_client_representative():
    token = request.args.get('token', '')
    rep_id = request.args.get('id', '')
    decoded_token, error_response, status_code = validate_token(token)
    
    if error_response:
        return jsonify(error_response), status_code
    
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
    token = request.args.get('token')

    decoded_token, error_response, status_code = validate_token(token)
    if error_response:
        response = make_response(jsonify(error_response), status_code)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    rep_id = decoded_token.get('rep_id')
    
    conn = get_db_connection()
    if conn is None:
        response = make_response(jsonify({'Error':'Could not connect to the database.'}), 500)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT rep_firstname, rep_lastname FROM ClientRepresentative WHERE rep_id = %s", (rep_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    response = make_response(jsonify(result))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

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
def get_appointments_in_month_and_year():
    token = request.args.get('token', '')
    month = request.args.get('month')
    year = request.args.get('year')


    decoded_token, error_response, status_code = validate_token(token)
    if error_response:
        return jsonify(error_response), status_code
    
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
    token = request.args.get('token')
    month = request.args.get('month')
    year = request.args.get('year')

    decoded_token, error_response, status_code = validate_token(token)
    if error_response:
        return jsonify(error_response), status_code
  
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
    token = data.get('token')
    apt_client = data.get('apt_client')
    apt_date = data.get('apt_date')
    new_apt_date = data.get('new_apt_date')
   
    # Validate token
    decoded_token, error_response, status_code = validate_token(token)
    if error_response:
        return jsonify(error_response), status_code

    if decoded_token.get('role') != 'Manager':
        return jsonify("Forbidden!"), 403


    # Check if employee is a manager
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cur = conn.cursor(dictionary=True)

    try:
        # Update appointment
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
    token = request.args.get('token')

    decoded_token, error_response, status_code = validate_token(token)
    if error_response:
        return jsonify(error_response), status_code
    
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
    token = request.args.get('token')  # Get the token from the query parameters

    if not date:
        return jsonify({"error": "Date parameter is required"}), 400

    # Validate token
    decoded_token, error_response, status_code = validate_token(token)
    if error_response:
        return jsonify(error_response), status_code
    
    if decoded_token.get('role') != 'Manager':
        return jsonify("Forbidden!"), 403

    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Database connection failed")

        cur = conn.cursor(dictionary=True)

        # Fetch unassigned appointments
        cur.execute("""
            SELECT a.apt_date, 
                   a.apt_client,  
                   c.client_name, 
                   c.client_city, 
                   c.client_street, 
                   c.client_street_number, 
                   cr.rep_phone 
            FROM Appointment a 
            LEFT JOIN Client c ON a.apt_client = c.client_id 
            LEFT JOIN ClientRepresentative cr ON c.client_rep = cr.rep_id 
            WHERE a.apt_date = %s AND a.apt_status = 'open' AND a.apt_emp_executive is NULL
        """, (date,))
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
    token = request.args.get('token')

    decoded_token, error_response, status_code = validate_token(token)
    if error_response:
        return jsonify(error_response), status_code

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
    data = request.get_json()
    token = data.get('token')
    decoded_token, error_response, status_code = validate_token(token)
    if error_response:
        return jsonify(error_response), status_code

    if decoded_token.get('role') != 'Manager':
        return jsonify("Forbidden!"), 403
    
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
    
# GET /clientData
@app.route('/clientData', methods=['GET'])
def get_client_data():
    token = request.args.get('token')
    client_id = request.args.get('client_id')
    decoded_token, error_response, status_code = validate_token(token)
    if error_response:
        return jsonify(error_response), status_code

    if not client_id:
        return jsonify({"error": "client_id is required query parameter."}), 400
    
    try:
        results = fetch_client_data(client_id)
        return jsonify(results), 200
    except Exception as error:
        return jsonify({"error": error}), 500

# GET /employeeData
@app.route('/employeeData', methods=['GET'])
def get_employee_data():

    token = request.args.get('token')
    decoded_token, error_response, status_code = validate_token(token)
    if error_response:
        return jsonify(error_response), status_code
    
    emp_ID = decoded_token.get('emp_ID')
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute('SELECT emp_ID, emp_firstname, emp_lastname, emp_role, emp_phone, emp_user FROM Employee WHERE emp_ID = %s', (emp_ID,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return jsonify(result), 200
    except mysql.connector.Error as err:
        app.logger.error("Database query failed.")
        app.logger.error(err)
        cursor.close()
        conn.close()
        return jsonify({'error': 'Database query failed'}), 500

# GET /allEquipmentReportsInDate
@app.route('/allEquipmentReportsInDate', methods=['GET'])
def get_all_equipment_reports_in_date():
    token = request.args.get('token')
    date = request.args.get('date')
    client_id = request.args.get('client_id')
    decoded_token, error_response, status_code = validate_token(token)
    if error_response:
        return jsonify(error_response), status_code

    if not date or not client_id:
        return jsonify({"error": "date and client_id are required query parameters."}), 400

    results, error = fetch_client_equipment_reports_in_date(date, client_id)

    if error:
        return jsonify({"error": error}), 500

    return jsonify(results), 200

# GET /allCabinetReportsInDate
@app.route('/allCabinetReportsInDate', methods=['GET'])
def get_all_cabinet_reports_in_date():
    token = request.args.get('token')
    date = request.args.get('date')
    client_id = request.args.get('client_id')

    decoded_token, error_response, status_code = validate_token(token)
    if error_response:
        return jsonify(error_response), status_code

    if not date or not client_id:
        return jsonify({"error": "date and client_id are required query parameters."}), 400

    results, error = fetch_client_cabinet_reports_in_date(date, client_id)

    if error:
        return jsonify({"error": error}), 500

    return jsonify(results), 200

# GET /lastCabinetReports
@app.route('/lastCabinetReports', methods=['GET'])
def get_last_cabinet_reports():
    token = request.args.get('token')
    client_id = request.args.get('client_id')
    decoded_token, error_response, status_code = validate_token(token)
    if error_response:
        return jsonify(error_response), status_code

    if not client_id:
        return jsonify({"error": "client_id is required query parameter."}), 400

    results, error = fetch_last_client_cabinet_reports(client_id)

    if error:
        return jsonify({"error": error}), 500

    return jsonify(results), 200


# POST /makeEquipmentReportsInDate
@app.route('/makeEquipmentReportsInDate', methods=['POST'])
def make_equipment_reports_in_date():
    data = request.get_json()
    token = data.get('token')
    date = data.get('date')
    client_id = data.get('client_id')  # Get the JSON data from the request body

    decoded_token, error_response, status_code = validate_token(token)
    if error_response:
        return jsonify(error_response), status_code

    reports_in_date, error = fetch_client_equipment_reports_in_date(date, client_id)

    if error:
        return jsonify({"error-fetch-in-date": error}), 500
    
    if reports_in_date:
        return jsonify({"message" : "This client already has equipment reports in this date."}), 200
    else:
        latest_reports, error = fetch_last_client_equipment_reports(client_id)

        if error:
            return jsonify({"error": error}), 500
        
        if not latest_reports:
            return jsonify({"message" : "This client has no equipment reports. It might be a new client."}), 200
        else:
            conn = get_db_connection()

            if conn is None:
                return jsonify({"error": "Database connection failed"}), 500
            
            cur = conn.cursor()

            try:
                for report in latest_reports:
                    cur.execute(""" INSERT INTO ReportedEquipment (reqp_id, reqp_date, reqp_client, reqp_details, reqp_location, reqp_belongs_cabinet, reqp_pressure_test_year)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s) 
                                """,(report['reqp_id'], date, client_id, report['reqp_details'], report['reqp_location'],report['reqp_belongs_cabinet'], report['reqp_pressure_test_year']))
                conn.commit()
            except mysql.connector.Error as err:
                conn.rollback()
                app.logger.error("Error: Could not execute INSERT statement.")
                app.logger.error(err)
                cur.close()
                conn.close()
                return jsonify({"error": err}), 500

            cur.close()
            conn.close()
            
            return jsonify({"message": "Reported equipments is made successfully!"}), 200


# POST /makeCabinetReportsInDate
@app.route('/makeCabinetReportsInDate', methods=['POST'])
def make_cabinet_reports_in_date():
    data = request.get_json()
    token = data.get('token')
    date = data.get('date')
    client_id = data.get('client_id')  # Get the JSON data from the request body

    decoded_token, error_response, status_code = validate_token(token)
    if error_response:
        return jsonify(error_response), status_code

    reports_in_date, error = fetch_client_cabinet_reports_in_date(date, client_id)

    if error:
        return jsonify({"error": error}), 500
    
    if reports_in_date:
        return jsonify({"message" : "This client already has cabinet reports in this date."}), 200
    else:
        latest_reports, error = fetch_last_client_cabinet_reports(client_id)

        if error:
            return jsonify({"error": error}), 500
        
        if not latest_reports:
            return jsonify({"error" : "This client has no cabinet reports. It might be a new client."}), 200
        else:
            conn = get_db_connection()

            if conn is None:
                return jsonify({"error": "Database connection failed"}), 500
            
            cur = conn.cursor()

            try:
                for report in latest_reports:
                    cur.execute(""" INSERT INTO ReportedCabinet (rcab_id, rcab_date, rcab_client, rcab_location, rcab_rollers, rcab_nozzle2s, rcab_hoses, rcab_firehydrants, rcab_firecabinets)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) 
                                """,(report['rcab_id'], date, client_id, report['rcab_location'], report['rcab_rollers'], report['rcab_nozzle2s'], report['rcab_hoses'], report['rcab_firehydrants'], report['rcab_firecabinets']))
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

            return jsonify({"message": "Reported cabinets is made successfully!"}), 200

# GET /allEquipments
@app.route('/allEquipments', methods=['GET'])
def get_all_equipments():
    """Fetch all equipments from the Equipment table."""
    token = request.args.get('token')
    decoded_token, error_response, status_code = validate_token(token)
    if error_response:
        return jsonify(error_response), status_code
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT * FROM Equipment
    """)
    results = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify(results)

# GET /allMeintenanceOps
@app.route('/allMeintenanceOps', methods=['GET'])
def get_all_meintenance_operations():
    """Fetch all maintenance operations from the MeintenanceOperations table."""
    token = request.args.get('token')

    decoded_token, error_response, status_code = validate_token(token)
    if error_response:
        return jsonify(error_response), status_code
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT * FROM MaintenanceOperations
    """)
    results = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify(results)


#POST /addReportedEquipment
@app.route('/addReportedEquipment', methods=['POST'])
def add_reported_equipment():
    """Add a new reported equipment entry to the ReportedEquipment table."""
    data = request.get_json()
    token = data.get('token')
    decoded_token, error_response, status_code = validate_token(token)

    if error_response:
        return jsonify(error_response), status_code
    
    new_reported_equipment = data.get('new_reported_equipment')
    required_fields = ['reqp_id', 
                       'reqp_date', 
                       'reqp_client', 
                       'reqp_details', 
                       'reqp_location', 
                       'reqp_belongs_cabinet', 
                       'reqp_is_new', 
                       'reqp_pressure_test_year']
    for field in required_fields:
        if field not in new_reported_equipment:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cur = conn.cursor(dictionary=True)
    
    try:
        cur.execute(
                "INSERT INTO ReportedEquipment (reqp_id, reqp_date, reqp_client, reqp_details, reqp_location, reqp_belongs_cabinet, reqp_is_new, reqp_pressure_test_year) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    new_reported_equipment['reqp_id'],
                    new_reported_equipment['reqp_date'],
                    new_reported_equipment['reqp_client'],
                    new_reported_equipment['reqp_details'],
                    new_reported_equipment['reqp_location'],
                    new_reported_equipment['reqp_belongs_cabinet'],
                    new_reported_equipment['reqp_is_new'],
                    new_reported_equipment['reqp_pressure_test_year'],
                )
            )
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        app.logger.error("Error: Could not execute INSERT statement.")
        app.logger.error(err)
        cur.close()
        conn.close()
        response = make_response(jsonify({"error": err}), 500)
        return response
    
    cur.close()
    conn.close()
    response = make_response(jsonify({'message': 'Reported equipment added successfully'}), 200)
    return response

#PUT /updateReportedEquipment
@app.route('/updateReportedEquipment', methods=['PUT'])
def update_reported_equipment():
    """Update an existing reported equipment entry in the ReportedEquipment table."""
    data = request.get_json()
    token = data.get('token')
    decoded_token, error_response, status_code = validate_token(token)

    if error_response:
        return jsonify(error_response), status_code

    updated_reported_equipment = data.get('updated_reported_equipment')
    required_fields = [
        'reqp_id',
        'reqp_date', 
        'reqp_client', 
        'reqp_details',
        'reqp_location', 
        'reqp_belongs_cabinet',
        'reqp_in_use',
        'reqp_pressure_test_year',
        'reqp_maintenance_ops', 
        'reqp_fix_desc',
        'reqp_future_treatment',
        'reqp_remarks'
    ]

    for field in required_fields:
        if field not in updated_reported_equipment:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cur = conn.cursor()
    
    try:
        cur.execute(
            """UPDATE ReportedEquipment 
               SET reqp_details = %s, 
                reqp_location = %s, 
                reqp_belongs_cabinet = %s, 
                reqp_in_use = %s, 
                reqp_pressure_test_year = %s, 
                reqp_maintenance_ops = %s, 
                reqp_fix_desc = %s,
                reqp_future_treatment = %s, 
                reqp_remarks = %s
               WHERE reqp_id = %s AND reqp_date = %s AND reqp_client = %s""",
            (
                updated_reported_equipment['reqp_details'], 
                updated_reported_equipment['reqp_location'],
                updated_reported_equipment['reqp_belongs_cabinet'],
                updated_reported_equipment['reqp_in_use'],
                updated_reported_equipment['reqp_pressure_test_year'],  
                updated_reported_equipment['reqp_maintenance_ops'], 
                updated_reported_equipment['reqp_fix_desc'],
                updated_reported_equipment['reqp_future_treatment'], 
                updated_reported_equipment['reqp_remarks'], 
                updated_reported_equipment['reqp_id'],
                updated_reported_equipment['reqp_date'],
                updated_reported_equipment['reqp_client']
            )
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
    return jsonify({'message': 'Reported equipment updated successfully'}), 200


@app.route('/addReportedCabinet', methods=['POST'])
def add_reported_cabinet():
    # Get JSON data from the request
    data = request.get_json()
    token = data.get('token')
    decoded_token, error_response, status_code = validate_token(token)
    
    if error_response:
        return jsonify(error_response), status_code
    
    new_reported_cabinet = data.get('new_reported_cabinet')

    # Extract required fields from the JSON data
    required_fields = [
        'rcab_date', 
        'rcab_client', 
        'rcab_location', 
        'rcab_rollers', 
        'rcab_nozzle2s', 
        'rcab_hoses', 
        'rcab_firehydrants', 
        'rcab_firecabinets'
    ]
    # Check if all required fields are present
    if not all(field in new_reported_cabinet for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    # Establish a connection to the database
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor()

    try:
        query = '''
            INSERT INTO ReportedCabinet (
                rcab_date, rcab_client, rcab_location, 
                rcab_rollers, rcab_nozzle2s, rcab_hoses, 
                rcab_firehydrants, rcab_firecabinets
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        '''
        cursor.execute(query, (
            new_reported_cabinet['rcab_date'],
            new_reported_cabinet['rcab_client'], 
            new_reported_cabinet['rcab_location'], 
            new_reported_cabinet['rcab_rollers'], 
            new_reported_cabinet['rcab_nozzle2s'], 
            new_reported_cabinet['rcab_hoses'], 
            new_reported_cabinet['rcab_firehydrants'], 
            new_reported_cabinet['rcab_firecabinets']
        ))
        conn.commit()
    except mysql.connector.Error as err:
        app.logger.error("Database insert failed.")
        app.logger.error(err)
        cursor.close()
        conn.close()
        return jsonify({'error': 'Database insert failed'}), 500
    
    cursor.close()
    conn.close()
    return jsonify({'message': 'Reported cabinet added successfully'}), 200

@app.route('/updateReportedCabinet', methods=['PUT'])
def update_reported_cabinet():
    # Get JSON data from the request
    data = request.get_json()
    token = data.get('token')
    decoded_token, error_response, status_code = validate_token(token)

    if error_response:
        return jsonify(error_response), status_code

    updated_reported_cabinet = data.get('updated_reported_cabinet')

    # Extract required fields from the JSON data
    required_fields = [
        'rcab_id', 
        'rcab_date', 
        'rcab_client', 
        'rcab_location', 
        'rcab_rollers', 
        'rcab_nozzle2s', 
        'rcab_hoses', 
        'rcab_firehydrants', 
        'rcab_firecabinets',
        'rcab_new_hoses', 
        'rcab_new_rollers', 
        'rcab_new_nozzle2s', 
        'rcab_new_nozzle1s', 
        'rcab_new_firehydrants', 
        'rcab_roller_standard', 
        'rcab_fix_desc', 
        'rcab_remarks'
    ]

    # Check if all required fields are present
    if not all(field in updated_reported_cabinet for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    # Establish a connection to the database
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor()

    try:
        query = '''
            UPDATE ReportedCabinet
            SET rcab_location = %s, rcab_rollers = %s, rcab_nozzle2s = %s, rcab_hoses = %s, 
                rcab_firehydrants = %s, rcab_firecabinets = %s, rcab_new_hoses = %s, 
                rcab_new_rollers = %s, rcab_new_nozzle2s = %s, rcab_new_nozzle1s = %s, 
                rcab_new_firehydrants = %s, rcab_roller_standard = %s, rcab_fix_desc = %s, 
                rcab_remarks = %s
            WHERE rcab_id = %s AND rcab_date = %s AND rcab_client = %s
        '''
        cursor.execute(query, (
            updated_reported_cabinet['rcab_location'], 
            updated_reported_cabinet['rcab_rollers'], 
            updated_reported_cabinet['rcab_nozzle2s'], 
            updated_reported_cabinet['rcab_hoses'], 
            updated_reported_cabinet['rcab_firehydrants'], 
            updated_reported_cabinet['rcab_firecabinets'], 
            updated_reported_cabinet['rcab_new_hoses'], 
            updated_reported_cabinet['rcab_new_rollers'], 
            updated_reported_cabinet['rcab_new_nozzle2s'], 
            updated_reported_cabinet['rcab_new_nozzle1s'], 
            updated_reported_cabinet['rcab_new_firehydrants'], 
            updated_reported_cabinet['rcab_roller_standard'], 
            updated_reported_cabinet['rcab_fix_desc'], 
            updated_reported_cabinet['rcab_remarks'], 
            updated_reported_cabinet['rcab_id'], 
            updated_reported_cabinet['rcab_date'], 
            updated_reported_cabinet['rcab_client']
        ))
        conn.commit()
    except mysql.connector.Error as err:
        app.logger.error("Database update failed.")
        app.logger.error(err)
        cursor.close()
        conn.close()
        return jsonify({'error': 'Database update failed'}), 500
    
    cursor.close()
    conn.close()
    return jsonify({'message': 'Reported cabinet updated successfully'}), 200

@app.route('/dailyEmployeeOpenTasks', methods=['GET'])
def daily_employee_open_tasks():
    # Get parameters from the request
    token = request.args.get('token')
    apt_date = request.args.get('apt_date')
    lat = request.args.get('lat')
    long = request.args.get('long')

    decoded_token, error_response, status_code = validate_token(token)
    if error_response:
        return jsonify(error_response), status_code

    apt_emp_executive = decoded_token.get('emp_ID')
    
    if not apt_date or not apt_emp_executive:
        return jsonify({'error': 'Missing required parameters'}), 400

    # Establish a connection to the database
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)

    try:
        query = '''
                SELECT 
                    a.apt_client,
                    c.client_name,
                    c.client_lat,
                    c.client_long,
                    c.client_city,
                    c.client_street,
                    c.client_street_number,
                    cr.rep_phone
                FROM 
                    Appointment a
                LEFT JOIN 
                    Client c ON a.apt_client = c.client_id
                LEFT JOIN 
                    ClientRepresentative cr ON c.client_rep = cr.rep_id
                WHERE 
                    a.apt_emp_executive = %s
                    AND a.apt_date = %s
                    AND a.apt_status = 'open'
                '''
        cursor.execute(query, (apt_emp_executive, apt_date))
        results = cursor.fetchall()
        cursor.close()
        conn.close()

        if not results:
            return jsonify(results), 200
        else:
            if lat and long:
                ordered_tasks, error = get_optimal_trip(lat, long, results)

                if error:
                    return jsonify(results), 401
                else:
                    return jsonify(ordered_tasks), 200
            else:
                return jsonify(results), 200
    except mysql.connector.Error as err:
        app.logger.error("Database query failed.")
        app.logger.error(err)
        cursor.close()
        conn.close()
        return jsonify({'error': 'Database query failed'}), 500

@app.route('/closeAppointment', methods=['PUT'])
def close_appointment():
    # Get JSON data from the request
    data = request.get_json()
    token = data.get('token')
    date = data.get('date')
    client_id = data.get('client_id')
    decoded_token, error_response, status_code = validate_token(token)

    if error_response:
        return jsonify(error_response), status_code

    # Check if all required fields are present
    if not date or not client_id:

        return jsonify({'error': 'Missing required fields'}), 400

    # Establish a connection to the database
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor()

    try:
        query = '''
            UPDATE Appointment
            SET apt_status = 'closed'
            WHERE apt_date = %s AND apt_client = %s
        '''
        cursor.execute(query, (date, client_id))
        conn.commit()
    except mysql.connector.Error as err:
        app.logger.error("Database update failed.")
        app.logger.error(err)
        return jsonify({'error': 'Database update failed'}), 500
    
    cursor.close()
    conn.close()
    return jsonify({'message': 'Appointment closed successfully'}), 200


basedir = os.path.abspath(os.path.dirname(__file__))

# Construct the full path to the PEM files
cert_file = os.path.join(basedir, 'certificate.pem')
key_file = os.path.join(basedir, 'privatekey.pem')

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=5000, debug=True)
    app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=(cert_file, key_file))