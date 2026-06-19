"""D'CLIC PRO — Données statiques (questions, référentiels, mappings)
Source: GitHub Luximon777/declic-pro
"""
from typing import Dict, List, Any


# ======================================================================
# VISUAL_QUESTIONS
# ======================================================================
VISUAL_QUESTIONS = [
    # BLOC 1 - SOURCE D'ÉNERGIE (E/I)
    {
        "id": "v1",
        "question": "Après une journée intense, vous préférez...",
        "category": "energie",
        "type": "visual",
        "choices": [
            {
                "id": "v1a",
                "value": "E",
                "label": "Retrouver des amis",
                "image": "https://images.unsplash.com/photo-1511988617509-a57c8a288659?w=600&h=400&fit=crop",
                "alt": "Groupe d'amis qui discutent"
            },
            {
                "id": "v1b",
                "value": "I",
                "label": "Un moment seul(e)",
                "image": "https://images.unsplash.com/photo-1506880018603-83d5b814b5a6?w=600&h=400&fit=crop",
                "alt": "Personne seule en réflexion"
            }
        ]
    },
    {
        "id": "v2",
        "question": "En réunion, vous êtes plutôt...",
        "category": "energie",
        "type": "visual",
        "choices": [
            {
                "id": "v2a",
                "value": "E",
                "label": "Je prends la parole",
                "image": "https://images.unsplash.com/photo-1660794483744-d6c7ab2ac6fd?w=600",
                "alt": "Personne qui présente"
            },
            {
                "id": "v2b",
                "value": "I",
                "label": "J'écoute et je réfléchis",
                "image": "https://images.pexels.com/photos/7437095/pexels-photo-7437095.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Personne attentive en réunion"
            }
        ]
    },
    
    # BLOC 2 - TRAITEMENT DE L'INFO (S/N)
    {
        "id": "v3",
        "question": "Pour résoudre un problème, je préfère...",
        "category": "perception",
        "type": "visual",
        "choices": [
            {
                "id": "v3a",
                "value": "S",
                "label": "Des étapes concrètes",
                "image": "https://images.unsplash.com/photo-1581291518857-4e27b48ff24e?w=600&h=400&fit=crop",
                "alt": "Main écrivant une checklist"
            },
            {
                "id": "v3b",
                "value": "N",
                "label": "Une vision globale",
                "image": "https://images.unsplash.com/photo-1486912500284-6f2462ba07ea?w=600&h=400&fit=crop",
                "alt": "Mind map avec idées et solutions"
            }
        ]
    },
    {
        "id": "v4",
        "question": "Classez ces approches de la plus naturelle (1) à la moins naturelle (4) pour vous :",
        "category": "perception",
        "type": "ranking",
        "instruction": "Glissez ou numérotez vos choix de 1 (le plus naturel) à 4 (le moins naturel)",
        "choices": [
            {
                "id": "v4a",
                "value": "S1",
                "label": "Les faits concrets et vérifiables",
                "image": "https://images.pexels.com/photos/590020/pexels-photo-590020.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Données et graphiques"
            },
            {
                "id": "v4b",
                "value": "N1",
                "label": "Les idées innovantes et créatives",
                "image": "https://images.pexels.com/photos/7369/startup-photos.jpg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Brainstorming et idées sur whiteboard"
            },
            {
                "id": "v4c",
                "value": "S2",
                "label": "Les méthodes éprouvées et pratiques",
                "image": "https://images.pexels.com/photos/416405/pexels-photo-416405.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Outils pratiques"
            },
            {
                "id": "v4d",
                "value": "N2",
                "label": "Les connexions et les possibilités futures",
                "image": "https://images.pexels.com/photos/3183150/pexels-photo-3183150.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Vision future"
            }
        ]
    },
    
    # BLOC 3 - MODE DE DÉCISION (T/F)
    {
        "id": "v5",
        "question": "Pour prendre une décision importante...",
        "category": "decision",
        "type": "visual",
        "choices": [
            {
                "id": "v5a",
                "value": "T",
                "label": "J'analyse les données",
                "image": "https://images.unsplash.com/photo-1666875753105-c63a6f3bdc86?w=600&h=400&fit=crop",
                "alt": "Analyse de données"
            },
            {
                "id": "v5b",
                "value": "F",
                "label": "J'écoute mon cœur",
                "image": "https://images.unsplash.com/photo-1579208570378-8c970854bc23?w=600&h=400&fit=crop",
                "alt": "Personne mains sur le coeur"
            }
        ]
    },
    {
        "id": "v6",
        "question": "Face à un conflit, je cherche d'abord...",
        "category": "decision",
        "type": "visual",
        "choices": [
            {
                "id": "v6a",
                "value": "T",
                "label": "La solution logique",
                "image": "https://images.pexels.com/photos/7370/startup-photo.jpg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Personne devant un diagramme logique"
            },
            {
                "id": "v6b",
                "value": "F",
                "label": "L'harmonie du groupe",
                "image": "https://images.pexels.com/photos/6340697/pexels-photo-6340697.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Équipe unie"
            }
        ]
    },
    
    # BLOC 4 - ORGANISATION (J/P)
    {
        "id": "v7",
        "question": "Je préfère travailler avec...",
        "category": "structure",
        "type": "visual",
        "choices": [
            {
                "id": "v7a",
                "value": "J",
                "label": "Un planning précis",
                "image": "https://images.unsplash.com/photo-1435527173128-983b87201f4d?w=600&h=400&fit=crop",
                "alt": "Calendrier et planning"
            },
            {
                "id": "v7b",
                "value": "P",
                "label": "De la flexibilité",
                "image": "https://images.unsplash.com/photo-1527856263669-12c3a0af2aa6?w=600&h=400&fit=crop",
                "alt": "Personne flexible avec post-its"
            }
        ]
    },
    {
        "id": "v8",
        "question": "Face à un imprévu...",
        "category": "structure",
        "type": "visual",
        "choices": [
            {
                "id": "v8a",
                "value": "J",
                "label": "Je réorganise tout",
                "image": "https://images.unsplash.com/photo-1435527173128-983b87201f4d?w=600",
                "alt": "Organisation structurée"
            },
            {
                "id": "v8b",
                "value": "P",
                "label": "Je m'adapte au fur et à mesure",
                "image": "https://images.pexels.com/photos/11719266/pexels-photo-11719266.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Personne décontractée faisant OK"
            }
        ]
    },
    
    # BLOC 5 - STYLE DISC (4 choix à classer)
    {
        "id": "v9",
        "question": "Classez ces styles de travail du plus naturel (1) au moins naturel (4) pour vous :",
        "category": "disc",
        "type": "ranking",
        "instruction": "Glissez ou numérotez vos choix de 1 (le plus naturel) à 4 (le moins naturel)",
        "choices": [
            {
                "id": "v9a",
                "value": "D",
                "label": "Décider et agir vite",
                "image": "https://images.pexels.com/photos/684387/pexels-photo-684387.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Leader décisif qui pointe"
            },
            {
                "id": "v9b",
                "value": "I",
                "label": "Motiver et convaincre",
                "image": "https://images.pexels.com/photos/29708260/pexels-photo-29708260.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Speaker enthousiaste devant public"
            },
            {
                "id": "v9c",
                "value": "S",
                "label": "Soutenir et coopérer",
                "image": "https://images.pexels.com/photos/5684551/pexels-photo-5684551.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Mains jointes solidarité équipe"
            },
            {
                "id": "v9d",
                "value": "C",
                "label": "Analyser et vérifier",
                "image": "https://images.unsplash.com/photo-1631558554770-74e921444006?w=600",
                "alt": "Scientifique analyse précise microscope"
            }
        ]
    },
    {
        "id": "v10",
        "question": "Classez vos réactions face aux difficultés, de la plus naturelle (1) à la moins naturelle (4) :",
        "category": "disc",
        "type": "ranking",
        "instruction": "Glissez ou numérotez vos choix de 1 (le plus naturel) à 4 (le moins naturel)",
        "choices": [
            {
                "id": "v10a",
                "value": "D",
                "label": "J'accélère pour rattraper",
                "image": "https://images.pexels.com/photos/684387/pexels-photo-684387.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Action rapide"
            },
            {
                "id": "v10b",
                "value": "I",
                "label": "Je cherche une alternative créative",
                "image": "https://images.pexels.com/photos/3094218/pexels-photo-3094218.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Créativité"
            },
            {
                "id": "v10c",
                "value": "S",
                "label": "Je reste calme et patient",
                "image": "https://images.pexels.com/photos/3756165/pexels-photo-3756165.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Calme et patience"
            },
            {
                "id": "v10d",
                "value": "C",
                "label": "J'analyse ce qui n'a pas marché",
                "image": "https://images.pexels.com/photos/5466247/pexels-photo-5466247.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Analyse détaillée"
            }
        ]
    },
    
    # BLOC 6 - MOTIVATION ENNÉAGRAMME (classement des 4 premiers choix)
    {
        "id": "v11",
        "question": "Classez ce qui vous rend heureux/se, du plus important (1) au moins important (4) :",
        "category": "ennea",
        "type": "ranking",
        "instruction": "Sélectionnez vos 4 choix dans l'ordre de préférence (1 = le plus important)",
        "choices": [
            {"id": "v11a", "value": "2", "label": "🤝 Aider les autres"},
            {"id": "v11b", "value": "3", "label": "🏆 Réussir mes objectifs"},
            {"id": "v11c", "value": "5", "label": "📚 Apprendre et comprendre"},
            {"id": "v11d", "value": "4", "label": "🎨 Créer quelque chose d'unique"},
            {"id": "v11e", "value": "6", "label": "🏠 Avoir de la stabilité"},
            {"id": "v11f", "value": "7", "label": "🌍 Vivre des aventures"},
            {"id": "v11g", "value": "8", "label": "💪 Avoir de l'influence"},
            {"id": "v11h", "value": "9", "label": "☮️ Être en paix avec tous"},
            {"id": "v11i", "value": "1", "label": "✅ Faire les choses bien"}
        ]
    },
    {
        "id": "v12",
        "question": "Classez ce qui vous stresse le plus, du plus stressant (1) au moins stressant (4) :",
        "category": "ennea",
        "type": "ranking",
        "instruction": "Sélectionnez vos 4 choix dans l'ordre (1 = le plus stressant)",
        "choices": [
            {"id": "v12a", "value": "2", "label": "😔 Me sentir inutile"},
            {"id": "v12b", "value": "3", "label": "😰 Échouer ou être ignoré(e)"},
            {"id": "v12c", "value": "5", "label": "🤯 Ne pas comprendre"},
            {"id": "v12d", "value": "4", "label": "😶 Être banal(e) ou incompris(e)"},
            {"id": "v12e", "value": "6", "label": "😟 L'incertitude et l'insécurité"},
            {"id": "v12f", "value": "7", "label": "🔒 Être limité(e) ou ennuyé(e)"},
            {"id": "v12g", "value": "8", "label": "⛓️ Être contrôlé(e) ou faible"},
            {"id": "v12h", "value": "9", "label": "⚔️ Les conflits"},
            {"id": "v12i", "value": "1", "label": "❌ L'imperfection et les erreurs"}
        ]
    },
    
    # ============================================================================
    # BLOC 7 - INTÉRÊTS PROFESSIONNELS RIASEC (Holland Codes)
    # 8 nouvelles questions pour affiner le profil RIASEC
    # ============================================================================
    
    # Question R1 - Réaliste vs Investigateur (vie quotidienne)
    {
        "id": "r1",
        "question": "Chez vous, quand quelque chose tombe en panne...",
        "category": "riasec",
        "type": "visual",
        "riasec_weight": {"primary": "R", "secondary": "I"},
        "choices": [
            {
                "id": "r1a",
                "value": "R",
                "label": "Je répare moi-même",
                "image": "https://images.pexels.com/photos/4491881/pexels-photo-4491881.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Personne qui répare un appareil avec des outils"
            },
            {
                "id": "r1b",
                "value": "I",
                "label": "Je cherche à comprendre pourquoi",
                "image": "https://images.pexels.com/photos/4145190/pexels-photo-4145190.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Personne qui analyse un problème technique"
            }
        ]
    },
    
    # Question R2 - Artistique vs Social (vie quotidienne)
    {
        "id": "r2",
        "question": "Pendant votre temps libre, vous préférez...",
        "category": "riasec",
        "type": "visual",
        "riasec_weight": {"primary": "A", "secondary": "S"},
        "choices": [
            {
                "id": "r2a",
                "value": "A",
                "label": "Créer (dessiner, écrire, jouer de la musique...)",
                "image": "https://images.pexels.com/photos/3094218/pexels-photo-3094218.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Personne en train de peindre ou créer"
            },
            {
                "id": "r2b",
                "value": "S",
                "label": "Aider ou accompagner quelqu'un",
                "image": "https://images.pexels.com/photos/6646918/pexels-photo-6646918.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Personne aidant une autre personne"
            }
        ]
    },
    
    # Question R3 - Entreprenant vs Conventionnel (professionnel)
    {
        "id": "r3",
        "question": "Dans un projet professionnel, vous préférez...",
        "category": "riasec",
        "type": "visual",
        "riasec_weight": {"primary": "E", "secondary": "C"},
        "choices": [
            {
                "id": "r3a",
                "value": "E",
                "label": "Convaincre et mener l'équipe",
                "image": "https://images.pexels.com/photos/3184291/pexels-photo-3184291.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Leader présentant devant son équipe"
            },
            {
                "id": "r3b",
                "value": "C",
                "label": "Organiser et structurer le travail",
                "image": "https://images.pexels.com/photos/669615/pexels-photo-669615.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Bureau bien organisé avec classements"
            }
        ]
    },
    
    # Question R4 - Classement 4 activités (vie quotidienne)
    {
        "id": "r4",
        "question": "Classez ces activités de la plus agréable (1) à la moins agréable (4) :",
        "category": "riasec",
        "type": "ranking",
        "instruction": "Glissez ou numérotez de 1 (ce que j'aime le plus) à 4 (ce que j'aime le moins)",
        "choices": [
            {
                "id": "r4a",
                "value": "R",
                "label": "Bricoler, jardiner ou cuisiner",
                "image": "https://images.pexels.com/photos/5691622/pexels-photo-5691622.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Personne qui bricole"
            },
            {
                "id": "r4b",
                "value": "A",
                "label": "Décorer, photographier ou customiser",
                "image": "https://images.pexels.com/photos/1092644/pexels-photo-1092644.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Décoration artistique"
            },
            {
                "id": "r4c",
                "value": "S",
                "label": "Rendre service ou conseiller un proche",
                "image": "https://images.pexels.com/photos/7176319/pexels-photo-7176319.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Deux personnes en discussion d'aide"
            },
            {
                "id": "r4d",
                "value": "E",
                "label": "Organiser une sortie ou un événement",
                "image": "https://images.pexels.com/photos/7551617/pexels-photo-7551617.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Organisation d'événement"
            }
        ]
    },
    
    # Question R5 - Investigateur vs Artistique (professionnel)
    {
        "id": "r5",
        "question": "Pour résoudre un problème complexe au travail...",
        "category": "riasec",
        "type": "visual",
        "riasec_weight": {"primary": "I", "secondary": "A"},
        "choices": [
            {
                "id": "r5a",
                "value": "I",
                "label": "J'analyse les données et les faits",
                "image": "https://images.pexels.com/photos/590020/pexels-photo-590020.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Analyse de données et graphiques"
            },
            {
                "id": "r5b",
                "value": "A",
                "label": "J'imagine des solutions créatives",
                "image": "https://images.pexels.com/photos/6224/hands-people-woman-working.jpg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Brainstorming créatif"
            }
        ]
    },
    
    # Question R6 - Classement 4 environnements de travail (professionnel)
    {
        "id": "r6",
        "question": "Classez ces environnements de travail du plus attirant (1) au moins attirant (4) :",
        "category": "riasec",
        "type": "ranking",
        "instruction": "Glissez ou numérotez de 1 (le plus attirant) à 4 (le moins attirant)",
        "choices": [
            {
                "id": "r6a",
                "value": "R",
                "label": "Atelier, chantier ou terrain",
                "image": "https://images.pexels.com/photos/1216589/pexels-photo-1216589.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Atelier avec outils"
            },
            {
                "id": "r6b",
                "value": "I",
                "label": "Laboratoire ou centre de recherche",
                "image": "https://images.pexels.com/photos/2280571/pexels-photo-2280571.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Laboratoire scientifique"
            },
            {
                "id": "r6c",
                "value": "C",
                "label": "Bureau avec procédures claires",
                "image": "https://images.pexels.com/photos/1170412/pexels-photo-1170412.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Bureau organisé"
            },
            {
                "id": "r6d",
                "value": "E",
                "label": "Open space dynamique ou commercial",
                "image": "https://images.pexels.com/photos/1181396/pexels-photo-1181396.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Open space moderne"
            }
        ]
    },
    
    # Question R7 - Social vs Réaliste (vie quotidienne)
    {
        "id": "r7",
        "question": "Le week-end, vous seriez plutôt du genre à...",
        "category": "riasec",
        "type": "visual",
        "riasec_weight": {"primary": "S", "secondary": "R"},
        "choices": [
            {
                "id": "r7a",
                "value": "S",
                "label": "Faire du bénévolat ou aider dans une association",
                "image": "https://images.pexels.com/photos/6646917/pexels-photo-6646917.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Bénévolat et entraide"
            },
            {
                "id": "r7b",
                "value": "R",
                "label": "Faire du sport ou une activité physique",
                "image": "https://images.pexels.com/photos/3764011/pexels-photo-3764011.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Activité sportive en extérieur"
            }
        ]
    },
    
    # Question R8 - Classement 4 types de tâches (professionnel)
    {
        "id": "r8",
        "question": "Classez ces tâches professionnelles de la plus motivante (1) à la moins motivante (4) :",
        "category": "riasec",
        "type": "ranking",
        "instruction": "Glissez ou numérotez de 1 (la plus motivante) à 4 (la moins motivante)",
        "choices": [
            {
                "id": "r8a",
                "value": "I",
                "label": "Analyser des données ou des rapports",
                "image": "https://images.pexels.com/photos/669619/pexels-photo-669619.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Analyse de données"
            },
            {
                "id": "r8b",
                "value": "A",
                "label": "Concevoir un visuel ou rédiger un contenu",
                "image": "https://images.pexels.com/photos/326503/pexels-photo-326503.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Design et création de contenu"
            },
            {
                "id": "r8c",
                "value": "S",
                "label": "Former ou accompagner des collègues",
                "image": "https://images.pexels.com/photos/5212345/pexels-photo-5212345.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Formation et accompagnement"
            },
            {
                "id": "r8d",
                "value": "C",
                "label": "Vérifier et classer des documents",
                "image": "https://images.pexels.com/photos/4792285/pexels-photo-4792285.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Organisation de documents"
            }
        ]
    },
    
    # ============================================================================
    # BLOC 8 - VERTUS ET VALEURS (Archéologie des Compétences)
    # 6 questions pour mesurer les vertus dominantes de Seligman/Peterson
    # ============================================================================
    
    # Question VV1 - Sagesse vs Courage (valeurs fondamentales)
    {
        "id": "vv1",
        "question": "Face à un défi important dans votre vie, vous comptez d'abord sur...",
        "category": "vertus",
        "type": "visual",
        "vertus_weight": {"primary": "sagesse", "secondary": "courage"},
        "choices": [
            {
                "id": "vv1a",
                "value": "sagesse",
                "label": "La réflexion et l'analyse pour comprendre",
                "image": "https://images.pexels.com/photos/3808057/pexels-photo-3808057.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Personne en réflexion"
            },
            {
                "id": "vv1b",
                "value": "courage",
                "label": "La détermination et l'action pour avancer",
                "image": "https://images.pexels.com/photos/3756165/pexels-photo-3756165.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Personne déterminée"
            }
        ]
    },
    
    # Question VV2 - Humanité vs Justice (relations sociales)
    {
        "id": "vv2",
        "question": "Dans vos relations avec les autres, ce qui compte le plus pour vous...",
        "category": "vertus",
        "type": "visual",
        "vertus_weight": {"primary": "humanite", "secondary": "justice"},
        "choices": [
            {
                "id": "vv2a",
                "value": "humanite",
                "label": "L'empathie et le soutien émotionnel",
                "image": "https://images.pexels.com/photos/6646918/pexels-photo-6646918.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Soutien et empathie"
            },
            {
                "id": "vv2b",
                "value": "justice",
                "label": "L'équité et le respect des engagements",
                "image": "https://images.pexels.com/photos/5668858/pexels-photo-5668858.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Justice et équité"
            }
        ]
    },
    
    # Question VV3 - Tempérance vs Transcendance (vie intérieure)
    {
        "id": "vv3",
        "question": "Ce qui vous apporte le plus de sérénité au quotidien...",
        "category": "vertus",
        "type": "visual",
        "vertus_weight": {"primary": "temperance", "secondary": "transcendance"},
        "choices": [
            {
                "id": "vv3a",
                "value": "temperance",
                "label": "L'organisation et la maîtrise de soi",
                "image": "https://images.pexels.com/photos/6802049/pexels-photo-6802049.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Organisation et calme"
            },
            {
                "id": "vv3b",
                "value": "transcendance",
                "label": "La beauté, la gratitude et le sens de la vie",
                "image": "https://images.pexels.com/photos/3560044/pexels-photo-3560044.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Contemplation et gratitude"
            }
        ]
    },
    
    # Question VV4 - Classement des 4 valeurs prioritaires (Schwartz)
    {
        "id": "vv4",
        "question": "Classez ces valeurs de la plus importante (1) à la moins importante (4) pour vous :",
        "category": "valeurs",
        "type": "ranking",
        "instruction": "Glissez ou numérotez de 1 (la plus importante) à 4 (la moins importante)",
        "choices": [
            {
                "id": "vv4a",
                "value": "autonomie",
                "label": "Autonomie - Liberté de penser et d'agir",
                "image": "https://images.pexels.com/photos/1051838/pexels-photo-1051838.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Liberté et autonomie"
            },
            {
                "id": "vv4b",
                "value": "bienveillance",
                "label": "Bienveillance - Prendre soin des proches",
                "image": "https://images.pexels.com/photos/7176317/pexels-photo-7176317.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Prendre soin des autres"
            },
            {
                "id": "vv4c",
                "value": "reussite",
                "label": "Réussite - Accomplissement personnel",
                "image": "https://images.pexels.com/photos/3184291/pexels-photo-3184291.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Succès et accomplissement"
            },
            {
                "id": "vv4d",
                "value": "securite",
                "label": "Sécurité - Stabilité et harmonie",
                "image": "https://images.pexels.com/photos/7176026/pexels-photo-7176026.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Stabilité et sécurité"
            }
        ]
    },
    
    # Question VV5 - Qualités humaines prioritaires
    {
        "id": "vv5",
        "question": "On vous reconnaît surtout pour...",
        "category": "qualites",
        "type": "visual",
        "choices": [
            {
                "id": "vv5a",
                "value": "creativite",
                "label": "Votre créativité et votre curiosité",
                "image": "https://images.pexels.com/photos/3094218/pexels-photo-3094218.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Créativité"
            },
            {
                "id": "vv5b",
                "value": "generosite",
                "label": "Votre générosité et votre écoute",
                "image": "https://images.pexels.com/photos/6646917/pexels-photo-6646917.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Générosité et écoute"
            }
        ]
    },
    
    # Question VV6 - Classement des savoir-être professionnels
    {
        "id": "vv6",
        "question": "Classez ces savoir-être du plus naturel (1) au moins naturel (4) pour vous :",
        "category": "savoirs_etre",
        "type": "ranking",
        "instruction": "Glissez ou numérotez de 1 (le plus naturel) à 4 (le moins naturel)",
        "choices": [
            {
                "id": "vv6a",
                "value": "initiative",
                "label": "Prendre des initiatives et proposer des idées",
                "image": "https://images.pexels.com/photos/3184325/pexels-photo-3184325.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Prise d'initiative"
            },
            {
                "id": "vv6b",
                "value": "ecoute",
                "label": "Être à l'écoute et au service des autres",
                "image": "https://images.pexels.com/photos/5212345/pexels-photo-5212345.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Écoute active"
            },
            {
                "id": "vv6c",
                "value": "rigueur",
                "label": "Faire preuve de rigueur et de précision",
                "image": "https://images.pexels.com/photos/669615/pexels-photo-669615.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Rigueur et précision"
            },
            {
                "id": "vv6d",
                "value": "leadership",
                "label": "Inspirer et donner du sens aux autres",
                "image": "https://images.pexels.com/photos/3184299/pexels-photo-3184299.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": "Leadership"
            }
        ]
    }
]


