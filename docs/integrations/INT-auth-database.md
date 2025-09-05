---
type: integrations
id: INT-auth-database
title: Authentication Database Integration
status: approved
owner: Backend Team
created: 2025-09-05
links:
  - prd: [PRD-user-auth]
  - arch: [ARCH-auth-architecture]
  - impl: [IMPL-auth-service]
  - exec: [EXEC-auth-deployment]
---

# Authentication Database Integration

## Overview
Integration specifications for connecting the authentication system with PostgreSQL and Redis databases.

## Database Schema

### Users Table (PostgreSQL)
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  email_verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### Sessions Table (Redis)
- Key: `session:{session_id}`
- Value: JSON with user_id, expires_at, created_at
- TTL: 24 hours

## API Endpoints

### Authentication Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `POST /api/auth/refresh` - Token refresh
- `POST /api/auth/forgot-password` - Password reset request
- `POST /api/auth/reset-password` - Password reset

### User Management Endpoints
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update user profile
- `DELETE /api/users/account` - Delete user account

## Security Requirements
- All passwords must be hashed with bcrypt
- JWT tokens must be signed with RS256
- Session cookies must be httpOnly and secure
- All endpoints must validate input
- Rate limiting must be applied

## Error Handling
- 400: Bad Request (validation errors)
- 401: Unauthorized (invalid credentials)
- 403: Forbidden (insufficient permissions)
- 404: Not Found (user not found)
- 429: Too Many Requests (rate limited)
- 500: Internal Server Error

## Testing Requirements
- Unit tests for all endpoints
- Integration tests with database
- Security tests for authentication flows
- Performance tests for rate limiting
