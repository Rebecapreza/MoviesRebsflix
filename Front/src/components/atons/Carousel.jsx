import { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import './Carousel.css';

import PosterAEA from '../../assets/PosteresCarrossel/PosterAindaEstouAqui.png';
import PosterCEEADV from '../../assets/PosteresCarrossel/PosterComoEuEraAntesDeVoce.png';
import PosterC from '../../assets/PosteresCarrossel/PosterCrepusculo.png';
import PosterR from '../../assets/PosteresCarrossel/PosterRio.png';

const SLIDES = [
  { id: 1, poster_url: PosterAEA },
  { id: 2, poster_url: PosterCEEADV },
  { id: 3, poster_url: PosterC },
  { id: 4, poster_url: PosterR },
];

function Carrossel({ onFilmeClick }) {
  const [indiceAtual, setIndiceAtual] = useState(0);

  useEffect(() => {
    const intervalo = setInterval(() => {
      setIndiceAtual((prev) => (prev + 1) % SLIDES.length);
    }, 5000);
    return () => clearInterval(intervalo);
  }, []);

  const anterior = () => setIndiceAtual((prev) => (prev - 1 + SLIDES.length) % SLIDES.length);
  const proximo = () => setIndiceAtual((prev) => (prev + 1) % SLIDES.length);

  const filmeAtual = SLIDES[indiceAtual];

  return (
    <section className="carrossel">
      <div className="carrosselContainer">
        <div className="carrosselImagem" onClick={() => onFilmeClick?.(filmeAtual.id)}>
          <img src={filmeAtual.poster_url} alt={filmeAtual.titulo} />
          <h2 className="carrosselTitulo">{filmeAtual.titulo}</h2>
        </div>

        <button type="button" className="carrosselControle carrosselControleEsquerda" onClick={anterior}>
          <ChevronLeft size={28} />
        </button>
        <button type="button" className="carrosselControle carrosselControleDireita" onClick={proximo}>
          <ChevronRight size={28} />
        </button>

        <div className="carrosselIndicadores">
          {SLIDES.map((_, index) => (
            <button
              key={index}
              type="button"
              className={`carrosselIndicador ${index === indiceAtual ? 'ativo' : ''}`}
              onClick={() => setIndiceAtual(index)}
            />
          ))}
        </div>
      </div>
    </section>
  );
}

export default Carrossel;
