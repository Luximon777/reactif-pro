# CAHIER DES CHARGES — UBUNTOO Web (reactif.pro) — résumé opérationnel

Version complète fournie par l'utilisateur (2026-06). Points clés :

## Positionnement
Réseau professionnel, communautaire et solidaire de RE'ACTIF PRO (PAS un réseau social généraliste). Entraide, mise en relation, mentorat, reconversions, partage d'opportunités. Pas de mécanique de "likes"/popularité → contributions utiles ("Utile").
Principe UX : « De qui ou de quoi ai-je besoin pour avancer dans ma trajectoire professionnelle ? »

## Principes
- Mobile First (navigation basse : Accueil | Réseau | Communautés | Messages | Profil)
- Compte unique Ré'Actif Pro (pas de compte Ubuntoo indépendant, SSO via token)
- Profil Ubuntoo auto-alimenté par le profil/passeport Ré'Actif Pro (pas de ressaisie)
- Confidentialité 3 niveaux par information : Privé / Réseau UBUNTOO / Professionnel
- Privacy by default (paramètres par défaut protecteurs)
- Mise en relation UNIQUEMENT par consentement : demande + motif → Accepter / Refuser / Voir le profil. Conversation créée après acceptation.
- API-first : toutes fonctionnalités via API sécurisées (préparer l'app mobile)

## MVP (section 31) — PÉRIMÈTRE ITÉRATION ACTUELLE
1. Profil communautaire (identité pro, projet, expériences, compétences, soft skills, centres d'intérêt, disponibilité pour aider : mentorat/partage d'expérience/conseil métier/découverte secteur/prépa entretien/réseau/orientation)
2. Gestion de la confidentialité (3 niveaux, par information)
3. Recherche de membres
4. Demande de mise en relation (consentement)
5. Réseau professionnel (contacts)
6. Messagerie individuelle
7. Communautés (~20 pré-créées, 4 catégories : Métiers [Informatique, Industrie, Commerce, Santé, Logistique, BTP] / Situations [Reconversion, Recherche d'emploi, Création d'entreprise, Premier emploi, Retour à l'emploi] / Territoires [Strasbourg, Alsace, Grand Est, France, Transfrontalier] / Thématiques [Soft skills, IA, Management, Handicap et emploi, Mobilité professionnelle, Formation]) + création par utilisateurs
8. Publications (types : question, expérience, information, ressource, opportunité, demande d'aide)
9. Signalement / modération (motifs : comportement inapproprié, discrimination, harcèlement, spam, fraude, contenu commercial, fausse info, atteinte confidentialité)
10. Notifications

## Phase 2 (plus tard)
Messagerie de groupe, mentorat, badges, opportunités, recommandations IA, intégration D'CLIC PRO et Ma trajectoire (trouver des pros du métier exploré), Carte Emploi, comptes employeurs.

## Phase 3
App mobile open source, push, audio/vidéo, transfrontalier.

## Tableau de bord accueil (section 5)
Mon réseau (nb contacts + récents) / Mes communautés / Mes conversations / Opportunités (phase 2) / Mes contributions / Mes badges (phase 2 — lien vers progression existante possible).

## Indicateurs : utilité pro réelle (mises en relation acceptées, taux de réponse, participation), PAS temps passé.

## Décisions utilisateur (2026-06)
- Reconstruction complète de zéro (nouvelles collections ubuntoo2_*, nouveau frontend /src/ubuntoo2/)
- MVP complet section 31
- Seed ~20 communautés + création libre par utilisateurs
- Nouvelle identité visuelle via design agent (mobile first)
