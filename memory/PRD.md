# Ré'Actif Pro - Product Requirements Document

## Core Concept
Plateforme d'intelligence professionnelle basée sur l'archéologie des compétences.
Chaîne relationnelle : Filière → Secteur → Métier → Mission → Savoir-faire/Capacité technique → Savoir-être/Capacité pro → Qualités humaines → Valeurs → Vertus

## Architecture
- Backend: FastAPI (server.py) + MongoDB
- Frontend: React + Tailwind CSS + Shadcn/UI
- AI: OpenAI GPT-5.2 via Emergent LLM Key
- Data: ODS import → MongoDB (referentiel_metiers, referentiel_metiers_flat, referentiel_se_links)

## Completed Features
- [x] Auth anonyme, 3 dashboards (Particulier, RH, Partenaire)
- [x] Passeport Dynamique (8 onglets), Lamri & Lubart, CCSP
- [x] Archéologie des Compétences (Vertus→Valeurs→Qualités→Savoir-être→Savoir-faire)
- [x] Analyse IA de CV (PDF/DOCX/TXT → 4 modèles CV) avec background processing + polling
- [x] Logo SVG vectoriel
- [x] **Explorateur Filières Professionnelles** (16 mars 2026)
  - 20 filières, 85 secteurs, 45 métiers, 105 savoir-faire, 11 savoir-être
  - Navigation arborescente interactive (Filière → Secteur → Métier → Détail)
  - Vue détaillée métier : savoir-faire + capacités techniques, savoir-être + chaîne qualités/valeurs/vertus
  - Recherche transversale (filières, secteurs, métiers, compétences)
  - Import ODS automatisé (import_filieres.py)
  - Lien qualités humaines → valeurs → vertus pour chaque savoir-être

## Key Endpoints
- POST `/api/cv/extract-text-b64` - PDF base64 → texte
- POST `/api/cv/analyze-text` - Texte → job_id (background)
- GET `/api/cv/analyze/status` - Poll résultats
- GET `/api/referentiel/explorer` - Toutes les filières + secteurs
- GET `/api/referentiel/explorer/stats` - Statistiques globales
- GET `/api/referentiel/explorer/secteur/{name}` - Métiers d'un secteur
- GET `/api/referentiel/explorer/metier/{name}` - Détail complet d'un métier
- GET `/api/referentiel/explorer/search?q=` - Recherche transversale

## Prioritized Backlog
### P0
- [ ] Refactoring backend (server.py ~3800+ lignes → routes modulaires)
- [ ] Refactoring frontend (sous-composants volumineux)
### P1
- [ ] Génération PDF des modèles de CV
- [ ] Quiz d'orientation basé sur l'explorateur
- [ ] Ateliers de Codéveloppement
- [ ] Micro-titres/badges
### P2
- [ ] CCSP diagnostic approfondi
- [ ] Soft Skills/Valeurs auto-évaluation
- [ ] Export PDF passeport, mode sombre
