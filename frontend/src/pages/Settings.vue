<template>
  <div class="space-y-6">
    <PageHeader
      icon="settings"
      title="Settings"
      subtitle="Reminder defaults, notification channels and compliance categories."
    />

    <div v-if="!session.canManageSettings && !canReadCategories" class="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
      You don't have permission to manage settings or categories.
    </div>

    <template v-else>
      <!-- Reminder & channel settings -->
      <section v-if="session.canManageSettings" class="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
        <h2 class="text-sm font-semibold text-gray-900">Reminders & notifications</h2>
        <p class="mt-0.5 text-sm text-gray-500">How and when renewal reminders are sent.</p>

        <div v-if="loadingSettings" class="flex justify-center py-8">
          <Spinner :size="22" class="text-brand-600" />
        </div>

        <div v-else class="mt-5 grid grid-cols-1 gap-x-5 gap-y-4 sm:grid-cols-2">
          <FormField
            v-model="s.default_reminder_days"
            class="sm:col-span-2"
            label="Default reminder days"
            placeholder="30,15,7,1"
            help="Global milestones (days before deadline). Overridden per-category and per-document."
          />
          <FormField
            v-model="s.send_email"
            type="checkbox"
            label="Email"
            checkbox-label="Send email reminders"
          />
          <FormField
            v-model="s.send_system_notification"
            type="checkbox"
            label="In-app"
            checkbox-label="Send in-app notifications"
          />
          <FormField
            v-model="s.default_cc"
            type="textarea"
            label="Default CC emails"
            placeholder="comma-separated"
          />
          <LinkField
            v-model="s.fallback_recipient"
            label="Fallback recipient"
            doctype="User"
            help="Notified when an item has no In-Charge person."
          />
          <FormField
            v-model="s.auto_update_status"
            type="checkbox"
            label="Status automation"
            checkbox-label="Auto-flip to Expired / Overdue after deadline"
          />
          <FormField
            v-model="s.escalate_after_expiry"
            type="checkbox"
            label="Escalation"
            checkbox-label="Keep reminding after the deadline"
          />
          <FormField
            v-if="s.escalate_after_expiry"
            v-model="s.escalation_interval_days"
            type="number"
            label="Escalation interval (days)"
          />
        </div>

        <div v-if="!loadingSettings" class="mt-5 flex items-center gap-3">
          <Button variant="solid" icon-left="check" :loading="savingSettings" @click="saveSettings">
            Save settings
          </Button>
          <span v-if="settingsSaved" class="text-sm text-brand-600">Saved ✓</span>
        </div>
      </section>

      <!-- Categories -->
      <section v-if="canReadCategories" class="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
        <div class="flex items-center justify-between border-b border-gray-100 px-5 py-3.5">
          <div>
            <h2 class="text-sm font-semibold text-gray-900">Compliance categories</h2>
            <p class="text-sm text-gray-500">Classify items and set per-category reminder defaults.</p>
          </div>
          <Button v-if="canCreateCategory" variant="subtle" icon-left="plus" @click="openCategory()">Add category</Button>
        </div>

        <div v-if="categories.loading && !catRows.length" class="flex justify-center py-10">
          <Spinner :size="22" class="text-brand-600" />
        </div>

        <table v-else class="min-w-full divide-y divide-gray-100">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-5 py-2.5 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">Name</th>
              <th class="px-5 py-2.5 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">Applies To</th>
              <th class="px-5 py-2.5 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">Reminder Days</th>
              <th class="w-16 px-5 py-2.5" />
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="c in catRows" :key="c.name" class="group hover:bg-gray-50">
              <td class="px-5 py-3 text-sm font-medium text-gray-900">
                {{ c.category_name }}
                <span v-if="c.disabled" class="ml-2 rounded bg-gray-100 px-1.5 py-0.5 text-[11px] text-gray-500">disabled</span>
              </td>
              <td class="px-5 py-3 text-sm text-gray-600">{{ c.applies_to }}</td>
              <td class="px-5 py-3 text-sm text-gray-600">{{ c.default_reminder_days || '—' }}</td>
              <td class="px-5 py-3 text-right">
                <div class="flex justify-end gap-1 opacity-0 transition group-hover:opacity-100">
                  <button v-if="canWriteCategory" class="rounded-md p-1.5 text-gray-400 hover:bg-gray-100 hover:text-brand-600" @click="openCategory(c)">
                    <Icon name="edit-2" :size="15" />
                  </button>
                  <button v-if="canDeleteCategory" class="rounded-md p-1.5 text-gray-400 hover:bg-red-50 hover:text-red-600" @click="askDeleteCategory(c)">
                    <Icon name="trash-2" :size="15" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </section>
    </template>

    <!-- Category dialog -->
    <Modal v-model="catOpen" :title="catEditName ? 'Edit category' : 'New category'" size="md">
      <div v-if="catError" class="mb-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{{ catError }}</div>
      <div class="grid grid-cols-1 gap-x-5 gap-y-4 sm:grid-cols-2">
        <FormField v-model="cat.category_name" class="sm:col-span-2" label="Category name" required :disabled="!!catEditName" />
        <FormField v-model="cat.applies_to" type="select" label="Applies to" :options="['All', 'Insurance', 'Compliance', 'Licence', 'Trademark']" required />
        <FormField v-model="cat.default_reminder_days" label="Default reminder days" placeholder="30,15,7,1" />
        <FormField v-model="cat.description" type="textarea" class="sm:col-span-2" label="Description" />
        <FormField v-model="cat.disabled" type="checkbox" label="Status" checkbox-label="Disabled" />
      </div>
      <template #footer>
        <Button variant="outline" @click="catOpen = false">Cancel</Button>
        <Button variant="solid" icon-left="check" :loading="savingCat" @click="saveCategory">Save</Button>
      </template>
    </Modal>

    <ConfirmDialog
      v-model="confirmCatOpen"
      title="Delete category?"
      :message="`Delete “${catDeleteName}”? Items using it will keep their value but lose the link.`"
      confirm-label="Delete"
      danger
      :loading="deletingCat"
      @confirm="doDeleteCategory"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { createListResource, call } from 'frappe-ui'
