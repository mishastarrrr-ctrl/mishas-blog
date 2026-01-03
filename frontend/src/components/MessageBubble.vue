<script setup>
import { ref, computed } from 'vue'
import Icon from './Icon.vue'
import ReactionPicker from './ReactionPicker.vue'
import { useChatStore } from '../stores/chat'

const props = defineProps({
  message: { type: Object, required: true },
  currentUser: { type: Object, default: null },
  isAdmin: { type: Boolean, default: false },
  //grouping props
  isFirstInGroup: { type: Boolean, default: true },
  isLastInGroup: { type: Boolean, default: true },
  showTime: { type: Boolean, default: true }
})

const emit = defineEmits(['react', 'delete', 'imageClick', 'openAttachments', 'showDetails', 'reply'])

const chatStore = useChatStore()
const showReactionPicker = ref(false)

//swipe logic state
const touchStartX = ref(0)
const touchStartY = ref(0)
const touchCurrentX = ref(0)
const isSwiping = ref(false)
const isScrolling = ref(false) 
const isDragging = ref(false) //track if actually dragging
const swipeThreshold = 50
const dragThreshold = 10 //minimum distance to consider it a drag

//mouse long press state
let longPressTimer = null
const isLongPress = ref(false)

const formattedTime = computed(() => {
  const date = new Date(props.message.created_at)
  return date.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })
})

const avatarUrl = computed(() => {
  return chatStore.getAvatarUrl(props.message.author_avatar)
})

const bubbleClass = computed(() => {
  const base = props.message.is_admin ? 'bubble-sent' : 'bubble-received'
  let radiusClass = ''
  
  if (props.message.is_admin) {
    if (props.isFirstInGroup && !props.isLastInGroup) radiusClass = 'group-sent-first'
    else if (!props.isFirstInGroup && !props.isLastInGroup) radiusClass = 'group-sent-middle'
    else if (!props.isFirstInGroup && props.isLastInGroup) radiusClass = 'group-sent-last'
  } else {
    if (props.isFirstInGroup && !props.isLastInGroup) radiusClass = 'group-received-first'
    else if (!props.isFirstInGroup && !props.isLastInGroup) radiusClass = 'group-received-middle'
    else if (!props.isFirstInGroup && props.isLastInGroup) radiusClass = 'group-received-last'
  }
  
  return `${base} ${radiusClass} ${props.message.is_pinned ? 'pinned' : ''}`
})

//only show swipe animation if admin AND actually dragging
const swipeStyle = computed(() => {
  if (!props.isAdmin) return {} //guests cant swipe
  if (!isSwiping.value || isScrolling.value || !isDragging.value) return {}
  
  const diff = touchCurrentX.value - touchStartX.value
  
  //SWIPE LEFT TO REPLY: diff must be negative
  if (diff > 0) return {}

  //resistive swipe logic (moving left = negative pixels)
  const translate = Math.max(diff * 0.4, -80)
  return { transform: `translateX(${translate}px)` }
})

const hasAttachments = computed(() => props.message.attachments && props.message.attachments.length > 0)
const firstAttachment = computed(() => hasAttachments.value ? props.message.attachments[0] : null)
const remainingAttachmentsCount = computed(() => hasAttachments.value ? props.message.attachments.length - 1 : 0)

function userHasReacted(reaction) {
  return props.currentUser && reaction.users.includes(props.currentUser.username)
}

function handleReactionClick(emoji) {
  if (!isLongPress.value) {
    emit('react', props.message.id, emoji)
    showReactionPicker.value = false
  }
  isLongPress.value = false
}

function handlePickerSelect(emoji) {
  emit('react', props.message.id, emoji)
  showReactionPicker.value = false
}

function handlePin() {
    chatStore.pinMessage(props.message.id)
}

function handleImageClick(url) {
  if (!isLongPress.value) {
    if (remainingAttachmentsCount.value > 0) {
      emit('openAttachments', props.message.attachments)
    } else {
      emit('imageClick', url)
    }
  }
}

function toggleReactionPicker(e) {
  if (e) {
    e.preventDefault()
    e.stopPropagation()
  }
  showReactionPicker.value = !showReactionPicker.value
}

// --- Gestures ---

