# Re'Actif Pro - PRD

## Probl\u00e8me original
R\u00e9pliquer D'CLIC PRO, int\u00e9grer Ubuntoo, coffre-fort num\u00e9rique, fonctionnalit\u00e9s IA.

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + Recharts
- Backend: FastAPI + MongoDB (Motor async)
- Auth: Pseudonyme anonyme (JWT tokens)
- LLM: OpenAI GPT-5.2 via Emergent LLM Key
- D\u00e9ploiement: Nginx + systemd, GitHub Actions \u2192 OVH VPS

## Impl\u00e9ment\u00e9
- Design D'CLIC PRO, Auth, Analyse CV, Passeport, Coffre-fort (UI base)
- Observatoire, Job Matching, Formations, Explorateur, Ubuntoo (base)
- CI/CD GitHub Actions \u2192 OVH VPS
- 27/03: Fix production zombie uvicorn, l\u00e9gende sources comp\u00e9tences, transfert CV coffre-fort, zone g\u00e9ographique + distance km, cache \u00c9volution
- 28/03: Fix comp\u00e9tence fant\u00f4me (filtrage sources valides), accents manquants CvAnalysisSection, cache \u00c9volution avec hash comp\u00e9tences, ajout filtres lieu de r\u00e9sidence et estimation salaire dans Job Matching
- 28/03: Ubuntoo int\u00e9gr\u00e9 nativement en route standalone /ubuntoo (6 onglets)
- 02/2026: Ubuntoo stylis\u00e9 avec CSS complet (hover translateY, gradients arc-en-ciel, tooltip Ubuntu, cartes glassmorphiques)
- 02/2026: Prompt \u00c9volution IA am\u00e9lior\u00e9 (personnalisation stricte, comp\u00e9tences du CV, formations r\u00e9elles)
- 02/2026: Pipeline Ubuntoo \u2194 Observatoire connect\u00e9 :
  - GET/POST /api/ubuntoo/community/exchanges (chargement dynamique + publication)
  - Analyse IA automatique (GPT-5.2) de chaque \u00e9change pour d\u00e9tecter comp\u00e9tences/outils/pratiques
  - Signaux d\u00e9tect\u00e9s automatiquement int\u00e9gr\u00e9s dans l'Observatoire Pr\u00e9dictif
  - Frontend dynamique (Discussions et Groupes chargent depuis DB, formulaire de publication avec feedback IA)
  - Lien "Ouvrir Ubuntoo" dans Observatoire corrig\u00e9 (\u2192 /ubuntoo)

## Bugs corrig\u00e9s
- 26/03: Passerelles/Job Matching incoh\u00e9rents
- 27/03: CV 502 BadGateway, production zombie uvicorn, load_dotenv override
- 28/03: Comp\u00e9tence fant\u00f4me espace personnel (filtrage par source)
- 28/03: Accents manquants CvAnalysisSection
- 28/03: Cache \u00c9volution non invalid\u00e9 lors de changement de profil
- 02/2026: \u00c9volution IA g\u00e9n\u00e9rique \u2192 personnalis\u00e9e (skills_at_risk vs CV r\u00e9el)

## Backlog
- P2: Coffre-fort upload r\u00e9el (fichiers libres utilisateur)
- P3: Narratif IA D'CLIC PRO, FranceConnect
- P4: Ateliers Cod\u00e9veloppement / Micro-badges
- Refactoring: DclicTestPage.jsx, ObservatoireView.jsx (>2000 lignes)
