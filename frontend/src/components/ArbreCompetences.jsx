import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Loader2, Plus, X, Save, Sparkles } from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL + "/api";

const LEVELS = [
  { key: "vertus", num: "1", label: "VERTUS", sub: "Racines", action: "À libérer", lien: "Potentiel", bg: "#3a2817", text: "#f3e9dc", pos: { left: "58%", top: "81%", width: "26%" } },
  { key: "valeurs", num: "2", label: "VALEURS", sub: "Tronc", action: "À préserver", lien: "Tuteur", bg: "#c2cc6b", text: "#3d4b1e", pos: { left: "26%", top: "48%", width: "20%" } },
  { key: "qualites", num: "3", label: "QUALITÉS HUMAINES", sub: "Branches", action: "À entretenir", lien: "Apprentissage", bg: "#98b849", text: "#ffffff", pos: { left: "79%", top: "25%", width: "22%" } },
  { key: "savoir_etre", num: "4", label: "SAVOIR-ÊTRE PRO.", sub: "Brindilles", action: "À raffiner", lien: "Apprentissage · Capacités", bg: "#79a83d", text: "#ffffff", pos: { left: "21%", top: "25%", width: "22%" } },
  { key: "savoir_faire", num: "5", label: "SAVOIR-FAIRE", sub: "Feuilles", action: "À renouveler", lien: "Formation · Capacités", bg: "#4e8b2f", text: "#ffffff", pos: { left: "50%", top: "15%", width: "27%" } },
];

const EMPTY_LEVELS = { savoir_faire: [], savoir_etre: [], qualites: [], valeurs: [], vertus: [] };

const DECOR_LEAVES = [
  [8, 6, -20], [16, 3, 30], [30, 8, 10], [70, 4, -35], [84, 7, 15], [92, 12, 40],
  [5, 30, 25], [95, 32, -15], [10, 46, -30], [90, 48, 20], [40, 4, -10], [60, 6, 25],
];

