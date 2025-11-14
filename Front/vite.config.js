import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/login': 'http://localhost:8000', // Rotas de API que usam GET/POST
      '/filmes': 'http://localhost:8000',// Rotas de API que usam GET/POST/PUT/DELETE
      //'/register': 'http://localhost:8000',
      '/api/register': 'http://localhost:8000',
    },
  }
})