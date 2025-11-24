import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // 🟢 TUDO que começar com /api vai para o servidor Python
      '/api': 'http://localhost:8000',

      // Rotas de filmes (que mantivemos sem /api por compatibilidade)
      '/filmes': 'http://localhost:8000',
      '/filme': 'http://localhost:8000',
      '/generos': 'http://localhost:8000',
      '/anos': 'http://localhost:8000',
      
      // Rotas de admin
      '/pendingcount': 'http://localhost:8000',
      '/filmespendentes': 'http://localhost:8000',
      '/aprovarfilme': 'http://localhost:8000',
      '/deletarfilme': 'http://localhost:8000',
      '/perfil': 'http://localhost:8000',
    },
  }
})