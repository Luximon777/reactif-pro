"""Tests UBUNTOO v2 — Mise en relation par consentement, messagerie, communautés, posts, confidentialité."""
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


def _login(pseudo, pwd):
    r = requests.post(f"{API}/auth/login", json={"pseudo": pseudo, "password": pwd}, timeout=30)
    assert r.status_code == 200, f"login {pseudo}: {r.status_code} {r.text}"
    return r.json()["token"]


@pytest.fixture(scope="module")
def tokens():
    return {u: _login(u, p) for u, p in ACCOUNTS.items()}


@pytest.fixture(scope="module")
def me_ids(tokens):
    ids = {}
    for u, t in tokens.items():
        r = requests.get(f"{U2}/me", params={"token": t}, timeout=20)
        assert r.status_code == 200, r.text
        ids[u] = r.json()["token_id"]
    return ids


# --- PROFIL ---
class TestProfile:
    def test_me_auto_creates(self, tokens):
        r = requests.get(f"{U2}/me", params={"token": tokens["peter7"]}, timeout=20)
        assert r.status_code == 200
        d = r.json()
        assert "display_name" in d and d["display_name"]
        assert "privacy" in d
        assert "competences" in d

    def test_update_profile_and_privacy(self, tokens):
        body = {"headline": "Testeur UBUNTOO", "privacy": {"competences": "public", "projet": "reseau"}}
        r = requests.put(f"{U2}/me", params={"token": tokens["peter7"]}, json=body, timeout=20)
        assert r.status_code == 200
        d = r.json()
        assert d["headline"] == "Testeur UBUNTOO"
        assert d["privacy"]["competences"] == "public"

    def test_resync(self, tokens):
        r = requests.post(f"{U2}/me/sync", params={"token": tokens["mike7"]}, timeout=20)
        assert r.status_code == 200
        assert "display_name" in r.json()


# --- Nettoyage demandes pending existantes entre peter7-mike7 ---
@pytest.fixture(scope="module", autouse=True)
def cleanup_pending(tokens, me_ids):
    # décline toute demande pending reçue par peter7 et mike7 l'un de l'autre
    for user in ("peter7", "mike7"):
        r = requests.get(f"{U2}/connections", params={"token": tokens[user], "box": "received"}, timeout=20)
        if r.status_code == 200:
            for c in r.json():
                if c["from_id"] in (me_ids["peter7"], me_ids["mike7"]):
                    requests.post(f"{U2}/connections/{c['id']}/respond",
                                  params={"token": tokens[user]}, json={"action": "decline"}, timeout=20)
    yield


# --- MISE EN RELATION ---
class TestConnections:
    conn_id = None

    def test_search_members(self, tokens):
        r = requests.get(f"{U2}/members", params={"token": tokens["peter7"], "q": "mike"}, timeout=30)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_send_request(self, tokens, me_ids):
        # S'assurer qu'ils ne sont pas déjà contacts/pending
        r = requests.post(f"{U2}/connections",
                          params={"token": tokens["peter7"]},
                          json={"to_id": me_ids["mike7"], "message": "Bonjour, échangeons !"}, timeout=20)
        if r.status_code == 400 and "déjà" in r.text:
            pytest.skip("Déjà en relation ou pending — nettoyage insuffisant")
        assert r.status_code == 200, r.text
        TestConnections.conn_id = r.json()["id"]

    def test_duplicate_request(self, tokens, me_ids):
        r = requests.post(f"{U2}/connections",
                          params={"token": tokens["peter7"]},
                          json={"to_id": me_ids["mike7"], "message": "duplicate"}, timeout=20)
        assert r.status_code == 400

    def test_mike_sees_request(self, tokens, me_ids):
        r = requests.get(f"{U2}/connections", params={"token": tokens["mike7"], "box": "received"}, timeout=20)
        assert r.status_code == 200
        reqs = r.json()
        found = [c for c in reqs if c["from_id"] == me_ids["peter7"]]
        assert found, "mike7 doit voir la demande de peter7"
        assert found[0]["message"] == "Bonjour, échangeons !"
        assert found[0]["member"]["display_name"]

    def test_notification_created(self, tokens):
        r = requests.get(f"{U2}/notifications", params={"token": tokens["mike7"]}, timeout=20)
        assert r.status_code == 200
        types = [n["type"] for n in r.json()]
        assert "connection_request" in types

    def test_accept(self, tokens):
        assert TestConnections.conn_id
        r = requests.post(f"{U2}/connections/{TestConnections.conn_id}/respond",
                          params={"token": tokens["mike7"]},
                          json={"action": "accept"}, timeout=20)
        assert r.status_code == 200
        assert r.json()["status"] == "accepted"

    def test_contacts_appear(self, tokens, me_ids):
        for u, other in [("peter7", "mike7"), ("mike7", "peter7")]:
            r = requests.get(f"{U2}/contacts", params={"token": tokens[u]}, timeout=20)
            assert r.status_code == 200
            ids = [c["token_id"] for c in r.json()]
            assert me_ids[other] in ids, f"{u} doit avoir {other} en contact"

    def test_accept_notification(self, tokens):
        r = requests.get(f"{U2}/notifications", params={"token": tokens["peter7"]}, timeout=20)
        assert r.status_code == 200
        assert "connection_accepted" in [n["type"] for n in r.json()]


