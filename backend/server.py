from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage

# Import France Travail API integration
from france_travail_api import (
    france_travail_api,
    search_job_france_travail,
    get_job_info_france_travail,
    is_france_travail_enabled
)

# Import ESCO API integration (European Skills/Occupations database)
from esco_api import (
    search_occupations_esco,
    get_occupation_details_esco,
    get_all_occupations_esco,
    is_esco_enabled,
    esco_api_status
)


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# LLM Configuration
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="RE'ACTIF PRO - Intelligence Professionnelle")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# ============================================================================
# DATA MODELS
# ============================================================================

class QuestionOption(BaseModel):
    id: str
    text: str
    value: str

class Question(BaseModel):
    id: str
    text: str
    category: str
    options: List[QuestionOption]

class QuestionnaireResponse(BaseModel):
    answers: Dict[str, str]  # question_id -> answer_value

class JobSearchRequest(BaseModel):
    answers: Dict[str, str]
    job_query: str
    birth_date: Optional[str] = None  # Format: YYYY-MM-DD ou DD/MM/YYYY

class ExploreRequest(BaseModel):
    answers: Dict[str, str]
    birth_date: Optional[str] = None  # Format: YYYY-MM-DD ou DD/MM/YYYY

class ProfileResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    # Profile dimensions
    energie: str  # E/I
    perception: str  # S/N
    decision: str  # T/F
    structure: str  # J/P
    disc: str  # D/I/S/C
    ennea_dominant: int
    ennea_runner_up: int
    # Computed
    motivations: List[str]
    competences_fortes: List[str]
    vigilances: List[str]
    dominant_vertus: List[Dict[str, Any]]


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
        "forces": ["Créativité", "Curiosité", "Jugement", "Amour de l'apprentissage", "Perspective"],
        "valeurs_schwartz": ["Autonomie", "Stimulation", "Réalisation de soi"],
        "qualites_humaines": ["Indépendance", "Créativité", "Curiosité", "Ouverture d'esprit", "Audace", "Liberté de pensée"],
        "competences_oms": ["Pensée critique", "Pensée créative", "Prise de décision"],
        "savoirs_etre": ["Faire preuve de curiosité", "Faire preuve de créativité, d'inventivité", "Prendre des initiatives et être force de proposition"],
        # Structure tripartite CK1
        "cognition": ["Connaissance", "Ouverture d'esprit", "Curiosité", "Pensée critique", "Lucidité", "Perspicacité"],
        "conation": ["Soif d'apprendre", "Initiative intellectuelle", "Audace créative", "Détermination à comprendre"],
        "affection": ["Partage de connaissances", "Tolérance des idées", "Respect de la diversité", "Humilité intellectuelle"]
    },
    "courage": {
        "name": "Courage",
        "forces": ["Bravoure", "Persévérance", "Honnêteté", "Enthousiasme"],
        "valeurs_schwartz": ["Hédonisme", "Réalisation de soi", "Stimulation"],
        "qualites_humaines": ["Joie de vivre", "Optimisme", "Gratitude", "Ambition", "Détermination", "Passion"],
        "competences_oms": ["Gestion du stress", "Résilience", "Estime de soi"],
        "savoirs_etre": ["Faire preuve de persévérance", "Gérer son stress", "Faire preuve de réactivité"],
        # Structure tripartite CK1
        "cognition": ["Lucidité face aux risques", "Évaluation des obstacles", "Conscience de soi", "Discernement"],
        "conation": ["Détermination", "Persévérance", "Bravoure", "Ambition", "Volonté", "Dynamisme"],
        "affection": ["Optimisme", "Joie de vivre", "Enthousiasme communicatif", "Confiance", "Vitalité"]
    },
    "humanite": {
        "name": "Humanité",
        "forces": ["Amour", "Gentillesse", "Intelligence sociale"],
        "valeurs_schwartz": ["Bienveillance", "Universalisme", "Affiliation"],
        "qualites_humaines": ["Empathie", "Gentillesse", "Générosité", "Altruisme", "Compassion", "Écoute", "Solidarité"],
        "competences_oms": ["Communication efficace", "Compétences relationnelles", "Empathie"],
        "savoirs_etre": ["Être à l'écoute", "Avoir le sens du service", "Travailler en équipe"],
        # Structure tripartite CK1
        "cognition": ["Intelligence sociale", "Compréhension d'autrui", "Lecture des émotions", "Psychologie intuitive"],
        "conation": ["Engagement relationnel", "Dévouement", "Volonté d'aider", "Serviabilité", "Hospitalité"],
        "affection": ["Empathie", "Compassion", "Gentillesse", "Bienveillance", "Amour", "Solidarité"]
    },
    "justice": {
        "name": "Justice",
        "forces": ["Travail d'équipe", "Équité", "Leadership"],
        "valeurs_schwartz": ["Égalité", "Responsabilité sociale", "Pouvoir"],
        "qualites_humaines": ["Justice", "Impartialité", "Équité", "Respect des droits", "Intégrité", "Humilité", "Charisme"],
        "competences_oms": ["Prise de décision", "Pensée critique", "Compétences relationnelles"],
        "savoirs_etre": ["Faire preuve de leadership", "Inspirer, donner du sens", "Respecter ses engagements, assumer ses responsabilités"],
        # Structure tripartite CK1
        "cognition": ["Logique", "Cohérence", "Méthodique", "Pragmatisme", "Objectivité", "Lucidité"],
        "conation": ["Leadership", "Engagement collectif", "Responsabilité", "Fermeté", "Esprit d'équipe"],
        "affection": ["Respect", "Équité", "Harmonie", "Conciliation", "Loyauté", "Intégrité"]
    },
    "temperance": {
        "name": "Tempérance",
        "forces": ["Pardon", "Humilité", "Prudence", "Maîtrise de soi"],
        "valeurs_schwartz": ["Conformité", "Sécurité", "Tradition"],
        "qualites_humaines": ["Respect des règles", "Prudence", "Stabilité", "Patience", "Humilité", "Modération", "Gratitude"],
        "competences_oms": ["Gestion des émotions", "Estime de soi", "Résilience"],
        "savoirs_etre": ["Faire preuve de rigueur et de précision", "Organiser son travail selon les priorités et les objectifs"],
        # Structure tripartite CK1
        "cognition": ["Prévoyance", "Prudence", "Raisonnement", "Calme réflexif", "Sobriété de jugement"],
        "conation": ["Discipline", "Constance", "Patience", "Maîtrise de soi", "Rigueur", "Organisation"],
        "affection": ["Modération", "Pardon", "Gratitude", "Sérénité", "Indulgence", "Stabilité émotionnelle"]
    },
    "transcendance": {
        "name": "Transcendance",
        "forces": ["Appréciation de la beauté", "Gratitude", "Espoir", "Humour", "Spiritualité"],
        "valeurs_schwartz": ["Universalisme", "Spiritualité", "Bienveillance"],
        "qualites_humaines": ["Tolérance", "Ouverture d'esprit", "Sagesse", "Gratitude", "Recherche de sens", "Sérénité", "Harmonie"],
        "competences_oms": ["Pensée créative", "Gestion du stress", "Résilience"],
        "savoirs_etre": ["S'adapter aux changements", "Faire preuve d'autonomie"],
        # Structure tripartite CK1
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
    """Fallback template for job match narrative."""
    
    job_label = job.get('label', job.get('intitule_rome', 'ce métier'))
    
    if score >= 80:
        compatibility_text = f"Avec un score de {score}%, le métier de {job_label} présente une excellente compatibilité avec votre profil."
    elif score >= 60:
        compatibility_text = f"Avec un score de {score}%, le métier de {job_label} est compatible avec votre profil et mérite d'être exploré."
    else:
        compatibility_text = f"Avec un score de {score}%, le métier de {job_label} pourrait nécessiter quelques ajustements mais reste accessible."
    
    return {
        "analyse_compatibilite": f"{compatibility_text} {reasons[0] if reasons else ''} Cette adéquation repose sur vos compétences naturelles et votre style de travail.",
        "fiche_metier": job.get('definition', f"Le métier de {job_label} offre des opportunités dans différents secteurs d'activité."),
        "vos_atouts": f"Vos principaux atouts pour ce métier sont : {', '.join(profile['competences_fortes'][:3])}. Ces compétences sont directement mobilisables et vous permettront de vous démarquer.",
        "recommandations": f"Pour maximiser vos chances de réussite, nous vous conseillons de {'développer ' + risks[0].lower() if risks else 'continuer à cultiver vos forces actuelles'}. N'hésitez pas à explorer également des métiers connexes dans le même secteur."
    }


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
        # PDF: Ingénieurs pour INTJ, INTP, ENTP, ISTP
        "mbti_compatible": ["INTJ", "INTP", "ENTP", "ISTP"],
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
        # PDF: Programmeurs analystes -> ISTJ, INTJ, ISTP, INTP, ENTP, ENFP
        "mbti_compatible": ["INTP", "INTJ", "ISTP", "ENTP"],
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
        # PDF: Designers, Décorateurs -> ISFJ, ESFP ; Créateurs -> ISFP ; Artistes -> INFP
        "mbti_compatible": ["ISFP", "INFP", "ISFJ", "ESFP"],
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

WEIGHTS = {
    "motivation": 15,
    "disc": 10,
    "mbti": 35,
    "environment": 20,
    "skills": 15,
    "constraints": 5,
}

# MBTI Compatibility - Types similaires par fonction dominante et mode de fonctionnement
# Correction: Les types Feeling (F) ne sont PAS similaires aux types Thinking (T)
MBTI_SIMILAR = {
    # NF - Les Idéalistes (Intuition + Feeling) - orientés relations et valeurs
    "ENFP": ["INFP", "ENFJ", "INFJ"],          # Tous NF
    "INFP": ["ENFP", "INFJ", "ENFJ"],          # Tous NF (retiré INTP)
    "ENFJ": ["INFJ", "ENFP", "INFP"],          # Tous NF
    "INFJ": ["ENFJ", "INFP", "ENFP"],          # Tous NF
    # NT - Les Rationnels (Intuition + Thinking) - orientés analyse et stratégie
    "ENTP": ["INTP", "ENTJ", "INTJ"],          # Tous NT
    "INTP": ["ENTP", "INTJ", "ENTJ"],          # Tous NT (retiré INFP)
    "ENTJ": ["INTJ", "ENTP", "INTP"],          # Tous NT
    "INTJ": ["ENTJ", "INTP", "ENTP"],          # Tous NT
    # SJ - Les Gardiens (Sensing + Judging) - orientés stabilité et tradition
    "ESTJ": ["ISTJ", "ESFJ", "ISFJ"],          # Tous SJ
    "ISTJ": ["ESTJ", "ISFJ", "ESFJ"],          # Tous SJ
    "ESFJ": ["ISFJ", "ESTJ", "ISTJ"],          # Tous SJ
    "ISFJ": ["ESFJ", "ISTJ", "ESTJ"],          # Tous SJ
    # SP - Les Artisans (Sensing + Perceiving) - orientés action et adaptation
    "ESTP": ["ISTP", "ESFP", "ISFP"],          # Tous SP
    "ISTP": ["ESTP", "ISFP", "ESFP"],          # Tous SP
    "ESFP": ["ISFP", "ESTP", "ISTP"],          # Tous SP
    "ISFP": ["ESFP", "ISTP", "ESTP"],          # Tous SP
}

def mbti_similarity(user_mbti: str, job_mbti_list: List[str]) -> float:
    """Calculate MBTI compatibility score (0-1)."""
    if not job_mbti_list or not user_mbti:
        return 0.5  # Neutral score if no MBTI data
    
    # Exact match = 100%
    if user_mbti in job_mbti_list:
        return 1.0
    
    # Similar type match = 75%
    similar_types = MBTI_SIMILAR.get(user_mbti, [])
    for similar in similar_types:
        if similar in job_mbti_list:
            return 0.75
    
    # Partial match (same temperament or 2+ letters in common)
    for job_mbti in job_mbti_list:
        common_letters = sum(1 for i in range(4) if i < len(user_mbti) and i < len(job_mbti) and user_mbti[i] == job_mbti[i])
        if common_letters >= 3:
            return 0.6
        if common_letters >= 2:
            return 0.4
    
    return 0.2  # Low compatibility

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
    """
    
    # Detect format: visual (v1, v2...) or legacy (q1, q2...)
    is_visual = any(k.startswith("v") for k in answers.keys())
    
    if is_visual:
        # VISUAL QUESTIONNAIRE FORMAT (v1-v12)
        # Énergie (v1, v2)
        energie_e = sum(1 for q in ["v1", "v2"] if answers.get(q) == "E")
        energie_i = sum(1 for q in ["v1", "v2"] if answers.get(q) == "I")
        
        # Perception (v3) - binary question
        perception_s = 1 if answers.get("v3") == "S" else 0
        perception_n = 1 if answers.get("v3") == "N" else 0
        
        # Perception (v4) - RANKING question with S1,S2,N1,N2
        v4_answer = answers.get("v4", "")
        if "," in v4_answer:
            v4_ranks = v4_answer.split(",")
            for idx, val in enumerate(v4_ranks[:4]):
                weight = 4 - idx  # 1st=4, 2nd=3, 3rd=2, 4th=1
                if val.startswith("S"):
                    perception_s += weight
                elif val.startswith("N"):
                    perception_n += weight
        else:
            if v4_answer.startswith("S"):
                perception_s += 1
            elif v4_answer.startswith("N"):
                perception_n += 1
        
        # Décision (v5, v6)
        decision_t = sum(1 for q in ["v5", "v6"] if answers.get(q) == "T")
        decision_f = sum(1 for q in ["v5", "v6"] if answers.get(q) == "F")
        
        # Structure (v7, v8)
        structure_j = sum(1 for q in ["v7", "v8"] if answers.get(q) == "J")
        structure_p = sum(1 for q in ["v7", "v8"] if answers.get(q) == "P")
        
        # DISC (v9, v10) - RANKING questions
        disc_counts = {"D": 0, "I": 0, "S": 0, "C": 0}
        for q in ["v9", "v10"]:
            val = answers.get(q, "")
            if "," in val:
                # Ranking format: "D,I,S,C" - first choice gets highest weight
                ranks = val.split(",")
                for idx, disc_val in enumerate(ranks[:4]):
                    disc_val = disc_val.strip().upper()
                    if disc_val in disc_counts:
                        weight = 4 - idx  # 1st=4, 2nd=3, 3rd=2, 4th=1
                        disc_counts[disc_val] += weight
            elif val in disc_counts:
                disc_counts[val] += 4  # Single choice gets full weight
        
        # Ennéagramme (v11, v12) - RANKING questions
        ennea_counts = {str(i): 0 for i in range(1, 10)}
        for q in ["v11", "v12"]:
            val = answers.get(q, "")
            if "," in val:
                # Ranking format: "7,2,4,3" - first choice gets highest weight
                ranks = val.split(",")
                for idx, ennea_val in enumerate(ranks[:4]):
                    ennea_val = ennea_val.strip()
                    if ennea_val in ennea_counts:
                        weight = 4 - idx  # 1st=4, 2nd=3, 3rd=2, 4th=1
                        ennea_counts[ennea_val] += weight
            elif val in ennea_counts:
                ennea_counts[val] += 4  # Single choice gets full weight
    else:
        # LEGACY QUESTIONNAIRE FORMAT (q1-q15)
        # Count MBTI dimensions
        energie_e = sum(1 for q in ["q1", "q2"] if answers.get(q) == "E")
        energie_i = sum(1 for q in ["q1", "q2"] if answers.get(q) == "I")
        
        perception_s = sum(1 for q in ["q4", "q6"] if answers.get(q) == "S")
        perception_n = sum(1 for q in ["q4", "q6"] if answers.get(q) == "N")
        
        decision_t = sum(1 for q in ["q5"] if answers.get(q) == "T")
        decision_f = sum(1 for q in ["q5"] if answers.get(q) == "F")
        
        structure_j = sum(1 for q in ["q7"] if answers.get(q) == "J")
        structure_p = sum(1 for q in ["q7"] if answers.get(q) == "P")
        
        # Count DISC
        disc_counts = {"D": 0, "I": 0, "S": 0, "C": 0}
        for q in ["q3", "q8", "q9", "q13", "q14", "q15"]:
            val = answers.get(q)
            if val in disc_counts:
                disc_counts[val] += 1
        
        # Count Enneagram
        ennea_counts = {str(i): 0 for i in range(1, 10)}
        for q in ["q10", "q11", "q12"]:
            val = answers.get(q)
            if val in ennea_counts:
                ennea_counts[val] += 1
    
    # Determine dominant values
    energie = "E" if energie_e >= energie_i else "I"
    perception = "S" if perception_s >= perception_n else "N"
    decision = "T" if decision_t >= decision_f else "F"
    structure = "J" if structure_j >= structure_p else "P"
    
    disc = max(disc_counts, key=disc_counts.get)
    
    sorted_ennea = sorted(ennea_counts.items(), key=lambda x: x[1], reverse=True)
    ennea_dominant = int(sorted_ennea[0][0]) if sorted_ennea[0][1] > 0 else 5
    ennea_runner_up = int(sorted_ennea[1][0]) if len(sorted_ennea) > 1 and sorted_ennea[1][1] > 0 else ennea_dominant
    
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
    """Calculate DISC similarity score."""
    user_disc = user_disc.upper()
    best = 0.0
    for d in job_discs:
        d = d.upper()
        if user_disc == d:
            sim = 1.0
        elif d in DISC_ADJACENT.get(user_disc, set()):
            sim = 0.6
        else:
            sim = 0.3
        best = max(best, sim)
    return best if job_discs else 0.5


def ennea_similarity(dominant: int, runner_up: int, compatible_list: List[int]) -> float:
    """Calculate Enneagram similarity score."""
    if not compatible_list:
        return 0.5
    if dominant in compatible_list:
        return 1.0
    if runner_up in compatible_list:
        return 0.6
    return 0.2


def score_environment(profile: Dict[str, Any], job: Dict[str, Any]) -> float:
    """Calculate environment compatibility score."""
    points = []
    
    # Interaction preference
    interaction = job.get("interaction", 1)
    if profile["energie"] == "E":
        points.append(1.0 if interaction >= 1 else 0.5)
    else:
        points.append(1.0 if interaction <= 1 else 0.5)
    
    # Cadre preference
    cadre = job.get("cadre", 1)
    if profile["structure"] == "J":
        points.append(1.0 if cadre >= 1 else 0.5)
    else:
        points.append(1.0 if cadre <= 1 else 0.5)
    
    # Complexity preference
    complexite = job.get("complexite", 1)
    if profile["perception"] == "N":
        points.append(1.0 if complexite >= 1 else 0.7)
    else:
        points.append(1.0 if complexite <= 1 else 0.7)
    
    # Rythme with vigilance
    rythme = job.get("rythme", 1)
    if any(v in str(profile.get("vigilances", [])) for v in ["stress", "surmenage", "perfectionnisme"]):
        points.append(0.6 if rythme == 2 else 1.0)
    else:
        points.append(1.0)
    
    return sum(points) / len(points) if points else 0.7


def score_skills(profile: Dict[str, Any], job: Dict[str, Any]) -> float:
    """Calculate skills match score."""
    req = job.get("competences_requises", [])
    if not req:
        return 0.5
    
    user_skills = set(s.lower() for s in profile.get("competences_fortes", []))
    job_skills = set(s.lower() for s in req)
    
    intersection = len(user_skills & job_skills)
    return min(1.0, intersection / min(5, len(req)))


def score_job(profile: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate overall job compatibility score."""
    
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
    
    # MBTI score (NEW)
    mbti_score = mbti_similarity(
        profile.get("mbti", ""),
        job.get("mbti_compatible", [])
    ) * WEIGHTS["mbti"]
    
    # Environment score
    env_score = score_environment(profile, job) * WEIGHTS["environment"]
    
    # Skills score
    skills_score = score_skills(profile, job) * WEIGHTS["skills"]
    
    # Constraints (simplified - full score for now)
    constraints_score = WEIGHTS["constraints"] * 1.0
    
    total = int(round(motivation_score + disc_score + mbti_score + env_score + skills_score + constraints_score))
    total = max(0, min(100, total))
    
    # Build reasons and risks
    reasons = []
    risks = []
    
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
    
    return {
        "job_id": job["id"],
        "job_label": job["label"],
        "filiere": job.get("filiere", ""),
        "secteur": job.get("secteur", ""),
        "score": total,
        "category": category,
        "reasons": reasons[:3],
        "risks": risks[:2],
        "breakdown": {
            "motivation": round(motivation_score, 1),
            "disc": round(disc_score, 1),
            "mbti": round(mbti_score, 1),
            "environment": round(env_score, 1),
            "skills": round(skills_score, 1),
            "constraints": round(constraints_score, 1)
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


def get_exploration_paths(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get recommended filieres and jobs for exploration."""
    # Score all jobs
    all_scores = [score_job(profile, job) for job in METIERS]
    all_scores.sort(key=lambda x: x["score"], reverse=True)
    
    # Group by filiere
    filiere_jobs = {}
    for score_result in all_scores:
        filiere = score_result["filiere"]
        if filiere not in filiere_jobs:
            filiere_jobs[filiere] = []
        filiere_jobs[filiere].append(score_result)
    
    # Build exploration paths
    MIN_COMPATIBILITY_SCORE = 50  # Lowered from 75 to show more filières
    paths = []
    for filiere_id, jobs in filiere_jobs.items():
        if not jobs:
            continue
        
        filiere_info = next((f for f in FILIERES if f["id"] == filiere_id), None)
        if not filiere_info:
            continue
        
        # Consider jobs with score >= 50% for the filiere
        compatible_jobs = [j for j in jobs if j["score"] >= MIN_COMPATIBILITY_SCORE]
        
        # If no jobs at 50%, take top 2 jobs regardless of score
        if not compatible_jobs:
            compatible_jobs = jobs[:2]
        
        if not compatible_jobs:
            continue
        
        avg_score = sum(j["score"] for j in compatible_jobs) / len(compatible_jobs)
        top_jobs = sorted(compatible_jobs, key=lambda x: x["score"], reverse=True)[:5]  # Show up to 5 jobs per filière
        
        paths.append({
            "filiere": filiere_info["name"],
            "filiere_id": filiere_id,
            "avg_compatibility": round(avg_score),
            "secteurs": filiere_info["secteurs"][:4],
            "indicative_jobs": [j["job_label"] for j in top_jobs],
            "top_match": top_jobs[0] if top_jobs else None
        })
    
    # Sort by average compatibility
    paths.sort(key=lambda x: x["avg_compatibility"], reverse=True)
    return paths[:8]  # Return up to 8 filières instead of 5


# ============================================================================
# API ROUTES
# ============================================================================

@api_router.get("/")
async def root():
    return {"message": "RE'ACTIF PRO - Intelligence Professionnelle API"}


@api_router.get("/status/france-travail")
async def get_france_travail_status():
    """Vérifier le statut de l'intégration France Travail."""
    return {
        "enabled": is_france_travail_enabled(),
        "message": "API France Travail configurée" if is_france_travail_enabled() else "API France Travail non configurée. Configurez FRANCE_TRAVAIL_CLIENT_ID et FRANCE_TRAVAIL_CLIENT_SECRET pour accéder à 1500+ métiers officiels."
    }


@api_router.get("/status/esco")
async def get_esco_status():
    """Vérifier le statut de l'intégration ESCO (European Skills/Occupations)."""
    return esco_api_status()


@api_router.get("/esco/search")
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


@api_router.get("/esco/occupation")
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


@api_router.get("/questionnaire")
async def get_questionnaire():
    """Get the complete questionnaire (legacy text format)."""
    return {"questions": QUESTIONNAIRE, "total": len(QUESTIONNAIRE)}


@api_router.get("/questionnaire/visual")
async def get_visual_questionnaire():
    """Get the visual questionnaire with images for accessibility."""
    return {"questions": VISUAL_QUESTIONS, "total": len(VISUAL_QUESTIONS), "format": "visual"}


@api_router.get("/filieres")
async def get_filieres():
    """Get all professional filieres."""
    return {"filieres": FILIERES}


@api_router.get("/metiers")
async def get_metiers():
    """Get all jobs."""
    return {"metiers": METIERS}


@api_router.post("/compute-profile")
async def compute_user_profile(request: QuestionnaireResponse):
    """Compute user profile from answers."""
    profile = compute_profile(request.answers)
    
    # Save to database
    profile_doc = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "answers": request.answers,
        **profile
    }
    await db.profiles.insert_one(profile_doc)
    
    return {"profile": profile}


@api_router.post("/job-match")
async def match_job(request: JobSearchRequest):
    """Match user profile with a specific job."""
    profile = compute_profile(request.answers)
    
    # Recherche hybride : base locale + France Travail API
    matching_jobs, france_travail_fiche = await search_job_hybrid(request.job_query)
    
    if not matching_jobs:
        raise HTTPException(status_code=404, detail="Aucun métier trouvé pour cette recherche")
    
    # Score all matching jobs - preserve search order for best_match selection
    results = [score_job(profile, job) for job in matching_jobs]
    
    # IMPORTANT: For job-match endpoint, the best_match should be the FIRST job from search results
    # (which is the most relevant to the query), not the one with highest profile compatibility.
    # We still compute profile scores for other_matches display, but the search relevance takes priority.
    # Sort other_matches by profile score for alternatives display
    results_sorted_by_profile = sorted(results, key=lambda x: x["score"], reverse=True)
    
    # Get profile info for Enneagram
    ennea_profile = ENNEA_TO_PROFILE.get(profile["ennea_dominant"], ENNEA_TO_PROFILE[5])
    vertu_key = ennea_profile["vertu"]
    vertu_data = VERTUS.get(vertu_key, VERTUS["sagesse"])
    
    # Get life path data if birth_date provided
    life_path_data = None
    if request.birth_date:
        life_path_data = get_life_path_data(request.birth_date)
    
    # Generate AI narratives
    profile_narrative = await generate_profile_narrative(profile, ennea_profile, vertu_data, life_path_data)
    
    # Get zones de vigilance (Cadran d'Ofman)
    zones_vigilance = get_zones_vigilance_for_profile(profile, vertu_data)
    
    best_match = results[0] if results else None
    job_narrative = None
    matched_job = None
    
    # Si France Travail a trouvé un métier, l'utiliser en priorité pour best_match
    if france_travail_fiche:
        # Créer un best_match basé sur la fiche France Travail
        best_match = {
            "job_id": france_travail_fiche.get("code_rome"),
            "job_label": france_travail_fiche.get("intitule_rome"),
            "secteur": "Référentiel ROME officiel",
            "filiere": france_travail_fiche.get("code_rome", "")[:1],  # Première lettre = domaine
            "score": results[0]["score"] if results else 65,  # Score basé sur le profil
            "reasons": results[0].get("reasons", []) if results else [],
            "risks": results[0].get("risks", []) if results else [],
            "source": "france_travail"
        }
        matched_job = france_travail_fiche
    elif best_match:
        matched_job = next((j for j in matching_jobs if j["id"] == best_match["job_id"]), matching_jobs[0])
    
    if matched_job:
        job_narrative = await generate_job_match_narrative(
            profile, 
            matched_job, 
            best_match["score"] if best_match else 50,
            best_match.get("reasons", []) if best_match else [],
            best_match.get("risks", []) if best_match else []
        )
    
    # Prepare job info - Priorité à France Travail si disponible, puis ESCO, puis local
    job_info = None
    esco_details = None
    
    # Try to get ESCO details for enrichment
    if request.job_query:
        esco_results = await search_occupations_esco(request.job_query, limit=1, language="fr")
        if esco_results:
            esco_uri = esco_results[0].get("uri")
            if esco_uri:
                esco_details = await get_occupation_details_esco(esco_uri, language="fr")
    
    if france_travail_fiche:
        # Utiliser la fiche France Travail (données officielles)
        job_info = {
            "code_rome": france_travail_fiche.get("code_rome"),
            "intitule_rome": france_travail_fiche.get("intitule_rome"),
            "definition": france_travail_fiche.get("definition"),
            "acces_emploi": france_travail_fiche.get("acces_emploi"),
            "soft_skills_essentiels": france_travail_fiche.get("soft_skills_essentiels", []),
            "hard_skills_essentiels": france_travail_fiche.get("hard_skills_essentiels", []),
            "source": "france_travail"
        }
    elif esco_details:
        # Utiliser ESCO (base européenne 3000+ métiers)
        job_info = {
            "code_esco": esco_details.get("code_esco"),
            "intitule_esco": esco_details.get("title"),
            "definition": esco_details.get("description"),
            "acces_emploi": "",
            "soft_skills_essentiels": esco_details.get("essential_skills", [])[:6],
            "hard_skills_essentiels": esco_details.get("optional_skills", [])[:6],
            "all_skills": esco_details.get("all_skills", []),
            "source": "esco"
        }
    elif best_match and matched_job:
        # Fallback sur la base locale
        job_info = {
            "code_rome": matched_job.get("code_rome"),
            "intitule_rome": matched_job.get("intitule_rome"),
            "definition": matched_job.get("definition"),
            "acces_emploi": matched_job.get("acces_emploi"),
            "soft_skills_essentiels": matched_job.get("soft_skills_essentiels", []),
            "hard_skills_essentiels": matched_job.get("hard_skills_essentiels", []),
            "source": "local"
        }
    
    # Generate cross-analysis between Numerology x DISC x MBTI x Enneagram
    cross_analysis = None
    if life_path_data:
        cross_analysis = get_cross_analysis(life_path_data, profile, profile["ennea_dominant"])
    
    # NEW: Generate functioning compass (Boussole de Fonctionnement)
    functioning_compass = get_functioning_compass(profile)
    
    # NEW: Generate integrated analysis (3 levels of reading)
    integrated_analysis = get_integrated_analysis(profile, vertu_data, life_path_data, zones_vigilance)
    
    # Si le score est inférieur à 70%, proposer des métiers alternatifs avec score >= 70%
    suggested_jobs = []
    current_score = best_match.get("score", 0) if best_match else 0
    
    if current_score < 70:
        # Calculer les scores pour tous les métiers de la base locale
        all_job_scores = [score_job(profile, job) for job in METIERS]
        all_job_scores.sort(key=lambda x: x["score"], reverse=True)
        
        # Filtrer les métiers avec score >= 70%
        high_score_jobs = [j for j in all_job_scores if j["score"] >= 70]
        
        # Prendre les 5 meilleurs (différents du métier recherché)
        for job_score in high_score_jobs[:5]:
            job_data = next((j for j in METIERS if j["id"] == job_score["job_id"]), None)
            if job_data:
                suggested_jobs.append({
                    "job_id": job_score["job_id"],
                    "job_label": job_score["job_label"],
                    "secteur": job_score["secteur"],
                    "filiere": job_score["filiere"],
                    "score": job_score["score"],
                    "code_rome": job_data.get("code_rome", ""),
                    "reasons": job_score.get("reasons", [])[:2]
                })
    
    # Add ESCO info to response
    esco_enrichment = None
    if esco_details:
        esco_enrichment = {
            "title": esco_details.get("title"),
            "uri": esco_details.get("uri"),
            "essential_skills": esco_details.get("essential_skills", [])[:8],
            "optional_skills": esco_details.get("optional_skills", [])[:8]
        }
    
    return {
        "profile_summary": {
            "competences_fortes": profile["competences_fortes"],
            "dominant_vertus": profile["dominant_vertus"],
            "disc_scores": profile.get("disc_scores", {"D": 0, "I": 0, "S": 0, "C": 0}),
            "disc_dominant": profile.get("disc", "S")
        },
        "profile_narrative": profile_narrative,
        "vertus_data": vertu_data,
        "zones_vigilance": zones_vigilance,
        "life_path": life_path_data,
        "cross_analysis": cross_analysis,
        "functioning_compass": functioning_compass,
        "integrated_analysis": integrated_analysis,
        "best_match": best_match,
        "job_info": job_info,
        "job_narrative": job_narrative,
        "other_matches": results_sorted_by_profile[1:5] if len(results_sorted_by_profile) > 1 else [],
        "suggested_jobs": suggested_jobs,  # Métiers suggérés si score < 70%
        "esco_enrichment": esco_enrichment,  # Données ESCO si disponibles
        "france_travail_enabled": is_france_travail_enabled(),
        "esco_enabled": is_esco_enabled()
    }


@api_router.post("/explore")
async def explore_careers(request: ExploreRequest):
    """Explore career paths based on profile."""
    profile = compute_profile(request.answers)
    
    # Get exploration paths
    paths = get_exploration_paths(profile)
    
    # Get all job scores and filter by minimum compatibility (>= 75%)
    all_scores = [score_job(profile, job) for job in METIERS]
    all_scores.sort(key=lambda x: x["score"], reverse=True)
    
    # Only keep jobs with score >= 50% (lowered from 75%)
    MIN_COMPATIBILITY_SCORE = 50
    compatible_jobs = [job for job in all_scores if job["score"] >= MIN_COMPATIBILITY_SCORE]
    
    # If not enough compatible jobs, take top 10 with score >= 40%
    if len(compatible_jobs) < 10:
        compatible_jobs = [job for job in all_scores if job["score"] >= 40][:10]
    
    # Limit to top 10 compatible jobs
    top_jobs = compatible_jobs[:10]
    
    # Get profile info
    ennea_profile = ENNEA_TO_PROFILE.get(profile["ennea_dominant"], ENNEA_TO_PROFILE[5])
    vertu_key = ennea_profile["vertu"]
    vertu_data = VERTUS.get(vertu_key, VERTUS["sagesse"])
    
    # Get life path data if birth_date provided
    life_path_data = None
    if request.birth_date:
        life_path_data = get_life_path_data(request.birth_date)
    
    # Generate AI narrative for profile
    profile_narrative = await generate_profile_narrative(profile, ennea_profile, vertu_data, life_path_data)
    
    # Get zones de vigilance (Cadran d'Ofman)
    zones_vigilance = get_zones_vigilance_for_profile(profile, vertu_data)
    
    # Generate cross-analysis between Numerology x DISC x MBTI x Enneagram
    cross_analysis = None
    if life_path_data:
        cross_analysis = get_cross_analysis(life_path_data, profile, profile["ennea_dominant"])
    
    # NEW: Generate functioning compass (Boussole de Fonctionnement)
    functioning_compass = get_functioning_compass(profile)
    
    # NEW: Generate integrated analysis (3 levels of reading)
    integrated_analysis = get_integrated_analysis(profile, vertu_data, life_path_data, zones_vigilance)
    
    return {
        "profile": profile,  # Include full profile with MBTI
        "profile_summary": {
            "mbti": profile.get("mbti", ""),
            "competences_fortes": profile["competences_fortes"],
            "dominant_vertus": profile["dominant_vertus"],
            "disc_scores": profile.get("disc_scores", {"D": 0, "I": 0, "S": 0, "C": 0}),
            "disc_dominant": profile.get("disc", "S")
        },
        "profile_narrative": profile_narrative,
        "vertus_data": vertu_data,
        "zones_vigilance": zones_vigilance,
        "life_path": life_path_data,
        "cross_analysis": cross_analysis,
        "functioning_compass": functioning_compass,
        "integrated_analysis": integrated_analysis,
        "exploration_paths": paths,
        "top_jobs": top_jobs  # Top 10 métiers compatibles
    }


@api_router.get("/vertus")
async def get_vertus():
    """Get all vertus with their details."""
    return {"vertus": VERTUS}


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
