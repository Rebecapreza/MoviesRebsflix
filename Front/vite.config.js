import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
<<<<<<< HEAD
      // 🟢 TUDO que começar com /api vai para o servidor Python
      '/api': 'http://localhost:8000',

      // Rotas de filmes (que mantivemos sem /api por compatibilidade)
=======
      '/api': 'http://localhost:8000',

>>>>>>> 4596edb31e8476a55856e6fdae96d4d3651b9f4f
      '/filmes': 'http://localhost:8000',
      '/filme': 'http://localhost:8000',
      '/generos': 'http://localhost:8000',
      '/anos': 'http://localhost:8000',
<<<<<<< HEAD
      
      // Rotas de admin
      '/pendingcount': 'http://localhost:8000',
      '/filmespendentes': 'http://localhost:8000',
      '/aprovarfilme': 'http://localhost:8000',
      '/deletarfilme': 'http://localhost:8000',
      '/perfil': 'http://localhost:8000',
=======
    
>>>>>>> 4596edb31e8476a55856e6fdae96d4d3651b9f4f
    },
  }
})