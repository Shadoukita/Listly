<template>
  <div class="field" :class="{ focused, error: !!error }">
    <label v-if="label" class="field-label">{{ label }}</label>
    <div class="field-row">
      <input
        v-bind="$attrs"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :autocomplete="autocomplete"
        :class="{ mono }"
        @input="$emit('update:modelValue', $event.target.value)"
        @focus="focused = true"
        @blur="focused = false"
      />
      <slot name="trailing" />
    </div>
    <span v-if="error" class="field-error">{{ error }}</span>
  </div>
</template>

<script setup>
import { ref } from 'vue'
defineOptions({ inheritAttrs: false })
defineProps({
  label:        { type: String,  default: '' },
  modelValue:   { type: String,  default: '' },
  placeholder:  { type: String,  default: '' },
  type:         { type: String,  default: 'text' },
  mono:         { type: Boolean, default: false },
  disabled:     { type: Boolean, default: false },
  error:        { type: String,  default: '' },
  autocomplete: { type: String,  default: 'off' },
})
defineEmits(['update:modelValue'])
const focused = ref(false)
</script>

<style scoped>
.field {
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: var(--r-field);
  padding: 10px 14px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  transition: border-color 0.15s;
}
.field.focused { border-color: var(--accent); }
.field.error   { border-color: var(--danger); }

.field-label {
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  color: var(--text-mute);
}
.field-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.field-row input {
  flex: 1;
  font-size: 14px;
  color: var(--text);
  min-width: 0;
}
.field-row input.mono {
  font-family: var(--font-mono);
  letter-spacing: 0.3px;
}
.field-error {
  font-size: 12px;
  color: var(--danger);
  margin-top: 2px;
}
</style>
