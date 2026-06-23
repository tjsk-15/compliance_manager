"""Public API surface for Compliance Manager."""

from __future__ import annotations

import frappe

from compliance_manager.services import reminders
from compliance_manager.utils.reminders_config import TRACKED_DOCTYPES

COMPLIANCE_ROLES = ("Compliance Manager", "Compliance User", "System Manager")


def has_app_permission(*args, **kwargs):
    """Gate the app launcher tile to compliance users only.

    Accepts/ignores any args so it stays compatible across Frappe versions that
    may call the ``add_to_apps_screen`` permission hook with or without context.
    """
    roles = set(frappe.get_roles())
    return bool(roles.intersection(COMPLIANCE_ROLES))


@frappe.whitelist()
def run_reminders_now():
    """Manually trigger the reminder engine (admins / compliance managers)."""
    return reminders.run_now()


@frappe.whitelist()
def get_expiry_summary():
    """Counts powering the workspace number cards / dashboard.

    Returns, per tracker, how many items are expiring within 30 days and how
    many have already expired/are overdue.
    """
    summary = {}
    for doctype, meta in TRACKED_DOCTYPES.items():
        date_field = meta["date_field"]
        status_field = meta["status_field"]
        expiring = frappe.db.count(
            doctype,
            filters={
                date_field: ["between", [frappe.utils.nowdate(),
                                         frappe.utils.add_days(frappe.utils.nowdate(), 30)]],
                status_field: ["in", meta["active_statuses"]],
            },
        )
        expired = frappe.db.count(
            doctype, filters={status_field: meta["expired_status"]}
        )
        summary[doctype] = {"expiring_30d": expiring, "expired": expired}
    return summary