//mobile touch swipe & Long Press
function handleTouchStart(e) {
  //always track start for long press
  touchStartX.value = e.touches[0].clientX
  touchStartY.value = e.touches[0].clientY
  touchCurrentX.value = e.touches[0].clientX
  
  if (props.isAdmin) {
    isSwiping.value = true
    isScrolling.value = false
    isDragging.value = false
  }
  
  startLongPress()
}

function handleTouchMove(e) {
  if (!isSwiping.value) return //if not swiping (e.g. guest or not started) => exit

  const currentX = e.touches[0].clientX
  const currentY = e.touches[0].clientY
  
  const diffX = Math.abs(currentX - touchStartX.value)
  const diffY = Math.abs(currentY - touchStartY.value)

  //if vertical movement is dominant => assume scrolling
  //i want a domina- wait...no
  if (diffY > diffX && diffY > 5) {
    isScrolling.value = true
    isSwiping.value = false
    isDragging.value = false
    cancelLongPress()
    return
  }

  //mark as dragging once we exceed the threshold
  if (diffX > dragThreshold) {
    isDragging.value = true
    cancelLongPress()
  }

  touchCurrentX.value = currentX
}

function handleTouchEnd() {
  cancelLongPress()
  
  if (!isSwiping.value || isScrolling.value) {
    resetSwipeState()
    return
  }
  
  const diff = touchCurrentX.value - touchStartX.value
  
  //SWIPE LEFT: diff is negative => must have been dragging
  //must've been the wind
  if (props.isAdmin && isDragging.value && diff < -swipeThreshold) {
    if (navigator.vibrate) navigator.vibrate(50)
    emit('reply', props.message)
  }
  
  resetSwipeState()
}

function resetSwipeState() {
  isSwiping.value = false
  isScrolling.value = false
  isDragging.value = false
  touchStartX.value = 0
  touchCurrentX.value = 0
}

//mouse events for desktop
function handleMouseDown(e) {
  //always track start for long press
  touchStartX.value = e.clientX
  touchStartY.value = e.clientY
  touchCurrentX.value = e.clientX
  
  if (props.isAdmin) {
    isSwiping.value = true
    isDragging.value = false
  }
  
  startLongPress()
}

function handleMouseMove(e) {
  if (!isSwiping.value) return
  
  const diffX = Math.abs(e.clientX - touchStartX.value)
  const diffY = Math.abs(e.clientY - touchStartY.value)
  
  //only start dragging if moved enough horizontally
  if (diffX > dragThreshold && diffX > diffY) {
    isDragging.value = true
    cancelLongPress()
  }
  
  //only update position if actually dragging
  if (isDragging.value) {
    touchCurrentX.value = e.clientX
  }
}

function handleMouseUp() {
  cancelLongPress()
  
  const diff = touchCurrentX.value - touchStartX.value
  
  //only trigger reply if actually dragging and exceeded threshold
  if (props.isAdmin && isDragging.value && diff < -swipeThreshold) {
    if (navigator.vibrate) navigator.vibrate(50)
    emit('reply', props.message)
  }
  
  resetSwipeState()
}

function handleMouseLeave() {
  if (isSwiping.value || longPressTimer) {
    cancelLongPress()
    resetSwipeState()
  }
}

//long press for reactions
function startLongPress() {
  isLongPress.value = false
  if (longPressTimer) clearTimeout(longPressTimer)
  
  longPressTimer = setTimeout(() => {
    isLongPress.value = true
    if (navigator.vibrate) navigator.vibrate(50)
    
    //long hold opens reaction picker under message bubble
    showReactionPicker.value = true
    
    //stop swiping if reaction picker opens
    isSwiping.value = false
    isDragging.value = false
  }, 500)
}

function cancelLongPress() {
  if (longPressTimer) {
    clearTimeout(longPressTimer)
    longPressTimer = null
  }
}
</script>

