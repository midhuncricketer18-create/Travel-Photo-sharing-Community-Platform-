# Online Photography Print Platform

A full-stack web application where photographers can sell physical prints of their photographs and customers can browse, purchase, and manage orders.

## Project Status

This is an academic/demo project for local college demonstration. The FastAPI/PostgreSQL backend provides JWT authentication, role-based authorization, photographer profiles, photo and product APIs, carts, orders, and administrator listings. The React/Vite frontend provides authentication, browsing, photo details, cart, Demo Checkout, order history, photographer management, and administrator overview flows. No real payment, shipping, printing, or production deployment is included.

## Local administrator demo account

Provision an administrator only from the backend environment with an interactive password prompt:

```powershell
Set-Location backend
python provision_admin.py --email admin.demo@example.com
```

The command does not expose an API endpoint or store a password in source code. Use `--promote-existing` only when intentionally changing an existing local account's role.

## Technology

- Frontend: React.js, Bootstrap, Axios
- Backend: Python FastAPI, SQLAlchemy
- Database: PostgreSQL
- Authentication: JWT
- Testing: Pytest
- Deployment: Render and Vercel
- Automation: GitHub Actions

## Project Folders

- `backend/`: FastAPI backend, SQLAlchemy models, API routers, schemas, authentication, and tests.
- `frontend/`: React/Vite client, API services, authentication context, pages, and styles.
- `docs/`: Project planning, test, and technical documentation.
- `docs/diagrams/`: System architecture documentation and future diagrams.

## Documentation

- [Problem Statement](Problem_Statement.md)
- [System Architecture](docs/diagrams/system_architecture.md)
- [ER Diagram](docs/diagrams/er_diagram.md)
- [Class/Module Diagram](docs/diagrams/class_module_diagram.md)
- [API Contract](docs/api_contract.md)
- [Authentication](docs/authentication.md)
- [Order Flow](docs/order_flow.md)
- [Test Report](docs/TEST_REPORT.md)
- [AI Enhancement Proposal](Enhancement_Proposal.md)

## Features

Customers can browse published work, select print formats, manage a cart, check out, view orders, and cancel eligible orders. Photographers have protected profile, photo, product, and related-order APIs. Administrators can perform supported order status transitions through the protected API.

## Live Demo and Demo Video

Coming soon.

## Getting Started

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

In another terminal:

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

## Environment Variables

Backend: `DATABASE_URL`, `JWT_SECRET_KEY`, optional `JWT_ALGORITHM`, `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`, and `CORS_ORIGINS`. Frontend: `VITE_API_BASE_URL`. Keep real values out of Git.

## API Documentation

See [docs/api_contract.md](docs/api_contract.md). FastAPI Swagger is available at `/docs`.

## Testing

Run `pytest` and `python -m compileall -q app` from `backend`. Run `npm run build` from `frontend`. GitHub Actions runs these checks in `.github/workflows/ci.yml`.

## Deployment

`render.yaml` prepares the backend for Render. The frontend is Vercel-compatible with `VITE_API_BASE_URL`. No live deployment is claimed yet.

## Folder Structure

- `backend/app/`: FastAPI application, models, schemas, routes, security, and database setup.
- `backend/tests/`: API and model tests.
- `frontend/src/`: React pages, services, context, components, and styles.
- `docs/`: API, authentication, order-flow, and architecture documentation.

## Future Enhancements

Possible academic enhancements include better search, image upload storage, and the opt-in AI tagging proposal in [Enhancement_Proposal.md](Enhancement_Proposal.md). Real payment and logistics are intentionally out of scope.

## License

No license has been selected yet.
