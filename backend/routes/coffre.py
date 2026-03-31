from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import Response
from typing import Optional
from datetime import datetime, timezone, timedelta
from models import CoffreDocument, DocumentShare, CreateDocumentRequest
from db import db
from helpers import get_current_token
from referentiel_data import DOCUMENT_CATEGORIES
from storage import put_object, get_object, get_mime_type
import uuid

router = APIRouter()


@router.get("/coffre/categories")
async def get_coffre_categories():
    return DOCUMENT_CATEGORIES


@router.get("/coffre/documents")
async def get_coffre_documents(token: str, category: Optional[str] = None, search: Optional[str] = None):
    token_doc = await get_current_token(token)
    query = {"token_id": token_doc["id"]}
    if category:
        query["category"] = category
    documents = await db.coffre_documents.find(query, {"_id": 0}).to_list(500)
    if search:
        search_lower = search.lower()
        documents = [d for d in documents if
            search_lower in d.get("title", "").lower() or
            search_lower in d.get("description", "").lower() or
            any(search_lower in c.lower() for c in d.get("competences_liees", []))]
    today = datetime.now(timezone.utc)
    for doc in documents:
        if doc.get("date_expiration"):
            try:
                exp_date = datetime.fromisoformat(doc["date_expiration"].replace('Z', '+00:00'))
                days_until = (exp_date - today).days
                doc["is_expiring_soon"] = 0 <= days_until <= 30
                doc["days_until_expiry"] = days_until
            except Exception:
                pass
    return sorted(documents, key=lambda x: x.get("created_at", ""), reverse=True)


