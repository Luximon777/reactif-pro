// UbuntooApp.jsx
// Application de messagerie Ubuntoo — PWA complète
// À placer dans : frontend/src/pages/UbuntooApp.jsx
// Route dans App.js : <Route path="/ubuntoo" element={<UbuntooApp />} />

import { useState, useEffect, useRef, useCallback } from "react";
import axios from "axios";

const API = process.env.REACT_APP_API_URL || "https://reactif.pro/api";

// ─── Palette ───────────────────────────────────────────────────────────────
const C = {
  navy: "#26215C",
  purple: "#534AB7",
  blue: "#378ADD",
  green: "#1D9E75",
  chat: "#E8EAF0",
  border: "#E2E8F0",
};

// ─── Styles globaux ────────────────────────────────────────────────────────
const G = {
  app: { display: "flex", flexDirection: "column", height: "100dvh", maxWidth: 480, margin: "0 auto", background: "#fff", fontFamily: "IBM Plex Sans, system-ui, sans-serif", overflow: "hidden", position: "relative" },
  hdr: { background: C.navy, padding: "12px 16px", display: "flex", alignItems: "center", gap: 10, flexShrink: 0 },
  hdrTitle: { color: "#fff", fontSize: 17, fontWeight: 500, flex: 1 },
  hdrSub: { color: "#B5D4F4", fontSize: 11, marginTop: 1 },
  btn: { border: "none", cursor: "pointer", borderRadius: 8 },
};

// ─── Utilitaires ───────────────────────────────────────────────────────────
const storage = {
  get: (k) => { try { return JSON.parse(localStorage.getItem(k)); } catch { return null; } },
  set: (k, v) => localStorage.setItem(k, JSON.stringify(v)),
  del: (k) => localStorage.removeItem(k),
};

const timeStr = (iso) => {
  if (!iso) return "";
  const d = new Date(iso);
  const now = new Date();
  if (d.toDateString() === now.toDateString()) return d.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" });
  return d.toLocaleDateString("fr-FR", { day: "2-digit", month: "2-digit" });
};

const Avatar = ({ nom = "?", size = 40, bg = C.navy, color = "#fff", online = false }) => (
  <div style={{ position: "relative", flexShrink: 0 }}>
    <div style={{ width: size, height: size, borderRadius: "50%", background: bg, display: "flex", alignItems: "center", justifyContent: "center", color, fontSize: size * 0.35, fontWeight: 600 }}>
      {nom[0]?.toUpperCase()}
    </div>
    {online && <div style={{ position: "absolute", bottom: 0, right: 0, width: 10, height: 10, borderRadius: "50%", background: C.green, border: "2px solid #fff" }} />}
  </div>
);

