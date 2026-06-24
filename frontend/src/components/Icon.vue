<template>
  <span class="inline-flex shrink-0 items-center justify-center" v-html="svg" />
</template>

<script setup>
import feather from 'feather-icons'
import { computed } from 'vue'

const props = defineProps({
  name: { type: String, required: true },
  size: { type: [Number, String], default: 18 },
  strokeWidth: { type: [Number, String], default: 2 },
})

const svg = computed(() => {
  const icon = feather.icons[props.name] || feather.icons['help-circle']
  return icon.toSvg({
    width: props.size,
    height: props.size,
    'stroke-width': props.strokeWidth,
  })
})
</script>
