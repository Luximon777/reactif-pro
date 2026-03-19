# Re'Actif Pro - PRD

## Problem Statement
Plateforme full-stack "Re'Actif Pro" pour l'analyse de CV par IA, l'optimisation ATS, et la gestion d'un Passeport de Competences dynamique.

## Flux CV en 3 etapes
1. **Charger** : Upload du CV (PDF, DOCX, TXT)
2. **Analyser** : Audit 10 regles pro + score /100 + diagnostic + suggestion modele + detection competences emergentes (~30s)
3. **Optimiser** : Choix de modele + offre d'emploi optionnelle pour ciblage ATS + optimisation IA (~15s) + telechargement Word/PDF

## Architecture Refactorisee
```
frontend/src/
  views/
    ParticulierView.jsx (354 lignes) - Dashboard principal
    PassportView.jsx (1670 lignes) - Passeport competences
  components/
    CvAnalysis/
      CvAnalysisSection.jsx (693 lignes) - Upload, analyse, optimisation CV
      CvPreview.jsx (105 lignes) - Apercu CV
    Passport/
      EmergingCompetenceCard.jsx (85 lignes) - Carte competence emergente
      passportConfig.js (84 lignes) - Config partagees
backend/
  routes/
    cv.py - Analyse CV + 3 appels LLM paralleles (audit + skills + emerging)
    emerging.py - CRUD competences emergentes
    passport.py, auth.py, etc.
```

## What's Implemented
- Audit CV 10 regles + score /100
- Optimisation ATS avec offre d'emploi cible
- 4 modeles CV (Classique, Competences, Transversal, Nouvelle Generation) avec SF/SE
- Telechargement Word + PDF
- Section strategie 3 canaux (ATS, Reseau, Approche directe)
- Passeport Profil Dynamique 7 dimensions
- Performance: analyse ~30s, optimisation ~15s
- Detection competences emergentes Phase 1 (backend + frontend)
- Endpoints: GET/POST emerging/competences, validate, observatory
- Refactoring: ParticulierView 1294->354 lignes, PassportView 1823->1670 lignes

## Backlog
- P1: Phase 2 - Filtres, tri, details avances pour competences emergentes
- P2: Phase 3 - Interface validation humaine (consultants valident/rejettent competences IA)
- P3: Phase 4 - Observatoire des competences (dashboard tendances)
- P4: Integration communautaire Ubuntoo
- P4: Coffre-fort numerique pour preuves
- Integration CCSP, diagnostic fonctionnel, auto-evaluation
- Ateliers Codeveloppement, micro-titres/badges
