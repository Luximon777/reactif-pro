import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Handshake, Users, TrendingUp, Plus, Eye, CheckCircle2, Clock,
  AlertTriangle, BarChart3, Target, FileText, ArrowUpRight, Calendar,
  Home as HomeIcon, Car, Heart, Baby, Accessibility, FileWarning,
  Wallet, HelpCircle, Trash2, ChevronRight, History, Award,
  X, PlusCircle, Shield
} from "lucide-react";
import { toast } from "sonner";

const FREIN_CATEGORIES = [
  { value: "logement", label: "Logement", icon: HomeIcon, color: "bg-orange-100 text-orange-700 border-orange-200" },
  { value: "sante", label: "Santé", icon: Heart, color: "bg-red-100 text-red-700 border-red-200" },
  { value: "mobilite", label: "Mobilité", icon: Car, color: "bg-blue-100 text-blue-700 border-blue-200" },
  { value: "garde_enfant", label: "Garde d'enfant", icon: Baby, color: "bg-pink-100 text-pink-700 border-pink-200" },
  { value: "handicap", label: "Handicap / RQTH", icon: Accessibility, color: "bg-purple-100 text-purple-700 border-purple-200" },
  { value: "administratif", label: "Administratif", icon: FileWarning, color: "bg-slate-100 text-slate-700 border-slate-200" },
  { value: "financier", label: "Financier", icon: Wallet, color: "bg-amber-100 text-amber-700 border-amber-200" },
  { value: "autre", label: "Autre", icon: HelpCircle, color: "bg-gray-100 text-gray-700 border-gray-200" },
];

const STATUS_OPTIONS = [
  { value: "En attente", color: "bg-slate-100 text-slate-700 border-slate-200", icon: Clock },
  { value: "En accompagnement", color: "bg-blue-100 text-blue-700 border-blue-200", icon: Users },
  { value: "Formation en cours", color: "bg-amber-100 text-amber-700 border-amber-200", icon: Target },
  { value: "Recherche d'emploi", color: "bg-[#1e3a5f]/10 text-[#1e3a5f] border-[#1e3a5f]/20", icon: Eye },
  { value: "En emploi", color: "bg-green-100 text-green-700 border-green-200", icon: CheckCircle2 },
];

