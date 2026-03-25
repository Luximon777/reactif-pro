from fastapi import APIRouter, HTTPException
from models import (
    AnonymousToken, Profile, CreateTokenRequest, UpdateProfileRequest,
    RegisterRequest, LoginRequest, UpgradeAccountRequest, ChangePasswordRequest,
    ConsentRecord, RegisterEntrepriseRequest, RegisterPartenaireRequest,
    Evidence, DclicProImport
)
from db import db
from helpers import get_current_token
import bcrypt
import secrets
from datetime import datetime, timezone
import re

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
        "identity_level": profile.get("identity_level", "none") if profile else "none",
        "company_name": profile.get("company_name") if profile else None,
        "profile_completion": profile.get("profile_completion", 0) if profile else 0
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



# ===== ENTREPRISE REGISTRATION =====

def _check_email_professional(email: str):
    """Check if email is professional (not gmail, yahoo, etc.) - returns warning, not blocking"""
    free_domains = ["gmail.com", "yahoo.com", "yahoo.fr", "hotmail.com", "hotmail.fr",
                    "outlook.com", "live.com", "live.fr", "orange.fr", "free.fr",
                    "sfr.fr", "laposte.net", "wanadoo.fr", "aol.com"]
    domain = email.split("@")[-1].lower() if "@" in email else ""
    return domain in free_domains


def _calc_profile_completion(profile: dict) -> int:
    """Calculate profile completion percentage based on role"""
    role = profile.get("role", "particulier")
    filled = 0
    total = 0

    if role == "entreprise":
        fields = [
            ("company_name", 15), ("siret", 15), ("referent_first_name", 10),
            ("referent_last_name", 10), ("referent_function", 10),
            ("charte_ethique_signed", 15), ("bio", 10), ("display_name", 5),
            ("visibility_level", 5), ("email_recovery", 5)
        ]
    elif role == "partenaire":
        fields = [
            ("company_name", 15), ("siret", 10), ("structure_type", 10),
            ("referent_first_name", 10), ("referent_last_name", 10),
            ("referent_function", 10), ("charte_ethique_signed", 15),
            ("bio", 10), ("display_name", 5), ("visibility_level", 5)
        ]
    else:
        fields = [
            ("pseudo", 10), ("display_name", 5), ("bio", 5),
            ("skills", 10), ("sectors", 10), ("experience_years", 5),
            ("visibility_level", 3), ("email_recovery", 5),
            ("target_job", 12), ("city", 5), ("mobility", 5),
            ("contract_types", 10), ("work_modes", 5), ("summary", 10),
        ]

    for field, weight in fields:
        total += weight
        val = profile.get(field)
        if val is not None and val != "" and val != [] and val != 0 and val is not False:
            filled += weight

    return min(100, int((filled / total) * 100)) if total > 0 else 0


