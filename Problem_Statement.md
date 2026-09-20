# Problem Statement

## 1. Title

Online Photography Print Selling Platform

## 2. Domain

E-Commerce / Photography / Full-Stack Web Application

## 3. Who is the user? (2-3 user types, with roles)

### 1. Photographer
- Creates an account and logs in.
- Uploads photographs.
- Manages photographs and print details.
- Manages available print products.

### 2. Customer
- Creates an account and logs in.
- Browses available photographs.
- Views photograph and print details.
- Adds prints to the shopping cart.
- Places orders and views order history.

### 3. Administrator
- Manages users and platform data.
- Monitors photographs and orders.
- Manages platform-level operations.

## 4. What problem are we solving? (3-5 sentences, real-life example)

Photographers need a simple online platform to showcase their photographs and sell them as physical prints. Customers may find it difficult to discover photographs from different photographers and purchase prints through a single platform. Traditional methods may require photographers to manage product information and orders manually. This project provides a centralized web application where photographers can upload photographs and offer prints for sale, while customers can browse photographs, add prints to a cart, and place orders.

## 5. Proposed Solution (what the application will do, feature-wise)

The proposed system is a full-stack web application for selling photography prints.

The application will provide the following features:

- User registration and login.
- Role-based access for photographers, customers, and administrators.
- Photographer profile management.
- Photograph upload and management.
- Photograph and print product listing.
- Customer browsing and viewing of photographs.
- Shopping cart management.
- Order creation and order history.
- Order management.
- Database storage for users, photographs, products, carts, and orders.
- REST APIs for frontend-backend communication.
- Secure authentication using JWT.
- API documentation using Swagger/OpenAPI.
- Cloud deployment of the application.
- Scope for third-party payment integration.
- Scope for a future AI-based enhancement.

## 6. Core Entities / Database Tables (list all, minimum 5)

The application will use the following core database tables:

1. Users
2. Photographer Profiles
3. Photos
4. Print Products
5. Cart Items
6. Orders
7. Order Items

These tables will have relationships to support user management, photograph management, shopping cart operations, and order processing.

## 7. User Roles & Permissions (minimum 2 distinct roles)

### Photographer

Permissions:
- Register and login.
- Manage photographer profile.
- Upload photographs.
- Add and manage print products.
- Update photograph/product information.
- Delete own photographs/products.
- View relevant orders.

### Customer

Permissions:
- Register and login.
- Browse photographs.
- View photograph and print details.
- Add prints to cart.
- Update cart quantity.
- Remove items from cart.
- Place orders.
- View own orders and order details.

### Administrator

Permissions:
- Login to the administration area.
- Manage users.
- Monitor photographers and customers.
- Monitor photographs/products.
- Monitor orders.
- Perform platform-level management operations.

## 8. Success Criteria

The project will be considered successful when:

- A user can register and securely log in.
- A photographer can upload and manage photographs.
- A customer can browse available photographs and print products.
- A customer can add products to the cart.
- A customer can place an order successfully.
- Customers can view their order history.
- Photographers can manage their uploaded photographs and products.
- Role-based access prevents unauthorized operations.
- Data is correctly stored and retrieved from the PostgreSQL database.
- The main application flows work successfully from frontend to backend to database.
- The application can be deployed and accessed through the cloud.

## 9. Out of Scope (clearly list what you will NOT build, to avoid over-commitment)

The following features are outside the initial project scope:

- Physical printing and delivery of photographs by the platform.
- Managing physical inventory in printing facilities.
- Real-world logistics and delivery tracking.
- Multiple payment providers.
- Advanced accounting and taxation systems.
- Native Android or iOS applications.
- Advanced photo editing software.
- Social-media-style posting and messaging features.
- Complex recommendation systems in the initial version.

AI-based enhancement may be added later as part of the final enhancement phase.

## 10. Chosen Track: Java (Spring Boot) / Python (Django or FastAPI)

### Chosen Track: Python — FastAPI

Technology stack:

- Frontend: React.js
- UI: Bootstrap
- Backend: Python FastAPI
- Database: PostgreSQL
- ORM: SQLAlchemy
- Authentication: JWT
- API Client: Axios
- Testing: Pytest
- API Documentation: FastAPI Swagger/OpenAPI
- Version Control: Git and GitHub
- CI/CD: GitHub Actions
- Backend Deployment: Render
- Frontend Deployment: Vercel
