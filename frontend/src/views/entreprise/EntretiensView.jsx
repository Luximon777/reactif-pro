import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Calendar, Plus, Clock, CheckCircle2, AlertCircle, User, FileText, RefreshCw, Trash2 } from "lucide-react";

const TYPES = [
  { key: "integration", label: "Intégration", color: "bg-blue-100 text-blue-700" },
  { key: "evaluation", label: "Évaluation annuelle", color: "bg-purple-100 text-purple-700" },
  { key: "evolution", label: "Évolution / Carrière", color: "bg-amber-100 text-amber-700" },
  { key: "suivi", label: "Suivi régulier", color: "bg-emerald-100 text-emerald-700" },
  { key: "recadrage", label: "Recadrage", color: "bg-red-100 text-red-700" },
  { key: "depart", label: "Entretien de départ", color: "bg-slate-100 text-slate-600" },
];

const STATUSES = [
  { key: "planifie", label: "Planifié", color: "bg-blue-100 text-blue-700", icon: Clock },
  { key: "realise", label: "Réalisé", color: "bg-emerald-100 text-emerald-700", icon: CheckCircle2 },
  { key: "annule", label: "Annulé", color: "bg-red-100 text-red-700", icon: AlertCircle },
];

const EntretiensView = ({ token }) => {
  const [entretiens, setEntretiens] = useState([]);
  const [collabs, setCollabs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [filterType, setFilterType] = useState("all");
  const [filterStatus, setFilterStatus] = useState("all");
  const [form, setForm] = useState({ collab_id: "", type: "suivi", date: "", notes: "", status: "planifie" });

  const load = async () => {
    try {
      const [e, c] = await Promise.all([
        axios.get(`${API}/entreprise/entretiens?token=${token}`),
        axios.get(`${API}/entreprise/collaborateurs?token=${token}`),
      ]);
      setEntretiens(e.data);
      setCollabs(c.data);
    } catch {}
    setLoading(false);
  };

  useEffect(() => { load(); }, [token]);

  const submit = async () => {
    if (!form.collab_id || !form.date) return;
    try {
      await axios.post(`${API}/entreprise/entretiens?token=${token}`, form);
      setShowForm(false);
      setForm({ collab_id: "", type: "suivi", date: "", notes: "", status: "planifie" });
      load();
    } catch {}
  };

  const updateStatus = async (id, status) => {
    try {
      await axios.put(`${API}/entreprise/entretiens/${id}/status?token=${token}&status=${status}`);
      load();
    } catch {}
  };

  const deleteEntretien = async (id) => {
    try {
      await axios.delete(`${API}/entreprise/entretiens/${id}?token=${token}`);
      load();
    } catch {}
  };

  const getCollabName = (id) => collabs.find(c => c.id === id)?.name || "—";
  const typeObj = (key) => TYPES.find(t => t.key === key) || TYPES[3];
  const statusObj = (key) => STATUSES.find(s => s.key === key) || STATUSES[0];

  const filtered = entretiens.filter(e =>
    (filterType === "all" || e.type === filterType) &&
    (filterStatus === "all" || e.status === filterStatus)
  ).sort((a, b) => new Date(b.date) - new Date(a.date));

  const stats = {
    total: entretiens.length,
    planifies: entretiens.filter(e => e.status === "planifie").length,
    realises: entretiens.filter(e => e.status === "realise").length,
  };

  if (loading) return <div className="flex justify-center py-20"><RefreshCw className="w-6 h-6 animate-spin text-slate-400" /></div>;

  return (
    <div className="space-y-6" data-testid="entretiens-view">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>Entretiens & Suivi</h1>
          <p className="text-sm text-slate-500 mt-1">Planifiez et suivez tous les entretiens RH</p>
        </div>
        <Button onClick={() => setShowForm(true)} className="bg-emerald-600 hover:bg-emerald-700" data-testid="new-entretien">
          <Plus className="w-4 h-4 mr-2" />Nouvel entretien
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: "Total", value: stats.total, icon: FileText, color: "bg-slate-100 text-slate-600" },
          { label: "Planifiés", value: stats.planifies, icon: Clock, color: "bg-blue-100 text-blue-600" },
          { label: "Réalisés", value: stats.realises, icon: CheckCircle2, color: "bg-emerald-100 text-emerald-600" },
        ].map(s => (
          <Card key={s.label}>
            <CardContent className="p-4 flex items-center gap-3">
              <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${s.color}`}>
                <s.icon className="w-5 h-5" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{s.value}</p>
                <p className="text-xs text-slate-500">{s.label}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Filters */}
      <div className="flex gap-3">
        <Select value={filterType} onValueChange={setFilterType}>
          <SelectTrigger className="w-44 h-9"><SelectValue placeholder="Type" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Tous les types</SelectItem>
            {TYPES.map(t => <SelectItem key={t.key} value={t.key}>{t.label}</SelectItem>)}
          </SelectContent>
        </Select>
        <Select value={filterStatus} onValueChange={setFilterStatus}>
          <SelectTrigger className="w-44 h-9"><SelectValue placeholder="Statut" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Tous les statuts</SelectItem>
            {STATUSES.map(s => <SelectItem key={s.key} value={s.key}>{s.label}</SelectItem>)}
          </SelectContent>
        </Select>
      </div>

      {/* List */}
      {filtered.length === 0 ? (
        <Card><CardContent className="p-12 text-center">
          <Calendar className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-500 text-sm">Aucun entretien</p>
        </CardContent></Card>
      ) : (
        <div className="space-y-2">
          {filtered.map(e => {
            const t = typeObj(e.type);
            const st = statusObj(e.status);
            const StIcon = st.icon;
            return (
              <Card key={e.id} className="hover:shadow-sm transition-shadow" data-testid={`entretien-${e.id}`}>
                <CardContent className="p-4 flex items-center gap-4">
                  <div className="w-12 h-12 rounded-lg bg-slate-100 flex flex-col items-center justify-center text-xs">
                    <span className="font-bold text-slate-700">{new Date(e.date).getDate()}</span>
                    <span className="text-slate-400">{new Date(e.date).toLocaleString("fr-FR", { month: "short" })}</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <User className="w-3.5 h-3.5 text-slate-400" />
                      <span className="font-semibold text-sm text-slate-900">{getCollabName(e.collab_id)}</span>
                    </div>
                    {e.notes && <p className="text-xs text-slate-500 mt-0.5 truncate">{e.notes}</p>}
                  </div>
                  <Badge className={`${t.color} text-xs`}>{t.label}</Badge>
                  <Badge className={`${st.color} text-xs flex items-center gap-1`}><StIcon className="w-3 h-3" />{st.label}</Badge>
                  <div className="flex gap-1">
                    {e.status === "planifie" && (
                      <Button variant="ghost" size="sm" className="text-emerald-600 hover:bg-emerald-50 text-xs h-7" onClick={() => updateStatus(e.id, "realise")}>Valider</Button>
                    )}
                    <Button variant="ghost" size="icon" className="h-7 w-7 text-slate-400 hover:text-red-500" onClick={() => deleteEntretien(e.id)}><Trash2 className="w-3.5 h-3.5" /></Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Dialog */}
      <Dialog open={showForm} onOpenChange={setShowForm}>
        <DialogContent className="max-w-md">
          <DialogHeader><DialogTitle>Planifier un entretien</DialogTitle></DialogHeader>
          <div className="space-y-4 mt-2">
            <div>
              <label className="text-sm font-medium">Collaborateur</label>
              <Select value={form.collab_id} onValueChange={v => setForm(f => ({ ...f, collab_id: v }))}>
                <SelectTrigger><SelectValue placeholder="Sélectionner" /></SelectTrigger>
                <SelectContent>{collabs.map(c => <SelectItem key={c.id} value={c.id}>{c.name}</SelectItem>)}</SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium">Type</label>
              <Select value={form.type} onValueChange={v => setForm(f => ({ ...f, type: v }))}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>{TYPES.map(t => <SelectItem key={t.key} value={t.key}>{t.label}</SelectItem>)}</SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium">Date</label>
              <Input type="date" value={form.date} onChange={e => setForm(f => ({ ...f, date: e.target.value }))} />
            </div>
            <div>
              <label className="text-sm font-medium">Notes</label>
              <Textarea value={form.notes} onChange={e => setForm(f => ({ ...f, notes: e.target.value }))} placeholder="Points à aborder..." rows={3} />
            </div>
            <Button onClick={submit} className="w-full bg-emerald-600 hover:bg-emerald-700" data-testid="submit-entretien">Planifier</Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default EntretiensView;
