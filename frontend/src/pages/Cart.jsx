import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { cartService, orderService } from '../services/services'

export default function Cart() {
  const [cart, setCart] = useState(null); const [error, setError] = useState(''); const [message, setMessage] = useState(''); const [busy, setBusy] = useState(false)
  function load() { cartService.get().then(({ data }) => setCart(data)).catch((err) => setError(err.userMessage || 'Could not load your cart.')) }
  useEffect(load, [])
  async function update(item, quantity) { try { await cartService.update(item.id, { quantity: Number(quantity) }); load() } catch (err) { setError(err.userMessage || 'Could not update this item.') } }
  async function remove(item) { try { await cartService.remove(item.id); load() } catch (err) { setError(err.userMessage || 'Could not remove this item.') } }
  async function checkout() { setBusy(true); setError(''); try { await orderService.create(); setMessage('Order placed. Your prints are on their way to the studio queue.'); load() } catch (err) { setError(err.userMessage || 'Checkout could not be completed.') } finally { setBusy(false) } }
  return <main className="page-shell"><p className="eyebrow">Your selections</p><h2>Cart.</h2>{message && <div className="alert" style={{ background: '#dbe5d9', color: '#294c32' }}>{message}</div>}{error && <div className="alert">{error}</div>}{!cart ? <p className="status">Loading cart...</p> : !cart.items.length ? <p className="status">Your cart is empty. <Link to="/browse">Browse the collection.</Link></p> : <><div className="table-wrap"><table><thead><tr><th>Print</th><th>Format</th><th>Quantity</th><th>Subtotal</th><th></th></tr></thead><tbody>{cart.items.map((item) => <tr key={item.id}><td>{item.product.name}</td><td>{item.product.size} · {item.product.material}</td><td><input style={{ width: 80 }} type="number" min="1" max={item.product.stock} value={item.quantity} onChange={(e) => update(item, e.target.value)} /></td><td>${item.subtotal}</td><td><button className="link-button" onClick={() => remove(item)}>Remove</button></td></tr>)}</tbody></table></div><div style={{ textAlign: 'right', marginTop: 28 }}><strong>Total ${cart.total_amount}</strong><br /><Link className="button" to="/checkout">Checkout</Link></div></>}</main>
}
