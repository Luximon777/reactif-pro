# Ré'Actif Pro - Product Requirements Document

## Original Problem Statement
Créer la plateforme Ré'Actif Pro - une plateforme de développement de carrière avec 3 types d'utilisateurs:
- **Particuliers**: analyse de profil, compétences, modules d'apprentissage, offres d'emploi avec matching IA
- **Entreprises/RH**: gestion des offres, candidats compatibles, métriques de recrutement
- **Partenaires Sociaux**: suivi des bénéficiaires, prescriptions, observations territoriales

Authentification anonyme avec tokens sécurisés, design mode clair avec couleur bleue, intégration OpenAI GPT-5.2 pour le matching intelligent.

## Architecture

### Backend (FastAPI + MongoDB)
- `/app/backend/server.py` - API complète avec:
  - Auth anonyme via tokens sécurisés
  - Gestion des profils utilisateurs
  - API offres d'emploi avec matching
  - API modules de formation
  - API bénéficiaires (partenaires)
  - Intégration OpenAI pour matching IA

### Frontend (React + Tailwind + Shadcn UI)
- `/app/frontend/src/pages/Landing.jsx` - Page d'accueil avec sélection de rôle
- `/app/frontend/src/pages/Dashboard.jsx` - Dashboard principal avec navigation
- `/app/frontend/src/views/ParticulierView.jsx` - Vue Particulier
- `/app/frontend/src/views/EntrepriseView.jsx` - Vue Entreprise/RH
- `/app/frontend/src/views/PartenaireView.jsx` - Vue Partenaire Social

## User Personas
1. **Particulier** - Individu en recherche d'emploi ou reconversion professionnelle
2. **RH/Entreprise** - Recruteur ou responsable RH recherchant des talents
3. **Partenaire Social** - Conseiller accompagnant des bénéficiaires vers l'emploi

## Core Requirements (Implemented)
- [x] Authentification anonyme sécurisée
- [x] 3 dashboards spécialisés par rôle
- [x] Affichage des offres d'emploi avec scoring
- [x] Modules de formation avec progression
- [x] Gestion des compétences utilisateur
- [x] Switch de rôle en temps réel
- [x] Données de démonstration pré-remplies
- [x] Design bleu professionnel (mode clair)
- [x] Intégration OpenAI GPT-5.2 pour matching IA

## What's Been Implemented (Jan 2026)
- Landing page avec présentation des 3 rôles
- Authentification anonyme via tokens
- Dashboard Particulier complet (métriques, compétences, emplois, formations)
- Dashboard Entreprise/RH (offres, candidats, création d'offres)
- Dashboard Partenaire (bénéficiaires, suivi, observations)
- API complète avec endpoints RESTful
- Données de démo automatiquement chargées
- Switch de rôle fonctionnel
- Design responsive avec thème bleu

## Prioritized Backlog
### P0 (Done)
- ✅ Core authentication
- ✅ 3 dashboard views
- ✅ Jobs & Learning modules display
- ✅ Demo data seeding

### P1 (Next)
- [ ] Matching IA amélioré avec analyse détaillée
- [ ] Notifications en temps réel
- [ ] Export PDF des profils/rapports
- [ ] Filtres avancés sur les offres

### P2 (Future)
- [ ] Mode sombre
- [ ] Messagerie interne
- [ ] Calendrier de rendez-vous intégré
- [ ] Analytics avancés pour RH/Partenaires

## Next Tasks
1. Améliorer l'analyse IA du matching emploi/profil
2. Ajouter des filtres de recherche sur les offres
3. Implémenter la messagerie entre utilisateurs
4. Ajouter des statistiques graphiques (charts)
