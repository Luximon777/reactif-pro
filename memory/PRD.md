# Re'Actif Pro - PRD

## Problem Statement
Plateforme full-stack "Re'Actif Pro" pour l'analyse de CV par IA, l'optimisation ATS, et la gestion d'un Passeport de Competences dynamique. Integration complete du questionnaire D'CLIC PRO.

## Architecture
```
frontend/src/
  pages/ Landing.jsx, Dashboard.jsx, SharedPassportPage.jsx, DclicTestPage.jsx
  views/ ParticulierView.jsx, PassportView.jsx, ObservatoireView.jsx, etc.
  components/ AuthModal.jsx, JobMatchingSection.jsx, CvAnalysis/, Passport/
backend/
  routes/ auth.py, cv.py, jobs.py, passport.py, dclic.py, observatoire.py, evolution.py, coffre.py, ubuntoo.py
  dclic_engine.py (moteur complet D'CLIC PRO - 6700+ lignes)
  job_matching.py, centres_interet.py, models.py, server.py, db.py
  data/ logo-reactif-pro.png
```

## What's Implemented
- Audit CV 10 regles + score /100
- Optimisation ATS avec offre cible + centres d'interet enrichis
- 4 modeles CV avec logo Re'Actif Pro en footer (DOCX + PDF)
- Passeport Profil Dynamique 7 dimensions
- Detection competences emergentes (4 phases)
- Anonymat & Pseudonymat 3 niveaux + verification SIRET
- Job Matching avance RQTH/EQTH
- Partage anonymise Passeport (lien 30j)
- Formations priorisees par competences emergentes
- Analyse centres d'interet (9 categories)
- **D'CLIC PRO - Questionnaire complet (24/03/2026):**
  - 26 questions visuelles et ranking
  - Pre-questionnaire: date de naissance + niveau d'etudes
  - Moteur complet: MBTI, DISC, Enneagramme, RIASEC, Vertus (Seligman/Peterson)
  - Analyse integree 3 niveaux, Boussole de Fonctionnement, Cadran d'Ofman
  - Analyse croisee (chemin de vie + profils), Pistes d'action, Carte d'identite pro
  - Code d'acces XXXX-XXXX pour recuperer le profil
  - 9 sections de resultats avec navigation laterale
  - Import dans profil Re'Actif Pro via code d'acces

## Key API Endpoints
- POST /api/auth/register, POST /api/auth/login
- GET/PUT /api/profile, POST /api/profile/import-dclic
- GET /api/dclic/questionnaire (26 questions)
- POST /api/dclic/submit (profil complet + code)
- POST /api/dclic/retrieve, POST /api/dclic/claim
- POST /api/cv/analyze-text, POST /api/cv/generate-models
- GET /api/cv/download/{type}, GET /api/cv/download-pdf/{type}
- GET /api/jobs/matching, GET /api/passport
- GET /api/learning

## Backlog
- P1: Integration communautaire Ubuntoo
- P2: Coffre-fort numerique pour preuves (upload fichiers)
- P3: FranceConnect, CCSP, Auto-evaluations
- P4: Ateliers Codeveloppement, micro-titres/badges
