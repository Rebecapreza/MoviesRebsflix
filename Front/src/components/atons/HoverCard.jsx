// src/components/atons/MovieCard.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import './MovieCard.css'; 

const MovieCard = ({ id, titulo, posterUrl, ano, duracao, rank }) => { // 🚨 Adicionado 'rank'
  
  
  return (
    <Link to={`/filme/${id}`} className={`movie-card-wrapper ${rank ? 'has-rank' : ''}`}>
      
      {/* 🚨 NOVO: Exibe o rank se ele existir */}
      {rank && <span className="movie-rank-badge">{rank}</span>}
      
      <img src={posterUrl} alt={`Pôster de ${titulo}`} className="movie-poster" />
      
      {/* Conteúdo que aparece no hover  */}
      <div className="movie-card-hover-content">
        <h3 className="hover-title">{titulo}</h3>
        <p className="hover-details">{ano} • {duracao}</p>
        <button className="hover-button">Ver mais</button>
      </div>
    </Link>
  );
};

export default MovieCard;