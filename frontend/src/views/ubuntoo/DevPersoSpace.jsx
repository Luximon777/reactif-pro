import { useState, useEffect, useCallback } from "react";
import {
  Compass, Target, Sparkles, Plus, X, Check, Loader2, RefreshCw,
  CheckCircle, Calendar, Clock, Zap, Heart, BookOpen, Users
} from "lucide-react";
import { toast } from "sonner";

const API = `${process.env.REACT_APP_BACKEND_URL || ""}/api`;

const INTENTION_TAGS = [
  "Équilibre vie pro/perso", "Confiance en moi", "Leadership", "Reconversion",
  "Mieux communiquer", "Gestion du stress", "Créativité", "Apprentissage continu",
  "Mise en réseau", "Engagement collectif", "Authenticité", "Sens & impact",
];

const CATEGORY_ICONS = {
  "Reflexion": BookOpen,
  "Action": Zap,
  "Apprentissage": Sparkles,
  "Lien": Users,
  "Bien-etre": Heart,
};

const DevPersoSpace = ({ token }) => {
  return (
    <div className="ub-devperso-grid ub-stagger" data-testid="devperso-space">
      <DailyAction token={token} />
      <IntentionsCard token={token} />
      <GoalsCard token={token} />
    </div>
  );
};

// ============== INTENTIONS ===============
const IntentionsCard = ({ token }) => {
  const [freeText, setFreeText] = useState("");
  const [tags, setTags] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [dirty, setDirty] = useState(false);

  const load = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API}/devperso/intentions?token=${token}`);
      if (res.ok) {
        const data = await res.json();
        setFreeText(data.free_text || "");
        setTags(data.tags || []);
      }
    } finally { setLoading(false); }
  }, [token]);

  useEffect(() => { load(); }, [load]);

  const toggleTag = (t) => {
    setTags(prev => prev.includes(t) ? prev.filter(x => x !== t) : [...prev, t].slice(0, 12));
    setDirty(true);
  };

  const save = async () => {
    setSaving(true);
    try {
      const res = await fetch(`${API}/devperso/intentions?token=${token}`, {
        method: "PUT", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ free_text: freeText, tags }),
      });
      if (res.ok) { toast.success("Intentions enregistrées"); setDirty(false); }
      else toast.error("Échec de l'enregistrement");
    } finally { setSaving(false); }
  };

  return (
    <div className="ub-profile-card ub-card-hover" data-testid="intentions-card">
      <h3 className="ub-devperso-title">
        <Compass size={16} style={{ color: "var(--ub-primary)" }} />
        Mes intentions
        <span className="ub-badge purple" style={{ fontSize: "10px" }}>Le pourquoi</span>
      </h3>
      <p className="ub-devperso-helper">L'énergie qui guide tes choix au quotidien.</p>

      {loading ? (
        <div style={{ textAlign: "center", padding: "20px" }}>
          <Loader2 size={18} className="ub-spin" />
        </div>
      ) : (
        <>
          <textarea
            className="ub-input"
            rows={3}
            value={freeText}
            onChange={(e) => { setFreeText(e.target.value); setDirty(true); }}
            maxLength={1000}
            placeholder="Ex: Je veux retrouver l'équilibre, oser dire non, créer plus de liens authentiques…"
            data-testid="intentions-free-text"
            style={{ resize: "vertical", fontFamily: "inherit" }}
          />
          <p className="ub-devperso-helper" style={{ marginTop: "10px", marginBottom: "6px" }}>Tags qui te parlent :</p>
          <div className="ub-pill-row" data-testid="intentions-tags">
            {INTENTION_TAGS.map(t => {
              const on = tags.includes(t);
              return (
                <button
                  key={t}
                  className={`ub-intention-tag ${on ? "active" : ""}`}
                  onClick={() => toggleTag(t)}
                  data-testid={`intention-tag-${t}`}
                >
                  {on && <Check size={11} />} {t}
                </button>
              );
            })}
          </div>
          <div style={{ display: "flex", justifyContent: "flex-end", marginTop: "12px" }}>
            <button
              className="ub-btn-primary"
              disabled={!dirty || saving}
              onClick={save}
              data-testid="intentions-save"
            >
              {saving ? <Loader2 size={13} className="ub-spin" /> : <><Check size={13} /> Enregistrer</>}
            </button>
          </div>
        </>
      )}
    </div>
  );
};

// ============== GOALS ===============
const GoalsCard = ({ token }) => {
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ title: "", target: "", metric: "", deadline: "" });
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API}/devperso/goals?token=${token}`);
      if (res.ok) {
        const data = await res.json();
        setGoals(data.goals || []);
      }
    } finally { setLoading(false); }
  }, [token]);

  useEffect(() => { load(); }, [load]);

  const createGoal = async () => {
    if (!form.title.trim()) { toast.error("Titre requis"); return; }
    setSaving(true);
    try {
      const res = await fetch(`${API}/devperso/goals?token=${token}`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      if (res.ok) {
        toast.success("Objectif créé");
        setShowForm(false);
        setForm({ title: "", target: "", metric: "", deadline: "" });
        load();
      } else { toast.error("Échec de la création"); }
    } finally { setSaving(false); }
  };

  const toggleStatus = async (goal) => {
    const next = goal.status === "done" ? "in_progress" : "done";
    await fetch(`${API}/devperso/goals/${goal.id}?token=${token}`, {
      method: "PUT", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: next }),
    });
    if (next === "done") toast.success("🎉 Objectif atteint !");
    load();
  };

  const removeGoal = async (id) => {
    if (!window.confirm("Supprimer cet objectif ?")) return;
    await fetch(`${API}/devperso/goals/${id}?token=${token}`, { method: "DELETE" });
    load();
  };

  return (
    <div className="ub-profile-card ub-card-hover" data-testid="goals-card">
      <h3 className="ub-devperso-title">
        <Target size={16} style={{ color: "var(--ub-secondary)" }} />
        Mes objectifs
        <span className="ub-badge orange" style={{ fontSize: "10px" }}>Le quoi · SMART</span>
      </h3>
      <p className="ub-devperso-helper">Cibles concrètes, mesurables et datées.</p>

      {loading ? (
        <div style={{ textAlign: "center", padding: "20px" }}><Loader2 size={18} className="ub-spin" /></div>
      ) : (
        <>
          {goals.length === 0 ? (
            <p style={{ fontSize: "12px", color: "var(--ub-text-muted)", textAlign: "center", padding: "16px 0" }}>
              Aucun objectif pour l'instant. Crée le premier !
            </p>
          ) : (
            <div className="ub-goal-list">
              {goals.map(g => {
                const done = g.status === "done";
                return (
                  <div key={g.id} className={`ub-goal-row ${done ? "done" : ""}`} data-testid={`goal-${g.id}`}>
                    <button
                      className="ub-goal-check"
                      onClick={() => toggleStatus(g)}
                      data-testid={`goal-toggle-${g.id}`}
                      title={done ? "Marquer comme en cours" : "Marquer comme atteint"}
                    >
                      {done ? <CheckCircle size={18} style={{ color: "#16a34a" }} /> : <span className="ub-circle" />}
                    </button>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <p className="ub-goal-title">{g.title}</p>
                      {(g.target || g.metric || g.deadline) && (
                        <p className="ub-goal-meta">
                          {g.target && <span><Sparkles size={10} /> {g.target}</span>}
                          {g.metric && <span><Zap size={10} /> {g.metric}</span>}
                          {g.deadline && <span><Calendar size={10} /> {g.deadline}</span>}
                        </p>
                      )}
                    </div>
                    <button
                      className="ub-goal-delete"
                      onClick={() => removeGoal(g.id)}
                      data-testid={`goal-del-${g.id}`}
                      title="Supprimer"
                    >
                      <X size={13} />
                    </button>
                  </div>
                );
              })}
            </div>
          )}

          {showForm ? (
            <div className="ub-goal-form" data-testid="goal-form">
              <input className="ub-input" placeholder="Titre (ex: Décrocher un poste de coach)"
                value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })}
                maxLength={200} data-testid="goal-title" />
              <input className="ub-input" placeholder="Cible (ex: 3 entretiens validés)"
                value={form.target} onChange={(e) => setForm({ ...form, target: e.target.value })}
                data-testid="goal-target" />
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "6px" }}>
                <input className="ub-input" placeholder="Métrique"
                  value={form.metric} onChange={(e) => setForm({ ...form, metric: e.target.value })}
                  data-testid="goal-metric" />
                <input type="date" className="ub-input"
                  value={form.deadline} onChange={(e) => setForm({ ...form, deadline: e.target.value })}
                  data-testid="goal-deadline" />
              </div>
              <div style={{ display: "flex", gap: "6px", justifyContent: "flex-end" }}>
                <button className="ub-btn-small" onClick={() => { setShowForm(false); setForm({ title: "", target: "", metric: "", deadline: "" }); }}>
                  Annuler
                </button>
                <button className="ub-btn-primary" disabled={saving || !form.title.trim()} onClick={createGoal} data-testid="goal-create">
                  {saving ? <Loader2 size={12} className="ub-spin" /> : <><Check size={12} /> Créer</>}
                </button>
              </div>
            </div>
          ) : (
            <button className="ub-btn-small" onClick={() => setShowForm(true)} data-testid="goal-add-btn" style={{ marginTop: "12px", width: "100%", justifyContent: "center" }}>
              <Plus size={12} /> Ajouter un objectif
            </button>
          )}
        </>
      )}
    </div>
  );
};

