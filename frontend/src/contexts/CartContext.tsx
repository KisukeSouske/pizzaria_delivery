import { createContext, useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'

import * as ordersService from '../services/orders.service'
import { ApiError } from '../services/http'
import type { Carrinho, Item, Pedido } from '../types'
import { useAuth } from '../hooks/useAuth'
import { lerIdCarrinho, limparIdCarrinho, salvarIdCarrinho } from '../utils/storage'

interface CartContextValor {
  carrinho: Carrinho | null
  carregando: boolean
  erro: string | null
  ultimoPedido: Pedido | null
  adicionar: (idPizza: number, quantidade?: number) => Promise<void>
  alterarQuantidade: (item: Item, idPizza: number, delta: number) => Promise<void>
  remover: (item: Item) => Promise<void>
  finalizar: () => Promise<Pedido | null>
}

export const CartContext = createContext<CartContextValor | null>(null)

export function CartProvider({ children }: { children: ReactNode }) {
  const { autenticado } = useAuth()
  const [carrinho, setCarrinho] = useState<Carrinho | null>(null)
  const [carregando, setCarregando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)
  const [ultimoPedido, setUltimoPedido] = useState<Pedido | null>(null)

  // Recupera o carrinho salvo ao abrir a página; descarta o id se a API não o aceitar mais.
  useEffect(() => {
    if (!autenticado) {
      setCarrinho(null)
      setUltimoPedido(null)
      return
    }
    const id = lerIdCarrinho()
    if (id === null) return

    let ativo = true
    ordersService
      .verCarrinho(id)
      .then((recuperado) => {
        if (ativo) setCarrinho(recuperado)
      })
      .catch(() => {
        limparIdCarrinho()
      })
    return () => {
      ativo = false
    }
  }, [autenticado])

  /** Garante um carrinho aberto: reaproveita o salvo ou cria um novo na API. */
  const garantirCarrinho = useCallback(async (): Promise<number> => {
    if (carrinho) return carrinho.id
    const { id } = await ordersService.criarCarrinho()
    salvarIdCarrinho(id)
    return id
  }, [carrinho])

  /** Envolve as operações do carrinho com estado de carregamento e mensagem de erro. */
  const executar = useCallback(async <T,>(operacao: () => Promise<T>): Promise<T | null> => {
    setCarregando(true)
    setErro(null)
    try {
      return await operacao()
    } catch (falha) {
      setErro(falha instanceof ApiError ? falha.message : 'Algo deu errado. Tente de novo.')
      return null
    } finally {
      setCarregando(false)
    }
  }, [])

  const adicionar = useCallback(
    async (idPizza: number, quantidade = 1) => {
      await executar(async () => {
        const idCarrinho = await garantirCarrinho()
        setCarrinho(await ordersService.adicionarItem(idCarrinho, idPizza, quantidade))
        setUltimoPedido(null)
      })
    },
    [executar, garantirCarrinho],
  )

  const remover = useCallback(
    async (item: Item) => {
      await executar(async () => {
        const idCarrinho = await garantirCarrinho()
        setCarrinho(await ordersService.removerItem(idCarrinho, item.id))
      })
    },
    [executar, garantirCarrinho],
  )

  /**
   * A API só sabe somar itens e apagá-los. Para diminuir a quantidade removemos
   * o item e o recriamos com o valor novo.
   */
  const alterarQuantidade = useCallback(
    async (item: Item, idPizza: number, delta: number) => {
      const nova = item.quantidade + delta
      await executar(async () => {
        const idCarrinho = await garantirCarrinho()
        if (delta > 0) {
          setCarrinho(await ordersService.adicionarItem(idCarrinho, idPizza, delta))
          return
        }
        const semItem = await ordersService.removerItem(idCarrinho, item.id)
        setCarrinho(
          nova > 0 ? await ordersService.adicionarItem(idCarrinho, idPizza, nova) : semItem,
        )
      })
    },
    [executar, garantirCarrinho],
  )

  /** O checkout consome o carrinho: a API o apaga e devolve o pedido criado. */
  const finalizar = useCallback(async () => {
    const pedido = await executar(async () => {
      const idCarrinho = await garantirCarrinho()
      return ordersService.finalizarPedido(idCarrinho)
    })
    if (pedido) {
      limparIdCarrinho()
      setCarrinho(null)
      setUltimoPedido(pedido)
    }
    return pedido
  }, [executar, garantirCarrinho])

  const valor = useMemo<CartContextValor>(
    () => ({
      carrinho,
      carregando,
      erro,
      ultimoPedido,
      adicionar,
      alterarQuantidade,
      remover,
      finalizar,
    }),
    [carrinho, carregando, erro, ultimoPedido, adicionar, alterarQuantidade, remover, finalizar],
  )

  return <CartContext.Provider value={valor}>{children}</CartContext.Provider>
}
