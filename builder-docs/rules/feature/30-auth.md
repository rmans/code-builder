---
description: Token & auth safety in browser code
globs: src/**/*.ts,src/**/*.tsx
alwaysApply: true
---
# Tokens in httpOnly Cookies — Never localStorage/sessionStorage
## Rule
- Never use localStorage/sessionStorage for tokens
- Never pass tokens in querystrings or URL fragments
- Always use httpOnly, secure cookies
- Always send requests with withCredentials true
