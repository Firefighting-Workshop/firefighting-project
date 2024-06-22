<template>
    <v-card class="login-card">
      <v-tabs class="login-tabs" v-model="tab" align-tabs="center" color="deep-purple-accent-4" grow>
        <v-tab :value="EmployeeLoginTab">כניסה כעובד</v-tab>
        <v-tab :value="ClientLoginTab">כניסה כלקוח</v-tab>
      </v-tabs>
      <v-card-text class="py-0 pb-2 px-2">
      <v-tabs-window v-model="tab">
        <v-tabs-window-item class="text-center pa-4" value="EmployeeLoginTab">
          <v-text-field class="mt-4" 
            v-model="employeeUser"
            label="שם משתמש" 
            hide-details="auto"
            prepend-inner-icon="mdi-account-outline" 
            variant="outlined"
            density="custom-input-density"
          >
          </v-text-field>
          <v-text-field
            class="mt-6"
            v-model="employeePassword"
            :append-inner-icon="visible ? 'mdi-eye-off' : 'mdi-eye'" 
            prepend-inner-icon="mdi-lock-outline" 
            :type="visible ? 'text' : 'password'"  
            label="סיסמה" 
            hide-details="auto"
            variant="outlined"
            density="custom-input-density"
            @click:append-inner="visible = !visible"></v-text-field>
            <p class="error-details mt-2 text-red">{{ employeeLoginError }}</p>
            <v-checkbox hide-details class="mt-3" v-model="rememberMe" color="red-darken-3" density="compact" label="זכור אותי"></v-checkbox>
          <v-btn class="login-btn mt-2" @click="employeeLogin" variant="flat" rounded="xl">כניסה</v-btn>
        </v-tabs-window-item>
        <v-tabs-window-item value="ClientLoginTab">
          <v-carousel id="client-login-slides" class="pa-4" v-model="activeSlide" hide-delimiters :continuous="false" :show-arrows="false" :touch="false">
            <v-carousel-item class="pa-0" :key="0">
              <p class="client-login-desc mt-2 pb-2 text-right">כניסה לשירות עם קוד חד פעמי לנייד</p>
              <v-text-field class="mt-6"
                hide-details 
                label="מספר ח.פ" 
                v-model="clientBn"
                @change="validateBnOnlyDigits()"
                prepend-inner-icon="mdi-numeric" 
                variant="outlined"
                density="custom-input-density"
                :maxlength="9">
              </v-text-field>
              <p class="error-details mt-2 text-red">{{ requestOtpError }}</p>
              <v-btn class="login-btn mt-7" @click="sendOTP" variant="flat" rounded="xl">שלח לי קוד</v-btn>
            </v-carousel-item>
            <v-carousel-item class="pa-0" :key="1">
              <p class="client-login-desc mt-2 pb-2 text-right">קוד כניסה חד פעמי נשלח לנייד הרשום אצלנו.</p>
              <v-text-field class="mt-6"
                hide-details
                v-model="otpInput"
                label="קוד אימות שקיבלת למכשיר הנייד" 
                prepend-inner-icon="mdi-numeric" 
                variant="outlined" 
                density="custom-input-density"
                :maxlength="6">
              </v-text-field>
              <p class="error-details mt-2 text-red">{{ otpError }}</p>
              <v-btn class="login-btn mt-6" @click="clientLogin" variant="flat" rounded="xl">כניסה</v-btn>
              <p class="mt-4">לא קיבלתם קוד? 
                <a class="resend_otp_link" @click="sendOTP" href="#">לחצו כאן</a>
              </p>
              <p class="error-details text-red">{{ requestOtpError }}</p>
            </v-carousel-item>
          </v-carousel>
        </v-tabs-window-item>
      </v-tabs-window>
    </v-card-text>
    </v-card>
</template>
<style>
.login-card
{
  width: 100%;
}

.login-card .v-tabs-window-item
{
  height: 275px;
}

#client-login-slides
{
  display: flex;
  height: 100%;
  overflow: hidden;
}

#client-login-slides .v-window__container
{
  width: 100%;
  text-align: center;
  flex-shrink: 0;
  flex-basis: auto;
  flex-grow: unset;
}

.client-login-desc
{
  font-weight: 600;
}

.login-tabs .v-tab
{
  font-size: 18px;
  color: #33333350;
}

.login-tabs .v-tab-item--selected
{
  color: #333333 !important;
}

.login-tabs .v-tab__slider
{
  height: 1px;
  border-bottom: 1px solid #797979;
  opacity:1;
}

.login-tabs .v-tab-item--selected .v-tab__slider
{
  height: 3px;
  border-bottom: 3px solid #333;
}

.login-btn
{
  width:250px;
  height: 40px !important;
  padding: 0;
  align-self: center;
  font-size: 18px !important;
  font-weight: 500;
  color: #fafafa !important;
  background-color: #d10019 !important;
  transition: unset !important;
}

