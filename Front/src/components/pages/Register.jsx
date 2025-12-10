import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import logoAzul from '../../assets/Rebsflix azul.png';
import rebsflixTitleAzul from '../../assets/nome rebsflix azul.png';

import './Register.css'; 

const Register = () => {
  const navigate = useNavigate();
  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [confirmarSenha, setConfirmarSenha] = useState(''); 
  const [erroCadastro, setErroCadastro] = useState('');
  const [loading, setLoading] = useState(false);

  const handleCadastro = async (e) => {
    e.preventDefault();

    if (!nome || !email || !senha || !confirmarSenha) {
      setErroCadastro('Por favor, preencha todos os campos.');
      return;
    }

    if (senha !== confirmarSenha) {
      setErroCadastro('As senhas não coincidem.');
      return;
    }

    setLoading(true);
    setErroCadastro('');

    try {
      const response = await fetch('/api/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ nome, email, password: senha }),
      });

      const result = await response.json();

      if (response.ok && result.status === 'success') {
        console.log("Cadastro bem-sucedido:", result.message); 
        navigate('/'); 
      } else {
        setErroCadastro(result.message || 'Erro desconhecido ao cadastrar.');
      }

    } catch (error) {
      console.error('Erro de rede ou servidor:', error);
      setErroCadastro('Não foi possível conectar ao servidor. Verifique o console.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="register-page">
      <div className="register-visual-background">
        <div className="background-circles-css"></div>
        <img src={rebsflixTitleAzul} alt="REBSFLIX" className="app-title-img" />
      </div>

      <div className="register-form-container">
        <div className="register-header">
          <img src={logoAzul} alt="RebsFlix Logo" className="logo-img-register" />
          <h1>Cadastro</h1>
        </div>

        <form onSubmit={handleCadastro} className="register-form">
          <input
            type="text"
            placeholder="Nome de usuário"
            className="register-input"
            required
            value={nome}
            onChange={(e) => setNome(e.target.value)}
          />
          <input
            type="email"
            placeholder="E-mail"
            className="register-input"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <input
            type="password"
            placeholder="Senha"
            className="register-input"
            required
            value={senha}
            onChange={(e) => setSenha(e.target.value)}
          />
          <input
            type="password"
            placeholder="Confirmar senha"
            className="register-input"
            required
            value={confirmarSenha}
            onChange={(e) => setConfirmarSenha(e.target.value)}
          />

          {erroCadastro && <p className="error-message">{erroCadastro}</p>}

          <button type="submit" className="register-button" disabled={loading}>
            {loading ? 'Cadastrando...' : 'Cadastrar'}
          </button>
        </form>

        <p className="login-prompt">
          Já tem uma conta?
          <a href="/">Faça login</a>
        </p>
      </div>
    </div>
  );
};

export default Register;