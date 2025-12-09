import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import "./Notifications.css";
import {
  FaCheckCircle,
  FaTimesCircle,
  FaInfoCircle,
  FaClock,
} from "react-icons/fa";

const Notifications = () => {
  const [notificacoes, setNotificacoes] = useState([]);
  const [loading, setLoading] = useState(true);
  const isAdmin = localStorage.getItem("tipo") === "admin";

  useEffect(() => {
    const fetchNotificacoes = async () => {
      if (!isAdmin) {
        setLoading(false);
        return;
      }

      try {
        const token = localStorage.getItem("token");
        const response = await fetch("/filmespendentes", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          // Transforma os filmes pendentes em formato de notificação
          const formatado = data.map((filme) => ({
            id: filme.id_filme,
            tipo: "pendente",
            mensagem: `O filme "${filme.titulo}" foi submetido e aguarda aprovação.`,
            timestamp: "Aguardando análise",
          }));
          setNotificacoes(formatado);
        }
      } catch (error) {
        console.error("Erro ao buscar notificações:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchNotificacoes();
  }, [isAdmin]);

  return (
    <div className="notifications-page">
      <h1>Notificações</h1>

      {loading ? (
        <p>Carregando...</p>
      ) : (
        <div className="notification-list-container">
          {!isAdmin && (
            <div className="notification-item">
              <FaInfoCircle
                className="notification-icon"
                style={{ color: "#2196F3" }}
              />
              <div className="notification-content">
                <p className="notification-message">
                  Bem-vindo ao Rebsflix! Fique ligado nas novidades.
                </p>
                <span className="notification-timestamp">Agora</span>
              </div>
            </div>
          )}

          {notificacoes.length > 0
            ? notificacoes.map((notif) => (
                <div key={notif.id} className="notification-item">
                  <FaClock
                    className="notification-icon"
                    style={{ color: "#FFC107" }}
                  />
                  <div className="notification-content">
                    <p className="notification-message">{notif.mensagem}</p>
                    <span className="notification-timestamp">
                      {notif.timestamp}
                    </span>
                    {/* Link rápido para ir ao filme aprovar */}
                    <Link
                      to={`/filme/${notif.id}`}
                      style={{
                        display: "block",
                        marginTop: "5px",
                        color: "#DE467C",
                        fontSize: "0.9rem",
                      }}
                    >
                      Ver Detalhes para Aprovar
                    </Link>
                  </div>
                </div>
              ))
            : isAdmin && (
                <p className="no-notifications">
                  Nenhum filme pendente de aprovação.
                </p>
              )}
        </div>
      )}
    </div>
  );
};

export default Notifications;
