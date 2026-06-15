# RE'ACTIF PRO - Product Requirements Document

## Core Concept
Plateforme d'intelligence professionnelle — Observatoire Predictif des Competences (OPC).
Infrastructure d'intelligence territoriale : Anticiper les competences, piloter l'emploi.
Code source de production restaure depuis le source map de reactif.pro.

## Architecture
- **Backend** : FastAPI (server.py ~4100 lignes + opc/ + ubuntoo_routes.py)
- **Frontend** : React + Tailwind + Shadcn/UI + react-router-dom (code de prod restaure)
- **DB** : MongoDB (users, tokens, profiles, passport_competences, admin_config, opc_*, etc.)
- **IA** : OpenAI GPT-5.2 via emergentintegrations (Emergent LLM Key)

## App Flow
1. Page loads → AdminGate (with Admin/Dev/Invite status selectors)
2. Space cards shown (gate-state open by default)
3. Click "Acceder" → AuthModal opens
4. Login (mike7/Solerys777!) → loginPseudo → POST /api/auth/login → token
5. AdminGate calls loginFromGate → sets adminStatus → shows routes
6. Redirect to /dashboard → Dashboard with tabs

## Routes Frontend (Production)
- `/` : Landing page (role-based cards) OR redirect to /dashboard if authenticated
- `/dashboard/*` : Main dashboard (ProtectedRoute)
- `/observatoire` : OPC Public Page
- `/ubuntoo` : Ubuntoo messaging page
- `/test-dclic` : Test D'CLIC PRO page
- `/passport/shared/:shareId` : Shared passport public page
- `/trajectoire/:shareId` : Shared trajectory public page

## Dashboard Tabs (ParticulierView)
- Accueil : Welcome, 4 etapes, actions rapides
- Profil : Profil professionnel
- Trajectoire : CV upload/analyse, frise, centres d'interet, analyse IA, audit, generer CV
- Competences : Competences transversales
- Marche : Observatoire, tendances metiers
- Opportunites : Offres d'emploi compatibles
- Job Dating : Evenements recrutement
- Portefeuille : Coffre-fort numerique
- Confidentialite : Parametres vie privee

## Key API Endpoints
### Auth
- `POST /api/auth/anonymous` : Create anonymous token + profile
- `POST /api/auth/login` : Login with pseudo/password → {token, role, profile_id, pseudo, auth_mode}
- `POST /api/auth/login-pro` : Login for entreprise/partenaire
- `POST /api/auth/register` : Register pseudo account
- `POST /api/auth/register-entreprise` : Register entreprise
- `POST /api/auth/register-partenaire` : Register partenaire
- `POST /api/auth/upgrade` : Upgrade anonymous to pseudo
- `GET /api/auth/verify` : Verify token → {valid, role, profile_id, auth_mode, pseudo, identity_level}
- `POST /api/auth/switch-role` : Switch user role

### Admin
- `GET /api/admin/gate-state` : Get gate open/closed state
- `POST /api/admin/gate-state` : Set gate state (requires admin password)

### CV Pipeline
- `POST /api/cv/extract-text-b64` : Upload CV en base64
- `POST /api/cv/analyze-text` : Analyse CV par IA (background task)
- `GET /api/cv/analyze/status` : Polling du statut analyse
- `GET /api/cv/last-analysis` : Derniere analyse completee
- `GET /api/cv/models` : 4 modeles de CV generes

## Source Files (Extracted from reactif.pro source map)
- App.js (364 lines) - AuthProvider, routing, AdminGate integration
- pages/Dashboard.jsx - Main dashboard hub
- pages/Landing.jsx - Landing page with role cards
- components/AdminGate.jsx - Admin gate with space cards
- components/AuthModal.jsx - Login/Register modal
- components/GpsDashboard.jsx - GPS coach dashboard
- components/CoachVirtuel.jsx - Coach RE'ACTIF widget
- components/CvAnalysis/ - CV analysis components
- views/ParticulierView.jsx - Main particulier dashboard
- views/EntrepriseView.jsx - Enterprise dashboard
- views/PartenaireView.jsx - Partner dashboard
- views/entreprise/ - Enterprise sub-views (10+ files)
- views/partenaire/ - Partner sub-views
- views/ubuntoo/ - Ubuntoo sub-views

## Completed
- [x] OPC complet avec 4 vues
- [x] Module Ubuntoo messagerie
- [x] Landing Page identique a reactif.pro
- [x] Auth pseudonyme (marc19, mike7 / Solerys777!)
- [x] Restauration COMPLETE du code source de production via source map
- [x] Dashboard avec 9 onglets, Coach RE'ACTIF, 4 etapes
- [x] Admin Gate avec gate-state API
- [x] Auth routes completes (login, register, upgrade, entreprise, partenaire, login-pro)
- [x] Seed automatique des utilisateurs (marc19, mike7, rh@, admin@)

## Source GitHub
https://github.com/Luximon777/reactif-pro

## Prioritized Backlog
### P1
- [ ] Refactoring backend server.py en modules routes/
### P2
- [ ] Export PDF des CV/passeport (4 modeles)
### P3
- [ ] Modules d'auto-evaluation (Soft Skills CSE, Valeurs VIA)
- [ ] Diagnostic CCSP
- [ ] Ateliers de Codeveloppement
- [ ] Systeme de micro-titres/badges
