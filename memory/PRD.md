# RE'ACTIF PRO - Product Requirements Document

## Core Concept
Plateforme d'intelligence professionnelle — Observatoire Predictif des Competences (OPC).
Infrastructure d'intelligence territoriale : Anticiper les competences, piloter l'emploi.
Page d'accueil avec 5 acces distincts, systeme d'analyse CV par IA, authentification par pseudonyme.

## Architecture
- **Backend** : FastAPI (server.py ~4000 lignes + opc/ + ubuntoo_routes.py)
- **Frontend** : React + Tailwind + Shadcn/UI + react-router-dom
- **DB** : MongoDB (users, passport_competences, cv_jobs, cv_models, tokens, profiles, etc.)
- **IA** : OpenAI GPT-5.2 via emergentintegrations (Emergent LLM Key)

## Routes Frontend
- `/` : LandingPage (page d'accueil avec 5 acces - clone de reactif.pro)
- `/observatoire` : Observatoire OPC (page OPC standalone)
- `/ubuntoo` : Application messagerie / Parcours VSI
- `/dashboard/*` : Dashboard principal (route protegee, requiert authentification)
  - `/dashboard` : Vue par defaut selon role (ParticulierView, EntrepriseView, PartenaireView)
  - `/dashboard/passeport` : Passeport dynamique de competences
  - `/dashboard/coffre-fort` : Coffre-fort numerique de documents
  - `/dashboard/observatoire` : Vue Observatoire integree
  - `/dashboard/explorateur` : Explorateur de metiers
  - `/dashboard/evolution` : Indice d'evolution
  - `/dashboard/jobs` : Offres d'emploi
  - `/dashboard/learning` : Formations

## 5 Acces Landing Page → Destinations
1. **Espace Personnel** → Modale login (mike7/Solerys777!) → /dashboard (ParticulierView avec CV upload)
2. **Parcours VSI** → /ubuntoo
3. **OPC** (cercle central) → /observatoire
4. **Espace Employeurs** → Login auto role=entreprise → /dashboard (EntrepriseView)
5. **Appui aux parcours** → Login auto role=partenaire → /dashboard (PartenaireView)

## Auth System
- AuthProvider dans App.js avec contexte (token, role, pseudonyme)
- Login anonyme: POST /api/auth/anonymous → cree token + profile
- Login pseudonyme: POST /api/auth/login → verifie identifiants puis cree token anonyme
- Routes protegees via ProtectedRoute (verifie isAuthenticated)
- Roles: particulier, entreprise, partenaire

## CV Analysis Pipeline (Backend)
- POST /api/cv/extract-text-b64 : Upload CV en base64 (pas de multipart, contourne proxy)
- POST /api/cv/analyze-text : Lance analyse IA en arriere-plan
- GET /api/cv/analyze/status : Polling du statut
- GET /api/cv/last-analysis : Derniere analyse completee
- GET /api/cv/models : 4 modeles de CV generes (classique, competences, fonctionnel, mixte)
- Background task: extraction texte → analyse competences IA → generation 4 CV → remplissage passeport

## Composants OPC originaux (GitHub source)
- components/opc/Observatoire.jsx : Page principale avec 4 onglets + param URL ?vue=
- components/opc/views/VueParticulier.jsx, VueRH.jsx, VueConseiller.jsx, VueInstitution.jsx

## Completed
- [x] Deploiement version GitHub (OPC complet avec 4 vues)
- [x] Seed des donnees demo Grand Est
- [x] Module Ubuntoo (messagerie) route /ubuntoo
- [x] Synthese predictive IA (Claude Sonnet 4.5)
- [x] Landing Page pixel-perfect depuis reactif.pro
- [x] Authentification pseudonyme (marc19 + mike7 / Solerys777!)
- [x] Navigation Landing Page : chaque espace mene a sa bonne destination
- [x] Restauration server.py complet (CV analysis, passport, tokens, profiles, coffre-fort)
- [x] Dashboard original restaure avec navigation et vues (ParticulierView avec CV upload)
- [x] AuthProvider avec contexte auth (token, role, loginWithPseudonyme)
- [x] Routes protegees /dashboard/* avec ProtectedRoute

## Source GitHub
https://github.com/Luximon777/reactif-pro

## Prioritized Backlog
### P1
- [ ] Refactoring backend server.py monolithique en modules routes/
### P2
- [ ] Export PDF des CV/passeport (4 modeles)
### P3
- [ ] Modules d'auto-evaluation (Soft Skills CSE, Valeurs VIA)
- [ ] Diagnostic CCSP
- [ ] Ateliers de Codeveloppement
- [ ] Systeme de micro-titres/badges
