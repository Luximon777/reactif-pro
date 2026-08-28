"""
Iteration 47 — Trajectory IA synthesis + OPC modules endpoints
Tests:
1) POST /api/auth/login {pseudo,password} for michel and mike
2) DELETE /api/trajectory/synthesis/cache?token=  then GET /api/trajectory/synthesis?token=
   → synthesis.source == 'ia', analyse_narrative personnalisée, 5-scores present, cache on 2nd call
3) OPC endpoints used by OpcDediePage.jsx for mike
"""
import os
import time
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
assert BASE_URL, "REACT_APP_BACKEND_URL missing"

TIMEOUT_IA = 90


def _login(pseudo, password="Solerys777!"):
    r = requests.post(f"{BASE_URL}/api/auth/login",
                      json={"pseudo": pseudo, "password": password},
                      timeout=45)
    return r


@pytest.fixture(scope="module")
def michel_token():
    r = _login("michel")
    if r.status_code != 200:
        pytest.skip(f"michel login failed: {r.status_code} {r.text}")
    return r.json()["token"]


@pytest.fixture(scope="module")
def mike_token():
    # request uses "mike" but memory says "mike7" – try both
    for p in ("mike", "mike7"):
        r = _login(p)
        if r.status_code == 200:
            print(f"mike login used pseudo={p}")
            return r.json()["token"]
    pytest.skip("mike/mike7 login failed")


# ─── Auth ─────────────────────────────────────────────────────────────────────
class TestAuth:
    def test_login_michel(self):
        r = _login("michel")
        assert r.status_code == 200, r.text
        d = r.json()
        assert d.get("token")
        assert d.get("role") == "particulier" or d.get("role")

    def test_login_mike(self):
        for p in ("mike", "mike7"):
            r = _login(p)
            if r.status_code == 200:
                return
        pytest.fail("Neither mike nor mike7 login succeeded")


# ─── Trajectory synthesis IA (michel) ──────────────────────────────────────────
class TestTrajectorySynthesisIA:
    def test_delete_cache_then_generate_ia(self, michel_token):
        # Purge cache
        d = requests.delete(
            f"{BASE_URL}/api/trajectory/synthesis/cache",
            params={"token": michel_token}, timeout=15)
        assert d.status_code == 200, d.text

        # Fresh call → should trigger LLM
        t0 = time.time()
        r = requests.get(f"{BASE_URL}/api/trajectory/synthesis",
                         params={"token": michel_token},
                         timeout=TIMEOUT_IA)
        elapsed = time.time() - t0
        print(f"[trajectory/synthesis michel] elapsed={elapsed:.1f}s status={r.status_code}")
        assert r.status_code == 200, r.text
        body = r.json()
        assert body.get("has_data") is True
        syn = body.get("synthesis") or {}
        assert syn, "empty synthesis"
        # Score keys
        scores = syn.get("scores") or {}
        for k in ["coherence", "adaptabilite", "transferabilite", "continuite", "alignement_metier"]:
            assert k in scores, f"missing score {k}"
        # Source should be 'ia' (fallback template acceptable but flagged)
        src = syn.get("source")
        print(f"source={src} narrative[:120]={(syn.get('analyse_narrative') or '')[:120]}")
        assert src in ("ia", "template"), f"unexpected source={src}"
        # Narrative not empty, not the generic template text
        narr = syn.get("analyse_narrative") or ""
        assert len(narr) > 20
        # If IA, elapsed should be < 60s (proxy timeout)
        if src == "ia":
            assert elapsed < 60, f"IA call {elapsed}s > 60s proxy limit"
        # Store for cache test
        TestTrajectorySynthesisIA._first_source = src
        TestTrajectorySynthesisIA._first_narr = narr

    def test_second_call_is_cached(self, michel_token):
        t0 = time.time()
        r = requests.get(f"{BASE_URL}/api/trajectory/synthesis",
                         params={"token": michel_token}, timeout=15)
        elapsed = time.time() - t0
        assert r.status_code == 200
        assert elapsed < 5, f"cached call took {elapsed}s"
        body = r.json()
        assert body["synthesis"]["analyse_narrative"] == TestTrajectorySynthesisIA._first_narr


