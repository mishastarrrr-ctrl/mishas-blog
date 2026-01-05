<script setup>
import { ref, watch, onMounted } from 'vue'
import { useChatStore } from '../stores/chat'
import Icon from './Icon.vue'

const emit = defineEmits(['select', 'close'])

const chatStore = useChatStore()
const searchQuery = ref('')
const gifs = ref([])
const loading = ref(false)
const nextPos = ref(null)
const searchTimeout = ref(null)
const error = ref('')

async function loadTrending() {
  loading.value = true
  error.value = ''
  try {
    const result = await chatStore.getTrendingGifs()
    gifs.value = result.results
    nextPos.value = result.next
  } catch (e) {
    error.value = e.message || 'Failed to load GIFs'
    console.error('Failed to load trending GIFs:', e)
  } finally {
    loading.value = false
  }
}

async function searchGifs() {
  if (!searchQuery.value.trim()) {
    await loadTrending()
    return
  }
  
  loading.value = true
  error.value = ''
  try {
    const result = await chatStore.searchGifs(searchQuery.value)
    gifs.value = result.results
    nextPos.value = result.next
  } catch (e) {
    error.value = e.message || 'Failed to search GIFs'
    console.error('Failed to search GIFs:', e)
  } finally {
    loading.value = false
  }
}

async function loadMore() {
  if (!nextPos.value || loading.value) return
  
  loading.value = true
  try {
    const result = searchQuery.value.trim()
      ? await chatStore.searchGifs(searchQuery.value, nextPos.value)
      : await chatStore.getTrendingGifs(nextPos.value)
    
    gifs.value = [...gifs.value, ...result.results]
    nextPos.value = result.next
  } catch (e) {
    console.error('Failed to load more GIFs:', e)
  } finally {
    loading.value = false
  }
}

function handleSearchInput() {
  clearTimeout(searchTimeout.value)
  searchTimeout.value = setTimeout(searchGifs, 300)
}

function selectGif(gif) {
  emit('select', {
    id: gif.id,
    url: gif.url,
    preview_url: gif.preview_url
  })
}

function handleScroll(e) {
  const { scrollTop, scrollHeight, clientHeight } = e.target
  if (scrollHeight - scrollTop - clientHeight < 200) {
    loadMore()
  }
}

onMounted(loadTrending)
</script>

<template>
  <div class="gif-picker-overlay" @click="emit('close')">
    <div class="gif-picker" @click.stop>
      <div class="gif-picker-header">
        <div class="gif-search-container">
          <Icon name="search" :size="18" class="gif-search-icon" />
          <input
            v-model="searchQuery"
            @input="handleSearchInput"
            type="text"
            placeholder="Search GIFs..."
            class="gif-search-input"
            autofocus
          />
        </div>
        <button @click="emit('close')" class="gif-close-btn">
          <Icon name="close" :size="20" />
        </button>
      </div>
      
      <div class="gif-content" @scroll="handleScroll">
        <div v-if="error" class="gif-error">
          {{ error }}
        </div>
        
        <div v-else-if="loading && gifs.length === 0" class="gif-loading">
          Loading...
        </div>
        
        <div v-else-if="gifs.length === 0" class="gif-empty">
          No GIFs found
        </div>
        
        <div v-else class="gif-grid">
          <div
            v-for="gif in gifs"
            :key="gif.id"
            class="gif-item"
            @click="selectGif(gif)"
          >
            <img 
              :src="gif.preview_url" 
              :alt="gif.title"
              loading="lazy"
            />
          </div>
        </div>
        
        <div v-if="loading && gifs.length > 0" class="gif-loading-more">
          Loading more...
        </div>
      </div>
      
      <div class="gif-footer">
        <span class="tenor-attribution">Powered by Tenor</span>
      </div>
    </div>
  </div>
</template>