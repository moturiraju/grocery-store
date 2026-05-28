import { useCart } from '../context/CartContext'

export default function ProductCard({ product }) {
  const { addToCart } = useCart()

  return (
    <div className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow overflow-hidden border border-gray-100 flex flex-col">
      <div className="h-44 overflow-hidden bg-gray-100">
        <img
          src={product.image_url}
          alt={product.name}
          className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
          onError={(e) => { e.target.src = `https://placehold.co/400x300?text=${encodeURIComponent(product.name)}` }}
        />
      </div>
      <div className="p-3 flex flex-col flex-1">
        <div className="flex justify-between items-start mb-1 gap-1">
          <h3 className="font-semibold text-gray-800 text-sm leading-tight">{product.name}</h3>
          <span className="text-green-600 font-bold text-sm shrink-0">\${product.price.toFixed(2)}</span>
        </div>
        <p className="text-gray-400 text-xs mb-3 line-clamp-2 flex-1">{product.description}</p>
        <div className="flex items-center justify-between mt-auto">
          <span className={`text-xs ${product.stock > 0 ? 'text-green-500' : 'text-red-400'}`}>
            {product.stock > 0 ? `${product.stock} left` : 'Out of stock'}
          </span>
          <button
            onClick={() => addToCart(product.id)}
            disabled={product.stock === 0}
            className="bg-green-500 hover:bg-green-600 disabled:bg-gray-200 disabled:text-gray-400 text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition"
          >
            + Add
          </button>
        </div>
      </div>
    </div>
  )
}
