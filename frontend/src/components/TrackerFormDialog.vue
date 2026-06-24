<template>
  <Modal
    :model-value="modelValue"
    :title="name ? `Edit ${tracker.singular}` : `New ${tracker.singular}`"
    :subtitle="name || 'Fill in the details below'"
    size="lg"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <div v-if="loading" class="flex items-center justify-center py-12 text-gray-400">
      <Spinner :size="24" class="text-brand-600" />
    </div>

    <template v-else>
      <div
        v-if="errorMsg"
        class="mb-4 flex items-start gap-2 rounded-lg bg-red-50 px-3 py-2.5 text-sm text-red-700"
      >
        <Icon name="alert-circle" :size="16" class="mt-0.5 shrink-0" />
        <span>{{ errorMsg }}</span>
      </div>

      <div class="grid grid-cols-1 gap-x-5 gap-y-4 sm:grid-cols-2">
        <div
          v-for="f in tracker.form"
          :key="f.field"
          :class="f.span === 2 ? 'sm:col-span-2' : ''"
        >
          <LinkField
            v-if="f.type === 'link'"
            v-model="form[f.field]"
            :label="f.label"
            :doctype="f.doctype"
            :filters="f.filters || {}"
            :required="f.required"
            :placeholder="f.placeholder"
            :help="f.help"
          />
          <FormField
            v-else
            v-model="form[f.field]"
            :label="f.label"
            :type="f.type"
            :options="f.options || []"
            :required="f.required"
            :placeholder="f.placeholder"
            :help="f.help"
            :error="errors[f.field]"
          />
        </div>
      </div>
    </template>

    <template #footer>
      <Button variant="outline" @click="$emit('update:modelValue', false)">Cancel</Button>
      <Button variant="solid" icon-left="check" :loading="saving" @click="save">
        {{ name ? 'Save changes' : `Create ${tracker.singular}` }}
      </Button>
    </template>
  </Modal>
</template>

<script setup>
import { reactive, ref, watch } from 'vue'
import { call } from 'frappe-ui'
import Modal from './Modal.vue'
import Button from './Button.vue'
import FormField from './FormField.vue'
import LinkField from './LinkField.vue'
import Icon from './Icon.vue'
import Spinner from './Spinner.vue'

const props = defineProps({
  modelValue: Boolean,
  tracker: { type: Object, required: true },
  name: String, // present => edit mode
})
const emit = defineEmits(['update:modelValue', 'saved'])

const form = reactive({})
const errors = reactive({})
const loading = ref(false)
const saving = ref(false)
const errorMsg = ref('')
let loadedDoc = null

function blankForm() {
  loadedDoc = null
  for (const k of Object.keys(form)) delete form[k]
  for (const k of Object.keys(errors)) delete errors[k]
  errorMsg.value = ''
  for (const f of props.tracker.form) form[f.field] = ''
  // Sensible default for the required status field.
  const statusField = props.tracker.form.find((f) => f.field === 'status')
  if (statusField?.options?.length) form.status = statusField.options[0]
}

async function loadDoc() {
  loading.value = true
  try {
    loadedDoc = await call('frappe.client.get', {
      doctype: props.tracker.doctype,
      name: props.name,
    })
    for (const f of props.tracker.form) {
      form[f.field] = loadedDoc[f.field] ?? ''
    }
  } catch (e) {
    errorMsg.value = readError(e)
  } finally {
    loading.value = false
  }
}

function validate() {
  for (const k of Object.keys(errors)) delete errors[k]
  let ok = true
  for (const f of props.tracker.form) {
    if (f.required && !String(form[f.field] ?? '').trim()) {
      errors[f.field] = `${f.label} is required`
      ok = false
    }
  }
  return ok
}

async function save() {
  errorMsg.value = ''
  if (!validate()) return
  saving.value = true
  try {
    if (props.name) {
      const doc = { ...loadedDoc }
      for (const f of props.tracker.form) doc[f.field] = form[f.field] === '' ? null : form[f.field]
      await call('frappe.client.save', { doc })
    } else {
      const doc = { doctype: props.tracker.doctype }
      for (const f of props.tracker.form) {
        const v = form[f.field]
        if (v !== '' && v !== null && v !== undefined) doc[f.field] = v
      }
      await call('frappe.client.insert', { doc })
    }
    emit('saved')
    emit('update:modelValue', false)
  } catch (e) {
    errorMsg.value = readError(e)
  } finally {
    saving.value = false
  }
}

function readError(e) {
  const msgs = e?.messages || e?._server_messages
  if (Array.isArray(msgs) && msgs.length) {
    try {
      const parsed = typeof msgs[0] === 'string' && msgs[0].startsWith('{') ? JSON.parse(msgs[0]) : null
      return parsed?.message || msgs[0]
    } catch {
      return msgs[0]
    }
  }
  return e?.message || 'Something went wrong. Please check the fields and try again.'
}

watch(
  () => props.modelValue,
  (open) => {
    if (!open) return
    if (props.name) loadDoc()
    else blankForm()
  },
)
</script>
