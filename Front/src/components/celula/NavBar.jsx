import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { FaHome, FaUser, FaBell, FaPlus } from "react-icons/fa";
import "./NavBar.css";
import logo from "../../assets/Rebsflix.png"; 
import logoText from "../../assets/nome rebsflix.png"; 

const NavBar = () => {
  const [tipoUsuario, setTipoUsuario] = useState('');

  useEffect(() => {
    const tipo = localStorage.getItem('tipo');
    setTipoUsuario(tipo);
  }, []);

  const menuItems = [
    { 
      to: "/home", 
      title: "Página inicial", 
      icon: FaHome, 
      permissao: "todos" 
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
      to: "/filmes/cadastro", 
      title: "Cadastrar novo filme", 
      icon: FaPlus, 
      permissao: "todos" 
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