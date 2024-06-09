<script setup>
  import HeaderItem from '../components/HeaderItem.vue';
  import { VDateInput } from 'vuetify/labs/VDateInput';
  import { useRouter } from 'vue-router';

  const router = useRouter();
</script>

<template>
  <v-container fluid class="main-section pa-0">
    <HeaderItem headerTitle="תורים שטרם שובצו" homeLink="/ClientHome" hideSignout />
    <v-row class="contents-row ma-0 px-3">
      <div class="work-date-input mt-9">
        <v-date-input
          v-model="selectedDate"
          @update:model-value="getUnassignedAppointmentsInDate"
          width="100%"
          label="מועד עבודה"
          prepend-icon="mdi-calendar"
          variant="outlined"
          cancel-text="בטל"
          ok-text="בחר"
          :min="minDate"
          density="custom-input-density"
          hide-details
        />
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
        single-line
      />
      <v-data-table
        :key="forceRerenderKey"
        class="appointments-table mt-4"
        v-model:page="page"
        v-model="selectedAppointment"
        :headers="headers"
        :items="appointments"
        :search="search"
        item-value="apt_client"
        :items-per-page="itemsPerPage"
        select-strategy="single"
        show-select
        return-object
      >
        <template v-slot:item.client_details="{ item }">
          <div v-html="renderClientDetails(item['client_details'])"></div>
        </template>
        <template v-slot:item.rep_phone_link="{ item }">
          <div v-html="renderClientDetails(item['rep_phone_link'])"></div>
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
            hide-details
          />
        </template>
        <template v-slot:bottom>
          <div class="appointments-footer text-center pa-2">
            <v-pagination class="appointments-pagination" v-model="page" :length="pageCount" size="30px" total-visible="0" />
            <v-btn
              class="ff-btn"
              variant="flat"
              rounded="0"
              v-show="isSelectedAppointmentNotEmpty"
              @click="showDateSelectDialog = true"
              width="95px"
            >
              שנה מועד
            </v-btn>
          </div>
        </template>
      </v-data-table>
    </v-row>
    <v-row class="contents-row ma-0 align-center px-3 py-0 pb-6 flex-0-1">
      <v-btn class="ff-btn" variant="flat" min-width="250px" width="80%" height="55px !important" prepend-icon="mdi-calendar-multiple-check" rounded="0" @click="router.go(-1)">חזור לשיבוץ משימות</v-btn>
    </v-row>
    <v-dialog v-model="showDateSelectDialog" fullscreen hide-overlay>
      <v-card>
        <HeaderItem headerTitle="שינוי מועד תור" hideSignout hideBack hideHome hidePlaceholder />
        <v-card-text class="date-select-content">
          <div class="alternative-date-input mt-9">
            <v-date-input
              v-model="selectedAlternativeDate"
              width="100%"
              label="מועד חלופי"
              prepend-icon="mdi-calendar"
              variant="outlined"
              cancel-text="בטל"
              ok-text="בחר"
              :min="minDate"
              density="custom-input-density"
              hide-details
            />
            <p class="error-details text-red text-center mt-4">{{ dateNotSelectedErrorMsg }}</p>
          </div>
          <div class="buttons-container mt-6">
            <v-btn class="ff-outlined-btn mx-3" variant="flat" width="145px" @click="cancelAlternativeDateSelection" rounded="0">
              בטל
            </v-btn>
            <v-btn class="ff-btn mx-3" variant="outlined" width="145px" @click="updateSelectedAppointments" rounded="0">
              אשר
            </v-btn>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import API from '@/api/api.js';

const api = new API();
const token = localStorage.getItem('LOCAL_STORAGE_TOKEN_KEY');

