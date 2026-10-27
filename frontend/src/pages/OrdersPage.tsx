import { useCallback, useEffect, useState } from 'react'

import { Aviso } from '../components/Aviso'
import { OrderCard } from '../components/OrderCard'
import { ApiError } from '../services/http'
import { listarPedidos } from '../services/orders.service'
import type { PedidoResumo } from '../types'
import estilos from './OrdersPage.module.css'

export function OrdersPage() {
  const [pedidos, setPedidos] = useState<PedidoResumo[]>([])
  const [carregando, setCarregando] = useState(true)
  const [erro, setErro] = useState<string | null>(null)

  const carregar = useCallback(async () => {
    setCarregando(true)
    setErro(null)
    try {
      setPedidos(await listarPedidos())
    } catch (falha) {
      setErro(falha instanceof ApiError ? falha.message : 'Não foi possível carregar os pedidos.')
    } finally {
      setCarregando(false)
    }
  }, [])

  useEffect(() => {
    void carregar()
  }, [carregar])

  return (
    <section className={estilos.pagina}>
      <h1 className={estilos.titulo}>Meus pedidos</h1>

      {erro && <Aviso tipo="erro">{erro}</Aviso>}
      {carregando && <Aviso>Carregando os pedidos…</Aviso>}
      {!carregando && !erro && pedidos.length === 0 && (
        <Aviso>Você ainda não fez nenhum pedido.</Aviso>
      )}

      <ul className={estilos.lista}>
        {pedidos.map((pedido) => (
          <OrderCard key={pedido.id} pedido={pedido} onAtualizar={carregar} />
        ))}
      </ul>
    </section>
  )
}
