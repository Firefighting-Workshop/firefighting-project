<script setup>
  import HeaderItem from '../components/HeaderItem.vue'
  import EditEquipment from '../components/EditEquipment.vue'
  import MaintenanceOps from '../components/MaintenanceOps.vue'
  import EquipmentFix from '../components/EquipmentFix.vue'
  import FutureTreatment from '../components/FutureTreatment.vue'
  import EquipmentRemarks from '../components/EquipmentRemarks.vue'
  import AddEquipment from '../components/AddEquipment.vue'
</script>
<template>
  <v-container fluid class="main-section pa-0">
    <HeaderItem headerTitle="דיווח תחזוקת ציוד" homeLink="/EmployeeHome" hideSignout></HeaderItem>
    <v-row class="contents-row ma-0 px-3">
      <v-card class="ff-card mt-9 pa-2" variant="outlined">
        <p class="ff-card-property mb-2">לקוח: <span>{{client.client_name}}</span></p>
        <p class="ff-card-property">כתובת: <span>{{client.client_street}} {{client.client_street_number}}, {{client.client_city}}</span></p>
      </v-card>
      <v-card class="ff-card mt-2 pa-2" variant="outlined">
        <p class="ff-card-property">ציוד מדווח:</p>
        <p>{{ currentReportedEquipmentDetails }}</p>
        <div class="d-flex justify-center mt-4">
           <v-btn class="ff-btn mx-2" variant="flat" rounded="0" height="35px !important" width="100px" @click="showEquipmentSelectDialog = true">בחר ציוד</v-btn>
           <v-btn class="ff-btn mx-2" variant="flat" rounded="0" height="35px !important" width="100px" @click="showAddEquipmentDialog">הוסף ציוד</v-btn>
        </div>
      </v-card>
      <v-alert
        v-show="isRequiredPressureTest"
        class="equipment-warning mt-2"
        density="compact"
        text="מטפה זה לא עבר בדיקת לחץ מזה 6 שנים ומעלה. לפי הרגולציה, הוא שוב נדרש לבדיקה."
        type="warning"
      ></v-alert>
      <div class="actions-container" v-show="!reportedEquipmentNotChosen">
        <h3 class="mt-6">מה ברצונך לבצע?</h3>
        <v-btn class="ff-btn action-btn mt-3" variant="flat" prepend-icon="mdi-square-edit-outline" @click="showEquipmentEditDialog" rounded="0">עריכת פרטי ציוד</v-btn>
        <v-btn class="ff-btn action-btn mt-2" variant="flat" prepend-icon="mdi-tools" rounded="0" @click="showMeintenanceOpsDialog">דיווח פעולות תחזוקה</v-btn>
        <v-btn class="ff-btn action-btn mt-2" variant="flat" prepend-icon="mdi-wrench-cog-outline" @click="showEquipmentFixDialog" rounded="0">דיווח על תיקון</v-btn>
        <v-btn class="ff-btn action-btn mt-2" variant="flat" prepend-icon="mdi-wrench-clock" @click="showFutureTreatmentDialog" rounded="0">דיווח על טיפול עתידי נדרש</v-btn>
        <v-btn class="ff-btn action-btn mt-2" variant="flat" prepend-icon="mdi-text-box-edit-outline" @click="showEquipmentRemarksDialog" rounded="0">רישום הערות</v-btn>
        <v-btn class="ff-btn action-btn mt-2" v-show="isCurrentEquipBelongsToCabinet" variant="flat" @click="moveToBelongsCabinet" prepend-icon="mdi-fireplace" rounded="0">עבור לדיווח עמדה שייכת</v-btn>
      </div>
      <div class="equipment_not_chosen" v-show="reportedEquipmentNotChosen">
        <v-icon icon="mdi-alert-circle" size="150"></v-icon>
        <h3 class="mt-3">יש לבחור ציוד לדיווח</h3>
      </div>
    </v-row>

    <v-dialog v-model="showEquipmentSelectDialog" fullscreen hide-overlay>
      <v-card>
        <HeaderItem headerTitle="בחירת ציוד לדיווח" hideSignout hideBack hideHome hidePlaceholder></HeaderItem>
        <v-card-text class="dialog-card-content">
          <div class="select-input mt-9">
            <v-autocomplete
              v-model="selectedReportedEquipment"
              :items="reportedEquipments"
              item-title="reqp_id"
              density="comfortable"
              variant="outlined"
              label="ציוד מדווח"
              placeholder="הזן את מספר הזיהוי או את שם הציוד"
              :custom-filter="customReportedEquipmentsFilter"
              chips
              return-object
              hide-details>
              <template v-slot:item="{ item, props }">
                <v-list-item v-bind="props">
                  <v-list-item-subtitle>שם: {{ item.raw.eqp_name }}</v-list-item-subtitle>
                  <v-list-item-subtitle>סוג: {{ item.raw.eqp_type }}</v-list-item-subtitle>
                </v-list-item>
              </template>
            </v-autocomplete>
          </div>
          <div class="buttons-container mt-6">
            <v-btn class="ff-outlined-btn mx-3" variant="flat" width="140px" @click="cancelReportedEquipmentSelection" rounded="0">בטל</v-btn>
            <v-btn class="ff-btn mx-3" variant="outlined" width="140px" @click="selectReportedEquipment" rounded="0">אשר</v-btn>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>
    <v-snackbar class="data-saved-snackbar" timeout="2000" color="success" v-model="showDataSavedMessage">פעולתך נקלטה בהצלחה!</v-snackbar>
  </v-container>
  <EditEquipment 
    v-if="showEquipmentEdit"
    :current-reported-equipment="currentReportedEquipment"
    :client="client"
    @close-dialog="showEquipmentEdit = false"
    @submit-form="editReportedEquipment"/>
  <AddEquipment
    v-if="showAddEquipment"
    :reported-equipments="reportedEquipments"
    :client="client"
    @close-dialog="showAddEquipment = false"
    @submit-form="addReportedEquipment"/>
  <MaintenanceOps 
    v-if="showMeintenanceOps"
    :current-reported-equipment="currentReportedEquipment"
    @close-dialog="showMeintenanceOps = false"
    @submit-form="updateMaintenanceOps"/>
  <EquipmentFix 
    v-if="showEquipmentFix"
    :current-reported-equipment="currentReportedEquipment"
    @close-dialog="showEquipmentFix = false"
    @submit-form="updateEquipmentFix"/>
  <FutureTreatment
    v-if="showFutureTreatment"
    :current-reported-equipment="currentReportedEquipment"
    @close-dialog="showFutureTreatment = false"
    @submit-form="updateFutureTreatment"/>
  <EquipmentRemarks 
    v-if="showEquipmentRemarks"
    :current-reported-equipment="currentReportedEquipment"
    @close-dialog="showEquipmentRemarks = false"
    @submit-form="updateEquipmentRemarks"/>
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

