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
- [x] (2026-07) Fix "0 résultat(s)" OPC Référentiel vivant : fallback dans GET /referentiel/search (recherche par mots dans referentiel_opc + fiches terrain fiches_metier_opc) + re-seed renforcé au démarrage (opc_metiers<10, opc_filieres<5, rome_metiers<100). NÉCESSITE REDÉPLOIEMENT pour la prod.
- [x] (2026-07) Fix compteur "0 résultat(s)" affiché sous le tableau OPC alors que des fiches sont visibles : le compteur (OpcDediePage.jsx, data-testid="opc-search-total") inclut désormais opcResults.length + results.total. Vérifié sur Preview (affiche "4 résultat(s)" pour "chef cuisinier"). NÉCESSITE REDÉPLOIEMENT pour reactif.pro.
- [x] (2026-07) DÉPLOYÉ en production : https://marche-cache.emergent.host (reactif.pro).
- [x] (2026-07) UBUNTOO — Parcours d'évolution des membres (iteration_45, 100% backend + frontend) : 7 niveaux (Explorateur→Contributeur→Ambassadeur→Expert→Mentor→Leader Communautaire→Pionnier Ubuntoo), 4 dimensions (Contribution/Expertise/Engagement/Impact humain), charte éthique (POST /api/social/charter/accept), dialog de célébration animé au passage de niveau, critères + déblocages par niveau. Backend: /app/backend/routes/ubuntoo_progression.py (GET /api/social/progression). Frontend: Progression.jsx intégré dans Profile.jsx (/ubuntoo/profile). Pionnier = flag manuel is_pioneer (comité). Logo dupliqué supprimé de la Navbar Ubuntoo (l'image contient déjà le mot ubuntoo). DÉPLOYÉ.
- [x] (2026-07) UBUNTOO — Système de badges complet selon spec PDF utilisateur (iteration_46, 100%) : Piste 1 "Preuves" connectée au portefeuille RE'ACTIF PRO (skill_illustrations + passports + coffre_documents par token_id) avec paliers 1/5/10/25/50 (Premier pas → Référent de confiance) + badge "Compétences démontrées" (diversité d'origines) + badge "Compétence vérifiée" (tiers qualifié) ; 5 familles de badges (Engagement, Expertise, Solidarité, Innovation, Leadership) ; ICU (Indice de Contribution Ubuntoo) à 5 dimensions (Compétence, Fiabilité, Collaboration, Impact, Engagement) + score global, remplace les 4 dimensions dans l'UI. Frontend: ProofsBadges.jsx + Progression.jsx (props data/reload, fetch unique dans Profile.jsx, ancienne section "Badges par catégorie" supprimée). Origines projet_perso/benevolat à 0 par design (non trackées). NÉCESSITE REDÉPLOIEMENT.

- [x] (2026-07) Page d'accueil : ajout de la carte "Certification officielle des Soft Skills" (AdminGate.jsx, data-testid="space-certification") entre Espace Personnel et Parcours VSI. Rangée haute passée à 3 colonnes. Clic → AuthModal particulier + redirect post-auth vers /dashboard/coffre-fort. Vérifié par screenshot. NÉCESSITE REDÉPLOIEMENT.
- [ ] (EN ATTENTE) Messagerie type WhatsApp (duo + groupes) : l'utilisateur a fourni files.zip (ws_routes.py, ubuntoo_messaging_routes.py, messaging_models.py, websocket_manager.py, ChatListPage.jsx, ChatWindow.jsx, MessageBubble.jsx, NewConversationModal.jsx, GroupInfoPanel.jsx, useUbuntooSocket.js, README.md) extrait dans /tmp/userzip. À intégrer dans le module Ubuntoo.

- [x] (2026-08) FIX BUG RÉCURRENT upload CV scanné ("cv jad.pdf", compte mike) : erreur "Le fichier ne contient pas assez de texte exploitable" car PDF scanné sans couche texte (PyPDF2 → 0 caractère). Ajout d'un fallback OCR par vision IA dans server.py (_ocr_pdf_via_vision : pymupdf rend les pages en PNG 200dpi → base64 → OpenAI gpt-5.2 via emergentintegrations ImageContent, max 4 pages). Déclenché quand texte < 50 car. sur un PDF. Message d'erreur enrichi si OCR échoue aussi. TESTÉ avec le vrai fichier cv_jad.pdf : analyse completed, 13 savoir-faire, 4 savoir-être, 4 expériences, 2 formations extraits. Dépendance ajoutée : pymupdf (requirements.txt à jour). NÉCESSITE REDÉPLOIEMENT.

- [x] (2026-08) FIX "Prompt Engineering" affiché à tort dans les compétences évaluées de mike (et 160 autres passeports) : la construction du passeport (server.py section "3. From Ubuntoo signals") injectait TOUTES les compétences émergentes globales de l'Observatoire comme compétences personnelles. Bloc supprimé + migration migrate_remove_ubuntoo_global_competences (migrations.py, $pull source:"ubuntoo") exécutée au démarrage → 161 passeports nettoyés sur Preview, s'exécutera aussi en prod au redéploiement. Vérifié via API : mike a 18 compétences, toutes liées à son profil chauffeur-livreur. NÉCESSITE REDÉPLOIEMENT.

- [x] (2026-08) FIX section "Compétences prioritaires à acquérir" vide (onglet Prédictions du Marché) : le frontend lisait gap.skill_name/gap.related_sectors alors que le backend renvoie name/sectors. Fallback ajouté dans ObservatoireView.jsx (~ligne 822). Vérifié par screenshot avec mike : les 2 lacunes prioritaires (FIMO/FCO, Arrimage/TMS) s'affichent avec leurs secteurs. NÉCESSITE REDÉPLOIEMENT.

- [x] (2026-08) FIX bouton "Lancer la détection IA" (onglet Détectées CV du Marché) sans effet : le frontend appelait GET /api/emerging/observatory qui N'EXISTAIT PAS (404 silencieux). Endpoint créé dans server.py (agrège get_user_emerging_competences en {top_emerging, by_category, by_level, total}). Vérifié E2E par screenshot avec mike : 12 compétences détectées, répartitions affichées. NÉCESSITE REDÉPLOIEMENT pour reactif.pro.

- [x] (2026-08) FIX bouton "Lancer l'analyse IA" de l'OPC (Preview) : l'endpoint POST /observatory/ia/analyse-complete dépassait le timeout proxy de 60s (502). Converti en tâche de fond : POST → {job_id}, GET /observatory/ia/analyse-complete/status?job_id= (collection opc_ia_jobs). Frontend OpcDediePage.jsx : fonction commune runAnalyseComplete (polling 4s, tolérante aux erreurs réseau transitoires) utilisée par le bouton header ET PredictifModule. Vérifié E2E par screenshot : succès en ~48s (12 émergentes, 8 corrélations, 8 trajectoires, 1 reco). NÉCESSITE REDÉPLOIEMENT.

## ⚠️ URL PREVIEW ACTUELLE
https://cv-analyzer-53.preview.emergentagent.com (l'ancienne skills-vault-16 est morte — cause des "Preview Unavailable")

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
