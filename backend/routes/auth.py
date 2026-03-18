from fastapi import APIRouter
from models import AnonymousToken, Profile, CreateTokenRequest, UpdateProfileRequest
from db import db
from helpers import get_current_token

router = APIRouter()


@router.post("/auth/anonymous")
async def create_anonymous_token(request: CreateTokenRequest):
    token = AnonymousToken(role=request.role)
    token_dict = token.model_dump()
    await db.tokens.insert_one(token_dict)
    profile = Profile(token_id=token.id, role=request.role, name=f"Utilisateur {token.id[:8].upper()}")
    profile_dict = profile.model_dump()
    await db.profiles.insert_one(profile_dict)
    await db.tokens.update_one({"id": token.id}, {"$set": {"profile_id": profile.id}})
    return {"token": token.token, "role": token.role, "profile_id": profile.id}


@router.get("/auth/verify")
async def verify_token(token: str):
    token_doc = await get_current_token(token)
    return {"valid": True, "role": token_doc["role"], "profile_id": token_doc.get("profile_id")}


@router.post("/auth/switch-role")
async def switch_role(token: str, new_role: str):
    from fastapi import HTTPException
    if new_role not in ["particulier", "entreprise", "partenaire"]:
        raise HTTPException(status_code=400, detail="Rôle invalide")
    await db.tokens.update_one({"token": token}, {"$set": {"role": new_role}})
    return {"message": "Rôle mis à jour", "role": new_role}


@router.get("/profile")
async def get_profile(token: str):
    from fastapi import HTTPException
    token_doc = await get_current_token(token)
    profile = await db.profiles.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
    return profile


@router.put("/profile")
async def update_profile(token: str, request: UpdateProfileRequest):
    token_doc = await get_current_token(token)
    update_data = {k: v for k, v in request.model_dump().items() if v is not None}
    if update_data:
        profile = await db.profiles.find_one({"token_id": token_doc["id"]}, {"_id": 0})
        if profile:
            skills_count = len(update_data.get("skills", profile.get("skills", [])))
            sectors_count = len(update_data.get("sectors", profile.get("sectors", [])))
            exp = update_data.get("experience_years", profile.get("experience_years", 0))
            score = min(100, skills_count * 10 + sectors_count * 5 + (10 if exp > 0 else 0) + 30)
            update_data["profile_score"] = score
        await db.profiles.update_one({"token_id": token_doc["id"]}, {"$set": update_data})
    return await db.profiles.find_one({"token_id": token_doc["id"]}, {"_id": 0})
