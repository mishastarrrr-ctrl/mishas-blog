<script setup>
import { ref, computed } from 'vue'
import Icon from './Icon.vue'
import { emojiCategories } from '../emojis'

const props = defineProps({
  customEmojis: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['select', 'close'])

const mode = ref('sticker') //'sticker' | 'emoji'
const activeCategory = ref(0)

const filteredEmojis = computed(() => {
  return emojiCategories[activeCategory.value]?.emojis || []
})

const filteredStickers = computed(() => props.customEmojis)

function selectEmoji(emoji) {
  emit('select', emoji, false)
}

function selectSticker(sticker) {
  emit('select', sticker, true)
}

function handleBackdropClick(e) {
  if (e.target === e.currentTarget) {
    emit('close')
  }
}
</script>

<template>
  <div class="emoji-picker-backdrop" @click="handleBackdropClick">
    <div class="emoji-picker-sheet">
      <div class="emoji-picker-handle">
        <div class="emoji-picker-handle-bar"></div>
      </div>
      
      <div class="emoji-picker-header">
        <h3 class="emoji-picker-title">{{ mode === 'sticker' ? 'Stickers' : 'Emoji' }}</h3>
        <button @click="emit('close')" class="emoji-picker-close">
          <Icon name="close" :size="24" />
        </button>
      </div>

      <div class="emoji-picker-toggle">
        <button 
          :class="['toggle-btn', { active: mode === 'sticker' }]"
          @click="mode = 'sticker'"
        >
          <span>Stickers</span>
        </button>
        <button 
          :class="['toggle-btn', { active: mode === 'emoji' }]"
          @click="mode = 'emoji'"
        >
          <span>Emoji</span>
        </button>
        <div class="toggle-indicator" :class="{ right: mode === 'emoji' }"></div>
      </div>

      <div class="mode-hint">
        <template v-if="mode === 'sticker'">
          <Icon name="info" :size="14" />
          <span>Stickers send as big custom emoji</span>
        </template>
        <template v-else>
          <Icon name="info" :size="14" />
          <span>Emoji inserts into your message</span>
        </template>
      </div>

      <div v-if="mode === 'sticker'" class="emoji-picker-content">
        <div class="category-label">Custom Stickers</div>
        
        <div v-if="filteredStickers.length > 0" class="sticker-grid">
          <button
            v-for="sticker in filteredStickers"
            :key="sticker.id || sticker.shortcode"
            class="sticker-option"
            @click="selectSticker(sticker)"
            :title="sticker.name || sticker.shortcode"
          >
            <img :src="sticker.url" :alt="sticker.name || sticker.shortcode" class="sticker-img" />
          </button>
        </div>

        <div v-else class="emoji-empty">
          <template v-if="customEmojis.length === 0">
            No custom stickers available
          </template>
          <template v-else>
            No stickers found
          </template>
        </div>
      </div>

      <template v-else>
        <div class="emoji-category-tabs">
          <button
            v-for="(category, index) in emojiCategories"
            :key="category.name"
            :class="['category-tab', { active: activeCategory === index }]"
            @click="activeCategory = index"
            :title="category.name"
          >
            {{ category.emojis[0] }}
          </button>
        </div>

        <div class="emoji-picker-content">
          <div class="category-label">
            {{ emojiCategories[activeCategory]?.name }}
          </div>
          
          <div class="emoji-grid-picker">
            <button
              v-for="emoji in filteredEmojis"
              :key="emoji"
              class="emoji-option"
              @click="selectEmoji(emoji)"
            >
              <span class="emoji-char">{{ emoji }}</span>
            </button>
          </div>

          <div v-if="filteredEmojis.length === 0" class="emoji-empty">
            No emoji found
          </div>
        </div>
      </template>
    </div>
  </div>
</template>