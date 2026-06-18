# RE'ACTIF PRO — PRD (Product Requirements Document)

## Probleme Original
Developpement d'une plateforme full-stack "Re'Actif Pro" basee sur l'analyse de competences avec un Observatoire Predictif des Competences (OPC) et un Espace Personnel complet.

## Architecture
- **Frontend** : React + Tailwind CSS + Shadcn/UI
- **Backend** : FastAPI + MongoDB (Motor) + GridFS
- **IA** : Claude Sonnet 4.5 / GPT-5.2 via Emergent LLM Key
- **Production** : Frontend sur GitHub Pages (reactif.pro) + Backend Emergent (marche-cache.emergent.host)

## Fonctionnalites Implementees

### Phase 1-5 — Infrastructure + CV + OPC (DONE)
- Page d'accueil, authentification pseudonyme, AdminGate, Dashboard 4 etapes
- Upload CV, analyse IA, passeport competences, frise Trajectoire, Audit CV
- 7 endpoints IA OPC, ETL RNCP (30k certs), Page OPC dediee 8 modules

### Phase 6 — Cartographie exhaustive IA (DONE - 16/06/2026)
- Endpoint cartographie-exhaustive : 35-50+ metiers categorises
- Recommandation personnalisee enrichie (profil complet)

### Phase 7 — Audit fonctionnel Espace Personnel (DONE - 17/06/2026)
- 13 endpoints manquants crees et testes (21/21 tests passes)

### Phase 8 — Upload Documents Justificatifs (DONE - 17/06/2026)
- GridFS MongoDB pour stockage persistant (PDF/JPG/PNG, max 10 Mo)

### Phase 8b — Coach RE'ACTIF Proactif (DONE - 17/06/2026)
- Bandeau "Prochaine etape a realiser" + message contextuel enrichi

### Phase 9 — Job Dating fonctionnel (DONE - 17/06/2026)
- 17 evenements couvrant 14 secteurs avec algorithme de matching intelligent

### Phase 10 — Scraping + Alerte Matching CV (DONE - 17/06/2026)
- Scraping URL France Travail, auto-scraping pour CV, alerte score matching

### Phase 10d — Deploiement GitHub Pages (DONE - 18/06/2026)
- Workflow GitHub Actions avec injection REACT_APP_BACKEND_URL

### Phase 11 — Bug Fix Coach Virtuel Navigation (DONE - 18/06/2026)
- Fix P0: "Mon CV" navigait vers mauvais sous-onglet
- Solution: param ?sub=cv + mapping cote frontend (resilient au backend)
- Fix doublons Coach: bouton non duplique dans la liste si dans banniere

### Phase 12 — D'CLIC PRO Backend Complet (DONE - 18/06/2026)
- **Cree `dclic_routes.py`** avec tout le systeme D'CLIC PRO:
  - `GET /api/dclic/questionnaire` : 22 questions couvrant MBTI, DISC, RIASEC, Enneagramme, Vertus, Valeurs, Style, Stress
  - `POST /api/dclic/submit` : Scoring algorithmique + generation profil IA (GPT-5.2) avec compass, vertu_data, integrated_analysis, life_path, cross_analysis, ofman_quadrant
  - `POST /api/dclic/retrieve` : Recuperation par code d'acces
  - `GET /api/dclic/claim` : Attribution a un utilisateur
  - `POST /api/profile/import-dclic` : Import dans le profil utilisateur + passport
- **Fix routing frontend** : `/test-dclic` ajoute aux routes publiques (accessible sans auth)
- **Corrections supplementaires** : Titre onglet "RE'ACTIF PRO" + suppression badge "Made with Emergent"

## Key Technical Details
- **DB**: test_database (MongoDB)
- **Routes files**: server.py (monolithe), dclic_routes.py, observatory_ia_routes.py, rncp_routes.py
- **D'CLIC scoring**: Algorithme hybride (scores bruts) + IA narrative (GPT-5.2)

## Backlog
- **P1** : Refactoring `server.py` (>7200 lignes) en routeurs dedies sous /app/backend/routes/
- **P2** : Soft Skills (CSE), Valeurs (VIA) via modules d'auto-evaluation
- **P2** : Outil diagnostic fonctionnel CCSP
- **P3** : Ateliers de Codeveloppement, micro-titres/badges
