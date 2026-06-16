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

### Phase 3 — OPC Endpoints IA (DONE)
- 7 endpoints IA (Claude Sonnet 4.5) : corrélations, émergentes, trajectoires, recommandation, prédictions, analyse complète, terrain SARE

### Phase 4 — Connecteur ETL RNCP (DONE)
- 30,022 certifications, 53,893 blocs, 66,491 mappings RNCP↔ROME, 40,998 certificateurs

### Phase 5 — Page OPC dédiée (DONE)
- Page autonome `/opc` avec sidebar (8 modules du cahier des charges)

### Phase 6 — Cartographie exhaustive IA (DONE - 16/06/2026)
- Endpoint `POST /api/observatory/ia/cartographie-exhaustive` : 35-50+ métiers catégorisés via IA
- Recommandation personnalisée enrichie (profil complet injecté dans le prompt)

### Phase 7 — Synchronisation profil + Actualisation Dashboard (DONE - 16/06/2026)
- **Header OPC** : Bouton "Synchroniser mon profil" charge le profil utilisateur (compétences, secteurs) comme contexte IA
- Badge vert affiché post-sync avec nom + nb compétences + bouton ✕ "Annuler la synchronisation"
- Mode libre conservé ("ou saisir un métier...") quand profil non synchronisé
- Bouton "Lancer l'analyse IA" actif uniquement si profil synchronisé ou métier saisi
- **Dashboard** : Bouton "Actualiser les données" avec date/heure du jour, compteurs ROME/OPC dynamiques

## Backlog
- **P1** : Refactoring `server.py` (>5200 lignes)
- **P2** : Export PDF des 4 modèles de CV
- **P3** : Soft Skills (CSE), Valeurs (VIA), diagnostic CCSP, Codéveloppement, micro-titres
