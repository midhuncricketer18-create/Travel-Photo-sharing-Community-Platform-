import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const { login } = useAuth(); const navigate = useNavigate(); const location = useLocation(); const [form, setForm] = useState({ email: '', password: '' }); const [error, setError] = useState(''); const [busy, setBusy] = useState(false)
  async function submit(event) { event.preventDefault(); setBusy(true); setError(''); try { const user = await login(form); const target = location.state?.from?.pathname || (user.role === 'PHOTOGRAPHER' ? '/studio' : user.role === 'ADMINISTRATOR' ? '/admin' : '/browse'); navigate(target, { replace: true }) } catch (err) { setError(err.userMessage || 'Unable to sign in.') } finally { setBusy(false) } }
  return <main className="page-shell"><div className="form-panel"><p className="eyebrow">Welcome back</p><h2>Sign in to Stillroom.</h2>{error && <div className="alert">{error}</div>}<form onSubmit={submit}><label>Email<input type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></label><label>Password<input type="password" required value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /></label><button className="button" disabled={busy}>{busy ? 'Signing in...' : 'Sign in'}</button></form><p className="meta">New here? <Link to="/register">Create an account</Link></p></div></main>
}
