import { createContext, useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'

import * as authService from '../services/auth.service'
import { EVENTO_SESSAO_EXPIRADA } from '../services/http'
import type { Credenciais, NovoUsuario, Usuario } from '../types'
import { lerSessao, limparIdCarrinho, limparSessao, salvarSessao } from '../utils/storage'

interface AuthContextValor {
  usuario: Usuario | null
  autenticado: boolean
  entrar: (credenciais: Credenciais) => Promise<void>
  cadastrar: (novoUsuario: NovoUsuario) => Promise<void>
  sair: () => void
}

export const AuthContext = createContext<AuthContextValor | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<Usuario | null>(() => lerSessao()?.usuario ?? null)

  const sair = useCallback(() => {
    limparSessao()
    limparIdCarrinho()
    setUsuario(null)
  }, [])

  // A API devolve 401 quando o token expira; o http dispara o evento e saímos da sessão.
  useEffect(() => {
    const aoExpirar = () => setUsuario(null)
    window.addEventListener(EVENTO_SESSAO_EXPIRADA, aoExpirar)
    return () => window.removeEventListener(EVENTO_SESSAO_EXPIRADA, aoExpirar)
  }, [])

  const entrar = useCallback(async (credenciais: Credenciais) => {
    const { access_token } = await authService.login(credenciais)
    // A API não expõe uma rota de perfil, então guardamos o que o formulário já sabe.
    const novoUsuario: Usuario = { nome: credenciais.email.split('@')[0], email: credenciais.email }
    limparIdCarrinho()
    salvarSessao({ token: access_token, usuario: novoUsuario })
    setUsuario(novoUsuario)
  }, [])

  const cadastrar = useCallback(
    async (novoUsuario: NovoUsuario) => {
      await authService.criarConta(novoUsuario)
      await entrar({ email: novoUsuario.email, senha: novoUsuario.senha })
    },
    [entrar],
  )

  const valor = useMemo<AuthContextValor>(
    () => ({ usuario, autenticado: usuario !== null, entrar, cadastrar, sair }),
    [usuario, entrar, cadastrar, sair],
  )

  return <AuthContext.Provider value={valor}>{children}</AuthContext.Provider>
}
