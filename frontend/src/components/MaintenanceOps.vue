<script setup>
  import HeaderItem from '../components/HeaderItem.vue'
</script>

<template>
  <v-container fluid class="main-section main-dialog-section pa-0">
    <HeaderItem class="dialog-header" headerTitle="דיווח פעולות תחזוקה" hideSignout hideBack hideHome hidePlaceholder></HeaderItem>
    <v-row class="contents-row ma-0 px-3">
      <v-form class="dialog-form-content" ref="form" v-model="valid" lazy-validation>
        <div class="mt-9 form-input">
            <h3>אילו פעולות ביצעת על ציוד זה?</h3>
            <v-card class="ff-card form-input maintenance_ops mt-3 pa-2" variant="outlined">
                <v-checkbox 
                v-for="op in maintenanceOps"
                v-model="maintenanceOpsSelected"
                :key="op.mop_id"
                :value="op.mop_id"
                :label="op.mop_desc"
                color="red darken-3"
                hide-details
                density="compact"
                ></v-checkbox>
            </v-card>
        </div>
      </v-form>
      <div class="buttons-container mt-9">
        <v-btn class="ff-outlined-btn mx-3" width="140px" variant="flat" rounded="0" @click="closeDialog">בטל</v-btn>
        <v-btn class="ff-btn mx-3" width="140px" variant="flat" rounded="0" @click="submitForm">שמור</v-btn>
      </div>
    </v-row>
  </v-container>
</template>

<script>
import API from '@/api/api.js';
let api = new API();

export default {
  name: 'MaintenanceOps',
  rtl: true,
  props: {
    currentReportedEquipment: {
      type: Object,
      required: true,
    }
  },
  data: () => ({
    dialog: true,
    valid: false,
    today: new Date(),
    formData: {
      reqp_maintenance_ops: ''
    },
    maintenanceOps: [],
    maintenanceOpsSelected: [],
    enforceRerenderKey: 0
  }),
  computed: {
    todayFormatted() {
      return this.formatDate(this.today);
    }
  },
  methods: {
    closeDialog() {
      this.$emit('close-dialog');
    },
    async submitForm() {
      this.formData.reqp_maintenance_ops = this.arrayToString(this.maintenanceOpsSelected);
      this.$emit('submit-form', this.formData);
    },
    async getAllMeintananceOps() {
      try {
        let token = localStorage.getItem('LOCAL_STORAGE_TOKEN_KEY');
        let response = await api.get('/allMeintenanceOps', {"token": token});
        this.maintenanceOps = response.data;
        console.log(this.maintenanceOps);
      } catch (error) {
        console.error('Error:', error);
      }
    },
    formatDate(date_input) {
      if (!date_input) return '';
      const date = new Date(date_input);
      const day = String(date.getDate()).padStart(2, '0');
      const month = String(date.getMonth() + 1).padStart(2, '0'); // Months are zero-based
      const year = date.getFullYear();
      return `${year}-${month}-${day}`;
    },
    stringToArray(str) {
      return str.split(' ').map(Number).filter(Boolean);
    },
    arrayToString(arr) {
      return arr.join(' ');
    }
  },
  async mounted() {
    await this.getAllMeintananceOps();
    this.formData = { ...this.currentReportedEquipment };
    this.maintenanceOpsSelected = this.stringToArray(this.formData.reqp_maintenance_ops);
  }
};
</script>

<style scoped>
.form-input {
  width: 100%;
  max-width: 500px;
  font-size: 14px;
}

.dialog-form-content {
  display: flex;
  flex-direction: column;
  flex-wrap: wrap;
  justify-content: center;
  width: 100%;
  align-items: center;
}

.dialog-header {
  top: 0;
}

.main-dialog-section {
  position: absolute;
  z-index: 200;
  background-color: #fafafa;
}

.buttons-container {
  display: flex;
  flex: 1;
  align-items: flex-end;
  width: 100%;
  justify-content: center;
}

.maintenance_ops
{
    height: 50dvh;
    overflow-y: scroll;
    -webkit-overflow-scrolling: touch; 
}
</style>