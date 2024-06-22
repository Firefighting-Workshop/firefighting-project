<script setup>
  import HeaderItem from '../components/HeaderItem.vue'
  import AddCabinet from '../components/AddCabinet.vue'
  import EditCabinet from '../components/EditCabinet.vue'
  import EquipmentInstallation from '../components/EquipmentInstallation.vue'
  import RollerStandard from '../components/RollerStandard.vue'
  import CabinetFix from '../components/CabinetFix.vue'
  import CabinetRemarks from '../components/CabinetRemarks.vue'
</script>
<template>
  <v-container fluid class="main-section pa-0">
    <HeaderItem headerTitle="דיווח תחזוקת עמדה" homeLink="/EmployeeHome" hideSignout></HeaderItem>
    <v-row class="contents-row ma-0 px-3">
      <v-card class="ff-card mt-9 pa-2" variant="outlined">
        <p class="ff-card-property mb-2">לקוח: <span>{{ client.client_name }}</span></p>
        <p class="ff-card-property">כתובת: <span>{{ client.client_street }} {{ client.client_street_number}}, {{ client.client_city }}</span></p>
      </v-card>
      <v-card class="ff-card mt-2 pa-2" variant="outlined">
        <p class="ff-card-property">עמדה מדווחת:</p>
        <p>{{ currentReportedCabinetDetails }}</p>
        <div class="d-flex justify-center mt-4">
           <v-btn class="ff-btn mx-2" variant="flat" rounded="0" height="35px !important" @click="showCabinetSelectDialog = true" width="100px">בחר עמדה</v-btn>
           <v-btn class="ff-btn mx-2" variant="flat" rounded="0" height="35px !important" @click="showAddCabinetDialog" width="100px">הוסף עמדה</v-btn>
        </div>
      </v-card>
      <div class="actions-container" v-show="!reportedCabinetNotChosen">
        <h3 class="mt-6">מה ברצונך לבצע?</h3>
        <v-btn class="ff-btn action-btn mt-3" variant="flat" prepend-icon="mdi-square-edit-outline" @click="showCabinetEditDialog" rounded="0">עריכת פרטי עמדה</v-btn>
        <v-btn class="ff-btn action-btn mt-2" variant="flat" prepend-icon="mdi-sprinkler-variant" @click="showEquipmentInstallationDialog" rounded="0">דיווח על התקנת ציוד חדש</v-btn>
        <v-btn class="ff-btn action-btn mt-2" variant="flat" prepend-icon="mdi-file-certificate-outline" @click="showRollerStandardDialog" rounded="0">דיווח תקן בדיקת גלגלון</v-btn>
        <v-btn class="ff-btn action-btn mt-2" variant="flat" prepend-icon="mdi-wrench-cog-outline" @click="showCabinetFixDialog" rounded="0">דיווח על תיקון</v-btn>
        <v-btn class="ff-btn action-btn mt-2" variant="flat" prepend-icon="mdi-text-box-edit-outline" @click="showCabinetRemarksDialog" rounded="0">רישום הערות</v-btn>
      </div>
      <div class="cabinet_not_chosen" v-show="reportedCabinetNotChosen">
        <v-icon icon="mdi-alert-circle" size="150"></v-icon>
        <h3 class="mt-3">יש לבחור עמדה לדיווח</h3>
      </div>
    </v-row>

    <v-dialog v-model="showCabinetSelectDialog" fullscreen hide-overlay>
      <v-card>
        <HeaderItem headerTitle="בחירת עמדה לדיווח" hideSignout hideBack hideHome hidePlaceholder></HeaderItem>
        <v-card-text class="dialog-card-content">
          <div class="select-input mt-9">
            <v-autocomplete
              v-model="selectedReportedCabinet"
              :items="reportedCabinets"
              item-title="rcab_location"
              density="comfortable"
              variant="outlined"
              label="עמדה מדווחת"
              placeholder="הזן את מיקום העמדה"
              chips
              return-object
              hide-details>
            </v-autocomplete>
          </div>
          <div class="buttons-container mt-6">
            <v-btn class="ff-outlined-btn mx-3" variant="flat" width="140px" @click="cancelReportedCabinetSelection" rounded="0">בטל</v-btn>
            <v-btn class="ff-btn mx-3" variant="outlined" width="140px" @click="selectReportedCabinet" rounded="0">אשר</v-btn>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-container>
  <AddCabinet 
    v-if="showAddCabinet"
    @close-dialog="showAddCabinet = false"
    @submit-form="addReportedCabinet"/>
  <EditCabinet 
    v-if="showCabinetEdit"
    :current-reported-cabinet="currentReportedCabinet"
    @close-dialog="showCabinetEdit = false"
    @submit-form="editReportedCabinet"/>
  <EquipmentInstallation 
    v-if="showEquipmentInstallation"
    :current-reported-cabinet="currentReportedCabinet"
    @close-dialog="showEquipmentInstallation = false"
    @submit-form="updateEquipmentInstallation"/>
  <RollerStandard 
    v-if="showRollerStandard"
    :current-reported-cabinet="currentReportedCabinet"
    @close-dialog="showRollerStandard = false"
    @submit-form="updateRollerStandard"/>
  <CabinetFix 
    v-if="showCabinetFix"
    :current-reported-cabinet="currentReportedCabinet"
    @close-dialog="showCabinetFix = false"
    @submit-form="updateCabinetFix"/>
  <CabinetRemarks 
    v-if="showCabinetRemarks"
    :current-reported-cabinet="currentReportedCabinet"
    @close-dialog="showCabinetRemarks = false"
    @submit-form="updateCabinetRemarks"/>
