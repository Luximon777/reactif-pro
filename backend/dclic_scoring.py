"""D'CLIC PRO — Moteur de scoring et calcul de profils
Source: GitHub Luximon777/declic-pro
"""
from typing import Dict, List, Any
import logging

from dclic_data import (
    VERTUS, ARCHEOLOGIE_COMPETENCES, TABLEAU_CK,
    RIASEC_DESCRIPTIONS, RIASEC_ADJACENT, RIASEC_OPPOSITE,
    MBTI_TO_VERTU_FALLBACK, ZONES_VIGILANCE, DISC_OFMAN,
    MBTI_ENERGIE_OFMAN, ENNEA_OFMAN, LIFE_PATHS,
    ROME_RIASEC_MAPPING, FILIERES, METIERS, METIER_TO_VERTU,
    get_vertu_for_metier
)

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
        "tension": tensions_disc.get(synergy_key_disc, "L'équilibre entre vos différentes facettes constitue à la fois un défi et une richesse. Apprenez à valoriser cette complémentarité."),
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
    
    if not cross_analysis["integration_insight"]:
        cross_analysis["integration_insight"] = "Votre profil unique combine des forces complémentaires. Cultivez cette diversité comme un avantage professionnel."
    
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


DISC_ADJACENT = {
    "D": {"I", "C"},
    "I": {"D", "S"},
    "S": {"I", "C"},
    "C": {"D", "S"},
}


# Adjacence des Vertus pour calculer la cohérence
VERTU_ADJACENT = {
    "sagesse": {"temperance", "justice"},
    "courage": {"justice", "transcendance"},
    "humanite": {"justice", "transcendance"},
    "justice": {"sagesse", "courage", "humanite"},
    "temperance": {"sagesse", "courage"},
    "transcendance": {"courage", "humanite"},
}

def calculate_vertu_coherence(user_vertu_key: str, metier_id: str) -> float:
    """Calculate coherence between user's dominant virtue and job's natural virtue.
    Returns: 1.0 (perfect match), 0.7 (adjacent), 0.3 (distant)
    """
    metier_vertu = get_vertu_for_metier(metier_id)
    if not user_vertu_key or not metier_vertu:
        return 0.5
    if user_vertu_key == metier_vertu:
        return 1.0
    if metier_vertu in VERTU_ADJACENT.get(user_vertu_key, set()):
        return 0.7
    return 0.3



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
