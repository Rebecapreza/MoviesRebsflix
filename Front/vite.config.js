import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',

      '/filmes': 'http://localhost:8000',
      '/filme': 'http://localhost:8000',
      '/generos': 'http://localhost:8000',
      '/anos': 'http://localhost:8000',
    
    },
  }
})