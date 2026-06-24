<template>
  <div class="flex flex-col items-center justify-center rounded-xl border border-dashed border-gray-300 bg-white px-6 py-14 text-center">
    <div class="flex h-12 w-12 items-center justify-center rounded-full bg-brand-50 text-brand-600">
      <Icon :name="icon" :size="22" />
    </div>
    <h3 class="mt-4 text-sm font-semibold text-gray-900">{{ title }}</h3>
    <p v-if="message" class="mt-1 max-w-sm text-sm text-gray-500">{{ message }}</p>
    <div v-if="$slots.action" class="mt-5">
      <slot name="action" />
    </div>
  </div>
</template>

<script setup>
import Icon from './Icon.vue'

defineProps({
  icon: { type: String, default: 'inbox' },
  title: String,
  message: String,
})
</script>
