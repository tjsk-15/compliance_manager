<template>
  <teleport to="body">
    <transition name="modal">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto p-4 sm:p-6"
      >
        <div
          class="fixed inset-0 bg-gray-900/40 backdrop-blur-[1px]"
          @click="closeOnOverlay && close()"
        />
        <div
          class="relative z-10 mt-6 w-full rounded-2xl bg-white shadow-xl ring-1 ring-black/5 sm:mt-12"
          :class="widths[size]"
        >
          <div class="flex items-start justify-between gap-4 border-b border-gray-100 px-5 py-4">
            <div class="min-w-0">
              <h3 class="truncate text-base font-semibold text-gray-900">{{ title }}</h3>
              <p v-if="subtitle" class="mt-0.5 truncate text-sm text-gray-500">{{ subtitle }}</p>
            </div>
            <button
              class="-mr-1 rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
              @click="close"
            >
              <Icon name="x" :size="18" />
            </button>
          </div>

          <div class="max-h-[70vh] overflow-y-auto px-5 py-4">
            <slot />
          </div>

          <div v-if="$slots.footer" class="flex justify-end gap-2 border-t border-gray-100 px-5 py-3.5">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import Icon from './Icon.vue'

const props = defineProps({
  modelValue: Boolean,
  title: String,
  subtitle: String,
  size: { type: String, default: 'md' }, // sm | md | lg
  closeOnOverlay: { type: Boolean, default: true },
})
const emit = defineEmits(['update:modelValue'])

const widths = {
  sm: 'max-w-md',
  md: 'max-w-2xl',
  lg: 'max-w-4xl',
}

function close() {
  emit('update:modelValue', false)
}

function onKey(e) {
  if (e.key === 'Escape' && props.modelValue) close()
}
onMounted(() => document.addEventListener('keydown', onKey))
onUnmounted(() => document.removeEventListener('keydown', onKey))
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.18s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
