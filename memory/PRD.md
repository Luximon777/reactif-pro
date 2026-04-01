# RE'ACTIF PRO - Product Requirements Document

## Problème Original
Répliquer le design exact, les images et l'approche de "D'CLIC PRO" dans "Ré'Actif Pro". Application de réactivation rapide des parcours vers l'emploi avec intelligence professionnelle.

## Architecture
- **Frontend**: React + Shadcn/UI + Tailwind CSS
- **Backend**: FastAPI + MongoDB
- **IA**: GPT-5.2 via Emergent LLM Key (analyse CV, OCR, prédictions personnalisées)
- **Stockage**: Emergent Object Storage (documents coffre-fort)

## Navigation (8 onglets)
1. Accueil
2. Mon Profil (+ bandeau D'CLIC PRO)
3. Ma Trajectoire
4. Mes Compétences
5. Le Marché (Observatoire, Évolution, Explorateur)
6. Opportunités (Matching, Formations)
7. Mon Coffre-fort
8. Confidentialité

## Fonctionnalités Implémentées

### Phase 1 - Core (DONE)
- Authentification par pseudo
- Import D'CLIC PRO (code d'accès)
- Analyse CV (avec OCR pour PDF scannés via PyMuPDF + GPT-5.2 Vision)
- Passeport de compétences
- Coffre-fort numérique

### Phase 2 - Personnalisation (DONE)
- Indice d'Évolution personnalisé (stats profil utilisateur)
- Stats à 0 pour nouveaux comptes
- Suppression MBTI dans D'CLIC Boost
- Restructuration navigation (8 onglets sans doublons)
- Bandeau D'CLIC PRO dans Mon Profil

### Phase 3 - Personnalisation Observatoire (DONE - 01/04/2026)
- **Prédictions personnalisées**: Onglet "Prédictions" basé sur le profil utilisateur (secteurs, compétences émergentes/déclin, alertes)
- **Détectées CV personnalisées**: Croisement CV/marché pour détecter compétences émergentes spécifiques
- Nettoyage route dupliquée `/emerging/observatory`

## Backlog

### P1 - Priorité haute
- Génération IA de narratif personnalisé à la fin des résultats D'CLIC PRO

### P2 - Priorité moyenne
- Intégration FranceConnect

### P3 - Priorité basse
- Ateliers de Codéveloppement + micro-titres/badges
- Export PDF du parcours trajectoire
- Refactoring PartenaireView.jsx

## Comptes Test
- testboost / Solerys777! (avec données CV)
- bob30 / Solerys777! (avec données)
- bob35 (pseudo sans mot de passe)
- newtest99 (compte vierge, pseudo sans mot de passe)
