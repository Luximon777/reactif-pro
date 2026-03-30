# Re'Actif Pro - PRD

## Positionnement strategique
RE'ACTIF PRO est une plateforme de valorisation et de securisation des trajectoires professionnelles, concue pour agir en complementarite des services publics, prives et des acteurs de l'accompagnement.

**Axe differanciant**: "Plateforme qui supprime la charge administrative invisible" — logique zero ressaisie, IA d'aide a la decision, autonomie beneficiaire.

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + Recharts
- Backend: FastAPI + MongoDB (Motor async)
- Auth: Pseudonyme anonyme (JWT) + Login pro (email/password)
- LLM: OpenAI GPT-4.1-mini via Emergent LLM Key (emergentintegrations)

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

### Demande d'acces beneficiaire avec approbation (29/03/2026)
- Recherche par nom -> Demander l'acces -> Approbation -> Synchroniser
- Bandeau notification sur dashboard pour syncs en attente

### Workflow "Zero charge administrative" — 7 modules (30/03/2026)

#### 1. Synthese pre-entretien IA
- Generation IA de synthese exploitable en 2 minutes
- Contenu: resume parcours, points forts, vigilances, freins, questions a explorer, dispositifs, recommandations
- Niveaux urgence et autonomie calcules automatiquement
- POST /api/partenaires/beneficiaires/{id}/synthese-pre-entretien

#### 2. Compte rendu d'entretien IA
- Formulaire: type entretien (diagnostic/intermediaire/final), notes, points abordes, decisions
- Generation IA d'un compte rendu professionnel (compatible outil France Travail)
- Texte copiable directement dans le SI du conseiller
- Boutons: Copier, Valider
- POST /api/partenaires/beneficiaires/{id}/compte-rendu
- GET /api/partenaires/beneficiaires/{id}/comptes-rendus
- PUT /api/partenaires/comptes-rendus/{id}/valider

#### 3. Plan d'action intelligent
- Generation IA: objectif principal, actions avec categories/priorites/echeances, dispositifs recommandes, jalons, risques
- Suivi de statut par action (a_faire / en_cours / termine / annule)
- POST /api/partenaires/beneficiaires/{id}/plan-action/generer
- GET /api/partenaires/beneficiaires/{id}/plan-action
- PUT /api/partenaires/plan-action/{id}/actions/{action_id}

#### 4. Vue lecture rapide (2 minutes)
- Identite + progression + score de risque
- Diagnostic resume (motivation, posture, autonomie, competences)
- Freins actifs, plan d'action resume, dernier entretien
- GET /api/partenaires/beneficiaires/{id}/lecture-rapide

#### 5. Export intelligent
- Export texte structure du dossier complet
- Format optimise copie/colle pour outil France Travail
- Boutons: Copier tout, Telecharger .txt
- GET /api/partenaires/beneficiaires/{id}/export

#### 6. Detection de decrochage
- Score de risque automatique (0-100) base sur: inactivite, freins critiques, motivation, autonomie, progression
- Niveaux: faible / moyen / eleve / critique
- Facteurs de risque identifies
- GET /api/partenaires/beneficiaires/{id}/risque
- GET /api/partenaires/risques-globaux

#### 7. Bilan de fin de parcours
- Generation IA: synthese globale, competences developpees, freins leves/restants, actions realisees, recommandations
- Texte copiable compatible outil metier
- POST /api/partenaires/beneficiaires/{id}/bilan-final
- GET /api/partenaires/beneficiaires/{id}/bilan-final

### Onglets dans la fiche beneficiaire
Vue rapide (defaut) | Profil | Diagnostic | Synthese IA | Entretiens | Plan d'action | Freins | Historique | Export/Bilan | Profil Re'Actif

## Backlog
- P1: Coffre-fort numerique avec upload de fichiers reels
- P2: Narratif IA personnalise D'CLIC PRO
- P2: FranceConnect
- P3: Ateliers de Codeveloppement / Micro-badges
- Refactoring: PartenaireView.jsx (>1800 lignes)

## Test Reports
- Iteration 46: Outils V2 + Consentement (100%)
- Iteration 47: Demande d'acces (100%)
- Iteration 48: Flux d'approbation (100%)
- Iteration 49: Workflow zero charge admin - 7 modules (Backend 14/14, Frontend 100%)
