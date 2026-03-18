# Re'Actif Pro - Changelog

## 2026-03-18 - PDF Generation + DOCX Validation
- **FEATURE**: Implemented PDF generation using `reportlab` for all CV models
- **FEATURE**: Added `GET /api/cv/download-pdf/{model_type}` endpoint
- **FEATURE**: Added PDF download buttons in UI (alongside Word buttons)
- **VALIDATED**: Full E2E DOCX flow tested and working (analysis -> generation -> download)
- **FIX**: Fixed button-inside-button React hydration warning in model selection grid
- **TESTED**: 100% pass rate on both backend (curl) and frontend (Playwright) tests

## Previous Sessions
- Backend refactoring from monolithic server.py to modular routes/
- 2-step CV analysis flow (fast analysis + on-demand generation)
- Claude AI integration for structured CV generation (JSON)
- DOCX generation with python-docx
- CV model selection grid with checkboxes
- Analysis result persistence across navigation
- Job suggestions from CV analysis
- All core platform features (Explorer, Passport, Observatory, etc.)
