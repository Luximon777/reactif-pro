import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Sparkles, Target, TrendingUp, Briefcase, BookOpen, Shield, ChevronRight, Loader2, Zap, Send } from "lucide-react";
import { toast } from "sonner";

const TYPE_INFO = {
  accompagnement: { color: "bg-emerald-100 text-emerald-700", icon: Target },
  mobilite: { color: "bg-amber-100 text-amber-700", icon: TrendingUp },
  formation: { color: "bg-blue-100 text-blue-700", icon: BookOpen },
  reclassement: { color: "bg-red-100 text-red-700", icon: Shield },
  suivi: { color: "bg-slate-100 text-slate-600", icon: Briefcase },
};

const MatchingView = ({ token, onNavigate }) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");
  const [executing, setExecuting] = useState(null);

  useEffect(() => {
    axios.get(`${API}/entreprise/matching?token=${token}&type=${filter}`)
      .then(r => setData(r.data)).catch(() => {}).finally(() => setLoading(false));
  }, [token, filter]);

  const executeAction = async (collabId, rec) => {
    setExecuting(`${collabId}-${rec.type}`);
    try {
      const actionMap = { accompagnement: "lancer_accompagnement", mobilite: "proposer_mobilite", formation: "proposer_formation", reclassement: "export_dossier", suivi: "entretien_pro" };
      await axios.post(`${API}/entreprise/collaborateurs/${collabId}/action?token=${token}`, { action_type: actionMap[rec.type] || "entretien_pro", detail: rec.label });
      toast.success("Action executee");
    } catch { toast.error("Erreur"); }
    setExecuting(null);
  };

  if (loading) return <div className="flex justify-center py-20"><Loader2 className="w-8 h-8 animate-spin text-emerald-600" /></div>;

  return (
    <div className="space-y-6" data-testid="matching-view">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>Matching & Opportunites</h1>
          <p className="text-sm text-slate-500">Recommandations basées sur les compétences réelles et les soft skills</p>
        </div>
        <Select value={filter} onValueChange={v => { setFilter(v); setLoading(true); }}>
          <SelectTrigger className="w-48 h-9"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Tous les profils</SelectItem>
            <SelectItem value="mobilite">Mobilité interne</SelectItem>
            <SelectItem value="pse">PSE / Reclassement</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Card className="border border-indigo-200 bg-gradient-to-r from-indigo-50 to-purple-50/30">
        <CardContent className="p-4 flex items-start gap-3">
          <Sparkles className="w-5 h-5 text-indigo-600 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-slate-800">Moteur de matching RE'ACTIF PRO</p>
            <p className="text-xs text-slate-500">Le matching repose sur les compétences réelles, les soft skills D'CLIC PRO et les aspirations — pas uniquement sur le diplôme.</p>
          </div>
        </CardContent>
      </Card>

      {data.length === 0 ? (
        <Card className="border-dashed border-2"><CardContent className="py-16 text-center">
          <Sparkles className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-500">Aucune recommandation disponible</p>
        </CardContent></Card>
      ) : (
        <div className="space-y-4">
          {data.map(item => (
            <Card key={item.collab_id} className="border border-slate-100 hover:border-emerald-200 transition-all" data-testid={`match-${item.collab_id}`}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3 cursor-pointer" onClick={() => onNavigate("collaborateurs", { collabId: item.collab_id })}>
                    <div className="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-700 font-bold text-sm">
                      {item.collab_name.split(" ").map(n => n[0]).join("").slice(0, 2)}
                    </div>
                    <div>
                      <h3 className="font-semibold text-slate-900">{item.collab_name}</h3>
                      <p className="text-xs text-slate-500">{item.poste}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Badge className={`text-xs ${item.risk_level === "critique" ? "bg-red-100 text-red-700" : item.risk_level === "eleve" ? "bg-orange-100 text-orange-700" : "bg-slate-100 text-slate-600"}`}>{item.risk_level}</Badge>
                  </div>
                </div>
                <div className="space-y-2">
                  {(item.recommendations || []).map((rec, i) => {
                    const info = TYPE_INFO[rec.type] || TYPE_INFO.suivi;
                    const Icon = info.icon;
                    return (
                      <div key={i} className="flex items-center justify-between p-2.5 rounded-lg bg-slate-50 border border-slate-100">
                        <div className="flex items-center gap-3">
                          <div className={`w-8 h-8 rounded-lg ${info.color} flex items-center justify-center`}><Icon className="w-4 h-4" /></div>
                          <div>
                            <p className="text-sm font-medium text-slate-800">{rec.label}</p>
                            <p className="text-xs text-slate-500">{rec.reason}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant="secondary" className="text-xs">{rec.score}%</Badge>
                          <Button size="sm" variant="outline" className="h-7 text-xs" onClick={() => executeAction(item.collab_id, rec)}
                            disabled={executing === `${item.collab_id}-${rec.type}`} data-testid={`propose-${item.collab_id}-${rec.type}`}>
                            {executing === `${item.collab_id}-${rec.type}` ? <Loader2 className="w-3 h-3 animate-spin" /> : <Send className="w-3 h-3 mr-1" />}Proposer
                          </Button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default MatchingView;
