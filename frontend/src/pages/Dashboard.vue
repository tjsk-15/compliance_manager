<template>
  <div class="space-y-6">
    <!-- Greeting -->
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-xl font-semibold tracking-tight text-gray-900">
          {{ greeting }}, {{ firstName }}
        </h1>
        <p class="mt-0.5 text-sm text-gray-500">{{ today }} · here's what needs your attention.</p>
      </div>
      <div class="flex items-center gap-2">
        <Button variant="ghost" icon-left="refresh-cw" :loading="loading" @click="load">
          Refresh
        </Button>
        <Button
          v-if="session.isManager"
          variant="outline"
          icon-left="bell"
          :loading="runningReminders"
          @click="runReminders"
        >
          Run reminders now
        </Button>
      </div>
    </div>

    <p v-if="reminderResult" class="rounded-lg bg-brand-50 px-3 py-2 text-sm text-brand-700">
      {{ reminderResult }}
    </p>

    <!-- Highlights -->
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <StatCard label="Due in next 30 days" :value="totals.expiring30" icon="calendar" accent="orange" />
      <StatCard
        label="Overdue / expired"
        :value="totals.overdue"
        icon="alert-triangle"
        accent="red"
      />
      <StatCard label="Items tracked" :value="totals.tracked" icon="check-circle" accent="brand" />
    </div>

    <!-- Per-tracker -->
    <div>
      <h2 class="mb-3 text-sm font-semibold text-gray-700">Trackers</h2>
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          v-for="t in trackerList"
          :key="t.key"
          :label="t.label"
          :value="summary[t.key]?.total ?? 0"
          :icon="t.icon"
          :accent="t.accent === 'brand' ? 'brand' : t.accent"
          :to="t.path"
          :badge="badgeFor(summary[t.key])"
          :badge-tone="summary[t.key]?.overdue ? 'red' : 'gray'"
        />
      </div>
    </div>

    <!-- Upcoming renewals -->
    <div class="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
      <div class="flex items-center justify-between border-b border-gray-100 px-5 py-3.5">
        <h2 class="text-sm font-semibold text-gray-900">Upcoming & overdue renewals</h2>
        <span class="text-xs text-gray-400">next 60 days</span>
      </div>

      <div v-if="loading" class="flex justify-center py-12">
        <Spinner :size="24" class="text-brand-600" />
      </div>

      <div v-else-if="!renewals.length" class="px-5 py-12 text-center">
        <div class="mx-auto flex h-11 w-11 items-center justify-center rounded-full bg-brand-50 text-brand-600">
          <Icon name="check" :size="20" />
        </div>
        <p class="mt-3 text-sm font-medium text-gray-900">All clear</p>
        <p class="text-sm text-gray-500">Nothing is due in the next 60 days.</p>
      </div>

      <ul v-else class="divide-y divide-gray-100">
        <li
          v-for="r in renewals"
          :key="r.doctype + r.name"
          class="flex cursor-pointer items-center gap-4 px-5 py-3 transition hover:bg-gray-50"
          @click="goTo(r)"
        >
          <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg" :class="chipFor(r.tracker)">
            <Icon :name="iconFor(r.tracker)" :size="17" />
          </div>
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm font-medium text-gray-900">{{ r.title || r.name }}</p>
            <p class="truncate text-xs text-gray-500">{{ r.tracker_label }} · {{ formatDate(r.date) }}</p>
          </div>
          <StatusBadge :status="r.status" />
          <span class="hidden w-24 text-right text-xs font-medium sm:block" :class="urgencyClasses(r.date)">
            {{ deadlineLabel(r.date) }}
          </span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { call } from 'frappe-ui'
import StatCard from '@/components/StatCard.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import Button from '@/components/Button.vue'
import Icon from '@/components/Icon.vue'
import Spinner from '@/components/Spinner.vue'
import { trackerList, getTracker } from '@/data/trackers'
import { session } from '@/data/session'
import { formatDate, deadlineLabel, urgencyClasses } from '@/utils/format'

const router = useRouter()
const summary = ref({})
const renewals = ref([])
const loading = ref(true)
const runningReminders = ref(false)
const reminderResult = ref('')

const firstName = computed(() => (session.fullName || 'there').split(' ')[0])
const today = computed(() =>
  new Date().toLocaleDateString(undefined, { weekday: 'long', month: 'long', day: 'numeric' }),
)
const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 12) return 'Good morning'
  if (h < 18) return 'Good afternoon'
  return 'Good evening'
})

const totals = computed(() => {
  const vals = Object.values(summary.value)
  return {
    expiring30: vals.reduce((s, v) => s + (v.expiring_30d || 0), 0),
    overdue: vals.reduce((s, v) => s + (v.overdue || 0), 0),
    tracked: vals.reduce((s, v) => s + (v.total || 0), 0),
  }
})

function badgeFor(s) {
  if (!s) return ''
  if (s.overdue) return `${s.overdue} overdue`
  if (s.expiring_30d) return `${s.expiring_30d} due soon`
  return ''
}
function iconFor(key) {
  return getTracker(key)?.icon || 'file-text'
}
const chips = {
  insurance: 'bg-brand-50 text-brand-600',
  licence: 'bg-blue-50 text-blue-600',
  trademark: 'bg-purple-50 text-purple-600',
  compliance: 'bg-orange-50 text-orange-600',
}
function chipFor(key) {
  return chips[key] || 'bg-gray-100 text-gray-600'
}
function goTo(r) {
  router.push(getTracker(r.tracker)?.path || '/')
}

async function runReminders() {
  runningReminders.value = true
  reminderResult.value = ''
  try {
    const res = await call('compliance_manager.api.run_reminders_now')
    const sent = Object.values(res || {}).reduce((s, v) => s + (v.reminders_sent || 0), 0)
    reminderResult.value = `Reminder run complete — ${sent} reminder(s) sent.`
    load()
  } catch (e) {
    reminderResult.value = 'Could not run reminders. Check the error log.'
  } finally {
    runningReminders.value = false
  }
}

async function load() {
  loading.value = true
  try {
    const [s, r] = await Promise.all([
      call('compliance_manager.api.get_expiry_summary'),
      call('compliance_manager.api.get_upcoming_renewals', { days: 60, include_overdue: 1 }),
    ])
    summary.value = s || {}
    renewals.value = r || []
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
