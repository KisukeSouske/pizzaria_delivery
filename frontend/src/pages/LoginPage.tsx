import { useState, type FormEvent } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

import { Aviso } from '../components/Aviso'
import { useAuth } from '../hooks/useAuth'
import { ApiError } from '../services/http'
import estilos from './LoginPage.module.css'

type Modo = 'entrar' | 'cadastrar'

export function LoginPage() {
  const [modo, setModo] = useState<Modo>('entrar')
  const [nome, setNome] = useState('')
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [erro, setErro] = useState<string | null>(null)
  const [enviando, setEnviando] = useState(false)

  const { entrar, cadastrar } = useAuth()
  const navegar = useNavigate()
  const localizacao = useLocation()
  const destino = (localizacao.state as { de?: string } | null)?.de ?? '/'

  function trocarModo(novo: Modo) {
    setModo(novo)
    setErro(null)
  }

  async function enviar(evento: FormEvent) {
    evento.preventDefault()
    setEnviando(true)
    setErro(null)
    try {
      if (modo === 'entrar') {
        await entrar({ email, senha })
      } else {
        await cadastrar({ nome, email, senha })
      }
      navegar(destino, { replace: true })
    } catch (falha) {
      setErro(falha instanceof ApiError ? falha.message : 'Não foi possível concluir. Tente de novo.')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <section className={estilos.pagina}>
      <div className={estilos.carta}>
        <div className={estilos.abas} role="tablist">
          <button
            type="button"
            role="tab"
            aria-selected={modo === 'entrar'}
            className={modo === 'entrar' ? `${estilos.aba} ${estilos.abaAtiva}` : estilos.aba}
            onClick={() => trocarModo('entrar')}
          >
            Entrar
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={modo === 'cadastrar'}
            className={modo === 'cadastrar' ? `${estilos.aba} ${estilos.abaAtiva}` : estilos.aba}
            onClick={() => trocarModo('cadastrar')}
          >
            Criar conta
          </button>
        </div>

        <form className={estilos.formulario} onSubmit={enviar}>
          {modo === 'cadastrar' && (
            <label className={estilos.campo}>
              Nome
              <input
                type="text"
                value={nome}
                onChange={(evento) => setNome(evento.target.value)}
                required
                autoComplete="name"
              />
            </label>
          )}

          <label className={estilos.campo}>
            E-mail
            <input
              type="email"
              value={email}
              onChange={(evento) => setEmail(evento.target.value)}
              required
              autoComplete="email"
            />
          </label>

          <label className={estilos.campo}>
            Senha
            <input
              type="password"
              value={senha}
              onChange={(evento) => setSenha(evento.target.value)}
              required
              autoComplete={modo === 'entrar' ? 'current-password' : 'new-password'}
            />
          </label>

          {erro && <Aviso tipo="erro">{erro}</Aviso>}

          <button type="submit" className={estilos.enviar} disabled={enviando}>
            {enviando ? 'Enviando…' : modo === 'entrar' ? 'Entrar' : 'Criar conta'}
          </button>
        </form>
      </div>
    </section>
  )
}
