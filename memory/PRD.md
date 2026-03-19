# Re'Actif Pro - PRD

## Problem Statement
Plateforme full-stack "Re'Actif Pro" pour l'analyse de CV par IA, l'optimisation ATS, et la gestion d'un Passeport de Competences dynamique.

## Flux CV en 3 etapes
1. **Charger** : Upload du CV (PDF, DOCX, TXT)
2. **Analyser** : Audit 10 regles pro + score /100 + diagnostic + suggestion modele + detection competences emergentes (~30s)
3. **Optimiser** : Choix de modele + offre d'emploi optionnelle pour ciblage ATS + optimisation IA (~15s) + telechargement Word/PDF

## Optimisation ATS
- Reprend les mots-cles exacts de l'offre d'emploi cible
- Format simple (Word/PDF basique) pour passer les filtres
- Intitules de poste clairs, competences explicites, dates structurees
- Pas de design graphique complexe, colonnes, pictogrammes

## Strategie hybride 3 canaux
1. Canal ATS : CV optimise mots-cles
2. Canal Reseau : Recommandations et contacts
3. Approche directe : Mail, LinkedIn, appel

## 4 Modeles de CV
- Classique, Competences, Transversal, Nouvelle Generation

## Passeport — Profil Dynamique 7 Dimensions
1. Identite professionnelle (anonymisable)
2. Intentions professionnelles
3. Competences avec preuves (SF + SE)
4. Experiences en situations
5. Potentiel et evolution
6. Valeurs et environnement
7. Validation (auto-declare, IA, humain)

## Detection des Competences Emergentes (Phase 1 - COMPLETE)
- 3eme appel LLM parallele lors de l'analyse CV
- Detecte 3-8 competences emergentes/rares/en croissance
- Score d'emergence 0-100, niveau (signal_faible/emergente/en_croissance/etablie)
- Categories: tech_emergente, hybride, soft_skill_avancee, methodologique, sectorielle
- Stockage MongoDB collection 'emerging_competences'
- Endpoints CRUD + observatoire
- Affichage enrichi dans PassportView onglet "Emergentes" avec:
  - Cercle de score SVG
  - Badges categorie/niveau/tendance
  - Indicateurs cles, secteurs porteurs, metiers associes

## What's Implemented
- Audit CV 10 regles + score /100
- Optimisation ATS avec offre d'emploi cible (9/9 mots-cles integres)
- 4 modeles CV avec SF/SE integres
- Telechargement Word + PDF
- Section strategie 3 canaux
- Passeport Profil Dynamique 7 dimensions
- Performance: analyse ~30s, optimisation ~15s
- Detection competences emergentes Phase 1 (backend + frontend)
- Endpoints: GET/POST emerging/competences, validate, observatory

## Backlog
- P1: Refactoring ParticulierView.jsx (~1293 lignes) et PassportView.jsx (~1700 lignes)
- P2: Phase 3 - Interface validation humaine (consultants valident/rejettent competences IA)
- P3: Phase 4 - Observatoire des competences (dashboard tendances)
- P4: Integration communautaire Ubuntoo
- P4: Coffre-fort numerique pour preuves
- Integration CCSP, diagnostic fonctionnel, auto-evaluation
- Ateliers Codeveloppement, micro-titres/badges
