import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Layout({ children }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const roleHome = user?.role === 'PHOTOGRAPHER' ? '/studio' : user?.role === 'ADMINISTRATOR' ? '/admin' : '/orders'
  return <>
    <header className="topbar"><Link className="brand" to="/">STILLROOM<span>.</span></Link><nav>
      <NavLink to="/browse">Browse</NavLink>
      {user?.role === 'CUSTOMER' && <><NavLink to="/dashboard">Dashboard</NavLink><NavLink to="/cart">Cart</NavLink><NavLink to="/orders">Orders</NavLink></>}
      {user?.role === 'PHOTOGRAPHER' && <NavLink to="/studio">Studio</NavLink>}
      {user?.role === 'ADMINISTRATOR' && <NavLink to="/admin">Admin</NavLink>}
      {user ? <button className="link-button" onClick={() => { logout(); navigate('/') }}>Sign out</button> : <NavLink to="/login">Sign in</NavLink>}
    </nav></header>
    {children}
    <footer><span>STILLROOM</span><span>Photographs worth living with.</span></footer>
  </>
}
