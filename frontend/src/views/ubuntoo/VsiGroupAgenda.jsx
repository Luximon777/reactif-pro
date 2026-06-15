import { useState, useEffect, useCallback } from "react";
import {
  CalendarDays, Clock, Plus, Video, X, Trash2, Edit2, ExternalLink,
  Check, HelpCircle, ChevronLeft, ChevronRight, Loader2, Sparkles
} from "lucide-react";
import { toast } from "sonner";

const API = `${process.env.REACT_APP_BACKEND_URL || ""}/api`;

const MONTH_NAMES = [
  "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
  "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
];
const DAY_NAMES = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"];

const fmtDateTime = (iso) => {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleString("fr-FR", {
      weekday: "short", day: "2-digit", month: "short",
      hour: "2-digit", minute: "2-digit"
    });
  } catch (_) { return iso; }
};

const fmtTime = (iso) => {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" });
  } catch (_) { return iso; }
};

const computeStatus = (event) => {
  try {
    const start = new Date(event.start_at).getTime();
    const end = start + (event.duration_min || 60) * 60_000;
    const now = Date.now();
    if (now < start - 10 * 60_000) return "upcoming";
    if (now < end) return "live";
    return "past";
  } catch (_) { return "upcoming"; }
};

const countdownText = (iso) => {
  try {
    const diff = new Date(iso).getTime() - Date.now();
    if (diff < 0) return null;
    const min = Math.floor(diff / 60_000);
    if (min < 60) return `dans ${min} min`;
    const h = Math.floor(min / 60);
    if (h < 24) return `dans ${h} h ${min % 60} min`;
    const d = Math.floor(h / 24);
    return `dans ${d} j ${h % 24} h`;
  } catch (_) { return null; }
};