# --- MESSAGERIE ---
class TestMessaging:
    conv_id = None

    def test_open_conv_rejected_non_contact(self, tokens, me_ids):
        r = requests.post(f"{U2}/conversations",
                          params={"token": tokens["peter7"]},
                          json={"contact_id": me_ids["marc19"]}, timeout=20)
        assert r.status_code == 403

    def test_open_conv_contact(self, tokens, me_ids):
        r = requests.post(f"{U2}/conversations",
                          params={"token": tokens["peter7"]},
                          json={"contact_id": me_ids["mike7"]}, timeout=20)
        assert r.status_code == 200
        TestMessaging.conv_id = r.json()["id"]

    def test_send_message(self, tokens):
        assert TestMessaging.conv_id
        r = requests.post(f"{U2}/conversations/{TestMessaging.conv_id}/messages",
                          params={"token": tokens["peter7"]},
                          json={"text": "Salut Mike, test automatisé"}, timeout=20)
        assert r.status_code == 200

    def test_unread_in_conversations(self, tokens):
        r = requests.get(f"{U2}/conversations", params={"token": tokens["mike7"]}, timeout=20)
        assert r.status_code == 200
        conv = next((c for c in r.json() if c["id"] == TestMessaging.conv_id), None)
        assert conv and conv["unread"] >= 1

    def test_dashboard_unread(self, tokens):
        r = requests.get(f"{U2}/dashboard", params={"token": tokens["mike7"]}, timeout=20)
        assert r.status_code == 200
        assert r.json()["unread_messages"] >= 1

    def test_get_messages_marks_read(self, tokens):
        r = requests.get(f"{U2}/conversations/{TestMessaging.conv_id}/messages",
                         params={"token": tokens["mike7"]}, timeout=20)
        assert r.status_code == 200
        assert len(r.json()) >= 1
        # 2e lecture: unread doit tomber à 0
        r2 = requests.get(f"{U2}/conversations", params={"token": tokens["mike7"]}, timeout=20)
        conv = next((c for c in r2.json() if c["id"] == TestMessaging.conv_id), None)
        assert conv["unread"] == 0

    def test_new_message_notif(self, tokens):
        r = requests.get(f"{U2}/notifications", params={"token": tokens["mike7"]}, timeout=20)
        assert "new_message" in [n["type"] for n in r.json()]


