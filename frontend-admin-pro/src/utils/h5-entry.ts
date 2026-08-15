import { platformApi } from '@/api/platform'

/** 仅员工/客户角色，应使用手机 H5，不能进 PC 管理后台 */
export function getH5PortalKind(me: {
  roles?: string[]
  is_superuser?: boolean
}): 'employee' | 'customer' | null {
  if (me.is_superuser) return null
  const roles = new Set(me.roles || [])
  if (roles.size === 0) return 'employee'
  const h5Only = ['employee', 'customer']
  const adminCapable = [...roles].filter((r) => !h5Only.includes(r))
  if (adminCapable.length > 0) return null
  if (roles.has('customer')) return 'customer'
  if (roles.has('employee')) return 'employee'
  return null
}

export async function buildH5Url(tenantCode: string, hashPath: string): Promise<string | null> {
  const cfg = await platformApi.publicConfig()
  const base = (cfg.h5_site_url || '').trim().replace(/\/$/, '')
  if (!base) return null
  const path = hashPath.startsWith('/') ? hashPath : `/${hashPath}`
  return `${base}#${path}`
}

export async function redirectToH5Portal(tenantCode: string, kind: 'employee' | 'customer') {
  const code = tenantCode.trim().toUpperCase()
  const url =
    kind === 'customer'
      ? await buildH5Url(code, `/t/${code}/customer/order`)
      : await buildH5Url(code, `/t/${code}/login`)
  if (url) {
    window.location.href = url
    return true
  }
  return false
}