// ─── Écran de connexion ────────────────────────────────────────────────────
function LoginScreen({ onLogin }) {
  const [mode, setMode] = useState("login"); // login | register
  const [form, setForm] = useState({ nom: "", email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handle = async () => {
    setError(""); setLoading(true);
    try {
      const endpoint = mode === "login" ? "/ubuntoo/auth/login" : "/ubuntoo/auth/register";
      const { data } = await axios.post(`${API}${endpoint}`, form);
      storage.set("ubuntoo_user", data);
      onLogin(data);
    } catch (e) {
      setError(e.response?.data?.detail || "Erreur de connexion");
    } finally { setLoading(false); }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100dvh", maxWidth: 480, margin: "0 auto", fontFamily: "IBM Plex Sans, system-ui, sans-serif" }}>
      <div style={{ background: C.navy, padding: "48px 24px 32px", textAlign: "center" }}>
        <div style={{ fontSize: 40, marginBottom: 8 }}>💬</div>
        <div style={{ color: "#fff", fontSize: 24, fontWeight: 600 }}>UBUNTOO</div>
        <div style={{ color: "#B5D4F4", fontSize: 13, marginTop: 4 }}>Espace de dialogue RE'ACTIF PRO</div>
      </div>

      <div style={{ flex: 1, padding: 24, overflowY: "auto" }}>
        <div style={{ display: "flex", background: "#F1F5F9", borderRadius: 10, padding: 4, marginBottom: 24 }}>
          {["login", "register"].map((m) => (
            <button key={m} onClick={() => { setMode(m); setError(""); }} style={{ flex: 1, padding: "8px 0", borderRadius: 8, border: "none", cursor: "pointer", background: mode === m ? "#fff" : "transparent", fontWeight: mode === m ? 500 : 400, color: mode === m ? C.navy : "#64748B", fontSize: 14, boxShadow: mode === m ? "0 1px 3px rgba(0,0,0,.1)" : "none" }}>
              {m === "login" ? "Connexion" : "Inscription"}
            </button>
          ))}
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {mode === "register" && (
            <input placeholder="Votre prénom et nom" value={form.nom} onChange={(e) => setForm({ ...form, nom: e.target.value })}
              style={{ padding: "12px 14px", borderRadius: 10, border: `1.5px solid ${C.border}`, fontSize: 15, outline: "none" }} />
          )}
          <input type="email" placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })}
            style={{ padding: "12px 14px", borderRadius: 10, border: `1.5px solid ${C.border}`, fontSize: 15, outline: "none" }} />
          <input type="password" placeholder="Mot de passe" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })}
            onKeyDown={(e) => e.key === "Enter" && handle()}
            style={{ padding: "12px 14px", borderRadius: 10, border: `1.5px solid ${C.border}`, fontSize: 15, outline: "none" }} />

          {error && <div style={{ color: "#D85A30", fontSize: 13, textAlign: "center" }}>{error}</div>}

          <button onClick={handle} disabled={loading}
            style={{ padding: "14px 0", background: C.navy, color: "#fff", borderRadius: 10, border: "none", fontSize: 15, fontWeight: 500, cursor: "pointer", marginTop: 8, opacity: loading ? 0.7 : 1 }}>
            {loading ? "..." : mode === "login" ? "Se connecter" : "Créer mon compte"}
          </button>
        </div>

        <div style={{ textAlign: "center", fontSize: 12, color: "#94A3B8", marginTop: 24, lineHeight: 1.6 }}>
          Prototype Ubuntoo · RE'ACTIF PRO · ALT&ACT<br />Loi 1908 Alsace-Moselle
        </div>
      </div>
    </div>
  );
}

