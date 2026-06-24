<template>
  <div class="flex flex-col items-center justify-center py-24 text-center">
    <div class="flex h-14 w-14 items-center justify-center rounded-full bg-gray-100 text-gray-400">
      <Icon name="compass" :size="26" />
    </div>
    <h1 class="mt-5 text-lg font-semibold text-gray-900">Page not found</h1>
    <p class="mt-1 text-sm text-gray-500">The page you're looking for doesn't exist.</p>
    <RouterLink to="/" class="mt-6">
      <Button variant="solid" icon-left="home">Back to dashboard</Button>
    </RouterLink>
  </div>
</template>

<script setup>
import Icon from '@/components/Icon.vue'
import Button from '@/components/Button.vue'
</script>
