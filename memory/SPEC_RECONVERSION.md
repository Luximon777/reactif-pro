# SPEC — « Explorer une nouvelle trajectoire » (Reconversion) — Ma Trajectoire Professionnelle

## Philosophie
La reconversion n'est PAS une rupture : nouvelle lecture de l'expérience acquise.
Chaîne : ce que j'ai fait → ce que ça m'a appris → ce que je sais faire → transférable → métiers possibles → écart à combler → nouvelle trajectoire.
L'IA ouvre des possibles, la personne construit son choix (approche phénoménologique/constructiviste). JAMAIS « ce métier vous correspond » pour le niveau 3 — toujours « ce métier mérite d'être exploré parce que… ».

## Point d'entrée
Dans Ma Trajectoire, après la visualisation des expériences : bouton **« Explorer une nouvelle trajectoire »** (pas « Reconversion », trop restrictif).

## Porte d'entrée D'CLIC PRO (recommandé, PAS bloquant)
Écran intermédiaire : « Avant d'explorer… nous vous recommandons D'CLIC PRO » → [Faire D'CLIC PRO] [Continuer sans D'CLIC PRO].
Croisement : expériences + savoir-faire + savoir-être + compétences transférables + résultats D'CLIC PRO + aspirations.

## Page « Ma reconversion » — chaîne de cohérence affichée
MES EXPÉRIENCES → MES ACQUIS → MES COMPÉTENCES TRANSFÉRABLES → MÉTIERS POSSIBLES → ÉCART À COMBLER → NOUVELLE TRAJECTOIRE

## Curseur 3 niveaux (Proche ←→ Rupture)
1. **Évoluer** : métiers proches du même univers (ex: serveur → responsable de restauration)
2. **Me reconvertir** (par compétences transférables) : métiers différents réutilisant les acquis (ex: → conseiller clientèle)
3. **Explorer autrement** (rupture) : métiers très différents, formulés en hypothèses argumentées

## Fiche « passerelle professionnelle » (par métier proposé)
- Pourquoi ce métier peut vous correspondre / mérite d'être exploré
- Ce que vous possédez déjà : N compétences transférables
- Savoir-faire mobilisables • Savoir-être mobilisables
- Ce qu'il vous manque : N compétences techniques à acquérir
- Comment réduire l'écart : Formation • certification • PMSMP • enquête métier • mentor UBUNTOO
- Tester ce métier : → Enquête professionnelle → Immersion → **Ajouter ce métier à « Ma trajectoire »**

## Ligne de cohérence (différenciateur clé)
L'IA extrait les INVARIANTS de la personne à travers ses expériences (ex: Aider/expliquer/organiser/résoudre/transmettre) et produit une formulation narrative : « Malgré des environnements différents, votre trajectoire montre une constante : … fil conducteur de votre identité professionnelle. »
→ cohérence du CV → cohérence de l'IDENTITÉ professionnelle.

## Connexions
Apply VSI PRO, OPC (référentiel), UBUNTOO (mentors), Job Matching : hypothèse → exploration → validation par l'expérience → nouvelle trajectoire.

## Architecture technique proposée
- Backend : POST /api/trajectoire/explorer (job+polling, LLM gpt-5.2) → { ligne_coherence, invariants[], niveaux: {evoluer[], reconvertir[], explorer[]}, chaque métier = fiche passerelle {pourquoi, sf_mobilisables, se_mobilisables, transferables_count, manquantes[], reduire_ecart[], rome_code?} } — croiser avec rome_metiers/opc_metiers/opc_certifications (search_word_patterns).
- Frontend : bouton dans ParticulierView (Ma Trajectoire) → page/vue ReconversionView avec écran D'CLIC gateway, curseur 3 niveaux, fiches passerelles, CTA (enquête, immersion, ajouter à trajectoire → POST /api/trajectory/steps type "projet").
- D'CLIC : lire profile.dclic_* ; si absent → bannière recommandation.
