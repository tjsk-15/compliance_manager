<template>
  <span
    class="inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset"
    :class="classes"
  >
    <span class="h-1.5 w-1.5 rounded-full bg-current opacity-70" />
    {{ status }}
  </span>
</template>

<script setup>
import { computed } from 'vue'
import { statusClasses } from '@/utils/format'

const props = defineProps({ status: String })
const classes = computed(() => statusClasses(props.status))
</script>
