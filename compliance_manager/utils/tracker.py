"""Shared base controller for the four tracker DocTypes.

Each tracker (Insurance Policy, Licence, Trademark, Compliance Record) subclasses
``ComplianceTrackerDocument`` and declares its issue/deadline field names. The
base handles the cross-cutting rules so the concrete controllers stay thin.
"""

from __future__ import annotations

import frappe
from frappe.model.document import Document
from frappe.utils import getdate

from compliance_manager.utils.reminders_config import parse_reminder_days


class ComplianceTrackerDocument(Document):
    # Overridden by subclasses.
    ISSUE_FIELD: str | None = None
    DEADLINE_FIELD: str | None = None

    def validate(self):
        self._normalize_reminder_days()
        self._validate_date_order()

    def _normalize_reminder_days(self):
        raw = self.get("reminder_days_before")
        days = parse_reminder_days(raw)
        if days:
            self.reminder_days_before = ",".join(str(d) for d in days)
        elif raw:
            frappe.throw(
                "Reminder Days must be a comma-separated list of non-negative "
                "numbers, e.g. 30,15,7,1 (leave blank to inherit the category "
                "or global default)."
            )

    def _validate_date_order(self):
        if not (self.ISSUE_FIELD and self.DEADLINE_FIELD):
            return
        issue = self.get(self.ISSUE_FIELD)
        deadline = self.get(self.DEADLINE_FIELD)
        if issue and deadline and getdate(deadline) < getdate(issue):
            issue_label = self.meta.get_label(self.ISSUE_FIELD)
            deadline_label = self.meta.get_label(self.DEADLINE_FIELD)
            frappe.throw(f"{deadline_label} cannot be earlier than {issue_label}.")