@router.post("/auth/register-entreprise")
async def register_entreprise(request: RegisterEntrepriseRequest):
    if not request.company_name.strip():
        raise HTTPException(status_code=400, detail="Le nom de l'entreprise est requis")
    siret_clean = request.siret.strip().replace(" ", "")
    if not siret_clean.isdigit() or len(siret_clean) not in (9, 14):
        raise HTTPException(status_code=400, detail="SIRET/SIREN invalide")
    if not request.email or "@" not in request.email:
        raise HTTPException(status_code=400, detail="Email professionnel requis")
    if len(request.password) < 6:
        raise HTTPException(status_code=400, detail="Le mot de passe doit contenir au moins 6 caractères")
    if not request.referent_first_name.strip() or not request.referent_last_name.strip():
        raise HTTPException(status_code=400, detail="Nom et prénom du référent requis")
    if not request.charte_ethique_signed:
        raise HTTPException(status_code=400, detail="Vous devez signer la charte éthique ALT&ACT")
    if not request.consent_cgu or not request.consent_privacy:
        raise HTTPException(status_code=400, detail="Vous devez accepter les CGU et la politique de confidentialité")

    # Check unique email for entreprise
    existing = await db.profiles.find_one({"email_recovery": request.email, "role": "entreprise"}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=409, detail="Cet email est déjà utilisé pour un compte entreprise")

    email_warning = _check_email_professional(request.email)

    token = AnonymousToken(role="entreprise")
    await db.tokens.insert_one(token.model_dump())

    display = f"{request.referent_first_name} {request.referent_last_name}"
    profile = Profile(
        token_id=token.id,
        role="entreprise",
        name=request.company_name.strip(),
        pseudo=request.email,
        email_recovery=request.email,
        password_hash=hash_password(request.password),
        auth_mode="pseudo",
        identity_level="none",
        visibility_level="limited",
        display_name=display,
        company_name=request.company_name.strip(),
        siret=siret_clean,
        referent_first_name=request.referent_first_name.strip(),
        referent_last_name=request.referent_last_name.strip(),
        referent_function=request.referent_function.strip(),
        charte_ethique_signed=True,
        charte_ethique_signed_at=datetime.now(timezone.utc).isoformat(),
        consent_cgu=True,
        consent_privacy=True,
    )
    profile_dict = profile.model_dump()
    profile_dict["profile_completion"] = _calc_profile_completion(profile_dict)
    await db.profiles.insert_one(profile_dict)
    await db.tokens.update_one({"id": token.id}, {"$set": {"profile_id": profile.id}})

    for ctype in ["cgu", "privacy", "charte_ethique"]:
        consent = ConsentRecord(user_id=profile.id, consent_type=ctype, consent_value=True)
        await db.consent_history.insert_one(consent.model_dump())

    return {
        "token": token.token,
        "role": "entreprise",
        "profile_id": profile.id,
        "auth_mode": "pseudo",
        "company_name": request.company_name.strip(),
        "email_warning": "Nous recommandons d'utiliser un email professionnel pour plus de crédibilité." if email_warning else None,
        "profile_completion": profile_dict["profile_completion"]
    }


# ===== PARTENAIRE REGISTRATION =====

@router.post("/auth/register-partenaire")
async def register_partenaire(request: RegisterPartenaireRequest):
    valid_types = ["organisme_formation", "association", "institution_publique", "acteur_insertion", "autre"]
    if request.structure_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Type de structure invalide. Valeurs acceptées: {', '.join(valid_types)}")
    if not request.structure_name.strip():
        raise HTTPException(status_code=400, detail="Le nom de la structure est requis")
    siret_clean = request.siret.strip().replace(" ", "")
    if not siret_clean.isdigit() or len(siret_clean) not in (9, 14):
        raise HTTPException(status_code=400, detail="SIRET/SIREN invalide")
    if not request.email or "@" not in request.email:
        raise HTTPException(status_code=400, detail="Email professionnel requis")
    if len(request.password) < 6:
        raise HTTPException(status_code=400, detail="Le mot de passe doit contenir au moins 6 caractères")
    if not request.referent_first_name.strip() or not request.referent_last_name.strip():
        raise HTTPException(status_code=400, detail="Nom et prénom du référent requis")
    if not request.charte_ethique_signed:
        raise HTTPException(status_code=400, detail="Vous devez signer la charte éthique ALT&ACT")
    if not request.consent_cgu or not request.consent_privacy:
        raise HTTPException(status_code=400, detail="Vous devez accepter les CGU et la politique de confidentialité")

    existing = await db.profiles.find_one({"email_recovery": request.email, "role": "partenaire"}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=409, detail="Cet email est déjà utilisé pour un compte partenaire")

    token = AnonymousToken(role="partenaire")
    await db.tokens.insert_one(token.model_dump())

    display = f"{request.referent_first_name} {request.referent_last_name}"
    profile = Profile(
        token_id=token.id,
        role="partenaire",
        name=request.structure_name.strip(),
        pseudo=request.email,
        email_recovery=request.email,
        password_hash=hash_password(request.password),
        auth_mode="pseudo",
        identity_level="none",
        visibility_level="limited",
        display_name=display,
        company_name=request.structure_name.strip(),
        siret=siret_clean,
        structure_type=request.structure_type,
        referent_first_name=request.referent_first_name.strip(),
        referent_last_name=request.referent_last_name.strip(),
        referent_function=request.referent_function.strip(),
        charte_ethique_signed=True,
        charte_ethique_signed_at=datetime.now(timezone.utc).isoformat(),
        consent_cgu=True,
        consent_privacy=True,
    )
    profile_dict = profile.model_dump()
    profile_dict["profile_completion"] = _calc_profile_completion(profile_dict)
    await db.profiles.insert_one(profile_dict)
    await db.tokens.update_one({"id": token.id}, {"$set": {"profile_id": profile.id}})

    for ctype in ["cgu", "privacy", "charte_ethique"]:
        consent = ConsentRecord(user_id=profile.id, consent_type=ctype, consent_value=True)
        await db.consent_history.insert_one(consent.model_dump())

    return {
        "token": token.token,
        "role": "partenaire",
        "profile_id": profile.id,
        "auth_mode": "pseudo",
        "structure_name": request.structure_name.strip(),
        "structure_type": request.structure_type,
        "profile_completion": profile_dict["profile_completion"]
    }


