import { reactive } from 'vue'
import { createResource, call } from 'frappe-ui'

// Single shared session/context store, populated once on app load.
export const session = reactive({
  user: null,
  fullName: '',
  userImage: null,
  roles: [],
  // Per-DocType permission map from the server: { [doctype]: { read, create, write, delete } }
  permissions: {},
  isManager: false,
  canManageSettings: false,
  isCompliance: false,
  loaded: false,
})

export const contextResource = createResource({
  url: 'compliance_manager.api.get_portal_context',
  onSuccess(data) {
    session.user = data.user
    session.fullName = data.full_name
    session.userImage = data.user_image
    session.roles = data.roles || []
    session.permissions = data.permissions || {}
    session.isManager = !!data.is_manager
    session.canManageSettings = !!data.can_manage_settings
    session.isCompliance = !!data.is_compliance_user
    session.loaded = true
  },
})

// True if the logged-in user has `ptype` permission on `doctype`, straight from
// Frappe's permission engine (see compliance_manager.api.get_portal_context).
// This is the single source of truth for showing/hiding actions in the portal.
export function can(doctype, ptype = 'read') {
  const p = session.permissions?.[doctype]
  return !!(p && p[ptype])
}

export async function logout() {
  // Clear the session via the API, then land on Frappe's login page
  // (redirect-to brings the user back to the portal after they sign in again).
  try {
    await call('logout')
  } catch (e) {
    // Session may already be gone — fall through to the redirect regardless.
  }
  window.location.href = '/login?redirect-to=/compliance'
}
