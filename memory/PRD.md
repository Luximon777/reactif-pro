# RE'ACTIF PRO — PRD (Product Requirements Document)

## Probleme Original
Developpement d'une plateforme full-stack "Re'Actif Pro" basee sur l'analyse de competences avec un Observatoire Predictif des Competences (OPC) et un Espace Personnel complet.

## Architecture
- **Frontend** : React + Tailwind CSS + Shadcn/UI
- **Backend** : FastAPI + MongoDB (Motor) + GridFS
- **IA** : Claude Sonnet 4.5 / GPT-5.2 via Emergent LLM Key
- **Production** : Frontend sur GitHub Pages (reactif.pro) + Backend Emergent (marche-cache.emergent.host)

## Fonctionnalites Implementees

### Phase 1-10 (sessions precedentes - DONE)
- Infrastructure, CV, OPC, Cartographie IA, Audit, Upload Documents, Coach RE'ACTIF, Job Dating, Scraping, Deploiement GitHub Pages

### Phase 11 — Bug Fix Coach Virtuel Navigation (DONE - 18/06/2026)
- Fix: "Mon CV" navigue vers bon sous-onglet via ?sub=cv + mapping frontend resilient
- Fix doublons Coach

### Phase 12 — D'CLIC PRO Backend Complet (DONE - 18/06/2026)
- Cree dclic_routes.py: questionnaire 22 questions (MBTI/DISC/RIASEC/Enneagramme/Vertus/Valeurs)
- Images illustratives sur 14 questions (photos Pexels/Unsplash pour choix)
- Scoring algorithmique + profil IA (GPT-5.2)
- 5 endpoints: questionnaire, submit, retrieve, claim, import-dclic
- Fix routing: /test-dclic accessible sans auth

### Phase 13 — Corrections UI (DONE - 18/06/2026)
- Titre onglet: "RE'ACTIF PRO | Intelligence Professionnelle"
- Badge "Made with Emergent" supprime

### Phase 14 — Predictions IA Observatoire (DONE - 18/06/2026)
- Cree endpoint GET /api/observatoire/personalized
- Croisement profil utilisateur × donnees observatoire (emerging_skills + sector_trends)
- Matching competences emergentes, identification lacunes prioritaires, secteurs pertinents
- Deduplication des resultats
- Champs compatibles frontend: observatory_skill, emergence_score, growth_rate, sector, hiring_trend, your_emerging_skills

## Key Technical Details
- **DB**: test_database (MongoDB)
- **Collections cles**: profiles, passports, cv_jobs, coach_progress, dclic_results, emerging_skills, sector_trends
- **Routes files**: server.py (monolithe ~7300 lignes), dclic_routes.py, observatory_ia_routes.py, rncp_routes.py

## Backlog
- **P1** : Refactoring server.py en routeurs dedies sous /app/backend/routes/
- **P2** : Soft Skills (CSE), Valeurs (VIA) via modules d'auto-evaluation
- **P2** : Outil diagnostic fonctionnel CCSP
- **P3** : Ateliers de Codeveloppement, micro-titres/badges
