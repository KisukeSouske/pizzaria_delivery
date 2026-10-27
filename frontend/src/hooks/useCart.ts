import { useContext } from 'react'

import { CartContext } from '../contexts/CartContext'

export function useCart() {
  const contexto = useContext(CartContext)
  if (!contexto) throw new Error('useCart precisa estar dentro de <CartProvider>.')
  return contexto
}
