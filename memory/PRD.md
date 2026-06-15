# RE'ACTIF PRO - Product Requirements Document

## Core Concept
Plateforme d'intelligence professionnelle — Observatoire Predictif des Competences (OPC).
Infrastructure d'intelligence territoriale : Anticiper les competences, piloter l'emploi.
Page d'accueil avec 5 acces distincts vers les vues OPC originales.

## Architecture
- **Backend** : FastAPI (server.py + opc/ + ubuntoo_routes.py)
- **Frontend** : React + Tailwind + Shadcn/UI + react-router-dom
- **DB** : MongoDB (users, passport_competences, opc_*)
- **IA** : OpenAI GPT-5.2 via emergentintegrations (Emergent LLM Key)

## Routes Frontend
- `/` : LandingPage (page d'accueil avec 5 acces - clone de reactif.pro)
- `/observatoire` : Observatoire OPC (page principale avec 4 onglets)
- `/observatoire?vue=particulier` : Observatoire → onglet Particulier (Espace Personnel)
- `/observatoire?vue=rh` : Observatoire → onglet Employeurs RH (Espace Employeurs)
- `/observatoire?vue=conseiller` : Observatoire → onglet Conseillers (Appui aux parcours)
- `/observatoire?vue=institution` : Observatoire → onglet Institutions
- `/ubuntoo` : Application messagerie / Parcours VSI

## 5 Acces Landing Page → Destinations
1. **Espace Personnel** → Modale login (marc19/Solerys777!) → /observatoire?vue=particulier (VueParticulier OPC)
2. **Parcours VSI** → /ubuntoo
3. **OPC** (cercle central) → /observatoire
4. **Espace Employeurs** → /observatoire?vue=rh (VueRH OPC)
5. **Appui aux parcours** → /observatoire?vue=conseiller (VueConseiller OPC)

## Composants OPC originaux (GitHub source)
- `components/opc/Observatoire.jsx` : Page principale avec 4 onglets
- `components/opc/views/VueParticulier.jsx` : Vue Particulier
- `components/opc/views/VueRH.jsx` : Vue Employeurs RH
- `components/opc/views/VueConseiller.jsx` : Vue Conseillers
- `components/opc/views/VueInstitution.jsx` : Vue Institutions
- `components/opc/FicheMetier.jsx` : Fiche metier
- `components/opc/RechercheMetier.jsx` : Recherche metier
- `components/opc/FranceTravailPanel.jsx` : Panel France Travail
- `components/opc/KpiCard.jsx` : Carte KPI
- `components/opc/Section.jsx` : Section generique
- `components/opc/StatutBadge.jsx` : Badge de statut
- `components/opc/MetierSelector.jsx` : Selecteur de metier

## Key API Endpoints
- `POST /api/auth/login` : Login pseudonyme + password
- `POST /api/auth/register` : Register pseudonyme + password
- `GET /api/reactif/impact` : Stats d'impact
- `POST /api/reactif/contact` : Formulaire de contact

## Modules OPC Backend
- `opc/routes_vues.py` : 4 vues publics (Particulier, RH, Conseiller, Institution)
- `opc/routes_ingestion.py` : Ingestion de donnees
- `opc/routes_ia.py` : Synthese predictive IA
- `opc/routes_admin.py` : Administration (France Travail sync)
- `opc/referentiel_metiers.py` : Referentiel statique (284 metiers, 20 filieres)
- `opc/seed.py` : Donnees demo Grand Est

## Completed
- [x] Deploiement version GitHub (OPC complet avec 4 vues)
- [x] Seed des donnees demo Grand Est
- [x] Module Ubuntoo (messagerie) route /ubuntoo
- [x] Synthese predictive IA (Claude Sonnet 4.5)
- [x] Landing Page pixel-perfect depuis reactif.pro
- [x] Authentification pseudonyme (marc19/Solerys777!)
- [x] Navigation Landing Page : chaque espace mene a sa vue OPC originale
- [x] Observatoire.jsx lit le parametre URL ?vue= pour ouvrir le bon onglet
- [x] Fix UbuntooApp API URL (reactif.pro → REACT_APP_BACKEND_URL)

## Fichiers crees par agents (non originaux)
- `EspacePersonnel.jsx` : Page placeholder (non utilisee, remplacee par vue OPC)
- `ReactifPro.js` : Pages separees (non originales, gardees pour reference)
- `ReactifLanding.js` : Page institutionnelle (non originale, gardee pour reference)

## Prioritized Backlog
### P1
- [ ] Refactoring backend server.py monolithique en modules routes/
### P2
- [ ] Export PDF des CV/passeport (4 modeles)
### P3
- [ ] Modules d'auto-evaluation (Soft Skills CSE, Valeurs VIA)
- [ ] Diagnostic CCSP
- [ ] Ateliers de Codeveloppement
- [ ] Systeme de micro-titres/badges

## Source GitHub
https://github.com/Luximon777/reactif-pro
