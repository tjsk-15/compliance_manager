<template>
  <component
    :is="to ? 'RouterLink' : 'div'"
    :to="to"
    class="group flex items-center gap-4 rounded-xl border border-gray-200 bg-white p-4 shadow-sm transition"
    :class="to ? 'hover:-translate-y-0.5 hover:border-gray-300 hover:shadow-md' : ''"
  >
    <div class="flex h-11 w-11 items-center justify-center rounded-lg" :class="chip">
      <Icon :name="icon" :size="20" />
    </div>
    <div class="min-w-0">
      <div class="flex items-baseline gap-2">
        <span class="text-2xl font-semibold text-gray-900">{{ value ?? '—' }}</span>
        <span v-if="badge" class="text-xs font-medium" :class="badgeClass">{{ badge }}</span>
      </div>
      <p class="truncate text-sm text-gray-500">{{ label }}</p>
    </div>
  </component>
</template>

<script setup>
import { computed } from 'vue'
import Icon from './Icon.vue'

const props = defineProps({
  label: String,
  value: [Number, String],
  icon: { type: String, default: 'activity' },
  accent: { type: String, default: 'brand' }, // brand | blue | purple | orange | red
  to: [String, Object],
  badge: String,
  badgeTone: { type: String, default: 'gray' }, // gray | red | green
})

const chips = {
  brand: 'bg-brand-50 text-brand-600',
  blue: 'bg-blue-50 text-blue-600',
  purple: 'bg-purple-50 text-purple-600',
  orange: 'bg-orange-50 text-orange-600',
  red: 'bg-red-50 text-red-600',
}
const chip = computed(() => chips[props.accent] || chips.brand)

const badgeClass = computed(
  () =>
    ({
      gray: 'text-gray-400',
      red: 'text-red-600',
      green: 'text-brand-600',
    })[props.badgeTone] || 'text-gray-400',
)
</script>
