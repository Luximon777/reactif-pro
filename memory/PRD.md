# Re'Actif Pro - PRD

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + Recharts
- Backend: FastAPI + MongoDB (Motor async)
- Auth: Pseudonyme anonyme (JWT tokens) + Login pro (email/password)
- LLM: OpenAI GPT via Emergent LLM Key (emergentintegrations)

## Implementé

### Core
- Design D'CLIC PRO, Auth multi-niveaux, Analyse CV, Passeport de competences
- Observatoire predictif, Job Matching, Formations, Explorateur
- CI/CD GitHub Actions -> OVH VPS

### Ubuntoo (Communauté)
- Section communautaire integree /ubuntoo (6 onglets)
- Pipeline Ubuntoo <-> Observatoire (AI detection signaux)
- Sync profil Re'Actif Pro -> Ubuntoo (AI)

### Espace Partenaires de Parcours (COMPLET)

**Phase 1 - Base:**
- Dashboard d'accompagnement multi-onglets
- Inscription partenaire avec validation SIRET + charte ethique ALT&ACT
- Consentement RGPD (CGU + Politique de confidentialite)
- Login pro par email
- CRUD beneficiaires (creation, statut, progression, notes, suppression)
- Gestion freins peripheriques (8 categories)
- Suivi competences validees
- Statistiques temps reel

**Phase 2 - ChatGPT Requirements:**
- Liaison beneficiaire <-> profil Re'Actif Pro (recherche par pseudo, consentement)
- Acces lecture profil lie (competences, CV, passeport, D'CLIC)
- Systeme d'alertes (inactivite 15j, freins critiques, attente prolongee)
- Diagnostic enrichi (contexte social, mobilite, motivation, posture, autonomie, soft skills, observations)
- Orientation IA (GPT: metiers recommandes, formations, dispositifs adaptes, actions immediates, vigilance)
- Contribution a l'Observatoire (freins recurrents, competences emergentes, tensions secteurs)
- Recherche d'utilisateurs Re'Actif Pro pour liaison

## Endpoints Partenaires
- POST /api/auth/register-partenaire (inscription structure)
- POST /api/auth/login-pro (connexion email)
- GET /api/partenaires/stats (statistiques dashboard incl. linked_profiles)
- GET /api/partenaires/profile (profil structure)
- GET /api/partenaires/alertes (alertes inactivite, freins critiques)
- GET/POST/PUT/DELETE /api/partenaires/beneficiaires (CRUD)
- GET /api/partenaires/beneficiaires/{id} (detail)
- POST /api/partenaires/beneficiaires/{id}/link (lier profil Re'Actif Pro)
- DELETE /api/partenaires/beneficiaires/{id}/link (delier)
- GET /api/partenaires/beneficiaires/{id}/linked-profile (profil complet lie)
- PUT /api/partenaires/beneficiaires/{id}/diagnostic (diagnostic enrichi)
- POST /api/partenaires/beneficiaires/{id}/orientation (orientation IA)
- POST /api/partenaires/beneficiaires/{id}/freins (ajouter frein)
- PUT /api/partenaires/beneficiaires/{id}/freins/{fid} (resoudre)
- POST /api/partenaires/beneficiaires/{id}/skills (valider competence)
- GET /api/partenaires/search-users (recherche utilisateurs)
- POST /api/partenaires/contribution-observatoire (contribution observatoire)

## Backlog
- P1: Coffre-fort numerique avec upload de fichiers reels (PDF, etc.)
- P2: Narratif IA personnalise D'CLIC PRO
- P2: FranceConnect
- P2: Coordination multi-acteurs (plusieurs partenaires pour un meme beneficiaire)
- P3: Ateliers de Codeveloppement / Micro-badges
- Refactoring: DclicTestPage.jsx, ObservatoireView.jsx (>2000 lignes)

## Test Reports
- Iteration 43: Phase 1 (25/25 backend, frontend 100%)
- Iteration 44: Phase 2 (15/15 backend, frontend 100%)
