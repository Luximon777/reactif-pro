# D'CLIC PRO Engine - Extracted from original D'CLIC PRO application
# Contains all data structures, profile computation, and analysis functions

from typing import Dict, Any, List, Optional
import logging
import secrets
import os
# Import France Travail API integration

# Import ESCO API integration (European Skills/Occupations database)
# esco_api not available



# LLM Configuration
# MongoDB connection


# Collection pour les résultats de tests avec code d'accès


# Create the main app without a prefix
# Create a router with the /api prefix


# ============================================================================
# FONCTIONS UTILITAIRES - CODE D'ACCÈS
# ============================================================================

def generate_access_code(length: int = 8) -> str:
    """
    Génère un code d'accès unique et lisible.
    Format: XXXX-XXXX (lettres majuscules et chiffres, sans caractères ambigus)
    """
    # Caractères non ambigus (pas de 0/O, 1/I/L)
    chars = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789'
    code_part1 = ''.join(secrets.choice(chars) for _ in range(4))
    code_part2 = ''.join(secrets.choice(chars) for _ in range(4))
    return f"{code_part1}-{code_part2}"


# ============================================================================
# GÉNÉRATION DE FICHE MÉTIER PAR IA (CLAUDE SONNET 4.5) + CACHE
# ============================================================================

# Collection pour le cache des fiches métiers générées par IA


def normalize_job_title_for_cache(title: str) -> str:
    """Normalise le titre du métier pour la clé de cache."""
    return title.lower().strip()

async def get_cached_ai_job(job_title: str) -> Optional[Dict[str, Any]]:
    """Récupère une fiche métier depuis le cache et incrémente le compteur."""
    try:
        normalized = normalize_job_title_for_cache(job_title)
        # Utiliser findOneAndUpdate pour incrémenter hit_count à chaque lecture
        cached = await ai_job_cache_collection.find_one_and_update(
            {"normalized_title": normalized},
            {"$inc": {"hit_count": 1}},
            projection={"_id": 0, "job_data": 1},
            return_document=True
        )
        if cached:
            logging.info(f"Fiche métier trouvée en cache pour: {job_title}")
            return cached.get("job_data")
        return None
    except Exception as e:
        logging.error(f"Erreur lecture cache: {e}")
        return None

async def save_ai_job_to_cache(job_title: str, job_data: Dict[str, Any]) -> bool:
    """Sauvegarde une fiche métier dans le cache."""
    try:
        normalized = normalize_job_title_for_cache(job_title)
        await ai_job_cache_collection.update_one(
            {"normalized_title": normalized},
            {
                "$set": {
                    "normalized_title": normalized,
                    "original_title": job_title,
                    "job_data": job_data,
                    "updated_at": datetime.now(timezone.utc)
                },
                "$setOnInsert": {
                    "created_at": datetime.now(timezone.utc),
                    "hit_count": 1
                }
            },
            upsert=True
        )
        logging.info(f"Fiche métier mise en cache pour: {job_title}")
        return True
    except Exception as e:
        logging.error(f"Erreur sauvegarde cache: {e}")
        return False

async def generate_job_description_with_ai(job_title: str) -> Optional[Dict[str, Any]]:
    """
    Génère une fiche métier complète via Claude Sonnet 4.5 quand le métier
    n'est pas trouvé dans notre base ni dans ESCO.
    Utilise un cache MongoDB pour éviter les appels répétés.
    """
    # 1. Vérifier le cache d'abord
    cached_job = await get_cached_ai_job(job_title)
    if cached_job:
        return cached_job
    
    # 2. Si pas en cache, générer via IA
    if not EMERGENT_LLM_KEY:
        logging.warning("EMERGENT_LLM_KEY non configurée, impossible de générer la fiche métier par IA")
        return None
    
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"job-gen-{uuid.uuid4().hex[:8]}",
            system_message="""Tu es un expert en orientation professionnelle et en ressources humaines.
Tu dois générer des fiches métiers précises, professionnelles et utiles pour l'orientation.
Réponds UNIQUEMENT en JSON valide, sans commentaires ni texte additionnel."""
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")
        
        prompt = f"""Génère une fiche métier complète pour le poste de "{job_title}" en français.

Réponds UNIQUEMENT avec ce format JSON (sans markdown, sans ```json) :
{{
    "intitule": "{job_title}",
    "definition": "Description détaillée du métier en 3-4 phrases, expliquant les missions principales et le contexte de travail.",
    "soft_skills_essentiels": [
        {{"nom": "Compétence comportementale 1", "importance": "essentielle", "description": "Pourquoi cette compétence est importante"}},
        {{"nom": "Compétence comportementale 2", "importance": "importante", "description": "Pourquoi cette compétence est importante"}},
        {{"nom": "Compétence comportementale 3", "importance": "importante", "description": "Pourquoi cette compétence est importante"}},
        {{"nom": "Compétence comportementale 4", "importance": "utile", "description": "Pourquoi cette compétence est importante"}}
    ],
    "hard_skills_essentiels": [
        {{"nom": "Compétence technique 1", "importance": "essentielle", "description": "Description de la compétence"}},
        {{"nom": "Compétence technique 2", "importance": "importante", "description": "Description de la compétence"}},
        {{"nom": "Compétence technique 3", "importance": "importante", "description": "Description de la compétence"}},
        {{"nom": "Compétence technique 4", "importance": "utile", "description": "Description de la compétence"}}
    ],
    "environnement_travail": "Description de l'environnement de travail typique",
    "perspectives_evolution": "Évolutions de carrière possibles"
}}"""

        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        # Parser la réponse JSON
        import json
        # Nettoyer la réponse si elle contient des backticks markdown
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        clean_response = clean_response.strip()
        
        job_data = json.loads(clean_response)
        job_data["source"] = "ai_generated"
        job_data["intitule_rome"] = job_data.get("intitule", job_title)
        
        # 3. Sauvegarder en cache pour les prochaines fois
        await save_ai_job_to_cache(job_title, job_data)
        
        logging.info(f"Fiche métier générée par IA pour: {job_title}")
        return job_data
        
    except json.JSONDecodeError as e:
        logging.error(f"Erreur parsing JSON de la réponse IA: {e}")
        return None
    except Exception as e:
        logging.error(f"Erreur génération fiche métier par IA: {e}")
        return None


# ============================================================================
# DATA MODELS
# ============================================================================

# ============================================================================
# STATIC DATA - QUESTIONNAIRE VISUEL (Images + Questions courtes)
# ============================================================================

