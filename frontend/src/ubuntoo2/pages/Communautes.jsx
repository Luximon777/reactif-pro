import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Users, Plus, Check, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { u2, CATEGORIES } from "../api";

export default function Communautes() {
  const [communities, setCommunities] = useState([]);
  const [category, setCategory] = useState("all");
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);
  const [form, setForm] = useState({ name: "", category: "thematiques", description: "" });
  const [creating, setCreating] = useState(false);
  const navigate = useNavigate();

  const load = async () => {
    setLoading(true);
    try {
      const res = await u2.get("/communities", category !== "all" ? { category } : {});
      setCommunities(res.data);
    } catch { /* silent */ }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, [category]); // eslint-disable-line

  const toggleJoin = async (c) => {
    try {
      await u2.post(`/communities/${c.id}/${c.joined ? "leave" : "join"}`);
      toast.success(c.joined ? `Vous avez quitté ${c.name}` : `Bienvenue dans ${c.name} !`);
      setCommunities(prev => prev.map(x => x.id === c.id ? { ...x, joined: !c.joined, members_count: x.members_count + (c.joined ? -1 : 1) } : x));
    } catch { toast.error("Erreur"); }
  };

  const create = async () => {
    setCreating(true);
    try {
      const res = await u2.post("/communities", form);
      toast.success(`Communauté « ${res.data.name} » créée`);
      setCreateOpen(false);
      setForm({ name: "", category: "thematiques", description: "" });
      load();
    } catch (e) { toast.error(e.response?.data?.detail || "Erreur"); }
    finally { setCreating(false); }
  };

  return (
    <div className="space-y-4" data-testid="ubuntoo-communautes">
      <div className="flex items-start justify-between gap-3 flex-wrap">
        <div>
          <h1 className="text-2xl font-extrabold u2-heading tracking-tight">Communautés</h1>
          <p className="text-sm text-stone-500 mt-1">Métiers, situations, territoires, thématiques : rejoignez vos espaces d'entraide.</p>
        </div>
        <Button size="sm" className="rounded-xl u2-btn-primary" onClick={() => setCreateOpen(true)} data-testid="create-community-btn">
          <Plus className="w-3.5 h-3.5 mr-1.5" />Créer
        </Button>
      </div>

      <div className="flex gap-2 overflow-x-auto pb-1 -mx-1 px-1">
        {[["all", "Toutes"], ...Object.entries(CATEGORIES)].map(([key, label]) => (
          <button key={key} onClick={() => setCategory(key)} data-testid={`filter-category-${key}`}
            className={`rounded-full px-3.5 py-1.5 text-xs font-medium whitespace-nowrap border transition-colors ${category === key ? "bg-[#C85A32] text-white border-transparent" : "bg-white text-stone-600 border-[#E2DFD8] hover:border-orange-300"}`}>
            {label}
          </button>
        ))}
      </div>

      {loading ? <div className="flex justify-center py-12"><Loader2 className="w-7 h-7 animate-spin text-[#C85A32]" /></div> : (
        <div className="grid gap-3 sm:grid-cols-2">
          {communities.map(c => (
            <Card key={c.id} className="rounded-2xl border border-[#E2DFD8] shadow-none bg-white hover:border-orange-300 transition-colors" data-testid={`community-card-${c.id}`}>
              <CardContent className="p-4 flex flex-col gap-3 h-full">
                <button className="text-left flex-1" onClick={() => navigate(`/ubuntoo/communautes/${c.id}`)} data-testid={`open-community-${c.id}`}>
                  <div className="flex items-center gap-2 mb-1">
                    <Badge variant="outline" className="rounded-full text-[10px] uppercase tracking-wide border-[#E2DFD8] text-stone-500">{CATEGORIES[c.category]}</Badge>
                    {c.joined && <Badge className="rounded-full text-[10px] bg-emerald-50 text-emerald-700 border border-emerald-200 hover:bg-emerald-50">Membre</Badge>}
                  </div>
                  <h3 className="text-base font-semibold u2-heading">{c.name}</h3>
                  <p className="text-xs text-stone-500 mt-1 leading-relaxed line-clamp-2">{c.description}</p>
                </button>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-stone-400 flex items-center gap-1"><Users className="w-3.5 h-3.5" />{c.members_count} membre{c.members_count > 1 ? "s" : ""}</span>
                  <Button size="sm" variant={c.joined ? "outline" : "default"}
                    className={`rounded-xl ${c.joined ? "text-stone-500" : "u2-btn-primary"}`}
                    onClick={() => toggleJoin(c)} data-testid={`join-community-${c.id}`}>
                    {c.joined ? "Quitter" : <><Check className="w-3.5 h-3.5 mr-1.5" />Rejoindre</>}
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={createOpen} onOpenChange={setCreateOpen}>
        <DialogContent className="max-w-md rounded-2xl" data-testid="create-community-dialog">
          <DialogHeader>
            <DialogTitle className="u2-heading">Créer une communauté</DialogTitle>
            <DialogDescription>Un espace d'entraide professionnelle autour d'un métier, d'une situation, d'un territoire ou d'une thématique.</DialogDescription>
          </DialogHeader>
          <div className="space-y-3">
            <Input value={form.name} onChange={e => setForm(p => ({ ...p, name: e.target.value }))} placeholder="Nom de la communauté" className="rounded-xl" data-testid="community-name-input" />
            <Select value={form.category} onValueChange={v => setForm(p => ({ ...p, category: v }))}>
              <SelectTrigger className="rounded-xl" data-testid="community-category-select"><SelectValue /></SelectTrigger>
              <SelectContent>{Object.entries(CATEGORIES).map(([k, l]) => <SelectItem key={k} value={k}>{l}</SelectItem>)}</SelectContent>
            </Select>
            <Textarea value={form.description} onChange={e => setForm(p => ({ ...p, description: e.target.value }))} rows={2} maxLength={300} placeholder="Description courte" className="rounded-xl" data-testid="community-description-input" />
            <div className="flex justify-end gap-2">
              <Button variant="outline" className="rounded-xl" onClick={() => setCreateOpen(false)}>Annuler</Button>
              <Button className="rounded-xl u2-btn-primary" onClick={create} disabled={creating} data-testid="submit-community-btn">
                {creating ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Plus className="w-4 h-4 mr-2" />}Créer
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