# ======================================================================
# QUESTIONNAIRE
# ======================================================================
QUESTIONNAIRE = [
    # PARTIE 1 - ENERGIE & INTERACTION (MBTI E/I + DISC)
    {
        "id": "q1",
        "text": "Après une journée bien remplie (cours, travail, activités...), vous préférez :",
        "category": "energie",
        "options": [
            {"id": "q1a", "text": "Retrouver des amis ou votre famille pour discuter", "value": "E"},
            {"id": "q1b", "text": "Prendre du temps seul(e) pour vous ressourcer", "value": "I"}
        ]
    },
    {
        "id": "q2",
        "text": "Lors d'une discussion de groupe (entre amis, en famille ou en réunion) :",
        "category": "energie",
        "options": [
            {"id": "q2a", "text": "Vous prenez facilement la parole et partagez vos idées", "value": "E"},
            {"id": "q2b", "text": "Vous écoutez d'abord, puis intervenez après réflexion", "value": "I"}
        ]
    },
    {
        "id": "q3",
        "text": "Face à quelqu'un qui impose fortement son point de vue :",
        "category": "disc",
        "options": [
            {"id": "q3a", "text": "Vous défendez clairement votre position", "value": "D"},
            {"id": "q3b", "text": "Vous cherchez à détendre l'atmosphère avec diplomatie", "value": "I"},
            {"id": "q3c", "text": "Vous analysez ses arguments avant de répondre", "value": "C"},
            {"id": "q3d", "text": "Vous vous adaptez pour maintenir l'harmonie", "value": "S"}
        ]
    },
    # PARTIE 2 - PRISE DE DECISION (MBTI T/F - S/N)
    {
        "id": "q4",
        "text": "Quand vous devez faire un choix important (achat, orientation, projet...) :",
        "category": "perception",
        "options": [
            {"id": "q4a", "text": "Vous vous appuyez sur des éléments concrets et vérifiables", "value": "S"},
            {"id": "q4b", "text": "Vous imaginez les possibilités et suivez votre intuition", "value": "N"}
        ]
    },
    {
        "id": "q5",
        "text": "Un(e) ami(e) ou proche traverse une période difficile :",
        "category": "decision",
        "options": [
            {"id": "q5a", "text": "Vous l'aidez à trouver des solutions pratiques", "value": "T"},
            {"id": "q5b", "text": "Vous êtes à l'écoute de ses émotions et le/la soutenez", "value": "F"}
        ]
    },
    {
        "id": "q6",
        "text": "Pour apprendre quelque chose de nouveau ou résoudre un problème :",
        "category": "perception",
        "options": [
            {"id": "q6a", "text": "Vous préférez suivre une méthode éprouvée, étape par étape", "value": "S"},
            {"id": "q6b", "text": "Vous aimez expérimenter et trouver votre propre façon de faire", "value": "N"}
        ]
    },
    # PARTIE 3 - STRUCTURE & ACTION (MBTI J/P - DISC D/C)
    {
        "id": "q7",
        "text": "Dans votre vie quotidienne (études, travail, loisirs...) :",
        "category": "structure",
        "options": [
            {"id": "q7a", "text": "Vous aimez planifier et savoir ce qui vous attend", "value": "J"},
            {"id": "q7b", "text": "Vous préférez rester flexible et vous adapter au fil de l'eau", "value": "P"}
        ]
    },
    {
        "id": "q8",
        "text": "Face à un défi ou un objectif ambitieux (examen, projet, compétition...) :",
        "category": "disc",
        "options": [
            {"id": "q8a", "text": "Vous foncez avec détermination", "value": "D"},
            {"id": "q8b", "text": "Vous préparez soigneusement chaque étape", "value": "C"},
            {"id": "q8c", "text": "Vous motivez les autres à vous rejoindre", "value": "I"},
            {"id": "q8d", "text": "Vous vous adaptez aux circonstances avec patience", "value": "S"}
        ]
    },
    {
        "id": "q9",
        "text": "Quand quelque chose ne se passe pas comme prévu (retard, imprévu, échec...) :",
        "category": "disc",
        "options": [
            {"id": "q9a", "text": "Vous accélérez pour rattraper le temps perdu", "value": "D"},
            {"id": "q9b", "text": "Vous analysez ce qui n'a pas fonctionné", "value": "C"},
            {"id": "q9c", "text": "Vous rassurez votre entourage et restez calme", "value": "S"},
            {"id": "q9d", "text": "Vous cherchez une alternative créative", "value": "I"}
        ]
    },
    # PARTIE 4 - MOTIVATION PROFONDE (Ennéagramme masqué)
    {
        "id": "q10",
        "text": "Ce qui vous donne le plus de satisfaction dans la vie :",
        "category": "ennea",
        "options": [
            {"id": "q10a", "text": "Aider les autres et me sentir utile", "value": "2"},
            {"id": "q10b", "text": "Atteindre mes objectifs et être reconnu(e)", "value": "3"},
            {"id": "q10c", "text": "Comprendre en profondeur comment les choses fonctionnent", "value": "5"},
            {"id": "q10d", "text": "Créer quelque chose d'unique et exprimer ma sensibilité", "value": "4"},
            {"id": "q10e", "text": "Avoir un cadre stable et des repères fiables", "value": "6"},
            {"id": "q10f", "text": "Prendre les décisions et avoir de l'influence", "value": "8"},
            {"id": "q10g", "text": "Vivre en harmonie avec les autres", "value": "9"},
            {"id": "q10h", "text": "Vivre des expériences variées et stimulantes", "value": "7"}
        ]
    },
    {
        "id": "q11",
        "text": "Ce qui vous affecte le plus négativement :",
        "category": "ennea",
        "options": [
            {"id": "q11a", "text": "Sentir que mes efforts ne sont pas appréciés", "value": "2"},
            {"id": "q11b", "text": "Échouer ou ne pas atteindre mes objectifs", "value": "3"},
            {"id": "q11c", "text": "Être perçu(e) comme incompétent(e) ou ignorant(e)", "value": "5"},
            {"id": "q11d", "text": "Ne pas être compris(e) ou reconnu(e) dans ma singularité", "value": "4"},
            {"id": "q11e", "text": "Me retrouver dans l'incertitude ou l'insécurité", "value": "6"},
            {"id": "q11f", "text": "Perdre le contrôle de la situation", "value": "8"},
            {"id": "q11g", "text": "Les conflits et les tensions", "value": "9"},
            {"id": "q11h", "text": "La routine et l'ennui", "value": "7"}
        ]
    },
    {
        "id": "q12",
        "text": "En période de stress ou de pression, vous avez tendance à :",
        "category": "ennea",
        "options": [
            {"id": "q12a", "text": "Vous occuper encore plus des autres pour vous sentir utile", "value": "2"},
            {"id": "q12b", "text": "Travailler plus dur pour prouver votre valeur", "value": "3"},
            {"id": "q12c", "text": "Vous isoler pour réfléchir et analyser", "value": "5"},
            {"id": "q12d", "text": "Vous replier sur vos émotions ou vous disperser", "value": "4"},
            {"id": "q12e", "text": "Chercher des garanties et du soutien", "value": "6"},
            {"id": "q12f", "text": "Prendre le contrôle et imposer votre rythme", "value": "8"},
            {"id": "q12g", "text": "Éviter les confrontations et temporiser", "value": "9"},
            {"id": "q12h", "text": "Chercher des distractions ou de nouveaux projets", "value": "7"}
        ]
    },
    # PARTIE 5 - POSTURE RELATIONNELLE (DISC final)
    {
        "id": "q13",
        "text": "Vos proches (amis, famille) diraient de vous que vous êtes plutôt :",
        "category": "disc",
        "options": [
            {"id": "q13a", "text": "Déterminé(e) et direct(e)", "value": "D"},
            {"id": "q13b", "text": "Enthousiaste et communicatif(ve)", "value": "I"},
            {"id": "q13c", "text": "Calme et fiable", "value": "S"},
            {"id": "q13d", "text": "Réfléchi(e) et rigoureux(se)", "value": "C"}
        ]
    },
    {
        "id": "q14",
        "text": "En cas de désaccord avec quelqu'un (ami, famille, collègue...) :",
        "category": "disc",
        "options": [
            {"id": "q14a", "text": "Vous dites clairement ce que vous pensez", "value": "D"},
            {"id": "q14b", "text": "Vous cherchez le dialogue et le compromis", "value": "I"},
            {"id": "q14c", "text": "Vous prenez du recul et laissez passer le temps", "value": "S"},
            {"id": "q14d", "text": "Vous vous appuyez sur des faits pour argumenter", "value": "C"}
        ]
    },
    {
        "id": "q15",
        "text": "Dans un projet collectif (association, groupe d'amis, équipe...) :",
        "category": "disc",
        "options": [
            {"id": "q15a", "text": "Vous prenez les initiatives et fixez le cap", "value": "D"},
            {"id": "q15b", "text": "Vous motivez le groupe et créez une bonne ambiance", "value": "I"},
            {"id": "q15c", "text": "Vous soutenez les autres et assurez la cohésion", "value": "S"},
            {"id": "q15d", "text": "Vous organisez, planifiez et veillez à la qualité", "value": "C"}
        ]
    }
]


# ======================================================================
# VERTUS
# ======================================================================
VERTUS = {
    "sagesse": {
        "name": "Sagesse et connaissance",
        "sous_vertus": ["Sagesse", "Connaissance", "Tempérance", "Prudence"],
        "forces": ["Créativité", "Curiosité", "Jugement", "Amour de l'apprentissage", "Perspective"],
        "valeurs_schwartz": ["Autonomie", "Stimulation", "Réalisation de soi"],
        "valeurs_universelles": ["Patience", "Ouverture d'esprit", "Indulgence", "Pardon", "Adaptabilité", "Modestie", "Créativité", "Curiosité"],
        "qualites_humaines": ["Indépendance", "Créativité", "Curiosité", "Ouverture d'esprit", "Audace", "Liberté de pensée",
                              "Courtoisie", "Gentillesse", "Consultation", "Adaptabilité", "Sincérité", "Sobriété"],
        "competences_oms": ["Pensée critique", "Pensée créative", "Prise de décision"],
        "competences_sociales": ["Prudent", "Modéré", "Calme", "Docile", "Raisonnable", "Curieux", "Maîtrise de soi"],
        "competences_pro": ["Diplomate", "Stable", "Prévoyant", "Médiateur", "Gérer son stress"],
        "savoirs_etre": ["Faire preuve de curiosité", "Faire preuve de créativité, d'inventivité", "Prendre des initiatives et être force de proposition"],
        "cognition": ["Connaissance", "Ouverture d'esprit", "Curiosité", "Pensée critique", "Lucidité", "Perspicacité"],
        "conation": ["Soif d'apprendre", "Initiative intellectuelle", "Audace créative", "Détermination à comprendre"],
        "affection": ["Partage de connaissances", "Tolérance des idées", "Respect de la diversité", "Humilité intellectuelle"]
    },
    "courage": {
        "name": "Courage",
        "sous_vertus": ["Courage", "Droiture"],
        "forces": ["Bravoure", "Persévérance", "Honnêteté", "Enthousiasme"],
        "valeurs_schwartz": ["Hédonisme", "Réalisation de soi", "Stimulation"],
        "valeurs_universelles": ["Sécurité", "Bravoure", "Persévérance", "Authenticité", "Vitalité",
                                  "Loyauté", "Dignité", "Excellence", "Liberté", "Autonomie", "Discipline"],
        "qualites_humaines": ["Joie de vivre", "Optimisme", "Gratitude", "Ambition", "Détermination", "Passion",
                              "Dynamisme", "Fiabilité", "Confiance", "Vigilance", "Endurant", "Volonté"],
        "competences_oms": ["Gestion du stress", "Résilience", "Estime de soi"],
        "competences_sociales": ["Habileté", "Rigueur", "Persévérant", "Responsabilité", "Intègre"],
        "competences_pro": ["Consciencieux", "Minutieux", "Spontané", "Assidu", "Engagé", "Entrepreneur",
                            "Organisé", "Ponctuel", "Déterminé", "Passionné"],
        "savoirs_etre": ["Faire preuve de persévérance", "Gérer son stress", "Faire preuve de réactivité"],
        "cognition": ["Lucidité face aux risques", "Évaluation des obstacles", "Conscience de soi", "Discernement"],
        "conation": ["Détermination", "Persévérance", "Bravoure", "Ambition", "Volonté", "Dynamisme"],
        "affection": ["Optimisme", "Joie de vivre", "Enthousiasme communicatif", "Confiance", "Vitalité"]
    },
    "humanite": {
        "name": "Humanité",
        "sous_vertus": ["Servitude", "Unicité", "Noblesse", "Humanité"],
        "forces": ["Amour", "Gentillesse", "Intelligence sociale"],
        "valeurs_schwartz": ["Bienveillance", "Universalisme", "Affiliation"],
        "valeurs_universelles": ["Affection", "Gentillesse", "Assertivité", "Humilité",
                                  "Universalisme", "Unité", "Bonté", "Hospitalité", "Générosité", "Détachement", "Respect"],
        "qualites_humaines": ["Empathie", "Gentillesse", "Générosité", "Altruisme", "Compassion", "Écoute", "Solidarité",
                              "Modestie", "Partager", "Amabilité", "Transmettre le savoir", "Fidélité"],
        "competences_oms": ["Communication efficace", "Compétences relationnelles", "Empathie"],
        "competences_sociales": ["Réservé", "Assertif", "Serviable", "Audacieux", "Intuitif", "Protecteur", "Éloquent", "Patient"],
        "competences_pro": ["Flexibilité", "Chercheur", "Conseiller", "Concepteur", "Pédagogue", "Perspicace", "Animation"],
        "savoirs_etre": ["Être à l'écoute", "Avoir le sens du service", "Travailler en équipe"],
        "cognition": ["Intelligence sociale", "Compréhension d'autrui", "Lecture des émotions", "Psychologie intuitive"],
        "conation": ["Engagement relationnel", "Dévouement", "Volonté d'aider", "Serviabilité", "Hospitalité"],
        "affection": ["Empathie", "Compassion", "Gentillesse", "Bienveillance", "Amour", "Solidarité"]
    },
    "justice": {
        "name": "Justice",
        "sous_vertus": ["Justice"],
        "forces": ["Travail d'équipe", "Équité", "Leadership"],
        "valeurs_schwartz": ["Égalité", "Responsabilité sociale", "Pouvoir"],
        "valeurs_universelles": ["Honnêteté", "Obéissance", "Équité", "Fermeté", "Harmonie"],
        "qualites_humaines": ["Justice", "Impartialité", "Équité", "Respect des droits", "Intégrité", "Humilité", "Charisme",
                              "Coopération", "Logique", "Juste"],
        "competences_oms": ["Prise de décision", "Pensée critique", "Compétences relationnelles"],
        "competences_sociales": ["Lucidité", "Cohérent", "Esprit d'équipe", "Leadership"],
        "competences_pro": ["Pragmatique", "Méthodique", "Ordonné", "Conciliant", "Travail en équipe"],
        "savoirs_etre": ["Faire preuve de leadership", "Inspirer, donner du sens", "Respecter ses engagements, assumer ses responsabilités"],
        "cognition": ["Logique", "Cohérence", "Méthodique", "Pragmatisme", "Objectivité", "Lucidité"],
        "conation": ["Leadership", "Engagement collectif", "Responsabilité", "Fermeté", "Esprit d'équipe"],
        "affection": ["Respect", "Équité", "Harmonie", "Conciliation", "Loyauté", "Intégrité"]
    },
    "temperance": {
        "name": "Tempérance",
        "sous_vertus": ["Tempérance", "Prudence"],
        "forces": ["Pardon", "Humilité", "Prudence", "Maîtrise de soi"],
        "valeurs_schwartz": ["Conformité", "Sécurité", "Tradition"],
        "valeurs_universelles": ["Modestie", "Patience", "Adaptabilité", "Sobriété", "Créativité", "Curiosité"],
        "qualites_humaines": ["Respect des règles", "Prudence", "Stabilité", "Patience", "Humilité", "Modération", "Gratitude",
                              "Sincérité", "Sobriété", "Modeste"],
        "competences_oms": ["Gestion des émotions", "Estime de soi", "Résilience"],
        "competences_sociales": ["Modéré", "Raisonnable", "Curieux", "Maîtrise de soi"],
        "competences_pro": ["Gérer son stress", "Prévoyant", "Stable"],
        "savoirs_etre": ["Faire preuve de rigueur et de précision", "Organiser son travail selon les priorités et les objectifs"],
        "cognition": ["Prévoyance", "Prudence", "Raisonnement", "Calme réflexif", "Sobriété de jugement"],
        "conation": ["Discipline", "Constance", "Patience", "Maîtrise de soi", "Rigueur", "Organisation"],
        "affection": ["Modération", "Pardon", "Gratitude", "Sérénité", "Indulgence", "Stabilité émotionnelle"]
    },
    "transcendance": {
        "name": "Transcendance",
        "sous_vertus": ["Pureté", "Spiritualité", "Transcendance"],
        "forces": ["Appréciation de la beauté", "Gratitude", "Espoir", "Humour", "Spiritualité"],
        "valeurs_schwartz": ["Universalisme", "Spiritualité", "Bienveillance"],
        "valeurs_universelles": ["Fidélité", "Gratitude", "Excellence", "Dévotion", "Bienveillance", "Respect", "Foi", "Beauté"],
        "qualites_humaines": ["Tolérance", "Ouverture d'esprit", "Sagesse", "Gratitude", "Recherche de sens", "Sérénité", "Harmonie",
                              "Joyeux", "Hédoniste", "Écouter", "Altruisme", "Compassion", "Politesse"],
        "competences_oms": ["Pensée créative", "Gestion du stress", "Résilience"],
        "competences_sociales": ["Propreté", "Souriant", "Optimisme", "Sensibilité", "Solidarité", "Force", "Doux", "Humour"],
        "competences_pro": ["Dévoué", "Sociable", "Souple", "Solidaire", "Délicat", "Bénévole"],
        "savoirs_etre": ["S'adapter aux changements", "Faire preuve d'autonomie"],
        "cognition": ["Perspective globale", "Vision holistique", "Contemplation", "Sagesse", "Intuition"],
        "conation": ["Quête de sens", "Espérance", "Dévotion", "Excellence", "Engagement spirituel"],
        "affection": ["Harmonie", "Sérénité", "Gratitude", "Compassion universelle", "Beauté", "Joie profonde"]
    }
}


# ======================================================================
# ARCHEOLOGIE_COMPETENCES
# ======================================================================
ARCHEOLOGIE_COMPETENCES = {
    "sagesse": {
        "forces": ["Créativité", "Curiosité", "Jugement", "Amour de l'apprentissage", "Perspective"],
        "valeurs_schwartz": ["Autonomie", "Stimulation", "Réalisation de soi",
                             "Patience", "Ouverture d'esprit", "Indulgence", "Pardon", "Adaptabilité"],
        "qualites": ["Indépendance", "Créativité", "Curiosité", "Ouverture d'esprit", "Audace", "Liberté de pensée",
                     "Courtoisie", "Gentillesse", "Consultation", "Adaptabilité", "Sincérité", "Sobriété"],
        "competences_oms": ["Pensée critique", "Pensée créative", "Prise de décision"],
        "savoirs_etre_pro": ["Curiosité", "Créativité", "Prise d'initiatives", "Esprit d'analyse",
                             "Diplomate", "Stable", "Prévoyant", "Médiateur", "Gérer son stress"],
        "competences_sociales": ["Prudent", "Modéré", "Calme", "Docile", "Raisonnable", "Curieux", "Maîtrise de soi"],
        "filieres_naturelles": ["SIN", "SI"],
        "mbti_coherents": ["INTJ", "INTP", "ENTJ", "ENTP", "ISTP"],
        "disc_coherents": ["C", "D"],
        "ennea_coherents": [5, 1, 7],
    },
    "courage": {
        "forces": ["Bravoure", "Persévérance", "Honnêteté", "Enthousiasme"],
        "valeurs_schwartz": ["Hédonisme", "Réalisation de soi", "Stimulation",
                             "Sécurité", "Loyauté", "Dignité", "Excellence", "Liberté", "Autonomie", "Discipline"],
        "qualites": ["Joie de vivre", "Optimisme", "Gratitude", "Ambition", "Détermination", "Passion",
                     "Dynamisme", "Fiabilité", "Confiance", "Vigilance", "Endurant", "Volonté", "Créatif"],
        "competences_oms": ["Gestion du stress", "Résilience", "Estime de soi"],
        "savoirs_etre_pro": ["Persévérance", "Gestion du stress", "Réactivité", "Prise de risque",
                             "Consciencieux", "Minutieux", "Spontané", "Assidu", "Engagé", "Entrepreneur",
                             "Organisé", "Ponctuel", "Déterminé", "Passionné"],
        "competences_sociales": ["Habileté", "Rigueur", "Persévérant", "Responsabilité", "Intègre"],
        "filieres_naturelles": ["SBTP", "SCV", "SI"],
        "mbti_coherents": ["ESTP", "ISTP", "ESTJ", "ENTJ"],
        "disc_coherents": ["D", "I"],
        "ennea_coherents": [8, 3, 7],
    },
    "humanite": {
        "forces": ["Amour", "Gentillesse", "Intelligence sociale"],
        "valeurs_schwartz": ["Bienveillance", "Universalisme", "Affiliation",
                             "Affection", "Gentillesse", "Assertivité", "Humilité",
                             "Bonté", "Hospitalité", "Générosité", "Détachement", "Respect"],
        "qualites": ["Empathie", "Gentillesse", "Générosité", "Altruisme", "Compassion", "Écoute", "Solidarité",
                     "Modestie", "Partager", "Amabilité", "Transmettre le savoir", "Fidélité"],
        "competences_oms": ["Communication efficace", "Compétences relationnelles", "Empathie"],
        "savoirs_etre_pro": ["Écoute", "Sens du service", "Travail en équipe", "Bienveillance",
                             "Flexibilité", "Chercheur", "Conseiller", "Concepteur", "Pédagogue",
                             "Perspicace", "Animation", "Persévérant"],
        "competences_sociales": ["Réservé", "Assertif", "Serviable", "Audacieux", "Intuitif",
                                  "Protecteur", "Éloquent", "Patient"],
        "filieres_naturelles": ["SSS", "SC"],
        "mbti_coherents": ["INFJ", "ENFJ", "ISFJ", "ESFJ", "INFP", "ENFP", "ESFP"],
        "disc_coherents": ["S", "I"],
        "ennea_coherents": [2, 9, 6],
    },
    "justice": {
        "forces": ["Travail d'équipe", "Équité", "Leadership"],
        "valeurs_schwartz": ["Égalité", "Responsabilité sociale", "Pouvoir",
                             "Honnêteté", "Obéissance", "Équité", "Fermeté", "Harmonie"],
        "qualites": ["Justice", "Impartialité", "Équité", "Intégrité", "Humilité", "Charisme", "Influence",
                     "Coopération", "Logique", "Juste"],
        "competences_oms": ["Prise de décision", "Pensée critique", "Compétences relationnelles"],
        "savoirs_etre_pro": ["Leadership", "Donner du sens", "Respect des engagements", "Responsabilité",
                             "Pragmatique", "Méthodique", "Ordonné", "Conciliant", "Travail en équipe"],
        "competences_sociales": ["Lucidité", "Cohérent", "Esprit d'équipe", "Leadership"],
        "filieres_naturelles": ["SGAE", "SC"],
        "mbti_coherents": ["ENTJ", "ESTJ", "ENFJ", "INTJ"],
        "disc_coherents": ["D", "C"],
        "ennea_coherents": [1, 8, 3],
    },
    "temperance": {
        "forces": ["Pardon", "Humilité", "Prudence", "Maîtrise de soi"],
        "valeurs_schwartz": ["Conformité", "Sécurité", "Tradition",
                             "Modestie", "Patience", "Adaptabilité", "Sobriété"],
        "qualites": ["Respect des règles", "Prudence", "Stabilité", "Patience", "Modération", "Gratitude",
                     "Sincérité", "Sobriété", "Modeste"],
        "competences_oms": ["Gestion des émotions", "Estime de soi", "Résilience"],
        "savoirs_etre_pro": ["Rigueur", "Précision", "Organisation", "Respect des priorités",
                             "Gérer son stress", "Prévoyant", "Stable"],
        "competences_sociales": ["Modéré", "Raisonnable", "Curieux", "Maîtrise de soi"],
        "filieres_naturelles": ["SGAE", "SI"],
        "mbti_coherents": ["ISTJ", "ISFJ", "ESTJ", "ESFJ", "INTP"],
        "disc_coherents": ["S", "C"],
        "ennea_coherents": [6, 1, 9],
    },
    "transcendance": {
        "forces": ["Appréciation de la beauté", "Gratitude", "Espoir", "Humour", "Spiritualité"],
        "valeurs_schwartz": ["Universalisme", "Spiritualité", "Bienveillance",
                             "Fidélité", "Gratitude", "Excellence", "Dévotion", "Respect", "Foi", "Beauté"],
        "qualites": ["Tolérance", "Ouverture d'esprit", "Sagesse", "Recherche de sens", "Sérénité", "Harmonie",
                     "Joyeux", "Hédoniste", "Écouter", "Altruisme", "Compassion", "Politesse"],
        "competences_oms": ["Pensée créative", "Gestion du stress", "Résilience"],
        "savoirs_etre_pro": ["Adaptation aux changements", "Autonomie", "Créativité", "Vision globale",
                             "Dévoué", "Sociable", "Souple", "Solidaire", "Délicat", "Bénévole"],
        "competences_sociales": ["Propreté", "Souriant", "Optimisme", "Sensibilité",
                                  "Solidarité", "Force", "Doux", "Humour"],
        "filieres_naturelles": ["SC", "SSS", "SIN"],
        "mbti_coherents": ["INFP", "ENFP", "ISFP", "INFJ"],
        "disc_coherents": ["I", "S"],
        "ennea_coherents": [4, 9, 7],
    },
}


