# RE'ACTIF PRO — PRD (Product Requirements Document)

## Problème Original
Développement d'une plateforme full-stack "Ré'Actif Pro" basée sur l'analyse de compétences avec un Observatoire Prédictif des Compétences (OPC) fonctionnel, intégrant l'IA pour l'analyse de CV, les trajectoires professionnelles, et les prédictions du marché de l'emploi.

## Architecture
- **Frontend** : React + Tailwind CSS + Shadcn/UI
- **Backend** : FastAPI + MongoDB (Motor)
- **IA** : Claude Sonnet 4.5 via Emergent LLM Key
- **Connecteurs** : API France Travail (ROME 4.0), France Compétences (RNCP/RS Open Data)

## Fonctionnalités Implémentées

### Phase 1-2 — Infrastructure + Analyse CV (DONE)
- Page d'accueil, authentification pseudonyme, AdminGate, Dashboard 4 étapes
- Upload CV, analyse IA, passeport compétences, frise Trajectoire, Audit CV

### Phase 3 — OPC Endpoints IA (DONE - 16/06/2026)
- 7 endpoints IA (Claude Sonnet 4.5) : corrélations, émergentes, trajectoires, recommandation, prédictions, analyse complète, terrain SARE

### Phase 4 — Connecteur ETL RNCP (DONE - 16/06/2026)
- 30,022 certifications, 53,893 blocs, 66,491 mappings RNCP↔ROME, 40,998 certificateurs
- 6 routes API RNCP : recherche, fiche, blocs, mapping ROME, gap analysis, tension

### Phase 5 — Page OPC dédiée (DONE - 16/06/2026)
- **Page autonome à `/opc`** avec sidebar dédiée (8 modules du cahier des charges)
- Modules : Tableau de bord, Référentiel vivant, Cartographie métiers, Transitions, Compétences émergentes, Certifications RNCP, Intelligence territoriale, Moteur prédictif
- Bug fixes : Référentiel vivant, Cartographie métiers, AdminGate, flèches IA, erreur 500 recommandation

### Phase 6 — Cartographie exhaustive des métiers IA (DONE - 16/06/2026)
- **Nouveau endpoint** : `POST /api/observatory/ia/cartographie-exhaustive`
- Croise TOUTES les données ROME (50 max), OPC (30 max) et RNCP (60+ certifs) pour un domaine
- Génère via Claude une arborescence catégorisée de 35-50+ métiers (ex: 47 métiers en 7-8 catégories pour "commercial")
- Inclut : métiers émergents (3-5), certifications clés (5-8), stats sources
- **Frontend** : Composant `CartographieExhaustiveDisplay` avec catégories dépliables, badges de tension, flèches de tendance, stats
- **Performance** : ~55-90s de temps de réponse (LLM-bound)

## Backlog
- **P1** : Refactoring `server.py` (>5200 lignes) — extraire routes /api/cv, /api/trajectory, /api/coach
- **P2** : Export PDF des 4 modèles de CV
- **P3** : Soft Skills (CSE), Valeurs (VIA), diagnostic CCSP, Codéveloppement, micro-titres
- **P3** : Connecteur ESCO européen, intelligence territoriale réelle par bassin
