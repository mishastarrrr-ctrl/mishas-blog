<script setup>
import { computed } from 'vue'

const props = defineProps({
  users: { type: Array, default: () => [] }
})

const typingText = computed(() => {
  if (props.users.length === 0) return ''
  if (props.users.length === 1) return `${props.users[0]} is typing`
  if (props.users.length === 2) return `${props.users[0]} and ${props.users[1]} are typing`
  return `${props.users.length} people are typing`
})
</script>

<template>
  <div class="typing-container">
    <div class="typing-indicator">
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
    </div>
    <span class="typing-text">{{ typingText }}</span>
  </div>
</template>

<style scoped lang="scss">
</style>