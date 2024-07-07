<script setup>
  import HeaderItem from '../components/HeaderItem.vue'
</script>
<template>
  <v-container fluid class="main-section pa-0">
    <HeaderItem headerTitle="בקשת שירות" hideHome hideBack></HeaderItem>
    <v-row class="contents-row ma-0 px-3">
      <p class="greeting-title mt-9">שלום <span>{{ clientRepName }}</span>!</p>
      <h3 class="mt-6">תור קרוב</h3>
      <v-card class="ff-card mt-2 pa-2" v-show="!appointmentNotFound" variant="outlined">
        <p class="ff-card-property mb-2">מועד: <span>{{ formattedAppointmentDate }}</span></p>
        <p class="ff-card-property mb-2">כתובת: <span>{{ clientStreet }} {{ clientStreetNumber }}, {{ clientCity }}</span></p>
        <p class="ff-card-property mb-2">טכנאי מבצע: <span>{{ executiveEmployee }}</span></p>
        <v-btn class="change-appointment ff-btn" variant="flat" rounded="0" to="/ChangeAppointment" prepend-icon="mdi-calendar-multiselect-outline">שנה תור</v-btn>
        <p class="text-center font-weight-medium mt-2">שים לב! שינוי תור יתאפשר עד שבוע מהמועד שנקבע.</p>
      </v-card>
      <v-card class="ff-card mt-2 pa-2" v-show="appointmentNotFound" variant="outlined">
        <p class="appointment-not-found">לא מצאנו תור קרוב שנקבע</p>
      </v-card>
      <v-btn class="ff-main-button mt-6" v-show="showMakeAppointmentButton" variant="flat" rounded="0" to="/MakeAppointment" prepend-icon="mdi-calendar-check-outline">קבע תור תחזוקה שנתית</v-btn>
    </v-row>
  </v-container>
</template>
<style scoped>
.greeting-title
{
  font-weight: bold;
  font-size: 28px;
}

.change-appointment
{
  width: 120px;
  align-self: center;
}

.appointment-not-found
{
  display: flex;
  flex-wrap: wrap;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 75px;
  font-weight: 500;
  font-size: 18px;
  color: #bdbdbd;
}
</style>
<script>
import API from '@/api/api.js';
export default {
  name: 'ClientHome',
  rtl: true,
  data: () => ({
      appointmentNotFound: true,
      appointmentDate: "",
      clientCity: "",
      clientStreet: "",
      clientStreetNumber: "",
      executiveEmployee: "",
      clientRepName: "",
      showMakeAppointmentButton: true
    }),
  methods: {
    
    },
  async mounted()
  {
    let api = new API();
    let token = localStorage.getItem('LOCAL_STORAGE_TOKEN_KEY');
    await api.get('/repName', { "token" : token })
      .then((response) => {
        console.log(response)
        this.clientRepName = response.data.rep_firstname;
      })
      .catch((error) => {
          console.error('Error:', error);  
      });

    await api.get('/nextAppointment', { "token" : token })
    .then((response) => {
      this.appointmentNotFound = false;
      this.showMakeAppointmentButton = false;
      this.appointmentDate = response.data.apt_date;
      this.clientCity = response.data.client_city;
      this.clientStreet = response.data.client_street;
      this.clientStreetNumber = response.data.client_street_number;
      this.executiveEmployee = 
        response.data.emp_firstname && response.data.emp_lastname ?
        response.data.emp_firstname + " " + response.data.emp_lastname:
        "- טרם שובץ -";
      this.appointmentDetailsCardKey += 1;
      this.notFoundCardKey += 1;
    })
    .catch((error) => {
        console.error('Error:', error);  
    });
  },
  computed:
  {
    formattedAppointmentDate() {
      if (!this.appointmentDate) return '';
      const date = new Date(this.appointmentDate);
      const day = String(date.getDate()).padStart(2, '0');
      const month = String(date.getMonth() + 1).padStart(2, '0'); // Months are zero-based
      const year = date.getFullYear();
      return `${day}/${month}/${year}`;
    }
  }
}
</script>