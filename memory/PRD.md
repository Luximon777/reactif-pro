# Ré'Actif Pro - Product Requirements Document

## Core Concept
Plateforme d'intelligence professionnelle basée sur l'archéologie des compétences.
Chaîne : Filière → Secteur → Métier → Mission → Savoir-faire/Capacité technique → Savoir-être → Capacité pro → Qualités humaines → Valeurs → Vertus

## Completed Features
- [x] Auth anonyme, 3 dashboards, Passeport Dynamique, Observatoire
- [x] Analyse IA de CV (PDF/DOCX/TXT) avec background processing + polling
- [x] Logo SVG vectoriel
- [x] **Explorateur des Métiers v2** (16 mars 2026)
  - Saisie métier + Entrée comme point d'entrée principal
  - Auto-complétion depuis la base (45 métiers) + génération IA pour tout métier inconnu
  - Fiche complète: Filière, Secteur, Mission, Métiers similaires, Savoir-faire/CT
  - **Chaîne archéologique complète** : SE → Capacité pro → Qualités → Valeurs → Vertus
  - Cache des fiches générées par l'IA (MongoDB: generated_metiers)
  - Background processing + polling pour la génération IA
- [x] **Correction bugs critiques CV** (14 juin 2026)
  - Clé LLM Emergent mise à jour (budget dépassé → nouvelle clé)
  - Persistance des données d'analyse CV lors de la navigation (nouvel endpoint GET /api/cv/last-analysis)
  - Auto-remplissage complet : compétences transversales, transférables, offres d'emploi, points forts, lacunes
  - Profil utilisateur mis à jour automatiquement (strengths, gaps, skills, sectors, profile_score)
  - Passeport enrichi avec competences_transversales, offres_emploi

## Key Endpoints
- GET `/api/referentiel/explorer/metier/{name}` - Fiche DB
- POST `/api/referentiel/explorer/generate` - Génération IA (background)
- GET `/api/referentiel/explorer/generate/status` - Poll résultat IA
- POST `/api/cv/analyze-text` - Lance analyse CV (background)
- GET `/api/cv/analyze/status` - Poll résultat analyse CV
- GET `/api/cv/last-analysis` - Dernière analyse complétée (NEW)
- GET `/api/cv/models` - Modèles CV générés

## Prioritized Backlog
### P0
- [ ] Refactoring backend (server.py ~4000+ lignes → routeurs modulaires)
### P1
- [ ] Génération PDF des modèles de CV
- [ ] Quiz d'orientation basé sur l'explorateur
### P2
- [ ] Modules d'auto-évaluation (Soft Skills CSE, Valeurs VIA)
- [ ] Diagnostic fonctionnel CCSP
- [ ] Ateliers de Codéveloppement
- [ ] Système de micro-titres/badges
- [ ] Mode sombre
