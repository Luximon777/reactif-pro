import { useState, useEffect, useCallback } from "react";
import {
  UserPlus, Search, Users, Tag, Link2, Send, X, Loader2,
  Check, Mail, Hash, Sparkles, Megaphone, Plus, CheckCircle
} from "lucide-react";
import { toast } from "sonner";

const API = `${process.env.REACT_APP_BACKEND_URL || ""}/api`;

/**
 * Admin panel embedded in VsiGroupDetail for the group admin only.
 * Tabs:
 *   - Invitations : search Ubuntoo users + invite (direct or request)
 *   - Tags        : edit group tags (autocomplete from existing)
 *   - Inter-groupes : list similar groups + cross-post + create cross-event
 */
const VsiGroupAdminPanel = ({ group, token, onChanged }) => {
  const [tab, setTab] = useState("invite"); // invite | tags | cross
  return (
    <div className="ub-vsi-admin-panel" data-testid="vsi-admin-panel">
      <div className="ub-vsi-admin-tabs">
        <button
          className={`ub-vsi-admin-tab ${tab === "invite" ? "active" : ""}`}
          onClick={() => setTab("invite")}
          data-testid="admin-tab-invite"
        ><UserPlus size={13} /> Inviter des pairs</button>
        <button
          className={`ub-vsi-admin-tab ${tab === "tags" ? "active" : ""}`}
          onClick={() => setTab("tags")}
          data-testid="admin-tab-tags"
        ><Tag size={13} /> Thématiques</button>
        <button
          className={`ub-vsi-admin-tab ${tab === "cross" ? "active" : ""}`}
          onClick={() => setTab("cross")}
          data-testid="admin-tab-cross"
        ><Link2 size={13} /> Groupes liés</button>
      </div>
      <div className="ub-vsi-admin-body">
        {tab === "invite" && <InviteSection group={group} token={token} onChanged={onChanged} />}
        {tab === "tags" && <TagsSection group={group} token={token} onChanged={onChanged} />}
        {tab === "cross" && <CrossGroupsSection group={group} token={token} />}
      </div>
    </div>
  );
};

