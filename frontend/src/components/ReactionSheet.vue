<script setup>
import { computed } from 'vue'
import { useChatStore } from '../stores/chat'
import { useAuthStore } from '../stores/auth'
import Icon from './Icon.vue'

const props = defineProps({
  message: { type: Object, required: true },
  isAdmin: { type: Boolean, default: false }
})

const emit = defineEmits(['close'])

const chatStore = useChatStore()
const authStore = useAuthStore()

//flatten reactions to show individual user entries
const reactionDetails = computed(() => {
  if (!props.message.reactions) return []
  
  const details = []
  props.message.reactions.forEach(reaction => {
    reaction.users.forEach((username, index) => {
      details.push({
        emoji: reaction.emoji,
        username: username,
        avatar: reaction.user_avatars ? reaction.user_avatars[index] : 'default',
        isMe: authStore.user?.username === username
      })
    })
  })
  return details
})

function handleDelete() {
  if (confirm('Are you sure you want to delete this message?')) {
    chatStore.deleteMessage(props.message.id)
    emit('close')
  }
}

async function removeReaction(emoji) {
  try {
    await chatStore.toggleReaction(props.message.id, emoji)
    //if no more reactions => close sheet
    if (props.message.reactions.length <= 1 && props.message.reactions[0].count <= 1) {
        emit('close')
    }
  } catch (e) {
    console.error(e)
  }
}

function getAvatarUrl(avatarId) {
  return chatStore.getAvatarUrl(avatarId)
}
</script>

<template>
  <div class="reaction-sheet-overlay">
    <div class="reaction-sheet-backdrop" @click="emit('close')"></div>
    
    <div class="reaction-sheet">
      <div class="reaction-sheet-handle" @click="emit('close')">
        <div class="reaction-sheet-handle-bar"></div>
      </div>
      
      <div class="reaction-sheet-header">
        <h3 class="reaction-sheet-title">Reactions</h3>
      </div>

      <div class="reaction-sheet-list">
        <div v-if="reactionDetails.length === 0" class="reaction-sheet-empty">
          No reactions
        </div>
        
        <div 
          v-for="(item, idx) in reactionDetails" 
          :key="idx"
          class="reaction-sheet-item"
        >
          <div class="reaction-sheet-user">
            <div class="reaction-sheet-avatar">
               <img :src="getAvatarUrl(item.avatar)" />
            </div>
            <span class="reaction-sheet-username">{{ item.username }}</span>
          </div>
          
          <div class="reaction-sheet-right">
            <span class="reaction-sheet-emoji">{{ item.emoji }}</span>
            <button 
              v-if="item.isMe" 
              @click="removeReaction(item.emoji)"
              class="reaction-sheet-remove"
            >
              Remove
            </button>
          </div>
        </div>
      </div>

      <div v-if="isAdmin" class="reaction-sheet-footer">
         <button @click="handleDelete" class="delete-btn">
           <Icon name="trash" :size="20" />
           Delete Message
         </button>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
</style>