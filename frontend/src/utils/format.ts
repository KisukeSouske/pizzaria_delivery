import type { StatusPedido } from '../types'

const moeda = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })

export function formatarPreco(valor: number): string {
  return moeda.format(valor)
}

const rotulos: Record<StatusPedido, string> = {
  AGUARDANDO_PGTO: 'Aguardando pagamento',
  FINALIZADO: 'Finalizado',
  CANCELADO: 'Cancelado',
}

export function rotuloStatus(status: StatusPedido): string {
  return rotulos[status] ?? status
}
