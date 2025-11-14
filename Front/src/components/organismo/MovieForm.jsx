import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import './MovieForm.css';
import { FaUpload, FaTrashAlt } from 'react-icons/fa'; // Importado FaTrashAlt

// Dados simulados do filme para preencher o formulário no modo Edição
const DUMMY_MOVIE_DATA = {
    titulo: 'O Segredo da Floresta (Dados Carregados)',
    ano: '2023', 
    genero: 'Suspense',
    sinopse: 'Um grupo de amigos descobre um segredo sombrio em uma floresta remota. Sinopse original do filme.',
    poster_url: 'http://example.com/poster-floresta.jpg',
};

const MovieForm = ({ isEditing = false }) => { 
    // Captura o ID da URL se estiver em modo de edição
    const { id } = useParams(); 
    
    // Define o título da página baseado no modo
    const pageTitle = isEditing ? "Edição de Filmes" : "Cadastro de Filmes";

    const [formData, setFormData] = useState({
        titulo: '',
        ano: '',
        genero: '',
        sinopse: '',
        poster_url: '',
    });

    // LÓGICA: Carrega dados (Edição) ou Limpa (Cadastro)
    useEffect(() => {
        if (isEditing && id) {
            // MODO EDIÇÃO: Preenche com dados mockados
            setFormData(DUMMY_MOVIE_DATA);
        } else if (!isEditing) {
             // MODO CADASTRO: Garante que esteja limpo
            setFormData({
                titulo: '',
                ano: '',
                genero: '',
                sinopse: '',
                poster_url: '',
            });
        }
    }, [isEditing, id]); 

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        
        // Simulação de envio
        alert(`Filme ${isEditing ? 'editado' : 'cadastrado'} com sucesso (Simulação)!`);
    };
    
    const handleDelete = (e) => {
        e.preventDefault();
        if (window.confirm(`Tem certeza que deseja excluir o filme ID ${id}?`)) {
            alert(`Filme ID ${id} excluído com sucesso (Simulação)!`);
            // Redirecionar para a home ou lista de filmes
        }
    }

    return (
        <div className="movie-form-page">
            <div className="form-card">
                <h1>{pageTitle}</h1>
                <form onSubmit={handleSubmit} className="movie-form">
                    
                    {/* Linha 1: Título e Ano */}
                    <div className="form-group row">
                        <input
                            type="text"
                            name="titulo"
                            placeholder="Título do Filme"
                            className="form-input"
                            value={formData.titulo}
                            onChange={handleChange}
                            required
                        />
                        <input
                            type="number"
                            name="ano"
                            placeholder="Ano de Lançamento"
                            className="form-input short-input"
                            value={formData.ano}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    {/* Linha 2: Gênero e Poster/Imagem */}
                    <div className="form-group row">
                        <input
                            type="text"
                            name="genero"
                            placeholder="Gênero (Ação, Comédia, etc.)"
                            className="form-input"
                            value={formData.genero}
                            onChange={handleChange}
                            required
                        />
                        <div className="poster-input-wrapper">
                            <input
                                type="url"
                                name="poster_url"
                                placeholder="URL do Poster"
                                className="form-input"
                                value={formData.poster_url}
                                onChange={handleChange}
                            />
                            <span className="upload-icon-overlay"><FaUpload /></span>
                        </div>
                    </div>

                    {/* Linha 3: Sinopse (Área de texto maior) */}
                    <textarea
                        name="sinopse"
                        placeholder="Sinopse Completa"
                        className="form-textarea"
                        rows="5"
                        value={formData.sinopse}
                        onChange={handleChange}
                        required
                    />
                    
                    {/* Container de Ações (Botões) */}
                    <div className="form-actions">
                        {/* Botão de Excluir (Apenas em Edição) */}
                        {isEditing && (
                            <button 
                                type="button" 
                                className="form-button btn-delete" 
                                onClick={handleDelete}
                            >
                                <FaTrashAlt /> Excluir Filme
                            </button>
                        )}
                        
                        {/* Botão Principal (Salvar Edição ou Cadastrar Filme) */}
                        <button type="submit" className={`form-button ${isEditing ? 'btn-save-edit' : 'btn-submit-new'}`}>
                            {isEditing ? "Salvar Edição" : "Cadastrar Filme"}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default MovieForm;