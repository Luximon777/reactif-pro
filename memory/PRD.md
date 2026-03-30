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
- Cote partenaire: Recherche par nom -> Demander l'acces -> attente approbation -> Synchroniser
- Cote beneficiaire: Notification + Accepter / Refuser
- Levee d'anonymat consentie
- Synchronisation complete du profil apres approbation

### Bandeau de synchronisation en attente (30/03/2026)
- Notification sur le dashboard partenaire quand des demandes sont acceptees mais non synchronisees
- Bouton "Synchroniser maintenant" directement sur le dashboard

### Calcul automatique de la progression du parcours (30/03/2026)
- Progression calculee automatiquement lors de la synchronisation basee sur:
  - Nom reel defini (5%) + Secteurs (5%)
  - Competences identifiees (max 20%)
  - CV analyse (20%)
  - Passeport de competences (25%)
  - Test D'CLIC PRO (25%)
- Endpoint POST /api/partenaires/beneficiaires/{id}/resync pour re-calculer la progression
- Bouton "Re-synchroniser" dans la fiche du beneficiaire

### Endpoints cles
- POST /api/partenaires/demande-acces/request
- GET /api/partenaires/demande-acces/status
- GET /api/partenaires/demande-acces/search
- GET /api/notifications/access-requests
- POST /api/notifications/access-requests/{id}/respond
- POST /api/partenaires/demande-acces/synchroniser
- POST /api/partenaires/beneficiaires/{id}/resync (NEW)

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
