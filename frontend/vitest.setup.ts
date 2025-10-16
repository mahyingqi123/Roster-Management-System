// Setup env for API base
import.meta.env = { ...(import.meta.env || {}), VITE_API_BASE: 'http://localhost:8000' } as any

// Stub out chart components in unit tests to avoid canvas context errors
import { vi } from 'vitest'
vi.mock('vue-chartjs', () => ({
  Bar: { name: 'Bar', render() { return null } }
}))

// @ts-ignore
if (typeof HTMLCanvasElement !== 'undefined' && !HTMLCanvasElement.prototype.getContext) {
  // @ts-ignore
  HTMLCanvasElement.prototype.getContext = () => ({})
}


