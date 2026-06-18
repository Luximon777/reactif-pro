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

### Phase 3 - D'CLIC PRO v2 (DONE - 19/06/2026)
- Questionnaire complet avec 5 blocs conformes au cahier des charges original:
  - Bloc 1: Archéologie des compétences (10 questions texte libre)
  - Bloc 2: Intérêts professionnels RIASEC (10 items, échelle 1-5)
  - Bloc 3: Valeurs professionnelles (10 items, échelle 1-5)
  - Bloc 4: Savoir-être professionnels (10 items, échelle 1-5)
  - Bloc 5: Projection professionnelle (5 questions mixtes: texte libre + choix)
- Scoring engine: RIASEC code, valeurs dominantes (Schwartz), forces SEP, catégorisation archéologique (5 catégories), projection
- Restitution frontend avec radar RIASEC, carte des valeurs, forces comportementales, archéologie, projection
- Code d'accès unique généré pour chaque passation
- Backend: /app/backend/dclic_routes.py (routes dédiées, prefix /api/dclic)
- Frontend: /app/frontend/src/pages/DclicTestPage.jsx

### Phase 4 - Auto-évaluation (DONE)
- Endpoint POST /api/passport/diagnostic/auto-evaluate

### Phase 5 - Job Matching avancé (DONE - 18/06/2026)
- Bug "Rechercher par scoring" corrigé (POST endpoint créé, format réponse aligné)
- Scoring avancé avec filtres et priorités
- Bouton France Travail avec moteur de recherche par ville/métier/département
- Liens directs vers les pages d'offres France Travail

### Phase 6 - Analyser une offre (DONE - 18/06/2026)
- POST /api/matching/analyze-offer-url : Récupère l'offre via API FT + analyse IA
- POST /api/matching/analyze-offer : Analyse du texte collé manuellement
- POST /api/matching/match-profile : Matching IA profil vs offre
- GET /api/matching/history : Historique des analyses
- Flow frontend 4 étapes : Comprendre → Importer → Analyser → Matching

### Phase 7 - ADN Pro + Candidatures (DONE - 18/06/2026)
- POST /api/profile/identity-adn : Génération ADN Pro dans onglet Inventaire
- POST /api/jobs/apply : Sauvegarder offre dans Mes Candidatures depuis Job Matching

## Issues connues
- (P2) server.py monolithique (~8600 lignes) - refactoring nécessaire
- (P2) DclicTestPage.jsx contient des anciens composants de résultats inutilisés (ProfilComportemental, BoussoleSection, etc.) - nettoyage souhaitable

## Tâches futures (Backlog)
- P1 : Filtrage ROME automatique pour France Travail
- P2 : Refactoring server.py → modules (routes, models)
- P2 : Soft Skills (CSE), Valeurs (VIA)
- P2 : Diagnostic CCSP
- P3 : Ateliers Codéveloppement
- P3 : Micro-titres/badges

## Déploiement
- Frontend : GitHub Actions -> GitHub Pages
- Backend : Emergent infrastructure
- "Save to Github" + "Redeploy" pour production

## Key Endpoints
- GET /api/dclic/questionnaire - Questionnaire D'CLIC PRO (5 blocs, 45 questions)
- POST /api/dclic/submit - Soumission et calcul profil D'CLIC PRO
- GET /api/dclic/results/{code} - Résultats par code d'accès
- GET /api/dclic/my-results?token= - Résultats liés au profil utilisateur
- GET /api/jobs/matching - Matching initial
- POST /api/jobs/matching/search - Scoring avec filtres
- POST /api/jobs/france-travail/search - Offres FT par ville/métier
- POST /api/matching/analyze-offer-url - Analyse URL offre
- POST /api/matching/analyze-offer - Analyse texte offre
- POST /api/matching/match-profile - Matching profil/offre
- GET /api/matching/history - Historique analyses
- POST /api/profile/identity-adn - Génération ADN Pro
- POST /api/jobs/apply - Sauvegarder candidature