<template>
  <div class="message-row">

    <div v-if="showTime" class="message-time">
      {{ formattedTime }}
    </div>

    <div 
      class="message-container"
      :class="{ 'justify-end': message.is_admin }"
      :style="swipeStyle"
      @touchstart="handleTouchStart"
      @touchmove="handleTouchMove"
      @touchend="handleTouchEnd"
      @mousedown="handleMouseDown"
      @mousemove="handleMouseMove"
      @mouseup="handleMouseUp"
      @mouseleave="handleMouseLeave"
    >
      <div v-if="!message.is_admin" class="avatar-space">
        <div v-if="isLastInGroup" class="avatar">
          <img v-if="avatarUrl" :src="avatarUrl" :alt="message.author_username" @error="$event.target.style.display='none'" />
          <div v-else class="avatar-fallback">
            <Icon name="user" :size="16" />
          </div>
        </div>
        <div v-else class="avatar-spacer"></div>
      </div>
      
      <div class="message-content-col" :class="{ 'items-end': message.is_admin, 'items-start': !message.is_admin }">
        <div v-if="!message.is_admin && isFirstInGroup" class="message-author">
          {{ message.author_username }}
        </div>
        
        <div v-if="message.is_pinned" class="pinned-label">
            <Icon name="pin" :size="12" /> Pinned
        </div>

        <div class="bubble-wrapper">

            <div class="desktop-actions">
                <button 
                  v-if="isAdmin"
                  @click.stop="emit('reply', message)" 
                  class="action-btn"
                  title="Reply"
                >
                  <Icon name="reply" :size="16" />
                </button>
                
                <button 
                  @click.stop="toggleReactionPicker" 
                  class="action-btn"
                  title="React"
                >
                  <Icon name="smile" :size="16" />
                </button>

                <button 
                  v-if="isAdmin"
                  @click.stop="handlePin"
                  class="action-btn"
                  :class="{ 'active': message.is_pinned }"
                  :title="message.is_pinned ? 'Unpin' : 'Pin'"
                >
                  <Icon name="pin" :size="16" />
                </button>
            </div>

            <div 
              class="bubble"
              :class="bubbleClass"
            >
              <div v-if="message.reply_to" class="reply-context">
                 <div class="reply-author">{{ message.reply_to.author_username }}</div>
                 <div class="reply-text">{{ message.reply_to.content || 'Attachment' }}</div>
              </div>
              <div v-if="hasAttachments" class="bubble-attachments">
                <div @click.stop="handleImageClick(firstAttachment.url)">
                    <img
                      v-if="firstAttachment.type === 'image'"
                      :src="firstAttachment.url"
                      class="attachment-img"
                    />
                    <video
                      v-else-if="firstAttachment.type === 'video'"
                      :src="firstAttachment.url"
                      controls
                      playsinline
                      preload="metadata"
                      class="attachment-video"
                      @click.stop
                    />
                    <audio
                      v-else-if="firstAttachment.type === 'audio'"
                      :src="firstAttachment.url"
                      controls
                      class="attachment-audio"
                      @click.stop
                    />
                    <a
                      v-else
                      :href="firstAttachment.url"
                      target="_blank"
                      class="attachment-file"
                      @click.stop
                    >
                      <Icon name="file" :size="24" />
                      <span class="attachment-file-name">{{ firstAttachment.name }}</span>
                    </a>
                </div>

                <div 
                    v-if="remainingAttachmentsCount > 0" 
                    class="attachment-more-overlay"
                    @click.stop="emit('openAttachments', message.attachments)"
                >
                    +{{ remainingAttachmentsCount }}
                </div>
              </div>

              <p v-if="message.content" class="bubble-text">
                {{ message.content }}
              </p>
            </div>

        </div>

        <div v-if="showReactionPicker" class="reaction-picker-wrapper">
           <ReactionPicker @select="handlePickerSelect" />
        </div>
        
        <div v-if="message.reactions?.length" class="reactions-container" :class="{ 'justify-end': message.is_admin }">
          <button
            v-for="reaction in message.reactions"
            :key="reaction.emoji"
            @click.stop="handleReactionClick(reaction.emoji)"
            @contextmenu.prevent="emit('showDetails', message)"
            class="reaction-btn"
            :class="{ 'active': userHasReacted(reaction) }"
          >
            <span class="reaction-emoji">{{ reaction.emoji }}</span>
            <span v-if="reaction.count > 1" class="reaction-count">{{ reaction.count }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.pinned-label {
    font-size: 10px;
    color: var(--bubble-sent-bg);
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 4px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    opacity: 0.8;
    
    svg {
      opacity: 0.9;
    }
}
</style>