# Re'Actif Pro - PRD

## Problème original
Répliquer D'CLIC PRO, intégrer Ubuntoo, coffre-fort numérique, fonctionnalités IA.

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + Recharts
- Backend: FastAPI + MongoDB (Motor async)
- Auth: Pseudonyme anonyme (JWT tokens)
- LLM: OpenAI GPT-5.2 via Emergent LLM Key
- Déploiement: Nginx + systemd, GitHub Actions → OVH VPS

## Implémenté ✅
- Design D'CLIC PRO, Auth, Analyse CV, Passeport, Coffre-fort (UI base)
- Observatoire, Job Matching, Formations, Explorateur, Ubuntoo (base)
- CI/CD GitHub Actions → OVH VPS
- **27/03 Session** :
  - Fix production: processus zombie tué, EnvironmentFile systemd
  - Légende sources compétences (D'CLIC PRO vert, IA bleu, Centres rose)
  - Transfert CV → Coffre-fort (original + modèles IA)
  - Zone géographique + Distance km dans Job Matching
  - Cache IA pour page Évolution + bouton rafraîchir

## Bugs corrigés
- 26/03: Passerelles/Job Matching incohérents
- 27/03: CV 502 BadGateway → retry 5x + pdfplumber
- 27/03: Production zombie uvicorn éliminé
- 27/03: load_dotenv override=True restauré

## Backlog
- P1: Ubuntoo enrichi
- P2: Coffre-fort upload réel
- P3: Narratif IA, FranceConnect
- P4: Ateliers Codéveloppement / Micro-badges
- Refactoring: DclicTestPage.jsx, ObservatoireView.jsx (>2000 lignes)
