import { reactive } from 'vue'
import { createResource, call } from 'frappe-ui'

// Single shared session/context store, populated once on app load.
export const session = reactive({
  user: null,
  fullName: '',
  userImage: null,
  roles: [],
  isManager: false,
  canWrite: false,
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
    session.isManager = !!data.is_manager
    session.canWrite = !!data.can_write
    session.isCompliance = !!data.is_compliance_user
    session.loaded = true
  },
})

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
