import frappe
from frappe.model.document import Document

from compliance_manager.utils.reminders_config import parse_reminder_days


class ComplianceCategory(Document):
    def validate(self):
        # Normalise the reminder string so downstream parsing is predictable.
        days = parse_reminder_days(self.default_reminder_days)
        if days:
            self.default_reminder_days = ",".join(str(d) for d in days)
        elif self.default_reminder_days:
            frappe.throw(
                "Default Reminder Days must be a comma-separated list of "
                "non-negative numbers, e.g. 30,15,7,1"
            )
