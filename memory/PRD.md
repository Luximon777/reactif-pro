# Ré'Actif Pro - Product Requirements Document (PRD)

## Vision produit
Plateforme full-stack d'analyse et de développement des compétences professionnelles.

## Stack technique
- **Frontend**: React, Tailwind CSS, Shadcn/UI, React Router
- **Backend**: FastAPI, MongoDB (Motor), Emergent LLM Key (GPT-5.2)
- **Data**: Pandas/Openpyxl/Odfpy pour traitement fichiers utilisateur

## Architecture
```
/app/backend/
├── server.py             # API principal (~9539 lignes, en cours de refactoring)
├── database.py           # DB partagée, helpers (_infer_sectors, get_current_token)
├── routes/
│   ├── __init__.py
│   └── jobdating.py      # Module Job Dating extrait (337 lignes)
├── opc/                  # Modules OPC dédiés
├── scripts/
│   └── enrich_ck1_ia.py  # Script enrichissement IA CK1
└── tests/

/app/frontend/src/
├── pages/
│   └── OpcDediePage.jsx  # Dashboard OPC + Référentiel Vivant (7 colonnes CK1)
├── views/
│   ├── CoffreFortView.jsx # Coffre-fort S.A.R.E
│   └── OpportunitesView.jsx
└── components/
    └── JobMatchingSection.jsx # France Travail + Filtrage ROME automatique
```

## Fonctionnalités implémentées

### Phase 1 — Authentification & Profil
- Login pseudonyme, création de compte, rôles (admin/dev/utilisateur)
- Profil utilisateur, import CV, analyse IA

### Phase 2 — Coffre-fort & Preuves S.A.R.E
- Portefeuille de compétences avec preuves S.A.R.E (Situation, Action, Résultat, Enseignement)
- Validation par case à cocher + envoi automatique à l'OPC si contrat certifié
- Upload de contrats de travail, bouton d'actualisation

### Phase 3 — OPC (Observatoire Prédictif des Compétences)
- Page autonome /opc avec navigation sidebar
- Tableau récapitulatif (Couche 2 Intelligence)
- Référentiel Vivant avec 7 colonnes : Métier, Hard Skills, Soft Skills, Qualités humaines, Vertus, Valeurs, Source
- Import de 68 fiches métiers depuis FILIERES PROFESSIONNELLES.ods
- Enrichissement CK1 complet (68/68 fiches) : Vertus, Valeurs, Qualités humaines, Compétences cognitives/émotionnelles/sociales
- Détail expansé avec sections CK1 colorées

### Phase 4 — Job Matching & France Travail
- Filtrage ROME automatique basé sur le profil utilisateur (expériences, compétences, D'CLIC)
- Recherche manuelle de codes ROME avec dropdown autocomplete
- Intégration API France Travail avec code ROME en paramètre
- 12 suggestions ROME max par profil

### Phase 5 — Job Dating
- Événements personnalisés avec scores de matching
- Inscription, évaluation, historique
- Module extrait dans routes/jobdating.py

### Phase 6 — Coach Virtuel & D'CLIC PRO
- Coach interactif (CIP) avec GPT-5.2
- Questionnaire D'CLIC PRO avec scoring RIASEC

### Phase 7 — Trajectoire & CV
- Génération de CV ciblé par IA
- Exploration de trajectoire professionnelle

## Endpoints clés
- `POST /api/auth/login` — Connexion
- `GET /api/opc/referentiel/search?q=` — Recherche référentiel OPC
- `GET /api/jobs/rome-suggestions?token=` — Suggestions ROME auto
- `GET /api/jobs/rome-search?q=` — Recherche codes ROME
- `POST /api/jobs/france-travail/search` — Recherche France Travail
- `GET /api/jobdating/events` — Événements Job Dating
- `PATCH /api/coffre/documents/{id}` — Mise à jour preuve

## Collections MongoDB clés
- `users` — Comptes utilisateurs
- `profiles` / `passports` — Profils et données professionnelles
- `referentiel_opc` — 68 fiches métiers enrichies CK1
- `rome_metiers` — 1911 codes ROME France Travail
- `skill_illustrations` — Preuves S.A.R.E
- `opc_contributions` — Contributions terrain

## Tâches futures (Backlog)
- **P2**: Continuer le refactoring server.py (auth, coffre, opc, cv...)
- **P2**: Modules Soft Skills (CSE) et Valeurs (VIA) indépendants
- **P2**: Diagnostic fonctionnel CCSP
- **P3**: Ateliers Codéveloppement
- **P3**: Micro-titres/badges Ubuntoo
