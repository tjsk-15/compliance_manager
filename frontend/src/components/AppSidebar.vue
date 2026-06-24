<template>
  <nav class="flex h-full flex-col bg-white">
    <div class="flex items-center gap-2.5 px-5 py-5">
      <img :src="logoUrl" alt="" class="h-8 w-8" />
      <div class="leading-tight">
        <div class="text-sm font-semibold text-gray-900">Compliance</div>
        <div class="text-xs text-gray-400">Manager</div>
      </div>
    </div>

    <div class="flex-1 space-y-0.5 overflow-y-auto px-3 pb-4">
      <RouterLink
        v-for="item in items"
        :key="item.to"
        :to="item.to"
        class="group flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition"
        :class="isActive(item) ? activeClass : inactiveClass"
        @click="$emit('navigate')"
      >
        <Icon :name="item.icon" :size="18" />
        <span class="truncate">{{ item.label }}</span>
      </RouterLink>
    </div>

    <div class="border-t border-gray-100 px-4 py-3">
      <p class="text-[11px] leading-relaxed text-gray-400">
        Stay ahead of renewals — insurances, licences, trademarks & compliances.
      </p>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Icon from './Icon.vue'
import { trackerList } from '@/data/trackers'
import { session } from '@/data/session'

defineEmits(['navigate'])

const route = useRoute()

// Runtime path served by Frappe (not bundled by Vite).
const logoUrl = '/assets/compliance_manager/images/logo.svg'

const items = computed(() => {
  const base = [{ to: '/', label: 'Dashboard', icon: 'home', exact: true }]
  for (const t of trackerList) {
    base.push({ to: t.path, label: t.label, icon: t.icon })
  }
  if (session.isManager) {
    base.push({ to: '/settings', label: 'Settings', icon: 'settings' })
  }
  return base
})

const activeClass = 'bg-brand-50 text-brand-700'
const inactiveClass = 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'

function isActive(item) {
  if (item.exact) return route.path === '/'
  return route.path === item.to || route.path.startsWith(item.to + '/')
}
</script>
