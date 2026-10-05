"""Flux positif complet UBUNTOO v2 — Candidature mentor → admin approve → mentor validé.
Et test Mentor confirmé auto via DB (seed d'une 2e connexion mentorat terminée+feedback)."""
import os
import time
import uuid
import pytest
import requests
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv("/app/backend/.env")

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://cv-analyzer-53.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"
U2 = f"{API}/ubuntoo2"
MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]


def _login(pseudo, pwd):
    r = requests.post(f"{API}/auth/login", json={"pseudo": pseudo, "password": pwd}, timeout=30)
    assert r.status_code == 200, r.text
    return r.json()["token"]


@pytest.fixture(scope="module")
def tok():
    return {
        "marc19": _login("marc19", "Solerys777!"),
        "peter7": _login("peter7", "Solerys777!"),
        "mike7": _login("mike7", "Solerys777!"),
        "admin": _login("admin@reactifpro.fr", "Choukette@777"),
    }


@pytest.fixture(scope="module")
def ids(tok):
    out = {}
    for u in ("marc19", "peter7", "mike7"):
        r = requests.get(f"{U2}/me", params={"token": tok[u]}, timeout=20)
        out[u] = r.json()["token_id"]
    return out


def _get_prog(token):
    return requests.get(f"{U2}/progression", params={"token": token}, timeout=20).json()


class TestMarc19Flow:
    """Promouvoir marc19 → Contributeur → candidature → approve."""

    def test_01_initial_state(self, tok):
        prog = _get_prog(tok["marc19"])
        print(f"marc19 initial: current_label={prog['current_label']}, mentor_status={prog['mentor_status']}, can_apply={prog['can_apply_mentor']}")
        # Peut être déjà mentor si un run précédent l'a validé → skip
        if prog["mentor_status"] in ("mentor", "confirme", "candidat"):
            pytest.skip(f"marc19 déjà en flux mentor ({prog['mentor_status']}) — flux déjà testé")

    def test_02_ensure_profile_complet(self, tok):
        requests.put(f"{U2}/me", params={"token": tok["marc19"]},
                     json={"headline": "Test marc19 contributeur",
                           "competences": ["Test", "Mentorat", "Automatisation"],
                           "help_offers": ["Mentorat"]}, timeout=20)

    def test_03_join_and_post_5_ressources(self, tok):
        # Lister communautés et rejoindre la 1ère
        comms = requests.get(f"{U2}/communities", params={"token": tok["marc19"]}, timeout=20).json()
        comm_id = comms[0]["id"]
        requests.post(f"{U2}/communities/{comm_id}/join",
                      params={"token": tok["marc19"]}, timeout=20)
        # Poster 5 ressources
        for i in range(5):
            r = requests.post(f"{U2}/communities/{comm_id}/posts",
                              params={"token": tok["marc19"]},
                              json={"type": "ressource", "title": f"TEST_i59_ressource_{i}",
                                    "content": f"Partage ressource test {i}"}, timeout=20)
            assert r.status_code == 200, r.text

    def test_04_marc19_is_contributeur(self, tok):
        prog = _get_prog(tok["marc19"])
        print(f"marc19 after posts: {prog['current_label']}, can_apply={prog['can_apply_mentor']}, contribs={prog['contributions']}")
        assert prog["levels"]["contributeur"] is True
        assert prog["can_apply_mentor"] is True

    def test_05_candidature_requires_charte(self, tok):
        r = requests.post(f"{U2}/progression/mentor-candidature",
                          params={"token": tok["marc19"]},
                          json={"accept_charte": False}, timeout=20)
        assert r.status_code == 400

    def test_06_candidature_with_charte(self, tok):
        r = requests.post(f"{U2}/progression/mentor-candidature",
                          params={"token": tok["marc19"]},
                          json={"accept_charte": True}, timeout=20)
        assert r.status_code == 200, r.text
        prog = _get_prog(tok["marc19"])
        assert prog["mentor_status"] == "candidat"

    def test_07_admin_sees_candidature(self, tok, ids):
        r = requests.get(f"{U2}/admin/candidatures", params={"token": tok["admin"]}, timeout=20)
        assert r.status_code == 200
        cands = r.json()
        mine = [c for c in cands if c["token_id"] == ids["marc19"] and c["type"] == "mentor"]
        assert mine, f"Aucune candidature pending pour marc19: {cands}"
        TestMarc19Flow.cand_id = mine[0]["id"]

    def test_08_admin_approve(self, tok):
        r = requests.post(f"{U2}/admin/candidatures/{TestMarc19Flow.cand_id}/decide",
                          params={"token": tok["admin"]},
                          json={"action": "approve"}, timeout=20)
        assert r.status_code == 200
        time.sleep(0.5)
        prog = _get_prog(tok["marc19"])
        assert prog["mentor_status"] == "mentor", f"Expected mentor got {prog['mentor_status']}"

    def test_09_notification_progression(self, tok):
        r = requests.get(f"{U2}/notifications", params={"token": tok["marc19"]}, timeout=20)
        types = [n["type"] for n in r.json()]
        assert "progression" in types

    def test_10_marc19_can_be_mentor_target(self, tok, ids):
        # Nouvelle demande mentorat mike7 → marc19 (maintenant validé)
        r = requests.post(f"{U2}/connections",
                          params={"token": tok["mike7"]},
                          json={"to_id": ids["marc19"], "kind": "mentorat",
                                "message": "demande mentorat validé"}, timeout=20)
        # 200 ok ou 400 si déjà existante
        assert r.status_code in (200, 400), r.text
        if r.status_code == 400:
            print(f"Note: {r.text}")


