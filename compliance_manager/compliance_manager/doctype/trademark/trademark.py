from compliance_manager.utils.tracker import ComplianceTrackerDocument


class Trademark(ComplianceTrackerDocument):
    ISSUE_FIELD = "issue_date"
    DEADLINE_FIELD = "valid_till"
