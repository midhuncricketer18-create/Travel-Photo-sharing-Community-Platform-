import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Register() {
  const { register } = useAuth(); const navigate = useNavigate(); const [form, setForm] = useState({ email: '', password: '', role: 'CUSTOMER' }); const [error, setError] = useState(''); const [busy, setBusy] = useState(false)
  async function submit(event) { event.preventDefault(); setBusy(true); setError(''); try { const user = await register(form); navigate(user.role === 'PHOTOGRAPHER' ? '/studio' : '/browse') } catch (err) { setError(err.userMessage || 'Unable to create your account.') } finally { setBusy(false) } }
  return <main className="page-shell"><div className="form-panel"><p className="eyebrow">Begin a collection</p><h2>Create your account.</h2>{error && <div className="alert">{error}</div>}<form onSubmit={submit}><label>Email<input type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></label><label>Password<input type="password" minLength="8" required value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /></label><label>Account type<select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}><option value="CUSTOMER">Customer</option><option value="PHOTOGRAPHER">Photographer</option></select></label><button className="button" disabled={busy}>{busy ? 'Creating...' : 'Create account'}</button></form><p className="meta">Already a member? <Link to="/login">Sign in</Link></p></div></main>
}