class TestMentorConfirmeAuto:
    """Via DB directe : ajouter 2e connexion mentorat terminée+feedback 5★ pour peter7 → confirme."""

    def test_seed_second_mentorat_and_check_confirme(self, tok, ids):
        async def run():
            client = AsyncIOMotorClient(MONGO_URL)
            db = client[DB_NAME]
            # Compter mentorats peter7 terminés
            existing = await db.ubuntoo2_connections.count_documents({
                "kind": "mentorat", "mentor_id": ids["peter7"], "mentorat_status": "termine"
            })
            with_fb = await db.ubuntoo2_connections.count_documents({
                "kind": "mentorat", "mentor_id": ids["peter7"], "feedback": {"$exists": True}
            })
            print(f"peter7 existing mentorats terminés: {existing}, avec feedback: {with_fb}")

            # Besoin de 2 feedback avec rating ≥4 pour passer à confirme
            if with_fb < 2:
                # Insérer directement une 2e connexion mentorat terminée+feedback
                seed_id = f"TEST_i59_{uuid.uuid4()}"
                await db.ubuntoo2_connections.insert_one({
                    "id": seed_id,
                    "kind": "mentorat",
                    "mentor_id": ids["peter7"],
                    "mentee_id": ids["marc19"],
                    "from_id": ids["marc19"],
                    "to_id": ids["peter7"],
                    "status": "accepted",
                    "mentorat_status": "termine",
                    "bilan": "TEST i59 bilan auto",
                    "terminated_at": "2026-01-15T00:00:00+00:00",
                    "terminated_by": ids["peter7"],
                    "feedback": {"rating": 5, "comment": "TEST i59 feedback auto", "created_at": "2026-01-15T00:01:00+00:00"},
                    "created_at": "2026-01-14T00:00:00+00:00",
                })
                print(f"Inserted test connection {seed_id}")
            client.close()

        asyncio.run(run())

        # Appeler progression → doit basculer confirme
        prog = _get_prog(tok["peter7"])
        print(f"peter7 progression apres seed: mentor_status={prog['mentor_status']}, mentorats_termines={prog['contributions']['mentorats_termines']}, note={prog['contributions']['note_moyenne_mentorat']}")
        assert prog["mentor_status"] == "confirme", f"Expected confirme, got {prog['mentor_status']}"
        assert prog["levels"]["mentor_confirme"] is True
        assert prog["can_apply_ambassadeur"] is True

    def test_ambassadeur_candidature(self, tok):
        r = requests.post(f"{U2}/progression/ambassadeur-candidature",
                          params={"token": tok["peter7"]}, json={}, timeout=20)
        # 200 ok ou refus si déjà candidat/ambassadeur
        if r.status_code == 400:
            prog = _get_prog(tok["peter7"])
            assert prog["ambassadeur_status"] in ("candidat", "ambassadeur")
            return
        assert r.status_code == 200, r.text
        prog = _get_prog(tok["peter7"])
        assert prog["ambassadeur_status"] in ("candidat", "ambassadeur")

    def test_admin_approve_ambassadeur(self, tok, ids):
        r = requests.get(f"{U2}/admin/candidatures", params={"token": tok["admin"]}, timeout=20)
        cands = [c for c in r.json() if c["token_id"] == ids["peter7"] and c["type"] == "ambassadeur"]
        if not cands:
            pytest.skip("Pas de candidature ambassadeur pending (déjà traitée)")
        r2 = requests.post(f"{U2}/admin/candidatures/{cands[0]['id']}/decide",
                           params={"token": tok["admin"]},
                           json={"action": "approve"}, timeout=20)
        assert r2.status_code == 200
        prog = _get_prog(tok["peter7"])
        assert prog["ambassadeur_status"] == "ambassadeur"
        assert prog["levels"]["ambassadeur"] is True


def teardown_module(module):
    """Nettoyage : supprimer connexions TEST_i59_* seedées."""
    async def cleanup():
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        res = await db.ubuntoo2_connections.delete_many({"id": {"$regex": "^TEST_i59_"}})
        # Supprimer aussi posts TEST_i59_
        res2 = await db.ubuntoo2_posts.delete_many({"title": {"$regex": "^TEST_i59_"}})
        print(f"Cleanup: {res.deleted_count} connections, {res2.deleted_count} posts")
        client.close()
    asyncio.run(cleanup())
