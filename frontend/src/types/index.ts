// Espelha os schemas Pydantic da API (app/schemas).

export type StatusPedido = 'AGUARDANDO_PGTO' | 'FINALIZADO' | 'CANCELADO'

export interface Pizza {
  id: number
  nome: string
  preco: number
  ativo: boolean
}

export interface Item {
  id: number
  pizza: string | null
  quantidade: number
  preco_unitario: number
  preco: number
}

export interface Carrinho {
  id: number
  preco_total: number
  itens: Item[]
}

export interface Pedido {
  id: number
  status: StatusPedido
  preco_total: number
  itens: Item[]
}

export interface PedidoResumo {
  id: number
  status: StatusPedido
  preco_total: number
}

export interface Credenciais {
  email: string
  senha: string
}

export interface NovoUsuario extends Credenciais {
  nome: string
}

export interface Usuario {
  nome: string
  email: string
}
