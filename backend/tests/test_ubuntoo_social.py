"""Backend tests for Ubuntoo Social (SSO from Ré'Actif Pro + all /api/social endpoints + WS)."""
import os
import json
import time
import uuid
import pytest
import requests
import websocket
import threading

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://cv-analyzer-53.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"
SOCIAL = f"{API}/social"

USERS = {
    "mike9": {"pseudo": "mike9", "password": "Solerys777!"},
    "peter7": {"pseudo": "peter7", "password": "Solerys777!"},
}


# -------- Fixtures : login Ré'Actif Pro -> SSO Ubuntoo -> JWT --------
def _reactif_login(pseudo, password):
    r = requests.post(f"{API}/auth/login", json={"pseudo": pseudo, "password": password}, timeout=30)
    assert r.status_code == 200, f"Réactif login failed for {pseudo}: {r.status_code} {r.text[:400]}"
    tok = r.json().get("token")
    assert tok
    return tok


def _sso(reactif_token):
    r = requests.post(f"{SOCIAL}/auth/sso", json={"token": reactif_token}, timeout=30)
    assert r.status_code == 200, f"SSO failed: {r.status_code} {r.text[:400]}"
    body = r.json()
    return body["token"], body["user"]


@pytest.fixture(scope="module")
def mike_jwt():
    reactif = _reactif_login(**USERS["mike9"])
    jwt_tok, user = _sso(reactif)
    return {"jwt": jwt_tok, "user": user, "headers": {"Authorization": f"Bearer {jwt_tok}"}}


@pytest.fixture(scope="module")
def peter_jwt():
    reactif = _reactif_login(**USERS["peter7"])
    jwt_tok, user = _sso(reactif)
    return {"jwt": jwt_tok, "user": user, "headers": {"Authorization": f"Bearer {jwt_tok}"}}


# ============== AUTH / SSO ==============
class TestAuthSSO:
    def test_sso_returns_jwt_and_user(self, mike_jwt):
        u = mike_jwt["user"]
        assert u["id"]
        assert u["full_name"]
        assert isinstance(u["badges"], list)
        assert "welcome" in u["badges"]

    def test_auth_me(self, mike_jwt):
        r = requests.get(f"{SOCIAL}/auth/me", headers=mike_jwt["headers"], timeout=15)
        assert r.status_code == 200
        d = r.json()
        assert d["id"] == mike_jwt["user"]["id"]

    def test_sso_invalid_token_401(self):
        r = requests.post(f"{SOCIAL}/auth/sso", json={"token": "invalid_token_xxx"}, timeout=15)
        assert r.status_code in (401, 403, 404)

    def test_auth_me_without_token(self):
        r = requests.get(f"{SOCIAL}/auth/me", timeout=15)
        assert r.status_code in (401, 403)


# ============== POSTS + REACTIONS + COMMENTS + REPORTS ==============
class TestPostsFlow:
    _post_id = None

    def test_create_post(self, mike_jwt):
        payload = {"content": f"TEST_post_{uuid.uuid4().hex[:8]}", "post_type": "temoignage"}
        r = requests.post(f"{SOCIAL}/posts", json=payload, headers=mike_jwt["headers"], timeout=15)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["content"] == payload["content"]
        assert d["post_type"] == "temoignage"
        assert d["author_id"] == mike_jwt["user"]["id"]
        TestPostsFlow._post_id = d["id"]

    def test_get_posts(self, mike_jwt):
        r = requests.get(f"{SOCIAL}/posts", headers=mike_jwt["headers"], timeout=15)
        assert r.status_code == 200
        posts = r.json()
        assert isinstance(posts, list)
        ids = [p["id"] for p in posts]
        assert TestPostsFlow._post_id in ids

    def test_react_toggle_exclusive(self, mike_jwt):
        pid = TestPostsFlow._post_id
        r = requests.post(f"{SOCIAL}/posts/{pid}/react", json={"reaction_type": "merci"}, headers=mike_jwt["headers"], timeout=15)
        assert r.status_code == 200
        assert r.json()["reaction"] == "merci"
        # Change reaction (exclusivity)
        r2 = requests.post(f"{SOCIAL}/posts/{pid}/react", json={"reaction_type": "bravo"}, headers=mike_jwt["headers"], timeout=15)
        assert r2.status_code == 200
        assert r2.json()["reaction"] == "bravo"
        # Toggle off
        r3 = requests.post(f"{SOCIAL}/posts/{pid}/react", json={"reaction_type": "bravo"}, headers=mike_jwt["headers"], timeout=15)
        assert r3.status_code == 200
        assert r3.json()["reaction"] is None

    def test_react_invalid_type(self, mike_jwt):
        pid = TestPostsFlow._post_id
        r = requests.post(f"{SOCIAL}/posts/{pid}/react", json={"reaction_type": "invalid_xxx"}, headers=mike_jwt["headers"], timeout=15)
        assert r.status_code == 400

    def test_add_and_get_comment(self, mike_jwt):
        pid = TestPostsFlow._post_id
        r = requests.post(f"{SOCIAL}/comments", json={"post_id": pid, "content": "TEST_comment"}, headers=mike_jwt["headers"], timeout=15)
        assert r.status_code == 200
        c = r.json()
        assert c["content"] == "TEST_comment"
        # GET
        r2 = requests.get(f"{SOCIAL}/posts/{pid}/comments", headers=mike_jwt["headers"], timeout=15)
        assert r2.status_code == 200
        arr = r2.json()
        assert any(cc["id"] == c["id"] for cc in arr)

    def test_report_post(self, mike_jwt):
        pid = TestPostsFlow._post_id
        r = requests.post(f"{SOCIAL}/reports", json={"target_type": "post", "target_id": pid, "reason": "TEST_reason"}, headers=mike_jwt["headers"], timeout=15)
        assert r.status_code == 200
        assert "id" in r.json()

    def test_badge_first_post(self, mike_jwt):
        r = requests.get(f"{SOCIAL}/auth/me", headers=mike_jwt["headers"], timeout=15)
        assert "first_post" in r.json().get("badges", [])


