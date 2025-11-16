import React, { useState, useEffect } from 'react'; // 🚨 Importar useState e useEffect
import { useParams, Link } from 'react-router-dom'; 
// ... (outros imports)

// REMOVER DUMMY_MOVIE_DETAILS
// Manter DUMMY_RELATED_MOVIES para simulação de seção relacionada.

const FilmDetails = () => {
    const { id } = useParams(); 
    const [movie, setMovie] = useState(null); // 🚨 NOVO ESTADO: Dados do filme
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchDetails = async () => {
            try {
                const response = await fetch(`/filme/${id}`); // 🚨 Chamada real ao backend
                const result = await response.json();
                
                if (response.ok && result.status === 'success') {
                    setMovie(result.movie);
                } else {
                    console.error("Filme não encontrado:", result.message);
                    setMovie(null); // Marcar como não encontrado
                }
            } catch (error) {
                console.error("Erro de rede ao buscar detalhes:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchDetails();
    }, [id]); 

    if (loading) {
        return <div className="film-details-page">Carregando detalhes do filme...</div>;
    }

    if (!movie) {
        return <div className="film-details-page">Filme não encontrado.</div>;
    }
    
    // O backend agora retorna campos como 'titulo', 'sinopse', 'ano', 'genero', 'duracao'
    // 'diretor' e 'atores' não foram implementados no backend para simplificar, mas os campos estão no JSX.
    // Usaremos as propriedades que o backend retorna para garantir que funcione.

    return (
        <div className="film-details-page">
            
            <div className="main-details-section">
                {/* ... Poster Column ... */}
                <div className="poster-column">
                    <img src={movie.poster_url} alt={`Pôster de ${movie.titulo}`} className="details-poster" />
                </div>

                {/* Coluna de Informação */}
                <div className="info-column">
                    <h1 className="movie-title-details">{movie.titulo}</h1>
                    
                    {/* Metadados: L, Ano, Duração, Gênero */}
                    <div className="movie-metadata">
                        <span className="rating-tag">Livre</span> {/* Simulado */}
                        <span>{movie.ano}</span>
                        <span className="separator">•</span>
                        <span>{movie.genero}</span>
                        <span className="separator">•</span>
                        <span>{movie.duracao}</span>
                    </div>

                    {/* ... (Avaliação e Sinopse) ... */}
                    <p className="movie-sinopse">{movie.sinopse}</p>

                    {/* Botões de Ação */}
                    <div className="action-buttons">
                        {/* ... (Ver trailer, Assistir) ... */}
                        <Link 
                            to={`/filmes/edicao/${movie.id_filme}`} 
                            className="btn-edit-film"
                            role="button"
                        >
                            <FaPencilAlt /> Editar
                        </Link>
                    </div>

                    {/* Diretor e Atores (Dados faltantes no backend, mas mantidos no front-end mockado para demonstração completa) */}
                    <div className="movie-cast-info">
                        <p><strong>Direção:</strong> N/A (Não implementado no backend)</p>
                        <p><strong>Elenco Principal:</strong> N/A (Não implementado no backend)</p>
                    </div>

                </div>
            </div>

            {/* ... (SEÇÃO DE FILMES RELACIONADOS) ... */}
        </div>
    );
};

export default FilmDetails;