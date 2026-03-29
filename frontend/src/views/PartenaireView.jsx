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
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Handshake, Users, TrendingUp, Plus, Eye, CheckCircle2, Clock,
  AlertTriangle, BarChart3, Target, ArrowUpRight, Calendar,
  Home as HomeIcon, Car, Heart, Baby, Accessibility, FileWarning,
  Wallet, HelpCircle, Trash2, ChevronRight, History, Award,
  PlusCircle, Shield, Bell, Link2, Unlink, Search, Brain,
  Briefcase, GraduationCap, Lightbulb, ClipboardList, FileText,
  ChevronDown, ChevronUp, Loader2, Compass, BookOpen,
  MessageSquare, Activity, Globe
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
  const [alertes, setAlertes] = useState([]);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("dashboard");
  const [selectedBeneficiaire, setSelectedBeneficiaire] = useState(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [freinDialogOpen, setFreinDialogOpen] = useState(false);
  const [freinTarget, setFreinTarget] = useState(null);

  useEffect(() => { loadAll(); }, [token]);

  const loadAll = async () => {
    setLoading(true);
    try {
      const [bRes, sRes, pRes, aRes] = await Promise.all([
        axios.get(`${API}/partenaires/beneficiaires?token=${token}`),
        axios.get(`${API}/partenaires/stats?token=${token}`),
        axios.get(`${API}/partenaires/profile?token=${token}`),
        axios.get(`${API}/partenaires/alertes?token=${token}`),
      ]);
      setBeneficiaires(bRes.data);
      setStats(sRes.data);
      setProfile(pRes.data);
      setAlertes(aRes.data);
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
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>
            Interface de coordination partenaires
          </h1>
          <p className="text-slate-500 mt-1 text-sm">
            {profile?.company_name && <span className="font-medium text-[#1e3a5f]">{profile.company_name}</span>}
            {profile?.company_name && " — "}
            Valorisation, coordination et sécurisation des parcours — en appui des dispositifs existants
          </p>
        </div>
        <Button onClick={() => setCreateDialogOpen(true)} className="bg-[#1e3a5f] hover:bg-[#152a45]" data-testid="add-beneficiaire-btn">
          <Plus className="w-4 h-4 mr-2" /> Nouveau bénéficiaire
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="bg-slate-100 border border-slate-200 flex-wrap h-auto gap-1 p-1">
          <TabsTrigger value="dashboard" data-testid="tab-dashboard"><BarChart3 className="w-4 h-4 mr-1.5" /> Tableau de bord</TabsTrigger>
          <TabsTrigger value="beneficiaires" data-testid="tab-beneficiaires"><Users className="w-4 h-4 mr-1.5" /> Bénéficiaires</TabsTrigger>
          <TabsTrigger value="freins" data-testid="tab-freins"><AlertTriangle className="w-4 h-4 mr-1.5" /> Freins</TabsTrigger>
          <TabsTrigger value="orientation" data-testid="tab-orientation"><Compass className="w-4 h-4 mr-1.5" /> Préparation parcours</TabsTrigger>
          <TabsTrigger value="outils" data-testid="tab-outils"><ClipboardList className="w-4 h-4 mr-1.5" /> Outils</TabsTrigger>
          <TabsTrigger value="observatoire" data-testid="tab-observatoire"><Globe className="w-4 h-4 mr-1.5" /> Contribution territoriale</TabsTrigger>
        </TabsList>

        <TabsContent value="dashboard" className="space-y-6 mt-4">
          <ComplementarityBanner />
          <StatsCards stats={stats} />
          {alertes.length > 0 && <AlertesPanel alertes={alertes} onNavigate={(b) => { setSelectedBeneficiaire(b); setActiveTab("beneficiaires"); }} />}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <RecentActivity beneficiaires={beneficiaires} onSelect={(b) => { setSelectedBeneficiaire(b); setActiveTab("beneficiaires"); }} />
            <FreinsSummary beneficiaires={beneficiaires} />
          </div>
        </TabsContent>

        <TabsContent value="beneficiaires" className="space-y-4 mt-4">
          <BeneficiairesList beneficiaires={beneficiaires} token={token} onRefresh={loadAll}
            selectedBeneficiaire={selectedBeneficiaire} setSelectedBeneficiaire={setSelectedBeneficiaire}
            onAddFrein={(b) => { setFreinTarget(b); setFreinDialogOpen(true); }} />
        </TabsContent>

        <TabsContent value="freins" className="space-y-4 mt-4">
          <FreinsView beneficiaires={beneficiaires} token={token} onRefresh={loadAll} />
        </TabsContent>

        <TabsContent value="orientation" className="space-y-4 mt-4">
          <OrientationView beneficiaires={beneficiaires} token={token} onRefresh={loadAll} />
        </TabsContent>

        <TabsContent value="outils" className="space-y-4 mt-4">
          <OutilsAccompagnement beneficiaires={beneficiaires} token={token} onRefresh={loadAll} />
        </TabsContent>

        <TabsContent value="observatoire" className="space-y-4 mt-4">
          <ObservatoireContribution token={token} stats={stats} beneficiaires={beneficiaires} />
        </TabsContent>
      </Tabs>

      <CreateBeneficiaireDialog open={createDialogOpen} onOpenChange={setCreateDialogOpen} token={token} onCreated={loadAll} />
      <AddFreinDialog open={freinDialogOpen} onOpenChange={setFreinDialogOpen} beneficiaire={freinTarget} token={token} onAdded={loadAll} />
    </div>
  );
};

// ===== ALERTES PANEL =====
const AlertesPanel = ({ alertes, onNavigate }) => {
  const [expanded, setExpanded] = useState(false);
  const shown = expanded ? alertes : alertes.slice(0, 3);
  return (
    <Card className="border-l-4 border-l-amber-500 border border-slate-100" data-testid="alertes-panel">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-base">
          <Bell className="w-5 h-5 text-amber-600" /> Alertes ({alertes.length})
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {shown.map((a, i) => (
            <div key={i} className={`flex items-center justify-between p-2.5 rounded-lg border ${
              a.severity === "critique" ? "bg-red-50 border-red-200" :
              a.severity === "eleve" ? "bg-orange-50 border-orange-200" : "bg-amber-50 border-amber-200"
            }`}>
              <div className="flex items-center gap-2">
                {a.type === "inactivite" ? <Clock className="w-4 h-4 text-slate-500" /> :
                 a.type === "frein_critique" ? <AlertTriangle className="w-4 h-4 text-red-500" /> :
                 <Clock className="w-4 h-4 text-amber-500" />}
                <div>
                  <p className="text-sm font-medium text-slate-700">{a.beneficiaire_name}</p>
                  <p className="text-xs text-slate-500">{a.message}</p>
                </div>
              </div>
              <Badge className={
                a.severity === "critique" ? "bg-red-100 text-red-700" :
                a.severity === "eleve" ? "bg-orange-100 text-orange-700" : "bg-amber-100 text-amber-700"
              }>{a.severity}</Badge>
            </div>
          ))}
        </div>
        {alertes.length > 3 && (
          <Button variant="ghost" size="sm" className="mt-2 w-full text-slate-500" onClick={() => setExpanded(!expanded)}>
            {expanded ? <><ChevronUp className="w-4 h-4 mr-1" /> Reduire</> : <><ChevronDown className="w-4 h-4 mr-1" /> Voir tout ({alertes.length})</>}
          </Button>
        )}
      </CardContent>
    </Card>
  );
};

// ===== COMPLEMENTARITY BANNER =====
const ComplementarityBanner = () => (
  <Card className="border border-[#1e3a5f]/10 bg-gradient-to-r from-slate-50 to-blue-50/30" data-testid="complementarity-banner">
    <CardContent className="p-4">
      <div className="flex items-start gap-3">
        <div className="w-9 h-9 rounded-lg bg-[#1e3a5f]/10 flex items-center justify-center flex-shrink-0 mt-0.5">
          <Handshake className="w-5 h-5 text-[#1e3a5f]" />
        </div>
        <div className="w-full">
          <p className="text-sm font-medium text-slate-800 mb-1.5">Brique complementaire de l'ecosysteme</p>
          <p className="text-xs text-slate-500 leading-relaxed mb-3">
            RE'ACTIF PRO n'a pas vocation à se substituer aux dispositifs existants. Il renforce leur efficacité par une meilleure qualification des profils, une coordination des parcours et une mise en visibilité des compétences et freins.
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-7 gap-2">
            <div className="flex items-center gap-2 p-2 rounded-lg bg-white border border-slate-100">
              <div className="w-2 h-2 rounded-full bg-blue-500 flex-shrink-0"></div>
              <div><p className="text-[11px] font-medium text-slate-700">France Travail</p><p className="text-[9px] text-slate-400">Emploi, aides, dispositifs</p></div>
            </div>
            <div className="flex items-center gap-2 p-2 rounded-lg bg-white border border-slate-100">
              <div className="w-2 h-2 rounded-full bg-green-500 flex-shrink-0"></div>
              <div><p className="text-[11px] font-medium text-slate-700">Mission Locale</p><p className="text-[9px] text-slate-400">Insertion jeunes</p></div>
            </div>
            <div className="flex items-center gap-2 p-2 rounded-lg bg-white border border-slate-100">
              <div className="w-2 h-2 rounded-full bg-amber-500 flex-shrink-0"></div>
              <div><p className="text-[11px] font-medium text-slate-700">APEC</p><p className="text-[9px] text-slate-400">Cadres, evolution pro</p></div>
            </div>
            <div className="flex items-center gap-2 p-2 rounded-lg bg-white border border-slate-100">
              <div className="w-2 h-2 rounded-full bg-sky-500 flex-shrink-0"></div>
              <div><p className="text-[11px] font-medium text-slate-700">Orient'Est</p><p className="text-[9px] text-slate-400">Metiers, formations</p></div>
            </div>
            <div className="flex items-center gap-2 p-2 rounded-lg bg-white border border-slate-100">
              <div className="w-2 h-2 rounded-full bg-red-500 flex-shrink-0"></div>
              <div><p className="text-[11px] font-medium text-slate-700">Region Grand Est</p><p className="text-[9px] text-slate-400">Politiques regionales</p></div>
            </div>
            <div className="flex items-center gap-2 p-2 rounded-lg bg-white border border-slate-100">
              <div className="w-2 h-2 rounded-full bg-indigo-500 flex-shrink-0"></div>
              <div><p className="text-[11px] font-medium text-slate-700">EURES</p><p className="text-[9px] text-slate-400">Mobilite europeenne</p></div>
            </div>
            <div className="flex items-center gap-2 p-2 rounded-lg bg-white border border-[#1e3a5f]/20">
              <div className="w-2 h-2 rounded-full bg-[#1e3a5f] flex-shrink-0"></div>
              <div><p className="text-[11px] font-medium text-[#1e3a5f]">RE'ACTIF PRO</p><p className="text-[9px] text-slate-400">Diagnostic, coordination</p></div>
            </div>
          </div>
        </div>
      </div>
    </CardContent>
  </Card>
);

// ===== STATS CARDS =====
const StatsCards = ({ stats }) => {
  if (!stats) return null;
  const metrics = [
    { title: "Personnes accompagnées", value: stats.total, icon: Users, accent: "bg-[#1e3a5f]/10 text-[#1e3a5f]" },
    { title: "Accompagnement actif", value: stats.en_accompagnement, icon: Handshake, accent: "bg-blue-100 text-blue-600" },
    { title: "Insertions réussies", value: stats.en_emploi, icon: CheckCircle2, accent: "bg-green-100 text-green-600" },
    { title: "Taux d'insertion", value: `${stats.taux_insertion}%`, icon: TrendingUp, accent: "bg-amber-100 text-amber-600" },
    { title: "Freins actifs", value: stats.freins_actifs, icon: AlertTriangle, accent: "bg-red-100 text-red-600" },
    { title: "Profils liés", value: stats.linked_profiles || 0, icon: Link2, accent: "bg-purple-100 text-purple-600" },
  ];
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3" data-testid="partenaire-metrics">
      {metrics.map((m, idx) => {
        const Icon = m.icon;
        return (
          <Card key={idx} className="border border-slate-100 hover:border-[#1e3a5f]/20 transition-all" data-testid={`metric-${idx}`}>
            <CardContent className="p-4">
              <div className={`w-8 h-8 rounded-lg ${m.accent} flex items-center justify-center mb-2`}><Icon className="w-4 h-4" /></div>
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
  const recent = [...beneficiaires].sort((a, b) => new Date(b.last_activity || 0) - new Date(a.last_activity || 0)).slice(0, 5);
  return (
    <Card className="lg:col-span-2 border border-slate-100" data-testid="recent-activity">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg"><Calendar className="w-5 h-5 text-[#1e3a5f]" /> Activité récente</CardTitle>
      </CardHeader>
      <CardContent>
        {recent.length === 0 ? <p className="text-sm text-slate-400 text-center py-8">Aucun bénéficiaire</p> : (
          <div className="space-y-3">
            {recent.map((b) => {
              const st = STATUS_OPTIONS.find(s => s.value === b.status) || STATUS_OPTIONS[0];
              const StIcon = st.icon;
              return (
                <div key={b.id} className="flex items-center justify-between p-3 rounded-xl border border-slate-100 hover:border-[#1e3a5f]/20 hover:bg-slate-50/50 transition-all cursor-pointer"
                  onClick={() => onSelect(b)} data-testid={`recent-${b.id}`}>
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-full bg-[#1e3a5f]/10 flex items-center justify-center"><Users className="w-4 h-4 text-[#1e3a5f]" /></div>
                    <div>
                      <p className="text-sm font-medium text-slate-900">{b.name}</p>
                      <div className="flex items-center gap-1.5 text-xs text-slate-400">
                        <span>{b.sector}</span>
                        {b.linked_token_id && <Badge className="bg-purple-100 text-purple-700 text-[10px] py-0 px-1"><Link2 className="w-2.5 h-2.5" /></Badge>}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge className={`${st.color} text-xs flex items-center gap-1`}><StIcon className="w-3 h-3" /> {b.status}</Badge>
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
  activeFreins.forEach(f => { categoryCounts[f.category] = (categoryCounts[f.category] || 0) + 1; });

  return (
    <Card className="border border-slate-100" data-testid="freins-summary">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg"><AlertTriangle className="w-5 h-5 text-amber-600" /> Freins périphériques</CardTitle>
        <CardDescription>{activeFreins.length} frein{activeFreins.length !== 1 ? "s" : ""} actif{activeFreins.length !== 1 ? "s" : ""}</CardDescription>
      </CardHeader>
      <CardContent>
        {activeFreins.length === 0 ? <p className="text-sm text-slate-400 text-center py-6">Aucun frein actif</p> : (
          <div className="space-y-2">
            {FREIN_CATEGORIES.filter(c => categoryCounts[c.value]).map(cat => {
              const Icon = cat.icon;
              return (
                <div key={cat.value} className="flex items-center justify-between p-2.5 rounded-lg bg-slate-50 border border-slate-100">
                  <div className="flex items-center gap-2">
                    <div className={`w-7 h-7 rounded-md ${cat.color} flex items-center justify-center`}><Icon className="w-3.5 h-3.5" /></div>
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
  const filtered = filter === "all" ? beneficiaires : beneficiaires.filter(b => b.status === filter);

  if (selectedBeneficiaire) {
    const b = beneficiaires.find(x => x.id === selectedBeneficiaire.id) || selectedBeneficiaire;
    return <BeneficiaireDetail b={b} onBack={() => setSelectedBeneficiaire(null)}
      onAddFrein={() => onAddFrein(b)} token={token} onRefresh={onRefresh} />;
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2" data-testid="status-filter">
        <Button variant={filter === "all" ? "default" : "outline"} size="sm" className={filter === "all" ? "bg-[#1e3a5f]" : ""} onClick={() => setFilter("all")}>Tous ({beneficiaires.length})</Button>
        {STATUS_OPTIONS.map(st => {
          const count = beneficiaires.filter(b => b.status === st.value).length;
          if (count === 0) return null;
          return <Button key={st.value} variant={filter === st.value ? "default" : "outline"} size="sm" className={filter === st.value ? "bg-[#1e3a5f]" : ""} onClick={() => setFilter(st.value)}>{st.value} ({count})</Button>;
        })}
      </div>

      {filtered.length === 0 ? (
        <Card className="border-dashed border-2 border-slate-200"><CardContent className="flex flex-col items-center justify-center py-12">
          <Users className="w-12 h-12 text-slate-300 mb-3" /><p className="text-slate-500 text-sm">Aucun beneficiaire</p>
        </CardContent></Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4" data-testid="beneficiaires-list">
          {filtered.map(b => {
            const st = STATUS_OPTIONS.find(s => s.value === b.status) || STATUS_OPTIONS[0];
            const StIcon = st.icon;
            const freinsActifs = (b.freins || []).filter(f => f.status !== "resolu").length;
            return (
              <Card key={b.id} className="border border-slate-100 hover:border-[#1e3a5f]/20 transition-all cursor-pointer"
                onClick={() => setSelectedBeneficiaire(b)} data-testid={`beneficiaire-card-${b.id}`}>
                <CardContent className="p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-[#1e3a5f]/10 flex items-center justify-center"><Users className="w-5 h-5 text-[#1e3a5f]" /></div>
                      <div>
                        <div className="flex items-center gap-1.5">
                          <h3 className="font-semibold text-slate-900">{b.name}</h3>
                          {b.linked_token_id && <Link2 className="w-3.5 h-3.5 text-purple-500" />}
                        </div>
                        <p className="text-xs text-slate-500">{b.sector}</p>
                      </div>
                    </div>
                    <Badge className={`${st.color} flex items-center gap-1 text-xs`}><StIcon className="w-3 h-3" /> {b.status}</Badge>
                  </div>
                  <div className="space-y-2 mb-3">
                    <div className="flex items-center justify-between text-xs"><span className="text-slate-500">Progression</span><span className="font-medium text-slate-800">{b.progress || 0}%</span></div>
                    <Progress value={b.progress || 0} className="h-1.5" />
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {(b.skills_acquired || []).length > 0 && <Badge variant="secondary" className="text-xs"><Award className="w-3 h-3 mr-1" />{b.skills_acquired.length} comp.</Badge>}
                      {freinsActifs > 0 && <Badge className="bg-amber-100 text-amber-700 border-amber-200 text-xs"><AlertTriangle className="w-3 h-3 mr-1" />{freinsActifs}</Badge>}
                      {b.diagnostic && Object.keys(b.diagnostic).length > 0 && <Badge className="bg-indigo-100 text-indigo-700 text-xs"><ClipboardList className="w-3 h-3 mr-1" />Diag.</Badge>}
                    </div>
                    <span className="text-xs text-slate-400">{b.last_activity ? new Date(b.last_activity).toLocaleDateString('fr-FR') : ""}</span>
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
const BeneficiaireDetail = ({ b, onBack, onAddFrein, token, onRefresh }) => {
  const [detailTab, setDetailTab] = useState("profil");
  const [newSkill, setNewSkill] = useState("");
  const [linkedProfile, setLinkedProfile] = useState(null);
  const [loadingProfile, setLoadingProfile] = useState(false);
  const [linkSearch, setLinkSearch] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [showLinkDialog, setShowLinkDialog] = useState(false);
  const [diagForm, setDiagForm] = useState(b.diagnostic || {});
  const [savingDiag, setSavingDiag] = useState(false);

  const st = STATUS_OPTIONS.find(s => s.value === b.status) || STATUS_OPTIONS[0];
  const StIcon = st.icon;
  const freinsActifs = (b.freins || []).filter(f => f.status !== "resolu");

  useEffect(() => {
    if (b.linked_token_id) loadLinkedProfile();
  }, [b.linked_token_id]);

  const loadLinkedProfile = async () => {
    setLoadingProfile(true);
    try {
      const res = await axios.get(`${API}/partenaires/beneficiaires/${b.id}/linked-profile?token=${token}`);
      setLinkedProfile(res.data);
    } catch { setLinkedProfile(null); }
    setLoadingProfile(false);
  };

  const updateStatus = async (newStatus) => {
    try {
      await axios.put(`${API}/partenaires/beneficiaires/${b.id}?token=${token}&status=${encodeURIComponent(newStatus)}`);
      toast.success("Statut mis à jour");
      onRefresh();
    } catch { toast.error("Erreur"); }
  };

  const deleteBeneficiaire = async () => {
    try {
      await axios.delete(`${API}/partenaires/beneficiaires/${b.id}?token=${token}`);
      toast.success("Supprimé");
      onBack();
      onRefresh();
    } catch { toast.error("Erreur"); }
  };

  const addSkill = async () => {
    if (!newSkill.trim()) return;
    try {
      await axios.post(`${API}/partenaires/beneficiaires/${b.id}/skills?token=${token}&skill=${encodeURIComponent(newSkill.trim())}`);
      toast.success("Compétence ajoutée");
      setNewSkill("");
      onRefresh();
    } catch { toast.error("Erreur"); }
  };

  const searchUsers = async () => {
    if (linkSearch.length < 2) return;
    setSearching(true);
    try {
      const res = await axios.get(`${API}/partenaires/search-users?token=${token}&query=${encodeURIComponent(linkSearch)}`);
      setSearchResults(res.data);
    } catch { toast.error("Erreur recherche"); }
    setSearching(false);
  };

  const linkUser = async (pseudo) => {
    try {
      await axios.post(`${API}/partenaires/beneficiaires/${b.id}/link?token=${token}&pseudo=${encodeURIComponent(pseudo)}`);
      toast.success("Profil lié !");
      setShowLinkDialog(false);
      onRefresh();
    } catch (err) { toast.error(err.response?.data?.detail || "Erreur"); }
  };

  const unlinkUser = async () => {
    try {
      await axios.delete(`${API}/partenaires/beneficiaires/${b.id}/link?token=${token}`);
      toast.success("Liaison supprimée");
      setLinkedProfile(null);
      onRefresh();
    } catch { toast.error("Erreur"); }
  };

  const saveDiagnostic = async () => {
    setSavingDiag(true);
    try {
      await axios.put(`${API}/partenaires/beneficiaires/${b.id}/diagnostic?token=${token}`, diagForm, { headers: { "Content-Type": "application/json" } });
      toast.success("Diagnostic sauvegardé");
      onRefresh();
    } catch { toast.error("Erreur"); }
    setSavingDiag(false);
  };

  const handleResolveFrein = async (freinId) => {
    try {
      await axios.put(`${API}/partenaires/beneficiaires/${b.id}/freins/${freinId}?token=${token}&status=resolu`);
      toast.success("Frein résolu !");
      onRefresh();
    } catch { toast.error("Erreur"); }
  };

  return (
    <div className="space-y-4" data-testid="beneficiaire-detail">
      <Button variant="ghost" onClick={onBack} className="text-slate-500 hover:text-slate-700 -ml-2" data-testid="back-to-list">
        <ChevronRight className="w-4 h-4 rotate-180 mr-1" /> Retour
      </Button>

      {/* Header Card */}
      <Card className="border border-slate-100">
        <CardContent className="p-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-full bg-[#1e3a5f]/10 flex items-center justify-center"><Users className="w-7 h-7 text-[#1e3a5f]" /></div>
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>{b.name}</h2>
                  {b.linked_token_id && <Badge className="bg-purple-100 text-purple-700 text-xs"><Link2 className="w-3 h-3 mr-1" /> Lie</Badge>}
                </div>
                <p className="text-sm text-slate-500">Secteur : {b.sector}</p>
                <Badge className={`${st.color} flex items-center gap-1 mt-1 w-fit text-xs`}><StIcon className="w-3 h-3" /> {b.status}</Badge>
              </div>
            </div>
            <div className="flex items-center gap-2 flex-wrap">
              {!b.linked_token_id ? (
                <Button variant="outline" size="sm" onClick={() => setShowLinkDialog(true)} data-testid="link-profile-btn">
                  <Link2 className="w-4 h-4 mr-1" /> Lier un profil
                </Button>
              ) : (
                <Button variant="outline" size="sm" onClick={unlinkUser} className="text-red-500 hover:text-red-700" data-testid="unlink-profile-btn">
                  <Unlink className="w-4 h-4 mr-1" /> Delier
                </Button>
              )}
              <Select value={b.status} onValueChange={updateStatus}>
                <SelectTrigger className="w-44 h-9 text-sm" data-testid="detail-status-select"><SelectValue /></SelectTrigger>
                <SelectContent>{STATUS_OPTIONS.map(s => <SelectItem key={s.value} value={s.value}>{s.value}</SelectItem>)}</SelectContent>
              </Select>
              <Button variant="outline" size="icon" className="text-red-500 hover:bg-red-50" onClick={deleteBeneficiaire} data-testid="delete-beneficiaire-btn">
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          </div>
          <div className="mt-4 space-y-1.5">
            <div className="flex justify-between text-sm"><span className="text-slate-500">Progression du parcours</span><span className="font-medium text-slate-900">{b.progress || 0}%</span></div>
            <Progress value={b.progress || 0} className="h-2" />
          </div>
          {b.notes && <p className="mt-3 text-sm text-slate-600 bg-slate-50 p-3 rounded-lg">{b.notes}</p>}
        </CardContent>
      </Card>

      {/* Detail Tabs */}
      <Tabs value={detailTab} onValueChange={setDetailTab}>
        <TabsList className="bg-slate-100 border border-slate-200 h-auto gap-1 p-1 flex-wrap">
          <TabsTrigger value="profil"><FileText className="w-3.5 h-3.5 mr-1" /> Profil</TabsTrigger>
          <TabsTrigger value="diagnostic"><ClipboardList className="w-3.5 h-3.5 mr-1" /> Diagnostic</TabsTrigger>
          <TabsTrigger value="freins_detail"><AlertTriangle className="w-3.5 h-3.5 mr-1" /> Freins</TabsTrigger>
          <TabsTrigger value="historique"><History className="w-3.5 h-3.5 mr-1" /> Historique</TabsTrigger>
          {b.linked_token_id && <TabsTrigger value="profil_reactif"><Eye className="w-3.5 h-3.5 mr-1" /> Profil Re'Actif</TabsTrigger>}
        </TabsList>

        {/* Profil Tab */}
        <TabsContent value="profil" className="mt-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card className="border border-slate-100">
              <CardHeader className="pb-3"><CardTitle className="text-base flex items-center gap-2"><Award className="w-4 h-4 text-[#1e3a5f]" /> Compétences validées</CardTitle></CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2 mb-3">
                  {(b.skills_acquired || []).map((skill, i) => <Badge key={i} className="bg-[#1e3a5f]/10 text-[#1e3a5f] border-[#1e3a5f]/20">{skill}</Badge>)}
                  {!(b.skills_acquired || []).length && <p className="text-sm text-slate-400">Aucune compétence validée</p>}
                </div>
                <div className="flex gap-2">
                  <Input placeholder="Ajouter une compétence..." value={newSkill} onChange={e => setNewSkill(e.target.value)}
                    onKeyDown={e => { if (e.key === "Enter") addSkill(); }} className="h-8 text-sm" data-testid="add-skill-input" />
                  <Button size="sm" variant="outline" className="h-8" onClick={addSkill} data-testid="add-skill-btn"><PlusCircle className="w-3.5 h-3.5" /></Button>
                </div>
              </CardContent>
            </Card>
            <Card className="border border-slate-100">
              <CardHeader className="pb-3"><CardTitle className="text-base flex items-center gap-2"><Activity className="w-4 h-4 text-[#1e3a5f]" /> Informations</CardTitle></CardHeader>
              <CardContent className="space-y-2 text-sm">
                <div className="flex justify-between"><span className="text-slate-500">Secteur</span><span className="font-medium">{b.sector}</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Statut</span><Badge className={`${st.color} text-xs`}>{b.status}</Badge></div>
                <div className="flex justify-between"><span className="text-slate-500">Freins actifs</span><span className="font-medium">{freinsActifs.length}</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Profil lie</span><span className="font-medium">{b.linked_pseudo || "Non"}</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Cree le</span><span>{b.created_at ? new Date(b.created_at).toLocaleDateString('fr-FR') : ""}</span></div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Diagnostic Tab */}
        <TabsContent value="diagnostic" className="mt-4">
          <Card className="border border-slate-100">
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><ClipboardList className="w-5 h-5 text-indigo-600" /> Diagnostic enrichi</CardTitle>              <CardDescription>Complément au profil : contexte social, motivation, posture, soft skills</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700">Contexte social</label>
                  <Textarea value={diagForm.contexte_social || ""} onChange={e => setDiagForm({ ...diagForm, contexte_social: e.target.value })}
                    placeholder="Situation familiale, conditions de vie..." className="resize-none h-20" data-testid="diag-contexte" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700">Mobilité (détail)</label>
                  <Textarea value={diagForm.mobilite_detail || ""} onChange={e => setDiagForm({ ...diagForm, mobilite_detail: e.target.value })}
                    placeholder="Permis, transports, rayon de déplacement..." className="resize-none h-20" data-testid="diag-mobilite" />
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700">Motivation</label>
                  <Select value={diagForm.motivation_level || ""} onValueChange={v => setDiagForm({ ...diagForm, motivation_level: v })}>
                    <SelectTrigger data-testid="diag-motivation"><SelectValue placeholder="Évaluer..." /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="tres_elevee">Très élevée</SelectItem><SelectItem value="elevee">Élevée</SelectItem>
                      <SelectItem value="moyenne">Moyenne</SelectItem><SelectItem value="faible">Faible</SelectItem>
                      <SelectItem value="a_travailler">À travailler</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700">Posture professionnelle</label>
                  <Select value={diagForm.posture || ""} onValueChange={v => setDiagForm({ ...diagForm, posture: v })}>
                    <SelectTrigger data-testid="diag-posture"><SelectValue placeholder="Évaluer..." /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="autonome">Autonome</SelectItem><SelectItem value="en_progression">En progression</SelectItem>
                      <SelectItem value="a_accompagner">À accompagner</SelectItem><SelectItem value="en_difficulte">En difficulté</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700">Autonomie</label>
                  <Select value={diagForm.autonomie || ""} onValueChange={v => setDiagForm({ ...diagForm, autonomie: v })}>
                    <SelectTrigger data-testid="diag-autonomie"><SelectValue placeholder="Évaluer..." /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="forte">Forte</SelectItem><SelectItem value="moyenne">Moyenne</SelectItem>
                      <SelectItem value="limitee">Limitée</SelectItem><SelectItem value="tres_limitee">Très limitée</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Observations complémentaires</label>
                <Textarea value={diagForm.observations || ""} onChange={e => setDiagForm({ ...diagForm, observations: e.target.value })}
                  placeholder="Observations, points de vigilance..." className="resize-none h-20" data-testid="diag-observations" />
              </div>
              <Button onClick={saveDiagnostic} disabled={savingDiag} className="bg-[#1e3a5f] hover:bg-[#152a45]" data-testid="save-diagnostic-btn">
                {savingDiag ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Sauvegarde...</> : <><CheckCircle2 className="w-4 h-4 mr-2" /> Sauvegarder le diagnostic</>}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Freins Tab */}
        <TabsContent value="freins_detail" className="mt-4">
          <Card className="border border-slate-100">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-base flex items-center gap-2"><AlertTriangle className="w-4 h-4 text-amber-600" /> Freins périphériques</CardTitle>
                <Button size="sm" variant="outline" onClick={onAddFrein} data-testid="add-frein-btn"><Plus className="w-3.5 h-3.5 mr-1" /> Ajouter</Button>
              </div>
            </CardHeader>
            <CardContent>
              {!freinsActifs.length && !(b.freins || []).filter(f => f.status === "resolu").length ? <p className="text-sm text-slate-400">Aucun frein déclaré</p> : (
                <div className="space-y-2">
                  {freinsActifs.map(f => {
                    const cat = FREIN_CATEGORIES.find(c => c.value === f.category) || FREIN_CATEGORIES[7];
                    const CIcon = cat.icon;
                    return (
                      <div key={f.id} className="flex items-center justify-between p-2.5 rounded-lg border border-slate-100 bg-slate-50">
                        <div className="flex items-center gap-2">
                          <div className={`w-7 h-7 rounded-md ${cat.color} flex items-center justify-center`}><CIcon className="w-3.5 h-3.5" /></div>
                          <div><p className="text-sm font-medium text-slate-700">{cat.label}</p>{f.description && <p className="text-xs text-slate-400">{f.description}</p>}</div>
                        </div>
                        <Button size="sm" variant="outline" className="text-green-600 hover:bg-green-50 h-7 text-xs" onClick={() => handleResolveFrein(f.id)}><CheckCircle2 className="w-3 h-3 mr-1" /> Résoudre</Button>
                      </div>
                    );
                  })}
                  {(b.freins || []).filter(f => f.status === "resolu").map(f => {
                    const cat = FREIN_CATEGORIES.find(c => c.value === f.category) || FREIN_CATEGORIES[7];
                    return <div key={f.id} className="flex items-center gap-2 p-2 rounded-lg opacity-50"><CheckCircle2 className="w-4 h-4 text-green-500" /><span className="text-xs text-slate-500 line-through">{cat.label}</span></div>;
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Historique Tab */}
        <TabsContent value="historique" className="mt-4">
          <Card className="border border-slate-100">
            <CardHeader className="pb-3"><CardTitle className="text-base flex items-center gap-2"><History className="w-4 h-4 text-[#1e3a5f]" /> Historique du parcours</CardTitle></CardHeader>
            <CardContent>
              {!(b.historique || []).length ? <p className="text-sm text-slate-400">Aucun historique</p> : (
                <div className="space-y-2">
                  {[...(b.historique || [])].reverse().slice(0, 20).map((h, i) => (
                    <div key={i} className="flex items-start gap-3 text-sm">
                      <div className="w-2 h-2 rounded-full bg-[#1e3a5f] mt-1.5 flex-shrink-0"></div>
                      <div><span className="text-slate-500 text-xs">{new Date(h.date).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' })}</span><p className="text-slate-700">{h.detail || h.action}</p></div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Linked Profile Tab */}
        {b.linked_token_id && (
          <TabsContent value="profil_reactif" className="mt-4">
            <LinkedProfileView data={linkedProfile} loading={loadingProfile} pseudo={b.linked_pseudo} />
          </TabsContent>
        )}
      </Tabs>

      {/* Link Dialog */}
      <Dialog open={showLinkDialog} onOpenChange={setShowLinkDialog}>
        <DialogContent className="sm:max-w-[500px]" data-testid="link-dialog">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2"><Link2 className="w-5 h-5 text-purple-600" /> Lier a un profil Re'Actif Pro</DialogTitle>
            <DialogDescription>Recherchez l'utilisateur par son pseudo</DialogDescription>          </DialogHeader>
          <div className="space-y-4 mt-2">
            <div className="flex gap-2">
              <Input placeholder="Rechercher un pseudo..." value={linkSearch} onChange={e => setLinkSearch(e.target.value)}
                onKeyDown={e => { if (e.key === "Enter") searchUsers(); }} data-testid="link-search-input" />
              <Button onClick={searchUsers} disabled={searching || linkSearch.length < 2} variant="outline" data-testid="link-search-btn">
                {searching ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
              </Button>
            </div>
            {searchResults.length > 0 && (
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {searchResults.map(u => (
                  <div key={u.pseudo} className="flex items-center justify-between p-3 rounded-lg border border-slate-100 hover:bg-slate-50">
                    <div>
                      <p className="text-sm font-medium">{u.display_name} <span className="text-slate-400">@{u.pseudo}</span></p>
                      <p className="text-xs text-slate-500">{u.skills_count} competences {u.sectors?.length ? `| ${u.sectors.slice(0, 2).join(", ")}` : ""}</p>
                    </div>
                    <Button size="sm" onClick={() => linkUser(u.pseudo)} className="bg-[#1e3a5f] hover:bg-[#152a45]" data-testid={`link-user-${u.pseudo}`}>
                      <Link2 className="w-3 h-3 mr-1" /> Lier
                    </Button>
                  </div>
                ))}
              </div>
            )}
            {searchResults.length === 0 && linkSearch.length >= 2 && !searching && <p className="text-sm text-slate-400 text-center py-4">Aucun utilisateur trouve</p>}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// ===== LINKED PROFILE VIEW =====
const LinkedProfileView = ({ data, loading, pseudo }) => {
  if (loading) return <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-[#1e3a5f]" /></div>;
  if (!data) return <p className="text-sm text-slate-400 text-center py-8">Impossible de charger le profil</p>;

  const { profile, passport, cv_analyses, dclic_results } = data;
  return (
    <div className="space-y-4" data-testid="linked-profile-view">
      <Card className="border-l-4 border-l-purple-500 border border-slate-100">
        <CardHeader className="pb-3"><CardTitle className="flex items-center gap-2 text-base"><Eye className="w-5 h-5 text-purple-600" /> Profil Re'Actif Pro — @{pseudo}</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          {profile && (
            <div>
              <h4 className="text-sm font-semibold text-slate-700 mb-2">Competences detectees ({(profile.skills || []).length})</h4>
              <div className="flex flex-wrap gap-1.5">
                {(profile.skills || []).slice(0, 20).map((s, i) => (
                  <Badge key={i} variant="secondary" className="text-xs">{typeof s === 'object' ? s.name : s}</Badge>
                ))}
              </div>
              {profile.sectors?.length > 0 && (
                <div className="mt-3"><h4 className="text-sm font-semibold text-slate-700 mb-1">Secteurs</h4>
                  <div className="flex flex-wrap gap-1.5">{profile.sectors.map((s, i) => <Badge key={i} className="bg-[#1e3a5f]/10 text-[#1e3a5f] text-xs">{s}</Badge>)}</div>
                </div>
              )}
            </div>
          )}
          {passport && (
            <div className="border-t border-slate-100 pt-4">
              <h4 className="text-sm font-semibold text-slate-700 mb-2 flex items-center gap-1.5"><BookOpen className="w-4 h-4" /> Passeport de competences</h4>
              {passport.professional_summary && <p className="text-sm text-slate-600 mb-2">{passport.professional_summary}</p>}
              {passport.career_project && <div className="bg-slate-50 p-3 rounded-lg"><p className="text-xs text-slate-500 mb-1">Projet professionnel</p><p className="text-sm text-slate-700">{passport.career_project}</p></div>}
              {(passport.competences || []).length > 0 && (
                <div className="mt-2"><p className="text-xs text-slate-500 mb-1">Competences passeport</p>
                  <div className="flex flex-wrap gap-1.5">{passport.competences.slice(0, 15).map((c, i) => <Badge key={i} variant="outline" className="text-xs">{typeof c === 'object' ? (c.name || c.label) : c}</Badge>)}</div>
                </div>
              )}
            </div>
          )}
          {dclic_results && dclic_results.scores && (
            <div className="border-t border-slate-100 pt-4">
              <h4 className="text-sm font-semibold text-slate-700 mb-2 flex items-center gap-1.5"><Brain className="w-4 h-4" /> Resultats D'CLIC PRO</h4>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                {Object.entries(dclic_results.scores).filter(([, v]) => typeof v === 'number').map(([k, v]) => (
                  <div key={k} className="bg-slate-50 rounded-lg p-2 text-center">
                    <p className="text-xs text-slate-500 capitalize">{k.replace(/_/g, ' ')}</p>
                    <p className="text-lg font-bold text-[#1e3a5f]">{v}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
          {cv_analyses && cv_analyses.length > 0 && (
            <div className="border-t border-slate-100 pt-4">
              <h4 className="text-sm font-semibold text-slate-700 mb-2 flex items-center gap-1.5"><FileText className="w-4 h-4" /> Analyses CV ({cv_analyses.length})</h4>
              <p className="text-sm text-slate-500">{cv_analyses.length} CV analyse{cv_analyses.length > 1 ? "s" : ""}</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

// ===== ORIENTATION VIEW =====
const OrientationView = ({ beneficiaires, token, onRefresh }) => {
  const [selectedId, setSelectedId] = useState("");
  const [orientation, setOrientation] = useState(null);
  const [loading, setLoading] = useState(false);

  const generateOrientation = async () => {
    if (!selectedId) return;
    setLoading(true);
    setOrientation(null);
    try {
      const res = await axios.post(`${API}/partenaires/beneficiaires/${selectedId}/orientation?token=${token}`);
      setOrientation(res.data);
      toast.success("Orientation générée !");
      onRefresh();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Erreur IA");
    }
    setLoading(false);
  };

  const selected = beneficiaires.find(b => b.id === selectedId);

  return (
    <div className="space-y-4" data-testid="orientation-view">
      <Card className="border border-slate-100">
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><Compass className="w-5 h-5 text-[#1e3a5f]" /> Préparation et qualification du parcours</CardTitle>
          <CardDescription>Révéler le potentiel, qualifier les compétences et préparer l'accès aux dispositifs existants (France Travail, Mission Locale, APEC, Orient'Est, Région Grand Est, EURES...)</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-3">
            <Select value={selectedId} onValueChange={setSelectedId}>
              <SelectTrigger className="flex-1" data-testid="orientation-select-beneficiaire"><SelectValue placeholder="Choisir un bénéficiaire..." /></SelectTrigger>
              <SelectContent>{beneficiaires.map(b => <SelectItem key={b.id} value={b.id}>{b.name} — {b.sector}</SelectItem>)}</SelectContent>
            </Select>
            <Button onClick={generateOrientation} disabled={loading || !selectedId} className="bg-[#1e3a5f] hover:bg-[#152a45]" data-testid="generate-orientation-btn">
              {loading ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Analyse IA...</> : <><Brain className="w-4 h-4 mr-2" /> Qualifier le parcours</>}
            </Button>
          </div>
          {selected && (
            <div className="mt-3 flex flex-wrap gap-2 text-xs">
              <Badge variant="secondary">{selected.sector}</Badge>
              {(selected.skills_acquired || []).map((s, i) => <Badge key={i} className="bg-[#1e3a5f]/10 text-[#1e3a5f]">{s}</Badge>)}
              {(selected.freins || []).filter(f => f.status !== "resolu").map(f => <Badge key={f.id} className="bg-amber-100 text-amber-700">{f.category}</Badge>)}
              {selected.linked_token_id && <Badge className="bg-purple-100 text-purple-700"><Link2 className="w-3 h-3 mr-1" /> Profil lié</Badge>}
            </div>
          )}
        </CardContent>
      </Card>

      {loading && (
        <Card className="border border-slate-100"><CardContent className="flex flex-col items-center justify-center py-12">
          <Loader2 className="w-10 h-10 animate-spin text-[#1e3a5f] mb-3" /><p className="text-slate-500">Analyse du profil par l'IA...</p>
        </CardContent></Card>
      )}

      {orientation && !loading && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {orientation.metiers_recommandes?.length > 0 && (
            <Card className="border border-slate-100">
              <CardHeader className="pb-2"><CardTitle className="text-base flex items-center gap-2"><Briefcase className="w-4 h-4 text-blue-600" /> Pistes métiers identifiées</CardTitle></CardHeader>
              <CardContent className="space-y-2">
                {orientation.metiers_recommandes.map((m, i) => (
                  <div key={i} className="p-3 rounded-lg bg-blue-50/50 border border-blue-100">
                    <div className="flex items-center justify-between mb-1"><span className="text-sm font-medium text-slate-800">{m.titre}</span><Badge className="bg-blue-100 text-blue-700 text-xs">{m.compatibilite}%</Badge></div>
                    <p className="text-xs text-slate-500">{m.raison}</p>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
          {orientation.formations_suggerees?.length > 0 && (
            <Card className="border border-slate-100">
              <CardHeader className="pb-2"><CardTitle className="text-base flex items-center gap-2"><GraduationCap className="w-4 h-4 text-green-600" /> Formations à explorer</CardTitle></CardHeader>
              <CardContent className="space-y-2">
                {orientation.formations_suggerees.map((f, i) => (
                  <div key={i} className="p-3 rounded-lg bg-green-50/50 border border-green-100">
                    <div className="flex items-center gap-2 mb-1"><span className="text-sm font-medium text-slate-800">{f.titre}</span><Badge variant="outline" className="text-xs">{f.type}</Badge></div>
                    <p className="text-xs text-slate-500">{f.raison}</p>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
          {orientation.dispositifs_adaptes?.length > 0 && (
            <Card className="border border-slate-100">
              <CardHeader className="pb-2"><CardTitle className="text-base flex items-center gap-2"><Lightbulb className="w-4 h-4 text-amber-600" /> Dispositifs adaptés</CardTitle></CardHeader>
              <CardContent className="space-y-2">
                {orientation.dispositifs_adaptes.map((d, i) => (
                  <div key={i} className="p-3 rounded-lg bg-amber-50/50 border border-amber-100">
                    <div className="flex items-center gap-2 mb-1"><span className="text-sm font-medium text-slate-800">{d.nom}</span><Badge className={d.pertinence === "haute" ? "bg-green-100 text-green-700" : "bg-amber-100 text-amber-700"} >{d.pertinence}</Badge></div>
                    <p className="text-xs text-slate-500">{d.description}</p>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
          {(orientation.actions_immediates?.length > 0 || orientation.points_vigilance?.length > 0) && (
            <Card className="border border-slate-100">
              <CardHeader className="pb-2"><CardTitle className="text-base flex items-center gap-2"><Target className="w-4 h-4 text-[#1e3a5f]" /> Actions et vigilance</CardTitle></CardHeader>
              <CardContent className="space-y-3">
                {orientation.actions_immediates?.length > 0 && (
                  <div><p className="text-xs font-semibold text-slate-500 mb-1.5 uppercase tracking-wider">Actions immédiates</p>
                    <ul className="space-y-1">{orientation.actions_immediates.map((a, i) => <li key={i} className="text-sm text-slate-700 flex items-start gap-2"><ArrowUpRight className="w-3.5 h-3.5 text-green-500 mt-0.5 flex-shrink-0" />{a}</li>)}</ul>
                  </div>
                )}
                {orientation.points_vigilance?.length > 0 && (
                  <div><p className="text-xs font-semibold text-slate-500 mb-1.5 uppercase tracking-wider">Points de vigilance</p>
                    <ul className="space-y-1">{orientation.points_vigilance.map((p, i) => <li key={i} className="text-sm text-slate-700 flex items-start gap-2"><AlertTriangle className="w-3.5 h-3.5 text-amber-500 mt-0.5 flex-shrink-0" />{p}</li>)}</ul>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
          </div>
          {/* Ecosystem references */}
          <Card className="border border-dashed border-slate-200 bg-slate-50/50">
            <CardContent className="p-4">
              <p className="text-xs font-medium text-slate-600 mb-2">Pour aller plus loin — dispositifs complémentaires</p>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 text-xs">
                <div className="flex items-center gap-2 p-2 rounded-lg bg-white border border-slate-100">
                  <div className="w-6 h-6 rounded bg-blue-100 flex items-center justify-center flex-shrink-0"><Briefcase className="w-3 h-3 text-blue-600" /></div>
                  <div><p className="font-medium text-slate-700">France Travail</p><p className="text-[10px] text-slate-400">Offres, aides, dispositifs</p></div>
                </div>
                <div className="flex items-center gap-2 p-2 rounded-lg bg-white border border-slate-100">
                  <div className="w-6 h-6 rounded bg-green-100 flex items-center justify-center flex-shrink-0"><Users className="w-3 h-3 text-green-600" /></div>
                  <div><p className="font-medium text-slate-700">Mission Locale</p><p className="text-[10px] text-slate-400">Insertion des jeunes</p></div>
                </div>
                <div className="flex items-center gap-2 p-2 rounded-lg bg-white border border-slate-100">
                  <div className="w-6 h-6 rounded bg-amber-100 flex items-center justify-center flex-shrink-0"><TrendingUp className="w-3 h-3 text-amber-600" /></div>
                  <div><p className="font-medium text-slate-700">APEC</p><p className="text-[10px] text-slate-400">Cadres, évolution pro</p></div>
                </div>
                <div className="flex items-center gap-2 p-2 rounded-lg bg-white border border-slate-100">
                  <div className="w-6 h-6 rounded bg-sky-100 flex items-center justify-center flex-shrink-0"><BookOpen className="w-3 h-3 text-sky-600" /></div>
                  <div><p className="font-medium text-slate-700">Orient'Est</p><p className="text-[10px] text-slate-400">Métiers, formations</p></div>
                </div>
                <div className="flex items-center gap-2 p-2 rounded-lg bg-white border border-slate-100">
                  <div className="w-6 h-6 rounded bg-red-100 flex items-center justify-center flex-shrink-0"><Target className="w-3 h-3 text-red-600" /></div>
                  <div><p className="font-medium text-slate-700">Région Grand Est</p><p className="text-[10px] text-slate-400">Politiques régionales</p></div>
                </div>
                <div className="flex items-center gap-2 p-2 rounded-lg bg-white border border-slate-100">
                  <div className="w-6 h-6 rounded bg-indigo-100 flex items-center justify-center flex-shrink-0"><Globe className="w-3 h-3 text-indigo-600" /></div>
                  <div><p className="font-medium text-slate-700">EURES</p><p className="text-[10px] text-slate-400">Mobilité européenne</p></div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

// ===== OUTILS D'ACCOMPAGNEMENT V2 =====
const PHASES = [
  { id: "diagnostic", label: "Diagnostic initial", color: "bg-sky-100 text-sky-700 border-sky-200", icon: Eye },
  { id: "bilan_pro", label: "Bilan professionnel", color: "bg-blue-100 text-blue-700 border-blue-200", icon: Briefcase },
  { id: "identite_valeurs", label: "Identité et valeurs", color: "bg-purple-100 text-purple-700 border-purple-200", icon: Heart },
  { id: "strategie", label: "Stratégie et trajectoire", color: "bg-amber-100 text-amber-700 border-amber-200", icon: Compass },
  { id: "activation", label: "Activation", color: "bg-green-100 text-green-700 border-green-200", icon: Target },
];

const FICHE_FIELDS = {
  positionnement_depart: [
    { key: "clarte", label: "Mon niveau de clarté actuel (0 à 10)", type: "select", options: ["0","1","2","3","4","5","6","7","8","9","10"] },
    { key: "energie", label: "Mon niveau d'énergie (0 à 10)", type: "select", options: ["0","1","2","3","4","5","6","7","8","9","10"] },
    { key: "urgence", label: "Mon urgence", type: "select", options: ["Immédiat", "3 mois", "6 mois", "Plus de 6 mois"] },
    { key: "question_cle", label: "Si rien ne change dans 6 mois, qu'est-ce que je risque ?", type: "textarea" },
    { key: "attentes", label: "Qu'attendez-vous de cet accompagnement ?", type: "textarea" },
    { key: "sujets_prioritaires", label: "Sujets à aborder en priorité", type: "textarea" },
  ],
  courbe_trajectoire: [
    { key: "pics_reussite", label: "Mes pics = conditions de réussite (quand, pourquoi)", type: "textarea" },
    { key: "zones_rupture", label: "Mes creux = zones de rupture (quand, pourquoi)", type: "textarea" },
    { key: "fil_rouge", label: "Mes constantes = mon fil rouge", type: "textarea" },
    { key: "ne_plus_revivre", label: "Ce que je ne veux plus revivre", type: "textarea" },
    { key: "tendance_actuelle", label: "Tendance actuelle et projection", type: "textarea" },
  ],
  recit_carriere: [
    { key: "periodes", label: "Grandes périodes du parcours (dates, postes, entreprises)", type: "textarea" },
    { key: "competences_par_poste", label: "Compétences développées par poste", type: "textarea" },
    { key: "energie_par_poste", label: "Énergie ressentie par poste (0 à 10)", type: "textarea" },
    { key: "alignement_valeurs", label: "Alignement avec mes valeurs par poste (0 à 10)", type: "textarea" },
    { key: "environnements_favorables", label: "Mes environnements favorables", type: "textarea" },
    { key: "environnements_toxiques", label: "Mes environnements toxiques", type: "textarea" },
    { key: "pattern_professionnel", label: "Mon pattern professionnel (récurrence identifiée)", type: "textarea" },
  ],
  realisations: [
    { key: "realisations_star", label: "Réalisations significatives (méthode STAR : Situation, Tâche, Action, Résultat)", type: "textarea" },
    { key: "impact_reel", label: "Impact réel de chaque réalisation (faible / moyen / fort)", type: "textarea" },
    { key: "niveau_preuve", label: "Niveau de preuve (ressenti / observable / mesuré)", type: "textarea" },
    { key: "ce_que_ca_dit", label: "Ce que ça dit de moi (compétence + posture)", type: "textarea" },
    { key: "contexte_reproductibilite", label: "Dans quel contexte je reproduis facilement cette réussite ?", type: "textarea" },
  ],
  competences_dynamiques: [
    { key: "techniques", label: "Compétences techniques (maîtrisées / en développement / à acquérir)", type: "textarea" },
    { key: "transversales", label: "Compétences transversales (maîtrisées / en développement / à acquérir)", type: "textarea" },
    { key: "comportementales", label: "Compétences comportementales (maîtrisées / en développement / à acquérir)", type: "textarea" },
    { key: "transferabilite", label: "Transférabilité : si je change de secteur, qu'est-ce que je garde ?", type: "textarea" },
  ],
  identite_professionnelle: [
    { key: "ce_que_je_suis", label: "Ce que je suis (ressenti)", type: "textarea" },
    { key: "ce_que_je_fais", label: "Ce que je fais (compétences)", type: "textarea" },
    { key: "ce_que_je_renvoie", label: "Ce que je renvoie (image perçue)", type: "textarea" },
    { key: "feedback_externe", label: "Feedback externe (perception recruteur, collègues)", type: "textarea" },
    { key: "phrase_identite", label: "Ma phrase d'identité professionnelle (exploitable CV / pitch)", type: "textarea" },
  ],
  valeurs_decisionnelles: [
    { key: "valeurs_essentielles", label: "Mes valeurs essentielles", type: "textarea" },
    { key: "exemples_vecus", label: "Exemple vécu pour chaque valeur", type: "textarea" },
    { key: "non_respect", label: "Situation où mes valeurs n'ont pas été respectées", type: "textarea" },
    { key: "impact_motivation", label: "Impact sur ma motivation", type: "textarea" },
    { key: "non_negociables", label: "Mes 5 NON NÉGOCIABLES pour mon futur poste", type: "textarea" },
  ],
  environnement_rqth: [
    { key: "contraintes_reelles", label: "Contraintes réelles (santé, mobilité, vie perso)", type: "textarea" },
    { key: "conditions_compatibles", label: "Conditions de travail compatibles", type: "textarea" },
    { key: "adaptations_rqth", label: "Si RQTH/EQTH : adaptations nécessaires et environnements favorables", type: "textarea" },
    { key: "conditions_non_negociables", label: "Conditions non négociables pour la suite", type: "textarea" },
  ],
  confrontation_marche: [
    { key: "metier_1", label: "Métier cible 1 : intitulé, compétences demandées, niveau d'accès, tension du marché", type: "textarea" },
    { key: "metier_2", label: "Métier cible 2 : intitulé, compétences demandées, niveau d'accès, tension du marché", type: "textarea" },
    { key: "metier_3", label: "Métier cible 3 : intitulé, compétences demandées, niveau d'accès, tension du marché", type: "textarea" },
    { key: "ecarts", label: "Mes écarts principaux", type: "textarea" },
    { key: "atouts_differenciants", label: "Mes atouts différenciants", type: "textarea" },
    { key: "decision", label: "Décision pour chaque métier", type: "select", options: ["GO", "PAS GO", "AJUSTEMENT"] },
  ],
  strategie_trajectoire: [
    { key: "scenario_principal", label: "Scénario 1 — Projet principal (description, faisabilité, risque, délai)", type: "textarea" },
    { key: "scenario_securise", label: "Scénario 2 — Projet sécurisé (description, faisabilité, risque, délai)", type: "textarea" },
    { key: "scenario_exploratoire", label: "Scénario 3 — Projet exploratoire (description, faisabilité, risque, délai)", type: "textarea" },
  ],
  reseau_leviers: [
    { key: "personnes_ressources", label: "Qui peut m'aider ? (personnes ressources)", type: "textarea" },
    { key: "entreprises_cibles", label: "Qui recrute ? (entreprises cibles)", type: "textarea" },
    { key: "inspirations", label: "Qui m'inspire ?", type: "textarea" },
    { key: "recommandations", label: "Qui peut me recommander ?", type: "textarea" },
    { key: "canaux_acces", label: "Canaux d'accès (réseau / candidature directe / plateforme)", type: "textarea" },
  ],
  plan_activation: [
    { key: "actions_terrain", label: "3 actions terrain à réaliser", type: "textarea" },
    { key: "contacts_pro", label: "3 contacts professionnels à prendre", type: "textarea" },
    { key: "mise_en_situation", label: "1 mise en situation concrète (immersion / test / projet)", type: "textarea" },
    { key: "suivi_resultats", label: "Suivi : fait / non fait / résultat / apprentissage", type: "textarea" },
  ],
};

const OutilsAccompagnement = ({ beneficiaires, token, onRefresh }) => {
  const [selectedBenId, setSelectedBenId] = useState("");
  const [selectedFiche, setSelectedFiche] = useState(null);
  const [bilanData, setBilanData] = useState({});
  const [ficheForm, setFicheForm] = useState({});
  const [saving, setSaving] = useState(false);
  const [fiches, setFiches] = useState([]);
  const [showConsent, setShowConsent] = useState(false);

  useEffect(() => {
    axios.get(`${API}/partenaires/outils/fiches?token=${token}`).then(r => setFiches(r.data)).catch(() => {});
  }, [token]);

  useEffect(() => {
    if (selectedBenId) {
      axios.get(`${API}/partenaires/beneficiaires/${selectedBenId}/bilan?token=${token}`)
        .then(r => setBilanData(r.data || {}))
        .catch(() => setBilanData({}));
    }
  }, [selectedBenId, token]);

  const openFiche = (fiche) => {
    setSelectedFiche(fiche);
    const saved = bilanData[fiche.id] || {};
    setFicheForm({ ...saved });
  };

  const saveFiche = async () => {
    if (!selectedFiche || !selectedBenId) return;
    setSaving(true);
    try {
      await axios.put(`${API}/partenaires/beneficiaires/${selectedBenId}/bilan?token=${token}`, { fiche_id: selectedFiche.id, data: ficheForm }, { headers: { "Content-Type": "application/json" } });
      toast.success("Fiche sauvegardée");
      setBilanData({ ...bilanData, [selectedFiche.id]: { ...ficheForm, updated_at: new Date().toISOString() } });
      setSelectedFiche(null);
      onRefresh();
    } catch { toast.error("Erreur"); }
    setSaving(false);
  };

  const selectedBen = beneficiaires.find(b => b.id === selectedBenId);
  const completedFiches = fiches.filter(f => bilanData[f.id]);

  // Decision block keys
  const DECISION_KEYS = [
    { key: "_decision_je_decide", label: "Ce que je décide" },
    { key: "_decision_je_arrete", label: "Ce que j'arrête" },
    { key: "_decision_je_teste", label: "Ce que je teste" },
  ];

  if (selectedFiche) {
    const fields = FICHE_FIELDS[selectedFiche.id] || [{ key: "contenu", label: "Contenu libre", type: "textarea" }];
    return (
      <div className="space-y-4" data-testid="fiche-editor">
        <Button variant="ghost" onClick={() => setSelectedFiche(null)} className="text-slate-500 -ml-2">
          <ChevronRight className="w-4 h-4 rotate-180 mr-1" /> Retour aux fiches
        </Button>
        <Card className="border border-slate-100">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Badge className="bg-[#1e3a5f]/10 text-[#1e3a5f]">Fiche {selectedFiche.number}</Badge>
              <CardTitle className="text-lg">{selectedFiche.title}</CardTitle>
            </div>
            <CardDescription>{selectedFiche.description}</CardDescription>
            {selectedBen && <p className="text-xs text-slate-400 mt-1">Bénéficiaire : {selectedBen.name}</p>}
          </CardHeader>
          <CardContent className="space-y-4">
            {fields.map(field => (
              <div key={field.key} className="space-y-1.5">
                <label className="text-sm font-medium text-slate-700">{field.label}</label>
                {field.type === "textarea" ? (
                  <Textarea value={ficheForm[field.key] || ""} onChange={e => setFicheForm({ ...ficheForm, [field.key]: e.target.value })}
                    placeholder="Saisissez ici..." className="resize-none min-h-[80px]" data-testid={`fiche-field-${field.key}`} />
                ) : field.type === "select" ? (
                  <Select value={ficheForm[field.key] || ""} onValueChange={v => setFicheForm({ ...ficheForm, [field.key]: v })}>
                    <SelectTrigger data-testid={`fiche-field-${field.key}`}><SelectValue placeholder="Choisir..." /></SelectTrigger>
                    <SelectContent>{field.options.map(o => <SelectItem key={o} value={o}>{o}</SelectItem>)}</SelectContent>
                  </Select>
                ) : null}
              </div>
            ))}

            {/* Bloc decisionnel V2 */}
            <div className="border-t border-slate-200 pt-4 mt-4">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-7 h-7 rounded-md bg-amber-100 flex items-center justify-center"><Lightbulb className="w-3.5 h-3.5 text-amber-700" /></div>
                <h4 className="text-sm font-semibold text-slate-800">Bloc décisionnel</h4>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {DECISION_KEYS.map(dk => (
                  <div key={dk.key} className="space-y-1.5">
                    <label className="text-xs font-medium text-slate-600">{dk.label}</label>
                    <Textarea value={ficheForm[dk.key] || ""} onChange={e => setFicheForm({ ...ficheForm, [dk.key]: e.target.value })}
                      placeholder={dk.label + "..."} className="resize-none min-h-[60px] text-sm" data-testid={`decision-${dk.key}`} />
                  </div>
                ))}
              </div>
            </div>

            <div className="flex gap-2 pt-2">
              <Button onClick={saveFiche} disabled={saving} className="bg-[#1e3a5f] hover:bg-[#152a45]" data-testid="save-fiche-btn">
                {saving ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Sauvegarde...</> : <><CheckCircle2 className="w-4 h-4 mr-2" /> Sauvegarder</>}
              </Button>
              <Button variant="outline" onClick={() => setSelectedFiche(null)}>Annuler</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (showConsent && selectedBenId) {
    return <ConsentManager beneficiaryId={selectedBenId} beneficiaryName={selectedBen?.name} token={token} onBack={() => setShowConsent(false)} />;
  }

  return (
    <div className="space-y-4" data-testid="outils-view">
      <Card className="border border-slate-100">
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><ClipboardList className="w-5 h-5 text-[#1e3a5f]" /> Outils d'accompagnement V2</CardTitle>
          <CardDescription>12 fiches augmentées — diagnostic, bilan, identité, stratégie, activation — avec blocs décisionnels intégrés</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center">
            <Select value={selectedBenId} onValueChange={setSelectedBenId}>
              <SelectTrigger className="flex-1" data-testid="outils-select-beneficiaire"><SelectValue placeholder="Choisir un bénéficiaire..." /></SelectTrigger>
              <SelectContent>{beneficiaires.map(b => <SelectItem key={b.id} value={b.id}>{b.name} — {b.sector}</SelectItem>)}</SelectContent>
            </Select>
            {selectedBenId && (
              <div className="flex items-center gap-2">
                <Progress value={selectedBen?.bilan_progress || 0} className="w-32 h-2" />
                <span className="text-xs text-slate-500 whitespace-nowrap">{completedFiches.length}/{fiches.length} fiches</span>
                <Button variant="outline" size="sm" className="text-xs" onClick={() => setShowConsent(true)} data-testid="consent-manage-btn">
                  <Shield className="w-3.5 h-3.5 mr-1" /> Consentement
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {selectedBenId && PHASES.map(phase => {
        const phaseFiches = fiches.filter(f => f.phase === phase.id);
        if (!phaseFiches.length) return null;
        const PhIcon = phase.icon;
        return (
          <Card key={phase.id} className="border border-slate-100">
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <div className={`w-7 h-7 rounded-md ${phase.color} flex items-center justify-center`}><PhIcon className="w-3.5 h-3.5" /></div>
                {phase.label}
                <Badge variant="secondary" className="text-xs ml-auto">{phaseFiches.filter(f => bilanData[f.id]).length}/{phaseFiches.length}</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {phaseFiches.map(fiche => {
                  const done = !!bilanData[fiche.id];
                  const hasDecisions = done && (bilanData[fiche.id]._decision_je_decide || bilanData[fiche.id]._decision_je_arrete || bilanData[fiche.id]._decision_je_teste);
                  return (
                    <div key={fiche.id} className={`flex items-center justify-between p-3 rounded-lg border cursor-pointer transition-all hover:border-[#1e3a5f]/30 ${done ? "bg-green-50/50 border-green-200" : "bg-white border-slate-100"}`}
                      onClick={() => openFiche(fiche)} data-testid={`fiche-card-${fiche.id}`}>
                      <div className="flex items-center gap-3">
                        <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold ${done ? "bg-green-100 text-green-700" : "bg-slate-100 text-slate-500"}`}>{fiche.number}</div>
                        <div>
                          <p className="text-sm font-medium text-slate-800">{fiche.title}</p>
                          <p className="text-[11px] text-slate-400 line-clamp-1">{fiche.description}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-1.5">
                        {hasDecisions && <Lightbulb className="w-4 h-4 text-amber-500 flex-shrink-0" />}
                        {done ? <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0" /> : <ChevronRight className="w-4 h-4 text-slate-300 flex-shrink-0" />}
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        );
      })}

      {!selectedBenId && (
        <Card className="border-dashed border-2 border-slate-200"><CardContent className="flex flex-col items-center justify-center py-12">
          <ClipboardList className="w-12 h-12 text-slate-300 mb-3" /><p className="text-slate-500 text-sm">Sélectionnez un bénéficiaire pour accéder aux fiches</p>
        </CardContent></Card>
      )}
    </div>
  );
};

// ===== CONSENT MANAGER =====
const CONSENT_LEVEL_INFO = {
  synthese: { label: "Synthèse partagée", description: "Le partenaire voit uniquement une synthèse générée", color: "bg-blue-100 text-blue-700 border-blue-200" },
  modulaire: { label: "Partage modulaire", description: "L'utilisateur choisit les rubriques visibles", color: "bg-amber-100 text-amber-700 border-amber-200" },
  complet_temporaire: { label: "Complet temporaire", description: "Accès étendu mais limité dans le temps", color: "bg-red-100 text-red-700 border-red-200" },
};

const ConsentManager = ({ beneficiaryId, beneficiaryName, token, onBack }) => {
  const [consents, setConsents] = useState([]);
  const [modules, setModules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [newLevel, setNewLevel] = useState("");
  const [newModules, setNewModules] = useState([]);
  const [newDuration, setNewDuration] = useState("90");
  const [newPurpose, setNewPurpose] = useState("Accompagnement socioprofessionnel");

  useEffect(() => { loadData(); }, [beneficiaryId]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [cRes, mRes] = await Promise.all([
        axios.get(`${API}/partenaires/consent/${beneficiaryId}?token=${token}`),
        axios.get(`${API}/partenaires/consent-modules?token=${token}`),
      ]);
      setConsents(cRes.data);
      setModules(mRes.data);
    } catch { }
    setLoading(false);
  };

  const createConsent = async () => {
    if (!newLevel) { toast.error("Choisissez un niveau"); return; }
    setCreating(true);
    try {
      const payload = {
        beneficiary_id: beneficiaryId,
        level: newLevel,
        modules: newLevel === "modulaire" ? newModules : null,
        duration_days: parseInt(newDuration),
        purpose: newPurpose,
      };
      await axios.post(`${API}/partenaires/consent?token=${token}`, payload, { headers: { "Content-Type": "application/json" } });
      toast.success("Consentement créé");
      setNewLevel("");
      setNewModules([]);
      loadData();
    } catch (err) { toast.error(err.response?.data?.detail || "Erreur"); }
    setCreating(false);
  };

  const revokeConsent = async (consentId) => {
    try {
      await axios.delete(`${API}/partenaires/consent/${consentId}?token=${token}`);
      toast.success("Consentement révoqué");
      loadData();
    } catch { toast.error("Erreur"); }
  };

  const toggleModule = (modId) => {
    setNewModules(prev => prev.includes(modId) ? prev.filter(m => m !== modId) : [...prev, modId]);
  };

  if (loading) return <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-[#1e3a5f]" /></div>;

  return (
    <div className="space-y-4" data-testid="consent-manager">
      <Button variant="ghost" onClick={onBack} className="text-slate-500 -ml-2">
        <ChevronRight className="w-4 h-4 rotate-180 mr-1" /> Retour aux fiches
      </Button>

      <Card className="border border-slate-100">
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><Shield className="w-5 h-5 text-[#1e3a5f]" /> Gestion du consentement</CardTitle>
          <CardDescription>Autorisations de partage pour {beneficiaryName} — granulaire, temporaire et révocable</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Active consents */}
          {consents.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-slate-700 mb-3">Consentements existants</h4>              <div className="space-y-2">
                {consents.map(c => {
                  const info = CONSENT_LEVEL_INFO[c.level] || CONSENT_LEVEL_INFO.synthese;
                  return (
                    <div key={c.id} className={`p-3 rounded-lg border ${c.active ? "border-slate-200 bg-white" : "border-slate-100 bg-slate-50 opacity-60"}`} data-testid={`consent-${c.id}`}>
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <Badge className={info.color}>{info.label}</Badge>
                          <Badge className={c.active ? "bg-green-100 text-green-700" : "bg-slate-100 text-slate-500"}>{c.status || (c.active ? "actif" : "inactif")}</Badge>
                          {c.remaining_days !== undefined && c.active && <span className="text-xs text-slate-500">{c.remaining_days}j restants</span>}
                        </div>
                        {c.active && (
                          <Button size="sm" variant="outline" className="text-red-500 hover:bg-red-50 h-7 text-xs" onClick={() => revokeConsent(c.id)} data-testid={`revoke-${c.id}`}>
                            Révoquer
                          </Button>
                        )}
                      </div>
                      <p className="text-xs text-slate-500">{c.purpose}</p>
                      {c.modules && c.modules.length > 0 && c.level === "modulaire" && (
                        <div className="flex flex-wrap gap-1 mt-2">
                          {c.modules.map(m => <Badge key={m} variant="secondary" className="text-[10px]">{modules.find(mod => mod.id === m)?.label || m}</Badge>)}
                        </div>
                      )}
                      <div className="flex items-center gap-3 mt-2 text-[10px] text-slate-400">
                        <span>Créé : {new Date(c.created_at).toLocaleDateString('fr-FR')}</span>
                        <span>Expire : {new Date(c.expires_at).toLocaleDateString('fr-FR')}</span>
                        {c.revoked_at && <span>Révoqué : {new Date(c.revoked_at).toLocaleDateString('fr-FR')}</span>}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Create new consent */}
          <div className="border-t border-slate-100 pt-4">
            <h4 className="text-sm font-semibold text-slate-700 mb-3">Nouveau consentement</h4>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {Object.entries(CONSENT_LEVEL_INFO).map(([key, info]) => (
                  <div key={key} className={`p-3 rounded-lg border-2 cursor-pointer transition-all ${newLevel === key ? "border-[#1e3a5f] bg-[#1e3a5f]/5" : "border-slate-100 hover:border-slate-300"}`}
                    onClick={() => setNewLevel(key)} data-testid={`consent-level-${key}`}>
                    <Badge className={`${info.color} mb-2`}>{info.label}</Badge>
                    <p className="text-xs text-slate-500">{info.description}</p>
                  </div>
                ))}
              </div>

              {newLevel === "modulaire" && (
                <div>
                  <label className="text-sm font-medium text-slate-700 mb-2 block">Modules à partager</label>
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                    {modules.map(m => (
                      <div key={m.id} className={`p-2 rounded-lg border cursor-pointer transition-all text-xs ${newModules.includes(m.id) ? "border-[#1e3a5f] bg-[#1e3a5f]/5 text-[#1e3a5f] font-medium" : "border-slate-100 text-slate-600 hover:border-slate-300"}`}
                        onClick={() => toggleModule(m.id)} data-testid={`module-${m.id}`}>
                        {m.label}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <label className="text-sm font-medium text-slate-700">Durée (jours)</label>
                  <Select value={newDuration} onValueChange={setNewDuration}>
                    <SelectTrigger data-testid="consent-duration"><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="30">30 jours</SelectItem>
                      <SelectItem value="60">60 jours</SelectItem>
                      <SelectItem value="90">90 jours</SelectItem>
                      <SelectItem value="180">180 jours</SelectItem>
                      <SelectItem value="365">1 an</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium text-slate-700">Objectif du partage</label>
                  <Input value={newPurpose} onChange={e => setNewPurpose(e.target.value)} data-testid="consent-purpose" />
                </div>
              </div>

              <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                <p className="text-xs text-slate-500 leading-relaxed">
                  <Shield className="w-3.5 h-3.5 inline mr-1 text-[#1e3a5f]" />
                  L'utilisateur conserve la maîtrise de ses données et peut autoriser, de manière ciblée, temporaire et réversible, le partage de tout ou partie de son espace personnel avec un partenaire de parcours.
                </p>
              </div>

              <Button onClick={createConsent} disabled={creating || !newLevel} className="bg-[#1e3a5f] hover:bg-[#152a45]" data-testid="create-consent-btn">
                {creating ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Création...</> : <><Shield className="w-4 h-4 mr-2" /> Créer le consentement</>}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// ===== OBSERVATOIRE CONTRIBUTION =====
const ObservatoireContribution = ({ token, stats, beneficiaires }) => {
  const [contributing, setContributing] = useState(false);
  const [lastContribution, setLastContribution] = useState(null);

  const freinsRepartition = {};
  const skillsCount = {};
  const sectorsCount = {};
  beneficiaires.forEach(b => {
    (b.freins || []).filter(f => f.status !== "resolu").forEach(f => { freinsRepartition[f.category] = (freinsRepartition[f.category] || 0) + 1; });
    (b.skills_acquired || []).forEach(s => { skillsCount[s] = (skillsCount[s] || 0) + 1; });
    sectorsCount[b.sector] = (sectorsCount[b.sector] || 0) + 1;
  });

  const contribute = async () => {
    setContributing(true);
    try {
      const res = await axios.post(`${API}/partenaires/contribution-observatoire?token=${token}`);
      setLastContribution(res.data);
      toast.success("Contribution envoyée !");
    } catch { toast.error("Erreur"); }
    setContributing(false);
  };

  return (
    <div className="space-y-4" data-testid="observatoire-contribution">
      <Card className="border border-slate-100">
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><Globe className="w-5 h-5 text-[#1e3a5f]" /> Contribution territoriale</CardTitle>
          <CardDescription>Alimentez l'observatoire prédictif avec vos données terrain — compétences émergentes, freins récurrents, tensions sectorielles — pour renforcer l'écosystème d'accompagnement</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="border border-slate-100 bg-slate-50">
              <CardContent className="p-4">
                <h4 className="text-sm font-semibold text-slate-700 mb-2 flex items-center gap-1.5"><AlertTriangle className="w-4 h-4 text-amber-600" /> Freins récurrents</h4>
                {Object.keys(freinsRepartition).length === 0 ? <p className="text-xs text-slate-400">Aucune donnée</p> : (
                  <div className="space-y-1.5">
                    {Object.entries(freinsRepartition).sort((a, b) => b[1] - a[1]).map(([cat, count]) => {
                      const fc = FREIN_CATEGORIES.find(c => c.value === cat) || FREIN_CATEGORIES[7];
                      return <div key={cat} className="flex items-center justify-between text-xs"><span className="text-slate-600">{fc.label}</span><Badge variant="secondary">{count}</Badge></div>;
                    })}
                  </div>
                )}
              </CardContent>
            </Card>
            <Card className="border border-slate-100 bg-slate-50">
              <CardContent className="p-4">
                <h4 className="text-sm font-semibold text-slate-700 mb-2 flex items-center gap-1.5"><Award className="w-4 h-4 text-[#1e3a5f]" /> Compétences émergentes</h4>
                {Object.keys(skillsCount).length === 0 ? <p className="text-xs text-slate-400">Aucune donnee</p> : (
                  <div className="flex flex-wrap gap-1.5">
                    {Object.entries(skillsCount).sort((a, b) => b[1] - a[1]).slice(0, 8).map(([skill, count]) => (
                      <Badge key={skill} className="bg-[#1e3a5f]/10 text-[#1e3a5f] text-xs">{skill} ({count})</Badge>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
            <Card className="border border-slate-100 bg-slate-50">
              <CardContent className="p-4">
                <h4 className="text-sm font-semibold text-slate-700 mb-2 flex items-center gap-1.5"><TrendingUp className="w-4 h-4 text-green-600" /> Tensions secteurs</h4>
                {Object.keys(sectorsCount).length === 0 ? <p className="text-xs text-slate-400">Aucune donnee</p> : (
                  <div className="space-y-1.5">
                    {Object.entries(sectorsCount).sort((a, b) => b[1] - a[1]).map(([sector, count]) => (
                      <div key={sector} className="flex items-center justify-between text-xs"><span className="text-slate-600">{sector}</span><Badge variant="secondary">{count}</Badge></div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
          <Button onClick={contribute} disabled={contributing} className="bg-[#1e3a5f] hover:bg-[#152a45]" data-testid="contribute-observatoire-btn">
            {contributing ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Envoi...</> : <><Globe className="w-4 h-4 mr-2" /> Envoyer à l'Observatoire</>}
          </Button>
          {lastContribution && <p className="text-xs text-green-600">Derniere contribution envoyee avec succes !</p>}
        </CardContent>
      </Card>
    </div>
  );
};

// ===== FREINS VIEW =====
const FreinsView = ({ beneficiaires, token, onRefresh }) => {
  const allFreins = beneficiaires.flatMap(b => (b.freins || []).map(f => ({ ...f, beneficiaire_name: b.name, beneficiaire_id: b.id })));
  const activeFreins = allFreins.filter(f => f.status !== "resolu");
  const resolvedFreins = allFreins.filter(f => f.status === "resolu");

  const handleResolve = async (benId, freinId) => {
    try {
      await axios.put(`${API}/partenaires/beneficiaires/${benId}/freins/${freinId}?token=${token}&status=resolu`);
      toast.success("Frein résolu !");
      onRefresh();
    } catch { toast.error("Erreur"); }
  };

  return (
    <div className="space-y-6" data-testid="freins-full-view">
      <Card className="border border-slate-100">
        <CardHeader><CardTitle className="flex items-center gap-2"><AlertTriangle className="w-5 h-5 text-amber-600" /> Freins actifs ({activeFreins.length})</CardTitle></CardHeader>
        <CardContent>
          {activeFreins.length === 0 ? <p className="text-sm text-slate-400 text-center py-8">Aucun frein actif</p> : (
            <div className="space-y-3">
              {activeFreins.map(f => {
                const cat = FREIN_CATEGORIES.find(c => c.value === f.category) || FREIN_CATEGORIES[7];
                const CIcon = cat.icon;
                return (
                  <div key={f.id} className="flex items-center justify-between p-3 rounded-xl border border-slate-100 hover:bg-slate-50 transition-all">
                    <div className="flex items-center gap-3">
                      <div className={`w-9 h-9 rounded-lg ${cat.color} flex items-center justify-center`}><CIcon className="w-4 h-4" /></div>
                      <div><p className="text-sm font-medium text-slate-900">{cat.label}</p><p className="text-xs text-slate-500">{f.beneficiaire_name}{f.description ? ` — ${f.description}` : ""}</p></div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={f.severity === "critique" ? "bg-red-100 text-red-700" : f.severity === "eleve" ? "bg-orange-100 text-orange-700" : "bg-amber-100 text-amber-700"}>{f.severity || "moyen"}</Badge>
                      <Button size="sm" variant="outline" className="text-green-600 hover:bg-green-50 h-8 text-xs" onClick={() => handleResolve(f.beneficiaire_id, f.id)}><CheckCircle2 className="w-3 h-3 mr-1" /> Résoudre</Button>
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
          <CardHeader><CardTitle className="flex items-center gap-2 text-base"><CheckCircle2 className="w-5 h-5 text-green-500" /> Resolus ({resolvedFreins.length})</CardTitle></CardHeader>
          <CardContent><div className="space-y-2">{resolvedFreins.map(f => {
            const cat = FREIN_CATEGORIES.find(c => c.value === f.category) || FREIN_CATEGORIES[7];
            return <div key={f.id} className="flex items-center gap-3 p-2 rounded-lg opacity-60"><CheckCircle2 className="w-4 h-4 text-green-500" /><span className="text-sm text-slate-500">{cat.label} — {f.beneficiaire_name}</span></div>;
          })}</div></CardContent>
        </Card>
      )}
    </div>
  );
};

// ===== DIALOGS =====
const CreateBeneficiaireDialog = ({ open, onOpenChange, token, onCreated }) => {
  const [name, setName] = useState(""); const [sector, setSector] = useState("Autre"); const [notes, setNotes] = useState(""); const [loading, setLoading] = useState(false);
  const handleCreate = async () => {
    if (!name.trim()) { toast.error("Nom requis"); return; }
    setLoading(true);
    try {
      await axios.post(`${API}/partenaires/beneficiaires?token=${token}&name=${encodeURIComponent(name.trim())}&sector=${encodeURIComponent(sector)}&notes=${encodeURIComponent(notes)}`);
      toast.success("Bénéficiaire ajouté !"); setName(""); setSector("Autre"); setNotes(""); onOpenChange(false); onCreated();
    } catch { toast.error("Erreur"); }
    setLoading(false);
  };
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[450px]" data-testid="create-beneficiaire-dialog">
        <DialogHeader><DialogTitle className="flex items-center gap-2"><Users className="w-5 h-5 text-[#1e3a5f]" /> Nouveau bénéficiaire</DialogTitle></DialogHeader>
        <div className="space-y-4 mt-2">
          <div className="space-y-2"><label className="text-sm font-medium text-slate-700">Nom *</label><Input placeholder="Prenom Nom" value={name} onChange={e => setName(e.target.value)} data-testid="create-name-input" /></div>
          <div className="space-y-2"><label className="text-sm font-medium text-slate-700">Secteur vise</label>
            <Select value={sector} onValueChange={setSector}><SelectTrigger data-testid="create-sector-select"><SelectValue /></SelectTrigger>
              <SelectContent>{["Administration", "Commerce", "Informatique", "Comptabilité", "Formation", "Santé", "Industrie", "Autre"].map(s => <SelectItem key={s} value={s}>{s}</SelectItem>)}</SelectContent>
            </Select></div>
          <div className="space-y-2"><label className="text-sm font-medium text-slate-700">Notes</label><Textarea placeholder="Contexte..." value={notes} onChange={e => setNotes(e.target.value)} className="resize-none h-20" data-testid="create-notes-input" /></div>
        </div>
        <DialogFooter className="mt-4"><Button variant="outline" onClick={() => onOpenChange(false)}>Annuler</Button>
          <Button onClick={handleCreate} disabled={loading || !name.trim()} className="bg-[#1e3a5f] hover:bg-[#152a45]" data-testid="create-submit-btn">{loading ? "Création..." : "Créer"}</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

const AddFreinDialog = ({ open, onOpenChange, beneficiaire, token, onAdded }) => {
  const [category, setCategory] = useState(""); const [description, setDescription] = useState(""); const [severity, setSeverity] = useState("moyen"); const [loading, setLoading] = useState(false);
  const handleAdd = async () => {
    if (!category || !beneficiaire) return;
    setLoading(true);
    try {
      await axios.post(`${API}/partenaires/beneficiaires/${beneficiaire.id}/freins?token=${token}&category=${encodeURIComponent(category)}&description=${encodeURIComponent(description)}&severity=${encodeURIComponent(severity)}`);
      toast.success("Frein ajouté"); setCategory(""); setDescription(""); setSeverity("moyen"); onOpenChange(false); onAdded();
    } catch (err) { toast.error(err.response?.data?.detail || "Erreur"); }
    setLoading(false);
  };
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[450px]" data-testid="add-frein-dialog">
        <DialogHeader><DialogTitle className="flex items-center gap-2"><AlertTriangle className="w-5 h-5 text-amber-600" /> Déclarer un frein</DialogTitle>
          <DialogDescription>{beneficiaire ? `Pour ${beneficiaire.name}` : ""}</DialogDescription></DialogHeader>
        <div className="space-y-4 mt-2">
          <div className="space-y-2"><label className="text-sm font-medium text-slate-700">Catégorie *</label>
            <Select value={category} onValueChange={setCategory}><SelectTrigger data-testid="frein-category-select"><SelectValue placeholder="Choisir..." /></SelectTrigger>
              <SelectContent>{FREIN_CATEGORIES.map(c => <SelectItem key={c.value} value={c.value}>{c.label}</SelectItem>)}</SelectContent></Select></div>
          <div className="space-y-2"><label className="text-sm font-medium text-slate-700">Description</label><Textarea placeholder="Details..." value={description} onChange={e => setDescription(e.target.value)} className="resize-none h-20" data-testid="frein-description-input" /></div>
          <div className="space-y-2"><label className="text-sm font-medium text-slate-700">Sévérité</label>
            <Select value={severity} onValueChange={setSeverity}><SelectTrigger data-testid="frein-severity-select"><SelectValue /></SelectTrigger>
              <SelectContent><SelectItem value="faible">Faible</SelectItem><SelectItem value="moyen">Moyen</SelectItem><SelectItem value="eleve">Eleve</SelectItem><SelectItem value="critique">Critique</SelectItem></SelectContent></Select></div>
        </div>
        <DialogFooter className="mt-4"><Button variant="outline" onClick={() => onOpenChange(false)}>Annuler</Button>
          <Button onClick={handleAdd} disabled={loading || !category} className="bg-[#1e3a5f] hover:bg-[#152a45]" data-testid="frein-submit-btn">{loading ? "Ajout..." : "Déclarer"}</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default PartenaireView;
