<script setup>
  import HeaderItem from '../components/HeaderItem.vue'
</script>
<template>
  <v-container fluid class="main-section main-dialog-section pa-0">
      <HeaderItem class="dialog-header" headerTitle="עריכת פרטי ציוד" hideSignout hideBack hideHome hidePlaceholder></HeaderItem>
      <v-row class="contents-row ma-0 px-3">
        <v-form class="dialog-form-content" ref="form" v-model="valid" lazy-validation>
          <div class="form-input mt-9">
            <v-autocomplete
              v-model="formData.reqp_details"
              :items="equipments"
              :custom-filter="customEquipmentFilter"
              item-title="eqp_name"
              item-value="eqp_cat_number"
              density="comfortable"
              variant="outlined"
              :rules="[v => !!v || 'זהו שדה חובה.']"
              label="סוג הציוד"
              chips
              required>

              <template v-slot:item="{ item, props }">
                <v-list-item v-bind="props">
                  <v-list-item-content>
                    <v-list-item-subtitle>מק"ט: {{ item.raw.eqp_cat_number }}</v-list-item-subtitle>
                    <v-list-item-subtitle>סוג: {{ item.raw.eqp_type }}</v-list-item-subtitle>
                    <v-list-item-subtitle>יצרן: {{ item.raw.eqp_manufacturer }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
              </template>

              <template v-slot:chip="{ props, item }">
                <v-chip
                  v-bind="props"
                >
                {{ item.raw.eqp_name }}, {{ item.raw.eqp_manufacturer }}
                </v-chip>
              </template>

            </v-autocomplete>
          </div>
          <v-card class="ff-card form-input mt-3 pa-2" variant="outlined">
            <h3>האם הציוד שייך לעמדה?</h3>
            <v-radio-group class="mt-2" v-model="formData.is_belongs_cabinet" inline hide-details>
              <v-radio class="me-9" label="כן" :value="1" color="red darken-3"></v-radio>
              <v-radio label="לא" :value="0" color="red darken-3"></v-radio>
            </v-radio-group>
            <div class="form-input mt-4"  v-show="formData.is_belongs_cabinet">
              <v-autocomplete
                v-model="formData.reqp_belongs_cabinet"
                :items="cabinets"
                item-title="rcab_location"
                item-value="rcab_id"
                density="comfortable"
                variant="outlined"
                label="עמדה שייכת"
                hide-details
                chips>
              </v-autocomplete>
            </div>
            <v-text-field
              class="form-input mt-4"
              v-show="!(formData.is_belongs_cabinet)"
              v-model="formData.reqp_location"
              density="comfortable"
              variant="outlined"
              label="מיקום הציוד אצל הלקוח"
              hide-details
            ></v-text-field>
          </v-card>
          <v-text-field
            class="form-input mt-9"
            v-model="formData.reqp_pressure_test_year"
            density="comfortable"
            variant="outlined"
            :rules="[v => v === null || v === '' || /^\d+$/.test(v) || 'יש להזין ערך מספרי.']"
            :maxlength="4"
            label="שנת בדיקת לחץ אחרונה (למטפה בלבד)"
            placeholder="YYYY"
          ></v-text-field>
          <div class="mt-3 form-input">
            <h3>האם הציוד עדיין קיים ובשימוש?</h3>
            <v-radio-group class="mt-2" v-model="formData.reqp_in_use" inline hide-details>
              <v-radio class="me-9" label="כן" :value="1" color="red darken-3"></v-radio>
              <v-radio label="לא" :value="0" color="red darken-3"></v-radio>
            </v-radio-group>
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
    name: 'EditEquipment',
    rtl: true,
    props: {
      client: {
        type: Object,
        required: true
      },
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
          reqp_details: '',
          reqp_location: '',
          reqp_belongs_cabinet: '',
          reqp_pressure_test_year: '',
          reqp_in_use: 0,
          is_belongs_cabinet: 0
        },
        equipments: [],
        cabinets: []
      }),
    watch: {
      currentReportedEquipment: {
        handler(newVal) {
          this.formData = { ...newVal };
        },
        immediate: true,
      },
    },
    computed:
    {
      todayFormatted()
      {
        return this.formatDate(this.today);
      }
    },
    methods: {
      closeDialog() {
        this.$emit('close-dialog');
      },
      async submitForm() {
        const { valid } = await this.$refs.form.validate();

        if (valid) {
          this.$emit('submit-form', this.formData);
        }
      },
      async getAllEquipments() {
        try {
          let token = localStorage.getItem('LOCAL_STORAGE_TOKEN_KEY');
          let response = await api.get('/allEquipments', {"token": token});
          this.equipments = response.data;
          console.log(this.equipments);
        } 
        catch (error) 
        {
          console.error('Error:', error);
        }
      },
      async getAllCabinets() {
        try {
          let token = localStorage.getItem('LOCAL_STORAGE_TOKEN_KEY');
          let response = await api.get('/allCabinetReportsInDate', {"token": token, "date": this.todayFormatted, "client_id": this.client.client_id });
          this.cabinets = response.data;
          console.log(this.cabinets);
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
      customEquipmentFilter(itemText, queryText, item) 
      {
        const catalogNumber = item.raw.eqp_cat_number.toLowerCase();
        const eqpName = item.raw.eqp_name.toLowerCase();
        const eqpType = item.raw.eqp_type.toLowerCase();
        const eqpManufacturer = item.raw.eqp_manufacturer.toLowerCase();
        const query = queryText.toLowerCase();
        return catalogNumber.includes(query) || eqpName.includes(query) || eqpType.includes(query) || eqpManufacturer.includes(query);
      }
    },
    created() 
    {
      this.formData = { ...this.currentReportedEquipment};

      if (!this.currentReportedEquipment.reqp_belongs_cabinet || this.currentReportedEquipment.reqp_belongs_cabinet == 0) 
      {
        this.formData.is_belongs_cabinet = 0;
      } 
      else 
      {
        this.formData.is_belongs_cabinet = 1;
      }
    },
    async mounted()
    {
        await this.getAllEquipments();
        await this.getAllCabinets();
    }
  };
  </script>
  
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
    flex-wrap: wrap;
    justify-content: center;
    width: 100%;
    align-items: center;
  }

  .dialog-header
  {
    top: 0;
  }

  .main-dialog-section
  {
      position: absolute;
      z-index: 200;
      background-color: #fafafa;
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
  