"""
Tests de régression — Travail du 22 juin 2026.
Vérifie que toutes les fonctionnalités implémentées fonctionnent.
Lancer: pytest /app/backend/tests/test_22juin.py -v
"""
import os
import pytest
import httpx

API_URL = os.environ.get("REACT_APP_BACKEND_URL", "http://localhost:8001")
if not API_URL.startswith("http"):
    API_URL = "http://localhost:8001"
API = f"{API_URL}/api"

PETER7_CREDS = {"pseudo": "peter7", "password": "Solerys777!"}
MIKE7_CREDS = {"pseudo": "mike7", "password": "Solerys777!"}


@pytest.fixture
def peter7_token():
    r = httpx.post(f"{API}/auth/login", json=PETER7_CREDS)
    assert r.status_code == 200
    return r.json()["token"]


@pytest.fixture
def mike7_token():
    r = httpx.post(f"{API}/auth/login", json=MIKE7_CREDS)
    assert r.status_code == 200
    return r.json()["token"]


# === 1. Gate State (Admin ouvre la plateforme) ===

def test_gate_state_get():
    r = httpx.get(f"{API}/admin/gate-state")
    assert r.status_code == 200
    assert "spaces_open" in r.json()


# === 2. Passport Formations ===

def test_passport_has_formations_field(peter7_token):
    r = httpx.get(f"{API}/passport?token={peter7_token}")
    assert r.status_code == 200
    data = r.json()
    assert "formations" in data, "Le passport doit contenir le champ 'formations'"


def test_add_formation(mike7_token):
    r = httpx.post(f"{API}/passport/formations?token={mike7_token}", json={
        "title": "Test Formation Régression",
        "institution": "Test Institut",
        "year": "2025",
        "type": "certification",
    })
    assert r.status_code == 200
    data = r.json()
    assert data.get("id"), "La formation doit avoir un ID"
    assert data["title"] == "Test Formation Régression"

    # Cleanup
    httpx.delete(f"{API}/passport/formations/{data['id']}?token={mike7_token}")


# === 3. Illustrations avec skill_type ===

def test_illustration_skill_type(mike7_token):
    # Get first experience
    r = httpx.get(f"{API}/passport?token={mike7_token}")
    exps = r.json().get("experiences", [])
    if not exps:
        pytest.skip("Aucune expérience pour mike7")

    exp_id = exps[0]["id"]
    r = httpx.post(f"{API}/passport/illustrations?token={mike7_token}", json={
        "experience_id": exp_id,
        "soft_skill": "Test Hard Skill Regression",
        "skill_type": "hard",
        "sare_situation": "Test situation",
        "sare_action": "Test action",
        "sare_resultat": "Test résultat",
        "sare_enseignement": "Test enseignement",
    })
    assert r.status_code == 200
    illus_id = r.json().get("id")
    assert illus_id

    # Cleanup
    httpx.delete(f"{API}/passport/illustrations/{illus_id}?token={mike7_token}")


# === 4. Coffre-fort sans fichier (Certifier) ===

def test_coffre_document_without_file(mike7_token):
    r = httpx.post(f"{API}/coffre/documents?token={mike7_token}", json={
        "title": "Certification Test Régression",
        "category": "experience_prouvee",
        "document_type": "certification_competences",
        "description": "Test sans fichier",
    })
    assert r.status_code == 200
    doc_id = r.json().get("id")
    assert doc_id, "Le document coffre doit avoir un ID"

    # Cleanup
    httpx.delete(f"{API}/coffre/documents/{doc_id}?token={mike7_token}")


# === 5. Scoring CV/Offre (IA) ===

def test_offer_scoring(peter7_token):
    r = httpx.post(f"{API}/cv/check-offer-match?token={peter7_token}", json={
        "offer_text": "Chef de Partie Cuisinier CDI Restauration traditionnelle Strasbourg"
    }, timeout=30)
    assert r.status_code == 200
    data = r.json()
    assert "score" in data
    assert data["score"] >= 50, f"Score trop bas ({data['score']}%) pour un chef de cuisine sur un poste cuisinier"


# === 6. Archéologie avec D'CLIC PRO ===

def test_archeologie_dclic_integration(peter7_token):
    r = httpx.get(f"{API}/passport/archeologie?token={peter7_token}")
    assert r.status_code == 200
    data = r.json()
    summary = data.get("summary", {})
    assert "dclic_integrated" in summary, "Le résumé doit indiquer si D'CLIC est intégré"

    # Si D'CLIC est intégré, vérifier les vertus
    if summary.get("dclic_integrated"):
        assert data.get("dclic_vertus") is not None, "Les vertus D'CLIC doivent être présentes"
        assert data["dclic_vertus"].get("scores"), "Les scores des 6 vertus doivent être présents"


# === 7. Job Dating matching enrichi ===

def test_jobdating_recommended(peter7_token):
    r = httpx.get(f"{API}/jobdating/recommended?token={peter7_token}")
    assert r.status_code == 200
    data = r.json()
    events = data.get("events", [])
    assert len(events) > 0, "Il doit y avoir des événements recommandés"

    # Les événements doivent avoir des URLs valides
    for evt in events:
        url = evt.get("registration_url", "")
        assert "mesevenementsemploi.francetravail.fr" in url, f"URL invalide: {url}"
        assert "evenement/10000" not in url, f"URL avec faux ID: {url}"

    # Le 1er événement doit être lié à la restauration pour peter7
    top = events[0]
    assert top["match_score"] >= 50, f"Score du top event trop bas: {top['match_score']}%"


# === 8. Job Dating events ===

def test_jobdating_events(peter7_token):
    r = httpx.get(f"{API}/jobdating/events?token={peter7_token}")
    assert r.status_code == 200
    data = r.json()
    assert "events" in data
    assert data["total"] > 0
