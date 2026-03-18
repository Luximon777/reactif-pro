# Re'Actif Pro - CHANGELOG

## 2026-03-18 - Session courante

### Feature: Selection des modeles de CV avant analyse
- Apres upload du CV, l'utilisateur choisit les modeles a generer (Classique, Competences, Fonctionnel, Mixte)
- Seuls les modeles selectionnes sont generes par l'IA → gain de temps significatif
- Option "analyse seule" (0 modeles) pour une analyse ultra-rapide
- Backend: CvTextPayload.selected_models parametre, filtrage dans _run_cv_analysis
- Frontend: ecran de selection interactif avec toggles, compteur et indice de vitesse

### Feature: Integration Claude AI pour la generation de CV
- Claude Sonnet (anthropic, claude-sonnet-4-5-20250929) genere les CV reconstitues
- GPT-5.2 reste utilise pour l'analyse des competences (extraction savoir-faire, savoir-etre)
- Fallback automatique vers GPT si Claude echoue (resilience)
- Flux en 2 etapes decouples:
  1. Upload → Analyse rapide des competences (~15s, sans generation de CV)
  2. Apres resultats → Selection des modeles souhaites → Generation a la demande par Claude IA
- L'utilisateur choisit 1, 2, 3 ou 4 modeles selon ses besoins
- Barre de progression pendant la generation (X/N modeles)

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
