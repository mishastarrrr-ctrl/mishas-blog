<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useChatStore } from '../stores/chat'
import MessageBubble from '../components/MessageBubble.vue'
import AvatarPicker from '../components/AvatarPicker.vue'
import ReactionSheet from '../components/ReactionSheet.vue'
import AttachmentModal from '../components/AttachmentModal.vue'
// import TypingIndicator from '../components/TypingIndicator.vue'
import Icon from '../components/Icon.vue'

const router = useRouter()
const authStore = useAuthStore()
const chatStore = useChatStore()

const messagesContainer = ref(null)
const messageInput = ref('')
const fileInput = ref(null)
const selectedFiles = ref([])
const showAvatarPicker = ref(false)
const selectedMessageForDetails = ref(null)
const selectedAttachments = ref(null)
const replyToMessage = ref(null)
const toast = ref('')
const lightboxImage = ref(null)

const currentTheme = ref(localStorage.getItem('blog-theme') || 'imessage')

const isAdmin = computed(() => authStore.isAdmin)

const avatarUrl = computed(() => {
  return chatStore.getAvatarUrl(authStore.user?.avatar)
})

function groupMessages(msgs) {
  if (!msgs.length) return []
  return msgs.map((msg, index) => {
    const prevMsg = msgs[index - 1]
    const nextMsg = msgs[index + 1]
    
    //check if part of a group (same author, < 5 mins apart)
    const isSameAuthorAsPrev = prevMsg && prevMsg.author_id === msg.author_id
    const isSameAuthorAsNext = nextMsg && nextMsg.author_id === msg.author_id
    
    const timeDiffPrev = prevMsg ? (new Date(msg.created_at) - new Date(prevMsg.created_at)) / 1000 / 60 : Infinity
    const timeDiffNext = nextMsg ? (new Date(nextMsg.created_at) - new Date(msg.created_at)) / 1000 / 60 : Infinity
    
    const GROUP_THRESHOLD = 5 
    const TIME_THRESHOLD = 15

    const isFirstInGroup = !isSameAuthorAsPrev || timeDiffPrev > GROUP_THRESHOLD
    const isLastInGroup = !isSameAuthorAsNext || Math.abs(timeDiffNext) > GROUP_THRESHOLD
    const showTime = !prevMsg || timeDiffPrev > TIME_THRESHOLD

    return {
      ...msg,
      _isFirstInGroup: isFirstInGroup,
      _isLastInGroup: isLastInGroup,
      _showTime: showTime
    }
  })
}

//message grouping logic
const groupedMessages = computed(() => groupMessages(chatStore.messages))
const pinnedMessages = computed(() => groupMessages(chatStore.pinnedMessages))

let typingTimeout = null

function scrollToBottom(smooth = true) {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTo({
        top: messagesContainer.value.scrollHeight,
        behavior: smooth ? 'smooth' : 'auto'
      })
    }
  })
}

function handleScroll() {
  if (messagesContainer.value) {
    const { scrollTop } = messagesContainer.value
    if (scrollTop === 0 && chatStore.hasMore && !chatStore.loading) {
      const firstMessage = chatStore.messages[0]
      if (firstMessage) {
        chatStore.fetchMessages(firstMessage.id)
      }
    }
  }
}

function handleTyping() {
  clearTimeout(typingTimeout)
  typingTimeout = setTimeout(() => {
    chatStore.sendTyping()
  }, 500)
}

async function sendMessage() {
  const content = messageInput.value.trim()
  const files = selectedFiles.value
  
  if (!content && files.length === 0) return
  if (!isAdmin.value) return
  
  try {
    await chatStore.sendMessage(content, files, replyToMessage.value?.id)
    messageInput.value = ''
    selectedFiles.value = []
    replyToMessage.value = null
    scrollToBottom()
  } catch (e) {
    showToast('Failed to send message')
  }
}

function triggerFileInput() {
  fileInput.value?.click()
}

function handleFileSelect(event) {
  const files = Array.from(event.target.files)
  selectedFiles.value = [...selectedFiles.value, ...files]
  event.target.value = ''
}

function removeFile(index) {
  selectedFiles.value.splice(index, 1)
}

function getFilePreview(file) {
  if (file.type.startsWith('image/')) {
    return URL.createObjectURL(file)
  }
  return null
}

