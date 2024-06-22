<script setup>
  import HeaderItem from '../components/HeaderItem.vue'
</script>
<template>
    <v-container fluid class="main-section pa-0">
      <HeaderItem headerTitle="מילוי דיווחי תחזוקה" homeLink="/EmployeeHome" hideSignout></HeaderItem>
      <v-row class="contents-row ma-0 px-3">
        <v-form class="dialog-form-content" ref="form" v-model="valid" lazy-validation>
            <div class="form-input mt-9">
            <v-autocomplete
              v-model="selectedDailyTask"
              :items="dailyTasks"
              :custom-filter="customTasksFilter"
              item-title="client_name"
              density="comfortable"
              variant="outlined"
              :rules="[v => !!v || 'זהו שדה חובה.']"
              label="אתר לדיווח"
              placeholder="הזן את שם העסק או כתובת"
              chips
              required
              return-object>
                <template v-slot:item="{ item, props }">
                    <v-list-item v-bind="props">
                        <v-list-item-subtitle>{{ item.raw.client_street }} {{ item.raw.client_street_number }}, {{ item.raw.client_city }}</v-list-item-subtitle>
                    </v-list-item>
                </template>

            </v-autocomplete>
          </div>
        </v-form>
        <div class="buttons-container mt-9">
          <v-btn class="ff-btn mx-3" width="140px" variant="flat" rounded="0" @click="submitForm">מלא דיווח</v-btn>
        </div>
      </v-row>
    </v-container>
</template>
<style scoped>
.form-input
{
width: 100%;
max-width: 500px;
font-size: 14px;
}

.dialog-form-content
{
display: flex;
flex-direction: column;
justify-content: center;
width: 100%;
align-items: center;
}

.buttons-container
  {
    display: flex;
    flex: 1;
    align-items: flex-end;
    width: 100%;
    justify-content: center;
  }
</style>
<script>
import API from '@/api/api.js';
let api = new API();

export default {
  name: 'SelectDailyTask',
  rtl: true,
  data: () => ({
      dialog: true,
      valid: false,
      today: new Date(),
      dailyTasks: [],
      selectedDailyTask: null
    }),
  computed:
  {
    todayFormatted()
    {
      return this.formatDate(this.today);
    }
  },
  methods:
  {
    formatDate(date_input)
    {
      if (!date_input) return '';
      const date = new Date(date_input);
      const day = String(date.getDate()).padStart(2, '0');
      const month = String(date.getMonth() + 1).padStart(2, '0'); // Months are zero-based
      const year = date.getFullYear();
      return `${year}-${month}-${day}`;
    },
    customTasksFilter(itemText, queryText, item) 
    {
        const clientName = item.raw.client_name.toLowerCase();
        const clientStreet = item.raw.client_street.toLowerCase();
        const clientStreetNumber = item.raw.client_street_number.toLowerCase();
        const clientCity = item.raw.client_city.toLowerCase();
        const query = queryText.toLowerCase();
        return clientName.includes(query) || clientStreet.includes(query) || clientStreetNumber.includes(query) || clientCity.includes(query);
    },
    async submitForm() 
    {
      const { valid } = await this.$refs.form.validate();

      if (valid) 
      {
        localStorage.setItem("CLIENT_ON_REPORT", this.selectedDailyTask.apt_client);

        try
        {
          let token = localStorage.getItem('LOCAL_STORAGE_TOKEN_KEY');
          await api.post('/makeEquipmentReportsInDate', {"token": token, "date": this.todayFormatted, "client_id" : this.selectedDailyTask.apt_client })
          await api.post('/makeCabinetReportsInDate', {"token": token, "date": this.todayFormatted, "client_id" : this.selectedDailyTask.apt_client })
          this.$router.push('/MainReport');
        }
        catch(error)
        {
          console.error('Error:', error);
        }
      }
    },
  },
  async mounted()
  {
    try
    {
      let token = localStorage.getItem('LOCAL_STORAGE_TOKEN_KEY');
      let response = await api.get('/dailyEmployeeOpenTasks', {"token": token, "apt_date": this.todayFormatted});
      this.dailyTasks = response.data;
      console.log(this.dailyTasks);
    } 
    catch (error) 
    {
      console.error('Error:', error);
    }
  }
}
</script>