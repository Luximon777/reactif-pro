# Ré'Actif Pro - Product Requirements Document

## Core Concept
Plateforme d'intelligence professionnelle basée sur l'archéologie des compétences.

## Architecture CV Analysis (Robust)
```
Browser                    Backend
  |                          |
  |-- Read file locally --   |
  |   (PDF→base64, TXT→text, DOCX→mammoth)
  |                          |
  |-- POST /cv/extract-text-b64 (PDF only, JSON) →  PyPDF2 extract
  |   (with retry x3 on 502/503/504)                |
  |← text response ---------|
  |                          |
  |-- POST /cv/analyze-text (JSON, text only) →  Create job, return job_id
  |   (with retry x3 on 502/503/504)            Launch asyncio background task
  |← {job_id} (instant) ----|
  |                          |-- LLM Call 1: Analyse compétences (~25s)
  |-- GET /cv/analyze/status  |-- LLM Call 2: Génération 4 CV (~25s)
  |   (poll every 3s)        |-- Save to DB
  |   (retry on 502/503/504) |
  |← {status: completed} ----|
```

## Completed Features
- [x] Auth anonyme, 3 dashboards, Coffre-Fort, Observatoire, Indice Évolution
- [x] Passeport Dynamique (8 onglets), Lamri & Lubart, CCSP
- [x] Archéologie des Compétences (Vertus→Valeurs→Qualités→Savoir-être→Savoir-faire)
- [x] **Analyse IA de CV** - PDF/DOCX/TXT → 4 modèles CV (16 mars 2026)
- [x] **Logo SVG vectoriel** - Composant CSS/SVG net (16 mars 2026)
- [x] **Background processing + polling** - Évite timeout proxy 60s (16 mars 2026)
- [x] **Base64 PDF upload** - Évite corruption multipart proxy (16 mars 2026)
- [x] **Auto-retry 502/503/504** - Resilience sur toutes les étapes (16 mars 2026)

## Key Endpoints
- POST `/api/cv/extract-text-b64` - PDF base64 → texte (rapide)
- POST `/api/cv/analyze-text` - Texte → job_id (instantané)
- GET `/api/cv/analyze/status` - Poll résultats (polling)
- POST `/api/cv/analyze` - Upload multipart (legacy)

## Prioritized Backlog
### P0
- [ ] Refactoring backend (server.py ~3700 lignes → routes modulaires)
- [ ] Refactoring frontend (sous-composants)
### P1
- [ ] Génération PDF des modèles de CV
- [ ] Quiz d'orientation, Ateliers Codéveloppement, Micro-titres/badges
### P2
- [ ] CCSP diagnostic, Soft Skills/Valeurs auto-évaluation
- [ ] Export PDF passeport, mode sombre
