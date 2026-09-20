import api from './api'

export const authService = {
  login: (payload) => api.post('/auth/login', payload),
  register: (payload) => api.post('/auth/register', payload),
  me: () => api.get('/auth/me'),
}

export const photographerService = {
  getProfile: () => api.get('/photographers/profile'),
  createProfile: (payload) => api.post('/photographers/profile', payload),
  updateProfile: (payload) => api.put('/photographers/profile', payload),
}

export const photoService = {
  list: () => api.get('/photos'),
  get: (id) => api.get(`/photos/${id}`),
  mine: () => api.get('/photos/mine'),
  create: (payload) => api.post('/photos', payload),
  update: (id, payload) => api.put(`/photos/${id}`, payload),
  remove: (id) => api.delete(`/photos/${id}`),
}

export const productService = {
  list: () => api.get('/products'),
  mine: () => api.get('/products/mine'),
  create: (payload) => api.post('/products', payload),
  update: (id, payload) => api.put(`/products/${id}`, payload),
  remove: (id) => api.delete(`/products/${id}`),
}

export const cartService = {
  get: () => api.get('/cart'),
  add: (payload) => api.post('/cart/items', payload),
  update: (id, payload) => api.put(`/cart/items/${id}`, payload),
  remove: (id) => api.delete(`/cart/items/${id}`),
}

export const orderService = {
  create: () => api.post('/orders'),
  list: () => api.get('/orders'),
  get: (id) => api.get(`/orders/${id}`),
  cancel: (id) => api.post(`/orders/${id}/cancel`),
  photographer: () => api.get('/orders/photographer'),
  updateStatus: (id, status) => api.patch(`/orders/${id}/status`, { status }),
}

export const adminService = {
  users: () => api.get('/admin/users'),
  photographers: () => api.get('/admin/photographers'),
  photos: () => api.get('/admin/photos'),
  products: () => api.get('/admin/products'),
  orders: () => api.get('/admin/orders'),
}
