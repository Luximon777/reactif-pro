# Re'Actif Pro - PRD

## Problem Statement
Plateforme full-stack "Re'Actif Pro" pour l'analyse de CV par IA, l'optimisation ATS, et la gestion d'un Passeport de Competences dynamique. La plateforme integre un systeme d'anonymat et pseudonymat pour proteger l'identite des utilisateurs.

## Flux CV en 3 etapes
1. **Charger** : Upload du CV (PDF, DOCX, TXT)
2. **Analyser** : Audit 10 regles pro + score /100 + diagnostic + suggestion modele + detection competences emergentes (~30s)
3. **Optimiser** : Choix de modele + offre d'emploi optionnelle pour ciblage ATS + optimisation IA (~15s) + telechargement Word/PDF

## Systeme d'identite (Anonymat & Pseudonymat)
3 niveaux d'acces:
1. **Espace Personnel** : Inscription sous pseudonyme (pseudo + mdp, email facultatif, aucune identite civile)
2. **Espace Employeurs** : Inscription entreprise (nom entreprise, SIRET avec verification API INSEE, email pro, mdp, referent RH nom+prenom+fonction, signature charte ethique ALT&ACT)
3. **Espace Partenaires** : Inscription structure (nom structure, type structure, SIRET, email pro, mdp, referent nom+prenom+fonction, signature charte ethique ALT&ACT)

Plus d'acces anonyme/rapide depuis la landing page.

Fonctionnalites auth:
- Verification SIRET automatique via API Recherche d'Entreprises (data.gouv.fr)
- Avertissement email non-professionnel (Gmail, Yahoo, etc.) - non bloquant
- Signature charte ethique ALT&ACT (10 principes) obligatoire pour entreprise et partenaire
- Login par email pour entreprise/partenaire, par pseudo pour espace personnel
- Profil progressif avec pourcentage de completion
- Export de donnees (RGPD) et suppression de compte
- Consentements CGU, confidentialite, marketing
- Niveaux de visibilite: prive, limite, public

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
    ObservatoireView.jsx - Observatoire predictif (personnalise avec CV)
    EvolutionIndexView.jsx - Indice d'evolution (enrichi avec CV)
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
    observatoire.py - Observatoire predictif + endpoint personnalise
    evolution.py - Indice d'evolution enrichi avec CV
    jobs.py - Emplois + Formations (learning avec pertinence CV)
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
- **Inscriptions par role** : Entreprise (SIRET+referent+charte), Partenaire (structure+type+charte)
- **Verification SIRET** : API Recherche d'Entreprises (data.gouv.fr) integration
- **Charte Ethique ALT&ACT** : 10 principes, signature obligatoire entreprise/partenaire
- **Confidentialite** : parametres de visibilite, export, suppression compte
- **Collections MongoDB** : consent_history, external_identities (prete pour FranceConnect)
- **Correlation CV x Observatoire** : endpoint /api/observatoire/personalized croise les competences du CV avec les tendances globales (compétences emergentes, lacunes, secteurs)
- **Correlation CV x Evolution** : endpoint /api/evolution-index/user-profile enrichi avec donnees CV + passeport + competences emergentes
- **Correlation CV x Formations** : endpoint /api/learning enrichi avec pertinence (haute/moyenne/basse) et lacunes combees

- **Correlation CV x Emergentes** : endpoint market-correlation + badges marche sur cartes de competences emergentes

## Backlog
- P1: Integration communautaire Ubuntoo (contribution participative)
- P2: Coffre-fort numerique pour preuves de competences
- P3: Certification identite via FranceConnect (architecture prete)
- P4: Integration CCSP, diagnostic fonctionnel, auto-evaluation
- P4: Ateliers Codeveloppement, micro-titres/badges
