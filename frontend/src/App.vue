<template>
  <div class="flex h-full bg-gray-50">
    <!-- Loading -->
    <div v-if="!session.loaded && !loadError" class="flex h-full w-full items-center justify-center">
      <div class="flex flex-col items-center gap-3 text-gray-400">
        <Spinner :size="30" class="text-brand-600" />
        <span class="text-sm">Loading Compliance Manager…</span>
      </div>
    </div>

    <!-- Load error -->
    <div v-else-if="loadError" class="flex h-full w-full items-center justify-center p-6">
      <div class="max-w-md rounded-2xl border border-gray-200 bg-white p-8 text-center shadow-sm">
        <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-red-50 text-red-600">
          <Icon name="wifi-off" :size="22" />
        </div>
        <h2 class="mt-4 text-lg font-semibold text-gray-900">Couldn't load</h2>
        <p class="mt-1 text-sm text-gray-500">We couldn't reach the server. Please check your connection and try again.</p>
        <Button class="mt-5" variant="solid" icon-left="refresh-cw" @click="reloadApp">Retry</Button>
      </div>
    </div>

    <!-- Access denied -->
    <div v-else-if="session.loaded && !session.isCompliance" class="flex h-full w-full items-center justify-center p-6">
      <div class="max-w-md rounded-2xl border border-gray-200 bg-white p-8 text-center shadow-sm">
        <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-amber-50 text-amber-600">
          <Icon name="lock" :size="22" />
        </div>
        <h2 class="mt-4 text-lg font-semibold text-gray-900">No access yet</h2>
        <p class="mt-1 text-sm text-gray-500">
          You're signed in as <b>{{ session.fullName }}</b>, but you don't have a Compliance role.
          Ask an administrator to grant you the <b>Compliance User</b> role.
        </p>
        <Button class="mt-5" variant="outline" icon-left="log-out" @click="logout">Sign out</Button>
      </div>
    </div>

    <!-- App -->
    <template v-else-if="session.loaded">
      <aside class="hidden w-64 shrink-0 border-r border-gray-200 lg:block">
        <AppSidebar />
      </aside>

      <transition name="drawer">
        <div v-if="mobileOpen" class="fixed inset-0 z-40 lg:hidden">
          <div class="absolute inset-0 bg-gray-900/40" @click="mobileOpen = false" />
          <aside class="absolute left-0 top-0 h-full w-64 shadow-xl">
            <AppSidebar @navigate="mobileOpen = false" />
          </aside>
        </div>
      </transition>

      <div class="flex min-w-0 flex-1 flex-col">
        <header class="sticky top-0 z-20 flex h-14 items-center gap-3 border-b border-gray-200 bg-white/80 px-4 backdrop-blur sm:px-6">
          <button
            class="rounded-lg p-2 text-gray-500 hover:bg-gray-100 lg:hidden"
            @click="mobileOpen = true"
          >
            <Icon name="menu" :size="20" />
          </button>

          <div class="flex-1" />

          <div ref="userMenuRef" class="relative">
            <button
              class="flex items-center gap-2 rounded-full py-1 pl-1 pr-2.5 transition hover:bg-gray-100"
              @click="userOpen = !userOpen"
            >
              <span class="flex h-8 w-8 items-center justify-center overflow-hidden rounded-full bg-brand-600 text-xs font-semibold text-white">
                <img v-if="session.userImage" :src="session.userImage" class="h-full w-full object-cover" />
                <template v-else>{{ initials(session.fullName) }}</template>
              </span>
              <span class="hidden text-sm font-medium text-gray-700 sm:block">{{ session.fullName }}</span>
              <Icon name="chevron-down" :size="15" class="hidden text-gray-400 sm:block" />
            </button>

            <transition name="drawer">
              <div
                v-if="userOpen"
                class="absolute right-0 mt-2 w-60 overflow-hidden rounded-xl border border-gray-200 bg-white shadow-lg"
              >
                <div class="border-b border-gray-100 px-4 py-3">
                  <p class="truncate text-sm font-semibold text-gray-900">{{ session.fullName }}</p>
                  <p class="truncate text-xs text-gray-500">{{ session.user }}</p>
                  <span
                    class="mt-2 inline-flex rounded-full bg-brand-50 px-2 py-0.5 text-[11px] font-medium text-brand-700"
                  >
                    {{ session.isManager ? 'Compliance Manager' : 'Compliance User' }}
                  </span>
                </div>
                <button
                  class="flex w-full items-center gap-2.5 px-4 py-2.5 text-sm text-gray-600 hover:bg-gray-50"
                  @click="openDesk"
                >
                  <Icon name="grid" :size="16" /> Open Desk view
                </button>
                <button
                  class="flex w-full items-center gap-2.5 px-4 py-2.5 text-sm text-red-600 hover:bg-red-50"
                  @click="logout"
                >
                  <Icon name="log-out" :size="16" /> Sign out
                </button>
              </div>
            </transition>
          </div>
        </header>

        <main class="flex-1 overflow-y-auto">
          <div class="mx-auto max-w-6xl px-4 py-6 sm:px-6 lg:px-8">
            <router-view v-slot="{ Component }">
              <component :is="Component" :key="$route.path" />
            </router-view>
          </div>
        </main>
      </div>
    </template>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import AppSidebar from '@/components/AppSidebar.vue'
import Button from '@/components/Button.vue'
import Icon from '@/components/Icon.vue'
import Spinner from '@/components/Spinner.vue'
import { contextResource, session, logout } from '@/data/session'
import { initials } from '@/utils/format'

const mobileOpen = ref(false)
const userOpen = ref(false)
const userMenuRef = ref(null)
const loadError = ref(false)

function onClickOutside(e) {
  if (userMenuRef.value && !userMenuRef.value.contains(e.target)) userOpen.value = false
}
function openDesk() {
  window.location.href = '/app/compliance'
}
function reloadApp() {
  window.location.reload()
}

onMounted(() => {
  contextResource.fetch().catch(() => (loadError.value = true))
  document.addEventListener('click', onClickOutside)
})
onUnmounted(() => document.removeEventListener('click', onClickOutside))
</script>

<style>
.drawer-enter-active,
.drawer-leave-active {
  transition: opacity 0.15s ease;
}
.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
}
</style>