# ============== GROUPS + DISCUSSIONS + REPLIES ==============
class TestGroupsDiscussions:
    _group_id = None
    _discussion_id = None

    def test_create_group(self, mike_jwt):
        payload = {"name": f"TEST_group_{uuid.uuid4().hex[:6]}", "description": "TEST_desc", "category": "entraide"}
        r = requests.post(f"{SOCIAL}/groups", json=payload, headers=mike_jwt["headers"], timeout=15)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["name"] == payload["name"]
        assert d["creator_id"] == mike_jwt["user"]["id"]
        assert d["members_count"] == 1
        TestGroupsDiscussions._group_id = d["id"]

    def test_list_groups(self, mike_jwt):
        r = requests.get(f"{SOCIAL}/groups", headers=mike_jwt["headers"], timeout=15)
        assert r.status_code == 200
        assert any(g["id"] == TestGroupsDiscussions._group_id for g in r.json())

    def test_join_group_toggle(self, peter_jwt):
        gid = TestGroupsDiscussions._group_id
        r = requests.post(f"{SOCIAL}/groups/{gid}/join", headers=peter_jwt["headers"], timeout=15)
        assert r.status_code == 200
        assert r.json()["joined"] is True
        # Leave
        r2 = requests.post(f"{SOCIAL}/groups/{gid}/join", headers=peter_jwt["headers"], timeout=15)
        assert r2.status_code == 200
        assert r2.json()["joined"] is False

    def test_create_discussion(self, mike_jwt):
        gid = TestGroupsDiscussions._group_id
        payload = {"title": "TEST_disc", "content": "TEST_content", "group_id": gid}
        r = requests.post(f"{SOCIAL}/discussions", json=payload, headers=mike_jwt["headers"], timeout=15)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["title"] == "TEST_disc"
        TestGroupsDiscussions._discussion_id = d["id"]

    def test_get_group_discussions(self, mike_jwt):
        gid = TestGroupsDiscussions._group_id
        r = requests.get(f"{SOCIAL}/groups/{gid}/discussions", headers=mike_jwt["headers"], timeout=15)
        assert r.status_code == 200
        assert any(d["id"] == TestGroupsDiscussions._discussion_id for d in r.json())

    def test_add_discussion_reply(self, mike_jwt):
        did = TestGroupsDiscussions._discussion_id
        r = requests.post(f"{SOCIAL}/discussions/{did}/replies", json={"content": "TEST_reply"}, headers=mike_jwt["headers"], timeout=15)
        assert r.status_code == 200
        # GET replies
        r2 = requests.get(f"{SOCIAL}/discussions/{did}/replies", headers=mike_jwt["headers"], timeout=15)
        assert r2.status_code == 200
        assert len(r2.json()) >= 1

    def test_get_discussion_detail(self, mike_jwt):
        did = TestGroupsDiscussions._discussion_id
        r = requests.get(f"{SOCIAL}/discussions/{did}", headers=mike_jwt["headers"], timeout=15)
        assert r.status_code == 200
        d = r.json()
        assert d["id"] == did
        assert d["replies_count"] >= 1

    def test_badge_builder_facilitator(self, mike_jwt):
        r = requests.get(f"{SOCIAL}/auth/me", headers=mike_jwt["headers"], timeout=15)
        badges = r.json().get("badges", [])
        assert "builder" in badges
        assert "facilitator" in badges