// ============================ INVITE SECTION ============================
const InviteSection = ({ group, token, onChanged }) => {
  const [q, setQ] = useState("");
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [target, setTarget] = useState(null);
  const [mode, setMode] = useState("request"); // request | direct
  const [message, setMessage] = useState("");
  const [sending, setSending] = useState(false);

  const runSearch = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const params = new URLSearchParams({ token, limit: "20" });
      if (q.trim()) params.set("q", q.trim());
      const res = await fetch(`${API}/vsi-groups/${group.id}/searchable-users?${params.toString()}`);
      if (res.ok) {
        const data = await res.json();
        setUsers(data.users || []);
      }
    } catch (_) {} finally { setLoading(false); }
  }, [token, group.id, q]);

  useEffect(() => { runSearch(); }, [runSearch]);

  const sendInvitation = async () => {
    if (!target) return;
    setSending(true);
    try {
      const res = await fetch(`${API}/vsi-groups/${group.id}/invite?token=${token}`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          peer_token_id: target.token_id,
          mode,
          message: message.trim(),
        }),
      });
      if (res.ok) {
        const data = await res.json();
        if (data.mode === "direct") {
          toast.success(`${target.name} a rejoint le groupe`);
        } else {
          toast.success(`Invitation envoyée à ${target.name}`);
        }
        setTarget(null);
        setMessage("");
        runSearch();
        onChanged && onChanged();
      } else {
        const err = await res.json();
        toast.error(err.detail || "Échec de l'invitation");
      }
    } catch (_) {
      toast.error("Erreur réseau");
    } finally { setSending(false); }
  };

  return (
    <div data-testid="invite-section">
      <p style={{ fontSize: "12px", color: "var(--ub-text-muted)", marginBottom: "10px" }}>
        Recherche un pair Ubuntoo et invite-le à rejoindre <strong>{group.name}</strong>. Tu peux l'ajouter directement ou attendre son accord.
      </p>

      <div className="ub-search-bar" style={{ marginBottom: "12px" }}>
        <Search size={14} style={{ color: "var(--ub-text-muted)" }} />
        <input
          type="text"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Nom, pseudo, métier, secteur, ville…"
          data-testid="invite-search"
          onKeyDown={(e) => { if (e.key === "Enter") runSearch(); }}
        />
        <button className="ub-btn-small" onClick={runSearch} data-testid="invite-search-go">
          {loading ? <Loader2 size={12} className="ub-spin" /> : "Rechercher"}
        </button>
      </div>

      {loading ? (
        <div style={{ textAlign: "center", padding: "20px" }}><Loader2 size={18} className="ub-spin" /></div>
      ) : users.length === 0 ? (
        <p style={{ fontSize: "12px", color: "var(--ub-text-muted)", textAlign: "center", padding: "20px" }}>
          Aucun utilisateur Ubuntoo trouvé.
        </p>
      ) : (
        <div className="ub-invite-grid" data-testid="invite-results">
          {users.map(u => (
            <div key={u.token_id} className="ub-invite-card" data-testid={`invite-user-${u.token_id}`}>
              <div className="ub-avatar-sm" style={{ width: "36px", height: "36px", fontSize: "12px" }}>
                {(u.name || "?").split(" ").map(n => n[0]).join("").slice(0, 2).toUpperCase()}
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <p className="ub-invite-name">{u.name}</p>
                {u.title && <p className="ub-invite-meta">{u.title}{u.territory ? ` · ${u.territory}` : ""}</p>}
                {(u.sectors || []).length > 0 && (
                  <div className="ub-pill-row" style={{ marginTop: "4px" }}>
                    {u.sectors.slice(0, 2).map((s, i) => <span key={i} className="ub-pill ub-pill-savoir-faire">{s}</span>)}
                  </div>
                )}
              </div>
              <button
                className={`ub-btn-${u.already_invited ? "small" : "primary"}`}
                disabled={u.already_invited}
                onClick={() => setTarget(u)}
                data-testid={`invite-btn-${u.token_id}`}
                style={{ flexShrink: 0 }}
              >
                {u.already_invited ? <><CheckCircle size={12} /> Invité·e</> : <><UserPlus size={12} /> Inviter</>}
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Invite modal */}
      {target && (
        <div className="ub-vsi-modal-overlay" data-testid="invite-modal" onClick={() => setTarget(null)}>
          <div className="ub-vsi-modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: "500px" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "12px" }}>
              <h3 style={{ fontSize: "16px", fontWeight: 700, color: "var(--ub-navy)", fontFamily: "'Outfit', sans-serif", display: "flex", alignItems: "center", gap: "6px" }}>
                <UserPlus size={16} style={{ color: "var(--ub-primary)" }} />
                Inviter {target.name}
              </h3>
              <button onClick={() => setTarget(null)} style={{ background: "none", border: "none", cursor: "pointer", color: "var(--ub-text-muted)" }}>
                <X size={16} />
              </button>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
              <div>
                <label className="ub-form-label">Mode d'invitation</label>
                <div className="ub-mode-switch">
                  <button
                    className={`ub-mode-btn ${mode === "request" ? "active" : ""}`}
                    onClick={() => setMode("request")}
                    data-testid="invite-mode-request"
                  >
                    <Mail size={12} /> Invitation à accepter
                  </button>
                  <button
                    className={`ub-mode-btn ${mode === "direct" ? "active" : ""}`}
                    onClick={() => setMode("direct")}
                    data-testid="invite-mode-direct"
                  >
                    <Check size={12} /> Ajout direct
                  </button>
                </div>
                <p style={{ fontSize: "11px", color: "var(--ub-text-muted)", marginTop: "4px" }}>
                  {mode === "request"
                    ? "Le pair recevra une notification et devra accepter."
                    : "Le pair sera ajouté immédiatement au groupe."}
                </p>
              </div>

              <div>
                <label className="ub-form-label">Message d'accompagnement (optionnel)</label>
                <textarea
                  className="ub-input"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder={`Bonjour ${target.name}, on aimerait t'inviter à rejoindre le groupe ${group.name}…`}
                  rows={3}
                  maxLength={500}
                  data-testid="invite-message"
                  style={{ resize: "vertical", fontFamily: "inherit" }}
                />
              </div>
            </div>

            <div style={{ display: "flex", gap: "8px", justifyContent: "flex-end", marginTop: "14px" }}>
              <button className="ub-btn-small" onClick={() => setTarget(null)} data-testid="invite-cancel">Annuler</button>
              <button className="ub-btn-primary" onClick={sendInvitation} disabled={sending} data-testid="invite-confirm">
                {sending ? <Loader2 size={13} className="ub-spin" /> : <><Send size={13} /> {mode === "direct" ? "Ajouter" : "Envoyer"}</>}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// ============================ TAGS SECTION ============================
const TagsSection = ({ group, token, onChanged }) => {
  const [tags, setTags] = useState(group.tags || []);
  const [draft, setDraft] = useState("");
  const [allTags, setAllTags] = useState([]);
  const [saving, setSaving] = useState(false);
  const initial = JSON.stringify((group.tags || []).slice().sort());

  useEffect(() => {
    fetch(`${API}/vsi-groups/tags/all?token=${token}`)
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d) setAllTags(d.tags || []); })
      .catch(() => {});
  }, [token]);

  const addTag = (val) => {
    const v = (val || draft).trim().toLowerCase();
    if (!v || v.length < 2 || v.length > 30) return;
    if (tags.includes(v)) { setDraft(""); return; }
    if (tags.length >= 10) { toast.error("Maximum 10 tags"); return; }
    setTags([...tags, v]);
    setDraft("");
  };
  const removeTag = (v) => setTags(tags.filter(t => t !== v));

  const save = async () => {
    setSaving(true);
    try {
      const res = await fetch(`${API}/vsi-groups/${group.id}?token=${token}`, {
        method: "PUT", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tags }),
      });
      if (res.ok) {
        toast.success("Thématiques enregistrées");
        onChanged && onChanged();
      } else {
        toast.error("Échec de la mise à jour");
      }
    } finally { setSaving(false); }
  };

  const isDirty = JSON.stringify(tags.slice().sort()) !== initial;
  const suggestions = allTags.filter(t => !tags.includes(t.name)).slice(0, 8);

  return (
    <div data-testid="tags-section">
      <p style={{ fontSize: "12px", color: "var(--ub-text-muted)", marginBottom: "10px" }}>
        Les <strong>thématiques</strong> permettent de relier ton groupe à d'autres cohortes par affinité (ex: <em>reconversion, IA, RH, insertion…</em>). 10 max, 2-30 caractères.
      </p>

      <div className="ub-tags-edit" data-testid="tags-edit">
        {tags.length === 0 && (
          <span style={{ fontSize: "12px", color: "var(--ub-text-muted)" }}>Aucune thématique pour l'instant.</span>
        )}
        {tags.map(t => (
          <span key={t} className="ub-tag-chip" data-testid={`tag-chip-${t}`}>
            <Hash size={10} /> {t}
            <button onClick={() => removeTag(t)} data-testid={`tag-remove-${t}`}><X size={10} /></button>
          </span>
        ))}
      </div>

      <div style={{ display: "flex", gap: "6px", marginTop: "10px", alignItems: "center" }}>
        <input
          className="ub-input"
          style={{ flex: 1 }}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); addTag(); } }}
          placeholder="Ajouter une thématique…"
          maxLength={30}
          data-testid="tag-input"
        />
        <button className="ub-btn-primary" onClick={() => addTag()} data-testid="tag-add">
          <Plus size={12} /> Ajouter
        </button>
      </div>

      {suggestions.length > 0 && (
        <div style={{ marginTop: "12px" }}>
          <p style={{ fontSize: "11px", color: "var(--ub-text-muted)", marginBottom: "4px" }}>Suggestions populaires :</p>
          <div className="ub-pill-row">
            {suggestions.map(s => (
              <button
                key={s.name}
                className="ub-tag-suggestion"
                onClick={() => addTag(s.name)}
                data-testid={`tag-suggest-${s.name}`}
              >
                + {s.name} <span style={{ opacity: 0.5 }}>({s.count})</span>
              </button>
            ))}
          </div>
        </div>
      )}

      <div style={{ display: "flex", justifyContent: "flex-end", marginTop: "14px" }}>
        <button className="ub-btn-primary" onClick={save} disabled={!isDirty || saving} data-testid="tags-save">
          {saving ? <Loader2 size={13} className="ub-spin" /> : <><Check size={13} /> Enregistrer</>}
        </button>
      </div>
    </div>
  );
};

