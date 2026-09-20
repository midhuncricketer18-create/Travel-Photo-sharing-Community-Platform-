# API Contract

All protected endpoints use the header:

```text
Authorization: Bearer <access_token>
```

Validation errors normally return `422`. Authentication failures return `401`; wrong roles return `403`; missing resources return `404`; duplicate resources or invalid business operations use `409` or `400` as implemented.

## Health and Documentation

### `GET /`

- Authentication: no
- Request body: none
- Success: `200`, `{"message": "Online Photography Print Platform API is running"}`

### `GET /docs`

- Authentication: no
- Success: FastAPI Swagger UI page

### Automatic FastAPI documentation routes

- `GET /openapi.json`: no authentication; returns the generated OpenAPI schema.
- `GET /redoc`: no authentication; returns the generated ReDoc documentation page.
- `GET /docs/oauth2-redirect`: no authentication; internal Swagger OAuth2 redirect support route.

## Authentication

### `POST /auth/register`

- Authentication: no
- Request body:

```json
{
  "email": "customer@example.com",
  "password": "strong-password",
  "role": "CUSTOMER"
}
```

- `role`: `CUSTOMER` or `PHOTOGRAPHER`; defaults to `CUSTOMER`.
- Success: `201`, user ID, email, role, and active status.
- Errors: `409` duplicate email; `422` invalid email/password/role.
- Passwords are never returned.

### `POST /auth/login`

- Authentication: no
- Request body:

```json
{
  "email": "customer@example.com",
  "password": "strong-password"
}
```

- Success: `200`, `{"access_token": "...", "token_type": "bearer"}`.
- Errors: `401` invalid email or password; `422` invalid input.

### `GET /auth/me`

- Authentication: yes
- Role: any authenticated role
- Request body: none
- Success: `200`, current user ID, email, role, and active status.
- Errors: `401` missing or invalid token.

## Photographer Profiles

### `POST /photographers/profile`

- Authentication: yes
- Role: `PHOTOGRAPHER`
- Request body: `{"display_name": "...", "bio": "..."}`.
- Success: `201`, photographer profile.
- Errors: `403` wrong role; `409` profile already exists; `422` invalid fields.

### `GET /photographers/profile`

- Authentication: yes
- Role: `PHOTOGRAPHER`
- Request body: none
- Success: `200`, own profile.
- Errors: `403` wrong role; `404` profile not found.

### `PUT /photographers/profile`

- Authentication: yes
- Role: `PHOTOGRAPHER`
- Request body: optional `display_name` and/or `bio`.
- Success: `200`, updated own profile.
- Errors: `403` wrong role; `404` profile not found; `422` invalid fields.

## Photos

### `POST /photos`

- Authentication: yes
- Role: `PHOTOGRAPHER`
- Request body: `title`, optional `description`, `image_url`, optional `category`, optional `status` (`DRAFT` or `PUBLISHED`).
- Success: `201`, created photo.
- Errors: `403` wrong role or missing profile; `422` invalid fields.

### `GET /photos/mine`

- Authentication: yes
- Role: `PHOTOGRAPHER`
- Request body: none
- Success: `200`, own photo list.
- Errors: `403` wrong role; `404` profile not found.

### `GET /photos`

- Authentication: yes
- Role: `CUSTOMER`
- Request body: none
- Success: `200`, published photo list.
- Errors: `401` missing token; `403` wrong role.

### `GET /photos/{photo_id}`

- Authentication: yes
- Role: `CUSTOMER`
- Path parameter: `photo_id`.
- Success: `200`, published photo.
- Errors: `403` wrong role; `404` missing or unpublished photo.

### `PUT /photos/{photo_id}`

- Authentication: yes
- Role: owning `PHOTOGRAPHER`
- Path parameter: `photo_id`.
- Request body: any subset of photo update fields.
- Success: `200`, updated photo.
- Errors: `403` wrong owner/role; `404` missing photo; `422` invalid fields.

### `DELETE /photos/{photo_id}`

- Authentication: yes
- Role: owning `PHOTOGRAPHER`
- Path parameter: `photo_id`.
- Success: `204`, no response body.
- Errors: `403` wrong owner/role; `404` missing photo.

## Products

### `POST /products`

- Authentication: yes
- Role: `PHOTOGRAPHER`
- Request body: `photo_id`, `name`, `size`, `material`, positive `price`, non-negative `stock`, optional `status` (`AVAILABLE` or `UNAVAILABLE`).
- Success: `201`, created product.
- Errors: `403` photo belongs to another photographer; `404` photo not found; `422` invalid price/stock/fields.

