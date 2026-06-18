# Ré'Actif Pro - PRD

## Problème original
Plateforme full-stack "Ré'Actif Pro" d'analyse de compétences avec OPC, espace personnel, coach virtuel, Job Matching, portefeuille de compétences et questionnaire D'CLIC PRO.

## Architecture
- Frontend: React + Tailwind + Shadcn/UI (SPA, GitHub Pages)
- Backend: FastAPI + MongoDB (Emergent infrastructure)
- IA: GPT-5.2 via Emergentintegrations (LlmChat) — appels exécutés dans un thread pool via `run_llm_nonblocking()`

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

### Correctifs critiques cette session
- **Event loop blocking** : Les appels LLM bloquaient le serveur FastAPI (tous les endpoints gelés pendant 30-60s). Corrigé avec `run_llm_nonblocking()` qui utilise `asyncio.to_thread()`.
- **NaN dans Observatoire** : Normalisation des données IA (emergence_score, growth_rate)
- **Secteurs génériques** : Analyse IA du profil réel au lieu de secteurs par défaut
- **Endpoint auto-evaluate manquant** : Créé
- **Endpoint marche-cache/diagnostic manquant** : Créé

## Issues connues
- (P1) Images D'CLIC PRO (EN PAUSE)
- (P2) server.py monolithique (>7900 lignes)

## Tâches futures (Backlog)
- P2 : Refactoring server.py
- P2 : Soft Skills (CSE), Valeurs (VIA)
- P2 : Diagnostic CCSP
- P3 : Ateliers Codéveloppement
- P3 : Micro-titres/badges

## Déploiement
- Frontend : GitHub Actions -> GitHub Pages (reactif.pro)
- Backend : Emergent infrastructure (marche-cache.emergent.host)
- "Save to Github" + "Redeploy" pour production
