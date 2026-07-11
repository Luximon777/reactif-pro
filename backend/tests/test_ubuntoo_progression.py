"""Backend tests — Ubuntoo Progression (Iteration 46 : ICU + Piste Preuves + 5 Familles).

Endpoints tested:
- POST /api/social/auth/sso        : SSO from Ré'Actif Pro JWT to Ubuntoo JWT
- GET  /api/social/progression     : levels[7], icu[5], proof_track, families[5], stats, level_up, new_badges
- POST /api/social/charter/accept  : sets charter_accepted=true
- PUT  /api/social/users/profile   : profile completion -> Explorateur criteria
- GET  /api/social/posts           : feed regression
"""
import os
import uuid
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://cv-analyzer-53.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"

LEVEL_IDS = ["explorateur", "contributeur", "ambassadeur", "expert", "mentor", "leader", "pionnier"]
ICU_DIMS = ["competence", "fiabilite", "collaboration", "impact", "engagement"]
PROOF_TIERS = [1, 5, 10, 25, 50]
FAMILY_IDS = ["engagement", "expertise", "solidarite", "innovation", "leadership"]
ORIGIN_IDS = ["experience_pro", "formation", "certification", "evaluation_terrain", "projet_perso", "benevolat"]


# ---------- Fixtures ----------
@pytest.fixture(scope="module")
def http():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


def _reactif_login(http, pseudo, password):
    r = http.post(f"{API}/auth/login", json={"pseudo": pseudo, "password": password}, timeout=20)
    return r


def _sso(http, reactif_token):
    return http.post(f"{API}/social/auth/sso", json={"token": reactif_token}, timeout=20)


@pytest.fixture(scope="module")
def peter_ubuntoo_jwt(http):
    """peter7 — already accepted charter, level Explorateur."""
    r = _reactif_login(http, "peter7", "Solerys777!")
    if r.status_code != 200:
        pytest.skip(f"peter7 Ré'Actif login failed: {r.status_code} {r.text[:200]}")
    tok = r.json().get("token")
    s = _sso(http, tok)
    assert s.status_code == 200, f"SSO failed: {s.status_code} {s.text[:200]}"
    return s.json()["token"]


@pytest.fixture(scope="module")
def fresh_user(http):
    """Creates a fresh Ré'Actif Pro user for progression testing."""
    pseudo = f"TEST_prog_{uuid.uuid4().hex[:8]}"
    pwd = "Test@Pass777!"
    r = http.post(f"{API}/auth/register", json={"pseudo": pseudo, "password": pwd}, timeout=20)
    if r.status_code not in (200, 201):
        pytest.skip(f"register failed: {r.status_code} {r.text[:200]}")
    data = r.json()
    tok = data.get("token") or data.get("access_token")
    if not tok:
        # try login
        rl = _reactif_login(http, pseudo, pwd)
        if rl.status_code == 200:
            tok = rl.json().get("token")
    assert tok, f"no token after register: {data}"
    s = _sso(http, tok)
    assert s.status_code == 200, f"SSO failed for fresh user: {s.status_code} {s.text[:200]}"
    return {"pseudo": pseudo, "password": pwd, "reactif_token": tok, "ubuntoo_jwt": s.json()["token"], "ubuntoo_user": s.json()["user"]}


# ---------- SSO ----------
class TestSSO:
    def test_sso_with_valid_reactif_token(self, http):
        r = _reactif_login(http, "peter7", "Solerys777!")
        if r.status_code != 200:
            pytest.skip("peter7 login unavailable")
        reactif_tok = r.json()["token"]
        s = _sso(http, reactif_tok)
        assert s.status_code == 200
        body = s.json()
        assert "token" in body and isinstance(body["token"], str) and len(body["token"]) > 20
        assert "user" in body and body["user"].get("id")

    def test_sso_invalid_token_rejected(self, http):
        s = _sso(http, "invalid.reactif.token.xxx")
        assert s.status_code in (401, 403, 422, 400)


