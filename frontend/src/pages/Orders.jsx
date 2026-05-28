import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/axios'

const STATUS_STYLES = {
  confirmed: 'bg-green-100 text-green-700',
  pending: 'bg-yellow-100 text-yellow-700',
  delivered: 'bg-blue-100 text-blue-700',
  cancelled: 'bg-red-100 text-red-700',
}

export default function Orders() {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/orders')
      .then(r => setOrders(r.data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className="flex justify-center py-20">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500" />
    </div>
  )

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">My Orders</h1>

      {orders.length === 0 ? (
        <div className="text-center py-20 text-gray-400">
          <div className="text-6xl mb-4">📦</div>
          <p className="text-xl font-medium mb-2">No orders yet</p>
          <p className="text-sm mb-6">Start shopping to see your orders here</p>
          <Link to="/" className="bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-xl font-semibold transition">
            Browse Products
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {orders.map(order => (
            <div key={order.id} className="bg-white rounded-2xl border shadow-sm overflow-hidden">
              <div className="p-4 bg-gray-50 border-b flex flex-wrap justify-between items-center gap-2">
                <div>
                  <span className="font-bold text-gray-800">Order #{order.id}</span>
                  <span className="text-gray-400 text-sm ml-3">
                    {new Date(order.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })}
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`text-xs font-semibold px-3 py-1 rounded-full capitalize ${STATUS_STYLES[order.status] || 'bg-gray-100 text-gray-600'}`}>
                    {order.status}
                  </span>
                  <span className="font-bold text-green-600">\${order.total.toFixed(2)}</span>
                </div>
              </div>
              <div className="p-4">
                <p className="text-sm text-gray-500 mb-3 flex gap-1 items-start">
                  <span>📍</span>
                  <span>{order.address}</span>
                </p>
                <div className="divide-y">
                  {order.items.map(item => (
                    <div key={item.id} className="flex items-center gap-3 py-2">
                      <img src={item.product.image_url} alt={item.product.name} className="w-12 h-12 object-cover rounded-lg shrink-0"
                        onError={e => { e.target.src = 'https://placehold.co/48' }} />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{item.product.name}</p>
                        <p className="text-xs text-gray-400">Qty {item.quantity} × \${item.price.toFixed(2)}</p>
                      </div>
                      <span className="text-sm font-semibold text-gray-700 shrink-0">
                        \${(item.quantity * item.price).toFixed(2)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
