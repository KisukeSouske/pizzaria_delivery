import type { Item } from '../types'
import { formatarPreco } from '../utils/format'
import { imagemDaPizza } from '../utils/pizzaImage'
import estilos from './CartItem.module.css'

interface Props {
  item: Item
  onAlterar: (delta: number) => void
  onRemover: () => void
  desabilitado?: boolean
}

export function CartItem({ item, onAlterar, onRemover, desabilitado = false }: Props) {
  const nome = item.pizza ?? 'Pizza'

  return (
    <li className={estilos.item}>
      <img className={estilos.miniatura} src={imagemDaPizza(item.pizza)} alt="" />

      <div className={estilos.detalhes}>
        <p className={estilos.nome}>{nome}</p>
        <div className={estilos.contador}>
          <button
            type="button"
            onClick={() => (item.quantidade > 1 ? onAlterar(-1) : onRemover())}
            disabled={desabilitado}
            aria-label={item.quantidade > 1 ? `Remover uma ${nome}` : `Tirar ${nome} do carrinho`}
          >
            −
          </button>
          <span aria-live="polite">{item.quantidade}</span>
          <button
            type="button"
            onClick={() => onAlterar(1)}
            disabled={desabilitado}
            aria-label={`Adicionar uma ${nome}`}
          >
            +
          </button>
        </div>
      </div>

      <span className={estilos.preco}>{formatarPreco(item.preco)}</span>
    </li>
  )
}