function getFileIcon(file) {
  if (file.type.startsWith('audio/')) return 'music'
  if (file.type.startsWith('video/')) return 'video'
  return 'file'
}

async function handleReaction(messageId, emoji) {
  try {
    await chatStore.toggleReaction(messageId, emoji)
  } catch (e) {
    showToast('Failed to add reaction')
  }
}

async function handleDelete(messageId) {
  if (!confirm('Delete this message?')) return
  try {
    await chatStore.deleteMessage(messageId)
  } catch (e) {
    showToast('Failed to delete message')
  }
}

function selectAvatar(avatar) {
  authStore.updateAvatar(avatar)
  chatStore.updateAvatar(avatar)
  showAvatarPicker.value = false
}

function openLightbox(imageUrl) {
  lightboxImage.value = imageUrl
  selectedAttachments.value = null //close attachment modal if open
}

function closeLightbox() {
  lightboxImage.value = null
}

function openAttachments(attachments) {
  selectedAttachments.value = attachments
}

function showToast(message) {
  toast.value = message
  setTimeout(() => toast.value = '', 3000)
}

function goToLogin() {
  router.push('/login')
}

function logout() {
  authStore.logout()
  chatStore.disconnect()
  window.location.reload()
}

function toggleTheme() {
  currentTheme.value = currentTheme.value === 'imessage' ? 'material' : 'imessage'
  document.documentElement.setAttribute('data-theme', currentTheme.value)
  localStorage.setItem('blog-theme', currentTheme.value)
}

function openReactionSheet(message) {
  selectedMessageForDetails.value = message
}

function handleReply(message) {
  //only admins can post => so only admins can reply
  if (!isAdmin.value) return
  
  replyToMessage.value = message
  //focus input
  nextTick(() => {
    const textarea = document.querySelector('.message-input')
    if (textarea) textarea.focus()
  })
}

function cancelReply() {
  replyToMessage.value = null
}

watch(() => chatStore.messages.length, (newLen, oldLen) => {
  if (newLen > oldLen) {
    scrollToBottom()
  }
})

onMounted(async () => {
  document.documentElement.setAttribute('data-theme', currentTheme.value)
  await chatStore.fetchAvatars()
  await chatStore.fetchMessages()
  chatStore.connectWebSocket()
  scrollToBottom(false)
})

onUnmounted(() => {
  chatStore.disconnect()
  clearTimeout(typingTimeout)
})
</script>

