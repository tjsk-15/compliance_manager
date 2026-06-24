<template>
  <Modal
    :model-value="modelValue"
    :title="title"
    size="sm"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <p class="text-sm text-gray-600">{{ message }}</p>
    <template #footer>
      <Button variant="outline" @click="$emit('update:modelValue', false)">Cancel</Button>
      <Button :variant="danger ? 'danger' : 'solid'" :loading="loading" @click="$emit('confirm')">
        {{ confirmLabel }}
      </Button>
    </template>
  </Modal>
</template>

<script setup>
import Modal from './Modal.vue'
import Button from './Button.vue'

defineProps({
  modelValue: Boolean,
  title: { type: String, default: 'Are you sure?' },
  message: String,
  confirmLabel: { type: String, default: 'Confirm' },
  danger: Boolean,
  loading: Boolean,
})
defineEmits(['update:modelValue', 'confirm'])
</script>
