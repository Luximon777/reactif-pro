# Re'Actif Pro - PRD

## Problem Statement
Plateforme full-stack "Re'Actif Pro" pour l'analyse de CV par IA, l'optimisation ATS, et la gestion d'un Passeport de Competences dynamique avec systeme d'anonymat et pseudonymat. Integration du questionnaire D'CLIC PRO pour profil personnalite et competences.

## Architecture
```
frontend/src/
  pages/ Landing.jsx, Dashboard.jsx, SharedPassportPage.jsx, DclicTestPage.jsx
  views/ ParticulierView.jsx, PassportView.jsx, ObservatoireView.jsx, etc.
  components/ AuthModal.jsx, JobMatchingSection.jsx, CvAnalysis/, Passport/
backend/
  routes/ auth.py, cv.py, jobs.py, passport.py, dclic.py, observatoire.py, evolution.py, coffre.py, ubuntoo.py
  job_matching.py, centres_interet.py, models.py, server.py, db.py
  data/ logo-reactif-pro.png
```

## What's Implemented
- Audit CV 10 regles + score /100
- Optimisation ATS avec offre cible + centres d'interet enrichis
- 4 modeles CV (classique, competences, transversale, nouvelle generation)
- Logo Re'Actif Pro en pied de page (bas droite) dans tous les CV generes (DOCX + PDF)
- Passeport Profil Dynamique 7 dimensions
- Detection competences emergentes (4 phases)
- Anonymat & Pseudonymat 3 niveaux + verification SIRET + Charte ALT&ACT
- Job Matching avance RQTH/EQTH
- Bouton "Preparer votre candidature" + titres offres/formations = liens Google Search
- Partage anonymise Passeport (lien 30j, logo Re'Actif Pro)
- Formations priorisees par competences emergentes (IA personnalisee)
- Analyse centres d'interet (9 categories, 3 niveaux, reformulations CV pro)
- Profil CV Nouvelle Generation (champs enrichis, preuves/evidences)
- **Questionnaire D'CLIC PRO integre** (24/03/2026):
  - 17 questions visuelles et ranking (MBTI, DISC, Enneagramme, RIASEC, Vertus/Valeurs)
  - Calcul de profil personnalite complet
  - Generation code d'acces XXXX-XXXX
  - Page /test-dclic accessible sans compte
  - Modale "Charger profil D'CLIC PRO" avec saisie du code et preview profil
  - Import du profil dans Re'Actif Pro (competences, vertus, forces)
- Nettoyage UI: suppression dropdown role inutile, suppression blocs "Competences Transversales" et "Besoins en Formation", zone CV pleine largeur
- Augmentation tailles de police dans tout le corps du site

## Key API Endpoints
- POST /api/auth/register, POST /api/auth/login
- GET/PUT /api/profile, POST /api/profile/import-dclic
- GET /api/dclic/questionnaire (17 questions)
- POST /api/dclic/submit (calcul profil + code acces)
- POST /api/dclic/retrieve (recuperer profil par code)
- POST /api/dclic/claim (marquer code comme utilise)
- POST /api/cv/analyze-text, POST /api/cv/generate-models
- GET /api/cv/download/{model_type}, GET /api/cv/download-pdf/{model_type}
- GET /api/jobs/matching, POST /api/jobs/apply
- GET /api/passport, POST /api/passport/share/create
- GET /api/learning

## Backlog
- P1: Integration communautaire Ubuntoo
- P2: Coffre-fort numerique pour preuves (upload fichiers)
- P3: FranceConnect, CCSP, Auto-evaluations
- P4: Ateliers Codeveloppement, micro-titres/badges
