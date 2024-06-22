<template>
  <v-card class="station-card pa-0" variant="outlined">
    <h3 class="station-title">תחנה {{ stationNumber }}</h3>
    <div class="pa-2">
      <p class="ff-card-property">לקוח: <span>{{ task.client_name }}</span></p>
      <p class="ff-card-property">כתובת: <span> {{ task.client_street }} {{ task.client_street_number }}, {{ task.client_city }}</span></p>
      <p class="ff-card-property">טלפון נציג: <span><a :href="'tel:' + task.rep_phone">{{ task.rep_phone }}</a></span></p>
      <div class="d-flex justify-center mt-4">
        <v-btn class="ff-btn mx-2" variant="flat" prepend-icon="mdi-file-document-edit-outline" @click="fillMaintenanceReport" rounded="0" height="35px !important">מלא דוח תחזוקה</v-btn>
        <v-btn class="ff-btn mx-2" variant="flat" prepend-icon="mdi-navigation-variant-outline" @click="openWazeLink" rounded="0" height="35px !important">נווט</v-btn>
      </div>
    </div>
  </v-card>
</template>

<script>
import API from '@/api/api.js';

let api = new API();

export default {
  name: 'StationCard',
  rtl: true,
  props: {
    task: {
      type: Object,
      required: true
    },
    stationNumber: {
      type: Number,
      default: 0
    },
  },
  methods: {
    formatDate(date_input) 
    {
      if (!date_input) return '';
      const date = new Date(date_input);
      const day = String(date.getDate()).padStart(2, '0');
      const month = String(date.getMonth() + 1).padStart(2, '0'); // Months are zero-based
      const year = date.getFullYear();
      return `${year}-${month}-${day}`;
    },
    openWazeLink() {
      const lat = this.task.client_lat;
      const long = this.task.client_long;
      const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
      const wazeUrl = `waze://?ll=${lat},${long}&navigate=yes`;
      const fallbackUrl = `https://www.waze.com/ul?ll=${lat},${long}&navigate=yes`;

      if (isMobile) {
        // Create a temporary anchor element to simulate a user click
        const tempLink = document.createElement('a');
        tempLink.href = wazeUrl;
        tempLink.style.display = 'none';
        document.body.appendChild(tempLink);
        
        // Set a timeout to open the fallback URL if Waze does not open
        const fallbackTimeout = setTimeout(() => {
          window.open(fallbackUrl, '_blank');
        }, 1000);

        // Add event listener for visibility change
        const handleVisibilityChange = () => {
          if (document.visibilityState === 'hidden') {
            clearTimeout(fallbackTimeout);
          } else {
            document.removeEventListener('visibilitychange', handleVisibilityChange);
          }
        };
        document.addEventListener('visibilitychange', handleVisibilityChange);

        // Simulate a click on the temporary link to attempt to open Waze
        tempLink.click();
        document.body.removeChild(tempLink);
      } else {
        // For desktop, directly open the web link
        window.open(fallbackUrl, '_blank');
      }
    },
    async fillMaintenanceReport()
    {
      localStorage.setItem("CLIENT_ON_REPORT", this.task.apt_client);
      let today = this.formatDate(new Date());
      try
        {
          let token = localStorage.getItem('LOCAL_STORAGE_TOKEN_KEY');
          await api.post('/makeEquipmentReportsInDate', {"token": token, "date": today, "client_id" : this.task.apt_client })
          await api.post('/makeCabinetReportsInDate', {"token": token, "date": today, "client_id" : this.task.apt_client })
          this.$router.push('/MainReport');
        }
        catch(error)
        {
          console.error('Error:', error);
        }
    }
  }
}
</script>

<style scoped>
.station-card {
  background-color: #ffffff;
  width: 100%;
  border-radius: 10px;
  border-color: #d10019;
  font-size: 14px;
  flex: 0;
  flex-shrink: 0;
}

.station-title {
  text-align: center;
  color: #fafafa;
  font-size: 18px;
  background-color: #d10019;
  padding: 2px 0px;
}
</style>