// ─── Liste des conversations ───────────────────────────────────────────────
function ConvList({ user, conversations, onOpen, onNewGroup, onNewDirect }) {
  const [tab, setTab] = useState("groupes"); // groupes | messages

  const groupes = conversations.filter((c) => c.type === "group");
  const directs = conversations.filter((c) => c.type === "direct");

  const ConvRow = ({ conv }) => {
    const name = conv.type === "group" ? conv.nom : conv.other_user?.nom || "...";
    const preview = conv.last_message || "Démarrer la discussion";
    const icon = conv.icon || null;
    const bg = conv.color || "#E6F1FB";
    return (
      <div onClick={() => onOpen(conv)} style={{ display: "flex", alignItems: "center", gap: 12, padding: "12px 16px", cursor: "pointer", borderBottom: `1px solid ${C.border}` }}
        onMouseEnter={(e) => e.currentTarget.style.background = "#F8F9FA"}
        onMouseLeave={(e) => e.currentTarget.style.background = "#fff"}>
        {icon
          ? <div style={{ width: 48, height: 48, borderRadius: "50%", background: bg, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 22, flexShrink: 0 }}>{icon}</div>
          : <Avatar nom={name} size={48} bg={C.purple} online={conv.other_user?.online} />
        }
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
            <span style={{ fontSize: 15, fontWeight: 500, color: "#0F172A" }}>{name}</span>
            <span style={{ fontSize: 11, color: "#94A3B8", flexShrink: 0 }}>{timeStr(conv.last_message_at)}</span>
          </div>
          <div style={{ fontSize: 13, color: "#64748B", marginTop: 2, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{preview}</div>
        </div>
      </div>
    );
  };

  return (
    <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
      <div style={G.hdr}>
        <div>
          <div style={G.hdrTitle}>UBUNTOO</div>
          <div style={G.hdrSub}>Bonjour {user.nom.split(" ")[0]} 👋</div>
        </div>
        <button onClick={tab === "groupes" ? onNewGroup : onNewDirect}
          style={{ ...G.btn, background: "rgba(255,255,255,.15)", color: "#fff", padding: "6px 12px", fontSize: 13 }}>
          {tab === "groupes" ? "+ Groupe" : "+ Message"}
        </button>
      </div>

      {/* Tabs */}
      <div style={{ display: "flex", background: C.navy, borderTop: "1px solid rgba(255,255,255,.1)" }}>
        {[["groupes", "👥 Groupes"], ["messages", "💬 Messages"]].map(([key, label]) => (
          <button key={key} onClick={() => setTab(key)}
            style={{ flex: 1, padding: "10px 0", background: "none", border: "none", cursor: "pointer", color: tab === key ? "#fff" : "#B5D4F4", fontSize: 13, fontWeight: tab === key ? 500 : 400, borderBottom: tab === key ? `2px solid ${C.blue}` : "2px solid transparent" }}>
            {label}
          </button>
        ))}
      </div>

      <div style={{ flex: 1, overflowY: "auto" }}>
        {tab === "groupes" && (
          groupes.length === 0
            ? <div style={{ textAlign: "center", padding: 32, color: "#94A3B8" }}>Aucun groupe pour l'instant</div>
            : groupes.map((c) => <ConvRow key={c.id} conv={c} />)
        )}
        {tab === "messages" && (
          directs.length === 0
            ? <div style={{ textAlign: "center", padding: 32, color: "#94A3B8" }}>
                Aucun message direct<br />
                <span style={{ fontSize: 12 }}>Appuyez sur "+ Message" pour en commencer un</span>
              </div>
            : directs.map((c) => <ConvRow key={c.id} conv={c} />)
        )}
      </div>
    </div>
  );
}

// ─── Écran de chat ─────────────────────────────────────────────────────────
function ChatScreen({ user, conv, onBack, onRefresh }) {
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");
  const [sending, setSending] = useState(false);
  const bottomRef = useRef(null);
  const lastMsgAt = useRef(null);

  const name = conv.type === "group" ? conv.nom : conv.other_user?.nom || "Discussion";

  const loadMessages = useCallback(async () => {
    try {
      const { data } = await axios.get(`${API}/ubuntoo/messages/${conv.id}`);
      setMessages(data);
      if (data.length > 0) lastMsgAt.current = data[data.length - 1].created_at;
    } catch {}
  }, [conv.id]);

  // Polling toutes les 8 secondes
  useEffect(() => {
    loadMessages();
    const interval = setInterval(async () => {
      if (!lastMsgAt.current) return;
      try {
        const { data } = await axios.get(`${API}/ubuntoo/messages/${conv.id}/new?since=${encodeURIComponent(lastMsgAt.current)}`);
        if (data.length > 0) {
          setMessages((prev) => [...prev, ...data]);
          lastMsgAt.current = data[data.length - 1].created_at;
        }
      } catch {}
    }, 8000);
    return () => clearInterval(interval);
  }, [conv.id, loadMessages]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length]);

  const send = async () => {
    const t = text.trim();
    if (!t || sending) return;
    setText(""); setSending(true);
    const optimistic = { id: `tmp_${Date.now()}`, sender_id: user.id, sender_nom: user.nom, text: t, created_at: new Date().toISOString(), tmp: true };
    setMessages((prev) => [...prev, optimistic]);
    try {
      const { data } = await axios.post(`${API}/ubuntoo/messages`, { conversation_id: conv.id, sender_id: user.id, text: t });
      setMessages((prev) => prev.map((m) => m.id === optimistic.id ? data : m));
      lastMsgAt.current = data.created_at;
      onRefresh();
    } catch {
      setMessages((prev) => prev.filter((m) => m.id !== optimistic.id));
      setText(t);
    } finally { setSending(false); }
  };

  // Groupement par date
  const grouped = messages.reduce((acc, msg) => {
    const day = new Date(msg.created_at).toLocaleDateString("fr-FR", { weekday: "long", day: "numeric", month: "long" });
    if (!acc.length || acc[acc.length - 1].day !== day) acc.push({ day, msgs: [] });
    acc[acc.length - 1].msgs.push(msg);
    return acc;
  }, []);

  return (
    <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
      {/* Header */}
      <div style={G.hdr}>
        <button onClick={onBack} style={{ ...G.btn, background: "none", color: "#fff", padding: 6, fontSize: 20 }}>←</button>
        {conv.icon
          ? <div style={{ width: 38, height: 38, borderRadius: "50%", background: conv.color || "#E6F1FB", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18 }}>{conv.icon}</div>
          : <Avatar nom={name} size={38} bg={C.purple} online={conv.other_user?.online} />
        }
        <div style={{ flex: 1 }}>
          <div style={{ ...G.hdrTitle, fontSize: 15 }}>{name}</div>
          {conv.type === "group" && conv.description && (
            <div style={G.hdrSub}>{conv.description}</div>
          )}
        </div>
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: "auto", padding: "12px 12px 0", background: C.chat, display: "flex", flexDirection: "column", gap: 4 }}>
        {grouped.map(({ day, msgs }) => (
          <div key={day}>
            <div style={{ textAlign: "center", fontSize: 11, color: "#64748B", background: "rgba(255,255,255,.75)", borderRadius: 12, padding: "3px 12px", display: "inline-block", margin: "8px auto", left: 0, right: 0, position: "relative", left: "50%", transform: "translateX(-50%)" }}>
              {day}
            </div>
            {msgs.map((msg) => {
              const mine = msg.sender_id === user.id;
              return (
                <div key={msg.id} style={{ display: "flex", flexDirection: "column", maxWidth: "82%", alignSelf: mine ? "flex-end" : "flex-start", alignItems: mine ? "flex-end" : "flex-start", marginBottom: 4 }}>
                  {!mine && conv.type === "group" && (
                    <span style={{ fontSize: 11, fontWeight: 500, color: C.purple, marginBottom: 2, paddingLeft: 4 }}>{msg.sender_nom}</span>
                  )}
                  <div style={{ padding: "8px 12px", borderRadius: mine ? "18px 18px 4px 18px" : "18px 18px 18px 4px", background: mine ? C.navy : "#fff", color: mine ? "#fff" : "#0F172A", fontSize: 14, lineHeight: 1.5, border: mine ? "none" : `1px solid ${C.border}`, opacity: msg.tmp ? 0.7 : 1 }}>
                    {msg.text}
                  </div>
                  <div style={{ fontSize: 10, color: "#94A3B8", marginTop: 2, paddingLeft: 4, paddingRight: 4 }}>
                    {timeStr(msg.created_at)}
                    {mine && <span style={{ marginLeft: 4 }}>✓✓</span>}
                  </div>
                </div>
              );
            })}
          </div>
        ))}
        <div ref={bottomRef} style={{ height: 8 }} />
      </div>

      {/* Saisie */}
      <div style={{ background: "#fff", padding: "8px 10px", display: "flex", alignItems: "flex-end", gap: 8, borderTop: `1px solid ${C.border}` }}>
        <div style={{ flex: 1, background: "#F1F5F9", borderRadius: 22, display: "flex", alignItems: "flex-end", padding: "8px 14px", gap: 8, border: `1px solid ${C.border}` }}>
          <textarea value={text} onChange={(e) => setText(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } }}
            placeholder="Votre message…" rows={1}
            style={{ flex: 1, background: "transparent", border: "none", outline: "none", fontSize: 14, color: "#0F172A", resize: "none", maxHeight: 100, lineHeight: 1.5, fontFamily: "inherit" }} />
        </div>
        <button onClick={send} disabled={!text.trim() || sending}
          style={{ width: 42, height: 42, borderRadius: "50%", background: text.trim() ? C.purple : C.navy, border: "none", color: "#fff", fontSize: 18, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
          ➤
        </button>
      </div>
    </div>
  );
}

