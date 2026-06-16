# RE'ACTIF PRO — PRD (Product Requirements Document)

## Problème Original
Développement d'une plateforme full-stack "Ré'Actif Pro" basée sur l'analyse de compétences avec un Observatoire Prédictif des Compétences (OPC) fonctionnel, intégrant l'IA pour l'analyse de CV, les trajectoires professionnelles, et les prédictions du marché de l'emploi.

## Architecture
- **Frontend** : React + Tailwind CSS + Shadcn/UI
- **Backend** : FastAPI + MongoDB (Motor)
- **IA** : Claude Sonnet 4.5 via Emergent LLM Key
- **Connecteurs** : API France Travail (ROME 4.0), France Compétences (RNCP/RS Open Data)
- **Base de données** : MongoDB avec collections OPC pyramidales

## Fonctionnalités Implémentées

### Phase 1 — Infrastructure de base (DONE)
- Page d'accueil avec 5 accès distincts
- Authentification par pseudonyme + AdminGate
- Dashboard utilisateur avec parcours en 4 étapes

### Phase 2 — Analyse de CV (DONE)
- Upload de CV (base64), analyse IA, auto-remplissage passeport compétences
- Frise Trajectoire (timeline des expériences)
- Audit CV avec scoring

### Phase 3 — OPC : Endpoints IA (DONE - 16/06/2026)
- 7 endpoints IA fonctionnels : corrélations, émergentes, trajectoires, recommandation, prédictions, analyse complète, terrain SARE
- Alimentés par Claude Sonnet 4.5 via Emergent LLM Key

### Phase 4 — Connecteur ETL RNCP (DONE - 16/06/2026)
- Script ETL `seed_rncp.py` : télécharge automatiquement données France Compétences
- 30,022 certifications, 53,893 blocs, 66,491 mappings RNCP↔ROME, 40,998 certificateurs
- 6 routes API RNCP : recherche, fiche, blocs, mapping ROME, gap analysis, tension
- Enrichissement IA avec certifications RNCP conseillées

### Phase 5 — Page OPC dédiée (DONE - 16/06/2026)
- **Page autonome à /opc** avec sa propre sidebar (8 modules du cahier des charges)
- Plus intégrée au dashboard utilisateur
- Les 8 modules fonctionnels :
  1. **Tableau de bord** — KPIs, sources connectées, répartition par niveau
  2. **Référentiel vivant** — Recherche fusionnée ROME + OPC
  3. **Cartographie métiers** — Navigation par filière/secteur/métier
  4. **Transitions** — Passerelles métiers IA + corrélations hard/soft skills
  5. **Compétences émergentes** — Détection IA des tendances
  6. **Certifications RNCP** — Recherche 30K+ certs, fiches détaillées, tension
  7. **Intelligence territoriale** — Bassins d'emploi Grand Est
  8. **Moteur prédictif** — Prédictions globales, recommandation, analyse complète

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
- Intelligence territoriale réelle par bassin d'emploi (Strasbourg, Mulhouse, Colmar, Haguenau, Metz, Nancy)
- Planification cron quotidienne ETL RNCP
