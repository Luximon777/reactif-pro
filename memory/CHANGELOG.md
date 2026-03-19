# Re'Actif Pro - Changelog

## 2026-03-19 - Refactoring Composants Frontend
- **REFACTORING**: ParticulierView.jsx 1294->354 lignes (-73%). Extraction de CvAnalysisSection.jsx (693 lignes) et CvPreview.jsx (105 lignes) dans /components/CvAnalysis/
- **REFACTORING**: PassportView.jsx 1823->1670 lignes. Extraction de EmergingCompetenceCard.jsx (85 lignes) et passportConfig.js (84 lignes) dans /components/Passport/
- **TESTED**: 100% frontend - tous les composants extraits fonctionnent correctement, navigation OK, onglets OK

## 2026-03-19 - Competences Emergentes Phase 1
- **FEATURE**: 3eme appel LLM parallele dans _run_cv_analysis pour detection competences emergentes
- **FEATURE**: Stockage MongoDB 'emerging_competences' avec score, niveau, categorie, justification, indicateurs
- **FEATURE**: Endpoints CRUD: GET /api/emerging/competences, GET /api/emerging/competence/{id}, POST /api/emerging/validate/{id}, GET /api/emerging/observatory
- **FEATURE**: Affichage enrichi PassportView onglet "Emergentes" avec EmergingCompetenceCard (score SVG, badges, indicateurs, secteurs, metiers)
- **TESTED**: 100% backend (12/12) + frontend (UI complete)

## 2026-03-18 - CV Nouvelle Generation + Profil Dynamique + Performance
- **PERF**: Optimisation CV reduite de 88s a ~15s (GPT-5.2 au lieu de Claude, parsing JSON robuste)
- **FIX**: Le CV optimise contient bien les donnees du candidat original (prompt ameliore)
- **FEATURE**: 4eme modele CV "Nouvelle Generation" (profil dynamique: intentions, preuves, potentiel, valeurs)
- **FEATURE**: Passeport — nouvel onglet "Profil Dynamique" avec 7 dimensions
- **FEATURE**: Dimensions: Identite anonymisable, Intentions, Competences avec preuves, Experiences en situations, Potentiel, Valeurs, Validation multi-niveaux
- **TESTED**: 100% backend (15/15) + frontend (UI complete)

## 2026-03-18 - Audit CV + Optimisation IA
- Audit 10 regles professionnelles, score global /100
- Suggestion automatique modele CV par l'IA
- Analyse parallele (audit + extraction) pour performance
- Labels UI "Optimiser votre CV par IA"

## 2026-03-18 - PDF + DOCX
- Generation PDF avec reportlab
- Validation flux DOCX bout en bout

## Previous Sessions
- Backend refactoring, 2-step CV flow, Claude AI integration, all core features
