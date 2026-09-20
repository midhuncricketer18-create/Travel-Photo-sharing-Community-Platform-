# Entity Relationship Diagram

This diagram reflects the SQLAlchemy models currently registered in `backend/app/models/`. There are eight implemented tables and no additional application tables in the model metadata.

```mermaid
erDiagram
    USERS ||--o| PHOTOGRAPHERS : has
    USERS ||--o| CARTS : owns
    USERS ||--o{ ORDERS : places
    PHOTOGRAPHERS ||--o{ PHOTOS : creates
    PHOTOS ||--o{ PRODUCTS : offers
    CARTS ||--o{ CART_ITEMS : contains
    PRODUCTS ||--o{ CART_ITEMS : selected_in
    ORDERS ||--o{ ORDER_ITEMS : contains
    PRODUCTS ||--o{ ORDER_ITEMS : purchased_as

    USERS {
        int id PK
        varchar email UK
        varchar hashed_password
        enum role
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    PHOTOGRAPHERS {
        int id PK
        int user_id FK UK
        varchar display_name
        text bio
        datetime created_at
        datetime updated_at
    }
    PHOTOS {
        int id PK
        int photographer_id FK
        varchar title
        text description
        varchar image_url
        varchar category
        enum status
        datetime created_at
        datetime updated_at
    }
    PRODUCTS {
        int id PK
        int photo_id FK
        varchar name
        varchar size
        varchar material
        decimal price
        int stock
        enum status
        datetime created_at
        datetime updated_at
    }
    CARTS {
        int id PK
        int user_id FK UK
        datetime created_at
        datetime updated_at
    }
    CART_ITEMS {
        int id PK
        int cart_id FK
        int product_id FK
        int quantity
    }
    ORDERS {
        int id PK
        int customer_id FK
        enum status
        decimal total_amount
        datetime created_at
        datetime updated_at
    }
    ORDER_ITEMS {
        int id PK
        int order_id FK
        int product_id FK
        int quantity
        decimal unit_price
    }
```

## Relationship Details

- One `User` has zero or one `Photographer` profile. `photographers.user_id` is unique and cascades on user deletion.
- One `User` has zero or one `Cart`. `carts.user_id` is unique and cascades on user deletion.
- One `User` places many `Orders` through `orders.customer_id`.
- One `Photographer` owns many `Photos` through `photos.photographer_id`; deleting a photographer cascades to photos.
- One `Photo` has many `Products` through `products.photo_id`; deleting a photo cascades to products.
- One `Cart` contains many `CartItems`; deleting a cart cascades to cart items.
- One `Product` can occur in many cart items.
- One `Order` contains many `OrderItems`; deleting an order cascades to order items.
- One `Product` can occur in many order items.
- `CartItem` has a unique `(cart_id, product_id)` pair.
- Product price must be positive and stock cannot be negative.
- Cart and order item quantities must be positive.
- `OrderItem.unit_price` stores the purchase-time price snapshot.

The `OrderStatus` enum also retains `SHIPPED` and `DELIVERED` in the current implementation, in addition to `PENDING`, `CONFIRMED`, `PROCESSING`, `COMPLETED`, and `CANCELLED`.
