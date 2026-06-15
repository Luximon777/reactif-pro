import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  RefreshCw, Clock, CheckCircle2, ArrowRight,
  Loader2, Calendar, Briefcase, ChevronDown, ChevronUp
} from "lucide-react";
import { toast } from "sonner";

const ActualisationOPC = ({ token, filieres = [] }) => {
  const [status, setStatus] = useState(null);
  const [updating, setUpdating] = useState(false);
  const [scope, setScope] = useState("all");
  const [selectedFiliere, setSelectedFiliere] = useState("");
  const [metierNom, setMetierNom] = useState("");
  const [result, setResult] = useState(null);
  const [cooldown, setCooldown] = useState(0);
  const [expanded, setExpanded] = useState(false);

  const loadStatus = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/referentiel/actualisation/status`);
      setStatus(res.data);
      if (res.data.cooldown_remaining_seconds > 0) {
        setCooldown(res.data.cooldown_remaining_seconds);
      }
    } catch { /* silent */ }
  }, []);

  useEffect(() => { loadStatus(); }, [loadStatus]);

  useEffect(() => {
    if (cooldown <= 0) return;
    const timer = setInterval(() => {
      setCooldown(prev => {
        if (prev <= 1) { clearInterval(timer); loadStatus(); return 0; }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [cooldown, loadStatus]);

  const formatCooldown = (seconds) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    if (h > 0) return `${h}h ${m.toString().padStart(2, "0")}min`;
    if (m > 0) return `${m}min ${s.toString().padStart(2, "0")}s`;
    return `${s}s`;
  };

  const formatDate = (isoStr) => {
    if (!isoStr) return "—";
    try {
      const d = new Date(isoStr);
      return d.toLocaleDateString("fr-FR", { day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" });
    } catch { return isoStr; }
  };

  const handleActualiser = async () => {
    if (updating) return;
    setUpdating(true);
    setResult(null);
    try {
      const body = { scope };
      if (scope === "filiere" && selectedFiliere) body.filiere_code = selectedFiliere;
      if (scope === "metier" && metierNom.trim()) body.metier_nom = metierNom.trim();
      const res = await axios.post(`${API}/referentiel/actualiser`, body, { timeout: 300000 });
      if (res.data.error) {
        toast.error(res.data.error);
        if (res.data.cooldown_remaining) setCooldown(res.data.cooldown_remaining);
      } else {
        setResult(res.data);
        toast.success(`Actualisation terminée : ${res.data.changes_count} modification(s)`);
        loadStatus();
      }
    } catch {
      toast.error("Erreur lors de l'actualisation");
    }
    setUpdating(false);
  };

  const urgenceColor = (level) => {
    const m = { fort: "bg-red-100 text-red-700 border-red-200", moyen: "bg-amber-100 text-amber-700 border-amber-200", faible: "bg-blue-100 text-blue-700 border-blue-200" };
    return m[level] || "bg-slate-100 text-slate-600 border-slate-200";
  };

  const typeLabel = (type) => {
    const labels = { intitule: "Intitulé", competences_ajoutees: "+ Compétences", competences_obsoletes: "Obsolètes", savoir_faire_ajoutes: "+ SF", descriptif_mis_a_jour: "Descriptif" };
    return labels[type] || type;
  };

  const lastDate = status?.last_actualisation?.completed_at;
  const canUpdate = status?.can_update !== false && !updating;
  const lastChanges = status?.last_actualisation?.changes || [];

  return (
    <div className="shrink-0 min-w-[260px] max-w-[340px]" data-testid="actualisation-opc">
      {/* Compact header — always visible in top-right */}
      <div
        className="bg-white/10 backdrop-blur-sm border border-white/15 rounded-xl px-3.5 py-2.5 cursor-pointer hover:bg-white/15 transition"
        onClick={() => setExpanded(!expanded)}
        data-testid="actualisation-toggle"
      >
        <div className="flex items-center justify-between gap-2 mb-1">
          <div className="flex items-center gap-1.5">
            <RefreshCw className="w-3.5 h-3.5 text-violet-300" />
            <span className="text-[11px] font-semibold text-white">Actualisation IA</span>
          </div>
          {expanded ? <ChevronUp className="w-3.5 h-3.5 text-violet-300" /> : <ChevronDown className="w-3.5 h-3.5 text-violet-300" />}
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <div className="flex items-center gap-1 text-[9px] text-violet-200">
            <Calendar className="w-2.5 h-2.5" />
            {lastDate ? formatDate(lastDate) : "Jamais"}
          </div>
          {cooldown > 0 && (
            <div className="flex items-center gap-1 text-[9px] text-amber-300">
              <Clock className="w-2.5 h-2.5" />
              {formatCooldown(cooldown)}
            </div>
          )}
        </div>
        {lastChanges.length > 0 && (
          <div className="mt-1">
            <Badge className="bg-violet-400/20 text-violet-200 border-violet-400/30 text-[8px]">
              {status?.last_actualisation?.summary}
            </Badge>
          </div>
        )}
      </div>

      {/* Expanded dropdown panel */}
      {expanded && (
        <Card className="mt-1.5 border-white/20 bg-white shadow-2xl shadow-black/20 rounded-xl absolute right-6 z-50 w-[400px]" data-testid="actualisation-panel">
          <CardContent className="p-4 space-y-3">
            {/* Scope + Button */}
            <div className="grid grid-cols-[1fr_auto] gap-2 items-end">
              <div>
                <label className="text-[10px] text-slate-500 mb-1 block">Portée de l'actualisation</label>
                <Select value={scope} onValueChange={setScope}>
                  <SelectTrigger className="h-8 text-xs"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Tous les métiers (207)</SelectItem>
                    <SelectItem value="filiere">Par filière</SelectItem>
                    <SelectItem value="metier">Par métier</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button
                size="sm"
                className="h-8 text-xs bg-indigo-600 hover:bg-indigo-700"
                onClick={(e) => { e.stopPropagation(); handleActualiser(); }}
                disabled={!canUpdate || (scope === "filiere" && !selectedFiliere) || (scope === "metier" && !metierNom.trim())}
                data-testid="actualiser-btn"
              >
                {updating ? (
                  <><Loader2 className="w-3 h-3 animate-spin mr-1" />En cours...</>
                ) : cooldown > 0 ? (
                  <><Clock className="w-3 h-3 mr-1" />{formatCooldown(cooldown)}</>
                ) : (
                  <><RefreshCw className="w-3 h-3 mr-1" />Actualiser</>
                )}
              </Button>
            </div>

            {scope === "filiere" && (
              <Select value={selectedFiliere} onValueChange={setSelectedFiliere}>
                <SelectTrigger className="h-8 text-xs"><SelectValue placeholder="Choisir une filière..." /></SelectTrigger>
                <SelectContent>{filieres.map(f => <SelectItem key={f.code} value={f.code}>{f.nom}</SelectItem>)}</SelectContent>
              </Select>
            )}
            {scope === "metier" && (
              <input
                type="text" value={metierNom} onChange={e => setMetierNom(e.target.value)}
                placeholder="Ex: Cariste, Chef cuisinier..."
                className="h-8 w-full text-xs border border-slate-200 rounded-lg px-2 focus:outline-none focus:ring-2 focus:ring-indigo-200"
                data-testid="metier-input"
              />
            )}

            {/* Result */}
            {result && (
              <div className="space-y-2" data-testid="actualisation-result">
                <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-200 rounded-lg px-3 py-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                  <div>
                    <p className="text-[10px] font-semibold text-emerald-800">{result.summary}</p>
                    <p className="text-[9px] text-emerald-600">{formatDate(result.completed_at)}</p>
                  </div>
                </div>
                {result.changes?.map((ch, i) => (
                  <div key={i} className="bg-slate-50 rounded-lg border p-2 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-semibold text-slate-800 flex items-center gap-1">
                        <Briefcase className="w-3 h-3 text-indigo-500" />{ch.metier}
                      </span>
                      <Badge className={`text-[7px] border ${urgenceColor(ch.niveau_urgence)}`}>{ch.niveau_urgence}</Badge>
                    </div>
                    {ch.modifications?.map((mod, j) => (
                      <div key={j} className="ml-4 text-[9px] text-slate-600">
                        {mod.type === "intitule" && (
                          <span className="flex items-center gap-1 flex-wrap">
                            <Badge variant="outline" className="text-[7px] text-rose-600 border-rose-200">Intitulé</Badge>
                            <span className="line-through text-slate-400">{mod.ancien}</span>
                            <ArrowRight className="w-2.5 h-2.5 text-slate-400" />
                            <span className="font-semibold text-indigo-700">{mod.nouveau}</span>
                          </span>
                        )}
                        {mod.type === "competences_ajoutees" && (
                          <div className="flex flex-wrap gap-1 items-center">
                            <Badge variant="outline" className="text-[7px] text-emerald-600 border-emerald-200">+ CT</Badge>
                            {mod.ajouts.map((a, k) => <span key={k} className="bg-emerald-50 text-emerald-700 px-1 py-0.5 rounded text-[8px]">{a}</span>)}
                          </div>
                        )}
                        {mod.type === "competences_obsoletes" && (
                          <div className="flex flex-wrap gap-1 items-center">
                            <Badge variant="outline" className="text-[7px] text-amber-600 border-amber-200">Obsolètes</Badge>
                            {mod.obsoletes.map((a, k) => <span key={k} className="text-amber-600 line-through text-[8px]">{a}</span>)}
                          </div>
                        )}
                        {mod.type === "savoir_faire_ajoutes" && (
                          <div className="flex flex-wrap gap-1 items-center">
                            <Badge variant="outline" className="text-[7px] text-blue-600 border-blue-200">+ SF</Badge>
                            {mod.ajouts.map((a, k) => <span key={k} className="bg-blue-50 text-blue-700 px-1 py-0.5 rounded text-[8px]">{a}</span>)}
                          </div>
                        )}
                        {mod.type === "descriptif_mis_a_jour" && (
                          <span className="flex items-start gap-1">
                            <Badge variant="outline" className="text-[7px] text-violet-600 border-violet-200 shrink-0">Desc.</Badge>
                            <span className="italic text-slate-500">{mod.nouveau}</span>
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                ))}
                {result.changes?.length === 0 && (
                  <p className="text-[10px] text-slate-500 text-center py-1">Base à jour — aucune modification</p>
                )}
              </div>
            )}

            {/* Previous changes */}
            {!result && lastChanges.length > 0 && (
              <div className="space-y-1.5">
                <p className="text-[9px] font-semibold text-slate-400 uppercase">Dernières modifications</p>
                {lastChanges.slice(0, 4).map((ch, i) => (
                  <div key={i} className="bg-slate-50 rounded border px-2 py-1.5 text-[9px] flex items-center gap-1.5">
                    <Briefcase className="w-3 h-3 text-indigo-400 shrink-0" />
                    <span className="font-medium text-slate-700">{ch.metier}</span>
                    <Badge className={`text-[7px] border ${urgenceColor(ch.niveau_urgence)}`}>{ch.niveau_urgence}</Badge>
                    <span className="text-slate-400 ml-auto">{ch.modifications?.map(m => typeLabel(m.type)).join(", ")}</span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default ActualisationOPC;
