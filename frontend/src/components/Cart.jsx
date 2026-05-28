import { useCart } from '../context/CartContext'
import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'

export default function Cart({ isOpen, onClose }) {
  const { cartItems, updateQuantity, removeFromCart, cartTotal } = useCart()
  const { user } = useAuth()
  const navigate = useNavigate()

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <div className="flex-1 bg-black bg-opacity-40" onClick={onClose} />
      <div className="w-full max-w-sm bg-white shadow-2xl flex flex-col">
        <div className="p-4 border-b flex justify-between items-center bg-green-600 text-white">
          <h2 className="text-lg font-bold">Your Cart ({cartItems.length} items)</h2>
          <button onClick={onClose} className="text-2xl leading-none hover:opacity-75">×</button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {cartItems.length === 0 ? (
            <div className="text-center py-16 text-gray-400">
              <div className="text-5xl mb-3">🛒</div>
              <p className="font-medium">Your cart is empty</p>
              <p className="text-sm mt-1">Add some fresh groceries!</p>
            </div>
          ) : (
            cartItems.map(item => (
              <div key={item.id} className="flex items-center gap-3 p-2 bg-gray-50 rounded-lg">
                <img
                  src={item.product.image_url}
                  alt={item.product.name}
                  className="w-14 h-14 object-cover rounded-lg shrink-0"
                  onError={(e) => { e.target.src = 'https://placehold.co/56' }}
                />
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm truncate">{item.product.name}</p>
                  <p className="text-green-600 font-semibold text-sm">\${item.product.price.toFixed(2)}</p>
                </div>
                <div className="flex items-center gap-1 shrink-0">
                  <button onClick={() => updateQuantity(item.id, item.quantity - 1)} className="w-7 h-7 rounded-full bg-gray-200 hover:bg-gray-300 text-sm font-bold flex items-center justify-center">−</button>
                  <span className="w-5 text-center text-sm font-semibold">{item.quantity}</span>
                  <button onClick={() => updateQuantity(item.id, item.quantity + 1)} className="w-7 h-7 rounded-full bg-green-500 hover:bg-green-600 text-white text-sm font-bold flex items-center justify-center">+</button>
                </div>
              </div>
            ))
          )}
        </div>

        {cartItems.length > 0 && (
          <div className="p-4 border-t">
            <div className="flex justify-between font-bold text-lg mb-3">
              <span>Total</span>
              <span className="text-green-600">\${cartTotal.toFixed(2)}</span>
            </div>
            <button
              onClick={() => { onClose(); navigate(user ? '/checkout' : '/login') }}
              className="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-3 rounded-xl transition"
            >
              {user ? 'Proceed to Checkout →' : 'Login to Checkout'}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
