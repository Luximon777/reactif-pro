# Test Credentials

## Espace Partenaire - Mission Locale Test
- Email: `test@missionlocale.fr`
- Password: `Solerys777!`
- Role: `partenaire`

## Espace Partenaire - Solerys
- Email: `cluximon@gmail.com`
- Password: `Solerys777!`
- Role: `partenaire`
- Structure: Solerys (acteur_insertion)

## Espace Particulier (Preview Users)
- bob15: password `Solerys777!` — visibility: limited, Robert Dupont
- bob18: password `Solerys777!` — visibility: limited, Alice Martin
- bob22: password `Solerys777!` — visibility: limited, Marc Lefevre
- bob23: password `Solerys777!`
- Login: POST /api/auth/login with {pseudo: "bob15", password: "Solerys777!"}
- Login pro: POST /api/auth/login-pro with {pseudo: "cluximon@gmail.com", password: "Solerys777!"}
