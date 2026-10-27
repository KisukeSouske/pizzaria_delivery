import type { StatusPedido } from '../types'
import { rotuloStatus } from '../utils/format'
import estilos from './StatusBadge.module.css'

const variantes: Record<StatusPedido, string> = {
  AGUARDANDO_PGTO: estilos.aguardando,
  FINALIZADO: estilos.finalizado,
  CANCELADO: estilos.cancelado,
}

export function StatusBadge({ status }: { status: StatusPedido }) {
  return <span className={`${estilos.selo} ${variantes[status]}`}>{rotuloStatus(status)}</span>
}
