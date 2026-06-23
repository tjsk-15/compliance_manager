import frappe
from frappe.utils import add_days, nowdate

from compliance_manager.services import reminders
from compliance_manager.tests import ComplianceTestCase
from compliance_manager.utils.reminders_config import (
    TRACKED_DOCTYPES,
    parse_reminder_days,
)

INS = TRACKED_DOCTYPES["Insurance Policy"]


class TestReminderHelpers(ComplianceTestCase):
    """Pure-logic tests — no records created."""

    def test_parse_reminder_days(self):
        self.assertEqual(parse_reminder_days("30,15,7,1"), [30, 15, 7, 1])
        self.assertEqual(parse_reminder_days("1 7 15 30"), [30, 15, 7, 1])
        self.assertEqual(parse_reminder_days("30,30,7"), [30, 7])
        self.assertEqual(parse_reminder_days(""), [])
        self.assertEqual(parse_reminder_days("abc,-5,7"), [7])

    def _milestone(self, days_to_deadline, settings=None):
        row = {"reminder_days_before": "30,15,7,1"}
        return reminders._due_milestone(row, INS, settings or {}, days_to_deadline)

    def test_milestone_picks_nearest_crossed_stage(self):
        # 12 days out: both 30 and 15 are crossed; nearest is 15, 30 superseded.
        key, label, superseded = self._milestone(12)
        self.assertEqual(key, "T-15")
        self.assertIn("T-30", superseded)

    def test_milestone_exact_offset(self):
        key, _, _ = self._milestone(7)
        self.assertEqual(key, "T-7")

    def test_milestone_due_today(self):
        key, _, _ = self._milestone(0)
        self.assertEqual(key, "DUE")

    def test_no_milestone_when_far_out(self):
        self.assertIsNone(self._milestone(45))

    def test_overdue_escalation_respects_setting(self):
        self.assertIsNone(self._milestone(-7, {}))
        settings = {"escalate_after_expiry": 1, "escalation_interval_days": 7}
        key, _, _ = self._milestone(-7, settings)
        self.assertEqual(key, "OVERDUE-7")
        # Not a multiple of the interval -> no reminder.
        self.assertIsNone(self._milestone(-6, settings))


class TestReminderEngine(ComplianceTestCase):
    def setUp(self):
        settings = frappe.get_single("Compliance Settings")
        settings.send_email = 1
        settings.send_system_notification = 1
        settings.auto_update_status = 1
        settings.default_reminder_days = "30,15,7,1"
        settings.save()

        if not frappe.db.exists("Compliance Category", "Test Insurance Cat"):
            frappe.get_doc(
                {
                    "doctype": "Compliance Category",
                    "category_name": "Test Insurance Cat",
                    "applies_to": "Insurance",
                    "default_reminder_days": "30,15,7,1",
                }
            ).insert()

    def _make_policy(self, expiry, status="Active"):
        return frappe.get_doc(
            {
                "doctype": "Insurance Policy",
                "document_name": "Test Policy",
                "insurance_type": "Test Insurance Cat",
                "in_charge": "Administrator",
                "status": status,
                "issue_date": add_days(nowdate(), -300),
                "expiry_date": expiry,
                "enable_reminders": 1,
            }
        ).insert()

    def test_reminder_sent_and_logged_once(self):
        policy = self._make_policy(add_days(nowdate(), 7))
        reminders.process_doctype("Insurance Policy")

        logs = frappe.get_all(
            "Compliance Reminder Log",
            filters={"reference_name": policy.name, "suppressed": 0},
        )
        self.assertEqual(len(logs), 1)

        # Re-running the same day must not send a duplicate.
        reminders.process_doctype("Insurance Policy")
        logs = frappe.get_all(
            "Compliance Reminder Log",
            filters={"reference_name": policy.name, "suppressed": 0},
        )
        self.assertEqual(len(logs), 1)

    def test_auto_status_flip_when_expired(self):
        policy = self._make_policy(add_days(nowdate(), -1))
        reminders.process_doctype("Insurance Policy")
        self.assertEqual(
            frappe.db.get_value("Insurance Policy", policy.name, "status"), "Expired"
        )

    def test_disabled_reminders_skipped(self):
        policy = self._make_policy(add_days(nowdate(), 7))
        frappe.db.set_value("Insurance Policy", policy.name, "enable_reminders", 0)
        reminders.process_doctype("Insurance Policy")
        logs = frappe.get_all(
            "Compliance Reminder Log", filters={"reference_name": policy.name}
        )
        self.assertEqual(len(logs), 0)
