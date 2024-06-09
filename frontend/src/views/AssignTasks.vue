<script setup>
  import HeaderItem from '../components/HeaderItem.vue'
  import { VDateInput } from 'vuetify/labs/VDateInput'
</script>

<template>
  <v-container fluid class="main-section pa-0">
    <HeaderItem headerTitle="שיבוץ משימות" homeLink="/ClientHome" hideSignout></HeaderItem>
    <v-row class="contents-row ma-0 px-3">
      <div class="work-date-input mt-9">
        <v-date-input
          v-model="selectedDate"
          @update:model-value="getAppointmentsInDate"
          width="100%"
          label="מועד עבודה"
          prepend-icon="mdi-calendar"
          variant="outlined"
          cancel-text="בטל"
          ok-text="בחר"
          :min="minDate"
          density="custom-input-density"
          hide-details>
        </v-date-input>
      </div>
      <h3 class="mt-6">תורים למועד: <span class="font-weight-regular">{{ formattedSelectedDateDisplay }}</span></h3>
      <v-text-field
        class="mt-4"
        v-model="search"
        label="חפש"
        prepend-inner-icon="mdi-magnify"
        variant="outlined"
        density="custom-input-density"
        hide-details
        single-line>
      </v-text-field>
      <v-data-table
        :key="forceRerenderKey"
        class="appointments-table mt-4"
        v-model:page="page"
        v-model="selectedAppointments"
        :headers="headers"
        :items="appointments"
        :search="search"
        item-value="apt_client"
        :items-per-page="itemsPerPage"
        show-select
        return-object>
        <template v-slot:item.client_details="{ item }">
          <div v-html="renderClientDetails(item['client_details'])"></div>
        </template>
        <template v-slot:header.data-table-select>
          <div class="hidden-select-all"></div>
        </template>
        <template #item.data-table-select="{ item, isSelected, toggleSelect }">
          <v-checkbox
            class="appointment-select-row"
            :model-value="isSelected({ value: item })"
            color="red darken-3"
            @update:model-value="toggleSelect({ value: item })"
            hide-details>
          </v-checkbox>
        </template>
        <template v-slot:bottom>
          <div class="appointments-footer text-center pa-2">
            <v-pagination class="appointments-pagination" v-model="page" :length="pageCount" size="30px" total-visible="0"/>
            <v-btn class="ff-btn me-4" variant="flat" rounded="0" v-show="isSelectedAppoinmentsNotEmpty" @click="showEmployeeSelectDialog = true" width="95px">שבץ טכנאי</v-btn>
            <v-btn class="ff-btn" variant="flat" rounded="0" v-show="isSelectedAppoinmentsNotEmpty" @click="cleanAssignments" width="95px">נקה שיבוץ</v-btn>
          </div>
        </template>
      </v-data-table>
    </v-row>
    <v-row class="contents-row ma-0 align-center px-3 py-0 pb-6 flex-0-1">
      <v-btn class="ff-btn" variant="flat" min-width="250px" width="80%" height="55px !important" prepend-icon="mdi-calendar-question-outline" rounded="0" to="/UnassignedTasks">עבור לתורים שטרם שובצו</v-btn>
    </v-row>
    <v-dialog v-model="showEmployeeSelectDialog" fullscreen hide-overlay>
      <v-card>
        <HeaderItem headerTitle="בחירת טכנאי" hideSignout hideBack hideHome hidePlaceholder></HeaderItem>
        <v-card-text class="employee-select-content">
          <div class="employee-select-input mt-9">
            <v-autocomplete
              v-model="selectedEmployee"
              :items="employees"
              item-title="emp_fullname"
              density="comfortable"
              variant="outlined"
              label="טכנאי"
              :custom-filter="customEmployeesFilter"
              chips
              return-object
              hide-details>
              <template v-slot:item="{ item, props }">
                <v-list-item v-bind="props">
                  <v-list-item-title>{{ item.emp_fullname }}</v-list-item-title>
                  <v-list-item-subtitle>{{ item.raw.emp_ID }}</v-list-item-subtitle>
                </v-list-item>
              </template>
            </v-autocomplete>
          </div>
          <div class="buttons-container mt-6">
            <v-btn class="ff-outlined-btn mx-3" variant="flat" width="145px" @click="cancelEmployeeSelection" rounded="0">בטל</v-btn>
            <v-btn class="ff-btn mx-3" variant="outlined" width="145px" @click="updateSelectedAppointments" rounded="0">אשר</v-btn>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import API from '@/api/api.js';

let api = new API();
let token = localStorage.getItem('LOCAL_STORAGE_TOKEN_KEY');

