"""Install / migrate lifecycle for Compliance Manager.

Creates the two app roles, seeds sensible Compliance Settings defaults, and
ships a starter set of Compliance Categories so the app is usable immediately
after ``install-app``.
"""

from __future__ import annotations

import frappe

ROLES = ("Compliance Manager", "Compliance User")

STARTER_CATEGORIES = [
    # (category_name, applies_to, default_reminder_days)
    ("Health Insurance", "Insurance", "30,15,7,1"),
    ("Vehicle Insurance", "Insurance", "30,15,7,1"),
    ("Liability Insurance", "Insurance", "45,30,15,7"),
    ("Property Insurance", "Insurance", "45,30,15,7"),
    ("Tax Filing", "Compliance", "30,15,7,3,1"),
    ("Safety Check", "Compliance", "30,15,7"),
    ("Environmental Clearance", "Compliance", "60,30,15"),
    ("HR Compliance", "Compliance", "30,15,7"),
    ("Business Licence", "Licence", "60,30,15,7"),
    ("Professional Certification", "Licence", "45,30,15"),
    ("ISO Certification", "Licence", "60,30,15"),
    ("Word Mark", "Trademark", "90,60,30,15"),
    ("Logo Mark", "Trademark", "90,60,30,15"),
]


def after_install():
    create_roles()
    seed_settings()
    seed_categories()
    frappe.db.commit()


def after_migrate():
    # Idempotent — keep roles present even if someone deleted them.
    create_roles()
    frappe.db.commit()


def create_roles():
    for role in ROLES:
        if not frappe.db.exists("Role", role):
            frappe.get_doc(
                {
                    "doctype": "Role",
                    "role_name": role,
                    "desk_access": 1,
                }
            ).insert(ignore_permissions=True)


def seed_settings():
    settings = frappe.get_single("Compliance Settings")
    if not settings.get("default_reminder_days"):
        settings.default_reminder_days = "30,15,7,1"
    # Only set channel defaults on a fresh install (all-zero state).
    if not (settings.send_email or settings.send_system_notification):
        settings.send_email = 1
        settings.send_system_notification = 1
    if not settings.auto_update_status:
        settings.auto_update_status = 1
    settings.escalation_interval_days = settings.escalation_interval_days or 7
    settings.save(ignore_permissions=True)


def seed_categories():
    for name, applies_to, days in STARTER_CATEGORIES:
        if frappe.db.exists("Compliance Category", name):
            continue
        frappe.get_doc(
            {
                "doctype": "Compliance Category",
                "category_name": name,
                "applies_to": applies_to,
                "default_reminder_days": days,
            }
        ).insert(ignore_permissions=True)
