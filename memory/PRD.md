# Re'Actif Pro - PRD

## Problème original
Répliquer D'CLIC PRO, intégrer Ubuntoo, coffre-fort numérique, fonctionnalités IA.

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + Recharts
- Backend: FastAPI + MongoDB (Motor async)
- Auth: Pseudonyme anonyme (JWT tokens)
- LLM: OpenAI GPT-5.2 via Emergent LLM Key
- Déploiement: Nginx + systemd, GitHub Actions → OVH VPS

## Implémenté
- Design D'CLIC PRO, Auth, Analyse CV, Passeport, Coffre-fort (UI base)
- Observatoire, Job Matching, Formations, Explorateur, Ubuntoo (base)
- CI/CD GitHub Actions → OVH VPS
- 27/03: Fix production zombie uvicorn, légende sources compétences, transfert CV coffre-fort, zone géographique + distance km, cache Évolution
- 28/03: Fix compétence fantôme (filtrage sources valides), accents manquants CvAnalysisSection, cache Évolution avec hash compétences, ajout filtres lieu de résidence et estimation salaire dans Job Matching

## Bugs corrigés
- 26/03: Passerelles/Job Matching incohérents
- 27/03: CV 502 BadGateway, production zombie uvicorn, load_dotenv override
- 28/03: Compétence fantôme espace personnel (filtrage par source)
- 28/03: Accents manquants CvAnalysisSection (critères, complété, données, Sélectionnez, modèle, etc.)
- 28/03: Cache Évolution non invalidé lors de changement de profil (ajout skills_hash)

## Backlog
- P1: Contenu Évolution plus pertinent (prompt IA amélioré, à valider par l'utilisateur)
- P1: Ubuntoo enrichi
- P2: Coffre-fort upload réel (fichiers libres utilisateur)
- P3: Narratif IA D'CLIC PRO, FranceConnect
- P4: Ateliers Codéveloppement / Micro-badges
- Refactoring: DclicTestPage.jsx, ObservatoireView.jsx (>2000 lignes)
