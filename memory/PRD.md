# Re'Actif Pro - PRD (Product Requirements Document)

## Problem Statement
Plateforme full-stack "Re'Actif Pro" axee sur l'analyse de CV par IA, la gestion d'un "Passeport de Competences" dynamique et l'exploration des metiers via une "archeologie des competences" (reliant savoir-faire, savoir-etre, qualites, valeurs et vertus).

## Core Requirements
1. **Authentification** : Systeme d'authentification anonyme
2. **Analyse de CV par IA** : Upload CV + extraction + analyse IA + auto-remplissage du passeport
3. **Explorateur de Metiers** : Interface search-first avec fiches metiers et chaine archeologique
4. **Passeport de Competences** : Visualisation dynamique des competences (CCSP, Lamri-Lubart)
5. **Observatoire des Competences** : Suivi des competences emergentes et tendances sectorielles
6. **Indice d'Evolution** : Mesure de la mutation des metiers et secteurs
7. **Ubuntoo Intelligence** : Analyse des signaux faibles du marche du travail
8. **Coffre-Fort Numerique** : Stockage securise de documents professionnels

## Tech Stack
- **Backend**: FastAPI, MongoDB, Python
- **Frontend**: React, Tailwind CSS, Shadcn/UI
- **AI**: OpenAI GPT-5.2 (via Emergent LLM Key)
- **Architecture**: Modular routes with APIRouter

## What's Been Implemented
- Analyse de CV robuste (background jobs + polling + client-side extraction)
- Explorateur de Metiers avec generation IA
- Passeport de Competences dynamique
- Observatoire des Competences
- Indice d'Evolution des Metiers
- Ubuntoo Intelligence
- Coffre-Fort Numerique
- Logo SVG corrige

## Architecture (v2.0 - Refactored)
```
/app/backend/
  server.py          # Slim app setup (45 lines)
  db.py              # Database connection
  models.py          # All Pydantic models
  helpers.py         # Shared helper functions
  referentiel_data.py # Static reference data
  routes/
    auth.py          # Auth + profile
    cv.py            # CV analysis (with persistence)
    passport.py      # Passport + archaeology
    explorer.py      # Referentiel explorer
    jobs.py          # Jobs, learning, RH, metrics
    coffre.py        # Coffre-fort
    observatoire.py  # Observatoire
    evolution.py     # Evolution index
    ubuntoo.py       # Ubuntoo intelligence
    seed.py          # Seed data + root
```
