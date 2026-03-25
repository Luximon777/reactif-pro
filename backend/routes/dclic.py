from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import secrets
from db import db

# Import the complete D'CLIC PRO engine
from dclic_engine import (
    VISUAL_QUESTIONS,
    VERTUS,
    LIFE_PATHS,
    compute_profile,
    calculate_ofman_quadrant,
    get_functioning_compass,
    get_cross_analysis,
    get_integrated_analysis,
    calculate_life_path,
    get_life_path_data,
    calculate_vertus_profile,
    calculate_riasec_profile,
    generate_access_code,
)

router = APIRouter(prefix="/dclic", tags=["dclic"])


# ============================================================================
# MODELS
# ============================================================================

class DclicSubmitRequest(BaseModel):
    answers: Dict[str, str]
    birth_date: Optional[str] = None
    education_level: Optional[str] = None

class DclicRetrieveRequest(BaseModel):
    access_code: str


# ============================================================================
# ROUTES
# ============================================================================

@router.get("/questionnaire")
async def get_dclic_questionnaire():
    return {"questions": VISUAL_QUESTIONS, "total": len(VISUAL_QUESTIONS)}


@router.post("/submit")
async def submit_dclic_test(request: DclicSubmitRequest):
    """Submit answers, compute FULL profile, generate access code."""
    
    # 1. Compute core profile
    profile = compute_profile(request.answers)
    
    # 2. Vertus profile (needs raw answers + mbti)
    vertus_profile = calculate_vertus_profile(request.answers, profile.get("mbti"))
    
    # 3. RIASEC profile (needs raw answers + profile)
    riasec_profile = calculate_riasec_profile(request.answers, profile)
    
    # 4. Functioning compass (MBTI axes)
    compass = get_functioning_compass(profile)
    
    # Get vertu data for analysis functions
    vertu_data = VERTUS.get(profile.get("vertu_dominante", "sagesse"), VERTUS["sagesse"])
    
    # 5. Ofman quadrant (zones de vigilance) - needed by integrated
    ofman = calculate_ofman_quadrant(profile, vertu_data)
    
    # 6. Life path (if birth date provided)
    life_path = None
    cross_analysis = None
    if request.birth_date:
        life_path = get_life_path_data(request.birth_date)
        cross_analysis = get_cross_analysis(life_path, profile, profile.get("ennea_dominant", 5))
    
    # 7. Integrated analysis (3 levels) - needs life_path and ofman
    integrated = get_integrated_analysis(profile, vertu_data, life_path, ofman)
    
    # 8. Generate access code
    access_code = generate_access_code()
    
    # Full result
    full_profile = {
        **profile,
        "vertus_profile": vertus_profile,
        "riasec_profile": riasec_profile,
        "compass": compass,
        "integrated_analysis": integrated,
        "ofman_quadrant": ofman,
        "life_path": life_path,
        "cross_analysis": cross_analysis,
        "education_level": request.education_level,
        "vertu_data": {
            "name": vertu_data.get("name", ""),
            "cognition": vertu_data.get("cognition", []),
            "conation": vertu_data.get("conation", []),
            "affection": vertu_data.get("affection", []),
            "valeurs_schwartz": vertu_data.get("valeurs_schwartz", []),
            "forces": vertu_data.get("forces", []),
            "savoirs_etre": vertu_data.get("savoirs_etre", []),
            "qualites_humaines": vertu_data.get("qualites_humaines", []),
        },
    }
    
    doc = {
        "access_code": access_code,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "is_claimed": False,
        "claimed_at": None,
        "answers": request.answers,
        "birth_date": request.birth_date,
        "education_level": request.education_level,
        "profile": full_profile,
    }
    await db.dclic_results.insert_one(doc)
    
    return {"access_code": access_code, "profile": full_profile}


@router.post("/retrieve")
async def retrieve_dclic_results(request: DclicRetrieveRequest):
    """Retrieve D'CLIC PRO results by access code."""
    code = request.access_code.upper().strip()
    if len(code) < 4:
        raise HTTPException(status_code=400, detail="Code trop court")
    
    result = await db.dclic_results.find_one({"access_code": code}, {"_id": 0})
    if not result:
        raise HTTPException(status_code=404, detail="Code d'acces non trouve")
    
    return {
        "success": True,
        "access_code": code,
        "profile": result.get("profile", {}),
        "is_claimed": result.get("is_claimed", False)
    }


@router.post("/claim")
async def claim_dclic_results(access_code: str, user_id: str):
    """Mark results as claimed by a Re'Actif Pro user."""
    code = access_code.upper().strip()
    result = await db.dclic_results.update_one(
        {"access_code": code, "is_claimed": False},
        {"$set": {"is_claimed": True, "claimed_at": datetime.now(timezone.utc).isoformat(), "claimed_by": user_id}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Code deja utilise ou inexistant")
    return {"success": True}
