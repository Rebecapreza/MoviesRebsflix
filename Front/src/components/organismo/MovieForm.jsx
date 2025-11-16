import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom'; // 🚨 Importar useNavigate
import './MovieForm.css';
import { FaUpload, FaTrashAlt } from 'react-icons/fa'; 

// REMOVER DUMMY_MOVIE_DATA

const MovieForm = ({ isEditing = false }) => { 
    const { id } = useParams(); 
    const navigate = useNavigate(); // Hook de navegação
    
    const pageTitle = isEditing ? "Edição de Filmes" : "Cadastro de Filmes";

    const [formData, setFormData] = useState({
        titulo: '',
        ano: '',
        genero: '',
        sinopse: '',
        poster_url: '',
    });
    const [loading, setLoading] = useState(false);

    // LÓGICA: Carrega dados (Edição)
    useEffect(() => {
        if (isEditing && id) {
            setLoading(true);
            const fetchMovie = async () => {
                try {
                    const response = await fetch(`/filme/${id}`); // 🚨 GET para pré-preenchimento
                    const result = await response.json();
                    
                    if (response.ok && result.status === 'success') {
                        // O backend retorna 'genero_unico' para o form
                        setFormData({
                            titulo: result.movie.titulo,
                            ano: result.movie.ano,
                            genero: result.movie.genero_unico,
                            sinopse: result.movie.sinopse,
                            poster_url: result.movie.poster_url,
                        });
                    } else {
                        alert(`Erro ao carregar filme: ${result.message}`);
                        navigate('/home');
                    }
                } catch (error) {
                    console.error("Erro de rede:", error);
                    alert("Erro de rede ao carregar filme.");
                    navigate('/home');
                } finally {
                    setLoading(false);
                }
            };
            fetchMovie();
        } 
    }, [isEditing, id, navigate]); 

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e) => { // 🚨 Tornar async
        e.preventDefault();
        setLoading(true);

        const method = isEditing ? 'PUT' : 'POST';
        const url = isEditing ? `/filmes/edicao/${id}` : '/filmes/cadastro';

        try {
            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData),
            });
            const result = await response.json();

            if (response.ok && result.status === 'success') {
                alert(`Filme ${isEditing ? 'editado' : 'cadastrado'} com sucesso!`);
                navigate('/home');
            } else {
                alert(`Falha: ${result.message}`);
            }
        } catch (error) {
            console.error("Erro de rede:", error);
            alert("Erro de rede ao submeter o formulário.");
        } finally {
            setLoading(false);
        }
    };
    
    const handleDelete = async (e) => { // 🚨 Tornar async
        e.preventDefault();
        if (!window.confirm(`Tem certeza que deseja excluir o filme ID ${id}?`)) {
            return;
        }

        setLoading(true);

        try {
            const response = await fetch(`/filmes/edicao/${id}`, { // 🚨 DELETE real
                method: 'DELETE',
            });
            const result = await response.json();

            if (response.ok && result.status === 'success') {
                alert(result.message);
                navigate('/home');
            } else {
                alert(`Falha na exclusão: ${result.message}`);
            }
        } catch (error) {
            console.error("Erro de rede:", error);
            alert("Erro de rede ao tentar excluir o filme.");
        } finally {
            setLoading(false);
        }
    }
    
    // ... (Seção de carregamento)

    return (
        <div className="movie-form-page">
            <div className="form-card">
                <h1>{pageTitle}</h1>
                <form onSubmit={handleSubmit} className="movie-form">
                    {/* ... (Linhas de input com campos controlados) ... */}

                    {/* Container de Ações (Botões) */}
                    <div className="form-actions">
                        {/* Botão de Excluir (Apenas em Edição) */}
                        {isEditing && (
                            <button 
                                type="button" 
                                className="form-button btn-delete" 
                                onClick={handleDelete}
                                disabled={loading}
                            >
                                <FaTrashAlt /> {loading ? 'Excluindo...' : 'Excluir Filme'}
                            </button>
                        )}
                        
                        {/* Botão Principal */}
                        <button type="submit" className={`form-button ${isEditing ? 'btn-save-edit' : 'btn-submit-new'}`} disabled={loading}>
                            {loading ? 'Processando...' : (isEditing ? "Salvar Edição" : "Cadastrar Filme")}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default MovieForm;