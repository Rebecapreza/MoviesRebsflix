// src/components/pages/HomeLayout.jsx
import React from 'react';
import NavBar from '../celula/NavBar';
import Home from './Home';
import '../../App.css'; 

const HomeLayout = ({ content }) => {
  return (
    <div className="app">
      <NavBar />
      {/* força o conteúdo a respeitar a largura da NavBar */}
      <div className="main-content-wrapper">
          {/* Renderiza o conteúdo dinâmico se for fornecido (FilmDetails, Profile), senão a Home */}
          {content ? content : <Home />}
      </div>
    </div>
  );
};

export default HomeLayout;