# Test Report

## Testing Overview

Testing was performed against the code that currently exists in the project. The current implementation contains FastAPI authentication, photographer, photo, product, cart, and order APIs backed by SQLAlchemy models. The React frontend and dedicated service layer are not implemented yet.

## Backend Tests

The following automated tests were executed with pytest:

- FastAPI root health endpoint
- FastAPI Swagger documentation endpoint
- Registration of all eight SQLAlchemy models
- SQLAlchemy relationship mapper configuration
- Required foreign keys
- Declared price, stock, and quantity constraints
- Safe in-memory schema creation

The latest complete backend result is **41 passed**.

Command:

```text
python -m pytest backend/tests -q
```

One third-party deprecation warning was reported by Starlette's TestClient dependency. It does not currently fail the tests.

## Database Tests

- SQLAlchemy model metadata: passed.
- Eight required table definitions: passed.
- Foreign-key declarations: passed.
- Relationship mapper configuration: passed.
- In-memory schema creation: passed.
- Real PostgreSQL connection: not available.

PostgreSQL was not installed or running locally. Port `5432` was unreachable, so no real PostgreSQL data was created or modified.

## API Tests

Implemented API coverage:

- `GET /`: passed with HTTP 200.
- `GET /docs`: passed with HTTP 200.

Authentication, photo, product, cart, and order endpoints are covered by the current backend test suite.

## Security Tests

Verified:

- No plain-text password field or password API exists.
- JWT authentication and role dependencies are implemented and tested.
- No hard-coded JWT secret was found.
- `.env` is ignored by `.gitignore`.
- `.venv` and `node_modules` are ignored.
- No frontend or sensitive API response exists to review yet.

Authentication, authorization, token validation, and protected-route security are covered by backend tests. CORS is not configured because the React frontend is not implemented yet.

## Frontend Tests

Not run. The `frontend/` directory contains no React application or `package.json`, so there is no frontend application to start or build.

## End-to-End Tests

Backend customer and photographer flows are covered by isolated API tests. A full browser flow cannot run because the React frontend does not exist yet.

## Error Handling Tests

Health, authentication, validation, database-model, cart, order, ownership, and authorization error responses are covered by backend tests.

## Build Verification

- Backend Python compilation: passed.
- Backend dependency check with `pip check`: passed.
- FastAPI startup: passed.
- Frontend build: not available because `frontend/package.json` does not exist.

## Bugs Found and Fixed

- Added the missing pytest test runner and FastAPI TestClient transport dependencies.
- Added focused automated tests for the implemented backend surface.
- No application runtime bug was found in the currently implemented health endpoint or model metadata.

## Remaining Known Issues

- PostgreSQL is not installed or running locally.
- No database migration setup exists.
- Authentication and JWT security are implemented.
- Resource APIs are implemented; a dedicated service layer is not.
- No React frontend exists.
- No GitHub Actions workflow exists.
- No `LICENSE` file exists.
- Architecture and API diagrams have not been created.
- The Starlette TestClient dependency emits a deprecation warning.

## Final Result

Backend tests for the currently implemented functionality: **41 passed**.

Overall project testing status: **backend partial**. The implemented backend passes its available automated checks, but frontend browser flows cannot be tested until the planned React application is implemented.