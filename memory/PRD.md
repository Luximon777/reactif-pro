# DE'CLIC PRO - PRD (Product Requirements Document)

## Énoncé du problème original
Créer le site DE'CLIC PRO - Intelligence Professionnelle, une plateforme de découverte de potentiel professionnel avec un parcours personnalisé pour identifier les soft skills, valeurs et métiers compatibles.

## Architecture

### Stack technique
- **Frontend**: React 19 + Tailwind CSS + React Router
- **Backend**: FastAPI (Python)
- **Base de données**: MongoDB
- **Hébergement**: Emergent Platform
- **APIs externes**: ESCO API (European Skills/Competences database)

### Structure
```
/app
├── frontend/
│   └── src/
│       ├── App.js (routeur principal avec questionnaire visuel et résultats)
│       └── components/ui/ (Shadcn components)
└── backend/
    ├── server.py (API FastAPI avec algorithme de matching - 4600+ lignes)
    ├── esco_api.py (Module API ESCO pour recherche de métiers européens)
    └── france_travail_api.py (Module API France Travail - actuellement bloqué)
```

## Personas utilisateurs
1. **Jeunes diplômés** - Cherchent à découvrir leur orientation professionnelle
2. **Professionnels en reconversion** - Veulent identifier leurs compétences transférables
3. **Conseillers RH** - Utilisent l'outil pour accompagner les candidats

## Fonctionnalités principales (Core Requirements)

