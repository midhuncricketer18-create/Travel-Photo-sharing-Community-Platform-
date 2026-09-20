# Class and Module Diagram

This diagram describes the modules and classes currently implemented in the backend. The service package exists but contains no service implementations.

```mermaid
flowchart TD
    Main[app/main.py\nFastAPI application]

    subgraph API[app/api]
        AuthAPI[auth.py\nregister, login, me]
        PhotographerAPI[photographers.py\nprofile endpoints]
        PhotoAPI[photos.py\nphoto endpoints]
        ProductAPI[products.py\nproduct endpoints]
        CartAPI[cart.py\ncart endpoints]
        OrderAPI[orders.py\norder endpoints]
    end

    subgraph Schemas[app/schemas]
        AuthSchemas[auth.py]
        PhotographerSchemas[photographer.py]
        PhotoSchemas[photo.py]
        ProductSchemas[product.py]
        CartSchemas[cart.py]
        OrderSchemas[order.py]
    end

    subgraph Core[app/core]
        Database[database.py\nengine, SessionLocal, Base]
        Security[security.py\nbcrypt, JWT]
        Dependencies[dependencies.py\ncurrent user and roles]
    end

    subgraph Models[app/models]
        User[User]
        Photographer[Photographer]
        Photo[Photo]
        Product[Product]
        Cart[Cart]
        CartItem[CartItem]
        Order[Order]
        OrderItem[OrderItem]
    end

    Main --> AuthAPI
    Main --> PhotographerAPI
    Main --> PhotoAPI
    Main --> ProductAPI
    Main --> CartAPI
    Main --> OrderAPI

    AuthAPI --> AuthSchemas
    PhotographerAPI --> PhotographerSchemas
    PhotoAPI --> PhotoSchemas
    ProductAPI --> ProductSchemas
    CartAPI --> CartSchemas
    OrderAPI --> OrderSchemas

    API --> Dependencies
    AuthAPI --> Security
    Dependencies --> Security
    API --> Database
    Database --> Models

    User --> Photographer
    User --> Cart
    User --> Order
    Photographer --> Photo
    Photo --> Product
    Cart --> CartItem
    CartItem --> Product
    Order --> OrderItem
    OrderItem --> Product

    Services[app/services\npackage only; no implementations]
```

## Module Responsibilities

- `app/main.py` creates the FastAPI application and registers all routers.
- `app/api/` contains the implemented route handlers and current business logic.
- `app/schemas/` contains Pydantic request and response models.
- `app/core/database.py` loads `DATABASE_URL`, creates the SQLAlchemy engine/session factory, and defines `Base`.
- `app/core/security.py` hashes passwords with bcrypt and creates/decodes JWTs.
- `app/core/dependencies.py` loads the authenticated user and provides customer, photographer, and administrator role dependencies.
- `app/models/` contains the eight SQLAlchemy models.
- `app/services/` currently contains only `__init__.py`; no service layer is claimed in this diagram.
