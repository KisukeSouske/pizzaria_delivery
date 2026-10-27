import type { Pizza } from '../types'
import { formatarPreco } from '../utils/format'
import { imagemDaPizza } from '../utils/pizzaImage'
import estilos from './PizzaCard.module.css'

interface Props {
  pizza: Pizza
  onAdicionar: (pizza: Pizza) => void
  desabilitado?: boolean
}

export function PizzaCard({ pizza, onAdicionar, desabilitado = false }: Props) {
  return (
    <article className={estilos.carta}>
      <img
        className={estilos.imagem}
        src={imagemDaPizza(pizza.nome)}
        alt={`Pizza de ${pizza.nome}`}
        loading="lazy"
      />
      <div className={estilos.rodape}>
        <h3 className={estilos.titulo}>
          {pizza.nome} — {formatarPreco(pizza.preco)}
        </h3>
        <button
          type="button"
          className={estilos.botao}
          onClick={() => onAdicionar(pizza)}
          disabled={desabilitado}
        >
          Adicionar
        </button>
      </div>
    </article>
  )
}
