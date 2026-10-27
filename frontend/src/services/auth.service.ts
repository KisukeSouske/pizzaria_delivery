import type { Credenciais, NovoUsuario } from '../types'
import { request } from './http'

interface RespostaLogin {
  access_token: string
  refresh_token: string
  token_type: string
}

export function login(credenciais: Credenciais) {
  return request<RespostaLogin>('/auth/login', { method: 'POST', body: credenciais })
}

export function criarConta(usuario: NovoUsuario) {
  return request<{ message: string }>('/auth/criar_conta', { method: 'POST', body: usuario })
}