const PartenaireView = ({ token }) => {
  const [beneficiaires, setBeneficiaires] = useState([]);
  const [stats, setStats] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("dashboard");
  const [selectedBeneficiaire, setSelectedBeneficiaire] = useState(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [freinDialogOpen, setFreinDialogOpen] = useState(false);
  const [freinTarget, setFreinTarget] = useState(null);

  useEffect(() => {
    loadAll();
  }, [token]);

  const loadAll = async () => {
    setLoading(true);
    try {
      const [bRes, sRes, pRes] = await Promise.all([
        axios.get(`${API}/partenaires/beneficiaires?token=${token}`),
        axios.get(`${API}/partenaires/stats?token=${token}`),
        axios.get(`${API}/partenaires/profile?token=${token}`),
      ]);
      setBeneficiaires(bRes.data);
      setStats(sRes.data);
      setProfile(pRes.data);
    } catch (err) {
      console.error("Erreur chargement:", err);
    }
    setLoading(false);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64" data-testid="partenaire-loading">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#1e3a5f]"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in" data-testid="partenaire-dashboard">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>
            Espace Partenaires de Parcours
          </h1>
          <p className="text-slate-500 mt-1 text-sm">
            {profile?.company_name && (
              <span className="font-medium text-[#1e3a5f]">{profile.company_name}</span>
            )}
            {profile?.company_name && " — "}
            Accompagnement et sécurisation des transitions professionnelles
          </p>
        </div>
        <Button
          onClick={() => setCreateDialogOpen(true)}
          className="bg-[#1e3a5f] hover:bg-[#152a45]"
          data-testid="add-beneficiaire-btn"
        >
          <Plus className="w-4 h-4 mr-2" />
          Nouveau bénéficiaire
        </Button>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="bg-slate-100 border border-slate-200">
          <TabsTrigger value="dashboard" data-testid="tab-dashboard">
            <BarChart3 className="w-4 h-4 mr-1.5" /> Tableau de bord
          </TabsTrigger>
          <TabsTrigger value="beneficiaires" data-testid="tab-beneficiaires">
            <Users className="w-4 h-4 mr-1.5" /> Bénéficiaires
          </TabsTrigger>
          <TabsTrigger value="freins" data-testid="tab-freins">
            <AlertTriangle className="w-4 h-4 mr-1.5" /> Freins périphériques
          </TabsTrigger>
        </TabsList>

        {/* TAB: Dashboard */}
        <TabsContent value="dashboard" className="space-y-6 mt-4">
          <StatsCards stats={stats} />
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <RecentActivity beneficiaires={beneficiaires} onSelect={(b) => { setSelectedBeneficiaire(b); setActiveTab("beneficiaires"); }} />
            <FreinsSummary beneficiaires={beneficiaires} />
          </div>
        </TabsContent>

        {/* TAB: Beneficiaires */}
        <TabsContent value="beneficiaires" className="space-y-4 mt-4">
          <BeneficiairesList
            beneficiaires={beneficiaires}
            token={token}
            onRefresh={loadAll}
            selectedBeneficiaire={selectedBeneficiaire}
            setSelectedBeneficiaire={setSelectedBeneficiaire}
            onAddFrein={(b) => { setFreinTarget(b); setFreinDialogOpen(true); }}
          />
        </TabsContent>

        {/* TAB: Freins */}
        <TabsContent value="freins" className="space-y-4 mt-4">
          <FreinsView
            beneficiaires={beneficiaires}
            token={token}
            onRefresh={loadAll}
          />
        </TabsContent>
      </Tabs>

      {/* Create Dialog */}
      <CreateBeneficiaireDialog
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
        token={token}
        onCreated={loadAll}
      />

      {/* Add Frein Dialog */}
      <AddFreinDialog
        open={freinDialogOpen}
        onOpenChange={setFreinDialogOpen}
        beneficiaire={freinTarget}
        token={token}
        onAdded={loadAll}
      />
    </div>
  );
};

// ===== STATS CARDS =====
const StatsCards = ({ stats }) => {
  if (!stats) return null;
  const metrics = [
    { title: "Personnes accompagnées", value: stats.total, icon: Users, accent: "bg-[#1e3a5f]/10 text-[#1e3a5f]" },
    { title: "Accompagnement actif", value: stats.en_accompagnement, icon: Handshake, accent: "bg-blue-100 text-blue-600" },
    { title: "Insertions réussies", value: stats.en_emploi, icon: CheckCircle2, accent: "bg-green-100 text-green-600" },
    { title: "Taux d'insertion", value: `${stats.taux_insertion}%`, icon: TrendingUp, accent: "bg-amber-100 text-amber-600" },
    { title: "Freins actifs", value: stats.freins_actifs, icon: AlertTriangle, accent: "bg-red-100 text-red-600" },
    { title: "Freins résolus", value: stats.freins_resolus, icon: Shield, accent: "bg-emerald-100 text-emerald-600" },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3" data-testid="partenaire-metrics">
      {metrics.map((m, idx) => {
        const Icon = m.icon;
        return (
          <Card key={idx} className="border border-slate-100 hover:border-[#1e3a5f]/20 transition-all" data-testid={`metric-${idx}`}>
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <div className={`w-8 h-8 rounded-lg ${m.accent} flex items-center justify-center`}>
                  <Icon className="w-4 h-4" />
                </div>
              </div>
              <p className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>{m.value}</p>
              <p className="text-xs text-slate-500 mt-0.5">{m.title}</p>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
};

// ===== RECENT ACTIVITY =====
const RecentActivity = ({ beneficiaires, onSelect }) => {
  const recent = [...beneficiaires]
    .sort((a, b) => new Date(b.last_activity || 0) - new Date(a.last_activity || 0))
    .slice(0, 5);

  return (
    <Card className="lg:col-span-2 border border-slate-100" data-testid="recent-activity">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Calendar className="w-5 h-5 text-[#1e3a5f]" />
          Activité récente
        </CardTitle>
        <CardDescription>Derniers parcours mis à jour</CardDescription>
      </CardHeader>
      <CardContent>
        {recent.length === 0 ? (
          <p className="text-sm text-slate-400 text-center py-8">Aucun bénéficiaire pour le moment</p>
        ) : (
          <div className="space-y-3">
            {recent.map((b) => {
              const st = STATUS_OPTIONS.find(s => s.value === b.status) || STATUS_OPTIONS[0];
              const StIcon = st.icon;
              return (
                <div
                  key={b.id}
                  className="flex items-center justify-between p-3 rounded-xl border border-slate-100 hover:border-[#1e3a5f]/20 hover:bg-slate-50/50 transition-all cursor-pointer"
                  onClick={() => onSelect(b)}
                  data-testid={`recent-${b.id}`}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-full bg-[#1e3a5f]/10 flex items-center justify-center">
                      <Users className="w-4 h-4 text-[#1e3a5f]" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-900">{b.name}</p>
                      <p className="text-xs text-slate-400">{b.sector}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge className={`${st.color} text-xs flex items-center gap-1`}>
                      <StIcon className="w-3 h-3" /> {b.status}
                    </Badge>
                    <ChevronRight className="w-4 h-4 text-slate-300" />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// ===== FREINS SUMMARY =====
const FreinsSummary = ({ beneficiaires }) => {
  const allFreins = beneficiaires.flatMap(b => (b.freins || []).map(f => ({ ...f, beneficiaire: b.name })));
  const activeFreins = allFreins.filter(f => f.status !== "resolu");

  const categoryCounts = {};
  activeFreins.forEach(f => {
    categoryCounts[f.category] = (categoryCounts[f.category] || 0) + 1;
  });

  return (
    <Card className="border border-slate-100" data-testid="freins-summary">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <AlertTriangle className="w-5 h-5 text-amber-600" />
          Freins périphériques
        </CardTitle>
        <CardDescription>{activeFreins.length} frein{activeFreins.length > 1 ? "s" : ""} actif{activeFreins.length > 1 ? "s" : ""}</CardDescription>
      </CardHeader>
      <CardContent>
        {activeFreins.length === 0 ? (
          <p className="text-sm text-slate-400 text-center py-6">Aucun frein actif</p>
        ) : (
          <div className="space-y-2">
            {FREIN_CATEGORIES.filter(c => categoryCounts[c.value]).map(cat => {
              const Icon = cat.icon;
              return (
                <div key={cat.value} className="flex items-center justify-between p-2.5 rounded-lg bg-slate-50 border border-slate-100">
                  <div className="flex items-center gap-2">
                    <div className={`w-7 h-7 rounded-md ${cat.color} flex items-center justify-center`}>
                      <Icon className="w-3.5 h-3.5" />
                    </div>
                    <span className="text-sm text-slate-700">{cat.label}</span>
                  </div>
                  <Badge variant="secondary" className="text-xs">{categoryCounts[cat.value]}</Badge>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// ===== BENEFICIAIRES LIST =====
const BeneficiairesList = ({ beneficiaires, token, onRefresh, selectedBeneficiaire, setSelectedBeneficiaire, onAddFrein }) => {
  const [filter, setFilter] = useState("all");

  const filtered = filter === "all"
    ? beneficiaires
    : beneficiaires.filter(b => b.status === filter);

  const updateStatus = async (id, newStatus) => {
    try {
      await axios.put(`${API}/partenaires/beneficiaires/${id}?token=${token}&status=${encodeURIComponent(newStatus)}`);
      toast.success("Statut mis à jour");
      onRefresh();
    } catch {
      toast.error("Erreur lors de la mise à jour");
    }
  };

  const deleteBeneficiaire = async (id) => {
    try {
      await axios.delete(`${API}/partenaires/beneficiaires/${id}?token=${token}`);
      toast.success("Bénéficiaire supprimé");
      if (selectedBeneficiaire?.id === id) setSelectedBeneficiaire(null);
      onRefresh();
    } catch {
      toast.error("Erreur lors de la suppression");
    }
  };

  const addSkill = async (id, skill) => {
    try {
      await axios.post(`${API}/partenaires/beneficiaires/${id}/skills?token=${token}&skill=${encodeURIComponent(skill)}`);
      toast.success("Compétence ajoutée");
      onRefresh();
    } catch {
      toast.error("Erreur");
    }
  };

  // Detail view
  if (selectedBeneficiaire) {
    const b = beneficiaires.find(x => x.id === selectedBeneficiaire.id) || selectedBeneficiaire;
    return (
      <BeneficiaireDetail
        b={b}
        onBack={() => setSelectedBeneficiaire(null)}
        onUpdateStatus={(s) => updateStatus(b.id, s)}
        onDelete={() => deleteBeneficiaire(b.id)}
        onAddSkill={(s) => addSkill(b.id, s)}
        onAddFrein={() => onAddFrein(b)}
        token={token}
        onRefresh={onRefresh}
      />
    );
  }

  return (
    <div className="space-y-4">
      {/* Filter bar */}
      <div className="flex flex-wrap gap-2" data-testid="status-filter">
        <Button variant={filter === "all" ? "default" : "outline"} size="sm"
          className={filter === "all" ? "bg-[#1e3a5f]" : ""}
          onClick={() => setFilter("all")}>
          Tous ({beneficiaires.length})
        </Button>
        {STATUS_OPTIONS.map(st => {
          const count = beneficiaires.filter(b => b.status === st.value).length;
          if (count === 0) return null;
          return (
            <Button key={st.value} variant={filter === st.value ? "default" : "outline"} size="sm"
              className={filter === st.value ? "bg-[#1e3a5f]" : ""}
              onClick={() => setFilter(st.value)}>
              {st.value} ({count})
            </Button>
          );
        })}
      </div>

      {filtered.length === 0 ? (
        <Card className="border-dashed border-2 border-slate-200">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Users className="w-12 h-12 text-slate-300 mb-3" />
            <p className="text-slate-500 text-sm">Aucun bénéficiaire {filter !== "all" ? "dans cette catégorie" : ""}</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4" data-testid="beneficiaires-list">
          {filtered.map(b => {
            const st = STATUS_OPTIONS.find(s => s.value === b.status) || STATUS_OPTIONS[0];
            const StIcon = st.icon;
            const freinsActifs = (b.freins || []).filter(f => f.status !== "resolu").length;
            return (
              <Card
                key={b.id}
                className="border border-slate-100 hover:border-[#1e3a5f]/20 transition-all cursor-pointer"
                onClick={() => setSelectedBeneficiaire(b)}
                data-testid={`beneficiaire-card-${b.id}`}
              >
                <CardContent className="p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-[#1e3a5f]/10 flex items-center justify-center">
                        <Users className="w-5 h-5 text-[#1e3a5f]" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-slate-900">{b.name}</h3>
                        <p className="text-xs text-slate-500">{b.sector}</p>
                      </div>
                    </div>
                    <Badge className={`${st.color} flex items-center gap-1 text-xs`}>
                      <StIcon className="w-3 h-3" /> {b.status}
                    </Badge>
                  </div>
                  <div className="space-y-2 mb-3">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-500">Progression</span>
                      <span className="font-medium text-slate-800">{b.progress || 0}%</span>
                    </div>
                    <Progress value={b.progress || 0} className="h-1.5" />
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {(b.skills_acquired || []).length > 0 && (
                        <Badge variant="secondary" className="text-xs">
                          <Award className="w-3 h-3 mr-1" />{b.skills_acquired.length} comp.
                        </Badge>
                      )}
                      {freinsActifs > 0 && (
                        <Badge className="bg-amber-100 text-amber-700 border-amber-200 text-xs">
                          <AlertTriangle className="w-3 h-3 mr-1" />{freinsActifs} frein{freinsActifs > 1 ? "s" : ""}
                        </Badge>
                      )}
                    </div>
                    <span className="text-xs text-slate-400">
                      {b.last_activity ? new Date(b.last_activity).toLocaleDateString('fr-FR') : "—"}
                    </span>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
};

// ===== BENEFICIAIRE DETAIL =====
const BeneficiaireDetail = ({ b, onBack, onUpdateStatus, onDelete, onAddSkill, onAddFrein, token, onRefresh }) => {
  const [newSkill, setNewSkill] = useState("");
  const st = STATUS_OPTIONS.find(s => s.value === b.status) || STATUS_OPTIONS[0];
  const StIcon = st.icon;
  const freinsActifs = (b.freins || []).filter(f => f.status !== "resolu");

  const handleResolveFrein = async (freinId) => {
    try {
      await axios.put(`${API}/partenaires/beneficiaires/${b.id}/freins/${freinId}?token=${token}&status=resolu`);
      toast.success("Frein résolu !");
      onRefresh();
    } catch {
      toast.error("Erreur");
    }
  };

  return (
    <div className="space-y-4" data-testid="beneficiaire-detail">
      <Button variant="ghost" onClick={onBack} className="text-slate-500 hover:text-slate-700 -ml-2" data-testid="back-to-list">
        <ChevronRight className="w-4 h-4 rotate-180 mr-1" /> Retour à la liste
      </Button>

      {/* Header */}
      <Card className="border border-slate-100">
        <CardContent className="p-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-full bg-[#1e3a5f]/10 flex items-center justify-center">
                <Users className="w-7 h-7 text-[#1e3a5f]" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>{b.name}</h2>
                <p className="text-sm text-slate-500">Secteur : {b.sector}</p>
                <Badge className={`${st.color} flex items-center gap-1 mt-1 w-fit text-xs`}>
                  <StIcon className="w-3 h-3" /> {b.status}
                </Badge>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Select value={b.status} onValueChange={onUpdateStatus}>
                <SelectTrigger className="w-48 h-9 text-sm" data-testid="detail-status-select">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {STATUS_OPTIONS.map(s => <SelectItem key={s.value} value={s.value}>{s.value}</SelectItem>)}
                </SelectContent>
              </Select>
              <Button variant="outline" size="icon" className="text-red-500 hover:text-red-700 hover:bg-red-50"
                onClick={onDelete} data-testid="delete-beneficiaire-btn">
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          </div>
          {/* Progress */}
          <div className="mt-4 space-y-1.5">
            <div className="flex justify-between text-sm">
              <span className="text-slate-500">Progression du parcours</span>
              <span className="font-medium text-slate-900">{b.progress || 0}%</span>
            </div>
            <Progress value={b.progress || 0} className="h-2" />
          </div>
          {b.notes && <p className="mt-3 text-sm text-slate-600 bg-slate-50 p-3 rounded-lg">{b.notes}</p>}
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Skills */}
        <Card className="border border-slate-100">
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <Award className="w-4 h-4 text-[#1e3a5f]" /> Compétences validées
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2 mb-3">
              {(b.skills_acquired || []).map((skill, i) => (
                <Badge key={i} className="bg-[#1e3a5f]/10 text-[#1e3a5f] border-[#1e3a5f]/20">{skill}</Badge>
              ))}
              {(b.skills_acquired || []).length === 0 && (
                <p className="text-sm text-slate-400">Aucune compétence validée</p>
              )}
            </div>
            <div className="flex gap-2">
              <Input placeholder="Ajouter une compétence..." value={newSkill}
                onChange={e => setNewSkill(e.target.value)}
                onKeyDown={e => { if (e.key === "Enter" && newSkill.trim()) { onAddSkill(newSkill.trim()); setNewSkill(""); } }}
                className="h-8 text-sm" data-testid="add-skill-input" />
              <Button size="sm" variant="outline" className="h-8"
                onClick={() => { if (newSkill.trim()) { onAddSkill(newSkill.trim()); setNewSkill(""); } }}
                data-testid="add-skill-btn">
                <PlusCircle className="w-3.5 h-3.5" />
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Freins */}
        <Card className="border border-slate-100">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-600" /> Freins périphériques
              </CardTitle>
              <Button size="sm" variant="outline" onClick={onAddFrein} data-testid="add-frein-btn">
                <Plus className="w-3.5 h-3.5 mr-1" /> Ajouter
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {freinsActifs.length === 0 && (b.freins || []).filter(f => f.status === "resolu").length === 0 ? (
              <p className="text-sm text-slate-400">Aucun frein déclaré</p>
            ) : (
              <div className="space-y-2">
                {freinsActifs.map(f => {
                  const cat = FREIN_CATEGORIES.find(c => c.value === f.category) || FREIN_CATEGORIES[7];
                  const CIcon = cat.icon;
                  return (
                    <div key={f.id} className="flex items-center justify-between p-2.5 rounded-lg border border-slate-100 bg-slate-50">
                      <div className="flex items-center gap-2">
                        <div className={`w-7 h-7 rounded-md ${cat.color} flex items-center justify-center`}>
                          <CIcon className="w-3.5 h-3.5" />
                        </div>
                        <div>
                          <p className="text-sm font-medium text-slate-700">{cat.label}</p>
                          {f.description && <p className="text-xs text-slate-400">{f.description}</p>}
                        </div>
                      </div>
                      <Button size="sm" variant="outline" className="text-green-600 hover:bg-green-50 h-7 text-xs"
                        onClick={() => handleResolveFrein(f.id)} data-testid={`resolve-frein-${f.id}`}>
                        <CheckCircle2 className="w-3 h-3 mr-1" /> Résoudre
                      </Button>
                    </div>
                  );
                })}
                {(b.freins || []).filter(f => f.status === "resolu").map(f => {
                  const cat = FREIN_CATEGORIES.find(c => c.value === f.category) || FREIN_CATEGORIES[7];
                  return (
                    <div key={f.id} className="flex items-center gap-2 p-2 rounded-lg opacity-50">
                      <CheckCircle2 className="w-4 h-4 text-green-500" />
                      <span className="text-xs text-slate-500 line-through">{cat.label}</span>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Historique */}
      <Card className="border border-slate-100">
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <History className="w-4 h-4 text-[#1e3a5f]" /> Historique du parcours
          </CardTitle>
        </CardHeader>
        <CardContent>
          {(b.historique || []).length === 0 ? (
            <p className="text-sm text-slate-400">Aucun historique</p>
          ) : (
            <div className="space-y-2">
              {[...(b.historique || [])].reverse().slice(0, 10).map((h, i) => (
                <div key={i} className="flex items-start gap-3 text-sm">
                  <div className="w-2 h-2 rounded-full bg-[#1e3a5f] mt-1.5 flex-shrink-0"></div>
                  <div>
                    <span className="text-slate-500 text-xs">{new Date(h.date).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' })}</span>
                    <p className="text-slate-700">{h.detail || h.action}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

// ===== FREINS VIEW (full tab) =====
const FreinsView = ({ beneficiaires, token, onRefresh }) => {
  const allFreins = beneficiaires.flatMap(b =>
    (b.freins || []).map(f => ({ ...f, beneficiaire_name: b.name, beneficiaire_id: b.id }))
  );
  const activeFreins = allFreins.filter(f => f.status !== "resolu");
  const resolvedFreins = allFreins.filter(f => f.status === "resolu");

  const handleResolve = async (benId, freinId) => {
    try {
      await axios.put(`${API}/partenaires/beneficiaires/${benId}/freins/${freinId}?token=${token}&status=resolu`);
      toast.success("Frein résolu !");
      onRefresh();
    } catch {
      toast.error("Erreur");
    }
  };

  return (
    <div className="space-y-6" data-testid="freins-full-view">
      <Card className="border border-slate-100">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-600" />
            Freins actifs ({activeFreins.length})
          </CardTitle>
          <CardDescription>Vue globale des freins périphériques de tous les bénéficiaires</CardDescription>
        </CardHeader>
        <CardContent>
          {activeFreins.length === 0 ? (
            <p className="text-sm text-slate-400 text-center py-8">Aucun frein actif. Bravo !</p>
          ) : (
            <div className="space-y-3">
              {activeFreins.map(f => {
                const cat = FREIN_CATEGORIES.find(c => c.value === f.category) || FREIN_CATEGORIES[7];
                const CIcon = cat.icon;
                return (
                  <div key={f.id} className="flex items-center justify-between p-3 rounded-xl border border-slate-100 hover:bg-slate-50 transition-all">
                    <div className="flex items-center gap-3">
                      <div className={`w-9 h-9 rounded-lg ${cat.color} flex items-center justify-center`}>
                        <CIcon className="w-4 h-4" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-slate-900">{cat.label}</p>
                        <p className="text-xs text-slate-500">
                          {f.beneficiaire_name} {f.description ? `— ${f.description}` : ""}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={
                        f.severity === "critique" ? "bg-red-100 text-red-700" :
                        f.severity === "eleve" ? "bg-orange-100 text-orange-700" :
                        "bg-amber-100 text-amber-700"
                      }>
                        {f.severity || "moyen"}
                      </Badge>
                      <Button size="sm" variant="outline" className="text-green-600 hover:bg-green-50 h-8 text-xs"
                        onClick={() => handleResolve(f.beneficiaire_id, f.id)}>
                        <CheckCircle2 className="w-3 h-3 mr-1" /> Résoudre
                      </Button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {resolvedFreins.length > 0 && (
        <Card className="border border-slate-100">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <CheckCircle2 className="w-5 h-5 text-green-500" />
              Freins résolus ({resolvedFreins.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {resolvedFreins.map(f => {
                const cat = FREIN_CATEGORIES.find(c => c.value === f.category) || FREIN_CATEGORIES[7];
                return (
                  <div key={f.id} className="flex items-center gap-3 p-2 rounded-lg opacity-60">
                    <CheckCircle2 className="w-4 h-4 text-green-500" />
                    <span className="text-sm text-slate-500">{cat.label} — {f.beneficiaire_name}</span>
                    {f.resolved_at && (
                      <span className="text-xs text-slate-400 ml-auto">
                        {new Date(f.resolved_at).toLocaleDateString('fr-FR')}
                      </span>
                    )}
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

// ===== CREATE DIALOG =====
const CreateBeneficiaireDialog = ({ open, onOpenChange, token, onCreated }) => {
  const [name, setName] = useState("");
  const [sector, setSector] = useState("Autre");
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(false);

  const handleCreate = async () => {
    if (!name.trim()) { toast.error("Nom requis"); return; }
    setLoading(true);
    try {
      await axios.post(
        `${API}/partenaires/beneficiaires?token=${token}&name=${encodeURIComponent(name.trim())}&sector=${encodeURIComponent(sector)}&notes=${encodeURIComponent(notes)}`
      );
      toast.success("Bénéficiaire ajouté !");
      setName(""); setSector("Autre"); setNotes("");
      onOpenChange(false);
      onCreated();
    } catch {
      toast.error("Erreur lors de la création");
    }
    setLoading(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[450px]" data-testid="create-beneficiaire-dialog">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Users className="w-5 h-5 text-[#1e3a5f]" />
            Nouveau bénéficiaire
          </DialogTitle>
          <DialogDescription>Créer un suivi d'accompagnement</DialogDescription>
        </DialogHeader>
        <div className="space-y-4 mt-2">
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700">Nom du bénéficiaire *</label>
            <Input placeholder="Prénom Nom" value={name} onChange={e => setName(e.target.value)}
              data-testid="create-name-input" />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700">Secteur visé</label>
            <Select value={sector} onValueChange={setSector}>
              <SelectTrigger data-testid="create-sector-select"><SelectValue /></SelectTrigger>
              <SelectContent>
                {["Administration", "Commerce", "Informatique", "Comptabilité", "Formation", "Santé", "Industrie", "Autre"].map(s =>
                  <SelectItem key={s} value={s}>{s}</SelectItem>
                )}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700">Notes (optionnel)</label>
            <Textarea placeholder="Contexte, observations..." value={notes} onChange={e => setNotes(e.target.value)}
              className="resize-none h-20" data-testid="create-notes-input" />
          </div>
        </div>
        <DialogFooter className="mt-4">
          <Button variant="outline" onClick={() => onOpenChange(false)}>Annuler</Button>
          <Button onClick={handleCreate} disabled={loading || !name.trim()} className="bg-[#1e3a5f] hover:bg-[#152a45]"
            data-testid="create-submit-btn">
            {loading ? "Création..." : "Créer le suivi"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

// ===== ADD FREIN DIALOG =====
const AddFreinDialog = ({ open, onOpenChange, beneficiaire, token, onAdded }) => {
  const [category, setCategory] = useState("");
  const [description, setDescription] = useState("");
  const [severity, setSeverity] = useState("moyen");
  const [loading, setLoading] = useState(false);

  const handleAdd = async () => {
    if (!category || !beneficiaire) return;
    setLoading(true);
    try {
      await axios.post(
        `${API}/partenaires/beneficiaires/${beneficiaire.id}/freins?token=${token}&category=${encodeURIComponent(category)}&description=${encodeURIComponent(description)}&severity=${encodeURIComponent(severity)}`
      );
      toast.success("Frein ajouté");
      setCategory(""); setDescription(""); setSeverity("moyen");
      onOpenChange(false);
      onAdded();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Erreur");
    }
    setLoading(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[450px]" data-testid="add-frein-dialog">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-600" />
            Déclarer un frein périphérique
          </DialogTitle>
          <DialogDescription>
            {beneficiaire ? `Pour ${beneficiaire.name}` : "Sélectionnez un bénéficiaire"}
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 mt-2">
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700">Catégorie *</label>
            <Select value={category} onValueChange={setCategory}>
              <SelectTrigger data-testid="frein-category-select"><SelectValue placeholder="Choisir..." /></SelectTrigger>
              <SelectContent>
                {FREIN_CATEGORIES.map(c => (
                  <SelectItem key={c.value} value={c.value}>{c.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700">Description</label>
            <Textarea placeholder="Détails sur le frein..." value={description} onChange={e => setDescription(e.target.value)}
              className="resize-none h-20" data-testid="frein-description-input" />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700">Sévérité</label>
            <Select value={severity} onValueChange={setSeverity}>
              <SelectTrigger data-testid="frein-severity-select"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="faible">Faible</SelectItem>
                <SelectItem value="moyen">Moyen</SelectItem>
                <SelectItem value="eleve">Élevé</SelectItem>
                <SelectItem value="critique">Critique</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        <DialogFooter className="mt-4">
          <Button variant="outline" onClick={() => onOpenChange(false)}>Annuler</Button>
          <Button onClick={handleAdd} disabled={loading || !category} className="bg-[#1e3a5f] hover:bg-[#152a45]"
            data-testid="frein-submit-btn">
            {loading ? "Ajout..." : "Déclarer le frein"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default PartenaireView;
