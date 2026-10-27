import type { Usuario } from '../types'

const CHAVE_SESSAO = 'pizzaria:sessao'
const CHAVE_CARRINHO = 'pizzaria:carrinho'

export interface Sessao {
  token: string
  usuario: Usuario
}

export function lerSessao(): Sessao | null {
  try {
    const bruto = localStorage.getItem(CHAVE_SESSAO)
    return bruto ? (JSON.parse(bruto) as Sessao) : null
  } catch {
    return null
  }
}

export function salvarSessao(sessao: Sessao) {
  localStorage.setItem(CHAVE_SESSAO, JSON.stringify(sessao))
}

export function limparSessao() {
  localStorage.removeItem(CHAVE_SESSAO)
}

export function lerIdCarrinho(): number | null {
  const bruto = localStorage.getItem(CHAVE_CARRINHO)
  const id = bruto ? Number(bruto) : NaN
  return Number.isInteger(id) ? id : null
}

export function salvarIdCarrinho(id: number) {
  localStorage.setItem(CHAVE_CARRINHO, String(id))
}

export function limparIdCarrinho() {
  localStorage.removeItem(CHAVE_CARRINHO)
}
