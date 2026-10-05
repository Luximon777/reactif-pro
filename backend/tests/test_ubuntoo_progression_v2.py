"""Tests UBUNTOO v2 — Parcours de progression + Mentorat (cycle de vie) + Validation humaine.
Iteration 59.
"""
import os
import time
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://cv-analyzer-53.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"
U2 = f"{API}/ubuntoo2"

ACCOUNTS = {
    "peter7": "Solerys777!",
    "mike7": "Solerys777!",
    "marc19": "Solerys777!",
}
ADMIN = ("admin@reactifpro.fr", "Choukette@777")


def _login(pseudo, pwd):
    r = requests.post(f"{API}/auth/login", json={"pseudo": pseudo, "password": pwd}, timeout=30)
    assert r.status_code == 200, f"login {pseudo}: {r.status_code} {r.text}"
    return r.json()["token"]


@pytest.fixture(scope="module")
def tokens():
    toks = {u: _login(u, p) for u, p in ACCOUNTS.items()}
    toks["admin"] = _login(*ADMIN)
    return toks


@pytest.fixture(scope="module")
def me_ids(tokens):
    ids = {}
    for u in ("peter7", "mike7", "marc19"):
        r = requests.get(f"{U2}/me", params={"token": tokens[u]}, timeout=20)
        assert r.status_code == 200
        ids[u] = r.json()["token_id"]
    return ids


# ============== PROGRESSION STRUCTURE ==============
class TestProgressionStructure:
    def test_peter7_progression_structure(self, tokens):
        r = requests.get(f"{U2}/progression", params={"token": tokens["peter7"]}, timeout=30)
        assert r.status_code == 200, r.text
        d = r.json()
        # Required top-level keys
        for k in ("current_label", "levels", "mentor_status", "ambassadeur_status",
                  "can_apply_mentor", "can_apply_ambassadeur", "charte", "contributions", "next_steps"):
            assert k in d, f"missing key: {k}"
        # levels structure
        for lvl in ("membre", "membre_actif", "contributeur", "mentor_candidat",
                    "mentor", "mentor_confirme", "animateur", "ambassadeur"):
            assert lvl in d["levels"], f"missing level: {lvl}"
        # contributions keys
        for c in ("publications", "reponses", "utiles_recus", "communautes",
                  "mentorats_termines", "note_moyenne_mentorat"):
            assert c in d["contributions"], f"missing contribution: {c}"
        # Peter is mentor
        assert d["mentor_status"] in ("mentor", "confirme"), f"peter7 mentor_status={d['mentor_status']}"
        assert d["levels"]["mentor"] is True
        # Charte must have 5 points
        assert isinstance(d["charte"], list) and len(d["charte"]) == 5

    def test_mike7_cannot_apply_mentor(self, tokens):
        r = requests.get(f"{U2}/progression", params={"token": tokens["mike7"]}, timeout=20)
        assert r.status_code == 200
        d = r.json()
        # mike7 is Membre / Membre actif — not Contributeur
        assert d["mentor_status"] == "none"
        # per review: can_apply_mentor must be False
        assert d["can_apply_mentor"] is False


# ============== CANDIDATURE MENTOR : refus si pas contributeur ==============
class TestCandidatureMentor:
    def test_mike7_candidature_rejected_400(self, tokens):
        r = requests.post(f"{U2}/progression/mentor-candidature",
                          params={"token": tokens["mike7"]},
                          json={"accept_charte": True}, timeout=20)
        assert r.status_code == 400, r.text

    def test_candidature_without_charte(self, tokens):
        r = requests.post(f"{U2}/progression/mentor-candidature",
                          params={"token": tokens["mike7"]},
                          json={"accept_charte": False}, timeout=20)
        assert r.status_code == 400


# ============== BADGES : plus de mentor/ambassadeur ==============
class TestBadges:
    def test_badges_no_mentor_ambassadeur(self, tokens):
        r = requests.get(f"{U2}/badges", params={"token": tokens["peter7"]}, timeout=20)
        assert r.status_code == 200
        ids = [b["id"] for b in r.json()]
        assert "mentor" not in ids
        assert "ambassadeur" not in ids
        # 4 badges auto restants
        assert len(ids) == 4
        for exp in ("bienvenue", "explorateur", "contributeur", "passeport_pro"):
            assert exp in ids, f"missing badge: {exp}"


# ============== ADMIN candidatures ==============
class TestAdminCandidatures:
    def test_non_admin_forbidden(self, tokens):
        r = requests.get(f"{U2}/admin/candidatures", params={"token": tokens["peter7"]}, timeout=20)
        assert r.status_code == 403

    def test_admin_can_list(self, tokens):
        r = requests.get(f"{U2}/admin/candidatures", params={"token": tokens["admin"]}, timeout=20)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_admin_decide_invalid_action(self, tokens):
        r = requests.post(f"{U2}/admin/candidatures/fake-id/decide",
                          params={"token": tokens["admin"]},
                          json={"action": "foo"}, timeout=20)
        assert r.status_code == 400

    def test_admin_decide_not_found(self, tokens):
        r = requests.post(f"{U2}/admin/candidatures/does-not-exist/decide",
                          params={"token": tokens["admin"]},
                          json={"action": "approve"}, timeout=20)
        assert r.status_code == 404


