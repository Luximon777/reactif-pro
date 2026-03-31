# Re'Actif Pro - PRD

## Positionnement strategique
RE'ACTIF PRO est une plateforme de valorisation et de securisation des trajectoires professionnelles, concue pour agir en complementarite des services publics, prives et des acteurs de l'accompagnement.

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + Recharts + qrcode.react + html-to-image
- Backend: FastAPI + MongoDB (Motor async)
- Auth: Pseudonyme anonyme (JWT) + Login pro (email/password)
- LLM: OpenAI GPT-4o via Emergent LLM Key (emergentintegrations)
- Storage: Emergent Object Storage (fichiers CV, documents coffre-fort)

## Implemente

### Core
- Design D'CLIC PRO, Auth, Analyse CV, Passeport, Observatoire, Job Matching, Formations, Explorateur, Ubuntoo

### Espace Personnel en 4 onglets (31/03/2026)
- Trajectoire: Frise chronologique, 11 types d'etapes, visibilite par etape
- Bloc Confiance + 4 cartes de visibilite avec toggles
- Synthese IA "Ce que mon parcours revele" (GPT-4o)
- Auto-import depuis passeport et D'CLIC
- Competences: D'CLIC Boost + CV Analysis + Skills Display
- Documents: Coffre-fort categories
- Matching: Job Matching + Formations

### Lien partageable + QR code (31/03/2026)
- Creation de liens uniques avec 3 audiences: accompagnateur, recruteur, public
- Duree de validite configurable (7/30/90/365 jours)
- Options: inclure carte D'CLIC, inclure competences
- QR code genere automatiquement
- Page publique /trajectoire/:shareId avec nom anonymise, carte D'CLIC, timeline filtree, competences
- Historique des liens actifs avec compteur de vues et revocation
- Journalisation des acces (trajectory_access_log)

### Carte D'CLIC PRO telechargeable (31/03/2026)
- Bouton "Telecharger la carte" dans la section CarteSection (DclicTestPage)
- Export PNG haute qualite via html-to-image
- QR code integre dans le pied de la carte
- 4 dimensions: Identite Personnelle, Professionnelle, Sociale, Profonde

### Coffre-fort numerique avec stockage reel (31/03/2026)
- Upload fichiers reels via Emergent Object Storage (max 10Mo)
- Auto-ajout CVs uploades et generes par IA

### Espace Partenaires (COMPLET)
- Dashboard, Beneficiaires, Workflow zero charge admin

### Identifiant France Travail (31/03/2026)
- Inscription + confidentialite + recherche partenaire

## Backlog
- P2: Narratif IA D'CLIC PRO
- P2: FranceConnect
- P3: Codeveloppement / Micro-badges
- P3: Refactoring PartenaireView.jsx (>1900 lignes)

## Test Reports
- Iteration 49: Workflow (Backend 14/14, Frontend 100%)
- Iteration 50: Identifiant FT (Backend 12/12, Frontend 100%)
- Iteration 51: Coffre-fort + Object Storage (Backend 19/19, Frontend 100%)
- Iteration 52: Espace Personnel 4 onglets (Backend 33/33, Frontend 100%)
- Iteration 53: Partage trajectoire + QR code + Carte telechargeable (Backend 14/14, Frontend 100%)