import PageHeader from '@/components/PageHeader.vue'
import Button from '@/components/Button.vue'
import Icon from '@/components/Icon.vue'
import Spinner from '@/components/Spinner.vue'
import FormField from '@/components/FormField.vue'
import LinkField from '@/components/LinkField.vue'
import Modal from '@/components/Modal.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import { session, can } from '@/data/session'

const canReadCategories = computed(() => can('Compliance Category', 'read'))
const canCreateCategory = computed(() => can('Compliance Category', 'create'))
const canWriteCategory = computed(() => can('Compliance Category', 'write'))
const canDeleteCategory = computed(() => can('Compliance Category', 'delete'))

const SETTINGS = 'Compliance Settings'
const settingsFields = [
  'default_reminder_days', 'send_email', 'send_system_notification', 'default_cc',
  'fallback_recipient', 'auto_update_status', 'escalate_after_expiry', 'escalation_interval_days',
]

const s = reactive({})
let settingsDoc = null
const loadingSettings = ref(true)
const savingSettings = ref(false)
const settingsSaved = ref(false)

async function loadSettings() {
  loadingSettings.value = true
  try {
    settingsDoc = await call('frappe.client.get', { doctype: SETTINGS, name: SETTINGS })
    for (const f of settingsFields) s[f] = settingsDoc[f] ?? ''
  } finally {
    loadingSettings.value = false
  }
}

async function saveSettings() {
  savingSettings.value = true
  settingsSaved.value = false
  try {
    const doc = { ...settingsDoc }
    for (const f of settingsFields) doc[f] = s[f] === '' ? null : s[f]
    settingsDoc = await call('frappe.client.save', { doc })
    settingsSaved.value = true
    setTimeout(() => (settingsSaved.value = false), 2500)
  } finally {
    savingSettings.value = false
  }
}

// Categories
const categories = createListResource({
  doctype: 'Compliance Category',
  fields: ['name', 'category_name', 'applies_to', 'default_reminder_days', 'disabled'],
  orderBy: 'applies_to asc',
  pageLength: 200,
  auto: canReadCategories.value,
})
const catRows = computed(() => categories.data || [])

const catOpen = ref(false)
const catEditName = ref(null)
const savingCat = ref(false)
const catError = ref('')
const cat = reactive({ category_name: '', applies_to: 'All', default_reminder_days: '', description: '', disabled: 0 })

function openCategory(row) {
  catError.value = ''
  catEditName.value = row?.name || null
  cat.category_name = row?.category_name || ''
  cat.applies_to = row?.applies_to || 'All'
  cat.default_reminder_days = row?.default_reminder_days || ''
  cat.description = row?.description || ''
  cat.disabled = row?.disabled || 0
  catOpen.value = true
}

async function saveCategory() {
  catError.value = ''
  if (!cat.category_name.trim()) {
    catError.value = 'Category name is required.'
    return
  }
  savingCat.value = true
  try {
    if (catEditName.value) {
      await call('frappe.client.set_value', {
        doctype: 'Compliance Category',
        name: catEditName.value,
        fieldname: {
          applies_to: cat.applies_to,
          default_reminder_days: cat.default_reminder_days || null,
          description: cat.description || null,
          disabled: cat.disabled ? 1 : 0,
        },
      })
    } else {
      await call('frappe.client.insert', {
        doc: {
          doctype: 'Compliance Category',
          category_name: cat.category_name,
          applies_to: cat.applies_to,
          default_reminder_days: cat.default_reminder_days || null,
          description: cat.description || null,
          disabled: cat.disabled ? 1 : 0,
        },
      })
    }
    catOpen.value = false
    categories.reload()
  } catch (e) {
    catError.value = e?.messages?.[0] || e?.message || 'Could not save category.'
  } finally {
    savingCat.value = false
  }
}

const confirmCatOpen = ref(false)
const catDeleteName = ref(null)
const catDeleteLabel = ref('')
const deletingCat = ref(false)
function askDeleteCategory(row) {
  catDeleteName.value = row.name
  catDeleteLabel.value = row.category_name
  confirmCatOpen.value = true
}
async function doDeleteCategory() {
  deletingCat.value = true
  try {
    await call('frappe.client.delete', { doctype: 'Compliance Category', name: catDeleteName.value })
    confirmCatOpen.value = false
    categories.reload()
  } finally {
    deletingCat.value = false
  }
}

onMounted(() => {
  if (session.canManageSettings) loadSettings()
})
</script>
