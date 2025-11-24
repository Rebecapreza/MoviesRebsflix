import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { FaPencilAlt } from 'react-icons/fa'; // 🟢 Import do ícone de lápis
import './FIlmDetails.css'; // 🟢 Import do CSS (Atenção: o nome do seu arquivo no sistema está com "FI" maiúsculo)

const FilmDetails = () => {
    const { id } = useParams();
    const [movie, setMovie] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchDetails = async () => {
            try {
                // 🟢 Rota ajustada para o singular, conforme o Back-end
                const response = await fetch(`/filme/${id}`);
                const result = await response.json();

                if (response.ok && result.status === 'success') {
                    setMovie(result.movie);
                } else {
                    console.error("Filme não encontrado:", result.message);
                    setMovie(null);
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

    return (
        <div className="film-details-page">
            <div className="main-details-section">
                {/* Coluna do Poster */}
                <div className="poster-column">
                    <img 
                        src={movie.poster_url} 
                        alt={`Pôster de ${movie.titulo}`} 
                        className="details-poster" 
                    />
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
                        <p><strong>Direção:</strong> {movie.diretor || "N/A"}</p>
                        <p><strong>Elenco Principal:</strong> {movie.atores || "N/A"}</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default FilmDetails;