<script setup>
  import HeaderItem from '../components/HeaderItem.vue'
</script>
<template>
  <v-container fluid class="main-section pa-0">
    <HeaderItem headerTitle="ראשי" hideHome hideBack></HeaderItem>
    <v-row class="contents-row ma-0 px-3">
      <p class="greeting-title mt-9">שלום <span>{{ employee.emp_firstname }} {{ employee.emp_lastname }}</span>!</p>
      <h3 class="mt-4">במה נוכל לעזור?</h3>
      <v-btn class="ff-main-button mt-6" variant="flat" rounded="0" to="/AssignTasks" prepend-icon="mdi-calendar-multiple-check">שיבוץ משימות</v-btn>
      <v-btn class="ff-main-button mt-3" variant="flat" rounded="0" to="/DailyWorkTrip" prepend-icon="mdi-map-marker-path">מסלול עבודה יומי</v-btn>
      <v-btn class="ff-main-button mt-3" variant="flat" rounded="0" to="/SelectDailyTask" prepend-icon="mdi-file-document-edit-outline">מילוי דיווחי תחזוקה</v-btn>
    </v-row>
  </v-container>
</template>
<style scoped>
.greeting-title
{
  font-weight: bold;
  font-size: 28px;
}
</style>
<script>
import API from '@/api/api.js';
let api = new API();

export default {
  name: 'EmployeeHome',
  rtl: true,
  data: () => ({
      employee: {},
    }),
  methods: {
    
    },
  async mounted()
  {
    try
    {
        let token = localStorage.getItem('LOCAL_STORAGE_TOKEN_KEY');
        let response = await api.get('/employeeData', { "token" : token });
        this.employee = response.data;
    }
    catch(error)
    {
      console.log('Error:', error.response);
    }
  }
}
</script>