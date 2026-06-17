# RE'ACTIF PRO — PRD (Product Requirements Document)

## Problème Original
Développement d'une plateforme full-stack "Ré'Actif Pro" basée sur l'analyse de compétences avec un Observatoire Prédictif des Compétences (OPC) et un Espace Personnel complet.

## Architecture
- **Frontend** : React + Tailwind CSS + Shadcn/UI
- **Backend** : FastAPI + MongoDB (Motor) + GridFS
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

### Phase 8 — Upload de Documents Justificatifs (DONE - 17/06/2026)
**Certification officielle des expériences :**
- `POST /api/passport/experiences/upload-proof` — Upload base64 (PDF/JPG/PNG, max 10 Mo) vers GridFS
- `GET /api/passport/experiences/proof-file/{file_id}` — Téléchargement/consultation du document
- `DELETE /api/passport/experiences/proof-file/{file_id}` — Suppression du document + mise à jour passeport
- Frontend ParticulierView : Bouton "Joindre un document officiel" sous chaque expérience (Trajectoire → Mon CV)
- Frontend ParticulierView : Affichage "Document officiel joint" + badge "Certifié" + boutons Voir/Supprimer
- Frontend PassportView : Badge "Certifié" dans l'ExperienceCard + bloc document avec bouton "Consulter"
- Frontend PassportView : Bouton "Certifier" (upload) pour les expériences non certifiées

**Tests : Backend 13/13 (100%), Frontend 100% (all UI verified)**

## Backlog
- **P1** : Refactoring `server.py` (>5900 lignes) en routeurs dédiés
- **P2** : Export PDF des 4 modèles de CV
- **P3** : Soft Skills (CSE), Valeurs (VIA), diagnostic CCSP, Codéveloppement, micro-titres
