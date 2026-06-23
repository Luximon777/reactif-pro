# Ré'Actif Pro — PRD

## Problème original
Plateforme full-stack "Ré'Actif Pro" — analyse de compétences avec OPC, audit CV, coach virtuel, job matching, portefeuille de compétences.

## Architecture
- **Frontend**: React, Tailwind CSS, Shadcn/UI, React Router
- **Backend**: FastAPI, MongoDB (Motor), migrations automatiques au démarrage
- **IA**: OpenAI GPT-5.2 via Emergent LLM Key
- **Production**: https://marche-cache.emergent.host

## Fonctionnalités implémentées

### Modules principaux
- OPC avec analyse IA, cartographie métier, référentiel vivant
- Portefeuille de compétences avec certification (méthode S.A.R.E.)
- Coach virtuel proactif (CIP)
- Job Dating / Job Matching avec France Travail (URLs réelles)
- Génération de CV ciblé
- Questionnaire D'CLIC PRO (6 vertus)
- Gestion Admin/Gate, Profil enrichi (Formations, Hard Skills)
- Scoring IA CV/Offres, Archéologie des compétences avec D'CLIC PRO

### Session 22-23 juin 2026
- Recherche OPC logique AND (tous les mots doivent correspondre)
- Classement Hard/Soft Skills dans OPC (HACCP→Hard, Rigueur→Soft)
- Colonnes Valeurs avant Vertus + enrichissement D'CLIC
- Migration données démo peter7/peter9 au démarrage
- Seed référentiel OPC complet (68 métiers + 289 fiches)
- Fix D'CLIC boost section (fallback depuis passeport)
- autoComplete="one-time-code" sur tous formulaires login
- peter9 ajouté au seed avec profil complet = peter7

## Backlog priorisé
### P1
- Refactoring `server.py` (~9900 lignes) → extraction `/app/backend/routes/`

### P2
- Outil de diagnostic CCSP
- Ateliers de Codéveloppement

### P3
- Micro-titres/badges (module Ubuntoo)
- Compteur global de preuves dans Référentiel OPC

## Comptes de test
- peter7 / Solerys777! (particulier)
- peter9 / Solerys777! (particulier)
- mike7 / Solerys777! (particulier)
- marc19 / Solerys777! (particulier)
- admin@reactifpro.fr / Choukette@777 (admin)
- rh@reactifpro.fr / Reactif@pro2026! (entreprise)
