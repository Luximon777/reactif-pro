"""
Connecteur France Travail (ex-Pôle Emploi)
OAuth2 client_credentials → Offres d'emploi v2 + ROME 4.0
Doc : https://francetravail.io
"""

import os
import time
from typing import Optional
import httpx


OAUTH_URL = "https://entreprise.francetravail.fr/connexion/oauth2/access_token"
API_BASE_OFFRES = "https://api.francetravail.io/partenaire/offresdemploi/v2"
API_BASE_ROME = "https://api.francetravail.io/partenaire/rome-metiers/v1"

# Départements composant la région Grand Est (INSEE)
GRAND_EST_DEPTS = ["08", "10", "51", "52", "54", "55", "57", "67", "68", "88"]


class FranceTravailClient:
    """Client OAuth2 avec cache du token par scope demandé."""

    def __init__(self):
        self.client_id = os.environ.get("FRANCE_TRAVAIL_CLIENT_ID", "")
        self.client_secret = os.environ.get("FRANCE_TRAVAIL_CLIENT_SECRET", "")
        self._tokens: dict = {}  # scope_str -> {token, expires_at}

    def is_configured(self) -> bool:
        return bool(self.client_id and self.client_secret)

    def _scope_offres(self) -> str:
        return f"application_{self.client_id} api_offresdemploiv2 o2dsoffre"

    def _scope_rome(self) -> str:
        return f"application_{self.client_id} api_rome-metiersv1 nomenclatureRome"

    async def _get_token(self, scope: str) -> str:
        cached = self._tokens.get(scope)
        if cached and time.time() < cached["expires_at"] - 60:
            return cached["token"]
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.post(
                OAUTH_URL,
                params={"realm": "/partenaire"},
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "scope": scope,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            if r.status_code != 200:
                raise httpx.HTTPStatusError(
                    f"OAuth FT: {r.status_code} {r.text[:200]}",
                    request=r.request, response=r,
                )
            data = r.json()
        self._tokens[scope] = {
            "token": data["access_token"],
            "expires_at": time.time() + int(data.get("expires_in", 1500)),
        }
        return data["access_token"]

    # ─── Diagnostic des scopes disponibles ─────────────────────────────

    async def check_scopes(self) -> dict:
        """Teste chaque scope nécessaire et indique ce qui est souscrit."""
        results = {}
        for label, scope in [
            ("offres_emploi_v2", self._scope_offres()),
            ("rome_4", self._scope_rome()),
        ]:
            try:
                await self._get_token(scope)
                results[label] = {"souscrit": True}
            except Exception as e:
                results[label] = {"souscrit": False, "raison": str(e)[:200]}
        return results

    # ─── Offres d'emploi v2 ────────────────────────────────────────────

    async def search_offres(self, departement: str, range_offres: str = "0-149",
                            code_rome: Optional[str] = None) -> dict:
        token = await self._get_token(self._scope_offres())
        params = {"departement": departement, "range": range_offres}
        if code_rome:
            params["codeROME"] = code_rome
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(
                f"{API_BASE_OFFRES}/offres/search",
                params=params,
                headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
            )
            if r.status_code == 401:
                self._tokens.pop(self._scope_offres(), None)
                token = await self._get_token(self._scope_offres())
                r = await client.get(
                    f"{API_BASE_OFFRES}/offres/search",
                    params=params,
                    headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
                )
            r.raise_for_status()
            return r.json()

    # ─── ROME 4.0 ──────────────────────────────────────────────────────

    async def get_metiers_rome(self) -> list:
        """Liste tous les métiers ROME (≈ 600). API ROME-Métiers v1."""
        token = await self._get_token(self._scope_rome())
        async with httpx.AsyncClient(timeout=45.0) as client:
            r = await client.get(
                f"{API_BASE_ROME}/metiers/metier",
                headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
            )
            r.raise_for_status()
            return r.json()


def _coerce_int(v):
    try:
        return int(float(v)) if v is not None else None
    except (TypeError, ValueError):
        return None


def map_offre_to_opc(offre: dict, departement: str) -> dict:
    contract_map = {
        "CDI": "CDI", "CDD": "CDD", "MIS": "interim",
        "DDI": "interim", "APP": "apprentissage", "FRA": "apprentissage",
        "SAI": "CDD", "LIB": "autre", "TT": "interim",
    }
    competences = [c.get("libelle") for c in (offre.get("competences") or [])[:20]
                   if c.get("libelle")]
    mots_cles = [q.get("libelle") for q in (offre.get("qualitesProfessionnelles") or [])[:10]
                 if q.get("libelle")]
    secteur = (offre.get("secteurActiviteLibelle") or "autre").lower()
    return {
        "source": "france_travail",
        "intitule_poste": offre.get("intitule", ""),
        "code_rome": offre.get("romeCode"),
        "competences_demandees": competences,
        "mots_cles_emergents": mots_cles,
        "salaire_min": None,
        "salaire_max": None,
        "localisation": (offre.get("lieuTravail") or {}).get("libelle") or f"Dépt {departement}",
        "code_departement": departement,
        "niveau_experience_requis": offre.get("experienceLibelle"),
        "type_contrat": contract_map.get(offre.get("typeContrat"), "autre"),
        "secteur": secteur,
        "validation": {
            "source": "france_travail",
            "fiabilite": "haute",
            "territoire": "Grand Est",
            "secteur": secteur,
            "niveau_preuve": "prouve",
            "consentement_rgpd": True,
            "anonymise": True,
        },
        "_ft_id": offre.get("id"),
    }
