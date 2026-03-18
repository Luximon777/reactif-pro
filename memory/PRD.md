# Re'Actif Pro - PRD (Product Requirements Document)

## Problem Statement
Plateforme full-stack "Re'Actif Pro" axee sur l'analyse de CV par IA, la gestion d'un "Passeport de Competences" dynamique et l'exploration des metiers via une "archeologie des competences".

## Core Requirements
1. **Authentification** : Systeme d'authentification anonyme
2. **Analyse de CV par IA** : Upload CV + extraction + analyse IA + auto-remplissage du passeport
3. **Generation de CV** : Generation de CV structures par Claude AI en format Word (DOCX) et PDF
4. **Explorateur de Metiers** : Interface search-first avec fiches metiers et chaine archeologique
5. **Passeport de Competences** : Visualisation dynamique des competences (CCSP, Lamri-Lubart)
6. **Observatoire des Competences** : Suivi des competences emergentes et tendances sectorielles
7. **Indice d'Evolution** : Mesure de la mutation des metiers et secteurs
8. **Ubuntoo Intelligence** : Analyse des signaux faibles du marche du travail
9. **Coffre-Fort Numerique** : Stockage securise de documents professionnels

## Tech Stack
- **Backend**: FastAPI, MongoDB, Python
- **Frontend**: React, Tailwind CSS, Shadcn/UI
- **AI**: OpenAI GPT-5.2 (analyse), Anthropic Claude Sonnet (generation CV) via Emergent LLM Key
- **File Generation**: python-docx (Word), reportlab (PDF)
- **Architecture**: Modular routes with APIRouter, 2-Step Background Jobs & Polling

## CV Analysis & Generation Flow
1. **Step 1 - Fast Analysis (~15s)**: User uploads CV -> text extraction -> AI analysis (skills, experience) -> passport auto-fill
2. **Step 2 - On-demand Generation**: User selects model types (classique/competences/fonctionnel/mixte) -> Claude AI generates structured JSON -> python-docx creates DOCX + reportlab creates PDF
3. **Download**: User can download Word or PDF for each generated model
4. **Preview**: Structured CV preview in the UI

## Architecture (v2.0 - Refactored)
```
/app/backend/
  server.py          # Slim app setup
  db.py              # Database connection
  models.py          # All Pydantic models
  helpers.py         # Shared helper functions
  referentiel_data.py # Static reference data
  routes/
    auth.py          # Auth + profile
    cv.py            # CV analysis + generation (DOCX + PDF)
    passport.py      # Passport + archaeology
    explorer.py      # Referentiel explorer
    jobs.py          # Jobs, learning, RH, metrics
    coffre.py        # Coffre-fort
    observatoire.py  # Observatoire
    evolution.py     # Evolution index
    ubuntoo.py       # Ubuntoo intelligence
    seed.py          # Seed data + root
```

## Key API Endpoints
- `POST /api/cv/analyze-text` - Fast CV analysis
- `POST /api/cv/generate-models` - Generate selected CV models (DOCX + PDF)
- `GET /api/cv/generate-models/status` - Poll generation progress
- `GET /api/cv/download/{model_type}` - Download DOCX
- `GET /api/cv/download-pdf/{model_type}` - Download PDF
- `GET /api/cv/models` - Get generated models data

## What's Been Implemented
- Analyse de CV robuste (background jobs + polling + client-side extraction)
- Generation de CV par Claude AI (4 modeles: classique, competences, fonctionnel, mixte)
- Telechargement Word (DOCX) et PDF pour chaque modele genere
- Previsualisation structuree du CV dans l'interface
- Explorateur de Metiers avec generation IA
- Passeport de Competences dynamique
- Observatoire des Competences
- Indice d'Evolution des Metiers
- Ubuntoo Intelligence
- Coffre-Fort Numerique
- Backend modulaire refactorise

## Backlog
- P2: Refactoring du composant ParticulierView.jsx (>1100 lignes)
- Integration approfondie du referentiel CCSP
- Outil de diagnostic fonctionnel base sur le CCSP
- Modules d'auto-evaluation pour Soft Skills (CSE) et Valeurs (VIA)
- Ateliers de Codeveloppement
- Systeme de micro-titres/badges
