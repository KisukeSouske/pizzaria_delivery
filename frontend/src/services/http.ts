import { lerSessao, limparSessao } from '../utils/storage'

const BASE_URL = '/api'

/** Disparado quando a API recusa o token; o AuthContext ouve e encerra a sessão. */
export const EVENTO_SESSAO_EXPIRADA = 'pizzaria:sessao-expirada'

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

type Detalhe = string | { msg?: string }[] | undefined

/** A API devolve `detail` como texto ou, em erros de validação, como lista. */
function extrairMensagem(detail: Detalhe, status: number): string {
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    const mensagens = detail.map((erro) => erro.msg).filter(Boolean)
    if (mensagens.length) return mensagens.join(', ')
  }
  return `Erro ${status} ao falar com o servidor.`
}

interface Opcoes {
  method?: string
  body?: unknown
}

export async function request<T>(caminho: string, opcoes: Opcoes = {}): Promise<T> {
  const headers: Record<string, string> = {}
  if (opcoes.body !== undefined) headers['Content-Type'] = 'application/json'

  const sessao = lerSessao()
  if (sessao) headers.Authorization = `Bearer ${sessao.token}`

  let resposta: Response
  try {
    resposta = await fetch(`${BASE_URL}${caminho}`, {
      method: opcoes.method ?? 'GET',
      headers,
      body: opcoes.body === undefined ? undefined : JSON.stringify(opcoes.body),
    })
  } catch {
    throw new ApiError(0, 'Não foi possível falar com o servidor. Ele está rodando?')
  }

  if (resposta.status === 401 && sessao) {
    limparSessao()
    window.dispatchEvent(new Event(EVENTO_SESSAO_EXPIRADA))
  }

  if (!resposta.ok) {
    const corpo = await resposta.json().catch(() => null)
    throw new ApiError(resposta.status, extrairMensagem(corpo?.detail, resposta.status))
  }

  if (resposta.status === 204) return undefined as T
  return (await resposta.json()) as T
}
