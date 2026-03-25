# Re'Actif Pro - PRD

## Problème original
Application web Ré'Actif Pro intégrant le questionnaire D'CLIC PRO pour l'accompagnement professionnel des individus.

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn/UI
- **Backend**: FastAPI + Python
- **Base de données**: MongoDB
- **Déploiement**: Emergent -> GitHub -> OVH (automatisé)

## Fonctionnalités implémentées

### Questionnaire D'CLIC PRO (Complet)
- 26 questions visuelles avec images uniques (64 images, 0 doublons)
- Moteur backend `dclic_engine.py` (~6700 lignes)
- Calcul de profil (MBTI, DISC, RIASEC, Vertus, Ennéagramme)
- Page de résultats avec 9 sections (Archéologie, Boussole, Analyse Intégrée, RIASEC, Vertus, Pistes d'Action, Analyse Croisée, Cadran d'Ofman, Carte d'Identité Pro)
- Système de code d'accès (XXXX-XXXX) avec import dans profil Ré'Actif Pro

### Design D'CLIC PRO (Complet - 22 Jan 2026)
- Thème sombre (#1e3a5f) fidèle au projet original GitHub
- Logo SVG animé D'CLIC PRO
- Cartes glassmorphiques avec backdrop-blur
- Boutons dégradés bleu-vert (#4f6df5 → #10b981)
- Barre de progression dégradée
- Navigation sidebar sombre avec 9 sections
- 16 doublons d'images remplacés par des images Pexels uniques

### Dashboard & Profils (Complet)
- Menu nettoyé, police augmentée
- Modale d'import de code D'CLIC PRO
- Logo Re'Actif Pro intégré aux CV (PDF/DOCX)

## Backlog prioritisé

### P1 - Espace communautaire Ubuntoo
- Intégration de l'espace communautaire

### P2 - Coffre-fort numérique
- Upload réel de fichiers pour les preuves

### P3 - Narratif IA personnalisé
- Génération IA de narratif à la fin des résultats D'CLIC PRO

### P3 - FranceConnect / CCSP
- Intégrer FranceConnect et diagnostic basé sur le CCSP

### P4 - Codéveloppement
- Ateliers de Codéveloppement et micro-titres/badges

## Endpoints API clés
- `GET /api/dclic/questionnaire` - Liste des 26 questions
- `POST /api/dclic/submit` - Soumission et calcul de profil
- `GET /api/dclic/result/{access_code}` - Récupération par code
- `POST /api/profile/import-dclic` - Import dans profil utilisateur

## Fichiers de référence
- `/app/backend/dclic_engine.py` - Moteur logique D'CLIC PRO
- `/app/backend/routes/dclic.py` - Endpoints API
- `/app/frontend/src/pages/DclicTestPage.jsx` - UI questionnaire (thème sombre)
- `/app/frontend/src/pages/Dashboard.jsx` - Dashboard principal
