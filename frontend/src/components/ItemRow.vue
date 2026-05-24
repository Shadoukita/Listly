<template>
  <div class="item-row">
    <!-- Checkbox -->
    <button class="item-cb" :class="{ checked: item.checked }" @click="$emit('toggle', item)" :aria-label="item.checked ? 'Uncheck' : 'Check'">
      <AppIcon v-if="item.checked" :d="I.check" :size="14" :sw="3" />
    </button>

    <!-- Name + qty -->
    <div class="item-body">
      <span class="item-name" :class="{ checked: item.checked }">{{ item.name }}</span>
      <span v-if="item.quantity && item.quantity !== '1'" class="item-qty">
        {{ item.quantity }}{{ /^\d+$/.test(item.quantity) ? '×' : '' }}
      </span>
    </div>

    <!-- Attribution -->
    <div class="item-meta">
      <Avatar
        :name="item.checked ? (item.checked_by_name || '?') : (item.added_by_name || '?')"
        :src="item.checked ? (item.checked_by_profile_image || '') : (item.added_by_profile_image || '')"
        :color="byColor"
        :size="18"
      />
      <span class="item-meta-text">
        {{ item.checked ? `${item.checked_by_name || ''} checked` : `by ${item.added_by_name || ''}` }}
      </span>
    </div>

    <span class="item-time">{{ formatTime(item.checked ? item.checked_at : item.created_at) }}</span>

    <!-- Delete -->
    <button class="item-del" @click="$emit('remove', item)" aria-label="Remove">
      <AppIcon :d="I.x" :size="14" />
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { avatarColor } from '../stores/auth'
import Avatar from './Avatar.vue'
import AppIcon from './AppIcon.vue'
import { I } from './icons.js'

const { t } = useI18n()
const props = defineProps({ item: { type: Object, required: true } })
defineEmits(['toggle', 'remove'])

const byColor = computed(() =>
  props.item.checked ? avatarColor(props.item.checked_by) : avatarColor(props.item.added_by)
)

function formatTime(ts) {
  if (!ts) return ''
  const d = new Date(ts.endsWith('Z') ? ts : ts + 'Z')
  const diff = Date.now() - d.getTime()
  if (diff < 60000)   return t('shopping.justNow')
  if (diff < 3600000) return t('shopping.minutesAgo', { n: Math.floor(diff / 60000) })
  if (diff < 86400000) return t('shopping.hoursAgo', { n: Math.floor(diff / 3600000) })
  return d.toLocaleDateString(undefined, { day: '2-digit', month: '2-digit' })
}
</script>

<style scoped>
.item-row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 18px;
}

.item-cb {
  width: 22px; height: 22px; border-radius: 6px; flex-shrink: 0;
  background: transparent;
  border: 1.5px solid var(--border-hi);
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; color: var(--accent-ink);
  transition: background 0.15s, border-color 0.15s;
}
.item-cb.checked { background: var(--accent); border-color: var(--accent); }

.item-body {
  flex: 1; min-width: 0;
  display: flex; align-items: baseline; gap: 10px;
}
.item-name {
  font-size: 15px; font-weight: 500; color: var(--text);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.item-name.checked {
  text-decoration: line-through;
  text-decoration-color: var(--text-mute);
  color: var(--text-mute);
}
.item-qty {
  font-family: var(--font-mono); font-size: 11px; color: var(--text-dim);
  padding: 2px 7px; border-radius: 6px; background: var(--surface-hi);
  flex-shrink: 0;
}

.item-meta {
  display: flex; align-items: center; gap: 8px; flex-shrink: 0;
}
.item-meta-text { font-size: 12px; color: var(--text-dim); white-space: nowrap; }

.item-time {
  font-family: var(--font-mono); font-size: 10px; font-weight: 500;
  letter-spacing: 0.5px; text-transform: uppercase; color: var(--text-mute);
  flex-shrink: 0;
}

.item-del {
  width: 28px; height: 28px; border-radius: 6px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  color: var(--text-mute); opacity: 0;
  cursor: pointer; transition: opacity 0.15s, background 0.15s, color 0.15s;
}
.item-row:hover .item-del { opacity: 1; }
.item-del:hover { background: var(--danger-bg); color: var(--danger); opacity: 1; }

@media (max-width: 600px) {
  .item-meta { display: none; }
  .item-del { opacity: 0.6; }
}
</style>
