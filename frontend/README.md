# Stillroom frontend

React and Vite client for the Online Photography Print Platform.

## Local setup

```powershell
npm install
Copy-Item .env.example .env
npm run dev
```

Set `VITE_API_BASE_URL` to the FastAPI origin. The backend must allow the frontend origin through `CORS_ORIGINS`.

## Current flows

The client includes registration, login, role guards, customer browsing, photo details, cart, checkout, order history, photographer overview, and the administrator operation notice. It uses the backend as the source of truth for permissions, stock, totals, and order status.