@router.get("/coffre/documents/{document_id}")
async def get_coffre_document(token: str, document_id: str):
    token_doc = await get_current_token(token)
    doc = await db.coffre_documents.find_one({"id": document_id, "token_id": token_doc["id"]}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    return doc


@router.post("/coffre/documents")
async def create_coffre_document(token: str, request: CreateDocumentRequest):
    token_doc = await get_current_token(token)
    document = CoffreDocument(token_id=token_doc["id"], **request.model_dump())
    await db.coffre_documents.insert_one(document.model_dump())
    if request.competences_liees:
        profile = await db.profiles.find_one({"token_id": token_doc["id"]}, {"_id": 0})
        if profile:
            existing_skills = [s.get("name") for s in profile.get("skills", [])]
            new_skills = profile.get("skills", [])
            for comp in request.competences_liees:
                if comp not in existing_skills:
                    new_skills.append({"name": comp, "level": 50, "proven": True})
            await db.profiles.update_one({"token_id": token_doc["id"]}, {"$set": {"skills": new_skills}})
    return document.model_dump()


@router.put("/coffre/documents/{document_id}")
async def update_coffre_document(token: str, document_id: str, request: CreateDocumentRequest):
    token_doc = await get_current_token(token)
    update_data = request.model_dump()
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    result = await db.coffre_documents.update_one({"id": document_id, "token_id": token_doc["id"]}, {"$set": update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    return await db.coffre_documents.find_one({"id": document_id}, {"_id": 0})


@router.delete("/coffre/documents/{document_id}")
async def delete_coffre_document(token: str, document_id: str):
    token_doc = await get_current_token(token)
    result = await db.coffre_documents.delete_one({"id": document_id, "token_id": token_doc["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    return {"message": "Document supprimé"}


@router.post("/coffre/documents/{document_id}/share")
async def share_document(token: str, document_id: str, shared_with_email: Optional[str] = None, shared_with_role: Optional[str] = None, expires_in_days: int = 7):
    token_doc = await get_current_token(token)
    doc = await db.coffre_documents.find_one({"id": document_id, "token_id": token_doc["id"]}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    expires_at = (datetime.now(timezone.utc) + timedelta(days=expires_in_days)).isoformat()
    share = DocumentShare(document_id=document_id, shared_by=token_doc["id"], shared_with_email=shared_with_email, shared_with_role=shared_with_role, expires_at=expires_at)
    await db.document_shares.insert_one(share.model_dump())
    await db.coffre_documents.update_one(
        {"id": document_id},
        {"$set": {"privacy_level": "shared_recruteur" if shared_with_role == "recruteur" else "shared_conseiller"}, "$push": {"shared_with": share.id}}
    )
    return {"share_id": share.id, "access_token": share.access_token, "expires_at": expires_at}


@router.get("/coffre/shares")
async def get_document_shares(token: str):
    token_doc = await get_current_token(token)
    shares = await db.document_shares.find({"shared_by": token_doc["id"]}, {"_id": 0}).to_list(100)
    for share in shares:
        doc = await db.coffre_documents.find_one({"id": share["document_id"]}, {"_id": 0})
        if doc:
            share["document_title"] = doc.get("title")
            share["document_category"] = doc.get("category")
    return shares


@router.delete("/coffre/shares/{share_id}")
async def revoke_share(token: str, share_id: str):
    token_doc = await get_current_token(token)
    share = await db.document_shares.find_one({"id": share_id, "shared_by": token_doc["id"]}, {"_id": 0})
    if not share:
        raise HTTPException(status_code=404, detail="Partage non trouvé")
    await db.document_shares.delete_one({"id": share_id})
    await db.coffre_documents.update_one({"id": share["document_id"]}, {"$pull": {"shared_with": share_id}})
    return {"message": "Partage révoqué"}


@router.get("/coffre/stats")
async def get_coffre_stats(token: str):
    token_doc = await get_current_token(token)
    documents = await db.coffre_documents.find({"token_id": token_doc["id"]}, {"_id": 0}).to_list(500)
    stats = {"total_documents": len(documents), "by_category": {}, "competences_prouvees": set(), "documents_partages": 0, "documents_expirants": 0, "documents_sensibles": 0}
    today = datetime.now(timezone.utc)
    for doc in documents:
        cat = doc.get("category", "autre")
        stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1
        for comp in doc.get("competences_liees", []):
            stats["competences_prouvees"].add(comp)
        if doc.get("privacy_level") != "private":
            stats["documents_partages"] += 1
        if doc.get("is_sensitive"):
            stats["documents_sensibles"] += 1
        if doc.get("date_expiration"):
            try:
                exp_date = datetime.fromisoformat(doc["date_expiration"].replace('Z', '+00:00'))
                if 0 <= (exp_date - today).days <= 30:
                    stats["documents_expirants"] += 1
            except Exception:
                pass
    stats["competences_prouvees"] = list(stats["competences_prouvees"])
    return stats


@router.get("/coffre/expiring")
async def get_expiring_documents(token: str):
    token_doc = await get_current_token(token)
    documents = await db.coffre_documents.find({"token_id": token_doc["id"]}, {"_id": 0}).to_list(500)
    today = datetime.now(timezone.utc)
    expiring = []
    for doc in documents:
        if doc.get("date_expiration"):
            try:
                exp_date = datetime.fromisoformat(doc["date_expiration"].replace('Z', '+00:00'))
                days_until = (exp_date - today).days
                if 0 <= days_until <= 30:
                    doc["days_until_expiry"] = days_until
                    expiring.append(doc)
            except Exception:
                pass
    return sorted(expiring, key=lambda x: x.get("days_until_expiry", 999))


@router.post("/coffre/transfer-cv")
async def transfer_cv_to_coffre(token: str, cv_type: str = "uploaded"):
    """Transfer uploaded CV or AI-generated CV to coffre-fort.
    cv_type: 'uploaded' for user's original CV, 'classique', 'competences', 'transversal', 'nouvelle_generation' for AI models
    """
    import uuid
    token_doc = await get_current_token(token)
    token_id = token_doc["id"]

    if cv_type == "uploaded":
        # Get the latest completed CV analysis
        cv_job = await db.cv_jobs.find_one(
            {"token_id": token_id, "status": "completed"},
            {"_id": 0},
            sort=[("created_at", -1)]
        )
        if not cv_job:
            raise HTTPException(status_code=404, detail="Aucune analyse CV trouvée")

        filename = cv_job.get("filename", "CV uploadé")
        # Check if already transferred
        existing = await db.coffre_documents.find_one({
            "token_id": token_id,
            "source_ref": f"cv_uploaded_{cv_job.get('job_id', '')}"
        }, {"_id": 0})
        if existing:
            raise HTTPException(status_code=409, detail="Ce CV est déjà dans le coffre-fort")

        competences = []
        if cv_job.get("result"):
            for sf in cv_job["result"].get("savoir_faire", []):
                if isinstance(sf, dict):
                    competences.append(sf.get("name", ""))
                elif isinstance(sf, str):
                    competences.append(sf)

        doc = CoffreDocument(
            token_id=token_id,
            title=f"CV original — {filename}",
            category="identite_professionnelle",
            description=f"CV uploadé et analysé le {cv_job.get('created_at', '')[:10]}",
            document_type="cv",
            competences_liees=competences[:10],
            source_ref=f"cv_uploaded_{cv_job.get('job_id', '')}",
        )
        await db.coffre_documents.insert_one(doc.model_dump())
        return {"message": "CV transféré dans le coffre-fort", "document_id": doc.id}

    else:
        # AI-generated CV model
        cv_models = await db.cv_models.find_one({"token_id": token_id}, {"_id": 0})
        if not cv_models or not cv_models.get("models", {}).get(cv_type):
            raise HTTPException(status_code=404, detail=f"Modèle CV '{cv_type}' non trouvé")

        existing = await db.coffre_documents.find_one({
            "token_id": token_id,
            "source_ref": f"cv_model_{cv_type}"
        }, {"_id": 0})
        if existing:
            raise HTTPException(status_code=409, detail=f"Le CV {cv_type} est déjà dans le coffre-fort")

        model_labels = {
            "classique": "CV Classique",
            "competences": "CV par Compétences",
            "transversal": "CV Transversal",
            "nouvelle_generation": "CV Nouvelle Génération"
        }
        label = model_labels.get(cv_type, cv_type.replace("_", " ").title())

        doc = CoffreDocument(
            token_id=token_id,
            title=f"{label} (généré par IA)",
            category="identite_professionnelle",
            description="CV optimisé généré par l'IA Re'Actif Pro",
            document_type="cv_genere",
            competences_liees=[],
            source_ref=f"cv_model_{cv_type}",
        )
        await db.coffre_documents.insert_one(doc.model_dump())
        return {"message": f"{label} transféré dans le coffre-fort", "document_id": doc.id}



@router.post("/coffre/upload")
async def upload_coffre_file(
    token: str,
    title: str = "",
    category: str = "documents_administratifs",
    document_type: str = "autre",
    description: str = "",
    competences_liees: str = "",
    file: UploadFile = File(...)
):
    token_doc = await get_current_token(token)
    file_content = await file.read()
    if len(file_content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Fichier trop volumineux (max 10 Mo)")

    filename = file.filename or "document"
    mime = file.content_type or get_mime_type(filename)
    file_id = str(uuid.uuid4())
    storage_path = f"reactif-pro/coffre/{token_doc['id']}/{file_id}_{filename}"

    try:
        put_object(storage_path, file_content, mime)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'upload: {str(e)}")

    comp_list = [c.strip() for c in competences_liees.split(",") if c.strip()] if competences_liees else []

    doc = CoffreDocument(
        token_id=token_doc["id"],
        title=title or filename,
        category=category,
        document_type=document_type,
        description=description,
        file_name=filename,
        file_size=len(file_content),
        mime_type=mime,
        competences_liees=comp_list,
        storage_path=storage_path,
    )
    await db.coffre_documents.insert_one(doc.model_dump())

    if comp_list:
        profile = await db.profiles.find_one({"token_id": token_doc["id"]}, {"_id": 0})
        if profile:
            existing_skills = [s.get("name") for s in profile.get("skills", [])]
            new_skills = list(profile.get("skills", []))
            for comp in comp_list:
                if comp not in existing_skills:
                    new_skills.append({"name": comp, "level": 50, "proven": True})
            await db.profiles.update_one({"token_id": token_doc["id"]}, {"$set": {"skills": new_skills}})

    return {"message": "Document uploadé dans le coffre-fort", "document_id": doc.id, "storage_path": storage_path}


@router.get("/coffre/download/{document_id}")
async def download_coffre_file(token: str, document_id: str):
    token_doc = await get_current_token(token)
    doc = await db.coffre_documents.find_one(
        {"id": document_id, "token_id": token_doc["id"]},
        {"_id": 0}
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    if not doc.get("storage_path"):
        raise HTTPException(status_code=404, detail="Aucun fichier associé à ce document")

    try:
        data, content_type = get_object(doc["storage_path"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du téléchargement: {str(e)}")

    filename = doc.get("file_name", "document")
    return Response(
        content=data,
        media_type=doc.get("mime_type", content_type),
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
