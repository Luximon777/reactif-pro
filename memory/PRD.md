# Ré'Actif Pro - Product Requirements Document

## Original Problem Statement
Plateforme Ré'Actif Pro - plateforme de développement de carrière fondée sur des principes philosophiques (axiologie, phénoménologie) et des modèles de compétences avancés. 3 types d'utilisateurs (Particuliers, Entreprises/RH, Partenaires Sociaux). Authentification anonyme, design bleu clair, intégration OpenAI GPT-5.2 pour matching intelligent.

## Core Concept: Archéologie des Compétences
Le modèle RE'ACTIF PRO repose sur une hiérarchisation:
- **Métiers** (dans des Filières/Secteurs)
  - → **Savoir-faire** (Hard Skills - compétences techniques)
    - → **Savoir-être** (Soft Skills - compétences comportementales)
      - → **Qualités humaines** (traits de personnalité)
        - → **Valeurs universelles** (Schwartz: 11 valeurs)
          - → **Vertus** (Seligman & Peterson: 6 vertus)

## Architecture
### Backend (FastAPI + MongoDB)
- `/app/backend/server.py` - API monolithique (à refactorer)

### Frontend (React + Tailwind + Shadcn UI)
- `/app/frontend/src/views/PassportView.jsx` - Passeport Dynamique (Lamri & Lubart + CCSP + Archéologie)
- `/app/frontend/src/views/ObservatoireView.jsx` - Observatoire + Signaux Ubuntoo
- `/app/frontend/src/views/CoffreFortView.jsx` - Coffre-Fort Numérique
- `/app/frontend/src/pages/Dashboard.jsx` - Dashboard + navigation

## Completed Features
- [x] Authentification anonyme sécurisée (JWT)
- [x] 3 dashboards spécialisés par rôle
- [x] Coffre-Fort Numérique
- [x] Observatoire Prédictif des Compétences
- [x] Indice d'Évolution des Compétences
- [x] Croisement Ubuntoo x Observatoire
- [x] Passeport Dynamique (7 onglets)
- [x] Intégration OpenAI GPT-5.2
- [x] **Modèle Lamri & Lubart** - 5 composantes
- [x] **Référentiel CCSP** - 3 pôles + 3 degrés
- [x] **Distinction Savoir-faire / Savoir-être** - classification nature avec badges et groupement visuel
- [x] **Archéologie des Compétences** - chaîne hiérarchique Vertus → Valeurs → Qualités → Savoir-être → Savoir-faire
- [x] **Référentiel complet** - 6 Vertus, 11 Valeurs, 14 Filières, 18 mappings Savoir-être

## Key API Endpoints
- `/api/auth/anonymous` - Auth anonyme
- `/api/passport/*` - Passeport Dynamique
- `/api/passport/competences/{id}/evaluate` - Évaluation Lamri & Lubart + CCSP
- `/api/passport/diagnostic` - Diagnostic avec nature_distribution
- `/api/passport/archeologie` - Archéologie des compétences de l'utilisateur
- `/api/referentiel/archeologie` - Référentiel complet (vertus, valeurs, filières, mappings)
- `/api/referentiel/filieres` - Filières professionnelles
- `/api/referentiel/vertus` - Vertus et valeurs
- `/api/coffre/*`, `/api/observatoire/*`, `/api/evolution-index/*`, `/api/ubuntoo/*`, `/api/jobs/*`

## Prioritized Backlog

### P0 (Next)
- [ ] Refactoring backend: découpage server.py en routeurs modulaires
- [ ] Intégrer les Soft Skills (CSE) et les Valeurs (VIA) dans le Passeport avec auto-évaluation
- [ ] Diagnostic fonctionnel avancé basé sur le CCSP
- [ ] Suggestion automatique de la chaîne archéologique (IA pour lier savoir-faire à savoir-être)

### P1 (Soon)
- [ ] Ateliers de Codéveloppement (modèle 6 étapes)
- [ ] Système de micro-titres/badges
- [ ] Export PDF du passeport
- [ ] Explorer les filières et métiers dans l'interface

### P2 (Future)
- [ ] Admin Ubuntoo, notifications, mode sombre
- [ ] Messagerie, analytics RH, calendrier
