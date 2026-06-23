"""Test helpers.

Frappe v16 renamed the standard test base class from ``FrappeTestCase``
(``frappe.tests.utils``) to ``IntegrationTestCase`` (``frappe.tests``). Import
the new name when available and fall back to the old one so the suite runs on
Frappe v14, v15 and v16 alike.
"""

try:  # Frappe v16+
    from frappe.tests import IntegrationTestCase as ComplianceTestCase
except ImportError:  # Frappe v14 / v15
    from frappe.tests.utils import FrappeTestCase as ComplianceTestCase

__all__ = ["ComplianceTestCase"]