# ===== LOGIN ENTREPRISE/PARTENAIRE (by email) =====

@router.post("/auth/login-pro")
async def login_pro(request: LoginRequest):
    """Login for entreprise/partenaire using email as pseudo"""
    email_clean = request.pseudo.strip()
    profile = await db.profiles.find_one(
        {"email_recovery": email_clean, "auth_mode": "pseudo", "role": {"$in": ["entreprise", "partenaire"]}},
        {"_id": 0}
    )
    if not profile:
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    if not profile.get("password_hash") or not verify_password(request.password, profile["password_hash"]):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    token_doc = await db.tokens.find_one({"id": profile["token_id"]}, {"_id": 0})
    if not token_doc:
        new_token = AnonymousToken(role=profile["role"])
        await db.tokens.insert_one(new_token.model_dump())
        await db.tokens.update_one({"id": new_token.id}, {"$set": {"profile_id": profile["id"]}})
        await db.profiles.update_one({"id": profile["id"]}, {"$set": {"token_id": new_token.id}})
        token_doc = new_token.model_dump()

    return {
        "token": token_doc["token"],
        "role": profile["role"],
        "profile_id": profile["id"],
        "pseudo": profile.get("pseudo"),
        "auth_mode": "pseudo",
        "company_name": profile.get("company_name"),
        "profile_completion": profile.get("profile_completion", 0)
    }


# ===== PROFILE COMPLETION =====

@router.get("/profile/completion")
async def get_profile_completion(token: str):
    token_doc = await get_current_token(token)
    profile = await db.profiles.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
    completion = _calc_profile_completion(profile)
    await db.profiles.update_one({"id": profile["id"]}, {"$set": {"profile_completion": completion}})
    return {"profile_completion": completion, "role": profile.get("role")}


# ===== EVIDENCE / PREUVES =====

