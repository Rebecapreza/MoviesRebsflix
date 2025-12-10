import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import "./Notifications.css";
import {
  FaCheckCircle,
  FaTimesCircle,
  FaInfoCircle,
  FaClock,
  FaCheck,
  FaTrash,
} from "react-icons/fa";

const Notifications = () => {
  const [notificacoes, setNotificacoes] = useState([]);
  const [loading, setLoading] = useState(true);
  const isAdmin = localStorage.getItem("tipo") === "admin";

  // Busca notificações
  useEffect(() => {
    const fetchNotificacoes = async () => {
      if (!isAdmin) {
        setLoading(false);
        return;
      }

      try {
        const token = localStorage.getItem("token");
        const response = await fetch("/filmespendentes", {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (response.ok) {
          const data = await response.json();
          const formatado = data.map((filme) => ({
            id: filme.id_filme,
            titulo: filme.titulo,
            tipo: "pendente",
            mensagem: `O filme "${filme.titulo}" (${filme.ano}) aguarda aprovação.`,
            timestamp: "Pendente",
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

  // Função Aprovar
  const handleAprovar = async (id) => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch("/aprovarfilme", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ id_filme: id }),
      });

      if (response.ok) {
        alert("Filme aprovado com sucesso!");
        setNotificacoes((prev) => prev.filter((n) => n.id !== id)); // Remove da lista
      } else {
        alert("Erro ao aprovar.");
      }
    } catch (error) {
      console.error(error);
    }
  };

  // Função Recusar (Deletar)
  const handleRecusar = async (id) => {
    if (!window.confirm("Tem certeza que deseja recusar (excluir) este filme?"))
      return;

    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`/filmes/edicao/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        alert("Filme recusado e removido.");
        setNotificacoes((prev) => prev.filter((n) => n.id !== id)); // Remove da lista
      } else {
        alert("Erro ao recusar.");
      }
    } catch (error) {
      console.error(error);
    }
  };

  const getNotificationStyle = (tipo) => {
    switch (tipo) {
      case "pendente":
        return { icon: FaClock, color: "#FFC107" };
      default:
        return { icon: FaInfoCircle, color: "#2196F3" };
    }
  };

  return (
    <div className="notifications-page">
      <h1>Notificações</h1>

      <div className="notification-list-container">
        {loading ? (
          <p>Carregando...</p>
        ) : (
          <>
            {!isAdmin && (
              <div className="notification-item">
                <FaInfoCircle
                  className="notification-icon"
                  style={{ color: "#2196F3" }}
                />
                <div className="notification-content">
                  <p className="notification-message">
                    Bem-vindo ao Rebsflix! Fique ligado.
                  </p>
                  <span className="notification-timestamp">Agora</span>
                </div>
              </div>
            )}

            {notificacoes.length > 0
              ? notificacoes.map((notif) => {
                  const { icon: Icon, color } = getNotificationStyle(
                    notif.tipo
                  );
                  return (
                    <div key={notif.id} className="notification-item">
                      <Icon
                        className="notification-icon"
                        style={{ color: color }}
                      />

                      <div className="notification-content">
                        <p className="notification-message">{notif.mensagem}</p>
                        <span className="notification-timestamp">
                          {notif.timestamp}
                        </span>

                        {/* Link Detalhes */}
                        <Link
                          to={`/filme/${notif.id}`}
                          className="details-link"
                        >
                          Ver detalhes
                        </Link>

                        {/* Botões de Ação (Apenas para Admin em itens pendentes) */}
                        {isAdmin && notif.tipo === "pendente" && (
                          <div className="notification-actions">
                            <button
                              className="btn-action btn-approve"
                              onClick={() => handleAprovar(notif.id)}
                            >
                              <FaCheck /> Aprovar
                            </button>
                            <button
                              className="btn-action btn-reject"
                              onClick={() => handleRecusar(notif.id)}
                            >
                              <FaTrash /> Recusar
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })
              : isAdmin && (
                  <p className="no-notifications">Nenhuma pendência.</p>
                )}
          </>
        )}
      </div>
    </div>
  );
};

export default Notifications;
