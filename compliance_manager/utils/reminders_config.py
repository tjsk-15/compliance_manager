"""Central configuration for the compliance reminder engine.

Each tracked DocType declares the date field that drives reminders, the status
field, and which status value means "no longer active" so the engine can both
send multi-stage reminders and auto-flip the status once the deadline passes.

Keeping this in one place means the reminder service stays generic and new
trackers can be added by appending a single entry here.
"""

from __future__ import annotations

# Fallback used when neither the document nor its category specify offsets.
DEFAULT_REMINDER_DAYS = [30, 15, 7, 1]


# fmt: off
TRACKED_DOCTYPES = {
    "Insurance Policy": {
        "title_field": "document_name",
        "date_field": "expiry_date",
        "status_field": "status",
        "category_field": "insurance_type",
        "active_statuses": ["Active", "Renewing"],
        "expired_status": "Expired",
        "owner_field": "in_charge",
        "noun": "insurance policy",
    },
    "Licence": {
        "title_field": "licence_name",
        "date_field": "expiry_date",
        "status_field": "status",
        "category_field": "licence_type",
        "active_statuses": ["Active", "Renewing"],
        "expired_status": "Expired",
        "owner_field": "in_charge",
        "noun": "licence",
    },
    "Trademark": {
        "title_field": "brand_name",
        "date_field": "valid_till",
        "status_field": "status",
        "category_field": "trademark_class",
        "active_statuses": ["Filed", "Advertised", "Registered"],
        "expired_status": "Expired",
        "owner_field": "in_charge",
        "noun": "trademark",
    },
    "Compliance Record": {
        "title_field": "compliance_name",
        "date_field": "due_date",
        "status_field": "status",
        "category_field": "category",
        "active_statuses": ["Pending", "In Progress"],
        "expired_status": "Overdue",
        "owner_field": "in_charge",
        "noun": "compliance item",
    },
}
# fmt: on


def parse_reminder_days(raw) -> list[int]:
    """Turn a comma/space separated string of offsets into a sorted int list.

    Accepts ``"30,15,7,1"`` or ``"30 15 7 1"``. Invalid tokens are ignored.
    Returns a descending, de-duplicated list of non-negative integers.
    """
    if not raw:
        return []

    if isinstance(raw, (list, tuple)):
        tokens = raw
    else:
        tokens = str(raw).replace("\n", ",").replace(" ", ",").split(",")

    days: set[int] = set()
    for token in tokens:
        token = str(token).strip()
        if not token:
            continue
        try:
            value = int(float(token))
        except (TypeError, ValueError):
            continue
        if value >= 0:
            days.add(value)

    return sorted(days, reverse=True)
