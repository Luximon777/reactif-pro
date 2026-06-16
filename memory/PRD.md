# RE'ACTIF PRO — PRD (Product Requirements Document)

## Problème Original
Plateforme full-stack "Ré'Actif Pro" basée sur l'analyse de compétences, avec une interface fidèle au site en production `reactif.pro`.

## Architecture
- Frontend: React + Tailwind + Shadcn (code extrait de prod via source maps)
- Backend: FastAPI (server.py ~5200 lignes) + MongoDB (db: test_database)
- IA: OpenAI GPT-5.2 via Emergent LLM Key
- BDD Référentiel: **20 filières, 289 métiers**, compétences, qualités humaines

## Ce qui est implémenté
- [x] Landing Page (réplique exacte de prod)
- [x] AdminGate (gestion des accès admin/dev/invité)
- [x] Auth par pseudonyme (login/register)
- [x] Dashboard Espace Personnel
- [x] Analyse CV par IA (upload, extraction texte, analyse structurée)
- [x] Auto-remplissage Passeport de Compétences depuis CV
- [x] Frise Trajectoire (création auto des étapes depuis CV)
- [x] Audit CV 10 critères avec score global
- [x] Synthèse Trajectoire (/trajectory/synthesis)
- [x] Coach RE'ACTIF virtuel avec suivi des étapes
- [x] **OPC complet avec BDD pyramidale** (16 juin 2026)
  - 20 filières × secteurs → 289 métiers avec missions, SF, SE, CT
  - Recherche cascade: Filière → Secteur → Métier → Résultats pyramidaux
  - Recherche textuelle: "comptable" → 33 résultats (filières, métiers, savoir-être, capacités)
  - Seed scripts: seed_filieres.py (ODS import) + seed_all_metiers.py (métiers détaillés)
- [x] Espace Employeurs (Cockpit RH)
- [x] Appui aux Parcours (Interface partenaires)
- [x] 20+ endpoints backend OPC/Observatoire/Entreprise/Partenaires

## Backlog
- P1: Refactoring server.py (monolithe > 5200 lignes)
- P2: Export PDF des 4 modèles de CV
- P2: Tableau de bord Admin avec statistiques d'usage
- P3: Soft Skills (CSE), Valeurs (VIA), Diagnostic CCSP
- P3: Ateliers Codéveloppement, Micro-titres/badges
