import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Users, TrendingUp, AlertTriangle, Link2, Activity, ArrowRight,
  CheckCircle2, Clock, Briefcase, ChevronRight, GitBranch, Shield
} from "lucide-react";

const STAGE_LABELS = { en_poste: "En poste", en_reflexion: "En réflexion", en_transition: "En transition", en_reclassement: "En reclassement", sorti: "Sorti" };
const STAGE_COLORS = { en_poste: "bg-emerald-100 text-emerald-700", en_reflexion: "bg-amber-100 text-amber-700", en_transition: "bg-blue-100 text-blue-700", en_reclassement: "bg-red-100 text-red-700", sorti: "bg-slate-100 text-slate-600" };
const RISK_COLORS = { faible: "text-emerald-600", moyen: "text-amber-600", eleve: "text-orange-600", critique: "text-red-600" };

const DashboardRH = ({ token, onNavigate }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${API}/entreprise/dashboard?token=${token}`)
      .then(r => setData(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [token]);

  if (loading) return <div className="flex justify-center py-20"><div className="animate-spin rounded-full h-10 w-10 border-b-2 border-emerald-600" /></div>;
  if (!data) return null;

  const kpis = [
    { label: "Collaborateurs suivis", value: data.total_collaborateurs, icon: Users, color: "bg-emerald-100 text-emerald-600" },
    { label: "Profils synchronisés", value: data.profils_synchronises, icon: Link2, color: "bg-purple-100 text-purple-600" },
    { label: "Transitions en cours", value: data.transitions_en_cours, icon: TrendingUp, color: "bg-blue-100 text-blue-600" },
    { label: "Risques identifiés", value: data.risques_identifies, icon: AlertTriangle, color: data.risques_identifies > 0 ? "bg-red-100 text-red-600" : "bg-slate-100 text-slate-500" },
    { label: "Mobilité interne", value: data.mobilite_interne, icon: GitBranch, color: "bg-amber-100 text-amber-600" },
    { label: "PSE / Reclassement", value: data.pse_reclassement, icon: Shield, color: "bg-orange-100 text-orange-600" },
  ];

  return (
    <div className="space-y-6" data-testid="rh-dashboard">
      <div>
        <h1 className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>Tableau de bord RH</h1>
        <p className="text-sm text-slate-500 mt-1">Vision globale des parcours et transitions</p>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3" data-testid="rh-kpis">
        {kpis.map((k, i) => {
          const Icon = k.icon;
          return (
            <Card key={i} className="border border-slate-100 hover:border-emerald-200 transition-all cursor-pointer"
              onClick={() => onNavigate("collaborateurs")} data-testid={`kpi-${i}`}>
              <CardContent className="p-4">
                <div className={`w-9 h-9 rounded-lg ${k.color} flex items-center justify-center mb-2`}><Icon className="w-4.5 h-4.5" /></div>
                <p className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>{k.value}</p>
                <p className="text-xs text-slate-500 mt-0.5">{k.label}</p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Parcours rapide */}
        <Card className="lg:col-span-1 border border-slate-100" data-testid="parcours-rapide">
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2"><GitBranch className="w-4 h-4 text-emerald-600" /> Carte des parcours</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {Object.entries(data.stages || {}).filter(([, v]) => v > 0).map(([stage, count]) => (
              <div key={stage} className="flex items-center justify-between p-2.5 rounded-lg bg-slate-50 border border-slate-100 cursor-pointer hover:bg-slate-100"
                onClick={() => onNavigate("parcours")}>
                <div className="flex items-center gap-2">
                  <Badge className={`${STAGE_COLORS[stage] || "bg-slate-100"} text-xs`}>{STAGE_LABELS[stage] || stage}</Badge>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold text-slate-700">{count}</span>
                  <ChevronRight className="w-3.5 h-3.5 text-slate-300" />
                </div>
              </div>
            ))}
            {Object.keys(data.stages || {}).length === 0 && <p className="text-sm text-slate-400 text-center py-4">Aucun collaborateur</p>}
          </CardContent>
        </Card>

        {/* Flux d'activité */}
        <Card className="lg:col-span-2 border border-slate-100" data-testid="activity-feed">
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2"><Activity className="w-4 h-4 text-emerald-600" /> Flux d'activité</CardTitle>
            <CardDescription>Dernières mises à jour en temps réel</CardDescription>
          </CardHeader>
          <CardContent>
            {(data.activity_feed || []).length === 0 ? (
              <p className="text-sm text-slate-400 text-center py-6">Aucune activité récente</p>
            ) : (
              <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
                {data.activity_feed.slice(0, 12).map((a, i) => (
                  <div key={i} className="flex items-start gap-3 text-sm cursor-pointer hover:bg-slate-50 rounded-lg p-2 -mx-2"
                    onClick={() => onNavigate("collaborateurs", { collabId: a.collab_id })}>
                    <div className={`w-2 h-2 rounded-full mt-1.5 shrink-0 ${
                      a.source === "systeme" ? "bg-purple-500" : a.source === "espace_personnel" ? "bg-blue-500" : "bg-emerald-500"
                    }`} />
                    <div className="flex-1 min-w-0">
                      <p className="text-slate-700"><span className="font-medium">{a.collab_name}</span> — {a.detail || a.action}</p>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className="text-xs text-slate-400">{new Date(a.date).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' })}</span>
                        <Badge variant="secondary" className="text-[10px] py-0">{a.source}</Badge>
                      </div>
                    </div>
                    <ChevronRight className="w-3.5 h-3.5 text-slate-300 mt-1 shrink-0" />
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Blocs pilotage Mobilité + PSE */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="border-l-4 border-l-amber-400 border border-slate-100 cursor-pointer hover:shadow-sm transition-all"
          onClick={() => onNavigate("parcours")} data-testid="bloc-mobilite">
          <CardContent className="p-4">
            <div className="flex items-center gap-3 mb-2">
              <GitBranch className="w-5 h-5 text-amber-600" />
              <h3 className="font-semibold text-slate-800">Pilotage Mobilité Interne</h3>
            </div>
            <p className="text-sm text-slate-500 mb-2">Collaborateurs en réflexion ou en transition vers un nouveau poste interne</p>
            <div className="flex items-center gap-4 text-sm">
              <span className="font-bold text-amber-700">{data.mobilite_interne}</span>
              <span className="text-slate-400">collaborateur{data.mobilite_interne !== 1 ? "s" : ""}</span>
              <ArrowRight className="w-4 h-4 text-slate-300 ml-auto" />
            </div>
          </CardContent>
        </Card>
        <Card className="border-l-4 border-l-red-400 border border-slate-100 cursor-pointer hover:shadow-sm transition-all"
          onClick={() => onNavigate("parcours")} data-testid="bloc-pse">
          <CardContent className="p-4">
            <div className="flex items-center gap-3 mb-2">
              <Shield className="w-5 h-5 text-red-600" />
              <h3 className="font-semibold text-slate-800">Pilotage PSE / Reclassement</h3>
            </div>
            <p className="text-sm text-slate-500 mb-2">Collaborateurs en reclassement interne/externe ou départ volontaire</p>
            <div className="flex items-center gap-4 text-sm">
              <span className="font-bold text-red-700">{data.pse_reclassement}</span>
              <span className="text-slate-400">collaborateur{data.pse_reclassement !== 1 ? "s" : ""}</span>
              <ArrowRight className="w-4 h-4 text-slate-300 ml-auto" />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default DashboardRH;
