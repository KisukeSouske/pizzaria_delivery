import { useState } from 'react'

import { ApiError } from '../services/http'
import { cancelarPedido, verPedido } from '../services/orders.service'
import type { Pedido, PedidoResumo } from '../types'
import { formatarPreco } from '../utils/format'
import { imagemDaPizza } from '../utils/pizzaImage'
import { Aviso } from './Aviso'
import { StatusBadge } from './StatusBadge'
import estilos from './OrderCard.module.css'

interface Props {
  pedido: PedidoResumo
  onAtualizar: () => void
}

export function OrderCard({ pedido, onAtualizar }: Props) {
  const [detalhes, setDetalhes] = useState<Pedido | null>(null)
  const [aberto, setAberto] = useState(false)
  const [ocupado, setOcupado] = useState(false)
  const [erro, setErro] = useState<string | null>(null)

  // Os itens só vêm na rota de detalhe, então são buscados na primeira abertura.
  async function alternarDetalhes() {
    if (aberto) {
      setAberto(false)
      return
    }
    setAberto(true)
    if (detalhes) return

    setOcupado(true)
    setErro(null)
    try {
      setDetalhes(await verPedido(pedido.id))
    } catch (falha) {
      setErro(falha instanceof ApiError ? falha.message : 'Não foi possível abrir o pedido.')
    } finally {
      setOcupado(false)
    }
  }

  async function cancelar() {
    setOcupado(true)
    setErro(null)
    try {
      await cancelarPedido(pedido.id)
      // O status mudou: fecha o detalhe antigo em vez de mostrá-lo desatualizado.
      setDetalhes(null)
      setAberto(false)
      onAtualizar()
    } catch (falha) {
      setErro(falha instanceof ApiError ? falha.message : 'Não foi possível cancelar o pedido.')
    } finally {
      setOcupado(false)
    }
  }

  return (
    <li className={estilos.carta}>
      <div className={estilos.cabecalho}>
        <div>
          <h2 className={estilos.numero}>Pedido nº {pedido.id}</h2>
          <p className={estilos.total}>{formatarPreco(pedido.preco_total)}</p>
        </div>
        <StatusBadge status={pedido.status} />
      </div>

      {erro && <Aviso tipo="erro">{erro}</Aviso>}

      {aberto && detalhes && (
        <ul className={estilos.itens}>
          {detalhes.itens.map((item) => (
            <li key={item.id} className={estilos.item}>
              <img className={estilos.miniatura} src={imagemDaPizza(item.pizza)} alt="" />
              <span>
                {item.quantidade}× {item.pizza ?? 'Pizza'}
              </span>
              <span className={estilos.itemPreco}>{formatarPreco(item.preco)}</span>
            </li>
          ))}
        </ul>
      )}

      <div className={estilos.acoes}>
        <button type="button" className={estilos.secundario} onClick={() => void alternarDetalhes()}>
          {aberto ? 'Ocultar itens' : 'Ver itens'}
        </button>
        {pedido.status === 'AGUARDANDO_PGTO' && (
          <button
            type="button"
            className={estilos.cancelar}
            onClick={() => void cancelar()}
            disabled={ocupado}
          >
            Cancelar pedido
          </button>
        )}
      </div>
    </li>
  )
}
