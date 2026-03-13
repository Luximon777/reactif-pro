# Ré'Actif Pro - Product Requirements Document

## Original Problem Statement
Créer la plateforme Ré'Actif Pro - une plateforme de développement de carrière avec 3 types d'utilisateurs:
- **Particuliers**: analyse de profil, compétences, modules d'apprentissage, offres d'emploi avec matching IA
- **Entreprises/RH**: gestion des offres, candidats compatibles, métriques de recrutement
- **Partenaires Sociaux**: suivi des bénéficiaires, prescriptions, observations territoriales

Authentification anonyme avec tokens sécurisés, design mode clair avec couleur bleue, intégration OpenAI GPT-5.2 pour le matching intelligent.

## Architecture

### Backend (FastAPI + MongoDB)
- `/app/backend/server.py` - API monolithique avec:
  - Auth anonyme via tokens sécurisés
  - Gestion des profils utilisateurs
  - API offres d'emploi avec matching IA (OpenAI GPT-5.2)
  - API modules de formation
  - API bénéficiaires (partenaires)
  - API Coffre-Fort Numérique (8 catégories)
  - API Observatoire Prédictif (contributions, compétences émergentes, tendances)
  - API Indice d'Évolution des Compétences (métiers, secteurs, analyse profil)

### Frontend (React + Tailwind + Shadcn UI)
- `/app/frontend/src/App.js` - Auth context, routing
- `/app/frontend/src/pages/Landing.jsx` - Page d'accueil avec sélection de rôle
- `/app/frontend/src/pages/Dashboard.jsx` - Dashboard principal avec navigation
- `/app/frontend/src/views/ParticulierView.jsx` - Vue Particulier
- `/app/frontend/src/views/EntrepriseView.jsx` - Vue Entreprise/RH
- `/app/frontend/src/views/PartenaireView.jsx` - Vue Partenaire Social
- `/app/frontend/src/views/CoffreFortView.jsx` - Coffre-Fort Numérique
- `/app/frontend/src/views/ObservatoireView.jsx` - Observatoire Prédictif
- `/app/frontend/src/views/EvolutionIndexView.jsx` - Indice d'Évolution

## User Personas
1. **Particulier** - Individu en recherche d'emploi ou reconversion professionnelle
2. **RH/Entreprise** - Recruteur ou responsable RH recherchant des talents
3. **Partenaire Social** - Conseiller accompagnant des bénéficiaires vers l'emploi

## Core Requirements
- [x] Authentification anonyme sécurisée
- [x] 3 dashboards spécialisés par rôle
- [x] Affichage des offres d'emploi avec scoring
- [x] Modules de formation avec progression
- [x] Gestion des compétences utilisateur
- [x] Switch de rôle en temps réel
- [x] Données de démonstration pré-remplies
- [x] Design bleu professionnel (mode clair)
- [x] Intégration OpenAI GPT-5.2 via Emergent LLM Key
- [x] Coffre-Fort Numérique (8 catégories, partage, indexation)
- [x] Observatoire Prédictif des Compétences
- [x] Indice d'Évolution des Compétences

## Key API Endpoints
- `/api/auth/anonymous` - Auth anonyme
- `/api/seed` - Données de démo
- `/api/coffre/*` - Coffre-Fort Numérique
- `/api/observatoire/*` - Observatoire Prédictif
- `/api/evolution-index/*` - Indice d'Évolution
- `/api/jobs/*` - Offres d'emploi + matching IA
- `/api/learning` - Modules de formation

## Prioritized Backlog

### P0 (Done)
- Core authentication
- 3 dashboard views
- Jobs & Learning modules
- Demo data seeding
- Coffre-Fort Numérique
- Observatoire Prédictif
- Indice d'Évolution des Compétences
- Intégration OpenAI (matching + analyse contributions)

### P1 (Next)
- [ ] Refactoring backend: découpage server.py en routeurs modulaires
- [ ] Matching IA amélioré avec analyse détaillée côté frontend
- [ ] Export PDF des profils/rapports

### P2 (Future)
- [ ] Notifications en temps réel
- [ ] Mode sombre
- [ ] Messagerie interne
- [ ] Calendrier de rendez-vous intégré
- [ ] Analytics avancés pour RH/Partenaires
