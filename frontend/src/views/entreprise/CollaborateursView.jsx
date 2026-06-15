import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Users, Search, Plus, ChevronRight, Link2, Unlink, Loader2, ArrowUpRight,
  Trash2, Brain, FileText, BookOpen, Target, History, Eye, Award, Clock,
  AlertTriangle, Briefcase, TrendingUp, Send, CheckCircle2, GitBranch,
  Heart, Lightbulb, Zap
} from "lucide-react";
import { toast } from "sonner";

const STAGES = [
  { key: "en_poste", label: "En poste", color: "bg-emerald-100 text-emerald-700" },
  { key: "en_reflexion", label: "En réflexion", color: "bg-amber-100 text-amber-700" },
  { key: "en_transition", label: "En transition", color: "bg-blue-100 text-blue-700" },
  { key: "en_reclassement", label: "En reclassement", color: "bg-red-100 text-red-700" },
  { key: "sorti", label: "Sorti", color: "bg-slate-100 text-slate-600" },
];
const RISKS = ["faible", "moyen", "eleve", "critique"];
const RISK_COLORS = { faible: "bg-emerald-100 text-emerald-700", moyen: "bg-amber-100 text-amber-700", eleve: "bg-orange-100 text-orange-700", critique: "bg-red-100 text-red-700" };
const PARCOURS = [
  { key: "mobilite_interne", label: "Mobilité interne" },
  { key: "pse_reclassement", label: "PSE / Reclassement" },
  { key: "depart_volontaire", label: "Départ volontaire" },
  { key: "autre", label: "Autre" },
];
const SAT_LABELS = ["", "Très insatisfait", "Insatisfait", "Neutre", "Satisfait", "Très satisfait"];

const CollaborateursView = ({ token, onRefresh, onNavigate }) => {
  const [collabs, setCollabs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState(null);
  const [filters, setFilters] = useState({ stage: "", risk: "", parcours: "", search: "" });
  const [createOpen, setCreateOpen] = useState(false);
  const [demandeOpen, setDemandeOpen] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ token });
      if (filters.stage) params.set("stage", filters.stage);
      if (filters.risk) params.set("risk", filters.risk);
      if (filters.parcours) params.set("parcours", filters.parcours);
      if (filters.search) params.set("search", filters.search);
      const r = await axios.get(`${API}/entreprise/collaborateurs?${params}`);
      setCollabs(r.data);
    } catch { }
    setLoading(false);
  }, [token, filters]);

  useEffect(() => { load(); }, [load]);
  useEffect(() => {
    if (window.__rh_select_collab) {
      const id = window.__rh_select_collab;
      delete window.__rh_select_collab;
      const found = collabs.find(c => c.id === id);
      if (found) setSelected(found);
    }
  }, [collabs]);

  if (selected) {
    return <CollabDetail c={selected} onBack={() => { setSelected(null); load(); }} token={token} onRefresh={() => { load(); onRefresh(); }} />;
  }

  return (
    <div className="space-y-4" data-testid="collaborateurs-view">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>Collaborateurs</h1>
          <p className="text-sm text-slate-500">{collabs.length} collaborateur{collabs.length !== 1 ? "s" : ""} suivis</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => setDemandeOpen(true)} className="bg-emerald-600 hover:bg-emerald-700" data-testid="demande-acces-btn">
            <Search className="w-4 h-4 mr-1.5" /> Demande d'acces
          </Button>
          <Button variant="outline" onClick={() => setCreateOpen(true)} data-testid="add-collab-btn">
            <Plus className="w-4 h-4 mr-1.5" /> Ajouter
          </Button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-2 items-center" data-testid="collab-filters">
        <Input placeholder="Rechercher..." className="w-48 h-9" value={filters.search}
          onChange={e => setFilters(f => ({...f, search: e.target.value}))} data-testid="search-input" />
        <Select value={filters.stage} onValueChange={v => setFilters(f => ({...f, stage: v === "all" ? "" : v}))}>
          <SelectTrigger className="w-40 h-9"><SelectValue placeholder="Étape" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Toutes étapes</SelectItem>
            {STAGES.map(s => <SelectItem key={s.key} value={s.key}>{s.label}</SelectItem>)}
          </SelectContent>
        </Select>
        <Select value={filters.risk} onValueChange={v => setFilters(f => ({...f, risk: v === "all" ? "" : v}))}>
          <SelectTrigger className="w-36 h-9"><SelectValue placeholder="Risque" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Tous risques</SelectItem>
            {RISKS.map(r => <SelectItem key={r} value={r}>{r.charAt(0).toUpperCase() + r.slice(1)}</SelectItem>)}
          </SelectContent>
        </Select>
        <Select value={filters.parcours} onValueChange={v => setFilters(f => ({...f, parcours: v === "all" ? "" : v}))}>
          <SelectTrigger className="w-44 h-9"><SelectValue placeholder="Parcours" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Tous parcours</SelectItem>
            {PARCOURS.map(p => <SelectItem key={p.key} value={p.key}>{p.label}</SelectItem>)}
          </SelectContent>
        </Select>
      </div>

      {loading ? (
        <div className="flex justify-center py-16"><Loader2 className="w-8 h-8 animate-spin text-emerald-600" /></div>
      ) : collabs.length === 0 ? (
        <Card className="border-dashed border-2"><CardContent className="py-16 text-center">
          <Users className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-500">Aucun collaborateur</p>
        </CardContent></Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3" data-testid="collab-list">
          {collabs.map(c => <CollabCard key={c.id} c={c} onClick={() => setSelected(c)} />)}
        </div>
      )}

      <CreateCollabDialog open={createOpen} onOpenChange={setCreateOpen} token={token} onCreated={() => { load(); onRefresh(); }} />
      <DemandeAccesDialog open={demandeOpen} onOpenChange={setDemandeOpen} token={token} onDone={() => { load(); onRefresh(); }} />
    </div>
  );
};