# ============== MESSAGES ==============
class TestMessages:
    def test_send_and_get_messages(self, mike_jwt, peter_jwt):
        content = f"TEST_msg_{uuid.uuid4().hex[:6]}"
        r = requests.post(
            f"{SOCIAL}/messages",
            json={"receiver_id": peter_jwt["user"]["id"], "content": content},
            headers=mike_jwt["headers"], timeout=15,
        )
        assert r.status_code == 200, r.text
        m = r.json()
        assert m["content"] == content
        assert m["sender_id"] == mike_jwt["user"]["id"]

        # GET conversation from peter side
        r2 = requests.get(f"{SOCIAL}/messages/{mike_jwt['user']['id']}", headers=peter_jwt["headers"], timeout=15)
        assert r2.status_code == 200
        msgs = r2.json()
        assert any(mm["id"] == m["id"] for mm in msgs)

    def test_conversations_list(self, mike_jwt, peter_jwt):
        r = requests.get(f"{SOCIAL}/messages/conversations", headers=mike_jwt["headers"], timeout=15)
        assert r.status_code == 200
        convs = r.json()
        assert any(c["user_id"] == peter_jwt["user"]["id"] for c in convs)


# ============== SEARCH / BADGES / STATS ==============
class TestSearchBadgesStats:
    def test_search(self, mike_jwt):
        r = requests.get(f"{SOCIAL}/search", params={"q": "TEST"}, headers=mike_jwt["headers"], timeout=15)
        assert r.status_code == 200
        d = r.json()
        assert "users" in d and "posts" in d and "groups" in d

    def test_badges_list(self, mike_jwt):
        r = requests.get(f"{SOCIAL}/badges", headers=mike_jwt["headers"], timeout=15)
        assert r.status_code == 200
        arr = r.json()
        assert len(arr) >= 5
        assert all("id" in b and "name" in b for b in arr)

    def test_stats(self, mike_jwt):
        r = requests.get(f"{SOCIAL}/stats", headers=mike_jwt["headers"], timeout=15)
        assert r.status_code == 200
        d = r.json()
        for k in ("users_count", "posts_count", "groups_count", "discussions_count"):
            assert k in d and isinstance(d[k], int)

    def test_profile_update(self, mike_jwt):
        payload = {"bio": "TEST_bio_updated", "location": "Paris", "sector": "Tech",
                   "skills": ["python", "react"]}
        r = requests.put(f"{SOCIAL}/users/profile", json=payload, headers=mike_jwt["headers"], timeout=15)
        assert r.status_code == 200
        u = r.json()
        assert u["bio"] == "TEST_bio_updated"
        assert u["location"] == "Paris"
        assert "python" in u["skills"]


# ============== WEBSOCKET ==============
class TestWebSocket:
    def test_ws_realtime_message(self, mike_jwt, peter_jwt):
        """mike opens WS, peter sends via REST, mike should receive over WS."""
        ws_host = BASE_URL.replace("https://", "wss://").replace("http://", "ws://")
        ws_url = f"{ws_host}/api/social/ws?token={mike_jwt['jwt']}"

        received = []
        connected_event = threading.Event()

        def on_message(_ws, msg):
            try:
                data = json.loads(msg)
                received.append(data)
                if data.get("type") == "presence_snapshot":
                    connected_event.set()
            except Exception:
                pass

        def on_open(_ws):
            connected_event.set()

        def on_error(_ws, err):
            print(f"WS error: {err}")

        ws = websocket.WebSocketApp(ws_url, on_message=on_message, on_open=on_open, on_error=on_error)
        t = threading.Thread(target=ws.run_forever, kwargs={"skip_utf8_validation": True}, daemon=True)
        t.start()
        assert connected_event.wait(timeout=10), "WebSocket did not connect within 10s"
        time.sleep(1.0)

        # Peter sends message to mike via REST
        content = f"TEST_ws_{uuid.uuid4().hex[:6]}"
        r = requests.post(
            f"{SOCIAL}/messages",
            json={"receiver_id": mike_jwt["user"]["id"], "content": content},
            headers=peter_jwt["headers"], timeout=15,
        )
        assert r.status_code == 200

        # Wait up to 5s for the message to arrive over WS
        deadline = time.time() + 5
        found = False
        while time.time() < deadline:
            for m in received:
                if m.get("type") == "message" and m.get("message", {}).get("content") == content:
                    found = True
                    break
            if found:
                break
            time.sleep(0.3)
        ws.close()
        assert found, f"Message not delivered via WS. Received: {received}"

    def test_ws_invalid_token_closes(self):
        ws_host = BASE_URL.replace("https://", "wss://").replace("http://", "ws://")
        ws_url = f"{ws_host}/api/social/ws?token=BADTOKEN"
        closed = threading.Event()
        error_seen = []

        def on_close(_ws, code, msg):
            closed.set()

        def on_error(_ws, err):
            error_seen.append(str(err))
            closed.set()

        ws = websocket.WebSocketApp(ws_url, on_close=on_close, on_error=on_error)
        threading.Thread(target=ws.run_forever, daemon=True).start()
        assert closed.wait(timeout=10), "WS with bad token did not close"
        ws.close()
