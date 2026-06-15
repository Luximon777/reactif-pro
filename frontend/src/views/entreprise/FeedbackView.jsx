import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { MessageSquare, ThumbsUp, Star, Plus, RefreshCw, Trash2, Lightbulb, AlertCircle, Heart } from "lucide-react";

const CATEGORIES = [
  { key: "idee", label: "Idée / Suggestion", icon: Lightbulb, color: "bg-amber-100 text-amber-700" },
  { key: "amelioration", label: "Amélioration", icon: Star, color: "bg-blue-100 text-blue-700" },
  { key: "probleme", label: "Problème signalé", icon: AlertCircle, color: "bg-red-100 text-red-700" },
  { key: "felicitation", label: "Félicitation / Bravo", icon: Heart, color: "bg-emerald-100 text-emerald-700" },
];

const FeedbackView = ({ token }) => {
  const [feedbacks, setFeedbacks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [filterCat, setFilterCat] = useState("all");
  const [form, setForm] = useState({ category: "idee", title: "", message: "", anonymous: true });

  const load = async () => {
    try {
      const r = await axios.get(`${API}/entreprise/feedback?token=${token}`);
      setFeedbacks(r.data);
    } catch {}
    setLoading(false);
  };

  useEffect(() => { load(); }, [token]);

  const submit = async () => {
    if (!form.title.trim() || !form.message.trim()) return;
    try {
      await axios.post(`${API}/entreprise/feedback?token=${token}`, form);
      setShowForm(false);
      setForm({ category: "idee", title: "", message: "", anonymous: true });
      load();
    } catch {}
  };

  const upvote = async (id) => {
    try {
      await axios.put(`${API}/entreprise/feedback/${id}/upvote?token=${token}`);
      load();
    } catch {}
  };

  const deleteFeedback = async (id) => {
    try {
      await axios.delete(`${API}/entreprise/feedback/${id}?token=${token}`);
      load();
    } catch {}
  };

  const catObj = (key) => CATEGORIES.find(c => c.key === key) || CATEGORIES[0];
  const filtered = feedbacks.filter(f => filterCat === "all" || f.category === filterCat)
    .sort((a, b) => (b.upvotes || 0) - (a.upvotes || 0));

  const stats = CATEGORIES.map(c => ({
    ...c,
    count: feedbacks.filter(f => f.category === c.key).length,
  }));

  if (loading) return <div className="flex justify-center py-20"><RefreshCw className="w-6 h-6 animate-spin text-slate-400" /></div>;

  return (
    <div className="space-y-6" data-testid="feedback-view">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>Feedback & Communication</h1>
          <p className="text-sm text-slate-500 mt-1">Boîte à idées, suggestions et reconnaissance entre collaborateurs</p>
        </div>
        <Button onClick={() => setShowForm(true)} className="bg-emerald-600 hover:bg-emerald-700" data-testid="new-feedback">
          <Plus className="w-4 h-4 mr-2" />Nouveau feedback
        </Button>
      </div>

      {/* Stats par catégorie */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {stats.map(s => {
          const Icon = s.icon;
          return (
            <Card key={s.key} className="cursor-pointer hover:shadow-sm transition-shadow" onClick={() => setFilterCat(filterCat === s.key ? "all" : s.key)}>
              <CardContent className="p-4 flex items-center gap-3">
                <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${s.color}`}>
                  <Icon className="w-4.5 h-4.5" />
                </div>
                <div>
                  <p className="text-xl font-bold text-slate-900">{s.count}</p>
                  <p className="text-[10px] text-slate-500">{s.label}</p>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Filtre actif */}
      {filterCat !== "all" && (
        <div className="flex items-center gap-2">
          <Badge className={`${catObj(filterCat).color}`}>{catObj(filterCat).label}</Badge>
          <Button variant="ghost" size="sm" className="text-xs h-6" onClick={() => setFilterCat("all")}>Tout afficher</Button>
        </div>
      )}

      {/* Liste des feedbacks */}
      {filtered.length === 0 ? (
        <Card><CardContent className="p-12 text-center">
          <MessageSquare className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-500 text-sm">Aucun feedback pour le moment</p>
        </CardContent></Card>
      ) : (
        <div className="space-y-3">
          {filtered.map(f => {
            const cat = catObj(f.category);
            const CatIcon = cat.icon;
            return (
              <Card key={f.id} className="hover:shadow-sm transition-shadow" data-testid={`feedback-${f.id}`}>
                <CardContent className="p-4">
                  <div className="flex items-start gap-4">
                    <button
                      className="flex flex-col items-center gap-0.5 pt-1 group"
                      onClick={() => upvote(f.id)}
                    >
                      <ThumbsUp className="w-4 h-4 text-slate-400 group-hover:text-emerald-500 transition-colors" />
                      <span className="text-xs font-bold text-slate-500">{f.upvotes || 0}</span>
                    </button>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge className={`${cat.color} text-[10px] px-1.5 py-0.5 flex items-center gap-1`}>
                          <CatIcon className="w-3 h-3" />{cat.label}
                        </Badge>
                        {f.anonymous && <Badge className="bg-slate-100 text-slate-500 text-[10px]">Anonyme</Badge>}
                        <span className="text-[10px] text-slate-400 ml-auto">{new Date(f.created_at).toLocaleDateString("fr-FR")}</span>
                      </div>
                      <h4 className="font-semibold text-sm text-slate-900">{f.title}</h4>
                      <p className="text-sm text-slate-600 mt-1">{f.message}</p>
                    </div>
                    <Button variant="ghost" size="icon" className="h-7 w-7 text-slate-400 hover:text-red-500" onClick={() => deleteFeedback(f.id)}>
                      <Trash2 className="w-3.5 h-3.5" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Formulaire */}
      {showForm && (
        <Card className="border-2 border-emerald-200">
          <CardHeader><CardTitle className="text-base">Nouveau feedback</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium">Catégorie</label>
              <Select value={form.category} onValueChange={v => setForm(f => ({ ...f, category: v }))}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>{CATEGORIES.map(c => <SelectItem key={c.key} value={c.key}>{c.label}</SelectItem>)}</SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium">Titre</label>
              <Input value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} placeholder="Résumé en quelques mots" />
            </div>
            <div>
              <label className="text-sm font-medium">Message</label>
              <Textarea value={form.message} onChange={e => setForm(f => ({ ...f, message: e.target.value }))} placeholder="Décrivez votre idée, suggestion ou retour..." rows={4} />
            </div>
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2 text-sm">
                <input type="checkbox" checked={form.anonymous} onChange={e => setForm(f => ({ ...f, anonymous: e.target.checked }))} className="rounded" />
                Publier anonymement
              </label>
            </div>
            <div className="flex gap-2">
              <Button onClick={submit} className="bg-emerald-600 hover:bg-emerald-700" data-testid="submit-feedback">Publier</Button>
              <Button variant="outline" onClick={() => setShowForm(false)}>Annuler</Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default FeedbackView;
