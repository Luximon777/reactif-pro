from fastapi import APIRouter, HTTPException
from models import (
    AnonymousToken, Profile, CreateTokenRequest, UpdateProfileRequest,
    RegisterRequest, LoginRequest, UpgradeAccountRequest, ChangePasswordRequest,
    ConsentRecord
)
from db import db
from helpers import get_current_token
import bcrypt
import secrets
from datetime import datetime, timezone

router = APIRouter()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


# ===== ANONYMOUS AUTH (existing, kept for backward compat) =====

@router.post("/auth/anonymous")
async def create_anonymous_token(request: CreateTokenRequest):
    token = AnonymousToken(role=request.role)
    token_dict = token.model_dump()
    await db.tokens.insert_one(token_dict)
    profile = Profile(
        token_id=token.id,
        role=request.role,
        name=f"Utilisateur {token.id[:8].upper()}",
        auth_mode="anonymous",
        identity_level="none",
        visibility_level="private"
    )
    profile_dict = profile.model_dump()
    await db.profiles.insert_one(profile_dict)
    await db.tokens.update_one({"id": token.id}, {"$set": {"profile_id": profile.id}})
    return {
        "token": token.token,
        "role": token.role,
        "profile_id": profile.id,
        "auth_mode": "anonymous"
    }


# ===== PSEUDONYMOUS AUTH (new) =====

@router.post("/auth/register")
async def register_pseudo(request: RegisterRequest):
    pseudo_clean = request.pseudo.strip()
    if len(pseudo_clean) < 3:
        raise HTTPException(status_code=400, detail="Le pseudo doit contenir au moins 3 caractères")
    if len(request.password) < 6:
        raise HTTPException(status_code=400, detail="Le mot de passe doit contenir au moins 6 caractères")
    if not request.consent_cgu or not request.consent_privacy:
        raise HTTPException(status_code=400, detail="Vous devez accepter les CGU et la politique de confidentialité")

    existing = await db.profiles.find_one({"pseudo": pseudo_clean}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=409, detail="Ce pseudo est déjà utilisé")

    token = AnonymousToken(role=request.role)
    token_dict = token.model_dump()
    await db.tokens.insert_one(token_dict)

    profile = Profile(
        token_id=token.id,
        role=request.role,
        name=pseudo_clean,
        pseudo=pseudo_clean,
        password_hash=hash_password(request.password),
        email_recovery=request.email_recovery,
        auth_mode="pseudo",
        identity_level="none",
        visibility_level="private",
        display_name=pseudo_clean,
        consent_cgu=True,
        consent_privacy=True,
        consent_marketing=request.consent_marketing
    )
    profile_dict = profile.model_dump()
    await db.profiles.insert_one(profile_dict)
    await db.tokens.update_one({"id": token.id}, {"$set": {"profile_id": profile.id}})

    # Record consent history
    for ctype, cval in [("cgu", True), ("privacy", True), ("marketing", request.consent_marketing)]:
        consent = ConsentRecord(user_id=profile.id, consent_type=ctype, consent_value=cval)
        await db.consent_history.insert_one(consent.model_dump())

    return {
        "token": token.token,
        "role": token.role,
        "profile_id": profile.id,
        "pseudo": pseudo_clean,
        "auth_mode": "pseudo"
    }


@router.post("/auth/login")
async def login_pseudo(request: LoginRequest):
    pseudo_clean = request.pseudo.strip()
    profile = await db.profiles.find_one({"pseudo": pseudo_clean, "auth_mode": "pseudo"}, {"_id": 0})
    if not profile:
        raise HTTPException(status_code=401, detail="Pseudo ou mot de passe incorrect")

    if not profile.get("password_hash") or not verify_password(request.password, profile["password_hash"]):
        raise HTTPException(status_code=401, detail="Pseudo ou mot de passe incorrect")

    token_doc = await db.tokens.find_one({"id": profile["token_id"]}, {"_id": 0})
    if not token_doc:
        new_token = AnonymousToken(role=profile["role"])
        new_token_dict = new_token.model_dump()
        await db.tokens.insert_one(new_token_dict)
        await db.tokens.update_one({"id": new_token.id}, {"$set": {"profile_id": profile["id"]}})
        await db.profiles.update_one({"id": profile["id"]}, {"$set": {"token_id": new_token.id}})
        token_doc = new_token_dict

    return {
        "token": token_doc["token"],
        "role": profile["role"],
        "profile_id": profile["id"],
        "pseudo": profile.get("pseudo"),
        "auth_mode": "pseudo"
    }


# ===== UPGRADE from anonymous to pseudo =====

@router.post("/auth/upgrade")
async def upgrade_to_pseudo(request: UpgradeAccountRequest, token: str = ""):
    if not token:
        raise HTTPException(status_code=401, detail="Token requis")
    token_doc = await get_current_token(token)
    profile = await db.profiles.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
    if profile.get("auth_mode") == "pseudo":
        raise HTTPException(status_code=400, detail="Ce compte est déjà un compte pseudonyme")

    pseudo_clean = request.pseudo.strip()
    if len(pseudo_clean) < 3:
        raise HTTPException(status_code=400, detail="Le pseudo doit contenir au moins 3 caractères")
    if len(request.password) < 6:
        raise HTTPException(status_code=400, detail="Le mot de passe doit contenir au moins 6 caractères")

    existing = await db.profiles.find_one({"pseudo": pseudo_clean}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=409, detail="Ce pseudo est déjà utilisé")

    update_data = {
        "pseudo": pseudo_clean,
        "password_hash": hash_password(request.password),
        "email_recovery": request.email_recovery,
        "auth_mode": "pseudo",
        "display_name": pseudo_clean,
        "name": pseudo_clean,
        "consent_cgu": True,
        "consent_privacy": True,
    }
    await db.profiles.update_one({"id": profile["id"]}, {"$set": update_data})

    for ctype, cval in [("cgu", True), ("privacy", True)]:
        consent = ConsentRecord(user_id=profile["id"], consent_type=ctype, consent_value=cval)
        await db.consent_history.insert_one(consent.model_dump())

    return {
        "message": "Compte mis à niveau vers pseudonyme",
        "pseudo": pseudo_clean,
        "auth_mode": "pseudo"
    }


