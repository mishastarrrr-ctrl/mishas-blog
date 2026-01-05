<script setup>
import { ref, computed, onMounted } from 'vue'
import Icon from './Icon.vue'

const props = defineProps({
  url: { type: String, required: true },
  theme: { type: String, default: 'imessage' }
})

const metaData = ref({
  title: null,
  image: null,
  description: null
})

const loading = ref(true)
const error = ref(false)

const domain = computed(() => {
  try {
    const u = new URL(props.url)
    return u.hostname.replace('www.', '')
  } catch {
    return props.url
  }
})

const isMd = computed(() => props.theme === 'material')

async function fetchMetadata() {
  loading.value = true
  error.value = false
  
  try {
    const response = await fetch(`https://api.microlink.io/?url=${encodeURIComponent(props.url)}`)
    const result = await response.json()
    
    if (result.status === 'success') {
      metaData.value = {
        title: result.data.title || domain.value,
        image: result.data.image?.url || null,
        description: result.data.description || result.data.url
      }
    } else {
      error.value = true
    }
  } catch (e) {
    console.error('Failed to fetch link preview', e)
    error.value = true
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchMetadata()
})
</script>

<template>
  <div class="link-preview" :class="theme">
    <a :href="url" target="_blank" class="link-preview-card">

      <div v-if="metaData.image" class="link-preview-image-container">
         <img :src="metaData.image" alt="Link preview" class="link-preview-img" loading="lazy" />
      </div>

      <div v-else class="link-preview-image-placeholder">
         <Icon name="search" :size="24" :theme="theme" />
      </div>

      <div class="link-preview-info">
        <div class="link-preview-title">{{ metaData.title || domain }}</div>
        <div class="link-preview-domain">{{ metaData.description || url }}</div>
      </div>
    </a>
  </div>
</template>