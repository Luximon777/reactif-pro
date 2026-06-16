# RE'ACTIF PRO — PRD (Product Requirements Document)

## Problème Original
Développement d'une plateforme full-stack "Ré'Actif Pro" basée sur l'analyse de compétences avec un Observatoire Prédictif des Compétences (OPC) fonctionnel, intégrant l'IA pour l'analyse de CV, les trajectoires professionnelles, et les prédictions du marché de l'emploi.

## Architecture
- **Frontend** : React + Tailwind CSS (copie pixel-perfect du site production reactif.pro)
- **Backend** : FastAPI + MongoDB (Motor)
- **IA** : Claude Sonnet 4.5 via Emergent LLM Key
- **Connecteurs** : API France Travail (ROME 4.0), France Compétences (RNCP/RS Open Data)
- **Base de données** : MongoDB avec collections OPC pyramidales

## Fonctionnalités Implémentées

### Phase 1 — Infrastructure de base ✅
- Page d'accueil avec 5 accès distincts
- Authentification par pseudonyme + AdminGate
- Dashboard utilisateur avec parcours en 4 étapes

### Phase 2 — Analyse de CV ✅
- Upload de CV (base64), analyse IA, auto-remplissage du passeport de compétences
- Frise Trajectoire (timeline des expériences)
- Audit CV avec scoring

### Phase 3 — Observatoire Prédictif des Compétences (OPC) ✅
- **Recherche fusionnée** : BDD interne (20 filières, 289 métiers) + ROME France Travail (1911 fiches)
- **4 onglets fonctionnels** :
  - Observer : données vivantes, recherche référentiel, contexte métier
  - Analyser : corrélations compétences techniques ↔ savoir-être (IA)
  - Anticiper : compétences émergentes, trajectoires IA, prédictions globales, analyse complète
  - Orienter : recommandation personnalisée avec certifications RNCP

### Phase 4 — Connecteur ETL RNCP / France Compétences ✅
- **Script ETL** (`seed_rncp.py`) : télécharge et charge automatiquement les données RNCP/RS
- **30,022 certifications** RNCP/RS chargées
- **53,893 blocs de compétences**
- **66,491 mappings RNCP ↔ ROME**
- **40,998 certificateurs**
- **Routes API** :
  - `GET /api/referentiel/rncp/search` : Recherche de certifications
  - `GET /api/referentiel/rncp/fiche/{code}` : Détail + blocs + ROME + certificateurs
  - `GET /api/referentiel/rncp/rome/{code_rome}` : Certifications par code ROME
  - `POST /api/referentiel/rncp/gap-analysis` : Analyse des écarts profil vs certification
  - `GET /api/referentiel/rncp/tension` : Certifications en tension
  - `GET /api/referentiel/rncp/stats` : Statistiques globales
- **Enrichissement IA** : les recommandations OPC incluent désormais les certifications RNCP conseillées

## Collections MongoDB

### OPC interne
- `opc_filieres` : 20 filières professionnelles
- `opc_metiers` : 289 métiers avec compétences détaillées
- `rome_metiers` : 1,911 fiches ROME France Travail

### RNCP / France Compétences
- `opc_certifications` : 30,022 fiches RNCP/RS
- `opc_blocs_competences` : 53,893 blocs
- `opc_rncp_rome` : 66,491 mappings certification ↔ ROME
- `opc_certificateurs` : 40,998 liens certification ↔ organisme

## Endpoints IA OPC (7 routes)
1. `POST /api/observatory/ia/correlations` — Corrélations hard/soft skills
2. `POST /api/observatory/ia/detect-emergentes` — Compétences émergentes
3. `POST /api/observatory/ia/trajectoires` — Passerelles métiers IA
4. `POST /api/observatory/ia/recommandation` — Recommandation personnalisée + RNCP
5. `POST /api/observatory/predict-competences` — Prédictions globales
6. `POST /api/observatory/ia/analyse-complete` — Analyse combinée
7. `GET /api/observatory/sare-terrain` — Preuves terrain S.A.R.E

## Backlog

### P1 — Refactoring technique
- Découper `server.py` (>5200 lignes) en modules sous `/app/backend/routes/`

### P2 — Export PDF
- Génération des 4 modèles de CV au format PDF

### P3 — Modules complémentaires
- Soft Skills (CSE) et Valeurs (VIA) via auto-évaluation
- Outil de diagnostic fonctionnel CCSP
- Ateliers de Codéveloppement
- Système de micro-titres/badges

### P3 — Vision cible
- Connecteur ESCO européen
- Données entreprises partenaires
- Intelligence territoriale par bassin d'emploi