// ─── Modal nouveau groupe ──────────────────────────────────────────────────
function NewGroupModal({ user, onClose, onCreated }) {
  const [form, setForm] = useState({ nom: "", description: "", theme: "LIBRE" });
  const [loading, setLoading] = useState(false);

  const themes = [
    { key: "VSI_PRO", label: "VSI PRO" }, { key: "EMPLOI", label: "Emploi" },
    { key: "ACCOMPAGNEMENT", label: "Accompagnement" }, { key: "FORMATION", label: "Formation" },
    { key: "LIBRE", label: "Libre" },
  ];

  const create = async () => {
    if (!form.nom.trim()) return;
    setLoading(true);
    try {
      const { data } = await axios.post(`${API}/ubuntoo/groups`, { ...form, creator_id: user.id });
      // Rejoindre automatiquement
      await axios.post(`${API}/ubuntoo/groups/${data.id}/join/${user.id}`);
      onCreated(data);
    } finally { setLoading(false); }
  };

  return (
    <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,.5)", display: "flex", alignItems: "flex-end", zIndex: 100 }}>
      <div style={{ background: "#fff", borderRadius: "20px 20px 0 0", padding: 24, width: "100%", maxWidth: 480, margin: "0 auto" }}>
        <div style={{ width: 40, height: 4, background: C.border, borderRadius: 2, margin: "0 auto 20px" }} />
        <div style={{ fontSize: 18, fontWeight: 500, color: "#0F172A", marginBottom: 16 }}>Créer un groupe</div>

        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <input placeholder="Nom du groupe" value={form.nom} onChange={(e) => setForm({ ...form, nom: e.target.value })}
            style={{ padding: "12px 14px", borderRadius: 10, border: `1.5px solid ${C.border}`, fontSize: 15, outline: "none" }} />
          <input placeholder="Description (optionnel)" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })}
            style={{ padding: "12px 14px", borderRadius: 10, border: `1.5px solid ${C.border}`, fontSize: 15, outline: "none" }} />

          <div>
            <div style={{ fontSize: 12, color: "#64748B", marginBottom: 8 }}>Thème</div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
              {themes.map((t) => (
                <button key={t.key} onClick={() => setForm({ ...form, theme: t.key })}
                  style={{ padding: "6px 12px", borderRadius: 20, border: `1.5px solid ${form.theme === t.key ? C.navy : C.border}`, background: form.theme === t.key ? C.navy : "#fff", color: form.theme === t.key ? "#fff" : "#64748B", fontSize: 13, cursor: "pointer" }}>
                  {t.label}
                </button>
              ))}
            </div>
          </div>

          <button onClick={create} disabled={!form.nom.trim() || loading}
            style={{ padding: "13px 0", background: C.navy, color: "#fff", borderRadius: 10, border: "none", fontSize: 15, fontWeight: 500, cursor: "pointer", marginTop: 4 }}>
            {loading ? "Création..." : "Créer le groupe"}
          </button>
          <button onClick={onClose} style={{ padding: "10px 0", background: "none", border: "none", color: "#64748B", fontSize: 14, cursor: "pointer" }}>
            Annuler
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── Modal nouveau message direct ──────────────────────────────────────────
function NewDirectModal({ user, onClose, onCreated }) {
  const [users, setUsers] = useState([]);
  const [search, setSearch] = useState("");

  useEffect(() => {
    axios.get(`${API}/ubuntoo/users?current_user_id=${user.id}`)
      .then(({ data }) => setUsers(data))
      .catch(() => {});
  }, [user.id]);

  const start = async (other) => {
    const { data } = await axios.post(`${API}/ubuntoo/conversations`, { user1_id: user.id, user2_id: other.id });
    onCreated({ ...data, other_user: other });
  };

  const filtered = users.filter((u) => u.nom.toLowerCase().includes(search.toLowerCase()));

  return (
    <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,.5)", display: "flex", alignItems: "flex-end", zIndex: 100 }}>
      <div style={{ background: "#fff", borderRadius: "20px 20px 0 0", padding: 24, width: "100%", maxWidth: 480, margin: "0 auto", maxHeight: "70vh", display: "flex", flexDirection: "column" }}>
        <div style={{ width: 40, height: 4, background: C.border, borderRadius: 2, margin: "0 auto 20px" }} />
        <div style={{ fontSize: 18, fontWeight: 500, color: "#0F172A", marginBottom: 16 }}>Nouveau message</div>
        <input placeholder="Rechercher un membre…" value={search} onChange={(e) => setSearch(e.target.value)}
          style={{ padding: "10px 14px", borderRadius: 10, border: `1.5px solid ${C.border}`, fontSize: 14, outline: "none", marginBottom: 12 }} />
        <div style={{ overflowY: "auto", flex: 1 }}>
          {filtered.map((u) => (
            <div key={u.id} onClick={() => start(u)} style={{ display: "flex", alignItems: "center", gap: 12, padding: "10px 0", cursor: "pointer", borderBottom: `1px solid ${C.border}` }}>
              <Avatar nom={u.nom} size={42} bg={C.purple} online={u.online} />
              <div>
                <div style={{ fontSize: 14, fontWeight: 500, color: "#0F172A" }}>{u.nom}</div>
                <div style={{ fontSize: 12, color: "#64748B" }}>{u.online ? "En ligne" : "Hors ligne"}</div>
              </div>
            </div>
          ))}
          {filtered.length === 0 && <div style={{ textAlign: "center", color: "#94A3B8", padding: 24 }}>Aucun membre trouvé</div>}
        </div>
        <button onClick={onClose} style={{ padding: "10px 0", background: "none", border: "none", color: "#64748B", fontSize: 14, cursor: "pointer", marginTop: 12 }}>
          Annuler
        </button>
      </div>
    </div>
  );
}

