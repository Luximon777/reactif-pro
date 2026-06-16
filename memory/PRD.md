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
2. Observatoire Prédictif des Compétences (OPC) fonctionnel
3. Analyse de CV par IA (upload base64, auto-remplissage passeport + frise Trajectoire + Audit)
4. Authentification par pseudonyme
5. Coach RE'ACTIF virtuel interactif

## Architecture
- Frontend: React + Tailwind + Shadcn (code extrait de prod via source maps)
- Backend: FastAPI (server.py monolithe ~5000 lignes) + MongoDB (db: test_database)
- IA: OpenAI GPT-5.2 via Emergent LLM Key

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
- [x] OPC complet (Observatoire Prédictif des Compétences) — Fix 16 juin 2026
  - Fix AdminGate: redirect OPC via localStorage (postAuthRedirect async fix)
  - Endpoints ajoutés: observatory/dashboard, observatory/predictions, competences/emergentes, metiers/tension, trajectoires, referentiel/rome/domaines, referentiel/actualisation/status, entreprise/dashboard|profile|seed-demo, partenaires/stats|alertes|demande-acces
- [x] Espace Employeurs (Cockpit RH) — Fait
- [x] Appui aux Parcours (Interface partenaires) — Fait
- [x] Endpoints alias cv: /cv/latest-analysis, /cv/centres-interet — Fait (16 juin 2026)

## Backlog
- P1: Refactoring server.py (monolithe > 5000 lignes) en routes modulaires
- P2: Export PDF des 4 modèles de CV
- P2: Tableau de bord Admin avec statistiques d'usage
- P3: Modules Soft Skills (CSE) et Valeurs (VIA)
- P3: Diagnostic fonctionnel CCSP
- P3: Ateliers Codéveloppement
- P3: Micro-titres/badges

## Endpoints API clés
- POST /api/auth/login, /api/auth/login-pro, /api/auth/register
- POST /api/cv/analyze-text, GET /api/cv/latest-analysis, GET /api/cv/models
- GET /api/trajectory/steps, GET /api/trajectory/synthesis
- GET /api/coach/progress
- GET /api/admin/gate-state, POST /api/admin/gate-state
- GET /api/observatory/dashboard, /api/observatory/predictions
- GET /api/competences/emergentes, /api/metiers/tension, /api/trajectoires
- GET /api/referentiel/rome/domaines, /api/referentiel/actualisation/status
- GET /api/entreprise/dashboard|profile, POST /api/entreprise/seed-demo
- GET /api/partenaires/stats|alertes|demande-acces/status

## DB Collections (test_database)
- tokens, users, profiles, passports
- cv_jobs, cv_models, cv_centres_interet
- trajectory_steps, trajectory_synthesis, trajectory_shares
- admin_config, notifications
- referentiel_metiers, emerging_skills