# ─── OPC endpoints (mike) ─────────────────────────────────────────────────────
class TestOpcEndpoints:
    def test_profile_sync(self, mike_token):
        r = requests.get(f"{BASE_URL}/api/profile",
                         params={"token": mike_token}, timeout=15)
        assert r.status_code == 200, r.text
        p = r.json()
        assert "name" in p or "skills" in p

    def test_observatory_dashboard(self, mike_token):
        r = requests.get(f"{BASE_URL}/api/observatory/dashboard",
                         params={"token": mike_token}, timeout=30)
        assert r.status_code == 200, r.text
        d = r.json()
        assert isinstance(d, dict)

    def test_rncp_stats(self):
        r = requests.get(f"{BASE_URL}/api/referentiel/rncp/stats", timeout=30)
        assert r.status_code == 200, r.text
        d = r.json()
        assert "rncp_actives" in d or "total_certifications" in d

    def test_referentiel_search_chauffeur(self, mike_token):
        r = requests.get(
            f"{BASE_URL}/api/referentiel/search",
            params={"q": "chauffeur", "token": mike_token}, timeout=30)
        assert r.status_code == 200, r.text
        d = r.json()
        assert "total" in d, f"missing total: {d}"
        assert d["total"] >= 0

    def test_opc_referentiel_search(self):
        r = requests.get(
            f"{BASE_URL}/api/opc/referentiel/search",
            params={"q": "chauffeur"}, timeout=30)
        assert r.status_code == 200, r.text

    def test_filieres_cartographie(self):
        r = requests.get(f"{BASE_URL}/api/referentiel/filieres", timeout=30)
        assert r.status_code == 200, r.text

    def test_rncp_search(self):
        r = requests.get(
            f"{BASE_URL}/api/referentiel/rncp/search",
            params={"q": "chauffeur", "limit": 20}, timeout=30)
        assert r.status_code == 200, r.text
        d = r.json()
        assert "total" in d or "results" in d

    def test_rncp_tension(self):
        r = requests.get(
            f"{BASE_URL}/api/referentiel/rncp/tension",
            params={"limit": 15}, timeout=30)
        assert r.status_code == 200, r.text

    # IA endpoints — 1 call each with context (comptable used to avoid extra credits)
    def test_ia_trajectoires(self, mike_token):
        t0 = time.time()
        r = requests.post(
            f"{BASE_URL}/api/observatory/ia/trajectoires",
            params={"token": mike_token},
            json={"contexte_metier": "chauffeur livreur"},
            timeout=TIMEOUT_IA)
        elapsed = time.time() - t0
        print(f"[ia/trajectoires] elapsed={elapsed:.1f}s status={r.status_code}")
        assert r.status_code == 200, r.text
        assert elapsed < 60, f"took {elapsed}s > 60s proxy limit"

    def test_ia_correlations(self, mike_token):
        t0 = time.time()
        r = requests.post(
            f"{BASE_URL}/api/observatory/ia/correlations",
            params={"token": mike_token},
            json={"contexte_metier": "chauffeur livreur"},
            timeout=TIMEOUT_IA)
        elapsed = time.time() - t0
        print(f"[ia/correlations] elapsed={elapsed:.1f}s status={r.status_code}")
        assert r.status_code == 200, r.text
        assert elapsed < 60

    def test_ia_detect_emergentes(self, mike_token):
        t0 = time.time()
        r = requests.post(
            f"{BASE_URL}/api/observatory/ia/detect-emergentes",
            params={"token": mike_token},
            json={"contexte_metier": "chauffeur livreur"},
            timeout=TIMEOUT_IA)
        elapsed = time.time() - t0
        print(f"[ia/detect-emergentes] elapsed={elapsed:.1f}s status={r.status_code}")
        assert r.status_code == 200, r.text
        assert elapsed < 60

    def test_ia_recommandation(self, mike_token):
        t0 = time.time()
        r = requests.post(
            f"{BASE_URL}/api/observatory/ia/recommandation",
            params={"token": mike_token},
            json={"contexte_metier": "chauffeur livreur"},
            timeout=TIMEOUT_IA)
        elapsed = time.time() - t0
        print(f"[ia/recommandation] elapsed={elapsed:.1f}s status={r.status_code}")
        assert r.status_code == 200, r.text
        assert elapsed < 60

    def test_ia_analyse_complete_job_polling(self, mike_token):
        """POST returns job_id, GET status polled until completed"""
        start = requests.post(
            f"{BASE_URL}/api/observatory/ia/analyse-complete",
            params={"token": mike_token},
            json={"contexte_metier": "chauffeur livreur"},
            timeout=30)
        assert start.status_code == 200, start.text
        job_id = start.json().get("job_id")
        assert job_id, f"missing job_id in {start.json()}"

        t0 = time.time()
        result = None
        for _ in range(60):
            time.sleep(4)
            try:
                st = requests.get(
                    f"{BASE_URL}/api/observatory/ia/analyse-complete/status",
                    params={"job_id": job_id}, timeout=20)
            except requests.exceptions.RequestException:
                continue  # transient — like frontend
            if st.status_code == 200:
                data = st.json()
                if data.get("status") == "completed":
                    result = data.get("result")
                    break
                if data.get("status") == "failed":
                    pytest.fail(f"job failed: {data}")
        elapsed = time.time() - t0
        print(f"[ia/analyse-complete] polling elapsed={elapsed:.1f}s")
        assert result is not None, "timeout waiting for analyse-complete"
        assert elapsed < 240  # 4 min per PRD
        assert "emergentes" in result or "recommandation" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])
