# Ré'Actif Pro - Product Requirements Document

## Core Concept: Archéologie des Compétences
Métiers -> Savoir-faire (Hard Skills) -> Savoir-être (Soft Skills) -> Qualités humaines -> Valeurs universelles -> Vertus

## Completed Features
- [x] Authentification anonyme (JWT)
- [x] 3 dashboards par rôle (Particulier, RH, Partenaire)
- [x] Coffre-Fort Numérique
- [x] Observatoire Prédictif + Indice d'Évolution
- [x] Croisement Ubuntoo x Observatoire
- [x] Passeport Dynamique (8 onglets: Profil, Compétences, Évaluation, Archéologie, Émergentes, Expériences, Parcours, Passerelles)
- [x] Modèle Lamri & Lubart (5 composantes)
- [x] Référentiel CCSP (3 pôles + 3 degrés)
- [x] Distinction Savoir-faire / Savoir-être
- [x] Distinction Transversale / Transférable (France Travail)
- [x] Archéologie des Compétences (6 Vertus, 11 Valeurs, 14 Filières)
- [x] **Analyse IA de CV** - Upload CV -> 4 modèles générés (Classique, Fonctionnel, Compétences, Mixte)
- [x] **Détection IA automatique** - Savoir-faire, savoir-être, compétences transversales
- [x] **Suggestions de formations** - Besoins identifiés par l'IA avec priorités
- [x] **Auto-remplissage Passeport** - Profil, compétences, expériences, formations complétés depuis le CV
- [x] **Logo SVG vectoriel** - Remplacement du PNG flou par un composant SVG/CSS net (16 mars 2026)
- [x] **Minuteur de progression CV** - Timer avec 12 étapes animées pendant l'analyse IA (16 mars 2026)

## Key API Endpoints
- `/api/cv/analyze` (POST) - Upload + analyse IA complète du CV
- `/api/cv/models` (GET) - 4 modèles de CV générés
- `/api/passport/*` - Passeport Dynamique complet
- `/api/referentiel/*` - Archéologie des compétences

## Architecture
- Backend: FastAPI (server.py monolithique ~3600+ lignes)
- Frontend: React + Tailwind CSS + Shadcn/UI
- Database: MongoDB
- AI: OpenAI GPT via Emergent LLM Key
- Logo: Composant SVG/CSS (`/app/frontend/src/components/LogoReactifPro.jsx`)

## Prioritized Backlog
### P0 (Next)
- [ ] Refactoring backend (server.py 3600+ lignes -> routes modulaires)
- [ ] Refactoring frontend (ParticulierView.jsx, PassportView.jsx -> sous-composants)

### P1
- [ ] Génération PDF des 4 modèles de CV
- [ ] Quiz d'orientation basé sur l'archéologie
- [ ] Ateliers de Codéveloppement
- [ ] Système de micro-titres/badges

### P2
- [ ] Intégration approfondie CCSP (outil de diagnostic)
- [ ] Intégrer Soft Skills (CSE) et Valeurs (VIA) via auto-évaluation
- [ ] Export PDF du passeport, admin Ubuntoo, notifications, mode sombre
