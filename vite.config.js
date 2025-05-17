import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    emptyOutDir: false // dist/ 자동 정리
  },
  server: {
    port: 3000,
    host: true
  }
})