import { NavLink, Link } from 'react-router-dom'

import { useAuth } from '../hooks/useAuth'
import { Logo } from './Logo'
import estilos from './Header.module.css'

const abas = [
  { para: '/', rotulo: 'Cardápio' },
  { para: '/pedidos', rotulo: 'Meus pedidos' },
]

export function Header() {
  const { usuario, autenticado, sair } = useAuth()

  const classeAba = ({ isActive }: { isActive: boolean }) =>
    isActive ? `${estilos.aba} ${estilos.abaAtiva}` : estilos.aba

  return (
    <header className={estilos.cabecalho}>
      <div className={estilos.conteudo}>
        <Link to="/" className={estilos.marca}>
          <Logo />
          <span>Pizzaria</span>
        </Link>

        <nav className={estilos.navegacao}>
          {abas.map((aba) => (
            <NavLink key={aba.para} to={aba.para} end className={classeAba}>
              {aba.rotulo}
            </NavLink>
          ))}
        </nav>

        <div className={estilos.conta}>
          {autenticado && usuario ? (
            <>
              <span className={estilos.avatar} aria-hidden="true">
                {usuario.nome.charAt(0).toUpperCase()}
              </span>
              <span className={estilos.nome}>{usuario.nome}</span>
              <button type="button" className={estilos.botao} onClick={sair}>
                Sair
              </button>
            </>
          ) : (
            <Link to="/login" className={estilos.botao}>
              Entrar
            </Link>
          )}
        </div>
      </div>
    </header>
  )
}
