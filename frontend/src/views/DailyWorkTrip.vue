<script setup>
import HeaderItem from '../components/HeaderItem.vue';
import MessageBox from '../components/MessageBox.vue';
import StationCard from '../components/StationCard.vue';
</script>

<template>
  <MessageBox v-show="showGeolocationError" v-bind="geolocationErrorMessageBox" :submitFunction="reloadPage" :messageHeader="geolocationErrorMessageBox.messageHeader"/>
  <v-container v-show="!showGeolocationError" fluid class="main-section pa-0">
    <HeaderItem headerTitle="מסלול עבודה יומי" homeLink="/EmployeeHome" hideSignout></HeaderItem>
    <v-row class="contents-row ma-0 px-3">
        <v-text-field
            class="station-search mt-9"
            v-model="search"
            placeholder="חפש לקוח/כתובת/טלפון"
            prepend-inner-icon="mdi-magnify"
            variant="outlined"
            density="comfortable"
            hide-details
            single-line>
        </v-text-field>
        <div class="stations-container mt-3 pa-2" v-show="!noAvailableStations" variant="outlined">
            <StationCard
            v-for="(task, index) in filteredTasks"
            class="mb-6"
            :key="index"
            :task="task"
            :stationNumber="index + 1"/>
        </div>
        <div class="no-available-stations mt-3 pa-2" v-show="noAvailableStations" variant="outlined">
          <v-icon icon="mdi-alert-circle" size="150"></v-icon>
          <h3>לא נמצאו תחנות עבודה להיום</h3>
        </div>
    </v-row>
    <v-snackbar class="optimal-trip-snackbar" v-model="optimalTripFailed">לא יכולנו למצוא מסלול עבודה אופטימלי בשבילך.</v-snackbar>
  </v-container>
</template>

<style scoped>
.station-search
{
    flex-grow: 0;
}

.stations-container, .no-available-stations
{
    display: flex;
    flex-direction: column;
    max-height: 65dvh;
    align-items: center;
    flex-grow: 1;
    overflow-y: scroll;
    -webkit-overflow-scrolling: touch;
}

.no-available-stations
{
  justify-content: center;
  color: #bdbdbd;
}
</style>
<style>
.optimal-trip-snackbar
{
  bottom: 5dvh;
}

.optimal-trip-snackbar .v-snackbar__content
{
  text-align: center;
}
</style>

<script>
import API from '@/api/api.js';

let api = new API();

export default {
  name: 'DailyWorkTrip',
  rtl: true,
  data: () => ({
      dailyTasks: [],
      search: '',
      userLat: '',
      userLong: '',
      userGeolocationError: '',
      showGeolocationError: false,
      optimalTripFailed: false,
      noAvailableStations: false,
      geolocationErrorMessageBox: 
     {
          messageTitle: "שגיאה",
          messageIcon: "mdi-close-circle",
          iconColor: "#E04F5F",
          messageHeader: "",
          cancelText: "חזור",
          submitText: "נסה שוב"
        },
      today: new Date()
    }),
  methods: 
  {
    async getEmployeeOpenTasks() 
    {
        try {
          let token = localStorage.getItem('LOCAL_STORAGE_TOKEN_KEY');
          let response = await api.get('/dailyEmployeeOpenTasks', { "token": token, "apt_date": this.todayFormatted, "lat": this.userLat, "long": this.userLong });
          this.dailyTasks = response.data;

          if(!this.dailyTasks || this.dailyTasks.length == 0)
          {
            this.noAvailableStations = true;
          }
          else
          {
            this.noAvailableStations = false;
          }
        } 
        catch (error) 
        {
          console.error('Error:', error);
        }
    },
    formatDate(date_input) 
    {
      if (!date_input) return '';
      const date = new Date(date_input);
      const day = String(date.getDate()).padStart(2, '0');
      const month = String(date.getMonth() + 1).padStart(2, '0'); // Months are zero-based
      const year = date.getFullYear();
      return `${year}-${month}-${day}`;
    },
    getLocation() 
    {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                this.handleSuccess,
                this.handleError
            );
        } 
        else {
            this.userGeolocationError = "שירותי המיקום אינם נתמכים בדפדפן זה.";
            this.checkGeolocationError();
        }
    },
    async handleSuccess(position) 
    {
        this.userLat = position.coords.latitude.toFixed(6);
        this.userLong = position.coords.longitude.toFixed(6);
        this.userGeolocationError = '';
        await this.checkGeolocationError();
    },
    async handleError(error) 
    {
        switch(error.code) 
        {
            case error.PERMISSION_DENIED:
                this.userGeolocationError = "יש להפעיל את שירותי המיקום במכשיר שלך כדי לגשת לדף זה.";
                break;
            case error.POSITION_UNAVAILABLE:
                this.userGeolocationError = "לא ניתן לקבל מידע עבור המיקום שבו אתה נמצא.";
                break;
            case error.UNKNOWN_ERROR:
                this.userGeolocationError = "אירעה שגיאה בלתי צפויה.";
                break;
        }
        await this.checkGeolocationError();
    },
    async checkGeolocationError()
    {
        if(this.userGeolocationError !== '')
        {
            this.geolocationErrorMessageBox.messageHeader = this.userGeolocationError;
            this.showGeolocationError = true;
        }
        else
        {
            await this.getEmployeeOpenTasks();
        }
    },
    reloadPage()
    {
        this.$router.go(0);
    }
  },
  computed: {
        todayFormatted() {
            return this.formatDate(this.today);
        },
        filteredTasks() {
            if (!this.search) 
            {
                console.log('No search query, returning all tasks.');
                return this.dailyTasks;
            }

            const filtered = this.dailyTasks.filter(task => {
                return (
                    task.client_name.includes(this.search) ||
                    task.client_street.includes(this.search) ||
                    task.client_street_number.includes(this.search) ||
                    task.client_city.includes(this.search) ||
                    task.rep_phone.includes(this.search)
                );
            });

            return filtered;
        }
    },
  async mounted()
  {
    await this.getLocation();
  },
  watch: 
  {
    async userGeolocationError(newVal) {
      if(newVal !== '') {
        this.geolocationErrorMessageBox.messageHeader = newVal;
        this.showGeolocationError = true;
      } 
      else {
        try
        {
          await this.getEmployeeOpenTasks();
        }
        catch(error)
        {
          switch (error.response.status) 
          {
            case 401:
            {
              this.optimalTripFailed = true;
            }
          }
        }
      }
    }
  }
}
</script>
