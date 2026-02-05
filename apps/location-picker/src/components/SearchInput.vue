<script setup lang="ts">
import { ref } from 'vue'

interface Location {
  lat: number
  lng: number
  name?: string
  country?: string
}

interface GeoResult {
  name: string
  country: string
  latitude: number
  longitude: number
}

const props = defineProps<{
  searchFn: (query: string) => Promise<GeoResult[]>
}>()

const emit = defineEmits<{
  (e: 'select', location: Location): void
}>()

const query = ref('')
const results = ref<GeoResult[]>([])
const isSearching = ref(false)
const showResults = ref(false)

let searchTimeout: ReturnType<typeof setTimeout> | null = null

function handleInput() {
  // Debounce search
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }

  if (query.value.length < 2) {
    results.value = []
    showResults.value = false
    return
  }

  searchTimeout = setTimeout(async () => {
    await performSearch()
  }, 300)
}

async function performSearch() {
  if (query.value.length < 2) return

  isSearching.value = true
  showResults.value = true

  try {
    results.value = await props.searchFn(query.value)
  } catch (error) {
    console.error('Search failed:', error)
    results.value = []
  } finally {
    isSearching.value = false
  }
}

// Expose for parent to call programmatically if needed
async function handleSearchWithCallback(searchFn: (q: string) => Promise<GeoResult[]>) {
  if (query.value.length < 2) return

  isSearching.value = true
  showResults.value = true

  try {
    results.value = await searchFn(query.value)
  } catch (error) {
    console.error('Search failed:', error)
    results.value = []
  } finally {
    isSearching.value = false
  }
}

function selectResult(result: GeoResult) {
  emit('select', {
    lat: result.latitude,
    lng: result.longitude,
    name: result.name,
    country: result.country,
  })
  query.value = `${result.name}, ${result.country}`
  showResults.value = false
}

function handleBlur() {
  // Delay hiding results to allow click on result
  setTimeout(() => {
    showResults.value = false
  }, 200)
}

// Expose for parent to call with search function
defineExpose({ handleSearchWithCallback })
</script>

<template>
  <div class="search-container">
    <div class="search-input-wrapper">
      <svg
        class="search-icon"
        xmlns="http://www.w3.org/2000/svg"
        width="18"
        height="18"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <circle cx="11" cy="11" r="8" />
        <path d="m21 21-4.3-4.3" />
      </svg>
      <input
        v-model="query"
        type="text"
        placeholder="Search for a city..."
        class="search-input"
        @input="handleInput"
        @focus="showResults = results.length > 0"
        @blur="handleBlur"
      />
      <div v-if="isSearching" class="spinner"></div>
    </div>

    <div v-if="showResults && results.length > 0" class="search-results">
      <button
        v-for="result in results"
        :key="`${result.latitude}-${result.longitude}`"
        class="search-result"
        @click="selectResult(result)"
      >
        <span class="result-name">{{ result.name }}</span>
        <span class="result-country">{{ result.country }}</span>
      </button>
    </div>

    <div v-else-if="showResults && !isSearching && query.length >= 2" class="search-results">
      <div class="no-results">No results found</div>
    </div>
  </div>
</template>

<style scoped>
.search-container {
  flex: 1;
  position: relative;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 12px;
  color: var(--text-secondary, #888);
  pointer-events: none;
}

.search-input {
  width: 100%;
  height: 40px;
  padding: 0 40px 0 40px;
  background: var(--bg-tertiary, #0f3460);
  border: 1px solid var(--border-color, #0f3460);
  border-radius: 6px;
  color: var(--text-primary, #eee);
  font-size: 0.9375rem;
  outline: none;
  transition: border-color 0.2s;
}

.search-input::placeholder {
  color: var(--text-secondary, #666);
}

.search-input:focus {
  border-color: var(--primary-color, #8b5cf6);
}

.spinner {
  position: absolute;
  right: 12px;
  width: 16px;
  height: 16px;
  border: 2px solid var(--border-color, #0f3460);
  border-top-color: var(--primary-color, #8b5cf6);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.search-results {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: var(--bg-secondary, #16213e);
  border: 1px solid var(--border-color, #0f3460);
  border-radius: 6px;
  overflow: hidden;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.search-result {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 0.75rem 1rem;
  background: none;
  border: none;
  color: var(--text-primary, #eee);
  cursor: pointer;
  text-align: left;
  transition: background-color 0.15s;
}

.search-result:hover {
  background: var(--bg-tertiary, #0f3460);
}

.search-result:not(:last-child) {
  border-bottom: 1px solid var(--border-color, #0f3460);
}

.result-name {
  font-weight: 500;
}

.result-country {
  color: var(--text-secondary, #888);
  font-size: 0.875rem;
}

.no-results {
  padding: 1rem;
  color: var(--text-secondary, #888);
  text-align: center;
  font-size: 0.875rem;
}
</style>
