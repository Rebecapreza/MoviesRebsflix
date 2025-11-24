// Front/src/components/auth/ProtectedRoute.jsx
import React from 'react';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children, roleRequired }) => {
    const tipoUsuario = localStorage.getItem('tipo');
    const isAuthenticated = !!localStorage.getItem('token');

    // 1. Se não estiver logado, manda pro login
    if (!isAuthenticated) {
        return <Navigate to="/" replace />;
    }

    // 2. Se exigir Admin e o usuário não for Admin, manda pra Home
    if (roleRequired === 'admin' && tipoUsuario !== 'admin') {
        alert("Acesso negado: Apenas administradores podem acessar esta página.");
        return <Navigate to="/home" replace />;
    }

    // Se passou nos testes, renderiza a página
    return children;
};

export default ProtectedRoute;