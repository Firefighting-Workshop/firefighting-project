<template>
    <v-card class="login-card">
      <v-tabs class="login-tabs" v-model="tab" align-tabs="center" color="deep-purple-accent-4" grow>
        <v-tab :value="WorkerLoginTab">כניסה כעובד</v-tab>
        <v-tab :value="ClientLoginTab">כניסה כלקוח</v-tab>
      </v-tabs>
      <v-card-text class="py-0 pb-2 px-2">
      <v-tabs-window v-model="tab">
        <v-tabs-window-item class="text-center pa-4" value="WorkerLoginTab">
          <v-text-field class="mt-4" 
            label="שם משתמש" 
            hide-details="auto"
            prepend-inner-icon="mdi-account-outline" 
            variant="outlined"
            density="custom-input-density"
          >
          </v-text-field>
          <v-text-field
            class="mt-6"
            :append-inner-icon="visible ? 'mdi-eye-off' : 'mdi-eye'" 
            prepend-inner-icon="mdi-lock-outline" 
            :type="visible ? 'text' : 'password'"  
            label="סיסמה" 
            hide-details="auto"
            variant="outlined"
            density="custom-input-density"
            @click:append-inner="visible = !visible"></v-text-field>
            <v-checkbox hide-details class="mt-3" color="red-darken-3" label="זכור אותי"></v-checkbox>
          <v-btn class="login-btn mt-2" variant="flat" rounded="xl">כניסה</v-btn>
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
              <p class="error-details mt-2 text-red">{{ RequestOtpError }}</p>
              <v-btn class="login-btn mt-7" @click="sendOTP()" variant="flat" rounded="xl">שלח לי קוד</v-btn>
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
              <p class="error-details mt-2 text-red">{{ OtpError }}</p>
              <v-btn class="login-btn mt-6" @click="login()" variant="flat" rounded="xl">כניסה</v-btn>
              <p class="mt-4">לא קיבלתם קוד? 
                <a class="resend_otp_link" @click="sendOTP()" href="#">לחצו כאן</a>
              </p>
              <p class="error-details text-red">{{ RequestOtpError }}</p>
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
export default {
  name: 'LoginCard',
  rtl: true,
  data: () => ({
      tab: null,
      visible: false,
      clientBn: '',
      otpInput: '',
      RequestOtpError: '',
      OtpError: '',
      activeSlide: 0
    }),
  methods: {
    validateBnOnlyDigits() {
      const regex = /^\d{9}$/;
      this.isValid = regex.test(this.clientBn);
      if (!this.isValid) {
        this.RequestOtpError = 'המספר שהזנת אינו תקין, יש להזין 9 ספרות.';
      }
      else
      {
        this.RequestOtpError = '';
      }
    },
    sendOTP()
    {
      if(this.RequestOtpError == '')
      {
        let api = new API();
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
                this.RequestOtpError = 'חרגת מסך בקשות לקוד כניסה, אנא נסה מאוחר יותר.'
                break;
              case 404:
                this.RequestOtpError = 'מספר זה אינו נמצא במאגרנו, וודא שהזנת את המספר הנכון.'
                break;
              case 429:
                console.log("Too many requests.");
                break;
              default:
                this.RequestOtpError = "אירעה שגיאה, אנא נסה שנית."
                console.error('Error:', error);
                break;
              }
          });
      }
    },
    login()
    {
      let api = new API();
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
                this.OtpError = 'חרגת מסך ניסיונות הכניסה, אנא נסה מאוחר יותר.'
                console.error('Error:', error);
                break;
              case 401:
                this.OtpError = 'הקוד שהזנת שגוי.'
                console.error('Error:', error);
                break;
              case 400:
                this.OtpError = 'פג תוקפו של קוד הכניסה.'
                console.error('Error:', error);
                break;
              case 429:
                console.log("Too many requests.");
                break;
              default:
                this.OtpError = "אירעה שגיאה, אנא נסה שנית."
                console.error('Error:', error);
                break;
              }
          });
    }
  }
}
</script>