import frappe
from frappe.utils import add_to_date, nowdate

from compliance_manager.utils.tracker import ComplianceTrackerDocument

FREQUENCY_MONTHS = {
    "Monthly": 1,
    "Quarterly": 3,
    "Half-Yearly": 6,
    "Annual": 12,
}


class ComplianceRecord(ComplianceTrackerDocument):
    DEADLINE_FIELD = "due_date"

    def validate(self):
        super().validate()
        if self.status == "Completed" and not self.completion_date:
            self.completion_date = nowdate()

    def on_update(self):
        # When a recurring item is completed, schedule the next occurrence.
        if (
            self.has_value_changed("status")
            and self.status == "Completed"
            and self.frequency in FREQUENCY_MONTHS
        ):
            self.create_next_occurrence()

    def create_next_occurrence(self):
        months = FREQUENCY_MONTHS[self.frequency]
        next_due = add_to_date(self.due_date, months=months)

        # Avoid duplicates if the controller fires more than once.
        existing = frappe.db.exists(
            "Compliance Record",
            {
                "compliance_name": self.compliance_name,
                "due_date": next_due,
                "frequency": self.frequency,
            },
        )
        if existing:
            return

        nxt = frappe.copy_doc(self)
        nxt.status = "Pending"
        nxt.due_date = next_due
        nxt.completion_date = None
        nxt.insert(ignore_permissions=True)
        frappe.msgprint(
            f"Next {self.frequency.lower()} occurrence created: "
            f"<a href='/app/compliance-record/{nxt.name}'>{nxt.name}</a> "
            f"due {next_due}.",
            alert=True,
        )
