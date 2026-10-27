import type { ReactNode } from 'react'

import estilos from './Aviso.module.css'

interface Props {
  tipo?: 'neutro' | 'erro'
  children: ReactNode
}

/** Mensagem curta para os estados de carregando, vazio e erro. */
export function Aviso({ tipo = 'neutro', children }: Props) {
  const classe = tipo === 'erro' ? `${estilos.aviso} ${estilos.erro}` : estilos.aviso
  return (
    <p className={classe} role={tipo === 'erro' ? 'alert' : undefined}>
      {children}
    </p>
  )
}
