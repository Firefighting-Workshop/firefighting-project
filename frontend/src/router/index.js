import { createRouter, createWebHistory } from 'vue-router'

import LoginPage from '../views/Login.vue'
import ClientHome from '../views/ClientHome.vue'
import EmployeeHome from '../views/EmployeeHome.vue'
import ChangeAppointment from '../views/ChangeAppointment.vue'
import MakeAppointment from '../views/MakeAppointment.vue'
import AssignTasks from '../views/AssignTasks.vue'
import UnassignedTasks from '../views/UnassignedTasks.vue'
import DailyWorkTrip from '../views/DailyWorkTrip.vue'
import SelectDailyTask from '../views/SelectDailyTask.vue'
import MainReport from '../views/MainReport.vue'
import EquipmentReport from '../views/EquipmentReport.vue'
import CabinetReport from '../views/CabinetReport.vue'

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
      path: '/EmployeeHome',
      name: 'EmployeeHome',
      component: EmployeeHome
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
    },
    {
      path: '/AssignTasks',
      name: 'AssignTasks',
      component: AssignTasks
    },
    {
      path: '/UnassignedTasks',
      name: 'UnassignedTasks',
      component: UnassignedTasks
    },
    {
      path: '/DailyWorkTrip',
      name: 'DailyWorkTrip',
      component: DailyWorkTrip
    },
    {
      path: '/MainReport',
      name: 'MainReport',
      component: MainReport
    },
    {
      path: '/SelectDailyTask',
      name: 'SelectDailyTask',
      component: SelectDailyTask
    },
    {
      path: '/EquipmentReport',
      name: 'EquipmentReport',
      component: EquipmentReport
    },
    {
      path: '/CabinetReport',
      name: 'CabinetReport',
      component: CabinetReport
    }
  ]
})

export default router
