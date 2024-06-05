import { createApp } from 'vue'
import router from './router'

import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import he from 'vuetify/lib/locale/he'
import en from 'vuetify/lib/locale/en'

import '@mdi/font/css/materialdesignicons.css'

import App from './App.vue'

const app = createApp(App)

const vuetify = createVuetify({
    components,
    directives,
    locale: {
      locale: 'he',
      fallback: 'en',
      messages: { he, en } 
  },
  icons: {
    defaultSet: 'mdi'
  }
})

app.use(router)
app.use(vuetify)

app.mount('#app')
