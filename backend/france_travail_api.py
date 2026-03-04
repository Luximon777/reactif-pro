"""
France Travail API Integration
API ROME 4.0 - Fiches Métiers et Référentiels

Documentation: https://francetravail.io/data/api
Endpoints:
- rome-fiches-metiers: Fiches métiers détaillées
- rome-metiers: Liste et recherche de métiers
"""

import os
import httpx
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
FRANCE_TRAVAIL_CLIENT_ID = os.environ.get('FRANCE_TRAVAIL_CLIENT_ID', '')
FRANCE_TRAVAIL_CLIENT_SECRET = os.environ.get('FRANCE_TRAVAIL_CLIENT_SECRET', '')

# API Endpoints
TOKEN_URL = "https://entreprise.francetravail.fr/connexion/oauth2/access_token"
BASE_URL = "https://api.francetravail.io/partenaire"
ROME_METIERS_URL = f"{BASE_URL}/rome-metiers/v1/metier"
ROME_FICHES_URL = f"{BASE_URL}/rome-fiches-metiers/v1/ficheMetier"

# Token cache
_token_cache = {
    "access_token": None,
    "expires_at": None
}

logger = logging.getLogger(__name__)


def is_france_travail_enabled() -> bool:
    """Check if France Travail API is configured."""
    return bool(FRANCE_TRAVAIL_CLIENT_ID and FRANCE_TRAVAIL_CLIENT_SECRET)


