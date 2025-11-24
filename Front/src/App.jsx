import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './components/pages/Login';
import Register from './components/pages/Register';
import HomeLayout from './components/pages/HomeLayout';
import MovieForm from './components/organismo/MovieForm';
import FilmDetails from './components/pages/FilmDetails';
import Profile from './components/pages/Profile';
import Notifications from './components/pages/Notifications';
import ProtectedRoute from './components/ProtectedRoute'; // 🟢 Importe o novo componente

import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} /> {/* Login é a raiz agora */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Rotas Abertas (Logadas) */}
        <Route path="/home" element={<HomeLayout />} />
        <Route path="/filme/:id" element={<HomeLayout content={<FilmDetails />} />} />
        <Route path="/perfil" element={<HomeLayout content={<Profile />} />} />
        <Route path="/notificacoes" element={<HomeLayout content={<Notifications />} />} />

        {/* Rota de Cadastro: Todos podem acessar (Usuário cria pendente, Admin cria aprovado) */}
        <Route
          path="/filmes/cadastro"
          element={
            <ProtectedRoute>
               <HomeLayout content={<MovieForm />} />
            </ProtectedRoute>
          }
        />

        {/* 🔒 Rota de Edição: APENAS ADMIN */}
        <Route
          path="/filmes/edicao/:id"
          element={
            <ProtectedRoute roleRequired="admin">
               <HomeLayout content={<MovieForm isEditing={true} />} />
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;