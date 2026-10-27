import { useCallback, useEffect, useState } from 'react'

import { ApiError } from '../services/http'
import { listarPizzas } from '../services/pizzas.service'
import type { Pizza } from '../types'

export function usePizzas() {
  const [pizzas, setPizzas] = useState<Pizza[]>([])
  const [carregando, setCarregando] = useState(true)
  const [erro, setErro] = useState<string | null>(null)

  const carregar = useCallback(async () => {
    setCarregando(true)
    setErro(null)
    try {
      setPizzas(await listarPizzas())
    } catch (falha) {
      setErro(falha instanceof ApiError ? falha.message : 'Não foi possível carregar o cardápio.')
    } finally {
      setCarregando(false)
    }
  }, [])

  useEffect(() => {
    void carregar()
  }, [carregar])

  return { pizzas, carregando, erro, recarregar: carregar }
}