async def get_access_token() -> Optional[str]:
    """Get OAuth2 access token (with caching)."""
    global _token_cache
    
    # Check if cached token is still valid
    if _token_cache["access_token"] and _token_cache["expires_at"]:
        if datetime.now() < _token_cache["expires_at"]:
            return _token_cache["access_token"]
    
    if not is_france_travail_enabled():
        logger.warning("France Travail API credentials not configured")
        return None
    
    try:
        async with httpx.AsyncClient() as client:
            # OAuth2 client credentials flow
            response = await client.post(
                TOKEN_URL,
                params={"realm": "/partenaire"},
                data={
                    "grant_type": "client_credentials",
                    "client_id": FRANCE_TRAVAIL_CLIENT_ID,
                    "client_secret": FRANCE_TRAVAIL_CLIENT_SECRET,
                    "scope": f"api_rome-fiches-metiersv1 api_rome-metiersv1 application_{FRANCE_TRAVAIL_CLIENT_ID}"
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                access_token = data.get("access_token")
                expires_in = data.get("expires_in", 1500)  # Default 25 minutes
                
                # Cache the token
                _token_cache["access_token"] = access_token
                _token_cache["expires_at"] = datetime.now() + timedelta(seconds=expires_in - 60)
                
                logger.info("France Travail token obtained successfully")
                return access_token
            else:
                logger.error(f"Token request failed: {response.status_code} - {response.text}")
                return None
                
    except Exception as e:
        logger.error(f"Error getting France Travail token: {e}")
        return None


async def search_job_france_travail(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search jobs in France Travail ROME database.
    Returns list of matching jobs with code_rome and label.
    """
    if not is_france_travail_enabled():
        return []
    
    token = await get_access_token()
    if not token:
        return []
    
    try:
        async with httpx.AsyncClient() as client:
            # Search in ROME métiers
            response = await client.get(
                f"{ROME_METIERS_URL}/recherche",
                params={
                    "motsCles": query,
                    "nombre": limit
                },
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/json"
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                results = response.json()
                jobs = []
                
                # Parse results - structure may vary
                if isinstance(results, list):
                    for item in results[:limit]:
                        jobs.append({
                            "code_rome": item.get("code") or item.get("codeRome"),
                            "label": item.get("libelle") or item.get("appellationCourt"),
                            "intitule_rome": item.get("libelleRome") or item.get("libelle"),
                            "source": "france_travail"
                        })
                elif isinstance(results, dict):
                    items = results.get("metiers", results.get("appellations", []))
                    for item in items[:limit]:
                        jobs.append({
                            "code_rome": item.get("code") or item.get("codeRome"),
                            "label": item.get("libelle") or item.get("appellationCourt"),
                            "intitule_rome": item.get("libelleRome") or item.get("libelle"),
                            "source": "france_travail"
                        })
                
                logger.info(f"France Travail search '{query}': {len(jobs)} results")
                return jobs
            else:
                logger.warning(f"France Travail search failed: {response.status_code}")
                return []
                
    except Exception as e:
        logger.error(f"Error searching France Travail: {e}")
        return []


async def get_job_info_france_travail(code_rome: str) -> Optional[Dict[str, Any]]:
    """
    Get detailed job information from France Travail ROME fiche métier.
    Returns structured job data including skills, access conditions, etc.
    """
    if not is_france_travail_enabled():
        return None
    
    if not code_rome:
        return None
    
    token = await get_access_token()
    if not token:
        return None
    
    try:
        async with httpx.AsyncClient() as client:
            # Get fiche métier by code ROME
            response = await client.get(
                f"{ROME_FICHES_URL}/{code_rome}",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/json"
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                fiche = response.json()
                
                # Extract and structure the data
                job_info = {
                    "code_rome": code_rome,
                    "intitule_rome": fiche.get("metier", {}).get("libelle") or fiche.get("libelle"),
                    "definition": fiche.get("definition") or fiche.get("metier", {}).get("definition"),
                    "acces_emploi": extract_acces_emploi(fiche),
                    "soft_skills_essentiels": extract_soft_skills(fiche),
                    "hard_skills_essentiels": extract_hard_skills(fiche),
                    "contextes_travail": extract_contextes(fiche),
                    "mobilite": extract_mobilite(fiche),
                    "source": "france_travail"
                }
                
                logger.info(f"France Travail fiche retrieved: {code_rome}")
                return job_info
            else:
                logger.warning(f"France Travail fiche not found: {code_rome} ({response.status_code})")
                return None
                
    except Exception as e:
        logger.error(f"Error getting France Travail fiche: {e}")
        return None


def extract_acces_emploi(fiche: Dict) -> str:
    """Extract employment access conditions from fiche."""
    acces = fiche.get("conditionsExercice", {}).get("accesEmploi")
    if acces:
        return acces
    
    # Try alternative paths
    formations = fiche.get("formations", [])
    if formations:
        return ", ".join([f.get("libelle", "") for f in formations[:3]])
    
    return ""


def extract_soft_skills(fiche: Dict) -> List[Dict[str, str]]:
    """Extract soft skills/savoir-être from fiche."""
    soft_skills = []
    
    # Try different possible paths in the API response
    savoirs_etre = fiche.get("savoirEtre", []) or fiche.get("savoirsEtre", [])
    
    for skill in savoirs_etre[:6]:
        if isinstance(skill, dict):
            soft_skills.append({
                "nom": skill.get("libelle", ""),
                "importance": "importante",
                "description": skill.get("definition", "")
            })
        elif isinstance(skill, str):
            soft_skills.append({
                "nom": skill,
                "importance": "importante",
                "description": ""
            })
    
    return soft_skills


def extract_hard_skills(fiche: Dict) -> List[Dict[str, str]]:
    """Extract hard skills/compétences techniques from fiche."""
    hard_skills = []
    
    # Competences from fiche
    competences = fiche.get("competences", []) or fiche.get("competencesMobilisees", [])
    
    for comp in competences[:8]:
        if isinstance(comp, dict):
            hard_skills.append({
                "nom": comp.get("libelle", ""),
                "importance": "critique" if comp.get("riasecMajeur") else "importante",
                "description": comp.get("definition", "")
            })
        elif isinstance(comp, str):
            hard_skills.append({
                "nom": comp,
                "importance": "importante",
                "description": ""
            })
    
    return hard_skills


def extract_contextes(fiche: Dict) -> List[str]:
    """Extract work contexts from fiche."""
    contextes = []
    
    ctx_list = fiche.get("contexteTravail", []) or fiche.get("contextesTravail", [])
    
    for ctx in ctx_list[:5]:
        if isinstance(ctx, dict):
            contextes.append(ctx.get("libelle", ""))
        elif isinstance(ctx, str):
            contextes.append(ctx)
    
    return contextes


def extract_mobilite(fiche: Dict) -> Dict[str, List[str]]:
    """Extract career mobility information from fiche."""
    mobilite = {
        "metiers_proches": [],
        "evolutions_possibles": []
    }
    
    # Métiers proches
    proches = fiche.get("metiersProches", []) or fiche.get("mobilitesProfessionnelles", {}).get("metiersProches", [])
    for m in proches[:5]:
        if isinstance(m, dict):
            mobilite["metiers_proches"].append(m.get("libelle", ""))
        elif isinstance(m, str):
            mobilite["metiers_proches"].append(m)
    
    # Evolutions
    evolutions = fiche.get("evolutionsPossibles", []) or fiche.get("mobilitesProfessionnelles", {}).get("evolutions", [])
    for e in evolutions[:5]:
        if isinstance(e, dict):
            mobilite["evolutions_possibles"].append(e.get("libelle", ""))
        elif isinstance(e, str):
            mobilite["evolutions_possibles"].append(e)
    
    return mobilite


# Utility function for API status
def france_travail_api():
    """Return API configuration status."""
    return {
        "enabled": is_france_travail_enabled(),
        "client_id_configured": bool(FRANCE_TRAVAIL_CLIENT_ID),
        "endpoints": {
            "token": TOKEN_URL,
            "metiers": ROME_METIERS_URL,
            "fiches": ROME_FICHES_URL
        }
    }
