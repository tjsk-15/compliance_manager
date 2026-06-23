import frappe
from frappe.model.document import Document

from compliance_manager.utils.reminders_config import parse_reminder_days


class ComplianceSettings(Document):
    def validate(self):
        days = parse_reminder_days(self.default_reminder_days)
        if days:
            self.default_reminder_days = ",".join(str(d) for d in days)
        if self.escalate_after_expiry and (self.escalation_interval_days or 0) < 1:
            frappe.throw("Escalation Interval must be at least 1 day.")
