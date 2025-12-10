import React, { useState, useEffect } from "react";
import SearchBar from "../atons/SearchBar";
import MovieCard from "../atons/MovieCard";
import Carousel from "../atons/Carousel";
import { FaFilter } from "react-icons/fa6";
import FilterModal from "../organismo/FilterModal";
import "./Home.css";
import { useNavigate } from "react-router-dom";

// Componente padrão para todas as listas
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

const Home = () => {
  const navigate = useNavigate();
  const [activeGenre, setActiveGenre] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState(""); 
  
  const [moviesData, setMoviesData] = useState([]); 
  const [allGenres, setAllGenres] = useState([]);   
  const [loading, setLoading] = useState(true);

  // Busca inicial
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const token = localStorage.getItem("token"); 
        
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

  const handleSearch = (term) => {
    setSearchTerm(term);
    if (term) setActiveGenre(null);
  };

  const handleGenreClick = (genre) => {
    setActiveGenre(activeGenre === genre ? null : genre);
    setSearchTerm("");
  };

  const handleOpenModal = () => {
    setIsModalOpen(true);
    setActiveGenre(null);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  // Filtros
  const filteredMovies = moviesData.filter(m => {
    if (searchTerm) {
      return m.titulo.toLowerCase().includes(searchTerm.toLowerCase());
    }
    if (activeGenre && activeGenre !== "Geral") {
      const g = m.generos_str || m.genero || "";
      return g.includes(activeGenre);
    }
    return true; 
  });

  const isFilteredPage = activeGenre !== null || searchTerm !== "";

  // Listas de Categorias
  const favsCategory = moviesData.slice(0, 5); // Exemplo: 5 primeiros
  const actionMovies = moviesData.filter(m => (m.generos_str || "").includes("Ação"));
  const comedyMovies = moviesData.filter(m => (m.generos_str || "").includes("Comédia"));
  const romanceMovies = moviesData.filter(m => (m.generos_str || "").includes("Romance"));
  const horrorMovies = moviesData.filter(m => (m.generos_str || "").includes("Terror"));

  if (loading) {
    return <div className="home" style={{ color: "white", textAlign: "center", marginTop: "50px" }}>Carregando...</div>;
  }

  return (
    <div className="home">
      <div className="home-header">
        <SearchBar onSearch={handleSearch} />
      </div>

      <Carousel />

      <div className="genre-navigation">
        <h2 className="section-title">Navegar por gênero</h2>
        <div className="genre-tags">
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

      <div className="content-scroll">
        {isFilteredPage ? (
          <React.Fragment>
            <h2 className="section-title">
              {searchTerm ? `Resultados para: "${searchTerm}"` : 
               activeGenre === "Geral" ? "Filtros Avançados" : `Gênero: ${activeGenre}`}
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
                <p className="no-results" style={{ width: '100%', textAlign: 'center', color: '#888' }}>
                    Nenhum filme encontrado.
                </p>
              )}
            </div>
          </React.Fragment>
        ) : (
          <React.Fragment>
            {/* 🟢 AGORA PADRONIZADO: Favs do momento usa MovieList */}
            {favsCategory.length > 0 && (
              <MovieList title="Favs do momento" movies={favsCategory} />
            )}
            
            {actionMovies.length > 0 && <MovieList title="Ação e Aventura" movies={actionMovies} />}
            {comedyMovies.length > 0 && <MovieList title="Comédias" movies={comedyMovies} />}
            {romanceMovies.length > 0 && <MovieList title="Romance e Drama" movies={romanceMovies} />}
            {horrorMovies.length > 0 && <MovieList title="Terror e Suspense" movies={horrorMovies} />}
            
            {moviesData.length === 0 && (
                <p style={{textAlign: 'center', marginTop: '20px', color: '#666'}}>
                    O catálogo está vazio.
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