@router.get("/profile/evidences")
async def get_evidences(token: str):
    token_doc = await get_current_token(token)
    evidences = await db.evidences.find({"token_id": token_doc["id"]}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return evidences


@router.post("/profile/evidences")
async def add_evidence(token: str, title: str, kind: str = "attestation", source: str = "", description: str = "", linked_skill_names: list = [], obtained_date: str = ""):
    token_doc = await get_current_token(token)
    evidence = Evidence(
        token_id=token_doc["id"],
        title=title,
        kind=kind,
        source=source,
        description=description,
        linked_skill_names=linked_skill_names,
        obtained_date=obtained_date,
    )
    await db.evidences.insert_one(evidence.model_dump())
    return evidence.model_dump()


@router.delete("/profile/evidences/{evidence_id}")
async def delete_evidence(evidence_id: str, token: str):
    token_doc = await get_current_token(token)
    result = await db.evidences.delete_one({"id": evidence_id, "token_id": token_doc["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Preuve non trouvée")
    return {"message": "Preuve supprimée"}


# ===== IMPORT D'CLIC PRO =====

@router.post("/profile/import-dclic")
async def import_dclic_pro(token: str, data: DclicProImport):
    """Import profile data from D'CLIC PRO format into Re'Actif Pro"""
    import uuid as _uuid
    token_doc = await get_current_token(token)
    token_id = token_doc["id"]

    profile_update = {}
    if data.target_job:
        profile_update["target_job"] = data.target_job
    if data.summary:
        profile_update["summary"] = data.summary
    if data.city:
        profile_update["city"] = data.city
    if data.mobility:
        profile_update["mobility"] = data.mobility
    if data.contract_types:
        profile_update["contract_types"] = data.contract_types
    if data.work_modes:
        profile_update["work_modes"] = data.work_modes

    # Map skills with status and levels
    if data.skills:
        mapped_skills = []
        for s in data.skills:
            mapped_skills.append({
                "id": s.get("id", str(_uuid.uuid4())),
                "name": s.get("name", ""),
                "category": s.get("category", "transversale"),
                "declared_level": s.get("declared_level", 3),
                "validated_level": s.get("validated_level", 0),
                "status": s.get("status", "declaree"),
            })
        profile_update["skills"] = mapped_skills

    if data.experiences:
        profile_update["experience_years"] = len(data.experiences)

    if profile_update:
        await db.profiles.update_one({"token_id": token_id}, {"$set": profile_update})

    # Store full D'CLIC PRO profile data
    if data.dclic_profile:
        dclic_data = data.dclic_profile
        dclic_enrichment = {
            "dclic_profile": dclic_data,
            "dclic_imported": True,
            "dclic_mbti": dclic_data.get("mbti"),
            "dclic_disc": dclic_data.get("disc"),
            "dclic_disc_label": dclic_data.get("disc_dominant_name") or dclic_data.get("disc_label"),
            "dclic_riasec_major": dclic_data.get("riasec_major_name"),
            "dclic_riasec_minor": dclic_data.get("riasec_minor_name"),
            "dclic_vertu_dominante": dclic_data.get("vertu_dominante_name"),
            "dclic_competences": dclic_data.get("competences_fortes", []),
            "dclic_vigilances": dclic_data.get("vigilances", []),
        }
        await db.profiles.update_one({"token_id": token_id}, {"$set": dclic_enrichment})

    # Import experiences into passport
    if data.experiences:
        passport = await db.passports.find_one({"token_id": token_id}, {"_id": 0})
        if passport:
            existing_exps = passport.get("experiences", [])
            for exp in data.experiences:
                existing_exps.append({
                    "title": exp.get("title", ""),
                    "organization": exp.get("organization", ""),
                    "description": exp.get("description", ""),
                    "achievements": exp.get("achievements", []),
                    "skills_used": exp.get("skills_used", []),
                    "start_date": exp.get("start_date", ""),
                    "end_date": exp.get("end_date", ""),
                    "is_current": exp.get("is_current", False),
                    "experience_type": exp.get("experience_type", "professional"),
                })
            update_fields = {"experiences": existing_exps}
            if data.target_job:
                update_fields["career_project"] = data.target_job
            if data.summary:
                update_fields["professional_summary"] = data.summary
            await db.passports.update_one({"token_id": token_id}, {"$set": update_fields})

    # Import evidences
    imported_evidences = 0
    if data.evidences:
        for ev in data.evidences:
            evidence = Evidence(
                token_id=token_id,
                title=ev.get("title", ""),
                kind=ev.get("kind", "attestation"),
                source=ev.get("source", "D'CLIC PRO"),
                description=ev.get("description", ""),
                linked_skill_names=ev.get("linked_skill_names", []),
                obtained_date=ev.get("obtained_date", ""),
            )
            await db.evidences.insert_one(evidence.model_dump())
            imported_evidences += 1

    # Recalculate completion
    profile = await db.profiles.find_one({"token_id": token_id}, {"_id": 0})
    completion = _calc_profile_completion(profile) if profile else 0
    await db.profiles.update_one({"token_id": token_id}, {"$set": {"profile_completion": completion}})

    return {
        "message": "Profil D'CLIC PRO importé avec succès",
        "fields_updated": list(profile_update.keys()),
        "experiences_imported": len(data.experiences),
        "skills_imported": len(data.skills),
        "evidences_imported": imported_evidences,
        "profile_completion": completion,
    }
