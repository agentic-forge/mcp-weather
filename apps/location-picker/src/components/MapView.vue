<script setup lang="ts">
import L from 'leaflet'
import { onMounted, onUnmounted, ref, watch } from 'vue'

interface Location {
  lat: number
  lng: number
  name?: string
  country?: string
}

const props = defineProps<{
  selectedLocation: Location | null
}>()

const emit = defineEmits<{
  (e: 'location-select', location: Location): void
}>()

const mapContainer = ref<HTMLDivElement | null>(null)
let map: L.Map | null = null
let marker: L.Marker | null = null

// Default center (Berlin)
const DEFAULT_CENTER: [number, number] = [52.52, 13.405]
const DEFAULT_ZOOM = 4

onMounted(() => {
  if (!mapContainer.value) return

  // Fix Leaflet icon paths (common issue with bundlers)
  // @ts-expect-error - Leaflet types don't expose _getIconUrl
  delete L.Icon.Default.prototype._getIconUrl
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  })

  // Create map
  map = L.map(mapContainer.value).setView(DEFAULT_CENTER, DEFAULT_ZOOM)

  // Add dark tile layer (CartoDB Dark Matter)
  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 19,
  }).addTo(map)

  // Handle click on map
  map.on('click', (e: L.LeafletMouseEvent) => {
    const { lat, lng } = e.latlng
    emit('location-select', { lat, lng })
  })

  // If there's already a selected location, show it
  if (props.selectedLocation) {
    updateMarker(props.selectedLocation)
  }
})

onUnmounted(() => {
  if (map) {
    map.remove()
    map = null
  }
})

watch(
  () => props.selectedLocation,
  (location) => {
    if (location) {
      updateMarker(location)
    }
  }
)

function updateMarker(location: Location) {
  if (!map) return

  const { lat, lng, name, country } = location

  // Remove existing marker
  if (marker) {
    marker.remove()
  }

  // Add new marker
  marker = L.marker([lat, lng]).addTo(map)

  // Add popup if we have a name
  if (name) {
    const popupContent = country ? `${name}, ${country}` : name
    marker.bindPopup(popupContent).openPopup()
  }

  // Pan to the location
  map.setView([lat, lng], Math.max(map.getZoom(), 10))
}
</script>

<template>
  <div ref="mapContainer" class="map-container"></div>
</template>

<style scoped>
.map-container {
  flex: 1;
  min-height: 300px;
}

/* Leaflet overrides for dark theme */
:deep(.leaflet-control-attribution) {
  background: rgba(22, 33, 62, 0.8) !important;
  color: #888 !important;
}

:deep(.leaflet-control-attribution a) {
  color: #8b5cf6 !important;
}

:deep(.leaflet-control-zoom a) {
  background: #16213e !important;
  color: #eee !important;
  border-color: #0f3460 !important;
}

:deep(.leaflet-control-zoom a:hover) {
  background: #0f3460 !important;
}

:deep(.leaflet-popup-content-wrapper) {
  background: #16213e;
  color: #eee;
  border-radius: 6px;
}

:deep(.leaflet-popup-tip) {
  background: #16213e;
}
</style>
