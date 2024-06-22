<script setup>
  import HeaderItem from '../components/HeaderItem.vue'
  import { VNumberInput } from 'vuetify/labs/VNumberInput'
</script>

<template>
  <v-container fluid class="main-section main-dialog-section pa-0">
    <HeaderItem class="dialog-header" headerTitle="הוספת עמדה" hideSignout hideBack hideHome hidePlaceholder></HeaderItem>
    <v-row class="contents-row ma-0 px-3">
      <v-form class="dialog-form-content" ref="form" v-model="valid" lazy-validation>
        <v-text-field
            class="form-input mt-9"
            v-model="formData.rcab_location"
            density="comfortable"
            variant="outlined"
            :rules="[v => !!v || 'זהו שדה חובה.']"
            label="מיקום/תיאור העמדה"
            required>
        </v-text-field>
        <div class="mt-3 form-input">
            <h3>ציוד קיים בעמדה</h3>
            <v-card class="ff-card form-input mt-2 pa-2" variant="outlined">
              <div class="number-input-container"> 
                <p>גלגלון</p>
                <v-number-input
                  v-model="formData.rcab_rollers"
                  class="number-input"
                  controlVariant="split"
                  variant="outlined"
                  min="0"
                  width="140px"
                  density="compact"
                  hide-details
                  readonly/>
              </div>
              <div class="number-input-container mt-3"> 
                <p>מזנק ''2</p>
                <v-number-input
                  v-model="formData.rcab_nozzle2s"
                  class="number-input"
                  controlVariant="split"
                  variant="outlined"
                  min="0"
                  width="140px"
                  density="compact"
                  hide-details
                  readonly/>
              </div>
              <div class="number-input-container mt-3"> 
                <p>זרנוק</p>
                <v-number-input
                  v-model="formData.rcab_hoses"
                  class="number-input"
                  controlVariant="split"
                  variant="outlined"
                  min="0"
                  width="140px"
                  density="compact"
                  hide-details
                  readonly/>
              </div>
              <div class="number-input-container mt-3"> 
                <p>ברז שריפה ''2</p>
                <v-number-input
                  v-model="formData.rcab_firehydrants"
                  class="number-input"
                  controlVariant="split"
                  variant="outlined"
                  min="0"
                  width="140px"
                  density="compact"
                  hide-details
                  readonly/>
              </div>
              <div class="number-input-container mt-3"> 
                <p>ארון כיבוי</p>
                <v-number-input
                  v-model="formData.rcab_firecabinets"
                  class="number-input"
                  controlVariant="split"
                  variant="outlined"
                  min="0"
                  width="140px"
                  density="compact"
                  hide-details
                  readonly/>
              </div>
            </v-card>
        </div>
      </v-form>
      <div class="buttons-container mt-9">
        <v-btn class="ff-outlined-btn mx-3" width="140px" variant="flat" rounded="0" @click="closeDialog">בטל</v-btn>
        <v-btn class="ff-btn mx-3" width="140px" variant="flat" rounded="0" @click="submitForm">הוסף</v-btn>
      </div>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: 'AddCabinet',
  rtl: true,
  data: () => ({
    formData: {
      rcab_date: '',
      rcab_client: '',
      rcab_location: '',
      rcab_rollers: 0,
      rcab_nozzle2s: 0,
      rcab_hoses: 0,
      rcab_firehydrants: 0,
      rcab_firecabinets: 0
    },
    enforceRerenderKey: 0
  }),
  methods: 
  {
    closeDialog() 
    {
      this.$emit('close-dialog');
    },
    
    async submitForm() 
    {
        const { valid } = await this.$refs.form.validate();

        if (valid) 
        {
          this.$emit('submit-form', this.formData);
        }
    },
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

.number-input-container
{
  display: flex;
  flex-wrap: wrap;
  width: 100%;
}

.number-input-container p
{
  display: flex;
  flex-wrap: wrap;
  align-content: center;
  font-size: 16px;
  font-weight: 500;
  flex-grow: 1;
}

.number-input-container .number-input
{
  flex-grow: 0;
}
</style>