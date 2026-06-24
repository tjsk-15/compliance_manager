<template>
  <div>
    <!-- Desktop table -->
    <div class="hidden overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm md:block">
      <table class="min-w-full divide-y divide-gray-100">
        <thead class="bg-gray-50">
          <tr>
            <th
              v-for="col in tracker.columns"
              :key="col.field"
              class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500"
            >
              {{ col.label }}
            </th>
            <th class="w-20 px-4 py-3" />
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr
            v-for="row in rows"
            :key="row.name"
            class="group cursor-pointer transition hover:bg-brand-50/40"
            @click="$emit('edit', row.name)"
          >
            <td v-for="col in tracker.columns" :key="col.field" class="px-4 py-3 align-middle">
              <template v-if="col.type === 'status'">
                <StatusBadge :status="row[col.field]" />
              </template>
              <template v-else-if="col.type === 'date'">
                <div class="text-sm text-gray-900">{{ formatDate(row[col.field]) }}</div>
                <div class="text-xs" :class="urgencyClasses(row[col.field])">
                  {{ deadlineLabel(row[col.field]) }}
                </div>
              </template>
              <template v-else>
                <span :class="col.primary ? 'font-medium text-gray-900' : 'text-gray-600'">
                  {{ row[col.field] || '—' }}
                </span>
              </template>
            </td>
            <td class="px-4 py-3 text-right" @click.stop>
              <div class="flex justify-end gap-1 opacity-0 transition group-hover:opacity-100">
                <button
                  class="rounded-md p-1.5 text-gray-400 hover:bg-gray-100 hover:text-brand-600"
                  title="Edit"
                  @click="$emit('edit', row.name)"
                >
                  <Icon name="edit-2" :size="16" />
                </button>
                <button
                  v-if="canDelete"
                  class="rounded-md p-1.5 text-gray-400 hover:bg-red-50 hover:text-red-600"
                  title="Delete"
                  @click="$emit('delete', row.name)"
                >
                  <Icon name="trash-2" :size="16" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Mobile cards -->
    <div class="space-y-3 md:hidden">
      <div
        v-for="row in rows"
        :key="row.name"
        class="rounded-xl border border-gray-200 bg-white p-4 shadow-sm"
        @click="$emit('edit', row.name)"
      >
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <p class="truncate font-medium text-gray-900">{{ row[tracker.titleField] || row.name }}</p>
            <p class="mt-0.5 text-sm text-gray-500">
              {{ formatDate(row[tracker.dateField]) }} ·
              <span :class="urgencyClasses(row[tracker.dateField])">{{ deadlineLabel(row[tracker.dateField]) }}</span>
            </p>
          </div>
          <StatusBadge :status="row.status" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import Icon from './Icon.vue'
import StatusBadge from './StatusBadge.vue'
import { formatDate, deadlineLabel, urgencyClasses } from '@/utils/format'

defineProps({
  tracker: { type: Object, required: true },
  rows: { type: Array, default: () => [] },
  canDelete: Boolean,
})
defineEmits(['edit', 'delete'])
</script>
