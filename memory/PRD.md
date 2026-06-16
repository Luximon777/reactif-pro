# RE'ACTIF PRO — PRD (Product Requirements Document)

## Problème Original
Plateforme full-stack "Ré'Actif Pro" basée sur l'analyse de compétences, avec une interface fidèle au site en production `reactif.pro`.

## Utilisateurs
- Particuliers (chercheurs d'emploi en reconversion)
- Employeurs / RH
- Partenaires / Accompagnateurs
- Administrateurs

## Exigences Core
1. Page d'accueil avec 5 accès (Espace Personnel, Parcours VSI, OPC, Espace Employeurs, Appui aux parcours)
2. Observatoire Prédictif des Compétences (OPC) fonctionnel avec BDD pyramidale
3. Analyse de CV par IA (upload base64, auto-remplissage passeport + frise Trajectoire + Audit)
4. Authentification par pseudonyme
5. Coach RE'ACTIF virtuel interactif

## Architecture
- Frontend: React + Tailwind + Shadcn (code extrait de prod via source maps)
- Backend: FastAPI (server.py monolithe ~5200 lignes) + MongoDB (db: test_database)
- IA: OpenAI GPT-5.2 via Emergent LLM Key
- BDD Référentiel: 20 filières, 69 métiers (SI), 13 fiches compétences, 12 qualités humaines

## Ce qui est implémenté
- [x] Landing Page (réplique exacte de prod) — Fait
- [x] AdminGate (gestion des accès admin/dev/invité) — Fait
- [x] Auth par pseudonyme (login/register) — Fait
- [x] Dashboard Espace Personnel (navigation interne) — Fait
- [x] Analyse CV par IA (upload, extraction texte, analyse structurée) — Fait
- [x] Auto-remplissage Passeport de Compétences depuis CV — Fait
- [x] Frise Trajectoire (création auto des étapes depuis CV) — Fait
- [x] Audit CV 10 critères avec score global — Fait (16 juin 2026)
- [x] Synthèse Trajectoire (endpoint /trajectory/synthesis) — Fait (16 juin 2026)
- [x] Coach RE'ACTIF virtuel avec suivi des étapes — Fait
- [x] **OPC complet avec BDD pyramidale** — Fait (16 juin 2026)
  - Import BDD: 20 filières, 69 métiers, compétences, qualités humaines (ODS → MongoDB)
  - Recherche en cascade: Filière → Secteur → Métier → Résultats pyramidaux
  - Résultats affichent: Métiers + Missions, Savoir-être + Qualités humaines, Capacités techniques + Savoir-faire
  - Fix redirect OPC via AdminGate (localStorage postAuthRedirect)
  - 20+ endpoints backend créés (observatory, referentiel, entreprise, partenaires, etc.)
- [x] Espace Employeurs (Cockpit RH) — Fait
- [x] Appui aux Parcours (Interface partenaires) — Fait

## Backlog
- P1: Refactoring server.py (monolithe > 5200 lignes) en routes modulaires
- P2: Export PDF des 4 modèles de CV
- P2: Tableau de bord Admin avec statistiques d'usage
- P2: Compléter les données des 19 autres filières (seule SI a des métiers détaillés)
- P3: Modules Soft Skills (CSE) et Valeurs (VIA)
- P3: Diagnostic fonctionnel CCSP
- P3: Ateliers Codéveloppement
- P3: Micro-titres/badges

## Endpoints API clés
- POST /api/auth/login, /api/auth/login-pro, /api/auth/register
- POST /api/cv/analyze-text, GET /api/cv/latest-analysis, GET /api/cv/models, GET /api/cv/centres-interet
- GET /api/trajectory/steps, GET /api/trajectory/synthesis, POST /api/trajectory/share
- GET /api/coach/progress
- GET /api/admin/gate-state, POST /api/admin/gate-state
- GET /api/referentiel/filieres, GET /api/referentiel/metiers, GET /api/referentiel/search, GET /api/referentiel/contexte
- GET /api/referentiel/rome/domaines, GET /api/referentiel/rome/metiers, GET /api/referentiel/actualisation/status
- GET /api/observatory/dashboard, /api/observatory/predictions
- GET /api/competences/emergentes, /api/metiers/tension, /api/trajectoires
- GET /api/entreprise/dashboard|profile, POST /api/entreprise/seed-demo
- GET /api/partenaires/stats|alertes|demande-acces/status

## DB Collections (test_database)
- tokens, users, profiles, passports
- cv_jobs, cv_models, cv_centres_interet
- trajectory_steps, trajectory_synthesis, trajectory_shares
- opc_filieres (20 filières), opc_metiers (69 métiers détaillés), opc_qualites (12 qualités)
- admin_config, notifications, emerging_skills
