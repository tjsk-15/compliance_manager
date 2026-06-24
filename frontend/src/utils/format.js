// Date + status formatting helpers shared across the portal.

export function formatDate(value, opts = {}) {
  if (!value) return '—'
  const d = new Date(value + 'T00:00:00')
  if (isNaN(d)) return value
  return d.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    ...opts,
  })
}

export function daysUntil(value) {
  if (!value) return null
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const d = new Date(value + 'T00:00:00')
  return Math.round((d - today) / 86400000)
}

// Human, urgency-aware label for a deadline: "in 5 days", "today", "3 days ago".
export function deadlineLabel(value) {
  const n = daysUntil(value)
  if (n === null) return '—'
  if (n === 0) return 'Due today'
  if (n === 1) return 'Tomorrow'
  if (n === -1) return 'Yesterday'
  if (n > 1) return `In ${n} days`
  return `${Math.abs(n)} days ago`
}

// Tailwind classes for the urgency pill next to a date.
export function urgencyClasses(value) {
  const n = daysUntil(value)
  if (n === null) return 'text-gray-400'
  if (n < 0) return 'text-red-600 font-medium'
  if (n <= 7) return 'text-orange-600 font-medium'
  if (n <= 30) return 'text-amber-600'
  return 'text-gray-500'
}

const STATUS_COLORS = {
  // shared status -> color key
  Active: 'green',
  Renewing: 'amber',
  Registered: 'green',
  Advertised: 'blue',
  Filed: 'gray',
  Completed: 'green',
  'In Progress': 'blue',
  Pending: 'amber',
  Expired: 'red',
  Overdue: 'red',
}

const COLOR_CLASSES = {
  green: 'bg-brand-50 text-brand-700 ring-brand-600/20',
  amber: 'bg-amber-50 text-amber-700 ring-amber-600/20',
  orange: 'bg-orange-50 text-orange-700 ring-orange-600/20',
  blue: 'bg-blue-50 text-blue-700 ring-blue-600/20',
  red: 'bg-red-50 text-red-700 ring-red-600/20',
  gray: 'bg-gray-100 text-gray-600 ring-gray-500/20',
}

export function statusClasses(status) {
  const color = STATUS_COLORS[status] || 'gray'
  return COLOR_CLASSES[color] || COLOR_CLASSES.gray
}

export function initials(name) {
  if (!name) return '?'
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((p) => p[0].toUpperCase())
    .join('')
}
