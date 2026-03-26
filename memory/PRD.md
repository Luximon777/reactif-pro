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

### Import D'CLIC → Dashboard (DONE)
- Retrieve par code d'accès (MBTI, DISC, RIASEC, Vertus)
- Sauvegarde complète dans le profil utilisateur
- Barre de progression animée
- Claim du code

### Analyse CV Interactive (DONE)
- Upload CV (PDF, DOCX, TXT) avec analyse IA
- Extraction centres d'intérêt via formulaire IA
- CV optimisé multi-modèles (classique)
- Compétences clés, savoir-faire, savoir-être

### Auto-évaluation CCSP (DONE)
- Endpoint /api/passport/auto-evaluate (43 compétences IA)
- Remplacement de l'évaluation manuelle

### Observatoire des compétences (DONE)
- Chargement asynchrone (bouton)
- Onglet "Détectées CV" avec matching contextuel

### Passerelles & Job Matching (DONE - fixé 26/03/2026)
- Fix critique: le titre du CV optimisé est maintenant la référence principale
- Séparation compétences techniques vs transférables dans les prompts IA
- Passerelles cohérentes avec le métier actuel du CV

### Bugs corrigés (25-26/03/2026)
- Passerelles incohérentes: proposaient des métiers basés sur compétences transférables anciennes au lieu du métier actuel du CV
- Job Matching: même problème corrigé, priorise compétences_cles et savoir_faire technique

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
- GET /api/passport/passerelles - Passerelles IA (fixé: priorise titre CV)
- GET /api/jobs/matching - Job matching IA (fixé: priorise métier actuel)

## DB Schema clés
- profiles: pseudo, token_id, dclic_imported, dclic_mbti, dclic_disc, etc.
- dclic_results: access_code, is_claimed, answers, profile
- cv_jobs: job_id, status, step, error, result
- cv_models: token_id, models (classique avec titre, competences_cles, savoir_faire)
- passports: token_id, competences, formations, passerelles