# ======================================================================
# TABLEAU_CK
# ======================================================================
TABLEAU_CK = {
    "sagesse": {
        "sous_vertus": ["Sagesse", "Connaissance", "Tempérance", "Prudence"],
        "valeurs_universelles": [
            "Patience", "Ouverture d'esprit", "Indulgence", "Pardon", "Adaptabilité",
            "Modestie", "Créativité", "Curiosité", "Aimer apprendre"
        ],
        "qualites_humaines": [
            "Courtoisie", "Gentillesse", "Consultation", "Adaptabilité",
            "Sincérité", "Sobriété", "Modeste", "Pardonner"
        ],
        "competences_sociales": [
            "Prudent", "Modéré", "Calme", "Docile", "Raisonnable", "Curieux", "Maîtrise de soi"
        ],
        "competences_pro_transferables": [
            "Diplomate", "Stable", "Prévoyant", "Médiateur", "Gérer son stress"
        ],
        "metiers_associes": ["Psychologue"],
    },
    "justice": {
        "sous_vertus": ["Justice"],
        "valeurs_universelles": [
            "Honnêteté", "Obéissance", "Équité", "Fermeté", "Harmonie"
        ],
        "qualites_humaines": [
            "Coopération", "Logique", "Juste", "Pouvoir"
        ],
        "competences_sociales": [
            "Lucidité", "Cohérent", "Esprit d'équipe", "Leadership"
        ],
        "competences_pro_transferables": [
            "Pragmatique", "Méthodique", "Ordonné", "Conciliant", "Travail en équipe"
        ],
        "metiers_associes": ["Juriste"],
    },
    "courage": {
        "sous_vertus": ["Courage", "Droiture"],
        "valeurs_universelles": [
            "Sécurité", "Bravoure", "Persévérance", "Authenticité", "Vitalité",
            "Loyauté", "Dignité", "Excellence", "Liberté", "Autonomie", "Discipline"
        ],
        "qualites_humaines": [
            "Dynamisme", "Fiabilité", "Confiance",
            "Vigilance", "Endurant", "Volonté", "Créatif", "Dextérité"
        ],
        "competences_sociales": [
            "Habileté", "Rigueur", "Persévérant", "Responsabilité", "Intègre"
        ],
        "competences_pro_transferables": [
            "Consciencieux", "Minutieux", "Spontané",
            "Assidu", "Engagé", "Entrepreneur", "Organisé", "Ponctuel", "Déterminé", "Passionné"
        ],
        "metiers_associes": ["Comptable", "Assureur", "Banquier", "Artisan", "Agent immobilier"],
    },
    "transcendance": {
        "sous_vertus": ["Pureté", "Spiritualité", "Transcendance"],
        "valeurs_universelles": [
            "Fidélité", "Gratitude", "Excellence", "Dévotion",
            "Bienveillance", "Respect", "Foi", "Beauté"
        ],
        "qualites_humaines": [
            "Joyeux", "Hédoniste", "Écouter",
            "Altruisme", "Compassion", "Politesse", "Tolérance", "Amitié", "Rigueur"
        ],
        "competences_sociales": [
            "Propreté", "Souriant", "Optimisme", "Sensibilité",
            "Solidarité", "Force", "Doux", "Humour"
        ],
        "competences_pro_transferables": [
            "Dévoué", "Sociable", "Souple", "Solidaire", "Délicat", "Bénévole"
        ],
        "metiers_associes": [],
    },
    "humanite": {
        "sous_vertus": ["Servitude", "Unicité", "Noblesse", "Humanité"],
        "valeurs_universelles": [
            "Affection", "Gentillesse", "Assertivité", "Humilité",
            "Universalisme", "Unité",
            "Bonté", "Hospitalité", "Magnanimité", "Générosité", "Détachement", "Respect"
        ],
        "qualites_humaines": [
            "Modestie", "Partager", "Amabilité",
            "Générosité", "Transmettre le savoir", "Accomplissement", "Enseigner",
            "Empathie", "Fidélité"
        ],
        "competences_sociales": [
            "Réservé", "Assertif", "Serviable",
            "Audacieux", "Intuitif",
            "Protecteur", "Éloquent", "Patient"
        ],
        "competences_pro_transferables": [
            "Flexibilité",
            "Chercheur", "Conseiller", "Concepteur", "Pédagogue", "Perspicace", "Animation",
            "Objectivité", "Persévérant"
        ],
        "metiers_associes": [],
    },
    "temperance": {
        "sous_vertus": ["Tempérance", "Prudence"],
        "valeurs_universelles": [
            "Modestie", "Créativité", "Curiosité", "Patience",
            "Adaptabilité", "Sobriété"
        ],
        "qualites_humaines": [
            "Sincérité", "Sobriété", "Modeste", "Pardonner"
        ],
        "competences_sociales": [
            "Modéré", "Raisonnable", "Curieux", "Maîtrise de soi"
        ],
        "competences_pro_transferables": [
            "Gérer son stress", "Prévoyant", "Stable"
        ],
        "metiers_associes": [],
    },
}


# ======================================================================
# ENNEA_TO_PROFILE
# ======================================================================
ENNEA_TO_PROFILE = {
    1: {"name": "Perfectionniste", "moteur": "Faire correctement", "vertu": "temperance"},
    2: {"name": "Altruiste", "moteur": "Être utile", "vertu": "humanite"},
    3: {"name": "Performeur", "moteur": "Réussir", "vertu": "courage"},
    4: {"name": "Créatif", "moteur": "Être authentique", "vertu": "transcendance"},
    5: {"name": "Analyste", "moteur": "Comprendre", "vertu": "sagesse"},
    6: {"name": "Loyal", "moteur": "Sécurité", "vertu": "temperance"},
    7: {"name": "Enthousiaste", "moteur": "Variété", "vertu": "transcendance"},
    8: {"name": "Leader", "moteur": "Impact", "vertu": "justice"},
    9: {"name": "Médiateur", "moteur": "Harmonie", "vertu": "humanite"},
}


# ======================================================================
# RIASEC_DESCRIPTIONS
# ======================================================================
RIASEC_DESCRIPTIONS = {
    "R": {
        "name": "Réaliste",
        "description": "Préfère les activités pratiques et manuelles, le travail avec des outils, machines ou animaux",
        "traits": ["Pratique", "Concret", "Manuel", "Technique", "Physique"],
        "environnements": ["Atelier", "Chantier", "Extérieur", "Laboratoire technique"],
        "mbti_affinite": ["ISTP", "ESTP", "ISTJ", "ISFP"],
        "disc_affinite": ["C", "S"],
        "ennea_affinite": [6, 9, 8]
    },
    "I": {
        "name": "Investigateur", 
        "description": "Aime observer, analyser, résoudre des problèmes complexes et chercher à comprendre",
        "traits": ["Analytique", "Curieux", "Méthodique", "Intellectuel", "Indépendant"],
        "environnements": ["Laboratoire", "Bureau", "Centre de recherche"],
        "mbti_affinite": ["INTP", "INTJ", "INFJ", "ENTP"],
        "disc_affinite": ["C", "D"],
        "ennea_affinite": [5, 1, 4]
    },
    "A": {
        "name": "Artistique",
        "description": "Valorise la créativité, l'expression personnelle et les activités non structurées",
        "traits": ["Créatif", "Original", "Expressif", "Imaginatif", "Intuitif"],
        "environnements": ["Studio", "Scène", "Atelier d'art", "Agence créative"],
        "mbti_affinite": ["INFP", "ENFP", "ISFP", "INFJ"],
        "disc_affinite": ["I", "S"],
        "ennea_affinite": [4, 7, 9]
    },
    "S": {
        "name": "Social",
        "description": "Aime aider, enseigner, conseiller et interagir avec les autres",
        "traits": ["Empathique", "Coopératif", "Serviable", "Patient", "Bienveillant"],
        "environnements": ["École", "Hôpital", "Centre social", "Cabinet"],
        "mbti_affinite": ["ENFJ", "ESFJ", "INFJ", "ISFJ"],
        "disc_affinite": ["S", "I"],
        "ennea_affinite": [2, 9, 6]
    },
    "E": {
        "name": "Entreprenant",
        "description": "Aime diriger, persuader, vendre et prendre des initiatives",
        "traits": ["Leader", "Ambitieux", "Persuasif", "Énergique", "Compétitif"],
        "environnements": ["Bureau direction", "Terrain commercial", "Politique"],
        "mbti_affinite": ["ENTJ", "ESTJ", "ENTP", "ENFJ"],
        "disc_affinite": ["D", "I"],
        "ennea_affinite": [3, 8, 7]
    },
    "C": {
        "name": "Conventionnel",
        "description": "Préfère les activités structurées, l'organisation des données et le respect des procédures",
        "traits": ["Organisé", "Méthodique", "Précis", "Fiable", "Consciencieux"],
        "environnements": ["Bureau", "Administration", "Banque", "Comptabilité"],
        "mbti_affinite": ["ISTJ", "ESTJ", "ISFJ", "INTJ"],
        "disc_affinite": ["C", "S"],
        "ennea_affinite": [1, 6, 5]
    }
}


# ======================================================================
# RIASEC_ADJACENT
# ======================================================================
RIASEC_ADJACENT = {
    "R": ["I", "C"],  # Adjacent: Investigateur, Conventionnel
    "I": ["R", "A"],  # Adjacent: Réaliste, Artistique  
    "A": ["I", "S"],  # Adjacent: Investigateur, Social
    "S": ["A", "E"],  # Adjacent: Artistique, Entreprenant
    "E": ["S", "C"],  # Adjacent: Social, Conventionnel
    "C": ["E", "R"],  # Adjacent: Entreprenant, Réaliste
}


# ======================================================================
# RIASEC_OPPOSITE
# ======================================================================
RIASEC_OPPOSITE = {
    "R": "S",  # Réaliste ↔ Social
    "I": "E",  # Investigateur ↔ Entreprenant
    "A": "C",  # Artistique ↔ Conventionnel
    "S": "R",
    "E": "I",
    "C": "A"
}


# ======================================================================
# MBTI_TO_VERTU_FALLBACK
# ======================================================================
MBTI_TO_VERTU_FALLBACK = {
    # NT - Analystes/Rationnels → Sagesse (connaissance, analyse, stratégie)
    "INTJ": ("sagesse", "justice"),
    "INTP": ("sagesse", "temperance"),
    "ENTJ": ("justice", "sagesse"),
    "ENTP": ("sagesse", "courage"),
    
    # NF - Diplomates/Idéalistes → Humanité ou Transcendance
    "INFJ": ("humanite", "transcendance"),
    "INFP": ("transcendance", "humanite"),
    "ENFJ": ("humanite", "justice"),
    "ENFP": ("transcendance", "humanite"),
    
    # SJ - Sentinelles/Gardiens → Justice ou Tempérance (ordre, devoir, stabilité)
    "ISTJ": ("justice", "temperance"),
    "ISFJ": ("humanite", "temperance"),
    "ESTJ": ("justice", "courage"),
    "ESFJ": ("humanite", "justice"),
    
    # SP - Explorateurs/Artisans → Courage (action, audace, pragmatisme)
    "ISTP": ("courage", "sagesse"),
    "ISFP": ("transcendance", "humanite"),
    "ESTP": ("courage", "temperance"),  # ESTP = action, prise de risque, pragmatisme
    "ESFP": ("humanite", "transcendance"),
}


# ======================================================================
# ZONES_VIGILANCE
# ======================================================================
ZONES_VIGILANCE = {
    # Qualités liées à l'Humanité
    "Empathie": {
        "qualite": "Empathie",
        "piege": "Sacrifice de soi, fusion émotionnelle",
        "defi": "Affirmation de soi, poser des limites",
        "allergie": "Indifférence, froideur",
        "recommandation": "Prenez conscience de vos besoins. Apprenez à dire non avec bienveillance et cultivez l'écoute de vous-même."
    },
    "Gentillesse": {
        "qualite": "Gentillesse",
        "piege": "Naïveté, se faire exploiter",
        "defi": "Assertivité, discernement",
        "allergie": "Dureté, méchanceté",
        "recommandation": "Cultivez votre bienveillance tout en développant votre capacité à poser des limites saines."
    },
    "Écoute": {
        "qualite": "Écoute active",
        "piege": "Effacement, oubli de soi",
        "defi": "Expression de soi, prise de parole",
        "allergie": "Monopolisation de la parole",
        "recommandation": "Votre écoute est précieuse. N'oubliez pas de partager aussi vos propres idées et besoins."
    },
    # Qualités liées à la Tempérance
    "Rigueur": {
        "qualite": "Rigueur",
        "piege": "Rigidité, perfectionnisme bloquant",
        "defi": "Souplesse, flexibilité",
        "allergie": "Laxisme, flou",
        "recommandation": "Tolérez l'imprévu. Pratiquez la flexibilité dans votre gestion du temps et des projets."
    },
    "Prudence": {
        "qualite": "Prudence",
        "piege": "Immobilisme, peur du risque",
        "defi": "Audace, prise d'initiative",
        "allergie": "Imprudence, témérité",
        "recommandation": "Votre prudence vous protège, mais osez parfois sortir de votre zone de confort pour saisir de nouvelles opportunités."
    },
    "Organisation": {
        "qualite": "Organisation",
        "piege": "Contrôle excessif, inflexibilité",
        "defi": "Lâcher-prise, spontanéité",
        "allergie": "Désordre, chaos",
        "recommandation": "Gardez votre structure tout en laissant de la place à l'imprévu et à la créativité."
    },
    # Qualités liées à la Sagesse
    "Créativité": {
        "qualite": "Créativité",
        "piege": "Dispersion, difficulté à concrétiser",
        "defi": "Ancrage, structure",
        "allergie": "Routine, conformisme",
        "recommandation": "Structurez vos idées avec des objectifs concrets. Utilisez des cartes mentales ou des journaux de bord."
    },
    "Curiosité": {
        "qualite": "Curiosité",
        "piege": "Éparpillement, superficialité",
        "defi": "Approfondissement, focus",
        "allergie": "Fermeture d'esprit",
        "recommandation": "Canalisez votre curiosité vers des sujets prioritaires pour approfondir réellement vos connaissances."
    },
    "Analyse": {
        "qualite": "Pensée analytique",
        "piege": "Paralysie par l'analyse, sur-réflexion",
        "defi": "Action, décision rapide",
        "allergie": "Impulsivité, superficialité",
        "recommandation": "Fixez-vous des délais de réflexion pour éviter de trop analyser avant d'agir."
    },
    # Qualités liées au Courage
    "Persévérance": {
        "qualite": "Persévérance",
        "piege": "Obstination, refus d'abandonner l'inadapté",
        "defi": "Flexibilité, savoir pivoter",
        "allergie": "Abandon facile, inconstance",
        "recommandation": "Distinguez persévérance utile et acharnement. Sachez reconnaître quand changer de direction."
    },
    "Ambition": {
        "qualite": "Ambition",
        "piege": "Arrivisme, négligence des autres",
        "defi": "Humilité, collaboration",
        "allergie": "Médiocrité, manque d'ambition",
        "recommandation": "Gardez vos objectifs élevés tout en restant attentif aux besoins de votre entourage professionnel."
    },
    "Dynamisme": {
        "qualite": "Dynamisme",
        "piege": "Agitation, burn-out",
        "defi": "Calme, récupération",
        "allergie": "Mollesse, passivité",
        "recommandation": "Votre énergie est un atout. Apprenez à la canaliser et à vous accorder des temps de pause."
    },
    # Qualités liées à la Justice
    "Leadership": {
        "qualite": "Leadership",
        "piege": "Autoritarisme, contrôle excessif",
        "defi": "Délégation, écoute",
        "allergie": "Suivisme, passivité",
        "recommandation": "Votre capacité à guider est précieuse. Cultivez l'écoute et la délégation pour un leadership inclusif."
    },
    "Sens de l'équité": {
        "qualite": "Sens de l'équité",
        "piege": "Rigidité dans l'application des règles",
        "defi": "Nuance, contextualisation",
        "allergie": "Injustice, favoritisme",
        "recommandation": "L'équité parfaite n'existe pas toujours. Apprenez à contextualiser vos jugements."
    },
    # Qualités liées à la Transcendance
    "Optimisme": {
        "qualite": "Optimisme",
        "piege": "Déni des problèmes, naïveté",
        "defi": "Réalisme, anticipation des risques",
        "allergie": "Pessimisme, négativité",
        "recommandation": "Gardez votre vision positive tout en restant lucide sur les obstacles à anticiper."
    },
    "Adaptabilité": {
        "qualite": "Adaptabilité",
        "piege": "Perte d'identité, suivisme",
        "defi": "Affirmation de ses valeurs",
        "allergie": "Rigidité, résistance au changement",
        "recommandation": "Votre flexibilité est un atout. Veillez à ne pas perdre vos valeurs fondamentales en vous adaptant."
    },
    # Soft skills professionnels
    "Communication": {
        "qualite": "Communication",
        "piege": "Bavardage, superficialité",
        "defi": "Écoute profonde, concision",
        "allergie": "Mutisme, repli sur soi",
        "recommandation": "Équilibrez expression et écoute. La qualité de vos échanges compte plus que leur quantité."
    },
    "Autonomie": {
        "qualite": "Autonomie",
        "piege": "Isolement, refus de l'aide",
        "defi": "Collaboration, demande de soutien",
        "allergie": "Dépendance, assistanat",
        "recommandation": "Votre indépendance est précieuse. N'hésitez pas à solliciter de l'aide quand c'est pertinent."
    },
    "Sens du service": {
        "qualite": "Sens du service",
        "piege": "Servilité, oubli de ses intérêts",
        "defi": "Équilibre donner/recevoir",
        "allergie": "Égoïsme, indifférence aux autres",
        "recommandation": "Votre générosité est admirable. Veillez à préserver aussi vos propres besoins et limites."
    },
    "Réactivité": {
        "qualite": "Réactivité",
        "piege": "Précipitation, manque de recul",
        "defi": "Réflexion, prise de recul",
        "allergie": "Lenteur, procrastination",
        "recommandation": "Votre rapidité d'action est un atout. Accordez-vous parfois un temps de réflexion avant d'agir."
    }
}


# ======================================================================
# DISC_OFMAN
# ======================================================================
DISC_OFMAN = {
    "D": {
        "qualite": "Détermination",
        "piege": "Autoritarisme, impatience",
        "defi": "Écoute, patience, diplomatie",
        "allergie": "Passivité, lenteur, indécision",
        "recommandation": "Votre capacité à décider et agir est précieuse. Développez l'écoute active pour embarquer les autres dans vos projets."
    },
    "I": {
        "qualite": "Enthousiasme",
        "piege": "Superficialité, dispersion",
        "defi": "Profondeur, concentration, suivi",
        "allergie": "Pessimisme, rigidité, froideur",
        "recommandation": "Votre énergie positive est contagieuse. Cultivez la constance pour transformer vos idées en réalisations concrètes."
    },
    "S": {
        "qualite": "Stabilité",
        "piege": "Résistance au changement, passivité",
        "defi": "Adaptabilité, initiative, affirmation",
        "allergie": "Chaos, changement brutal, instabilité",
        "recommandation": "Votre fiabilité est un atout majeur. Osez sortir de votre zone de confort pour saisir de nouvelles opportunités."
    },
    "C": {
        "qualite": "Précision",
        "piege": "Perfectionnisme paralysant, critique excessive",
        "defi": "Tolérance à l'imperfection, action rapide",
        "allergie": "Approximation, négligence, erreurs",
        "recommandation": "Votre rigueur garantit la qualité. Acceptez que 'assez bien' peut parfois suffire pour avancer."
    }
}


# ======================================================================
# MBTI_ENERGIE_OFMAN
# ======================================================================
MBTI_ENERGIE_OFMAN = {
    "E": {
        "qualite": "Sociabilité",
        "piege": "Dépendance aux autres, superficialité relationnelle",
        "defi": "Introspection, autonomie émotionnelle",
        "allergie": "Isolement, repli sur soi",
        "recommandation": "Votre aisance sociale est un atout. Cultivez aussi des moments de solitude pour mieux vous connaître."
    },
    "I": {
        "qualite": "Réflexion profonde",
        "piege": "Isolement, difficulté à s'exprimer",
        "defi": "Expression, partage, connexion aux autres",
        "allergie": "Agitation, bavardage, superficialité",
        "recommandation": "Votre capacité d'analyse est précieuse. Osez partager vos idées plus souvent avec les autres."
    }
}


