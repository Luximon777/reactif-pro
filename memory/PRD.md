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
  - Observatoire : données personnalisées auto-chargées (compétences vs marché)
  - Évolution : score d'exposition, métiers liés, formations (enrichi avec passport/CV)
  - Marché caché : diagnostic IA automatique (score, forces, faiblesses, recommandations)
  - Explorateur : suggestions de métiers basées sur le profil
- Endpoint `/api/observatoire/personalized` 
- Endpoint `/api/marche-cache/diagnostic` (POST, IA GPT-5.2)
- Endpoint `/api/referentiel/explorer/suggestions`
- Endpoint `/api/evolution-index/user-profile` (enrichi)

### Phase 3 - D'CLIC PRO (DONE)
- Questionnaire complet avec routes backend
- Scoring IA (MBTI, DISC, RIASEC)
- Frontend accessible via `/test-dclic`

### Autres (DONE)
- Navigation Coach Virtuel ("Mon CV" via `?sub=cv`)
- Suppression badge Emergent + titre index.html
- Routage frontend D'CLIC PRO pour utilisateurs authentifiés

## Issues connues
- (P1) Images D'CLIC PRO : utilisateur veut anciennes photos (EN PAUSE)
- (P2) server.py monolithique (>7400 lignes) : à refactorer en routes distinctes

## Tâches futures (Backlog)
- P2 : Refactoring server.py en modules routes/
- P2 : Intégrer Soft Skills (CSE) et Valeurs (VIA) 
- P2 : Diagnostic CCSP
- P3 : Ateliers de Codéveloppement
- P3 : Système de micro-titres/badges

## Déploiement
- Frontend : GitHub Actions -> GitHub Pages (reactif.pro)
- Backend : Emergent infrastructure (marche-cache.emergent.host)
- IMPORTANT : Utilisateur doit "Save to Github" (frontend) ET "Redeploy" (backend) pour production
