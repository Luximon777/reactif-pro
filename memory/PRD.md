# PRD - Ré'Actif Pro

## Problème original
Plateforme full-stack d'analyse de compétences professionnelles avec :
- OPC (Observatoire Prédictif des Compétences)
- Portefeuille de compétences certifiées
- Coach virtuel CIP
- Job Dating / Job Matching
- Génération de CV ciblé
- Questionnaire D'CLIC PRO

## Architecture
- Frontend: React + Tailwind CSS + Shadcn/UI
- Backend: FastAPI + MongoDB (Motor) + BackgroundTasks
- Auth: JWT pseudo/password
- Migration: Script automatique au démarrage (migrations.py)

## Ce qui est implémenté
- [x] OPC avec recherche stricte AND + fusion terrain
- [x] Portefeuille de compétences (3 couches : Confiance, Intelligence, Actions)
- [x] Coffre-fort numérique avec preuves S.A.R.E
- [x] Système de badges (Contributeur, Certifié, Expert Certifié)
- [x] Dashboard avec D'CLIC PRO boost
- [x] Upload CV avec analyse en background
- [x] Migration automatique données démo (peter7, peter9)
- [x] Seed complet : 33 coffre docs + 20 skill_illustrations + 10 contrats + proof_document sur 10 expériences
- [x] Admin Gate (3 statuts : Admin, Dev, Invité)

## Comptes démo
- peter7 / Solerys777! (profil complet, Expert Certifié level 3)
- peter9 / Solerys777! (clone de peter7)
- mike7 / Solerys777!
- admin@reactifpro.fr / Choukette@777

## Backlog
- P1: Refactoring server.py (~10000 lignes) en routers modulaires
- P2: Outil diagnostic CCSP
- P2: Ateliers Codéveloppement
- P3: Micro-titres/badges (Ubuntoo)
- P3: Compteur global preuves OPC
