import { Navigate, Outlet, useLocation } from 'react-router-dom'

import { useAuth } from '../hooks/useAuth'

/** Manda para o login quem não tem sessão e guarda a página pedida. */
export function RotaProtegida() {
  const { autenticado } = useAuth()
  const localizacao = useLocation()

  if (!autenticado) {
    return <Navigate to="/login" replace state={{ de: localizacao.pathname }} />
  }
  return <Outlet />
}
