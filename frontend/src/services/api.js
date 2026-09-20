import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('stillroom_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) localStorage.removeItem('stillroom_token')
    const detail = error.response?.data?.detail
    error.userMessage = Array.isArray(detail) ? detail.map((item) => item.msg).join(', ') : detail || 'Something went wrong.'
    return Promise.reject(error)
  },
)

export default api
