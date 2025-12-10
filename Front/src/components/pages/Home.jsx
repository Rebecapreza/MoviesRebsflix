import React, { useState, useEffect } from "react";
import SearchBar from "../atons/SearchBar";
import MovieCard from "../atons/MovieCard";
import Carousel from "../atons/Carousel";
import { FaFilter } from "react-icons/fa6";
import FilterModal from "../organismo/FilterModal";
import "./Home.css";
import { useNavigate } from "react-router-dom";

// Componente reutilizável para renderizar listas horizontais
const MovieList = ({ title, movies }) => (
  <div className="movie-list-section">
    <h2>{title}</h2>
    <div className="movie-list-container">
      {movies.map((movie) => (
        <MovieCard
          key={movie.id_filme}
          id={movie.id_filme}
          titulo={movie.titulo}
          posterUrl={movie.poster}
          ano={movie.ano}
          duracao={movie.duracao_str || movie.duracao || "N/A"}
        />
      ))}
    </div>
  </div>
);

// Componente para renderizar a lista Top 3
const Top3List = ({ title, movies }) => (
  <div className="movie-list-section top-3-section">
    <h2>{title}</h2>
    <div className="movie-list-container top-3-container">
      {movies.slice(0, 3).map((movie, index) => (
        <MovieCard
          key={movie.id_filme}
          id={movie.id_filme}
          titulo={movie.titulo}
          posterUrl={movie.poster}
          ano={movie.ano}
          duracao={movie.duracao_str || movie.duracao || "N/A"}
          rank={index + 1}
        />
      ))}
    </div>
  </div>
);

const Home = () => {
  const navigate = useNavigate();
  const [activeGenre, setActiveGenre] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  // Estados de dados
  const [moviesData, setMoviesData] = useState([]); 
  const [allGenres, setAllGenres] = useState([]);   
  const [loading, setLoading] = useState(true);

  // 1. Busca inicial de TODOS os filmes para extrair Gêneros e montar a Home padrão
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const token = localStorage.getItem("token"); 
        
        // Busca todos os filmes 
        const response = await fetch('/filmes', {
          headers: { 'Authorization': token ? `Bearer ${token}` : "" },
        });

        if (response.ok) {
          const data = await response.json();
          setMoviesData(data);

          const genresSet = new Set();
          data.forEach(movie => {
            const generoRaw = movie.generos_str || movie.genero || "";
            if (generoRaw) {
              generoRaw.split(',').forEach(g => genresSet.add(g.trim()));
            }
          });
          setAllGenres(Array.from(genresSet).sort());

        } else {
          if (response.status === 401) navigate("/");
        }
      } catch (error) {
        console.error("Erro de rede:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchInitialData();
  }, [navigate]);

  // 2. Lógica de Filtro 
  const handleGenreClick = (genre) => {
    setActiveGenre(activeGenre === genre ? null : genre);
  };

  const handleOpenModal = () => {
    setIsModalOpen(true);
    setActiveGenre(null);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  // Aplica o filtro de gênero nos filmes
  const filteredMovies = activeGenre && activeGenre !== "Geral"
    ? moviesData.filter(m => {
        const g = m.generos_str || m.genero || "";
        return g.includes(activeGenre);
      })
    : moviesData;

  // 1. Recentes: Os primeiros 10 filmes 
  const recentMovies = moviesData.slice(0, 10);

  // 2. Categorias Específicas 
  const actionMovies = moviesData.filter(m => (m.generos_str || "").includes("Ação"));
  const comedyMovies = moviesData.filter(m => (m.generos_str || "").includes("Comédia"));
  const romanceMovies = moviesData.filter(m => (m.generos_str || "").includes("Romance"));
  const horrorMovies = moviesData.filter(m => (m.generos_str || "").includes("Terror"));

  const isFilteredPage = activeGenre !== null;

  if (loading) {
    return <div className="home" style={{ color: "white", textAlign: "center", marginTop: "50px" }}>Carregando catálogo...</div>;
  }

  return (
    <div className="home">
      <div className="home-header">
        <SearchBar />
      </div>

      <Carousel />

      {/* Navegação por Gênero */}
      <div className="genre-navigation">
        <h2 className="section-title">Navegar por gênero</h2>
        <div className="genre-tags">
          {/* Mapeia os gêneros que existem no banco */}
          {allGenres.map((genre) => (
            <button
              key={genre}
              className={`genre-tag ${activeGenre === genre ? "active" : ""}`}
              onClick={() => handleGenreClick(genre)}
            >
              {genre}
            </button>
          ))}

          <button
            className={`genre-tag general-filter ${activeGenre === "Geral" ? "active" : ""}`}
            onClick={handleOpenModal}
          >
            <FaFilter /> Geral
          </button>
        </div>
      </div>

      {/* Conteúdo Principal */}
      <div className="content-scroll">
        {isFilteredPage ? (
          // VISUALIZAÇÃO FILTRADA (GRID)
          <React.Fragment>
            <h2 className="section-title">
              {activeGenre === "Geral" ? "Filtros Avançados" : `Gênero: ${activeGenre}`}
            </h2>
            <div className="movie-grid-filtered">
              {filteredMovies.map((movie) => (
                <MovieCard
                  key={movie.id_filme}
                  id={movie.id_filme}
                  titulo={movie.titulo}
                  posterUrl={movie.poster}
                  ano={movie.ano}
                  duracao={movie.duracao_str || "N/A"}
                />
              ))}
              {filteredMovies.length === 0 && (
                <p className="no-results">Nenhum filme encontrado.</p>
              )}
            </div>
          </React.Fragment>
        ) : (
          <React.Fragment>
            {recentMovies.length > 0 && (
              <Top3List title="Adicionados Recentemente" movies={recentMovies} />
            )}

            {/* Listas por Gênero (Só aparecem se tiver filme) */}
            {actionMovies.length > 0 && <MovieList title="Ação e Aventura" movies={actionMovies} />}
            {comedyMovies.length > 0 && <MovieList title="Comédias" movies={comedyMovies} />}
            {romanceMovies.length > 0 && <MovieList title="Romance e Drama" movies={romanceMovies} />}
            {horrorMovies.length > 0 && <MovieList title="Terror e Suspense" movies={horrorMovies} />}
            
            {/* Fallback se o banco estiver vazio */}
            {moviesData.length === 0 && (
                <p style={{textAlign: 'center', marginTop: '20px', color: '#666'}}>
                    O catálogo está vazio. Adicione filmes pelo menu "Cadastrar novo filme".
                </p>
            )}
          </React.Fragment>
        )}
      </div>

      <FilterModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        onApply={(filters) => {
            console.log("Filtros:", filters);
            setActiveGenre("Geral");
        }} 
      />
    </div>
  );
};

export default Home;