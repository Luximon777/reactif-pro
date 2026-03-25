# Re'Actif Pro - PRD

## Problème original
Répliquer le design D'CLIC PRO, intégrer l'espace communautaire Ubuntoo, mettre en place un coffre-fort numérique.

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + Recharts
- Backend: FastAPI + MongoDB (Motor)
- Auth: Pseudonyme anonyme
- LLM: OpenAI GPT-5.2 via Emergent LLM Key
- Déploiement: Nginx, Let's Encrypt, GitHub Actions vers VPS OVH

## Ce qui a été implémenté

### Design D'CLIC PRO (DONE)
- Thème sombre, cartes glassmorphiques, 26 questions
- Graphiques radar Recharts (Tripartite, DISC, Archéologie)
- Tooltips de définitions, images contextuelles
- Boutons de validation du rapport

### Import D'CLIC → Dashboard (DONE - fixé 25/03/2026)
- Retrieve par code d'accès (MBTI, DISC, RIASEC, Vertus)
- Sauvegarde complète dans le profil utilisateur
- Barre de progression animée
- Claim du code

### Bugs corrigés (25/03/2026)
- `DclicTestPage.jsx`: Import API partagé depuis `@/App` (évite `undefined/api/...` en prod)
- `Dashboard.jsx`: `profileId` manquant dans la déstructuration `useAuth()` → crash à l'import
- `models.py`: `dclic_profile` manquant dans `DclicProImport` → `AttributeError` backend
- `helpers.py`: Retry LLM augmenté (3 tentatives + backoff exponentiel)
- `cv.py`: `asyncio.gather` avec `return_exceptions=True` pour résilience
- `ParticulierView.jsx`: Ouverture D'CLIC en nouvel onglet

### Reconstruction VPS OVH (DONE)
- Nginx, SSL Let's Encrypt, MongoDB migré sur /data (75Go)

## Backlog priorité

### P0 - Déploiement GitHub Actions
- Le secret `VPS_SSH_KEY` doit être mis à jour par l'utilisateur sur GitHub

### P1 - Espace communautaire Ubuntoo
- À implémenter

### P2 - Coffre-fort numérique
- Upload de fichiers pour preuves de compétences

### P3 - Narratif IA personnalisé
- Génération IA en fin de test D'CLIC PRO

### P3 - FranceConnect / CCSP
- Intégration diagnostic CCSP

### P4 - Ateliers Codéveloppement / Micro-badges
- Système de badges et ateliers

## API Endpoints clés
- POST /api/auth/register, /api/auth/login
- POST /api/dclic/retrieve - Récupère profil par code
- POST /api/dclic/claim - Marque code comme utilisé
- POST /api/profile/import-dclic - Import complet dans profil
- POST /api/cv/analyze-text - Analyse CV par texte
- GET /api/cv/analyze/status - Polling résultat CV

## DB Schema clés
- profiles: pseudo, token_id, dclic_imported, dclic_mbti, dclic_disc, etc.
- dclic_results: access_code, is_claimed, answers, profile
- cv_jobs: job_id, status, step, error, result
- passports: token_id, competences, formations