export default {
  name: 'AssignTasks',
  rtl: true,
  data: () => ({
    selectedDate: new Date(),
    search: '',
    page: 1,
    itemsPerPage: 5,
    headers: [
      { title: 'פרטי הלקוח', value: 'client_details', width: '70%' },
      { title: 'טכנאי מבצע', value: 'emp_fullname', width: '30%' },
    ],
    appointments: [],
    selectedAppointments: [],
    employees: [],
    showEmployeeSelectDialog: false,
    forceRerenderKey: 0,
    selectedEmployee: null,
  }),
  async mounted() {
    await this.getAppointmentsInDate();
    await this.getAllEmployees();
  },
  methods: {
    async getAppointmentsInDate() {
      try {
        let response = await api.get('/appointmentsInDate', { "date": this.formattedSelectedDate });
        this.appointments = response.data.map(appointment => ({
          ...appointment,
          "emp_fullname": `${appointment['emp_firstname'] || ''} ${appointment['emp_lastname'] || ''}`,
          "client_details": `
            <p class="client-col-details">לקוח: <span>${appointment['client_name'] || ''}</span></p>
            <p class="client-col-details">כתובת: <span>${appointment['client_street'] || ''} ${appointment['client_street_number'] || ''}, ${appointment['client_city'] || ''}</span></p>`
        }));
        this.selectedAppointments = [];
        this.forceRerenderKey++;
      } 
      catch (error) {
        console.error('Error:', error);
      }
    },
    async updateSelectedAppointmentsInDB(appointments)
    {
      try {
        let response = await api.put('/assignExecutiveEmployee', { "appointments": appointments });
        this.forceRerenderKey++;
        console.log(response.data);
      } 
      catch (error) {
        console.error('Error:', error);
      }
    },
    renderClientDetails(details) {
      return details;
    },
    async getAllEmployees() {
      try {
        let response = await api.get('/allEmployees');
        this.employees = response.data.map(employee => ({
          ...employee,
          "emp_fullname": `${employee.emp_firstname} ${employee.emp_lastname}`
        }));
        this.forceRerenderKey++;
      } 
      catch (error) 
      {
        console.error('Error:', error);
      }
    },
    customEmployeesFilter(itemText, queryText, item) {
      const empFullName = item.raw.emp_fullname.toLowerCase();
      const empID = item.raw.emp_ID.toLowerCase();
      const query = queryText.toLowerCase();
      return empFullName.includes(query) || empID.includes(query);
    },
    cancelEmployeeSelection() {
      this.selectedEmployee = null;
      this.showEmployeeSelectDialog = false;
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
    async updateSelectedAppointments() {
      if (this.selectedEmployee)
      {
        this.selectedAppointments.forEach(appointment => {
          appointment.emp_firstname = this.selectedEmployee.emp_firstname;
          appointment.emp_lastname = this.selectedEmployee.emp_lastname;
          appointment.apt_emp_executive = this.selectedEmployee.emp_ID;
          appointment.emp_fullname = this.selectedEmployee.emp_fullname;
        });

        const duplicateAppointments = this.selectedAppointments.map(appointment => {
          return {
            "apt_client": appointment.apt_client,
            "apt_date": this.formatDate(appointment.apt_date),
            "apt_emp_executive": appointment.apt_emp_executive
          };
        });

        console.log(this.selectedAppointments);
        await this.updateSelectedAppointmentsInDB(duplicateAppointments);
        await this.getAppointmentsInDate();
      }
      
      this.selectedAppointments = [];
      this.cancelEmployeeSelection();
  },
  async cleanAssignments() {
        const duplicateAppointments = this.selectedAppointments.map(appointment => {
          return {
            "apt_client": appointment.apt_client,
            "apt_date": this.formatDate(appointment.apt_date),
            "apt_emp_executive": null
          };
        });

        console.log(this.selectedAppointments);
        await this.updateSelectedAppointmentsInDB(duplicateAppointments);
        await this.getAppointmentsInDate();
        this.selectedAppointments = [];
  }
},
  computed: {
    minDate() {
      const today = new Date();
      const year = today.getFullYear();
      const month = String(today.getMonth() + 1).padStart(2, '0');
      const day = String(today.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    },
    formattedSelectedDateDisplay() {
      if (!this.selectedDate) return '';
      const date = new Date(this.selectedDate);
      const day = String(date.getDate()).padStart(2, '0');
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const year = date.getFullYear();
      const weekday = new Intl.DateTimeFormat('he-IL', { weekday: 'short' }).format(date);
      return `${day}/${month}/${year}, ${weekday}`;
    },
    formattedSelectedDate() {
      if (!this.selectedDate) return '';
      const date = new Date(this.selectedDate);
      const day = String(date.getDate()).padStart(2, '0');
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const year = date.getFullYear();
      return `${year}-${month}-${day}`;
    },
    pageCount() {
      return Math.ceil(this.appointments.length / this.itemsPerPage);
    },
    isSelectedAppoinmentsNotEmpty()
    {
      return this.selectedAppointments.length > 0
    }
  },
}
</script>

<style scoped>
.v-input {
  flex-grow: 0;
}

.work-date-input {
  width: 85%;
  max-width: 400px;
  align-self: center;
}

.appointments-table {
  border-radius: 10px !important;
  border: 1px solid #bdbdbd !important;
  min-height: 400px;
}

.appointments-table th {
  font-weight: bold !important;
}

.appointments-table .v-selection-control {
  width: 25px !important;
}

.appointments-footer {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}

.employee-select-content {
  display: flex;
  flex-wrap: wrap;
  flex-direction: column;
  align-items: center;
  padding-top: 50px !important;
}

.buttons-container
{
    display: flex;
    width: 100%;
    justify-content: center;
}

.employee-select-input
{
  flex: 1;
  width: 100%;
  max-width: 500px;
}
</style>

<style>
.v-table > .v-table__wrapper > table > tbody > tr > td,
.v-table > .v-table__wrapper > table > tbody > tr > th,
.v-table > .v-table__wrapper > table > thead > tr > td,
.v-table > .v-table__wrapper > table > thead > tr > th,
.v-table > .v-table__wrapper > table > tfoot > tr > td,
.v-table > .v-table__wrapper > table > tfoot > tr > th {
  padding: 0 4px !important;
}

.v-table th {
  font-weight: 900 !important;
  --v-table-header-height: 40px;
}

.v-data-table-rows-no-data
{
  color: #bdbdbd;
  font-size: 18px;
  font-weight: 500;
}

.client-col-details {
  font-size: 14px;
  font-weight: bold;
}

.client-col-details span {
  font-weight: normal;
}

.appointments-pagination {
  flex: 1;
}

.hidden-select-all 
{
  width: 40px;
}

.appointment-select-row
{
  width:25px;
}
</style>
