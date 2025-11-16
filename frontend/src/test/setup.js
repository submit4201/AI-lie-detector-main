// Test setup file for Vitest
import '@testing-library/jest-dom'
// Polyfill ResizeObserver for Recharts in JSDOM tests
class ResizeObserver {
	constructor(callback) { this.callback = callback }
	observe() {}
	unobserve() {}
	disconnect() {}
}
global.ResizeObserver = global.ResizeObserver || ResizeObserver;
