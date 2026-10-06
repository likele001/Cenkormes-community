import { createApp } from 'vue'
import { createHead } from '@unhead/vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)
// 6月24日新增：全局 head 管理（用于 SEO meta）
app.use(createHead())
app.use(router)
app.mount('#app')
