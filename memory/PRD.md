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
    ExplorateurView.jsx - Explorateur de metiers (ISCO)
  components/
    AuthModal.jsx - Modal connexion/inscription pseudonyme
    JobMatchingSection.jsx - NEW: Section Job Matching avec filtres + scoring avancé
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
    jobs.py - Job Matching avancé + Formations + RH
    passport.py, coffre.py, etc.
  job_matching.py - Algorithme de scoring pondéré (5 niveaux, critères bloquants, vigilances, points forts)
  models.py - Profile enrichi + CandidateSearchProfile/CandidateSearchCriterion
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
- **Anonymat & Pseudonymat** : systeme complet 3 niveaux
- **Auth pseudo** : inscription, connexion, upgrade, changement mdp
- **Inscriptions par role** : Entreprise (SIRET+referent+charte), Partenaire (structure+type+charte)
- **Verification SIRET** : API Recherche d'Entreprises (data.gouv.fr)
- **Charte Ethique ALT&ACT** : 10 principes, signature obligatoire
- **Confidentialite** : parametres de visibilite, export, suppression compte
- **Correlation CV x Observatoire/Evolution/Formations/Emergentes** : endpoints personnalises
- **Integration matrice ISCO INSEE** : 5853 metiers importes, recherche enrichie
- **Bouton Rechercher** dans Explorateur
- **Job Matching avancé** : algorithme de scoring pondéré à 5 niveaux avec critères bloquants
  - Filtres: métier, secteur, contrat, temps de travail, mobilité, télétravail, aménagement, restrictions RQTH
  - Scoring transparent: score global, blocages (rouge), vigilances (orange), points forts (vert)
  - Sauvegarde des préférences utilisateur en DB
  - Offres générées par GPT-5.2 puis scorées par l'algorithme
  - Endpoints: POST /api/jobs/matching/search, GET/PUT /api/jobs/matching/preferences

## Backlog
- P0: Candidature via annonce sélectionnée (postuler directement)
- P1: Integration communautaire Ubuntoo (contribution participative)
- P2: Coffre-fort numerique pour preuves de competences
- P3: Certification identite via FranceConnect (architecture prete)
- P4: Integration CCSP, diagnostic fonctionnel, auto-evaluation
- P4: Ateliers Codeveloppement, micro-titres/badges
