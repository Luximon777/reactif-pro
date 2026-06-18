# Ré'Actif Pro - PRD

## Problème original
Plateforme full-stack "Ré'Actif Pro" d'analyse de compétences avec OPC, espace personnel, coach virtuel, Job Matching, portefeuille de compétences et questionnaire D'CLIC PRO.

## Architecture
- Frontend: React + Tailwind + Shadcn/UI (SPA, GitHub Pages)
- Backend: FastAPI + MongoDB (Emergent infrastructure)
- IA: GPT-5.2 via Emergentintegrations (LlmChat)

## Fonctionnalités implémentées

### Phase 1 - Core (DONE)
- Authentification JWT (login/register)
- GPS Dashboard avec analyse de CV
- Coach Virtuel interactif
- Portefeuille de compétences
- Job Dating / Job Matching

### Phase 2 - Observatoire et Marché (DONE)
- OPC (Observatoire Prédictif des Compétences) autonome
- Vue "Le Marché" avec 4 onglets personnalisés :
  - Observatoire : données personnalisées auto-chargées
  - Évolution : score d'exposition enrichi (passport/CV)
  - Marché caché : diagnostic IA automatique (GPT-5.2)
  - Explorateur : suggestions de métiers personnalisées
- Endpoints : `/api/observatoire/personalized`, `/api/marche-cache/diagnostic`, `/api/referentiel/explorer/suggestions`, `/api/evolution-index/user-profile`

### Phase 3 - D'CLIC PRO (DONE)
- Questionnaire complet avec routes backend
- Scoring IA (MBTI, DISC, RIASEC)
- Frontend `/test-dclic`

### Phase 4 - Auto-évaluation Compétences (DONE)
- Endpoint `POST /api/passport/diagnostic/auto-evaluate` créé
- Évaluation IA automatique selon Lamri & Lubart (5 composantes) et CCSP (pôles + degrés)
- Classification nature (savoir-faire / savoir-être)
- Diagnostic visuel avec radar chart et barres CCSP

### Autres (DONE)
- Navigation Coach Virtuel ("Mon CV" via `?sub=cv`)
- Suppression badge Emergent + titre index.html

## Issues connues
- (P1) Images D'CLIC PRO (EN PAUSE par l'utilisateur)
- (P2) server.py monolithique (>7600 lignes)

## Tâches futures (Backlog)
- P2 : Refactoring server.py en modules routes/
- P2 : Intégrer Soft Skills (CSE) et Valeurs (VIA) 
- P2 : Diagnostic CCSP
- P3 : Ateliers de Codéveloppement
- P3 : Système de micro-titres/badges

## Déploiement
- Frontend : GitHub Actions -> GitHub Pages (reactif.pro)
- Backend : Emergent infrastructure
- IMPORTANT : "Save to Github" (frontend) + "Redeploy" (backend) pour production
