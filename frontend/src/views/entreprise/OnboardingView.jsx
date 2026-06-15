import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Rocket, CheckCircle2, Clock, Circle, Plus, User, RefreshCw, ChevronRight } from "lucide-react";

const DEFAULT_STEPS = [
  { label: "Accueil & présentation équipe", category: "jour_1" },
  { label: "Remise du matériel & accès", category: "jour_1" },
  { label: "Visite des locaux", category: "jour_1" },
  { label: "Présentation de la culture d'entreprise", category: "semaine_1" },
  { label: "Formation aux outils internes", category: "semaine_1" },
  { label: "Rencontre avec le parrain/marraine", category: "semaine_1" },
  { label: "Point d'étape à 1 semaine", category: "semaine_1" },
  { label: "Prise en main des missions principales", category: "mois_1" },
  { label: "Entretien de suivi à 1 mois", category: "mois_1" },
  { label: "Feedback 360° à 3 mois", category: "mois_3" },
  { label: "Bilan d'intégration à 6 mois", category: "mois_6" },
  { label: "Validation de la période d'essai", category: "mois_6" },
];

const CATEGORIES = [
  { key: "jour_1", label: "Jour 1", color: "bg-blue-100 text-blue-700" },
  { key: "semaine_1", label: "Semaine 1", color: "bg-purple-100 text-purple-700" },
  { key: "mois_1", label: "Mois 1", color: "bg-amber-100 text-amber-700" },
  { key: "mois_3", label: "Mois 3", color: "bg-teal-100 text-teal-700" },
  { key: "mois_6", label: "Mois 6", color: "bg-emerald-100 text-emerald-700" },
];

