# Test Credentials

## Espace Personnel (Pseudonyme Login)
- **Pseudonyme**: marc19
- **Password**: Solerys777!
- **Pseudonyme**: mike7
- **Password**: Solerys777!

## Notes
- Login via the "Espace Personnel" card on the landing page
- Opens a modal dialog for pseudonyme/password entry
- After login, redirects to /dashboard with full CV upload, passeport, coffre-fort features
- Users are auto-seeded on backend startup (see server.py on_startup event)
- Anonymous tokens are also created for API calls (used by Dashboard views)
