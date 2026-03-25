# Re'Actif Pro - PRD

## Problème original
Application web Ré'Actif Pro intégrant le questionnaire D'CLIC PRO pour l'accompagnement professionnel.

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn/UI
- **Backend**: FastAPI + Python
- **Base de données**: MongoDB
- **Déploiement**: Emergent -> GitHub -> OVH (automatisé via GitHub Actions)
- **VPS OVH**: 51.91.124.85, Debian 12, nginx + certbot SSL, MongoDB 7.0, données sur /data (75 Go)

## Fonctionnalités implémentées

### Questionnaire D'CLIC PRO (Complet)
- 26 questions visuelles avec images uniques (64 images, 0 doublons)
- Thème sombre (#1e3a5f) fidèle au projet original
- Logo SVG animé, cartes glassmorphiques, boutons dégradés
- Résultats en 10 sections avec tooltips au survol
- Section "Profil Comportemental" avec graphiques radar (Tripartite, DISC, Archéologie)
- Section "Archéologie des Compétences" (GSCA) avec Cognition/Conation/Affection + Valeurs Schwartz/Forces Seligman/Savoirs-être France Travail
- Disclaimer légal sur la page de résultats
- Boutons: "Valider le rapport" → "Générer dans votre espace personnel" + "Refaire le test"

### Import D'CLIC PRO dans profil (Complet - 25 Mar 2026)
- Bouton mis en valeur (dégradé + animation pulse)
- Import enrichi: stocke MBTI, DISC, RIASEC, Vertus, compétences, vigilances
- Modale de saisie du code d'accès avec prévisualisation

### Dashboard & Profils (Complet)
- Menu nettoyé, police augmentée
- Logo Re'Actif Pro intégré aux CV (PDF/DOCX)

### Déploiement OVH (Complet - 25 Mar 2026)
- Serveur configuré: nginx + SSL Let's Encrypt + MongoDB + FastAPI systemd
- Pipeline GitHub Actions avec clé SSH ED25519

## Backlog prioritisé

### P1 - Génération CV depuis Carte d'Identité Pro (si pas de CV)
- Si l'utilisateur n'a pas de CV, générer un CV basé sur la Carte d'Identité Pro

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
- `POST /api/profile/import-dclic` - Import enrichi dans profil utilisateur
- `POST /api/dclic/retrieve` - Vérifier un code et prévisualiser
- `POST /api/dclic/claim` - Associer un résultat à un utilisateur
