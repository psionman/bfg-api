## API conventions

- All endpoints that mutate state use POST
- POST bodies are JSON
- No JSON is passed in URLs
- CSRF is required for all POST requests
- Client must call /ensure-csrf/ once on app startup
- CSRF token is sent via X-CSRFToken header
- Cookies must be sent with credentials: 'include'

## CSRF flow

1. Client calls GET /ensure-csrf/
2. Django sets csrftoken cookie
3. Client includes:
   - Cookie (credentials: 'include')
   - Header: X-CSRFToken=<csrftoken>
4. All POST endpoints require this

## Production checklist

- CSRF_COOKIE_SECURE = True (HTTPS)
- SESSION_COOKIE_SECURE = True
- CSRF_TRUSTED_ORIGINS includes frontend domain
- ensure-csrf endpoint not cached