const CollabCard = ({ c, onClick }) => {
  const stage = STAGES.find(s => s.key === c.stage) || STAGES[0];
  return (
    <Card className="border border-slate-100 hover:border-emerald-200 transition-all cursor-pointer"
      onClick={onClick} data-testid={`collab-card-${c.id}`}>
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-2">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-700 font-bold text-sm">
              {c.name.split(" ").map(n => n[0]).join("").slice(0, 2)}
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <h3 className="font-semibold text-slate-900 text-sm">{c.name}</h3>
                {c.linked_token_id && <Link2 className="w-3 h-3 text-purple-500" />}
              </div>
              <p className="text-xs text-slate-500">{c.poste}{c.department ? ` — ${c.department}` : ""}</p>
            </div>
          </div>
          <Badge className={`${stage.color} text-xs`}>{stage.label}</Badge>
        </div>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5 flex-wrap">
            <Badge className={`${RISK_COLORS[c.risk_level] || RISK_COLORS.faible} text-[10px]`}>{c.risk_level}</Badge>
            {c.synced && <Badge className="bg-green-100 text-green-700 text-[10px]"><CheckCircle2 className="w-2.5 h-2.5 mr-0.5" />Sync</Badge>}
            {c.has_dclic && <Badge className="bg-indigo-100 text-indigo-700 text-[10px]"><Brain className="w-2.5 h-2.5 mr-0.5" />D'CLIC</Badge>}
            {(c.skills||[]).length > 0 && <Badge variant="secondary" className="text-[10px]"><Award className="w-2.5 h-2.5 mr-0.5" />{c.skills.length}</Badge>}
          </div>
          <ChevronRight className="w-4 h-4 text-slate-300" />
        </div>
        {c.next_action && <p className="text-xs text-amber-600 mt-2 flex items-center gap-1"><Zap className="w-3 h-3" />{c.next_action}</p>}
      </CardContent>
    </Card>
  );
};

const CollabDetail = ({ c, onBack, token, onRefresh }) => {
  const [tab, setTab] = useState("synthese");
  const [linkedProfile, setLinkedProfile] = useState(null);
  const [loadingProfile, setLoadingProfile] = useState(false);
  const [resyncing, setResyncing] = useState(false);
  const [linkDialogOpen, setLinkDialogOpen] = useState(false);
  const [actionDialogOpen, setActionDialogOpen] = useState(false);

  const stage = STAGES.find(s => s.key === c.stage) || STAGES[0];

  useEffect(() => {
    if (c.linked_token_id) {
      setLoadingProfile(true);
      axios.get(`${API}/entreprise/collaborateurs/${c.id}/linked-profile?token=${token}`)
        .then(r => setLinkedProfile(r.data)).catch(() => {}).finally(() => setLoadingProfile(false));
    }
  }, [c.linked_token_id, c.id, token]);

  const updateField = async (field, value) => {
    try {
      await axios.put(`${API}/entreprise/collaborateurs/${c.id}?token=${token}`, { [field]: value });
      toast.success("Mis a jour");
      onRefresh();
    } catch { toast.error("Erreur"); }
  };

  const syncProfile = async () => {
    setResyncing(true);
    try {
      await axios.post(`${API}/entreprise/collaborateurs/${c.id}/sync?token=${token}`);
      toast.success("Synchronisé !");
      onRefresh();
    } catch (err) { toast.error(err.response?.data?.detail || "Erreur"); }
    setResyncing(false);
  };

  const deleteCollab = async () => {
    if (!window.confirm("Supprimer ce collaborateur ?")) return;
    try {
      await axios.delete(`${API}/entreprise/collaborateurs/${c.id}?token=${token}`);
      toast.success("Supprimé");
      onBack();
    } catch { toast.error("Erreur"); }
  };

  return (
    <div className="space-y-4" data-testid="collab-detail">
      <Button variant="ghost" onClick={onBack} className="-ml-2 text-slate-500" data-testid="back-btn">
        <ChevronRight className="w-4 h-4 rotate-180 mr-1" /> Retour
      </Button>

      {/* Header */}
      <Card className="border border-slate-100">
        <CardContent className="p-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-700 font-bold text-lg">
                {c.name.split(" ").map(n => n[0]).join("").slice(0, 2)}
              </div>
              <div>
                <div className="flex items-center gap-2 flex-wrap">
                  <h2 className="text-xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>{c.name}</h2>
                  {c.linked_token_id && <Badge className="bg-purple-100 text-purple-700 text-xs"><Link2 className="w-3 h-3 mr-1" />Lie</Badge>}
                  {c.synced && <Badge className="bg-green-100 text-green-700 text-xs"><CheckCircle2 className="w-3 h-3 mr-1" />Sync</Badge>}
                </div>
                <p className="text-sm text-slate-500">{c.poste}{c.department ? ` — ${c.department}` : ""}</p>
                <div className="flex items-center gap-2 mt-1">
                  <Badge className={`${stage.color} text-xs`}>{stage.label}</Badge>
                  <Badge className={`${RISK_COLORS[c.risk_level]} text-xs`}>Risque {c.risk_level}</Badge>
                  {c.consent_level && <Badge variant="secondary" className="text-xs">Consentement {c.consent_level}</Badge>}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2 flex-wrap">
              {c.linked_token_id ? (
                <>
                  <Button size="sm" variant="outline" onClick={syncProfile} disabled={resyncing} className="text-green-600" data-testid="sync-btn">
                    {resyncing ? <Loader2 className="w-4 h-4 mr-1 animate-spin" /> : <ArrowUpRight className="w-4 h-4 mr-1" />}Synchroniser
                  </Button>
                  <Button size="sm" variant="outline" className="text-red-500"
                    onClick={async () => { await axios.delete(`${API}/entreprise/collaborateurs/${c.id}/link?token=${token}`); toast.success("Délié"); onRefresh(); }}
                    data-testid="unlink-btn"><Unlink className="w-4 h-4 mr-1" />Delier</Button>
                </>
              ) : (
                <Button size="sm" variant="outline" onClick={() => setLinkDialogOpen(true)} data-testid="link-btn">
                  <Link2 className="w-4 h-4 mr-1" />Lier un profil
                </Button>
              )}
              <Button size="sm" className="bg-emerald-600 hover:bg-emerald-700" onClick={() => setActionDialogOpen(true)} data-testid="action-rh-btn">
                <Zap className="w-4 h-4 mr-1" />Action RH
              </Button>
              <Button size="sm" variant="outline" className="text-red-500" onClick={deleteCollab} data-testid="delete-btn"><Trash2 className="w-4 h-4" /></Button>
            </div>
          </div>
          {c.next_action && <div className="mt-3 p-2.5 rounded-lg bg-amber-50 border border-amber-200 text-sm text-amber-700 flex items-center gap-2"><Zap className="w-4 h-4" />Prochaine action : {c.next_action}</div>}
        </CardContent>
      </Card>

      {/* Tabs */}
      <Tabs value={tab} onValueChange={setTab}>
        <TabsList className="bg-slate-100 border border-slate-200 h-auto gap-1 p-1 flex-wrap">
          <TabsTrigger value="synthese" data-testid="tab-synthese"><Eye className="w-3.5 h-3.5 mr-1" />Synthese</TabsTrigger>
          <TabsTrigger value="parcours" data-testid="tab-parcours"><GitBranch className="w-3.5 h-3.5 mr-1" />Parcours</TabsTrigger>
          <TabsTrigger value="competences" data-testid="tab-competences"><Award className="w-3.5 h-3.5 mr-1" />Compétences</TabsTrigger>
          <TabsTrigger value="aspirations" data-testid="tab-aspirations"><Lightbulb className="w-3.5 h-3.5 mr-1" />Aspirations</TabsTrigger>
          {c.linked_token_id && <TabsTrigger value="profil_reactif" data-testid="tab-profil"><Brain className="w-3.5 h-3.5 mr-1" />Profil RE'ACTIF</TabsTrigger>}
        </TabsList>

        <TabsContent value="synthese" className="mt-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card className="border border-slate-100">
              <CardHeader className="pb-3"><CardTitle className="text-base">Informations</CardTitle></CardHeader>
              <CardContent className="space-y-2.5 text-sm">
                <Row label="Poste" value={c.poste} />
                <Row label="Département" value={c.department || "—"} />
                <Row label="Parcours" value={PARCOURS.find(p => p.key === c.parcours_type)?.label || "—"} />
                <Row label="Satisfaction" value={<span className="flex items-center gap-1">{SAT_LABELS[c.satisfaction] || "—"} <span className="text-amber-500">{"★".repeat(c.satisfaction || 0)}</span></span>} />
                <Row label="Intention mobilité" value={c.mobility_intent || "—"} />
                <Row label="Profil lié" value={c.linked_pseudo ? `@${c.linked_pseudo}` : "Non"} />
                <Row label="Sources sync" value={(c.sync_sources||[]).join(", ") || "—"} />
              </CardContent>
            </Card>
            <Card className="border border-slate-100">
              <CardHeader className="pb-3"><CardTitle className="text-base">Gestion RH</CardTitle></CardHeader>
              <CardContent className="space-y-3">
                <div className="space-y-1">
                  <label className="text-xs font-medium text-slate-600">Étape du parcours</label>
                  <Select value={c.stage} onValueChange={v => updateField("stage", v)}>
                    <SelectTrigger className="h-9"><SelectValue /></SelectTrigger>
                    <SelectContent>{STAGES.map(s => <SelectItem key={s.key} value={s.key}>{s.label}</SelectItem>)}</SelectContent>
                  </Select>
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-medium text-slate-600">Niveau de risque</label>
                  <Select value={c.risk_level} onValueChange={v => updateField("risk_level", v)}>
                    <SelectTrigger className="h-9"><SelectValue /></SelectTrigger>
                    <SelectContent>{RISKS.map(r => <SelectItem key={r} value={r}>{r.charAt(0).toUpperCase() + r.slice(1)}</SelectItem>)}</SelectContent>
                  </Select>
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-medium text-slate-600">Type de parcours</label>
                  <Select value={c.parcours_type} onValueChange={v => updateField("parcours_type", v)}>
                    <SelectTrigger className="h-9"><SelectValue /></SelectTrigger>
                    <SelectContent>{PARCOURS.map(p => <SelectItem key={p.key} value={p.key}>{p.label}</SelectItem>)}</SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="parcours" className="mt-4">
          <Card className="border border-slate-100">
            <CardHeader className="pb-3"><CardTitle className="text-base flex items-center gap-2"><History className="w-4 h-4 text-emerald-600" />Parcours chronologique</CardTitle></CardHeader>
            <CardContent>
              {!(c.timeline||[]).length ? <p className="text-sm text-slate-400 text-center py-8">Aucun événement</p> : (
                <div className="relative pl-6 space-y-4">
                  <div className="absolute left-2.5 top-0 bottom-0 w-0.5 bg-slate-200" />
                  {[...(c.timeline||[])].reverse().slice(0, 30).map((t, i) => (
                    <div key={i} className="relative">
                      <div className={`absolute -left-3.5 w-3 h-3 rounded-full border-2 border-white ${
                        t.source === "systeme" ? "bg-purple-500" : t.source === "espace_personnel" ? "bg-blue-500" : "bg-emerald-500"
                      }`} />
                      <div className="bg-slate-50 rounded-lg p-3 border border-slate-100">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs text-slate-400">{new Date(t.date).toLocaleDateString('fr-FR', { day: '2-digit', month: 'long', year: 'numeric' })}</span>
                          <Badge variant="secondary" className="text-[10px]">{t.source || "rh"}</Badge>
                        </div>
                        <p className="text-sm text-slate-700">{t.detail || t.type}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="competences" className="mt-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card className="border border-slate-100">
              <CardHeader className="pb-3"><CardTitle className="text-base">Hard Skills ({(c.skills||[]).length})</CardTitle></CardHeader>
              <CardContent><div className="flex flex-wrap gap-2">{(c.skills||[]).map((s,i) => <Badge key={i} className="bg-emerald-50 text-emerald-700 border-emerald-200">{s}</Badge>)}{!(c.skills||[]).length && <p className="text-sm text-slate-400">Aucune</p>}</div></CardContent>
            </Card>
            <Card className="border border-slate-100">
              <CardHeader className="pb-3"><CardTitle className="text-base">Soft Skills D'CLIC PRO</CardTitle></CardHeader>
              <CardContent>
                {(c.soft_skills||[]).length === 0 ? <p className="text-sm text-slate-400">Aucune</p> : (
                  <div className="space-y-2">{(c.soft_skills||[]).map((ss, i) => (
                    <div key={i} className="flex items-center justify-between">
                      <span className="text-sm text-slate-700">{typeof ss === "object" ? ss.name : ss}</span>
                      {typeof ss === "object" && ss.score && <div className="flex items-center gap-2"><div className="w-24 h-2 bg-slate-100 rounded-full overflow-hidden"><div className="h-full bg-emerald-500 rounded-full" style={{width: `${ss.score}%`}} /></div><span className="text-xs text-slate-500 w-8">{ss.score}</span></div>}
                    </div>
                  ))}</div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="aspirations" className="mt-4">
          <Card className="border border-slate-100">
            <CardHeader className="pb-3"><CardTitle className="text-base flex items-center gap-2"><Lightbulb className="w-4 h-4 text-amber-600" />Aspirations & signaux faibles</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              {(c.aspirations||[]).length > 0 && <div className="space-y-2">{(c.aspirations||[]).map((a,i) => (
                <div key={i} className="flex items-start gap-3 p-3 bg-amber-50 rounded-lg border border-amber-100">
                  <Target className="w-4 h-4 text-amber-600 mt-0.5" />
                  <div><p className="text-xs text-amber-600 font-medium">{a.type === "projet_pro" ? "Projet professionnel" : a.type === "secteurs" ? "Secteurs vises" : a.type}</p><p className="text-sm text-slate-700">{a.value}</p></div>
                </div>
              ))}</div>}
              {c.mobility_intent && <div className="p-3 bg-blue-50 rounded-lg border border-blue-100"><p className="text-xs text-blue-600 font-medium mb-1">Intention de mobilité</p><p className="text-sm text-slate-700">{c.mobility_intent}</p></div>}
              <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                <p className="text-xs text-slate-500 font-medium mb-1">Satisfaction</p>
                <div className="flex items-center gap-2"><span className="text-amber-500 text-lg">{"★".repeat(c.satisfaction || 0)}{"☆".repeat(5 - (c.satisfaction || 0))}</span><span className="text-sm text-slate-600">{SAT_LABELS[c.satisfaction] || ""}</span></div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {c.linked_token_id && (
          <TabsContent value="profil_reactif" className="mt-4">
            {loadingProfile ? <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-emerald-600" /></div> : !linkedProfile ? <p className="text-sm text-slate-400 text-center py-8">Profil non disponible</p> : (
              <LinkedProfileContent data={linkedProfile} pseudo={c.linked_pseudo} />
            )}
          </TabsContent>
        )}
      </Tabs>

      <LinkDialog open={linkDialogOpen} onOpenChange={setLinkDialogOpen} token={token} collabId={c.id} onDone={onRefresh} />
      <ActionRHDialog open={actionDialogOpen} onOpenChange={setActionDialogOpen} token={token} collabId={c.id} collabName={c.name} onDone={onRefresh} />
    </div>
  );
};

const Row = ({ label, value }) => <div className="flex justify-between"><span className="text-slate-500">{label}</span><span className="font-medium text-right">{value}</span></div>;

const LinkedProfileContent = ({ data, pseudo }) => {
  const { profile, passport, dclic_results, cv_analyses } = data;
  return (
    <div className="space-y-4" data-testid="linked-profile-view">
      <Card className="border-l-4 border-l-emerald-500 border border-slate-100">
        <CardHeader className="pb-3"><CardTitle className="text-base flex items-center gap-2"><Eye className="w-5 h-5 text-emerald-600" />Profil RE'ACTIF PRO — @{pseudo}</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          {profile && <div><h4 className="text-sm font-semibold mb-2">Compétences ({(profile.skills||[]).length})</h4><div className="flex flex-wrap gap-1.5">{(profile.skills||[]).slice(0,20).map((s,i) => <Badge key={i} variant="secondary" className="text-xs">{typeof s === "object" ? s.name : s}</Badge>)}</div></div>}
          {passport && <div className="border-t border-slate-100 pt-4"><h4 className="text-sm font-semibold mb-2 flex items-center gap-1.5"><BookOpen className="w-4 h-4" />Passeport</h4>{passport.career_project && <div className="bg-slate-50 p-3 rounded-lg"><p className="text-xs text-slate-500 mb-1">Projet professionnel</p><p className="text-sm">{passport.career_project}</p></div>}</div>}
          {dclic_results?.scores && <div className="border-t border-slate-100 pt-4"><h4 className="text-sm font-semibold mb-2 flex items-center gap-1.5"><Brain className="w-4 h-4" />D'CLIC PRO</h4><div className="grid grid-cols-2 sm:grid-cols-4 gap-2">{Object.entries(dclic_results.scores).filter(([,v]) => typeof v === "number").map(([k,v]) => <div key={k} className="bg-slate-50 rounded-lg p-2 text-center"><p className="text-xs text-slate-500 capitalize">{k.replace(/_/g, " ")}</p><p className="text-lg font-bold text-emerald-700">{v}</p></div>)}</div></div>}
          {cv_analyses?.length > 0 && <div className="border-t border-slate-100 pt-4"><h4 className="text-sm font-semibold mb-2"><FileText className="w-4 h-4 inline mr-1" />{cv_analyses.length} CV analyse{cv_analyses.length > 1 ? "s" : ""}</h4></div>}
        </CardContent>
      </Card>
    </div>
  );
};

const CreateCollabDialog = ({ open, onOpenChange, token, onCreated }) => {
  const [name, setName] = useState("");
  const [poste, setPoste] = useState("");
  const [dept, setDept] = useState("");
  const [parcours, setParcours] = useState("autre");
  const [creating, setCreating] = useState(false);

  const handle = async () => {
    if (!name.trim()) { toast.error("Nom obligatoire"); return; }
    setCreating(true);
    try {
      await axios.post(`${API}/entreprise/collaborateurs?token=${token}`, { name: name.trim(), poste: poste.trim() || "Non précisé", department: dept.trim(), parcours_type: parcours });
      toast.success("Collaborateur ajoute");
      setName(""); setPoste(""); setDept(""); setParcours("autre");
      onOpenChange(false); onCreated();
    } catch (err) { toast.error(err.response?.data?.detail || "Erreur"); }
    setCreating(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]" data-testid="create-collab-dialog">
        <DialogHeader><DialogTitle>Ajouter un collaborateur</DialogTitle></DialogHeader>
        <div className="space-y-3 mt-2">
          <div><label className="text-sm font-medium">Nom *</label><Input placeholder="Prenom Nom" value={name} onChange={e => setName(e.target.value)} data-testid="create-name" /></div>
          <div><label className="text-sm font-medium">Poste</label><Input placeholder="Ex: Developpeur" value={poste} onChange={e => setPoste(e.target.value)} /></div>
          <div><label className="text-sm font-medium">Département</label><Input placeholder="Ex: IT, RH, Production" value={dept} onChange={e => setDept(e.target.value)} /></div>
          <div><label className="text-sm font-medium">Type de parcours</label>
            <Select value={parcours} onValueChange={setParcours}><SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>{PARCOURS.map(p => <SelectItem key={p.key} value={p.key}>{p.label}</SelectItem>)}</SelectContent></Select></div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>Annuler</Button>
          <Button onClick={handle} disabled={creating} className="bg-emerald-600 hover:bg-emerald-700" data-testid="submit-create">
            {creating ? <Loader2 className="w-4 h-4 mr-1 animate-spin" /> : <Plus className="w-4 h-4 mr-1" />}Ajouter
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

const DemandeAccesDialog = ({ open, onOpenChange, token, onDone }) => {
  const [q, setQ] = useState(""); const [results, setResults] = useState([]); const [searching, setSearching] = useState(false); const [requesting, setRequesting] = useState(null);
  const search = async () => { if (q.length < 2) return; setSearching(true); try { const r = await axios.get(`${API}/entreprise/demande-acces/search?token=${token}&query=${encodeURIComponent(q)}`); setResults(r.data); } catch {} setSearching(false); };
  const sendReq = async (u) => { setRequesting(u.token_id); try { await axios.post(`${API}/entreprise/demande-acces/request?token=${token}`, { user_token_id: u.token_id }); toast.success(`Demande envoyee a ${u.full_name}`); onDone(); } catch (err) { toast.error(err.response?.data?.detail || "Erreur"); } setRequesting(null); };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]" data-testid="demande-acces-dialog">
        <DialogHeader><DialogTitle className="flex items-center gap-2"><Search className="w-5 h-5 text-emerald-600" />Demande d'acces candidat</DialogTitle><DialogDescription>Recherchez un utilisateur RE'ACTIF PRO</DialogDescription></DialogHeader>
        <div className="space-y-3 mt-2">
          <div className="flex gap-2">
            <Input placeholder="Nom, prenom ou pseudo..." value={q} onChange={e => setQ(e.target.value)} onKeyDown={e => { if (e.key === "Enter") search(); }} data-testid="demande-search-input" />
            <Button onClick={search} disabled={searching || q.length < 2} variant="outline">{searching ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}</Button>
          </div>
          {results.length > 0 && <div className="space-y-2 max-h-60 overflow-y-auto">{results.map(u => (
            <div key={u.token_id} className="flex items-center justify-between p-3 rounded-lg border border-slate-100 hover:bg-slate-50">
              <div><p className="text-sm font-medium">{u.full_name} <span className="text-slate-400">@{u.pseudo}</span></p><div className="flex gap-1.5 mt-0.5">{u.has_dclic && <Badge className="bg-indigo-100 text-indigo-700 text-[10px]">D'CLIC</Badge>}<span className="text-xs text-slate-500">{u.skills_count} comp.</span></div></div>
              <Button size="sm" className="bg-emerald-600 hover:bg-emerald-700 h-8 text-xs" onClick={() => sendReq(u)} disabled={requesting === u.token_id}>
                {requesting === u.token_id ? <Loader2 className="w-3 h-3 mr-1 animate-spin" /> : <Send className="w-3 h-3 mr-1" />}Envoyer
              </Button>
            </div>
          ))}</div>}
        </div>
      </DialogContent>
    </Dialog>
  );
};

const LinkDialog = ({ open, onOpenChange, token, collabId, onDone }) => {
  const [q, setQ] = useState(""); const [results, setResults] = useState([]); const [searching, setSearching] = useState(false);
  const search = async () => { if (q.length < 2) return; setSearching(true); try { const r = await axios.get(`${API}/entreprise/search-users?token=${token}&query=${encodeURIComponent(q)}`); setResults(r.data); } catch {} setSearching(false); };
  const link = async (pseudo) => { try { await axios.post(`${API}/entreprise/collaborateurs/${collabId}/link?token=${token}&pseudo=${encodeURIComponent(pseudo)}`); toast.success("Lié !"); onOpenChange(false); onDone(); } catch (err) { toast.error(err.response?.data?.detail || "Erreur"); } };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]" data-testid="link-dialog">
        <DialogHeader><DialogTitle><Link2 className="w-5 h-5 inline mr-2 text-purple-600" />Lier a un profil RE'ACTIF PRO</DialogTitle></DialogHeader>
        <div className="space-y-3 mt-2">
          <div className="flex gap-2">
            <Input placeholder="Rechercher un pseudo..." value={q} onChange={e => setQ(e.target.value)} onKeyDown={e => { if (e.key === "Enter") search(); }} data-testid="link-search" />
            <Button onClick={search} disabled={searching || q.length < 2} variant="outline">{searching ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}</Button>
          </div>
          {results.length > 0 && <div className="space-y-2 max-h-60 overflow-y-auto">{results.map(u => (
            <div key={u.pseudo} className="flex items-center justify-between p-3 rounded-lg border border-slate-100 hover:bg-slate-50">
              <div><p className="text-sm font-medium">{u.display_name} <span className="text-slate-400">@{u.pseudo}</span></p><p className="text-xs text-slate-500">{u.skills_count} comp.</p></div>
              <Button size="sm" className="bg-emerald-600 hover:bg-emerald-700" onClick={() => link(u.pseudo)} data-testid={`link-${u.pseudo}`}><Link2 className="w-3 h-3 mr-1" />Lier</Button>
            </div>
          ))}</div>}
        </div>
      </DialogContent>
    </Dialog>
  );
};

const ActionRHDialog = ({ open, onOpenChange, token, collabId, collabName, onDone }) => {
  const [actionType, setActionType] = useState("proposer_mobilite");
  const [detail, setDetail] = useState("");
  const [sending, setSending] = useState(false);
  const actions = [
    { key: "proposer_mobilite", label: "Proposer mobilité interne" },
    { key: "proposer_formation", label: "Proposer formation" },
    { key: "lancer_accompagnement", label: "Lancer accompagnement" },
    { key: "export_dossier", label: "Exporter le dossier" },
    { key: "entretien_pro", label: "Programmer entretien professionnel" },
  ];
  const handle = async () => {
    setSending(true);
    try { await axios.post(`${API}/entreprise/collaborateurs/${collabId}/action?token=${token}`, { action_type: actionType, detail }); toast.success("Action enregistrée"); setDetail(""); onOpenChange(false); onDone(); } catch { toast.error("Erreur"); }
    setSending(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]" data-testid="action-rh-dialog">
        <DialogHeader><DialogTitle>Action RH — {collabName}</DialogTitle><DialogDescription>Choisissez une action a entreprendre</DialogDescription></DialogHeader>
        <div className="space-y-3 mt-2">
          <Select value={actionType} onValueChange={setActionType}><SelectTrigger><SelectValue /></SelectTrigger>
            <SelectContent>{actions.map(a => <SelectItem key={a.key} value={a.key}>{a.label}</SelectItem>)}</SelectContent></Select>
          <Textarea placeholder="Detail (optionnel)..." value={detail} onChange={e => setDetail(e.target.value)} className="resize-none h-20" />
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>Annuler</Button>
          <Button onClick={handle} disabled={sending} className="bg-emerald-600 hover:bg-emerald-700" data-testid="submit-action">
            {sending ? <Loader2 className="w-4 h-4 mr-1 animate-spin" /> : <Zap className="w-4 h-4 mr-1" />}Executer
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default CollaborateursView;

