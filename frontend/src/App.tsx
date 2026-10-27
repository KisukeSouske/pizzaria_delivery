import { Navigate, Route, Routes } from 'react-router-dom'

import { Header } from './components/Header'
import { RotaProtegida } from './components/RotaProtegida'
import { CartProvider } from './contexts/CartContext'
import { LoginPage } from './pages/LoginPage'
import { MenuPage } from './pages/MenuPage'
import { OrdersPage } from './pages/OrdersPage'
import estilos from './App.module.css'

export default function App() {
  return (
    <CartProvider>
      <Header />
      <main className={estilos.conteudo}>
        <Routes>
          <Route path="/" element={<MenuPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route element={<RotaProtegida />}>
            <Route path="/pedidos" element={<OrdersPage />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </CartProvider>
  )
}