# ======================================================================
# ENNEA_OFMAN
# ======================================================================
ENNEA_OFMAN = {
    1: {
        "qualite": "Intégrité",
        "piege": "Perfectionnisme rigide, critique excessive",
        "defi": "Acceptation, tolérance, sérénité",
        "allergie": "Négligence, laxisme, médiocrité",
        "recommandation": "Votre sens de l'éthique est admirable. Apprenez à accepter l'imperfection chez vous et chez les autres."
    },
    2: {
        "qualite": "Générosité",
        "piege": "Sacrifice de soi, manipulation affective",
        "defi": "Recevoir, s'occuper de soi, autonomie",
        "allergie": "Égoïsme, indifférence aux besoins des autres",
        "recommandation": "Votre dévouement est précieux. N'oubliez pas de prendre soin de vous et d'accepter l'aide des autres."
    },
    3: {
        "qualite": "Efficacité",
        "piege": "Obsession de l'image, workaholic",
        "defi": "Authenticité, être vs paraître",
        "allergie": "Échec, improductivité, médiocrité",
        "recommandation": "Votre drive est impressionnant. Connectez-vous à vos vraies valeurs plutôt qu'aux attentes des autres."
    },
    4: {
        "qualite": "Authenticité",
        "piege": "Mélancolie, sentiment d'être incompris",
        "defi": "Équilibre émotionnel, apprécier l'ordinaire",
        "allergie": "Banalité, superficialité, conformisme",
        "recommandation": "Votre sensibilité est une force créative. Cultivez la gratitude pour ce que vous avez déjà."
    },
    5: {
        "qualite": "Expertise",
        "piege": "Retrait, accumulation de connaissances sans action",
        "defi": "Engagement, partage, présence physique",
        "allergie": "Intrusion, demandes émotionnelles excessives",
        "recommandation": "Votre profondeur intellectuelle est rare. Osez vous impliquer davantage dans le monde concret."
    },
    6: {
        "qualite": "Loyauté",
        "piege": "Doute excessif, anxiété, méfiance",
        "defi": "Confiance en soi, prise de risque mesurée",
        "allergie": "Trahison, imprévisibilité, déloyauté",
        "recommandation": "Votre vigilance protège les autres. Développez votre confiance intérieure pour oser davantage."
    },
    7: {
        "qualite": "Optimisme",
        "piege": "Fuite de la douleur, dispersion",
        "defi": "Profondeur, engagement, accepter les difficultés",
        "allergie": "Négativité, limitation, routine ennuyeuse",
        "recommandation": "Votre joie de vivre est contagieuse. Apprenez à rester présent même dans les moments difficiles."
    },
    8: {
        "qualite": "Force",
        "piege": "Intimidation, contrôle excessif",
        "defi": "Vulnérabilité, douceur, délégation",
        "allergie": "Faiblesse, soumission, manipulation",
        "recommandation": "Votre puissance inspire le respect. Montrez aussi votre côté protecteur et bienveillant."
    },
    9: {
        "qualite": "Harmonie",
        "piege": "Évitement des conflits, oubli de soi",
        "defi": "Affirmation de soi, prise de position",
        "allergie": "Conflit, agressivité, discorde",
        "recommandation": "Votre capacité à créer la paix est précieuse. Osez exprimer vos propres besoins et opinions."
    }
}


# ======================================================================
# LIFE_PATHS
# ======================================================================
LIFE_PATHS = {
    "1": {
        "label": "Autonomie & Initiative",
        "themes": ["autonomie", "initiative", "affirmation", "leadership", "démarrage"],
        "strengths": ["capacité à lancer", "décision", "indépendance", "sens de l'action"],
        "watchouts": ["isolement", "rigidité", "impatience", "difficulté à déléguer"],
        "work_preferences": ["objectifs clairs", "autonomie", "responsabilités", "défis concrets"],
        "micro_actions": [
            {"action": "Pratiquez l'écoute active : lors d'une réunion, reformulez ce que dit votre interlocuteur avant de répondre.", "focus": "Écoute Active"},
            {"action": "Développez votre capacité à déléguer : identifiez une tâche que vous pouvez confier à un collègue cette semaine.", "focus": "Délégation"},
            {"action": "Travaillez votre patience : avant de prendre une décision rapide, accordez-vous 24h de réflexion.", "focus": "Prise de Recul"}
        ]
    },
    "2": {
        "label": "Coopération & Relation",
        "themes": ["coopération", "écoute", "diplomatie", "sens du lien", "harmonie"],
        "strengths": ["capacité à soutenir", "médiation", "écoute", "cohésion"],
        "watchouts": ["suradaptation", "peur du conflit", "difficulté à dire non", "dépendance à la validation"],
        "work_preferences": ["travail d'équipe", "climat serein", "rôle de support", "relations de qualité"],
        "micro_actions": [
            {"action": "Renforcez votre assertivité : exprimez clairement votre opinion lors de la prochaine décision d'équipe.", "focus": "Assertivité"},
            {"action": "Apprenez à dire non : refusez poliment une demande non prioritaire en proposant une alternative.", "focus": "Affirmation de Soi"},
            {"action": "Développez votre autonomie décisionnelle : prenez une décision sans demander validation extérieure.", "focus": "Confiance en Soi"}
        ]
    },
    "3": {
        "label": "Expression & Créativité",
        "themes": ["expression", "créativité", "communication", "visibilité", "enthousiasme"],
        "strengths": ["capacité à transmettre", "dynamisme", "créativité", "mise en valeur"],
        "watchouts": ["dispersion", "procrastination sur la finition", "sensibilité au regard des autres", "sur-engagement social"],
        "work_preferences": ["variété", "projets visibles", "communication", "environnements stimulants"],
        "micro_actions": [
            {"action": "Améliorez votre capacité à conclure : terminez un projet en cours avant d'en démarrer un nouveau.", "focus": "Persévérance"},
            {"action": "Développez votre rigueur : créez une liste de tâches quotidienne et respectez les priorités définies.", "focus": "Organisation"},
            {"action": "Renforcez votre résistance au feedback : demandez un retour critique sur votre travail et accueillez-le sereinement.", "focus": "Ouverture au Feedback"}
        ]
    },
    "4": {
        "label": "Structure & Méthode",
        "themes": ["organisation", "méthode", "rigueur", "stabilité", "construction"],
        "strengths": ["fiabilité", "sens du détail", "discipline", "capacité à bâtir"],
        "watchouts": ["perfectionnisme", "rigidité", "difficulté avec l'imprévu", "auto-critique"],
        "work_preferences": ["cadre clair", "processus", "qualité", "missions durables"],
        "micro_actions": [
            {"action": "Développez votre flexibilité : acceptez qu'un livrable soit 'suffisamment bon' plutôt que parfait.", "focus": "Adaptabilité"},
            {"action": "Renforcez votre gestion du changement : proposez une amélioration à un processus existant.", "focus": "Innovation"},
            {"action": "Travaillez votre bienveillance envers vous-même : célébrez une réussite récente, même mineure.", "focus": "Estime de Soi"}
        ]
    },
    "5": {
        "label": "Liberté & Adaptation",
        "themes": ["liberté", "mouvement", "adaptation", "expérimentation", "changement"],
        "strengths": ["agilité", "curiosité terrain", "capacité à gérer l'imprévu", "apprentissage rapide"],
        "watchouts": ["instabilité", "ennui rapide", "dispersion", "difficulté à maintenir une routine"],
        "work_preferences": ["autonomie", "variété", "missions courtes", "environnements évolutifs"],
        "micro_actions": [
            {"action": "Développez votre constance : engagez-vous sur un objectif à 30 jours et tenez-le jusqu'au bout.", "focus": "Persévérance"},
            {"action": "Renforcez votre sens de l'engagement : respectez scrupuleusement vos délais cette semaine.", "focus": "Fiabilité"},
            {"action": "Améliorez votre concentration : travaillez 25 minutes sans interruption sur une seule tâche.", "focus": "Focus"}
        ]
    },
    "6": {
        "label": "Responsabilité & Harmonie",
        "themes": ["responsabilité", "service", "harmonie", "protection", "engagement"],
        "strengths": ["fiabilité relationnelle", "sens du service", "capacité à soutenir", "organisation du quotidien"],
        "watchouts": ["sur-responsabilisation", "culpabilité", "difficulté à se prioriser", "charge mentale"],
        "work_preferences": ["utilité concrète", "cadre clair", "collectif", "missions de soin/coordination"],
        "micro_actions": [
            {"action": "Développez votre capacité à prioriser : identifiez vos 3 tâches les plus importantes chaque matin.", "focus": "Priorisation"},
            {"action": "Renforcez vos limites professionnelles : définissez des horaires de travail et respectez-les.", "focus": "Équilibre"},
            {"action": "Travaillez votre lâcher-prise : déléguez une responsabilité sans micro-manager le résultat.", "focus": "Confiance"}
        ]
    },
    "7": {
        "label": "Analyse & Recherche de sens",
        "themes": ["analyse", "profondeur", "recherche", "introspection", "sens"],
        "strengths": ["pensée critique", "capacité à comprendre", "expertise", "recul"],
        "watchouts": ["retrait", "sur-analyse", "difficulté à passer à l'action", "isolement"],
        "work_preferences": ["autonomie", "temps de réflexion", "sujets complexes", "qualité intellectuelle"],
        "micro_actions": [
            {"action": "Développez votre capacité à agir : prenez une décision en suspens dans les 24h et passez à l'action.", "focus": "Passage à l'Action"},
            {"action": "Renforcez votre communication : partagez une de vos analyses avec un collègue de manière synthétique.", "focus": "Communication"},
            {"action": "Travaillez votre collaboration : participez activement à une réunion d'équipe en exprimant vos idées.", "focus": "Travail d'Équipe"}
        ]
    },
    "8": {
        "label": "Impact & Réalisation",
        "themes": ["ambition", "impact", "gestion", "pouvoir d'action", "résultats"],
        "strengths": ["capacité à décider", "orientation résultats", "négociation", "leadership"],
        "watchouts": ["contrôle excessif", "dureté relationnelle", "surmenage", "impatience"],
        "work_preferences": ["responsabilités", "leviers d'action", "enjeux élevés", "autonomie"],
        "micro_actions": [
            {"action": "Développez votre empathie : avant de donner un feedback, demandez d'abord le ressenti de votre interlocuteur.", "focus": "Intelligence Émotionnelle"},
            {"action": "Renforcez votre écoute : posez 3 questions ouvertes avant de proposer votre solution.", "focus": "Écoute Active"},
            {"action": "Travaillez votre patience : laissez vos collaborateurs terminer leurs phrases sans les interrompre.", "focus": "Respect"}
        ]
    },
    "9": {
        "label": "Humanisme & Vision",
        "themes": ["humanisme", "vision", "contribution", "tolérance", "universalité"],
        "strengths": ["capacité à fédérer", "apaisement", "vision globale", "empathie"],
        "watchouts": ["évitement", "inertie", "oubli de soi", "difficulté à trancher"],
        "work_preferences": ["sens", "collectifs", "missions utiles", "climat serein"],
        "micro_actions": [
            {"action": "Développez votre assertivité : exprimez un désaccord de manière constructive lors d'une prochaine réunion.", "focus": "Affirmation de Soi"},
            {"action": "Renforcez votre prise de décision : tranchez une question en suspens sans rechercher le consensus parfait.", "focus": "Décision"},
            {"action": "Travaillez votre auto-affirmation : définissez et communiquez clairement vos besoins professionnels.", "focus": "Expression des Besoins"}
        ]
    },
    "11": {
        "label": "Inspiration & Intuition",
        "themes": ["intuition", "inspiration", "sens", "vision", "créativité élevée"],
        "strengths": ["capacité à inspirer", "intuition", "créativité", "vision"],
        "watchouts": ["hypersensibilité", "surcharge mentale", "doute", "instabilité émotionnelle"],
        "work_preferences": ["projets porteurs de sens", "création", "transmission", "espaces d'autonomie"],
        "micro_actions": [
            {"action": "Développez votre ancrage : validez vos intuitions avec des données concrètes avant d'agir.", "focus": "Esprit Critique"},
            {"action": "Renforcez votre résilience : accueillez un feedback négatif comme une opportunité d'apprentissage.", "focus": "Résilience"},
            {"action": "Travaillez votre gestion émotionnelle : identifiez vos déclencheurs de stress et préparez des réponses adaptées.", "focus": "Gestion du Stress"}
        ]
    },
    "22": {
        "label": "Construction & Ambition",
        "themes": ["construction", "impact durable", "organisation", "vision concrète", "responsabilité"],
        "strengths": ["capacité à structurer", "endurance", "vision long terme", "pilotage"],
        "watchouts": ["pression interne", "sur-contrôle", "charge excessive", "difficulté à ralentir"],
        "work_preferences": ["projets structurants", "responsabilités", "missions long terme", "leviers d'action"],
        "micro_actions": [
            {"action": "Développez votre lâcher-prise : acceptez qu'une tâche soit réalisée différemment de votre vision.", "focus": "Flexibilité"},
            {"action": "Renforcez votre équilibre vie pro/perso : protégez un temps personnel sacré cette semaine.", "focus": "Équilibre"},
            {"action": "Travaillez votre bienveillance : reconnaissez publiquement la contribution d'un collaborateur.", "focus": "Reconnaissance"}
        ]
    },
    "33": {
        "label": "Service & Transmission",
        "themes": ["service", "compassion", "transmission", "inspiration", "harmonie"],
        "strengths": ["capacité à soutenir", "pédagogie", "soin relationnel", "inspiration"],
        "watchouts": ["sur-don", "épuisement", "culpabilité", "limites floues"],
        "work_preferences": ["transmission", "accompagnement", "collectifs", "projets humanistes"],
        "micro_actions": [
            {"action": "Développez vos limites : dites non à une demande supplémentaire pour préserver votre énergie.", "focus": "Affirmation de Soi"},
            {"action": "Renforcez votre auto-soin : planifiez une activité ressourçante obligatoire cette semaine.", "focus": "Bien-être"},
            {"action": "Travaillez votre détachement : accompagnez sans vous sentir responsable du résultat final.", "focus": "Lâcher-prise"}
        ]
    }
}


# ======================================================================
# ROME_RIASEC_MAPPING
# ======================================================================
ROME_RIASEC_MAPPING = {
    # Santé - Principalement I (Investigation) et S (Social)
    "J1102": "IS",  # Médecin généraliste
    "J1104": "SI",  # Sage-femme
    "J1404": "SR",  # Kinésithérapeute
    "J1406": "SA",  # Orthophoniste
    "J1202": "IC",  # Pharmacien
    "J1506": "SI",  # Infirmier
    "J1501": "SR",  # Aide-soignant
    
    # BTP - Principalement R (Réaliste)
    "F1603": "RC",  # Plombier
    "F1703": "RC",  # Maçon
    "F1101": "AI",  # Architecte
    "F1202": "RE",  # Chef de chantier
    "F1602": "RC",  # Électricien
    "I1308": "RC",  # Chauffagiste
    
    # Informatique - Principalement I (Investigation) et C (Conventionnel)
    "M1805": "IC",  # Développeur web
    "M1801": "IC",  # Admin systèmes
    "M1844": "IC",  # Cybersécurité
    "M1828": "EI",  # Chef de projet digital
    "E1205": "AI",  # UX/UI Designer
    "I1401": "RC",  # Technicien support
    
    # Commerce/Vente - Principalement E (Entreprenant)
    "D1402": "ES",  # Commercial
    "D1106": "ES",  # Vendeur conseil
    "M1705": "EA",  # Responsable marketing
    
    # RH/Administration - Principalement S (Social) et C (Conventionnel)
    "M1503": "SE",  # Responsable RH
    "M1502": "SE",  # Chargé de recrutement
    "M1501": "SC",  # Assistant RH
    "M1604": "CS",  # Assistant de direction
    
    # Finance/Comptabilité - Principalement C (Conventionnel) et I (Investigation)
    "M1203": "CI",  # Comptable
    "M1201": "IC",  # Analyste financier
    "M1202": "CI",  # Auditeur
    "M1204": "CI",  # Contrôleur de gestion
    
    # Social/Éducation - Principalement S (Social)
    "K1207": "SA",  # Éducateur spécialisé
    "K1801": "SE",  # Conseiller insertion
    "K2111": "SA",  # Formateur
    "K2107": "SA",  # Enseignant
    "K1206": "SA",  # Animateur socioculturel
    "K1204": "SA",  # Médiateur social
    "K1104": "IS",  # Psychologue
    "K1103": "SE",  # Coach professionnel
    
    # Communication - Principalement A (Artistique) et E (Entreprenant)
    "E1103": "AE",  # Chargé de communication
    "E1101": "AE",  # Community Manager
    "E1106": "AI",  # Journaliste
    "E1401": "AR",  # Graphiste
    
    # Logistique/Transport - Principalement R (Réaliste) et C (Conventionnel)
    "N1101": "RC",  # Cariste
    "N1103": "CR",  # Magasinier
    "N1105": "RC",  # Manutentionnaire
    "N4101": "RC",  # Chauffeur PL
    "N1301": "EC",  # Responsable logistique
    
    # Restauration - Principalement R (Réaliste) et S (Social)
    "G1609": "RA",  # Cuisinier
    "G1803": "SE",  # Serveur
    
    # Juridique - Principalement I (Investigation) et E (Entreprenant)
    "K1901": "IC",  # Notaire
    
    # Recherche - Principalement I (Investigation)
    "K2401": "IA",  # Chercheur
    
    # Industrie
    "H1206": "IR",  # Ingénieur mécanique
    "I1304": "RC",  # Technicien maintenance
    "H1208": "IR",  # Automaticien
    
    # ============================================================================
    # MÉTIERS PORTEURS - Ajouts des PDF France Travail / Grand Est
    # ============================================================================
    
    # Agriculture / Environnement (R dominant)
    "A1202": "RC",  # Entretien espaces naturels
    "A1203": "RC",  # Agent entretien espaces naturels
    "A1204": "RA",  # Aménagement espaces verts (créativité jardinage)
    "A1301": "IS",  # Conseil assistance agriculture
    "A1303": "IR",  # Ingénierie agriculture environnement
    "A1403": "RS",  # Aide élevage agricole
    "A1407": "RS",  # Élevage bovin équin
    "A1416": "RC",  # Polyculture élevage
    
    # Artisanat (A/R dominants)
    "B1302": "AR",  # Décoration objets art artisanaux
    "B1303": "AR",  # Gravure ciselure
    "B1401": "AR",  # Réalisation objets fibres végétaux
    "B1402": "AC",  # Reliure restauration livres
    "B1501": "AR",  # Fabrication réparation instruments musique
    "B1601": "RA",  # Métallerie art
    "B1603": "AR",  # Réalisation bijouterie joaillerie orfèvrerie
    "B1604": "RC",  # Réparation systèmes horlogers
    "B1701": "RI",  # Conservation reconstitution espèces animales
    "B1801": "AR",  # Réalisation articles chapellerie
    "B1802": "AR",  # Réalisation articles cuir
    "B1803": "AR",  # Réalisation vêtements mesure
    "B1804": "AR",  # Réalisation ouvrages art fils
    
    # Banque / Assurance / Immobilier (C/E dominants)
    "C1102": "ES",  # Conseil clientèle assurances
    "C1103": "EC",  # Courtage assurances
    "C1105": "IC",  # Études actuarielles assurances
    "C1106": "IC",  # Expertise risques assurance
    "C1107": "CS",  # Indemnisations assurances
    "C1109": "CE",  # Rédaction gestion assurances
    "C1110": "CE",  # Souscription assurances
    "C1201": "CS",  # Accueil services bancaires
    "C1202": "IC",  # Analyse crédits risques bancaires
    "C1203": "ES",  # Relation clients banque finance
    "C1205": "EI",  # Conseil gestion patrimoine financier
    "C1206": "ES",  # Gestion clientèle bancaire
    "C1302": "CI",  # Gestion back middle-office marchés
    "C1501": "CE",  # Gérance immobilière
    "C1502": "CE",  # Gestion locative immobilière
    "C1503": "EI",  # Management projet immobilier
    "C1504": "ES",  # Transaction immobilière
    
    # Commerce / Vente / Services (E/S dominants)
    "D1101": "RA",  # Boucherie (artisanat manuel)
    "D1102": "RA",  # Boulangerie viennoiserie
    "D1103": "RA",  # Charcuterie traiteur
    "D1104": "AR",  # Pâtisserie confiserie chocolaterie
    "D1105": "RS",  # Poissonnerie
    "D1107": "EC",  # Vente gros produits frais
    "D1202": "AS",  # Coiffure (créatif + social)
    "D1203": "SR",  # Hydrothérapie
    "D1204": "ES",  # Location véhicules matériel
    "D1205": "RC",  # Nettoyage articles textiles
    "D1206": "RC",  # Réparation articles cuir
    "D1207": "RC",  # Retouches habillement
    "D1208": "AS",  # Soins esthétiques corporels
    "D1301": "EC",  # Management magasin détail
    "D1401": "CE",  # Assistance commerciale
    "D1403": "ES",  # Relation commerciale particuliers
    "D1404": "ES",  # Relation commerciale véhicules
    "D1405": "SI",  # Conseil information médicale
    "D1406": "EC",  # Management force vente
    "D1407": "EI",  # Relation technico-commerciale
    "D1408": "ES",  # Téléconseil télévente
    "D1501": "ES",  # Animation vente
    "D1504": "EC",  # Direction magasin grande distribution
    "D1506": "EC",  # Marchandisage
    "D1509": "EC",  # Management département grande distribution
    
    # Communication / Arts graphiques (A dominant)
    "E1108": "AI",  # Traduction interprétariat
    "E1202": "AR",  # Production laboratoire cinématographique
    "E1301": "RC",  # Conduite machines impression
    "E1302": "RC",  # Conduite machines façonnage routage
    "E1303": "EC",  # Encadrement industries graphiques
    "E1304": "RC",  # Façonnage routage
    "E1305": "AC",  # Préparation correction édition presse
    "E1306": "AC",  # Prépresse
    "E1307": "CR",  # Reprographie
    "E1308": "RC",  # Intervention technique industries graphiques
    
    # BTP / Construction (R dominant)
    "F1103": "IC",  # Contrôle diagnostic bâtiment
    "F1104": "CI",  # Dessin BTP
    "F1106": "IR",  # Ingénierie études BTP
    "F1201": "ER",  # Conduite travaux BTP
    "F1301": "RC",  # Conduite de grue
    "F1302": "RC",  # Conduite engins terrassement
    "F1501": "RC",  # Montage structures charpentes bois
    "F1502": "RC",  # Montage structures métalliques
    "F1604": "RC",  # Montage agencements
    "F1605": "RC",  # Montage réseaux électriques
    "F1606": "RA",  # Peinture bâtiment
    "F1607": "RC",  # Pose fermetures menuisées
    "F1608": "RC",  # Pose revêtements rigides
    "F1609": "RC",  # Pose revêtements souples
    "F1610": "RC",  # Pose restauration couvertures
    "F1611": "RC",  # Réalisation façades
    "F1613": "RC",  # Travaux étanchéité isolation
    "F1701": "RC",  # Construction béton
    "F1702": "RC",  # Construction routes voies
    "F1705": "RC",  # Pose canalisations
    
    # Hôtellerie / Restauration / Tourisme (S/E dominants)
    "G1101": "SE",  # Accueil touristique
    "G1302": "EI",  # Optimisation produits touristiques
    "G1303": "ES",  # Vente voyages
    "G1401": "EC",  # Assistance direction hôtel-restaurant
    "G1402": "EC",  # Management hôtel-restaurant
    "G1403": "EC",  # Gestion structure loisirs hébergement
    "G1404": "EC",  # Management restauration collective
    "G1501": "SC",  # Personnel étage
    "G1502": "SR",  # Personnel polyvalent hôtellerie
    "G1503": "ES",  # Management personnel étage
    "G1601": "ES",  # Management personnel cuisine
    "G1602": "RA",  # Personnel cuisine
    "G1603": "SR",  # Personnel polyvalent restauration
    "G1604": "RA",  # Fabrication crêpes pizzas
    "G1605": "RC",  # Plonge restauration
    "G1701": "SE",  # Conciergerie hôtellerie
    "G1702": "SE",  # Personnel hall
    "G1703": "SE",  # Réception hôtellerie
    "G1801": "SE",  # Café bar brasserie
    "G1802": "ES",  # Management service restauration
    "G1804": "AE",  # Sommellerie
    
    # Industrie (R/I/C dominants)
    "H1101": "SI",  # Assistance support technique client
    "H1102": "EI",  # Management ingénierie affaires
    "H1202": "IC",  # Conception dessin électricité électronique
    "H1203": "IC",  # Conception dessin mécanique
    "H1207": "CI",  # Rédaction technique
    "H1209": "IR",  # Intervention études développement électronique
    "H1303": "IC",  # Intervention technique HSE
    "H1403": "CI",  # Intervention technique gestion industrielle
    "H1404": "IC",  # Intervention technique méthodes industrialisation
    "H1503": "IC",  # Intervention technique laboratoire
    "H1504": "IC",  # Intervention contrôle qualité électricité
    "H2201": "RC",  # Assemblage ouvrages bois
    "H2202": "RC",  # Conduite équipement fabrication bois
    "H2206": "RA",  # Réalisation menuiserie bois
    "H2502": "EI",  # Management ingénierie production
    "H2503": "RC",  # Pilotage unité production mécanique
    "H2601": "RC",  # Bobinage électrique
    "H2602": "RC",  # Câblage électrique électromécanique
    "H2604": "RC",  # Montage produits électriques électroniques
    "H2901": "RC",  # Ajustement montage fabrication
    "H2902": "RC",  # Chaudronnerie tôlerie
    "H2903": "RC",  # Conduite équipement usinage
    "H2904": "RC",  # Conduite équipement déformation métaux
    "H2905": "RC",  # Conduite équipement formage découpage
    "H2906": "RC",  # Conduite installation automatisée
    "H2909": "RC",  # Montage assemblage mécanique
    "H2911": "RC",  # Réalisation structures métalliques
    "H2912": "RC",  # Réglage équipement production
    "H2913": "RC",  # Soudage manuel
    "H3202": "RC",  # Réglage équipement formage plastiques
    "H3401": "RC",  # Conduite traitement abrasion surface
    "H3402": "RC",  # Conduite traitement dépôt surface
    "H3403": "RC",  # Conduite traitement thermique
    "H3404": "RC",  # Peinture industrielle
    
    # Installation / Maintenance (R dominant)
    "I1101": "EI",  # Direction ingénierie entretien infrastructure
    "I1301": "RC",  # Installation maintenance ascenseurs
    "I1302": "RC",  # Installation maintenance automatismes
    "I1303": "RC",  # Installation maintenance distributeurs
    "I1305": "RC",  # Installation maintenance électronique
    "I1306": "RC",  # Installation maintenance froid climatisation
    "I1307": "RC",  # Installation maintenance télécoms
    "I1309": "RC",  # Maintenance électrique
    "I1310": "RC",  # Maintenance mécanique industrielle
    "I1402": "RS",  # Réparation biens électrodomestiques
    "I1502": "RI",  # Intervention milieu subaquatique
    "I1503": "RI",  # Intervention milieux produits nocifs
    "I1601": "RC",  # Installation maintenance nautisme
    "I1602": "RI",  # Maintenance aéronefs
    "I1603": "RC",  # Maintenance engins chantier levage
    "I1604": "RC",  # Mécanique automobile
    "I1605": "RC",  # Mécanique marine
    "I1606": "RA",  # Réparation carrosserie
    "I1607": "RC",  # Réparation cycles motocycles
    
    # Santé (I/S dominants)
    "J1301": "SA",  # Développement personnel bien-être
    "J1302": "IC",  # Analyses médicales
    "J1303": "SR",  # Assistance médico-technique
    "J1304": "SA",  # Aide puériculture
    "J1305": "SR",  # Conduite véhicules sanitaires
    "J1306": "IR",  # Imagerie médicale
    "J1307": "CI",  # Préparation pharmacie
    "J1401": "IR",  # Audioprothèses
    "J1402": "SI",  # Diététique
    "J1403": "SI",  # Ergothérapie
    "J1405": "IR",  # Optique lunetterie
    "J1407": "SI",  # Orthoptique
    "J1408": "SI",  # Ostéopathie chiropraxie
    "J1409": "SR",  # Pédicurie podologie
    "J1410": "RI",  # Prothèses dentaires
    "J1411": "RI",  # Prothèses orthèses
    "J1412": "SI",  # Rééducation psychomotricité
    "J1502": "ES",  # Coordination services médicaux
    "J1503": "IS",  # Soins infirmiers anesthésie
    "J1504": "IS",  # Soins infirmiers bloc opératoire
    "J1505": "SI",  # Soins infirmiers prévention
    "J1507": "SA",  # Soins infirmiers puériculture
    
    # Services / Social / Education (S dominant)
    "K1202": "SA",  # Éducation jeunes enfants
    "K1203": "SE",  # Encadrement technique insertion
    "K1301": "SA",  # Accompagnement médicosocial
    "K1302": "SR",  # Assistance auprès adultes
    "K1304": "SR",  # Services domestiques
    "K1305": "SA",  # Intervention sociale familiale
    "K1903": "IE",  # Défense conseil juridique
    "K2101": "SE",  # Conseil formation
    "K2102": "SE",  # Coordination pédagogique
    "K2110": "SR",  # Formation conduite véhicules
    "K2301": "RC",  # Distribution assainissement eau
    "K2303": "RC",  # Nettoyage espaces urbains
    "K2304": "RC",  # Revalorisation produits industriels
    "K2305": "RI",  # Salubrité traitement nuisibles
    "K2402": "IR",  # Recherche sciences univers matière vivant
    "K2501": "CR",  # Gardiennage locaux
    "K2502": "EC",  # Management sécurité privée
    "K2503": "CR",  # Sécurité surveillance privées
    
    # Support entreprise / SI (C/I dominants)
    "M1101": "CE",  # Achats
    "M1102": "EC",  # Direction achats
    "M1205": "EC",  # Direction administrative financière
    "M1206": "CE",  # Management service comptable
    "M1207": "CI",  # Trésorerie financement
    "M1402": "EI",  # Conseil organisation management
    "M1403": "IC",  # Études prospectives socio-économiques
    "M1601": "SC",  # Accueil renseignements
    "M1602": "CE",  # Opérations administratives
    "M1603": "CR",  # Distribution documents
    "M1701": "CE",  # Administration ventes
    "M1702": "IC",  # Analyse tendance
    "M1703": "EI",  # Management gestion produit
    "M1704": "ES",  # Management relation clientèle
    "M1706": "EA",  # Promotion ventes
    "M1707": "EI",  # Stratégie commerciale
    "M1802": "IC",  # Conseil maîtrise ouvrage SI
    "M1803": "EI",  # Direction systèmes information
    "M1804": "IC",  # Études développement réseaux télécoms
    "M1806": "IC",  # Expertise support technique SI
    "M1808": "IC",  # Information géographique
    "M1809": "IC",  # Information météorologique
    "M1810": "CI",  # Production exploitation SI
    
    # Transport / Logistique (R/C dominants)
    "N1104": "RC",  # Manœuvre conduite engins lourds
    "N1201": "CE",  # Affrètement transport
    "N1202": "CE",  # Gestion opérations circulation internationale
    "N1302": "EC",  # Direction site logistique
    "N1303": "CR",  # Intervention technique exploitation logistique
    "N2201": "SE",  # Personnel escale aéroportuaire
    "N2204": "CI",  # Préparation vols
    "N3102": "RC",  # Équipage navigation maritime
    "N3103": "RC",  # Navigation fluviale
    "N3201": "EC",  # Exploitation opérations portuaires transport maritime
    "N3202": "EC",  # Exploitation transport fluvial
    "N4102": "RS",  # Conduite transport particuliers
    "N4103": "RS",  # Conduite transport commun route
    "N4104": "RC",  # Courses livraisons express
    "N4105": "RC",  # Conduite livraison courte distance
    "N4201": "EC",  # Direction exploitation transports marchandises
    "N4202": "EC",  # Direction exploitation transports personnes
    "N4203": "CR",  # Intervention technique transports marchandises
    "N4204": "CR",  # Intervention technique transports personnes
    "N4401": "CR",  # Circulation réseau ferré
}


