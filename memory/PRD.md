# Re'Actif Pro - PRD

## Positionnement strategique
RE'ACTIF PRO est une plateforme de valorisation et de securisation des trajectoires professionnelles, concue pour agir en complementarite des services publics, prives et des acteurs de l'accompagnement.

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + Recharts
- Backend: FastAPI + MongoDB (Motor async)
- Auth: Pseudonyme anonyme (JWT) + Login pro (email/password)
- LLM: OpenAI GPT-4.1-mini via Emergent LLM Key (emergentintegrations)

## Implemente

### Core
- Design D'CLIC PRO, Auth, Analyse CV, Passeport, Observatoire, Job Matching, Formations, Explorateur, Ubuntoo

### Espace Partenaires (COMPLET)
- Dashboard, Beneficiaires, Freins, Preparation IA, Contribution, Outils V2, Workflow zero charge admin

### Identifiant France Travail (31/03/2026)
- Champ a l'inscription + parametres de confidentialite
- Recherche partenaire: Identifiant FT + Nom/Prenom
- Conditions: FT + D'CLIC + Profil booste + Limite

### Corrections dashboard (31/03/2026)
- Profile score recalcule automatiquement apres CV, D'CLIC, import
- GET /profile recalcule le score si 0 (rattrapage utilisateurs existants)
- Dashboard: Job Matching affiche total offres si 0 compatibles
- Dashboard: Formations affiche total suggestions si 0 en cours
- Image D'CLIC "Retrouver des amis" remplacee par image pertinente

## Backlog
- P1: Coffre-fort numerique avec upload fichiers reels
- P2: Narratif IA D'CLIC PRO
- P2: FranceConnect
- P3: Codeveloppement / Micro-badges

## Test Reports
- Iteration 46-48: V2 + Consent + Approbation (100%)
- Iteration 49: Workflow 7 modules (Backend 14/14, Frontend 100%)
- Iteration 50: Identifiant FT + Recherche (Backend 12/12, Frontend 100%)
