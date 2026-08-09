# Authentication

## Overview

The project uses JWT authentication.

## Login Flow

1. User logs in
2. Refresh token is stored in an HttpOnly cookie
3. Access token is returned
4. GraphQL requests send:

```http
Authorization: Bearer <access_token>
```

## Security

- HttpOnly refresh cookie
- SameSite=Lax
- CSRF protection
