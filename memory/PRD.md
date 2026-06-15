# RE'ACTIF PRO - Product Requirements Document

## Core Concept
Plateforme d'intelligence professionnelle — Observatoire Predictif des Competences (OPC).
Infrastructure d'intelligence territoriale : Anticiper les competences, piloter l'emploi.
Page d'accueil avec 5 acces distincts, systeme d'analyse CV par IA, authentification par pseudonyme.

## Architecture
- **Backend** : FastAPI (server.py + opc/ + ubuntoo_routes.py)
- **Frontend** : React + Tailwind + Shadcn/UI + react-router-dom
- **DB** : MongoDB (users, passport_competences, reactif_contacts, opc_*)
- **IA** : OpenAI GPT-5.2 via emergentintegrations (Emergent LLM Key)

## Routes Frontend
- `/` : LandingPage (page d'accueil avec 5 acces)
- `/observatoire` : OPC - Observatoire Predictif des Competences
- `/ubuntoo` : Application messagerie / Parcours VSI
- `/espace-personnel` : Espace Personnel (post-login marc19)
- `/reactif` : Page institutionnelle ReactifLanding
- `/reactif/accueil` : ReactifHome (hub du dispositif)
- `/reactif/particuliers` : Page Particuliers
- `/reactif/services-rh` : Page Services RH / Espace Employeurs
- `/reactif/partenaires` : Page Partenaires / Appui aux parcours

## 5 Acces Landing Page
1. **Espace Personnel** -> Modale login (marc19/Solerys777!) -> /espace-personnel
2. **Parcours VSI** -> /ubuntoo
3. **OPC** (cercle central) -> /observatoire
4. **Espace Employeurs** -> /reactif/services-rh
5. **Appui aux parcours** -> /reactif/partenaires

## Key API Endpoints
- `POST /api/auth/login` : Login pseudonyme + password
- `POST /api/auth/register` : Register pseudonyme + password
- `GET /api/reactif/impact` : Stats d'impact
- `POST /api/reactif/contact` : Formulaire de contact
- `POST /api/cv/extract-text-b64` : Upload CV en base64
- `POST /api/cv/analyze-text` : Analyse CV par IA
- `GET /api/cv/last-analysis` : Derniere analyse CV

## Modules OPC Backend
- `opc/routes_vues.py` : 4 vues publics (Particulier, RH, Conseiller, Institution)
- `opc/routes_ingestion.py` : Ingestion de donnees
- `opc/routes_ia.py` : Synthese predictive IA
- `opc/routes_admin.py` : Administration (France Travail sync)
- `opc/referentiel_metiers.py` : Referentiel statique (284 metiers, 20 filieres)
- `opc/seed.py` : Donnees demo Grand Est

## Completed
- [x] Deploiement version GitHub (OPC complet)
- [x] Seed des donnees demo Grand Est
- [x] 4 vues operationnelles OPC (Conseillers, Particulier, RH, Institutions)
- [x] Module Ubuntoo (messagerie) route /ubuntoo
- [x] Synthese predictive IA (Claude Sonnet 4.5)
- [x] Fiche metier avec fallback IA Claude
- [x] Upload CV + analyse IA (base64, polling, auto-remplissage passeport)
- [x] Landing Page pixel-perfect depuis reactif.pro
- [x] Authentification pseudonyme (marc19/Solerys777!)
- [x] Correction navigation Landing Page (5 acces vers bonnes destinations)
- [x] Routes ReactifPro ajoutees (services-rh, partenaires, accueil, etc.)
- [x] Routes backend /api/reactif/contact et /api/reactif/impact
- [x] Fix UbuntooApp API URL (reactif.pro -> REACT_APP_BACKEND_URL)

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