# ---------- Progression schema ----------
class TestProgressionSchema:
    def test_progression_returns_full_shape(self, http, peter_ubuntoo_jwt):
        r = http.get(f"{API}/social/progression", headers={"Authorization": f"Bearer {peter_ubuntoo_jwt}"}, timeout=20)
        assert r.status_code == 200, r.text[:300]
        data = r.json()
        # top-level keys
        for k in ["current_level", "next_level", "levels", "dimensions", "stats", "level_up"]:
            assert k in data, f"missing key {k}"
        # 7 levels in the correct order
        assert isinstance(data["levels"], list) and len(data["levels"]) == 7
        assert [lv["id"] for lv in data["levels"]] == LEVEL_IDS
        # each level has criteria list + unlocks + achieved bool + index
        for i, lv in enumerate(data["levels"]):
            assert lv["index"] == i
            assert isinstance(lv["achieved"], bool)
            assert isinstance(lv["unlocks"], list) and len(lv["unlocks"]) >= 1
            assert isinstance(lv["criteria"], list) and len(lv["criteria"]) >= 1
            for c in lv["criteria"]:
                assert "label" in c and "met" in c and isinstance(c["met"], bool)

        # 4 dimensions with 0..100 ints  (regression: legacy 'dimensions' still present)
        for k in ["contribution", "expertise", "engagement", "impact"]:
            assert k in data["dimensions"]
            v = data["dimensions"][k]
            assert isinstance(v, int) and 0 <= v <= 100
        # stats fields
        for k in ["profile_completion", "charter_accepted", "posts_count", "comments_count"]:
            assert k in data["stats"]


# ---------- Iteration 46 : ICU + Proof Track + Families ----------
class TestICUAndProofsSchema:
    def test_progression_returns_icu_proof_track_families(self, http, peter_ubuntoo_jwt):
        r = http.get(f"{API}/social/progression", headers={"Authorization": f"Bearer {peter_ubuntoo_jwt}"}, timeout=20)
        assert r.status_code == 200, r.text[:300]
        d = r.json()
        # ICU — 5 dimensions + global
        assert "icu" in d, "missing icu"
        icu = d["icu"]
        for k in ICU_DIMS + ["global"]:
            assert k in icu, f"icu missing {k}"
            assert isinstance(icu[k], int) and 0 <= icu[k] <= 100
        # proof_track
        assert "proof_track" in d
        pt = d["proof_track"]
        assert "count" in pt and isinstance(pt["count"], int)
        assert "tiers" in pt and len(pt["tiers"]) == 5
        assert [t["threshold"] for t in pt["tiers"]] == PROOF_TIERS
        assert [t["id"] for t in pt["tiers"]] == [f"proof_{n}" for n in PROOF_TIERS]
        for t in pt["tiers"]:
            assert "earned" in t and isinstance(t["earned"], bool)
            assert "name" in t
        assert "next_tier" in pt  # may be None
        assert "origins" in pt and len(pt["origins"]) == 6
        assert [o["id"] for o in pt["origins"]] == ORIGIN_IDS
        assert "diversity_earned" in pt and isinstance(pt["diversity_earned"], bool)
        assert "verified_earned" in pt and isinstance(pt["verified_earned"], bool)
        # families
        assert "families" in d and len(d["families"]) == 5
        assert [f["id"] for f in d["families"]] == FAMILY_IDS
        for f in d["families"]:
            assert "name" in f and "desc" in f and "icon" in f
            assert isinstance(f["badges"], list) and len(f["badges"]) >= 1
            for b in f["badges"]:
                assert "id" in b and "name" in b and "earned" in b
        # new_badges
        assert "new_badges" in d and isinstance(d["new_badges"], list)

    def test_peter7_all_proof_tiers_earned(self, http, peter_ubuntoo_jwt):
        """peter7 has 52+ preuves RE'ACTIF PRO → all 5 tiers + diversity + verified earned."""
        h = {"Authorization": f"Bearer {peter_ubuntoo_jwt}"}
        r = http.get(f"{API}/social/progression", headers=h, timeout=20)
        assert r.status_code == 200
        d = r.json()
        pt = d["proof_track"]
        # count >= 50
        assert pt["count"] >= 50, f"peter7 should have >=50 preuves, got {pt['count']}"
        # all 5 tiers earned
        for t in pt["tiers"]:
            assert t["earned"] is True, f"tier {t['id']} not earned (count={pt['count']})"
        assert pt["next_tier"] is None, "no next_tier when all earned"
        assert pt["diversity_earned"] is True
        assert pt["verified_earned"] is True
        # famille expertise 7/7 badges earned
        expertise = next(f for f in d["families"] if f["id"] == "expertise")
        assert len(expertise["badges"]) == 7
        for b in expertise["badges"]:
            assert b["earned"] is True, f"expertise badge {b['id']} not earned"

    def test_peter7_idempotent_new_badges(self, http, peter_ubuntoo_jwt):
        """Second call after all proof badges earned → new_badges=[] (persisted)."""
        h = {"Authorization": f"Bearer {peter_ubuntoo_jwt}"}
        # Call twice
        r1 = http.get(f"{API}/social/progression", headers=h, timeout=20)
        assert r1.status_code == 200
        r2 = http.get(f"{API}/social/progression", headers=h, timeout=20)
        assert r2.status_code == 200
        # After the first call, badges are persisted, so second should return []
        assert r2.json()["new_badges"] == [], f"new_badges not idempotent: {r2.json()['new_badges']}"

    def test_icu_ancient_dimensions_removed_from_ui_but_backend_keeps_legacy(self, http, peter_ubuntoo_jwt):
        """The spec says UI must use ICU (5 dims). Backend still returns legacy 'dimensions'
        for backward-compat. Assert both are present with distinct keys."""
        h = {"Authorization": f"Bearer {peter_ubuntoo_jwt}"}
        d = http.get(f"{API}/social/progression", headers=h, timeout=20).json()
        # legacy dims exist (backend regression)
        for k in ["contribution", "expertise", "engagement", "impact"]:
            assert k in d["dimensions"]
        # ICU is separate
        assert set(d["icu"].keys()) - {"global"} == set(ICU_DIMS)


