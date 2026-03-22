from fastapi import APIRouter
import httpx
import logging

router = APIRouter()


@router.get("/siret/verify")
async def verify_siret(siret: str):
    """Verify a SIRET number using the free API Recherche d'Entreprises (data.gouv.fr)"""
    siret_clean = siret.strip().replace(" ", "")

    if not siret_clean.isdigit() or len(siret_clean) not in (9, 14):
        return {
            "valid": False,
            "error": "Le numéro doit contenir 9 chiffres (SIREN) ou 14 chiffres (SIRET)"
        }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"https://recherche-entreprises.api.gouv.fr/search?q={siret_clean}&per_page=1"
            )
            if resp.status_code != 200:
                return {"valid": False, "error": "Service de vérification temporairement indisponible"}

            data = resp.json()
            results = data.get("results", [])

            if not results:
                return {"valid": False, "error": "Aucune entreprise trouvée pour ce numéro"}

            company = results[0]
            nom = company.get("nom_complet", "")
            siren = company.get("siren", "")
            siege = company.get("siege", {})
            naf = siege.get("activite_principale", "")
            adresse = siege.get("adresse", "")
            nature = company.get("nature_juridique", "")
            tranche = company.get("tranche_effectif_salarie", "")

            # Check if it matches
            found_siren = siren
            found_siret = siege.get("siret", "")

            is_match = (siret_clean == found_siren or siret_clean == found_siret
                        or found_siren.startswith(siret_clean) or siret_clean.startswith(found_siren))

            return {
                "valid": is_match,
                "company_name": nom,
                "siren": found_siren,
                "siret": found_siret,
                "naf": naf,
                "adresse": adresse,
                "nature_juridique": nature,
                "tranche_effectif": tranche
            }

    except Exception as e:
        logging.warning(f"SIRET verification error: {e}")
        return {"valid": False, "error": "Erreur lors de la vérification. Réessayez plus tard."}
