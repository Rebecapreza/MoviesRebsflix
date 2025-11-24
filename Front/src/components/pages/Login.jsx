import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import logo from '../../assets/Rebsflix.png'; 
import rebsflixTitle from '../../assets/nome rebsflix.png'; 
import './Login.css'; 

const Login = () => {
  const navigate = useNavigate(); 
  const [usuario, setUsuario] = useState(''); 
  const [senha, setSenha] = useState(''); 
  const [erroLogin, setErroLogin] = useState('');  
  const [loading, setLoading] = useState(false); 

<<<<<<< HEAD
  const handleLogin = async (e) => { 
=======
 const handleLogin = async (e) => { 
>>>>>>> 4596edb31e8476a55856e6fdae96d4d3651b9f4f
  e.preventDefault();
  setLoading(true); 
  setErroLogin(''); 

  try {
<<<<<<< HEAD
    // 🟢 CORREÇÃO: Adicionado '/api' antes do login
=======
    // 🟢 CORREÇÃO: Usar apenas '/login' para o Proxy do Vite cuidar da porta (8000)
>>>>>>> 4596edb31e8476a55856e6fdae96d4d3651b9f4f
    const response = await fetch("/api/login", { 
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email: usuario, senha: senha }),
    });

    const result = await response.json();

    if (response.ok) {
      localStorage.setItem("token", result.token);
<<<<<<< HEAD
      localStorage.setItem("tipo", result.user.tipo);
      localStorage.setItem("email", result.user.email);
      // Se tiver ID no retorno, salve também:
      if(result.user.id) localStorage.setItem("id", result.user.id);
      localStorage.setItem("nome", result.user.nome); 
=======
      localStorage.setItem("tipo", result.user.tipo); // Ajustado conforme retorno do Server.py
      localStorage.setItem("email", result.user.email);
>>>>>>> 4596edb31e8476a55856e6fdae96d4d3651b9f4f

      navigate("/home");
    } else {
      setErroLogin(result.error || "Email ou senha inválidos.");
    }
  } catch (error) {
    console.error(error);
    setErroLogin("Não foi possível conectar ao servidor.");
  } finally {
    setLoading(false);
  }
};
<<<<<<< HEAD
=======

>>>>>>> 4596edb31e8476a55856e6fdae96d4d3651b9f4f
  return (
    <div className="login-page">
      <div className="login-visual-background">
        <div className="background-circles-css"></div>
        <img src={rebsflixTitle} alt="REBSFLIX" className="app-title-img" />
      </div>

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