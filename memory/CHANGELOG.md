# Re'Actif Pro - Changelog

## 2026-03-18 - Audit CV 12 Regles + Optimisation IA
- **FEATURE**: Audit CV selon 12 regles professionnelles (clarte, titre cible, accroche, valorisation, ATS, etc.)
- **FEATURE**: Score global /100 + score par critere /10 avec diagnostic et recommandations
- **FEATURE**: Suggestion automatique du modele de CV le plus adapte au profil
- **FEATURE**: Optimisation du CV par IA (corrige les points faibles identifies dans l'audit)
- **UI**: "Generer vos CV avec Claude IA" -> "Optimiser votre CV par IA"
- **UI**: Section audit avec grille 2 colonnes, codes couleur (OK/Ameliorable/Absent)
- **UI**: Auto-selection du modele suggere

## 2026-03-18 - PDF Generation + DOCX Validation
- **FEATURE**: Generation PDF avec reportlab
- **FEATURE**: Endpoint GET /api/cv/download-pdf/{model_type}
- **FEATURE**: Boutons Word + PDF dans l'UI
- **VALIDATED**: Flux DOCX bout en bout
- **FIX**: Warning React button imbrique

## Previous Sessions
- Backend refactoring (monolith -> modular routes)
- 2-step CV analysis flow
- Claude AI integration for CV generation
- DOCX generation with python-docx
- All core platform features
