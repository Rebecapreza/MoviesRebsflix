import React, { useState, useEffect } from 'react';
import './Profile.css'; 
import { FaUserCircle } from 'react-icons/fa'; 

const Profile = () => {
    const [userData, setUserData] = useState({
        nome: '',
        email: '',
        senha: '••••••••', 
    });
    
    const [isEditing, setIsEditing] = useState(false);
    const [loading, setLoading] = useState(false); 

    // Carregar dados iniciais do localStorage (opcional, mas bom para UX)
    useEffect(() => {
        const emailSalvo = localStorage.getItem('email') || '';
        setUserData(prev => ({ ...prev, email: emailSalvo }));
    }, []);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setUserData({
            ...userData,
            [name]: value
        });
    };

    const handleSave = async (e) => { 
        e.preventDefault();
        setLoading(true);

        // 🟢 CORREÇÃO: Pegar o token para autorizar a requisição
        const token = localStorage.getItem('token');

        try {
            const response = await fetch('/perfil', { 
                method: 'PUT',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}` // 🟢 IMPORTANTE: Envia o token
                },
                body: JSON.stringify(userData), 
            });
            const result = await response.json();

            if (response.ok && result.status === 'success') {
                alert("Perfil atualizado com sucesso!");
                setIsEditing(false); 
                setUserData(prev => ({ ...prev, senha: '••••••••' })); 
            } else {
                alert(`Falha ao salvar: ${result.message || result.error}`);
            }
        } catch (error) {
            console.error("Erro de rede:", error);
            alert("Erro de rede ao tentar salvar o perfil.");
        } finally {
            setLoading(false);
        }
    };
    
    const handleLogout = () => {
        localStorage.clear();
        window.location.href = "/"; // Redireciona para login
    };

    return (
        <div className="profile-page">
            <div className="profile-card">
                <FaUserCircle className="profile-icon" />
                <h1>Meu Perfil</h1>
                
                <form onSubmit={handleSave} className="profile-form">
                    {/* Campo Nome */}
                    <div className="form-group">
                        <label>Nome</label>
                        <input
                            type="text"
                            name="nome"
                            className="profile-input"
                            value={userData.nome}
                            onChange={handleChange}
                            disabled={!isEditing || loading}
                            placeholder="Seu nome"
                        />
                    </div>

                    {/* Campo Email */}
                    <div className="form-group">
                        <label>E-mail</label>
                        <input
                            type="email"
                            name="email"
                            className="profile-input"
                            value={userData.email}
                            onChange={handleChange}
                            disabled={!isEditing || loading}
                        />
                    </div>
                    
                    {/* Campo Senha */}
                    <div className="form-group">
                        <label>Senha</label>
                        <input
                            type={isEditing ? 'text' : 'password'} 
                            name="senha"
                            className="profile-input"
                            value={userData.senha}
                            onChange={handleChange}
                            disabled={!isEditing || loading} 
                            placeholder="Nova senha"
                        />
                    </div>
                    
                    {/* Botões de Ação */}
                    <div className="profile-actions">
                        {isEditing ? (
                            <button type="submit" className="btn-save" disabled={loading}>
                                {loading ? 'Salvando...' : 'Salvar'}
                            </button>
                        ) : (
                            <button type="button" className="btn-edit" onClick={() => setIsEditing(true)} disabled={loading}>
                                Editar Perfil
                            </button>
                        )}
                        
                        <button type="button" className="btn-logout" onClick={handleLogout} disabled={loading}>
                            Sair
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default Profile;