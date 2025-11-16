import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // 🚨 AVISO: Certifique-se de que o objeto proxy esteja usando a sintaxe correta do JavaScript/JSON
    proxy: {
      // Usando aspas duplas (opcional, mas mais seguro) e vírgula após cada par, exceto o último.
      '/register': 'http://localhost:8000',
      '/login': 'http://localhost:8000',
      '/logout': 'http://localhost:8000',
      '/filmes': 'http://localhost:8000', // Captura /filmes, /filmes/1, /filmes/pending, etc.
      '/generos': 'http://localhost:8000',
      '/anos': 'http://localhost:8000',
      // Não deve haver vírgula após a última entrada!
      // Se houver mais rotas, adicione-as aqui:
      // '/sua_outra_rota': 'http://localhost:8000' 
    },
  }
})