export default {
  name: 'UnssignedTasks',
  rtl: true,
  data: () => ({
    selectedDate: new Date(),
    search: '',
    page: 1,
    itemsPerPage: 5,
    headers: [
      { title: 'פרטי הלקוח', value: 'client_details', width: '70%' },
      { title: 'טלפון הנציג', value: 'rep_phone_link', width: '30%' },
    ],
    appointments: [],
    selectedAppointment: [],
    showDateSelectDialog: false,
    forceRerenderKey: 0,
    selectedAlternativeDate: null,
    dateNotSelectedErrorMsg: ''
  }),
  async mounted() {
    await this.getUnassignedAppointmentsInDate();
  },
  methods: {
    async getUnassignedAppointmentsInDate() {
      try {
        const response = await api.get('/unassignedAppointmentsInDate', { date: this.formattedSelectedDate });
        this.appointments = response.data.map(appointment => ({
          ...appointment,
          rep_phone_link: `<a href="tel:${appointment.rep_phone}">${appointment.rep_phone}</a>`,
          client_details: `
            <p class="client-col-details">לקוח: <span>${appointment.client_name || ''}</span></p>
            <p class="client-col-details">כתובת: <span>${appointment.client_street || ''} ${appointment.client_street_number || ''}, ${appointment.client_city || ''}</span></p>`
        }));
        this.selectedAppointment = [];
        this.forceRerenderKey++;
      } catch (error) {
        console.error('Error:', error);
      }
    },
    async changeSelectedAppointmentDateInDB() {
      const formatedAptDate = this.formatDate(this.selectedAppointment[0].apt_date);
      try {
        await api.put('/changeClientAppointment', {
          apt_client: this.selectedAppointment[0].apt_client,
          apt_date: formatedAptDate,
          new_apt_date: this.formattedSelectedAlternativeDate
        });
      } catch (error) {
        console.error('Error:', error);
      }
    },
    renderClientDetails(details) {
      return details;
    },
    cancelAlternativeDateSelection() {
      this.selectedAlternativeDate = null;
      this.showDateSelectDialog = false;
    },
    formatDate(dateInput) {
      if (!dateInput) return '';
      const date = new Date(dateInput);
      const day = String(date.getDate()).padStart(2, '0');
      const month = String(date.getMonth() + 1).padStart(2, '0'); // Months are zero-based
      const year = date.getFullYear();
      return `${year}-${month}-${day}`;
    },
    async updateSelectedAppointments() {
      if (!this.selectedAlternativeDate) {
        this.dateNotSelectedErrorMsg = 'יש לבחור תאריך';
      } else {
        await this.changeSelectedAppointmentDateInDB();
        await this.getUnassignedAppointmentsInDate();
        this.cancelAlternativeDateSelection();
      }
    }
  },
  computed: {
    minDate() {
      const today = new Date();
      return this.formatDate(today);
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
      return this.formatDate(this.selectedDate);
    },
    formattedSelectedAlternativeDate() {
      return this.formatDate(this.selectedAlternativeDate);
    },
    pageCount() {
      return Math.ceil(this.appointments.length / this.itemsPerPage);
    },
    isSelectedAppointmentNotEmpty() {
      return this.selectedAppointment.length > 0;
    }
  },
}
</script>

<style scoped>
.v-input {
  flex-grow: 0;
}

.work-date-input,
.alternative-date-input {
  width: 85%;
  max-width: 400px;
  align-self: center;
}

.alternative-date-input {
  flex: 1;
}

.appointments-table {
  border-radius: 10px !important;
  border: 1px solid #bdbdbd !important;
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

.date-select-content {
  display: flex;
  flex-wrap: wrap;
  flex-direction: column;
  align-items: center;
  padding-top: 50px !important;
}

.buttons-container {
  display: flex;
  width: 100%;
  justify-content: center;
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

.v-data-table-rows-no-data
{
  color: #bdbdbd;
  font-size: 18px;
  font-weight: 500;
}

.v-table th {
  font-weight: 900 !important;
  --v-table-header-height: 40px;
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

.hidden-select-all {
  width: 40px;
}

.appointment-select-row {
  width: 25px;
}
</style>