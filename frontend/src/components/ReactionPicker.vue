<script setup>
const emojis = ['❤️', '😂', '😮', '😢', '😡', '👍'] //default reaction can be changed as wished
defineEmits(['select'])
</script>

<template>
  <div class="reaction-picker">
    <button 
      v-for="emoji in emojis" 
      :key="emoji" 
      @click="$emit('select', emoji)" 
      class="reaction-option"
    >
      {{ emoji }}
    </button>
  </div>
</template>

<style scoped lang="scss">
</style>