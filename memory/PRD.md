# Re'Actif Pro - PRD

## Problème original
Répliquer le design D'CLIC PRO, intégrer l'espace communautaire Ubuntoo, mettre en place un coffre-fort numérique, et assurer le bon fonctionnement de toutes les fonctionnalités d'analyse IA.

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + Recharts
- Backend: FastAPI + MongoDB (Motor async)
- Auth: Pseudonyme anonyme (JWT tokens)
- LLM: OpenAI GPT-5.2 via Emergent LLM Key
- Déploiement: Nginx, Let's Encrypt, GitHub Actions vers VPS OVH

## Ce qui a été implémenté

### Design D'CLIC PRO ✅
- Thème sombre (#1e3a5f), cartes glassmorphiques, 26 questions avec images
- Graphiques radar Recharts (Tripartite, DISC, Archéologie)

### Authentification ✅
- Register/Login/Logout avec pseudonyme, changement mdp, export données

### Analyse CV ✅ (corrigé 27/03/2026)
- Upload CV (PDF, DOCX, TXT) avec analyse IA
- Retry amélioré : 5 tentatives + backoff exponentiel
- Extraction PDF robuste (PyPDF2 + pdfplumber fallback)
- Résilience post-traitement (sections indépendantes)
- Messages d'erreur frontend spécifiques (502, fichier illisible, crédit)
- Audit 10 critères, extraction compétences, offres emploi, centres intérêt
- Génération 4 modèles CV optimisés (DOCX + PDF)

### Passeport de Compétences ✅
- 8 sous-onglets, Auto-évaluation CCSP IA, Passerelles IA corrigées

### Coffre-fort Numérique ✅ (UI de base)
### Observatoire des Compétences ✅
### Job Matching ✅
### Formations ✅
### Explorateur de métiers ✅
### Ubuntoo (interface de base) ✅

## Bugs corrigés
- 26/03/2026: Passerelles/Job Matching incohérents → Corrigé
- 27/03/2026: Analyse CV erreur 502 BadGateway + EOF PDF → Corrigé (retry + pdfplumber + résilience)

## Deployment Readiness (27/03/2026)
- ✅ load_dotenv(override=False) corrigé
- ✅ .gitignore nettoyé (pas de blocage .env)
- ✅ URLs hardcodées supprimées (process.env.REACT_APP_BACKEND_URL)
- ✅ Deployment agent: PASS

## Backlog

### P0 - Production
- Déployer corrections via Save to GitHub
- Variable EMERGENT_LLM_KEY en production

### P1 - Ubuntoo
- Enrichir l'interface communautaire

### P2 - Coffre-fort numérique
- Upload réel de fichiers

### P3 - Narratif IA / FranceConnect
### P4 - Ateliers Codéveloppement / Micro-badges
### Refactoring - DclicTestPage.jsx, ObservatoireView.jsx
