import React, { useState, useEffect } from "react";
import SearchBar from "../atons/SearchBar";
import MovieCard from "../atons/MovieCard";
import Carousel from "../atons/Carousel";
import { FaClapperboard, FaFilter } from "react-icons/fa6";
import FilterModal from "../organismo/FilterModal";
import "./Home.css";
import { useNavigate } from "react-router-dom";

// --- DADOS BÁSICOS PARA SIMULAÇÃO DE CATEGORIAS ---
const GENRES = [
  "Fantasia",
  "Terror",
  "Ação",
  "Romance",
  "Comédia",
  "Drama"
];
// ----------------------------------------

// Componente reutilizável para renderizar listas horizontais
const MovieList = ({ title, movies }) => (
  <div className="movie-list-section">
    <h2>{title}</h2>
    <div className="movie-list-container">
      {movies.map((movie) => (
        <MovieCard
          key={movie.id_filme} // 🚨 Usar id_filme da API
          id={movie.id_filme}
          titulo={movie.titulo}
          posterUrl={movie.poster} // 🚨 Usar 'poster' da API
          ano={movie.ano}
          duracao={movie.duracao_str || "1h30m"} // Simulação, já que o backend não retorna duracao
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
      {movies.slice(0, 3).map(
        (
          movie,
          index // Limita a 3
        ) => (
          <MovieCard
            key={movie.id_filme}
            id={movie.id_filme}
            titulo={movie.titulo}
            posterUrl={movie.poster}
            ano={movie.ano}
            duracao={movie.duracao_str || "1h30m"}
            rank={index + 1} // Passa o rank (1, 2, 3)
          />
        )
      )}
    </div>
  </div>
);

const Home = () => {
  const navigate = useNavigate();
  const [activeGenre, setActiveGenre] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [generalFilters, setGeneralFilters] = useState({});
  const [moviesData, setMoviesData] = useState([]);
  const [loading, setLoading] = useState(true);

  // 🚨 LÓGICA DE BUSCA DE FILMES
  useEffect(() => {
    const fetchMovies = async () => {
      // 🚨 Substitua pela lógica de autenticação real (Ex: usar token no header)
      const token = localStorage.getItem("authToken");

      try {
        // Ajusta a URL para incluir filtros se estiverem ativos
        let url = "/filmes";
        const queryParams = new URLSearchParams();
        if (activeGenre && activeGenre !== "Geral") {
          queryParams.append("genero", activeGenre);
        }
        // Adicionar outros filtros se generalFilters estiverem ativos (Não implementado no back, mas preparado no front)

        if (queryParams.toString()) {
          url = `/filmes?${queryParams.toString()}`;
        }

        const response = await fetch(url, {
          headers: {
            Authorization: token ? `Bearer ${token}` : "",
          },
        });

        const result = await response.json();

        if (response.ok) {
          // O backend retorna 'generos' como string (generos_str) na lista, precisamos dela aqui.
          setMoviesData(result);
        } else {
          console.error(
            "Erro ao buscar filmes:",
            result.error || "Erro desconhecido"
          );
          // Se o erro for 401, redireciona para login
          if (response.status === 401) {
            navigate("/");
          }
          setMoviesData([]);
        }
      } catch (error) {
        console.error("Erro de rede ao buscar filmes:", error);
        setMoviesData([]);
      } finally {
        setLoading(false);
      }
    };
    fetchMovies();
  }, [activeGenre, generalFilters, navigate]);

  // Simulação de categorias usando os dados da API
  const categories = [
    { id: "1", title: "Favs do momento", movies: moviesData.slice(0, 5) },
    { id: "2", title: "Filmes do mês", movies: moviesData.slice(5, 10) },
    {
      id: "3",
      title: "Comédias",
      movies: moviesData
        .filter((m) => m.generos_str && m.generos_str.includes("Comédia"))
        .slice(0, 5),
    },
    {
      id: "4",
      title: "Ação e Aventura",
      movies: moviesData
        .filter((m) => m.generos_str && m.generos_str.includes("Ação"))
        .slice(0, 5),
    },
  ];

  const handleGenreClick = (genre) => {
    setActiveGenre(activeGenre === genre ? null : genre);
    setGeneralFilters({}); // Limpa filtros gerais ao selecionar um gênero
  };

  const handleOpenModal = () => {
    setIsModalOpen(true);
    setActiveGenre(null); // Limpa o filtro de gênero ao abrir o filtro geral
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  const handleApplyGeneralFilter = (filters) => {
    // 🚨 FUTURO: Implementar chamada de API com filtros detalhados
    console.log("Filtros Gerais Aplicados:", filters);
    setGeneralFilters(filters);
    // Para fins de simulação, se algum filtro foi aplicado, consideramos a página como filtrada
    if (Object.values(filters).some((val) => val && val !== "")) {
      setActiveGenre("Geral"); // Usamos 'Geral' como um indicador de filtro ativo
    } else {
      setActiveGenre(null); // Nenhum filtro aplicado, volta para a home
    }
  };

  const isFilteredPage = activeGenre !== null;

  const favsCategory = categories.find((c) => c.title === "Favs do momento");
  const otherCategories = categories.filter(
    (c) => c.title !== "Favs do momento"
  );

  let filteredPageTitle = "";
  if (activeGenre === "Geral") {
    const activeFilters = Object.entries(generalFilters)
      .filter(([, value]) => value && value !== "")
      .map(([, value]) => `${value}`);

    filteredPageTitle = `Resultados de: ${
      activeFilters.join(" • ") || "Filtro Geral"
    }`;
  } else if (activeGenre) {
    filteredPageTitle = `Filmes de ${activeGenre}`;
  }

  if (loading) {
    return (
      <div
        className="home"
        style={{ color: "white", textAlign: "center", marginTop: "50px" }}
      >
        Carregando filmes...
      </div>
    );
  }

  // Define o conteúdo principal: lista filtrada ou listas por categoria
  const mainContent = isFilteredPage ? (
    <React.Fragment>
      <h2 className="section-title">{filteredPageTitle}</h2>

      <div className="movie-grid-filtered">
        {moviesData.map((movie) => (
          <MovieCard
            key={movie.id_filme}
            id={movie.id_filme}
            titulo={movie.titulo}
            posterUrl={movie.poster}
            ano={movie.ano}
            duracao={movie.duracao_str || "1h30m"}
          />
        ))}
        {moviesData.length === 0 && (
          <p style={{ width: "100%", textAlign: "center", color: "#a0a0a0" }}>
            Nenhum filme encontrado para os filtros selecionados.
          </p>
        )}
      </div>
    </React.Fragment>
  ) : (
    // CONTEÚDO DA HOME PAGE (Listas) - ONDE OCORRE O ERRO DE SINTAXE
    // 🚨 ABRIR E FECHAR O FRAGMENTO NO MESMO BLOCO
    <React.Fragment>
      {/* Renderiza a lista Top 3 separadamente no topo */}
      {favsCategory && favsCategory.movies.length > 0 && (
        <Top3List title={favsCategory.title} movies={favsCategory.movies} />
      )}

      {/* Renderiza as outras listas normais */}
      {otherCategories.map(
        (category) =>
          category.movies.length > 0 && (
            <MovieList
              key={category.id}
              title={category.title}
              movies={category.movies}
            />
          )
      )}
    </React.Fragment>
  );

  return (
    <div className="home">
      <div className="home-header">
        <SearchBar />
      </div>

      <Carousel />

      {/* 2. Filtros (Rolagem Horizontal Sem Setas) */}
      <div className="genre-navigation">
        <h2 className="section-title">Navegar por gênero</h2>

        <div className="genre-tags">
          {GENRES.map((genre) => (
            <button
              key={genre}
              className={`genre-tag ${activeGenre === genre ? "active" : ""}`}
              onClick={() => handleGenreClick(genre)}
            >
              {genre}
            </button>
          ))}

          <button
            className={`genre-tag general-filter ${
              activeGenre === "Geral" ? "active" : ""
            }`}
            onClick={handleOpenModal}
            title="Abrir filtros avançados (Ano, Diretor, etc.)"
          >
            <FaFilter /> Geral
          </button>
        </div>
      </div>

      {/* 3. Conteúdo Principal (Lista Filtrada ou Listas da Home) */}
      <div className="content-scroll">{mainContent}</div>

      {/* Modal de Filtro Geral */}
      <FilterModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        onApply={handleApplyGeneralFilter} 
      />
    </div>
  );
};

export default Home;
