# Re'Actif Pro - PRD

## Problem Statement
Plateforme full-stack "Re'Actif Pro" pour l'analyse de CV par IA, l'optimisation ATS, et la gestion d'un Passeport de Competences dynamique avec systeme d'anonymat et pseudonymat.

## Architecture
```
frontend/src/
  pages/ Landing.jsx, Dashboard.jsx, SharedPassportPage.jsx
  views/ ParticulierView.jsx, PassportView.jsx, ObservatoireView.jsx, etc.
  components/ AuthModal.jsx, JobMatchingSection.jsx, CvAnalysis/, Passport/
backend/
  routes/ auth.py, cv.py, jobs.py, passport.py, observatoire.py, evolution.py
  job_matching.py, centres_interet.py, models.py, server.py, db.py
```

## What's Implemented
- Audit CV 10 regles + score /100
- Optimisation ATS avec offre cible + centres d'interet enrichis
- 4 modeles CV (classique, competences, transversale, nouvelle generation)
- Passeport Profil Dynamique 7 dimensions
- Detection competences emergentes (4 phases)
- Anonymat & Pseudonymat 3 niveaux + verification SIRET + Charte ALT&ACT
- Job Matching avance RQTH/EQTH (contexte, jamais discriminant)
- Bouton "Preparer votre candidature" + titres offres/formations = liens Google Search
- Partage anonymise Passeport (lien 30j, logo Re'Actif Pro)
- Formations priorisees par competences emergentes (IA personnalisee)
- Analyse centres d'interet (9 categories, 3 niveaux, reformulations CV pro)
- **Profil CV Nouvelle Generation** (24/03/2026):
  - Champs enrichis: poste cible, ville, mobilite, types contrat, modes travail, resume
  - Gestion preuves/evidences: CRUD (diplome, certificat, attestation, portfolio, recommandation)
  - Bouton "Charger mon profil D'CLIC PRO" dans la navbar
  - Import complet: profil + competences + experiences + preuves
  - Score de completion dynamique du profil

## Key API Endpoints
- POST /api/auth/register, POST /api/auth/login
- GET/PUT /api/profile, POST /api/profile/import-dclic
- GET/POST/DELETE /api/profile/evidences
- POST /api/cv/analyze-text, POST /api/cv/generate-models
- GET /api/jobs/matching, POST /api/jobs/apply
- GET /api/passport, POST /api/passport/share/create
- GET /api/passport/shared/{id} (public)
- GET /api/learning, GET /api/learning/recommendations

## Backlog
- P1: Integration communautaire Ubuntoo
- P2: Coffre-fort numerique pour preuves (upload fichiers)
- P3: FranceConnect, CCSP, Auto-evaluations
- P4: Ateliers Codeveloppement, micro-titres/badges
