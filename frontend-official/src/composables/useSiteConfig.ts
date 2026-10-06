import { ref } from 'vue'

interface SiteContact {
  wechat: string
  phone: string
  email: string
  bdEmail: string
  supportEmail: string
}

const contact = ref<SiteContact>({
  wechat: '',
  phone: '',
  email: '',
  bdEmail: '',
  supportEmail: '',
})
let loaded = false

const PUBLIC_SITE_API = 'https://www.cenkor.cn/api/v1/public/site'

export function useSiteConfig() {
  async function fetchContact() {
    if (loaded) return contact.value
    loaded = true
    try {
      const res = await fetch(PUBLIC_SITE_API, { method: 'GET' })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const json = await res.json()
      const cfg = json?.site_config ?? {}
      contact.value = {
        wechat: cfg['contact.wechat'] ?? '',
        phone: cfg['contact.phone'] ?? '',
        email: cfg['contact.email'] ?? '',
        bdEmail: cfg['contact.bd_email'] ?? '',
        supportEmail: cfg['contact.support_email'] ?? '',
      }
    } catch {
      loaded = false
    }
    return contact.value
  }

  return { contact, fetchContact }
}
