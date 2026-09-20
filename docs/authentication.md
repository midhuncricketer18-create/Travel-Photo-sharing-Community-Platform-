# Authentication and Authorization

## Authentication Flow

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant Database

    Client->>FastAPI: POST /auth/register
    FastAPI->>FastAPI: Validate email, password, and registration role
    FastAPI->>FastAPI: Hash password with bcrypt
    FastAPI->>Database: Store user and hashed password
    Database-->>FastAPI: User record
    FastAPI-->>Client: UserResponse

    Client->>FastAPI: POST /auth/login
    FastAPI->>Database: Find user by email
    FastAPI->>FastAPI: Verify bcrypt password
    FastAPI->>FastAPI: Create JWT with user ID and role
    FastAPI-->>Client: Bearer access token

    Client->>FastAPI: Protected request with Authorization header
    FastAPI->>FastAPI: Decode and validate JWT
    FastAPI->>Database: Load active user by token subject
    Database-->>FastAPI: User record
    FastAPI->>FastAPI: Apply role dependency
    FastAPI-->>Client: Protected response or 401/403 error
```

## Implemented Endpoints

- `POST /auth/register`: creates a customer or photographer account.
- `POST /auth/login`: verifies the password and returns a JWT access token.
- `GET /auth/me`: returns the authenticated user profile.

Public registration does not accept `ADMINISTRATOR`. Administrator accounts are provisioned separately and can use administrator-protected endpoints.

## Token Details

- Passwords are hashed with bcrypt before storage.
- The JWT contains the user ID in `sub` and the role in `role`.
- The JWT algorithm, secret, and expiration are loaded from environment variables.
- Clients send the token as `Authorization: Bearer <token>`.
- The backend loads the user from the database and checks that the user is active.
- Missing or invalid credentials return `401 Unauthorized`.
- A valid user with the wrong role returns `403 Forbidden`.

## Roles and Current Access

### CUSTOMER

- Can access `/auth/me`.
- Can browse published photos and available products.
- Can access their own cart.
- Can create and view their own orders.
- Can cancel their own cancellable orders.
- Cannot manage photographer profiles, photos, or products.
- Cannot update order statuses.

### PHOTOGRAPHER

- Can access `/auth/me`.
- Can create, view, and update their own photographer profile.
- Can create, view, update, and delete their own photos.
- Can create, view, update, and delete products belonging to their own photos.
- Can view order items related to their own products.
- Cannot access customer-only cart or customer order endpoints.

### ADMINISTRATOR

- Can access `/auth/me`.
- Can update valid order status transitions through `PATCH /orders/{order_id}/status`.
- No administrator user-management API is currently implemented.
- Administrator access does not imply access to customer carts or customer order listings.
