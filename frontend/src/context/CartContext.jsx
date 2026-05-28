import { createContext, useContext, useState, useEffect } from 'react'
import api from '../api/axios'
import toast from 'react-hot-toast'
import { useAuth } from './AuthContext'

const CartContext = createContext(null)

export function CartProvider({ children }) {
  const [cartItems, setCartItems] = useState([])
  const { user } = useAuth()

  useEffect(() => {
    if (user) fetchCart()
    else setCartItems([])
  }, [user])

  const fetchCart = async () => {
    try {
      const res = await api.get('/cart')
      setCartItems(res.data)
    } catch {}
  }

  const addToCart = async (productId, quantity = 1) => {
    if (!user) { toast.error('Please login to add items'); return }
    try {
      await api.post('/cart', { product_id: productId, quantity })
      await fetchCart()
      toast.success('Added to cart!')
    } catch { toast.error('Failed to add to cart') }
  }

  const updateQuantity = async (itemId, quantity) => {
    if (quantity <= 0) { await removeFromCart(itemId); return }
    try {
      await api.put(`/cart/${itemId}`, { quantity })
      await fetchCart()
    } catch { toast.error('Failed to update') }
  }

  const removeFromCart = async (itemId) => {
    try {
      await api.delete(`/cart/${itemId}`)
      await fetchCart()
      toast.success('Item removed')
    } catch { toast.error('Failed to remove') }
  }

  const clearCart = () => setCartItems([])
  const cartTotal = cartItems.reduce((s, i) => s + i.product.price * i.quantity, 0)
  const cartCount = cartItems.reduce((s, i) => s + i.quantity, 0)

  return (
    <CartContext.Provider value={{ cartItems, addToCart, updateQuantity, removeFromCart, clearCart, cartTotal, cartCount, fetchCart }}>
      {children}
    </CartContext.Provider>
  )
}

export const useCart = () => useContext(CartContext)
