import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Users, GitBranch, AlertTriangle, Zap, ChevronRight, Shield, TrendingUp, Loader2 } from "lucide-react";
import { toast } from "sonner";

const STAGES = [
  { key: "en_poste", label: "En poste stable", color: "bg-emerald-50 border-emerald-200 text-emerald-700", dotColor: "bg-emerald-500" },
  { key: "en_reflexion", label: "En réflexion", color: "bg-amber-50 border-amber-200 text-amber-700", dotColor: "bg-amber-500" },
  { key: "en_transition", label: "En transition active", color: "bg-blue-50 border-blue-200 text-blue-700", dotColor: "bg-blue-500" },
  { key: "en_reclassement", label: "En reclassement", color: "bg-red-50 border-red-200 text-red-700", dotColor: "bg-red-500" },
  { key: "sorti", label: "Sorti", color: "bg-slate-50 border-slate-200 text-slate-600", dotColor: "bg-slate-400" },
];
const RISK_BADGE = { faible: "bg-emerald-100 text-emerald-700", moyen: "bg-amber-100 text-amber-700", eleve: "bg-orange-100 text-orange-700", critique: "bg-red-100 text-red-700" };
const PARCOURS_BADGE = { mobilite_interne: "bg-amber-100 text-amber-700", pse_reclassement: "bg-red-100 text-red-700", depart_volontaire: "bg-purple-100 text-purple-700", autre: "bg-slate-100 text-slate-600" };

const ParcoursPipeline = ({ token, onRefresh, onNavigate }) => {
  const [collabs, setCollabs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    axios.get(`${API}/entreprise/collaborateurs?token=${token}`)
      .then(r => setCollabs(r.data)).catch(() => {}).finally(() => setLoading(false));
  }, [token]);

  const updateStage = async (id, stage) => {
    try {
      await axios.put(`${API}/entreprise/collaborateurs/${id}?token=${token}`, { stage });
      toast.success("Étape mise à jour");
      const r = await axios.get(`${API}/entreprise/collaborateurs?token=${token}`);
      setCollabs(r.data); onRefresh();
    } catch { toast.error("Erreur"); }
  };

  const filtered = filter === "all" ? collabs :
    filter === "mobilite" ? collabs.filter(c => c.parcours_type === "mobilite_interne") :
    filter === "pse" ? collabs.filter(c => c.parcours_type === "pse_reclassement") : collabs;

  if (loading) return <div className="flex justify-center py-20"><Loader2 className="w-8 h-8 animate-spin text-emerald-600" /></div>;

  return (
    <div className="space-y-6" data-testid="parcours-pipeline">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>Parcours & Transitions</h1>
          <p className="text-sm text-slate-500">Pipeline des trajectoires professionnelles</p>
        </div>
        <div className="flex gap-2">
          <Button variant={filter === "all" ? "default" : "outline"} size="sm" className={filter === "all" ? "bg-emerald-600" : ""} onClick={() => setFilter("all")}>Tous ({collabs.length})</Button>
          <Button variant={filter === "mobilite" ? "default" : "outline"} size="sm" className={filter === "mobilite" ? "bg-amber-600" : ""} onClick={() => setFilter("mobilite")} data-testid="filter-mobilite">
            <GitBranch className="w-3.5 h-3.5 mr-1" />Mobilité ({collabs.filter(c => c.parcours_type === "mobilite_interne").length})
          </Button>
          <Button variant={filter === "pse" ? "default" : "outline"} size="sm" className={filter === "pse" ? "bg-red-600" : ""} onClick={() => setFilter("pse")} data-testid="filter-pse">
            <Shield className="w-3.5 h-3.5 mr-1" />PSE ({collabs.filter(c => c.parcours_type === "pse_reclassement").length})
          </Button>
        </div>
      </div>

      {/* Alertes */}
      {filtered.some(c => c.risk_level === "critique") && (
        <Card className="border-l-4 border-l-red-500 border-red-200 bg-red-50/50" data-testid="alert-critique">
          <CardContent className="p-3 flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 text-red-600" />
            <p className="text-sm text-red-700"><span className="font-semibold">{filtered.filter(c => c.risk_level === "critique").length}</span> collaborateur{filtered.filter(c => c.risk_level === "critique").length > 1 ? "s" : ""} en risque critique — action immediate requise</p>
          </CardContent>
        </Card>
      )}

      {/* Pipeline columns */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3" data-testid="pipeline-columns">
        {STAGES.map(stage => {
          const stageCandidates = filtered.filter(c => c.stage === stage.key);
          return (
            <Card key={stage.key} className={`border ${stage.color}`} data-testid={`col-${stage.key}`}>
              <CardHeader className="pb-2 px-3 pt-3">
                <CardTitle className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <div className={`w-2.5 h-2.5 rounded-full ${stage.dotColor}`} />
                    {stage.label}
                  </div>
                  <Badge variant="secondary" className="text-xs">{stageCandidates.length}</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="px-3 pb-3 space-y-2 max-h-[400px] overflow-y-auto">
                {stageCandidates.length === 0 ? <p className="text-xs text-slate-400 text-center py-4">Aucun</p> : (
                  stageCandidates.map(c => (
                    <div key={c.id} className="p-2.5 rounded-lg bg-white border border-slate-100 hover:border-emerald-200 hover:shadow-sm transition-all cursor-pointer"
                      onClick={() => onNavigate("collaborateurs", { collabId: c.id })} data-testid={`pipe-card-${c.id}`}>
                      <div className="flex items-center gap-2 mb-1">
                        <div className="w-7 h-7 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-700 font-bold text-[10px]">
                          {c.name.split(" ").map(n => n[0]).join("").slice(0, 2)}
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className="text-xs font-semibold text-slate-800 truncate">{c.name}</p>
                          <p className="text-[10px] text-slate-500 truncate">{c.poste}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-1 flex-wrap">
                        <Badge className={`${RISK_BADGE[c.risk_level]} text-[10px] py-0`}>{c.risk_level}</Badge>
                        {c.parcours_type && c.parcours_type !== "autre" && (
                          <Badge className={`${PARCOURS_BADGE[c.parcours_type]} text-[10px] py-0`}>{c.parcours_type === "mobilite_interne" ? "Mob." : "PSE"}</Badge>
                        )}
                      </div>
                      {c.next_action && <p className="text-[10px] text-amber-600 mt-1 flex items-center gap-0.5"><Zap className="w-2.5 h-2.5" />{c.next_action}</p>}
                      {/* Move stage */}
                      <Select value={c.stage} onValueChange={v => updateStage(c.id, v)}>
                        <SelectTrigger className="h-7 text-[10px] mt-1.5 bg-white" onClick={e => e.stopPropagation()}><SelectValue /></SelectTrigger>
                        <SelectContent>{STAGES.map(s => <SelectItem key={s.key} value={s.key} className="text-xs">{s.label}</SelectItem>)}</SelectContent>
                      </Select>
                    </div>
                  ))
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
};

export default ParcoursPipeline;