</template>
<style scoped>
.action-btn
{
  width: 80%;
  max-width: 400px;
  height: 45px !important;
  align-self: center;
  justify-content: flex-start;
}

.actions-container, .cabinet_not_chosen
{
  display: flex;
  flex-direction: column;
  flex-wrap: wrap;
  flex: 1;
}

.cabinet_not_chosen
{
  justify-content: center;
  align-items: center;
  color: #bdbdbd;
}

.select-input
{
  flex: 1;
  width: 100%;
  max-width: 500px;
}

.buttons-container
{
    display: flex;
    width: 100%;
    justify-content: center;
}
</style>
<script>
import API from '@/api/api.js';

let api = new API();

export default {
  name: 'CabinetReport',
  rtl: true,
  data: () => ({
      client: {},
      reportedCabinets: [],
      selectedReportedCabinet: null,
      currentReportedCabinet: null,
      showCabinetSelectDialog: false,
      showAddCabinet: false,
      showCabinetEdit: false,
      showRollerStandard: false,
      showEquipmentInstallation: false,
      showCabinetFix: false,
      showCabinetRemarks: false,
      reportedCabinetNotChosen: true,
      currentReportedCabinetDetails: 'טרם נבחרה',
      appointmentDate: "",
      today: new Date(),
      forceRerenderKey: 0,
    }),
  methods: {
    async getClientData(client_id) 
    {
        try {
          let token = localStorage.getItem('LOCAL_STORAGE_TOKEN_KEY');
          let response = await api.get('/clientData', {"token": token, "client_id": client_id });
          this.client = response.data;
        } 
        catch (error) 
        {
          console.error('Error:', error);
        }
    },
    async getAllReportedCabinets() 
    {
        try {
          let token = localStorage.getItem('LOCAL_STORAGE_TOKEN_KEY');
          let storedCabinetId = localStorage.getItem('CABINET_ID');
          let response = await api.get('/allCabinetReportsInDate', {"token": token, "date": this.todayFormatted, "client_id": this.client.client_id });
          this.reportedCabinets = response.data;
          console.log(this.reportedCabinets);

          if (this.reportedCabinets)
          {
              if(storedCabinetId)
              {
                localStorage.removeItem('CABINET_ID');
                this.currentReportedCabinet = this.reportedCabinets.find(cabinet => cabinet.rcab_id == storedCabinetId);
              }
              else if(this.currentReportedCabinet)
              {
                this.currentReportedCabinet = this.reportedCabinets.find(cabinet => cabinet.rcab_id == this.currentReportedCabinet.rcab_id);
              }
              else
              {
                return;
              }

              this.selectedReportedCabinet = this.currentReportedCabinet;
              this.currentReportedCabinetDetails = this.currentReportedCabinet.rcab_location;
              this.reportedCabinetNotChosen = false;  
          }

          console.log(this.currentReportedCabinet);
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
    showAddCabinetDialog()
    {
      this.showAddCabinet = true;
    },
    showCabinetEditDialog()
    {
      this.showCabinetEdit = true;
    },
    showEquipmentInstallationDialog()
    {
      this.showEquipmentInstallation = true;
    },
    showRollerStandardDialog()
    {
      this.showRollerStandard = true;
    },
    showCabinetFixDialog()
    {
      this.showCabinetFix = true;
    },
    showCabinetRemarksDialog()
    {
      this.showCabinetRemarks = true;
    },
    cancelReportedCabinetSelection() 
    {
      this.selectedReportedCabinet = this.currentReportedCabinet;
      this.showCabinetSelectDialog = false;
    },
    selectReportedCabinet()
    {
      this.currentReportedCabinet = this.selectedReportedCabinet;
      console.log(this.currentReportedCabinet)

      if(this.currentReportedCabinet)
      {
        this.currentReportedCabinetDetails = this.currentReportedCabinet.rcab_location;
        this.reportedCabinetNotChosen = false;
      }
      else
      {
        this.currentReportedCabinetDetails = 'טרם נבחרה';
        this.reportedCabinetNotChosen = true;
      }

      this.showCabinetSelectDialog = false;
    },
    async addReportedCabinet(newCabinet)
    {
      newCabinet.rcab_date = this.todayFormatted;
      newCabinet.rcab_client = this.client.client_id;
      this.showAddCabinet = false;

      try
      {
        let token = localStorage.getItem('LOCAL_STORAGE_TOKEN_KEY');
        await api.post('/addReportedCabinet', {"token": token, "new_reported_cabinet": newCabinet });
        await this.getAllReportedCabinets();
      }
      catch(error)
      {
        console.error('Error:', error);
      }
    },
    async editReportedCabinet(updatedCabinet) 
    {
      this.showCabinetEdit = false;
      updatedCabinet.rcab_date = this.todayFormatted;

      try
      {
        let token = localStorage.getItem('LOCAL_STORAGE_TOKEN_KEY');
        await api.put('/updateReportedCabinet', {"token": token, "updated_reported_cabinet" : updatedCabinet });
        await this.getAllReportedCabinets();
      }
      catch(error)
      {
        console.error('Error:', error);
      }
    },
    async updateEquipmentInstallation(updatedCabinet) 
    {
      this.showEquipmentInstallation = false;
      updatedCabinet.rcab_date = this.todayFormatted;

      try
      {
        let token = localStorage.getItem('LOCAL_STORAGE_TOKEN_KEY');
        await api.put('/updateReportedCabinet', {"token": token, "updated_reported_cabinet" : updatedCabinet });
        await this.getAllReportedCabinets();
      }
      catch(error)
      {
        console.error('Error:', error);
      }
    },
    async updateRollerStandard(updatedCabinet) 
    {
      this.showRollerStandard = false;
      updatedCabinet.rcab_date = this.todayFormatted;

      try
      {
        let token = localStorage.getItem('LOCAL_STORAGE_TOKEN_KEY');
        await api.put('/updateReportedCabinet', {"token": token, "updated_reported_cabinet" : updatedCabinet });
        await this.getAllReportedCabinets();
      }
      catch(error)
      {
        console.error('Error:', error);
      }
    },
    async updateCabinetFix(updatedCabinet) 
    {
      this.showCabinetFix = false;
      updatedCabinet.rcab_date = this.todayFormatted;

      try
      {
        let token = localStorage.getItem('LOCAL_STORAGE_TOKEN_KEY');
        await api.put('/updateReportedCabinet', {"token": token, "updated_reported_cabinet" : updatedCabinet });
        await this.getAllReportedCabinets();
      }
      catch(error)
      {
        console.error('Error:', error);
      }
    },
    async updateCabinetRemarks(updatedCabinet) 
    {
      this.showCabinetRemarks = false;
      updatedCabinet.rcab_date = this.todayFormatted;

      try
      {
        let token = localStorage.getItem('LOCAL_STORAGE_TOKEN_KEY');
        await api.put('/updateReportedCabinet', {"token": token, "updated_reported_cabinet" : updatedCabinet });
        await this.getAllReportedCabinets();
      }
      catch(error)
      {
        console.error('Error:', error);
      }
    },
  },
  async mounted()
  {
    let reportedClient = localStorage.getItem("CLIENT_ON_REPORT");
    await this.getClientData(reportedClient);
    await this.getAllReportedCabinets();
  },
  computed:
  {
    todayFormatted()
      {
        return this.formatDate(this.today);
      }
  }
}
</script>