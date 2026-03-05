"""
ESCO API Integration
European Skills, Competences, Qualifications and Occupations

API Documentation: https://ec.europa.eu/esco/api/doc/esco_api_doc.html
Base URL: https://ec.europa.eu/esco/api

This API provides access to 3000+ occupations with skills and competences.
No authentication required - completely free to use.
"""

import httpx
import logging
from typing import Optional, Dict, Any, List

# API Configuration
ESCO_BASE_URL = "https://ec.europa.eu/esco/api"
ESCO_SEARCH_URL = f"{ESCO_BASE_URL}/search"
ESCO_RESOURCE_URL = f"{ESCO_BASE_URL}/resource/occupation"

logger = logging.getLogger(__name__)

# Cache for occupation details
_occupation_cache = {}


def is_esco_enabled() -> bool:
    """ESCO API is always available - no credentials needed."""
    return True


async def search_occupations_esco(query: str, limit: int = 20, language: str = "fr") -> List[Dict[str, Any]]:
    """
    Search occupations in ESCO database.
    
    Args:
        query: Search text (e.g., "recrutement", "développeur")
        limit: Maximum number of results (default 20)
        language: Language code (default "fr" for French)
    
    Returns:
        List of occupations with title, uri, and description
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                ESCO_SEARCH_URL,
                params={
                    "text": query,
                    "language": language,
                    "type": "occupation",
                    "limit": limit,
                    "full": "true"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("_embedded", {}).get("results", [])
                
                occupations = []
                for r in results:
                    occupations.append({
                        "uri": r.get("uri", ""),
                        "title": r.get("title", ""),
                        "label": r.get("title", ""),  # Alias for compatibility
                        "description": r.get("description", ""),
                        "code_esco": extract_esco_code(r.get("uri", "")),
                        "source": "esco"
                    })
                
                logger.info(f"ESCO search '{query}': {len(occupations)} results")
                return occupations
            else:
                logger.warning(f"ESCO search failed: {response.status_code}")
                return []
                
    except Exception as e:
        logger.error(f"Error searching ESCO: {e}")
        return []


async def get_occupation_details_esco(uri: str, language: str = "fr") -> Optional[Dict[str, Any]]:
    """
    Get detailed information about an occupation from ESCO.
    
    Args:
        uri: ESCO occupation URI
        language: Language code
    
    Returns:
        Detailed occupation data including skills and competences
    """
    # Check cache first
    cache_key = f"{uri}_{language}"
    if cache_key in _occupation_cache:
        return _occupation_cache[cache_key]
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                ESCO_RESOURCE_URL,
                params={
                    "uri": uri,
                    "language": language
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract skills
                essential_skills = []
                optional_skills = []
                
                if "_links" in data:
                    links = data["_links"]
                    
                    # Essential skills
                    if "hasEssentialSkill" in links:
                        skills = links["hasEssentialSkill"]
                        if isinstance(skills, list):
                            essential_skills = [{"nom": s.get("title", ""), "importance": "critique"} for s in skills[:10]]
                        elif isinstance(skills, dict):
                            essential_skills = [{"nom": skills.get("title", ""), "importance": "critique"}]
                    
                    # Optional skills
                    if "hasOptionalSkill" in links:
                        skills = links["hasOptionalSkill"]
                        if isinstance(skills, list):
                            optional_skills = [{"nom": s.get("title", ""), "importance": "importante"} for s in skills[:10]]
                        elif isinstance(skills, dict):
                            optional_skills = [{"nom": skills.get("title", ""), "importance": "importante"}]
                
                occupation_details = {
                    "uri": uri,
                    "code_esco": extract_esco_code(uri),
                    "title": data.get("title", ""),
                    "description": data.get("description", ""),
                    "definition": data.get("description", ""),
                    "essential_skills": essential_skills,
                    "optional_skills": optional_skills,
                    "all_skills": essential_skills + optional_skills,
                    "source": "esco"
                }
                
                # Cache the result
                _occupation_cache[cache_key] = occupation_details
                
                logger.info(f"ESCO occupation retrieved: {data.get('title', uri)}")
                return occupation_details
            else:
                logger.warning(f"ESCO occupation not found: {uri} ({response.status_code})")
                return None
                
    except Exception as e:
        logger.error(f"Error getting ESCO occupation: {e}")
        return None


async def get_occupations_by_skill(skill: str, limit: int = 10, language: str = "fr") -> List[Dict[str, Any]]:
    """
    Find occupations that require a specific skill.
    
    Args:
        skill: Skill name to search for
        limit: Maximum results
        language: Language code
    
    Returns:
        List of occupations requiring this skill
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # First search for the skill
            response = await client.get(
                ESCO_SEARCH_URL,
                params={
                    "text": skill,
                    "language": language,
                    "type": "skill",
                    "limit": 1
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                skills = data.get("_embedded", {}).get("results", [])
                
                if skills:
                    skill_uri = skills[0].get("uri", "")
                    
                    # Get occupations for this skill
                    skill_response = await client.get(
                        f"{ESCO_BASE_URL}/resource/skill",
                        params={
                            "uri": skill_uri,
                            "language": language
                        }
                    )
                    
                    if skill_response.status_code == 200:
                        skill_data = skill_response.json()
                        
                        occupations = []
                        links = skill_data.get("_links", {})
                        
                        # Get occupations that require this skill
                        for key in ["isEssentialSkillFor", "isOptionalSkillFor"]:
                            if key in links:
                                occs = links[key]
                                if isinstance(occs, list):
                                    for o in occs[:limit]:
                                        occupations.append({
                                            "uri": o.get("uri", ""),
                                            "title": o.get("title", ""),
                                            "source": "esco"
                                        })
                                elif isinstance(occs, dict):
                                    occupations.append({
                                        "uri": occs.get("uri", ""),
                                        "title": occs.get("title", ""),
                                        "source": "esco"
                                    })
                        
                        return occupations[:limit]
            
            return []
            
    except Exception as e:
        logger.error(f"Error searching occupations by skill: {e}")
        return []


async def get_all_occupations_esco(limit: int = 100, language: str = "fr") -> List[Dict[str, Any]]:
    """
    Get a list of occupations from ESCO for exploration.
    Uses common search terms to get a diverse set.
    """
    search_terms = [
        "manager", "développeur", "commercial", "assistant",
        "technicien", "ingénieur", "consultant", "responsable",
        "chef", "analyste", "coordinateur", "directeur"
    ]
    
    all_occupations = {}
    
    for term in search_terms:
        results = await search_occupations_esco(term, limit=20, language=language)
        for r in results:
            if r["uri"] not in all_occupations:
                all_occupations[r["uri"]] = r
        
        if len(all_occupations) >= limit:
            break
    
    return list(all_occupations.values())[:limit]


def extract_esco_code(uri: str) -> str:
    """Extract the ESCO code from a URI."""
    if uri:
        parts = uri.split("/")
        if parts:
            return parts[-1][:12]  # Return first 12 chars of the UUID
    return ""


def esco_api_status() -> Dict[str, Any]:
    """Return API status information."""
    return {
        "enabled": True,
        "source": "ESCO - European Skills, Competences, Qualifications and Occupations",
        "base_url": ESCO_BASE_URL,
        "documentation": "https://ec.europa.eu/esco/api/doc/esco_api_doc.html",
        "features": [
            "3000+ occupations",
            "Skills and competences",
            "Multiple languages",
            "Free to use"
        ]
    }
