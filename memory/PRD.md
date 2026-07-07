# PRD - Ré'Actif Pro

## Problème original
Plateforme full-stack d'analyse de compétences professionnelles avec :
- OPC (Observatoire Prédictif des Compétences)
- Portefeuille de compétences certifiées
- Coach virtuel CIP
- Job Dating / Job Matching
- Génération de CV ciblé
- Questionnaire D'CLIC PRO

## Architecture
- Frontend: React + Tailwind CSS + Shadcn/UI
- Backend: FastAPI + MongoDB (Motor) + BackgroundTasks
- Auth: JWT pseudo/password
- Migration: Script automatique au démarrage (migrations.py)

## Ce qui est implémenté
- [x] OPC avec recherche stricte AND + fusion terrain
- [x] Portefeuille de compétences (3 couches : Confiance, Intelligence, Actions)
- [x] Coffre-fort numérique avec preuves S.A.R.E
- [x] Système de badges (Contributeur, Certifié, Expert Certifié)
- [x] Dashboard avec D'CLIC PRO boost
- [x] Upload CV avec analyse en background
- [x] Migration automatique données démo (peter7, peter9)
- [x] Seed complet : 33 coffre docs + 20 skill_illustrations + 10 contrats + proof_document sur 10 expériences
- [x] Admin Gate (3 statuts : Admin, Dev, Invité)
- [x] (2026-06) Extraction formations + centres d'intérêt lors de l'upload CV (prompt enrichi, sauvegarde passeport + cv_centres_interet, cv_text brut stocké dans cv_jobs)
- [x] (2026-06) Fallback /passport/refresh basé sur le texte complet du CV (cv_text) au lieu du résumé — plus d'inventions IA
- [x] (2026-06) Optimisation CV ciblée : mots-clés ATS extraits de l'offre (check-offer-match + generate-models), bannière de confirmation "Offre prise en compte" + chips ATS dans l'UI
- [x] (2026-06) Fix affichage carte Formations (mapping title/institution/year)
- [x] (2026-06) Marché caché : diagnostic IA en job arrière-plan + polling + cache (fini les timeouts proxy en prod)
- [x] (2026-06) Job matching : GET /jobs/matching interroge France Travail selon le profil (ROME/expériences) en priorité, fallback interne filtré score >= 45
- [x] (2026-06) Job dating : inscription/sauvegarde stockent les détails complets de l'événement ; historique affiche titre/ville/date réels ; onglet Sauvegardés réparé (filtre par id)
- [x] (2026-06) Refonte Archéologie : Arbre des Compétences infographique (5 bulles remplissables : savoirs-faire, savoirs-être, qualités, valeurs, vertus/racines), préremplissage profil, sauvegarde (GET/POST /passport/arbre), suppression contenu répétitif et mention ennéagramme
- [x] (2026-06) Arbre : renumérotation depuis les racines (1 Vertus → 5 Savoir-faire) + rails Formation/Apprentissage/Capacités/Tuteur/Potentiel + légende explicative
- [x] (2026-06) Arbre : panneau résumé à droite (progression vertus → savoir-faire, X/5 niveaux, stepper cliquable) + citation C.K. Luximon

## Comptes démo
- peter7 / Solerys777! (profil complet, Expert Certifié level 3)
- peter9 / Solerys777! (clone de peter7)
- mike7 / Solerys777!
- admin@reactifpro.fr / Choukette@777

## Backlog
- P1: Refactoring server.py (~10000 lignes) en routers modulaires
- P2: Outil diagnostic CCSP
- P2: Ateliers Codéveloppement
- P3: Micro-titres/badges (Ubuntoo)
- P3: Compteur global preuves OPC

## Note environnements
- Les corrections sont faites sur Preview. L'utilisateur doit REDÉPLOYER pour les voir sur reactif.pro (production). Les comptes prod (ex: aurelie67) bénéficieront des correctifs lors du prochain upload de CV ou via le bouton "Actualiser" du passeport (refresh).
