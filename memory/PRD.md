# Ré'Actif Pro - Product Requirements Document

## Original Problem Statement
Plateforme Ré'Actif Pro - plateforme de développement de carrière fondée sur des principes philosophiques (axiologie, phénoménologie) et des modèles de compétences avancés. 3 types d'utilisateurs (Particuliers, Entreprises/RH, Partenaires Sociaux). Authentification anonyme, design bleu clair, intégration OpenAI GPT-5.2 pour matching intelligent.

## Architecture
### Backend (FastAPI + MongoDB)
- `/app/backend/server.py` - API monolithique avec toutes les routes

### Frontend (React + Tailwind + Shadcn UI)
- `/app/frontend/src/pages/Dashboard.jsx` - Dashboard + navigation
- `/app/frontend/src/views/PassportView.jsx` - Passeport Dynamique de Compétences (Lamri & Lubart + CCSP)
- `/app/frontend/src/views/ObservatoireView.jsx` - Observatoire + Signaux Ubuntoo
- `/app/frontend/src/views/EvolutionIndexView.jsx` - Indice d'Évolution
- `/app/frontend/src/views/CoffreFortView.jsx` - Coffre-Fort Numérique
- `/app/frontend/src/views/ParticulierView.jsx` - Vue Particulier
- `/app/frontend/src/views/EntrepriseView.jsx` - Vue Entreprise
- `/app/frontend/src/views/PartenaireView.jsx` - Vue Partenaire

## Completed Features
- [x] Authentification anonyme sécurisée (JWT)
- [x] 3 dashboards spécialisés par rôle
- [x] Coffre-Fort Numérique (8 catégories, partage, indexation)
- [x] Observatoire Prédictif des Compétences
- [x] Indice d'Évolution des Compétences
- [x] Croisement Ubuntoo x Observatoire (Intelligence collective, signaux, pipeline validation, éthique)
- [x] Passeport Dynamique de Compétences (7 onglets, CRUD, agrégation automatique, passerelles IA)
- [x] Intégration OpenAI GPT-5.2 (matching, analyse contributions, passerelles)
- [x] **Modèle Lamri & Lubart** - Évaluation 5 composantes (Connaissance, Cognition, Conation, Affection, Sensori-moteur)
- [x] **Référentiel CCSP** - Classification 3 pôles (Réalisation, Interaction, Initiative) + 3 degrés (Imitation, Adaptation, Transposition)
- [x] **Onglet Évaluation** - Diagnostic avec radar charts, barres CCSP, recommandations

## Key API Endpoints
- `/api/auth/anonymous` - Auth anonyme
- `/api/seed` - Données de démo
- `/api/passport/*` - Passeport Dynamique (GET, refresh, profile, competences, experiences, passerelles, sharing)
- `/api/passport/competences/{id}/evaluate` - Évaluation Lamri & Lubart + CCSP
- `/api/passport/diagnostic` - Diagnostic CCSP avec profil moyen et recommandations
- `/api/coffre/*` - Coffre-Fort Numérique
- `/api/observatoire/*` - Observatoire Prédictif
- `/api/evolution-index/*` - Indice d'Évolution
- `/api/ubuntoo/*` - Intelligence Ubuntoo
- `/api/jobs/*` - Offres d'emploi + matching IA

## Prioritized Backlog

### P0 (Next)
- [ ] Refactoring backend: découpage server.py en routeurs modulaires
- [ ] Intégrer les Soft Skills (CSE) et les Valeurs (VIA) dans le Passeport
- [ ] Diagnostic fonctionnel basé sur le CCSP

### P1 (Soon)
- [ ] Intégrer le référentiel CCSP complet (Doc 1 & 2) pour évaluation structurée
- [ ] Ateliers de Codéveloppement (modèle 6 étapes)
- [ ] Système de micro-titres/badges
- [ ] Export PDF du passeport

### P2 (Future)
- [ ] Interface d'administration pour signaux Ubuntoo
- [ ] Notifications en temps réel
- [ ] Mode sombre
- [ ] Messagerie interne
- [ ] Analytics avancés pour RH/Partenaires
- [ ] Calendrier de rendez-vous intégré
