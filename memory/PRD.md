# Re'Actif Pro - PRD

## Problem Statement
Plateforme full-stack "Re'Actif Pro" pour l'analyse de CV par IA, l'optimisation professionnelle, et la gestion d'un Passeport de Competences dynamique.

## Flux CV en 3 etapes
1. **Charger** : Upload du CV (PDF, DOCX, TXT)
2. **Analyser** : Audit 10 regles professionnelles + score /100 + diagnostic + suggestion modele (~30s)
3. **Optimiser** : Choix de modele (classique/competences/transversale/nouvelle_generation) + optimisation IA + telechargement Word/PDF (~15s)

## Les 10 Regles d'Audit
Clarte, Titre cible, Accroche, Experiences, Competences, Formation, Mots-cles ATS, Superflu, Coherence, Structure

## 4 Modeles de CV
- **Classique** : Chronologique, sobre
- **Competences** : Axe savoir-faire/savoir-etre
- **Transversal** : Competences transferables
- **Nouvelle Generation** : Profil dynamique (intentions, preuves, potentiel, valeurs)

## Passeport — Profil Dynamique 7 Dimensions
1. Identite professionnelle (anonymisable)
2. Intentions professionnelles
3. Competences avec preuves
4. Experiences en situations (Contexte/Actions/Resultats)
5. Potentiel et capacites d'evolution
6. Valeurs et environnement de travail
7. Niveaux de validation (auto-declare, IA, humain)

## Tech Stack
- Backend: FastAPI, MongoDB, Python, python-docx, reportlab
- Frontend: React, Tailwind CSS, Shadcn/UI
- AI: OpenAI GPT-5.2 (analyse + optimisation) via Emergent LLM Key
- Architecture: Modular routes, 2-step background jobs, parallel LLM calls

## What's Implemented
- Audit CV 10 regles + score global /100
- 4 modeles CV avec optimisation IA (GPT-5.2)
- Telechargement Word + PDF
- Passeport avec onglet Profil Dynamique 7 dimensions
- Performance: analyse ~30s, optimisation ~15s
- Toutes les fonctionnalites de base (Explorer, Observatoire, etc.)

## Backlog
- P2: Refactoring ParticulierView.jsx et PassportView.jsx
- Integration CCSP, diagnostic fonctionnel, auto-evaluation
- Ateliers Codeveloppement, micro-titres/badges
