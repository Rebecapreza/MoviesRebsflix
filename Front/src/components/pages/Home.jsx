import React, { useState } from "react";
import SearchBar from "../atons/SearchBar";
import MovieCard from "../atons/MovieCard"; 
import Carousel from "../atons/Carousel"; 
import { FaClapperboard, FaFilter } from "react-icons/fa6"; 
import FilterModal from "../organismo/FilterModal"; // Modal de Filtro
import "./Home.css"; 

// --- DADOS FICTÍCIOS PARA SIMULAÇÃO ---
const DUMMY_MOVIES = [
    { id: 1, titulo: "Filme 1", posterUrl: "/posters/dama.jpg", ano: 2021, duracao: '1h45m' },
    { id: 2, titulo: "Filme 2", posterUrl: "/posters/dark.jpg", ano: 2019, duracao: '2h01m' },
    { id: 3, titulo: "Filme 3", posterUrl: "/posters/arrival.jpg", ano: 2016, duracao: '1h56m' },
    { id: 4, titulo: "Filme 4", posterUrl: "/posters/sabrina.jpg", ano: 2018, duracao: '1h35m' },
    { id: 5, titulo: "Filme 5", posterUrl: "/posters/dark.jpg", ano: 2020, duracao: '1h50m' },
    { id: 10, titulo: "Favs 1", posterUrl: "/posters/favs1.jpg", ano: 2022, duracao: '1h30m' },
];

const categories = [
    { id: '1', title: "Filmes do mês", movies: DUMMY_MOVIES.slice(0, 5) },
    { id: '2', title: "Favs do momento", movies: DUMMY_MOVIES.slice(1, 6) },
    { id: '3', title: "Comédias românticas", movies: DUMMY_MOVIES.slice(0, 5) },
    { id: '4', title: "Ação", movies: DUMMY_MOVIES.slice(2, 7) },
];

const GENRES = ["Fantasia", "Terror", "Ação", "Romance", "Comédia", "Drama", "Ficção", "Documentário", "Infantil", "Suspense", "Animação"];
// ----------------------------------------

