# Ré'Actif Pro - PRD

## Problème original
Plateforme full-stack "Ré'Actif Pro" d'analyse de compétences avec OPC, espace personnel, coach virtuel, Job Matching, portefeuille de compétences et questionnaire D'CLIC PRO.

## Architecture
- Frontend: React + Tailwind + Shadcn/UI (SPA, GitHub Pages)
- Backend: FastAPI + MongoDB (Emergent infrastructure)
- IA: GPT-5.2 via Emergentintegrations (LlmChat) — appels exécutés dans un thread pool via `run_llm_nonblocking()`
- API France Travail: OAuth2 client_credentials (ROME 4.0 + Offres d'emploi v2)

## Fonctionnalités implémentées

### Phase 1 - Core (DONE)
- Authentification JWT
- GPS Dashboard + analyse de CV
- Coach Virtuel interactif
- Portefeuille de compétences
- Job Dating / Job Matching

### Phase 2 - Observatoire et Marché (DONE)
- OPC autonome
- Vue "Le Marché" — 4 onglets TOUS personnalisés par IA :
  - Observatoire : analyse IA profil/marché (GPT-5.2)
  - Évolution : score d'exposition, métiers liés, formations (enrichi passport/CV)
  - Marché caché : diagnostic IA automatique (GPT-5.2)
  - Explorateur : suggestions de métiers personnalisées

### Phase 3 - D'CLIC PRO (DONE)
- Questionnaire complet, scoring IA (MBTI, DISC, RIASEC)

### Phase 4 - Auto-évaluation (DONE)
- Endpoint POST /api/passport/diagnostic/auto-evaluate
- Évaluation IA Lamri & Lubart + CCSP

### Phase 5 - Job Matching avancé (DONE - 18/06/2026)
- **Bug corrigé** : "Rechercher par scoring" ne fonctionnait pas (POST vers un GET endpoint, format de réponse incompatible)
- **GET /api/jobs/matching** : Retourne le format correct `{has_data, has_filters, profile_summary, matches}`
- **POST /api/jobs/matching/search** : Scoring avancé basé sur les filtres avec priorités (métier, secteur, contrat, localisation, salaire, télétravail, restrictions RQTH/EQTH)
- **POST /api/jobs/france-travail/search** : Recherche d'offres France Travail en temps réel via API Offres d'emploi v2 + fallback base interne
- **GET /api/jobs/matching/preferences** : Format correct `{has_preferences, filters}`
- **Bouton France Travail** dans JobMatchingSection avec saisie département
- **Fixes testing agent** : gestion Array.isArray() pour filtres sauvegardés, loadApplications() format response

### Correctifs critiques sessions précédentes
- **Event loop blocking** : `run_llm_nonblocking()` avec `asyncio.to_thread()`
- **NaN dans Observatoire** : Normalisation données IA
- **Secteurs génériques** : Analyse IA du profil réel
- **Endpoints manquants** : auto-evaluate, marche-cache/diagnostic

## Issues connues
- (P1) Images D'CLIC PRO (EN PAUSE - attente demande utilisateur)
- (P2) server.py monolithique (~8200 lignes)

## Tâches futures (Backlog)
- P2 : Refactoring server.py → modules dans /app/backend/routes/
- P2 : Soft Skills (CSE), Valeurs (VIA)
- P2 : Diagnostic CCSP
- P3 : Ateliers Codéveloppement
- P3 : Micro-titres/badges

## Déploiement
- Frontend : GitHub Actions -> GitHub Pages (reactif.pro)
- Backend : Emergent infrastructure
- "Save to Github" + "Redeploy" pour production

## Key Endpoints - Job Matching
- GET /api/jobs/matching - Matching initial basé sur profil
- POST /api/jobs/matching/search - Scoring avancé avec filtres
- GET /api/jobs/matching/preferences - Préférences sauvegardées
- POST /api/jobs/france-travail/search - Offres France Travail