# Images pour les choix visuels
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
                "image": "/q1-groupe.png",
                "alt": "Groupe d'amis qui discutent"
            },
            {
                "id": "v1b",
                "value": "I",
                "label": "Un moment seul(e)",
                "image": "/q1-seul.png",
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
                "image": "/q3-etape.png",
                "alt": "Main écrivant une checklist"
            },
            {
                "id": "v3b",
                "value": "N",
                "label": "Une vision globale",
                "image": "/q3-vision.png",
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
                "image": "/q5-analyse.png",
                "alt": "Analyse de données"
            },
            {
                "id": "v5b",
                "value": "F",
                "label": "J'écoute mon cœur",
                "image": "/q5-coeur.png",
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
                "image": "/q7-planning.png",
                "alt": "Calendrier et planning"
            },
            {
                "id": "v7b",
                "value": "P",
                "label": "De la flexibilité",
                "image": "/q7-flexibilite.png",
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
                "image": "/q10-accelere.png",
                "alt": "Action rapide"
            },
            {
                "id": "v10b",
                "value": "I",
                "label": "Je cherche une alternative créative",
                "image": "/q10-creative.png",
                "alt": "Créativité"
            },
            {
                "id": "v10c",
                "value": "S",
                "label": "Je reste calme et patient",
                "image": "/q10-calme.png",
                "alt": "Calme et patience"
            },
            {
                "id": "v10d",
                "value": "C",
                "label": "J'analyse ce qui n'a pas marché",
                "image": "/q10-analyse.png",
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

# Ancien questionnaire (conservé pour compatibilité)
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


# ============================================================================
# STATIC DATA - VERTUS (Seligman & Peterson)
# ============================================================================

# ============================================================================
# VERTUS (Seligman & Peterson) - Structure Tripartite : Cognition/Conation/Affection
# Basé sur le tableau CK1 - Archéologie des Compétences
# ============================================================================

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


# ============================================================================
# CADRAN D'OFMAN - ZONES DE VIGILANCE
# ============================================================================

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

# ============================================================================
# CADRAN D'OFMAN - CALCUL DYNAMIQUE BASÉ SUR LE PROFIL
# ============================================================================

# Mapping DISC -> Cadran d'Ofman
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

# Mapping MBTI Énergie -> Cadran d'Ofman
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

# Mapping Ennéagramme -> Cadran d'Ofman
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


def calculate_ofman_quadrant(profile: Dict[str, Any], vertu_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Calcule dynamiquement le Cadran d'Ofman basé sur le profil DISC, MBTI et Ennéagramme.
    Retourne les zones de vigilance personnalisées.
    """
    zones = []
    
    # 1. Zone basée sur le profil DISC dominant
    disc = profile.get("disc", "S")
    if disc in DISC_OFMAN:
        disc_zone = DISC_OFMAN[disc].copy()
        disc_zone["source"] = f"Profil DISC ({disc})"
        zones.append(disc_zone)
    
    # 2. Zone basée sur l'Ennéagramme dominant
    ennea = profile.get("ennea_dominant", 5)
    if ennea in ENNEA_OFMAN:
        ennea_zone = ENNEA_OFMAN[ennea].copy()
        ennea_zone["source"] = f"Type Ennéagramme ({ennea})"
        zones.append(ennea_zone)
    
    # 3. Zone basée sur l'énergie MBTI (E/I)
    energie = profile.get("energie", "I")
    if energie in MBTI_ENERGIE_OFMAN:
        energie_zone = MBTI_ENERGIE_OFMAN[energie].copy()
        energie_zone["source"] = f"Énergie MBTI ({energie})"
        zones.append(energie_zone)
    
    # 4. Zone basée sur les vertus dominantes (référentiel existant)
    user_qualities = []
    for qualite in vertu_data.get("qualites_humaines", [])[:2]:
        user_qualities.append(qualite)
    for force in vertu_data.get("forces", [])[:1]:
        user_qualities.append(force)
    
    # Chercher une correspondance dans le référentiel ZONES_VIGILANCE
    for qualite in user_qualities:
        if qualite in ZONES_VIGILANCE and len(zones) < 4:
            vertu_zone = ZONES_VIGILANCE[qualite].copy()
            vertu_zone["source"] = f"Qualité dominante"
            # Vérifier que cette zone n'est pas trop similaire aux autres
            if not any(z["qualite"] == vertu_zone["qualite"] for z in zones):
                zones.append(vertu_zone)
                break
        else:
            # Partial match
            for key, zone in ZONES_VIGILANCE.items():
                if qualite.lower() in key.lower() or key.lower() in qualite.lower():
                    if not any(z["qualite"] == zone["qualite"] for z in zones) and len(zones) < 4:
                        vertu_zone = zone.copy()
                        vertu_zone["source"] = f"Qualité dominante"
                        zones.append(vertu_zone)
                        break
    
    return zones[:4]  # Maximum 4 zones


def get_zones_vigilance_for_profile(profile: Dict[str, Any], vertu_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """Get relevant zones de vigilance based on user profile - using dynamic Ofman calculation."""
    return calculate_ofman_quadrant(profile, vertu_data)


# ============================================================================
# CHEMIN DE VIE - RÉFÉRENTIEL (sans mentionner numérologie)
# ============================================================================

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


def calculate_life_path(birth_date: str) -> str:
    """Calculate life path number from birth date (format: YYYY-MM-DD or DD/MM/YYYY)."""
    try:
        # Clean and parse date
        date_str = birth_date.replace("/", "-").replace(".", "-")
        parts = date_str.split("-")
        
        if len(parts[0]) == 4:  # YYYY-MM-DD
            year, month, day = parts[0], parts[1], parts[2]
        else:  # DD-MM-YYYY
            day, month, year = parts[0], parts[1], parts[2]
        
        # Sum all digits
        all_digits = day + month + year
        total = sum(int(d) for d in all_digits if d.isdigit())
        
        # Reduce to single digit, keeping master numbers
        while total > 9 and total not in [11, 22, 33]:
            total = sum(int(d) for d in str(total))
        
        return str(total)
    except Exception:
        return "5"  # Default to adaptability if parsing fails


def get_life_path_data(birth_date: str) -> Dict[str, Any]:
    """Get life path data for a birth date."""
    path_number = calculate_life_path(birth_date)
    path_data = LIFE_PATHS.get(path_number, LIFE_PATHS["5"])
    return {
        "path_number": path_number,
        **path_data
    }


# ============================================================================
# CROSS-ANALYSIS: Numérologie x DISC x MBTI x Ennéagramme
# ============================================================================

def get_cross_analysis(life_path_data: Dict[str, Any], profile: Dict[str, Any], ennea_type: int) -> Dict[str, Any]:
    """
    Cross-reference numerology (life path) with DISC, MBTI and Enneagram 
    to generate deeper insights and identify synergies/tensions.
    """
    if not life_path_data:
        return None
    
    path_number = life_path_data.get("path_number", "5")
    disc = profile.get("disc", "S")
    energie = profile.get("energie", "E")
    structure = profile.get("structure", "J")
    
    # Synergies (Style de travail x Profil personnel) - SANS termes techniques
    synergies_disc = {
        ("1", "D"): "Votre leadership naturel s'aligne parfaitement avec votre style décisionnaire. Vous êtes fait(e) pour initier et diriger.",
        ("1", "C"): "Votre besoin d'excellence combiné à votre rigueur crée un profil de perfectionniste constructif.",
        ("2", "S"): "Votre sensibilité relationnelle et votre stabilité forment une combinaison idéale pour l'accompagnement.",
        ("2", "I"): "Votre empathie naturelle amplifiée par votre communication chaleureuse vous rend très apprécié(e).",
        ("3", "I"): "Votre créativité expressive et votre charisme créent une synergie puissante pour inspirer les autres.",
        ("3", "D"): "Votre ambition créative combinée à votre détermination vous pousse vers des réalisations remarquables.",
        ("4", "C"): "Votre besoin de structure et votre méthode analytique forment une base solide pour construire durablement.",
        ("4", "S"): "Votre fiabilité et votre constance font de vous un pilier sur lequel on peut compter.",
        ("5", "I"): "Votre soif de liberté et votre sociabilité vous permettent de créer des connexions variées et enrichissantes.",
        ("5", "D"): "Votre adaptabilité et votre audace ouvrent des portes vers des expériences professionnelles variées.",
        ("6", "S"): "Votre sens des responsabilités et votre dévouement font de vous un soutien précieux pour votre entourage.",
        ("6", "C"): "Votre exigence de qualité et votre précision garantissent un travail irréprochable.",
        ("7", "C"): "Votre profondeur analytique et votre rigueur intellectuelle vous permettent d'exceller dans la recherche et l'expertise.",
        ("7", "I"): "Votre sagesse partagée avec enthousiasme fait de vous un transmetteur de connaissances apprécié.",
        ("8", "D"): "Votre puissance d'action et votre leadership créent un profil d'entrepreneur ou de dirigeant naturel.",
        ("8", "C"): "Votre ambition canalisée par votre méthode vous permet d'atteindre des objectifs ambitieux avec précision.",
        ("9", "S"): "Votre humanisme et votre bienveillance créent un environnement harmonieux autour de vous.",
        ("9", "I"): "Votre vision universelle et votre talent de communication vous permettent de fédérer largement.",
        ("11", "I"): "Votre intuition élevée et votre capacité à inspirer font de vous un visionnaire charismatique.",
        ("22", "D"): "Votre vision constructrice et votre détermination vous destinent à des réalisations d'envergure.",
        ("22", "C"): "Votre capacité à structurer et votre méthode vous permettent de bâtir des projets durables.",
        ("33", "S"): "Votre vocation de service et votre soutien inconditionnel font de vous un guide bienveillant.",
    }
    
    # Tensions à gérer (opportunités de croissance) - SANS termes techniques
    tensions_disc = {
        ("1", "S"): "Votre besoin d'autonomie peut parfois entrer en tension avec votre tendance à vous adapter aux autres. Apprenez à affirmer vos positions tout en restant à l'écoute.",
        ("2", "D"): "Votre désir d'harmonie peut être challengé par votre côté direct. Cette tension peut devenir une force : aidez avec assertivité.",
        ("3", "S"): "Votre ambition peut être freinée par votre prudence naturelle. Osez prendre plus de risques calculés.",
        ("4", "I"): "Votre besoin de stabilité peut être bousculé par votre enthousiasme. Canalisez votre énergie dans des projets structurés.",
        ("5", "C"): "Votre soif de liberté peut être contrainte par votre perfectionnisme. Acceptez l'imperfection comme source de liberté.",
        ("6", "D"): "Votre sens du devoir peut créer une tension avec votre autorité naturelle. Apprenez à déléguer sans culpabilité.",
        ("7", "I"): "Votre besoin de profondeur peut être dilué par votre sociabilité. Préservez des temps de solitude réflexive.",
        ("8", "S"): "Votre puissance peut être tempérée par votre diplomatie. Trouvez l'équilibre entre impact et harmonie.",
        ("9", "D"): "Votre idéalisme peut être challengé par votre pragmatisme. Utilisez votre sens pratique au service de vos valeurs.",
    }
    
    # Synergies (Moteur x Profil personnel) - SANS termes techniques
    synergies_ennea = {
        ("1", 3): "Double énergie de réussite : votre essence profonde et votre moteur convergent vers l'accomplissement et l'excellence.",
        ("1", 8): "Leadership amplifié : vous êtes naturellement programmé(e) pour prendre les commandes et influencer.",
        ("2", 2): "Vocation relationnelle confirmée : votre essence profonde est tournée vers l'aide et le soutien aux autres.",
        ("2", 9): "Harmonie intérieure : votre profil soutient votre quête de paix et de connexion.",
        ("3", 3): "Créativité décuplée : expression et réalisation sont au cœur de votre identité.",
        ("3", 7): "Énergie et optimisme combinés : vous avez un potentiel d'enthousiasme et d'innovation remarquable.",
        ("4", 1): "Structure et perfection : vous excellez dans la construction méthodique de projets durables.",
        ("4", 6): "Fiabilité exceptionnelle : on peut compter sur vous en toutes circonstances.",
        ("5", 4): "Liberté créative : vous avez besoin d'espaces d'expression originaux et non conventionnels.",
        ("5", 7): "Curiosité insatiable : vous êtes fait(e) pour explorer, apprendre et expérimenter sans cesse.",
        ("6", 2): "Dévouement authentique : prendre soin des autres est inscrit dans votre ADN.",
        ("6", 6): "Loyauté profonde : la confiance et l'engagement sont vos valeurs cardinales.",
        ("7", 5): "Intelligence profonde : analyse et compréhension sont vos forces majeures.",
        ("7", 4): "Sensibilité intellectuelle : vous combinez profondeur de pensée et finesse émotionnelle.",
        ("8", 8): "Puissance maximale : vous avez une capacité d'impact et d'influence exceptionnelle.",
        ("8", 3): "Ambition stratégique : vous savez où vous allez et comment y arriver.",
        ("9", 9): "Sagesse universelle : vous êtes naturellement orienté(e) vers l'harmonie et le bien commun.",
        ("9", 2): "Humanité profonde : servir les autres avec bienveillance est votre mission naturelle.",
    }
    
    # Construire l'analyse croisée
    synergy_key_disc = (path_number, disc)
    synergy_key_ennea = (path_number, ennea_type)
    
    cross_analysis = {
        "has_cross_analysis": True,
        "synergy_disc": synergies_disc.get(synergy_key_disc, "Votre style de travail et votre profil personnel se complètent, créant un équilibre unique et constructif."),
        "synergy_ennea": synergies_ennea.get(synergy_key_ennea, "Votre essence profonde résonne avec votre moteur intérieur, renforçant votre cohérence personnelle."),
        "tension": tensions_disc.get(synergy_key_disc),
        "integration_insight": None
    }
    
    # Insight d'intégration global - SANS termes techniques
    if energie == "E" and path_number in ["1", "3", "5", "8"]:
        cross_analysis["integration_insight"] = "Votre extraversion amplifie naturellement votre énergie créative. Vous rayonnez et inspirez les autres."
    elif energie == "I" and path_number in ["4", "6", "7", "9"]:
        cross_analysis["integration_insight"] = "Votre introversion nourrit votre profondeur de réflexion. Vous gagnez en sagesse et en impact durable."
    elif structure == "J" and path_number in ["4", "6", "22"]:
        cross_analysis["integration_insight"] = "Votre sens de l'organisation est un atout majeur pour concrétiser vos ambitions et construire durablement."
    elif structure == "P" and path_number in ["3", "5", "7", "11"]:
        cross_analysis["integration_insight"] = "Votre flexibilité naturelle vous permet d'explorer pleinement les possibilités qui s'offrent à vous."
    
    return cross_analysis


# ============================================================================
# BOUSSOLE DE FONCTIONNEMENT - Préférences Cognitives (MBTI/IJTI caché)
# ============================================================================

def get_functioning_compass(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Génère la "Boussole de Fonctionnement" basée sur les préférences cognitives.
    4 axes: Énergie (E/I), Information (S/N), Décision (T/F), Structure (J/P)
    """
    energie = profile.get("energie", "E")
    perception = profile.get("perception", "S")
    decision = profile.get("decision", "T")
    structure = profile.get("structure", "J")
    
    compass = {
        "axes": [
            {
                "name": "Source d'énergie",
                "pole_a": {"label": "Interaction", "code": "E", "description": "Vous vous ressourcez dans l'échange et l'action collective"},
                "pole_b": {"label": "Réflexion", "code": "I", "description": "Vous vous ressourcez dans le calme et l'introspection"},
                "dominant": energie,
                "score": 75 if energie == profile.get("energie") else 25,
                "insight": "Vous êtes naturellement tourné(e) vers les échanges et l'action" if energie == "E" else "Vous préférez la réflexion et les temps de solitude pour vous ressourcer"
            },
            {
                "name": "Traitement de l'information",
                "pole_a": {"label": "Concret", "code": "S", "description": "Vous vous appuyez sur les faits, les détails et l'expérience"},
                "pole_b": {"label": "Conceptuel", "code": "N", "description": "Vous privilégiez les idées, les connexions et les possibilités"},
                "dominant": perception,
                "score": 70 if perception == "S" else 30,
                "insight": "Vous êtes ancré(e) dans le concret et les faits tangibles" if perception == "S" else "Vous êtes orienté(e) vers les idées et les possibilités futures"
            },
            {
                "name": "Mode de décision",
                "pole_a": {"label": "Logique", "code": "T", "description": "Vous décidez selon des critères objectifs et rationnels"},
                "pole_b": {"label": "Valeurs", "code": "F", "description": "Vous décidez en tenant compte de l'impact humain et des valeurs"},
                "dominant": decision,
                "score": 65 if decision == "T" else 35,
                "insight": "Vous privilégiez la logique et l'objectivité dans vos décisions" if decision == "T" else "Vous accordez une grande importance aux valeurs humaines et à l'harmonie"
            },
            {
                "name": "Rapport à l'organisation",
                "pole_a": {"label": "Structure", "code": "J", "description": "Vous aimez planifier, organiser et conclure"},
                "pole_b": {"label": "Flexibilité", "code": "P", "description": "Vous préférez l'adaptabilité et garder vos options ouvertes"},
                "dominant": structure,
                "score": 70 if structure == "J" else 30,
                "insight": "Vous appréciez l'organisation, la planification et les cadres clairs" if structure == "J" else "Vous préférez la flexibilité et l'adaptation aux circonstances"
            }
        ],
        "global_profile": f"{energie}{perception}{decision}{structure}",
        "summary": generate_compass_summary(energie, perception, decision, structure)
    }
    
    return compass


def generate_compass_summary(energie: str, perception: str, decision: str, structure: str) -> str:
    """Génère un résumé narratif de la boussole de fonctionnement."""
    
    summaries = {
        # Profils orientés action
        "ESTJ": "Vous êtes un(e) organisateur(trice) pragmatique. Vous excellez dans la structuration et la gestion concrète des projets.",
        "ENTJ": "Vous êtes un(e) leader stratégique. Vous combinez vision et capacité à organiser pour atteindre vos objectifs.",
        "ESTP": "Vous êtes un(e) pragmatique adaptable. Vous réagissez vite et efficacement aux situations concrètes.",
        "ENTP": "Vous êtes un(e) innovateur(trice) dynamique. Vous aimez explorer de nouvelles idées et débattre.",
        
        # Profils orientés relation
        "ESFJ": "Vous êtes un(e) facilitateur(trice) bienveillant(e). Vous créez naturellement l'harmonie dans les groupes.",
        "ENFJ": "Vous êtes un(e) inspirateur(trice) empathique. Vous savez motiver les autres vers un objectif commun.",
        "ESFP": "Vous êtes un(e) animateur(trice) enthousiaste. Vous apportez de l'énergie positive dans vos environnements.",
        "ENFP": "Vous êtes un(e) créatif(ve) enthousiaste. Vous inspirez les autres par votre optimisme et vos idées.",
        
        # Profils orientés analyse
        "ISTJ": "Vous êtes un(e) méthodique fiable. Vous excellez dans l'exécution rigoureuse et la gestion des détails.",
        "INTJ": "Vous êtes un(e) stratège indépendant(e). Vous développez des visions à long terme avec rigueur.",
        "ISTP": "Vous êtes un(e) analyste pragmatique. Vous résolvez les problèmes avec logique et efficacité.",
        "INTP": "Vous êtes un(e) penseur(se) conceptuel(le). Vous excellez dans l'analyse approfondie et la théorie.",
        
        # Profils orientés accompagnement
        "ISFJ": "Vous êtes un(e) protecteur(trice) attentionné(e). Vous soutenez les autres avec constance et dévouement.",
        "INFJ": "Vous êtes un(e) conseiller(ère) visionnaire. Vous guidez les autres avec profondeur et empathie.",
        "ISFP": "Vous êtes un(e) artisan(e) sensible. Vous apportez une touche personnelle et authentique à vos réalisations.",
        "INFP": "Vous êtes un(e) idéaliste engagé(e). Vous êtes guidé(e) par vos valeurs profondes et votre créativité."
    }
    
    profile_code = f"{energie}{perception}{decision}{structure}"
    return summaries.get(profile_code, "Votre profil unique combine plusieurs dimensions de manière équilibrée.")


# ============================================================================
# ANALYSE INTÉGRÉE - 3 NIVEAUX DE LECTURE
# ============================================================================

def get_integrated_analysis(profile: Dict[str, Any], vertu_data: Dict[str, Any], life_path_data: Dict[str, Any], ofman_zones: List[Dict]) -> Dict[str, Any]:
    """
    Crée une analyse intégrée selon les 3 niveaux de lecture:
    1. PREUVES (Archéologie) - Ce que vous faites naturellement bien
    2. FONCTIONNEMENT (DISC + MBTI) - Comment vous fonctionnez
    3. RÉGULATION (Ofman + Ennéagramme) - Comment vous vous réglez et évoluez
    """
    
    disc = profile.get("disc", "S")
    ennea = profile.get("ennea_dominant", 5)
    
    # Niveau 1: PREUVES (Archéologie des compétences)
    niveau_preuves = {
        "titre": "Ce que vous faites naturellement bien",
        "description": "Vos compétences prouvées et conditions de réussite",
        "elements": {
            "competences_prouvees": vertu_data.get("competences_oms", [])[:4],
            "soft_skills": vertu_data.get("savoirs_etre", [])[:4],
            "forces_cles": vertu_data.get("forces", [])[:3],
            "qualites_humaines": vertu_data.get("qualites_humaines", [])[:4],
            "conditions_reussite": get_success_conditions(disc, profile.get("energie", "E"))
        }
    }
    
    # Niveau 2: FONCTIONNEMENT (DISC + Préférences cognitives)
    niveau_fonctionnement = {
        "titre": "Comment vous fonctionnez",
        "description": "Votre style de travail et vos préférences naturelles",
        "elements": {
            "style_disc": get_disc_style_description(disc),
            "preferences_cognitives": get_cognitive_preferences(profile),
            "environnement_favorable": get_favorable_environment(disc, profile),
            "mode_communication": get_communication_style(disc, profile.get("energie", "E"))
        }
    }
    
    # Niveau 3: RÉGULATION (Ofman + Ennéagramme)
    niveau_regulation = {
        "titre": "Comment vous vous réglez et évoluez",
        "description": "Vos zones de vigilance et leviers de développement",
        "elements": {
            "cadran_ofman": ofman_zones[:3] if ofman_zones else [],
            "moteur_ennea": get_ennea_motor(ennea),
            "leviers_croissance": get_growth_levers(ennea, disc),
            "signaux_stress": get_stress_signals(ennea, disc)
        }
    }
    
    # Croisement Archéologie → Ofman (validation des qualités)
    validation_archeologie = validate_qualities_with_archeology(vertu_data, ofman_zones)
    
    return {
        "niveau_1_preuves": niveau_preuves,
        "niveau_2_fonctionnement": niveau_fonctionnement,
        "niveau_3_regulation": niveau_regulation,
        "validation_archeologie": validation_archeologie,
        "synthese": generate_integrated_synthesis(profile, vertu_data, life_path_data)
    }


def get_success_conditions(disc: str, energie: str) -> List[str]:
    """Retourne les conditions de réussite basées sur le profil."""
    conditions = {
        "D": ["Autonomie décisionnelle", "Objectifs clairs et challengeants", "Résultats mesurables", "Liberté d'action"],
        "I": ["Environnement collaboratif", "Reconnaissance sociale", "Variété des tâches", "Possibilité d'influencer"],
        "S": ["Stabilité et prévisibilité", "Relations de confiance", "Temps de réflexion", "Soutien d'équipe"],
        "C": ["Cadre structuré", "Accès à l'information", "Standards de qualité élevés", "Autonomie technique"]
    }
    base = conditions.get(disc, conditions["S"])
    if energie == "E":
        base.append("Interactions régulières")
    else:
        base.append("Temps de concentration individuel")
    return base[:5]


def get_disc_style_description(disc: str) -> Dict[str, str]:
    """Retourne la description du style DISC."""
    styles = {
        "D": {
            "style": "Directif et orienté résultats",
            "force_principale": "Capacité à décider et agir rapidement",
            "contribution": "Vous faites avancer les projets et prenez des décisions",
            "besoin": "Challenges et autonomie"
        },
        "I": {
            "style": "Enthousiaste et communicatif",
            "force_principale": "Capacité à motiver et créer du lien",
            "contribution": "Vous fédérez les équipes et créez une dynamique positive",
            "besoin": "Reconnaissance et interactions"
        },
        "S": {
            "style": "Stable et coopératif",
            "force_principale": "Capacité à soutenir et maintenir l'harmonie",
            "contribution": "Vous apportez fiabilité et continuité aux projets",
            "besoin": "Sécurité et temps d'adaptation"
        },
        "C": {
            "style": "Analytique et précis",
            "force_principale": "Capacité à analyser et garantir la qualité",
            "contribution": "Vous assurez la rigueur et l'exactitude du travail",
            "besoin": "Information et standards clairs"
        }
    }
    return styles.get(disc, styles["S"])


def get_cognitive_preferences(profile: Dict[str, Any]) -> Dict[str, str]:
    """Retourne les préférences cognitives."""
    return {
        "energie": "Interaction et action" if profile.get("energie") == "E" else "Réflexion et intériorité",
        "information": "Faits concrets et détails" if profile.get("perception") == "S" else "Idées et possibilités",
        "decision": "Logique et objectivité" if profile.get("decision") == "T" else "Valeurs et harmonie",
        "organisation": "Planification et structure" if profile.get("structure") == "J" else "Flexibilité et adaptation"
    }


def get_favorable_environment(disc: str, profile: Dict[str, Any]) -> List[str]:
    """Retourne les caractéristiques de l'environnement favorable."""
    env = {
        "D": ["Leadership possible", "Défis réguliers", "Autonomie", "Résultats visibles"],
        "I": ["Ambiance collaborative", "Créativité encouragée", "Feedback positif", "Variété"],
        "S": ["Équipe stable", "Procédures claires", "Temps d'intégration", "Confiance mutuelle"],
        "C": ["Rigueur valorisée", "Expertise reconnue", "Données accessibles", "Qualité prioritaire"]
    }
    return env.get(disc, env["S"])


def get_communication_style(disc: str, energie: str) -> str:
    """Retourne le style de communication."""
    styles = {
        "D": "Direct et orienté solution - allez droit au but avec des faits",
        "I": "Enthousiaste et expressif - partagez vos idées avec énergie",
        "S": "Calme et à l'écoute - prenez le temps d'établir la confiance",
        "C": "Précis et factuel - appuyez-vous sur les données et la logique"
    }
    return styles.get(disc, styles["S"])


def get_ennea_motor(ennea: int) -> Dict[str, str]:
    """Retourne le moteur interne de l'Ennéagramme."""
    motors = {
        1: {"moteur": "Amélioration et intégrité", "evitement": "L'erreur et l'imperfection", "quete": "Faire les choses correctement"},
        2: {"moteur": "Connexion et utilité", "evitement": "Être rejeté ou inutile", "quete": "Être aimé et apprécié"},
        3: {"moteur": "Réussite et reconnaissance", "evitement": "L'échec et l'insignifiance", "quete": "Être admiré et valorisé"},
        4: {"moteur": "Authenticité et sens", "evitement": "La banalité et le vide", "quete": "Être unique et compris"},
        5: {"moteur": "Connaissance et compétence", "evitement": "L'incompétence et l'intrusion", "quete": "Comprendre et maîtriser"},
        6: {"moteur": "Sécurité et loyauté", "evitement": "Le danger et l'abandon", "quete": "Être en sécurité et soutenu"},
        7: {"moteur": "Liberté et plaisir", "evitement": "La souffrance et la limitation", "quete": "Vivre pleinement et sans contraintes"},
        8: {"moteur": "Force et contrôle", "evitement": "La faiblesse et la dépendance", "quete": "Être fort et autonome"},
        9: {"moteur": "Harmonie et paix", "evitement": "Le conflit et la séparation", "quete": "Être en paix avec tous"}
    }
    return motors.get(ennea, motors[5])


def get_growth_levers(ennea: int, disc: str) -> List[str]:
    """Retourne les leviers de croissance personnalisés."""
    levers = {
        1: ["Accepter l'imperfection", "Cultiver la bienveillance envers soi", "Apprécier le processus autant que le résultat"],
        2: ["Apprendre à recevoir", "Poser des limites saines", "Identifier ses propres besoins"],
        3: ["Ralentir pour se connecter", "Distinguer être et paraître", "Valoriser les relations authentiques"],
        4: ["Apprécier l'ordinaire", "S'engager dans l'action", "Cultiver la gratitude"],
        5: ["S'engager dans le monde", "Partager ses connaissances", "Accepter l'incertitude"],
        6: ["Développer la confiance en soi", "Agir malgré le doute", "Accueillir le changement"],
        7: ["Approfondir plutôt que multiplier", "Rester présent dans les difficultés", "Finir ce qui est commencé"],
        8: ["Montrer sa vulnérabilité", "Écouter avant d'agir", "Faire confiance aux autres"],
        9: ["Affirmer sa position", "Prioriser ses propres besoins", "Exprimer ses opinions"]
    }
    return levers.get(ennea, levers[5])


def get_stress_signals(ennea: int, disc: str) -> List[str]:
    """Retourne les signaux de stress à surveiller."""
    signals = {
        1: ["Critique excessive", "Rigidité accrue", "Irritabilité"],
        2: ["Surinvestissement", "Frustration relationnelle", "Épuisement"],
        3: ["Surmenage", "Impatience", "Déconnexion émotionnelle"],
        4: ["Mélancolie", "Repli sur soi", "Sentiment d'incompréhension"],
        5: ["Retrait excessif", "Suranalyse", "Détachement émotionnel"],
        6: ["Anxiété", "Méfiance", "Indécision paralysante"],
        7: ["Dispersion", "Évitement", "Superficialité"],
        8: ["Confrontation excessive", "Contrôle accru", "Colère"],
        9: ["Passivité", "Procrastination", "Déni des problèmes"]
    }
    return signals.get(ennea, signals[5])


def validate_qualities_with_archeology(vertu_data: Dict[str, Any], ofman_zones: List[Dict]) -> Dict[str, Any]:
    """Valide les qualités d'Ofman avec l'archéologie des compétences."""
    validated = []
    for zone in ofman_zones[:3]:
        qualite = zone.get("qualite", "")
        # Vérifier si cette qualité est confirmée par les vertus
        is_validated = any(
            qualite.lower() in str(v).lower() 
            for v in vertu_data.get("qualites_humaines", []) + vertu_data.get("forces", [])
        )
        validated.append({
            "qualite": qualite,
            "validee_par_archeologie": is_validated,
            "source": zone.get("source", "Analyse"),
            "niveau_confiance": "Élevé" if is_validated else "À explorer"
        })
    return {
        "qualites_validees": validated,
        "message": "Vos qualités fondamentales sont cohérentes avec votre profil de compétences" if any(v["validee_par_archeologie"] for v in validated) else "Explorez ces qualités à travers des expériences concrètes"
    }


def generate_integrated_synthesis(profile: Dict[str, Any], vertu_data: Dict[str, Any], life_path_data: Dict[str, Any]) -> str:
    """Génère une synthèse intégrée des 3 niveaux."""
    disc = profile.get("disc", "S")
    ennea = profile.get("ennea_dominant", 5)
    
    disc_adj = {"D": "déterminé(e)", "I": "enthousiaste", "S": "fiable", "C": "rigoureux(se)"}
    ennea_adj = {1: "intègre", 2: "généreux(se)", 3: "ambitieux(se)", 4: "authentique", 
                 5: "réfléchi(e)", 6: "loyal(e)", 7: "optimiste", 8: "fort(e)", 9: "pacifique"}
    
    return f"Vous êtes une personne {disc_adj.get(disc, 'équilibrée')} et {ennea_adj.get(ennea, 'réfléchie')}, dont les forces naturelles s'expriment pleinement dans un environnement qui respecte vos besoins. Votre chemin de développement passe par la conscience de vos zones de vigilance et l'utilisation de vos leviers de croissance."


# ============================================================================
# AI NARRATIVE GENERATION
# ============================================================================

async def generate_profile_narrative(profile: Dict[str, Any], ennea_profile: Dict[str, Any], vertu_data: Dict[str, Any], life_path_data: Dict[str, Any] = None) -> Dict[str, str]:
    """Generate personalized narrative analysis using AI with complete competency synthesis."""
    
    if not EMERGENT_LLM_KEY:
        # Fallback to template-based narrative
        return generate_fallback_narrative(profile, ennea_profile, vertu_data, life_path_data)
    
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"profile-{uuid.uuid4()}",
            system_message="""Tu es un expert en insertion professionnelle et en orientation, spécialiste reconnu des tests de personnalité (DISC, MBTI, Ennéagramme) et de l'archéologie des compétences.

Tu rédiges comme un professionnel de l'accompagnement avec 20 ans d'expérience.
Tu génères des analyses personnalisées, bienveillantes et concrètes basées sur l'archéologie des compétences.
Tu ne mentionnes JAMAIS les termes techniques comme MBTI, DISC, Ennéagramme, ou les codes (ISTJ, type 5, etc.) dans tes réponses - tu traduis ces concepts en langage accessible.
Tu parles directement à la personne en utilisant "vous".
Tes analyses sont positives, constructives et orientées vers l'action concrète.
Tu intègres naturellement les différentes dimensions (vertus, forces, valeurs, qualités, compétences, savoirs-être).
Tu écris en français courant et accessible, avec un ton professionnel mais chaleureux."""
        ).with_model("openai", "gpt-5.2")
        
        # Build context for AI
        energie_desc = "tourné vers les autres et les échanges" if profile["energie"] == "E" else "réservant votre énergie pour la réflexion personnelle"
        perception_desc = "ancré dans le concret et les faits" if profile["perception"] == "S" else "orienté vers les idées et les possibilités"
        decision_desc = "privilégiant la logique et l'objectivité" if profile["decision"] == "T" else "accordant de l'importance aux valeurs humaines"
        structure_desc = "appréciant l'organisation et la planification" if profile["structure"] == "J" else "préférant la flexibilité et l'adaptation"
        
        disc_descriptions = {
            "D": "orienté vers l'action et les résultats, avec une capacité naturelle à prendre des décisions",
            "I": "doté d'un talent naturel pour communiquer et motiver les autres",
            "S": "appréciant la stabilité et excellant dans le soutien aux équipes",
            "C": "rigoureux et méthodique, avec un souci du détail remarquable"
        }
        disc_desc = disc_descriptions.get(profile["disc"], "équilibré dans votre approche")
        
        # Prepare all competency dimensions
        forces_str = ", ".join(vertu_data.get("forces", [])[:4])
        valeurs_str = ", ".join(vertu_data.get("valeurs_schwartz", [])[:3])
        qualites_str = ", ".join(vertu_data.get("qualites_humaines", [])[:5])
        competences_oms_str = ", ".join(vertu_data.get("competences_oms", [])[:3])
        savoirs_etre_str = ", ".join(vertu_data.get("savoirs_etre", [])[:3])
        
        prompt = f"""Génère une SYNTHÈSE COMPLÈTE du profil professionnel en intégrant toutes les dimensions de l'archéologie des compétences.

DONNÉES DU PROFIL:
- Mode d'énergie: {energie_desc}
- Perception du monde: {perception_desc}
- Prise de décision: {decision_desc}
- Rapport à la structure: {structure_desc}
- Style de travail: {disc_desc}
- Moteur principal: {ennea_profile['moteur']}

ARCHÉOLOGIE DES COMPÉTENCES (à intégrer dans la synthèse):
- Vertu dominante: {vertu_data['name']}
- Forces de caractère: {forces_str}
- Valeurs fondamentales: {valeurs_str}
- Qualités humaines: {qualites_str}
- Compétences psychosociales (OMS): {competences_oms_str}
- Savoirs-être professionnels: {savoirs_etre_str}

- Compétences transversales identifiées: {', '.join(profile['competences_fortes'])}
- Points de vigilance: {', '.join(profile['vigilances']) if profile['vigilances'] else 'Aucun identifié'}
{f'''
PROFIL PERSONNEL ENRICHI:
- Thématique dominante: {life_path_data.get('label', 'Non renseigné')}
- Forces naturelles révélées: {', '.join(life_path_data.get('strengths', [])[:4])}
- Points de vigilance personnels: {', '.join(life_path_data.get('watchouts', [])[:3])}
- Préférences de travail alignées: {', '.join(life_path_data.get('work_preferences', [])[:3])}

IMPORTANT: Ces éléments doivent être intégrés subtilement dans la synthèse, sans JAMAIS mentionner les termes techniques (numérologie, chemin de vie, MBTI, DISC, Ennéagramme, etc.).
''' if life_path_data else ''}
GÉNÈRE exactement 6 sections avec ce format JSON:
{{
  "synthese_personnalite": "Un paragraphe de 4-5 phrases décrivant la personnalité professionnelle globale. Commence par 'Vous êtes...'. Intègre naturellement le moteur principal et le style de travail.",
  "forces_et_talents": "Un paragraphe de 4-5 phrases détaillant les forces de caractère et comment elles se manifestent concrètement.",
  "valeurs_et_qualites": "Un paragraphe de 3-4 phrases sur les valeurs fondamentales et qualités humaines qui guident les choix professionnels.",
  "competences_cles": "Un paragraphe de 3-4 phrases synthétisant les compétences psychosociales OMS et les savoirs-être professionnels en actions concrètes.",
  "environnement_ideal": "Un paragraphe de 3-4 phrases décrivant l'environnement de travail idéal en intégrant les préférences de travail révélées.",
  "axes_de_developpement": "Un paragraphe de 2-3 phrases bienveillant sur les axes de progression, formulés comme opportunités de croissance."
}}
{'''
INSTRUCTIONS SUPPLÉMENTAIRES CRITIQUES:
- NE JAMAIS mentionner : "numérologie", "chemin de vie", "chemin X", "date de naissance", "MBTI", "DISC", "Ennéagramme", ou tout autre terme technique d'analyse
- Présente les observations comme des traits naturels de la personne
- Les tensions identifiées doivent être reformulées positivement comme des "équilibres à trouver"
- Le profil personnel enrichit CHAQUE section de manière cohérente et naturelle
''' if life_path_data else ''}
Réponds UNIQUEMENT avec le JSON, sans texte avant ou après."""

        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        # Parse JSON response
        import json
        # Clean response if needed
        response_text = response.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        narrative = json.loads(response_text.strip())
        return narrative
        
    except Exception as e:
        logger.error(f"AI narrative generation failed: {e}")
        return generate_fallback_narrative(profile, ennea_profile, vertu_data)


async def generate_job_match_narrative(profile: Dict[str, Any], job: Dict[str, Any], score: int, reasons: List[str], risks: List[str]) -> Dict[str, str]:
    """Generate narrative analysis for job matching with ROME info and soft skills."""
    
    if not EMERGENT_LLM_KEY:
        return generate_fallback_job_narrative(profile, job, score, reasons, risks)
    
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"job-match-{uuid.uuid4()}",
            system_message="""Tu es un expert en insertion professionnelle et en orientation, spécialiste reconnu des tests de personnalité (DISC, MBTI, Ennéagramme) et du matching profil-métier.

Tu rédiges comme un conseiller professionnel expérimenté avec une approche bienveillante et pragmatique.
Tu analyses la compatibilité entre un profil et un métier de manière constructive et réaliste.
Tu intègres les informations de la fiche métier ROME et les soft skills essentiels.
Tu ne mentionnes JAMAIS les termes techniques (MBTI, DISC, Ennéagramme, codes types) dans tes réponses - tu traduis en langage courant.
Tu parles directement à la personne en utilisant "vous".
Tu es encourageant même quand la compatibilité n'est pas parfaite, en proposant des pistes d'amélioration concrètes.
Tu écris avec un ton professionnel mais chaleureux."""
        ).with_model("openai", "gpt-5.2")
        
        ennea_profile = ENNEA_TO_PROFILE.get(profile["ennea_dominant"], ENNEA_TO_PROFILE[5])
        
        # Extract soft skills info
        soft_skills = job.get("soft_skills_essentiels", [])
        soft_skills_critiques = [s["nom"] for s in soft_skills if s.get("importance") == "critique"]
        soft_skills_importants = [s["nom"] for s in soft_skills if s.get("importance") == "importante"]
        soft_skills_desc = [f"{s['nom']}: {s['description']}" for s in soft_skills[:4]]
        
        prompt = f"""Génère une analyse de compatibilité métier personnalisée avec fiche ROME et soft skills.

=== FICHE MÉTIER ROME ===
MÉTIER: {job.get('label', job.get('intitule_rome', 'Métier recherché'))}
CODE ROME: {job.get('code_rome', 'N/A')}
INTITULÉ ROME: {job.get('intitule_rome', job.get('label', 'N/A'))}
DÉFINITION: {job.get('definition', 'Non renseigné')}
SECTEUR: {job.get('secteur', '')}
ACCÈS À L'EMPLOI: {job.get('acces_emploi', 'Non renseigné')}

=== SOFT SKILLS ESSENTIELS DU MÉTIER ===
Critiques (indispensables): {', '.join(soft_skills_critiques) if soft_skills_critiques else 'Non renseigné'}
Importants: {', '.join(soft_skills_importants) if soft_skills_importants else 'Non renseigné'}
Détail: {'; '.join(soft_skills_desc) if soft_skills_desc else 'Non renseigné'}

=== VOTRE PROFIL ===
Score de compatibilité: {score}%
Catégorie: {"Très compatible" if score >= 80 else "Compatible" if score >= 60 else "Partiellement compatible" if score >= 40 else "À approfondir"}
Moteur principal: {ennea_profile['moteur']}
Vos compétences fortes: {', '.join(profile['competences_fortes'])}
Vos points de vigilance: {', '.join(profile['vigilances']) if profile['vigilances'] else 'Aucun identifié'}

=== ANALYSE MATCHING ===
Points d'alignement: {', '.join(reasons)}
Points d'attention: {', '.join(risks)}

GÉNÈRE exactement 5 sections avec ce format JSON:
{{
  "fiche_metier": "Un paragraphe de 2-3 phrases présentant le métier de façon attractive et concrète, sans répéter le code ROME.",
  "soft_skills_requis": "Un paragraphe de 3-4 phrases détaillant les soft skills essentiels de ce métier et pourquoi ils sont importants au quotidien.",
  "analyse_compatibilite": "Un paragraphe de 3-4 phrases analysant la compatibilité entre votre profil et les exigences du métier, notamment sur les soft skills.",
  "vos_atouts": "Un paragraphe de 2-3 phrases sur les soft skills que vous possédez déjà et comment ils vous aideront.",
  "axes_progression": "Un paragraphe de 2-3 phrases sur les soft skills à développer et comment y parvenir concrètement."
}}

Réponds UNIQUEMENT avec le JSON."""

        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        import json
        response_text = response.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        narrative = json.loads(response_text.strip())
        return narrative
        
    except Exception as e:
        logger.error(f"AI job match narrative failed: {e}")
        return generate_fallback_job_narrative(profile, job, score, reasons, risks)


