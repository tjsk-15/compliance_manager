// One config object per tracker drives navigation, list columns and the
// create/edit form — mirroring the backend `TRACKED_DOCTYPES` registry so the
// UI stays consistent and adding a tracker is a single edit here.

const REMIND_HELP = 'Days before the deadline to remind, e.g. 30,15,7,1. Blank = use the category/global default.'

export const trackers = {
  insurance: {
    key: 'insurance',
    doctype: 'Insurance Policy',
    label: 'Insurance Policies',
    singular: 'Insurance Policy',
    icon: 'shield',
    accent: 'brand',
    titleField: 'document_name',
    dateField: 'expiry_date',
    dateLabel: 'Expiry',
    listFields: [
      'name', 'document_name', 'insurance_type', 'issuer',
      'expiry_date', 'status', 'in_charge',
    ],
    columns: [
      { field: 'document_name', label: 'Policy', primary: true },
      { field: 'insurance_type', label: 'Type' },
      { field: 'issuer', label: 'Provider', hideOnMobile: true },
      { field: 'expiry_date', label: 'Expiry', type: 'date' },
      { field: 'status', label: 'Status', type: 'status' },
    ],
    form: [
      { field: 'document_name', label: 'Document Name', type: 'text', required: true, span: 2 },
      { field: 'insurance_type', label: 'Type', type: 'link', doctype: 'Compliance Category', filters: { applies_to: ['in', ['Insurance', 'All']], disabled: 0 } },
      { field: 'status', label: 'Status', type: 'select', options: ['Active', 'Renewing', 'Expired'] },
      { field: 'issuer', label: 'Issuer / Provider', type: 'text' },
      { field: 'policy_number', label: 'Policy Number', type: 'text' },
      { field: 'agent_name', label: 'Agent Name', type: 'text' },
      { field: 'agent_contact', label: 'Agent Contact', type: 'text' },
      { field: 'in_charge', label: 'In-Charge Person', type: 'link', doctype: 'User', labelField: 'full_name' },
      { field: 'issue_date', label: 'Issue Date', type: 'date' },
      { field: 'expiry_date', label: 'Expiry Date', type: 'date', required: true },
      { field: 'reminder_days_before', label: 'Remind Before (days)', type: 'text', placeholder: '30,15,7,1', help: REMIND_HELP, span: 2 },
      { field: 'description', label: 'Description', type: 'textarea', span: 2 },
      { field: 'notes', label: 'Notes', type: 'textarea', span: 2 },
    ],
  },

  licence: {
    key: 'licence',
    doctype: 'Licence',
    label: 'Licences',
    singular: 'Licence',
    icon: 'award',
    accent: 'blue',
    titleField: 'licence_name',
    dateField: 'expiry_date',
    dateLabel: 'Expiry',
    listFields: [
      'name', 'licence_name', 'licence_type', 'issuing_authority',
      'expiry_date', 'status', 'in_charge',
    ],
    columns: [
      { field: 'licence_name', label: 'Licence', primary: true },
      { field: 'licence_type', label: 'Type' },
      { field: 'issuing_authority', label: 'Authority', hideOnMobile: true },
      { field: 'expiry_date', label: 'Expiry', type: 'date' },
      { field: 'status', label: 'Status', type: 'status' },
    ],
    form: [
      { field: 'licence_name', label: 'Licence Name', type: 'text', required: true, span: 2 },
      { field: 'licence_type', label: 'Type', type: 'link', doctype: 'Compliance Category', filters: { applies_to: ['in', ['Licence', 'All']], disabled: 0 } },
      { field: 'status', label: 'Status', type: 'select', options: ['Active', 'Renewing', 'Expired'] },
      { field: 'issuing_authority', label: 'Issuing Authority', type: 'text' },
      { field: 'licence_number', label: 'Licence Number', type: 'text' },
      { field: 'in_charge', label: 'In-Charge Person', type: 'link', doctype: 'User', labelField: 'full_name' },
      { field: 'issue_date', label: 'Issue Date', type: 'date' },
      { field: 'expiry_date', label: 'Expiry Date', type: 'date', required: true },
      { field: 'reminder_days_before', label: 'Remind Before (days)', type: 'text', placeholder: '60,30,15,7', help: REMIND_HELP, span: 2 },
      { field: 'description', label: 'Description', type: 'textarea', span: 2 },
      { field: 'notes', label: 'Notes', type: 'textarea', span: 2 },
    ],
  },

  trademark: {
    key: 'trademark',
    doctype: 'Trademark',
    label: 'Trademarks',
    singular: 'Trademark',
    icon: 'bookmark',
    accent: 'purple',
    titleField: 'brand_name',
    dateField: 'valid_till',
    dateLabel: 'Valid Till',
    listFields: [
      'name', 'brand_name', 'trademark_class', 'application_number',
      'valid_till', 'status', 'in_charge',
    ],
    columns: [
      { field: 'brand_name', label: 'Brand', primary: true },
      { field: 'application_number', label: 'Application #', hideOnMobile: true },
      { field: 'trademark_class', label: 'Class / Type' },
      { field: 'valid_till', label: 'Valid Till', type: 'date' },
      { field: 'status', label: 'Status', type: 'status' },
    ],
    form: [
      { field: 'brand_name', label: 'Brand Name', type: 'text', required: true },
      { field: 'trade_name', label: 'Trade Name', type: 'text' },
      { field: 'trademark_class', label: 'Class / Type', type: 'link', doctype: 'Compliance Category', filters: { applies_to: ['in', ['Trademark', 'All']], disabled: 0 } },
      { field: 'nice_class', label: 'Class Number', type: 'text' },
      { field: 'application_number', label: 'Application Number', type: 'text' },
      { field: 'status', label: 'Status', type: 'select', options: ['Filed', 'Advertised', 'Registered', 'Expired'] },
      { field: 'vendor_name', label: 'Vendor / Agent', type: 'text' },
      { field: 'vendor_contact', label: 'Vendor Contact', type: 'text' },
      { field: 'in_charge', label: 'In-Charge Person', type: 'link', doctype: 'User', labelField: 'full_name' },
      { field: 'followup_status', label: 'Follow-Up Status', type: 'text' },
      { field: 'application_date', label: 'Application Date', type: 'date' },
      { field: 'issue_date', label: 'Registration Date', type: 'date' },
      { field: 'valid_till', label: 'Valid Till', type: 'date' },
      { field: 'reminder_days_before', label: 'Remind Before (days)', type: 'text', placeholder: '90,60,30,15', help: REMIND_HELP, span: 2 },
      { field: 'description', label: 'Description', type: 'textarea', span: 2 },
      { field: 'notes', label: 'Notes', type: 'textarea', span: 2 },
    ],
  },

  compliance: {
    key: 'compliance',
    doctype: 'Compliance Record',
    label: 'Compliance Records',
    singular: 'Compliance Record',
    icon: 'check-circle',
    accent: 'orange',
    titleField: 'compliance_name',
    dateField: 'due_date',
    dateLabel: 'Due',
    listFields: [
      'name', 'compliance_name', 'category', 'priority',
      'due_date', 'status', 'in_charge',
    ],
    columns: [
      { field: 'compliance_name', label: 'Item', primary: true },
      { field: 'category', label: 'Category' },
      { field: 'priority', label: 'Priority', hideOnMobile: true },
      { field: 'due_date', label: 'Due', type: 'date' },
      { field: 'status', label: 'Status', type: 'status' },
    ],
    form: [
      { field: 'compliance_name', label: 'Compliance Name', type: 'text', required: true, span: 2 },
      { field: 'category', label: 'Category', type: 'link', doctype: 'Compliance Category', filters: { applies_to: ['in', ['Compliance', 'All']], disabled: 0 } },
      { field: 'status', label: 'Status', type: 'select', options: ['Pending', 'In Progress', 'Completed', 'Overdue'] },
      { field: 'priority', label: 'Priority', type: 'select', options: ['Low', 'Medium', 'High'] },
      { field: 'frequency', label: 'Frequency', type: 'select', options: ['One-time', 'Monthly', 'Quarterly', 'Half-Yearly', 'Annual'], help: 'Recurring items auto-create the next occurrence when completed.' },
      { field: 'in_charge', label: 'In-Charge Person', type: 'link', doctype: 'User', labelField: 'full_name' },
      { field: 'due_date', label: 'Due Date', type: 'date', required: true },
      { field: 'completion_date', label: 'Completion Date', type: 'date' },
      { field: 'reminder_days_before', label: 'Remind Before (days)', type: 'text', placeholder: '30,15,7,3,1', help: REMIND_HELP, span: 2 },
      { field: 'description', label: 'Description', type: 'textarea', span: 2 },
      { field: 'notes', label: 'Notes', type: 'textarea', span: 2 },
    ],
  },
}

export const trackerPaths = {
  insurance: '/insurance',
  licence: '/licence',
  trademark: '/trademark',
  compliance: '/compliance-records',
}

export const trackerList = Object.values(trackers).map((t) => ({
  ...t,
  path: trackerPaths[t.key],
}))

export function getTracker(key) {
  return trackers[key]
}

export function trackerPath(key) {
  return trackerPaths[key]
}
