# AI Enhancement Proposal

## Problem
Collectors need a faster way to discover photographs by subject and mood, while photographers currently enter categories manually.

## Proposed enhancement
Add opt-in automatic photo categorization and tag suggestions when a photographer creates or edits a photo.

## Why it helps
Consistent tags improve browsing and discovery without changing the photographer's ownership of the final description. Customers can search by meaningful subjects once search is added to the catalog.

## Technical approach
A backend service would send an image reference to a vision model through an environment-configured provider. The provider response would be validated against an allow-list and stored as editable metadata. The feature should be disabled when no provider key is configured.

## Integration points
- Add a tag field to the photo model and schema.
- Add a provider adapter under `backend/app/services/`.
- Trigger suggestions explicitly from the photographer dashboard.
- Expose approved tags through the customer photo response.

## Risks
External image processing can create privacy, cost, and inaccurate-label risks. Requests must be opt-in, rate-limited, logged without secrets, and easy to override.

## Testing plan
Unit-test provider response validation and the disabled-without-key path. Add an API test proving that only the owning photographer can request suggestions.

This proposal is intentionally not enabled until the core payment and deployment flows are implemented and verified.
