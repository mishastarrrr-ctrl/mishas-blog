<script setup>
import Icon from './Icon.vue'

const props = defineProps({
  attachments: { type: Array, required: true }
})

const emit = defineEmits(['close', 'view'])

function handleBackdropClick(e) {
  if (e.target === e.currentTarget) {
    emit('close')
  }
}

function getIconName(type) {
  if (type === 'audio') return 'music'
  if (type === 'video') return 'video'
  return 'file'
}
</script>

<template>
  <div class="attachment-modal" @click="handleBackdropClick">
    <div class="attachment-card">
      <div class="attachment-modal-header">
         <span class="attachment-modal-title">{{ attachments.length }} Attachments</span>
         <button @click="$emit('close')" class="attachment-modal-close">
           <Icon name="close" :size="20" />
         </button>
      </div>

      <div class="attachment-modal-content">
        <div class="attachment-grid">
          <div 
            v-for="(file, index) in attachments" 
            :key="index"
            class="attachment-item"
            @click="$emit('view', file.url)"
          >
            <img 
              v-if="file.type === 'image'" 
              :src="file.url" 
              class="attachment-image" 
              loading="lazy"
            />
            <div v-else class="attachment-placeholder">
               <Icon :name="getIconName(file.type)" :size="32" />
               <span class="attachment-placeholder-name">{{ file.name }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.attachment-modal {
  position: fixed;
  inset: 0;
  z-index: 150;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.2s ease-out forwards;
  padding: 20px;
}

.attachment-card {
  width: 100%;
  max-width: 600px;
  max-height: 80vh;
  background: var(--color-bg);
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.2);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: modalScaleIn 0.25s cubic-bezier(0.32, 0.72, 0, 1) forwards;
}

.attachment-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--input-border);
  background: var(--color-header-bg);
}

.attachment-modal-title {
  color: var(--color-text);
  font-weight: 600;
  font-size: 16px;
}

.attachment-modal-close {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 9999px;
  background: transparent;
  color: var(--color-text-secondary);
  border: none;
  cursor: pointer;
  transition: background-color 0.2s;
  
  &:hover {
    background: rgba(0, 0, 0, 0.05);
    color: var(--color-text);
  }
}

.attachment-modal-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.attachment-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 12px;
}

.attachment-item {
  aspect-ratio: 1;
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  background: var(--input-container-bg);
  cursor: pointer;
  border: 1px solid var(--input-border);
  transition: transform 0.2s, box-shadow 0.2s;
  
  &:hover {
    transform: scale(1.02);
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  }
}

.attachment-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.attachment-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
  padding: 8px;
  gap: 8px;
}

.attachment-placeholder-name {
  font-size: 11px;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  width: 100%;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes modalScaleIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
</style>