<template>
  <div class="space-y-5">
    <PageHeader :icon="tracker.icon" :title="tracker.label" :subtitle="subtitle">
      <template #actions>
        <Button v-if="canCreate" variant="solid" icon-left="plus" @click="openNew">
          New {{ tracker.singular }}
        </Button>
      </template>
    </PageHeader>

    <!-- Toolbar -->
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center">
      <div class="relative flex-1">
        <span class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
          <Icon name="search" :size="16" />
        </span>
        <input
          v-model="search"
          :placeholder="`Search ${tracker.label.toLowerCase()}…`"
          class="w-full rounded-lg border border-gray-300 bg-white py-2 pl-9 pr-3 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/30"
          @input="debouncedApply"
        />
      </div>
      <div class="flex items-center gap-1 overflow-x-auto">
        <button
          v-for="opt in statusFilters"
          :key="opt"
          class="whitespace-nowrap rounded-lg px-3 py-1.5 text-sm font-medium transition"
          :class="statusFilter === opt ? 'bg-brand-600 text-white' : 'bg-white text-gray-600 ring-1 ring-gray-200 hover:bg-gray-50'"
          @click="setStatus(opt)"
        >
          {{ opt }}
        </button>
      </div>
    </div>

    <!-- Content -->
    <div v-if="list.loading && !rows.length" class="flex justify-center py-16">
      <Spinner :size="26" class="text-brand-600" />
    </div>

    <EmptyState
      v-else-if="!rows.length"
      :icon="tracker.icon"
      :title="`No ${tracker.label.toLowerCase()} yet`"
      :message="search || statusFilter !== 'All' ? 'No records match your filters.' : `Add your first ${tracker.singular.toLowerCase()} to start tracking renewals.`"
    >
      <template v-if="canCreate && !search && statusFilter === 'All'" #action>
        <Button variant="solid" icon-left="plus" @click="openNew">New {{ tracker.singular }}</Button>
      </template>
    </EmptyState>

    <template v-else>
      <TrackerTable
        :tracker="tracker"
        :rows="rows"
        :can-delete="canDelete"
        @edit="openEdit"
        @delete="askDelete"
      />
      <div v-if="list.hasNextPage" class="flex justify-center pt-1">
        <Button variant="outline" :loading="list.loading" @click="list.next()">Load more</Button>
      </div>
    </template>

    <TrackerFormDialog
      v-model="formOpen"
      :tracker="tracker"
      :name="editName"
      :read-only="!canWrite"
      @saved="onSaved"
    />

    <ConfirmDialog
      v-model="confirmOpen"
      title="Delete record?"
      :message="`This will permanently delete “${deleteName}”. This cannot be undone.`"
      confirm-label="Delete"
      danger
      :loading="deleting"
      @confirm="doDelete"
    />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { createListResource, call } from 'frappe-ui'
import PageHeader from '@/components/PageHeader.vue'
import Button from '@/components/Button.vue'
import Icon from '@/components/Icon.vue'
import Spinner from '@/components/Spinner.vue'
import EmptyState from '@/components/EmptyState.vue'
import TrackerTable from '@/components/TrackerTable.vue'
import TrackerFormDialog from '@/components/TrackerFormDialog.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import { getTracker } from '@/data/trackers'
import { can } from '@/data/session'

const route = useRoute()
const tracker = getTracker(route.meta.tracker)

const canCreate = computed(() => can(tracker.doctype, 'create'))
const canWrite = computed(() => can(tracker.doctype, 'write'))
const canDelete = computed(() => can(tracker.doctype, 'delete'))

const search = ref('')
const statusFilter = ref('All')
const statusFilters = ['All', ...(tracker.form.find((f) => f.field === 'status')?.options || [])]

const list = createListResource({
  doctype: tracker.doctype,
  fields: tracker.listFields,
  orderBy: `${tracker.dateField} asc`,
  pageLength: 20,
  auto: true,
})

const rows = computed(() => list.data || [])
const subtitle = computed(() => {
  const n = rows.value.length
  return list.loading ? 'Loading…' : `${n}${list.hasNextPage ? '+' : ''} record${n === 1 ? '' : 's'}`
})

function buildFilters() {
  const filters = {}
  if (statusFilter.value !== 'All') filters[tracker.statusField || 'status'] = statusFilter.value
  if (search.value.trim()) filters[tracker.titleField] = ['like', `%${search.value.trim()}%`]
  return filters
}

function applyFilters() {
  list.update({ filters: buildFilters() })
  list.reload()
}

let t
function debouncedApply() {
  clearTimeout(t)
  t = setTimeout(applyFilters, 300)
}

function setStatus(opt) {
  statusFilter.value = opt
  applyFilters()
}

// CRUD dialogs
const formOpen = ref(false)
const editName = ref(null)
function openNew() {
  editName.value = null
  formOpen.value = true
}
function openEdit(name) {
  editName.value = name
  formOpen.value = true
}
function onSaved() {
  list.reload()
}

const confirmOpen = ref(false)
const deleteName = ref(null)
const deleting = ref(false)
function askDelete(name) {
  deleteName.value = name
  confirmOpen.value = true
}
async function doDelete() {
  deleting.value = true
  try {
    await call('frappe.client.delete', { doctype: tracker.doctype, name: deleteName.value })
    confirmOpen.value = false
    list.reload()
  } finally {
    deleting.value = false
  }
}
</script>