// ─── App principale ────────────────────────────────────────────────────────
export default function UbuntooApp() {
  const [user, setUser] = useState(() => storage.get("ubuntoo_user"));
  const [conversations, setConversations] = useState([]);
  const [activeConv, setActiveConv] = useState(null);
  const [showNewGroup, setShowNewGroup] = useState(false);
  const [showNewDirect, setShowNewDirect] = useState(false);

  // Charge les conversations
  const loadConversations = useCallback(async (u) => {
    if (!u) return;
    try {
      const [{ data: groups }, { data: directs }] = await Promise.all([
        axios.get(`${API}/ubuntoo/groups`),
        axios.get(`${API}/ubuntoo/conversations/user/${u.id}`),
      ]);
      setConversations([...groups, ...directs.filter((d) => d.type === "direct")]);
    } catch {}
  }, []);

  // Init groupes par défaut au premier chargement
  useEffect(() => {
    axios.post(`${API}/ubuntoo/groups/init`).catch(() => {});
  }, []);

  useEffect(() => {
    if (user) loadConversations(user);
  }, [user, loadConversations]);

  // Polling conversations toutes les 15s
  useEffect(() => {
    if (!user) return;
    const t = setInterval(() => loadConversations(user), 15000);
    return () => clearInterval(t);
  }, [user, loadConversations]);

  const handleLogin = (u) => {
    setUser(u);
    loadConversations(u);
  };

  const handleLogout = async () => {
    if (user) await axios.post(`${API}/ubuntoo/auth/logout/${user.id}`).catch(() => {});
    storage.del("ubuntoo_user");
    setUser(null);
    setConversations([]);
    setActiveConv(null);
  };

  if (!user) return <LoginScreen onLogin={handleLogin} />;

  return (
    <div style={G.app}>
      {activeConv ? (
        <ChatScreen
          user={user}
          conv={activeConv}
          onBack={() => setActiveConv(null)}
          onRefresh={() => loadConversations(user)}
        />
      ) : (
        <ConvList
          user={user}
          conversations={conversations}
          onOpen={(conv) => setActiveConv(conv)}
          onNewGroup={() => setShowNewGroup(true)}
          onNewDirect={() => setShowNewDirect(true)}
        />
      )}

      {showNewGroup && (
        <NewGroupModal
          user={user}
          onClose={() => setShowNewGroup(false)}
          onCreated={(conv) => { setShowNewGroup(false); loadConversations(user); setActiveConv(conv); }}
        />
      )}

      {showNewDirect && (
        <NewDirectModal
          user={user}
          onClose={() => setShowNewDirect(false)}
          onCreated={(conv) => { setShowNewDirect(false); loadConversations(user); setActiveConv(conv); }}
        />
      )}
    </div>
  );
}