class TestFreshUserProofsAndICU:
    def test_fresh_user_no_proofs(self, http, fresh_user):
        """Fresh user (no RE'ACTIF preuves) → count=0, no tier earned, low icu.competence."""
        h = {"Authorization": f"Bearer {fresh_user['ubuntoo_jwt']}"}
        d = http.get(f"{API}/social/progression", headers=h, timeout=20).json()
        pt = d["proof_track"]
        assert pt["count"] == 0
        for t in pt["tiers"]:
            assert t["earned"] is False, f"tier {t['id']} unexpectedly earned"
        assert pt["diversity_earned"] is False
        assert pt["verified_earned"] is False
        # first tier is next
        assert pt["next_tier"] is not None
        assert pt["next_tier"]["threshold"] == 1
        # icu.competence should be 0 (no proofs, no origins, not verified)
        assert d["icu"]["competence"] == 0, f"expected competence=0 got {d['icu']['competence']}"
        # No proof badges awarded
        assert d["new_badges"] == []
        # families still returned
        assert len(d["families"]) == 5
        expertise = next(f for f in d["families"] if f["id"] == "expertise")
        # All expertise badges should be locked
        for b in expertise["badges"]:
            assert b["earned"] is False, f"unexpected earned badge {b['id']} on fresh user"


# ---------- Charter ----------
class TestCharter:
    def test_accept_charter_endpoint(self, http, fresh_user):
        h = {"Authorization": f"Bearer {fresh_user['ubuntoo_jwt']}"}
        # initially likely not accepted
        r0 = http.get(f"{API}/social/progression", headers=h, timeout=20)
        assert r0.status_code == 200
        # accept
        ra = http.post(f"{API}/social/charter/accept", headers=h, timeout=20)
        assert ra.status_code == 200
        assert ra.json() == {"accepted": True}
        # verify persistence
        r1 = http.get(f"{API}/social/progression", headers=h, timeout=20)
        assert r1.status_code == 200
        assert r1.json()["stats"]["charter_accepted"] is True


