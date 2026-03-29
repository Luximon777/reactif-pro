# Test Credentials

## Espace Partenaire
- Email: `test@missionlocale.fr`
- Password: `Solerys777!`
- Role: `partenaire`
- Login: POST /api/auth/login-pro with {pseudo: email, password: pwd}

## Espace Particulier (Preview Users)
- bob15: password `Solerys777!` — visibility: limited, real_first_name: Robert, real_last_name: Dupont
- bob18: password `Solerys777!` — visibility: limited, real_first_name: Alice, real_last_name: Martin
- bob22: password `Solerys777!` — visibility: limited, real_first_name: Marc, real_last_name: Lefevre (synced to partner)
- Login: POST /api/auth/login with {pseudo: "bob15", password: "Solerys777!"}

## Synced Beneficiaries
- Marc Lefevre (bob22) — synced=True, linked to partner test@missionlocale.fr
- Sophie Bernard — linked to bob18 (manual)
- Jean Martin — linked to bob15 (manual)
