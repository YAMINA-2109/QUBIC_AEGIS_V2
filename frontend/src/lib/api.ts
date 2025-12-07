/**
 * API Configuration
 * Centralized configuration for backend API endpoints
 * Automatically detects local vs production and uses appropriate protocols
 */

// Get API URL from environment variable or use default
let API_URL = import.meta.env.VITE_API_URL;
let WS_URL = import.meta.env.VITE_WS_URL;

// If not set in env, use defaults based on environment
if (!API_URL) {
  // Check if we're in development mode or running on localhost
  const isLocal =
    import.meta.env.DEV ||
    window.location.hostname === "localhost" ||
    window.location.hostname === "127.0.0.1" ||
    window.location.hostname === "";

  if (isLocal) {
    API_URL = "http://localhost:8000";
    WS_URL = "ws://localhost:8000";
  } else {
    API_URL = "https://qubic-aegis-backend.onrender.com";
    WS_URL = "wss://qubic-aegis-backend.onrender.com";
  }
}

// If WS_URL is not set but API_URL is, derive WS_URL from API_URL
if (!WS_URL && API_URL) {
  if (API_URL.startsWith("https://")) {
    WS_URL = API_URL.replace("https://", "wss://");
  } else if (API_URL.startsWith("http://")) {
    WS_URL = API_URL.replace("http://", "ws://");
  } else {
    // If no protocol, assume https/wss for production, http/ws for local
    const isLocalUrl =
      API_URL.includes("localhost") ||
      API_URL.includes("127.0.0.1") ||
      API_URL.startsWith("localhost") ||
      API_URL.startsWith("127.0.0.1");

    if (isLocalUrl) {
      WS_URL = `ws://${API_URL.replace(/^https?:\/\//, "")}`;
    } else {
      WS_URL = `wss://${API_URL.replace(/^https?:\/\//, "")}`;
    }
  }
}

// Ensure URLs don't have trailing slash
const cleanApiUrl = API_URL.replace(/\/$/, "");
const cleanWsUrl = WS_URL.replace(/\/$/, "");

export const API_BASE_URL = cleanApiUrl;
export const WS_BASE_URL = cleanWsUrl;

/**
 * Helper function to build API endpoint URLs
 */
export function apiUrl(endpoint: string): string {
  // Remove leading slash if present to avoid double slashes
  const cleanEndpoint = endpoint.startsWith("/") ? endpoint.slice(1) : endpoint;
  return `${API_BASE_URL}/${cleanEndpoint}`;
}

/**
 * Helper function to build WebSocket URLs
 */
export function wsUrl(endpoint: string): string {
  // Remove leading slash if present
  const cleanEndpoint = endpoint.startsWith("/") ? endpoint.slice(1) : endpoint;
  return `${WS_BASE_URL}/${cleanEndpoint}`;
}
