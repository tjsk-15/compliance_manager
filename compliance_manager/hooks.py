app_name = "compliance_manager"
app_title = "Compliance Manager"
app_publisher = "Tejas Kutnikar"
app_description = (
    "Centralized tracking and reminders for organizational compliance: "
    "insurances, licences, trademarks and regulatory obligations."
)
app_email = "tjs.kutnikar@gmail.com"
app_license = "MIT"

# This is a pure Frappe app. It installs on a plain Frappe site and also
# appears inside ERPNext. It must NOT hard-depend on ERPNext.
required_apps = ["frappe"]

# ---------------------------------------------------------------------------
# Workspaces / Desk
# ---------------------------------------------------------------------------
# The "Compliance" workspace ships as a module-owned JSON
# (compliance_manager/compliance_manager/workspace/compliance/compliance.json)
# and is restricted to the Compliance roles so non-compliance modules stay
# hidden for compliance-only users.

add_to_apps_screen = [
    {
        "name": "compliance_manager",
        "logo": "/assets/compliance_manager/images/logo.svg",
        "title": "Compliance Manager",
        "route": "/app/compliance",
        # Only show the app launcher tile to users who hold a compliance role.
        "has_permission": "compliance_manager.api.has_app_permission",
    }
]

# ---------------------------------------------------------------------------
# Install / setup lifecycle
# ---------------------------------------------------------------------------
after_install = "compliance_manager.install.after_install"
after_migrate = "compliance_manager.install.after_migrate"

# ---------------------------------------------------------------------------
# Scheduled tasks — the reminder engine
# ---------------------------------------------------------------------------
scheduler_events = {
    "daily_long": [
        "compliance_manager.services.reminders.run_daily_reminders",
    ],
}

# ---------------------------------------------------------------------------
# Client scripts
# ---------------------------------------------------------------------------
doctype_js = {
    "Insurance Policy": "public/js/insurance_policy.js",
    "Licence": "public/js/licence.js",
    "Trademark": "public/js/trademark.js",
    "Compliance Record": "public/js/compliance_record.js",
}

# ---------------------------------------------------------------------------
# Fixtures — export the roles and supporting records with the app
# ---------------------------------------------------------------------------
fixtures = [
    {
        "doctype": "Role",
        "filters": {"name": ["in", ["Compliance Manager", "Compliance User"]]},
    },
]
