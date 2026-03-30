# Re'Actif Pro - PRD

## Positionnement stratégique
RE'ACTIF PRO est une plateforme de valorisation et de sécurisation des trajectoires professionnelles, conçue pour agir en complémentarité des services publics, privés et des acteurs de l'accompagnement.

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + Recharts
- Backend: FastAPI + MongoDB (Motor async)
- Auth: Pseudonyme anonyme (JWT) + Login pro (email/password)
- LLM: OpenAI GPT via Emergent LLM Key (emergentintegrations)

## Implémenté

### Core
- Design D'CLIC PRO, Auth multi-niveaux, Analyse CV, Passeport de compétences
- Observatoire prédictif, Job Matching, Formations, Explorateur
- Ubuntoo (Communauté)

### Espace Partenaires de Parcours (COMPLET)
- 6 onglets: Dashboard, Bénéficiaires, Freins, Préparation parcours IA, Contribution territoriale, Outils V2
- Bandeau complémentarité (7 acteurs)

### Outils d'accompagnement V2 (29/03/2026)
- 12 fiches augmentées en 5 phases + blocs décisionnels

### Consentement granulaire (29/03/2026)
- 3 niveaux: Synthèse, Modulaire, Complet temporaire

### Demande d'accès bénéficiaire RE'ACTIF PRO avec approbation (29/03/2026)
- **Côté partenaire**: Recherche par nom → "Demander l'accès" → attente approbation → Synchroniser (après acceptation)
- **Côté bénéficiaire**: Notification sur le dashboard + dans les paramètres de confidentialité → Accepter / Refuser
- Le bénéficiaire reste maître de ses données et propriétaire de ses décisions
- Levée d'anonymat consentie : champs nom/prénom requis quand visibilité = "Limité"
- Synchronisation complète du profil (compétences, passeport, CV, D'CLIC) après approbation
- Collection MongoDB: access_requests (id, partner_id, user_token_id, status, created_at, responded_at)

### Endpoints clés (demande d'accès)
- POST /api/partenaires/demande-acces/request (envoie demande)
- GET /api/partenaires/demande-acces/status (statuts côté partenaire)
- GET /api/partenaires/demande-acces/search (recherche par nom)
- GET /api/notifications/access-requests (demandes côté bénéficiaire)
- POST /api/notifications/access-requests/{id}/respond (accepter/refuser)
- POST /api/partenaires/demande-acces/synchroniser (sync après approbation)

## Backlog
- P1: Coffre-fort numérique avec upload de fichiers réels
- P2: Narratif IA personnalisé D'CLIC PRO
- P2: FranceConnect
- P3: Ateliers de Codéveloppement / Micro-badges
- Refactoring: PartenaireView.jsx (>1800 lignes)

## Test Reports
- Iteration 43-45: Partenaires Phase 1-2 + Outils V1
- Iteration 46: Outils V2 + Consentement (100%)
- Iteration 47: Demande d'accès bénéficiaire (100%)
- Iteration 48: Flux d'approbation complet (Backend 13/13, Frontend 100%)
