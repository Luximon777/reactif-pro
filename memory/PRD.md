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
- Auto-import depuis passeport, D'CLIC et CV

### Auto-remplissage frise depuis CV (31/03/2026)
- Apres analyse CV, experiences detectees auto-ajoutees comme etapes de trajectoire
- Notification "Frise de parcours mise a jour" dans CvAnalysisSection
- Option d'ajouter/modifier manuellement les etapes

### Visuel "Boostez votre profil" D'CLIC PRO (31/03/2026)
- Carte gradient indigo/violet avec icone eclair jaune
- Badges: Personnalite, Orientation, Competences validees, Carte Pro
- 4 dimensions placeholders: MBTI, DISC, RIASEC, Vertus
- Bouton "Passer le test" bien visible
- Se transforme en D'CLIC Boost Section apres le test

### Lien partageable + QR code (31/03/2026)
- Liens uniques 3 audiences: accompagnateur, recruteur, public
- QR code, copie lien, gestion liens actifs, revocation
- Page publique /trajectoire/:shareId

### Carte D'CLIC PRO telechargeable (31/03/2026)
- Export PNG haute qualite via html-to-image
- QR code integre dans le pied de la carte

### Coffre-fort numerique avec stockage reel (31/03/2026)
- Upload fichiers reels via Emergent Object Storage (max 10Mo)
- Auto-ajout CVs uploades et generes par IA

### Sections CV completes dans Competences
- Audit CV (10 criteres, score, recommandations)
- Centres d'interet (analyse IA, detection automatique)
- URL offre d'emploi (adaptation ATS)
- Generation CV optimises (4 modeles)

### Espace Partenaires (COMPLET)
- Dashboard, Beneficiaires, Workflow zero charge admin

### Identifiant France Travail (31/03/2026)
- Inscription + confidentialite + recherche partenaire

### Mode Compact CvAnalysisSection dans Trajectoire (31/03/2026)
- Prop `compact` dans CvAnalysisSection: bouton upload seul, progression, resultat bref
- Onglet Trajectoire: upload CV en haut, frise chronologique en dessous
- Onglet Competences: mode complet inchange (audit, centres d'interet, generation CV)
- Teste avec bob23 (5 etapes) et testboost (0 etapes)

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
- Iteration 55: Compact CV mode dans Trajectoire (Frontend 100%)
