<template>
  <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
    <div class="flex items-center gap-3">
      <div
        v-if="icon"
        class="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-50 text-brand-600"
      >
        <Icon :name="icon" :size="20" />
      </div>
      <div>
        <h1 class="text-xl font-semibold tracking-tight text-gray-900">{{ title }}</h1>
        <p v-if="subtitle" class="mt-0.5 text-sm text-gray-500">{{ subtitle }}</p>
      </div>
    </div>
    <div v-if="$slots.actions" class="flex items-center gap-2">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup>
import Icon from './Icon.vue'

defineProps({
  title: String,
  subtitle: String,
  icon: String,
})
</script>
