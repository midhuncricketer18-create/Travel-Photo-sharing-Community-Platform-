import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import Home from './pages/Home'
import Browse from './pages/Browse'
import PhotoDetails from './pages/PhotoDetails'
import Login from './pages/Login'
import Register from './pages/Register'
import Cart from './pages/Cart'
import Orders from './pages/Orders'
import CustomerDashboard from './pages/CustomerDashboard'
import Checkout from './pages/Checkout'
import OrderDetails from './pages/OrderDetails'
import Studio from './pages/Studio'
import Admin from './pages/Admin'

export default function App() {
  return <BrowserRouter><Layout><Routes>
    <Route path="/" element={<Home />} /><Route path="/browse" element={<Browse />} /><Route path="/photos/:photoId" element={<PhotoDetails />} />
    <Route path="/login" element={<Login />} /><Route path="/register" element={<Register />} />
    <Route element={<ProtectedRoute roles={['CUSTOMER']} />}><Route path="/dashboard" element={<CustomerDashboard />} /><Route path="/cart" element={<Cart />} /><Route path="/checkout" element={<Checkout />} /><Route path="/orders" element={<Orders />} /><Route path="/orders/:orderId" element={<OrderDetails />} /></Route>
    <Route element={<ProtectedRoute roles={['PHOTOGRAPHER']} />}><Route path="/studio" element={<Studio />} /></Route>
    <Route element={<ProtectedRoute roles={['ADMINISTRATOR']} />}><Route path="/admin" element={<Admin />} /></Route>
    <Route path="*" element={<Home />} />
  </Routes></Layout></BrowserRouter>
}
