# Ré'Actif Pro — PRD (Product Requirements Document)

## Problème original
Développer une plateforme full-stack "Ré'Actif Pro" basée sur l'analyse de compétences avec OPC, audit CV, coach virtuel, job matching, portefeuille de compétences.

## Architecture
- **Frontend**: React, Tailwind CSS, Shadcn/UI, React Router
- **Backend**: FastAPI, MongoDB (Motor), migrations automatiques au démarrage
- **IA**: OpenAI GPT-5.2 via Emergent LLM Key

## Fonctionnalités implémentées

### Sessions précédentes
- OPC avec analyse IA, cartographie métier et statistiques
- Portefeuille de compétences avec certification (méthode S.A.R.E.)
- Coach virtuel proactif (CIP)
- Job Dating / Job Matching avec France Travail (URLs réelles)
- Génération de CV ciblé
- Questionnaire D'CLIC PRO (6 vertus)
- Gestion Admin/Gate stabilisée
- Profil utilisateur enrichi (Formations, Hard Skills dans Coffre-fort)
- Scoring IA CV/Offres d'emploi
- Archéologie des compétences avec D'CLIC PRO
- Migrations automatiques (`migrations.py`) au démarrage
- Tests de régression (`test_22juin.py`)

### 22 juin 2026
- **Fix recherche OPC** : Logique AND (tous les mots doivent correspondre) au lieu de OR dans `/api/opc/referentiel/search`
- **Fix classement Hard/Soft Skills OPC** : Les contributions terrain stockent désormais `skill_type` dans `fiches_metier_opc.competences`. Le code de recherche classe les skills dans la bonne colonne. Migration ajoutée pour backfill.

## Backlog priorisé

### P1
- Refactoring `server.py` (~9800 lignes) — extraction vers `/app/backend/routes/`

### P2
- Outil de diagnostic CCSP
- Ateliers de Codéveloppement

### P3
- Micro-titres/badges (module Ubuntoo)
- Compteur global de preuves dans Référentiel OPC

## Comptes de test
- `peter7` / `Solerys777!`
- `mike7` / `Solerys777!`
- Admin: `admin@reactifpro.fr` / `Choukette@777`
- RH: `rh@reactifpro.fr`

## DB Schema clé
- `coffre_documents`: skill_type (hard/soft), file_name optionnel
- `passports`: array formations
- `fiches_metier_opc`: contributions terrain, competences avec skill_type (hard/soft)
- `referentiel_opc`: base théorique métiers