.login-btn:hover
{
  background-color: #fafafa !important;
  color: #d10019 !important;
  border: 2px solid #d10019;
  transition: unset !important;
}
</style>
<script>
import API from '@/api/api.js';
let api = new API();

export default {
  name: 'LoginCard',
  rtl: true,
  data: () => ({
      tab: null,
      visible: false,
      employeeUser: null,
      employeePassword: null,
      employeeLoginError: '',
      clientBn: '',
      otpInput: '',
      requestOtpError: '',
      otpError: '',
      rememberMe: false,
      activeSlide: 0
    }),
  methods: {
    validateBnOnlyDigits() {
      const regex = /^\d{9}$/;
      this.isValid = regex.test(this.clientBn);
      if (!this.isValid) {
        this.requestOtpError = 'המספר שהזנת אינו תקין, יש להזין 9 ספרות.';
      }
      else
      {
        this.requestOtpError = '';
      }
    },
    sendOTP()
    {
      if(this.requestOtpError == '')
      {
        console.log("Client ID:", this.clientBn);
        api.post('/requestClientAuth', { "client_id" : this.clientBn })
          .then((response) => {
            console.log(response)
            this.result = response.data;
            this.activeSlide = 1;
          })
          .catch((error) => {
            switch (error.response.status) { 
              case 403:
                this.requestOtpError = 'חרגת מסך בקשות לקוד כניסה, אנא נסה מאוחר יותר.';
                break;
              case 404:
                this.requestOtpError = 'מספר זה אינו נמצא במאגרנו, וודא שהזנת את המספר הנכון.';
                break;
              case 429:
                this.requestOtpError = 'חרגת מסך בקשות לקוד כניסה, אנא נסה מאוחר יותר.';
                console.log("Too many requests.");
                break;
              default:
                this.requestOtpError = "אירעה שגיאה, אנא נסה שנית.";
                console.error('Error:', error);
                break;
              }
          });
      }
    },
    clientLogin()
    {
      console.log("Client ID:", this.clientBn);
      api.post('/clientAuth', { "client_id" : this.clientBn, "otp": this.otpInput })
        .then((response) => {
          console.log(response)
          localStorage.setItem('LOCAL_STORAGE_TOKEN_KEY', response.data.token);
          this.$router.push('/ClientHome');
        })
        .catch((error) => {
          switch (error.response.status) { 
            case 403:
              this.otpError = 'חרגת מסך ניסיונות הכניסה, אנא נסה מאוחר יותר.';
              console.error('Error:', error);
              break;
            case 401:
              this.otpError = 'הקוד שהזנת שגוי.';
              console.error('Error:', error);
              break;
            case 400:
              this.otpError = 'פג תוקפו של קוד הכניסה.';
              console.error('Error:', error);
              break;
            case 429:
              this.otpError = 'חרגת מסך ניסיונות הכניסה, אנא נסה מאוחר יותר.';
              console.log("Too many requests.");
              break;
            default:
              this.otpError = "אירעה שגיאה, אנא נסה שנית.";
              console.error('Error:', error);
              break;
            }
        });
    },
    async employeeLogin()
    {
        try
        {
            let response = await api.post('/employeeAuth', { "emp_user" : this.employeeUser, "emp_password": this.employeePassword});
            localStorage.setItem('LOCAL_STORAGE_TOKEN_KEY', response.data.token);
            this.$router.push('/EmployeeHome');
        }
        catch(error)
        {
          console.log(error);

          switch (error.response.status) 
          {
            case 400:
              this.employeeLoginError = "יש להזין שם משתמש וסיסמה.";
              break;
            case 401:
              this.employeeLoginError = "שם המשתמש או הסיסמה שהוזנו לא נכונים."
              break;
            case 403:
              this.employeeLoginError = 'חרגת מסך ניסיונות הכניסה, אנא נסה מאוחר יותר.'
              break;
            case 429:
              this.employeeLoginError = 'חרגת מסך ניסיונות הכניסה, אנא נסה מאוחר יותר.'
              break;
            default:
              this.employeeLoginError = "אירעה שגיאה, אנא נסה שנית."
                break;
          }
        }
    }
  },
  watch: {
    rememberMe(newValue) {
      if (newValue && this.employeeUser) {
        localStorage.setItem("REMEMBER_ME", true);
        localStorage.setItem("LAST_USER", this.employeeUser);
      } else {
        localStorage.removeItem("REMEMBER_ME");
        localStorage.removeItem("LAST_USER");
      }
    },
    employeeUser(newValue) {
      if (this.rememberMe && newValue) {
        localStorage.setItem("LAST_USER", newValue);
      }
    }
  },
  mounted()
  {
    let rememberMe = localStorage.getItem("REMEMBER_ME");
    console.log(rememberMe);
    let lastUser = localStorage.getItem("LAST_USER");

    if(rememberMe == "true")
    {
      this.employeeUser = lastUser;
      this.rememberMe = true;
    }
    else
    {
        this.rememberMe = false;
    }
  }
}
</script>