# Re'Actif Pro - PRD (Product Requirements Document)

## Problem Statement
Plateforme full-stack "Re'Actif Pro" axee sur l'analyse de CV par IA, la gestion d'un "Passeport de Competences" dynamique et l'exploration des metiers via une "archeologie des competences".

## Core Requirements
1. **Authentification** : Systeme d'authentification anonyme
2. **Analyse de CV par IA** : Upload CV + extraction + analyse IA + audit 12 regles + auto-remplissage du passeport
3. **Audit CV (12 regles)** : Clarte, titre cible, accroche, valorisation experiences, competences, formation, adaptation offre, mots-cles ATS, absence superflu, coherence, structure, strategie globale
4. **Optimisation de CV** : L'IA corrige les points faibles et genere un CV optimise et percutant
5. **Generation de documents** : CV optimise en Word (DOCX) et PDF
6. **Suggestion de modele** : L'IA recommande le modele le plus adapte au profil
7. **Explorateur de Metiers** : Interface search-first avec fiches metiers
8. **Passeport de Competences** : Visualisation dynamique des competences
9. **Observatoire des Competences** : Suivi des competences emergentes
10. **Indice d'Evolution** : Mesure de la mutation des metiers
11. **Ubuntoo Intelligence** : Analyse des signaux faibles du marche
12. **Coffre-Fort Numerique** : Stockage securise de documents professionnels

## CV Optimization Flow (12 Rules)
1. **Upload** : L'utilisateur telecharge son CV (PDF, DOCX, TXT)
2. **Audit rapide** : L'IA analyse le CV selon 12 criteres professionnels et attribue un score /10 par regle + score global /100
3. **Diagnostic** : Affichage des points forts (OK), a ameliorer, et absents avec recommandations concretes
4. **Suggestion de modele** : L'IA recommande le meilleur modele (classique/competences/fonctionnel/mixte)
5. **Optimisation** : L'utilisateur selectionne les modeles et l'IA genere des CV optimises corrigeant les faiblesses
6. **Telechargement** : Word + PDF pour chaque modele optimise

### Les 12 Regles d'Audit
1. Clarte et lisibilite
2. Titre clair et cible
3. Accroche professionnelle impactante
4. Valorisation des experiences (verbes d'action + chiffres)
5. Mise en avant des competences (hard + soft skills)
6. Formation synthetique
7. Adaptation a l'offre
8. Mots-cles ATS
9. Absence de superflu
10. Coherence et authenticite
11. Structure type respectee
12. Strategie globale (lisibilite, credibilite, alignement)

## Tech Stack
- **Backend**: FastAPI, MongoDB, Python
- **Frontend**: React, Tailwind CSS, Shadcn/UI
- **AI**: OpenAI GPT-5.2 (analyse), Anthropic Claude Sonnet (optimisation CV) via Emergent LLM Key
- **File Generation**: python-docx (Word), reportlab (PDF)

## Architecture
```
/app/backend/
  server.py          # Slim app setup
  db.py              # Database connection
  models.py          # All Pydantic models
  helpers.py         # Shared helper functions
  routes/
    cv.py            # CV analysis, audit, optimization, download (DOCX + PDF)
    auth.py, passport.py, explorer.py, jobs.py, coffre.py, observatoire.py, evolution.py, ubuntoo.py, seed.py
```

## Key API Endpoints
- `POST /api/cv/analyze-text` - Fast CV analysis with 12-rule audit
- `POST /api/cv/generate-models` - Optimize selected CV models (uses audit findings)
- `GET /api/cv/download/{model_type}` - Download DOCX
- `GET /api/cv/download-pdf/{model_type}` - Download PDF

## What's Been Implemented
- Audit CV 12 regles professionnelles avec score global
- Suggestion de modele de CV par l'IA
- Optimisation de CV (corrige les points faibles)
- Generation DOCX et PDF
- Previsualisation structuree
- Toutes les fonctionnalites de base (Explorer, Passeport, Observatoire, etc.)

## Backlog
- P2: Refactoring du composant ParticulierView.jsx (>1200 lignes)
- Integration CCSP, diagnostic fonctionnel, auto-evaluation, codeveloppement, micro-titres
