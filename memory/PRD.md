# RE'ACTIF PRO — PRD (Product Requirements Document)

## Probleme Original
Developpement d'une plateforme full-stack "Re'Actif Pro" basee sur l'analyse de competences avec un Observatoire Predictif des Competences (OPC) et un Espace Personnel complet.

## Architecture
- **Frontend** : React + Tailwind CSS + Shadcn/UI
- **Backend** : FastAPI + MongoDB (Motor) + GridFS
- **IA** : Claude Sonnet 4.5 / GPT-5.2 via Emergent LLM Key

## Fonctionnalites Implementees

### Phase 1-5 — Infrastructure + CV + OPC (DONE)
- Page d'accueil, authentification pseudonyme, AdminGate, Dashboard 4 etapes
- Upload CV, analyse IA, passeport competences, frise Trajectoire, Audit CV
- 7 endpoints IA OPC, ETL RNCP (30k certs), Page OPC dediee 8 modules

### Phase 6 — Cartographie exhaustive IA (DONE - 16/06/2026)
- Endpoint cartographie-exhaustive : 35-50+ metiers categorises
- Recommandation personnalisee enrichie (profil complet)
- Synchronisation profil OPC, bouton Actualiser Dashboard

### Phase 7 — Audit fonctionnel Espace Personnel (DONE - 17/06/2026)
- 13 endpoints manquants crees et testes (21/21 tests passes)
- Passport sync, Audit CV normalisation, centres d'interet, route wildcard fix

### Phase 8 — Upload Documents Justificatifs (DONE - 17/06/2026)
- POST/GET/DELETE /api/passport/experiences/(upload-proof|proof-file/{id})
- GridFS MongoDB pour stockage persistant (PDF/JPG/PNG, max 10 Mo)
- Frontend: upload + badge Certifie dans ParticulierView et PassportView
- Tests: Backend 13/13 + Frontend 100%

### Phase 8b — Coach RE'ACTIF Proactif (DONE - 17/06/2026)
- current_step corrige, compteurs savoir-faire/savoir-etre fixes
- Bandeau "Prochaine etape a realiser" + message contextuel enrichi
- Endpoint /coach/chat enrichi avec passport + cv_jobs + profile

### Phase 9 — Job Dating fonctionnel (DONE - 17/06/2026)
- 17 evenements couvrant 14 secteurs avec IDs stables (evt-*)
- Algorithme de matching intelligent : inference de secteurs depuis experiences et competences
- 3 niveaux de scoring : secteur (+40), experience (+15/match), competences (+5/match)
- AI summary personnalise avec secteurs detectes et competences
- Endpoints complets : events, recommended, sectors, save/unsave, register, history, evaluate
- Backend 13/13 tests passes + Frontend 100%

## Key Technical Details
- **DB**: test_database (MongoDB)
- **Matching**: _infer_sectors_from_profile() detecte les secteurs via keywords mapping
- **Events**: Generes dynamiquement avec _generate_job_dating_events()
- **IDs**: Stables (evt-it-paris, evt-resto-bordeaux, etc.)

### Phase 10 — Correction Job Matching Frontend (DONE - 17/06/2026)
- Fix P0: Carte "Job Matching" affichait 0 car le dashboard appelait `/api/jobs` (scores generiques=25) au lieu de `/api/jobs/matching` (scores personnalises)
- Correction dans `ParticulierView.jsx`: appel vers `/api/jobs/matching` + parsing format `{jobs:[...]}`
- Resultat: 3 offres compatibles (scores >= 60%) correctement affichees sur Trajectoire et Accueil

## Backlog
- **P1** : Refactoring `server.py` (>6900 lignes) en routeurs dedies sous /app/backend/routes/
- **P2** : Soft Skills (CSE), Valeurs (VIA) via modules d'auto-evaluation
- **P2** : Outil diagnostic CCSP
- **P3** : Ateliers de Codeveloppement, micro-titres/badges
