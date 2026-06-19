# Ré'Actif Pro - PRD

## Problème original
Plateforme full-stack "Ré'Actif Pro" d'analyse de compétences avec OPC, espace personnel, coach virtuel, Job Matching, portefeuille de compétences et questionnaire D'CLIC PRO.

## Architecture
- Frontend: React + Tailwind + Shadcn/UI (SPA)
- Backend: FastAPI + MongoDB
- IA: GPT-5.2 via Emergentintegrations (LlmChat)
- API France Travail: OAuth2 client_credentials (ROME 4.0 + Offres d'emploi v2)

## D'CLIC PRO — Version GitHub intégrale (19/06/2026)

### Questionnaire Visuel (26 questions, 8 blocs)
- **Bloc 1** : Énergie E/I (2q visuelles)
- **Bloc 2** : Perception S/N (1q visuelle + 1q ranking)
- **Bloc 3** : Décision T/F (2q visuelles)
- **Bloc 4** : Organisation J/P (2q visuelles)
- **Bloc 5** : Style DISC (2q ranking)
- **Bloc 6** : Motivation Ennéagramme (2q ranking)
- **Bloc 7** : Intérêts RIASEC (5q visuelles + 3q ranking)
- **Bloc 8** : Vertus & Valeurs (3q visuelles + 2q ranking + 1q visuelle)

### Scoring déterministe
- MBTI (4 axes croisés) + DISC (4 scores) + Ennéagramme (9 types) + RIASEC (6 dimensions) + Vertus Seligman&Peterson (6 vertus)
- Croisement Ennéagramme × Vertus pour vertu dominante enrichie

### Restitution
- Narrative IA (GPT-5.2) : portrait, fonctionnement, forces/vigilance, conseil
- Référentiel scientifique injecté (6 Vertus → Forces → Valeurs → Qualités → CPS OMS → Compétences transférables → Métiers → Citations → Penseurs)
- Zones de vigilance, Compas de fonctionnement, Analyse intégrée
- Cadran d'Ofman (3 quadrants), Pistes de vie professionnelle
- 10 sections navigables dans la sidebar (Archéologie, Comportemental, Boussole, RIASEC, Vertus, Intégré, Ofman, Pistes, Croisé, Carte d'identité)

### Modules backend
- `/app/backend/dclic_data.py` (3664 lignes) — Questions visuelles, legacy, VERTUS, FILIERES, METIERS, ENNEA, RIASEC, LIFE_PATHS
- `/app/backend/dclic_scoring.py` (2116 lignes) — Moteur de scoring complet (compute_profile, vertus, riasec, ofman, etc.)
- `/app/backend/dclic_referentiel.py` — Référentiel scientifique enrichi + citations
- `/app/backend/dclic_routes.py` — Routes API (/questionnaire/visual, /submit, /job-match, /explore, /results, /filieres, /metiers, /vertus)

## Fonctionnalités implémentées

### Phase 1 - Core (DONE)
- Auth JWT, GPS Dashboard, Analyse CV, Coach Virtuel, Portefeuille, Job Dating/Matching

### Phase 2 - OPC (DONE)
- Observatoire autonome, Vue "Le Marché" (4 onglets personnalisés par IA)

### Phase 3 - D'CLIC PRO v3 GitHub (DONE - 19/06/2026)
- Questionnaire visuel 26 questions / 8 blocs (remplace l'ancien 45 questions)
- Scoring MBTI+DISC+Ennéagramme+RIASEC+Vertus croisé
- Narrative IA + Référentiel scientifique (Seligman & Peterson)
- Job matching avec FILIERES et METIERS (54 métiers + scoring)
- Exploration de carrières

### Phase 3b - Import D'CLIC PRO "Booster mon profil" (DONE - 19/06/2026)
- Flow complet : test → code d'accès → Dashboard → aperçu → import → profil mis à jour
- Endpoints : /api/dclic/retrieve, /api/dclic/claim, /api/profile/import-dclic
- Dashboard : bouton "Boost mon profil" (violet pulsant) → dialog → preview MBTI/DISC/Vertu/RIASEC/Ennéagramme → import avec barre de progression → toast succès
- Après import : bouton passe en vert "Profil boosté", flag dclic_imported=true dans profiles
- Fusion intelligente des compétences dans le passport (merge sans doublons)
- Test complet validé à 100% (backend 17/17 + frontend OK)

### Phase 4-7 (DONE) — Auto-évaluation, Matching avancé, Analyse offre, ADN Pro

## Key Endpoints
- GET /api/dclic/questionnaire/visual — 26 questions visuelles
- GET /api/dclic/questionnaire — 15 questions legacy
- POST /api/dclic/submit — Scoring + narrative IA → profil complet
- POST /api/dclic/job-match — Matching métiers
- POST /api/dclic/explore — Exploration de carrières
- GET /api/dclic/results/{code} — Résultats par code
- POST /api/dclic/retrieve — Récupérer profil via code (pour Dashboard)
- POST /api/dclic/claim — Marquer un code comme utilisé
- POST /api/profile/import-dclic — Importer les résultats D'CLIC dans le passport
- GET /api/dclic/my-results — Résultats D'CLIC de l'utilisateur connecté
- GET /api/dclic/filieres, /api/dclic/metiers, /api/dclic/vertus

## Tâches futures (Backlog)
- P1 : Filtrage ROME automatique France Travail
- P2 : Refactoring server.py → modules (~8800 lignes)
- P2 : Modules Soft Skills (CSE), Valeurs (VIA) indépendants
- P2 : Diagnostic CCSP
- P3 : Ateliers Codéveloppement
- P3 : Micro-titres/badges
