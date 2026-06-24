# Compliance Manager

A custom **Frappe** app that centralizes and streamlines the management of
organizational compliance documents — **insurances, licences, trademarks** and
**regulatory obligations** — with categorization, ownership, attachments and
multi-stage renewal **reminders**.

> **Deployment answer (your first question):** this is a **pure Frappe app with
> zero hard dependency on ERPNext.** It installs and runs on a plain Frappe
> site, and it _also_ drops cleanly into an ERPNext site where it appears in the
> sidebar alongside Accounting, HR, Projects, etc. You do **not** need ERPNext.
> See [Why standalone Frappe](#why-standalone-frappe-and-not-erpnext).

---

## Feature map

| Requested feature | Implemented as |
| --- | --- |
| Insurance Tracker | **Insurance Policy** DocType |
| Compliance Tracker | **Compliance Record** DocType (with recurrence) |
| Licence Tracker | **Licence** DocType |
| Trademark Tracker | **Trademark** DocType (+ vendor follow-up table) |
| Compliance Categories (Settings) | **Compliance Category** master (`Applies To` filter) |
| Reminders & notifications | **Reminder engine** (daily scheduler) → Email + in-app |
| Configurable "Remind Before Days" | `Remind Before Days` per document / category / global |
| Status tracking | `Status` field per tracker + auto-expiry |
| Ownership assignment | `In-Charge Person` → Link to **User** |
| Attachments | Native Frappe attachments + a primary `Attach` field |
| Tags & Notes | Native Frappe tags + `Description` / `Notes` fields |
| ERPNext sidebar integration | Role-gated **Compliance** workspace |

---

## Requirements

- A Frappe bench (Frappe **v14, v15, or v16**). ERPNext optional.
- Redis + a running scheduler/worker (standard bench setup) for reminders.

### Version compatibility

Verified against the Frappe **v16** API surface. Specifically:

- `pyproject.toml` declares `frappe = ">=14.0.0,<17.0.0"`, so bench accepts the
  app on v16 (the earlier `<16.0.0` bound would have rejected it).
- The `Compliance` workspace JSON sets the **`type: "Workspace"`** field that v16
  made required on the Workspace doctype.
- Tests import the base class through a shim
  ([tests/`__init__`.py](compliance_manager/tests/__init__.py)) that uses v16's
  `frappe.tests.IntegrationTestCase` and falls back to `FrappeTestCase` on
  v14/v15.
- The app launcher permission hook tolerates the v16 call signature.
- No deprecated/removed APIs are used; all type hints are guarded by
  `from __future__ import annotations` (safe on Python 3.10–3.12).

## Installation

```bash
# from your frappe-bench directory
bench get-app compliance_manager /path/to/this/repo   # or: git clone into apps/
bench --site yoursite.local install-app compliance_manager
bench --site yoursite.local migrate
bench restart            # picks up hooks.py + scheduler events
```

Installing seeds two roles, sensible **Compliance Settings** defaults, and a
starter set of **Compliance Categories** (Health/Vehicle/Liability insurance,
Tax Filing, Safety Check, ISO, etc.) so the app is usable immediately.

### Build the web portal (one extra step)

The friendly end-user UI is a Vue 3 single-page app under `frontend/`. Build it
once (and after any frontend change):

```bash
cd apps/compliance_manager/frontend
yarn install        # or: npm install
yarn build          # outputs to ../compliance_manager/public/frontend
                    # and generates ../compliance_manager/www/compliance.html
cd -
bench build --app compliance_manager
bench --site yoursite.local clear-cache
```

For active frontend development with hot reload:

```bash
cd apps/compliance_manager/frontend
yarn dev            # Vite dev server; proxies API calls to your bench
```

---

## Web portal — `/compliance`

The portal is the primary, staff-friendly way to use the app — no Desk knowledge
required. Open **`/compliance`** (the app-launcher tile also points here).

- **Dashboard** — greeting, at-a-glance counts (due in 30 days, overdue, active),
  a card per tracker, and a unified **upcoming & overdue renewals** list.
- **Trackers** — searchable, status-filterable lists for Insurance, Licences,
  Trademarks and Compliance Records with inline **create / edit / delete** in a
  clean dialog (no raw DocType form).
- **Settings** (managers only) — reminder defaults, notification channels,
  escalation, and full **category management**.
- **Auth** — all staff sign in as Frappe users; unauthenticated visits bounce to
  login and return. Users need a **Compliance User** (or Manager) role; the portal
  shows a clear "no access yet" screen otherwise.
- **Branding** — a "trustworthy green" theme (matches the shield logo), defined in
  `frontend/tailwind.config.js` under the `brand` color scale. Change those hex
  values to rebrand; drop a new `public/images/logo.svg` to swap the logo.
- **Mobile-friendly** — responsive sidebar drawer and card layouts.

Design notes: the UI uses **Frappe UI** for the data layer (`createResource`,
`createListResource`, `call`) and self-contained, themable Vue components for the
visuals, so the green branding is exact and the build has no fragile component
dependencies. All four trackers are driven by one config object
([frontend/src/data/trackers.js](compliance_manager/frontend/src/data/trackers.js)) —
adding a tracker is a single edit there plus a registry entry in the backend.

Power users / admins can still use the Desk workspace at **`/app/compliance`**.

Make sure the scheduler is enabled (reminders run once daily):

```bash
bench --site yoursite.local enable-scheduler
bench --site yoursite.local doctor      # verify workers + scheduler
```

---

## The reminder engine

A single daily job (`scheduler_events["daily_long"]` →
`compliance_manager.services.reminders.run_daily_reminders`) does two things for
every tracked record that has reminders enabled:

1. **Auto status update** — once a deadline passes, the item flips to
   `Expired` (insurance / licence / trademark) or `Overdue` (compliance),
   if *Auto-update Status* is on.
2. **Multi-stage reminders** — sends an **Email** and/or **in-app
   notification** to the In-Charge person at each configured milestone before
   the deadline (default `30, 15, 7, 1` days), on the due date, and — optionally
   — on a recurring interval after it (overdue escalation).

**Where the milestones come from** (first match wins):

```
document "Remind Before Days"  →  category default  →  global default  →  30,15,7,1
```

**Idempotent by design.** Every send is recorded in a **Compliance Reminder
Log** keyed by `(record, milestone)`, so re-running the job — or catching up
after downtime — never sends the same stage twice. If several milestones were
missed during downtime, only the *most urgent* crossed milestone is sent and the
older ones are marked superseded (no backfill spam).

**Channels** are toggled in **Compliance Settings**:
Email · In-app notification · Default CC list · Fallback recipient ·
Overdue escalation interval.

Run it on demand (admins / Compliance Managers):

```python
# bench console, or via the whitelisted API
frappe.call("compliance_manager.api.run_reminders_now")
```

> **SMS / WhatsApp** were intentionally left out per your channel selection.
> The dispatcher in `services/reminders.py` (`_dispatch_reminder`) has a clear
> seam to add a third channel later — wire an SMS/WhatsApp provider there and
> add a toggle to Compliance Settings.

---

## Focused experience — hiding everything else

You asked for compliance users to see **only** what this app needs, not the rest
of Frappe/ERPNext. This is achieved with **roles + a role-gated workspace**:

- Two roles ship with the app: **Compliance Manager** (full control) and
  **Compliance User** (create/edit, no delete).
- The **Compliance** workspace is restricted to those roles (and System
  Manager), so it only appears for compliance users.

To give a user the focused view, assign them **only** a compliance role
(no *System Manager*, no module-specific ERPNext roles). Then:

1. Their sidebar shows the **Compliance** workspace and little else, because
   workspaces and DocTypes they have no role for are hidden automatically.
2. Optionally set the Compliance workspace as their landing page via
   **User → Default Workspace**, and clear other default app access under
   **User → Allow Modules** / a **Role Profile** named e.g. "Compliance Only".

> On ERPNext sites, also create a **Role Profile** ("Compliance Only") that
> contains just the two compliance roles and assign it to those users — this is
> the cleanest way to keep Accounting/HR/etc. out of their view.

---

## Data model summary

| DocType | Naming | Key fields | Deadline field |
| --- | --- | --- | --- |
| Insurance Policy | `INS-YYYY-#####` | document_name, insurance_type, issuer, agent_name/contact, in_charge, status | `expiry_date` |
| Licence | `LIC-YYYY-#####` | licence_name, licence_type, issuing_authority, in_charge, status | `expiry_date` |
| Trademark | `TM-YYYY-#####` | brand_name, trademark_class, application_number, vendor, status, follow_ups[] | `valid_till` |
| Compliance Record | `CMP-YYYY-#####` | compliance_name, category, in_charge, status, priority, frequency | `due_date` |
| Compliance Category | by name | category_name, applies_to, default_reminder_days | — |
| Compliance Settings | single | channels, defaults, escalation | — |
| Compliance Reminder Log | hash | reference, milestone, channels (system-generated) | — |

**Compliance Record recurrence:** set `Frequency` to Monthly/Quarterly/
Half-Yearly/Annual and, when you mark an item **Completed**, the next occurrence
is auto-created with the next due date — turning the tracker into a compliance
calendar.

Adding a new tracker later is a one-line entry in
`compliance_manager/utils/reminders_config.py::TRACKED_DOCTYPES`; the reminder
engine is generic over it.

---

## Roles & permissions

| Role | Read | Create | Write | Delete | Settings |
| --- | --- | --- | --- | --- | --- |
| Compliance Manager | ✓ | ✓ | ✓ | ✓ | ✓ |
| Compliance User | ✓ | ✓ | ✓ | ✗ | read-only |
| System Manager | ✓ | ✓ | ✓ | ✓ | ✓ |

---

## Testing

```bash
bench --site yoursite.local run-tests --app compliance_manager
```

Covers reminder-milestone resolution, the end-to-end reminder engine
(send-once / idempotency / auto-expiry), and Compliance Record recurrence.

---

## Why standalone Frappe (and not ERPNext)

Every requested field maps to native Frappe primitives:

- **In-Charge Person** → Link to **User** (Frappe core), not HR `Employee`.
- **Issuer / Supplier**, **Agent**, **Vendor** → plain fields, not ERPNext
  `Supplier`/`Contact`, so no Buying/Selling modules are pulled in.
- Reminders use Frappe's **email queue**, **Notification Log**, and
  **scheduler** — all core.

This keeps the app lightweight and deployable on a bare Frappe site, while still
rendering inside ERPNext for organizations that already run it.

### Later ERPNext integration

If you eventually want native ERPNext links (e.g. In-Charge → `Employee`,
Issuer → `Supplier`), do it additively without breaking standalone installs:

- Add **optional** Link fields guarded by `"erpnext" in frappe.get_installed_apps()`.
- Or ship them as a thin companion app that depends on this one.

No change to the core model is required.

---

## License

MIT © 2026 Tejas Kutnikar
