<script setup lang="ts">
import { ref } from 'vue'
import MapView from './components/MapView.vue'
import SearchInput from './components/SearchInput.vue'
import { useAppBridge } from './composables/useAppBridge'

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

const selectedLocation = ref<Location | null>(null)
const { updateModelContext, callServerTool } = useAppBridge()

async function handleLocationSelect(location: Location) {
  selectedLocation.value = location

  // Update model context with the selected location
  await updateModelContext({
    location: {
      lat: location.lat,
      lng: location.lng,
      name: location.name,
      country: location.country,
    },
  })
}

async function searchGeocode(query: string): Promise<GeoResult[]> {
  try {
    // Call the geocode tool on the MCP server
    const result = await callServerTool('geocode', { city: query })
    return (result as GeoResult[]) || []
  } catch (error) {
    console.error('Geocode failed:', error)
    return []
  }
}

async function handleUseMyLocation() {
  if (!navigator.geolocation) {
    console.warn('Geolocation not supported')
    return
  }

  navigator.geolocation.getCurrentPosition(
    (position) => {
      handleLocationSelect({
        lat: position.coords.latitude,
        lng: position.coords.longitude,
        name: 'My Location',
      })
    },
    (error) => {
      console.error('Geolocation error:', error)
    }
  )
}
</script>

<template>
  <div class="location-picker">
    <div class="search-bar">
      <SearchInput :search-fn="searchGeocode" @select="handleLocationSelect" />
      <button class="my-location-btn" @click="handleUseMyLocation" title="Use my location">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <circle cx="12" cy="12" r="3" />
          <path d="M12 2v4M12 18v4M2 12h4M18 12h4" />
        </svg>
      </button>
    </div>

    <MapView :selected-location="selectedLocation" @location-select="handleLocationSelect" />

    <div v-if="selectedLocation" class="selected-info">
      <span class="location-name">{{ selectedLocation.name || 'Selected Location' }}</span>
      <span class="coordinates">
        {{ selectedLocation.lat.toFixed(4) }}, {{ selectedLocation.lng.toFixed(4) }}
      </span>
    </div>
  </div>
</template>

<style scoped>
.location-picker {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bg-primary, #1a1a2e);
}

.search-bar {
  display: flex;
  gap: 0.5rem;
  padding: 0.75rem;
  background: var(--bg-secondary, #16213e);
  border-bottom: 1px solid var(--border-color, #0f3460);
}

.my-location-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: var(--bg-tertiary, #0f3460);
  border: 1px solid var(--border-color, #0f3460);
  border-radius: 6px;
  color: var(--text-secondary, #888);
  cursor: pointer;
  transition: all 0.2s;
}

.my-location-btn:hover {
  background: var(--primary-color, #8b5cf6);
  color: white;
  border-color: var(--primary-color, #8b5cf6);
}

.selected-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: var(--bg-secondary, #16213e);
  border-top: 1px solid var(--border-color, #0f3460);
}

.location-name {
  font-weight: 500;
  color: var(--text-primary, #eee);
}

.coordinates {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 0.875rem;
  color: var(--text-secondary, #888);
}
</style>
