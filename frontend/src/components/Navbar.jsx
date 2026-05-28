import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useCart } from '../context/CartContext'
import Cart from './Cart'

export default function Navbar() {
  const { user, logout } = useAuth()
  const { cartCount } = useCart()
  const [cartOpen, setCartOpen] = useState(false)
  const navigate = useNavigate()

  return (
    <>
      <nav className="bg-green-600 text-white shadow-lg sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link to="/" className="text-2xl font-bold flex items-center gap-2">
            🛒 FreshMart
          </Link>
          <div className="flex items-center gap-3">
            {user ? (
              <>
                <span className="text-sm hidden sm:block">Hi, {user.name.split(' ')[0]}</span>
                <Link to="/orders" className="text-sm hover:underline hidden sm:block">My Orders</Link>
                <button onClick={logout} className="text-sm hover:underline">Logout</button>
              </>
            ) : (
              <>
                <Link to="/login" className="text-sm hover:underline">Login</Link>
                <Link to="/register" className="bg-white text-green-600 text-sm font-semibold px-3 py-1.5 rounded-full hover:bg-green-50 transition">
                  Sign Up
                </Link>
              </>
            )}
            <button
              onClick={() => setCartOpen(true)}
              className="relative bg-green-700 hover:bg-green-800 p-2 rounded-full transition"
            >
              🛍️
              {cartCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold">
                  {cartCount}
                </span>
              )}
            </button>
          </div>
        </div>
      </nav>
      <Cart isOpen={cartOpen} onClose={() => setCartOpen(false)} />
    </>
  )
}
