import { useNavigate } from 'react-router-dom'

import { Aviso } from '../components/Aviso'
import { Cart } from '../components/Cart'
import { PizzaCard } from '../components/PizzaCard'
import { useAuth } from '../hooks/useAuth'
import { useCart } from '../hooks/useCart'
import { usePizzas } from '../hooks/usePizzas'
import type { Pizza } from '../types'
import estilos from './MenuPage.module.css'

export function MenuPage() {
  const { pizzas, carregando, erro } = usePizzas()
  const { autenticado } = useAuth()
  const { adicionar, carregando: salvando } = useCart()
  const navegar = useNavigate()

  function aoAdicionar(pizza: Pizza) {
    if (!autenticado) {
      navegar('/login', { state: { de: '/' } })
      return
    }
    void adicionar(pizza.id)
  }

  return (
    <div className={estilos.pagina}>
      <section>
        <h1 className={estilos.titulo}>Cardápio</h1>

        {erro && <Aviso tipo="erro">{erro}</Aviso>}
        {carregando && <Aviso>Carregando o cardápio…</Aviso>}
        {!carregando && !erro && pizzas.length === 0 && (
          <Aviso>Nenhuma pizza disponível no momento.</Aviso>
        )}

        <div className={estilos.grade}>
          {pizzas.map((pizza) => (
            <PizzaCard
              key={pizza.id}
              pizza={pizza}
              onAdicionar={aoAdicionar}
              desabilitado={salvando}
            />
          ))}
        </div>
      </section>

      <Cart pizzas={pizzas} />
    </div>
  )
}
