import React, { useEffect } from "react";
import "../../components/organismo/FilterModal.css";


export default function FiltroModal({ isOpen, onClose, onApply }) {
  // Fecha modal ao pressionar "ESC"
  useEffect(() => {
    const handleEsc = (event) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, [onClose]);

  if (!isOpen) return null;

  const handleSubmit = (event) => {
    event.preventDefault();
    const data = new FormData(event.target);
    const filtros = {
      generos: data.getAll("generos"),
      atores: data.get("atores"),
      diretor: data.get("diretor"),
      ano: data.get("ano"),
    };
    onApply(filtros);
    onClose();
  };

  return (
    <div className="filtro-overlay" role="dialog" aria-modal="true">
      <div className="filtro-modal">
        <button
          className="filtro-fechar"
          onClick={onClose}
          aria-label="Fechar modal"
        >
          ✕
        </button>

        <form onSubmit={handleSubmit} className="filtro-form">
          <h2 className="filtro-titulo">Filtrar por:</h2>

          {/* --- GÊNEROS --- */}
          <div className="filtro-generos">
            {[
              "Romance",
              "Fantasia",
              "Suspense",
              "Aventura",
              "Comédia",
              "Drama",
              "Musical",
              "Terror",
              "Ação",
            ].map((genero) => (
              <label key={genero} className="checkbox-label">
                <input
                  type="checkbox"
                  name="generos"
                  value={genero}
                  className="checkbox-input"
                />
                {genero}
              </label>
            ))}
          </div>

          {/* --- CAMPOS DE BUSCA --- */}
          <div className="filtro-campo">
            <label htmlFor="atores">Pesquise por:</label>
            <input
              type="text"
              id="atores"
              name="atores"
              placeholder="Atores principais..."
            />
          </div>

          <div className="filtro-campo">
            <label htmlFor="diretor">Pesquise por:</label>
            <input
              type="text"
              id="diretor"
              name="diretor"
              placeholder="Nome do diretor..."
            />
          </div>

          <div className="filtro-campo">
            <label htmlFor="ano">Pesquise por:</label>
            <select id="ano" name="ano">
              <option value="">Data de lançamento</option>
              <option value="2025">2025</option>
              <option value="2024">2024</option>
              <option value="2023">2023</option>
              <option value="antigo">Anterior a 2020</option>
            </select>
          </div>

          <div className="filtro-botoes">
            <button type="submit" className="btn-aplicar">
              Aplicar filtros
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
