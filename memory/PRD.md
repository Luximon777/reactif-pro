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
├── server.py             # API principal (~9570 lignes, en cours de refactoring)
├── database.py           # DB partagée, helpers (_infer_sectors, get_current_token)
├── routes/
│   ├── __init__.py
│   └── jobdating.py      # Module Job Dating extrait (337 lignes)
├── opc/                  # Modules OPC dédiés
├── scripts/
│   ├── enrich_ck1_ia.py          # Script enrichissement CK1
│   └── enrich_hard_soft_skills.py # Script enrichissement Hard/Soft Skills
└── tests/

/app/frontend/src/
├── pages/
│   └── OpcDediePage.jsx  # Dashboard OPC + Référentiel Vivant (6 colonnes, badges validation, modale preuve)
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
- **Admin gate** : Connexion admin auto-ouvre la plateforme (gate_state → spaces_open: true)
- **Blocage admin** : L'admin ne peut pas accéder à l'Espace Personnel (toast informatif)
- Modale de connexion (AuthModal) avec onglets Se connecter / Créer un compte

### Phase 2 — Coffre-fort & Preuves S.A.R.E
- Portefeuille de compétences avec preuves S.A.R.E
- Validation par case à cocher + envoi automatique à l'OPC si contrat certifié
- Upload de contrats de travail

### Phase 3 — OPC (Observatoire Prédictif des Compétences)
- Page autonome /opc avec navigation sidebar
- Référentiel Vivant avec 6 colonnes : Métier, Hard Skills, Soft Skills, Qualités humaines, Vertus, Valeurs
- 68 fiches métiers enrichies CK1 + Hard/Soft Skills via IA
- **Badges de validation terrain** : compétences prouvées S.A.R.E en vert + compteur contributeurs
- **Modale de preuve** : visualisation S.A.R.E complète au clic (Situation, Action, Résultat, Enseignement)
- Recherche multi-mots avec scoring de pertinence (filtre résultats peu pertinents)

### Phase 4 — Job Matching & France Travail
- Filtrage ROME automatique basé sur le profil utilisateur
- Recherche manuelle de codes ROME avec dropdown autocomplete
- Intégration API France Travail

### Phase 5 — Job Dating
- Événements personnalisés avec scores de matching
- Module extrait dans routes/jobdating.py

### Phase 6 — Coach Virtuel & D'CLIC PRO
- Coach interactif (CIP) avec GPT-5.2
- Questionnaire D'CLIC PRO avec scoring RIASEC

### Phase 7 — Trajectoire & CV
- Génération de CV ciblé par IA

## Endpoints clés
- `POST /api/auth/login` — Connexion utilisateur
- `GET/POST /api/admin/gate-state` — État de la porte admin (spaces_open)
- `GET /api/opc/referentiel/search?q=` — Recherche référentiel OPC (avec skill_validations)
- `GET /api/jobs/rome-suggestions?token=` — Suggestions ROME auto
- `GET /api/jobs/rome-search?q=` — Recherche codes ROME
- `POST /api/jobs/france-travail/search` — Recherche France Travail
- `GET /api/jobdating/events` — Événements Job Dating

## Collections MongoDB clés
- `referentiel_opc` — 68 fiches métiers enrichies CK1 + Hard/Soft Skills
- `fiches_metier_opc` — Contributions terrain (preuves S.A.R.E par compétence)
- `rome_metiers` — 1911 codes ROME France Travail
- `skill_illustrations` — Preuves S.A.R.E brutes

## Tâches futures (Backlog)
- **P2**: Continuer le refactoring server.py (auth, coffre, opc, cv...)
- **P2**: Modules Soft Skills (CSE), Valeurs (VIA) indépendants
- **P2**: Diagnostic CCSP
- **P3**: Ateliers Codéveloppement
- **P3**: Micro-titres/badges Ubuntoo