// ========================== CROSS GROUPS SECTION ==========================
const CrossGroupsSection = ({ group, token }) => {
  const [similar, setSimilar] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedIds, setSelectedIds] = useState([]);
  const [postBody, setPostBody] = useState("");
  const [posting, setPosting] = useState(false);

  // Cross-event modal
  const [showEventModal, setShowEventModal] = useState(false);
  const [evTitle, setEvTitle] = useState("");
  const [evDesc, setEvDesc] = useState("");
  const [evDate, setEvDate] = useState("");
  const [evTime, setEvTime] = useState("14:00");
  const [evDuration, setEvDuration] = useState(60);
  const [evMeet, setEvMeet] = useState("");
  const [savingEvent, setSavingEvent] = useState(false);

  const loadSimilar = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/vsi-groups/${group.id}/similar?token=${token}`);
      if (res.ok) {
        const data = await res.json();
        setSimilar(data.groups || []);
      }
    } finally { setLoading(false); }
  }, [token, group.id]);

  useEffect(() => { loadSimilar(); }, [loadSimilar]);

  const toggle = (id) => {
    setSelectedIds(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);
  };

  const crossPost = async () => {
    if (!postBody.trim()) { toast.error("Le message ne peut pas être vide"); return; }
    if (selectedIds.length === 0) { toast.error("Sélectionne au moins un groupe cible"); return; }
    setPosting(true);
    try {
      const res = await fetch(`${API}/vsi-groups/${group.id}/cross-post?token=${token}`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          body: postBody.trim(),
          target_group_ids: [group.id, ...selectedIds],
        }),
      });
      if (res.ok) {
        const data = await res.json();
        toast.success(`Posté dans ${data.total} groupe${data.total > 1 ? "s" : ""}`);
        setPostBody("");
        setSelectedIds([]);
      } else {
        const err = await res.json();
        toast.error(err.detail || "Échec du post");
      }
    } finally { setPosting(false); }
  };

  const createCrossEvent = async () => {
    if (!evTitle.trim()) { toast.error("Titre requis"); return; }
    if (!evDate) { toast.error("Date requise"); return; }
    if (selectedIds.length === 0) { toast.error("Sélectionne au moins un groupe lié"); return; }
    setSavingEvent(true);
    try {
      const res = await fetch(`${API}/vsi-groups/${group.id}/cross-event?token=${token}`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: evTitle.trim(),
          description: evDesc.trim(),
          start_at: `${evDate}T${evTime}:00`,
          duration_min: parseInt(evDuration, 10),
          meet_url: evMeet.trim(),
          linked_group_ids: selectedIds,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        toast.success(`Événement inter-groupes créé · ${data.attendees?.length || 0} participants notifiés`);
        setShowEventModal(false);
        setEvTitle(""); setEvDesc(""); setEvDate(""); setEvMeet("");
      } else {
        const err = await res.json();
        toast.error(err.detail || "Échec");
      }
    } finally { setSavingEvent(false); }
  };

  return (
    <div data-testid="cross-section">
      <p style={{ fontSize: "12px", color: "var(--ub-text-muted)", marginBottom: "12px" }}>
        Découvre les groupes affinitaires (par thématiques ou secteurs), <strong>partage un message multi-groupes</strong> ou organise un <strong>RDV visio inter-cohortes</strong>.
      </p>

      {loading ? (
        <div style={{ textAlign: "center", padding: "20px" }}><Loader2 size={18} className="ub-spin" /></div>
      ) : similar.length === 0 ? (
        <div className="ub-search-empty" style={{ padding: "20px" }}>
          <Sparkles size={28} style={{ color: "var(--ub-text-muted)", opacity: 0.4 }} />
          <p style={{ marginTop: "8px", color: "var(--ub-text-muted)", fontSize: "13px" }}>
            Aucun groupe similaire pour l'instant. Ajoute des thématiques pour créer des ponts !
          </p>
        </div>
      ) : (
        <>
          <p style={{ fontSize: "11px", color: "var(--ub-text-muted)", marginBottom: "6px" }}>
            {similar.length} groupe{similar.length > 1 ? "s" : ""} affinitaire{similar.length > 1 ? "s" : ""} — sélectionne ceux à associer
          </p>
          <div className="ub-cross-grid" data-testid="cross-list">
            {similar.map(g => {
              const sel = selectedIds.includes(g.id);
              return (
                <button
                  key={g.id}
                  className={`ub-cross-card${sel ? " selected" : ""}`}
                  onClick={() => toggle(g.id)}
                  data-testid={`cross-toggle-${g.id}`}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "6px" }}>
                    <h4 className="ub-cross-name">{g.name}</h4>
                    {sel ? <CheckCircle size={14} style={{ color: "var(--ub-primary)" }} /> : <Plus size={14} style={{ color: "var(--ub-text-muted)" }} />}
                  </div>
                  {g.theme && <p style={{ fontSize: "11px", color: "var(--ub-text-secondary)", margin: "2px 0" }}>{g.theme}</p>}
                  <p style={{ fontSize: "10px", color: "var(--ub-text-muted)", marginTop: "4px" }}>
                    <Users size={9} /> {g.participant_count} membres
                  </p>
                  {(g.shared_tags || []).length > 0 && (
                    <div className="ub-pill-row" style={{ marginTop: "6px" }}>
                      {g.shared_tags.slice(0, 3).map(t => <span key={t} className="ub-pill ub-pill-savoir-etre">#{t}</span>)}
                    </div>
                  )}
                  {(g.shared_sectors || []).length > 0 && (
                    <div className="ub-pill-row" style={{ marginTop: "4px" }}>
                      {g.shared_sectors.slice(0, 2).map(s => <span key={s} className="ub-pill ub-pill-savoir-faire">{s}</span>)}
                    </div>
                  )}
                </button>
              );
            })}
          </div>

          {/* Cross-post composer */}
          <div className="ub-cross-action-card">
            <h4 className="ub-cross-action-title"><Megaphone size={13} /> Post multi-groupes</h4>
            <textarea
              className="ub-input"
              value={postBody}
              onChange={(e) => setPostBody(e.target.value)}
              placeholder={`Annonce à publier dans ${group.name}${selectedIds.length ? ` + ${selectedIds.length} groupe${selectedIds.length > 1 ? "s" : ""}` : ""}…`}
              rows={3}
              maxLength={2000}
              data-testid="cross-post-body"
              style={{ resize: "vertical", fontFamily: "inherit", marginTop: "8px" }}
            />
            <button
              className="ub-btn-primary"
              onClick={crossPost}
              disabled={posting || !postBody.trim() || selectedIds.length === 0}
              data-testid="cross-post-send"
              style={{ marginTop: "8px" }}
            >
              {posting ? <Loader2 size={13} className="ub-spin" /> : <><Send size={13} /> Publier ({selectedIds.length + 1} groupes)</>}
            </button>
          </div>

          {/* Cross-event button */}
          <div className="ub-cross-action-card">
            <h4 className="ub-cross-action-title"><Link2 size={13} /> Événement inter-groupes</h4>
            <p style={{ fontSize: "11px", color: "var(--ub-text-muted)", margin: "4px 0 8px" }}>
              Crée un RDV visio qui réunit ton groupe et les groupes sélectionnés.
            </p>
            <button
              className="ub-btn-primary"
              onClick={() => setShowEventModal(true)}
              disabled={selectedIds.length === 0}
              data-testid="cross-event-open"
            >
              <Plus size={13} /> Programmer ({selectedIds.length} liés)
            </button>
          </div>
        </>
      )}

      {showEventModal && (
        <div className="ub-vsi-modal-overlay" data-testid="cross-event-modal" onClick={() => setShowEventModal(false)}>
          <div className="ub-vsi-modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: "520px" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "12px" }}>
              <h3 style={{ fontSize: "16px", fontWeight: 700, color: "var(--ub-navy)", fontFamily: "'Outfit', sans-serif", display: "flex", alignItems: "center", gap: "6px" }}>
                <Link2 size={16} style={{ color: "var(--ub-primary)" }} />
                Événement inter-groupes
              </h3>
              <button onClick={() => setShowEventModal(false)} style={{ background: "none", border: "none", cursor: "pointer", color: "var(--ub-text-muted)" }}>
                <X size={16} />
              </button>
            </div>
            <p style={{ fontSize: "11px", color: "var(--ub-text-muted)", marginBottom: "10px" }}>
              <strong>{selectedIds.length}</strong> groupe{selectedIds.length > 1 ? "s" : ""} sélectionné{selectedIds.length > 1 ? "s" : ""} + ton groupe primaire.
            </p>

            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              <div>
                <label className="ub-form-label">Titre *</label>
                <input className="ub-input" value={evTitle} onChange={(e) => setEvTitle(e.target.value)} data-testid="cross-event-title" />
              </div>
              <div>
                <label className="ub-form-label">Description</label>
                <textarea className="ub-input" value={evDesc} onChange={(e) => setEvDesc(e.target.value)} rows={3}
                  data-testid="cross-event-desc" style={{ resize: "vertical", fontFamily: "inherit" }} />
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "8px" }}>
                <div>
                  <label className="ub-form-label">Date *</label>
                  <input type="date" className="ub-input" value={evDate} onChange={(e) => setEvDate(e.target.value)} data-testid="cross-event-date" />
                </div>
                <div>
                  <label className="ub-form-label">Heure *</label>
                  <input type="time" className="ub-input" value={evTime} onChange={(e) => setEvTime(e.target.value)} data-testid="cross-event-time" />
                </div>
                <div>
                  <label className="ub-form-label">Durée</label>
                  <select className="ub-input" value={evDuration} onChange={(e) => setEvDuration(parseInt(e.target.value, 10))} data-testid="cross-event-duration">
                    {[30, 45, 60, 90, 120].map(d => <option key={d} value={d}>{d} min</option>)}
                  </select>
                </div>
              </div>
              <div>
                <label className="ub-form-label">Lien Google Meet</label>
                <input className="ub-input" value={evMeet} onChange={(e) => setEvMeet(e.target.value)}
                  placeholder="https://meet.google.com/abc-defg-hij" data-testid="cross-event-meet" />
              </div>
            </div>
            <div style={{ display: "flex", gap: "8px", justifyContent: "flex-end", marginTop: "14px" }}>
              <button className="ub-btn-small" onClick={() => setShowEventModal(false)}>Annuler</button>
              <button className="ub-btn-primary" onClick={createCrossEvent} disabled={savingEvent} data-testid="cross-event-save">
                {savingEvent ? <Loader2 size={13} className="ub-spin" /> : <><Plus size={13} /> Programmer</>}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VsiGroupAdminPanel;
