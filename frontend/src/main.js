import './index.css'

import { createApp } from 'vue'
import { setConfig, frappeRequest, resourcesPlugin } from 'frappe-ui'

import App from './App.vue'
import router from './router'

// Route all frappe-ui resources through frappeRequest (handles CSRF + /api).
setConfig('resourceFetcher', frappeRequest)

const app = createApp(App)
app.use(resourcesPlugin)
app.use(router)
app.mount('#app')
