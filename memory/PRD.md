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
- 13 endpoints manquants créés et testés (21/21 tests passés)
- Passport sync, Audit CV normalisation, centres d'intérêt, route wildcard fix

### Phase 8 — Upload Documents Justificatifs (DONE - 17/06/2026)
- POST/GET/DELETE /api/passport/experiences/(upload-proof|proof-file/{id})
- GridFS MongoDB pour stockage persistant (PDF/JPG/PNG, max 10 Mo)
- Frontend: upload + badge Certifié dans ParticulierView et PassportView
- Tests: Backend 13/13 + Frontend 100%

### Phase 8b — Coach RE'ACTIF Proactif (DONE - 17/06/2026)
**Bugs corrigés :**
- current_step calculait incorrectement (sautait à step 4 si complété avant step 2)
- Compteurs savoir-faire/savoir-être à 0 (ne consultait pas le passport)
- Pas de guidance proactive vers la prochaine étape

**Améliorations :**
- Bandeau "Prochaine étape à réaliser" dans le Coach (StepsView) avec bouton action
- Message contextuel avec résumé du profil + prochaine étape explicite
- Endpoint /coach/chat enrichi : consulte passport + cv_jobs + profile pour contexte complet
- Actions cliquables dans le chat menant à la bonne section

## Backlog
- **P1** : Refactoring `server.py` (>6000 lignes) en routeurs dédiés
- **P2** : Export PDF des 4 modèles de CV
- **P3** : Soft Skills (CSE), Valeurs (VIA), diagnostic CCSP, Codéveloppement, micro-titres
