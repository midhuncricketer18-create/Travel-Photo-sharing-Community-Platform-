import { Link } from 'react-router-dom'

export default function Home() {
  return <main className="hero"><div className="page-shell hero-copy"><p className="eyebrow">Independent photography, made tangible</p><h1>Images with a place in the room.</h1><p className="lede">Stillroom is a considered marketplace for archival prints by independent photographers. Find a frame for the quiet moments.</p><Link className="button" to="/browse">Explore the collection</Link><Link className="button alt" to="/register">Join Stillroom</Link></div></main>
}
