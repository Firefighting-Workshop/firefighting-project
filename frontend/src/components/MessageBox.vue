<script setup>
import { useRouter } from 'vue-router';
import HeaderItem from './HeaderItem.vue';

const router = useRouter();

const defaultCancelFunction = () => {
  router.go(-1);
};
</script>

<template>
    <v-container fluid class="main-section pa-0">
        <HeaderItem :headerTitle="messageTitle" hideSignout hideHome hideBack hidePlaceholder></HeaderItem>
        <v-row class="contents-row message-container ma-0 px-3">
            <v-icon :icon="messageIcon" :color="iconColor" size="150"></v-icon>
            <div class="message-contents mt-6">
                <h3 class="message-header">{{ messageHeader }}</h3>
                <p class="message-details mt-4">{{ messageDetails }}</p>
            </div>
            <div class="buttons-container mt-6">
                <v-btn class="cancel-btn ff-outlined-btn mx-3" v-show="!hideCancel" variant="flat" @click="cancelFunction ? cancelFunction() : defaultCancelFunction()" rounded="0">{{ cancelText }}</v-btn>
                <v-btn class="submit-btn ff-btn mx-3" variant="outlined" v-show="!hideSubmit" @click="submitFunction" rounded="0">{{ submitText }}</v-btn>
            </div>
        </v-row>
    </v-container>
</template>

<script>
export default {
  name: "MessageBox",
  props: {
    messageTitle: String,
    messageIcon: String,
    iconColor: String,
    messageHeader: String,
    messageDetails: String,
    homeLink: String,
    cancelText: String,
    submitText: String,
    hideCancel: { type: Boolean, default: false },
    hideSubmit: { type: Boolean, default: false },
    submitFunction: { type: Function, default: () => {} },
    cancelFunction: { type: Function, default: null }
  }
}
</script>

<style scoped>
.message-container {
  justify-content: center;
  align-items: center;
}

.message-contents {
  min-height: 150px;
  text-align: center;
}

.message-header, .message-details {
  font-weight: 500;
}

.message-details {
  color: #aaaaaa;
  font-size: 16px;
}

.submit-btn, .cancel-btn {
  width: 145px;
  align-self: center;
}

.buttons-container {
  display: flex;
  width: 100%;
  justify-content: center;
}
</style>