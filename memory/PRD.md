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
- Analyse CV complète (audit 10 critères, extraction, offres emploi, centres intérêt)
- Retry LLM amélioré (5 tentatives, backoff exponentiel)
- Extraction PDF robuste (PyPDF2 + pdfplumber fallback)
- Passeport de Compétences (8 sous-onglets)
- Coffre-fort Numérique (UI base)
- Observatoire des Compétences
- Job Matching IA
- Formations, Explorateur métiers
- Ubuntoo (interface base)

## Bugs corrigés
- 26/03: Passerelles/Job Matching incohérents
- 27/03: CV erreur 502 BadGateway + EOF PDF → retry + pdfplumber
- 27/03: **CRITIQUE** - Production `load_dotenv(override=False)` cassait la clé LLM → corrigé avec `override=True`

## Backlog
- P0: Vérifier production post-deploy
- P1: Ubuntoo enrichi
- P2: Coffre-fort upload fichiers
- P3: Narratif IA, FranceConnect
- P4: Ateliers Codéveloppement / Micro-badges
- Refactoring: DclicTestPage.jsx, ObservatoireView.jsx (>2000 lignes)