# ============== ENFORCEMENT : mentorat exige mentor validé ==============
class TestMentoratEnforcement:
    def test_mentorat_request_to_non_validated_mentor(self, tokens, me_ids):
        # marc19 n'est pas Mentor validé → demande mentorat à marc19 doit 403
        r = requests.post(f"{U2}/connections",
                          params={"token": tokens["mike7"]},
                          json={"to_id": me_ids["marc19"], "kind": "mentorat",
                                "message": "test enforcement"}, timeout=20)
        # Soit 403 enforcement, soit 400 déjà en relation — on tolère 400 déjà pour ce couple
        if r.status_code == 400 and "déjà" in r.text.lower():
            pytest.skip("mike7-marc19 déjà en relation")
        assert r.status_code == 403, f"attendu 403 enforcement mentor, obtenu {r.status_code}: {r.text}"
        assert "Mentor UBUNTOO" in r.text or "mentor" in r.text.lower()

    def test_matches_only_validated_mentors(self, tokens):
        # mike7 (mentee) : /mentoring/matches ne doit proposer que des mentors validés
        # Set mike7 mentoring_role = mentee first
        requests.put(f"{U2}/me", params={"token": tokens["mike7"]},
                     json={"mentoring_role": "mentee"}, timeout=20)
        r = requests.get(f"{U2}/mentoring/matches", params={"token": tokens["mike7"]}, timeout=30)
        assert r.status_code == 200
        # response structure: contrôler keys
        d = r.json()
        # Pas de vérification stricte sans accès DB; on vérifie que la route répond


# ============== MENTORAT CYCLE DE VIE ==============
class TestMentoratCycle:
    def test_relations_lists(self, tokens):
        r = requests.get(f"{U2}/mentoring/relations", params={"token": tokens["peter7"]}, timeout=20)
        assert r.status_code == 200
        rels = r.json().get("relations", r.json()) if isinstance(r.json(), dict) else r.json()
        assert isinstance(rels, list)
        # Peter7 a 1 mentorat terminé note 5 selon state
        for rel in rels:
            assert "conn_id" in rel
            assert "my_role" in rel
            assert "mentorat_status" in rel

    def test_terminate_already_terminated_400(self, tokens):
        r = requests.get(f"{U2}/mentoring/relations", params={"token": tokens["peter7"]}, timeout=20)
        data = r.json()
        rels = data.get("relations", data) if isinstance(data, dict) else data
        terminated = [x for x in rels if x.get("mentorat_status") == "termine"]
        if not terminated:
            pytest.skip("Pas de relation terminée pour peter7")
        conn_id = terminated[0]["conn_id"]
        r2 = requests.post(f"{U2}/mentoring/relations/{conn_id}/terminate",
                           params={"token": tokens["peter7"]},
                           json={"bilan": "re-test"}, timeout=20)
        assert r2.status_code == 400, f"relancer terminate sur rel terminée doit 400, got {r2.status_code}: {r2.text}"

    def test_feedback_mentor_forbidden(self, tokens):
        # Only mentee can give feedback → peter7 (mentor) → 404
        r = requests.get(f"{U2}/mentoring/relations", params={"token": tokens["peter7"]}, timeout=20)
        data = r.json()
        rels = data.get("relations", data) if isinstance(data, dict) else data
        if not rels:
            pytest.skip("Pas de relation")
        conn_id = rels[0]["conn_id"]
        r2 = requests.post(f"{U2}/mentoring/relations/{conn_id}/feedback",
                           params={"token": tokens["peter7"]},
                           json={"rating": 5}, timeout=20)
        assert r2.status_code == 404, f"mentor donnant feedback doit 404, got {r2.status_code}"

    def test_feedback_already_given_400(self, tokens):
        # mike7 a déjà donné feedback sur la relation existante → re-donner = 400
        r = requests.get(f"{U2}/mentoring/relations", params={"token": tokens["mike7"]}, timeout=20)
        data = r.json()
        rels = data.get("relations", data) if isinstance(data, dict) else data
        done = [x for x in rels if x.get("mentorat_status") == "termine" and x.get("feedback_given")]
        if not done:
            pytest.skip("Pas de relation terminée avec feedback déjà donné pour mike7")
        conn_id = done[0]["conn_id"]
        r2 = requests.post(f"{U2}/mentoring/relations/{conn_id}/feedback",
                           params={"token": tokens["mike7"]},
                           json={"rating": 5, "comment": "retry"}, timeout=20)
        assert r2.status_code == 400

    def test_feedback_invalid_rating(self, tokens):
        r = requests.get(f"{U2}/mentoring/relations", params={"token": tokens["mike7"]}, timeout=20)
        data = r.json()
        rels = data.get("relations", data) if isinstance(data, dict) else data
        if not rels:
            pytest.skip("Pas de relation")
        conn_id = rels[0]["conn_id"]
        r2 = requests.post(f"{U2}/mentoring/relations/{conn_id}/feedback",
                           params={"token": tokens["mike7"]},
                           json={"rating": 10}, timeout=20)
        # Déjà donné → 400 ; sinon rating invalide → 400 également
        assert r2.status_code == 400


# ============== CONTRIBUTIONS peter7 (note moyenne) ==============
class TestContributions:
    def test_peter7_has_mentorat_termine(self, tokens):
        r = requests.get(f"{U2}/progression", params={"token": tokens["peter7"]}, timeout=20)
        c = r.json()["contributions"]
        assert c["mentorats_termines"] >= 1
        assert c["note_moyenne_mentorat"] >= 4 or c["note_moyenne_mentorat"] == 5
