<template>
  <div>
    <label v-if="label" :for="id" class="mb-1 block text-sm font-medium text-gray-700">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>

    <textarea
      v-if="type === 'textarea'"
      :id="id"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      rows="3"
      :class="control"
      @input="emit('update:modelValue', $event.target.value)"
    />

    <select
      v-else-if="type === 'select'"
      :id="id"
      :value="modelValue"
      :disabled="disabled"
      :class="control"
      @change="emit('update:modelValue', $event.target.value)"
    >
      <option value="">— Select —</option>
      <option v-for="opt in normalizedOptions" :key="opt.value" :value="opt.value">
        {{ opt.label }}
      </option>
    </select>

    <label
      v-else-if="type === 'checkbox'"
      class="flex cursor-pointer items-center gap-2.5 rounded-lg border border-gray-200 bg-white px-3 py-2.5"
    >
      <input
        type="checkbox"
        :checked="!!modelValue"
        :disabled="disabled"
        class="h-4 w-4 rounded border-gray-300 text-brand-600 focus:ring-brand-500"
        @change="emit('update:modelValue', $event.target.checked ? 1 : 0)"
      />
      <span class="text-sm text-gray-700">{{ checkboxLabel }}</span>
    </label>

    <input
      v-else
      :id="id"
      :type="type === 'number' ? 'number' : type === 'date' ? 'date' : 'text'"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :class="control"
      @input="emit('update:modelValue', $event.target.value)"
    />

    <p v-if="help && !error" class="mt-1 text-xs text-gray-500">{{ help }}</p>
    <p v-if="error" class="mt-1 text-xs text-red-600">{{ error }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: [String, Number, Boolean],
  label: String,
  type: { type: String, default: 'text' },
  options: { type: Array, default: () => [] },
  placeholder: String,
  help: String,
  error: String,
  required: Boolean,
  disabled: Boolean,
  checkboxLabel: String,
})
const emit = defineEmits(['update:modelValue'])

const id = `f-${Math.random().toString(36).slice(2, 9)}`

const control =
  'w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 placeholder-gray-400 shadow-sm transition focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/30 disabled:bg-gray-50 disabled:text-gray-500'

const normalizedOptions = computed(() =>
  props.options.map((o) => (typeof o === 'string' ? { label: o, value: o } : o)),
)
</script>
