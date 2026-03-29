# Re'Actif Pro - PRD

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + Recharts
- Backend: FastAPI + MongoDB (Motor async)
- Auth: Pseudonyme anonyme (JWT tokens)
- LLM: OpenAI GPT-5.2 via Emergent LLM Key

## Implémenté
- Design D'CLIC PRO, Auth, Analyse CV, Passeport, Coffre-fort (UI base)
- Observatoire, Job Matching, Formations, Explorateur
- CI/CD GitHub Actions -> OVH VPS
- 28/03: Fix compétence fantôme, accents, cache Évolution, filtres Job Matching
- 02/2026: Ubuntoo intégré nativement /ubuntoo (6 onglets), CSS complet style Re'Actif Pro
- 02/2026: Prompt Évolution IA personnalisé (skills_at_risk vs CV réel)
- 02/2026: Pipeline Ubuntoo <-> Observatoire (POST exchanges -> AI détection -> signaux)
- 02/2026: Sync profil Re'Actif Pro -> Ubuntoo (AI génère profil depuis CV/D'CLIC/Passeport)
- 03/2026: **Espace Partenaires de Parcours - Phase 1** :
  - Dashboard d'accompagnement multi-onglets (Tableau de bord, Bénéficiaires, Freins périphériques)
  - Inscription partenaire avec validation SIRET, type de structure, charte éthique ALT&ACT
  - Mécanisme de consentement RGPD (CGU + Politique de confidentialité)
  - Login pro par email (POST /api/auth/login-pro)
  - CRUD bénéficiaires avec progression, statut, notes, historique
  - Gestion des freins périphériques (8 catégories: logement, santé, mobilité, garde_enfant, handicap, administratif, financier, autre)
  - Suivi des compétences validées par bénéficiaire
  - Statistiques temps réel (taux d'insertion, freins actifs/résolus)
  - Backend dédié: /app/backend/routes/partenaires.py
  - Fix seed script (ne supprime plus les bénéficiaires)

## Backlog
- P1: Coffre-fort upload réel (fichiers libres)
- P2: Narratif IA D'CLIC PRO
- P2: FranceConnect
- P3: Ateliers Codéveloppement / Micro-badges
- Refactoring: DclicTestPage.jsx, ObservatoireView.jsx (>2000 lignes)

## Endpoints Partenaires
- POST /api/auth/register-partenaire (inscription structure)
- POST /api/auth/login-pro (connexion email)
- GET /api/partenaires/stats (statistiques dashboard)
- GET /api/partenaires/profile (profil structure)
- GET/POST/PUT/DELETE /api/partenaires/beneficiaires (CRUD)
- GET /api/partenaires/beneficiaires/{id} (détail)
- POST /api/partenaires/beneficiaires/{id}/freins (ajouter frein)
- PUT /api/partenaires/beneficiaires/{id}/freins/{fid} (résoudre)
- POST /api/partenaires/beneficiaires/{id}/skills (valider compétence)