.actions-container, .equipment_not_chosen
{
  display: flex;
  flex-direction: column;
  flex-wrap: wrap;
  flex: 1;
}

.equipment_not_chosen
{
  justify-content: center;
  align-items: center;
  color: #bdbdbd;
}

.equipment-warning
{
  flex-grow: 0;
}
</style>
<style>
.data-saved-snackbar
{
  bottom: 5dvh;
}

.data-saved-snackbar .v-snackbar__content
{
  text-align: center;
}
</style>
<script>
import API from '@/api/api.js';

let api = new API();

export default {
  name: 'EquipmentReport',
  rtl: true,
  data: () => ({
      client: {},
      reportedEquipments: [],
      selectedReportedEquipment: null,
      currentReportedEquipment: null,
      showEquipmentSelectDialog: false,
      showEquipmentEdit: false,
      showMeintenanceOps: false,
      showAddEquipment: false,
      showEquipmentFix: false,
      showFutureTreatment: false,
      showEquipmentRemarks: false,
      reportedEquipmentNotChosen: true,
      currentReportedEquipmentDetails: 'טרם נבחר',
      isCurrentEquipBelongsToCabinet: false,
      isRequiredPressureTest: false,
      showDataSavedMessage: false,
      today: new Date(),
      forceRerenderKey: 0,
    }),
  methods: 
  {
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
    async getAllReportedEquipments() {
      try {
        let token = localStorage.getItem('LOCAL_STORAGE_TOKEN_KEY');
        let lastReportedEquipmentId = localStorage.getItem('LAST_EQUIPMENT_ID');
        let response = await api.get('/allEquipmentReportsInDate', {"token": token, "date": this.todayFormatted, "client_id": this.client.client_id });
        this.reportedEquipments = response.data;
        this.isRequiredPressureTest = false;

        if (this.reportedEquipments)
        {
          if(lastReportedEquipmentId)
          {
            localStorage.removeItem('LAST_EQUIPMENT_ID');
            this.currentReportedEquipment = this.reportedEquipments.find(equipment => equipment.reqp_id == lastReportedEquipmentId);
          }
          else if(this.currentReportedEquipment)
          {
            this.currentReportedEquipment = this.reportedEquipments.find(equipment => equipment.reqp_id == this.currentReportedEquipment.reqp_id);
          }
          else
          {
            return;
          }

          this.selectedReportedEquipment = this.currentReportedEquipment;
          this.currentReportedEquipmentDetails = this.currentReportedEquipment.reqp_id + " - " + this.currentReportedEquipment.eqp_name;
          this.reportedEquipmentNotChosen = false;

          if(!this.currentReportedEquipment.reqp_belongs_cabinet || this.currentReportedEquipment.reqp_belongs_cabinet == 0)
          {
            this.isCurrentEquipBelongsToCabinet = false;
          }
          else
          {
            this.isCurrentEquipBelongsToCabinet = true;
          }

          if(this.currentReportedEquipment.reqp_pressure_test_year)
          {
            let lastPressureTestDiff = this.today.getFullYear() - this.currentReportedEquipment.reqp_pressure_test_year;
            console.log(this.today.getFullYear() + " - " + this.currentReportedEquipment.reqp_pressure_test_year);

            if(this.currentReportedEquipment.eqp_type == 'מטפה' && lastPressureTestDiff >= 6)
            {
              this.isRequiredPressureTest = true;
            }
          }
        }
      } 
      catch (error) 
      {
        console.error('Error:', error);
      }
    },
    showEquipmentEditDialog()
    {
      this.showEquipmentEdit = true;
    },
    showMeintenanceOpsDialog()
    {
      this.showMeintenanceOps = true;
    },
    showAddEquipmentDialog()
    {
      this.showAddEquipment = true;
    },
    showEquipmentFixDialog()
    {
      this.showEquipmentFix = true;
    },
    showFutureTreatmentDialog()
    {
      this.showFutureTreatment = true;
    },
    showEquipmentRemarksDialog()
    {
      this.showEquipmentRemarks = true;
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
    customReportedEquipmentsFilter(itemText, queryText, item) 
    {
      const reqpID = item.raw.reqp_id.toLowerCase();
      const eqpName = item.raw.eqp_name.toLowerCase();
      const eqpType = item.raw.eqp_type.toLowerCase();
      const query = queryText.toLowerCase();
      return reqpID.includes(query) || eqpName.includes(query) || eqpType.includes(query);
    },
    cancelReportedEquipmentSelection() 
    {
      this.selectedReportedEquipment = this.currentReportedEquipment;
      this.showEquipmentSelectDialog = false;
    },
    selectReportedEquipment()
    {
      this.currentReportedEquipment = this.selectedReportedEquipment;
      console.log(this.currentReportedEquipment)

      if(this.currentReportedEquipment)
      {
        this.currentReportedEquipmentDetails = this.currentReportedEquipment.reqp_id + " - " + this.currentReportedEquipment.eqp_name;
        this.reportedEquipmentNotChosen = false;

        if(!this.currentReportedEquipment.reqp_belongs_cabinet || this.currentReportedEquipment.reqp_belongs_cabinet == 0)
        {
          this.isCurrentEquipBelongsToCabinet = false;
        }
        else
        {
          this.isCurrentEquipBelongsToCabinet = true;
        }

        if(this.currentReportedEquipment.reqp_pressure_test_year)
        {
          let lastPressureTestDiff = this.today.getFullYear() - this.currentReportedEquipment.reqp_pressure_test_year;

          if(this.currentReportedEquipment.eqp_type == 'מטפה' && lastPressureTestDiff >= 6)
          {
            this.isRequiredPressureTest = true;
          }
        }
      }
      else
      {
        this.currentReportedEquipmentDetails = 'טרם נבחר';
        this.reportedEquipmentNotChosen = true;
        this.isRequiredPressureTest = false;
      }

      this.showEquipmentSelectDialog = false;
    },
    async addReportedEquipment(newEquipment)
    {
      this.showAddEquipment = false;

      try
      {
        let token = localStorage.getItem('LOCAL_STORAGE_TOKEN_KEY');
        await api.post('/addReportedEquipment', {"token": token, "new_reported_equipment" : newEquipment });
        await this.getAllReportedEquipments();
        this.showDataSavedMessage = true;
      }
      catch(error)
      {
        console.error('Error:', error);
      }
    },
    async editReportedEquipment(updatedEquipment) 
    {
      this.showEquipmentEdit = false;
      updatedEquipment.reqp_date = this.formatDate(updatedEquipment.reqp_date);

      try
      {
        let token = localStorage.getItem('LOCAL_STORAGE_TOKEN_KEY');
        await api.put('/updateReportedEquipment', {"token": token, "updated_reported_equipment" : updatedEquipment });
        await this.getAllReportedEquipments();
        this.showDataSavedMessage = true;
      }
      catch(error)
      {
        console.error('Error:', error);
      }
    },
    async updateMaintenanceOps(updatedEquipment) 
    {
      this.showMeintenanceOps = false;
      updatedEquipment.reqp_date = this.formatDate(updatedEquipment.reqp_date);

      try
      {
        let token = localStorage.getItem('LOCAL_STORAGE_TOKEN_KEY');
        await api.put('/updateReportedEquipment', {"token": token, "updated_reported_equipment" : updatedEquipment });
        await this.getAllReportedEquipments();
        this.showDataSavedMessage = true;
      }
      catch(error)
      {
        console.error('Error:', error);
      }
    },
    async updateEquipmentFix(updatedEquipment) 
    {
      this.showEquipmentFix = false;
      updatedEquipment.reqp_date = this.formatDate(updatedEquipment.reqp_date);

      try
      {
        let token = localStorage.getItem('LOCAL_STORAGE_TOKEN_KEY');
        await api.put('/updateReportedEquipment', {"token": token, "updated_reported_equipment" : updatedEquipment });
        await this.getAllReportedEquipments();
        this.showDataSavedMessage = true;
      }
      catch(error)
      {
        console.error('Error:', error);
      }
    },
    async updateFutureTreatment(updatedEquipment) 
    {
      this.showFutureTreatment = false;
      updatedEquipment.reqp_date = this.formatDate(updatedEquipment.reqp_date);

      try
      {
        let token = localStorage.getItem('LOCAL_STORAGE_TOKEN_KEY');
        await api.put('/updateReportedEquipment', {"token": token, "updated_reported_equipment" : updatedEquipment });
        await this.getAllReportedEquipments();
        this.showDataSavedMessage = true;
      }
      catch(error)
      {
        console.error('Error:', error);
      }
    },
    async updateEquipmentRemarks(updatedEquipment) 
    {
      this.showEquipmentRemarks = false;
      updatedEquipment.reqp_date = this.formatDate(updatedEquipment.reqp_date);

      try
      {
        let token = localStorage.getItem('LOCAL_STORAGE_TOKEN_KEY');
        await api.put('/updateReportedEquipment', {"token": token, "updated_reported_equipment" : updatedEquipment });
        await this.getAllReportedEquipments();
        this.showDataSavedMessage = true;
      }
      catch(error)
      {
        console.error('Error:', error);
      }
    },
    moveToBelongsCabinet()
    {
      localStorage.setItem('LAST_EQUIPMENT_ID', this.currentReportedEquipment.reqp_id);
      localStorage.setItem('CABINET_ID', this.currentReportedEquipment.reqp_belongs_cabinet);
      this.$router.push('/CabinetReport');
    }
  },
  async mounted()
  {
      let reportedClient = localStorage.getItem("CLIENT_ON_REPORT");
      await this.getClientData(reportedClient);
      await this.getAllReportedEquipments();
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