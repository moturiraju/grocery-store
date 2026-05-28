import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCart } from '../context/CartContext'
import api from '../api/axios'
import toast from 'react-hot-toast'

export default function Checkout() {
  const { cartItems, cartTotal, clearCart } = useCart()
  const [address, setAddress] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleOrder = async (e) => {
    e.preventDefault()
    if (!address.trim()) { toast.error('Please enter a delivery address'); return }
    setLoading(true)
    try {
      await api.post('/orders', { address })
      clearCart()
      toast.success('Order placed successfully! 🎉')
      navigate('/orders')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to place order')
    } finally {
      setLoading(false)
    }
  }

  if (cartItems.length === 0) {
    return (
      <div className="max-w-lg mx-auto px-4 py-20 text-center">
        <div className="text-6xl mb-4">🛒</div>
        <h2 className="text-xl font-bold text-gray-700 mb-2">Your cart is empty</h2>
        <button onClick={() => navigate('/')} className="mt-4 bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-xl font-semibold transition">
          Browse Products
        </button>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Checkout</h1>
      <div className="grid md:grid-cols-2 gap-8">

        {/* Order Summary */}
        <div>
          <h2 className="text-lg font-semibold text-gray-700 mb-4">Order Summary</h2>
          <div className="space-y-3">
            {cartItems.map(item => (
              <div key={item.id} className="flex items-center gap-3 bg-white p-3 rounded-xl border">
                <img src={item.product.image_url} alt={item.product.name} className="w-14 h-14 object-cover rounded-lg"
                  onError={e => { e.target.src = 'https://placehold.co/56' }} />
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm truncate">{item.product.name}</p>
                  <p className="text-gray-400 text-xs">Qty: {item.quantity} × \${item.product.price.toFixed(2)}</p>
                </div>
                <span className="font-bold text-green-600 text-sm shrink-0">
                  \${(item.product.price * item.quantity).toFixed(2)}
                </span>
              </div>
            ))}
          </div>
          <div className="mt-4 p-4 bg-green-50 border border-green-100 rounded-xl">
            <div className="flex justify-between font-bold text-lg">
              <span>Total</span>
              <span className="text-green-600">\${cartTotal.toFixed(2)}</span>
            </div>
          </div>
        </div>

        {/* Delivery Details */}
        <div>
          <h2 className="text-lg font-semibold text-gray-700 mb-4">Delivery Details</h2>
          <form onSubmit={handleOrder} className="bg-white rounded-xl border p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Delivery Address</label>
              <textarea
                placeholder="Enter your full delivery address including apartment, city, state and zip code..."
                value={address}
                onChange={e => setAddress(e.target.value)}
                required
                rows={5}
                className="w-full border border-gray-300 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-green-400 resize-none"
              />
            </div>
            <button type="submit" disabled={loading}
              className="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-3 rounded-xl transition disabled:opacity-60 text-lg">
              {loading ? 'Placing Order...' : `Place Order • \$${cartTotal.toFixed(2)}`}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
