from compliance_manager.utils.tracker import ComplianceTrackerDocument


class Licence(ComplianceTrackerDocument):
    ISSUE_FIELD = "issue_date"
    DEADLINE_FIELD = "expiry_date"
