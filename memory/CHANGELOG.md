# Re'Actif Pro - Changelog

## 2026-03-22 - Correlation CV x Observatoire/Evolution/Formations
- **Observatoire personnalise** : Nouvel endpoint `GET /api/observatoire/personalized?token=` qui croise les competences du CV (passport, cv_jobs, emerging_competences) avec les tendances globales (emerging_skills, sector_trends). Affiche: competences emergentes du CV, lacunes a combler, alertes de declin, secteurs pertinents.
- **Evolution enrichie** : Endpoint `GET /api/evolution-index/user-profile` enrichi pour utiliser les donnees du CV + passeport (pas seulement le profil). Affiche: sources de donnees (profile/passport/cv_analysis), competences emergentes du CV, formations recommandees.
- **Formations correlees** : Endpoint `GET /api/learning` enrichi avec pertinence (haute/moyenne/basse) et score de pertinence base sur les lacunes du CV. Les modules qui comblent des lacunes sont marques "Recommande pour vous".
- **Frontend** : Nouvelle carte PersonalizedObservatoireCard dans ObservatoireView, EvolutionExposureCard enrichie avec plus de sections, LearningCard avec badges de pertinence.
- Tests: 100% backend (21/21), 100% frontend - iteration_22.json

## Sessions precedentes
- Anonymat & Pseudonymat (3 phases)
- Inscriptions Employeurs / Partenaires avec SIRET
- Charte Ethique ALT&ACT
- CI/CD GitHub Actions pour VPS OVH
- Scraping offres d'emploi
- Algorithme passerelles metiers enrichi
- Mot de passe oublie
- Resilience upload CV
