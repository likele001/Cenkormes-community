const TENANT_KEY = 'lightmes_tenant_code'

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

export function clearStoredTenantCode() {
  localStorage.removeItem(TENANT_KEY)
}

/** 登录后跳转：仅当 redirect 属于当前租户时才沿用，否则进当前租户首页 */
export function resolvePostLoginPath(tenantCode: string, redirect?: string | null): string {
  const tc = tenantCode.trim().toUpperCase()
  const base = `/t/${encodeURIComponent(tc)}/home`
  if (!redirect || typeof redirect !== 'string') return base
  const pathTenant = parseTenantFromPath(redirect)
  if (pathTenant && pathTenant !== tc) return base
  if (pathTenant) return redirect
  return tenantAdminPath(redirect, tc)
}

export function tenantLoginPath(code: string) {
  return `/t/${encodeURIComponent(code)}/login`
}

export function tenantAdminBase(code: string) {
  return `/t/${encodeURIComponent(code)}`
}

/** 将 /home、/production/orders 转为 /t/{code}/home（已含 /t/ 则原样） */
export function tenantAdminPath(subpath: string, code?: string): string {
  const normalized = subpath.startsWith('/') ? subpath : `/${subpath}`
  if (/^\/t\/[^/]+/i.test(normalized)) return normalized
  const c = (code || getStoredTenantCode()).trim().toUpperCase()
  if (!c) return normalized
  return `/t/${encodeURIComponent(c)}${normalized}`
}