def generate_fallback_narrative(profile: Dict[str, Any], ennea_profile: Dict[str, Any], vertu_data: Dict[str, Any], life_path_data: Dict[str, Any] = None) -> Dict[str, str]:
    """Fallback template-based narrative when AI is unavailable."""
    
    energie_text = "Vous puisez votre énergie dans les échanges avec les autres et appréciez le travail collaboratif." if profile["energie"] == "E" else "Vous avez besoin de temps de réflexion personnelle pour donner le meilleur de vous-même."
    
    disc_texts = {
        "D": "Vous êtes naturellement orienté vers l'action et les résultats. Vous savez prendre des décisions rapidement et assumez volontiers des responsabilités.",
        "I": "Vous avez un talent naturel pour communiquer et créer des liens. Votre enthousiasme est contagieux et vous savez motiver les équipes.",
        "S": "Vous êtes un pilier de stabilité dans les équipes. Votre fiabilité et votre sens du soutien aux autres sont vos grandes forces.",
        "C": "Vous êtes reconnu pour votre rigueur et votre précision. Votre capacité d'analyse et votre attention aux détails sont remarquables."
    }
    
    besoin_text = "d'échanges" if profile["energie"] == "E" else "de concentration"
    savoirs_joined = ", ".join(vertu_data.get("savoirs_etre", [])[:2]).lower()
    competences_joined = ", ".join(profile["competences_fortes"][:3])
    vigilances_joined = ", ".join(profile["vigilances"]) if profile["vigilances"] else "maintenir votre équilibre actuel"
    forces_joined = ", ".join(vertu_data.get("forces", [])[:3]).lower()
    valeurs_joined = ", ".join(vertu_data.get("valeurs_schwartz", [])[:3]).lower()
    qualites_joined = ", ".join(vertu_data.get("qualites_humaines", [])[:4]).lower()
    competences_oms_joined = ", ".join(vertu_data.get("competences_oms", [])[:3]).lower()
    
    # Life path additions
    life_path_text = ""
    if life_path_data:
        life_path_text = f" Votre profil personnel révèle une orientation vers {life_path_data.get('label', '').lower()}."
    
    env_addon = ""
    if life_path_data and life_path_data.get("work_preferences"):
        prefs = ", ".join(life_path_data["work_preferences"][:2]).lower()
        env_addon = f" Vous appréciez particulièrement les environnements offrant {prefs}."
    
    return {
        "synthese_personnalite": f"Vous êtes une personne dont le moteur principal est de {ennea_profile['moteur'].lower()}.{life_path_text} {energie_text} {disc_texts.get(profile['disc'], '')}",
        "forces_et_talents": f"Vos forces de caractère dominantes sont : {forces_joined}. Ces forces vous permettent d'exceller dans des situations qui demandent {competences_joined}. Elles constituent le socle de votre contribution professionnelle unique.",
        "valeurs_et_qualites": f"Vos choix professionnels sont guidés par des valeurs profondes : {valeurs_joined}. Ces valeurs se traduisent par des qualités humaines reconnues telles que {qualites_joined}.",
        "competences_cles": f"Vous disposez de compétences psychosociales essentielles : {competences_oms_joined}. Dans le quotidien professionnel, cela se manifeste par votre capacité à {savoirs_joined}.",
        "environnement_ideal": f"Vous vous épanouissez dans des environnements qui valorisent {savoirs_joined}. Un cadre de travail qui respecte votre besoin {besoin_text} sera particulièrement favorable à votre réussite.{env_addon}",
        "axes_de_developpement": f"Comme axes de développement, vous pourriez porter attention à : {vigilances_joined}. Ces points ne sont pas des faiblesses mais des opportunités de croissance professionnelle."
    }


