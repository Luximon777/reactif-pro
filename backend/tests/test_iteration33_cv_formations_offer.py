"""
Iteration 33 - Regression tests for CV analysis (formations + centres d'intérêt)
and CV offer targeting (job_offer_used, target_job, ats_keywords).

Bug fix validation:
- POST /api/cv/analyze extracts formations + centres_interet and stores them
- POST /api/cv/check-offer-match returns ats_keywords non-empty
- POST /api/cv/generate-models with job_offer returns job_offer_used / target_job / ats_keywords
- GET /api/cv/models exposes the same fields
"""
import os
import time
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://cv-analyzer-53.preview.emergentagent.com").rstrip("/")

PSEUDO = "mike9"
PASSWORD = "Solerys777!"

EXPECTED_FORMATIONS = [
    "Titre professionnel Conseiller en Insertion Professionnelle (CIP)",
    "Licence de Psychologie",
    'Certification "Accompagnement à la VAE"',
    'MOOC "Numérique et inclusion"',
]

EXPECTED_CENTRES_THEMES = ["Course à pied", "Bénévolat", "Photographie"]


@pytest.fixture(scope="module")
def token():
    r = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"pseudo": PSEUDO, "password": PASSWORD},
        timeout=30,
    )
    assert r.status_code == 200, f"login failed: {r.status_code} - {r.text}"
    data = r.json()
    assert "token" in data
    return data["token"]


class TestPassportFormationsFromCv:
    def test_passport_formations_present(self, token):
        r = requests.get(f"{BASE_URL}/api/passport", params={"token": token}, timeout=30)
        assert r.status_code == 200
        data = r.json()
        formations = data.get("formations", [])
        assert isinstance(formations, list)
        assert len(formations) >= 4, f"expected >=4 formations, got {len(formations)}"

        labels = []
        for f in formations:
            label = f.get("libelle") or f.get("title") or f.get("intitule") or ""
            labels.append(label)

        for expected in EXPECTED_FORMATIONS:
            assert any(expected in lab for lab in labels), (
                f"missing formation '{expected}', got: {labels}"
            )

    def test_passport_formations_source_cv_analysis(self, token):
        r = requests.get(f"{BASE_URL}/api/passport", params={"token": token}, timeout=30)
        data = r.json()
        formations = data.get("formations", [])
        cv_sourced = [f for f in formations if f.get("source") == "cv_analysis"]
        assert len(cv_sourced) >= 4, f"expected >=4 with source=cv_analysis, got {len(cv_sourced)}"


class TestCentresInteret:
    def test_centres_interet_returned(self, token):
        r = requests.get(
            f"{BASE_URL}/api/cv/centres-interet", params={"token": token}, timeout=30
        )
        assert r.status_code == 200
        data = r.json()
        centres = data.get("centres", [])
        assert isinstance(centres, list)
        assert len(centres) >= 3, f"expected >=3 centres, got {len(centres)}"

        themes = [c.get("theme", "") for c in centres]
        for expected in EXPECTED_CENTRES_THEMES:
            assert any(expected in t for t in themes), (
                f"missing centre '{expected}', got: {themes}"
            )


class TestCheckOfferMatch:
    def test_returns_ats_keywords_and_score(self, token):
        offer = (
            "POSTE: Conseiller emploi\n"
            "Missions: entretiens individuels, ateliers collectifs. "
            "Compétences: conduite d entretien, Pack Office."
        )
        r = requests.post(
            f"{BASE_URL}/api/cv/check-offer-match",
            params={"token": token},
            json={"offer_text": offer},
            timeout=120,
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert "score" in data
        assert isinstance(data["score"], (int, float))
        assert 0 <= data["score"] <= 100

        assert "matched_skills" in data
        assert isinstance(data["matched_skills"], list)

        assert "ats_keywords" in data, f"missing ats_keywords in response: {list(data.keys())}"
        assert isinstance(data["ats_keywords"], list)
        assert len(data["ats_keywords"]) > 0, "ats_keywords is empty"


class TestGetCvModels:
    """Regression on existing generated models with job offer."""

    def test_models_include_offer_fields(self, token):
        r = requests.get(f"{BASE_URL}/api/cv/models", params={"token": token}, timeout=30)
        assert r.status_code == 200
        data = r.json()
        assert data.get("job_offer_used") is True, f"job_offer_used should be True, got {data.get('job_offer_used')}"
        assert data.get("target_job"), "target_job is empty"
        assert isinstance(data.get("ats_keywords"), list)
        assert len(data.get("ats_keywords", [])) > 0, "ats_keywords empty in /api/cv/models"

        # target_job should match offer we tested previously (Conseiller emploi et insertion)
        assert "conseiller" in data["target_job"].lower()

        models = data.get("models", {})
        assert isinstance(models, dict)
        assert len(models) >= 1, "no models present"

        # The generated CV titre should be aligned with the target job
        for mtype, mdata in models.items():
            titre = mdata.get("titre", "")
            assert "conseiller" in titre.lower(), (
                f"model {mtype} title '{titre}' not aligned with target_job"
            )


class TestGenerateModelsWithJobOffer:
    """Optional live re-generation test (long: 30-90s per model).

    We only run this if env RUN_LONG=1 to keep the suite fast.
    """

    def test_generate_classique_with_offer(self, token):
        if os.environ.get("RUN_LONG") != "1":
            pytest.skip("skipping long LLM generation test (set RUN_LONG=1 to enable)")

        offer = (
            "POSTE: Conseiller emploi et insertion (H/F)\n"
            "Missions: entretiens individuels, ateliers collectifs, prospection entreprises."
        )
        r = requests.post(
            f"{BASE_URL}/api/cv/generate-models",
            params={"token": token},
            json={"model_types": ["classique"], "job_offer": offer},
            timeout=60,
        )
        assert r.status_code == 200, r.text

        # poll status
        deadline = time.time() + 240
        last_status = None
        while time.time() < deadline:
            sr = requests.get(
                f"{BASE_URL}/api/cv/generate-models/status",
                params={"token": token},
                timeout=30,
            )
            assert sr.status_code == 200
            last_status = sr.json()
            if last_status.get("status") in ("completed", "failed"):
                break
            time.sleep(5)

        assert last_status and last_status.get("status") == "completed", (
            f"generation not completed: {last_status}"
        )
        assert last_status.get("job_offer_used") is True
        assert last_status.get("target_job")
        assert isinstance(last_status.get("ats_keywords"), list)
        assert len(last_status.get("ats_keywords", [])) > 0
