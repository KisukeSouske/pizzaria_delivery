import { Link } from 'react-router-dom'

import { useAuth } from '../hooks/useAuth'
import { useCart } from '../hooks/useCart'
import type { Pizza } from '../types'
import { formatarPreco } from '../utils/format'
import { Aviso } from './Aviso'
import { CartItem } from './CartItem'
import { StatusBadge } from './StatusBadge'
import estilos from './Cart.module.css'

interface Props {
  pizzas: Pizza[]
}

export function Cart({ pizzas }: Props) {
  const { autenticado } = useAuth()
  const { carrinho, carregando, erro, ultimoPedido, alterarQuantidade, remover, finalizar } =
    useCart()

  // Os itens guardam o nome da pizza, não o id; o cardápio faz a ponte de volta.
  const idPorNome = new Map(pizzas.map((pizza) => [pizza.nome, pizza.id]))

  // Diminuir a quantidade recria o item com outro id; ordenar pelo nome evita
  // que a lista salte de posição a cada clique.
  const itens = [...(carrinho?.itens ?? [])].sort((a, b) =>
    (a.pizza ?? '').localeCompare(b.pizza ?? '', 'pt-BR'),
  )

  return (
    <aside className={estilos.painel} aria-label="Seu carrinho">
      <h2 className={estilos.titulo}>Seu carrinho</h2>

      {!autenticado ? (
        <Aviso>
          <Link to="/login" className={estilos.link}>
            Entre na sua conta
          </Link>{' '}
          para montar um pedido.
        </Aviso>
      ) : (
        <>
          {erro && <Aviso tipo="erro">{erro}</Aviso>}

          {itens.length === 0 ? (
            <Aviso>Seu carrinho está vazio. Escolha um sabor no cardápio.</Aviso>
          ) : (
            <ul className={estilos.itens}>
              {itens.map((item) => (
                <CartItem
                  key={item.id}
                  item={item}
                  desabilitado={carregando}
                  onRemover={() => void remover(item)}
                  onAlterar={(delta) => {
                    const idPizza = item.pizza ? idPorNome.get(item.pizza) : undefined
                    if (idPizza !== undefined) void alterarQuantidade(item, idPizza, delta)
                  }}
                />
              ))}
            </ul>
          )}

          {itens.length > 0 && (
            <>
              <p className={estilos.total}>Total: {formatarPreco(carrinho?.preco_total ?? 0)}</p>
              <button
                type="button"
                className={estilos.finalizar}
                onClick={() => void finalizar()}
                disabled={carregando}
              >
                {carregando ? 'Processando…' : 'Finalizar pedido'}
              </button>
            </>
          )}

          {ultimoPedido && (
            <div className={estilos.confirmacao}>
              <StatusBadge status={ultimoPedido.status} />
              <Link to="/pedidos" className={estilos.link}>
                Ver o pedido nº {ultimoPedido.id}
              </Link>
            </div>
          )}
        </>
      )}
    </aside>
  )
}
