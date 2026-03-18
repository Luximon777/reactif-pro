# Re'Actif Pro - CHANGELOG

## 2026-03-18 - Session courante

### P0 Bug Fix: Persistance des resultats d'analyse CV
- Cree endpoint `GET /api/cv/latest-analysis` qui retourne la derniere analyse completee
- Frontend `CvAnalysisSection` charge l'analyse precedente au montage du composant
- Les resultats persistent desormais lors de la navigation entre onglets

### P0 Feature: Enrichissement de l'analyse CV
- Prompt IA mis a jour pour generer `competences_transversales` (5-10 items) et `offres_emploi_suggerees` (3-5 offres)
- Frontend affiche les offres d'emploi suggerees avec type de contrat, secteur et competences requises

### P1 Refactoring: Decoupe du backend monolithique
- `server.py` reduit de 3942 lignes a 45 lignes
- 10 modules de routes crees sous `/app/backend/routes/`
- Modules partages: `db.py`, `models.py`, `helpers.py`, `referentiel_data.py`
- Tests de regression: 37/37 backend + 9/9 frontend = 100% succes

## Sessions precedentes
- Analyse de CV robuste (background jobs + polling)
- Explorateur de Metiers fonctionnel (recherche, fiches detaillees, generation IA, chaine archeologique)
- Logo SVG corrige