# --- COMMUNAUTES ---
class TestCommunities:
    comm_id = None
    created_id = None

    def test_list_seeded(self, tokens):
        r = requests.get(f"{U2}/communities", params={"token": tokens["peter7"]}, timeout=30)
        assert r.status_code == 200
        comms = r.json()
        assert len(comms) >= 22
        cats = set(c["category"] for c in comms)
        assert {"metiers", "situations", "territoires", "thematiques"}.issubset(cats)
        TestCommunities.comm_id = comms[0]["id"]

    def test_filter_category(self, tokens):
        r = requests.get(f"{U2}/communities", params={"token": tokens["peter7"], "category": "metiers"}, timeout=20)
        assert r.status_code == 200
        assert all(c["category"] == "metiers" for c in r.json())

    def test_join_leave(self, tokens):
        r = requests.post(f"{U2}/communities/{TestCommunities.comm_id}/join",
                          params={"token": tokens["peter7"]}, timeout=20)
        assert r.status_code == 200
        r = requests.post(f"{U2}/communities/{TestCommunities.comm_id}/leave",
                          params={"token": tokens["peter7"]}, timeout=20)
        assert r.status_code == 200
        # Rejoindre pour tests de posts
        requests.post(f"{U2}/communities/{TestCommunities.comm_id}/join",
                      params={"token": tokens["peter7"]}, timeout=20)

    def test_create_community(self, tokens):
        name = f"TEST_Comm_{int(time.time())}"
        r = requests.post(f"{U2}/communities", params={"token": tokens["peter7"]},
                          json={"name": name, "category": "thematiques", "description": "test"}, timeout=20)
        assert r.status_code == 200
        TestCommunities.created_id = r.json()["id"]
        # Doublon
        r2 = requests.post(f"{U2}/communities", params={"token": tokens["peter7"]},
                           json={"name": name}, timeout=20)
        assert r2.status_code == 400

    def test_post_requires_membership(self, tokens):
        # mike7 non-membre de la communauté créée
        r = requests.post(f"{U2}/communities/{TestCommunities.created_id}/posts",
                          params={"token": tokens["mike7"]},
                          json={"content": "test non membre"}, timeout=20)
        assert r.status_code == 403


# --- POSTS ---
class TestPosts:
    post_id = None

    def test_create_post_valid_type(self, tokens):
        r = requests.post(f"{U2}/communities/{TestCommunities.comm_id}/posts",
                          params={"token": tokens["peter7"]},
                          json={"type": "question", "title": "Test Q", "content": "Ceci est un test"}, timeout=20)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["type"] == "question"
        TestPosts.post_id = d["id"]

    def test_invalid_type_fallback(self, tokens):
        r = requests.post(f"{U2}/communities/{TestCommunities.comm_id}/posts",
                          params={"token": tokens["peter7"]},
                          json={"type": "invalid_type", "content": "fallback test"}, timeout=20)
        assert r.status_code == 200
        assert r.json()["type"] == "information"

    def test_toggle_utile(self, tokens):
        r = requests.post(f"{U2}/posts/{TestPosts.post_id}/utile",
                          params={"token": tokens["mike7"]}, timeout=20)
        assert r.status_code == 200
        d = r.json()
        assert d["utile"] is True
        assert d["utile_count"] >= 1
        # Toggle off
        r2 = requests.post(f"{U2}/posts/{TestPosts.post_id}/utile",
                           params={"token": tokens["mike7"]}, timeout=20)
        assert r2.json()["utile"] is False

    def test_reply_and_notify(self, tokens):
        # Rejoindre d'abord
        requests.post(f"{U2}/communities/{TestCommunities.comm_id}/join",
                      params={"token": tokens["mike7"]}, timeout=20)
        r = requests.post(f"{U2}/posts/{TestPosts.post_id}/replies",
                         params={"token": tokens["mike7"]},
                         json={"content": "ma réponse test"}, timeout=20)
        assert r.status_code == 200
        # replies_count
        r2 = requests.get(f"{U2}/communities/{TestCommunities.comm_id}/posts",
                          params={"token": tokens["peter7"]}, timeout=20)
        p = next((x for x in r2.json() if x["id"] == TestPosts.post_id), None)
        assert p and p["replies_count"] >= 1
        # notif post_reply pour peter7
        r3 = requests.get(f"{U2}/notifications", params={"token": tokens["peter7"]}, timeout=20)
        assert "post_reply" in [n["type"] for n in r3.json()]


