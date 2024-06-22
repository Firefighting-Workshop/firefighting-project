<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();
</script>
<template>
    <v-container class="header-container ma-0 pa-0" fluid>
      <router-link class="header-btn" v-show="!hideSignout" to="/">
        <v-icon icon="mdi-logout" size="35"></v-icon>
      </router-link>
      <button class="header-btn" v-show="!hideBack" @click="router.go(-1)">
        <v-icon icon="mdi-chevron-right" size="40"></v-icon>
      </button>
      <h1 class="header-title">{{ headerTitle }}</h1>
      <router-link class="header-btn home-btn" v-show="!hideHome" :to="homeLink">
        <v-icon icon="mdi-home" size="40"></v-icon>
      </router-link>
      <div class="home-placeholder" v-show="!hidePlaceholder && hideHome"></div>
    </v-container>
</template>
<script>
export default {
  name: "HeaderItem",
  rtl: true,
  props: 
  {
    headerTitle: String,
    homeLink: String,
    hideBack: {type: Boolean, default: false},
    hideSignout: {type: Boolean, default: false},
    hideHome: {type: Boolean, default: false},
    hidePlaceholder: {type: Boolean, default: false},
  }
}
</script>
<style scoped>
.header-container
{
    display: flex;
    position: fixed;
    z-index: 1;
    flex-wrap: wrap;
    width: 100%;
    background-color: #d10019;
    height: 50px;
    box-shadow: 0px 1px 5px #00000059;
    color: #fafafa;
}

.header-btn, .home-placeholder
{
  width: 50px;
  color: #fafafa;
  display: flex;
  justify-content: center;
  align-items: center;
  text-decoration: none;
}

.header-title
{
  display: flex;
  justify-content: center;
  align-items: center;
  flex-grow: 1;
  font-size: 20px;
  font-weight: bold;
}
</style>