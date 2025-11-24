import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { FaHome, FaUser, FaBell, FaPen, FaPlus } from "react-icons/fa";
import "./NavBar.css";
import logo from "../../assets/Rebsflix.png"; 
import logoText from "../../assets/nome rebsflix.png"; 

const NavBar = () => {
  const [tipoUsuario, setTipoUsuario] = useState('');

  useEffect(() => {
    // Pega o tipo salvo no login ('admin' ou 'usuario')
    const tipo = localStorage.getItem('tipo');
    setTipoUsuario(tipo);
  }, []);

  // Definição dos itens com permissão
  const menuItems = [
    { 
      to: "/home", 
      title: "Página inicial", 
      icon: FaHome, 
      permissao: "todos" // Todos veem
    },
    { 
      to: "/perfil", 
      title: "Perfil", 
      icon: FaUser, 
      permissao: "todos" 
    },
    { 
      to: "/notificacoes", 
      title: "Notificações", 
      icon: FaBell, 
      permissao: "todos" 
    },
    { 
      to: "/filmes/edicao/1", // Link de exemplo (idealmente levaria para uma lista)
      title: "Editar filmes", 
      icon: FaPen, 
      permissao: "admin" // 🔒 APENAS ADMIN
    },
    { 
      to: "/filmes/cadastro", 
      title: "Cadastrar novo filme", 
      icon: FaPlus, 
      permissao: "todos" // Usuário comum pode cadastrar (vai como pendente)
    }
  ];

  return (
    <aside className="sidebar">
      <div className="logo logo-expanded">
        <Link to="/home" className="logo-link">
          <img src={logo} alt="RebsFlix Logo" className="logo-img" />
          <img src={logoText} alt="REBSFLIX" className="logo-text" /> 
        </Link>
      </div>

      <nav className="menu">
        {menuItems.map((item, index) => {
          // Lógica de Verificação:
          // Se a permissão for 'admin' E o usuário NÃO for admin, não renderiza nada.
          if (item.permissao === 'admin' && tipoUsuario !== 'admin') {
            return null;
          }

          return (
            <Link key={index} to={item.to} title={item.title}>
              <item.icon className="menu-icon" /> 
              <span className="menu-text">{item.title}</span> 
            </Link>
          );
        })}
      </nav>
    </aside>
  );
};

export default NavBar;