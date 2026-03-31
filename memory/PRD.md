# Re'Actif Pro - PRD

## Positionnement strategique
RE'ACTIF PRO est une plateforme de valorisation et de securisation des trajectoires professionnelles, concue pour agir en complementarite des services publics, prives et des acteurs de l'accompagnement.

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + Recharts + qrcode.react + html-to-image + framer-motion
- Backend: FastAPI + MongoDB (Motor async)
- Auth: Pseudonyme anonyme (JWT) + Login pro (email/password)
- LLM: OpenAI GPT-5.2 via Emergent LLM Key (emergentintegrations)
- Storage: Emergent Object Storage (fichiers CV, documents coffre-fort)

## Navigation (8 rubriques - restructure 31/03/2026)
| # | Rubrique | Route | Sous-rubriques |
|---|---|---|---|
| 1 | Accueil | /dashboard | 4 stats + 6 cartes navigation |
| 2 | Mon Profil | /dashboard/profil | Profil, Experiences, Passerelles, Profil Dynamique |
| 3 | Ma Trajectoire | /dashboard/trajectoire | Frise chronologique, CV upload, insights IA |
| 4 | Mes Competences | /dashboard/competences | Inventaire, Evaluation, Archeologie, Emergentes |
| 5 | Le Marche | /dashboard/marche | Observatoire, Evolution, Explorateur |
| 6 | Opportunites | /dashboard/opportunites | Matching, Formations |
| 7 | Mon Coffre-fort | /dashboard/coffre-fort | Documents, Candidatures, Partages |
| 8 | Confidentialite | /dashboard/confidentialite | Parametres vie privee |

## Implemente

### Core
- Design D'CLIC PRO, Auth, Analyse CV, Passeport, Observatoire, Job Matching, Formations, Explorateur, Ubuntoo

### Espace Personnel en 4 onglets (31/03/2026)
- Trajectoire: Frise chronologique, 11 types d'etapes, visibilite par etape
- Bloc Confiance + 4 cartes de visibilite avec toggles
- Synthese IA (GPT-5.2)
- Auto-import depuis passeport, D'CLIC et CV

### Refonte Trajectoire 2 colonnes + Insights IA (31/03/2026)
- Header dark gradient, Layout 2 colonnes, Sidebar IA

### Suppression carte MBTI + Charger CV depuis coffre-fort (31/03/2026)
- Carte MBTI supprimee de D'CLIC Boost, bouton "Depuis mon coffre-fort" ajoute
- Endpoints GET /api/coffre/cv-files et POST /api/cv/analyze-from-coffre

### Personnalisation Indice Evolution des Competences (31/03/2026)
- Cartes resume, repartition et vue d'ensemble personnalisees au profil utilisateur

### Restructuration Navigation Complete (31/03/2026)
- 9 rubriques reduites a 8, tous doublons elimines
- Progression logique: Se connaitre > Mon parcours > Mes acquis > Le marche > Agir > Securiser > Controler
- Doublons supprimes: Competences x3 > unique, Documents x2 > unique, Matching x2 > unique, Emergentes x2 > unique
- Nouveaux wrappers: LeMarcheView.jsx, OpportunitesView.jsx
- PassportView et ParticulierView acceptent viewMode prop pour filtrer les onglets
- CoffreFortView reduit de 7 a 3 onglets
- Accueil "Mon Espace" avec dashboard d'overview et cartes de navigation
- Redirections legacy pour compatibilite arriere (6 anciennes routes)

## Backlog
- P1: Narratif IA D'CLIC PRO
- P2: FranceConnect
- P3: Codeveloppement / Micro-badges
- P3: Export PDF trajectoire
- P3: Refactoring PartenaireView.jsx / ParticulierView.jsx (>1700 lignes)

## Test Reports
- Iteration 57: Suppression MBTI + Coffre-fort CV picker (Backend 100%, Frontend 100%)
- Iteration 58: Restructuration Navigation (Frontend 100% - 8 tabs, all routes, legacy redirects)
