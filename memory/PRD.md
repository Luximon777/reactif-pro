# Ré'Actif Pro - Product Requirements Document

## Core Concept
Plateforme d'intelligence professionnelle basée sur l'archéologie des compétences.
Chaîne relationnelle : Filière → Secteur → Métier → Mission → Savoir-faire/Capacité technique → Savoir-être/Capacité pro → Qualités humaines → Valeurs → Vertus

## Completed Features
- [x] Auth anonyme, 3 dashboards, Passeport Dynamique, Observatoire
- [x] Analyse IA de CV (PDF/DOCX/TXT) avec background processing + polling
- [x] Logo SVG vectoriel
- [x] **Explorateur des Métiers v2** (16 mars 2026)
  - Saisie de métier comme point d'entrée principal avec auto-complétion
  - Fiche complète: Filière pro, Secteur, Mission, Métiers similaires
  - Savoir-faire numérotés avec capacités techniques détaillées
  - Chaîne archéologique: Savoir-être → Capacité pro → Qualités → Valeurs → Vertus
  - Exemples de métiers en accès rapide, statistiques globales
  - 20 filières, 85 secteurs, 45 métiers, 105 SF, 11 SE

## Key Endpoints
- GET `/api/referentiel/explorer` - Filières + secteurs + noms métiers
- GET `/api/referentiel/explorer/metier/{name}` - Fiche complète + métiers similaires
- GET `/api/referentiel/explorer/search?q=` - Recherche transversale
- GET `/api/referentiel/explorer/stats` - Statistiques

## Prioritized Backlog
### P0
- [ ] Refactoring backend (server.py ~3800+ lignes)
- [ ] Refactoring frontend
### P1
- [ ] Génération PDF des modèles de CV
- [ ] Quiz d'orientation basé sur l'explorateur
### P2
- [ ] CCSP diagnostic, Soft Skills auto-évaluation
- [ ] Export PDF passeport, mode sombre
