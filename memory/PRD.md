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
  pages/ Landing.jsx, Dashboard.jsx
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
- **Job Matching avancé avec RQTH/EQTH** :
  - RQTH/EQTH = contexte uniquement (jamais discriminant, jamais bloquant)
  - 8 restrictions fonctionnelles : port_charges, station_debout_prolongee, travail_nuit, env_calme, horaires_stables, accessibilite, deplacements_frequents, cadence_elevee
  - Score d'inclusion employeur (0-100) : entreprise_inclusive, partenaire_cap_emploi, experience_handicap, referent_handicap, obligation_emploi, poste_adapte
  - Compatibilite metier + handicap (critere combine)
  - Ciblage employeurs inclusifs + Accessibilite metier handicap
  - Structure offre enrichie : exigences_metier (nested) + employeur (nested)
  - Sauvegarde preferences, recherche scoree, affichage transparent
  - 35 tests backend + frontend 100% passes (iteration_28)

## Backlog
- P0: Candidature via annonce selectionnee (postuler directement)
- P1: Integration communautaire Ubuntoo
- P2: Coffre-fort numerique pour preuves
- P3: FranceConnect, CCSP, Auto-evaluations
- P4: Ateliers Codeveloppement, micro-titres/badges