<template>
  <div class="chat-container">
    <header class="header">
      <div class="header-left">
        <template v-if="!isAdmin">
          <button @click="goToLogin" class="header-btn">
             <Icon name="back" :size="22" />
             <span class="header-btn-text hidden-mobile">Admin</span>
          </button>
        </template>
        <template v-else>
           <button @click="logout" class="header-btn">
             Logout
           </button>
        </template>
      </div>

      <div class="header-center">
        <span class="header-title">Blog</span>
        <span class="header-subtitle">{{ chatStore.onlineCount }} online</span>
      </div>

      <div class="header-right">
        <button @click="toggleTheme" class="icon-btn" title="Switch Theme">
          <Icon name="palette" :size="22" />
        </button>
        
        <button
          @click="showAvatarPicker = !showAvatarPicker"
          class="avatar avatar-btn"
          :title="authStore.user?.username"
        >
          <img v-if="avatarUrl" :src="avatarUrl" :alt="authStore.user?.username" />
          <div v-else class="avatar-fallback">
            <Icon name="user" :size="16" />
          </div>
        </button>

        <AvatarPicker
          v-if="showAvatarPicker"
          :current-avatar="authStore.user?.avatar"
          @select="selectAvatar"
          @close="showAvatarPicker = false"
        />
      </div>
    </header>
    
    <div
      ref="messagesContainer"
      class="messages-area"
      @scroll="handleScroll"
    >
      <div v-if="chatStore.loading && !chatStore.messages.length" class="loading-text">
        Loading...
      </div>

      <div v-if="pinnedMessages.length > 0" class="pinned-section">
        <div class="pinned-header">
           <Icon name="pin" :size="12" /> Pinned Messages
        </div>
        <MessageBubble
          v-for="message in pinnedMessages"
          :key="'pinned-'+message.id"
          :message="message"
          :current-user="authStore.user"
          :is-admin="isAdmin"
          :is-first-in-group="message._isFirstInGroup"
          :is-last-in-group="message._isLastInGroup"
          :show-time="false"
          @react="handleReaction"
          @delete="handleDelete"
          @image-click="openLightbox"
          @open-attachments="openAttachments"
          @show-details="openReactionSheet"
          @reply="handleReply"
        />
        <div class="pinned-divider"></div>
      </div>

      <div v-if="!chatStore.loading && chatStore.messages.length === 0 && pinnedMessages.length === 0" class="empty-state">
        <Icon name="chat" :size="64" class="empty-state-icon" />
        <h2 class="empty-state-text">No messages yet</h2>
      </div>
      
      <TransitionGroup name="message">
        <MessageBubble
          v-for="message in groupedMessages"
          :key="message.id"
          :message="message"
          :current-user="authStore.user"
          :is-admin="isAdmin"
          :is-first-in-group="message._isFirstInGroup"
          :is-last-in-group="message._isLastInGroup"
          :show-time="message._showTime"
          @react="handleReaction"
          @delete="handleDelete"
          @image-click="openLightbox"
          @open-attachments="openAttachments"
          @show-details="openReactionSheet"
          @reply="handleReply"
        />
      </TransitionGroup>
      
    </div>
    
    <div v-if="isAdmin">
      <div v-if="replyToMessage" class="reply-preview">
        <div class="reply-preview-content">
           <span class="reply-preview-label">Replying to {{ replyToMessage.author_username }}</span>
           <span class="reply-preview-text">{{ replyToMessage.content || 'Attachment' }}</span>
        </div>
        <button @click="cancelReply" class="reply-preview-close">
           <Icon name="close" :size="20" />
        </button>
      </div>

      <div v-if="selectedFiles.length > 0" class="file-preview-container">
        <div
          v-for="(file, index) in selectedFiles"
          :key="index"
          class="file-preview-item"
        >
          <img v-if="getFilePreview(file)" :src="getFilePreview(file)" />
          <div v-else class="file-preview-placeholder">
            <Icon :name="getFileIcon(file)" :size="24" />
          </div>
          <button @click="removeFile(index)" class="file-preview-remove">x</button>
        </div>
      </div>
      
      <div class="input-container">
        <input
          ref="fileInput"
          type="file"
          multiple
          accept="image/*,audio/*,video/*"
          class="hidden"
          @change="handleFileSelect"
        />
        <button @click="triggerFileInput" class="icon-btn" title="Attach files">
          <Icon name="plus" :size="26" />
        </button>
        
        <textarea
          v-model="messageInput"
          @input="handleTyping"
          @keydown.enter.exact.prevent="sendMessage"
          class="message-input"
          placeholder="Write a new message..."
          rows="1"
        ></textarea>
        
        <button
          @click="sendMessage"
          :disabled="!messageInput.trim() && selectedFiles.length === 0"
          class="send-btn"
          title="Send"
        >
          <Icon name="send" :size="18" />
        </button>
      </div>
    </div>
    
    <div v-else class="guest-footer">
      Viewing as <strong>{{ authStore.user?.username }}</strong> · Long press to react
    </div>

    <Teleport to="body">
      <Transition name="fade">
        <div v-if="lightboxImage" class="lightbox" @click="closeLightbox">
          <img :src="lightboxImage" class="lightbox-image" @click.stop />
          <button @click="closeLightbox" class="lightbox-close">
             <Icon name="close" :size="32" />
          </button>
        </div>
      </Transition>
    </Teleport>

    <Teleport to="body">
      <Transition name="fade">
        <AttachmentModal 
          v-if="selectedAttachments"
          :attachments="selectedAttachments"
          @view="openLightbox"
          @close="selectedAttachments = null"
        />
      </Transition>
    </Teleport>

    <Teleport to="body">
      <Transition name="fade">
        <ReactionSheet
          v-if="selectedMessageForDetails"
          :message="selectedMessageForDetails"
          :is-admin="isAdmin"
          @close="selectedMessageForDetails = null"
        />
      </Transition>
    </Teleport>
    
    <Teleport to="body">
      <Transition name="slide-up">
        <div v-if="toast" class="toast">
            {{ toast }}
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped lang="scss">
</style>