import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import logo from '../../assets/Rebsflix.png'; // Assume que este é o ícone rosa
import rebsflixTitle from '../../assets/nome rebsflix.png'; // Assume que este é o texto rosa
import './Login.css'; // CSS para estilizar a página de login

const Login = () => {
  const navigate = useNavigate(); 
  const [usuario, setUsuario] = useState(''); // Estado para o e-mail/usuário
  const [senha, setSenha] = useState(''); // Estado para a senha
  const [erroLogin, setErroLogin] = useState('');  // Estado para mensagens de erro
  const [loading, setLoading] = useState(false); // Estado para gerenciar o carregamento

  const handleLogin = async (e) => { 
    e.preventDefault();

    setLoading(true); 
    setErroLogin(''); 

    try {
      const response = await fetch('/login', { 
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        // CRÍTICO: O backend (Server.py/Auth.py) espera 'password', não 'senha'
        body: JSON.stringify({ email: usuario, password: senha }), 
      });

      const result = await response.json();

      // CORREÇÃO: O backend retorna o objeto de sessão em caso de sucesso (status 200) e não possui o campo 'status: success'.
      if (response.ok) { 
        // Armazena o token para ser usado nas requisições protegidas (Home, CRUD)
        localStorage.setItem("authToken", result.token); 
        
        console.log("Login bem-sucedido:", result); 
        navigate('/home'); 
      } else {
        // Falha na autenticação (erros 400, 401). O backend retorna a mensagem em 'error'.
        setErroLogin(result.error || 'Email ou senha inválidos.');
      }
    } catch (error) {
      console.error('Erro de rede ou servidor:', error);
      setErroLogin('Não foi possível conectar ao servidor.');
    } finally {
      setLoading(false); 
    }
  };

  return (
    <div className="login-page">
      {/* Container visual da esquerda (Fundo Escuro) */}
      <div className="login-visual-background">
        <div className="background-circles-css"></div>
        <img src={rebsflixTitle} alt="REBSFLIX" className="app-title-img" />
      </div>

      {/* Container do Formulário de Login (Direita) */}
      <div className="login-form-container">
        <div className="login-header">
          <img src={logo} alt="RebsFlix Logo" className="logo-img-login" />
          <h1>Bem-vindo de volta!</h1>
        </div>

        <form onSubmit={handleLogin} className="login-form">
          <input
            type="email"
            placeholder="E-mail"
            className="login-input"
            required
            value={usuario}
            onChange={(e) => setUsuario(e.target.value)}
            disabled={loading}
          />
          <input
            type="password"
            placeholder="Senha"
            className="login-input"
            required
            value={senha}
            onChange={(e) => setSenha(e.target.value)}
            disabled={loading}
          />
          
          {erroLogin && <p className="error-message" style={{color: '#DE467C'}}>{erroLogin}</p>}

          <div className="forgot-password">Esqueceu a senha?</div>

          <button type="submit" className="login-button" disabled={loading}>
            {loading ? 'Entrando...' : 'Entrar'}
          </button>
        </form>

        <p className="register-prompt">
          Não tem uma conta?
          <a href="/register">Cadastre-se</a>
        </p>
      </div>
    </div>
  );
};

export default Login;