import { createHead } from '@unhead/vue/client'
import { createPinia } from 'pinia'
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './style.css'
import 'vue-sonner/style.css'

const app = createApp(App)
const pinia = createPinia()
const head = createHead()
app.use(pinia)
app.use(head)
app.use(router)
app.mount('#app')
