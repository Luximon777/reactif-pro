# Re'Actif Pro - PRD

## Problème original
Répliquer le design D'CLIC PRO, intégrer Ubuntoo, coffre-fort numérique, fonctionnalités IA.

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + Recharts
- Backend: FastAPI + MongoDB (Motor async)
- Auth: Pseudonyme anonyme (JWT tokens)
- LLM: OpenAI GPT-5.2 via Emergent LLM Key
- Déploiement: Nginx + systemd, GitHub Actions vers VPS OVH

## Ce qui a été implémenté ✅
- Design D'CLIC PRO (thème sombre, radar, glassmorphic)
- Authentification pseudonyme
- Analyse CV complète (audit, extraction, offres emploi, centres intérêt)
- Retry LLM (5 tentatives, backoff exponentiel)
- Extraction PDF robuste (PyPDF2 + pdfplumber)
- Passeport de Compétences (8 sous-onglets)
- Coffre-fort Numérique (UI base)
- Observatoire, Job Matching, Formations, Explorateur
- Ubuntoo (interface base)
- CI/CD GitHub Actions → OVH VPS

## Bugs corrigés
- 26/03: Passerelles/Job Matching incohérents
- 27/03: CV erreur 502 BadGateway + EOF PDF → retry + pdfplumber
- 27/03: Production `load_dotenv(override=False)` → corrigé `override=True`
- 27/03: **CRITIQUE** Processus uvicorn zombie sur `/home/ubuntu/reactif-pro/backend/` bloquait le port 8000 avec du vieux code → éliminé via `fuser -k 8000/tcp` dans deploy.yml
- 27/03: Deploy.yml: `EnvironmentFile` au lieu de `Environment=` individuels dans systemd

## Backlog
- P1: Ubuntoo enrichi
- P2: Coffre-fort upload fichiers réel
- P3: Narratif IA, FranceConnect
- P4: Ateliers Codéveloppement / Micro-badges
- Refactoring: DclicTestPage.jsx, ObservatoireView.jsx (>2000 lignes)
