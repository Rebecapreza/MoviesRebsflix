import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',

      // Rotas de filmes
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