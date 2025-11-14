// src/components/pages/Profile.jsx
import React, { useState } from 'react';
import './Profile.css'; 
import { FaUserCircle } from 'react-icons/fa'; // Ícone de perfil

const Profile = () => {
    // 🚨 1. Estado para os dados do usuário (simulação)
    const [userData, setUserData] = useState({
        nome: 'Rebeca Preza',
        email: 'rebeca.preza@rebsflix.com',
        senha: '••••••••', // A senha nunca é preenchida, apenas exibida
    });
    
    // 🚨 2. Estado para controlar se o formulário está em modo de edição
    const [isEditing, setIsEditing] = useState(false);

    // Função para atualizar os dados ao digitar
    const handleChange = (e) => {
        const { name, value } = e.target;
        setUserData({
            ...userData,
            [name]: value
        });
    };

    // Função executada ao clicar em Salvar
    const handleSave = (e) => {
        e.preventDefault();
        // 🚨 FUTURO: Aqui você enviará os dados atualizados para o Server.py (rota PUT)
        console.log("Perfil salvo:", userData);
        setIsEditing(false); // Volta para o modo de visualização
    };

    return (
        <div className="profile-page">
            <div className="profile-card">
                <FaUserCircle className="profile-icon" />
                <h1>Meu Perfil</h1>

                <form onSubmit={handleSave} className="profile-form">
                    
                    {/* Campo Nome */}
                    <div className="form-group">
                        <label>Nome de Usuário</label>
                        <input
                            type="text"
                            name="nome"
                            className="profile-input"
                            value={userData.nome}
                            onChange={handleChange}
                            disabled={!isEditing}
                        />
                    </div>
                    
                    {/* Campo Email */}
                    <div className="form-group">
                        <label>Email</label>
                        <input
                            type="email"
                            name="email"
                            className="profile-input"
                            value={userData.email}
                            onChange={handleChange}
                            disabled={!isEditing}
                        />
                    </div>
                    
                    {/* Campo Senha (para alteração) */}
                    <div className="form-group">
                        <label>Senha</label>
                        <input
                            // Usa 'text' apenas para simulação, deve ser 'password' em produção
                            type={isEditing ? 'text' : 'password'} 
                            name="senha"
                            className="profile-input"
                            value={userData.senha}
                            onChange={handleChange}
                            disabled={!isEditing}
                        />
                    </div>
                    
                    {/* Botões de Ação */}
                    <div className="profile-actions">
                        {/* Se estiver editando, mostra o botão Salvar */}
                        {isEditing ? (
                            <button type="submit" className="btn-save">
                                Salvar
                            </button>
                        ) : (
                            // Se NÃO estiver editando, mostra o botão Editar
                            <button type="button" className="btn-edit" onClick={() => setIsEditing(true)}>
                                Editar Perfil
                            </button>
                        )}
                        
                        {/* Botão de Logout */}
                        <button type="button" className="btn-logout" onClick={() => console.log('Usuário deslogado')}>
                            Sair
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default Profile;