const OnboardingView = ({ token }) => {
  const [parcours, setParcours] = useState([]);
  const [collabs, setCollabs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showNew, setShowNew] = useState(false);
  const [selectedCollab, setSelectedCollab] = useState("");
  const [expandedId, setExpandedId] = useState(null);

  const load = async () => {
    try {
      const [p, c] = await Promise.all([
        axios.get(`${API}/entreprise/onboarding?token=${token}`),
        axios.get(`${API}/entreprise/collaborateurs?token=${token}`),
      ]);
      setParcours(p.data);
      setCollabs(c.data);
    } catch {}
    setLoading(false);
  };

  useEffect(() => { load(); }, [token]);

  const createParcours = async () => {
    if (!selectedCollab) return;
    try {
      await axios.post(`${API}/entreprise/onboarding?token=${token}`, {
        collab_id: selectedCollab,
        steps: DEFAULT_STEPS.map(s => ({ ...s, done: false })),
      });
      setShowNew(false);
      setSelectedCollab("");
      load();
    } catch {}
  };

  const toggleStep = async (parcoursId, stepIdx) => {
    try {
      await axios.put(`${API}/entreprise/onboarding/${parcoursId}/step/${stepIdx}?token=${token}`);
      load();
    } catch {}
  };

  const getCollabName = (id) => collabs.find(c => c.id === id)?.name || "—";
  const getProgress = (steps) => {
    const done = steps.filter(s => s.done).length;
    return Math.round((done / steps.length) * 100);
  };

  if (loading) return <div className="flex justify-center py-20"><RefreshCw className="w-6 h-6 animate-spin text-slate-400" /></div>;

  return (
    <div className="space-y-6" data-testid="onboarding-view">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>Onboarding</h1>
          <p className="text-sm text-slate-500 mt-1">Parcours d'intégration structurés pour les nouveaux collaborateurs</p>
        </div>
        <Button onClick={() => setShowNew(true)} className="bg-emerald-600 hover:bg-emerald-700" data-testid="new-onboarding">
          <Plus className="w-4 h-4 mr-2" />Nouveau parcours
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: "Parcours actifs", value: parcours.filter(p => getProgress(p.steps) < 100).length, color: "bg-blue-100 text-blue-600" },
          { label: "Terminés", value: parcours.filter(p => getProgress(p.steps) === 100).length, color: "bg-emerald-100 text-emerald-600" },
          { label: "Taux moyen", value: parcours.length > 0 ? Math.round(parcours.reduce((a, p) => a + getProgress(p.steps), 0) / parcours.length) + "%" : "—", color: "bg-amber-100 text-amber-600" },
        ].map(s => (
          <Card key={s.label}>
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold text-slate-900">{s.value}</p>
              <p className="text-xs text-slate-500">{s.label}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Parcours list */}
      {parcours.length === 0 ? (
        <Card><CardContent className="p-12 text-center">
          <Rocket className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-500 text-sm">Aucun parcours d'intégration</p>
          <p className="text-slate-400 text-xs mt-1">Créez un parcours pour un nouveau collaborateur</p>
        </CardContent></Card>
      ) : (
        <div className="space-y-3">
          {parcours.map(p => {
            const progress = getProgress(p.steps);
            const expanded = expandedId === p.id;
            return (
              <Card key={p.id} className="overflow-hidden" data-testid={`onboarding-${p.id}`}>
                <div className="p-4 flex items-center gap-4 cursor-pointer hover:bg-slate-50" onClick={() => setExpandedId(expanded ? null : p.id)}>
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center ${progress === 100 ? "bg-emerald-100" : "bg-blue-100"}`}>
                    {progress === 100 ? <CheckCircle2 className="w-5 h-5 text-emerald-600" /> : <User className="w-5 h-5 text-blue-600" />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-sm text-slate-900">{getCollabName(p.collab_id)}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <Progress value={progress} className="h-1.5 flex-1" />
                      <span className="text-xs font-medium text-slate-500">{progress}%</span>
                    </div>
                  </div>
                  <Badge className={progress === 100 ? "bg-emerald-100 text-emerald-700" : "bg-blue-100 text-blue-700"}>
                    {p.steps.filter(s => s.done).length}/{p.steps.length}
                  </Badge>
                  <ChevronRight className={`w-4 h-4 text-slate-400 transition-transform ${expanded ? "rotate-90" : ""}`} />
                </div>
                {expanded && (
                  <div className="border-t border-slate-100 p-4 space-y-4">
                    {CATEGORIES.map(cat => {
                      const catSteps = p.steps.map((s, i) => ({ ...s, idx: i })).filter(s => s.category === cat.key);
                      if (catSteps.length === 0) return null;
                      return (
                        <div key={cat.key}>
                          <Badge className={`${cat.color} text-xs mb-2`}>{cat.label}</Badge>
                          <div className="space-y-1.5 ml-1">
                            {catSteps.map(step => (
                              <button key={step.idx}
                                className="w-full flex items-center gap-3 p-2 rounded-lg hover:bg-slate-50 text-left transition-colors"
                                onClick={() => toggleStep(p.id, step.idx)}
                              >
                                {step.done
                                  ? <CheckCircle2 className="w-4.5 h-4.5 text-emerald-500 flex-shrink-0" />
                                  : <Circle className="w-4.5 h-4.5 text-slate-300 flex-shrink-0" />
                                }
                                <span className={`text-sm ${step.done ? "text-slate-400 line-through" : "text-slate-700"}`}>{step.label}</span>
                              </button>
                            ))}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </Card>
            );
          })}
        </div>
      )}

      {/* Dialog */}
      <Dialog open={showNew} onOpenChange={setShowNew}>
        <DialogContent className="max-w-md">
          <DialogHeader><DialogTitle>Nouveau parcours d'intégration</DialogTitle></DialogHeader>
          <div className="space-y-4 mt-2">
            <div>
              <label className="text-sm font-medium">Collaborateur</label>
              <Select value={selectedCollab} onValueChange={setSelectedCollab}>
                <SelectTrigger><SelectValue placeholder="Sélectionner un collaborateur" /></SelectTrigger>
                <SelectContent>{collabs.map(c => <SelectItem key={c.id} value={c.id}>{c.name}</SelectItem>)}</SelectContent>
              </Select>
            </div>
            <p className="text-xs text-slate-500">{DEFAULT_STEPS.length} étapes pré-configurées seront créées (Jour 1 → Mois 6)</p>
            <Button onClick={createParcours} className="w-full bg-emerald-600 hover:bg-emerald-700" data-testid="submit-onboarding">Créer le parcours</Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default OnboardingView;
