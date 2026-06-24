import frappe

no_cache = 1


def get_context(context):
    """Server-side guard + boot data for the /compliance portal.

    All staff are Frappe users, so an unauthenticated visit bounces to login and
    comes back to the portal afterwards. The Vue app additionally checks roles.

    The built page (frappe-ui ``jinjaBootData``) injects ``window[key] = boot[key]``
    for every key in ``boot`` — so ``csrf_token`` here becomes ``window.csrf_token``,
    which frappe-ui's request layer needs for create/update/delete calls.
    """
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/compliance"
        raise frappe.Redirect

    context.boot = {
        "csrf_token": frappe.sessions.get_csrf_token(),
        "sitename": frappe.local.site,
        "user": frappe.session.user,
    }
    context.no_cache = 1
    return context
