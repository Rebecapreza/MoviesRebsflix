import React, { useState } from 'react'; //useState - gerencia o estado no componente funcional
import { useNavigate } from 'react-router-dom';
import logo from '../../assets/Rebsflix.png'; // Logo (botão de play)
import rebsflixTitle from '../../assets/nome rebsflix.png'; // Logo de texto "REBSFLIX"
import './Login.css';

const Login = () => {
  const navigate = useNavigate(); //Usada para redirecionar o usuário para outras páginas
  const [usuario, setUsuario] = useState(''); //Armazena o estado do usuário
  const [senha, setSenha] = useState(''); //Armazena o estado da senha
  const [erroLogin, setErroLogin] = useState('');  // Para exibir mensagem de erro
  const [loading, setLoading] = useState(false); // Novo estado para simular carregamento

  const handleLogin = (e) => {
    e.preventDefault();

    setLoading(true); // Inicia o estado de carregamento
    setErroLogin(''); // Limpa erros anteriores
    
    setTimeout(() => {
        setLoading(false);

        // Verifica se é o usuário ADM ou Comum para simulação
        // Por enquanto, vamos considerar qualquer login como sucesso de Usuário Comum
        if (usuario && senha) {
             // Simulação de sucesso: navega para a página home
            navigate('/home'); 
        } else {
             // Simulação de erro, caso os campos estejam vazios (embora 'required' no input já impeça)
            setErroLogin('Nome de usuário/senha incorretos (simulação)');
        }
       
    }, 1000); // 1 segundo de simulação
    // 🚨 FIM DA SIMULAÇÃO
  };

  return (
    <div className="login-page">
      {/* Container visual da esquerda */}
      <div className="login-visual-background">
        {/* Elemento para o padrão de bolinhas, estilizado via CSS com a imagem */}
        <div className="background-circles-css"></div>
        
        {/* Texto REBSFLIX estilizado como imagem */}
        <img src={rebsflixTitle} alt="REBSFLIX" className="app-title-img" />
      </div>
      
      <div className="login-form-container">
        <div className="login-header">
          {/* Logo (botão de play) */}
          <img src={logo} alt="RebsFlix Logo" className="logo-img-login" />
          <h1>Login</h1>
        </div>

        <form onSubmit={handleLogin} className="login-form">
          <input 
            type="text" 
            placeholder="Email ou nome de usuário" 
            className="login-input" 
            required 
            value={usuario}
            onChange={(e) => setUsuario(e.target.value)}  // Atualiza o estado do nome de usuário/email
            disabled={loading} // Desabilita o input durante o carregamento
          />
          <input 
            type="password" 
            placeholder="Senha" 
            className="login-input" 
            required 
            value={senha}
            onChange={(e) => setSenha(e.target.value)}  // Atualiza o estado da senha
            disabled={loading} // Desabilita o input durante o carregamento
          />
          
          {/* Exibe mensagem de erro caso ocorra algum problema no login */}
          {erroLogin && <p className="error-message">{erroLogin}</p>}

          <div className="forgot-password">
            Esqueceu a senha?
          </div>

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