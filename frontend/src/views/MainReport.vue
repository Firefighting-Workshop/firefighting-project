<script setup>
  import HeaderItem from '../components/HeaderItem.vue'
  import MessageBox from '../components/MessageBox.vue'
</script>
<template>
  <MessageBox v-key="forceRerenderKey" v-bind="sendReportMessageBox" :cancelFunction="cancelSendReport" :submitFunction="submitSendReport" v-show="toggleSendReportDialog"></MessageBox>
  <v-container v-show="!toggleSendReportDialog" v-key="forceRerenderKey" fluid class="main-section pa-0">
    <HeaderItem headerTitle="מילוי דיווח תחזוקה" homeLink="/EmployeeHome" hideSignout></HeaderItem>
    <v-row class="contents-row ma-0 px-3">
      <v-card class="ff-card mt-9 pa-2" variant="outlined">
        <p class="ff-card-property mb-2">לקוח: <span>{{client.client_name}}</span></p>
        <p class="ff-card-property">כתובת: <span>{{client.client_street}} {{client.client_street_number}}, {{client.client_city}}</span></p>
      </v-card>
      <div class="actions-container" v-show="!reportedEquipmentNotChosen">
        <h3 class="mt-6">מה ברצונך לבצע?</h3>
        <v-btn class="ff-main-button action-btn mt-3" variant="flat" prepend-icon="mdi-fire-extinguisher" to="/EquipmentReport" rounded="0">דיווח תחזוקת ציוד</v-btn>
        <v-btn class="ff-main-button action-btn mt-2" variant="flat" prepend-icon="mdi-fireplace" rounded="0" to="/CabinetReport">דיווח תחזוקת עמדות</v-btn>
        <v-btn class="ff-main-button action-btn mt-2" variant="flat" prepend-icon="mdi-file-document-check-outline" @click="toggleSendReportDialog = true" rounded="0">שליחת דוח תחזוקה</v-btn>
      </div>
    </v-row>
  </v-container>
</template>
<style scoped>
.actions-container
{
  display: flex;
  flex-direction: column;
  flex-wrap: wrap;
  flex: 1;
}

.action-btn
{
  align-self: center;
  justify-content: flex-start;
}
</style>
<script>
import API from '@/api/api.js';

let api = new API();

export default {
  name: 'MainReport',
  rtl: true,
  data: () => ({
      client: {},
      today: new Date(),
      toggleSendReportDialog: false,
      enforceRerenderkey: 0,
      sendReportMessageBox: 
        {
          messageTitle: "שליחת דוח תחזוקה",
          messageIcon: "mdi-alert-circle",
          iconColor: "#FFC048",
          messageHeader: "האם אתה בטוח שברצונך לשלוח את דוח התחזוקה?",
          messageDetails: "הדוח לא יהיה ניתן יותר לעריכה.",
          cancelText: "לא",
          submitText: "כן"
        }
  }),
  methods:
  {
    async getClientData(client_id) 
    {
      try 
      {
        let token = localStorage.getItem('LOCAL_STORAGE_TOKEN_KEY');
        let response = await api.get('/clientData', {"token": token, "client_id": client_id });
        this.client = response.data;
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
    cancelSendReport()
    {
      this.toggleSendReportDialog = false;
      this.enforceRerenderkey++;
    },
    async submitSendReport()
    {
      try
      {
        let token = localStorage.getItem('LOCAL_STORAGE_TOKEN_KEY');
        await api.put('/closeAppointment', {"token": token, "date": this.todayFormatted, "client_id" : this.client.client_id});
        this.$router.push('/EmployeeHome');
      }
      catch(error)
      {
        console.log(error);
      }
    }
  },
  computed:
  {
    todayFormatted()
    {
      return this.formatDate(this.today);
    }
  },
  async mounted()
  {
    let reportedClient = localStorage.getItem("CLIENT_ON_REPORT");
    await this.getClientData(reportedClient);
  }
}
</script>