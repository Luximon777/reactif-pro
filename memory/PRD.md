# Re'Actif Pro - PRD

## Problem Statement
Plateforme full-stack "Re'Actif Pro" pour l'analyse de CV par IA, l'optimisation ATS, et la gestion d'un Passeport de Competences dynamique. La plateforme integre un systeme d'anonymat et pseudonymat pour proteger l'identite des utilisateurs.

## Flux CV en 3 etapes
1. **Charger** : Upload du CV (PDF, DOCX, TXT)
2. **Analyser** : Audit 10 regles pro + score /100 + diagnostic + suggestion modele + detection competences emergentes (~30s)
3. **Optimiser** : Choix de modele + offre d'emploi optionnelle pour ciblage ATS + optimisation IA (~15s) + telechargement Word/PDF

## Systeme d'identite (Anonymat & Pseudonymat)
3 niveaux d'acces:
1. **Espace Personnel** : Inscription sous pseudonyme
2. **Espace Employeurs** : Inscription entreprise (SIRET+referent+charte)
3. **Espace Partenaires** : Inscription structure (type+SIRET+referent+charte)

## Architecture
```
frontend/src/
  pages/ Landing.jsx, Dashboard.jsx, SharedPassportPage.jsx
  views/ ParticulierView.jsx, PassportView.jsx, ObservatoireView.jsx, etc.
  components/ AuthModal.jsx, JobMatchingSection.jsx, CvAnalysis/, Passport/
backend/
  routes/ auth.py, cv.py, jobs.py, passport.py, observatoire.py, evolution.py, explorer.py, etc.
  job_matching.py - Algorithme de scoring avec RQTH/EQTH (contexte, jamais discriminant)
  models.py, server.py, db.py, helpers.py
```

## What's Implemented
- Audit CV 10 regles + score /100
- Optimisation ATS avec offre d'emploi cible
- 4 modeles CV avec telechargement Word/PDF
- Passeport Profil Dynamique 7 dimensions
- Detection competences emergentes (4 phases)
- Anonymat & Pseudonymat complet 3 niveaux
- Verification SIRET, Charte Ethique ALT&ACT, Confidentialite
- Correlation CV x Observatoire/Evolution/Formations/Emergentes
- Integration matrice ISCO INSEE (5853 metiers)
- Job Matching avance avec RQTH/EQTH (contexte, jamais discriminant)
- Fix crash React P0 (23/03/2026): Mapping offres_emploi_suggerees (objets FR vs strings)
- Bouton Postuler P1 (23/03/2026): POST /api/jobs/apply + GET /api/jobs/applications + UI
- Fix route ordering (23/03/2026): /jobs/apply et /jobs/applications avant /jobs/{job_id}
- **Partage anonymise Passeport** (23/03/2026):
  - Lien unique anonymise avec expiration 30 jours
  - Vue publique sans authentification (/passport/shared/:shareId)
  - Generation, copie, revocation depuis PassportView
  - Compteur de vues par lien
  - Anonymisation verifiee (token_id, pseudo, email non exposes)

## Backlog
- P1: Integration communautaire Ubuntoo
- P2: Coffre-fort numerique pour preuves
- P3: FranceConnect, CCSP, Auto-evaluations
- P4: Ateliers Codeveloppement, micro-titres/badges

## Key API Endpoints
- POST /api/auth/register, POST /api/auth/login
- GET /api/jobs, GET /api/jobs/matching, POST /api/jobs/matching/search
- POST /api/jobs/apply, GET /api/jobs/applications
- GET /api/passport, POST /api/passport/share/create, GET /api/passport/shares
- DELETE /api/passport/shares/{share_id}, GET /api/passport/shared/{share_id} (public)
- GET /api/evolution/user-profile, GET /api/observatoire/personalized
- GET /api/profile, GET /api/learning

## Tech Stack
- Frontend: React, Tailwind CSS, Shadcn/UI
- Backend: FastAPI, Python, GPT-5.2 via Emergent LLM Key
- Database: MongoDB (Motor async)
