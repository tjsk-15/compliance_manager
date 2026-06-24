<template>
  <div ref="root" class="relative">
    <label v-if="label" class="mb-1 block text-sm font-medium text-gray-700">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>

    <button
      type="button"
      :class="control"
      @click="toggle"
    >
      <span class="truncate" :class="displayLabel ? 'text-gray-900' : 'text-gray-400'">
        {{ displayLabel || placeholder || 'Select…' }}
      </span>
      <span class="ml-2 flex items-center gap-1">
        <Icon
          v-if="modelValue"
          name="x"
          :size="14"
          class="text-gray-400 hover:text-gray-600"
          @click.stop="clear"
        />
        <Icon name="chevron-down" :size="16" class="text-gray-400" />
      </span>
    </button>

    <div
      v-if="open"
      class="absolute z-30 mt-1 w-full overflow-hidden rounded-lg border border-gray-200 bg-white shadow-lg"
    >
      <div class="border-b border-gray-100 p-2">
        <input
          ref="searchInput"
          v-model="query"
          placeholder="Search…"
          class="w-full rounded-md border border-gray-200 px-2.5 py-1.5 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500/30"
        />
      </div>
      <ul class="max-h-56 overflow-y-auto py-1">
        <li v-if="loading" class="px-3 py-2 text-sm text-gray-400">Loading…</li>
        <li
          v-for="opt in filtered"
          :key="opt.value"
          class="flex cursor-pointer items-center justify-between gap-2 px-3 py-2 text-sm hover:bg-brand-50"
          :class="opt.value === modelValue ? 'bg-brand-50 text-brand-700' : 'text-gray-700'"
          @click="select(opt)"
        >
          <span class="truncate">{{ opt.label }}</span>
          <span v-if="opt.description && opt.description !== opt.label" class="truncate text-xs text-gray-400">
            {{ opt.description }}
          </span>
        </li>
        <li v-if="!loading && filtered.length === 0" class="px-3 py-2 text-sm text-gray-400">
          No matches
        </li>
      </ul>
    </div>

    <p v-if="help" class="mt-1 text-xs text-gray-500">{{ help }}</p>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { call } from 'frappe-ui'
import Icon from './Icon.vue'

const props = defineProps({
  modelValue: String,
  label: String,
  doctype: { type: String, required: true },
  filters: { type: Object, default: () => ({}) },
  required: Boolean,
  placeholder: String,
  help: String,
})
const emit = defineEmits(['update:modelValue'])

const root = ref(null)
const searchInput = ref(null)
const open = ref(false)
const loading = ref(false)
const query = ref('')
const options = ref([])

const control =
  'flex w-full items-center justify-between rounded-lg border border-gray-300 bg-white px-3 py-2 text-left text-sm shadow-sm transition focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/30'

const displayLabel = computed(() => {
  if (!props.modelValue) return ''
  const found = options.value.find((o) => o.value === props.modelValue)
  return found ? found.label : props.modelValue
})

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return options.value
  return options.value.filter(
    (o) =>
      o.label.toLowerCase().includes(q) ||
      (o.description || '').toLowerCase().includes(q),
  )
})

async function load() {
  loading.value = true
  try {
    options.value = await call('compliance_manager.api.get_link_options', {
      doctype: props.doctype,
      filters: props.filters || {},
    })
  } catch (e) {
    options.value = []
  } finally {
    loading.value = false
  }
}

function toggle() {
  open.value = !open.value
  if (open.value) {
    if (!options.value.length) load()
    nextTick(() => searchInput.value?.focus())
  }
}

function select(opt) {
  emit('update:modelValue', opt.value)
  open.value = false
  query.value = ''
}

function clear() {
  emit('update:modelValue', '')
}

function onClickOutside(e) {
  if (root.value && !root.value.contains(e.target)) open.value = false
}

// Preload so the selected label resolves on edit.
onMounted(() => {
  load()
  document.addEventListener('click', onClickOutside)
})
onUnmounted(() => document.removeEventListener('click', onClickOutside))

watch(
  () => JSON.stringify(props.filters),
  () => {
    options.value = []
    load()
  },
)
</script>
