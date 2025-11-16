// src/components/pages/Profile.jsx
import React, { useState } from 'react';
import './Profile.css'; 
import { FaUserCircle } from 'react-icons/fa'; 

const Profile = () => {
    const [userData, setUserData] = useState({
        nome: 'Rebeca Preza',
        email: 'rebeca.preza@rebsflix.com',
        senha: '••••••••', // Placeholder para senha
    });
    
    const [isEditing, setIsEditing] = useState(false);
    const [loading, setLoading] = useState(false); // 🚨 NOVO ESTADO

    const handleChange = (e) => {
        const { name, value } = e.target;
        setUserData({
            ...userData,
            [name]: value
        });
    };

    const handleSave = async (e) => { // 🚨 Tornar async
        e.preventDefault();
        setLoading(true);

        try {
            const response = await fetch('/perfil', { // 🚨 Requisição PUT
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(userData), // Envia os dados do formulário
            });
            const result = await response.json();

            if (response.ok && result.status === 'success') {
                alert("Perfil atualizado com sucesso!");
                setIsEditing(false); // Volta para o modo de visualização
                // Reseta o campo de senha para o placeholder após o sucesso
                setUserData(prev => ({ ...prev, senha: '••••••••' })); 
            } else {
                alert(`Falha ao salvar: ${result.message}`);
            }
        } catch (error) {
            console.error("Erro de rede:", error);
            alert("Erro de rede ao tentar salvar o perfil.");
        } finally {
            setLoading(false);
        }
    };
    
    // ... (restante do componente)

    return (
        <div className="profile-page">
            <div className="profile-card">
                {/* ... */}
                <form onSubmit={handleSave} className="profile-form">
                    {/* ... (Campos Nome e Email) */}
                    
                    {/* Campo Senha */}
                    <div className="form-group">
                        <label>Senha</label>
                        <input
                            type={isEditing ? 'text' : 'password'} 
                            name="senha"
                            className="profile-input"
                            value={userData.senha}
                            onChange={handleChange}
                            disabled={!isEditing || loading} // 🚨 Adicionado loading
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
                        
                        <button type="button" className="btn-logout" onClick={() => console.log('Usuário deslogado')} disabled={loading}>
                            Sair
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default Profile;