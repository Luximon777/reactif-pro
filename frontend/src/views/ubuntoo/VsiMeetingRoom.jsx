import { useState, useEffect, useCallback, useRef } from "react";
import {
  Video, ExternalLink, ArrowLeft, Loader2, Send, Smile, Paperclip,
  X, Image as ImageIcon, FileText, Download, MessageCircle, Clock, Users, Copy
} from "lucide-react";
import { toast } from "sonner";
import { fmtDateTime, computeStatus, countdownText } from "./VsiGroupAgenda";

const API = `${process.env.REACT_APP_BACKEND_URL || ""}/api`;

const QUICK_EMOJIS = ["😊", "👍", "❤️", "🎉", "🙏", "🔥", "💡", "👏", "🤔", "😅", "🚀", "🇪🇺"];

/**
 * VsiMeetingRoom — When the user joins an event, this view opens:
 *   - Left: meeting card (Google Meet link, countdown, RSVPs, participants)
 *   - Right: chat sidebar (reuses group chat with emojis, attachments)
 */
const VsiMeetingRoom = ({ event, groupId, group, token, onBack }) => {
  const [messages, setMessages] = useState([]);
  const [reply, setReply] = useState("");
  const [sending, setSending] = useState(false);
  const [pendingAttachments, setPendingAttachments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [showEmojis, setShowEmojis] = useState(false);
  const [now, setNow] = useState(Date.now());
  const fileInputRef = useRef(null);

  const status = computeStatus(event);
  const cd = countdownText(event.start_at);

  // Live clock tick
  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), 30_000);
    return () => clearInterval(id);
  }, []);

  const loadMessages = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API}/vsi-groups/${groupId}/messages?token=${token}`);
      if (res.ok) {
        const data = await res.json();
        setMessages(data.messages || []);
      }
    } catch (_) {}
  }, [token, groupId]);

  useEffect(() => {
    loadMessages();
    const id = setInterval(loadMessages, 8000);
    return () => clearInterval(id);
  }, [loadMessages]);

  const handleFilePick = async (e) => {
    const files = Array.from(e.target.files || []);
    if (!files.length || !token) return;
    setUploading(true);
    try {
      for (const file of files.slice(0, 5)) {
        if (file.size > 3 * 1024 * 1024) { toast.error(`${file.name} dépasse 3 Mo`); continue; }
        const dataUrl = await new Promise((resolve, reject) => {
          const r = new FileReader();
          r.onload = () => resolve(r.result); r.onerror = reject;
          r.readAsDataURL(file);
        });
        const res = await fetch(`${API}/ubuntoo/upload?token=${token}`, {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ data_url: dataUrl, name: file.name }),
        });
        if (res.ok) {
          const meta = await res.json();
          setPendingAttachments(prev => [...prev, meta]);
        } else {
          toast.error("Upload impossible");
        }
      }
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const removePending = (id) => setPendingAttachments(prev => prev.filter(a => a.id !== id));
  const insertEmoji = (e) => { setReply(prev => prev + e); setShowEmojis(false); };

  const send = async () => {
    if ((!reply.trim() && pendingAttachments.length === 0) || !token) return;
    setSending(true);
    try {
      const res = await fetch(`${API}/vsi-groups/${groupId}/messages?token=${token}`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          body: reply.trim(),
          attachments: pendingAttachments.map(a => ({
            id: a.id, name: a.name, content_type: a.content_type, size: a.size, is_image: a.is_image,
          })),
        }),
      });
      if (res.ok) {
        setReply(""); setPendingAttachments([]);
        loadMessages();
      }
    } finally { setSending(false); }
  };

  const copyMeetLink = () => {
    if (!event.meet_url) return;
    navigator.clipboard.writeText(event.meet_url).then(
      () => toast.success("Lien copié dans le presse-papiers"),
      () => toast.error("Copie impossible")
    );
  };

  // Count RSVPs
  const rsvpYes = Object.values(event.rsvps || {}).filter(v => v === "yes").length;
  const rsvpMaybe = Object.values(event.rsvps || {}).filter(v => v === "maybe").length;
  const rsvpNo = Object.values(event.rsvps || {}).filter(v => v === "no").length;

  return (
    <div className="ub-meeting-room" data-testid="vsi-meeting-room">
      {/* Header */}
      <div className="ub-meeting-header">
        <button className="ub-btn-small" onClick={onBack} data-testid="meeting-back-btn">
          <ArrowLeft size={14} /> Retour à l'agenda
        </button>
        <div style={{ flex: 1 }}>
          <h2 className="ub-meeting-title">
            <Video size={18} style={{ color: "var(--ub-primary)" }} /> {event.title}
          </h2>
          <p style={{ fontSize: "12px", color: "var(--ub-text-muted)", margin: "2px 0 0" }}>
            {group?.name} · {fmtDateTime(event.start_at)} · {event.duration_min} min
          </p>
        </div>
        {status === "live" && (
          <span className="ub-badge green" style={{ fontSize: "11px", animation: "ub-pulse 2s infinite" }}>
            ● En direct
          </span>
        )}
        {cd && status !== "past" && (
          <span className="ub-badge orange" style={{ fontSize: "11px" }}>
            <Clock size={11} /> {cd}
          </span>
        )}
      </div>

      {/* Main layout: visio (left) + chat sidebar (right) */}
      <div className="ub-meeting-layout">
        {/* === Visio panel === */}
        <div className="ub-meeting-visio" data-testid="meeting-visio-panel">
          <div className="ub-meeting-visio-card">
            {event.meet_url ? (
              <>
                <div className="ub-meeting-visio-illustration">
                  <Video size={64} style={{ color: "var(--ub-primary)" }} />
                </div>
                <h3 className="ub-meeting-cta-title">
                  {status === "live" ? "La réunion est en cours" : status === "upcoming" ? "Salon de réunion ouvert" : "Réunion passée"}
                </h3>
                <p style={{ fontSize: "13px", color: "var(--ub-text-secondary)", textAlign: "center", marginBottom: "16px", maxWidth: "440px" }}>
                  {status === "past"
                    ? "Cette réunion s'est tenue. Le chat reste accessible pour discuter de la suite."
                    : "Clique ci-dessous pour rejoindre la visio Google Meet dans un nouvel onglet. Le chat de cohorte continue ici en parallèle."}
                </p>
                <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", justifyContent: "center" }}>
                  <a
                    href={event.meet_url}
                    target="_blank"
                    rel="noreferrer"
                    className="ub-btn-primary ub-meeting-join-btn"
                    data-testid="meeting-join-meet"
                  >
                    <Video size={16} /> Rejoindre la visio
                    <ExternalLink size={14} />
                  </a>
                  <button className="ub-btn-small" onClick={copyMeetLink} data-testid="meeting-copy-link">
                    <Copy size={12} /> Copier le lien
                  </button>
                </div>
                <p style={{ fontSize: "11px", color: "var(--ub-text-muted)", marginTop: "16px", textAlign: "center", wordBreak: "break-all" }}>
                  {event.meet_url}
                </p>
              </>
            ) : (
              <div style={{ textAlign: "center", padding: "30px" }}>
                <Video size={36} style={{ color: "var(--ub-text-muted)", opacity: 0.5 }} />
                <p style={{ marginTop: "12px", fontSize: "13px", color: "var(--ub-text-muted)" }}>
                  Aucun lien de visio renseigné pour ce rendez-vous.
                </p>
                <p style={{ fontSize: "12px", color: "var(--ub-text-muted)", marginTop: "8px" }}>
                  L'organisateur peut éditer l'événement pour ajouter un lien Google Meet.
                </p>
              </div>
            )}
          </div>

          {/* Event details */}
          {event.description && (
            <div className="ub-meeting-desc-card" data-testid="meeting-desc">
              <h4 style={{ fontSize: "13px", fontWeight: 700, color: "var(--ub-navy)", marginBottom: "6px" }}>Ordre du jour</h4>
              <p style={{ fontSize: "13px", color: "var(--ub-text-secondary)", lineHeight: 1.5, whiteSpace: "pre-wrap" }}>
                {event.description}
              </p>
            </div>
          )}

          {/* RSVPs counts */}
          <div className="ub-meeting-rsvps" data-testid="meeting-rsvps">
            <h4 style={{ fontSize: "13px", fontWeight: 700, color: "var(--ub-navy)", marginBottom: "6px" }}>
              <Users size={13} /> Participations
            </h4>
            <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
              <span className="ub-badge green" style={{ fontSize: "11px" }}>✓ {rsvpYes} oui</span>
              <span className="ub-badge orange" style={{ fontSize: "11px" }}>? {rsvpMaybe} peut-être</span>
              <span className="ub-badge" style={{ fontSize: "11px", background: "#fee2e2", color: "#991b1b" }}>✕ {rsvpNo} non</span>
            </div>
          </div>
        </div>

        {/* === Chat sidebar === */}
        <div className="ub-meeting-chat" data-testid="meeting-chat-sidebar">
          <div className="ub-meeting-chat-header">
            <MessageCircle size={14} /> Discussion du salon
          </div>
          <div className="ub-meeting-chat-thread" data-testid="meeting-chat-thread">
            {messages.length === 0 ? (
              <p style={{ color: "var(--ub-text-muted)", fontSize: "12px", textAlign: "center", padding: "20px" }}>
                Aucun message. Lance la conversation !
              </p>
            ) : messages.map((m, i) => (
              <div key={i} data-testid={`meeting-msg-${i}`} className="ub-meeting-msg">
                <div className="ub-avatar-sm" style={{ width: "24px", height: "24px", fontSize: "9px", flexShrink: 0 }}>
                  {(m.from_name || "?").split(" ").map(n => n[0]).join("").slice(0, 2).toUpperCase()}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", gap: "6px" }}>
                    <span style={{ fontSize: "11px", fontWeight: 700, color: "var(--ub-navy)" }}>{m.from_name}</span>
                    <span style={{ fontSize: "10px", color: "var(--ub-text-muted)" }}>
                      {new Date(m.created_at).toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" })}
                    </span>
                  </div>
                  {m.body && <p style={{ fontSize: "12px", color: "var(--ub-text-primary)", margin: "2px 0", lineHeight: 1.4, wordBreak: "break-word" }}>{m.body}</p>}
                  {(m.attachments || []).length > 0 && (
                    <div style={{ marginTop: "4px", display: "flex", flexDirection: "column", gap: "4px" }}>
                      {m.attachments.map(a => {
                        const url = `${process.env.REACT_APP_BACKEND_URL || ""}/api/ubuntoo/attachments/${a.id}`;
                        if (a.is_image) {
                          return (
                            <a key={a.id} href={url} target="_blank" rel="noreferrer">
                              <img src={url} alt={a.name} style={{ maxWidth: "180px", maxHeight: "120px", borderRadius: "8px", display: "block" }} />
                            </a>
                          );
                        }
                        return (
                          <a key={a.id} href={url} target="_blank" rel="noreferrer" download={a.name}
                            style={{ display: "inline-flex", alignItems: "center", gap: "6px", background: "rgba(0,0,0,0.05)", padding: "5px 8px", borderRadius: "8px", fontSize: "11px", color: "var(--ub-navy)", textDecoration: "none" }}
                          >
                            <FileText size={12} /> {a.name} <Download size={11} />
                          </a>
                        );
                      })}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
          {pendingAttachments.length > 0 && (
            <div className="ub-pending-attachments" data-testid="meeting-pending-attachments">
              {pendingAttachments.map(a => (
                <div key={a.id} className="ub-pending-chip" data-testid={`meeting-pending-${a.id}`}>
                  {a.is_image ? <ImageIcon size={11} /> : <FileText size={11} />}
                  <span style={{ maxWidth: "80px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{a.name}</span>
                  <button onClick={() => removePending(a.id)}><X size={9} /></button>
                </div>
              ))}
            </div>
          )}
          <div className="ub-meeting-chat-composer">
            <button
              className="ub-icon-btn ub-icon-btn-sm"
              onClick={() => setShowEmojis(v => !v)}
              data-testid="meeting-emoji-btn"
              title="Insérer un emoji"
            >
              <Smile size={14} />
            </button>
            {showEmojis && (
              <div className="ub-emoji-popover" data-testid="meeting-emoji-popover" style={{ left: "8px", bottom: "60px" }}>
                {QUICK_EMOJIS.map(e => (
                  <button key={e} onClick={() => insertEmoji(e)}>
                    <span style={{ fontSize: "20px" }}>{e}</span>
                  </button>
                ))}
              </div>
            )}
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept="image/*,application/pdf,.doc,.docx,.txt,.csv,.zip"
              onChange={handleFilePick}
              style={{ display: "none" }}
              data-testid="meeting-attach-input"
            />
            <button
              className="ub-icon-btn ub-icon-btn-sm"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              data-testid="meeting-attach-btn"
              title="Joindre"
            >
              {uploading ? <Loader2 size={14} className="ub-spin" /> : <Paperclip size={14} />}
            </button>
            <textarea
              data-testid="meeting-chat-reply"
              value={reply}
              onChange={(e) => setReply(e.target.value)}
              placeholder="Message au salon…"
              rows={2}
              onKeyDown={(e) => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) { e.preventDefault(); send(); } }}
            />
            <button
              className="ub-btn-primary ub-icon-btn-sm"
              data-testid="meeting-chat-send"
              disabled={(!reply.trim() && pendingAttachments.length === 0) || sending}
              onClick={send}
              style={{ opacity: ((!reply.trim() && pendingAttachments.length === 0) || sending) ? 0.5 : 1 }}
            >
              {sending ? <Loader2 size={14} className="ub-spin" /> : <Send size={14} />}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VsiMeetingRoom;
