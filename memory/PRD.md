# Ré'Actif Pro - PRD

## Problème original
Plateforme full-stack "Ré'Actif Pro" d'analyse de compétences avec OPC, espace personnel, coach virtuel, Job Matching, portefeuille de compétences et questionnaire D'CLIC PRO.

## Architecture
- Frontend: React + Tailwind + Shadcn/UI (SPA)
- Backend: FastAPI + MongoDB
- IA: GPT-5.2 via Emergentintegrations (LlmChat) — appels exécutés via `asyncio.to_thread`
- API France Travail: OAuth2 client_credentials (ROME 4.0 + Offres d'emploi v2)

## Fonctionnalités implémentées

### Phase 1 - Core (DONE)
- Authentification JWT, GPS Dashboard, analyse de CV, Coach Virtuel, Portefeuille de compétences, Job Dating/Matching

### Phase 2 - Observatoire et Marché (DONE)
- OPC autonome, Vue "Le Marché" (4 onglets personnalisés par IA)

### Phase 3 - D'CLIC PRO v2 avec Restitution IA Riche (DONE - 19/06/2026)
- **Questionnaire** : 45 questions / 5 blocs (Archéologie 10q texte, RIASEC 10q échelle, Valeurs 10q échelle, Savoir-être 10q échelle, Projection 5q mixtes)
- **Scoring déterministe** : RIASEC code, valeurs Schwartz, forces savoir-être, catégorisation archéologique (5 catégories)
- **Analyse IA enrichie (GPT-5.2)** : Génère MBTI, DISC, Boussole de Fonctionnement (4 axes), Profil de Vertus (6 vertus Seligman&Peterson), Generic Skills Approach (Cognition/Conation/Affection), RIASEC enrichi (traits, environnements), Analyse intégrée (3 niveaux), Analyse croisée, Cadran d'Ofman (3 quadrants: qualité→piège→défi→allergie), Pistes d'action
- **Restitution graphique** : 10 sections navigables via sidebar (Archéologie, Profil Comportemental avec radars, Boussole MBTI, Analyse Intégrée, RIASEC, Vertus, Pistes, Analyse Croisée, Cadran d'Ofman, Carte d'Identité Pro avec QR code)
- **Fallback** : Si l'IA échoue, profil enrichi déterministe de secours
- Backend: `/app/backend/dclic_routes.py` | Frontend: `/app/frontend/src/pages/DclicTestPage.jsx`

### Phase 4 - Auto-évaluation (DONE)
- POST /api/passport/diagnostic/auto-evaluate

### Phase 5 - Job Matching avancé (DONE)
- Scoring avancé, France Travail par ville/métier, liens directs offres

### Phase 6 - Analyser une offre (DONE)
- Analyse URL, texte collé, matching IA profil/offre, historique

### Phase 7 - ADN Pro + Candidatures (DONE)
- Génération ADN Pro, sauvegarde candidatures depuis Job Matching

## Tâches futures (Backlog)
- P1 : Filtrage ROME automatique pour France Travail
- P2 : Refactoring server.py → modules (routes, models)
- P2 : Soft Skills (CSE), Valeurs (VIA)
- P2 : Diagnostic CCSP
- P3 : Ateliers Codéveloppement
- P3 : Micro-titres/badges

## Key Endpoints
- GET /api/dclic/questionnaire — 5 blocs, 45 questions
- POST /api/dclic/submit — Scoring + analyse IA → profil riche (MBTI, DISC, Ofman, etc.)
- GET /api/dclic/results/{code} — Résultats par code d'accès
- GET /api/dclic/my-results?token= — Résultats liés au profil utilisateur
- POST /api/jobs/matching/search, POST /api/jobs/france-travail/search
- POST /api/matching/analyze-offer-url, POST /api/matching/match-profile
- POST /api/profile/identity-adn, POST /api/jobs/apply
