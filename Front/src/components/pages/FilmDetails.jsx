import React from 'react';
import { useParams, Link } from 'react-router-dom'; 
import MovieCard from '../atons/MovieCard';
import { FaPlay, FaRegBookmark, FaStar, FaPencilAlt } from 'react-icons/fa'; 
import './FIlmDetails.css';

const DUMMY_MOVIE_DETAILS = {
    id: 1,
    titulo: 'Bambi', // Baseado no mockup de Page filme individual
    sinopse: "O jovem veado Bambi, que acaba de nascer, explora a vida na floresta com seus amigos: um coelho chamado Tambor e uma gambá chamada Flor. Ele descobre a alegria e a dor da vida e aprende lições preciosas sobre amizade, família e sobrevivência. No entanto, ele deve enfrentar os perigos do mundo dos humanos, especialmente 'O Homem', que representa uma ameaça constante.",
    posterUrl: '/posters/bambi-big.jpg', // Use um poster grande aqui
    ano: 1942,
    genero: 'Animação, Drama, Família',
    duracao: '1h 10m',
    diretor: 'David Hand',
    atores: 'Bobby Stewart, Donnie Dunagan, Hardie Albright',
    classificacao: 'Livre',
};

const DUMMY_RELATED_MOVIES = [
    { id: 2, titulo: "Filme Relacionado 1", posterUrl: "/posters/related1.jpg", ano: 2020, duracao: "1h30m" },
    { id: 3, titulo: "Filme Relacionado 2", posterUrl: "/posters/related2.jpg", ano: 2018, duracao: "2h05m" },
    { id: 4, titulo: "Filme Relacionado 3", posterUrl: "/posters/related3.jpg", ano: 2021, duracao: "1h40m" },
    { id: 5, titulo: "Filme Relacionado 4", posterUrl: "/posters/related4.jpg", ano: 2019, duracao: "1h50m" },
    { id: 6, titulo: "Filme Relacionado 5", posterUrl: "/posters/related5.jpg", ano: 2022, duracao: "1h25m" },
];

const FilmDetails = () => {
    // Captura o ID do filme da URL (ex: /filme/1)
    const { id } = useParams(); 
    
    // Na implementação real: Usar 'id' para buscar os detalhes do filme na API
    // Usamos o ID mockado para DUMMY_MOVIE_DETAILS para ter certeza de que o link funciona
    const movie = DUMMY_MOVIE_DETAILS; 

    return (
        <div className="film-details-page">
            
            <div className="main-details-section">
                {/* ... Poster Column ... */}
                <div className="poster-column">
                    <img src={movie.posterUrl} alt={`Pôster de ${movie.titulo}`} className="details-poster" />
                </div>

                {/* Coluna de Informação */}
                <div className="info-column">
                    <h1 className="movie-title-details">{movie.titulo}</h1>
                    
                    {/* Metadados: L, Ano, Duração, Gênero */}
                    <div className="movie-metadata">
                        {/* Classificação 'Livre' (simulada) */}
                        <span className="rating-tag">{movie.classificacao}</span> 
                        <span>{movie.ano}</span>
                        <span className="separator">•</span>
                        <span>{movie.genero}</span>
                        <span className="separator">•</span>
                        <span>{movie.duracao}</span>
                    </div>

                    {/* Estrelas de Avaliação (Simulação do mockup) */}
                    <div className="movie-rating">
                        <FaStar /> <FaStar /> <FaStar /> <FaStar /> <FaStar />
                    </div>

                    <p className="movie-sinopse">{movie.sinopse}</p>

                    {/* Botões de Ação */}
                    <div className="action-buttons">
                        <button className="btn-primary-play">
                            Ver trailer
                        </button>
                        <button className="btn-secondary-watch">
                            Assistir
                        </button>
                        {/* 🚨 CORREÇÃO: Substituir <button> por <Link> e usar o ID */}
                        <Link 
                            to={`/filmes/edicao/${movie.id}`} // Usar movie.id (que é 1)
                            className="btn-edit-film"
                            role="button"
                        >
                            <FaPencilAlt /> Editar
                        </Link>
                    </div>

                    {/* ... Diretor e Atores (Seção mantida) ... */}
                    <div className="movie-cast-info">
                        <p><strong>Direção:</strong> {movie.diretor}</p>
                        <p><strong>Elenco Principal:</strong> {movie.atores}</p>
                    </div>

                </div>
            </div>

            {/* 2. SEÇÃO DE FILMES RELACIONADOS (Recomendações) */}
            <div className="related-movies-section">
                <h2>Mais filmes que você pode gostar:</h2>
                <div className="movie-list-container"> 
                    {DUMMY_RELATED_MOVIES.map(relMovie => (
                        <MovieCard 
                            key={relMovie.id} 
                            id={relMovie.id} 
                            titulo={relMovie.titulo} 
                            posterUrl={relMovie.posterUrl}
                            ano={relMovie.ano}
                            duracao={relMovie.duracao}
                        />
                    ))}
                </div>
            </div>
        </div>
    );
};

export default FilmDetails;