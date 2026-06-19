# Test Credentials — Ré'Actif Pro

## Utilisateurs de test
| Pseudonyme | Mot de passe | Rôle | Notes |
|---|---|---|---|
| mike7 | Solerys777! | Utilisateur | Profil vide (pas de suggestions ROME) |
| pierre7 | Solerys777! | Utilisateur | Profil riche : expériences, preuves S.A.R.E, données OPC, 12 suggestions ROME |
| marc19 | Solerys777! | Utilisateur | |
| admin@reactifpro.fr | Choukette@777 | Admin | Accès admin complet |
| rh@reactifpro.fr | Solerys777! | RH | Espace employeur |

## API Login
```bash
curl -X POST "$API_URL/api/auth/login" -H "Content-Type: application/json" \
  -d '{"pseudo":"pierre7","password":"Solerys777!"}'
```
Note: Le champ est `pseudo` (pas `pseudonyme` ni `username`).
