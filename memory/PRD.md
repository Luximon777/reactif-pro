# Re'Actif Pro - PRD

## Positionnement strategique
RE'ACTIF PRO est une plateforme de valorisation et de securisation des trajectoires professionnelles, concue pour agir en complementarite des services publics, prives et des acteurs de l'accompagnement.

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + Recharts
- Backend: FastAPI + MongoDB (Motor async)
- Auth: Pseudonyme anonyme (JWT) + Login pro (email/password)
- LLM: OpenAI GPT via Emergent LLM Key (emergentintegrations)

## Implemente

### Core
- Design D'CLIC PRO, Auth multi-niveaux, Analyse CV, Passeport de competences
- Observatoire predictif, Job Matching, Formations, Explorateur
- Ubuntoo (Communaute)

### Espace Partenaires de Parcours (COMPLET)
- 6 onglets: Dashboard, Beneficiaires, Freins, Preparation parcours IA, Contribution territoriale, Outils V2
- Bandeau complementarite (7 acteurs)

### Outils d'accompagnement V2 (29/03/2026)
- 12 fiches augmentees en 5 phases + blocs decisionnels

### Consentement granulaire (29/03/2026)
- 3 niveaux: Synthese, Modulaire, Complet temporaire

### Demande d'acces beneficiaire RE'ACTIF PRO avec approbation (29/03/2026)
- **Cote partenaire**: Recherche par nom -> "Demander l'acces" -> attente approbation -> Synchroniser (apres acceptation)
- **Cote beneficiaire**: Notification sur le dashboard + dans les parametres de confidentialite -> Accepter / Refuser
- Le beneficiaire reste maitre de ses donnees et proprietaire de ses decisions
- Levee d'anonymat consentie : champs nom/prenom requis quand visibilite = "Limite"
- Synchronisation complete du profil (competences, passeport, CV, D'CLIC) apres approbation
- Collection MongoDB: access_requests (id, partner_id, user_token_id, status, created_at, responded_at)

### Bandeau de synchronisation en attente (30/03/2026)
- Notification sur le dashboard partenaire quand des demandes sont acceptees mais non synchronisees
- Bouton "Synchroniser maintenant" directement sur le dashboard (plus besoin de re-chercher)
- Detection automatique des demandes acceptees non liees a un beneficiaire existant

### Endpoints cles (demande d'acces)
- POST /api/partenaires/demande-acces/request (envoie demande)
- GET /api/partenaires/demande-acces/status (statuts cote partenaire)
- GET /api/partenaires/demande-acces/search (recherche par nom)
- GET /api/notifications/access-requests (demandes cote beneficiaire)
- POST /api/notifications/access-requests/{id}/respond (accepter/refuser)
- POST /api/partenaires/demande-acces/synchroniser (sync apres approbation)

## Backlog
- P1: Coffre-fort numerique avec upload de fichiers reels
- P2: Narratif IA personnalise D'CLIC PRO
- P2: FranceConnect
- P3: Ateliers de Codeveloppement / Micro-badges
- Refactoring: PartenaireView.jsx (>1800 lignes)

## Test Reports
- Iteration 43-45: Partenaires Phase 1-2 + Outils V1
- Iteration 46: Outils V2 + Consentement (100%)
- Iteration 47: Demande d'acces beneficiaire (100%)
- Iteration 48: Flux d'approbation complet (Backend 13/13, Frontend 100%)
