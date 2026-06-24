"""The compliance reminder engine.

Runs once a day (``scheduler_events["daily_long"]``) and, for every tracked
DocType, does two things:

1. **Auto status update** — flips an item to its "expired/overdue" status once
   the deadline has passed (if enabled in Compliance Settings).
2. **Multi-stage reminders** — sends an email and/or in-app notification at each
   configured milestone before the deadline (e.g. 30 / 15 / 7 / 1 days), on the
   due date itself, and — optionally — on a recurring interval after it.

Every send is recorded in a *Compliance Reminder Log* so reminders are
idempotent: re-running the job (or a catch-up after downtime) never spams the
same milestone twice.
"""

from __future__ import annotations

import frappe
from frappe.utils import date_diff, get_url_to_form, getdate, nowdate

from compliance_manager.utils.reminders_config import (
    DEFAULT_REMINDER_DAYS,
    TRACKED_DOCTYPES,
    parse_reminder_days,
)

SETTINGS_DOCTYPE = "Compliance Settings"
LOG_DOCTYPE = "Compliance Reminder Log"


# ---------------------------------------------------------------------------
# Scheduler entry point
# ---------------------------------------------------------------------------
def run_daily_reminders():
    """Scheduled daily. Process every tracked DocType."""
    settings = _get_settings()
    summary = {}
    for doctype in TRACKED_DOCTYPES:
        try:
            summary[doctype] = process_doctype(doctype, settings)
        except Exception:
            frappe.log_error(
                title=f"Compliance reminders failed for {doctype}",
                message=frappe.get_traceback(),
            )
    frappe.logger("compliance_manager").info({"compliance_reminders": summary})
    return summary


def process_doctype(doctype: str, settings=None) -> dict:
    """Update statuses and send due reminders for one tracked DocType."""
    settings = settings or _get_settings()
    meta = TRACKED_DOCTYPES[doctype]
    today = getdate(nowdate())

    fields = list(
        {
            "name",
            meta["date_field"],
            meta["status_field"],
            meta["owner_field"],
            meta["category_field"],
            meta["title_field"],
            "reminder_days_before",
            "enable_reminders",
        }
    )

    rows = frappe.get_all(
        doctype,
        filters={
            meta["date_field"]: ["is", "set"],
            meta["status_field"]: [
                "in",
                meta["active_statuses"] + [meta["expired_status"]],
            ],
        },
        fields=fields,
    )

    sent = 0
    flipped = 0
    for row in rows:
        deadline = row.get(meta["date_field"])
        if not deadline:
            continue
        days_to_deadline = date_diff(getdate(deadline), today)

        # 1) Auto status update (expired / overdue) -------------------------
        if (
            int(settings.get("auto_update_status") or 0)
            and days_to_deadline < 0
            and row.get(meta["status_field"]) in meta["active_statuses"]
        ):
            frappe.db.set_value(
                doctype, row["name"], meta["status_field"], meta["expired_status"]
            )
            row[meta["status_field"]] = meta["expired_status"]
            flipped += 1

        # 2) Reminders ------------------------------------------------------
        if not int(row.get("enable_reminders") or 0):
            continue

        milestone = _due_milestone(row, meta, settings, days_to_deadline)
        if not milestone:
            continue

        key, label, superseded_keys = milestone
        if _already_sent(doctype, row["name"], key):
            continue

        _dispatch_reminder(doctype, row, meta, settings, key, label, days_to_deadline)
        # Suppress (don't backfill) any earlier milestones missed during downtime.
        for sk in superseded_keys:
            if not _already_sent(doctype, row["name"], sk):
                _record_log(
                    doctype, row, meta, sk, f"Superseded by {label}", days_to_deadline,
                    channels="", suppressed=1,
                )
        sent += 1

    if not frappe.flags.in_test:
        frappe.db.commit()
    return {"reminders_sent": sent, "statuses_updated": flipped, "scanned": len(rows)}


# ---------------------------------------------------------------------------
# Milestone resolution
# ---------------------------------------------------------------------------
def _due_milestone(row, meta, settings, days_to_deadline):
    """Return ``(key, label, superseded_keys)`` for the reminder due today, else None."""
    offsets = _resolve_offsets(row, meta, settings)

    # Before the deadline: pick the nearest crossed milestone not yet sent.
    if days_to_deadline > 0:
        reached = [m for m in offsets if days_to_deadline <= m and m > 0]
        if not reached:
            return None
        current = min(reached)
        superseded = [f"T-{m}" for m in reached if m != current]
        return (f"T-{current}", f"{days_to_deadline} day(s) left", superseded)

    # On the deadline.
    if days_to_deadline == 0:
        return ("DUE", "due today", [])

    # After the deadline — optional recurring escalation.
    if int(settings.get("escalate_after_expiry") or 0):
        interval = int(settings.get("escalation_interval_days") or 7) or 7
        overdue_days = -days_to_deadline
        if overdue_days % interval == 0:
            return (f"OVERDUE-{overdue_days}", f"overdue by {overdue_days} day(s)", [])

    return None