// Componente reutilizável para renderizar listas horizontais
const MovieList = ({ title, movies }) => (
    <div className="movie-list-section">
        <h2>{title}</h2>
        <div className="movie-list-container">
            {movies.map(movie => (
                <MovieCard 
                    key={movie.id} 
                    id={movie.id} 
                    titulo={movie.titulo} 
                    posterUrl={movie.posterUrl}
                    ano={movie.ano} 
                    duracao={movie.duracao} 
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
            {movies.slice(0, 3).map((movie, index) => ( // Limita a 3
                <MovieCard 
                    key={movie.id} 
                    id={movie.id} 
                    titulo={movie.titulo} 
                    posterUrl={movie.posterUrl}
                    ano={movie.ano} 
                    duracao={movie.duracao} 
                    rank={index + 1} // Passa o rank (1, 2, 3)
                />
            ))}
        </div>
    </div>
);

const Home = () => {
  const [activeGenre, setActiveGenre] = useState(null); 
  // Estado para o Modal de Filtro
  const [isModalOpen, setIsModalOpen] = useState(false);
  // Estado para armazenar o filtro geral aplicado
  const [generalFilters, setGeneralFilters] = useState({});
  
  // Lista de filmes simulada para a Page Filtrada
  const filteredMovies = [
    { id: 6, titulo: "Bambi", posterUrl: "/posters/bambi.jpg", genre: "Fantasia", ano: 1942, duracao: '1h10m' },
    { id: 7, titulo: "Ice Age", posterUrl: "/posters/iceage.jpg", genre: "Fantasia", ano: 2002, duracao: '1h21m' },
    { id: 8, titulo: "Good Boy", posterUrl: "/posters/goodboy.jpg", genre: "Fantasia", ano: 2020, duracao: '1h35m' },
    { id: 9, titulo: "Winnie", posterUrl: "/posters/winnie.jpg", genre: "Fantasia", ano: 2011, duracao: '1h03m' },
  ];

  const handleGenreClick = (genre) => {
    // Lógica para alternar: clica no ativo, desativa.
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
    // 🚨 FUTURO: Aqui você chamaria a API para buscar filmes com os 'filters' aplicados
    console.log("Filtros Gerais Aplicados:", filters);
    setGeneralFilters(filters);
    // Para fins de simulação, se algum filtro foi aplicado, consideramos a página como filtrada
    if (Object.values(filters).some(val => val !== '')) {
        setActiveGenre('Geral'); // Usamos 'Geral' como um indicador de filtro ativo
    } else {
        setActiveGenre(null); // Nenhum filtro aplicado, volta para a home
    }
  };
  
  // Função para rolar o carrossel de gênero - REMOVIDA
  
  const isFilteredPage = activeGenre !== null;
  
  // Identifica a categoria Top 3
  const favsCategory = categories.find(c => c.title === "Favs do momento");
  // Filtra as outras categorias
  const otherCategories = categories.filter(c => c.title !== "Favs do momento");

  // DETERMINA O TÍTULO PARA A PÁGINA FILTRADA
  let filteredPageTitle = '';
  if (activeGenre === 'Geral') {
      // Cria um título descritivo a partir dos filtros gerais
      const activeFilters = Object.entries(generalFilters)
          .filter(([, value]) => value !== '')
          .map(([, value]) => `${value}`);
          
      filteredPageTitle = `Resultados de: ${activeFilters.join(' • ') || 'Filtro Geral'}`;
  } else if (activeGenre) {
      filteredPageTitle = `Filmes de ${activeGenre}`;
  }


  // DEFINIÇÃO DO CONTEÚDO PRINCIPAL (COM TÍTULO DINÂMICO)
  const mainContent = isFilteredPage ? (
    <>
      {/* 🚨 TÍTULO DINÂMICO PARA FILTRO 🚨 */}
      <h2 className="section-title">{filteredPageTitle}</h2>
      
      {/* CONTEÚDO DA PAGE FILTRADA (o grid) */}
      <div className="movie-grid-filtered">
          {/* Usamos a lista de filmes mockada para a simulação */}
          {filteredMovies.map(movie => (
              <MovieCard 
                  key={movie.id} 
                  id={movie.id} 
                  titulo={movie.titulo} 
                  posterUrl={movie.posterUrl}
                  ano={movie.ano}
                  duracao={movie.duracao}
              />
          ))}
      </div>
    </>
  ) : (
    // CONTEÚDO DA HOME PAGE (Listas)
    <>
        {/* Renderiza a lista Top 3 separadamente no topo */}
        {favsCategory && <Top3List title={favsCategory.title} movies={favsCategory.movies} />}

        {/* Renderiza as outras listas normais */}
        {otherCategories.map(category => (
            <MovieList 
                key={category.id} 
                title={category.title} 
                movies={category.movies} 
            />
        ))}
    </>
  );

  return (
    <div className="home">
      <div className="home-header">
        <SearchBar />
      </div>
      
      {/* INTEGRAÇÃO DO CARROSSEL */}
      <Carousel />
      
      
      
      {/* 2. Filtros (Rolagem Horizontal Sem Setas) */}
      <div className="genre-navigation">
        <h2 className="section-title">Navegar por gênero</h2>
        
        {/* Container principal das tags - sem wrapper e sem refs */}
        <div className="genre-tags">
            {GENRES.map(genre => (
                <button 
                    key={genre}
                    className={`genre-tag ${activeGenre === genre ? 'active' : ''}`}
                    onClick={() => handleGenreClick(genre)}
                >
                    {genre}
                </button>
            ))}
            
            {/* Botão Filtro Geral */}
            <button 
                className={`genre-tag general-filter ${activeGenre === 'Geral' ? 'active' : ''}`}
                onClick={handleOpenModal}
                title="Abrir filtros avançados (Ano, Diretor, etc.)"
            >
                <FaFilter /> Geral
            </button>
        </div>
        
      </div>
      
      {/* 3. Conteúdo Principal (Lista Filtrada ou Listas da Home) */}
      <div className="content-scroll">
        {mainContent}
      </div>
      
      {/* Modal de Filtro Geral */}
      <FilterModal
          isOpen={isModalOpen}
          onClose={handleCloseModal}
          onApplyFilter={handleApplyGeneralFilter}
      />
    </div>
  );
};

export default Home;