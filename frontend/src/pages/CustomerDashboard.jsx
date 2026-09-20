import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { cartService, orderService } from '../services/services'

export default function CustomerDashboard() {
  const { user } = useAuth(); const [cart, setCart] = useState(null); const [orders, setOrders] = useState([]); const [error, setError] = useState('')
  useEffect(() => { Promise.all([cartService.get(), orderService.list()]).then(([cartResponse, orderResponse]) => { setCart(cartResponse.data); setOrders(orderResponse.data) }).catch((err) => setError(err.userMessage || 'Could not load your dashboard.')) }, [])
  return <main className="page-shell"><p className="eyebrow">Your account</p><h2>Good to see you, {user.email}.</h2>{error && <div className="alert">{error}</div>}<div className="grid"><article className="photo-card" style={{ minHeight: 180 }}><div className="photo-card-body"><p className="eyebrow">Cart</p><h3>{cart?.items.length ?? '...'}</h3><p className="meta"><Link to="/cart">Review selections</Link></p></div></article><article className="photo-card" style={{ minHeight: 180 }}><div className="photo-card-body"><p className="eyebrow">Orders</p><h3>{orders.length}</h3><p className="meta"><Link to="/orders">View order history</Link></p></div></article></div><Link className="button" to="/browse">Browse photographs</Link></main>
}
