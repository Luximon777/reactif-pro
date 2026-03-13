# Ré'Actif Pro - Product Requirements Document

## Original Problem Statement
Créer la plateforme Ré'Actif Pro - une plateforme de développement de carrière avec 3 types d'utilisateurs:
- **Particuliers**: analyse de profil, compétences, modules d'apprentissage, offres d'emploi avec matching IA
- **Entreprises/RH**: gestion des offres, candidats compatibles, métriques de recrutement
- **Partenaires Sociaux**: suivi des bénéficiaires, prescriptions, observations territoriales

## Architecture

### Backend (FastAPI + MongoDB)
- `/app/backend/server.py` - API avec:
  - Auth anonyme via tokens sécurisés
  - Gestion des profils utilisateurs
  - API offres d'emploi avec matching IA (OpenAI GPT-5.2 via Emergent LLM Key)
  - API Coffre-Fort Numérique (8 catégories)
  - API Observatoire Prédictif (contributions, compétences émergentes, tendances)
  - API Indice d'Évolution des Compétences
  - **API Intelligence Ubuntoo** (signaux, échanges, insights, validation, cross-reference)

### Frontend (React + Tailwind + Shadcn UI)
- `/app/frontend/src/pages/Dashboard.jsx` - Dashboard avec navigation + bouton Ubuntoo
- `/app/frontend/src/views/ObservatoireView.jsx` - Observatoire + onglet Signaux Ubuntoo
- `/app/frontend/src/views/EvolutionIndexView.jsx` - Indice d'Évolution
- Autres vues: CoffreFortView, ParticulierView, EntrepriseView, PartenaireView

## Core Requirements (Completed)
- [x] Authentification anonyme sécurisée
- [x] 3 dashboards spécialisés par rôle
- [x] Intégration OpenAI GPT-5.2 via Emergent LLM Key
- [x] Coffre-Fort Numérique (8 catégories)
- [x] Observatoire Prédictif des Compétences
- [x] Indice d'Évolution des Compétences
- [x] **Croisement Ubuntoo × Observatoire** (Intelligence collective, signaux, pipeline validation, éthique)

## Key API Endpoints
- `/api/auth/anonymous` - Auth anonyme
- `/api/seed` - Données de démo
- `/api/coffre/*` - Coffre-Fort Numérique
- `/api/observatoire/*` - Observatoire Prédictif
- `/api/evolution-index/*` - Indice d'Évolution
- `/api/ubuntoo/dashboard` - Dashboard intelligence Ubuntoo
- `/api/ubuntoo/signals` - Signaux détectés (filtrable)
- `/api/ubuntoo/signals/{id}` - Détail signal + cross-references
- `/api/ubuntoo/signals/{id}/validate` - Validation humaine
- `/api/ubuntoo/analyze` - Analyse IA des échanges
- `/api/ubuntoo/insights` - Insights croisés
- `/api/ubuntoo/cross-reference` - Croisement données

## Prioritized Backlog

### P0 (Done)
- Toutes les fonctionnalités core implémentées et testées

### P1 (Next)
- [ ] Refactoring backend: découpage server.py en routeurs modulaires
- [ ] Interface de validation humaine des signaux Ubuntoo (admin panel)
- [ ] Export PDF des rapports observatoire/évolution

### P2 (Future)
- [ ] Notifications en temps réel
- [ ] Mode sombre
- [ ] Messagerie interne
- [ ] Analytics avancés pour RH/Partenaires
