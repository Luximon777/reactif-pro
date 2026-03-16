# Ré'Actif Pro - Product Requirements Document

## Core Concept: Archéologie des Compétences
Métiers -> Savoir-faire (Hard Skills) -> Savoir-être (Soft Skills) -> Qualités humaines -> Valeurs universelles -> Vertus

## Completed Features
- [x] Authentification anonyme (JWT)
- [x] 3 dashboards par rôle (Particulier, RH, Partenaire)
- [x] Coffre-Fort Numérique
- [x] Observatoire Prédictif + Indice d'Évolution
- [x] Croisement Ubuntoo x Observatoire
- [x] Passeport Dynamique (8 onglets)
- [x] Modèle Lamri & Lubart (5 composantes)
- [x] Référentiel CCSP (3 pôles + 3 degrés)
- [x] Distinction Savoir-faire / Savoir-être / Transversale / Transférable
- [x] Archéologie des Compétences (6 Vertus, 11 Valeurs, 14 Filières)
- [x] **Analyse IA de CV** - Upload + 4 modèles CV (Classique, Fonctionnel, Compétences, Mixte)
- [x] **Détection IA automatique** - Savoir-faire, savoir-être, compétences transversales
- [x] **Suggestions de formations** - Besoins identifiés par l'IA
- [x] **Auto-remplissage Passeport** - Depuis CV
- [x] **Logo SVG vectoriel** - Composant CSS/SVG net (16 mars 2026)
- [x] **Minuteur de progression CV** - Timer avec 12 étapes animées (16 mars 2026)
- [x] **Background processing CV** - Pattern job_id + polling pour éviter timeout proxy 60s (16 mars 2026)
  - POST /api/cv/analyze retourne immédiatement un job_id
  - GET /api/cv/analyze/status?job_id=xxx pour polling toutes les 3s
  - 2 appels IA séparés (analyse + génération CV) avec retry
  - Gestion d'erreurs robuste frontend + backend

## Key API Endpoints
- `/api/cv/analyze` (POST) - Lance l'analyse en background, retourne job_id
- `/api/cv/analyze/status` (GET) - Poll status du job (started/analyzing/completed/failed)
- `/api/cv/models` (GET) - 4 modèles de CV générés
- `/api/passport/*` - Passeport Dynamique complet
- `/api/referentiel/*` - Archéologie des compétences

## Architecture
- Backend: FastAPI (server.py ~3600+ lignes) + asyncio background tasks
- Frontend: React + Tailwind CSS + Shadcn/UI
- Database: MongoDB (cv_jobs collection pour le suivi des analyses)
- AI: OpenAI GPT-5.2 via Emergent LLM Key (2 appels séparés: analyse + CV)
- Logo: Composant SVG/CSS (LogoReactifPro.jsx)

## Prioritized Backlog
### P0 (Next)
- [ ] Refactoring backend (server.py -> routes modulaires)
- [ ] Refactoring frontend (sous-composants)

### P1
- [ ] Génération PDF des 4 modèles de CV
- [ ] Quiz d'orientation basé sur l'archéologie
- [ ] Ateliers de Codéveloppement
- [ ] Système de micro-titres/badges

### P2
- [ ] Intégration approfondie CCSP (outil de diagnostic)
- [ ] Soft Skills (CSE) et Valeurs (VIA) via auto-évaluation
- [ ] Export PDF du passeport, mode sombre
