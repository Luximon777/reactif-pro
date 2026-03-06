# DE'CLIC PRO & RE'ACTIF PRO - PRD

## Projets

### 1. DE'CLIC PRO
Plateforme d'orientation professionnelle guidant les utilisateurs à travers un questionnaire multi-modèles (MBTI, DISC, Ennéagramme, RIASEC, Archéologie des Compétences) pour déterminer leur profil de personnalité et recommander des métiers compatibles.

**URL**: https://profil-emploi.preview.emergentagent.com

### 2. RE'ACTIF PRO (NOUVEAU)
Plateforme d'accompagnement professionnel personnalisé avec 3 espaces :
- **Mon Espace Pro** : Compte pseudonyme confidentiel (actif)
- **Entreprise RH** : Espace professionnels RH (à venir)
- **Partenaires Sociaux** : Consultation et collaboration (à venir)

**URL**: https://profil-emploi.preview.emergentagent.com/reactif-pro

---

## Ce qui a été implémenté

### Mars 2026 (Session actuelle)

#### RE'ACTIF PRO - Création du projet ✅
- [x] **Page d'accueil RE'ACTIF PRO** avec 3 cartes d'accès
- [x] **Système d'authentification pseudonyme** :
  - Inscription sans identité civile obligatoire
  - Pseudo + mot de passe obligatoires
  - Email de récupération facultatif
  - Code d'accès DE'CLIC PRO facultatif pour récupérer les résultats
  - Consentements CGU/Confidentialité/Marketing
- [x] **Backend FastAPI** :
  - Collection MongoDB `reactif_users`, `reactif_profiles`, `reactif_user_data`, `reactif_audit_logs`
  - Authentification JWT (tokens 7 jours)
  - Hash mot de passe SHA-256 + salt
  - Routes `/api/reactif/auth/register`, `/api/reactif/auth/login`
  - Routes `/api/reactif/user/profile`, `/api/reactif/user/results`
  - Export données RGPD `/api/reactif/user/export-data`
  - Suppression compte `/api/reactif/user/account`
- [x] **Dashboard utilisateur** avec navigation sidebar
- [x] **Intégration DE'CLIC PRO** :
  - Génération code d'accès XXXX-XXXX après test
  - Endpoint `/api/retrieve-results` pour récupérer résultats
  - Import automatique des résultats lors de l'inscription RE'ACTIF PRO

#### DE'CLIC PRO - Améliorations ✅
- [x] **"Soft skills à développer"** affiche une liste spécifique (pas générique)
- [x] **Croisement Ennéagramme × Questions Vertus** (60% questions + 30% Ennéagramme + 10% CK1)
- [x] **Scoring filières amélioré** avec mapping RIASEC/Vertus/DISC/Ennéagramme
- [x] **Filières filtrées** (score >= 65% seulement)
- [x] **Code d'accès** généré et affiché après le test
- [x] **Section "Au-delà du diplôme"** sur page d'accueil
- [x] **Textes mis à jour** ("Avant d'envoyer ton CV", "Découvres tes possibilités", etc.)

---

## Architecture Technique

### Stack
- **Frontend**: React 18 + Tailwind CSS + Shadcn/UI
- **Backend**: FastAPI (Python)
- **Base de données**: MongoDB
- **Authentification**: JWT (RE'ACTIF PRO)

### Structure des fichiers clés
```
/app/
├── backend/
│   └── server.py           # API DE'CLIC PRO + RE'ACTIF PRO
├── frontend/src/
│   ├── App.js              # DE'CLIC PRO (monolithique)
│   ├── App.css             # Styles DE'CLIC PRO
│   └── pages/reactif-pro/
│       ├── ReactifProApp.jsx   # Application RE'ACTIF PRO
│       └── ReactifPro.css      # Styles RE'ACTIF PRO
```

### Collections MongoDB RE'ACTIF PRO
- `reactif_users` : Authentification (pseudo, password_hash, email_recovery, consentements)
- `reactif_profiles` : Profil visible (display_name, visibility_level)
- `reactif_user_data` : Données métier (résultats DE'CLIC PRO, parcours, etc.)
- `reactif_audit_logs` : Journal d'audit minimal
- `test_results` : Résultats DE'CLIC PRO avec code d'accès

---

## Endpoints API

### DE'CLIC PRO
- `POST /api/job-match` - Matching métiers (retourne access_code)
- `POST /api/explore` - Exploration filières
- `POST /api/retrieve-results` - Récupérer résultats via code d'accès
- `GET /api/questionnaire` - Questions du questionnaire

### RE'ACTIF PRO
- `POST /api/reactif/auth/register` - Inscription
- `POST /api/reactif/auth/login` - Connexion
- `GET /api/reactif/user/profile` - Profil utilisateur
- `GET /api/reactif/user/results` - Résultats DE'CLIC PRO
- `POST /api/reactif/user/import-results` - Import via code
- `GET /api/reactif/user/export-data` - Export RGPD
- `DELETE /api/reactif/user/account` - Supprimer compte

---

## Prochaines tâches (P1)

### RE'ACTIF PRO
- [ ] Dashboard avec statistiques réelles
- [ ] Passation questionnaire depuis l'espace pro
- [ ] Gestion projets professionnels
- [ ] Plan d'action personnalisé
- [ ] Espace "Entreprise RH"
- [ ] Espace "Partenaires Sociaux"

### DE'CLIC PRO
- [ ] Export PDF de la carte d'identité Pro
- [ ] Partage sur réseaux sociaux
- [ ] Refactoring backend (modularisation)
- [ ] Refactoring frontend (composants)

---

## Backlog (P2)
- Dashboard administrateur
- API France Travail (bloquée - erreur 403 externe)
- Notifications email
- Historique des questionnaires
- Système de badges/gamification

---

## Conformité RGPD/AI Act

### RE'ACTIF PRO respecte :
- ✅ Compte pseudonyme (pas d'identité civile obligatoire)
- ✅ Email facultatif
- ✅ Consentements explicites (CGU, Confidentialité, Marketing)
- ✅ Droit à l'export des données
- ✅ Droit à la suppression du compte
- ✅ Données séparées (auth vs métier)
- ✅ Journal d'audit minimal
