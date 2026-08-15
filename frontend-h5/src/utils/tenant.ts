const TENANT_KEY = 'lightmes_h5_tenant_code'

export function parseTenantFromPath(path: string): string | null {
  const m = path.match(/^\/t\/([^/]+)/i)
  return m ? decodeURIComponent(m[1]).toUpperCase() : null
}

export function getStoredTenantCode(): string {
  return localStorage.getItem(TENANT_KEY) || ''
}

export function setStoredTenantCode(code: string) {
  if (code) localStorage.setItem(TENANT_KEY, code.trim().toUpperCase())
  else localStorage.removeItem(TENANT_KEY)
}

export function tenantH5LoginPath(code: string) {
  return `/#/t/${encodeURIComponent(code)}/login`
}

/** 将 /home、/tasks 等转为 /t/{code}/home（已含 /t/ 则原样返回） */
export function tenantH5Path(subpath: string, code?: string): string {
  const normalized = subpath.startsWith('/') ? subpath : `/${subpath}`
  if (/^\/t\/[^/]+/i.test(normalized)) return normalized
  const c = (code || getStoredTenantCode()).trim().toUpperCase()
  if (!c) return normalized
  return `/t/${encodeURIComponent(c)}${normalized}`
}

export function stripTenantPrefix(path: string): string {
  const stripped = path.replace(/^\/t\/[^/]+/i, '')
  return stripped || '/'
}

/** 修正 /customer/customer/order 等错误拼接；有变化则返回完整 path，否则 null */
export function fixDuplicateH5Path(path: string): string | null {
  const code = parseTenantFromPath(path)
  let sub = stripTenantPrefix(path)
  const before = sub
  sub = sub.replace(/\/customer\/customer(\/|$)/g, '/customer$1')
  sub = sub.replace(/\/home\/home(\/|$)/g, '/home$1')
  if (sub === before) return null
  if (code) return `/t/${encodeURIComponent(code)}${sub}`
  return sub
}