def generate_fallback_job_narrative(profile: Dict[str, Any], job: Dict[str, Any], score: int, reasons: List[str], risks: List[str]) -> Dict[str, str]:
    """Fallback template for job match narrative with specific soft skills to develop."""
    
    job_label = job.get('label', job.get('intitule_rome', 'ce métier'))
    
    if score >= 80:
        compatibility_text = f"Avec un score de {score}%, le métier de {job_label} présente une excellente compatibilité avec votre profil."
    elif score >= 60:
        compatibility_text = f"Avec un score de {score}%, le métier de {job_label} est compatible avec votre profil et mérite d'être exploré."
    else:
        compatibility_text = f"Avec un score de {score}%, le métier de {job_label} pourrait nécessiter quelques ajustements mais reste accessible."
    
    # Calculer les soft skills à développer
    job_soft_skills = job.get('soft_skills_essentiels', [])
    user_competences = set(c.lower() for c in profile.get('competences_fortes', []))
    
    # Identifier les soft skills du métier que l'utilisateur n'a pas encore
    soft_skills_to_develop = []
    for skill in job_soft_skills:
        skill_name = skill.get('nom', skill) if isinstance(skill, dict) else skill
        skill_desc = skill.get('description', '') if isinstance(skill, dict) else ''
        skill_importance = skill.get('importance', 'importante') if isinstance(skill, dict) else 'importante'
        
        # Vérifier si ce skill n'est pas déjà dans les compétences de l'utilisateur
        skill_words = set(skill_name.lower().split())
        if not any(word in user_competences for word in skill_words if len(word) > 4):
            soft_skills_to_develop.append({
                'nom': skill_name,
                'description': skill_desc,
                'importance': skill_importance
            })
    
    # Limiter à 4 soft skills à développer
    soft_skills_to_develop = soft_skills_to_develop[:4]
    
    # Générer le texte pour les axes de progression
    if soft_skills_to_develop:
        skills_names = [s['nom'] for s in soft_skills_to_develop]
        axes_text = f"Pour exceller dans ce métier, nous vous recommandons de développer : {', '.join(skills_names[:3])}. "
        
        # Ajouter des conseils spécifiques selon le premier skill
        if soft_skills_to_develop[0]:
            first_skill = soft_skills_to_develop[0]['nom'].lower()
            if 'créatif' in first_skill or 'créativité' in first_skill:
                axes_text += "Pratiquez des exercices de brainstorming et exposez-vous à différentes sources d'inspiration."
            elif 'communi' in first_skill:
                axes_text += "Exercez-vous à présenter vos idées en public et à adapter votre discours à différents interlocuteurs."
            elif 'rigueur' in first_skill or 'précision' in first_skill:
                axes_text += "Adoptez des méthodes de travail structurées et vérifiez systématiquement votre travail."
            elif 'adapt' in first_skill or 'flexib' in first_skill:
                axes_text += "Confrontez-vous régulièrement à des situations nouvelles et acceptez les changements comme des opportunités."
            elif 'écoute' in first_skill or 'empathie' in first_skill:
                axes_text += "Pratiquez l'écoute active et cherchez à comprendre le point de vue des autres avant de répondre."
            elif 'leader' in first_skill or 'management' in first_skill:
                axes_text += "Cherchez des opportunités de mener des projets et développez votre capacité à motiver une équipe."
            elif 'techni' in first_skill:
                axes_text += "Investissez dans une formation continue et pratiquez régulièrement pour maîtriser les outils du métier."
            else:
                axes_text += "Cherchez des formations ou des mises en situation pratiques pour développer ces compétences progressivement."
    else:
        axes_text = "Votre profil correspond déjà bien aux exigences du métier. Continuez à cultiver vos forces et restez curieux des évolutions du secteur."
    
    return {
        "analyse_compatibilite": f"{compatibility_text} {reasons[0] if reasons else ''} Cette adéquation repose sur vos compétences naturelles et votre style de travail.",
        "fiche_metier": job.get('definition', f"Le métier de {job_label} offre des opportunités dans différents secteurs d'activité."),
        "vos_atouts": f"Vos principaux atouts pour ce métier sont : {', '.join(profile['competences_fortes'][:3])}. Ces compétences sont directement mobilisables et vous permettront de vous démarquer.",
        "axes_progression": axes_text,
        "soft_skills_to_develop": soft_skills_to_develop,  # Liste structurée pour le frontend
        "recommandations": f"Pour maximiser vos chances de réussite, nous vous conseillons de {'développer ' + risks[0].lower() if risks else 'continuer à cultiver vos forces actuelles'}. N'hésitez pas à explorer également des métiers connexes dans le même secteur."
    }


# ============================================================================
# FILIERE - RIASEC - VERTUS MAPPING (pour scoring des filières)
# ============================================================================

FILIERE_PROFILE_MAPPING = {
    "SI": {  # Filière Industrielle
        "riasec_primary": ["R", "I"],
        "riasec_secondary": ["C"],
        "vertus_compatible": ["sagesse", "temperance", "courage"],
        "disc_compatible": ["C", "D"],
        "ennea_compatible": [1, 5, 6, 3],
        "mbti_compatible": ["ISTJ", "ISTP", "INTJ", "INTP", "ESTJ", "ESTP"]
    },
    "SBTP": {  # Filière BTP
        "riasec_primary": ["R"],
        "riasec_secondary": ["C", "E"],
        "vertus_compatible": ["courage", "temperance", "justice"],
        "disc_compatible": ["D", "C"],
        "ennea_compatible": [8, 1, 3, 6],
        "mbti_compatible": ["ISTP", "ESTP", "ISTJ", "ESTJ"]
    },
    "SSS": {  # Filière Santé et Social
        "riasec_primary": ["S", "A"],
        "riasec_secondary": ["I"],
        "vertus_compatible": ["humanite", "transcendance", "justice"],
        "disc_compatible": ["S", "I"],
        "ennea_compatible": [2, 4, 9, 6, 1],  # Ajout du type 4 pour INFP
        "mbti_compatible": ["INFP", "INFJ", "ENFJ", "ENFP", "ISFJ", "ESFJ"]  # NF et SF prioritaires
    },
    "SCV": {  # Filière Commerce et Vente
        "riasec_primary": ["E"],
        "riasec_secondary": ["S", "C"],
        "vertus_compatible": ["courage", "humanite", "justice"],
        "disc_compatible": ["I", "D"],
        "ennea_compatible": [3, 8, 7, 2],  # Type 7 moins prioritaire
        "mbti_compatible": ["ESTP", "ESTJ", "ENTJ", "ESFP", "ESFJ"]  # ENTP retiré - plus adapté à SIN/SC
    },
    "SIN": {  # Filière Informatique et Numérique
        "riasec_primary": ["I", "A"],  # Ajout de A pour les innovateurs
        "riasec_secondary": ["C", "R"],
        "vertus_compatible": ["sagesse", "temperance", "transcendance"],  # Ajout transcendance
        "disc_compatible": ["C", "D"],
        "ennea_compatible": [5, 7, 1, 6],  # Ajout du 7 pour ENTP
        "mbti_compatible": ["INTJ", "INTP", "ENTP", "ENTJ", "ISTJ"]  # ENTP monté en priorité
    },
    "SGAE": {  # Filière Gestion et Administration
        "riasec_primary": ["C"],
        "riasec_secondary": ["E", "I"],
        "vertus_compatible": ["temperance", "justice", "sagesse"],
        "disc_compatible": ["C", "S"],
        "ennea_compatible": [1, 6, 3, 5],
        "mbti_compatible": ["ISTJ", "ESTJ", "ISFJ", "ESFJ", "INTJ"]
    },
    "SC": {  # Filière Communication et Formation
        "riasec_primary": ["S", "A"],
        "riasec_secondary": ["E", "I"],  # Ajout de I pour les introvertis créatifs
        "vertus_compatible": ["humanite", "transcendance", "sagesse"],
        "disc_compatible": ["I", "S"],
        "ennea_compatible": [2, 4, 7, 9],  # Type 7 pour ENTP
        "mbti_compatible": ["ENFJ", "ENFP", "ENTP", "INFJ", "INFP", "ESFJ", "ISFJ"]  # ENTP ajouté
    }
}


def score_filiere(profile: Dict[str, Any], filiere_id: str, user_riasec: Dict[str, Any] = None, vertus_profile: Dict[str, Any] = None) -> float:
    """
    Score de compatibilité avec une filière basé sur le croisement MBTI + RIASEC + Vertus + DISC + Ennéagramme.
    Retourne un score entre 0 et 100.
    
    PONDÉRATION:
    - MBTI: 25% (nouveau)
    - RIASEC: 25%
    - Vertus: 20%
    - DISC: 15%
    - Ennéagramme: 15%
    """
    filiere_mapping = FILIERE_PROFILE_MAPPING.get(filiere_id, {})
    if not filiere_mapping:
        return 50.0  # Score neutre si filière inconnue
    
    score = 0.0
    max_score = 0.0
    
    # 1. Score MBTI (poids: 25%) - NOUVEAU
    max_score += 25
    user_mbti = profile.get("mbti", "")
    mbti_compatible = filiere_mapping.get("mbti_compatible", [])
    
    if user_mbti in mbti_compatible:
        position = mbti_compatible.index(user_mbti)
        # Premier = 25pts, 2ème = 20pts, 3ème = 15pts, 4ème = 12pts, 5ème+ = 10pts
        if position == 0:
            score += 25
        elif position == 1:
            score += 20
        elif position == 2:
            score += 15
        elif position == 3:
            score += 12
        else:
            score += 10
    else:
        # Vérifier compatibilité partielle (même groupe NF, NT, SJ, SP)
        user_group = get_mbti_group_code(user_mbti)
        for compatible_mbti in mbti_compatible[:3]:
            if get_mbti_group_code(compatible_mbti) == user_group:
                score += 8  # Bonus partiel si même groupe
                break
    
    # 2. Score RIASEC (poids: 25%)
    max_score += 25
    if user_riasec:
        user_riasec_scores = user_riasec.get("scores", {})
        user_top_codes = sorted(user_riasec_scores.keys(), key=lambda x: user_riasec_scores.get(x, 0), reverse=True)[:3]
        
        # Match avec codes primaires (15 pts)
        primary_match = sum(1 for code in user_top_codes[:2] if code in filiere_mapping.get("riasec_primary", []))
        score += primary_match * 7.5
        
        # Match avec codes secondaires (10 pts)
        secondary_match = sum(1 for code in user_top_codes if code in filiere_mapping.get("riasec_secondary", []))
        score += min(secondary_match * 3.5, 10)
    else:
        score += 12.5  # Score neutre si pas de RIASEC
    
    # 3. Score Vertus (poids: 20%)
    max_score += 20
    user_dominant_vertu = vertus_profile.get("dominant", "") if vertus_profile else ""
    user_secondary_vertu = vertus_profile.get("secondary", "") if vertus_profile else ""
    vertus_compatible = filiere_mapping.get("vertus_compatible", [])
    
    # Match vertu dominante (14 pts)
    if user_dominant_vertu in vertus_compatible:
        position = vertus_compatible.index(user_dominant_vertu)
        score += 14 - (position * 4)  # 14, 10, 6 pts selon position
    
    # Match vertu secondaire (6 pts)
    if user_secondary_vertu in vertus_compatible:
        score += 6
    
    # 4. Score DISC (poids: 15%)
    max_score += 15
    user_disc = profile.get("disc", "")
    if user_disc in filiere_mapping.get("disc_compatible", []):
        position = filiere_mapping.get("disc_compatible", []).index(user_disc)
        score += 15 - (position * 4)  # 15, 11, 7, 3 pts selon position
    else:
        score += 3  # Score minimal si DISC non compatible
    
    # 5. Score Ennéagramme (poids: 15%)
    max_score += 15
    user_ennea = profile.get("ennea_dominant", 9)
    user_ennea_secondary = profile.get("ennea_runner_up", 9)
    ennea_compatible = filiere_mapping.get("ennea_compatible", [])
    
    if user_ennea in ennea_compatible:
        position = ennea_compatible.index(user_ennea)
        score += 15 - (position * 3)  # 15, 12, 9, 6 pts selon position
    elif user_ennea_secondary in ennea_compatible:
        score += 6  # Bonus si secondaire match
    else:
        score += 3  # Score minimal
    
    # Normaliser sur 100
    final_score = (score / max_score) * 100 if max_score > 0 else 50
    return round(final_score, 1)


def get_mbti_group_code(mbti: str) -> str:
    """Retourne le code du groupe MBTI (NT, NF, SJ, SP)."""
    if len(mbti) < 4:
        return ""
    if mbti[1] == "N" and mbti[2] == "T":
        return "NT"
    elif mbti[1] == "N" and mbti[2] == "F":
        return "NF"
    elif mbti[1] == "S" and mbti[3] == "J":
        return "SJ"
    elif mbti[1] == "S" and mbti[3] == "P":
        return "SP"
    return ""


# ============================================================================
# STATIC DATA - FILIERES & METIERS
# ============================================================================

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

# ============================================================================
# NIVEAU D'ÉTUDES PAR MÉTIER
# 0 = Sans diplôme/CAP, 3 = Bac, 5 = Bac+2, 6 = Bac+3, 7 = Bac+5, 8 = Bac+8
# ============================================================================
METIER_NIVEAU_ETUDES = {
    # Filière Industrielle (SI)
    "M001": 7,  # Ingénieur en mécanique - Bac+5
    "M002": 5,  # Technicien de maintenance industrielle - Bac+2
    "M003": 5,  # Automaticien - Bac+2
    
    # Filière BTP (SBTP)
    "M004": 5,  # Chef de chantier - Bac+2 + expérience
    "M005": 3,  # Électricien bâtiment - CAP/Bac Pro
    "M038": 3,  # Plombier / Plombière - CAP
    "M053": 3,  # Maçon / Maçonne - CAP
    "M054": 3,  # Chauffagiste - CAP
    "M039": 7,  # Architecte - Bac+5
    
    # Filière Santé et Social (SSS)
    "M006": 6,  # Infirmier(e) - Bac+3
    "M007": 6,  # Éducateur spécialisé - Bac+3
    "M008": 6,  # Conseiller en insertion professionnelle - Bac+3
    "M017": 3,  # Aide-soignant(e) - Formation 10 mois
    "M028": 7,  # Psychologue - Bac+5 (Master obligatoire)
    "M029": 6,  # Médiateur(rice) social(e) - Bac+3
    "M034": 8,  # Médecin généraliste - Bac+9
    "M035": 7,  # Sage-femme - Bac+5
    "M036": 6,  # Kinésithérapeute - Bac+4
    "M037": 7,  # Pharmacien(ne) - Bac+6
    "M052": 7,  # Orthophoniste - Bac+5
    
    # Filière Commerce et Vente (SCV)
    "M009": 5,  # Commercial / Attaché commercial - Bac+2
    "M010": 7,  # Responsable marketing - Bac+5
    "M018": 3,  # Vendeur conseil en magasin - Bac
    
    # Filière Informatique et Numérique (SIN)
    "M011": 5,  # Développeur web / fullstack - Bac+2 à Bac+5
    "M012": 5,  # Administrateur systèmes et réseaux - Bac+2
    "M013": 6,  # UX/UI Designer - Bac+3
    "M019": 5,  # Technicien support informatique - Bac+2
    "M040": 7,  # Analyste Cybersécurité - Bac+5
    "M041": 7,  # Chef de projet digital - Bac+5
    
    # Filière Gestion et Administration (SGAE)
    "M014": 5,  # Comptable - Bac+2
    "M015": 7,  # Responsable RH / Chargé(e) RH - Bac+5
    "M016": 7,  # Contrôleur de gestion - Bac+5
    "M020": 5,  # Assistant(e) de direction - Bac+2
    "M042": 7,  # Analyste financier - Bac+5
    "M043": 7,  # Auditeur / Auditrice - Bac+5
    "M044": 5,  # Assistant(e) RH - Bac+2
    "M049": 7,  # Notaire - Bac+7
    
    # Formation et Communication (SC)
    "M024": 5,  # Chargé(e) de communication - Bac+2
    "M025": 6,  # Formateur / Formatrice - Bac+3
    "M026": 6,  # Coach professionnel / Coach de vie - Bac+3
    "M027": 6,  # Journaliste / Rédacteur(rice) - Bac+3
    "M030": 5,  # Community Manager - Bac+2
    "M031": 6,  # Enseignant(e) / Professeur(e) - Bac+3 à Bac+5
    "M032": 5,  # Animateur(rice) socioculturel(le) - Bac+2
    "M033": 6,  # Chargé(e) de recrutement - Bac+3
    "M051": 5,  # Graphiste - Bac+2
    
    # Logistique et Transport
    "M021": 0,  # Cariste - Sans diplôme/CACES
    "M022": 0,  # Magasinier / Préparateur de commandes - Sans diplôme
    "M023": 0,  # Agent de quai / Manutentionnaire - Sans diplôme
    "M045": 3,  # Chauffeur poids lourd - Permis C
    "M046": 5,  # Responsable logistique - Bac+2 à Bac+5
    
    # Hôtellerie/Restauration
    "M047": 3,  # Cuisinier / Cuisinière - CAP
    "M048": 0,  # Serveur / Serveuse - Sans diplôme
    
    # Recherche
    "M050": 8,  # Chercheur / Chercheuse - Bac+8
}

def get_metier_niveau(metier_id: str) -> int:
    """Retourne le niveau d'études requis pour un métier (défaut: 5 = Bac+2)"""
    return METIER_NIVEAU_ETUDES.get(metier_id, 5)

def filter_jobs_by_education(jobs: List[Dict], user_level: str) -> List[Dict]:
    """
    Filtre et priorise les métiers selon le niveau d'études de l'utilisateur.
    Les métiers du niveau exact ou inférieur sont priorisés.
    """
    if not user_level:
        return jobs
    
    try:
        user_level_int = int(user_level)
    except (ValueError, TypeError):
        return jobs
    
    # Séparer les métiers accessibles et ceux nécessitant plus de formation
    accessible = []
    stretch = []  # Métiers nécessitant 1 niveau de plus (objectif réaliste)
    aspirational = []  # Métiers nécessitant beaucoup plus de formation
    
    for job in jobs:
        job_id = job.get("job_id", job.get("id", ""))
        job_level = get_metier_niveau(job_id)
        
        # Ajouter le niveau au job pour l'affichage
        job_with_level = {**job, "niveau_etudes_requis": job_level}
        
        level_diff = job_level - user_level_int
        
        if level_diff <= 0:
            # Accessible avec le niveau actuel
            accessible.append(job_with_level)
        elif level_diff <= 2:
            # Stretch goal - atteignable avec formation complémentaire
            stretch.append(job_with_level)
        else:
            # Aspirationnel - nécessite formation longue
            aspirational.append(job_with_level)
    
    # Retourner les métiers ordonnés: accessibles d'abord, puis stretch, puis aspirationnels
    return accessible + stretch + aspirational



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


# ============================================================================
# SCORING ENGINE
# ============================================================================

DISC_ADJACENT = {
    "D": {"I", "C"},
    "I": {"D", "S"},
    "S": {"I", "C"},
    "C": {"D", "S"},
}

# ============================================================================
# RIASEC MODEL (Holland Codes) - Intérêts professionnels
# ============================================================================
# R = Réaliste (manuel, technique, pratique)
# I = Investigateur (scientifique, analytique, curieux)
# A = Artistique (créatif, expressif, original)
# S = Social (aide, enseigne, accompagne)
# E = Entreprenant (leader, persuasif, ambitieux)
# C = Conventionnel (organisé, méthodique, précis)

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

# Hexagone RIASEC - Types adjacents (corrélation positive) et opposés (corrélation négative)
RIASEC_ADJACENT = {
    "R": ["I", "C"],  # Adjacent: Investigateur, Conventionnel
    "I": ["R", "A"],  # Adjacent: Réaliste, Artistique  
    "A": ["I", "S"],  # Adjacent: Investigateur, Social
    "S": ["A", "E"],  # Adjacent: Artistique, Entreprenant
    "E": ["S", "C"],  # Adjacent: Social, Conventionnel
    "C": ["E", "R"],  # Adjacent: Entreprenant, Réaliste
}