export const ArbreCompetences = ({ token }) => {
  const [levels, setLevels] = useState(EMPTY_LEVELS);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editing, setEditing] = useState(null);
  const [newItem, setNewItem] = useState("");
  const [dirty, setDirty] = useState(false);

  const load = useCallback(async (prefill = 0) => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/passport/arbre?token=${token}&prefill=${prefill}`);
      setLevels({ ...EMPTY_LEVELS, ...res.data.levels });
      setDirty(prefill === 1);
      if (prefill) toast.success("Arbre pré-rempli depuis votre profil — pensez à enregistrer");
    } catch {
      toast.error("Erreur de chargement de l'arbre");
    }
    setLoading(false);
  }, [token]);

  useEffect(() => { if (token) load(); }, [token, load]);

  const save = async () => {
    setSaving(true);
    try {
      await axios.post(`${API}/passport/arbre?token=${token}`, { levels });
      setDirty(false);
      toast.success("Votre arbre des compétences est enregistré");
    } catch {
      toast.error("Erreur lors de l'enregistrement");
    }
    setSaving(false);
  };

  const addItem = (key) => {
    const v = newItem.trim();
    if (!v) return;
    if ((levels[key] || []).some((x) => x.toLowerCase() === v.toLowerCase())) {
      toast.info("Déjà présent dans ce niveau");
      return;
    }
    setLevels((prev) => ({ ...prev, [key]: [...(prev[key] || []), v] }));
    setNewItem("");
    setDirty(true);
  };

  const removeItem = (key, idx) => {
    setLevels((prev) => ({ ...prev, [key]: prev[key].filter((_, i) => i !== idx) }));
    setDirty(true);
  };

  const editingLevel = LEVELS.find((l) => l.key === editing);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16" data-testid="arbre-loading">
        <Loader2 className="w-8 h-8 text-[#1e3a5f] animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-4" data-testid="arbre-competences">
      {/* Actions */}
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-xs text-slate-500">Cliquez sur une bulle pour compléter le niveau correspondant.</p>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => load(1)} data-testid="arbre-prefill-btn">
            <Sparkles className="w-3.5 h-3.5 mr-1.5" />Pré-remplir depuis mon profil
          </Button>
          <Button size="sm" className="bg-[#1e3a5f] hover:bg-[#152a45] text-white" onClick={save} disabled={saving || !dirty} data-testid="arbre-save-btn">
            {saving ? <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" /> : <Save className="w-3.5 h-3.5 mr-1.5" />}
            Enregistrer
          </Button>
        </div>
      </div>

      {/* Légende + Arbre + résumé de progression */}
      <div className="grid grid-cols-1 lg:grid-cols-[260px_1fr_300px] gap-4 items-start">

      {/* Légende des liens (gauche) */}
      <aside className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm space-y-3 lg:sticky lg:top-4 order-2 lg:order-none" data-testid="arbre-legende">
        <div>
          <h4 className="text-sm font-bold text-[#1e3a5f]">Comprendre l'arbre</h4>
          <p className="text-[11px] text-slate-500">Ce qui nourrit et soutient vos compétences</p>
        </div>
        <p className="text-xs text-slate-600 border-l-2 border-[#4e8b2f] pl-2"><span className="font-bold text-[#4e8b2f]">Formation</span> — nourrit et renouvelle vos <strong>savoir-faire</strong> (5 · feuilles)</p>
        <p className="text-xs text-slate-600 border-l-2 border-[#79a83d] pl-2"><span className="font-bold text-[#79a83d]">Apprentissage</span> — l'expérience façonne vos <strong>savoir-être pro.</strong> et <strong>qualités humaines</strong> (4 · 3)</p>
        <p className="text-xs text-slate-600 border-l-2 border-[#98b849] pl-2"><span className="font-bold text-[#98b849]">Capacités</span> — la partie visible de l'arbre : ce que vous exprimez au quotidien (3 à 5)</p>
        <p className="text-xs text-slate-600 border-l-2 border-[#3d4b1e] pl-2"><span className="font-bold text-[#3d4b1e]">Tuteur</span> — le soutien (coach, mentor, réseau) qui aide l'arbre à grandir droit et préserve vos <strong>valeurs</strong> (2 · tronc)</p>
        <p className="text-xs text-slate-600 border-l-2 border-[#3a2817] pl-2"><span className="font-bold text-[#3a2817]">Potentiel</span> — vos <strong>vertus</strong> (1 · racines), invisibles mais fondatrices : tout part d'elles, à libérer</p>
      </aside>

      {/* Infographic tree */}
      <div className="relative w-full max-w-3xl mx-auto rounded-2xl overflow-hidden shadow-lg order-1 lg:order-none" style={{ aspectRatio: "9/10" }} data-testid="arbre-visuel">
        {/* Background + flat tree (SVG) */}
        <svg viewBox="0 0 900 1000" preserveAspectRatio="none" className="absolute inset-0 w-full h-full">
          <defs>
            <pattern id="soilDots" width="60" height="50" patternUnits="userSpaceOnUse">
              <ellipse cx="14" cy="12" rx="7" ry="4" fill="#5d3f24" opacity="0.6" />
              <ellipse cx="44" cy="34" rx="6" ry="3.5" fill="#5d3f24" opacity="0.5" />
              <ellipse cx="30" cy="44" rx="4" ry="2.5" fill="#7a5533" opacity="0.5" />
            </pattern>
          </defs>
          {/* Sky */}
          <rect x="0" y="0" width="900" height="590" fill="#f0f3e4" />
          {/* Foliage cluster behind bubbles */}
          <circle cx="450" cy="190" r="180" fill="#a5c95e" opacity="0.55" />
          <circle cx="260" cy="250" r="120" fill="#8bbc4a" opacity="0.5" />
          <circle cx="650" cy="250" r="120" fill="#b7d276" opacity="0.5" />
          <circle cx="450" cy="320" r="110" fill="#96c257" opacity="0.45" />
          {/* Trunk + branches */}
          <path d="M430,600 L436,420 Q438,360 430,310 L450,300 Q462,360 462,420 L470,600 Z" fill="#7a4a21" />
          <path d="M436,420 Q360,330 250,290 L258,272 Q370,310 442,392 Z" fill="#7a4a21" />
          <path d="M458,420 Q540,330 648,290 L640,272 Q530,310 452,392 Z" fill="#7a4a21" />
          <path d="M438,470 Q380,450 320,455 L322,438 Q384,432 440,452 Z" fill="#8a5527" />
          {/* Hill */}
          <path d="M0,585 Q450,520 900,585 L900,620 L0,620 Z" fill="#7fae3f" />
          {/* Soil */}
          <rect x="0" y="605" width="900" height="395" fill="#6b4a2b" />
          <rect x="0" y="605" width="900" height="395" fill="url(#soilDots)" />
          {/* Roots */}
          <path d="M430,600 Q420,680 330,720 L336,736 Q430,700 446,620 Z" fill="#4a3018" />
          <path d="M470,600 Q490,700 540,760 L524,772 Q468,706 452,620 Z" fill="#4a3018" />
          <path d="M450,610 Q452,720 500,800 L484,808 Q440,724 436,614 Z" fill="#3f2914" />
          <path d="M440,605 Q360,660 250,672 L252,688 Q368,678 450,622 Z" fill="#4a3018" />
          <path d="M460,605 Q580,660 680,668 L678,684 Q572,678 450,622 Z" fill="#4a3018" />
          {/* Falling leaves */}
          {DECOR_LEAVES.map(([x, y, r], i) => (
            <ellipse key={i} cx={x * 9} cy={y * 10} rx="9" ry="4.5" fill={i % 2 ? "#9ab54a" : "#c6d648"} opacity="0.8" transform={`rotate(${r} ${x * 9} ${y * 10})`} />
          ))}
        </svg>

        {/* Concept rails (comme le schéma de référence) */}
        <div className="absolute left-1 sm:left-2 z-10 pointer-events-none flex items-center" style={{ top: "6%", height: "18%" }} data-testid="arbre-rail-formation">
          <span className="text-[8px] sm:text-[10px] font-bold tracking-widest text-[#4e6b2f] bg-white/60 rounded-full px-0.5 py-2 backdrop-blur-[1px]" style={{ writingMode: "vertical-rl", transform: "rotate(180deg)" }}>FORMATION</span>
        </div>
        <div className="absolute left-1 sm:left-2 z-10 pointer-events-none flex items-center" style={{ top: "27%", height: "30%" }} data-testid="arbre-rail-apprentissage">
          <span className="text-[8px] sm:text-[10px] font-bold tracking-widest text-[#4e6b2f] bg-white/60 rounded-full px-0.5 py-2 backdrop-blur-[1px]" style={{ writingMode: "vertical-rl", transform: "rotate(180deg)" }}>APPRENTISSAGE</span>
        </div>
        <div className="absolute right-1 sm:right-2 z-10 pointer-events-none flex items-center" style={{ top: "8%", height: "48%" }} data-testid="arbre-rail-tuteur">
          <span className="text-[8px] sm:text-[10px] font-bold tracking-widest text-[#4e6b2f] bg-white/60 rounded-full px-0.5 py-2 backdrop-blur-[1px]" style={{ writingMode: "vertical-rl" }}>TUTEUR</span>
        </div>
        <div className="absolute left-1/2 -translate-x-1/2 z-10 pointer-events-none" style={{ top: "1.5%" }} data-testid="arbre-rail-capacites">
          <span className="text-[8px] sm:text-[10px] font-bold tracking-widest text-[#3d4b1e] bg-white/70 px-2.5 py-0.5 rounded-full backdrop-blur-[1px]">CAPACITÉS</span>
        </div>
        <div className="absolute left-1/2 -translate-x-1/2 z-10 pointer-events-none" style={{ bottom: "2%" }} data-testid="arbre-rail-potentiel">
          <span className="text-[8px] sm:text-[10px] font-bold tracking-widest text-[#f3e9dc] bg-black/30 px-2.5 py-0.5 rounded-full backdrop-blur-[1px]">POTENTIEL</span>
        </div>

        {/* Level bubbles */}
        {LEVELS.map((lvl) => {
          const items = levels[lvl.key] || [];
          const isActive = editing === lvl.key;
          return (
            <div
              key={lvl.key}
              role="button"
              tabIndex={0}
              onClick={() => { setEditing(isActive ? null : lvl.key); setNewItem(""); }}
              className={`absolute rounded-full flex flex-col items-center justify-center text-center cursor-pointer shadow-xl transition-transform duration-200 hover:scale-105 ${isActive ? "ring-4 ring-amber-300" : ""}`}
              style={{
                left: lvl.pos.left, top: lvl.pos.top, width: lvl.pos.width,
                aspectRatio: "1/1", transform: "translate(-50%, -50%)",
                backgroundColor: lvl.bg, color: lvl.text,
              }}
              data-testid={`arbre-bulle-${lvl.key}`}
            >
              <div className="px-3 sm:px-4">
                <p className="text-[13px] sm:text-lg font-black opacity-80 leading-none" style={{ fontFamily: "Outfit, sans-serif" }}>{lvl.num}</p>
                <p className="text-[9px] sm:text-xs font-bold tracking-wide leading-tight mt-0.5">{lvl.label}</p>
                {lvl.sub && <p className="text-[7px] sm:text-[9px] italic opacity-80">{lvl.sub} — {lvl.action}</p>}
                <div className="mt-1 space-y-0 leading-tight">
                  {items.slice(0, 3).map((it, i) => (
                    <p key={i} className="text-[7px] sm:text-[9px] opacity-90 truncate max-w-[110px] sm:max-w-[150px] mx-auto">• {it}</p>
                  ))}
                  {items.length > 3 && <p className="text-[7px] sm:text-[9px] font-bold opacity-80">+{items.length - 3} autres</p>}
                  {items.length === 0 && <p className="text-[7px] sm:text-[9px] italic opacity-70">Cliquez pour remplir</p>}
                </div>
                <p className="text-[6px] sm:text-[8px] uppercase tracking-wider opacity-70 mt-1">{lvl.lien}</p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Résumé de progression : des vertus vers les savoir-faire */}
      <aside className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm lg:sticky lg:top-4 order-3 lg:order-none" data-testid="arbre-resume">
        <h4 className="text-sm font-bold text-[#1e3a5f]">Votre progression</h4>
        <p className="text-[11px] text-slate-500 mb-3">Des vertus (racines) vers les savoir-faire (feuilles)</p>

        {/* Barre globale */}
        {(() => {
          const filled = LEVELS.filter((l) => (levels[l.key] || []).length > 0).length;
          return (
            <div className="mb-4" data-testid="arbre-resume-global">
              <div className="flex items-center justify-between text-[11px] text-slate-600 mb-1">
                <span>Niveaux complétés</span>
                <span className="font-bold">{filled}/5</span>
              </div>
              <div className="h-2 rounded-full bg-slate-100 overflow-hidden">
                <div className="h-full rounded-full bg-gradient-to-r from-[#3a2817] via-[#98b849] to-[#4e8b2f] transition-all duration-500" style={{ width: `${(filled / 5) * 100}%` }} />
              </div>
            </div>
          );
        })()}

        {/* Étapes 1 → 5 */}
        <div className="space-y-0">
          {LEVELS.map((lvl, idx) => {
            const items = levels[lvl.key] || [];
            const done = items.length > 0;
            return (
              <div key={lvl.key} className="relative pl-8 pb-3 last:pb-0" data-testid={`arbre-resume-step-${lvl.key}`}>
                {idx < LEVELS.length - 1 && <span className="absolute left-[13px] top-7 bottom-0 w-0.5 bg-slate-200" aria-hidden="true" />}
                <button
                  onClick={() => { setEditing(lvl.key); setNewItem(""); }}
                  className="absolute left-0 top-0.5 w-[27px] h-[27px] rounded-full flex items-center justify-center text-[11px] font-black shadow-sm transition-transform hover:scale-110"
                  style={{ backgroundColor: done ? lvl.bg : "#e2e8f0", color: done ? lvl.text : "#94a3b8" }}
                  title={`Compléter : ${lvl.label}`}
                >
                  {lvl.num}
                </button>
                <div className="flex items-center justify-between gap-2">
                  <p className={`text-xs font-bold ${done ? "text-slate-800" : "text-slate-400"}`}>{lvl.label}</p>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-semibold ${done ? "bg-emerald-50 text-emerald-700 border border-emerald-200" : "bg-slate-50 text-slate-400 border border-slate-200"}`}>
                    {items.length}
                  </span>
                </div>
                <p className="text-[10px] text-slate-400 italic">{lvl.sub} — {lvl.action}</p>
                {items.length > 0 && (
                  <p className="text-[10px] text-slate-500 truncate">{items.slice(0, 2).join(", ")}{items.length > 2 ? "…" : ""}</p>
                )}
              </div>
            );
          })}
        </div>

        {/* Citation */}
        <blockquote className="mt-4 border-l-4 border-[#4e8b2f] bg-[#f0f3e4] rounded-r-lg px-3 py-2.5" data-testid="arbre-citation">
          <p className="text-xs italic text-slate-700 leading-relaxed">« Transmettre le fruit de votre travail constitue le sens même de la noblesse. »</p>
          <footer className="text-[10px] font-semibold text-[#4e6b2f] mt-1">— C.K. Luximon</footer>
        </blockquote>
      </aside>
      </div>

      {/* Edit panel */}
      {editingLevel && (
        <div className="max-w-3xl mx-auto rounded-xl border-2 p-4 space-y-3 bg-white shadow-sm" style={{ borderColor: editingLevel.bg }} data-testid="arbre-edit-panel">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-black" style={{ backgroundColor: editingLevel.bg, color: editingLevel.text }}>{editingLevel.num}</span>
              <div>
                <h4 className="text-sm font-bold text-slate-900">{editingLevel.label}</h4>
                <p className="text-[11px] text-slate-500">{editingLevel.action}</p>
              </div>
            </div>
            <Button variant="ghost" size="sm" onClick={() => setEditing(null)} data-testid="arbre-edit-close">
              <X className="w-4 h-4" />
            </Button>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {(levels[editingLevel.key] || []).map((it, i) => (
              <span key={i} className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-slate-100 text-slate-700 border border-slate-200" data-testid={`arbre-item-${editingLevel.key}-${i}`}>
                {it}
                <button onClick={() => removeItem(editingLevel.key, i)} className="text-slate-400 hover:text-red-500" data-testid={`arbre-remove-${editingLevel.key}-${i}`}>
                  <X className="w-3 h-3" />
                </button>
              </span>
            ))}
            {(levels[editingLevel.key] || []).length === 0 && (
              <p className="text-xs text-slate-400 italic">Aucun élément — ajoutez le vôtre ci-dessous ou utilisez « Pré-remplir depuis mon profil ».</p>
            )}
          </div>
          <div className="flex gap-2">
            <Input
              value={newItem}
              onChange={(e) => setNewItem(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") addItem(editingLevel.key); }}
              placeholder={`Ajouter un élément (ex: ${editingLevel.key === "vertus" ? "Courage, Sagesse..." : editingLevel.key === "valeurs" ? "Bienveillance, Autonomie..." : editingLevel.key === "qualites" ? "Patience, Rigueur..." : editingLevel.key === "savoir_etre" ? "Écoute active, Adaptabilité..." : "Conduite d'entretien, Excel..."})`}
              className="text-sm"
              data-testid="arbre-add-input"
            />
            <Button size="sm" onClick={() => addItem(editingLevel.key)} className="bg-[#1e3a5f] hover:bg-[#152a45] text-white shrink-0" data-testid="arbre-add-btn">
              <Plus className="w-4 h-4" />
            </Button>
          </div>
          {dirty && (
            <div className="flex justify-end">
              <Button size="sm" className="bg-[#1e3a5f] hover:bg-[#152a45] text-white" onClick={save} disabled={saving} data-testid="arbre-save-btn-panel">
                {saving ? <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" /> : <Save className="w-3.5 h-3.5 mr-1.5" />}
                Enregistrer mon arbre
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