# --- CONFIDENTIALITE ---
class TestPrivacy:
    def test_prive_hides_from_contact(self, tokens, me_ids):
        # mike7 met competences=prive
        requests.put(f"{U2}/me", params={"token": tokens["mike7"]},
                     json={"privacy": {"competences": "prive"}}, timeout=20)
        r = requests.get(f"{U2}/members/{me_ids['mike7']}", params={"token": tokens["peter7"]}, timeout=20)
        assert r.status_code == 200
        assert "competences" not in r.json()

    def test_reseau_visible_contact_not_other(self, tokens, me_ids):
        requests.put(f"{U2}/me", params={"token": tokens["mike7"]},
                     json={"privacy": {"competences": "reseau"}}, timeout=20)
        # peter7 contact
        r1 = requests.get(f"{U2}/members/{me_ids['mike7']}", params={"token": tokens["peter7"]}, timeout=20)
        assert "competences" in r1.json()
        # marc19 non-contact
        r2 = requests.get(f"{U2}/members/{me_ids['mike7']}", params={"token": tokens["marc19"]}, timeout=20)
        assert "competences" not in r2.json()

    def test_public_visible_all(self, tokens, me_ids):
        requests.put(f"{U2}/me", params={"token": tokens["mike7"]},
                     json={"privacy": {"competences": "public"}}, timeout=20)
        r = requests.get(f"{U2}/members/{me_ids['mike7']}", params={"token": tokens["marc19"]}, timeout=20)
        assert "competences" in r.json()


# --- SIGNALEMENT ---
class TestReports:
    def test_valid_reason(self, tokens):
        r = requests.post(f"{U2}/reports", params={"token": tokens["peter7"]},
                          json={"reason": "Spam", "target_type": "post", "target_id": "x"}, timeout=20)
        assert r.status_code == 200

    def test_invalid_reason(self, tokens):
        r = requests.post(f"{U2}/reports", params={"token": tokens["peter7"]},
                          json={"reason": "WrongReason"}, timeout=20)
        assert r.status_code == 400


# --- NOTIFICATIONS ---
class TestNotifications:
    def test_mark_read(self, tokens):
        r = requests.post(f"{U2}/notifications/mark-read", params={"token": tokens["peter7"]}, timeout=20)
        assert r.status_code == 200
        r2 = requests.get(f"{U2}/notifications", params={"token": tokens["peter7"]}, timeout=20)
        assert all(n["read"] for n in r2.json())


# --- Decline flow (nouveau couple peter7->marc19) ---
class TestDecline:
    def test_decline_flow(self, tokens, me_ids):
        # cleanup existing
        for u in ("marc19",):
            r = requests.get(f"{U2}/connections", params={"token": tokens[u], "box": "received"}, timeout=20)
            for c in r.json():
                if c["from_id"] == me_ids["peter7"]:
                    requests.post(f"{U2}/connections/{c['id']}/respond",
                                  params={"token": tokens[u]}, json={"action": "decline"}, timeout=20)
        r = requests.post(f"{U2}/connections", params={"token": tokens["peter7"]},
                          json={"to_id": me_ids["marc19"], "message": "decline test"}, timeout=20)
        if r.status_code == 400:
            pytest.skip("Déjà en relation peter7-marc19")
        cid = r.json()["id"]
        r2 = requests.post(f"{U2}/connections/{cid}/respond", params={"token": tokens["marc19"]},
                           json={"action": "decline"}, timeout=20)
        assert r2.status_code == 200
        assert r2.json()["status"] == "declined"
        # Non-contacts
        r3 = requests.get(f"{U2}/contacts", params={"token": tokens["peter7"]}, timeout=20)
        assert me_ids["marc19"] not in [c["token_id"] for c in r3.json()]
