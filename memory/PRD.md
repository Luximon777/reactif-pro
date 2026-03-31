# Re'Actif Pro - PRD

## Positionnement strategique
RE'ACTIF PRO est une plateforme de valorisation et de securisation des trajectoires professionnelles, concue pour agir en complementarite des services publics, prives et des acteurs de l'accompagnement.

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + Recharts
- Backend: FastAPI + MongoDB (Motor async)
- Auth: Pseudonyme anonyme (JWT) + Login pro (email/password)
- LLM: OpenAI GPT-4o via Emergent LLM Key (emergentintegrations)
- Storage: Emergent Object Storage (fichiers CV, documents coffre-fort)

## Implemente

### Core
- Design D'CLIC PRO, Auth, Analyse CV, Passeport, Observatoire, Job Matching, Formations, Explorateur, Ubuntoo

### Espace Personnel restructure en 4 onglets (31/03/2026)
- **Onglet Trajectoire**: Frise chronologique verticale avec 11 types d'etapes (emploi, formation, stage, interim, reconversion, recherche, pause, benevolat, creation, mobilite, certification). Codes couleur par type. Visibilite par etape (prive, accompagnateur, recruteur, public)
- **Bloc Confiance**: "Vous controlez votre parcours" + 4 cartes de visibilite (Moi, Conseiller, Recruteur, Partenaire) avec toggles
- **Synthese IA**: "Ce que mon parcours revele" genere par GPT-4o (fil conducteur, forces recurrentes, competences transferables, axes evolution)
- **Auto-import**: Bouton "Importer depuis mes donnees" qui cree des etapes a partir du passeport et du profil D'CLIC
- **Onglet Competences**: D'CLIC Boost Section + CV Analysis + Skills Display avec sources
- **Onglet Documents**: Coffre-fort banner + 3 categories (Identite pro, Diplomes, Preuves)
- **Onglet Matching**: Job Matching + Parcours Formation previews

### Espace Partenaires (COMPLET)
- Dashboard, Beneficiaires, Freins, Preparation IA, Contribution, Outils V2, Workflow zero charge admin

### Identifiant France Travail (31/03/2026)
- Champ a l'inscription + parametres de confidentialite
- Recherche partenaire: Identifiant FT + Nom/Prenom

### D'CLIC Boost Section visuelle (31/03/2026)
- 4 cartes de dimension: MBTI, DISC, RIASEC, Vertu dominante
- Toggle expand/collapse pour competences et skills importes

### Coffre-fort numerique avec stockage reel (31/03/2026)
- Upload de fichiers reels via Emergent Object Storage (max 10Mo)
- Download de fichiers avec Content-Disposition
- Auto-ajout des CVs uploades et generes par IA

### Corrections dashboard (31/03/2026)
- Profile score recalcule automatiquement
- Image D'CLIC remplacee

## Backlog
- P2: Narratif IA D'CLIC PRO
- P2: FranceConnect
- P3: Codeveloppement / Micro-badges
- P3: Refactoring PartenaireView.jsx (>1900 lignes)
- P3: Historique des consultations du parcours
- P3: Versions adaptees partageables (CV dynamique, lien, QR code)

## Test Reports
- Iteration 46-48: V2 + Consent + Approbation (100%)
- Iteration 49: Workflow 7 modules (Backend 14/14, Frontend 100%)
- Iteration 50: Identifiant FT + Recherche (Backend 12/12, Frontend 100%)
- Iteration 51: D'CLIC Boost + Coffre-fort + Object Storage (Backend 19/19, Frontend 100%)
- Iteration 52: Espace Personnel 4 onglets + Trajectoire (Backend 33/33, Frontend 100%)
