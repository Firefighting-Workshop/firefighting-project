<script setup>
  import HeaderItem from '../components/HeaderItem.vue'
  import MessageBox from '../components/MessageBox.vue'
</script>
<template>
  <MessageBox v-key="forceRerenderKey" v-bind="appointmentExistError" v-show="!hideAppointmentExistError"></MessageBox>
  <v-container v-show="hideAppointmentExistError" fluid class="main-section pa-0">
    <HeaderItem headerTitle="קביעת תור תחזוקה שנתית" homeLink="/ClientHome" hideSignout hideHome></HeaderItem>
    <v-row class="contents-row ma-0 px-3">
      <h3 class="mt-9">מתי אתם פנויים?</h3>
      <p class="error-details text-red mt-2">{{ dateNotSelectedErrorMsg }}</p>
      <v-date-picker class="appointment-date-picker mt-2" v-model="selectedDate"
        :month="datepickerMonth"
        :year="datepickerYear" 
        width="300px" 
        color="red-darken-3" 
        :title="datepickerTitle"
        :allowed-dates="allowedDates" 
        header="בחר תאריך"
        :key="forceRerenderKey">
      </v-date-picker>
      <div class="buttons-container mt-9">
        <v-btn class="cancel-btn ff-outlined-btn me-6" variant="flat" to="/ClientHome" rounded="0">בטל</v-btn>
        <v-btn class="make-appointment ff-btn" variant="outlined" @click="makeAppointment" rounded="0">קבע תור</v-btn>
      </div>
    </v-row>
  </v-container>
</template>
<style scoped>
.make-appointment, .cancel-btn
{
  width: 145px;
  align-self: center;
}

.buttons-container
{
    display: flex;
    width: 100%;
    justify-content: center;
}
</style>
<style>
.appointment-date-picker
{
  align-self: center;
  border: 1px solid #C62828 !important;
}
.appointment-date-picker .v-date-picker-controls
{
  display:none !important;
}

.appointment-date-picker .v-date-picker-month__weekday
{
  font-weight: bold;
}
</style>
<script>
import API from '@/api/api.js';
export default {
  name: 'MakeAppointment',
  rtl: true,
  data: () => ({
      lastAppointmentDate: null,
      datepickerMonth: 0,
      datepickerYear: 0,
      dateNotSelectedErrorMsg: "",
      appointmentsCount: {},
      appointmentsQouta: 20,
      selectedDate: null,
      today: new Date(),
      forceRerenderKey: 0,
      hideTimeWindowError: true,
      hideAppointmentExistError: true,
      appointmentExistError: {
        messageTitle: "שגיאה",
        messageIcon: "mdi-close-circle",
        iconColor: "#E04F5F",
        messageHeader: "כבר נקבע עבורך תור לשירות תחזוקה שנתי",
        cancelText: "חזור",
        hideSubmit: true,
      }
    }),
  methods: {
    makeAppointment()
    {
      if(this.selectedDate == null)
      {
        this.dateNotSelectedErrorMsg = "יש לבחור תאריך";
      }
      else
      {
        this.dateNotSelectedErrorMsg = "";
        let api = new API();
        let token = localStorage.getItem('LOCAL_STORAGE_TOKEN_KEY');
        api.post('/makeAppointment', { "token": token, "apt_date": this.formattedSelectedDate})
        .then((response) => {
          console.log(response)
          this.$router.push('/ClientHome');
        })
        .catch((error) => {
          console.error('Error:', error);  
        });
      }
    },
    allowedDates(date) {
      const currentDate = new Date(date);
      const day = currentDate.getDay();
      const today = this.today;
      
      // Disable all past dates including today
      if (currentDate < today) {
        return false;
      }

      // Get the start and end of the current week (Sunday to Saturday)
      const startOfWeek = new Date(today);
      startOfWeek.setDate(today.getDate() - today.getDay());
      const endOfWeek = new Date(today);
      endOfWeek.setDate(today.getDate() + (6 - today.getDay()));

      // Disable dates in the same week as today
      if (currentDate >= startOfWeek && currentDate <= endOfWeek) {
        return false;
      }

      // Disable Saturdays
      if (day === 6) {
        return false;
      }

      // Check if the date appears in appointmentsCount and if the value is equal or greater than 1
      const formattedDate = currentDate.toLocaleDateString('en-CA');
      if (this.appointmentsCount[formattedDate] && this.appointmentsCount[formattedDate] >= this.appointmentsQouta) {
        console.log(formattedDate);
        return false;
      }
      return true;
    }
  },
  async mounted()
  {
    let api = new API();
    let token = localStorage.getItem('LOCAL_STORAGE_TOKEN_KEY');

    try
    {
        let response = await api.get('/nextAppointment', { "token" : token });
        let appointmentDate = new Date(response.data.apt_date);
        let dayDifference = Math.ceil((appointmentDate.getTime() - this.today.getTime()) / (1000 * 3600 * 24));
        console.log(dayDifference);

        if (appointmentDate != null)
        {
          this.hideAppointmentExistError = false;
        }
    }
    catch(error)
    {
      console.error('Error:', error);
    }
    
    if(this.hideAppointmentExistError)
    {
      try
      {
          let response =  await api.get('/lastAppointment', { "token" : token });
          this.lastAppointmentDate = new Date(response.data.apt_date);
          this.datepickerMonth = this.lastAppointmentDate.getMonth();
          this.datepickerYear = this.today.getFullYear();

          if(this.datepickerMonth < this.today.getMonth())
          {
            this.datepickerYear += 1;
          }
      }
      catch(error)
      {
        console.error('Error:', error);  
      }

      try
      {
        let response = await api.get('/appointmentsCount', { "month" : this.datepickerMonth + 1, "year" : this.datepickerYear});        
        console.log(response)
        this.appointmentsCount = response.data;
        console.log(this.appointmentsCount);

      }
      catch(error)
      {
        console.error('Error:', error);
      }
    }

    this.forceRerenderKey += 1;
  },
  computed: {
    datepickerTitle()
    {
      const monthNames = ['ינואר', 'פברואר', 'מרץ', 'אפריל', 'מאי', 'יוני',
        'יולי', 'אוגוסט', 'ספטמבר', 'אוקטובר', 'נובמבר', 'דצמבר'
      ]
      return monthNames[parseInt(this.datepickerMonth)] + " " + this.datepickerYear;
    },
    formattedSelectedDate() {
      if (!this.selectedDate) return '';
      const date = new Date(this.selectedDate);
      const day = String(date.getDate()).padStart(2, '0');
      const month = String(date.getMonth() + 1).padStart(2, '0'); // Months are zero-based
      const year = date.getFullYear();
      return `${year}-${month}-${day}`;
    }
  }
    
  }
</script>