def _resolve_offsets(row, meta, settings) -> list[int]:
    """Resolution order: document → category → settings → built-in default."""
    offsets = parse_reminder_days(row.get("reminder_days_before"))
    if offsets:
        return offsets

    category = row.get(meta["category_field"])
    if category:
        cat_days = frappe.db.get_value(
            "Compliance Category", category, "default_reminder_days"
        )
        offsets = parse_reminder_days(cat_days)
        if offsets:
            return offsets

    offsets = parse_reminder_days(settings.get("default_reminder_days"))
    return offsets or list(DEFAULT_REMINDER_DAYS)


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------
def _dispatch_reminder(doctype, row, meta, settings, key, label, days_to_deadline):
    recipients = _recipient_emails(row, meta, settings)
    user = row.get(meta["owner_field"])
    title = row.get(meta["title_field"]) or row["name"]
    deadline = row.get(meta["date_field"])
    url = get_url_to_form(doctype, row["name"])

    subject = f"Compliance reminder: {title} ({meta['noun']}) — {label}"
    body = _build_email(meta, title, deadline, label, url, doctype, row["name"])

    channels = []
    if int(settings.get("send_email") or 0) and recipients:
        try:
            frappe.sendmail(
                recipients=recipients,
                subject=subject,
                message=body,
                reference_doctype=doctype,
                reference_name=row["name"],
                now=False,
            )
            channels.append("Email")
        except Exception:
            frappe.log_error(
                title="Compliance reminder email failed",
                message=frappe.get_traceback(),
            )

    if int(settings.get("send_system_notification") or 0) and user:
        try:
            _make_notification_log(user, subject, body, doctype, row["name"])
            channels.append("System Notification")
        except Exception:
            frappe.log_error(
                title="Compliance reminder notification failed",
                message=frappe.get_traceback(),
            )

    _record_log(
        doctype, row, meta, key, label, days_to_deadline,
        channels=", ".join(channels), recipients=", ".join(recipients),
    )


def _build_email(meta, title, deadline, label, url, doctype, name):
    noun = meta["noun"].title()
    return f"""
        <p>Hello,</p>
        <p>This is an automated compliance reminder.</p>
        <table cellpadding="6" style="border-collapse:collapse">
            <tr><td><b>Item</b></td><td>{frappe.utils.escape_html(title)}</td></tr>
            <tr><td><b>Type</b></td><td>{noun}</td></tr>
            <tr><td><b>Deadline</b></td><td>{frappe.utils.formatdate(deadline)}</td></tr>
            <tr><td><b>Status</b></td><td>{frappe.utils.escape_html(label)}</td></tr>
        </table>
        <p><a href="{url}">Open {doctype}: {name}</a></p>
        <p>— Compliance Manager</p>
    """


def _make_notification_log(user, subject, body, doctype, name):
    note = frappe.new_doc("Notification Log")
    note.subject = subject
    note.email_content = body
    note.for_user = user
    note.type = "Alert"
    note.document_type = doctype
    note.document_name = name
    note.insert(ignore_permissions=True)


def _recipient_emails(row, meta, settings) -> list[str]:
    emails: list[str] = []
    user = row.get(meta["owner_field"])
    if user:
        email = frappe.db.get_value("User", user, "email") or user
        if email and "@" in email:
            emails.append(email)

    for cc in (settings.get("default_cc") or "").replace("\n", ",").split(","):
        cc = cc.strip()
        if cc and cc not in emails:
            emails.append(cc)

    if not emails and settings.get("fallback_recipient"):
        fb = settings.get("fallback_recipient")
        email = frappe.db.get_value("User", fb, "email") or fb
        if email:
            emails.append(email)

    return emails


# ---------------------------------------------------------------------------
# Reminder log (idempotency)
# ---------------------------------------------------------------------------
def _already_sent(doctype, name, milestone) -> bool:
    return bool(
        frappe.db.exists(
            LOG_DOCTYPE,
            {
                "reference_doctype": doctype,
                "reference_name": name,
                "milestone": milestone,
            },
        )
    )


def _record_log(doctype, row, meta, milestone, label, days_to_deadline,
                channels="", recipients="", suppressed=0):
    frappe.get_doc(
        {
            "doctype": LOG_DOCTYPE,
            "reference_doctype": doctype,
            "reference_name": row["name"],
            "milestone": milestone,
            "stage_label": label,
            "days_to_deadline": days_to_deadline,
            "channels": channels,
            "recipients": recipients,
            "suppressed": suppressed,
        }
    ).insert(ignore_permissions=True)


def _get_settings():
    return frappe.get_cached_doc(SETTINGS_DOCTYPE)


# ---------------------------------------------------------------------------
# Manual trigger (used by the "Run reminders now" button / API)
# ---------------------------------------------------------------------------
def run_now():
    # Same gate as the portal's "manager" concept: write access to settings.
    if not frappe.has_permission("Compliance Settings", "write"):
        frappe.throw("Not permitted to run reminders.", frappe.PermissionError)
    return run_daily_reminders()
