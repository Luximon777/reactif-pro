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
- Vue "Le Marché" avec 4 onglets TOUS personnalisés par IA :
  - Observatoire : analyse IA croisée profil/marché (secteurs, compétences émergentes, lacunes, déclin)
  - Évolution : score d'exposition enrichi (passport/CV, jobs, formations)
  - Marché caché : diagnostic IA automatique (score d'accès, forces, faiblesses, recommandations, canaux)
  - Explorateur : suggestions de métiers basées sur le profil
- Endpoints :
  - `GET /api/observatoire/personalized` → Analyse IA complète (GPT-5.2)
  - `POST /api/marche-cache/diagnostic` → Diagnostic marché caché IA
  - `GET /api/referentiel/explorer/suggestions` → Métiers suggérés
  - `GET /api/evolution-index/user-profile` → Enrichi passport/CV
  - `POST /api/passport/diagnostic/auto-evaluate` → Auto-évaluation Lamri & Lubart + CCSP

### Phase 3 - D'CLIC PRO (DONE)
- Questionnaire complet avec routes backend
- Scoring IA (MBTI, DISC, RIASEC)
- Frontend `/test-dclic`

### Phase 4 - Auto-évaluation Compétences (DONE)
- Évaluation IA automatique selon Lamri & Lubart et CCSP
- Diagnostic visuel avec radar chart et barres CCSP

## Issues résolues cette session
- NaN dans les scores de l'Observatoire → Normalisation des données IA
- Secteurs génériques au lieu de personnalisés → Analyse IA du profil réel
- Endpoint auto-evaluate manquant (404) → Créé
- Endpoint marche-cache/diagnostic manquant (404) → Créé

## Issues connues
- (P1) Images D'CLIC PRO (EN PAUSE par l'utilisateur)
- (P2) server.py monolithique (>7800 lignes)

## Tâches futures (Backlog)
- P2 : Refactoring server.py en modules routes/
- P2 : Intégrer Soft Skills (CSE) et Valeurs (VIA) 
- P2 : Diagnostic CCSP
- P3 : Ateliers de Codéveloppement
- P3 : Système de micro-titres/badges

## Déploiement
- Frontend : GitHub Actions -> GitHub Pages (reactif.pro)
- Backend : Emergent infrastructure (marche-cache.emergent.host)
- IMPORTANT : "Save to Github" (frontend) + "Redeploy" (backend) pour production
