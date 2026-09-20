# Changelog

## Unreleased

- Added the Vite/React frontend foundation with environment-based Axios configuration, authentication context, role guards, responsive marketplace pages, cart, checkout, order history, and photographer overview.
- Added environment-driven backend CORS configuration for local and deployed frontend origins.
- Added GitHub Actions CI and Render backend deployment configuration.
- Added the AI enhancement proposal; implementation remains intentionally deferred until payment and deployment prerequisites are available.
- Added protected administrator listing endpoints and a local admin dashboard with order status controls.
- Added customer dashboard, Demo Checkout, order details, and photographer profile/photo/product management screens.
- Made the existing `PROCESSING -> SHIPPED` order transition available for the demonstration flow.

- Created the initial project folder structure.
- Added planning and configuration files.
- Added the initial FastAPI database connection configuration.
- Added SQLAlchemy models and relationships for users, photographers, photos, products, carts, cart items, orders, and order items.
- Added JWT authentication, bcrypt password hashing, and role-based authorization.
- Added photographer profile, photo, product, cart, and order APIs.
- Added backend tests for the implemented API and database model behavior.
- Added system architecture documentation.
- Added the ER diagram, class/module diagram, API contract, authentication documentation, and order-flow documentation.
- Linked the design and API documentation from README.md.
- Real payment, shipping, cloud deployment, and AI enhancement remain intentionally out of scope for this academic demo.
