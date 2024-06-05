import { createRouter, createWebHistory } from 'vue-router'

import LoginPage from '../views/Login.vue'
import ClientHome from '../views/ClientHome.vue'
import ChangeAppointment from '../views/ChangeAppointment.vue'
import MakeAppointment from '../views/MakeAppointment.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Login',
      component: LoginPage
    },
    {
      path: '/ClientHome',
      name: 'ClientHome',
      component: ClientHome
    },
    {
      path: '/ChangeAppointment',
      name: 'ChangeAppointment',
      component: ChangeAppointment
    },
    {
      path: '/MakeAppointment',
      name: 'MakeAppointment',
      component: MakeAppointment
    }
  ]
})

export default router
