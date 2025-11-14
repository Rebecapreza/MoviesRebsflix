import React from "react";
import { Link } from "react-router-dom";
import { FaHome, FaUser, FaBell, FaPen, FaPlus, FaTrash } from "react-icons/fa";
import "./NavBar.css";
import logo from "../../assets/Rebsflix.png"; 
import logoText from "../../assets/nome rebsflix.png"; 

const menuItems = [
  { to: "/home", title: "Página inicial", icon: FaHome },
  { to: "/perfil", title: "Perfil", icon: FaUser },
  { to: "/notificacoes", title: "Notificações", icon: FaBell },
  { to: "/filmes/edicao/1", title: "Editar filmes", icon: FaPen },
  { to: "/filmes/cadastro", title: "Cadastrar novo filme", icon: FaPlus }
];

const NavBar = () => {
  return (
    <aside className="sidebar">

      <div className="logo logo-expanded">
        <Link to="/home" className="logo-link">
          <img src={logo} alt="RebsFlix Logo" className="logo-img" />
          <img src={logoText} alt="REBSFLIX" className="logo-text" /> 
        </Link>
      </div>

      <nav className="menu">
        {menuItems.map((item, index) => (
          <Link key={index} to={item.to} title={item.title}>
            <item.icon className="menu-icon" /> 
            <span className="menu-text">{item.title}</span> 
          </Link>
        ))}
      </nav>
    </aside>
  );
};

export default NavBar;