### Page d'accueil
- Logo DE'CLIC PRO avec gradient orange-vert
- 2 cartes CTA : "Je cherche mon job" et "Je cherche encore..."
- Phrase sur le questionnaire anonyme et gratuit
- Footer avec logos partenaires (Alt&Act, Ubuntoo, RE'ACTIF PRO, AI Act)

### Questionnaire (/questionnaire)
- Questions visuelles avec images
- Questions de classement (ranking 1-4)
- Barre de progression animée
- Champ date de naissance
- Navigation Précédent/Suivant

### Page Résultats
- Profil de personnalité (DISC, Ennéagramme, MBTI, **RIASEC**)
- Cadran d'Ofman (zones de vigilance)
- Boussole de fonctionnement
- **Nouveau: Profil RIASEC (Holland Codes)** avec barres de score et traits
- Liste des métiers compatibles avec scores
- Narratif personnalisé généré par IA

### API Backend
- `POST /api/job-match` - Matching métier avec profil (inclut RIASEC)
- `POST /api/explore` - Exploration des filières (inclut RIASEC)
- `GET /api/questionnaire/visual` - Questions visuelles
- `GET /api/metiers` - Liste des métiers (54 métiers)

## Ce qui a été implémenté

### Mars 2026 (Session actuelle)
- [x] **"Soft skills à développer" - Affichage spécifique** ✅
  - Backend : `generate_fallback_job_narrative()` calcule les soft skills manquants en comparant le profil utilisateur aux exigences du métier
  - Retourne `soft_skills_to_develop` dans `job_narrative` avec: `nom`, `description`, `importance` (critique/importante)
  - Frontend : Nouveau composant affichant une liste structurée avec badges visuels (⚡ Prioritaire / 📈 Recommandé)
  - CSS : Styles `.soft-skills-to-develop-list`, `.skill-to-develop-item` avec animations hover
  - Tests automatisés passés (7/7)

### Décembre 2025 (Sessions précédentes)
- [x] **Intégration complète du modèle RIASEC (Holland Codes)** ✅
  - Fonction `calculate_riasec_profile()` pour calculer le profil RIASEC à partir de MBTI/DISC/Ennéagramme
  - Fonction `riasec_congruence()` pour calculer la compatibilité métier-utilisateur
  - Fonction `get_job_riasec()` pour obtenir le code RIASEC d'un métier via le mapping ROME
  - Mapping `ROME_RIASEC_MAPPING` avec 358 codes ROME → RIASEC
  - Score RIASEC intégré dans `score_job()` avec un poids de 20%
  - Composant frontend `RiasecProfile` avec barres de score et affichage des traits
  - Tests automatisés passés (5/5)

- [x] **Enrichissement du questionnaire avec 8 questions RIASEC directes** ✅
  - 5 questions à 2 choix visuels (r1, r2, r3, r5, r7) : vie quotidienne et professionnelle
  - 3 questions de classement à 4 choix (r4, r6, r8) : activités, environnements, tâches
  - Système de pondération: 5 pts pour choix direct, 5/3/2/1 pts pour classement
  - Total questionnaire: 20 questions (+ date de naissance)
  - Tests automatisés passés (5/5)

### Décembre 2025 (Sessions précédentes)
- [x] Bug fix critique: Algorithme de recherche de métiers
- [x] Nouveau métier: "Chargé(e) de recrutement" (M033)
- [x] Intégration API ESCO (3000+ métiers européens)
- [x] Base de données enrichie à 54 métiers avec codes ROME

### Mars 2026 (sessions précédentes)
- [x] Page d'accueil complète avec design glassmorphism
- [x] Thème sombre avec gradients orange-vert
- [x] Questionnaire interactif avec questions visuelles
- [x] Carte d'identité Pro avec profil personnalisé
- [x] API de création de profil MongoDB
- [x] Algorithme de matching métiers (DISC + Ennéagramme + MBTI + RIASEC + environnement)
- [x] Animations et transitions CSS
- [x] Design responsive mobile/desktop

## Backlog priorisé

### P0 (Critique) - Fait ✅
- Toutes les fonctionnalités core sont implémentées
- Bug de matching métiers corrigé
- **Intégration RIASEC complète** ✅
- **"Soft skills à développer" affiche une liste spécifique** ✅

### P1 (Important)
- [ ] Export PDF de la carte d'identité Pro
- [ ] Partage sur réseaux sociaux
- [ ] Historique des questionnaires complétés
- [ ] Authentification utilisateur

### P2 (Nice to have)
- [ ] Dashboard administrateur
- [ ] Statistiques d'utilisation
- [ ] Intégration API France Travail (bloquée par erreur 403 - à résoudre avec France Travail)
- [ ] Personnalisation des questions
- [ ] Refactoring backend server.py (4600+ lignes → modules)
- [ ] Refactoring frontend App.js → composants

## Prochaines tâches
1. Implémenter l'export PDF de la carte d'identité
2. Ajouter la fonctionnalité de partage social
3. Créer un système d'authentification utilisateur
4. Résoudre l'accès API France Travail (contacter leur support)

## Notes techniques

### Algorithme de recherche de métiers
Le système utilise une fonction `normalize_text` pour:
- Supprimer les accents (normalisation Unicode NFD)
- Supprimer les caractères spéciaux (parenthèses, etc.)
- Ignorer les mots vides (de, du, le, la, etc.)

L'endpoint `/api/job-match` préserve la pertinence de recherche pour `best_match` tout en affichant les alternatives triées par compatibilité de profil dans `other_matches`.

### Scoring des métiers (mis à jour avec RIASEC)
Basé sur 7 critères pondérés (total = 100%):
- Motivation (Ennéagramme): 12%
- Style DISC: 8%
- Personnalité MBTI: 25%
- **RIASEC (Holland Codes): 20%** ← NOUVEAU
- Environnement de travail: 15%
- Compétences: 15%
- Contraintes: 5%

### Modèle RIASEC (Holland Codes)
- **R** = Réaliste (manuel, technique)
- **I** = Investigateur (scientifique, analytique)
- **A** = Artistique (créatif, expressif)
- **S** = Social (aide, enseigne)
- **E** = Entreprenant (leader, persuasif)
- **C** = Conventionnel (organisé, méthodique)

Le profil RIASEC de l'utilisateur est calculé à partir des dimensions MBTI, DISC et Ennéagramme. La congruence avec le métier utilise l'hexagone de Holland (types adjacents vs opposés).

## Problèmes connus
- **API France Travail** : Erreur 403 `insufficient_scope`. Nécessite une action de l'utilisateur auprès du support France Travail pour résoudre les permissions.