// ============== DAILY ACTION (AI) ===============
const DailyAction = ({ token }) => {
  const [action, setAction] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const res = await fetch(`${API}/devperso/action-today?token=${token}`);
      if (res.ok) setAction(await res.json());
    } finally { setLoading(false); }
  }, [token]);

  useEffect(() => { load(); }, [load]);

  const refresh = async () => {
    setRefreshing(true);
    try {
      const res = await fetch(`${API}/devperso/action-today/refresh?token=${token}`, { method: "POST" });
      if (res.ok) { setAction(await res.json()); toast.success("Nouvelle suggestion générée"); }
      else toast.error("Impossible de régénérer");
    } finally { setRefreshing(false); }
  };

  const markStatus = async (status) => {
    if (!action) return;
    await fetch(`${API}/devperso/actions/${action.id}/status?token=${token}`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status }),
    });
    setAction({ ...action, status });
    toast.success(status === "completed" ? "Bravo ! Action validée 🎉" : "Action passée");
  };

  const Icon = action ? (CATEGORY_ICONS[action.category] || Sparkles) : Sparkles;

  return (
    <div className="ub-profile-card ub-daily-action" data-testid="daily-action">
      <div className="ub-daily-head">
        <h3 className="ub-devperso-title" style={{ margin: 0 }}>
          <Icon size={16} style={{ color: "var(--ub-gold-dark)" }} />
          Action du jour
          <span className="ub-badge gold" style={{ fontSize: "10px" }}>Coach IA</span>
        </h3>
        <button
          className="ub-icon-btn"
          onClick={refresh}
          disabled={refreshing}
          data-testid="daily-action-refresh"
          title="Suggère-moi autre chose"
        >
          {refreshing ? <Loader2 size={14} className="ub-spin" /> : <RefreshCw size={14} />}
        </button>
      </div>

      {loading ? (
        <div style={{ textAlign: "center", padding: "30px" }}>
          <Loader2 size={20} className="ub-spin" style={{ color: "var(--ub-primary)" }} />
          <p style={{ fontSize: "12px", color: "var(--ub-text-muted)", marginTop: "8px" }}>
            Le coach prépare ta suggestion…
          </p>
        </div>
      ) : !action ? (
        <p style={{ fontSize: "12px", color: "var(--ub-text-muted)", textAlign: "center", padding: "16px" }}>
          Aucune suggestion disponible pour le moment.
        </p>
      ) : (
        <>
          <h4 className="ub-daily-title">{action.title}</h4>
          <p className="ub-daily-desc">{action.description}</p>
          <div className="ub-daily-meta">
            <span><Clock size={11} /> ~ {action.duration_min} min</span>
            {action.category && <span className="ub-badge indigo" style={{ fontSize: "10px" }}>{action.category}</span>}
            {action.linked_to && <span style={{ fontStyle: "italic" }}>→ {action.linked_to}</span>}
          </div>
          {action.status === "completed" ? (
            <div className="ub-daily-done" data-testid="daily-action-done">
              <CheckCircle size={14} /> Réalisée — bravo !
            </div>
          ) : (
            <div style={{ display: "flex", gap: "6px", marginTop: "12px" }}>
              <button className="ub-btn-primary" style={{ flex: 1, justifyContent: "center" }}
                onClick={() => markStatus("completed")} data-testid="daily-action-done-btn">
                <CheckCircle size={13} /> Je l'ai faite
              </button>
              <button className="ub-btn-small" onClick={() => markStatus("skipped")} data-testid="daily-action-skip-btn">
                Passer
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default DevPersoSpace;
