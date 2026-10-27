import type { Pizza } from '../types'
import { request } from './http'

/** Cardápio público: só as pizzas ativas. */
export function listarPizzas() {
  return request<Pizza[]>('/pizzas/')
}