// =========================== Calendar Grid ===========================
const CalendarGrid = ({ events, viewMonth, onPrev, onNext, onSelectDay, selectedDay }) => {
  const year = viewMonth.getFullYear();
  const month = viewMonth.getMonth();
  const firstDay = new Date(year, month, 1);
  const startWeekday = (firstDay.getDay() + 6) % 7; // Monday-first
  const daysInMonth = new Date(year, month + 1, 0).getDate();

  // Map events by yyyy-mm-dd
  const eventsByDay = {};
  events.forEach(e => {
    const d = new Date(e.start_at);
    const key = `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`;
    eventsByDay[key] = (eventsByDay[key] || []).concat(e);
  });

  const cells = [];
  for (let i = 0; i < startWeekday; i++) cells.push({ blank: true });
  for (let d = 1; d <= daysInMonth; d++) cells.push({ day: d });

  return (
    <div className="ub-cal" data-testid="vsi-calendar">
      <div className="ub-cal-header">
        <button className="ub-icon-btn" onClick={onPrev} data-testid="cal-prev"><ChevronLeft size={16} /></button>
        <h3 className="ub-cal-title">{MONTH_NAMES[month]} {year}</h3>
        <button className="ub-icon-btn" onClick={onNext} data-testid="cal-next"><ChevronRight size={16} /></button>
      </div>
      <div className="ub-cal-weekdays">
        {DAY_NAMES.map(d => <span key={d}>{d}</span>)}
      </div>
      <div className="ub-cal-grid">
        {cells.map((c, i) => {
          if (c.blank) return <div key={i} className="ub-cal-cell blank" />;
          const key = `${year}-${month}-${c.day}`;
          const dayEvents = eventsByDay[key] || [];
          const isToday = (() => {
            const t = new Date();
            return t.getFullYear() === year && t.getMonth() === month && t.getDate() === c.day;
          })();
          const isSelected = selectedDay && selectedDay.getFullYear() === year
            && selectedDay.getMonth() === month && selectedDay.getDate() === c.day;
          return (
            <button
              key={i}
              data-testid={`cal-day-${c.day}`}
              className={`ub-cal-cell${isToday ? " today" : ""}${isSelected ? " selected" : ""}${dayEvents.length ? " has-events" : ""}`}
              onClick={() => onSelectDay && onSelectDay(new Date(year, month, c.day))}
            >
              <span className="ub-cal-day-num">{c.day}</span>
              {dayEvents.length > 0 && (
                <div className="ub-cal-dots">
                  {dayEvents.slice(0, 3).map((e, idx) => (
                    <span key={idx} className={`ub-cal-dot ${computeStatus(e)}`} title={e.title} />
                  ))}
                  {dayEvents.length > 3 && <span className="ub-cal-dots-more">+{dayEvents.length - 3}</span>}
                </div>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
};

// =========================== Event Modal (create/edit) ===========================
const EventModal = ({ initial, onClose, onSave, saving }) => {
  const [title, setTitle] = useState(initial?.title || "");
  const [description, setDescription] = useState(initial?.description || "");
  const [date, setDate] = useState(initial?.start_at ? initial.start_at.slice(0, 10) : "");
  const [time, setTime] = useState(initial?.start_at ? initial.start_at.slice(11, 16) : "14:00");
  const [duration, setDuration] = useState(initial?.duration_min || 60);
  const [meetUrl, setMeetUrl] = useState(initial?.meet_url || "");

  const handleSave = () => {
    if (!title.trim()) { toast.error("Le titre est requis"); return; }
    if (!date) { toast.error("La date est requise"); return; }
    if (!time) { toast.error("L'heure est requise"); return; }
    const start_at = `${date}T${time}:00`;
    onSave({
      title: title.trim(),
      description: description.trim(),
      start_at,
      duration_min: parseInt(duration, 10),
      meet_url: meetUrl.trim(),
    });
  };

  return (
    <div className="ub-vsi-modal-overlay" onClick={onClose} data-testid="vsi-event-modal">
      <div className="ub-vsi-modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: "520px" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "16px" }}>
          <h3 style={{ fontSize: "18px", fontWeight: 700, color: "var(--ub-navy)", fontFamily: "'Outfit', sans-serif", display: "flex", alignItems: "center", gap: "8px" }}>
            <Video size={18} style={{ color: "var(--ub-primary)" }} />
            {initial?.id ? "Modifier le rendez-vous" : "Nouveau rendez-vous visio"}
          </h3>
          <button onClick={onClose} style={{ background: "none", border: "none", cursor: "pointer", color: "var(--ub-text-muted)" }}>
            <X size={18} />
          </button>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          <div>
            <label className="ub-form-label">Titre *</label>
            <input
              className="ub-input"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Ex: Bilan mensuel cohorte"
              data-testid="event-title"
            />
          </div>

          <div>
            <label className="ub-form-label">Description</label>
            <textarea
              className="ub-input"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Ordre du jour, intentions, ressources à préparer…"
              rows={3}
              data-testid="event-description"
              style={{ resize: "vertical", fontFamily: "inherit" }}
            />
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "10px" }}>
            <div>
              <label className="ub-form-label">Date *</label>
              <input
                type="date"
                className="ub-input"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                data-testid="event-date"
              />
            </div>
            <div>
              <label className="ub-form-label">Heure *</label>
              <input
                type="time"
                className="ub-input"
                value={time}
                onChange={(e) => setTime(e.target.value)}
                data-testid="event-time"
              />
            </div>
            <div>
              <label className="ub-form-label">Durée (min)</label>
              <select
                className="ub-input"
                value={duration}
                onChange={(e) => setDuration(parseInt(e.target.value, 10))}
                data-testid="event-duration"
              >
                {[15, 30, 45, 60, 90, 120, 180].map(d => (
                  <option key={d} value={d}>{d} min</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="ub-form-label">Lien Google Meet</label>
            <input
              className="ub-input"
              value={meetUrl}
              onChange={(e) => setMeetUrl(e.target.value)}
              placeholder="https://meet.google.com/abc-defg-hij"
              data-testid="event-meet-url"
            />
            <p style={{ fontSize: "11px", color: "var(--ub-text-muted)", marginTop: "4px" }}>
              💡 Crée ta réunion sur <a href="https://meet.google.com/new" target="_blank" rel="noreferrer" style={{ color: "var(--ub-primary)" }}>meet.google.com/new</a> puis colle le lien ici (modifiable plus tard).
            </p>
          </div>
        </div>

        <div style={{ display: "flex", gap: "8px", justifyContent: "flex-end", marginTop: "16px" }}>
          <button className="ub-btn-small" onClick={onClose} data-testid="event-cancel">Annuler</button>
          <button
            className="ub-btn-primary"
            disabled={saving || !title.trim() || !date || !time}
            onClick={handleSave}
            data-testid="event-save"
          >
            {saving ? <Loader2 size={14} className="ub-spin" /> : (initial?.id ? "Enregistrer" : "Programmer")}
          </button>
        </div>
      </div>
    </div>
  );
};

// =========================== Agenda Main ===========================
const VsiGroupAgenda = ({ groupId, token, group, onJoinMeeting }) => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState("month"); // "month" | "list"
  const [viewMonth, setViewMonth] = useState(new Date());
  const [selectedDay, setSelectedDay] = useState(new Date());
  const [showCreate, setShowCreate] = useState(false);
  const [editEvent, setEditEvent] = useState(null);
  const [saving, setSaving] = useState(false);

  // My token_id is derived from group.participants_detail (already loaded by parent)
  const myTokenId = (group?.participants_detail || []).find(p => p.is_me)?.token_id || null;

  const loadEvents = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const res = await fetch(`${API}/vsi-groups/${groupId}/events?token=${token}`);
      if (res.ok) {
        const data = await res.json();
        setEvents(data.events || []);
      }
    } catch (_) {} finally { setLoading(false); }
  }, [token, groupId]);

  useEffect(() => { loadEvents(); }, [loadEvents]);

  const saveEvent = async (data) => {
    setSaving(true);
    try {
      const url = editEvent?.id
        ? `${API}/vsi-groups/${groupId}/events/${editEvent.id}?token=${token}`
        : `${API}/vsi-groups/${groupId}/events?token=${token}`;
      const res = await fetch(url, {
        method: editEvent?.id ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (res.ok) {
        toast.success(editEvent?.id ? "Rendez-vous mis à jour" : "Rendez-vous programmé");
        setShowCreate(false);
        setEditEvent(null);
        loadEvents();
      } else {
        const err = await res.json();
        toast.error("Erreur : " + (err.detail || "impossible d'enregistrer"));
      }
    } catch (_) {
      toast.error("Erreur réseau");
    } finally { setSaving(false); }
  };

  const deleteEvent = async (eventId) => {
    if (!window.confirm("Annuler définitivement ce rendez-vous ? Tous les participants seront notifiés.")) return;
    try {
      const res = await fetch(`${API}/vsi-groups/${groupId}/events/${eventId}?token=${token}`, { method: "DELETE" });
      if (res.ok) {
        toast.success("Rendez-vous annulé");
        loadEvents();
      } else {
        const err = await res.json();
        toast.error("Erreur : " + (err.detail || "impossible d'annuler"));
      }
    } catch (_) { toast.error("Erreur réseau"); }
  };

  const sendRsvp = async (eventId, answer) => {
    try {
      const res = await fetch(`${API}/vsi-groups/${groupId}/events/${eventId}/rsvp?token=${token}`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answer }),
      });
      if (res.ok) {
        loadEvents();
        toast.success("Réponse enregistrée");
      }
    } catch (_) {}
  };

  // Filter list by selected day if viewMode === "month"
  const dayFilteredEvents = events.filter(e => {
    if (viewMode !== "month") return true;
    const d = new Date(e.start_at);
    return d.getFullYear() === selectedDay.getFullYear()
      && d.getMonth() === selectedDay.getMonth()
      && d.getDate() === selectedDay.getDate();
  });

  const upcomingEvents = events.filter(e => computeStatus(e) !== "past")
    .sort((a, b) => new Date(a.start_at) - new Date(b.start_at));
  const pastEvents = events.filter(e => computeStatus(e) === "past")
    .sort((a, b) => new Date(b.start_at) - new Date(a.start_at));

  const listEvents = viewMode === "month" ? dayFilteredEvents : upcomingEvents;

  return (
    <div className="ub-vsi-agenda" data-testid="vsi-agenda">
      <div className="ub-vsi-agenda-header">
        <h2 className="ub-vsi-side-title" style={{ fontSize: "16px" }}>
          <CalendarDays size={16} /> Agenda du groupe
          <span className="ub-badge indigo" style={{ fontSize: "10px" }}>{upcomingEvents.length} à venir</span>
        </h2>
        <div style={{ display: "flex", gap: "6px", alignItems: "center" }}>
          <div className="ub-cal-view-switch">
            <button
              className={viewMode === "month" ? "active" : ""}
              onClick={() => setViewMode("month")}
              data-testid="cal-view-month"
            >Mois</button>
            <button
              className={viewMode === "list" ? "active" : ""}
              onClick={() => setViewMode("list")}
              data-testid="cal-view-list"
            >Liste</button>
          </div>
          <button
            className="ub-btn-primary"
            onClick={() => { setEditEvent(null); setShowCreate(true); }}
            data-testid="vsi-new-event-btn"
          >
            <Plus size={14} /> Nouveau RDV
          </button>
        </div>
      </div>

      <div className="ub-vsi-agenda-body">
        {viewMode === "month" && (
          <CalendarGrid
            events={events}
            viewMonth={viewMonth}
            onPrev={() => setViewMonth(new Date(viewMonth.getFullYear(), viewMonth.getMonth() - 1, 1))}
            onNext={() => setViewMonth(new Date(viewMonth.getFullYear(), viewMonth.getMonth() + 1, 1))}
            onSelectDay={(d) => setSelectedDay(d)}
            selectedDay={selectedDay}
          />
        )}

        <div className="ub-vsi-events-list" data-testid="vsi-events-list">
          {loading ? (
            <div style={{ textAlign: "center", padding: "30px" }}>
              <Loader2 size={20} className="ub-spin" style={{ color: "var(--ub-primary)" }} />
            </div>
          ) : listEvents.length === 0 ? (
            <div className="ub-search-empty" style={{ padding: "30px 16px" }}>
              <CalendarDays size={28} style={{ color: "var(--ub-text-muted)", opacity: 0.4 }} />
              <p style={{ marginTop: "10px", color: "var(--ub-text-muted)", fontSize: "13px" }}>
                {viewMode === "month"
                  ? `Aucun rendez-vous le ${selectedDay.toLocaleDateString("fr-FR")}`
                  : "Aucun rendez-vous à venir"}
              </p>
              <button
                className="ub-btn-small"
                onClick={() => { setEditEvent(null); setShowCreate(true); }}
                data-testid="vsi-empty-create-btn"
                style={{ marginTop: "12px" }}
              >
                <Plus size={12} /> Programmer un rendez-vous
              </button>
            </div>
          ) : (
            <>
              {listEvents.map(e => {
                const status = computeStatus(e);
                const cd = countdownText(e.start_at);
                const myRsvp = (e.rsvps || {})[myTokenId];
                const isMine = e.created_by === myTokenId;
                return (
                  <div key={e.id} className={`ub-vsi-event-card ${status}`} data-testid={`vsi-event-${e.id}`}>
                    <div className="ub-vsi-event-head">
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <h3 className="ub-vsi-event-title">{e.title}</h3>
                        <p className="ub-vsi-event-meta">
                          <Clock size={11} /> {fmtDateTime(e.start_at)}
                          <span style={{ opacity: 0.5 }}>·</span>
                          <span>{e.duration_min} min</span>
                          {cd && status !== "past" && <span className="ub-badge orange" style={{ fontSize: "10px" }}>{cd}</span>}
                          {status === "live" && <span className="ub-badge green" style={{ fontSize: "10px" }}>● En direct</span>}
                          {status === "past" && <span className="ub-badge" style={{ fontSize: "10px", background: "#e2e8f0", color: "#64748b" }}>Terminé</span>}
                        </p>
                        {e.description && <p className="ub-vsi-event-desc">{e.description}</p>}
                        <p style={{ fontSize: "11px", color: "var(--ub-text-muted)", marginTop: "4px" }}>
                          Créé par <strong>{e.creator_name}</strong>
                        </p>
                      </div>
                      {isMine && (
                        <div style={{ display: "flex", gap: "6px", flexShrink: 0 }}>
                          <button
                            className="ub-icon-btn"
                            onClick={() => { setEditEvent(e); setShowCreate(true); }}
                            title="Modifier"
                            data-testid={`vsi-event-edit-${e.id}`}
                          >
                            <Edit2 size={14} />
                          </button>
                          <button
                            className="ub-icon-btn"
                            onClick={() => deleteEvent(e.id)}
                            title="Annuler"
                            data-testid={`vsi-event-delete-${e.id}`}
                            style={{ color: "#dc2626" }}
                          >
                            <Trash2 size={14} />
                          </button>
                        </div>
                      )}
                    </div>

                    {status !== "past" && (
                      <div className="ub-vsi-event-actions">
                        <div className="ub-vsi-event-rsvp" data-testid={`vsi-rsvp-${e.id}`}>
                          <span className="ub-rsvp-label">Tu participes ?</span>
                          <button
                            className={`ub-rsvp-btn yes${myRsvp === "yes" ? " active" : ""}`}
                            onClick={() => sendRsvp(e.id, "yes")}
                            data-testid={`vsi-rsvp-yes-${e.id}`}
                          >
                            <Check size={11} /> Oui
                          </button>
                          <button
                            className={`ub-rsvp-btn maybe${myRsvp === "maybe" ? " active" : ""}`}
                            onClick={() => sendRsvp(e.id, "maybe")}
                            data-testid={`vsi-rsvp-maybe-${e.id}`}
                          >
                            <HelpCircle size={11} /> Peut-être
                          </button>
                          <button
                            className={`ub-rsvp-btn no${myRsvp === "no" ? " active" : ""}`}
                            onClick={() => sendRsvp(e.id, "no")}
                            data-testid={`vsi-rsvp-no-${e.id}`}
                          >
                            <X size={11} /> Non
                          </button>
                        </div>
                        <button
                          className="ub-btn-primary"
                          onClick={() => onJoinMeeting && onJoinMeeting(e)}
                          data-testid={`vsi-event-join-${e.id}`}
                          disabled={!e.meet_url && status !== "live"}
                          style={{ opacity: (!e.meet_url && status !== "live") ? 0.5 : 1 }}
                        >
                          <Video size={13} /> {status === "live" ? "Rejoindre maintenant" : "Ouvrir le salon"}
                        </button>
                      </div>
                    )}
                  </div>
                );
              })}

              {viewMode === "list" && pastEvents.length > 0 && (
                <details style={{ marginTop: "12px" }}>
                  <summary style={{ cursor: "pointer", fontSize: "12px", color: "var(--ub-text-muted)" }}>
                    <Sparkles size={11} /> Voir les {pastEvents.length} événement{pastEvents.length > 1 ? "s" : ""} passé{pastEvents.length > 1 ? "s" : ""}
                  </summary>
                  <div style={{ marginTop: "8px", display: "flex", flexDirection: "column", gap: "8px" }}>
                    {pastEvents.map(e => (
                      <div key={e.id} className="ub-vsi-event-card past" data-testid={`vsi-past-event-${e.id}`}>
                        <div className="ub-vsi-event-head">
                          <div style={{ flex: 1 }}>
                            <h3 className="ub-vsi-event-title">{e.title}</h3>
                            <p className="ub-vsi-event-meta"><Clock size={11} /> {fmtDateTime(e.start_at)}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </details>
              )}
            </>
          )}
        </div>
      </div>

      {showCreate && (
        <EventModal
          initial={editEvent}
          onClose={() => { setShowCreate(false); setEditEvent(null); }}
          onSave={saveEvent}
          saving={saving}
        />
      )}
    </div>
  );
};

export default VsiGroupAgenda;
export { fmtDateTime, fmtTime, computeStatus, countdownText };
