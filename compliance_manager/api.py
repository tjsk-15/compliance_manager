"""Public API surface for Compliance Manager.

Includes the RPC endpoints consumed by the Vue portal (served at /compliance).
"""

from __future__ import annotations

import frappe
from frappe.utils import add_days, date_diff, nowdate

from compliance_manager.services import reminders
from compliance_manager.utils.reminders_config import TRACKED_DOCTYPES

COMPLIANCE_ROLES = ("Compliance Manager", "Compliance User", "System Manager")
MANAGER_ROLES = ("Compliance Manager", "System Manager")

# DocType <-> stable frontend key / label.
_TRACKER_KEYS = {
    "Insurance Policy": "insurance",
    "Licence": "licence",
    "Trademark": "trademark",
    "Compliance Record": "compliance",
}
_TRACKER_LABELS = {
    "Insurance Policy": "Insurance Policies",
    "Licence": "Licences",
    "Trademark": "Trademarks",
    "Compliance Record": "Compliance Records",
}


def has_app_permission(*args, **kwargs):
    """Gate the app launcher tile to compliance users only.

    Accepts/ignores any args so it stays compatible across Frappe versions that
    may call the ``add_to_apps_screen`` permission hook with or without context.
    """
    roles = set(frappe.get_roles())
    return bool(roles.intersection(COMPLIANCE_ROLES))


# ---------------------------------------------------------------------------
# Portal endpoints
# ---------------------------------------------------------------------------
@frappe.whitelist()
def get_portal_context():
    """Who is the logged-in user and what may they do. Called once on app load."""
    user = frappe.session.user
    roles = set(frappe.get_roles())
    return {
        "user": user,
        "full_name": frappe.db.get_value("User", user, "full_name") or user,
        "user_image": frappe.db.get_value("User", user, "user_image"),
        "roles": sorted(roles),
        "is_manager": bool(roles.intersection(MANAGER_ROLES)),
        "can_write": bool(roles.intersection(COMPLIANCE_ROLES)),
        "is_compliance_user": bool(roles.intersection(COMPLIANCE_ROLES)),
    }


@frappe.whitelist()
def get_expiry_summary():
    """Per-tracker counts powering the dashboard stat cards."""
    today = nowdate()
    in_30 = add_days(today, 30)
    in_7 = add_days(today, 7)
    summary = {}
    for doctype, meta in TRACKED_DOCTYPES.items():
        df, sf = meta["date_field"], meta["status_field"]
        active = meta["active_statuses"]
        summary[_TRACKER_KEYS[doctype]] = {
            "doctype": doctype,
            "key": _TRACKER_KEYS[doctype],
            "label": _TRACKER_LABELS[doctype],
            "total": frappe.db.count(doctype),
            "active": frappe.db.count(doctype, {sf: ["in", active]}),
            "expiring_7d": frappe.db.count(
                doctype, {df: ["between", [today, in_7]], sf: ["in", active]}
            ),
            "expiring_30d": frappe.db.count(
                doctype, {df: ["between", [today, in_30]], sf: ["in", active]}
            ),
            "overdue": frappe.db.count(doctype, {sf: meta["expired_status"]}),
        }
    return summary


@frappe.whitelist()
def get_upcoming_renewals(days=60, include_overdue=1, limit=100):
    """Unified, date-sorted list of renewals across every tracker (for the dashboard)."""
    days = int(days)
    include_overdue = int(include_overdue)
    limit = int(limit)
    today = nowdate()
    upto = add_days(today, days)
    start = "1900-01-01" if include_overdue else today

    rows = []
    for doctype, meta in TRACKED_DOCTYPES.items():
        df, sf, tf = meta["date_field"], meta["status_field"], meta["title_field"]
        for r in frappe.get_all(
            doctype,
            filters={
                df: ["between", [start, upto]],
                sf: ["in", meta["active_statuses"]],
            },
            fields=[
                "name",
                f"`{tf}` as title",
                f"`{df}` as date",
                f"`{sf}` as status",
                f"`{meta['owner_field']}` as in_charge",
            ],
            order_by=f"`{df}` asc",
            limit=limit,
        ):
            r["doctype"] = doctype
            r["tracker"] = _TRACKER_KEYS[doctype]
            r["tracker_label"] = _TRACKER_LABELS[doctype]
            r["days_left"] = date_diff(r["date"], today) if r["date"] else None
            rows.append(r)

    rows.sort(key=lambda x: (x["date"] or "9999-12-31"))
    return rows[:limit]


ALLOWED_LINK_DOCTYPES = {"User", "Compliance Category"}


@frappe.whitelist()
def get_link_options(doctype, filters=None):
    """Safe option lists for the portal's link pickers (In-Charge, Category).

    Whitelisted so any logged-in staff member can populate the dropdowns without
    needing direct read permission on the User doctype. Only the two link
    targets the portal uses are permitted, and only their name/label are exposed.
    """
    if doctype not in ALLOWED_LINK_DOCTYPES:
        frappe.throw("Link options not available for this type.", frappe.PermissionError)

    filters = frappe.parse_json(filters) if isinstance(filters, str) else (filters or {})

    if doctype == "User":
        rows = frappe.get_all(
            "User",
            filters={"enabled": 1, "user_type": "System User", "name": ["not in", ["Guest"]]},
            fields=["name", "full_name"],
            order_by="full_name asc",
            limit_page_length=0,
            ignore_permissions=True,
        )
        return [
            {"value": r.name, "label": r.full_name or r.name, "description": r.name}
            for r in rows
        ]

    rows = frappe.get_all(
        "Compliance Category",
        filters=filters,
        fields=["name"],
        order_by="name asc",
        limit_page_length=0,
        ignore_permissions=True,
    )
    return [{"value": r.name, "label": r.name} for r in rows]


@frappe.whitelist()
def run_reminders_now():
    """Manually trigger the reminder engine (admins / compliance managers)."""
    return reminders.run_now()