# ---------- Progression logic ----------
class TestProgressionLogic:
    def test_fresh_user_no_level_before_profile(self, http, fresh_user):
        h = {"Authorization": f"Bearer {fresh_user['ubuntoo_jwt']}"}
        r = http.get(f"{API}/social/progression", headers=h, timeout=20)
        assert r.status_code == 200
        d = r.json()
        # Fresh user with empty profile and no charter should not have Explorateur achieved
        expl = next(lv for lv in d["levels"] if lv["id"] == "explorateur")
        assert expl["achieved"] is False

    def test_sequential_levels(self, http, fresh_user):
        """A user who is not Explorateur cannot be Contributeur (sequential)."""
        h = {"Authorization": f"Bearer {fresh_user['ubuntoo_jwt']}"}
        r = http.get(f"{API}/social/progression", headers=h, timeout=20)
        d = r.json()
        expl = next(lv for lv in d["levels"] if lv["id"] == "explorateur")
        contr = next(lv for lv in d["levels"] if lv["id"] == "contributeur")
        if not expl["achieved"]:
            assert contr["achieved"] is False, "Contributeur should not be achieved before Explorateur"

    def test_complete_profile_charter_reaches_explorateur(self, http, fresh_user):
        h = {"Authorization": f"Bearer {fresh_user['ubuntoo_jwt']}"}
        # Complete profile
        profile = {
            "bio": "Membre passionné par la solidarité et l'entraide dans la communauté.",
            "location": "Paris, France",
            "sector": "Ressources humaines",
            "skills": ["mentorat", "communication", "gestion de projet"],
            "jobs_sought": ["Chef de projet", "Consultant RH"],
            "availability": "temps_plein",
            "languages": ["Français", "Anglais"],
        }
        pu = http.put(f"{API}/social/users/profile", headers=h, json=profile, timeout=20)
        assert pu.status_code == 200, pu.text[:300]

        # Accept charter (idempotent)
        ac = http.post(f"{API}/social/charter/accept", headers=h, timeout=20)
        assert ac.status_code == 200

        # First call -> level_up should be True (transition from -1 to 0)
        r1 = http.get(f"{API}/social/progression", headers=h, timeout=20)
        assert r1.status_code == 200
        d1 = r1.json()
        # Explorateur should be achieved (profile ≥70%, charter accepted, bio present)
        expl = next(lv for lv in d1["levels"] if lv["id"] == "explorateur")
        assert expl["achieved"] is True, f"Explorateur should be achieved. criteria={expl['criteria']} stats={d1['stats']}"
        assert d1["current_level"] is not None and d1["current_level"]["id"] == "explorateur"
        assert d1["level_up"] is True, f"first call after unlock should be level_up=True. level_up={d1['level_up']}"

        # Second call -> level_up should be False (idempotent, stored level_index=0)
        r2 = http.get(f"{API}/social/progression", headers=h, timeout=20)
        assert r2.status_code == 200
        d2 = r2.json()
        assert d2["current_level"]["id"] == "explorateur"
        assert d2["level_up"] is False, "second call should be idempotent, level_up=False"


# ---------- Regression: feed still works ----------
class TestFeedRegression:
    def test_get_posts(self, http, peter_ubuntoo_jwt):
        r = http.get(f"{API}/social/posts", headers={"Authorization": f"Bearer {peter_ubuntoo_jwt}"}, timeout=20)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_create_and_read_post(self, http, peter_ubuntoo_jwt):
        h = {"Authorization": f"Bearer {peter_ubuntoo_jwt}"}
        payload = {"content": f"TEST_post {uuid.uuid4().hex[:6]} — regression check", "post_type": "text"}
        rc = http.post(f"{API}/social/posts", headers=h, json=payload, timeout=20)
        assert rc.status_code == 200, rc.text[:200]
        assert rc.json().get("content", "").startswith("TEST_post")
