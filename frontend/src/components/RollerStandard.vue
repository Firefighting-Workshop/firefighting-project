<script setup>
  import HeaderItem from '../components/HeaderItem.vue'
</script>

<template>
  <v-container fluid class="main-section main-dialog-section pa-0">
    <HeaderItem class="dialog-header" headerTitle="דיווח תקן בדיקת גלגלון" hideSignout hideBack hideHome hidePlaceholder></HeaderItem>
    <v-row class="contents-row ma-0 px-3">
      <v-form class="dialog-form-content" ref="form" v-model="valid" lazy-validation>
        <div class="mt-9 form-input">
            <h3>באיזה תקן נבדק הגלגלון בעמדה?</h3>
            <v-radio-group class="mt-2" v-model="formData.rcab_roller_standard" hide-details>
                <v-radio label="תקן חדש" value="תקן חדש" color="red darken-3"></v-radio>
                <v-radio label="תקן ישן" value="תקן ישן" color="red darken-3"></v-radio>
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
export default {
  name: 'RollerStandard',
  rtl: true,
  props: {
    currentReportedCabinet: {
      type: Object,
      required: true,
    }
  },
  data: () => ({
    formData: {
        rcab_roller_standard: null
    },
    enforceRerenderKey: 0
  }),
  methods: {
    closeDialog() 
    {
      this.$emit('close-dialog');
    },
    async submitForm() 
    {
      this.$emit('submit-form', this.formData);
    },
  },
  async mounted() 
  {
    this.formData = { ...this.currentReportedCabinet };
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
</style>