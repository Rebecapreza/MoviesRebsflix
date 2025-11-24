import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './MovieForm.css';
import { FaUpload, FaTrashAlt } from 'react-icons/fa'; 

const MovieForm = ({ isEditing = false }) => { 
    const { id } = useParams(); 
    const navigate = useNavigate(); 
    
    const pageTitle = isEditing ? "Edição de Filmes" : "Cadastro de Filmes";

    const [formData, setFormData] = useState({
        titulo: '',
        ano: '',
        genero: '',
        sinopse: '',
        poster_url: '',
        duracao: '', // Adicionei duração pois o backend suporta
        orcamento: '' // Adicionei orçamento pois o backend suporta
    });
    
    const [loading, setLoading] = useState(false);

    // LÓGICA: Carrega dados (Edição)
    useEffect(() => {
        if (isEditing && id) {
            setLoading(true);
            const fetchMovie = async () => {
                try {
                    // Rota singular ajustada conforme correções anteriores
                    const response = await fetch(`/filme/${id}`); 
                    const result = await response.json();
                    
                    if (response.ok && result.status === 'success') {
                        setFormData({
                            titulo: result.movie.titulo || '',
                            ano: result.movie.ano || '',
                            genero: result.movie.genero_unico || result.movie.genero || '',
                            sinopse: result.movie.sinopse || '',
                            poster_url: result.movie.poster_url || '',
                            duracao: result.movie.tp_duracao || '', // Se vier formatado, ok. Se não, o usuário edita.
                            orcamento: result.movie.orcamento || ''
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

    const handleSubmit = async (e) => { 
        e.preventDefault();
        setLoading(true);

        // Se estiver editando, usa PUT. Se cadastrando, usa POST.
        // Ajuste as rotas conforme seu Server.py:
        // Cadastro: /filmes/cadastro
        // Edição: /filmes/edicao/<id> (ou /editarfilme via POST se preferir a rota antiga, mas vamos usar o padrão REST)
        
        // NOTA: Baseado no seu Server.py atualizado no passo anterior, 
        // a rota de cadastro é POST /filmes/cadastro.
        // A rota de edição via PUT é /filmes/edicao/ID.
        
        const method = isEditing ? 'PUT' : 'POST';
        // Adicionei o ID no corpo para garantir compatibilidade com algumas lógicas de backend
        const bodyData = { ...formData, id: id }; 
        
        const url = isEditing ? `/filmes/edicao/${id}` : '/filmes/cadastro';

        // Lógica de autorização (Token)
        const token = localStorage.getItem('token');

        try {
            const response = await fetch(url, {
                method: method,
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}` // Importante enviar o token
                },
                body: JSON.stringify(bodyData),
            });
            const result = await response.json();

            if (response.ok) {
                alert(`Filme ${isEditing ? 'editado' : 'cadastrado'} com sucesso!`);
                navigate('/home');
            } else {
                alert(`Falha: ${result.message || result.error}`);
            }
        } catch (error) {
            console.error("Erro de rede:", error);
            alert("Erro de rede ao submeter o formulário.");
        } finally {
            setLoading(false);
        }
    };
    
    const handleDelete = async (e) => { 
        e.preventDefault();
        if (!window.confirm(`Tem certeza que deseja excluir o filme ID ${id}?`)) {
            return;
        }

        setLoading(true);
        const token = localStorage.getItem('token');

        try {
            const response = await fetch(`/filmes/edicao/${id}`, { 
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            const result = await response.json();

            if (response.ok) {
                alert(result.message || "Filme excluído.");
                navigate('/home');
            } else {
                alert(`Falha na exclusão: ${result.message || result.error}`);
            }
        } catch (error) {
            console.error("Erro de rede:", error);
            alert("Erro de rede ao tentar excluir o filme.");
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="movie-form-page">
            <div className="form-card">
                <h1>{pageTitle}</h1>
                <form onSubmit={handleSubmit} className="movie-form">
                    
                    {/* --- 1. Título --- */}
                    <div className="form-group">
                        <input 
                            type="text" 
                            name="titulo" 
                            placeholder="Título do Filme" 
                            className="form-input"
                            value={formData.titulo}
                            onChange={handleChange}
                            required 
                        />
                    </div>

                    {/* --- 2. Ano, Duração e Orçamento (Linha) --- */}
                    <div className="form-group row">
                        <input 
                            type="number" 
                            name="ano" 
                            placeholder="Ano" 
                            className="form-input short-input"
                            value={formData.ano}
                            onChange={handleChange}
                            required 
                        />
                        <input 
                            type="text" 
                            name="duracao" 
                            placeholder="Duração (min)" 
                            className="form-input short-input"
                            value={formData.duracao}
                            onChange={handleChange}
                        />
                         <input 
                            type="text" 
                            name="orcamento" 
                            placeholder="Orçamento" 
                            className="form-input"
                            value={formData.orcamento}
                            onChange={handleChange}
                        />
                    </div>

                    {/* --- 3. Gênero --- */}
                    <div className="form-group">
                        <input 
                            type="text" 
                            name="genero" 
                            placeholder="Gêneros (separados por vírgula)" 
                            className="form-input"
                            value={formData.genero}
                            onChange={handleChange}
                            required 
                        />
                    </div>

                    {/* --- 4. Poster URL --- */}
                    <div className="form-group">
                        <div className="poster-input-wrapper">
                            <input 
                                type="text" 
                                name="poster_url" 
                                placeholder="URL da imagem do Poster" 
                                className="form-input"
                                value={formData.poster_url}
                                onChange={handleChange}
                                required 
                            />
                            <FaUpload className="upload-icon-overlay" />
                        </div>
                    </div>

                    {/* --- 5. Sinopse --- */}
                    <div className="form-group">
                        <textarea 
                            name="sinopse" 
                            placeholder="Sinopse do filme..." 
                            className="form-textarea"
                            value={formData.sinopse}
                            onChange={handleChange}
                            required
                        ></textarea>
                    </div>

                    {/* --- Botões de Ação --- */}
                    <div className="form-actions">
                        {/* Botão de Excluir (Apenas em Edição) */}
                        {isEditing && (
                            <button 
                                type="button" 
                                className="form-button btn-delete" 
                                onClick={handleDelete}
                                disabled={loading}
                            >
                                <FaTrashAlt /> {loading ? '...' : 'Excluir Filme'}
                            </button>
                        )}
                        
                        {/* Botão Principal */}
                        <button 
                            type="submit" 
                            className={`form-button ${isEditing ? 'btn-save-edit' : 'btn-submit-new'}`} 
                            disabled={loading}
                        >
                            {loading ? 'Processando...' : (isEditing ? "Salvar Edição" : "Cadastrar Filme")}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default MovieForm;