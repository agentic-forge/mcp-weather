/**
 * MCP Apps Bridge Composable
 *
 * Handles communication between the MCP App and the host (forge-ui or dev host)
 * using JSON-RPC over postMessage.
 *
 * In production, this would use @modelcontextprotocol/ext-apps SDK.
 * For now, we implement a minimal bridge that works with our dev host.
 */

type JsonRpcRequest = {
  jsonrpc: '2.0'
  id: number
  method: string
  params?: unknown
}

type JsonRpcResponse = {
  jsonrpc: '2.0'
  id: number
  result?: unknown
  error?: { code: number; message: string }
}

type PendingRequest = {
  resolve: (value: unknown) => void
  reject: (error: Error) => void
}

let requestId = 0
const pendingRequests = new Map<number, PendingRequest>()

// Listen for responses from the host
if (typeof window !== 'undefined') {
  window.addEventListener('message', (event) => {
    const message = event.data as JsonRpcResponse

    if (!message || message.jsonrpc !== '2.0' || message.id === undefined) {
      return
    }

    const pending = pendingRequests.get(message.id)
    if (!pending) {
      return
    }

    pendingRequests.delete(message.id)

    if (message.error) {
      pending.reject(new Error(message.error.message))
    } else {
      pending.resolve(message.result)
    }
  })
}

function sendRequest(method: string, params?: unknown): Promise<unknown> {
  return new Promise((resolve, reject) => {
    const id = ++requestId

    const request: JsonRpcRequest = {
      jsonrpc: '2.0',
      id,
      method,
      params,
    }

    pendingRequests.set(id, { resolve, reject })

    // Send to parent window (the host)
    if (window.parent && window.parent !== window) {
      window.parent.postMessage(request, '*')
    } else {
      // Running standalone (not in iframe) - resolve immediately for dev
      console.warn('[AppBridge] Not running in iframe, request will be ignored:', method)
      pendingRequests.delete(id)
      resolve(null)
    }

    // Timeout after 30 seconds
    setTimeout(() => {
      if (pendingRequests.has(id)) {
        pendingRequests.delete(id)
        reject(new Error(`Request timeout: ${method}`))
      }
    }, 30000)
  })
}

export function useAppBridge() {
  /**
   * Update the model context with new data.
   * This is how the app communicates selected values back to the LLM.
   */
  async function updateModelContext(context: Record<string, unknown>): Promise<void> {
    await sendRequest('updateModelContext', { context })
  }

  /**
   * Call a tool on the MCP server.
   * The host will forward this to the appropriate backend.
   */
  async function callServerTool(toolName: string, args: Record<string, unknown>): Promise<unknown> {
    const response = await sendRequest('callServerTool', {
      toolName,
      arguments: args,
    })
    return (response as { result?: unknown })?.result ?? response
  }

  /**
   * Open a link in the user's browser.
   * Links cannot be opened directly due to sandbox restrictions.
   */
  async function openLink(url: string): Promise<void> {
    await sendRequest('openLink', { url })
  }

  /**
   * Log a message to the host's console.
   */
  async function log(level: 'debug' | 'info' | 'warn' | 'error', message: string): Promise<void> {
    await sendRequest('log', { level, message })
  }

  /**
   * Get the current theme from the host.
   */
  async function getTheme(): Promise<'light' | 'dark'> {
    const response = await sendRequest('getTheme', {})
    return (response as { theme?: 'light' | 'dark' })?.theme ?? 'dark'
  }

  return {
    updateModelContext,
    callServerTool,
    openLink,
    log,
    getTheme,
  }
}