RIASEC_OPPOSITE = {
    "R": "S",  # Réaliste ↔ Social
    "I": "E",  # Investigateur ↔ Entreprenant
    "A": "C",  # Artistique ↔ Conventionnel
    "S": "R",
    "E": "I",
    "C": "A"
}

# Mapping ROME Code → RIASEC (basé sur le référentiel France Travail)
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

# ============================================================================
# MAPPING MBTI → VERTU PAR DÉFAUT (fallback quand questions VV non répondues)
# ============================================================================
# Basé sur les caractéristiques psychologiques de chaque type MBTI
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


# ============================================================================
# ARCHÉOLOGIE DES COMPÉTENCES - Système de hiérarchisation
# Basé sur Seligman & Peterson (Vertus) + Schwartz (Valeurs) + OMS (Compétences)
# ============================================================================
# Hiérarchie: VERTU (socle) → Forces → Valeurs → Qualités → Compétences → Savoirs-être

# ============================================================================
# TABLEAU CK - Données enrichies de l'Archéologie des Compétences
# Source: TABLEAU CK.ods - Hiérarchie complète:
# Vertu → Sous-vertus → Valeurs Universelles → Qualités Humaines →
# Compétences Sociales → Compétences Pro Transférables → Métiers
# ============================================================================
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

# Mapping inverse : Métier → Vertu principale
# Utilisé pour le parcours "Je cherche mon job" (droite → gauche)
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

def get_vertu_for_metier(metier_id: str) -> str:
    """Retourne la vertu principale associée à un métier."""
    return METIER_TO_VERTU.get(metier_id, "temperance")  # Défaut: tempérance

def calculate_vertu_coherence(user_vertu: str, metier_id: str) -> float:
    """
    Calcule la cohérence entre la vertu de l'utilisateur et celle du métier.
    Score de 0.0 à 1.0
    """
    metier_vertu = get_vertu_for_metier(metier_id)
    
    if user_vertu == metier_vertu:
        return 1.0  # Parfaite cohérence
    
    # Vertus proches (affinités naturelles)
    VERTU_AFFINITES = {
        "sagesse": ["transcendance", "justice"],
        "courage": ["justice", "temperance"],
        "humanite": ["transcendance", "justice"],
        "justice": ["courage", "sagesse", "temperance"],
        "temperance": ["justice", "sagesse"],
        "transcendance": ["humanite", "sagesse"],
    }
    
    if metier_vertu in VERTU_AFFINITES.get(user_vertu, []):
        return 0.7  # Bonne affinité
    
    return 0.3  # Faible cohérence

def check_profile_coherence_for_job(profile: Dict, metier: Dict, user_riasec: Dict, vertus_profile: Dict) -> Dict:
    """
    Parcours "Je cherche mon job" : Métier → Vertus → Validation du profil
    Retourne un diagnostic de cohérence.
    """
    metier_id = metier.get("id", "")
    metier_vertu = get_vertu_for_metier(metier_id)
    archeologie = ARCHEOLOGIE_COMPETENCES.get(metier_vertu, {})
    
    user_vertu = vertus_profile.get("dominant", "temperance")
    user_mbti = profile.get("mbti", "")
    user_disc = profile.get("disc", "")
    user_ennea = profile.get("ennea_dominant", 5)
    
    coherence_scores = {
        "vertu": 1.0 if user_vertu == metier_vertu else (0.7 if metier_vertu in ARCHEOLOGIE_COMPETENCES.get(user_vertu, {}).get("filieres_naturelles", []) else 0.3),
        "mbti": 1.0 if user_mbti in archeologie.get("mbti_coherents", []) else 0.4,
        "disc": 1.0 if user_disc in archeologie.get("disc_coherents", []) else 0.5,
        "ennea": 1.0 if user_ennea in archeologie.get("ennea_coherents", []) else 0.5,
    }
    
    # Score global pondéré
    global_score = (
        coherence_scores["vertu"] * 0.40 +
        coherence_scores["mbti"] * 0.30 +
        coherence_scores["disc"] * 0.15 +
        coherence_scores["ennea"] * 0.15
    )
    
    return {
        "metier_vertu": metier_vertu,
        "user_vertu": user_vertu,
        "coherence_scores": coherence_scores,
        "global_coherence": round(global_score * 100),
        "is_coherent": global_score >= 0.6,
        "qualites_requises": archeologie.get("qualites", []),
        "savoirs_etre_requis": archeologie.get("savoirs_etre_pro", []),
    }


def generate_job_fiche_with_archeology(metier: Dict, profile: Dict = None, vertus_profile: Dict = None) -> Dict:
    """
    Génère une fiche métier enrichie avec la chaîne complète d'archéologie des compétences.
    
    Chaîne : Vertu → Valeurs → Qualités → Savoirs-être → Savoir-faire (Métier)
    
    Cette fonction est utilisée pour :
    1. Afficher la fiche métier avec contexte de l'archéologie
    2. Calculer le score de compatibilité basé sur l'alignement de la chaîne
    """
    metier_id = metier.get("id", "")
    metier_vertu = get_vertu_for_metier(metier_id)
    archeologie = ARCHEOLOGIE_COMPETENCES.get(metier_vertu, {})
    
    # Soft skills du métier (savoir-faire comportementaux)
    soft_skills_metier = [s["nom"] for s in metier.get("soft_skills_essentiels", [])]
    competences_metier = metier.get("competences_requises", [])
    
    # Construire la chaîne d'archéologie
    ck_data = TABLEAU_CK.get(metier_vertu, {})
    chaine_archeologie = {
        "niveau_1_vertu": {
            "nom": metier_vertu.capitalize(),
            "sous_vertus": ck_data.get("sous_vertus", []),
            "description": f"Socle fondamental - {metier_vertu}",
            "forces_caractere": archeologie.get("forces", [])
        },
        "niveau_2_valeurs": {
            "valeurs_schwartz": archeologie.get("valeurs_schwartz", []),
            "valeurs_universelles": ck_data.get("valeurs_universelles", []),
            "description": "Valeurs qui guident l'action"
        },
        "niveau_3_qualites": {
            "qualites": archeologie.get("qualites", []),
            "qualites_humaines_ck": ck_data.get("qualites_humaines", []),
            "description": "Qualités personnelles mobilisées"
        },
        "niveau_4_savoirs_etre": {
            "savoirs_etre_pro": archeologie.get("savoirs_etre_pro", []),
            "competences_sociales": ck_data.get("competences_sociales", []),
            "competences_pro_transferables": ck_data.get("competences_pro_transferables", []),
            "description": "Comportements professionnels attendus"
        },
        "niveau_5_savoir_faire": {
            "competences_techniques": competences_metier,
            "soft_skills": soft_skills_metier,
            "description": "Compétences opérationnelles du métier"
        }
    }
    
    # Calculer le score de cohérence entre les savoirs-être de l'archéologie et ceux du métier
    savoirs_etre_arch = set([s.lower() for s in archeologie.get("savoirs_etre_pro", [])])
    savoirs_etre_metier = set([s.lower() for s in soft_skills_metier])
    qualites_arch = set([q.lower() for q in archeologie.get("qualites", [])])
    
    # Intersection entre archéologie et métier
    coherence_savoirs_etre = len(savoirs_etre_arch.intersection(savoirs_etre_metier)) / max(len(savoirs_etre_metier), 1)
    coherence_qualites = len(qualites_arch.intersection(savoirs_etre_metier)) / max(len(savoirs_etre_metier), 1)
    
    # Score de cohérence interne de la fiche (archéologie ↔ métier)
    coherence_interne = (coherence_savoirs_etre * 0.6) + (coherence_qualites * 0.4)
    
    # Si profil utilisateur fourni, calculer la compatibilité
    compatibilite_utilisateur = None
    if profile and vertus_profile:
        user_vertu = vertus_profile.get("dominant", "temperance")
        user_qualites = vertus_profile.get("qualites", [])
        
        # Vérifier alignement Vertu
        alignement_vertu = 1.0 if user_vertu == metier_vertu else (0.7 if metier_vertu in ARCHEOLOGIE_COMPETENCES.get(user_vertu, {}).get("filieres_naturelles", []) else 0.3)
        
        # Vérifier alignement Qualités
        user_qualites_set = set([q.lower() for q in user_qualites])
        alignement_qualites = len(qualites_arch.intersection(user_qualites_set)) / max(len(qualites_arch), 1)
        
        # Vérifier alignement MBTI
        user_mbti = profile.get("mbti", "")
        mbti_coherents = archeologie.get("mbti_coherents", [])
        alignement_mbti = 1.0 if user_mbti in mbti_coherents else 0.4
        
        # Score global de compatibilité
        score_compatibilite = (
            alignement_vertu * 0.40 +      # Vertu = socle
            alignement_qualites * 0.25 +   # Qualités
            alignement_mbti * 0.25 +       # MBTI
            coherence_interne * 0.10       # Cohérence interne fiche
        )
        
        compatibilite_utilisateur = {
            "score_global": round(score_compatibilite * 100),
            "alignement_vertu": round(alignement_vertu * 100),
            "alignement_qualites": round(alignement_qualites * 100),
            "alignement_mbti": round(alignement_mbti * 100),
            "user_vertu": user_vertu,
            "metier_vertu": metier_vertu,
            "est_coherent": score_compatibilite >= 0.6
        }
    
    return {
        "metier": {
            "id": metier_id,
            "label": metier.get("label", ""),
            "definition": metier.get("definition", ""),
            "filiere": metier.get("filiere", ""),
            "secteur": metier.get("secteur", ""),
            "acces_emploi": metier.get("acces_emploi", ""),
        },
        "archeologie": chaine_archeologie,
        "vertu_associee": metier_vertu,
        "coherence_interne": round(coherence_interne * 100),
        "compatibilite_utilisateur": compatibilite_utilisateur,
        "mbti_compatibles": archeologie.get("mbti_coherents", []),
        "disc_compatibles": archeologie.get("disc_coherents", []),
        "ennea_compatibles": archeologie.get("ennea_coherents", []),
    }


def generate_savoirs_etre_from_archeology(metier_vertu: str, metier_soft_skills: List[str] = None) -> List[Dict]:
    """
    Génère les savoirs-être pour un métier en se basant sur l'archéologie des compétences.
    
    Les savoirs-être sont dérivés de :
    1. La vertu du métier → Qualités → Savoirs-être pro
    2. Les soft skills spécifiques du métier (si fournis)
    
    Utilisé par l'IA pour générer des fiches cohérentes.
    """
    archeologie = ARCHEOLOGIE_COMPETENCES.get(metier_vertu, {})
    
    # Savoirs-être de base depuis l'archéologie
    savoirs_etre_base = archeologie.get("savoirs_etre_pro", [])
    qualites = archeologie.get("qualites", [])
    forces = archeologie.get("forces", [])
    
    # Construire la liste enrichie
    savoirs_etre_enrichis = []
    
    for se in savoirs_etre_base:
        # Trouver la qualité source
        qualite_source = next((q for q in qualites if q.lower() in se.lower() or se.lower() in q.lower()), qualites[0] if qualites else "Non défini")
        
        savoirs_etre_enrichis.append({
            "nom": se,
            "source_qualite": qualite_source,
            "source_vertu": metier_vertu,
            "importance": "critique" if se in savoirs_etre_base[:2] else "importante"
        })
    
    # Ajouter les soft skills du métier s'ils ne sont pas déjà présents
    if metier_soft_skills:
        existants = [s["nom"].lower() for s in savoirs_etre_enrichis]
        for skill in metier_soft_skills:
            if skill.lower() not in existants:
                savoirs_etre_enrichis.append({
                    "nom": skill,
                    "source_qualite": "Compétence métier",
                    "source_vertu": metier_vertu,
                    "importance": "importante"
                })
    
    return savoirs_etre_enrichis



def calculate_vertus_profile(answers: Dict[str, Any], mbti_type: str = None) -> Dict[str, Any]:
    """
    Calcule le profil de vertus basé sur les questions vv1-vv6.
    Retourne les vertus dominantes et les valeurs/qualités associées.
    
    Hiérarchie: Vertus → Valeurs → Qualités → Savoir-être → Compétences
    """
    vertus_scores = {
        "sagesse": 0,
        "courage": 0,
        "humanite": 0,
        "justice": 0,
        "temperance": 0,
        "transcendance": 0
    }
    
    valeurs_scores = {
        "autonomie": 0,
        "bienveillance": 0,
        "reussite": 0,
        "securite": 0
    }
    
    qualites_scores = {
        "creativite": 0,
        "generosite": 0
    }
    
    savoirs_etre_scores = {
        "initiative": 0,
        "ecoute": 0,
        "rigueur": 0,
        "leadership": 0
    }
    
    # ============================================================================
    # PARTIE 1: Questions directes sur les vertus (vv1, vv2, vv3) - Poids élevé
    # ============================================================================
    
    # vv1: Sagesse vs Courage
    vv1 = answers.get("vv1", "")
    if vv1 in vertus_scores:
        vertus_scores[vv1] += 5
    
    # vv2: Humanité vs Justice
    vv2 = answers.get("vv2", "")
    if vv2 in vertus_scores:
        vertus_scores[vv2] += 5
    
    # vv3: Tempérance vs Transcendance
    vv3 = answers.get("vv3", "")
    if vv3 in vertus_scores:
        vertus_scores[vv3] += 5
    
    # ============================================================================
    # PARTIE 2: Classement des valeurs (vv4) - Schwartz
    # ============================================================================
    vv4 = answers.get("vv4", "")
    if vv4 and isinstance(vv4, str) and "," in vv4:
        ranking_weights = [5, 3, 2, 1]
        ranked_values = [v.strip().lower() for v in vv4.split(",")]
        for idx, val in enumerate(ranked_values[:4]):
            if val in valeurs_scores and idx < len(ranking_weights):
                valeurs_scores[val] += ranking_weights[idx]
                
                # Mapper les valeurs vers les vertus
                valeur_to_vertu = {
                    "autonomie": "sagesse",
                    "bienveillance": "humanite",
                    "reussite": "courage",
                    "securite": "temperance"
                }
                if val in valeur_to_vertu:
                    vertus_scores[valeur_to_vertu[val]] += ranking_weights[idx] * 0.5
    
    # ============================================================================
    # PARTIE 3: Qualités humaines (vv5)
    # ============================================================================
    vv5 = answers.get("vv5", "")
    if vv5 in qualites_scores:
        qualites_scores[vv5] += 5
        
        # Mapper les qualités vers les vertus
        qualite_to_vertu = {
            "creativite": "sagesse",
            "generosite": "humanite"
        }
        if vv5 in qualite_to_vertu:
            vertus_scores[qualite_to_vertu[vv5]] += 3
    
    # ============================================================================
    # PARTIE 4: Savoir-être professionnels (vv6)
    # ============================================================================
    vv6 = answers.get("vv6", "")
    if vv6 and isinstance(vv6, str) and "," in vv6:
        ranking_weights = [5, 3, 2, 1]
        ranked_savoirs = [s.strip().lower() for s in vv6.split(",")]
        for idx, savoir in enumerate(ranked_savoirs[:4]):
            if savoir in savoirs_etre_scores and idx < len(ranking_weights):
                savoirs_etre_scores[savoir] += ranking_weights[idx]
                
                # Mapper les savoir-être vers les vertus
                savoir_to_vertu = {
                    "initiative": "courage",
                    "ecoute": "humanite",
                    "rigueur": "temperance",
                    "leadership": "justice"
                }
                if savoir in savoir_to_vertu:
                    vertus_scores[savoir_to_vertu[savoir]] += ranking_weights[idx] * 0.5
    
    # ============================================================================
    # DÉTERMINATION DE LA VERTU DOMINANTE
    # ============================================================================
    
    # Vérifier si des réponses VV ont été fournies (score total > 0)
    total_score = sum(vertus_scores.values())
    
    logging.info(f"[VERTUS] Scores calculés: {vertus_scores}")
    logging.info(f"[VERTUS] Score total VV: {total_score}")
    
    if total_score > 0:
        # Cas normal: utiliser les scores calculés
        sorted_vertus = sorted(vertus_scores.items(), key=lambda x: x[1], reverse=True)
        dominant_vertu = sorted_vertus[0][0]
        secondary_vertu = sorted_vertus[1][0]
        logging.info(f"[VERTUS] Source: Réponses VV directes")
    else:
        # FALLBACK: Aucune réponse VV → utiliser le mapping MBTI
        if mbti_type and mbti_type.upper() in MBTI_TO_VERTU_FALLBACK:
            dominant_vertu, secondary_vertu = MBTI_TO_VERTU_FALLBACK[mbti_type.upper()]
            logging.info(f"[VERTUS] Source: Fallback MBTI ({mbti_type}) → {dominant_vertu}, {secondary_vertu}")
        else:
            # Fallback ultime si pas de MBTI non plus
            dominant_vertu = "courage"
            secondary_vertu = "humanite"
            logging.warning(f"[VERTUS] Source: Défaut (aucune donnée VV ni MBTI)")
    
    logging.info(f"[VERTUS] RÉSULTAT - Dominant: {dominant_vertu}, Secondaire: {secondary_vertu}")
    
    # Normaliser les scores (0-100)
    max_score = max(vertus_scores.values()) if max(vertus_scores.values()) > 0 else 1
    normalized_vertus = {k: round((v / max_score) * 100) for k, v in vertus_scores.items()}
    
    return {
        "vertus_scores": normalized_vertus,
        "vertus_raw": vertus_scores,
        "dominant": dominant_vertu,
        "secondary": secondary_vertu,
        "dominant_name": VERTUS.get(dominant_vertu, {}).get("name", dominant_vertu.capitalize()),
        "secondary_name": VERTUS.get(secondary_vertu, {}).get("name", secondary_vertu.capitalize()),
        "valeurs_scores": valeurs_scores,
        "qualites_scores": qualites_scores,
        "savoirs_etre_scores": savoirs_etre_scores,
        "qualites_dominantes": VERTUS.get(dominant_vertu, {}).get("qualites_humaines", [])[:4],
        "savoirs_etre_dominants": VERTUS.get(dominant_vertu, {}).get("savoirs_etre", [])[:3],
        "competences_oms": VERTUS.get(dominant_vertu, {}).get("competences_oms", [])[:3]
    }


