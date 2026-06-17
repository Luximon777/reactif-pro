# RE'ACTIF PRO — PRD (Product Requirements Document)

## Problème Original
Développement d'une plateforme full-stack "Ré'Actif Pro" basée sur l'analyse de compétences avec un Observatoire Prédictif des Compétences (OPC) et un Espace Personnel complet.

## Architecture
- **Frontend** : React + Tailwind CSS + Shadcn/UI
- **Backend** : FastAPI + MongoDB (Motor)
- **IA** : Claude Sonnet 4.5 / GPT-5.2 via Emergent LLM Key

## Fonctionnalités Implémentées

### Phase 1-5 — Infrastructure + CV + OPC (DONE)
- Page d'accueil, authentification pseudonyme, AdminGate, Dashboard 4 étapes
- Upload CV, analyse IA, passeport compétences, frise Trajectoire, Audit CV
- 7 endpoints IA OPC, ETL RNCP (30k certs), Page OPC dédiée 8 modules

### Phase 6 — Cartographie exhaustive IA (DONE - 16/06/2026)
- Endpoint cartographie-exhaustive : 35-50+ métiers catégorisés
- Recommandation personnalisée enrichie (profil complet)
- Synchronisation profil OPC, bouton Actualiser Dashboard

### Phase 7 — Audit fonctionnel Espace Personnel (DONE - 17/06/2026)
**13 endpoints manquants créés :**
1. `POST /coach/step-chat` — Chat interactif IA avec le Coach RE'ACTIF (GPT-5.2)
2. `POST /cv/generate-models` + `GET /status` — Génération de CV optimisés par IA (background job)
3. `GET /coffre/cv-files` + `POST /coffre/transfer-cv` — Gestion fichiers CV dans le coffre-fort
4. `GET /jobs/matching` — Job matching personnalisé avec scores
5. `GET /jobs/matching/preferences` + `POST` — Préférences de matching
6. `GET /jobs/matching/search` — Recherche d'offres filtrée
7. `POST /jobs/apply` + `GET /jobs/applications` — Candidatures
8. `POST /notifications/mark-read` + `mark-all-read` — Gestion notifications
9. `GET /emerging/market-correlation` — Corrélation compétences/marché
10. `GET /learning/recommendations` — Recommandations formation personnalisées

**Bug fixes :**
- Passport sync : savoir_faire (15) + savoir_etre (6) depuis analyse CV
- Audit CV : normalisation noms de champs (rule→regle, status→statut)
- Centres d'intérêt : affichage en mode audit
- Route wildcard conflict : /jobs/matching AVANT /jobs/{job_id}

**Tests : 21/21 passés (100%)**

## Backlog
- **P1** : Refactoring `server.py` (>5600 lignes)
- **P2** : Export PDF des 4 modèles de CV
- **P3** : Soft Skills (CSE), Valeurs (VIA), diagnostic CCSP, Codéveloppement, micro-titres
