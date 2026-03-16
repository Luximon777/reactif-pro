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

## Key Endpoints
- GET `/api/referentiel/explorer/metier/{name}` - Fiche DB
- POST `/api/referentiel/explorer/generate` - Génération IA (background)
- GET `/api/referentiel/explorer/generate/status` - Poll résultat IA

## Prioritized Backlog
### P0
- [ ] Refactoring backend (server.py ~3900+ lignes)
### P1
- [ ] Génération PDF des modèles de CV
- [ ] Quiz d'orientation basé sur l'explorateur
### P2
- [ ] CCSP diagnostic, export PDF passeport, mode sombre
