# Re'Actif Pro - PRD

## Positionnement strategique
RE'ACTIF PRO est une plateforme de valorisation et de securisation des trajectoires professionnelles, concue pour agir en complementarite des services publics, prives et des acteurs de l'accompagnement.

**Axe differanciant**: "Plateforme qui supprime la charge administrative invisible" — logique zero ressaisie, IA d'aide a la decision, autonomie beneficiaire.

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + Recharts
- Backend: FastAPI + MongoDB (Motor async)
- Auth: Pseudonyme anonyme (JWT) + Login pro (email/password)
- LLM: OpenAI GPT-4.1-mini via Emergent LLM Key (emergentintegrations)

## Implemente

### Core
- Design D'CLIC PRO, Auth multi-niveaux, Analyse CV, Passeport de competences
- Observatoire predictif, Job Matching, Formations, Explorateur
- Ubuntoo (Communaute)

### Espace Partenaires de Parcours (COMPLET)
- 6 onglets: Dashboard, Beneficiaires, Freins, Preparation parcours IA, Contribution territoriale, Outils V2
- Bandeau complementarite (7 acteurs)

### Outils d'accompagnement V2 (29/03/2026)
- 12 fiches augmentees en 5 phases + blocs decisionnels

### Consentement granulaire (29/03/2026)
- 3 niveaux: Synthese, Modulaire, Complet temporaire

### Identifiant France Travail + Recherche revisee (31/03/2026)
- **Inscription**: Champ "Identifiant France Travail" (facultatif) dans le formulaire de creation de compte
- **Parametres de confidentialite**: Champ identifiant FT affiche en mode "Limite"
- **Conditions pour etre trouvable par les partenaires**:
  1. Identifiant France Travail renseigne
  2. Test D'CLIC PRO passe
  3. Profil booste (competences ou passeport complete)
  4. Statut "Limite" active
- **Recherche partenaire**: 2 champs — Identifiant France Travail + Nom/Prenom
- Resultats: badges "Profil verifie" (vert) ou "Conditions non remplies" (orange) + details manquants
- Backend: identifiant_france_travail stocke dans profiles, recherche avec $regex

### Demande d'acces beneficiaire avec approbation (29/03/2026)
- Recherche par identifiant FT + nom -> Demander l'acces -> Approbation -> Synchroniser
- Bandeau notification sur dashboard pour syncs en attente

### Workflow "Zero charge administrative" — 7 modules (30/03/2026)
1. Synthese pre-entretien IA
2. Compte rendu d'entretien IA (copiable pour outil metier)
3. Plan d'action intelligent (actions, echeances, dispositifs)
4. Vue lecture rapide (2 minutes)
5. Export intelligent (texte structure, copie/colle France Travail)
6. Detection de decrochage (score de risque 0-100)
7. Bilan de fin de parcours

### Onglets fiche beneficiaire
Vue rapide (defaut) | Profil | Diagnostic | Synthese IA | Entretiens | Plan d'action | Freins | Historique | Export/Bilan | Profil Re'Actif

## Backlog
- P1: Coffre-fort numerique avec upload de fichiers reels
- P2: Narratif IA personnalise D'CLIC PRO
- P2: FranceConnect
- P3: Ateliers de Codeveloppement / Micro-badges
- Refactoring: PartenaireView.jsx (>1800 lignes)

## Test Reports
- Iteration 46: Outils V2 + Consentement (100%)
- Iteration 47: Demande d'acces (100%)
- Iteration 48: Flux d'approbation (100%)
- Iteration 49: Workflow zero charge admin (Backend 14/14, Frontend 100%)
- Iteration 50: Identifiant France Travail + Recherche (Backend 12/12, Frontend 100%)