# ======================================================================
# METIER_TO_VERTU
# ======================================================================
METIER_TO_VERTU = {
    # Sagesse (analyse, tech, recherche)
    "M001": "sagesse",  # Ingénieur en mécanique
    "M011": "sagesse",  # Développeur web
    "M012": "sagesse",  # Administrateur systèmes
    "M040": "sagesse",  # Analyste Cybersécurité
    "M050": "sagesse",  # Chercheur
    "M037": "sagesse",  # Pharmacien
    "M042": "sagesse",  # Analyste financier
    
    # Courage (action, terrain, commerce)
    "M004": "courage",  # Chef de chantier
    "M005": "courage",  # Électricien bâtiment
    "M009": "courage",  # Commercial
    "M010": "courage",  # Responsable marketing
    "M038": "courage",  # Plombier
    "M047": "courage",  # Cuisinier
    "M053": "courage",  # Maçon
    "M054": "courage",  # Chauffagiste
    
    # Humanité (soin, aide, service)
    "M006": "humanite",  # Infirmier
    "M007": "humanite",  # Éducateur spécialisé
    "M008": "humanite",  # Conseiller insertion
    "M017": "humanite",  # Aide-soignant
    "M028": "humanite",  # Psychologue
    "M029": "humanite",  # Médiateur social
    "M032": "humanite",  # Animateur socioculturel
    "M035": "humanite",  # Sage-femme
    "M036": "humanite",  # Kinésithérapeute
    "M048": "humanite",  # Serveur (service client)
    "M052": "humanite",  # Orthophoniste
    
    # Justice (management, organisation, responsabilité)
    "M015": "justice",  # Responsable RH
    "M016": "justice",  # Contrôleur de gestion
    "M041": "justice",  # Chef de projet digital
    "M043": "justice",  # Auditeur
    "M046": "justice",  # Responsable logistique
    "M049": "justice",  # Notaire
    
    # Tempérance (rigueur, précision, organisation)
    "M002": "temperance",  # Technicien maintenance
    "M003": "temperance",  # Automaticien
    "M014": "temperance",  # Comptable
    "M019": "temperance",  # Technicien support
    "M020": "temperance",  # Assistant de direction
    "M021": "temperance",  # Cariste
    "M022": "temperance",  # Magasinier
    "M034": "temperance",  # Médecin (rigueur + humanité)
    "M044": "temperance",  # Assistant RH
    "M051": "temperance",  # Graphiste (rigueur créative)
    
    # Transcendance (créativité, sens, vision)
    "M013": "sagesse",  # UX/UI Designer - Tech + Analyse + Tests (pas transcendance car métier technique)
    "M024": "transcendance",  # Chargé de communication
    "M025": "transcendance",  # Formateur
    "M026": "transcendance",  # Coach professionnel
    "M027": "transcendance",  # Journaliste
    "M030": "transcendance",  # Community Manager
    "M031": "transcendance",  # Enseignant
    "M033": "transcendance",  # Chargé de recrutement
    "M039": "transcendance",  # Architecte
    
    # Métiers logistique sans diplôme
    "M023": "courage",  # Agent de quai (action physique)
    "M045": "temperance",  # Chauffeur PL (rigueur, règles)
    "M018": "humanite",  # Vendeur conseil (relation client)
}


# ======================================================================
# FILIERES
# ======================================================================
FILIERES = [
    {
        "id": "SI",
        "name": "Filière Industrielle",
        "secteurs": ["Mécanique", "Électrotechnique", "Automatisme", "Génie civil", "Chimie", "Métallurgie", "Logistique"]
    },
    {
        "id": "SBTP",
        "name": "Filière BTP",
        "secteurs": ["Maçonnerie", "Menuiserie", "Plomberie", "Électricité du bâtiment", "Charpenterie"]
    },
    {
        "id": "SSS",
        "name": "Filière Santé et Social",
        "secteurs": ["Infirmier(e)", "Aide-soignant(e)", "Assistant(e) de service social", "Éducateur(trice) spécialisé(e)", "Psychologie", "Médiation", "Animation"]
    },
    {
        "id": "SCV",
        "name": "Filière Commerce et Vente",
        "secteurs": ["Vente en magasin", "Commerce international", "Négociation commerciale", "Marketing"]
    },
    {
        "id": "SIN",
        "name": "Filière Informatique et Numérique",
        "secteurs": ["Développement web et mobile", "Administration systèmes", "Cybersécurité", "Design numérique"]
    },
    {
        "id": "SGAE",
        "name": "Filière Gestion et Administration",
        "secteurs": ["Gestion comptable", "Ressources humaines", "Gestion administrative", "Audit et contrôle"]
    },
    {
        "id": "SC",
        "name": "Filière Communication et Formation",
        "secteurs": ["Communication", "Formation", "Accompagnement", "Médias", "Digital", "Éducation"]
    }
]