# ===== CHANGE PASSWORD =====

@router.post("/auth/change-password")
async def change_password(request: ChangePasswordRequest, token: str = ""):
    if not token:
        raise HTTPException(status_code=401, detail="Token requis")
    token_doc = await get_current_token(token)
    profile = await db.profiles.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    if not profile or profile.get("auth_mode") != "pseudo":
        raise HTTPException(status_code=400, detail="Changement de mot de passe disponible uniquement pour les comptes pseudonymes")

    if not verify_password(request.current_password, profile["password_hash"]):
        raise HTTPException(status_code=401, detail="Mot de passe actuel incorrect")

    if len(request.new_password) < 6:
        raise HTTPException(status_code=400, detail="Le nouveau mot de passe doit contenir au moins 6 caractères")

    await db.profiles.update_one(
        {"id": profile["id"]},
        {"$set": {"password_hash": hash_password(request.new_password)}}
    )
    return {"message": "Mot de passe modifié avec succès"}


# ===== TOKEN VERIFICATION =====

@router.get("/auth/verify")
async def verify_token(token: str):
    token_doc = await get_current_token(token)
    profile = await db.profiles.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    return {
        "valid": True,
        "role": token_doc["role"],
        "profile_id": token_doc.get("profile_id"),
        "auth_mode": profile.get("auth_mode", "anonymous") if profile else "anonymous",
        "pseudo": profile.get("pseudo") if profile else None,
        "identity_level": profile.get("identity_level", "none") if profile else "none"
    }


@router.post("/auth/switch-role")
async def switch_role(token: str, new_role: str):
    if new_role not in ["particulier", "entreprise", "partenaire"]:
        raise HTTPException(status_code=400, detail="Rôle invalide")
    await db.tokens.update_one({"token": token}, {"$set": {"role": new_role}})
    return {"message": "Rôle mis à jour", "role": new_role}


# ===== PROFILE =====

@router.get("/profile")
async def get_profile(token: str):
    token_doc = await get_current_token(token)
    profile = await db.profiles.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
    # Never return password_hash to frontend
    profile.pop("password_hash", None)
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
    result = await db.profiles.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    if result:
        result.pop("password_hash", None)
    return result


# ===== PRIVACY SETTINGS =====

@router.put("/profile/privacy")
async def update_privacy(token: str, visibility_level: str = None, display_name: str = None, bio: str = None, consent_marketing: bool = None):
    token_doc = await get_current_token(token)
    profile = await db.profiles.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouvé")

    update = {}
    if visibility_level and visibility_level in ("private", "limited", "public"):
        update["visibility_level"] = visibility_level
    if display_name is not None:
        update["display_name"] = display_name
    if bio is not None:
        update["bio"] = bio
    if consent_marketing is not None:
        update["consent_marketing"] = consent_marketing
        consent = ConsentRecord(user_id=profile["id"], consent_type="marketing", consent_value=consent_marketing)
        await db.consent_history.insert_one(consent.model_dump())

    if update:
        await db.profiles.update_one({"id": profile["id"]}, {"$set": update})

    updated = await db.profiles.find_one({"id": profile["id"]}, {"_id": 0})
    if updated:
        updated.pop("password_hash", None)
    return updated


# ===== DELETE ACCOUNT =====

@router.delete("/auth/account")
async def delete_account(token: str):
    token_doc = await get_current_token(token)
    profile = await db.profiles.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouvé")

    profile_id = profile["id"]
    # Delete all user data
    await db.profiles.delete_one({"id": profile_id})
    await db.tokens.delete_one({"id": token_doc["id"]})
    await db.passports.delete_many({"token_id": token_doc["id"]})
    await db.coffre_documents.delete_many({"token_id": token_doc["id"]})
    await db.consent_history.delete_many({"user_id": profile_id})
    await db.external_identities.delete_many({"user_id": profile_id})
    await db.cv_analyses.delete_many({"token_id": token_doc["id"]})

    return {"message": "Compte et données supprimés avec succès"}


# ===== EXPORT DATA =====

@router.get("/auth/export-data")
async def export_data(token: str):
    token_doc = await get_current_token(token)
    profile = await db.profiles.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouvé")

    profile.pop("password_hash", None)

    passport = await db.passports.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    documents = await db.coffre_documents.find({"token_id": token_doc["id"]}, {"_id": 0}).to_list(1000)
    consents = await db.consent_history.find({"user_id": profile["id"]}, {"_id": 0}).to_list(1000)
    cv_analyses = await db.cv_analyses.find({"token_id": token_doc["id"]}, {"_id": 0}).to_list(100)

    return {
        "export_date": datetime.now(timezone.utc).isoformat(),
        "profile": profile,
        "passport": passport,
        "documents": documents,
        "consent_history": consents,
        "cv_analyses": cv_analyses
    }


# ===== CHECK PSEUDO AVAILABILITY =====

@router.get("/auth/check-pseudo")
async def check_pseudo(pseudo: str):
    pseudo_clean = pseudo.strip()
    if len(pseudo_clean) < 3:
        return {"available": False, "reason": "Le pseudo doit contenir au moins 3 caractères"}
    existing = await db.profiles.find_one({"pseudo": pseudo_clean}, {"_id": 0})
    return {"available": existing is None}
