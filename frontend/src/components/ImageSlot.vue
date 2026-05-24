<template>
  <label class="image-slot" :class="{ filled: !!modelValue }" :style="{ borderRadius: radius + 'px', aspectRatio }">
    <img v-if="modelValue" :src="modelValue" alt="" />
    <div v-else class="placeholder">
      <AppIcon :d="I.image" :size="28" class="icon" />
      <span>{{ placeholder }}</span>
    </div>
    <input type="file" accept="image/*" @change="onChange" hidden />
    <div v-if="uploading" class="uploading">Uploading…</div>
  </label>
</template>

<script setup>
import { ref } from 'vue'
import AppIcon from './AppIcon.vue'
import { I } from './icons.js'
import { api } from '../stores/api'

const props = defineProps({
  modelValue:  { type: String,  default: '' },
  placeholder: { type: String,  default: 'Add photo' },
  aspectRatio: { type: String,  default: '16/10' },
  radius:      { type: Number,  default: 12 },
  type:        { type: String,  default: 'recipe' },
  resourceId:  { type: String,  default: '' },
  deferred:    { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue', 'file'])
const uploading = ref(false)

async function onChange(e) {
  const file = e.target.files[0]
  if (!file) return

  // Deferred mode: show local preview, hand the File to the parent for upload later
  if (props.deferred) {
    const preview = URL.createObjectURL(file)
    emit('update:modelValue', preview)
    emit('file', file)
    e.target.value = ''
    return
  }

  uploading.value = true
  try {
    const fd = new FormData()
    fd.append('file', file)
    fd.append('type', props.type)
    if (props.resourceId) fd.append('id', props.resourceId)
    const token = localStorage.getItem('token')
    const res = await fetch('/api/upload', {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: fd,
    })
    const data = await res.json()
    if (data.url) emit('update:modelValue', data.url)
  } catch(err) {
    console.error('Upload failed', err)
  } finally {
    uploading.value = false
    e.target.value = ''
  }
}
</script>

<style scoped>
.image-slot {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  background: var(--surface);
  border: 1.5px dashed var(--border-hi);
  cursor: pointer;
  overflow: hidden;
  position: relative;
  transition: border-color 0.15s;
}
.image-slot:hover { border-color: var(--accent); }
.image-slot.filled { border-style: solid; border-color: var(--border); }
.image-slot img { width: 100%; height: 100%; object-fit: cover; display: block; }

.placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: var(--text-mute);
  font-size: 13px;
}
.placeholder .icon { color: var(--text-mute); }

.uploading {
  position: absolute;
  inset: 0;
  background: rgba(10,11,13,0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  color: var(--text-dim);
}
</style>
