# Re'Actif Pro - PRD

## Positionnement strategique
RE'ACTIF PRO est une plateforme de valorisation et de securisation des trajectoires professionnelles, concue pour agir en complementarite des services publics, prives et des acteurs de l'accompagnement.

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + Recharts + qrcode.react + html-to-image + framer-motion
- Backend: FastAPI + MongoDB (Motor async)
- Auth: Pseudonyme anonyme (JWT) + Login pro (email/password)
- LLM: OpenAI GPT-5.2 via Emergent LLM Key (emergentintegrations)
- Storage: Emergent Object Storage (fichiers CV, documents coffre-fort)

## Implemente

### Core
- Design D'CLIC PRO, Auth, Analyse CV, Passeport, Observatoire, Job Matching, Formations, Explorateur, Ubuntoo

### Espace Personnel en 4 onglets (31/03/2026)
- Trajectoire: Frise chronologique, 11 types d'etapes, visibilite par etape
- Bloc Confiance + 4 cartes de visibilite avec toggles
- Synthese IA "Ce que mon parcours revele" (GPT-5.2)
- Auto-import depuis passeport, D'CLIC et CV

### Auto-remplissage frise depuis CV (31/03/2026)
- Apres analyse CV, experiences detectees auto-ajoutees comme etapes de trajectoire
- Notification "Frise de parcours mise a jour" dans CvAnalysisSection
- Option d'ajouter/modifier manuellement les etapes

### Visuel "Boostez votre profil" D'CLIC PRO (31/03/2026)
- Carte gradient indigo/violet avec icone eclair jaune
- Badges: Personnalite, Orientation, Competences validees, Carte Pro
- 3 dimensions: DISC, RIASEC, Vertus (MBTI supprime)
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

### Refonte Trajectoire 2 colonnes + Insights IA (31/03/2026)
- Header dark gradient: titre, badge, stats (coherence/etapes), boutons CV et partage
- Layout 2 colonnes: gauche (viewers + frise), droite (sidebar insights)
- Viewers cards: Moi/Conseiller/Recruteurs avec switches et onglets Frise/Acces
- Frise enrichie: cartes avec gradient par type, competences, acquis, selecteur visibilite
- Sidebar IA: narrative, competences dominantes, 5 scores coherence (progress bars)
- Partage 3 versions: accompagnement, recrutement, publique
- Carte confiance: "Votre parcours vous appartient"
- Backend synthesis enrichi: scores (coherence, adaptabilite, transferabilite, continuite, alignement), competences_dominantes, analyse_narrative
- Auto-chargement synthese IA quand etapes existent
- Animations framer-motion

### Mode Compact CvAnalysisSection dans Trajectoire (31/03/2026)
- Prop `compact` dans CvAnalysisSection: bouton upload seul, progression, resultat bref
- Onglet Trajectoire: upload CV en haut, frise chronologique en dessous
- Onglet Competences: mode complet inchange (audit, centres d'interet, generation CV)

### Suppression carte MBTI + Charger CV depuis coffre-fort (31/03/2026)
- Supprime la carte "Personnalite MBTI - Analysee" de la section D'CLIC Boost
- Ajoute bouton "Depuis mon coffre-fort" dans le mode compact CvAnalysisSection
- Endpoint GET /api/coffre/cv-files pour lister les fichiers CV du coffre-fort
- Endpoint POST /api/cv/analyze-from-coffre pour analyser un CV depuis le coffre-fort
- Picker dropdown avec liste des CVs disponibles dans le coffre-fort
- Option disponible dans l'etat initial et l'etat resultat

## Backlog
- P1: Narratif IA D'CLIC PRO
- P2: FranceConnect
- P3: Codeveloppement / Micro-badges
- P3: Export PDF trajectoire
- P3: Refactoring PartenaireView.jsx / ParticulierView.jsx (>1700 lignes)

## Test Reports
- Iteration 49: Workflow (Backend 14/14, Frontend 100%)
- Iteration 50: Identifiant FT (Backend 12/12, Frontend 100%)
- Iteration 51: Coffre-fort + Object Storage (Backend 19/19, Frontend 100%)
- Iteration 52: Espace Personnel 4 onglets (Backend 33/33, Frontend 100%)
- Iteration 53: Partage trajectoire + QR code + Carte telechargeable (Backend 14/14, Frontend 100%)
- Iteration 55: Compact CV mode dans Trajectoire (Frontend 100%)
- Iteration 56: Refonte Trajectoire 2 colonnes + Insights IA (Frontend 100%)
- Iteration 57: Suppression MBTI + Coffre-fort CV picker (Backend 100%, Frontend 100%)
