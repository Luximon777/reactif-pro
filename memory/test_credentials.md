# Test Credentials

## Espace Personnel (Pseudonyme Login)
- **Pseudonyme**: marc19
- **Password**: Solerys777!
- **Pseudonyme**: mike7
- **Password**: Solerys777!

## Espace Employeurs (Admin bypass)
- **Email**: rh@reactifpro.fr
- **Password**: Reactif@pro2026!

## Appui aux parcours (Admin bypass)
- **Email**: admin@reactifpro.fr
- **Password**: Choukette@777

## Admin Gate Passwords
- **Admin**: Choukette@777
- **Dev/Programmeur**: Reactif@pro2026!
- **Invité**: Reactif@pro2026!

## Notes
- Login via the "Espace Personnel" card → "Accéder" button → AuthModal
- After login, redirects to /dashboard with full features
- Users are auto-seeded on backend startup
- Admin gate spaces are open by default (GET /api/admin/gate-state returns spaces_open: true)
