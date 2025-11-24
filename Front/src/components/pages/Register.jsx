import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import logoAzul from '../../assets/Rebsflix azul.png';
import rebsflixTitleAzul from '../../assets/nome rebsflix azul.png';

import './Register.css'; 

const Register = () => {
  const navigate = useNavigate(); // Hook para navegação
  const [nome, setNome] = useState(''); // Estado para armazenar o nome de usuário
  const [email, setEmail] = useState(''); // Estado para armazenar o e-mail
  const [senha, setSenha] = useState(''); // Estado para armazenar a senha
  const [confirmarSenha, setConfirmarSenha] = useState(''); 
  const [erroCadastro, setErroCadastro] = useState(''); // Estado para mensagens de erro
  const [loading, setLoading] = useState(false); // Novo estado para simular carregamento

  // Função que será chamada quando o formulário for enviado
  const handleCadastro = async (e) => {
    e.preventDefault();

    // Validação inicial do lado do cliente
    if (!nome || !email || !senha || !confirmarSenha) {
      setErroCadastro('Por favor, preencha todos os campos.');
      return;
    }

    if (senha !== confirmarSenha) {
      setErroCadastro('As senhas não coincidem.');
      return;
    }

    setLoading(true); // Inicia o estado de carregamento
    setErroCadastro(''); // Limpa erros anteriores

    try {
<<<<<<< HEAD
      // 🚨 CONEXÃO REAL COM O BACK-END PYTHON na rota /register
=======
>>>>>>> 4596edb31e8476a55856e6fdae96d4d3651b9f4f
      const response = await fetch('/api/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        // Certifique-se de que os nomes de campo (nome, email, senha) 
        // correspondem exatamente aos esperados pelo Server.py
        body: JSON.stringify({ nome, email, password: senha }),
      });

      const result = await response.json();

      if (response.ok && result.status === 'success') {
        // Sucesso no cadastro
        // Substituindo alert por console.log para não bloquear o iFrame.
        console.log("Cadastro bem-sucedido:", result.message); 
        // alert(result.message); 
        navigate('/'); // Redireciona para o login
      } else {
        // Falha (erros de validação ou do DB - ex: e-mail já existe)
        setErroCadastro(result.message || 'Erro desconhecido ao cadastrar.');
      }

    } catch (error) {
      // Erro de rede ou servidor
      console.error('Erro de rede ou servidor:', error);
      setErroCadastro('Não foi possível conectar ao servidor. Verifique o console.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="register-page">
      {/* Container visual da esquerda (Fundo Rosa) */}
      <div className="register-visual-background">
        <div className="background-circles-css"></div>
        {/* Usa o logo AZUL para o título no fundo rosa */}
        <img src={rebsflixTitleAzul} alt="REBSFLIX" className="app-title-img" />
      </div>

      {/* Container do Formulário (Fundo Branco) */}
      <div className="register-form-container">
        <div className="register-header">
          {/* Usa o logo AZUL para o ícone no fundo branco */}
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

          {/* Exibe a mensagem de erro, se houver */}
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