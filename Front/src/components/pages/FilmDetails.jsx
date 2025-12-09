import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { FaPencilAlt } from 'react-icons/fa';
import './FIlmDetails.css'; 

const FilmDetails = () => {
    const { id } = useParams();
    const [movie, setMovie] = useState(null);
    const [loading, setLoading] = useState(true);
    const [errorMsg, setErrorMsg] = useState(null);

    useEffect(() => {
        const fetchDetails = async () => {
            try {
                // Verifica no console o ID que está sendo buscado
                console.log("Buscando filme ID:", id);

                const response = await fetch(`/filme/${id}`);
                
                // Se o servidor devolver erro (404 ou 500)
                if (!response.ok) {
                    throw new Error(`Erro do servidor: ${response.status}`);
                }

                const result = await response.json();
                console.log("Dados recebidos do servidor:", result); 

                if (result.status === 'success' && result.movie) {
                    const dados = result.movie;
                    
                    // Tratamento de dados para evitar quebra
                    setMovie({
                        id_filme: dados.id_filme,
                        titulo: dados.titulo || "Título indisponível",
                        poster_url: dados.poster_url || "", // Garante string vazia se nulo
                        ano: dados.ano || "N/A",
                        // Verifica qual campo o banco mandou
                        duracao: dados.duracao || dados.tp_duracao || "N/A",
                        genero: dados.genero_unico || dados.genero || dados.generos_str || "Gênero não informado",
                        sinopse: dados.sinopse || "Sem sinopse.",
                        diretor: dados.diretor || "N/A",
                        atores: dados.atores || "N/A"
                    });
                } else {
                    setErrorMsg("Filme não encontrado na resposta da API.");
                }
            } catch (error) {
                console.error("Erro no fetch:", error);
                setErrorMsg("Falha ao carregar detalhes. Verifique a conexão.");
            } finally {
                setLoading(false);
            }
        };
        
        if (id) fetchDetails();
    }, [id]);

    if (loading) {
        return <div className="film-details-page" style={{color:'white', padding:'40px'}}>Carregando detalhes...</div>;
    }

    if (errorMsg || !movie) {
        return (
            <div className="film-details-page" style={{color:'white', padding:'40px'}}>
                <h2>Ops!</h2>
                <p>{errorMsg || "Filme não encontrado."}</p>
                <Link to="/home" style={{color: '#DE467C'}}>Voltar para Home</Link>
            </div>
        );
    }

    return (
        <div className="film-details-page">
            <div className="main-details-section">
                {/* Coluna do Poster */}
                <div className="poster-column">
                    {movie.poster_url ? (
                        <img 
                            src={movie.poster_url} 
                            alt={`Pôster de ${movie.titulo}`} 
                            className="details-poster" 
                            onError={(e) => { e.target.src = "https://via.placeholder.com/300x450?text=Sem+Imagem"; }} // Fallback se imagem quebrar
                        />
                    ) : (
                        <div className="details-poster-placeholder">Sem Imagem</div>
                    )}
                </div>

                {/* Coluna de Informações */}
                <div className="info-column">
                    <h1 className="movie-title-details">{movie.titulo}</h1>

                    {/* Metadados */}
                    <div className="movie-metadata">
                        <span className="rating-tag">Livre</span>
                        <span>{movie.ano}</span>
                        <span className="separator">•</span>
                        <span>{movie.genero}</span>
                        <span className="separator">•</span>
                        <span>{movie.duracao}</span>
                    </div>

                    <p className="movie-sinopse">{movie.sinopse}</p>

                    {/* Botões de Ação */}
                    <div className="action-buttons">
                        <Link
                            to={`/filmes/edicao/${movie.id_filme}`}
                            className="btn-edit-film"
                            role="button"
                        >
                            <FaPencilAlt /> Editar
                        </Link>
                    </div>

                    {/* Informações Técnicas */}
                    <div className="movie-cast-info">
                        <p><strong>Direção:</strong> {movie.diretor}</p>
                        <p><strong>Elenco Principal:</strong> {movie.atores}</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default FilmDetails;