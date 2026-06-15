# Ré'Actif Pro - Product Requirements Document

## Core Concept
Plateforme d'intelligence professionnelle — Observatoire Prédictif des Compétences (OPC).
Infrastructure d'intelligence territoriale : Anticiper les compétences, piloter l'emploi.

## Architecture actuelle (Version GitHub - base)
- **Backend** : FastAPI modulaire (server.py ~100 lignes + opc/ routeurs + ubuntoo_routes.py)
- **Frontend** : React + Tailwind + Shadcn/UI + @tanstack/react-query
- **Page d'accueil** : Observatoire Prédictif des Compétences
- **4 vues** : Particulier, Employeurs RH, Conseillers, Institutions
- **Module Ubuntoo** : App de messagerie (route /ubuntoo)

## Modules OPC Backend
- `opc/routes_vues.py` : 4 vues publics (Particulier, RH, Conseiller, Institution)
- `opc/routes_ingestion.py` : Ingestion de données
- `opc/routes_ia.py` : Synthèse prédictive IA
- `opc/routes_admin.py` : Administration (France Travail sync)
- `opc/referentiel_metiers.py` : Référentiel statique (284 métiers, 20 filières)
- `opc/seed.py` : Données démo Grand Est
- `opc/schemas.py` : 8 flux Pydantic (profils, entreprises, offres, formations, institutionnel, terrain, parcours, référentiels)

## Rubriques VueParticulier (OPC)
1. Profil (métier visé, métier exercé, compétences techniques, soft skills)
2. Écart compétences prioritaires (gap analysis)
3. Fiche métier (mission, capacités techniques, capacités pro, savoirs-être, qualités humaines)
4. Trajectoires conseillées (code ROME, horizon, taux tension)
5. Offres compatibles (poste, salaire, localisation, contrat, secteur, mots-clés émergents)
6. Formations accessibles (organisme, durée, taux insertion, financements)
7. Suivi parcours

## Completed
- [x] Déploiement de la version GitHub (OPC complet)
- [x] Seed des données démo Grand Est
- [x] 4 vues opérationnelles (Conseillers, Particulier, RH, Institutions)
- [x] Module Ubuntoo (messagerie) route /ubuntoo
- [x] Synthèse prédictive IA (Claude Sonnet 4.5)
- [x] Fiche métier avec fallback IA Claude

## Prioritized Backlog
### P0
- [ ] Upload CV + analyse IA aligné sur les rubriques OPC
### P1
- [ ] Export PDF des CV/passeport
### P2
- [ ] Modules d'auto-évaluation (Soft Skills CSE, Valeurs VIA)
- [ ] Diagnostic CCSP
- [ ] Ateliers de Codéveloppement
- [ ] Système de micro-titres/badges
