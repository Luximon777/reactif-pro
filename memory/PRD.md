# Re'Actif Pro - PRD

## Positionnement stratégique
RE'ACTIF PRO est une plateforme de valorisation et de sécurisation des trajectoires professionnelles, conçue pour agir en complémentarité des services publics, privés et des acteurs de l'accompagnement. Elle n'a pas vocation à se substituer aux dispositifs existants comme Orient'Est ou EURES, mais à renforcer leur efficacité par une meilleure qualification des profils, une coordination des parcours et une mise en visibilité des compétences, freins et potentiels.

### Vocabulaire institutionnel
- "Interface de coordination" (pas "portail")
- "Brique complémentaire" (pas "solution alternative")
- "Outil d'appui aux parcours" (pas "outil d'orientation")

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + Recharts
- Backend: FastAPI + MongoDB (Motor async)
- Auth: Pseudonyme anonyme (JWT) + Login pro (email/password)
- LLM: OpenAI GPT via Emergent LLM Key (emergentintegrations)

## Implémenté

### Core
- Design D'CLIC PRO, Auth multi-niveaux, Analyse CV, Passeport de compétences
- Observatoire prédictif, Job Matching, Formations, Explorateur

### Ubuntoo (Communauté)
- Section communautaire intégrée /ubuntoo

### Espace Partenaires de Parcours (COMPLET)
- Interface de coordination (6 onglets)
- Bandeau complémentarité (7 acteurs)
- Dashboard, Bénéficiaires, Freins, Préparation parcours IA, Contribution territoriale, Outils V2

### Outils d'accompagnement V2 (COMPLET - 29/03/2026)
- 12 fiches augmentées en 5 phases (Diagnostic, Bilan pro, Identité/Valeurs, Stratégie, Activation)
- Blocs décisionnels ("Ce que je décide / Ce que j'arrête / Ce que je teste")
- Backward compatibility avec les fiches V1

### Consentement granulaire (COMPLET - 29/03/2026)
- 3 niveaux: Synthèse partagée, Partage modulaire, Complet temporaire
- 12 modules partageables, création/révocation, expiration automatique

### Demande d'accès bénéficiaire RE'ACTIF PRO (COMPLET - 29/03/2026)
- Flux principal: Recherche par nom → Vérification autorisation → Synchronisation profil complet
- Deux boutons coexistent: "Demande d'accès RE'ACTIF PRO" + "Création manuelle"
- Recherche par nom (real_first_name / real_last_name)
- Badge "Compte ouvert autorisé" + bouton "Synchroniser" quand visibilité = limité
- Badge "Accès non autorisé" quand visibilité = privé
- Paramètres de confidentialité: champs nom/prénom requis + avertissement levée d'anonymat
- Synchronisation complète: nom, compétences, passeport, résultats D'CLIC, CV analyses
- Consent history enregistré pour chaque synchronisation

### Accents français (COMPLET - 29/03/2026)
- Correction systématique de tous les textes (backend + frontend)

## Endpoints clés
- POST /api/auth/register-partenaire, POST /api/auth/login-pro
- GET /api/partenaires/stats, /beneficiaires, /alertes
- GET /api/partenaires/demande-acces/search (recherche par nom)
- POST /api/partenaires/demande-acces/synchroniser (sync profil)
- PUT /api/profile/privacy (avec real_first_name/real_last_name)
- GET /api/partenaires/outils/fiches (V2: 12 fiches)
- POST/GET/PUT/DELETE /api/partenaires/consent

## Backlog
- P1: Coffre-fort numérique avec upload de fichiers réels
- P2: Narratif IA personnalisé D'CLIC PRO
- P2: FranceConnect
- P3: Ateliers de Codéveloppement / Micro-badges
- Refactoring: PartenaireView.jsx (>1700 lignes), DclicTestPage.jsx, ObservatoireView.jsx

## Test Reports
- Iteration 43: Phase 1 Partenaires (25/25)
- Iteration 44: Phase 2 Partenaires (15/15)
- Iteration 45: Outils/Fiches V1 (100%)
- Iteration 46: Outils V2 + Consentement (Backend 16/16, Frontend 100%)
- Iteration 47: Demande d'accès bénéficiaire (Backend 16/16, Frontend 100%)
