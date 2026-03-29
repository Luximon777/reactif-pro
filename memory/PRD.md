# Re'Actif Pro - PRD

## Positionnement strategique
RE'ACTIF PRO est une plateforme de valorisation et de securisation des trajectoires professionnelles, concue pour agir en complementarite des services publics, prives et des acteurs de l'accompagnement. Elle n'a pas vocation a se substituer aux dispositifs existants comme Orient'Est ou EURES, mais a renforcer leur efficacite par une meilleure qualification des profils, une coordination des parcours et une mise en visibilite des competences, freins et potentiels.

### Repartition strategique
- **Orient'Est** : Information, decouverte metiers, formations, ressources regionales, espace d'orientation
- **EURES** : Mobilite europeenne, recrutement transfrontalier, accompagnement employeurs et candidats
- **RE'ACTIF PRO** : Diagnostic enrichi, valorisation du potentiel, accompagnement multi-acteurs, levee des freins, preparation a l'acces aux dispositifs et opportunites

### Vocabulaire institutionnel
- "Interface de coordination" (pas "portail")
- "Brique complementaire" (pas "solution alternative")
- "Outil d'appui aux parcours" (pas "outil d'orientation")
- "Couche de valorisation et de securisation" (pas "plateforme qui centralise")
- "Solution interoperable avec les acteurs existants" (pas "guichet unique")

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + Recharts
- Backend: FastAPI + MongoDB (Motor async)
- Auth: Pseudonyme anonyme (JWT) + Login pro (email/password)
- LLM: OpenAI GPT via Emergent LLM Key (emergentintegrations)

## Implemente

### Core
- Design D'CLIC PRO, Auth multi-niveaux, Analyse CV, Passeport de competences
- Observatoire predictif, Job Matching, Formations, Explorateur

### Ubuntoo (Communaute)
- Section communautaire integree /ubuntoo
- Pipeline Ubuntoo <-> Observatoire (AI detection signaux)
- Sync profil Re'Actif Pro -> Ubuntoo (AI)

### Espace Partenaires de Parcours (COMPLET)
- Interface de coordination (pas "Espace Partenaires")
- Bandeau de complementarite (France Travail / Mission Locale / APEC / Orient'Est / Region Grand Est / EURES / RE'ACTIF PRO)
- Dashboard multi-onglets: Tableau de bord, Beneficiaires, Freins, Preparation parcours IA, Contribution territoriale, Outils V2
- Inscription SIRET + charte ethique + RGPD
- CRUD beneficiaires, freins peripheriques (8 categories), competences validees
- Liaison beneficiaire <-> profil Re'Actif Pro (recherche, consentement, acces profil complet)
- Systeme d'alertes (inactivite, freins critiques, attente prolongee)
- Diagnostic enrichi (contexte social, mobilite, motivation, posture, autonomie)
- Preparation de parcours IA (posture de preparation, renvoi vers Orient'Est/EURES/France Travail)
- Contribution territoriale (freins recurrents, competences emergentes, tensions secteurs)

### Outils d'accompagnement V2 (COMPLET - 29/03/2026)
- 12 fiches augmentees en 5 phases:
  1. Diagnostic initial: Positionnement de depart, Courbe de trajectoire
  2. Bilan professionnel: Recit de carriere analytique, Realisations et impact, Competences dynamiques
  3. Identite et valeurs: Identite professionnelle, Valeurs decisionnelles, Environnement et contraintes
  4. Strategie et trajectoire: Confrontation au marche, Strategie de trajectoire (3 scenarios)
  5. Activation: Reseau et leviers, Mon plan d'activation
- Blocs decisionnels sur chaque fiche: "Ce que je decide / Ce que j'arrete / Ce que je teste"
- Backward compatibility avec les fiches V1

### Consentement granulaire (COMPLET - 29/03/2026)
- 3 niveaux: Synthese partagee, Partage modulaire, Complet temporaire
- 12 modules partageables (profil, parcours, competences, valeurs, documents, etc.)
- Creation, consultation, mise a jour, revocation
- Tracabilite: qui, pourquoi, quelles donnees, duree, statut
- Expiration automatique
- UI complete dans l'onglet Outils

## Endpoints Partenaires
- POST /api/auth/register-partenaire
- POST /api/auth/login-pro
- GET /api/partenaires/stats, /profile, /alertes, /search-users
- CRUD /api/partenaires/beneficiaires
- POST /link, DELETE /link, GET /linked-profile
- PUT /diagnostic
- POST /orientation (GPT IA avec posture complementarite)
- POST/PUT /freins, POST /skills
- POST /contribution-observatoire
- GET /api/partenaires/outils/fiches (V2: 12 fiches)
- GET/PUT /api/partenaires/beneficiaires/{id}/bilan
- POST/GET/PUT/DELETE /api/partenaires/consent
- GET /api/partenaires/consent-modules

## Backlog
- P1: Coffre-fort numerique avec upload de fichiers reels
- P2: Narratif IA personnalise D'CLIC PRO
- P2: Coordination multi-acteurs (plusieurs partenaires / meme beneficiaire)
- P2: FranceConnect
- P3: Ateliers de Codeveloppement / Micro-badges
- Refactoring: DclicTestPage.jsx, ObservatoireView.jsx, PartenaireView.jsx (>1500 lignes)

## Test Reports
- Iteration 43: Phase 1 Partenaires (25/25)
- Iteration 44: Phase 2 Partenaires (15/15)
- Iteration 45: Outils/Fiches V1 (100%)
- Iteration 46: Outils V2 + Consentement granulaire (Backend 16/16, Frontend 100%)
