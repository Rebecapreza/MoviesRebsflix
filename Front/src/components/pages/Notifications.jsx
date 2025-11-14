// src/components/pages/Notifications.jsx
import React from 'react';
import './Notifications.css'; // Importe o CSS
import { FaCheckCircle, FaTimesCircle, FaInfoCircle } from 'react-icons/fa';

// Dados Fictícios para Notificações
const DUMMY_NOTIFICATIONS = [
    { 
        id: 1, 
        tipo: 'aprovacao', 
        mensagem: 'O seu filme "Midnight Sun" foi aprovado e agora está disponível no catálogo!', 
        timestamp: '2 horas atrás' 
    },
    { 
        id: 2, 
        tipo: 'rejeicao', 
        mensagem: 'Seu filme "A Jornada" foi rejeitado. Verifique os requisitos de poster.', 
        timestamp: '1 dia atrás' 
    },
    { 
        id: 3, 
        tipo: 'geral', 
        mensagem: 'Novas regras de submissão foram publicadas. Leia para evitar rejeições.', 
        timestamp: '3 dias atrás' 
    },
];

// Mapeamento de ícones e cores
const getNotificationIcon = (tipo) => {
    switch (tipo) {
        case 'aprovacao':
            return { icon: FaCheckCircle, color: '#4CAF50' }; // Verde para sucesso
        case 'rejeicao':
            return { icon: FaTimesCircle, color: '#F44336' }; // Vermelho para erro
        default:
            return { icon: FaInfoCircle, color: '#2196F3' }; // Azul para informação
    }
};

const Notifications = () => {
  return (
    <div className="notifications-page">
      <h1>Notificações</h1>

      <div className="notification-list-container">
        {DUMMY_NOTIFICATIONS.length > 0 ? (
          DUMMY_NOTIFICATIONS.map(notif => {
            const { icon: Icon, color } = getNotificationIcon(notif.tipo);
            return (
              <div key={notif.id} className="notification-item">
                <Icon className="notification-icon" style={{ color: color }} />
                <div className="notification-content">
                  <p className="notification-message">{notif.mensagem}</p>
                  <span className="notification-timestamp">{notif.timestamp}</span>
                </div>
              </div>
            );
          })
        ) : (
          <p className="no-notifications">Nenhuma notificação recente.</p>
        )}
      </div>
    </div>
  );
};

export default Notifications;