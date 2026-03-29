# Re'Actif Pro - PRD

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + Recharts
- Backend: FastAPI + MongoDB (Motor async)
- Auth: Pseudonyme anonyme (JWT tokens)
- LLM: OpenAI GPT-5.2 via Emergent LLM Key

## Impl\u00e9ment\u00e9
- Design D'CLIC PRO, Auth, Analyse CV, Passeport, Coffre-fort (UI base)
- Observatoire, Job Matching, Formations, Explorateur
- CI/CD GitHub Actions \u2192 OVH VPS
- 28/03: Fix comp\u00e9tence fant\u00f4me, accents, cache \u00c9volution, filtres Job Matching
- 02/2026: Ubuntoo int\u00e9gr\u00e9 nativement /ubuntoo (6 onglets), CSS complet style Re'Actif Pro
- 02/2026: Prompt \u00c9volution IA personnalis\u00e9 (skills_at_risk vs CV r\u00e9el)
- 02/2026: Pipeline Ubuntoo \u2194 Observatoire (POST exchanges \u2192 AI d\u00e9tection \u2192 signaux)
- 02/2026: Sync profil Re'Actif Pro \u2192 Ubuntoo :
  - GET /api/ubuntoo/profile (v\u00e9rifie si profil sync\u00e9)
  - POST /api/ubuntoo/sync-profile (AI g\u00e9n\u00e8re profil depuis CV/D'CLIC/Passeport)
  - Banni\u00e8re auto "Actualise ton espace" pour 1\u00e8re visite
  - Bouton "Re-synchroniser" pour mises \u00e0 jour
  - Profil sauvegard\u00e9 en base (collection ubuntoo_profiles)
  - Design refait style Re'Actif Pro (fond blanc, navy, cartes propres)

## Backlog
- P2: Coffre-fort upload r\u00e9el (fichiers libres)
- P3: Narratif IA D'CLIC PRO, FranceConnect
- P4: Ateliers Cod\u00e9veloppement / Micro-badges
- Refactoring: DclicTestPage.jsx, ObservatoireView.jsx (>2000 lignes)
