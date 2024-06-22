<script setup>
  import LoginCard from '../components/LoginCard.vue'
</script>

<template>
    <v-container fluid class="login-section px-2 mx-0">
      <img class="logo" src="..\..\static\images\mfink-logo.png"/>
      <h1 class="login-header mb-3">התחברות</h1>
      <LoginCard></LoginCard>
    </v-container>
</template>

<script>
export default 
{
  name: 'LoginPage',
  rtl: true,
  data: () => ({
      tab: null,
    }),
  methods: {
    
    },
  mounted()
  {
      localStorage.removeItem("LOCAL_STORAGE_TOKEN_KEY");
  }
}
</script>

<style scoped>
.login-section
{
  height: 100%;
  max-width: 500px;
  display: flex;
  flex-direction: column;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  align-self:center;
}

.login-header
{
  align-self: flex-start;
  font-size: 32px;
}

.logo 
{
  width: 100%;
  min-width: 300px;
  margin-bottom: 35px;
}
</style>