import type { Carrinho, Pedido, PedidoResumo } from '../types'
import { request } from './http'

export function criarCarrinho() {
  return request<{ mensagem: string; id: number }>('/orders/carrinho', { method: 'POST' })
}

export function verCarrinho(idCarrinho: number) {
  return request<Carrinho>(`/orders/carrinho/${idCarrinho}`)
}

/** Soma `quantidade` ao item; se a pizza ainda não está no carrinho, cria o item. */
export function adicionarItem(idCarrinho: number, idPizza: number, quantidade: number) {
  return request<Carrinho>(`/orders/carrinho/${idCarrinho}/itens`, {
    method: 'POST',
    body: { id_pizza: idPizza, quantidade },
  })
}

export function removerItem(idCarrinho: number, idItem: number) {
  return request<Carrinho>(`/orders/carrinho/${idCarrinho}/itens/${idItem}`, { method: 'DELETE' })
}

export function finalizarPedido(idCarrinho: number) {
  return request<Pedido>('/orders/pedido', { method: 'POST', body: { carrinho: idCarrinho } })
}

export function listarPedidos() {
  return request<PedidoResumo[]>('/orders/')
}

export function verPedido(idPedido: number) {
  return request<Pedido>(`/orders/pedido/${idPedido}`)
}

export function cancelarPedido(idPedido: number) {
  return request<{ mensagem: string }>(`/orders/pedido/cancelar/${idPedido}`, { method: 'POST' })
}
