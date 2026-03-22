# Re'Actif Pro - PRD

## Problem Statement
Plateforme full-stack "Re'Actif Pro" pour l'analyse de CV par IA, l'optimisation ATS, et la gestion d'un Passeport de Competences dynamique. La plateforme integre un systeme d'anonymat et pseudonymat pour proteger l'identite des utilisateurs.

## Flux CV en 3 etapes
1. **Charger** : Upload du CV (PDF, DOCX, TXT)
2. **Analyser** : Audit 10 regles pro + score /100 + diagnostic + suggestion modele + detection competences emergentes (~30s)
3. **Optimiser** : Choix de modele + offre d'emploi optionnelle pour ciblage ATS + optimisation IA (~15s) + telechargement Word/PDF

## Systeme d'identite (Anonymat & Pseudonymat)
3 niveaux d'acces:
1. **Visiteur anonyme** : Acces libre sans compte
2. **Compte pseudonyme** : Pseudo + mot de passe, email facultatif, aucune identite civile requise
3. **Compte certifie** (futur) : Identite verifiee via FranceConnect / L'Identite Numerique La Poste

Fonctionnalites:
- Inscription sous pseudo (min 3 chars) + mot de passe (min 6 chars)
- Email de recuperation facultatif
- Consentements CGU, confidentialite, marketing
- Upgrade anonymous -> pseudo
- Niveaux de visibilite: prive, limite, public
- Changement mot de passe
- Export de donnees (RGPD)
- Suppression de compte

## Architecture
```
frontend/src/
  pages/
    Landing.jsx - Page d'accueil avec AuthModal
    Dashboard.jsx - Dashboard avec nav Confidentialite
  views/
    ParticulierView.jsx - Dashboard personnel
    PassportView.jsx - Passeport competences
    PrivacySettingsView.jsx - Parametres de confidentialite
  components/
    AuthModal.jsx - Modal connexion/inscription pseudonyme
    CvAnalysis/
      CvAnalysisSection.jsx - Upload, analyse, optimisation CV
      CvPreview.jsx - Apercu CV
    Passport/
      EmergingCompetenceCard.jsx - Carte competence emergente
      passportConfig.js - Config partagees
backend/
  routes/
    auth.py - Auth (anonymous, register, login, upgrade, privacy, export, delete)
    cv.py - Analyse CV + 3 appels LLM paralleles
    emerging.py - CRUD competences emergentes
    passport.py, coffre.py, etc.
  models.py - Profile enrichi (pseudo, auth_mode, visibility_level, consent_*)
```

## What's Implemented
- Audit CV 10 regles + score /100
- Optimisation ATS avec offre d'emploi cible
- 4 modeles CV (Classique, Competences, Transversal, Nouvelle Generation) avec SF/SE
- Telechargement Word + PDF
- Section strategie 3 canaux (ATS, Reseau, Approche directe)
- Passeport Profil Dynamique 7 dimensions
- Performance: analyse ~30s, optimisation ~15s
- Detection competences emergentes (4 phases completes)
- Endpoints: GET/POST emerging/competences, validate, observatory
- Refactoring: ParticulierView 1294->354 lignes, PassportView 1823->1670 lignes
- **Anonymat & Pseudonymat** : systeme complet 3 niveaux (anonymous/pseudo/certified architecture)
- **Auth pseudo** : inscription, connexion, upgrade, changement mdp
- **Confidentialite** : parametres de visibilite, export, suppression compte
- **Collections MongoDB** : consent_history, external_identities (prete pour FranceConnect)

## Backlog
- P1: Integration communautaire Ubuntoo (contribution participative)
- P2: Coffre-fort numerique pour preuves de competences
- P3: Certification identite via FranceConnect (architecture prete)
- P4: Integration CCSP, diagnostic fonctionnel, auto-evaluation
- P4: Ateliers Codeveloppement, micro-titres/badges
