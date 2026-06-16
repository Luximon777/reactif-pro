# RE'ACTIF PRO — PRD (Product Requirements Document)

## Problème Original
Plateforme full-stack "Ré'Actif Pro" basée sur l'analyse de compétences, avec une interface fidèle au site en production `reactif.pro`.

## Architecture
- Frontend: React + Tailwind + Shadcn (code extrait de prod via source maps)
- Backend: FastAPI (server.py ~5250 lignes) + MongoDB (db: test_database)
- IA: OpenAI GPT-5.2 via Emergent LLM Key
- **API France Travail** : ROME 4.0 (1 911 fiches métiers, 14 grands domaines)
- BDD Référentiel interne: 20 filières, 289 métiers

## Ce qui est implémenté
- [x] Landing Page (réplique exacte de prod)
- [x] AdminGate (accès admin/dev/invité)
- [x] Auth par pseudonyme (login/register)
- [x] Dashboard Espace Personnel
- [x] Analyse CV par IA + auto-remplissage Passeport + Trajectoire + Audit CV
- [x] Coach RE'ACTIF virtuel avec suivi des étapes
- [x] **OPC complet** (16 juin 2026)
  - BDD pyramidale interne: 20 filières × secteurs → 289 métiers (SF, SE, CT)
  - **API France Travail ROME 4.0** : 1 911 fiches officielles importées (14 grands domaines A-N)
  - Recherche en cascade: Filière → Secteur → Métier → Résultats pyramidaux
  - Onglet ROME : Grand domaine → Fiches ROME avec codes M1203, M1211, etc.
  - Recherche textuelle multi-source ("comptable" → 40 résultats interne+ROME)
- [x] Espace Employeurs (Cockpit RH)
- [x] Appui aux Parcours (Interface partenaires)
- [x] Synthèse Trajectoire + 20+ endpoints backend

## Intégrations 3rd Party
- OpenAI GPT-5.2 via Emergent LLM Key (analyse CV)
- **France Travail API** (ROME 4.0) — Client ID + Secret dans .env

## Backlog
- P1: Refactoring server.py (monolithe > 5250 lignes)
- P2: Export PDF des 4 modèles de CV
- P2: Tableau de bord Admin avec statistiques d'usage
- P3: Soft Skills (CSE), Valeurs (VIA), Diagnostic CCSP
- P3: Ateliers Codéveloppement, Micro-titres/badges
