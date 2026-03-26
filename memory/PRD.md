# Re'Actif Pro - PRD

## Problème original
Répliquer le design D'CLIC PRO, intégrer l'espace communautaire Ubuntoo, mettre en place un coffre-fort numérique, et assurer le bon fonctionnement de toutes les fonctionnalités d'analyse IA.

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + Recharts
- Backend: FastAPI + MongoDB (Motor async)
- Auth: Pseudonyme anonyme (JWT tokens)
- LLM: OpenAI GPT-5.2 via Emergent LLM Key
- Déploiement: Nginx, Let's Encrypt, GitHub Actions vers VPS OVH

## Ce qui a été implémenté (complet et testé)

### Design D'CLIC PRO ✅
- Thème sombre (#1e3a5f), cartes glassmorphiques, 26 questions avec images
- Graphiques radar Recharts (Tripartite, DISC, Archéologie)
- Code d'accès XXXX-XXXX avec résultats DISC/MBTI/RIASEC/Vertus

### Système d'authentification ✅
- Register/Login/Logout/Reconnexion avec pseudonyme
- Changement de mot de passe
- Export de données personnelles
- Niveaux de visibilité (Privé/Limité/Public)

### Import D'CLIC → Dashboard ✅
- Retrieve par code d'accès
- Import complet dans le profil utilisateur

### Analyse CV Interactive ✅
- Upload CV (PDF, DOCX, TXT) avec analyse IA
- Extraction centres d'intérêt via formulaire IA
- CV optimisé multi-modèles

### Passeport de Compétences ✅ (8 sous-onglets)
- Profil, Compétences, Évaluation, Archéologie, Émergentes, Expériences, Passerelles, Profil Dynamique
- Auto-évaluation CCSP IA (43 compétences)
- Passerelles IA corrigées (priorise titre CV métier actuel)
- Partage de passeport par lien

### Coffre-fort Numérique ✅ (UI de base)
- CRUD documents avec catégories
- Recherche et filtres

### Observatoire des Compétences ✅
- Tendances sectorielles, compétences émergentes
- Onglet "Détectées CV" avec matching contextuel

### Job Matching ✅
- Matching IA basé sur profil CV réel
- Filtres de recherche

### Autres ✅
- Formations (modules IA personnalisés)
- Explorateur de métiers (ISCO + IA)
- Index d'évolution
- Ubuntoo (interface communautaire de base)
- Responsive mobile

## Bugs corrigés (26/03/2026)
- Passerelles incohérentes : proposaient "Consultant en évolution pro" pour un Concierge → Corrigé (priorise titre CV)
- Job Matching : même problème → Corrigé (filtre savoir_faire par catégorie)

## Test de régression complet (26/03/2026)
- 40+ endpoints backend : 100% OK
- Frontend E2E complet : 100% OK
- D'CLIC PRO 26 questions → submit → résultats : OK
- Auth complète : OK
- Responsive mobile : OK
- Rapport : /app/test_reports/iteration_38.json

## Backlog priorité

### P0 - Déploiement GitHub Actions
- BLOQUÉ : L'utilisateur doit mettre à jour `VPS_SSH_KEY` dans les settings GitHub

### P1 - Espace communautaire Ubuntoo
- Enrichir l'interface existante (forum, échanges, signaux)

### P2 - Coffre-fort numérique
- Upload réel de fichiers (preuves, attestations, diplômes)
- Stockage Object Storage

### P3 - Narratif IA personnalisé
- Génération IA en fin de test D'CLIC PRO

### P3 - FranceConnect
- Certification d'identité

### P4 - Ateliers Codéveloppement / Micro-badges
- Système de badges et ateliers collaboratifs

### Refactoring
- DclicTestPage.jsx (~2000 lignes) → scinder en composants
- ObservatoireView.jsx (~2000 lignes) → scinder en composants

## API Endpoints clés
- POST /api/auth/register, /api/auth/login, GET /api/auth/verify
- POST /api/dclic/submit, /api/dclic/retrieve, /api/dclic/claim
- POST /api/profile/import-dclic, PUT /api/profile
- POST /api/cv/analyze-text, GET /api/cv/models
- GET /api/passport, /api/passport/passerelles, /api/passport/diagnostic
- GET /api/coffre/documents, POST /api/coffre/documents
- GET /api/observatoire/dashboard, /api/observatoire/personalized
- GET /api/jobs/matching, GET /api/learning
- GET /api/ubuntoo/dashboard, /api/ubuntoo/signals

## DB Collections (36 total)
- profiles (579), tokens (579), passports (220)
- cv_models (73), cv_jobs (125), dclic_results (54)
- isco_metiers (5853), coffre_documents (3)
- emerging_skills (10), sector_trends (6)
- ubuntoo_signals (8), learning_modules_personalized (80)