def calculate_riasec_profile(answers: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calcule le profil RIASEC basé sur les réponses au questionnaire et le profil MBTI/DISC.
    Utilise les correspondances MBTI→RIASEC et DISC→RIASEC pour inférer les intérêts.
    NOUVEAU: Intègre les 8 questions RIASEC directes (r1-r8) pour un profil plus précis.
    """
    riasec_scores = {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0}
    
    # ============================================================================
    # PARTIE 1: Réponses DIRECTES aux questions RIASEC (r1-r8) - Poids élevé (5 pts)
    # Ces réponses sont les plus fiables car directement liées aux intérêts
    # ============================================================================
    
    # Questions à 2 choix (r1, r2, r3, r5, r7) - Poids de 5 points
    direct_questions = ["r1", "r2", "r3", "r5", "r7"]
    for q_id in direct_questions:
        answer = answers.get(q_id, "")
        if answer in riasec_scores:
            riasec_scores[answer] += 5
    
    # Questions de classement (r4, r6, r8) - Poids selon le rang
    # Rang 1 = 5 pts, Rang 2 = 3 pts, Rang 3 = 2 pts, Rang 4 = 1 pt
    ranking_questions = ["r4", "r6", "r8"]
    ranking_weights = [5, 3, 2, 1]
    
    for q_id in ranking_questions:
        answer = answers.get(q_id, "")
        if answer and isinstance(answer, str):
            # Format: "R,A,S,E" (ordre de préférence)
            ranked_codes = [c.strip().upper() for c in answer.split(",")]
            for idx, code in enumerate(ranked_codes[:4]):
                if code in riasec_scores and idx < len(ranking_weights):
                    riasec_scores[code] += ranking_weights[idx]
    
    # ============================================================================
    # PARTIE 2: Inférence depuis MBTI (poids moyen: 3 pts)
    # ============================================================================
    mbti = profile.get("mbti", "")
    for riasec_code, riasec_data in RIASEC_DESCRIPTIONS.items():
        if mbti in riasec_data.get("mbti_affinite", []):
            riasec_scores[riasec_code] += 3  # Fort poids pour correspondance directe
    
    # ============================================================================
    # PARTIE 3: Inférence depuis DISC (poids moyen: 2 pts)
    # ============================================================================
    disc = profile.get("disc", "S")
    for riasec_code, riasec_data in RIASEC_DESCRIPTIONS.items():
        if disc in riasec_data.get("disc_affinite", []):
            riasec_scores[riasec_code] += 2
    
    # ============================================================================
    # PARTIE 4: Inférence depuis Ennéagramme (poids moyen: 2 pts dominant, 1 pt secondaire)
    # ============================================================================
    ennea_dom = profile.get("ennea_dominant", 9)
    ennea_sec = profile.get("ennea_runner_up", 9)
    for riasec_code, riasec_data in RIASEC_DESCRIPTIONS.items():
        if ennea_dom in riasec_data.get("ennea_affinite", []):
            riasec_scores[riasec_code] += 2
        if ennea_sec in riasec_data.get("ennea_affinite", []):
            riasec_scores[riasec_code] += 1
    
    # ============================================================================
    # PARTIE 5: Ajustements basés sur les dimensions MBTI (poids faible: 2 pts)
    # ============================================================================
    # E/I influence sur E(ntreprenant) et I(nvestigateur)
    if profile.get("energie") == "E":
        riasec_scores["E"] += 2
        riasec_scores["S"] += 1
    else:
        riasec_scores["I"] += 2
        riasec_scores["A"] += 1
    
    # S/N influence sur R(éaliste) et A(rtistique)
    if profile.get("perception") == "S":
        riasec_scores["R"] += 2
        riasec_scores["C"] += 1
    else:
        riasec_scores["A"] += 2
        riasec_scores["I"] += 1
    
    # T/F influence sur I(nvestigateur) et S(ocial)
    if profile.get("decision") == "T":
        riasec_scores["I"] += 2
        riasec_scores["R"] += 1
    else:
        riasec_scores["S"] += 2
        riasec_scores["A"] += 1
    
    # J/P influence sur C(onventionnel) et A(rtistique)
    if profile.get("structure") == "J":
        riasec_scores["C"] += 2
        riasec_scores["E"] += 1
    else:
        riasec_scores["A"] += 2
        riasec_scores["R"] += 1
    
    # Calculer les scores normalisés (0-100)
    max_score = max(riasec_scores.values()) if riasec_scores.values() else 1
    normalized_scores = {k: round((v / max_score) * 100) for k, v in riasec_scores.items()}
    
    # Trier par score décroissant pour obtenir le code RIASEC
    sorted_riasec = sorted(riasec_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Code RIASEC principal (3 lettres) et secondaire (2 lettres)
    riasec_code_3 = "".join([x[0] for x in sorted_riasec[:3]])
    riasec_code_2 = "".join([x[0] for x in sorted_riasec[:2]])
    riasec_major = sorted_riasec[0][0]
    riasec_minor = sorted_riasec[1][0]
    
    return {
        "scores": normalized_scores,
        "raw_scores": riasec_scores,
        "code_3": riasec_code_3,
        "code_2": riasec_code_2,
        "major": riasec_major,
        "minor": riasec_minor,
        "major_name": RIASEC_DESCRIPTIONS[riasec_major]["name"],
        "minor_name": RIASEC_DESCRIPTIONS[riasec_minor]["name"],
        "major_description": RIASEC_DESCRIPTIONS[riasec_major]["description"],
        "traits": RIASEC_DESCRIPTIONS[riasec_major]["traits"][:3] + RIASEC_DESCRIPTIONS[riasec_minor]["traits"][:2],
        "environnements_preferes": RIASEC_DESCRIPTIONS[riasec_major]["environnements"][:2]
    }


def riasec_congruence(user_riasec: str, job_riasec: str) -> float:
    """
    Calcule la congruence RIASEC entre le profil utilisateur et le métier.
    Basé sur le modèle hexagonal de Holland.
    
    Returns: Score de 0 à 1
    """
    if not user_riasec or not job_riasec:
        return 0.5  # Score neutre si pas de données
    
    user_major = user_riasec[0] if len(user_riasec) > 0 else ""
    user_minor = user_riasec[1] if len(user_riasec) > 1 else ""
    job_major = job_riasec[0] if len(job_riasec) > 0 else ""
    job_minor = job_riasec[1] if len(job_riasec) > 1 else ""
    
    score = 0.0
    
    # Correspondance exacte majeur-majeur (très forte) = 0.55
    if user_major == job_major:
        score += 0.55
    # Type adjacent au majeur = 0.4
    elif job_major in RIASEC_ADJACENT.get(user_major, []):
        score += 0.4
    # Type opposé (pénalité légère) = 0.15
    elif job_major == RIASEC_OPPOSITE.get(user_major, ""):
        score += 0.15
    else:
        score += 0.25
    
    # Correspondance mineur
    if user_minor == job_minor:
        score += 0.35
    elif user_minor == job_major or user_major == job_minor:
        score += 0.3  # Cross-match valorisé
    elif job_minor in RIASEC_ADJACENT.get(user_minor, []):
        score += 0.2
    else:
        score += 0.1
    
    # Bonus si le code complet est identique ou inversé
    if user_riasec == job_riasec:
        score += 0.1
    elif len(user_riasec) >= 2 and len(job_riasec) >= 2:
        if user_riasec[0] == job_riasec[1] and user_riasec[1] == job_riasec[0]:
            score += 0.05  # Code inversé (AI vs IA) - encore compatible
    
    return min(score, 1.0)


WEIGHTS = {
    # ARCHÉOLOGIE DES COMPÉTENCES - La Vertu est le socle principal
    "archeologie": 35,     # Vertu → Compétences (SOCLE PRINCIPAL)
    "mbti": 25,            # Personnalité MBTI (doit être cohérent avec Vertu)
    "riasec": 15,          # Intérêts professionnels (Holland)
    "motivation": 8,       # Ennéagramme - motivation profonde
    "disc": 7,             # Style comportemental DISC
    "environment": 5,      # Environnement de travail
    "skills": 3,           # Compétences directes
    "constraints": 2,      # Contraintes
    # Total = 100
}

# MBTI Compatibility - Types similaires par fonction dominante et mode de fonctionnement
# Correction: Les types Feeling (F) ne sont PAS similaires aux types Thinking (T)
MBTI_SIMILAR = {
    # Groupes basés sur les 2 lettres centrales (S/N et T/F) qui définissent le "core"
    # NF - Les Idéalistes (Intuition + Feeling) - orientés relations et valeurs
    "ENFP": ["INFP", "ENFJ", "INFJ"],          # Tous NF
    "INFP": ["ENFP", "INFJ", "ENFJ"],          # Tous NF
    "ENFJ": ["INFJ", "ENFP", "INFP"],          # Tous NF
    "INFJ": ["ENFJ", "INFP", "ENFP"],          # Tous NF
    # NT - Les Rationnels (Intuition + Thinking) - orientés analyse et stratégie
    "ENTP": ["INTP", "ENTJ", "INTJ"],          # Tous NT
    "INTP": ["ENTP", "INTJ", "ENTJ"],          # Tous NT
    "ENTJ": ["INTJ", "ENTP", "INTP"],          # Tous NT
    "INTJ": ["ENTJ", "INTP", "ENTP"],          # Tous NT
    # ST - Les Praticiens (Sensing + Thinking) - orientés efficacité et logique pratique
    "ESTP": ["ISTP", "ESTJ", "ISTJ"],          # Tous ST (pas ESFP/ISFP qui sont SF!)
    "ISTP": ["ESTP", "ISTJ", "ESTJ"],          # Tous ST
    "ESTJ": ["ISTJ", "ESTP", "ISTP"],          # Tous ST
    "ISTJ": ["ESTJ", "ISTP", "ESTP"],          # Tous ST
    # SF - Les Protecteurs (Sensing + Feeling) - orientés service et harmonie
    "ESFP": ["ISFP", "ESFJ", "ISFJ"],          # Tous SF (pas ESTP/ISTP qui sont ST!)
    "ISFP": ["ESFP", "ISFJ", "ESFJ"],          # Tous SF
    "ESFJ": ["ISFJ", "ESFP", "ISFP"],          # Tous SF
    "ISFJ": ["ESFJ", "ISFP", "ESFP"],          # Tous SF
}

def mbti_similarity(user_mbti: str, job_mbti_list: List[str]) -> float:
    """
    Calculate MBTI compatibility score (0-1).
    PÉNALITÉ FORTE si le MBTI n'est pas compatible.
    """
    if not job_mbti_list or not user_mbti:
        return 0.5  # Score neutre
    
    user_mbti = user_mbti.upper()
    
    # Exact match = 100%
    if user_mbti in job_mbti_list:
        return 1.0
    
    # Similar type match (même famille NF/NT/SF/ST) = 85%
    similar_types = MBTI_SIMILAR.get(user_mbti, [])
    for similar in similar_types:
        if similar in job_mbti_list:
            return 0.85
    
    # Partial match - avec PÉNALITÉ plus forte pour incompatibilité
    best_score = 0.20  # Score minimum beaucoup plus bas (était 0.45)
    
    for job_mbti in job_mbti_list:
        if len(job_mbti) != 4:
            continue
        
        # Compter les lettres communes
        common_letters = sum(1 for i in range(4) if i < len(user_mbti) and user_mbti[i] == job_mbti[i])
        
        # Vérifier si même "core" (N/S et F/T identiques)
        same_core = (len(user_mbti) >= 3 and len(job_mbti) >= 3 and 
                     user_mbti[1] == job_mbti[1] and user_mbti[2] == job_mbti[2])
        
        if common_letters >= 3:
            score = 0.70 if same_core else 0.60
        elif common_letters >= 2:
            if same_core:
                score = 0.55  # Même core mais 2 lettres différentes
            else:
                score = 0.35  # 2 lettres communes mais core différent = faible
        else:
            score = 0.20  # Très incompatible
        
        best_score = max(best_score, score)
    
    return best_score

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


def compute_profile(answers: Dict[str, str]) -> Dict[str, Any]:
    """Compute user profile from questionnaire answers.
    Supports both legacy format (q1-q15) and visual format (v1-v12).
    
    SÉCURISATION:
    - Validation du format des réponses
    - Logging détaillé pour debug
    - Valeurs par défaut sécurisées
    - Vérification de cohérence
    """
    
    # ========================================================================
    # ÉTAPE 1: DÉTECTION ET VALIDATION DU FORMAT
    # ========================================================================
    visual_keys = [k for k in answers.keys() if k.startswith("v")]
    legacy_keys = [k for k in answers.keys() if k.startswith("q")]
    
    is_visual = len(visual_keys) > len(legacy_keys)
    
    logging.info(f"[PROFILING] Format détecté: {'VISUEL' if is_visual else 'LEGACY'}")
    logging.info(f"[PROFILING] Clés visuelles: {len(visual_keys)}, Clés legacy: {len(legacy_keys)}")
    
    # Valeurs par défaut pour éviter les erreurs
    energie_e, energie_i = 0, 0
    perception_s, perception_n = 0, 0
    decision_t, decision_f = 0, 0
    structure_j, structure_p = 0, 0
    disc_counts = {"D": 0, "I": 0, "S": 0, "C": 0}
    ennea_counts = {str(i): 0 for i in range(1, 10)}
    
    if is_visual:
        # ====================================================================
        # VISUAL QUESTIONNAIRE FORMAT (v1-v12)
        # ====================================================================
        
        # Énergie (v1, v2) - E/I
        for q in ["v1", "v2"]:
            val = answers.get(q, "").upper()
            if val == "E":
                energie_e += 1
            elif val == "I":
                energie_i += 1
            else:
                logging.warning(f"[PROFILING] Réponse invalide pour {q}: '{val}' (attendu: E ou I)")
        
        # Perception (v3) - S/N binary
        v3 = answers.get("v3", "").upper()
        if v3 == "S":
            perception_s += 1
        elif v3 == "N":
            perception_n += 1
        else:
            logging.warning(f"[PROFILING] Réponse invalide pour v3: '{v3}' (attendu: S ou N)")
        
        # Perception (v4) - RANKING S1,S2,N1,N2
        v4_answer = answers.get("v4", "")
        if "," in v4_answer:
            v4_ranks = [x.strip().upper() for x in v4_answer.split(",")]
            for idx, val in enumerate(v4_ranks[:4]):
                weight = 4 - idx  # 1st=4, 2nd=3, 3rd=2, 4th=1
                if val.startswith("S"):
                    perception_s += weight
                elif val.startswith("N"):
                    perception_n += weight
        elif v4_answer:
            if v4_answer.upper().startswith("S"):
                perception_s += 2
            elif v4_answer.upper().startswith("N"):
                perception_n += 2
        
        # Décision (v5, v6) - T/F
        for q in ["v5", "v6"]:
            val = answers.get(q, "").upper()
            if val == "T":
                decision_t += 1
            elif val == "F":
                decision_f += 1
            else:
                logging.warning(f"[PROFILING] Réponse invalide pour {q}: '{val}' (attendu: T ou F)")
        
        # Structure (v7, v8) - J/P
        for q in ["v7", "v8"]:
            val = answers.get(q, "").upper()
            if val == "J":
                structure_j += 1
            elif val == "P":
                structure_p += 1
            else:
                logging.warning(f"[PROFILING] Réponse invalide pour {q}: '{val}' (attendu: J ou P)")
        
        # DISC (v9, v10) - RANKING
        for q in ["v9", "v10"]:
            val = answers.get(q, "")
            if "," in val:
                ranks = [x.strip().upper() for x in val.split(",")]
                for idx, disc_val in enumerate(ranks[:4]):
                    if disc_val in disc_counts:
                        weight = 4 - idx
                        disc_counts[disc_val] += weight
            elif val.upper() in disc_counts:
                disc_counts[val.upper()] += 4
        
        # Ennéagramme (v11, v12) - RANKING
        for q in ["v11", "v12"]:
            val = answers.get(q, "")
            if "," in val:
                ranks = [x.strip() for x in val.split(",")]
                for idx, ennea_val in enumerate(ranks[:4]):
                    if ennea_val in ennea_counts:
                        weight = 4 - idx
                        ennea_counts[ennea_val] += weight
            elif val in ennea_counts:
                ennea_counts[val] += 4
                
    else:
        # ====================================================================
        # LEGACY QUESTIONNAIRE FORMAT (q1-q15)
        # ====================================================================
        
        # MBTI - Énergie (q1, q2)
        for q in ["q1", "q2"]:
            val = answers.get(q, "").upper()
            if val == "E":
                energie_e += 1
            elif val == "I":
                energie_i += 1
        
        # MBTI - Perception (q4, q6)
        for q in ["q4", "q6"]:
            val = answers.get(q, "").upper()
            if val == "S":
                perception_s += 1
            elif val == "N":
                perception_n += 1
        
        # MBTI - Décision (q5)
        val = answers.get("q5", "").upper()
        if val == "T":
            decision_t += 1
        elif val == "F":
            decision_f += 1
        
        # MBTI - Structure (q7)
        val = answers.get("q7", "").upper()
        if val == "J":
            structure_j += 1
        elif val == "P":
            structure_p += 1
        
        # DISC (q3, q8, q9, q13, q14, q15)
        for q in ["q3", "q8", "q9", "q13", "q14", "q15"]:
            val = answers.get(q, "").upper()
            if val in disc_counts:
                disc_counts[val] += 1
        
        # Ennéagramme (q10, q11, q12)
        for q in ["q10", "q11", "q12"]:
            val = answers.get(q, "")
            if val in ennea_counts:
                ennea_counts[val] += 1
    
    # ========================================================================
    # ÉTAPE 2: CALCUL DES DIMENSIONS AVEC VALIDATION
    # ========================================================================
    
    # MBTI - Détermination avec gestion des égalités
    # En cas d'égalité, on choisit une valeur par défaut cohérente
    if energie_e > energie_i:
        energie = "E"
    elif energie_i > energie_e:
        energie = "I"
    else:
        # Égalité: défaut vers I (plus introspectif pour l'orientation)
        energie = "I"
        logging.info(f"[PROFILING] Égalité E/I ({energie_e}/{energie_i}), défaut: I")
    
    if perception_s > perception_n:
        perception = "S"
    elif perception_n > perception_s:
        perception = "N"
    else:
        perception = "N"  # Défaut vers N (plus ouvert aux possibilités)
        logging.info(f"[PROFILING] Égalité S/N ({perception_s}/{perception_n}), défaut: N")
    
    if decision_t > decision_f:
        decision = "T"
    elif decision_f > decision_t:
        decision = "F"
    else:
        decision = "T"  # Défaut vers T
        logging.info(f"[PROFILING] Égalité T/F ({decision_t}/{decision_f}), défaut: T")
    
    if structure_j > structure_p:
        structure = "J"
    elif structure_p > structure_j:
        structure = "P"
    else:
        structure = "J"  # Défaut vers J (plus structuré)
        logging.info(f"[PROFILING] Égalité J/P ({structure_j}/{structure_p}), défaut: J")
    
    mbti = f"{energie}{perception}{decision}{structure}"
    
    # DISC - Détermination du dominant
    disc_max = max(disc_counts.values())
    if disc_max == 0:
        disc = "S"  # Défaut: Stabilité
        logging.warning(f"[PROFILING] Aucune réponse DISC, défaut: S")
    else:
        disc = max(disc_counts, key=disc_counts.get)
    
    # Ennéagramme - Détermination
    sorted_ennea = sorted(ennea_counts.items(), key=lambda x: x[1], reverse=True)
    if sorted_ennea[0][1] > 0:
        ennea_dominant = int(sorted_ennea[0][0])
        ennea_runner_up = int(sorted_ennea[1][0]) if len(sorted_ennea) > 1 and sorted_ennea[1][1] > 0 else ennea_dominant
    else:
        ennea_dominant = 9  # Défaut: Type 9 (Médiateur, neutre)
        ennea_runner_up = 9
        logging.warning(f"[PROFILING] Aucune réponse Ennéagramme, défaut: 9")
    
    # ========================================================================
    # ÉTAPE 3: LOGGING DE VALIDATION
    # ========================================================================
    logging.info(f"[PROFILING] RÉSULTAT - MBTI: {mbti} (E:{energie_e}/I:{energie_i}, S:{perception_s}/N:{perception_n}, T:{decision_t}/F:{decision_f}, J:{structure_j}/P:{structure_p})")
    logging.info(f"[PROFILING] RÉSULTAT - DISC: {disc} (D:{disc_counts['D']}, I:{disc_counts['I']}, S:{disc_counts['S']}, C:{disc_counts['C']})")
    logging.info(f"[PROFILING] RÉSULTAT - Ennéagramme: {ennea_dominant} (runner-up: {ennea_runner_up})")
    
    # Determine motivations and competences
    ennea_profile = ENNEA_TO_PROFILE.get(ennea_dominant, ENNEA_TO_PROFILE[5])
    vertu_key = ennea_profile["vertu"]
    vertu_data = VERTUS.get(vertu_key, VERTUS["sagesse"])
    
    # Build competences based on profile
    competences_fortes = vertu_data["competences_oms"][:3]
    
    # Add DISC-based competences
    if disc == "D":
        competences_fortes.append("Leadership")
    elif disc == "I":
        competences_fortes.append("Communication")
    elif disc == "S":
        competences_fortes.append("Écoute active")
    elif disc == "C":
        competences_fortes.append("Analyse")
    
    # Determine vigilances
    vigilances = []
    if ennea_dominant == 2:
        vigilances.append("Surinvestissement émotionnel")
    elif ennea_dominant == 3:
        vigilances.append("Surmenage lié à la performance")
    elif ennea_dominant == 5:
        vigilances.append("Retrait sous stress")
    elif ennea_dominant == 6:
        vigilances.append("Doute excessif")
    elif ennea_dominant == 1:
        vigilances.append("Perfectionnisme")
    elif ennea_dominant == 4:
        vigilances.append("Dispersion émotionnelle")
    elif ennea_dominant == 7:
        vigilances.append("Dispersion")
    elif ennea_dominant == 8:
        vigilances.append("Confrontation excessive")
    elif ennea_dominant == 9:
        vigilances.append("Évitement des conflits")
    
    if structure == "P":
        vigilances.append("Difficulté avec les cadres rigides")
    if energie == "I" and disc == "D":
        vigilances.append("Tension entre action et besoin de recul")
    
    # Build dominant vertus
    dominant_vertus = [
        {
            "vertu": vertu_data["name"],
            "key_strengths": vertu_data["forces"][:3],
            "key_oms_competencies": vertu_data["competences_oms"],
            "key_soft_skills": vertu_data["savoirs_etre"]
        }
    ]
    
    # Build MBTI type string
    mbti = energie + perception + decision + structure
    
    return {
        "energie": energie,
        "perception": perception,
        "decision": decision,
        "structure": structure,
        "mbti": mbti,
        "disc": disc,
        "disc_scores": disc_counts,  # Scores détaillés pour le radar DISC
        "ennea_dominant": ennea_dominant,
        "ennea_runner_up": ennea_runner_up,
        "motivations": [ennea_profile["moteur"]],
        "competences_fortes": list(set(competences_fortes)),
        "vigilances": vigilances[:3],
        "dominant_vertus": dominant_vertus
    }


def disc_similarity(user_disc: str, job_discs: List[str]) -> float:
    """Calculate DISC similarity score - optimisé pour des scores plus élevés."""
    user_disc = user_disc.upper()
    if not job_discs:
        return 0.7  # Score neutre plus généreux
    
    best = 0.5
    for d in job_discs:
        d = d.upper()
        if user_disc == d:
            sim = 1.0  # Match parfait
        elif d in DISC_ADJACENT.get(user_disc, set()):
            sim = 0.75  # Adjacent = bon match
        else:
            sim = 0.45  # Non adjacent mais pas incompatible
        best = max(best, sim)
    return best


def ennea_similarity(dominant: int, runner_up: int, compatible_list: List[int]) -> float:
    """Calculate Enneagram similarity score - optimisé."""
    if not compatible_list:
        return 0.65  # Score neutre plus généreux
    if dominant in compatible_list:
        return 1.0   # Match parfait
    if runner_up in compatible_list:
        return 0.75  # Bon match avec secondaire
    return 0.4  # Pas de match mais pas forcément incompatible


def score_environment(profile: Dict[str, Any], job: Dict[str, Any]) -> float:
    """Calculate environment compatibility score - optimisé pour des scores plus élevés."""
    points = []
    
    # Interaction preference
    interaction = job.get("interaction", 1)
    if profile["energie"] == "E":
        points.append(1.0 if interaction >= 1 else 0.7)
    else:
        points.append(1.0 if interaction <= 1 else 0.7)
    
    # Cadre preference
    cadre = job.get("cadre", 1)
    if profile["structure"] == "J":
        points.append(1.0 if cadre >= 1 else 0.7)
    else:
        points.append(1.0 if cadre <= 1 else 0.7)
    
    # Complexity preference
    complexite = job.get("complexite", 1)
    if profile["perception"] == "N":
        points.append(1.0 if complexite >= 1 else 0.8)
    else:
        points.append(1.0 if complexite <= 1 else 0.8)
    
    # Rythme with vigilance
    rythme = job.get("rythme", 1)
    if any(v in str(profile.get("vigilances", [])) for v in ["stress", "surmenage", "perfectionnisme"]):
        points.append(0.75 if rythme == 2 else 1.0)
    else:
        points.append(1.0)
    
    return sum(points) / len(points) if points else 0.8


def score_skills(profile: Dict[str, Any], job: Dict[str, Any]) -> float:
    """
    Calculate skills match score - basé sur l'Archéologie des Compétences.
    Utilise la hiérarchie: Vertus → Valeurs → Qualités → Savoir-être → Compétences → Métier
    """
    req = job.get("competences_requises", [])
    user_skills = profile.get("competences_fortes", [])
    
    # Si pas de compétences définies, score neutre-positif
    if not req:
        return 0.7
    if not user_skills:
        return 0.6
    
    # Normaliser les compétences
    user_skills_lower = set(s.lower().strip() for s in user_skills)
    job_skills_lower = set(s.lower().strip() for s in req)
    
    # Match direct
    direct_match = len(user_skills_lower & job_skills_lower)
    
    # Match partiel (mots-clés communs)
    partial_match = 0
    for user_skill in user_skills_lower:
        for job_skill in job_skills_lower:
            # Match si un mot significatif est commun
            user_words = set(w for w in user_skill.split() if len(w) > 3)
            job_words = set(w for w in job_skill.split() if len(w) > 3)
            if user_words & job_words:
                partial_match += 0.5
                break
    
    # Compétences transverses toujours valorisées
    transversal_skills = {"communication", "écoute", "analyse", "leadership", "empathie", 
                         "créativité", "organisation", "adaptabilité", "résolution"}
    user_transversal = sum(1 for s in user_skills_lower if any(t in s for t in transversal_skills))
    transversal_bonus = min(0.3, user_transversal * 0.1)
    
    # Calcul du score final
    total_matches = direct_match + partial_match
    base_score = min(1.0, total_matches / max(3, len(req)))
    
    # Score minimum de 0.5 si l'utilisateur a des compétences, + bonus transversal
    final_score = max(0.5, base_score) + transversal_bonus
    return min(1.0, final_score)


def score_archeologie(profile: Dict[str, Any], job: Dict[str, Any], vertus_profile: Dict[str, Any] = None) -> float:
    """
    Score basé sur l'Archéologie des Compétences avec CROISEMENT COMPLET.
    Calcule la cohérence entre les vertus/qualités de l'utilisateur et les soft skills du métier.
    
    Hiérarchie CK1: Vertus → Valeurs → Qualités → Savoir-être → Compétences → Métier
    
    CROISEMENT de 3 sources:
    1. Les réponses directes aux questions vv1-vv6 (vertus_profile) - Poids 60%
    2. L'inférence depuis l'Ennéagramme (profile) - Poids 30%
    3. Les dimensions CK1 (Cognition, Conation, Affection) - Poids 10% bonus
    """
    # ============================================================================
    # SOURCE 1: Vertus depuis les questions directes (prioritaire - 60%)
    # ============================================================================
    if vertus_profile and vertus_profile.get("vertus_scores"):
        user_vertu_key = vertus_profile.get("dominant", "sagesse")
        secondary_vertu_key = vertus_profile.get("secondary", "temperance")
        vertus_scores = vertus_profile.get("vertus_scores", {})
        
        # Récupérer les données depuis la hiérarchie Archéologie
        user_savoirs_etre_from_answers = set(
            s.lower() for s in vertus_profile.get("savoirs_etre_dominants", [])
        )
        user_qualites_from_answers = set(
            q.lower() for q in vertus_profile.get("qualites_dominantes", [])
        )
        user_competences_oms_from_answers = set(
            c.lower() for c in vertus_profile.get("competences_oms", [])
        )
    else:
        user_vertu_key = "sagesse"
        secondary_vertu_key = "temperance"
        vertus_scores = {}
        user_savoirs_etre_from_answers = set()
        user_qualites_from_answers = set()
        user_competences_oms_from_answers = set()
    
    # ============================================================================
    # SOURCE 2: Vertus inférées depuis l'Ennéagramme (30%)
    # ============================================================================
    ennea_dominant = profile.get("ennea_dominant", 5)
    ennea_secondary = profile.get("ennea_runner_up", 9)
    ennea_profile = ENNEA_TO_PROFILE.get(ennea_dominant, ENNEA_TO_PROFILE[5])
    ennea_vertu_key = ennea_profile.get("vertu", "sagesse")
    ennea_vertu = VERTUS.get(ennea_vertu_key, VERTUS["sagesse"])
    
    # ============================================================================
    # CROISEMENT: Combiner les deux sources avec pondération
    # ============================================================================
    # Vertu finale = moyenne pondérée (60% questions, 40% Ennéagramme)
    user_vertu = VERTUS.get(user_vertu_key, ennea_vertu)
    
    # Union des savoirs-être et qualités des deux sources
    user_savoirs_etre = user_savoirs_etre_from_answers | set(
        s.lower() for s in user_vertu.get("savoirs_etre", [])
    ) | set(
        s.lower() for s in ennea_vertu.get("savoirs_etre", [])
    )
    
    user_qualites = user_qualites_from_answers | set(
        q.lower() for q in user_vertu.get("qualites_humaines", [])
    ) | set(
        q.lower() for q in ennea_vertu.get("qualites_humaines", [])
    )
    
    user_competences_oms = user_competences_oms_from_answers | set(
        c.lower() for c in user_vertu.get("competences_oms", [])
    ) | set(
        c.lower() for c in ennea_vertu.get("competences_oms", [])
    )
    
    # ============================================================================
    # SOURCE 3: Dimensions CK1 (Cognition, Conation, Affection)
    # ============================================================================
    user_cognition = set(c.lower() for c in user_vertu.get("cognition", []))
    user_conation = set(c.lower() for c in user_vertu.get("conation", []))
    user_affection = set(a.lower() for a in user_vertu.get("affection", []))
    
    # ============================================================================
    # SOURCE 4: TABLEAU CK - Compétences sociales et pro transférables
    # ============================================================================
    ck_data = TABLEAU_CK.get(user_vertu_key, {})
    user_comp_sociales = set(c.lower() for c in ck_data.get("competences_sociales", []))
    user_comp_pro = set(c.lower() for c in ck_data.get("competences_pro_transferables", []))
    user_valeurs_univ = set(v.lower() for v in ck_data.get("valeurs_universelles", []))
    
    # Récupérer les soft skills requis par le métier
    job_soft_skills = job.get("soft_skills_essentiels", [])
    job_skill_names = set()
    for skill in job_soft_skills:
        if isinstance(skill, dict):
            job_skill_names.add(skill.get("nom", "").lower())
        elif isinstance(skill, str):
            job_skill_names.add(skill.lower())
    
    # Récupérer aussi les compétences requises du métier
    job_competences = set(c.lower() for c in job.get("competences_requises", []))
    
    # ============================================================================
    # CALCUL DU SCORE avec hiérarchie pondérée
    # ============================================================================
    score = 0.0
    
    # 1. Match savoirs-être avec soft skills du métier (poids élevé: 35%)
    if user_savoirs_etre and job_skill_names:
        matches = 0
        for savoir in user_savoirs_etre:
            for job_skill in job_skill_names:
                if savoir in job_skill or job_skill in savoir:
                    matches += 1
                    break
                savoir_words = set(w for w in savoir.split() if len(w) > 3)
                skill_words = set(w for w in job_skill.split() if len(w) > 3)
                if savoir_words & skill_words:
                    matches += 0.5
                    break
        score += min(0.35, matches * 0.08)
    
    # 2. Match qualités humaines avec soft skills (poids moyen: 25%)
    if user_qualites and job_skill_names:
        matches = 0
        for qualite in user_qualites:
            for job_skill in job_skill_names:
                if qualite in job_skill or job_skill in qualite:
                    matches += 1
                    break
                if len(set(qualite.split()) & set(job_skill.split())) > 0:
                    matches += 0.5
                    break
        score += min(0.25, matches * 0.06)
    
    # 3. Match compétences OMS avec compétences requises (poids moyen: 20%)
    if user_competences_oms and job_competences:
        matches = 0
        for comp_oms in user_competences_oms:
            for job_comp in job_competences:
                if comp_oms in job_comp or job_comp in comp_oms:
                    matches += 1
                    break
                oms_words = set(w for w in comp_oms.split() if len(w) > 3)
                comp_words = set(w for w in job_comp.split() if len(w) > 3)
                if oms_words & comp_words:
                    matches += 0.5
                    break
        score += min(0.2, matches * 0.05)
    
    # 4. Bonus CK1: Match dimensions Cognition/Conation/Affection (10%)
    ck1_matches = 0
    all_ck1 = user_cognition | user_conation | user_affection
    for ck1_item in all_ck1:
        for job_skill in job_skill_names | job_competences:
            if ck1_item in job_skill or job_skill in ck1_item:
                ck1_matches += 1
                break
    score += min(0.1, ck1_matches * 0.02)
    
    # 4b. TABLEAU CK: Match compétences sociales avec soft skills (bonus 8%)
    if user_comp_sociales and job_skill_names:
        matches = 0
        for comp in user_comp_sociales:
            for job_skill in job_skill_names | job_competences:
                if comp in job_skill or job_skill in comp:
                    matches += 1
                    break
                comp_words = set(w for w in comp.split() if len(w) > 3)
                skill_words = set(w for w in job_skill.split() if len(w) > 3)
                if comp_words & skill_words:
                    matches += 0.5
                    break
        score += min(0.08, matches * 0.02)
    
    # 4c. TABLEAU CK: Match compétences pro transférables (bonus 7%)
    if user_comp_pro and (job_skill_names or job_competences):
        matches = 0
        all_job = job_skill_names | job_competences
        for comp in user_comp_pro:
            for job_item in all_job:
                if comp in job_item or job_item in comp:
                    matches += 1
                    break
                comp_words = set(w for w in comp.split() if len(w) > 3)
                job_words = set(w for w in job_item.split() if len(w) > 3)
                if comp_words & job_words:
                    matches += 0.5
                    break
        score += min(0.07, matches * 0.02)
    
    # 5. COHÉRENCE VERTU-MÉTIER : Le facteur le plus important
    # La vertu de l'utilisateur doit correspondre à la vertu naturelle du métier
    metier_id = job.get("id", "")
    metier_vertu = get_vertu_for_metier(metier_id)
    
    # Calculer la cohérence vertu utilisateur ↔ vertu métier
    vertu_coherence = calculate_vertu_coherence(user_vertu_key, metier_id)
    
    # Bonus/Malus basé sur la cohérence Vertu-Métier (FACTEUR DÉCISIF)
    if vertu_coherence >= 1.0:
        score += 0.25  # Parfaite cohérence = gros bonus
    elif vertu_coherence >= 0.7:
        score += 0.10  # Bonne affinité = bonus modéré
    else:
        score -= 0.15  # Faible cohérence = malus

    # 6. Bonus cohérence: Vertus directes = Ennéagramme
    if vertus_profile and user_vertu_key == ennea_vertu_key:
        score += 0.08
    elif vertus_profile and secondary_vertu_key == ennea_vertu_key:
        score += 0.04  # Bonus partiel si secondaire match
    
    # Score minimum de 0.25 (réduit car l'archéologie doit discriminer)
    # Score maximum de 1.0
    final_score = max(0.25, min(1.0, score + 0.30))
    return final_score


def get_job_riasec(job: Dict[str, Any]) -> str:
    """
    Obtient le code RIASEC d'un métier à partir de son code ROME.
    Utilise le mapping ROME_RIASEC_MAPPING ou retourne une valeur par défaut.
    """
    code_rome = job.get("code_rome", "")
    
    # Lookup direct dans le mapping
    if code_rome in ROME_RIASEC_MAPPING:
        return ROME_RIASEC_MAPPING[code_rome]
    
    # Si pas de mapping direct, inférer depuis le secteur/filière
    filiere = job.get("filiere", "").upper()
    secteur = job.get("secteur", "").lower()
    
    # Inférence par filière
    filiere_riasec = {
        "SI": "IR",      # Industrielle → Investigateur/Réaliste
        "SBTP": "RC",    # BTP → Réaliste/Conventionnel
        "SSS": "SA",     # Santé Social → Social/Artistique
        "SN": "IR",      # Numérique → Investigateur/Réaliste
        "SC": "ES",      # Commerce → Entreprenant/Social
        "SA": "CE",      # Administrative → Conventionnel/Entreprenant
        "SENV": "RI",    # Environnement → Réaliste/Investigateur
        "SART": "AE",    # Art/Culture → Artistique/Entreprenant
    }
    
    if filiere in filiere_riasec:
        return filiere_riasec[filiere]
    
    # Inférence par mots-clés du secteur
    if any(kw in secteur for kw in ["technique", "mécanique", "maintenance", "électricité"]):
        return "RC"
    if any(kw in secteur for kw in ["informatique", "développement", "data", "cybersécurité"]):
        return "IC"
    if any(kw in secteur for kw in ["santé", "social", "éducation", "aide"]):
        return "SI"
    if any(kw in secteur for kw in ["commerce", "vente", "marketing"]):
        return "ES"
    if any(kw in secteur for kw in ["art", "design", "créatif", "communication"]):
        return "AE"
    if any(kw in secteur for kw in ["comptabilité", "finance", "administration"]):
        return "CI"
    
    return "SC"  # Valeur par défaut neutre (Social/Conventionnel)


def score_job(profile: Dict[str, Any], job: Dict[str, Any], user_riasec: Dict[str, Any] = None, vertus_profile: Dict[str, Any] = None) -> Dict[str, Any]:
    """Calculate overall job compatibility score including RIASEC model and Archéologie des Compétences."""
    
    # Motivation score (Enneagram)
    motivation_score = ennea_similarity(
        profile["ennea_dominant"],
        profile["ennea_runner_up"],
        job.get("ennea_compatible", [])
    ) * WEIGHTS["motivation"]
    
    # DISC score
    disc_score = disc_similarity(
        profile["disc"],
        job.get("disc_attendu", [])
    ) * WEIGHTS["disc"]
    
    # MBTI score
    mbti_score = mbti_similarity(
        profile.get("mbti", ""),
        job.get("mbti_compatible", [])
    ) * WEIGHTS["mbti"]
    
    # RIASEC score (Holland Codes)
    riasec_score_raw = 0.5  # Score neutre par défaut
    job_riasec = get_job_riasec(job)
    
    if user_riasec:
        user_riasec_code = user_riasec.get("code_2", "")
        if user_riasec_code and job_riasec:
            riasec_score_raw = riasec_congruence(user_riasec_code, job_riasec)
    
    riasec_score = riasec_score_raw * WEIGHTS["riasec"]
    
    # Score Archéologie des Compétences (Vertus → Compétences) avec profil de vertus
    archeologie_score = score_archeologie(profile, job, vertus_profile) * WEIGHTS["archeologie"]
    
    # Environment score
    env_score = score_environment(profile, job) * WEIGHTS["environment"]
    
    # Skills score
    skills_score = score_skills(profile, job) * WEIGHTS["skills"]
    
    # Constraints (simplified - full score for now)
    constraints_score = WEIGHTS["constraints"] * 1.0
    
    total = int(round(motivation_score + disc_score + mbti_score + riasec_score + archeologie_score + env_score + skills_score + constraints_score))
    total = max(0, min(100, total))
    
    # Build reasons and risks
    reasons = []
    risks = []
    
    # Archéologie des compétences feedback (priorité haute - socle du système)
    if archeologie_score >= WEIGHTS["archeologie"] * 0.7:
        reasons.append("Vos vertus et qualités naturelles correspondent aux savoir-être du métier")
    elif archeologie_score >= WEIGHTS["archeologie"] * 0.5:
        reasons.append("Certaines de vos qualités humaines sont transférables à ce métier")
    elif archeologie_score < WEIGHTS["archeologie"] * 0.4:
        risks.append("Vos vertus dominantes sont peu sollicitées dans ce métier")
    
    # RIASEC compatibility feedback
    if riasec_score >= WEIGHTS["riasec"] * 0.7:
        reasons.append("Intérêts professionnels (Holland) fortement alignés avec ce métier")
    elif riasec_score >= WEIGHTS["riasec"] * 0.5:
        reasons.append("Intérêts professionnels partiellement compatibles")
    elif riasec_score < WEIGHTS["riasec"] * 0.3:
        risks.append("Intérêts professionnels peu alignés avec ce type de métier")
    
    # MBTI compatibility feedback
    if mbti_score >= WEIGHTS["mbti"] * 0.7:
        reasons.append("Personnalité naturellement adaptée à ce type de métier")
    elif mbti_score < WEIGHTS["mbti"] * 0.4:
        risks.append("Type de personnalité peu aligné avec les attentes du poste")
    
    if motivation_score >= WEIGHTS["motivation"] * 0.6:
        reasons.append("Motivation globalement alignée avec la nature du poste")
    else:
        risks.append("Motivation potentiellement peu nourrie par ce type de poste")
    
    if disc_score >= WEIGHTS["disc"] * 0.6:
        reasons.append("Style de contribution compatible avec les attentes")
    else:
        risks.append("Style relationnel pouvant nécessiter un ajustement")
    
    if skills_score >= WEIGHTS["skills"] * 0.4:
        reasons.append("Compétences fortes directement mobilisables")
    else:
        risks.append("Écart de compétences à combler pour réussir")
    
    if env_score >= WEIGHTS["environment"] * 0.7:
        reasons.append("Environnement de travail adapté à votre fonctionnement")
    else:
        risks.append("Environnement pouvant générer de la fatigue sur la durée")
    
    # Category
    if total >= 80:
        category = "Très compatible"
    elif total >= 60:
        category = "Compatible"
    elif total >= 40:
        category = "Partiellement compatible"
    else:
        category = "À risque"
    
    # Obtenir les détails d'archéologie pour enrichir la fiche
    metier_vertu = get_vertu_for_metier(job["id"])
    archeologie_data = ARCHEOLOGIE_COMPETENCES.get(metier_vertu, {})
    user_vertu = vertus_profile.get("dominant", "temperance") if vertus_profile else "temperance"
    
    # Générer les savoirs-être enrichis
    soft_skills = [s["nom"] for s in job.get("soft_skills_essentiels", [])]
    savoirs_etre_enrichis = generate_savoirs_etre_from_archeology(metier_vertu, soft_skills)
    
    return {
        "job_id": job["id"],
        "job_label": job["label"],
        "filiere": job.get("filiere", ""),
        "secteur": job.get("secteur", ""),
        "score": total,
        "category": category,
        "reasons": reasons[:3],
        "risks": risks[:2],
        "job_riasec": job_riasec,
        "breakdown": {
            "motivation": round(motivation_score, 1),
            "disc": round(disc_score, 1),
            "mbti": round(mbti_score, 1),
            "riasec": round(riasec_score, 1),
            "archeologie": round(archeologie_score, 1),
            "environment": round(env_score, 1),
            "skills": round(skills_score, 1),
            "constraints": round(constraints_score, 1)
        },
        # NOUVEAU: Détails archéologie des compétences
        "archeologie_details": {
            "metier_vertu": metier_vertu,
            "user_vertu": user_vertu,
            "vertu_alignee": user_vertu == metier_vertu,
            "qualites_requises": archeologie_data.get("qualites", [])[:5],
            "valeurs_associees": archeologie_data.get("valeurs_schwartz", [])[:3],
            "savoirs_etre": savoirs_etre_enrichis[:5],
            "forces_mobilisees": archeologie_data.get("forces", [])[:3]
        }
    }


def normalize_text(text: str) -> str:
    """Normalize text for search: remove accents, special chars, and lowercase."""
    import re
    import unicodedata
    # Normalize unicode and remove accents
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    # Remove special characters but keep spaces
    text = re.sub(r'[^\w\s]', ' ', text)
    # Convert to lowercase and clean up spaces
    text = ' '.join(text.lower().split())
    return text


def search_job_by_query(query: str) -> List[Dict[str, Any]]:
    """Search jobs matching query with flexible matching (base locale)."""
    query_normalized = normalize_text(query)
    query_words = set(query_normalized.split())
    # Remove common stop words from query
    stop_words = {'de', 'du', 'des', 'le', 'la', 'les', 'un', 'une', 'en', 'et', 'ou'}
    query_words_significant = query_words - stop_words
    
    scored_matches = []
    
    for job in METIERS:
        job_text = f"{job['label']} {job.get('secteur', '')} {job.get('filiere', '')} {job.get('intitule_rome', '')} {job.get('definition', '')}".lower()
        job_text_normalized = normalize_text(job_text)
        job_words = set(job_text_normalized.split())
        
        score = 0
        
        # 1. Exact normalized substring match (highest priority)
        if query_normalized in job_text_normalized:
            score = 100
        else:
            # 2. Check if all significant query words appear in job text (high priority)
            if query_words_significant and query_words_significant <= job_words:
                score = 95
            else:
                # 3. Partial word matching - check if query words are substrings of job words
                partial_matches = 0
                for qw in query_words_significant:
                    if len(qw) >= 3:  # Only match words with 3+ chars
                        for jw in job_words:
                            if qw in jw or jw in qw:
                                partial_matches += 1
                                break
                
                if partial_matches > 0 and query_words_significant:
                    # Score based on percentage of significant words matched
                    score = (partial_matches / len(query_words_significant)) * 85
                
                # 4. Fallback: Check exact word intersection
                if score == 0:
                    matching_words = query_words_significant & job_words
                    if matching_words:
                        score = (len(matching_words) / len(query_words_significant)) * 70 if query_words_significant else 0
        
        if score > 0:
            scored_matches.append((job, score))
    
    # Sort by score (descending), then by job label (alphabetical) for consistency
    scored_matches.sort(key=lambda x: (-x[1], x[0]['label']))
    matches = [job for job, score in scored_matches if score >= 30]
    
    return matches if matches else METIERS[:5]  # Return first 5 if no match


async def search_job_hybrid(query: str) -> tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """
    Recherche hybride : France Travail API + base locale
    Retourne (jobs_locaux, fiche_france_travail)
    """
    # 1. Toujours chercher dans la base locale pour le scoring
    local_jobs = search_job_by_query(query)
    
    # 2. Si France Travail est configuré, enrichir avec l'API
    france_travail_fiche = None
    
    if is_france_travail_enabled():
        try:
            # Rechercher des métiers correspondants via France Travail
            ft_results = await search_job_france_travail(query)
            
            if ft_results:
                # Prendre le premier résultat le plus pertinent
                best_ft_match = ft_results[0]
                code_rome = best_ft_match.get("code_rome")
                
                if code_rome:
                    # Récupérer la fiche métier complète
                    france_travail_fiche = await get_job_info_france_travail(code_rome)
                    
                    if france_travail_fiche:
                        logging.info(f"Fiche métier France Travail récupérée: {code_rome}")
        except Exception as e:
            logging.error(f"Erreur API France Travail: {e}")
    
    return local_jobs, france_travail_fiche


def get_exploration_paths(profile: Dict[str, Any], user_riasec: Dict[str, Any] = None, vertus_profile: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    Get recommended filieres and jobs for exploration.
    Le score de filière est principalement basé sur les métiers qu'elle contient.
    Si un métier est très compatible (85%), sa filière devrait l'être aussi.
    """
    # 1. D'abord, scorer tous les métiers
    all_job_scores = [score_job(profile, job, user_riasec, vertus_profile) for job in METIERS]
    all_job_scores.sort(key=lambda x: x["score"], reverse=True)
    
    # 2. Grouper les métiers par filière et calculer le score basé sur les métiers
    filiere_jobs = {}
    filiere_best_scores = {}  # Score max par filière
    
    for score_result in all_job_scores:
        filiere = score_result["filiere"]
        if filiere not in filiere_jobs:
            filiere_jobs[filiere] = []
            filiere_best_scores[filiere] = 0
        filiere_jobs[filiere].append(score_result)
        
        # Garder le meilleur score de métier pour cette filière
        if score_result["score"] > filiere_best_scores[filiere]:
            filiere_best_scores[filiere] = score_result["score"]
    
    # 3. Construire les chemins d'exploration
    paths = []
    for filiere in FILIERES:
        filiere_id = filiere["id"]
        
        jobs = filiere_jobs.get(filiere_id, [])
        
        if jobs:
            # Prendre les 5 meilleurs métiers de cette filière
            top_jobs = sorted(jobs, key=lambda x: x["score"], reverse=True)[:5]
            
            # Score basé sur les métiers (plus réaliste)
            best_job_score = top_jobs[0]["score"]
            avg_top_3_score = sum(j["score"] for j in top_jobs[:3]) / min(3, len(top_jobs))
            
            # Score final = 70% meilleur métier + 30% moyenne top 3
            # Cela garantit que si UX Designer = 85%, la filière ≈ 80%+
            final_score = (best_job_score * 0.7) + (avg_top_3_score * 0.3)
        else:
            final_score = 40  # Score bas si pas de métiers
            top_jobs = []
        
        # Déterminer les secteurs les plus pertinents
        relevant_sectors = filiere["secteurs"][:4]
        
        paths.append({
            "filiere": filiere["name"],
            "filiere_id": filiere_id,
            "avg_compatibility": round(final_score),
            "best_job_score": round(top_jobs[0]["score"]) if top_jobs else 0,
            "secteurs": relevant_sectors,
            "indicative_jobs": [j["job_label"] for j in top_jobs[:5]],
            "top_match": top_jobs[0] if top_jobs else None,
            "job_count": len(jobs)
        })
    
    # 4. Trier par compatibilité globale
    paths.sort(key=lambda x: x["avg_compatibility"], reverse=True)
    
    # 5. Filtrer les filières avec score >= 50%
    # et garder au minimum 3 filières
    MIN_FILIERE_SCORE = 50
    filtered_paths = [p for p in paths if p["avg_compatibility"] >= MIN_FILIERE_SCORE]
    
    # Si moins de 3 filières après filtrage, prendre les 3 meilleures
    if len(filtered_paths) < 3:
        filtered_paths = paths[:3]
    
    return filtered_paths


# ============================================================================
# API ROUTES
# ============================================================================

async def root():
    return {"message": "RE'ACTIF PRO - Intelligence Professionnelle API"}


async def get_france_travail_status():
    """Vérifier le statut de l'intégration France Travail."""
    return {
        "enabled": is_france_travail_enabled(),
        "message": "API France Travail configurée" if is_france_travail_enabled() else "API France Travail non configurée. Configurez FRANCE_TRAVAIL_CLIENT_ID et FRANCE_TRAVAIL_CLIENT_SECRET pour accéder à 1500+ métiers officiels."
    }


async def get_esco_status():
    """Vérifier le statut de l'intégration ESCO (European Skills/Occupations)."""
    return esco_api_status()


async def search_esco_occupations(query: str, limit: int = 20):
    """
    Rechercher des métiers dans la base ESCO européenne (3000+ métiers).
    
    Args:
        query: Terme de recherche (ex: "développeur", "commercial")
        limit: Nombre max de résultats (défaut: 20)
    """
    results = await search_occupations_esco(query, limit=limit, language="fr")
    return {
        "query": query,
        "count": len(results),
        "source": "ESCO - European Skills, Competences, Qualifications and Occupations",
        "results": results
    }


async def get_esco_occupation_details(uri: str):
    """
    Obtenir les détails d'un métier ESCO (compétences, description).
    
    Args:
        uri: URI ESCO du métier
    """
    details = await get_occupation_details_esco(uri, language="fr")
    if details:
        return details
    raise HTTPException(status_code=404, detail="Métier non trouvé dans ESCO")


async def get_questionnaire():
    """Get the complete questionnaire (legacy text format)."""
    return {"questions": QUESTIONNAIRE, "total": len(QUESTIONNAIRE)}


async def get_visual_questionnaire():
    """Get the visual questionnaire with images for accessibility."""
    return {"questions": VISUAL_QUESTIONS, "total": len(VISUAL_QUESTIONS), "format": "visual"}


async def get_filieres():
    """Get all professional filieres."""
    return {"filieres": FILIERES}


async def get_metiers():
    """Get all jobs."""
    return {"metiers": METIERS}


async def get_vertus():
    """Get all vertus with their details."""
    return {"vertus": VERTUS}


# ============================================================================
# ENDPOINT DE DIAGNOSTIC - VALIDATION DU PROFILAGE
# ============================================================================

def get_mbti_group(mbti: str) -> str:
    """Retourne le groupe MBTI (NT, NF, SJ, SP)."""
    if len(mbti) < 4:
        return "?"
    if mbti[1] == "N" and mbti[2] == "T":
        return "NT (Analystes)"
    elif mbti[1] == "N" and mbti[2] == "F":
        return "NF (Diplomates)"
    elif mbti[1] == "S" and mbti[3] == "J":
        return "SJ (Sentinelles)"
    elif mbti[1] == "S" and mbti[3] == "P":
        return "SP (Explorateurs)"
    return "?"


# ============================================================================
# ENDPOINT POUR RÉCUPÉRER LES RÉSULTATS VIA CODE D'ACCÈS (pour RE'ACTIF PRO)
# ============================================================================

async def claim_test_results(access_code: str, user_id: str):
    """
    Marque les résultats comme récupérés par un utilisateur RE'ACTIF PRO.
    Appelé après création réussie du compte.
    """
    success = await claim_test_result(access_code, user_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Impossible de récupérer ces résultats")
    
    return {"success": True, "message": "Résultats associés à votre compte"}


# Include the router in the main app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
