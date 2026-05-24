import { ref } from 'vue'

// true  = server reachable
// false = confirmed unreachable (show overlay)
export const serverOnline  = ref(true)

// Only true when the server explicitly told us setup_done=false.
// Prevents users from typing /setup manually.
export const setupAllowed  = ref(false)

let _pollTimer = null

export function markOnline() {
  if (serverOnline.value === false) {
    // Was offline — reload for a clean re-init rather than trying to patch state
    window.location.reload()
    return
  }
  serverOnline.value = true
  _stopPoll()
}

export function markOffline() {
  if (serverOnline.value === false) return  // already offline
  serverOnline.value = false
  _startPoll()
}

function _startPoll() {
  if (_pollTimer) return
  _pollTimer = setInterval(async () => {
    try {
      const res = await fetch('/api/status', { cache: 'no-store' })
      if (res.ok) markOnline()
    } catch (_) {}
  }, 4000)
}

function _stopPoll() {
  clearInterval(_pollTimer)
  _pollTimer = null
}
