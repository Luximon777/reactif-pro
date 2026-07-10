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
- [x] (2026-06) Arbre : légende "Comprendre l'arbre" (Formation/Apprentissage/Capacités/Tuteur/Potentiel) déplacée à gauche de l'arbre (layout 3 colonnes) ; résumé limité en hauteur pour ne plus être masqué par le widget Coach
- [x] (2026-07) UBUNTOO intégré : réseau social solidaire récupéré depuis GitHub (Luximon777/ubuntoo, branche conflict_090726_1613) et porté dans Ré'Actif Pro. Backend routes/ubuntoo_social.py (/api/social, collections ubuntoo_*, SSO auto-provisionné depuis la session Ré'Actif Pro, WebSocket /api/social/ws). Frontend views/ubuntoo-social/ monté sur /ubuntoo/* (Fil+réactions solidaires, groupes+discussions, messagerie temps réel, communauté, recherche, profil, badges d'expérience). Ancienne UbuntooView (VSI meeting rooms) détachée mais conservée dans views/.
- [x] (2026-07) Prototype UBUNTOO ORIGINAL (branche main, mars 2026) monté sur /ubuntoo-ancien pour comparaison : thème sombre gradients, profil avec statuts + import RE'ACTIF PRO mock (/api/social/legacy/import-reactif-pro), groupes d'entraide, discussions forum/Q&A/chat, mentorat, impact + démo reactif-pro embarquée. CSS isolé (.ubuntoo-ancien, nesting natif). EN ATTENTE : choix utilisateur entre les 2 versions pour /ubuntoo.

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
