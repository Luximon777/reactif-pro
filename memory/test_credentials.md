# Test Credentials

## Authentication System
The app uses pseudonyme + password authentication for Espace Personnel.

### Login Credentials:
- **Pseudonyme:** marc19
- **Password:** Solerys777!

### How to authenticate:
POST /api/auth/login with {"pseudonyme": "marc19", "password": "Solerys777!"}

### API Response:
```json
{
  "id": "uuid",
  "pseudonyme": "marc19",
  "created_at": "timestamp"
}
```

### Note:
The user marc19 is seeded automatically on backend startup (see server.py on_startup event).