# ======================================================================
# METIERS
# ======================================================================
METIERS = [
    # ============================================================================
    # FILIÈRE INDUSTRIELLE (SI)
    # ============================================================================
    {
        "id": "M001", 
        "label": "Ingénieur en mécanique", 
        "code_rome": "H1206",
        "intitule_rome": "Management et ingénierie études, recherche et développement industriel",
        "filiere": "SI", 
        "secteur": "Mécanique",
        "definition": "Conçoit et développe des produits ou des systèmes mécaniques. Pilote des projets d'études et de recherche industrielle.",
        "disc_attendu": ["C", "D"], 
        "ennea_compatible": [5, 1, 3],
        # PDF: Ingénieurs pour INTJ, INTP, ENTP, ISTP + ENTJ (leader technique)
        "mbti_compatible": ["INTJ", "INTP", "ENTP", "ISTP", "ENTJ"],
        "competences_requises": ["Analyse technique", "Résolution de problèmes", "Organisation", "Rigueur"],
        "soft_skills_essentiels": [
            {"nom": "Rigueur", "importance": "critique", "description": "Précision dans les calculs et la conception"},
            {"nom": "Pensée analytique", "importance": "critique", "description": "Capacité à décomposer les problèmes complexes"},
            {"nom": "Autonomie", "importance": "importante", "description": "Capacité à mener des projets de façon indépendante"},
            {"nom": "Communication technique", "importance": "importante", "description": "Savoir expliquer des concepts techniques"}
        ],
        "hard_skills_essentiels": [
            {"nom": "CAO (SolidWorks/CATIA)", "importance": "critique", "description": "Conception assistée par ordinateur"},
            {"nom": "Résistance des matériaux", "importance": "critique", "description": "Calculs de structures et dimensionnement"},
            {"nom": "Simulation numérique (FEM)", "importance": "critique", "description": "Analyse par éléments finis"},
            {"nom": "Lecture de plans techniques", "importance": "importante", "description": "Interprétation des dessins industriels"},
            {"nom": "Gestion de projet", "importance": "importante", "description": "Planification et suivi de projets"},
            {"nom": "Normes ISO", "importance": "importante", "description": "Application des standards qualité"}
        ],
        "acces_emploi": "Diplôme d'ingénieur ou Master en mécanique. Expérience en bureau d'études appréciée.",
        "interaction": 1, "cadre": 2, "rythme": 1, "complexite": 2, "autonomie": 2
    },
    {
        "id": "M002", 
        "label": "Technicien de maintenance industrielle", 
        "code_rome": "I1304",
        "intitule_rome": "Installation et maintenance d'équipements industriels et d'exploitation",
        "filiere": "SI", 
        "secteur": "Mécanique",
        "definition": "Assure la maintenance préventive et curative des équipements de production industrielle.",
        "disc_attendu": ["C", "S"], 
        "ennea_compatible": [6, 5, 1],
        # PDF: Mécaniciens pour ISTP ; techniciens pour ISTJ, ESTP
        "mbti_compatible": ["ISTP", "ISTJ", "ESTP", "ESTJ"],
        "competences_requises": ["Diagnostic", "Résolution de problèmes", "Rigueur", "Adaptabilité"],
        "soft_skills_essentiels": [
            {"nom": "Réactivité", "importance": "critique", "description": "Intervenir rapidement en cas de panne"},
            {"nom": "Rigueur", "importance": "critique", "description": "Respect des procédures de sécurité"},
            {"nom": "Adaptabilité", "importance": "importante", "description": "S'adapter à différents types d'équipements"},
            {"nom": "Esprit d'équipe", "importance": "importante", "description": "Travailler avec les équipes de production"}
        ],
        "acces_emploi": "Bac Pro maintenance ou BTS maintenance industrielle. Habilitations électriques requises.",
        "interaction": 1, "cadre": 2, "rythme": 1, "complexite": 1, "autonomie": 1
    },
    {
        "id": "M003", 
        "label": "Automaticien", 
        "code_rome": "H1208",
        "intitule_rome": "Intervention technique en études et développement électronique",
        "filiere": "SI", 
        "secteur": "Automatisme",
        "definition": "Conçoit, programme et met en service des systèmes automatisés de production.",
        "disc_attendu": ["C", "D"], 
        "ennea_compatible": [5, 6, 1],
        # PDF: Programmeurs/analystes systèmes pour INTP, INTJ, ISTJ, ISTP, ENTP
        "mbti_compatible": ["INTP", "INTJ", "ISTJ", "ISTP"],
        "competences_requises": ["Analyse", "Programmation", "Résolution de problèmes", "Rigueur"],
        "soft_skills_essentiels": [
            {"nom": "Pensée logique", "importance": "critique", "description": "Structurer la programmation automate"},
            {"nom": "Précision", "importance": "critique", "description": "Paramétrage exact des systèmes"},
            {"nom": "Curiosité technique", "importance": "importante", "description": "Se tenir à jour des nouvelles technologies"},
            {"nom": "Patience", "importance": "importante", "description": "Débugger et optimiser les programmes"}
        ],
        "acces_emploi": "BTS CIRA, DUT GEII ou Licence pro automatisme. Connaissance des langages automates.",
        "interaction": 0, "cadre": 2, "rythme": 1, "complexite": 2, "autonomie": 2
    },
    # ============================================================================
    # FILIÈRE BTP (SBTP)
    # ============================================================================
    {
        "id": "M004", 
        "label": "Chef de chantier", 
        "code_rome": "F1202",
        "intitule_rome": "Direction de chantier du BTP",
        "filiere": "SBTP", 
        "secteur": "Maçonnerie",
        "definition": "Dirige et coordonne les travaux d'un chantier de construction. Manage les équipes et assure le respect des délais.",
        "disc_attendu": ["D", "S"], 
        "ennea_compatible": [8, 3, 6],
        # PDF: Chefs militaires, gestionnaires, leaders pour ESTJ, ENTJ, ISTJ
        "mbti_compatible": ["ESTJ", "ENTJ", "ISTJ", "ESTP"],
        "competences_requises": ["Leadership", "Organisation", "Communication", "Gestion du stress"],
        "soft_skills_essentiels": [
            {"nom": "Leadership", "importance": "critique", "description": "Diriger et motiver les équipes sur le terrain"},
            {"nom": "Gestion du stress", "importance": "critique", "description": "Gérer les imprévus et les délais serrés"},
            {"nom": "Communication", "importance": "critique", "description": "Coordonner avec les différents corps de métier"},
            {"nom": "Sens des responsabilités", "importance": "importante", "description": "Garantir la sécurité sur le chantier"}
        ],
        "acces_emploi": "BTS bâtiment ou travaux publics. Expérience terrain de plusieurs années.",
        "interaction": 2, "cadre": 1, "rythme": 2, "complexite": 1, "autonomie": 2
    },
    {
        "id": "M005", 
        "label": "Électricien bâtiment", 
        "code_rome": "F1602",
        "intitule_rome": "Électricité bâtiment",
        "filiere": "SBTP", 
        "secteur": "Électricité du bâtiment",
        "definition": "Réalise les travaux d'installation électrique dans les bâtiments résidentiels et tertiaires.",
        "disc_attendu": ["C", "S"], 
        "ennea_compatible": [6, 1, 5],
        # PDF: Charpentiers/mécaniciens techniques pour ISTP ; métiers techniques pour ISTJ
        "mbti_compatible": ["ISTP", "ISTJ", "ESTP", "ESTJ"],
        "competences_requises": ["Rigueur", "Autonomie", "Résolution de problèmes", "Lecture de plans"],
        "soft_skills_essentiels": [
            {"nom": "Rigueur", "importance": "critique", "description": "Respect strict des normes de sécurité électrique"},
            {"nom": "Autonomie", "importance": "importante", "description": "Travailler seul sur des interventions"},
            {"nom": "Sens de l'organisation", "importance": "importante", "description": "Planifier les interventions efficacement"},
            {"nom": "Minutie", "importance": "importante", "description": "Réaliser des raccordements précis"}
        ],
        "acces_emploi": "CAP électricien ou BP électricien. Habilitations électriques obligatoires.",
        "interaction": 1, "cadre": 2, "rythme": 1, "complexite": 1, "autonomie": 1
    },
    # ============================================================================
    # FILIÈRE SANTÉ ET SOCIAL (SSS)
    # ============================================================================
    {
        "id": "M006", 
        "label": "Infirmier(e)", 
        "code_rome": "J1506",
        "intitule_rome": "Soins infirmiers généralistes",
        "filiere": "SSS", 
        "secteur": "Infirmier(e)",
        "definition": "Dispense des soins infirmiers sur prescription médicale. Assure le suivi des patients et leur accompagnement.",
        "disc_attendu": ["S", "I"], 
        "ennea_compatible": [2, 6, 9],
        # PDF: Infirmiers -> ISFJ ; Infirmier/urgentiste -> ESTP ; Soins -> ESFJ
        "mbti_compatible": ["ISFJ", "ESFJ", "ESTP", "INFJ"],
        "competences_requises": ["Empathie", "Communication", "Gestion du stress", "Rigueur"],
        "soft_skills_essentiels": [
            {"nom": "Empathie", "importance": "critique", "description": "Comprendre et accompagner la souffrance des patients"},
            {"nom": "Gestion du stress", "importance": "critique", "description": "Garder son calme en situation d'urgence"},
            {"nom": "Écoute active", "importance": "critique", "description": "Recueillir les informations essentielles du patient"},
            {"nom": "Rigueur", "importance": "importante", "description": "Administrer les traitements sans erreur"},
            {"nom": "Travail en équipe", "importance": "importante", "description": "Collaborer avec l'équipe soignante"}
        ],
        "hard_skills_essentiels": [
            {"nom": "Soins techniques", "importance": "critique", "description": "Injections, pansements, prises de sang"},
            {"nom": "Pharmacologie", "importance": "critique", "description": "Connaissance des médicaments et interactions"},
            {"nom": "Gestes d'urgence (AFGSU)", "importance": "critique", "description": "Réanimation et premiers secours"},
            {"nom": "Logiciels médicaux", "importance": "importante", "description": "Dossier patient informatisé"},
            {"nom": "Hygiène hospitalière", "importance": "importante", "description": "Protocoles de prévention des infections"},
            {"nom": "Transmissions ciblées", "importance": "importante", "description": "Documentation des soins"}
        ],
        "acces_emploi": "Diplôme d'État d'Infirmier (3 ans après le bac). Inscription à l'Ordre des infirmiers.",
        "interaction": 2, "cadre": 2, "rythme": 2, "complexite": 1, "autonomie": 1
    },
    {
        "id": "M007", 
        "label": "Éducateur spécialisé", 
        "code_rome": "K1207",
        "intitule_rome": "Intervention socioéducative",
        "filiere": "SSS", 
        "secteur": "Éducateur(trice) spécialisé(e)",
        "definition": "Accompagne des personnes en difficulté sociale ou en situation de handicap dans leur parcours d'insertion.",
        "disc_attendu": ["S", "I"], 
        "ennea_compatible": [2, 9, 4],
        # PDF: Assistants sociaux -> ISFJ, INFJ, ISFP, ESFJ, ENFJ + INFP mentionné
        "mbti_compatible": ["ISFJ", "INFJ", "INFP", "ENFJ"],
        "competences_requises": ["Empathie", "Communication", "Créativité", "Adaptabilité"],
        "soft_skills_essentiels": [
            {"nom": "Empathie", "importance": "critique", "description": "Se mettre à la place des personnes accompagnées"},
            {"nom": "Patience", "importance": "critique", "description": "Accompagner sur le long terme sans découragement"},
            {"nom": "Créativité", "importance": "importante", "description": "Inventer des activités adaptées aux besoins"},
            {"nom": "Stabilité émotionnelle", "importance": "importante", "description": "Maintenir une posture professionnelle"},
            {"nom": "Sens de l'observation", "importance": "importante", "description": "Détecter les signaux faibles"}
        ],
        "acces_emploi": "Diplôme d'État d'Éducateur Spécialisé (DEES). Formation de 3 ans post-bac.",
        "interaction": 2, "cadre": 1, "rythme": 1, "complexite": 1, "autonomie": 1
    },
    {
        "id": "M008", 
        "label": "Conseiller en insertion professionnelle", 
        "code_rome": "K1801",
        "intitule_rome": "Conseil en emploi et insertion socioprofessionnelle",
        "filiere": "SSS", 
        "secteur": "Assistant(e) de service social",
        "definition": "Accompagne des personnes dans leur parcours d'insertion professionnelle. Aide à définir un projet et à lever les freins.",
        "disc_attendu": ["S", "I"], 
        "ennea_compatible": [2, 9, 6, 4],
        # PDF: Conseiller -> ENFP ; Assistants sociaux -> ISFJ, INFJ, ESFJ, ENFJ ; INFP ajouté car profil d'accompagnement
        "mbti_compatible": ["ENFP", "ENFJ", "INFJ", "INFP", "ESFJ", "ISFJ"],
        "competences_requises": ["Empathie", "Communication", "Organisation", "Écoute active"],
        "soft_skills_essentiels": [
            {"nom": "Écoute active", "importance": "critique", "description": "Comprendre les besoins et contraintes de chacun"},
            {"nom": "Bienveillance", "importance": "critique", "description": "Créer un climat de confiance"},
            {"nom": "Persévérance", "importance": "importante", "description": "Accompagner malgré les échecs"},
            {"nom": "Sens pédagogique", "importance": "importante", "description": "Expliquer les démarches clairement"},
            {"nom": "Réseau relationnel", "importance": "importante", "description": "Mobiliser les partenaires emploi"}
        ],
        "hard_skills_essentiels": [
            {"nom": "Techniques d'entretien", "importance": "critique", "description": "Conduite d'entretiens d'accompagnement"},
            {"nom": "Connaissance du marché du travail", "importance": "critique", "description": "Secteurs, métiers, tendances emploi"},
            {"nom": "Outils numériques emploi", "importance": "importante", "description": "Pôle Emploi, LinkedIn, job boards"},
            {"nom": "Rédaction de CV/LM", "importance": "importante", "description": "Accompagnement à la candidature"},
            {"nom": "Dispositifs d'insertion", "importance": "importante", "description": "IAE, contrats aidés, formations"},
            {"nom": "Bureautique", "importance": "importante", "description": "Pack Office, outils collaboratifs"}
        ],
        "acces_emploi": "Titre professionnel CIP ou Licence pro intervention sociale. Connaissance du marché du travail.",
        "interaction": 2, "cadre": 1, "rythme": 1, "complexite": 1, "autonomie": 1
    },
    {
        "id": "M017", 
        "label": "Aide-soignant(e)", 
        "code_rome": "J1501",
        "intitule_rome": "Soins d'hygiène, de confort du patient",
        "filiere": "SSS", 
        "secteur": "Aide-soignant(e)",
        "definition": "Assure les soins d'hygiène et de confort aux patients sous la responsabilité de l'infirmier.",
        "disc_attendu": ["S", "C"], 
        "ennea_compatible": [2, 6, 9],
        # PDF: Soins, Puériculteurs -> ISFJ, INFJ, ISFP, ESFP, ESFJ
        "mbti_compatible": ["ISFJ", "ESFJ", "ISFP", "ESFP"],
        "competences_requises": ["Empathie", "Patience", "Résistance physique", "Rigueur"],
        "soft_skills_essentiels": [
            {"nom": "Bienveillance", "importance": "critique", "description": "Respecter la dignité des patients"},
            {"nom": "Patience", "importance": "critique", "description": "Accompagner les personnes dépendantes"},
            {"nom": "Résistance physique", "importance": "importante", "description": "Manipuler et déplacer les patients"},
            {"nom": "Discrétion", "importance": "importante", "description": "Respecter l'intimité et la confidentialité"}
        ],
        "acces_emploi": "Diplôme d'État d'Aide-Soignant (DEAS). Formation de 10 mois.",
        "interaction": 2, "cadre": 2, "rythme": 2, "complexite": 0, "autonomie": 0
    },
    # ============================================================================
    # FILIÈRE COMMERCE ET VENTE (SCV)
    # ============================================================================
    {
        "id": "M009", 
        "label": "Commercial / Attaché commercial", 
        "code_rome": "D1402",
        "intitule_rome": "Relation commerciale grands comptes et entreprises",
        "filiere": "SCV", 
        "secteur": "Négociation commerciale",
        "definition": "Prospecte et développe un portefeuille clients. Négocie et conclut des ventes de produits ou services.",
        "disc_attendu": ["D", "I"], 
        "ennea_compatible": [3, 7, 8],
        # PDF: Représentant/vendeur -> ESTP, ESFP, ENTP, ESTJ
        "mbti_compatible": ["ESTP", "ENTP", "ESTJ", "ESFP"],
        "competences_requises": ["Communication", "Persuasion", "Résistance au stress", "Dynamisme"],
        "soft_skills_essentiels": [
            {"nom": "Persévérance", "importance": "critique", "description": "Ne pas se décourager face aux refus"},
            {"nom": "Aisance relationnelle", "importance": "critique", "description": "Créer rapidement le contact"},
            {"nom": "Écoute active", "importance": "importante", "description": "Comprendre les besoins du client"},
            {"nom": "Résistance au stress", "importance": "importante", "description": "Gérer la pression des objectifs"},
            {"nom": "Enthousiasme", "importance": "importante", "description": "Transmettre une énergie positive"}
        ],
        "hard_skills_essentiels": [
            {"nom": "Techniques de vente", "importance": "critique", "description": "Méthodes de prospection et closing"},
            {"nom": "CRM (Salesforce/HubSpot)", "importance": "critique", "description": "Gestion de la relation client"},
            {"nom": "Négociation commerciale", "importance": "critique", "description": "Argumentation et traitement des objections"},
            {"nom": "Pack Office (Excel)", "importance": "importante", "description": "Reporting et tableaux de bord"},
            {"nom": "Connaissance produit", "importance": "importante", "description": "Maîtrise de l'offre commerciale"},
            {"nom": "Social Selling", "importance": "importante", "description": "Prospection via LinkedIn et réseaux"}
        ],
        "acces_emploi": "BTS NDRC, BUT techniques de commercialisation ou école de commerce. Permis B souvent requis.",
        "interaction": 2, "cadre": 0, "rythme": 2, "complexite": 1, "autonomie": 2
    },
    {
        "id": "M010", 
        "label": "Responsable marketing", 
        "code_rome": "M1705",
        "intitule_rome": "Marketing",
        "filiere": "SCV", 
        "secteur": "Marketing",
        "definition": "Définit et met en œuvre la stratégie marketing de l'entreprise. Analyse le marché et pilote les campagnes.",
        "disc_attendu": ["I", "D"], 
        "ennea_compatible": [3, 7, 4],
        # PDF: Personnel de marketing -> ESTP, ENTP ; Stratégie -> ENTJ
        "mbti_compatible": ["ENTP", "ESTP", "ENTJ", "ENFP"],
        "competences_requises": ["Créativité", "Analyse", "Communication", "Leadership"],
        "soft_skills_essentiels": [
            {"nom": "Créativité", "importance": "critique", "description": "Imaginer des campagnes innovantes"},
            {"nom": "Pensée stratégique", "importance": "critique", "description": "Anticiper les tendances du marché"},
            {"nom": "Leadership", "importance": "importante", "description": "Coordonner les équipes et prestataires"},
            {"nom": "Curiosité", "importance": "importante", "description": "Se tenir informé des évolutions digitales"}
        ],
        "acces_emploi": "Master marketing ou école de commerce. Expérience de 3-5 ans en marketing.",
        "interaction": 2, "cadre": 1, "rythme": 1, "complexite": 2, "autonomie": 2
    },
    {
        "id": "M018", 
        "label": "Vendeur conseil en magasin", 
        "code_rome": "D1106",
        "intitule_rome": "Vente en alimentation",
        "filiere": "SCV", 
        "secteur": "Vente en magasin",
        "definition": "Accueille et conseille les clients en magasin. Assure la mise en rayon et l'encaissement.",
        "disc_attendu": ["I", "S"], 
        "ennea_compatible": [2, 7, 9],
        # PDF: Commerçants -> ISFJ ; Représentants/vendeurs -> ESTP, ESFP
        "mbti_compatible": ["ISFJ", "ESFJ", "ESFP", "ESTP"],
        "competences_requises": ["Accueil", "Conseil", "Présentation produits", "Encaissement"],
        "soft_skills_essentiels": [
            {"nom": "Sens du service", "importance": "critique", "description": "Satisfaire les attentes du client"},
            {"nom": "Sourire", "importance": "critique", "description": "Créer une ambiance accueillante"},
            {"nom": "Patience", "importance": "importante", "description": "Gérer les clients difficiles"},
            {"nom": "Dynamisme", "importance": "importante", "description": "Maintenir l'énergie toute la journée"}
        ],
        "acces_emploi": "CAP vente ou Bac pro commerce. Première expérience appréciée.",
        "interaction": 2, "cadre": 2, "rythme": 1, "complexite": 0, "autonomie": 0
    },
    # ============================================================================
    # FILIÈRE INFORMATIQUE ET NUMÉRIQUE (SIN)
    # ============================================================================
    {
        "id": "M011", 
        "label": "Développeur web / fullstack", 
        "code_rome": "M1805",
        "intitule_rome": "Études et développement informatique",
        "filiere": "SIN", 
        "secteur": "Développement web et mobile",
        "definition": "Conçoit et développe des applications web et mobiles. Code les fonctionnalités frontend et/ou backend.",
        "disc_attendu": ["C", "I"], 
        "ennea_compatible": [5, 4, 6],
        # PDF: Programmeurs analystes -> ISTJ, INTJ, ISTP, INTP, ENTP, ENFP + ENTJ (leader technique)
        "mbti_compatible": ["INTP", "INTJ", "ISTP", "ENTP", "ENTJ"],
        "competences_requises": ["Analyse", "Créativité", "Résolution de problèmes", "Rigueur"],
        "soft_skills_essentiels": [
            {"nom": "Rigueur", "importance": "critique", "description": "Écrire du code propre et maintenable"},
            {"nom": "Curiosité", "importance": "critique", "description": "Apprendre continuellement de nouvelles technologies"},
            {"nom": "Persévérance", "importance": "importante", "description": "Débugger sans se décourager"},
            {"nom": "Esprit d'équipe", "importance": "importante", "description": "Collaborer avec les autres développeurs"}
        ],
        "hard_skills_essentiels": [
            {"nom": "JavaScript/TypeScript", "importance": "critique", "description": "Langages de programmation web fondamentaux"},
            {"nom": "React/Vue/Angular", "importance": "critique", "description": "Frameworks frontend modernes"},
            {"nom": "Node.js/Python", "importance": "critique", "description": "Langages et environnements backend"},
            {"nom": "SQL/NoSQL", "importance": "importante", "description": "Gestion des bases de données"},
            {"nom": "Git", "importance": "importante", "description": "Versioning et collaboration de code"},
            {"nom": "API REST/GraphQL", "importance": "importante", "description": "Conception et consommation d'APIs"}
        ],
        "acces_emploi": "BTS SIO, BUT informatique, école d'ingénieur ou bootcamp. Portfolio de projets recommandé.",
        "interaction": 1, "cadre": 1, "rythme": 1, "complexite": 2, "autonomie": 2
    },
    {
        "id": "M012", 
        "label": "Administrateur systèmes et réseaux", 
        "code_rome": "M1801",
        "intitule_rome": "Administration de systèmes d'information",
        "filiere": "SIN", 
        "secteur": "Administration systèmes",
        "definition": "Gère l'infrastructure informatique de l'entreprise. Assure la disponibilité et la sécurité des systèmes.",
        "disc_attendu": ["C", "S"], 
        "ennea_compatible": [5, 6, 1],
        # PDF: Programmeurs analystes systèmes -> ISTJ, INTJ, ISTP, INTP
        "mbti_compatible": ["ISTJ", "INTJ", "ISTP", "INTP"],
        "competences_requises": ["Rigueur", "Analyse", "Résolution de problèmes", "Organisation"],
        "soft_skills_essentiels": [
            {"nom": "Rigueur", "importance": "critique", "description": "Documenter et suivre les procédures"},
            {"nom": "Réactivité", "importance": "critique", "description": "Intervenir rapidement en cas d'incident"},
            {"nom": "Discrétion", "importance": "importante", "description": "Gérer des accès et données sensibles"},
            {"nom": "Pédagogie", "importance": "importante", "description": "Accompagner les utilisateurs"}
        ],
        "hard_skills_essentiels": [
            {"nom": "Linux/Windows Server", "importance": "critique", "description": "Administration de systèmes d'exploitation"},
            {"nom": "Virtualisation (VMware/Hyper-V)", "importance": "critique", "description": "Gestion d'infrastructures virtuelles"},
            {"nom": "Active Directory", "importance": "critique", "description": "Gestion des identités et accès"},
            {"nom": "Réseaux TCP/IP", "importance": "importante", "description": "Configuration et dépannage réseau"},
            {"nom": "Scripting (PowerShell/Bash)", "importance": "importante", "description": "Automatisation des tâches"},
            {"nom": "Cloud (AWS/Azure)", "importance": "importante", "description": "Administration cloud"}
        ],
        "acces_emploi": "BTS SIO, Licence pro réseaux ou école d'ingénieur. Certifications (Cisco, Microsoft) appréciées.",
        "interaction": 0, "cadre": 2, "rythme": 1, "complexite": 2, "autonomie": 1
    },
    {
        "id": "M013", 
        "label": "UX/UI Designer", 
        "code_rome": "E1205",
        "intitule_rome": "Réalisation de contenus multimédias",
        "filiere": "SIN", 
        "secteur": "Design numérique",
        "definition": "Conçoit l'expérience utilisateur et les interfaces des applications et sites web.",
        "disc_attendu": ["I", "C"], 
        "ennea_compatible": [4, 7, 5],
        # CORRIGÉ: UX/UI Designer = métier technique + créatif (pas INFP qui est trop introspectif)
        # France Travail: transition numérique, développement, tests, paramétrage
        "mbti_compatible": ["ISFP", "ENTP", "INTP", "ISTP"],  # Créatifs techniques, pas NF purs
        "competences_requises": ["Créativité", "Empathie", "Communication", "Analyse"],
        "soft_skills_essentiels": [
            {"nom": "Empathie", "importance": "critique", "description": "Se mettre à la place de l'utilisateur"},
            {"nom": "Créativité", "importance": "critique", "description": "Proposer des interfaces innovantes"},
            {"nom": "Écoute", "importance": "importante", "description": "Intégrer les retours utilisateurs"},
            {"nom": "Curiosité", "importance": "importante", "description": "Suivre les tendances du design"}
        ],
        "acces_emploi": "Formation en design (école de design, DSAA) ou reconversion avec portfolio solide.",
        "interaction": 2, "cadre": 0, "rythme": 1, "complexite": 2, "autonomie": 2
    },
    {
        "id": "M019", 
        "label": "Technicien support informatique", 
        "code_rome": "I1401",
        "intitule_rome": "Maintenance informatique et bureautique",
        "filiere": "SIN", 
        "secteur": "Administration systèmes",
        "definition": "Assure le support technique aux utilisateurs. Diagnostique et résout les problèmes informatiques.",
        "disc_attendu": ["S", "C"], 
        "ennea_compatible": [6, 2, 9],
        # PDF: Support technique informatique, Technicien PC -> ESTP
        "mbti_compatible": ["ESTP", "ISTJ", "ISTP", "ISFJ"],
        "competences_requises": ["Diagnostic", "Communication", "Patience", "Résolution de problèmes"],
        "soft_skills_essentiels": [
            {"nom": "Patience", "importance": "critique", "description": "Accompagner des utilisateurs non-techniques"},
            {"nom": "Pédagogie", "importance": "critique", "description": "Expliquer simplement les solutions"},
            {"nom": "Sens du service", "importance": "importante", "description": "Être disponible pour les utilisateurs"},
            {"nom": "Calme", "importance": "importante", "description": "Gérer les utilisateurs stressés"}
        ],
        "acces_emploi": "Bac pro SN, BTS SIO ou titre professionnel TSSR. Première expérience en helpdesk appréciée.",
        "interaction": 2, "cadre": 2, "rythme": 1, "complexite": 1, "autonomie": 1
    },
    # ============================================================================
    # FILIÈRE GESTION ET ADMINISTRATION (SGAE)
    # ============================================================================
    {
        "id": "M014", 
        "label": "Comptable", 
        "code_rome": "M1203",
        "intitule_rome": "Comptabilité",
        "filiere": "SGAE", 
        "secteur": "Gestion comptable",
        "definition": "Tient la comptabilité de l'entreprise. Enregistre les opérations, établit les déclarations et prépare les bilans.",
        "disc_attendu": ["C", "S"], 
        "ennea_compatible": [1, 6, 5],
        # PDF: Comptables, agents financiers -> ISTJ, ISFJ, ESFJ
        "mbti_compatible": ["ISTJ", "ISFJ", "ESFJ", "ESTJ"],
        "competences_requises": ["Rigueur", "Organisation", "Analyse", "Précision"],
        "soft_skills_essentiels": [
            {"nom": "Rigueur", "importance": "critique", "description": "Ne pas tolérer les erreurs de chiffres"},
            {"nom": "Organisation", "importance": "critique", "description": "Respecter les échéances fiscales"},
            {"nom": "Discrétion", "importance": "importante", "description": "Manipuler des données confidentielles"},
            {"nom": "Concentration", "importance": "importante", "description": "Travailler sur des tâches répétitives"}
        ],
        "acces_emploi": "BTS Comptabilité-Gestion, DCG ou DSCG. Maîtrise des logiciels comptables.",
        "interaction": 0, "cadre": 2, "rythme": 1, "complexite": 1, "autonomie": 1
    },
    {
        "id": "M015", 
        "label": "Responsable RH / Chargé(e) RH", 
        "code_rome": "M1503",
        "intitule_rome": "Management des ressources humaines",
        "filiere": "SGAE", 
        "secteur": "Ressources humaines",
        "definition": "Gère les ressources humaines de l'entreprise : recrutement, formation, paie, relations sociales.",
        "disc_attendu": ["S", "I"], 
        "ennea_compatible": [2, 9, 6],
        # PDF: Ressources humaines -> ENFJ ; Administration -> ISFJ, ESFJ
        "mbti_compatible": ["ENFJ", "ESFJ", "ISFJ", "ENFP"],
        "competences_requises": ["Communication", "Empathie", "Organisation", "Leadership"],
        "soft_skills_essentiels": [
            {"nom": "Écoute", "importance": "critique", "description": "Comprendre les besoins des collaborateurs"},
            {"nom": "Diplomatie", "importance": "critique", "description": "Gérer les situations délicates"},
            {"nom": "Discrétion", "importance": "critique", "description": "Traiter des informations sensibles"},
            {"nom": "Sens de l'équité", "importance": "importante", "description": "Appliquer les règles de façon juste"}
        ],
        "acces_emploi": "Master RH, école de commerce ou IEP. Expérience en recrutement ou administration du personnel.",
        "interaction": 2, "cadre": 1, "rythme": 1, "complexite": 1, "autonomie": 2
    },
    {
        "id": "M033", 
        "label": "Chargé(e) de recrutement", 
        "code_rome": "M1502",
        "intitule_rome": "Développement des ressources humaines",
        "filiere": "SGAE", 
        "secteur": "Ressources humaines",
        "definition": "Recruteur spécialisé qui identifie, évalue et sélectionne les candidats pour pourvoir les postes de l'entreprise. Gère le processus de recrutement de A à Z : définition des besoins, sourcing, entretiens, intégration. Aussi appelé talent acquisition, chasseur de têtes ou consultant en recrutement.",
        "disc_attendu": ["I", "S"], 
        "ennea_compatible": [2, 3, 7],
        "mbti_compatible": ["ENFJ", "ENFP", "ESFJ", "ENTJ"],
        "competences_requises": ["Communication", "Écoute active", "Analyse", "Négociation", "Organisation"],
        "soft_skills_essentiels": [
            {"nom": "Écoute active", "importance": "critique", "description": "Comprendre les besoins des managers et les attentes des candidats"},
            {"nom": "Sens du relationnel", "importance": "critique", "description": "Créer un climat de confiance avec les candidats"},
            {"nom": "Capacité d'analyse", "importance": "critique", "description": "Évaluer les compétences et le potentiel des candidats"},
            {"nom": "Persuasion", "importance": "importante", "description": "Convaincre les meilleurs talents de rejoindre l'entreprise"},
            {"nom": "Organisation", "importance": "importante", "description": "Gérer plusieurs recrutements en parallèle"}
        ],
        "hard_skills_essentiels": [
            {"nom": "Techniques d'entretien", "importance": "critique", "description": "Conduite d'entretiens structurés et comportementaux"},
            {"nom": "Sourcing candidats", "importance": "critique", "description": "LinkedIn Recruiter, jobboards, chasse"},
            {"nom": "ATS (Applicant Tracking System)", "importance": "critique", "description": "Gestion des candidatures (Workday, Taleo, etc.)"},
            {"nom": "Assessment", "importance": "importante", "description": "Tests de personnalité, mises en situation"},
            {"nom": "Droit du travail", "importance": "importante", "description": "Cadre juridique du recrutement"},
            {"nom": "Marque employeur", "importance": "importante", "description": "Communication RH et attractivité"}
        ],
        "acces_emploi": "Licence/Master RH, Psychologie du travail ou école de commerce. Première expérience en cabinet de recrutement appréciée.",
        "interaction": 2, "cadre": 1, "rythme": 2, "complexite": 1, "autonomie": 2
    },
    {
        "id": "M016", 
        "label": "Contrôleur de gestion", 
        "code_rome": "M1204",
        "intitule_rome": "Contrôle de gestion",
        "filiere": "SGAE", 
        "secteur": "Audit et contrôle",
        "definition": "Pilote la performance financière de l'entreprise. Élabore les budgets et analyse les écarts.",
        "disc_attendu": ["C", "D"], 
        "ennea_compatible": [1, 5, 3],
        # PDF: Planificateurs stratégiques -> INTP ; Agents financiers -> ISTJ, ESTJ
        "mbti_compatible": ["ISTJ", "INTJ", "INTP", "ENTJ"],
        "competences_requises": ["Analyse", "Rigueur", "Communication", "Organisation"],
        "soft_skills_essentiels": [
            {"nom": "Esprit de synthèse", "importance": "critique", "description": "Produire des reportings clairs"},
            {"nom": "Rigueur", "importance": "critique", "description": "Fiabiliser les données financières"},
            {"nom": "Assertivité", "importance": "importante", "description": "Challenger les opérationnels"},
            {"nom": "Pédagogie", "importance": "importante", "description": "Expliquer les indicateurs aux managers"}
        ],
        "acces_emploi": "Master CCA, école de commerce ou DSCG. Expérience en cabinet d'audit appréciée.",
        "interaction": 1, "cadre": 2, "rythme": 1, "complexite": 2, "autonomie": 2
    },
    {
        "id": "M020", 
        "label": "Assistant(e) de direction", 
        "code_rome": "M1604",
        "intitule_rome": "Assistanat de direction",
        "filiere": "SGAE", 
        "secteur": "Gestion administrative",
        "definition": "Assiste un ou plusieurs dirigeants. Gère l'agenda, organise les réunions et assure le suivi administratif.",
        "disc_attendu": ["S", "C"], 
        "ennea_compatible": [6, 2, 1],
        # PDF: Adjoints administratifs -> ISFJ, ESFJ
        "mbti_compatible": ["ISFJ", "ESFJ", "ISTJ", "ESTJ"],
        "competences_requises": ["Organisation", "Discrétion", "Communication", "Polyvalence"],
        "soft_skills_essentiels": [
            {"nom": "Discrétion", "importance": "critique", "description": "Gérer des informations confidentielles"},
            {"nom": "Organisation", "importance": "critique", "description": "Gérer plusieurs priorités simultanément"},
            {"nom": "Anticipation", "importance": "importante", "description": "Prévoir les besoins du dirigeant"},
            {"nom": "Diplomatie", "importance": "importante", "description": "Interagir avec différents interlocuteurs"}
        ],
        "acces_emploi": "BTS Support à l'Action Managériale ou Licence pro gestion. Maîtrise des outils bureautiques.",
        "interaction": 2, "cadre": 2, "rythme": 1, "complexite": 1, "autonomie": 1
    },
    # ============================================================================
    # FILIÈRE LOGISTIQUE / TRANSPORT
    # ============================================================================
    {
        "id": "M021", 
        "label": "Cariste", 
        "code_rome": "N1101",
        "intitule_rome": "Conduite d'engins de déplacement des charges",
        "filiere": "SI", 
        "secteur": "Logistique",
        "definition": "Conduit un chariot élévateur pour déplacer, charger et décharger des marchandises. Assure le stockage et le réapprovisionnement des zones de production ou d'expédition.",
        "disc_attendu": ["S", "C"], 
        "ennea_compatible": [6, 9, 1],
        # PDF: Mécaniciens, travail manuel -> ISTP ; Organisation -> ISTJ
        "mbti_compatible": ["ISTP", "ISTJ", "ESTP", "ISFJ"],
        "competences_requises": ["Conduite engins", "Organisation", "Vigilance", "Rigueur"],
        "soft_skills_essentiels": [
            {"nom": "Vigilance", "importance": "critique", "description": "Attention constante à la sécurité"},
            {"nom": "Rigueur", "importance": "critique", "description": "Respect des procédures et des zones de stockage"},
            {"nom": "Réactivité", "importance": "importante", "description": "S'adapter aux flux de production"},
            {"nom": "Esprit d'équipe", "importance": "importante", "description": "Coordination avec les équipes logistiques"}
        ],
        "hard_skills_essentiels": [
            {"nom": "CACES R489", "importance": "critique", "description": "Certificat de conduite de chariots élévateurs"},
            {"nom": "Conduite chariot élévateur", "importance": "critique", "description": "Maîtrise des manœuvres de chargement"},
            {"nom": "Lecture de bons de commande", "importance": "importante", "description": "Compréhension des documents logistiques"},
            {"nom": "WMS (logiciel gestion stock)", "importance": "importante", "description": "Utilisation des outils informatiques entrepôt"},
            {"nom": "Règles de sécurité", "importance": "importante", "description": "Normes et procédures en entrepôt"}
        ],
        "acces_emploi": "CACES R489 (anciennement R389) obligatoire. CAP/BEP logistique apprécié. Formation possible en entreprise.",
        "interaction": 1, "cadre": 1, "rythme": 1, "complexite": 0, "autonomie": 1
    },
    {
        "id": "M022", 
        "label": "Magasinier / Préparateur de commandes", 
        "code_rome": "N1103",
        "intitule_rome": "Magasinage et préparation de commandes",
        "filiere": "SI", 
        "secteur": "Logistique",
        "definition": "Réceptionne, stocke et prépare les commandes de produits. Assure la gestion des stocks et le conditionnement des marchandises.",
        "disc_attendu": ["S", "C"], 
        "ennea_compatible": [6, 1, 9],
        # PDF: Organisation méthodique -> ISTJ, ISFJ
        "mbti_compatible": ["ISTJ", "ISFJ", "ISTP", "ESTJ"],
        "competences_requises": ["Organisation", "Rigueur", "Rapidité", "Attention aux détails"],
        "soft_skills_essentiels": [
            {"nom": "Organisation", "importance": "critique", "description": "Gérer efficacement les emplacements de stockage"},
            {"nom": "Précision", "importance": "critique", "description": "Éviter les erreurs de préparation"},
            {"nom": "Endurance physique", "importance": "importante", "description": "Supporter les manutentions répétitives"},
            {"nom": "Autonomie", "importance": "importante", "description": "Travailler de manière indépendante"}
        ],
        "acces_emploi": "CAP/BEP logistique ou expérience équivalente. CACES apprécié. Formation en entreprise possible.",
        "interaction": 0, "cadre": 1, "rythme": 1, "complexite": 0, "autonomie": 1
    },
    {
        "id": "M023", 
        "label": "Agent de quai / Manutentionnaire", 
        "code_rome": "N1105",
        "intitule_rome": "Manutention manuelle de charges",
        "filiere": "SI", 
        "secteur": "Logistique",
        "definition": "Effectue des opérations de manutention, chargement et déchargement de marchandises. Participe au tri et à la distribution des colis.",
        "disc_attendu": ["S", "D"], 
        "ennea_compatible": [9, 6, 8],
        # PDF: Athlètes, travail physique -> ISTP, ESTP
        "mbti_compatible": ["ISTP", "ESTP", "ISTJ", "ESFP"],
        "competences_requises": ["Manutention", "Endurance", "Rapidité", "Travail en équipe"],
        "soft_skills_essentiels": [
            {"nom": "Endurance physique", "importance": "critique", "description": "Résister aux efforts prolongés"},
            {"nom": "Fiabilité", "importance": "critique", "description": "Être ponctuel et constant"},
            {"nom": "Esprit d'équipe", "importance": "importante", "description": "Coordonner avec les collègues"},
            {"nom": "Adaptabilité", "importance": "importante", "description": "S'adapter aux variations de charge"}
        ],
        "acces_emploi": "Aucun diplôme requis. Formation sur le terrain. Bonne condition physique indispensable.",
        "interaction": 1, "cadre": 1, "rythme": 2, "complexite": 0, "autonomie": 0
    },
    # ============================================================================
    # FILIÈRE COMMUNICATION / CRÉATIVITÉ / ACCOMPAGNEMENT (adaptée aux profils NF)
    # ============================================================================
    {
        "id": "M024", 
        "label": "Chargé(e) de communication", 
        "code_rome": "E1103",
        "intitule_rome": "Communication",
        "filiere": "SC", 
        "secteur": "Communication",
        "definition": "Conçoit et met en œuvre des actions de communication interne et externe pour valoriser l'image d'une organisation.",
        "disc_attendu": ["I", "S"], 
        "ennea_compatible": [3, 7, 4],
        # PDF: Communication, Écrivain/Journaliste -> ENFP, ENFJ
        "mbti_compatible": ["ENFP", "ENFJ", "ENTP", "ESFJ"],
        "competences_requises": ["Créativité", "Communication", "Rédaction", "Relations publiques"],
        "soft_skills_essentiels": [
            {"nom": "Créativité", "importance": "critique", "description": "Imaginer des campagnes originales et impactantes"},
            {"nom": "Aisance relationnelle", "importance": "critique", "description": "Interagir avec de nombreux interlocuteurs"},
            {"nom": "Rédaction", "importance": "critique", "description": "Produire des contenus clairs et engageants"},
            {"nom": "Adaptabilité", "importance": "importante", "description": "S'adapter aux différents publics et supports"}
        ],
        "hard_skills_essentiels": [
            {"nom": "Réseaux sociaux", "importance": "critique", "description": "Maîtrise des plateformes social media"},
            {"nom": "PAO (Canva, InDesign)", "importance": "importante", "description": "Création de visuels"},
            {"nom": "Rédaction web", "importance": "importante", "description": "SEO et contenus digitaux"},
            {"nom": "Relations presse", "importance": "importante", "description": "Contacts médias et communiqués"}
        ],
        "acces_emploi": "Licence ou Master en communication, journalisme ou sciences politiques.",
        "interaction": 2, "cadre": 1, "rythme": 1, "complexite": 1, "autonomie": 2
    },
    {
        "id": "M025", 
        "label": "Formateur / Formatrice", 
        "code_rome": "K2111",
        "intitule_rome": "Formation professionnelle",
        "filiere": "SC", 
        "secteur": "Formation",
        "definition": "Conçoit et anime des formations pour adultes. Transmet des savoirs et accompagne le développement des compétences.",
        "disc_attendu": ["I", "S"], 
        "ennea_compatible": [2, 7, 3],
        # PDF: Enseignants -> INFJ, ESTJ, ESFJ, ENFP, INFP ; Professeurs -> INTJ, ISFP, ENFJ
        "mbti_compatible": ["ENFJ", "ENFP", "INFJ", "INFP"],
        "competences_requises": ["Pédagogie", "Communication", "Animation", "Adaptabilité"],
        "soft_skills_essentiels": [
            {"nom": "Pédagogie", "importance": "critique", "description": "Transmettre des savoirs de manière accessible"},
            {"nom": "Écoute active", "importance": "critique", "description": "S'adapter aux besoins des apprenants"},
            {"nom": "Dynamisme", "importance": "importante", "description": "Maintenir l'attention et la motivation"},
            {"nom": "Patience", "importance": "importante", "description": "Accompagner chacun à son rythme"}
        ],
        "hard_skills_essentiels": [
            {"nom": "Ingénierie pédagogique", "importance": "critique", "description": "Concevoir des parcours de formation"},
            {"nom": "Outils digitaux", "importance": "importante", "description": "E-learning, visioconférence, quiz"},
            {"nom": "Expertise métier", "importance": "critique", "description": "Maîtrise du domaine enseigné"}
        ],
        "acces_emploi": "Titre de formateur professionnel ou expérience métier + formation pédagogique.",
        "interaction": 2, "cadre": 1, "rythme": 1, "complexite": 1, "autonomie": 2
    },
    {
        "id": "M026", 
        "label": "Coach professionnel / Coach de vie", 
        "code_rome": "K1103",
        "intitule_rome": "Développement personnel et bien-être de la personne",
        "filiere": "SC", 
        "secteur": "Accompagnement",
        "definition": "Accompagne des personnes dans leur développement personnel ou professionnel pour atteindre leurs objectifs.",
        "disc_attendu": ["I", "S"], 
        "ennea_compatible": [2, 7, 4],
        # PDF: Consultant, Conseiller -> ENFP, ENTP, ESFP, ENFJ
        "mbti_compatible": ["ENFP", "ENFJ", "ENTP", "INFJ"],
        "competences_requises": ["Écoute", "Empathie", "Questionnement", "Motivation"],
        "soft_skills_essentiels": [
            {"nom": "Écoute active", "importance": "critique", "description": "Comprendre les enjeux profonds du coaché"},
            {"nom": "Empathie", "importance": "critique", "description": "Créer un lien de confiance"},
            {"nom": "Questionnement puissant", "importance": "critique", "description": "Faire émerger les prises de conscience"},
            {"nom": "Non-jugement", "importance": "importante", "description": "Accueillir sans diriger"}
        ],
        "hard_skills_essentiels": [
            {"nom": "Techniques de coaching", "importance": "critique", "description": "PNL, analyse transactionnelle, etc."},
            {"nom": "Conduite d'entretien", "importance": "critique", "description": "Structurer les séances"},
            {"nom": "Entrepreneuriat", "importance": "importante", "description": "Gérer son activité indépendante"}
        ],
        "acces_emploi": "Certification en coaching (ICF, RNCP). Expérience professionnelle préalable recommandée.",
        "interaction": 2, "cadre": 0, "rythme": 0, "complexite": 1, "autonomie": 2
    },
    {
        "id": "M027", 
        "label": "Journaliste / Rédacteur(rice)", 
        "code_rome": "E1106",
        "intitule_rome": "Journalisme et information média",
        "filiere": "SC", 
        "secteur": "Médias",
        "definition": "Recherche, vérifie et rédige des informations pour les diffuser via différents médias (presse, web, TV, radio).",
        "disc_attendu": ["I", "D"], 
        "ennea_compatible": [4, 7, 5],
        # PDF: Écrivains/Journalistes -> ENFP, INFP, ENFJ ; Rédacteurs techniques -> INTP
        "mbti_compatible": ["ENFP", "INFP", "ENFJ", "INTP"],
        "competences_requises": ["Rédaction", "Curiosité", "Investigation", "Synthèse"],
        "soft_skills_essentiels": [
            {"nom": "Curiosité", "importance": "critique", "description": "S'intéresser à tous les sujets"},
            {"nom": "Esprit de synthèse", "importance": "critique", "description": "Résumer l'essentiel rapidement"},
            {"nom": "Ténacité", "importance": "importante", "description": "Persévérer dans les enquêtes"},
            {"nom": "Réactivité", "importance": "importante", "description": "Traiter l'actualité en temps réel"}
        ],
        "hard_skills_essentiels": [
            {"nom": "Rédaction journalistique", "importance": "critique", "description": "Écriture claire et factuelle"},
            {"nom": "Vérification des sources", "importance": "critique", "description": "Fact-checking"},
            {"nom": "SEO / Réseaux sociaux", "importance": "importante", "description": "Diffusion digitale"}
        ],
        "acces_emploi": "École de journalisme reconnue ou parcours universitaire en communication/lettres.",
        "interaction": 2, "cadre": 0, "rythme": 2, "complexite": 1, "autonomie": 2
    },
    {
        "id": "M028", 
        "label": "Psychologue", 
        "code_rome": "K1104",
        "intitule_rome": "Psychologie",
        "filiere": "SSS", 
        "secteur": "Psychologie",
        "definition": "Étudie et accompagne le fonctionnement psychique des individus. Propose un soutien thérapeutique ou des évaluations.",
        "disc_attendu": ["S", "C"], 
        "ennea_compatible": [4, 5, 2],
        # PDF: Psychologues -> INFJ, ISFP, INFP, ENFP, ENTP, ENFJ
        "mbti_compatible": ["INFJ", "INFP", "ENFP", "ENFJ"],
        "competences_requises": ["Écoute", "Analyse", "Empathie", "Discrétion"],
        "soft_skills_essentiels": [
            {"nom": "Écoute active", "importance": "critique", "description": "Accueillir la parole sans jugement"},
            {"nom": "Empathie", "importance": "critique", "description": "Comprendre les émotions d'autrui"},
            {"nom": "Stabilité émotionnelle", "importance": "critique", "description": "Ne pas se laisser envahir"},
            {"nom": "Éthique", "importance": "critique", "description": "Respecter le secret professionnel"}
        ],
        "hard_skills_essentiels": [
            {"nom": "Psychopathologie", "importance": "critique", "description": "Connaissance des troubles mentaux"},
            {"nom": "Techniques thérapeutiques", "importance": "critique", "description": "TCC, psychanalyse, etc."},
            {"nom": "Tests psychologiques", "importance": "importante", "description": "Passation et interprétation"}
        ],
        "acces_emploi": "Master 2 en psychologie + stage. Titre protégé.",
        "interaction": 2, "cadre": 1, "rythme": 0, "complexite": 2, "autonomie": 2
    },
    {
        "id": "M029", 
        "label": "Médiateur(rice) social(e)", 
        "code_rome": "K1204",
        "intitule_rome": "Médiation sociale et facilitation de la vie en société",
        "filiere": "SSS", 
        "secteur": "Médiation",
        "definition": "Intervient pour prévenir et résoudre les conflits dans l'espace public ou au sein d'institutions.",
        "disc_attendu": ["S", "I"], 
        "ennea_compatible": [9, 2, 6],
        # PDF: Diplomates, Assistants sociaux -> profils FJ
        "mbti_compatible": ["ENFJ", "INFJ", "ESFJ", "ENFP"],
        "competences_requises": ["Écoute", "Diplomatie", "Calme", "Communication"],
        "soft_skills_essentiels": [
            {"nom": "Diplomatie", "importance": "critique", "description": "Apaiser les tensions"},
            {"nom": "Neutralité", "importance": "critique", "description": "Ne pas prendre parti"},
            {"nom": "Calme", "importance": "critique", "description": "Garder son sang-froid en situation tendue"},
            {"nom": "Empathie", "importance": "importante", "description": "Comprendre les positions de chacun"}
        ],
        "hard_skills_essentiels": [
            {"nom": "Techniques de médiation", "importance": "critique", "description": "Gestion des conflits"},
            {"nom": "Connaissance du territoire", "importance": "importante", "description": "Acteurs locaux et ressources"},
            {"nom": "Réglementation", "importance": "importante", "description": "Droits et devoirs des citoyens"}
        ],
        "acces_emploi": "Titre professionnel de médiateur social ou formation équivalente.",
        "interaction": 2, "cadre": 0, "rythme": 1, "complexite": 1, "autonomie": 1
    },
    {
        "id": "M030", 
        "label": "Community Manager", 
        "code_rome": "E1101",
        "intitule_rome": "Animation de site multimédia",
        "filiere": "SC", 
        "secteur": "Digital",
        "definition": "Anime et développe les communautés en ligne d'une marque ou d'une organisation sur les réseaux sociaux.",
        "disc_attendu": ["I", "D"], 
        "ennea_compatible": [7, 3, 4],
        # PDF: Marketing, Communication -> ENFP, ENTP ; Acteurs -> ESFP
        "mbti_compatible": ["ENFP", "ENTP", "ESFP", "ENFJ"],
        "competences_requises": ["Créativité", "Réactivité", "Rédaction", "Analyse"],
        "soft_skills_essentiels": [
            {"nom": "Créativité", "importance": "critique", "description": "Créer des contenus engageants"},
            {"nom": "Réactivité", "importance": "critique", "description": "Répondre rapidement aux interactions"},
            {"nom": "Sens de l'humour", "importance": "importante", "description": "Ton décalé et engageant"},
            {"nom": "Veille", "importance": "importante", "description": "Suivre les tendances"}
        ],
        "hard_skills_essentiels": [
            {"nom": "Réseaux sociaux", "importance": "critique", "description": "Instagram, LinkedIn, TikTok, X..."},
            {"nom": "Création de contenus", "importance": "critique", "description": "Visuels, vidéos, textes"},
            {"nom": "Analyse de données", "importance": "importante", "description": "KPIs et reporting"}
        ],
        "acces_emploi": "Formation en communication digitale ou marketing. Expérience personnelle appréciée.",
        "interaction": 2, "cadre": 1, "rythme": 2, "complexite": 1, "autonomie": 2
    },
    {
        "id": "M031", 
        "label": "Enseignant(e) / Professeur(e)", 
        "code_rome": "K2107",
        "intitule_rome": "Enseignement général du second degré",
        "filiere": "SC", 
        "secteur": "Éducation",
        "definition": "Transmet des connaissances et accompagne les élèves dans leur parcours scolaire et leur développement.",
        "disc_attendu": ["I", "S"], 
        "ennea_compatible": [2, 1, 5],
        # PDF: Enseignants -> INFJ, ESTJ, ESFJ ; Professeurs -> INTJ, ISFP, ENFJ, ENTJ + INFP
        "mbti_compatible": ["ENFJ", "INFJ", "INFP", "ESTJ"],
        "competences_requises": ["Pédagogie", "Patience", "Organisation", "Communication"],
        "soft_skills_essentiels": [
            {"nom": "Pédagogie", "importance": "critique", "description": "Adapter son enseignement aux élèves"},
            {"nom": "Patience", "importance": "critique", "description": "Accompagner chaque élève"},
            {"nom": "Autorité bienveillante", "importance": "importante", "description": "Maintenir un cadre propice"},
            {"nom": "Enthousiasme", "importance": "importante", "description": "Transmettre le goût d'apprendre"}
        ],
        "hard_skills_essentiels": [
            {"nom": "Expertise disciplinaire", "importance": "critique", "description": "Maîtrise de la matière enseignée"},
            {"nom": "Didactique", "importance": "critique", "description": "Méthodes d'enseignement"},
            {"nom": "Outils numériques", "importance": "importante", "description": "ENT, supports interactifs"}
        ],
        "acces_emploi": "Concours de l'Éducation nationale (CAPES, Agrégation) ou Master MEEF.",
        "interaction": 2, "cadre": 2, "rythme": 1, "complexite": 1, "autonomie": 1
    },
    {
        "id": "M032", 
        "label": "Animateur(rice) socioculturel(le)", 
        "code_rome": "K1206",
        "intitule_rome": "Intervention socioculturelle",
        "filiere": "SSS", 
        "secteur": "Animation",
        "definition": "Conçoit et met en œuvre des projets d'animation visant à favoriser le lien social et l'épanouissement.",
        "disc_attendu": ["I", "S"], 
        "ennea_compatible": [7, 2, 9],
        # PDF: Artistes/acteurs, Assistants sociaux -> ESFP, ENFP, ESFJ, ENFJ
        "mbti_compatible": ["ESFP", "ENFP", "ESFJ", "ENFJ"],
        "competences_requises": ["Animation", "Créativité", "Organisation", "Relationnel"],
        "soft_skills_essentiels": [
            {"nom": "Dynamisme", "importance": "critique", "description": "Entraîner et motiver les groupes"},
            {"nom": "Créativité", "importance": "critique", "description": "Imaginer des activités originales"},
            {"nom": "Écoute", "importance": "importante", "description": "Identifier les besoins du public"},
            {"nom": "Adaptabilité", "importance": "importante", "description": "S'ajuster aux publics variés"}
        ],
        "hard_skills_essentiels": [
            {"nom": "Méthodologie de projet", "importance": "critique", "description": "Concevoir et évaluer des actions"},
            {"nom": "Techniques d'animation", "importance": "critique", "description": "Jeux, débats, ateliers"},
            {"nom": "Gestion de budget", "importance": "importante", "description": "Subventions et dépenses"}
        ],
        "acces_emploi": "BPJEPS animation sociale ou culturelle. DEJEPS pour les postes de coordination.",
        "interaction": 2, "cadre": 0, "rythme": 1, "complexite": 1, "autonomie": 1
    },
    # ============ NOUVEAUX MÉTIERS ROME 2025 ============
    {
        "id": "M034", 
        "label": "Médecin généraliste", 
        "code_rome": "J1102",
        "intitule_rome": "Médecin généraliste",
        "filiere": "SSS", 
        "secteur": "Santé",
        "definition": "Assure le diagnostic, le traitement et le suivi des patients. Premier recours dans le parcours de soins.",
        "disc_attendu": ["C", "S"], 
        "ennea_compatible": [1, 5, 2],
        "mbti_compatible": ["ISTJ", "ISFJ", "INTJ", "INFJ"],
        "competences_requises": ["Diagnostic", "Écoute", "Rigueur", "Empathie"],
        "soft_skills_essentiels": [
            {"nom": "Empathie", "importance": "critique", "description": "Comprendre le patient"},
            {"nom": "Rigueur", "importance": "critique", "description": "Précision dans le diagnostic"}
        ],
        "hard_skills_essentiels": [
            {"nom": "Médecine générale", "importance": "critique", "description": "Connaissances médicales larges"},
            {"nom": "Pharmacologie", "importance": "critique", "description": "Prescription médicamenteuse"}
        ],
        "acces_emploi": "Doctorat en médecine (9 ans d'études minimum).",
        "interaction": 2, "cadre": 1, "rythme": 2, "complexite": 2, "autonomie": 2
    },
    {
        "id": "M035", 
        "label": "Sage-femme", 
        "code_rome": "J1104",
        "intitule_rome": "Sage-femme",
        "filiere": "SSS", 
        "secteur": "Santé",
        "definition": "Accompagne les femmes pendant la grossesse, l'accouchement et le post-partum.",
        "disc_attendu": ["S", "C"], 
        "ennea_compatible": [2, 6, 9],
        "mbti_compatible": ["ISFJ", "ESFJ", "INFJ", "ENFJ"],
        "competences_requises": ["Accompagnement", "Urgence", "Écoute", "Technique médicale"],
        "soft_skills_essentiels": [
            {"nom": "Calme", "importance": "critique", "description": "Gestion des situations d'urgence"},
            {"nom": "Bienveillance", "importance": "critique", "description": "Accompagnement humain"}
        ],
        "hard_skills_essentiels": [
            {"nom": "Obstétrique", "importance": "critique", "description": "Suivi de grossesse et accouchement"},
            {"nom": "Échographie", "importance": "importante", "description": "Diagnostic prénatal"}
        ],
        "acces_emploi": "Diplôme d'État de sage-femme (5 ans d'études).",
        "interaction": 2, "cadre": 1, "rythme": 2, "complexite": 2, "autonomie": 2
    },
    {
        "id": "M036", 
        "label": "Kinésithérapeute", 
        "code_rome": "J1404",
        "intitule_rome": "Kinésithérapeute",
        "filiere": "SSS", 
        "secteur": "Santé",
        "definition": "Rééduque les patients par le mouvement et les techniques manuelles.",
        "disc_attendu": ["S", "I"], 
        "ennea_compatible": [2, 9, 7],
        "mbti_compatible": ["ISFJ", "ESFJ", "ISFP", "ESFP"],
        "competences_requises": ["Rééducation", "Anatomie", "Relationnel", "Patience"],
        "soft_skills_essentiels": [
            {"nom": "Patience", "importance": "critique", "description": "Accompagner la progression"},
            {"nom": "Encouragement", "importance": "importante", "description": "Motiver le patient"}
        ],
        "hard_skills_essentiels": [
            {"nom": "Techniques de massage", "importance": "critique", "description": "Rééducation manuelle"},
            {"nom": "Anatomie", "importance": "critique", "description": "Connaissance du corps humain"}
        ],
        "acces_emploi": "Diplôme d'État de masseur-kinésithérapeute (5 ans d'études).",
        "interaction": 2, "cadre": 1, "rythme": 1, "complexite": 1, "autonomie": 2
    },
    {
        "id": "M037", 
        "label": "Pharmacien(ne)", 
        "code_rome": "J1202",
        "intitule_rome": "Pharmacien / Pharmacienne",
        "filiere": "SSS", 
        "secteur": "Santé",
        "definition": "Délivre les médicaments et conseille les patients sur leur utilisation.",
        "disc_attendu": ["C", "S"], 
        "ennea_compatible": [1, 5, 6],
        "mbti_compatible": ["ISTJ", "ESTJ", "INTJ", "ISFJ"],
        "competences_requises": ["Pharmacologie", "Conseil", "Rigueur", "Gestion"],
        "soft_skills_essentiels": [
            {"nom": "Rigueur", "importance": "critique", "description": "Précision dans la délivrance"},
            {"nom": "Conseil", "importance": "importante", "description": "Accompagnement patient"}
        ],
        "hard_skills_essentiels": [
            {"nom": "Pharmacologie", "importance": "critique", "description": "Connaissance des médicaments"},
            {"nom": "Gestion d'officine", "importance": "importante", "description": "Management et stocks"}
        ],
        "acces_emploi": "Diplôme d'État de docteur en pharmacie (6 ans d'études).",
        "interaction": 1, "cadre": 1, "rythme": 1, "complexite": 1, "autonomie": 2
    },
    {
        "id": "M038", 
        "label": "Plombier / Plombière", 
        "code_rome": "F1603",
        "intitule_rome": "Plombier / Plombière sanitaire",
        "filiere": "SBTP", 
        "secteur": "BTP",
        "definition": "Installe et répare les équipements sanitaires et la plomberie.",
        "disc_attendu": ["C", "S"], 
        "ennea_compatible": [6, 9, 1],
        "mbti_compatible": ["ISTP", "ISTJ", "ESTP", "ESTJ"],
        "competences_requises": ["Technique", "Autonomie", "Résolution problèmes", "Manuel"],
        "soft_skills_essentiels": [
            {"nom": "Autonomie", "importance": "critique", "description": "Travail seul sur chantier"},
            {"nom": "Minutie", "importance": "importante", "description": "Précision des installations"}
        ],
        "hard_skills_essentiels": [
            {"nom": "Plomberie", "importance": "critique", "description": "Installation sanitaire"},
            {"nom": "Lecture de plans", "importance": "importante", "description": "Compréhension technique"}
        ],
        "acces_emploi": "CAP/BEP Plomberie ou équivalent. BP pour chef d'entreprise.",
        "interaction": 0, "cadre": 0, "rythme": 1, "complexite": 1, "autonomie": 2
    },
    {
        "id": "M039", 
        "label": "Architecte", 
        "code_rome": "F1101",
        "intitule_rome": "Architecte du bâtiment",
        "filiere": "SBTP", 
        "secteur": "Architecture",
        "definition": "Conçoit des bâtiments et supervise leur construction.",
        "disc_attendu": ["C", "I"], 
        "ennea_compatible": [4, 5, 7],
        "mbti_compatible": ["INTJ", "INFJ", "INTP", "ENFP", "ENTJ"],
        "competences_requises": ["Créativité", "Technique", "Vision spatiale", "Gestion projet"],
        "soft_skills_essentiels": [
            {"nom": "Créativité", "importance": "critique", "description": "Conception originale"},
            {"nom": "Vision spatiale", "importance": "critique", "description": "Imaginer les volumes"}
        ],
        "hard_skills_essentiels": [
            {"nom": "CAO/DAO", "importance": "critique", "description": "AutoCAD, Revit, SketchUp"},
            {"nom": "Réglementation", "importance": "importante", "description": "Normes construction"}
        ],
        "acces_emploi": "Diplôme d'État d'architecte (5-6 ans en école d'architecture).",
        "interaction": 1, "cadre": 1, "rythme": 1, "complexite": 2, "autonomie": 2
    },
    {
        "id": "M040", 
        "label": "Analyste Cybersécurité", 
        "code_rome": "M1844",
        "intitule_rome": "Analyste en cybersécurité",
        "filiere": "SI", 
        "secteur": "Informatique",
        "definition": "Protège les systèmes informatiques contre les cybermenaces.",
        "disc_attendu": ["C", "D"], 
        "ennea_compatible": [5, 6, 1],
        "mbti_compatible": ["INTJ", "ISTJ", "INTP", "ENTJ"],
        "competences_requises": ["Sécurité IT", "Analyse", "Veille", "Réactivité"],
        "soft_skills_essentiels": [
            {"nom": "Vigilance", "importance": "critique", "description": "Détection des menaces"},
            {"nom": "Sang-froid", "importance": "importante", "description": "Gestion des incidents"}
        ],
        "hard_skills_essentiels": [
            {"nom": "Sécurité réseau", "importance": "critique", "description": "Firewall, IDS/IPS"},
            {"nom": "Ethical hacking", "importance": "importante", "description": "Tests de pénétration"}
        ],
        "acces_emploi": "Bac+5 en cybersécurité ou informatique + certifications (CEH, CISSP).",
        "interaction": 0, "cadre": 1, "rythme": 2, "complexite": 2, "autonomie": 1
    },
    {
        "id": "M041", 
        "label": "Chef de projet digital", 
        "code_rome": "M1828",
        "intitule_rome": "Chef de projet digital",
        "filiere": "SI", 
        "secteur": "Informatique",
        "definition": "Pilote des projets web, mobile ou transformation digitale.",
        "disc_attendu": ["D", "I"], 
        "ennea_compatible": [3, 7, 8],
        "mbti_compatible": ["ENTJ", "ENTP", "ESTJ", "ENFJ"],
        "competences_requises": ["Gestion projet", "Digital", "Communication", "Leadership"],
        "soft_skills_essentiels": [
            {"nom": "Leadership", "importance": "critique", "description": "Coordonner les équipes"},
            {"nom": "Communication", "importance": "critique", "description": "Interface client/technique"}
        ],
        "hard_skills_essentiels": [
            {"nom": "Méthodologies Agile", "importance": "critique", "description": "Scrum, Kanban"},
            {"nom": "Outils PM", "importance": "importante", "description": "Jira, Trello, MS Project"}
        ],
        "acces_emploi": "Bac+5 digital/informatique + 3-5 ans d'expérience projet.",
        "interaction": 2, "cadre": 1, "rythme": 2, "complexite": 2, "autonomie": 2
    },
    {
        "id": "M042", 
        "label": "Analyste financier", 
        "code_rome": "M1201",
        "intitule_rome": "Analyste financier / Analyste financière",
        "filiere": "SGAE", 
        "secteur": "Finance",
        "definition": "Analyse les données financières pour conseiller les décisions d'investissement.",
        "disc_attendu": ["C", "D"], 
        "ennea_compatible": [5, 1, 3],
        "mbti_compatible": ["INTJ", "ISTJ", "ENTJ", "INTP"],
        "competences_requises": ["Analyse financière", "Modélisation", "Rigueur", "Excel avancé"],
        "soft_skills_essentiels": [
            {"nom": "Rigueur", "importance": "critique", "description": "Précision des analyses"},
            {"nom": "Esprit critique", "importance": "importante", "description": "Évaluation objective"}
        ],
        "hard_skills_essentiels": [
            {"nom": "Modélisation financière", "importance": "critique", "description": "DCF, multiples"},
            {"nom": "Excel/VBA", "importance": "critique", "description": "Analyse quantitative"}
        ],
        "acces_emploi": "Bac+5 Finance/Gestion + CFA apprécié.",
        "interaction": 1, "cadre": 1, "rythme": 2, "complexite": 2, "autonomie": 1
    },
    {
        "id": "M043", 
        "label": "Auditeur / Auditrice", 
        "code_rome": "M1202",
        "intitule_rome": "Auditeur comptable et financier",
        "filiere": "SGAE", 
        "secteur": "Finance",
        "definition": "Contrôle les comptes et processus internes des entreprises.",
        "disc_attendu": ["C", "D"], 
        "ennea_compatible": [1, 5, 6],
        "mbti_compatible": ["ISTJ", "INTJ", "ESTJ", "ENTJ"],
        "competences_requises": ["Audit", "Comptabilité", "Analyse", "Rédaction"],
        "soft_skills_essentiels": [
            {"nom": "Intégrité", "importance": "critique", "description": "Indépendance du jugement"},
            {"nom": "Rigueur", "importance": "critique", "description": "Contrôles exhaustifs"}
        ],
        "hard_skills_essentiels": [
            {"nom": "Normes comptables", "importance": "critique", "description": "IFRS, French GAAP"},
            {"nom": "Techniques d'audit", "importance": "critique", "description": "Échantillonnage, contrôles"}
        ],
        "acces_emploi": "Bac+5 Audit/Comptabilité. DEC pour commissaire aux comptes.",
        "interaction": 1, "cadre": 1, "rythme": 2, "complexite": 2, "autonomie": 1
    },
    {
        "id": "M044", 
        "label": "Assistant(e) RH", 
        "code_rome": "M1501",
        "intitule_rome": "Assistant / Assistante Ressources Humaines",
        "filiere": "SGAE", 
        "secteur": "Ressources humaines",
        "definition": "Assiste le service RH dans la gestion administrative du personnel.",
        "disc_attendu": ["S", "I"], 
        "ennea_compatible": [2, 6, 9],
        "mbti_compatible": ["ISFJ", "ESFJ", "ENFJ", "INFJ"],
        "competences_requises": ["Administration", "Paie", "Relationnel", "Organisation"],
        "soft_skills_essentiels": [
            {"nom": "Discrétion", "importance": "critique", "description": "Confidentialité des données"},
            {"nom": "Organisation", "importance": "importante", "description": "Gestion multi-tâches"}
        ],
        "hard_skills_essentiels": [
            {"nom": "Paie", "importance": "importante", "description": "Éléments variables, DSN"},
            {"nom": "Droit du travail", "importance": "importante", "description": "Bases juridiques RH"}
        ],
        "acces_emploi": "Bac+2/3 RH ou gestion. Licence pro GRH.",
        "interaction": 2, "cadre": 1, "rythme": 1, "complexite": 1, "autonomie": 1
    },
    {
        "id": "M045", 
        "label": "Chauffeur poids lourd", 
        "code_rome": "N4101",
        "intitule_rome": "Conducteur / Conductrice de poids lourd",
        "filiere": "SL", 
        "secteur": "Transport",
        "definition": "Transporte des marchandises par route sur longues distances.",
        "disc_attendu": ["S", "C"], 
        "ennea_compatible": [6, 9, 8],
        "mbti_compatible": ["ISTP", "ISTJ", "ESTP", "ISFP"],
        "competences_requises": ["Conduite", "Autonomie", "Réglementation", "Logistique"],
        "soft_skills_essentiels": [
            {"nom": "Autonomie", "importance": "critique", "description": "Travail en solo"},
            {"nom": "Vigilance", "importance": "critique", "description": "Sécurité routière"}
        ],
        "hard_skills_essentiels": [
            {"nom": "Permis C/CE", "importance": "critique", "description": "Conduite poids lourd"},
            {"nom": "FIMO/FCO", "importance": "critique", "description": "Formation obligatoire"}
        ],
        "acces_emploi": "Permis C ou CE + FIMO (Formation Initiale Minimale Obligatoire).",
        "interaction": 0, "cadre": 0, "rythme": 1, "complexite": 0, "autonomie": 2
    },
    {
        "id": "M046", 
        "label": "Responsable logistique", 
        "code_rome": "N1301",
        "intitule_rome": "Responsable logistique",
        "filiere": "SL", 
        "secteur": "Logistique",
        "definition": "Organise et optimise les flux de marchandises et les stocks.",
        "disc_attendu": ["D", "C"], 
        "ennea_compatible": [3, 8, 1],
        "mbti_compatible": ["ESTJ", "ENTJ", "ISTJ", "INTJ"],
        "competences_requises": ["Supply chain", "Management", "Optimisation", "ERP"],
        "soft_skills_essentiels": [
            {"nom": "Organisation", "importance": "critique", "description": "Planification des flux"},
            {"nom": "Leadership", "importance": "importante", "description": "Management d'équipe"}
        ],
        "hard_skills_essentiels": [
            {"nom": "Supply chain", "importance": "critique", "description": "Gestion des flux"},
            {"nom": "ERP/WMS", "importance": "importante", "description": "SAP, Oracle, logiciels logistiques"}
        ],
        "acces_emploi": "Bac+5 Supply Chain/Logistique ou école de commerce + expérience.",
        "interaction": 2, "cadre": 1, "rythme": 2, "complexite": 2, "autonomie": 2
    },
    {
        "id": "M047", 
        "label": "Cuisinier / Cuisinière", 
        "code_rome": "G1609",
        "intitule_rome": "Cuisinier / Cuisinière",
        "filiere": "SHCR", 
        "secteur": "Restauration",
        "definition": "Prépare les plats en cuisine selon les recettes et les commandes.",
        "disc_attendu": ["D", "C"], 
        "ennea_compatible": [3, 7, 8],
        "mbti_compatible": ["ISTP", "ESTP", "ISFP", "ESFP"],
        "competences_requises": ["Cuisine", "Créativité", "Rapidité", "Hygiène"],
        "soft_skills_essentiels": [
            {"nom": "Résistance au stress", "importance": "critique", "description": "Gestion du coup de feu"},
            {"nom": "Créativité", "importance": "importante", "description": "Innovation culinaire"}
        ],
        "hard_skills_essentiels": [
            {"nom": "Techniques culinaires", "importance": "critique", "description": "Préparations, cuissons"},
            {"nom": "Normes HACCP", "importance": "critique", "description": "Hygiène alimentaire"}
        ],
        "acces_emploi": "CAP Cuisine minimum. Bac pro ou BTS pour chef de partie.",
        "interaction": 1, "cadre": 0, "rythme": 2, "complexite": 1, "autonomie": 1
    },
    {
        "id": "M048", 
        "label": "Serveur / Serveuse", 
        "code_rome": "G1803",
        "intitule_rome": "Serveur / Serveuse en restauration",
        "filiere": "SHCR", 
        "secteur": "Restauration",
        "definition": "Accueille les clients et assure le service en salle.",
        "disc_attendu": ["I", "S"], 
        "ennea_compatible": [2, 7, 3],
        "mbti_compatible": ["ESFJ", "ENFJ", "ESFP", "ENFP"],
        "competences_requises": ["Service", "Relationnel", "Rapidité", "Mémoire"],
        "soft_skills_essentiels": [
            {"nom": "Sourire", "importance": "critique", "description": "Accueil chaleureux"},
            {"nom": "Réactivité", "importance": "importante", "description": "Service efficace"}
        ],
        "hard_skills_essentiels": [
            {"nom": "Techniques de service", "importance": "critique", "description": "Port de plateau, dressage"},
            {"nom": "Connaissance carte", "importance": "importante", "description": "Conseils clients"}
        ],
        "acces_emploi": "CAP Service ou expérience. Pas de diplôme obligatoire.",
        "interaction": 2, "cadre": 0, "rythme": 2, "complexite": 0, "autonomie": 1
    },
    {
        "id": "M049", 
        "label": "Notaire", 
        "code_rome": "K1901",
        "intitule_rome": "Notaire",
        "filiere": "SGAE", 
        "secteur": "Juridique",
        "definition": "Officier public qui authentifie les actes juridiques (ventes, successions).",
        "disc_attendu": ["C", "S"], 
        "ennea_compatible": [1, 5, 6],
        "mbti_compatible": ["ISTJ", "INTJ", "ESTJ", "ISFJ"],
        "competences_requises": ["Droit", "Rédaction", "Rigueur", "Conseil"],
        "soft_skills_essentiels": [
            {"nom": "Rigueur", "importance": "critique", "description": "Précision juridique"},
            {"nom": "Discrétion", "importance": "critique", "description": "Secret professionnel"}
        ],
        "hard_skills_essentiels": [
            {"nom": "Droit immobilier", "importance": "critique", "description": "Ventes, hypothèques"},
            {"nom": "Droit des successions", "importance": "critique", "description": "Héritages, donations"}
        ],
        "acces_emploi": "Diplôme de notaire (Master 2 + formation professionnelle 2 ans).",
        "interaction": 1, "cadre": 1, "rythme": 1, "complexite": 2, "autonomie": 2
    },
    {
        "id": "M050", 
        "label": "Chercheur / Chercheuse", 
        "code_rome": "K2401",
        "intitule_rome": "Chercheur / Chercheuse en sciences",
        "filiere": "SCF", 
        "secteur": "Recherche",
        "definition": "Mène des travaux de recherche dans un domaine scientifique.",
        "disc_attendu": ["C", "I"], 
        "ennea_compatible": [5, 4, 1],
        "mbti_compatible": ["INTP", "INTJ", "INFJ", "ENTP"],
        "competences_requises": ["Recherche", "Analyse", "Rédaction", "Rigueur scientifique"],
        "soft_skills_essentiels": [
            {"nom": "Curiosité", "importance": "critique", "description": "Soif de découverte"},
            {"nom": "Persévérance", "importance": "critique", "description": "Recherche de long terme"}
        ],
        "hard_skills_essentiels": [
            {"nom": "Méthodologie recherche", "importance": "critique", "description": "Protocoles scientifiques"},
            {"nom": "Publication", "importance": "importante", "description": "Articles, conférences"}
        ],
        "acces_emploi": "Doctorat (Bac+8) obligatoire. Post-doc souvent nécessaire.",
        "interaction": 1, "cadre": 1, "rythme": 0, "complexite": 2, "autonomie": 2
    },
    {
        "id": "M051", 
        "label": "Graphiste", 
        "code_rome": "E1205",
        "intitule_rome": "Designer graphique",
        "filiere": "SCF", 
        "secteur": "Communication",
        "definition": "Crée des visuels et supports de communication (print et digital).",
        "disc_attendu": ["I", "C"], 
        "ennea_compatible": [4, 7, 3],
        "mbti_compatible": ["ISFP", "INFP", "ENFP", "ISTP"],
        "competences_requises": ["Créativité", "Design", "Logiciels graphiques", "Sens esthétique"],
        "soft_skills_essentiels": [
            {"nom": "Créativité", "importance": "critique", "description": "Concepts originaux"},
            {"nom": "Sens du détail", "importance": "importante", "description": "Finitions soignées"}
        ],
        "hard_skills_essentiels": [
            {"nom": "Suite Adobe", "importance": "critique", "description": "Photoshop, Illustrator, InDesign"},
            {"nom": "UI/UX", "importance": "importante", "description": "Design d'interfaces"}
        ],
        "acces_emploi": "BTS Design graphique, DN MADE, école d'art ou portfolio solide.",
        "interaction": 1, "cadre": 1, "rythme": 1, "complexite": 1, "autonomie": 2
    },
    {
        "id": "M052", 
        "label": "Orthophoniste", 
        "code_rome": "J1406",
        "intitule_rome": "Orthophoniste",
        "filiere": "SSS", 
        "secteur": "Santé",
        "definition": "Rééduque les troubles du langage, de la parole et de la communication.",
        "disc_attendu": ["S", "C"], 
        "ennea_compatible": [2, 4, 9],
        "mbti_compatible": ["ISFJ", "INFJ", "ENFJ", "INFP"],
        "competences_requises": ["Rééducation", "Patience", "Écoute", "Pédagogie"],
        "soft_skills_essentiels": [
            {"nom": "Patience", "importance": "critique", "description": "Rééducation progressive"},
            {"nom": "Empathie", "importance": "critique", "description": "Compréhension des difficultés"}
        ],
        "hard_skills_essentiels": [
            {"nom": "Techniques de rééducation", "importance": "critique", "description": "Exercices orthophoniques"},
            {"nom": "Bilan orthophonique", "importance": "critique", "description": "Diagnostic des troubles"}
        ],
        "acces_emploi": "Certificat de capacité d'orthophoniste (5 ans d'études).",
        "interaction": 2, "cadre": 1, "rythme": 1, "complexite": 1, "autonomie": 2
    },
    {
        "id": "M053", 
        "label": "Maçon / Maçonne", 
        "code_rome": "F1703",
        "intitule_rome": "Maçon / Maçonne",
        "filiere": "SBTP", 
        "secteur": "BTP",
        "definition": "Construit les structures en béton, briques ou parpaings.",
        "disc_attendu": ["S", "D"], 
        "ennea_compatible": [6, 9, 8],
        "mbti_compatible": ["ISTP", "ISTJ", "ESTP", "ESTJ"],
        "competences_requises": ["Construction", "Endurance", "Lecture plans", "Travail équipe"],
        "soft_skills_essentiels": [
            {"nom": "Endurance physique", "importance": "critique", "description": "Travail de force"},
            {"nom": "Précision", "importance": "importante", "description": "Alignement, niveau"}
        ],
        "hard_skills_essentiels": [
            {"nom": "Maçonnerie", "importance": "critique", "description": "Montage murs, coffrages"},
            {"nom": "Lecture de plans", "importance": "importante", "description": "Compréhension technique"}
        ],
        "acces_emploi": "CAP Maçon ou équivalent. BP pour chef d'équipe.",
        "interaction": 1, "cadre": 0, "rythme": 1, "complexite": 1, "autonomie": 1
    },
    {
        "id": "M054", 
        "label": "Chauffagiste", 
        "code_rome": "I1308",
        "intitule_rome": "Chauffagiste",
        "filiere": "SBTP", 
        "secteur": "BTP",
        "definition": "Installe et entretient les systèmes de chauffage et climatisation.",
        "disc_attendu": ["C", "S"], 
        "ennea_compatible": [6, 9, 5],
        "mbti_compatible": ["ISTP", "ISTJ", "ESTP", "INTP"],
        "competences_requises": ["Thermique", "Électricité", "Dépannage", "Autonomie"],
        "soft_skills_essentiels": [
            {"nom": "Autonomie", "importance": "critique", "description": "Interventions seul"},
            {"nom": "Résolution problèmes", "importance": "importante", "description": "Diagnostic pannes"}
        ],
        "hard_skills_essentiels": [
            {"nom": "Thermique", "importance": "critique", "description": "Chaudières, PAC, clim"},
            {"nom": "Électricité", "importance": "importante", "description": "Raccordements, régulation"}
        ],
        "acces_emploi": "CAP/BEP Installation thermique. BP pour chef d'entreprise.",
        "interaction": 0, "cadre": 0, "rythme": 1, "complexite": 1, "autonomie": 2
    }
]


def get_vertu_for_metier(metier_id: str) -> str:
    """Retourne la vertu principale associée à un métier."""
    return METIER_TO_VERTU.get(metier_id, "temperance")