### `GET /products/mine`

- Authentication: yes
- Role: `PHOTOGRAPHER`
- Success: `200`, products belonging to the photographer's photos.
- Errors: `403` wrong role; `404` profile not found.

### `GET /products`

- Authentication: yes
- Role: `CUSTOMER`
- Success: `200`, available products belonging to published photos.
- Errors: `401` missing token; `403` wrong role.

### `GET /products/{product_id}`

- Authentication: yes
- Role: `CUSTOMER`
- Path parameter: `product_id`.
- Success: `200`, available product from a published photo.
- Errors: `403` wrong role; `404` missing, unavailable, or unpublished product.

### `PUT /products/{product_id}`

- Authentication: yes
- Role: owning `PHOTOGRAPHER`
- Request body: optional product fields; price must be positive and stock non-negative.
- Success: `200`, updated product.
- Errors: `403` wrong owner/role; `404` missing product; `422` invalid fields.

### `DELETE /products/{product_id}`

- Authentication: yes
- Role: owning `PHOTOGRAPHER`
- Success: `204`, no response body.
- Errors: `403` wrong owner/role; `404` missing product.

## Cart

### `GET /cart`

- Authentication: yes
- Role: `CUSTOMER`
- Success: `200`, own cart, item product information, subtotals, and `total_amount`.
- The cart is created if the customer does not have one.
- Errors: `401` missing token; `403` wrong role.

### `GET /cart/items`

- Authentication: yes
- Role: `CUSTOMER`
- Success: `200`, own cart item list.
- Errors: `401` or `403`.

### `POST /cart/items`

- Authentication: yes
- Role: `CUSTOMER`
- Request body: `{"product_id": 1, "quantity": 2}`.
- Success: `201`, updated cart response.
- Re-adding the same product increases its existing quantity.
- Errors: `400` unavailable/unpublished product or insufficient stock; `404` product not found; `422` invalid IDs/quantity.

### `PUT /cart/items/{item_id}`

- Authentication: yes
- Role: `CUSTOMER` who owns the cart item
- Request body: `{"quantity": 2}`.
- Success: `200`, updated cart response.
- Errors: `400` quantity exceeds stock; `404` item/product not found; `422` invalid quantity.

### `DELETE /cart/items/{item_id}`

- Authentication: yes
- Role: `CUSTOMER` who owns the cart item
- Success: `204`, no response body.
- Errors: `404` item not found.

## Orders

### `POST /orders`

- Authentication: yes
- Role: `CUSTOMER`
- Request body: none; uses the current cart.
- Success: `201`, order with order items, purchase-time prices, total, and `PENDING` status.
- Errors: `400` empty cart, unavailable/unpublished product, or insufficient stock; `404` cart/product not found.

### `GET /orders`

- Authentication: yes
- Role: `CUSTOMER`
- Success: `200`, only the current customer's orders.
- Errors: `401` or `403`.

### `GET /orders/{order_id}`

- Authentication: yes
- Role: owning `CUSTOMER`
- Path parameter: `order_id`.
- Success: `200`, order details and items.
- Errors: `403` wrong role; `404` missing or another customer's order.

### `GET /orders/photographer`

- Authentication: yes
- Role: `PHOTOGRAPHER`
- Success: `200`, orders containing the photographer's products, filtered to related items and totals.
- Errors: `403` wrong role; `404` photographer profile not found.

### `POST /orders/{order_id}/cancel`

- Authentication: yes
- Role: owning `CUSTOMER`
- Request body: none.
- Success: `200`, cancelled order; product stock is restored.
- Errors: `400` cancellation is not allowed or already cancelled; `404` missing/foreign order.

### `PATCH /orders/{order_id}/status`

- Authentication: yes
- Role: `ADMINISTRATOR`
- Request body: `{"status": "CONFIRMED"}` using the implemented `OrderStatus` values.
- Success: `200`, updated order.
- Errors: `400` invalid transition; `403` wrong role; `404` order not found; `422` invalid status.

## Administrator Listings

These local demonstration endpoints require an `ADMINISTRATOR` token:

- `GET /admin/users`: list registered users.
- `GET /admin/photographers`: list photographer profiles.
- `GET /admin/photos`: list all photographs, including drafts.
- `GET /admin/products`: list all print products, including unavailable products.
- `GET /admin/orders`: list all orders with their items and totals.

All return `200` JSON arrays. Missing/invalid authentication returns `401`; non-administrator roles return `403`.
