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
- Vue "Le Marché" — 4 onglets personnalisés par IA

### Phase 3 - D'CLIC PRO (DONE)
- Questionnaire complet, scoring IA (MBTI, DISC, RIASEC)

### Phase 4 - Auto-évaluation (DONE)
- Endpoint POST /api/passport/diagnostic/auto-evaluate

### Phase 5 - Job Matching avancé (DONE - 18/06/2026)
- Bug "Rechercher par scoring" corrigé (POST endpoint créé, format réponse aligné)
- Scoring avancé avec filtres et priorités
- Bouton France Travail avec moteur de recherche par ville/métier/département
- Liens directs vers les pages d'offres France Travail

### Phase 6 - Analyser une offre (DONE - 18/06/2026)
- **POST /api/matching/analyze-offer-url** : Récupère l'offre via API FT (par ID) + analyse IA complète (titre, missions, compétences, score qualité)
- **POST /api/matching/analyze-offer** : Analyse du texte collé manuellement
- **POST /api/matching/match-profile** : Matching IA profil vs offre (score global, 4 dimensions, recommandations, message d'accroche)
- **GET /api/matching/history** : Historique des analyses
- Flow frontend 4 étapes : Comprendre → Importer → Analyser → Matching

## Issues connues
- (P1) Images D'CLIC PRO (EN PAUSE)
- (P2) server.py monolithique (~8500 lignes)

## Tâches futures (Backlog)
- P2 : Refactoring server.py → modules
- P2 : Soft Skills (CSE), Valeurs (VIA)
- P2 : Diagnostic CCSP
- P3 : Ateliers Codéveloppement
- P3 : Micro-titres/badges

## Déploiement
- Frontend : GitHub Actions -> GitHub Pages
- Backend : Emergent infrastructure
- "Save to Github" + "Redeploy" pour production

## Key Endpoints
- GET /api/jobs/matching - Matching initial
- POST /api/jobs/matching/search - Scoring avec filtres
- POST /api/jobs/france-travail/search - Offres FT par ville/métier
- POST /api/matching/analyze-offer-url - Analyse URL offre
- POST /api/matching/analyze-offer - Analyse texte offre
- POST /api/matching/match-profile - Matching profil/offre
- GET /api/matching/history - Historique analyses
