import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { photoService, productService } from '../services/services'

export default function Browse() {
  const [photos, setPhotos] = useState([]); const [products, setProducts] = useState([]); const [error, setError] = useState(''); const [loading, setLoading] = useState(true)
  useEffect(() => { Promise.all([photoService.list(), productService.list()]).then(([photoResponse, productResponse]) => { setPhotos(photoResponse.data); setProducts(productResponse.data) }).catch((err) => setError(err.userMessage || 'Sign in as a customer to browse the collection.')).finally(() => setLoading(false)) }, [])
  if (loading) return <main className="page-shell"><p className="status">Developing the collection...</p></main>
  return <main className="page-shell"><div className="section-head"><div><p className="eyebrow">The collection</p><h2>Find your image.</h2></div><p className="meta">{photos.length} photographs available</p></div>{error && <div className="alert">{error} <Link to="/login">Sign in</Link></div>} {!error && !photos.length && <p className="status">The collection is quiet for now.</p>}<div className="grid">{photos.map((photo) => { const options = products.filter((product) => product.photo_id === photo.id); return <Link to={`/photos/${photo.id}`} className="photo-card" key={photo.id}><img src={photo.image_url} alt={photo.title} /><div className="photo-card-body"><h3>{photo.title}</h3><p className="meta">{photo.category || 'Fine art print'} · {options.length} format{options.length === 1 ? '' : 's'}</p>{options[0] && <p className="price">From ${options[0].price}</p>}</div></Link> })}</div></main>
}
