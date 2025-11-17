import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './components/pages/Login';
import Register from './components/pages/Register';
import HomeLayout from './components/pages/HomeLayout';

import MovieForm from './components/organismo/MovieForm';
import FilmDetails from './components/pages/FilmDetails';
import Profile from './components/pages/Profile';
import Notifications from './components/pages/Notifications';

import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        {/* PÁGINA INICIAL AGORA É A HOME */}
        <Route path="/" element={<HomeLayout />} />

        {/* Rotas de Autenticação */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Rotas Principais */}
        <Route path="/home" element={<HomeLayout />} />
        <Route path="/filme/:id" element={<HomeLayout content={<FilmDetails />} />} />
        <Route path="/perfil" element={<HomeLayout content={<Profile />} />} />
        <Route path="/notificacoes" element={<HomeLayout content={<Notifications />} />} />

        {/* Rotas de CRUD */}
        <Route
          path="/filmes/cadastro"
          element={<HomeLayout content={<MovieForm />} />}
        />

        <Route
          path="/filmes/edicao/:id"
          element={<HomeLayout content={<MovieForm isEditing={true} />} />}
        />
      </Routes>
    </Router>
  );
}

export default App;
