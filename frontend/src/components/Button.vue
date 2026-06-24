<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :class="[base, sizes[size], variants[variant], block ? 'w-full' : '']"
  >
    <Spinner v-if="loading" :size="size === 'sm' ? 14 : 16" />
    <Icon v-else-if="iconLeft" :name="iconLeft" :size="size === 'sm' ? 15 : 17" />
    <span v-if="$slots.default"><slot /></span>
    <Icon v-if="iconRight && !loading" :name="iconRight" :size="size === 'sm' ? 15 : 17" />
  </button>
</template>

<script setup>
import Icon from './Icon.vue'
import Spinner from './Spinner.vue'

defineProps({
  variant: { type: String, default: 'solid' }, // solid | subtle | outline | ghost | danger | white
  size: { type: String, default: 'md' }, // sm | md | lg
  type: { type: String, default: 'button' },
  iconLeft: String,
  iconRight: String,
  loading: Boolean,
  disabled: Boolean,
  block: Boolean,
})

const base =
  'inline-flex items-center justify-center gap-1.5 rounded-lg font-medium transition focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-500/40 focus-visible:ring-offset-1 disabled:opacity-50 disabled:cursor-not-allowed select-none'

const sizes = {
  sm: 'h-8 px-3 text-xs',
  md: 'h-9 px-3.5 text-sm',
  lg: 'h-11 px-5 text-base',
}

const variants = {
  solid: 'bg-brand-600 text-white hover:bg-brand-700 active:bg-brand-800 shadow-sm',
  subtle: 'bg-brand-50 text-brand-700 hover:bg-brand-100',
  outline: 'border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 hover:border-gray-400',
  ghost: 'text-gray-600 hover:bg-gray-100 hover:text-gray-900',
  danger: 'bg-red-600 text-white hover:bg-red-700 active:bg-red-800 shadow-sm',
  white: 'bg-white text-gray-700 border border-gray-200 shadow-sm hover:bg-gray-50',
}
</script>
