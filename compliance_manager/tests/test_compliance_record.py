import frappe
from frappe.utils import add_to_date, nowdate

from compliance_manager.tests import ComplianceTestCase


class TestComplianceRecordRecurrence(ComplianceTestCase):
    def test_completing_recurring_item_creates_next(self):
        rec = frappe.get_doc(
            {
                "doctype": "Compliance Record",
                "compliance_name": "Quarterly GST Filing",
                "status": "Pending",
                "frequency": "Quarterly",
                "due_date": nowdate(),
                "in_charge": "Administrator",
            }
        ).insert()

        rec.status = "Completed"
        rec.save()

        next_due = add_to_date(nowdate(), months=3)
        self.assertTrue(
            frappe.db.exists(
                "Compliance Record",
                {
                    "compliance_name": "Quarterly GST Filing",
                    "due_date": next_due,
                    "status": "Pending",
                },
            )
        )

    def test_one_time_item_does_not_recur(self):
        rec = frappe.get_doc(
            {
                "doctype": "Compliance Record",
                "compliance_name": "One Off Audit",
                "status": "Pending",
                "frequency": "One-time",
                "due_date": nowdate(),
            }
        ).insert()

        rec.status = "Completed"
        rec.save()

        count = frappe.db.count(
            "Compliance Record", filters={"compliance_name": "One Off Audit"}
        )
        self.assertEqual(count, 1)
