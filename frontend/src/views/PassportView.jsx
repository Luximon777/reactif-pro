import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Slider } from "@/components/ui/slider";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";
import {
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell, PieChart, Pie
} from "recharts";
import {
  User, Briefcase, GraduationCap, Sparkles, Target, Plus, RefreshCw,
  Shield, FolderLock, Brain, MessageCircle, Compass, TrendingUp,
  ChevronRight, Star, Award, BookOpen, Share2, Trash2, Zap, Edit3,
  Save, Check, ArrowRight, Layers, Activity, Hexagon, CircleDot
} from "lucide-react";

const SOURCE_CONFIG = {
  declaratif: { label: "Déclaré", color: "bg-slate-100 text-slate-600", icon: User },
  coffre_fort: { label: "Coffre-fort", color: "bg-blue-100 text-blue-700", icon: FolderLock },
  profil: { label: "Profil", color: "bg-indigo-100 text-indigo-700", icon: User },
  module: { label: "Formation", color: "bg-emerald-100 text-emerald-700", icon: GraduationCap },
  plateforme: { label: "RE'ACTIF PRO", color: "bg-blue-100 text-blue-700", icon: BookOpen },
  ubuntoo: { label: "Ubuntoo", color: "bg-teal-100 text-teal-700", icon: MessageCircle },
  ia_detectee: { label: "Détecté IA", color: "bg-violet-100 text-violet-700", icon: Brain },
  contribution: { label: "Contribution", color: "bg-amber-100 text-amber-700", icon: Sparkles },
};

const LEVEL_CONFIG = {
  debutant: { label: "Débutant", color: "bg-slate-200 text-slate-700", width: 25 },
  intermediaire: { label: "Intermédiaire", color: "bg-blue-200 text-blue-700", width: 50 },
  avance: { label: "Avancé", color: "bg-emerald-200 text-emerald-700", width: 75 },
  expert: { label: "Expert", color: "bg-amber-200 text-amber-700", width: 100 },
};

const CATEGORY_CONFIG = {
  technique: { label: "Technique", color: "text-blue-700 bg-blue-50 border-blue-200" },
  transversale: { label: "Transversale", color: "text-violet-700 bg-violet-50 border-violet-200" },
  transferable: { label: "Transférable", color: "text-amber-700 bg-amber-50 border-amber-200" },
  sectorielle: { label: "Sectorielle", color: "text-slate-700 bg-slate-50 border-slate-200" },
  relationnelle: { label: "Relationnelle", color: "text-emerald-700 bg-emerald-50 border-emerald-200" },
};

const NATURE_CONFIG = {
  savoir_faire: { label: "Savoir-faire", color: "bg-sky-600 text-white", icon: Briefcase, bgLight: "bg-sky-50 border-sky-200 text-sky-700" },
  savoir_etre: { label: "Savoir-être", color: "bg-rose-500 text-white", icon: Activity, bgLight: "bg-rose-50 border-rose-200 text-rose-700" },
};

const CCSP_POLES = {
  realisation: { label: "Réalisation", color: "bg-blue-600", textColor: "text-blue-700", bgLight: "bg-blue-50" },
  interaction: { label: "Interaction", color: "bg-emerald-600", textColor: "text-emerald-700", bgLight: "bg-emerald-50" },
  initiative: { label: "Initiative", color: "bg-amber-600", textColor: "text-amber-700", bgLight: "bg-amber-50" },
};

const CCSP_DEGREES = {
  imitation: { label: "Imitation", color: "bg-slate-500", level: 1 },
  adaptation: { label: "Adaptation", color: "bg-blue-500", level: 2 },
  transposition: { label: "Transposition", color: "bg-emerald-500", level: 3 },
};

const COMPONENT_LABELS = {
  connaissance: { label: "Connaissance", short: "Sav.", desc: "Savoirs théoriques et factuels", icon: BookOpen, color: "#3b82f6" },
  cognition: { label: "Cognition", short: "Cog.", desc: "Analyse, raisonnement, résolution", icon: Brain, color: "#8b5cf6" },
  conation: { label: "Conation", short: "Con.", desc: "Motivation, volonté, engagement", icon: Zap, color: "#f59e0b" },
  affection: { label: "Affection", short: "Aff.", desc: "Gestion émotionnelle, empathie", icon: Activity, color: "#ef4444" },
  sensori_moteur: { label: "Sensori-moteur", short: "S-M.", desc: "Habiletés physiques et pratiques", icon: Hexagon, color: "#10b981" },
};

const PassportView = ({ token }) => {
  const [passport, setPassport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState("profile");
  const [addCompDialogOpen, setAddCompDialogOpen] = useState(false);
  const [addExpDialogOpen, setAddExpDialogOpen] = useState(false);
  const [editingProfile, setEditingProfile] = useState(false);
  const [loadingPasserelles, setLoadingPasserelles] = useState(false);
  const [diagnostic, setDiagnostic] = useState(null);
  const [loadingDiagnostic, setLoadingDiagnostic] = useState(false);
  const [evaluatingComp, setEvaluatingComp] = useState(null);
  const [evalComponents, setEvalComponents] = useState({ connaissance: 0, cognition: 0, conation: 0, affection: 0, sensori_moteur: 0 });
  const [evalCcspPole, setEvalCcspPole] = useState("");
  const [evalCcspDegree, setEvalCcspDegree] = useState("");

  const [newComp, setNewComp] = useState({ name: "", nature: "", category: "technique", level: "intermediaire", experience_years: 0, components: null, ccsp_pole: "", ccsp_degree: "" });
  const [newExp, setNewExp] = useState({ title: "", organization: "", description: "", skills_used: "", achievements: "", experience_type: "professionnel" });
  const [profileEdit, setProfileEdit] = useState({ professional_summary: "", career_project: "", motivations: "", compatible_environments: "", target_sectors: "" });
  const [archeologie, setArcheologie] = useState(null);
  const [loadingArcheologie, setLoadingArcheologie] = useState(false);

  const loadPassport = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/passport?token=${token}`);
      setPassport(res.data);
    } catch (error) {
      console.error("Error loading passport:", error);
    }
    setLoading(false);
  }, [token]);

  useEffect(() => { loadPassport(); }, [loadPassport]);

  const loadDiagnostic = async () => {
    setLoadingDiagnostic(true);
    try {
      const res = await axios.get(`${API}/passport/diagnostic?token=${token}`);
      setDiagnostic(res.data);
    } catch (e) { toast.error("Erreur lors du chargement du diagnostic"); }
    setLoadingDiagnostic(false);
  };

  const loadArcheologie = async () => {
    setLoadingArcheologie(true);
    try {
      const res = await axios.get(`${API}/passport/archeologie?token=${token}`);
      setArcheologie(res.data);
    } catch (e) { toast.error("Erreur lors du chargement de l'archéologie"); }
    setLoadingArcheologie(false);
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await axios.post(`${API}/passport/refresh?token=${token}`);
      await loadPassport();
      toast.success("Passeport actualisé depuis toutes les sources");
    } catch (e) { toast.error("Erreur lors de l'actualisation"); }
    setRefreshing(false);
  };

  const handleAddCompetence = async () => {
    if (!newComp.name.trim()) return;
    try {
      const payload = { ...newComp };
      if (!payload.ccsp_pole) delete payload.ccsp_pole;
      if (!payload.ccsp_degree) delete payload.ccsp_degree;
      await axios.post(`${API}/passport/competences?token=${token}`, payload);
      toast.success("Compétence ajoutée");
      setAddCompDialogOpen(false);
      setNewComp({ name: "", nature: "", category: "technique", level: "intermediaire", experience_years: 0, components: null, ccsp_pole: "", ccsp_degree: "" });
      await loadPassport();
    } catch (e) { toast.error("Erreur lors de l'ajout"); }
  };

  const handleAddExperience = async () => {
    if (!newExp.title.trim()) return;
    try {
      const payload = {
        ...newExp,
        skills_used: newExp.skills_used ? newExp.skills_used.split(",").map(s => s.trim()).filter(Boolean) : [],
        achievements: newExp.achievements ? newExp.achievements.split(",").map(s => s.trim()).filter(Boolean) : [],
      };
      await axios.post(`${API}/passport/experiences?token=${token}`, payload);
      toast.success("Expérience ajoutée");
      setAddExpDialogOpen(false);
      setNewExp({ title: "", organization: "", description: "", skills_used: "", achievements: "", experience_type: "professionnel" });
      await loadPassport();
    } catch (e) { toast.error("Erreur lors de l'ajout"); }
  };

  const handleDeleteCompetence = async (compId) => {
    try {
      await axios.delete(`${API}/passport/competences/${compId}?token=${token}`);
      toast.success("Compétence supprimée");
      await loadPassport();
    } catch (e) { toast.error("Erreur lors de la suppression"); }
  };

  const handleDeleteExperience = async (expId) => {
    try {
      await axios.delete(`${API}/passport/experiences/${expId}?token=${token}`);
      toast.success("Expérience supprimée");
      await loadPassport();
    } catch (e) { toast.error("Erreur lors de la suppression"); }
  };

  const handleStartEditProfile = () => {
    setProfileEdit({
      professional_summary: passport?.professional_summary || "",
      career_project: passport?.career_project || "",
      motivations: (passport?.motivations || []).join(", "),
      compatible_environments: (passport?.compatible_environments || []).join(", "),
      target_sectors: (passport?.target_sectors || []).join(", "),
    });
    setEditingProfile(true);
  };

  const handleSaveProfile = async () => {
    try {
      await axios.put(`${API}/passport/profile?token=${token}`, {
        professional_summary: profileEdit.professional_summary || null,
        career_project: profileEdit.career_project || null,
        motivations: profileEdit.motivations ? profileEdit.motivations.split(",").map(s => s.trim()).filter(Boolean) : null,
        compatible_environments: profileEdit.compatible_environments ? profileEdit.compatible_environments.split(",").map(s => s.trim()).filter(Boolean) : null,
        target_sectors: profileEdit.target_sectors ? profileEdit.target_sectors.split(",").map(s => s.trim()).filter(Boolean) : null,
      });
      toast.success("Profil mis à jour");
      setEditingProfile(false);
      await loadPassport();
    } catch (e) { toast.error("Erreur lors de la mise à jour"); }
  };

  const handleLoadPasserelles = async () => {
    setLoadingPasserelles(true);
    try {
      const res = await axios.get(`${API}/passport/passerelles?token=${token}`);
      await loadPassport();
      if (res.data.passerelles?.length > 0) {
        toast.success(`${res.data.passerelles.length} passerelles identifiées par l'IA`);
      } else {
        toast.info("Ajoutez plus de compétences pour obtenir des suggestions");
      }
    } catch (e) { toast.error("Erreur lors de l'analyse IA"); }
    setLoadingPasserelles(false);
  };

  const handleOpenEvaluation = (comp) => {
    setEvaluatingComp(comp);
    setEvalComponents(comp.components || { connaissance: 0, cognition: 0, conation: 0, affection: 0, sensori_moteur: 0 });
    setEvalCcspPole(comp.ccsp_pole || "");
    setEvalCcspDegree(comp.ccsp_degree || "");
  };

  const handleSaveEvaluation = async () => {
    if (!evaluatingComp) return;
    try {
      await axios.put(`${API}/passport/competences/${evaluatingComp.id}/evaluate?token=${token}`, {
        components: evalComponents,
        ccsp_pole: evalCcspPole || null,
        ccsp_degree: evalCcspDegree || null,
      });
      toast.success("Évaluation enregistrée");
      setEvaluatingComp(null);
      await loadPassport();
    } catch (e) { toast.error("Erreur lors de l'évaluation"); }
  };

  if (loading) return <div className="flex items-center justify-center h-64"><RefreshCw className="w-8 h-8 animate-spin text-blue-600" /></div>;
  if (!passport) return <div className="text-center py-12 text-slate-500">Impossible de charger le passeport</div>;

  const { completeness_score = 0, competences = [], experiences = [], learning_path = [], passerelles = [], sources_count = {} } = passport;
  const mainCompetences = competences.filter(c => !c.is_emerging);
  const emergingCompetences = competences.filter(c => c.is_emerging);
  const savoirFaire = competences.filter(c => c.nature === "savoir_faire");
  const savoirEtre = competences.filter(c => c.nature === "savoir_etre");
  const nonClassees = competences.filter(c => !c.nature);

  return (
    <div className="space-y-6" data-testid="passport-view">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-[#1e3a5f] flex items-center gap-3">
            <Shield className="w-8 h-8" />
            Mon Passeport de Compétences
          </h1>
          <p className="text-slate-500 mt-1">Votre identité professionnelle numérique évolutive</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={handleRefresh} disabled={refreshing} data-testid="passport-refresh-btn">
            <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? "animate-spin" : ""}`} />
            Actualiser
          </Button>
        </div>
      </div>

      {/* Completeness + Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        <Card className="lg:col-span-2 bg-gradient-to-br from-[#1e3a5f] to-[#2d5a8e] text-white border-0">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold">Complétude du passeport</h3>
                <p className="text-blue-200 text-sm">Enrichissez votre profil pour de meilleures recommandations</p>
              </div>
              <div className="text-4xl font-bold">{completeness_score}%</div>
            </div>
            <Progress value={completeness_score} className="h-3 bg-white/20" />
            <div className="flex flex-wrap gap-3 mt-4">
              {Object.entries(sources_count).map(([src, count]) => {
                const config = SOURCE_CONFIG[src] || SOURCE_CONFIG.declaratif;
                return (
                  <div key={src} className="flex items-center gap-1 text-sm text-blue-100">
                    <config.icon className="w-3 h-3" />
                    <span>{config.label}: {count}</span>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
        <StatCard icon={Layers} value={competences.length} label="Compétences" sublabel={`${savoirFaire.length} savoir-faire / ${savoirEtre.length} savoir-être`} color="bg-blue-600" />
        <StatCard icon={Briefcase} value={experiences.length} label="Expériences" sublabel={`${learning_path.length} formations`} color="bg-emerald-600" />
      </div>

      {/* Main Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="flex flex-wrap gap-1 h-auto p-1 bg-slate-100">
          <TabsTrigger value="profile" className="text-xs sm:text-sm py-2" data-testid="passport-tab-profile">
            <User className="w-4 h-4 mr-1 hidden sm:inline" />Profil
          </TabsTrigger>
          <TabsTrigger value="competences" className="text-xs sm:text-sm py-2" data-testid="passport-tab-competences">
            <Star className="w-4 h-4 mr-1 hidden sm:inline" />Compétences
          </TabsTrigger>
          <TabsTrigger value="evaluation" className="text-xs sm:text-sm py-2" data-testid="passport-tab-evaluation">
            <Activity className="w-4 h-4 mr-1 hidden sm:inline" />Évaluation
          </TabsTrigger>
          <TabsTrigger value="archeologie" className="text-xs sm:text-sm py-2" data-testid="passport-tab-archeologie">
            <Layers className="w-4 h-4 mr-1 hidden sm:inline" />Archéologie
          </TabsTrigger>
          <TabsTrigger value="emerging" className="text-xs sm:text-sm py-2" data-testid="passport-tab-emerging">
            <Sparkles className="w-4 h-4 mr-1 hidden sm:inline" />Émergentes
          </TabsTrigger>
          <TabsTrigger value="experiences" className="text-xs sm:text-sm py-2" data-testid="passport-tab-experiences">
            <Briefcase className="w-4 h-4 mr-1 hidden sm:inline" />Expériences
          </TabsTrigger>
          <TabsTrigger value="passerelles" className="text-xs sm:text-sm py-2" data-testid="passport-tab-passerelles">
            <Compass className="w-4 h-4 mr-1 hidden sm:inline" />Passerelles
          </TabsTrigger>
        </TabsList>

        {/* Profile Tab */}
        <TabsContent value="profile" className="space-y-4 mt-4">
          <ProfileSection
            passport={passport}
            editing={editingProfile}
            profileEdit={profileEdit}
            setProfileEdit={setProfileEdit}
            onStartEdit={handleStartEditProfile}
            onSave={handleSaveProfile}
            onCancel={() => setEditingProfile(false)}
          />
        </TabsContent>

        {/* Main Competences Tab - with savoir-faire / savoir-être distinction */}
        <TabsContent value="competences" className="space-y-6 mt-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-slate-900">Mes compétences ({competences.length})</h3>
            <Dialog open={addCompDialogOpen} onOpenChange={setAddCompDialogOpen}>
              <DialogTrigger asChild>
                <Button size="sm" data-testid="add-competence-btn"><Plus className="w-4 h-4 mr-1" />Ajouter</Button>
              </DialogTrigger>
              <DialogContent className="max-w-lg max-h-[85vh] overflow-y-auto">
                <DialogHeader><DialogTitle>Ajouter une compétence</DialogTitle></DialogHeader>
                <AddCompetenceForm newComp={newComp} setNewComp={setNewComp} onSubmit={handleAddCompetence} />
              </DialogContent>
            </Dialog>
          </div>

          {/* Nature distribution bar */}
          {competences.length > 0 && (
            <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-xl">
              <div className="flex items-center gap-2 text-sm">
                <Briefcase className="w-4 h-4 text-sky-600" />
                <span className="font-medium text-sky-700">Savoir-faire: {savoirFaire.length}</span>
              </div>
              <div className="flex-1 h-3 bg-slate-200 rounded-full overflow-hidden flex">
                <div className="h-full bg-sky-500 transition-all" style={{ width: `${competences.length ? (savoirFaire.length / competences.length) * 100 : 0}%` }} />
                <div className="h-full bg-rose-400 transition-all" style={{ width: `${competences.length ? (savoirEtre.length / competences.length) * 100 : 0}%` }} />
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Activity className="w-4 h-4 text-rose-500" />
                <span className="font-medium text-rose-600">Savoir-être: {savoirEtre.length}</span>
              </div>
              {nonClassees.length > 0 && (
                <Badge variant="outline" className="text-xs text-slate-500">{nonClassees.length} non classées</Badge>
              )}
            </div>
          )}

          {/* Savoir-faire section */}
          {savoirFaire.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-3">
                <Briefcase className="w-4 h-4 text-sky-600" />
                <h4 className="font-medium text-sky-700">Savoir-faire (Hard Skills)</h4>
                <Badge className="bg-sky-100 text-sky-700 text-xs">{savoirFaire.length}</Badge>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {savoirFaire.map(comp => (
                  <CompetenceCard key={comp.id} comp={comp} onDelete={handleDeleteCompetence} onEvaluate={handleOpenEvaluation} />
                ))}
              </div>
            </div>
          )}

          {/* Savoir-être section */}
          {savoirEtre.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-3">
                <Activity className="w-4 h-4 text-rose-500" />
                <h4 className="font-medium text-rose-600">Savoir-être (Soft Skills)</h4>
                <Badge className="bg-rose-100 text-rose-600 text-xs">{savoirEtre.length}</Badge>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {savoirEtre.map(comp => (
                  <CompetenceCard key={comp.id} comp={comp} onDelete={handleDeleteCompetence} onEvaluate={handleOpenEvaluation} />
                ))}
              </div>
            </div>
          )}

          {/* Non-classées */}
          {nonClassees.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-3">
                <CircleDot className="w-4 h-4 text-slate-400" />
                <h4 className="font-medium text-slate-500">Non classées</h4>
                <Badge variant="outline" className="text-xs">{nonClassees.length}</Badge>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {nonClassees.map(comp => (
                  <CompetenceCard key={comp.id} comp={comp} onDelete={handleDeleteCompetence} onEvaluate={handleOpenEvaluation} />
                ))}
              </div>
            </div>
          )}

          {competences.length === 0 && <EmptyState text="Ajoutez vos compétences pour enrichir votre passeport" />}
        </TabsContent>

        {/* Evaluation Tab (Lamri & Lubart + CCSP) */}
        <TabsContent value="evaluation" className="space-y-6 mt-4">
          <EvaluationTab
            competences={competences}
            diagnostic={diagnostic}
            loadingDiagnostic={loadingDiagnostic}
            onLoadDiagnostic={loadDiagnostic}
            onEvaluate={handleOpenEvaluation}
          />
        </TabsContent>

        {/* Archéologie Tab (NEW) */}
        <TabsContent value="archeologie" className="space-y-6 mt-4">
          <ArcheologieTab
            archeologie={archeologie}
            loading={loadingArcheologie}
            onLoad={loadArcheologie}
            savoirFaire={savoirFaire}
            savoirEtre={savoirEtre}
            nonClassees={nonClassees}
          />
        </TabsContent>

        {/* Emerging Competences Tab */}
        <TabsContent value="emerging" className="space-y-4 mt-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-slate-900">Compétences émergentes ({emergingCompetences.length})</h3>
            <Badge className="bg-violet-100 text-violet-700"><Brain className="w-3 h-3 mr-1" />Détectées automatiquement</Badge>
          </div>
          <p className="text-sm text-slate-500">Compétences identifiées via l'IA, les échanges Ubuntoo et vos contributions</p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {emergingCompetences.map(comp => (
              <CompetenceCard key={comp.id} comp={comp} onDelete={handleDeleteCompetence} onEvaluate={handleOpenEvaluation} emerging />
            ))}
          </div>
          {emergingCompetences.length === 0 && <EmptyState text="Les compétences émergentes seront détectées automatiquement" />}
        </TabsContent>

        {/* Experiences Tab */}
        <TabsContent value="experiences" className="space-y-4 mt-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-slate-900">Expériences et réalisations ({experiences.length})</h3>
            <Dialog open={addExpDialogOpen} onOpenChange={setAddExpDialogOpen}>
              <DialogTrigger asChild>
                <Button size="sm" data-testid="add-experience-btn"><Plus className="w-4 h-4 mr-1" />Ajouter</Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader><DialogTitle>Ajouter une expérience</DialogTitle></DialogHeader>
                <div className="space-y-3">
                  <Input placeholder="Titre du poste / mission" value={newExp.title} onChange={e => setNewExp({...newExp, title: e.target.value})} data-testid="exp-title-input" />
                  <Input placeholder="Organisation" value={newExp.organization} onChange={e => setNewExp({...newExp, organization: e.target.value})} />
                  <Input placeholder="Description" value={newExp.description} onChange={e => setNewExp({...newExp, description: e.target.value})} />
                  <Input placeholder="Compétences utilisées (séparées par des virgules)" value={newExp.skills_used} onChange={e => setNewExp({...newExp, skills_used: e.target.value})} />
                  <Input placeholder="Réalisations clés (séparées par des virgules)" value={newExp.achievements} onChange={e => setNewExp({...newExp, achievements: e.target.value})} />
                  <Select value={newExp.experience_type} onValueChange={v => setNewExp({...newExp, experience_type: v})}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="professionnel">Professionnel</SelectItem>
                      <SelectItem value="personnel">Personnel</SelectItem>
                      <SelectItem value="benevole">Bénévole</SelectItem>
                      <SelectItem value="projet">Projet</SelectItem>
                    </SelectContent>
                  </Select>
                  <Button className="w-full" onClick={handleAddExperience} data-testid="submit-experience-btn">
                    <Check className="w-4 h-4 mr-2" />Ajouter l'expérience
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
          <div className="space-y-3">
            {experiences.map(exp => (
              <ExperienceCard key={exp.id} exp={exp} onDelete={handleDeleteExperience} />
            ))}
          </div>
          {experiences.length === 0 && <EmptyState text="Ajoutez vos expériences professionnelles et personnelles" />}
        </TabsContent>

        {/* Learning Path Tab */}
        <TabsContent value="learning" className="space-y-4 mt-4">
          <h3 className="font-semibold text-slate-900">Parcours d'apprentissage ({learning_path.length})</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {learning_path.map((item, idx) => (
              <LearningCard key={idx} item={item} />
            ))}
          </div>
          {learning_path.length === 0 && <EmptyState text="Les formations suivies apparaîtront ici automatiquement" />}
        </TabsContent>

        {/* Passerelles Tab */}
        <TabsContent value="passerelles" className="space-y-4 mt-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-slate-900">Passerelles professionnelles</h3>
              <p className="text-sm text-slate-500">Métiers compatibles avec votre profil, identifiés par l'IA</p>
            </div>
            <Button onClick={handleLoadPasserelles} disabled={loadingPasserelles} data-testid="load-passerelles-btn">
              {loadingPasserelles ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Brain className="w-4 h-4 mr-2" />}
              {loadingPasserelles ? "Analyse IA..." : "Analyser mon profil"}
            </Button>
          </div>
          <div className="space-y-3">
            {passerelles.map((p, idx) => (
              <PasserelleCard key={idx} passerelle={p} />
            ))}
          </div>
          {passerelles.length === 0 && !loadingPasserelles && (
            <EmptyState text="Cliquez sur 'Analyser mon profil' pour découvrir vos passerelles professionnelles" />
          )}
        </TabsContent>
      </Tabs>

      {/* Evaluation Dialog */}
      <Dialog open={!!evaluatingComp} onOpenChange={(open) => { if (!open) setEvaluatingComp(null); }}>
        <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-[#1e3a5f]" />
              Évaluer : {evaluatingComp?.name}
            </DialogTitle>
          </DialogHeader>
          <EvaluationForm
            components={evalComponents}
            setComponents={setEvalComponents}
            ccspPole={evalCcspPole}
            setCcspPole={setEvalCcspPole}
            ccspDegree={evalCcspDegree}
            setCcspDegree={setEvalCcspDegree}
            onSave={handleSaveEvaluation}
          />
        </DialogContent>
      </Dialog>
    </div>
  );
};

// ============== ADD COMPETENCE FORM ==============

const AddCompetenceForm = ({ newComp, setNewComp, onSubmit }) => (
  <div className="space-y-4">
    <Input placeholder="Nom de la compétence" value={newComp.name} onChange={e => setNewComp({...newComp, name: e.target.value})} data-testid="comp-name-input" />

    {/* Nature: Savoir-faire vs Savoir-être */}
    <div>
      <label className="text-xs font-medium text-slate-500 mb-1.5 block">Nature de la compétence</label>
      <div className="grid grid-cols-2 gap-2">
        <button
          type="button"
          onClick={() => setNewComp({...newComp, nature: "savoir_faire"})}
          className={`flex items-center gap-2 p-3 rounded-lg border-2 transition-all text-sm font-medium ${
            newComp.nature === "savoir_faire"
              ? "border-sky-500 bg-sky-50 text-sky-700"
              : "border-slate-200 text-slate-500 hover:border-slate-300"
          }`}
          data-testid="nature-savoir-faire"
        >
          <Briefcase className="w-4 h-4" />
          <div className="text-left">
            <p>Savoir-faire</p>
            <p className="text-xs font-normal opacity-70">Hard Skill technique</p>
          </div>
        </button>
        <button
          type="button"
          onClick={() => setNewComp({...newComp, nature: "savoir_etre"})}
          className={`flex items-center gap-2 p-3 rounded-lg border-2 transition-all text-sm font-medium ${
            newComp.nature === "savoir_etre"
              ? "border-rose-500 bg-rose-50 text-rose-700"
              : "border-slate-200 text-slate-500 hover:border-slate-300"
          }`}
          data-testid="nature-savoir-etre"
        >
          <Activity className="w-4 h-4" />
          <div className="text-left">
            <p>Savoir-être</p>
            <p className="text-xs font-normal opacity-70">Soft Skill comportemental</p>
          </div>
        </button>
      </div>
    </div>

    <div className="grid grid-cols-2 gap-3">
      <div>
        <label className="text-xs font-medium text-slate-500 mb-1 block">Catégorie</label>
        <Select value={newComp.category} onValueChange={v => setNewComp({...newComp, category: v})}>
          <SelectTrigger><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="technique">Technique</SelectItem>
            <SelectItem value="transversale">Transversale</SelectItem>
            <SelectItem value="transferable">Transférable</SelectItem>
            <SelectItem value="sectorielle">Sectorielle</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div>
        <label className="text-xs font-medium text-slate-500 mb-1 block">Niveau</label>
        <Select value={newComp.level} onValueChange={v => setNewComp({...newComp, level: v})}>
          <SelectTrigger><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="debutant">Débutant</SelectItem>
            <SelectItem value="intermediaire">Intermédiaire</SelectItem>
            <SelectItem value="avance">Avancé</SelectItem>
            <SelectItem value="expert">Expert</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>

    {/* CCSP Classification */}
    <div className="border-t pt-3">
      <p className="text-sm font-medium text-slate-700 mb-2 flex items-center gap-1">
        <CircleDot className="w-4 h-4" />Classification CCSP (optionnel)
      </p>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="text-xs text-slate-500 mb-1 block">Pôle</label>
          <Select value={newComp.ccsp_pole || "none"} onValueChange={v => setNewComp({...newComp, ccsp_pole: v === "none" ? "" : v})}>
            <SelectTrigger><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="none">Non défini</SelectItem>
              <SelectItem value="realisation">Réalisation</SelectItem>
              <SelectItem value="interaction">Interaction</SelectItem>
              <SelectItem value="initiative">Initiative</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div>
          <label className="text-xs text-slate-500 mb-1 block">Degré</label>
          <Select value={newComp.ccsp_degree || "none"} onValueChange={v => setNewComp({...newComp, ccsp_degree: v === "none" ? "" : v})}>
            <SelectTrigger><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="none">Non défini</SelectItem>
              <SelectItem value="imitation">Imitation</SelectItem>
              <SelectItem value="adaptation">Adaptation</SelectItem>
              <SelectItem value="transposition">Transposition</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>

    <Button className="w-full" onClick={onSubmit} data-testid="submit-competence-btn">
      <Check className="w-4 h-4 mr-2" />Ajouter la compétence
    </Button>
  </div>
);

// ============== EVALUATION FORM ==============

const EvaluationForm = ({ components, setComponents, ccspPole, setCcspPole, ccspDegree, setCcspDegree, onSave }) => {
  const radarData = Object.entries(COMPONENT_LABELS).map(([key, cfg]) => ({
    component: cfg.short,
    fullName: cfg.label,
    value: components[key] || 0,
    fullMark: 5,
  }));

  return (
    <div className="space-y-5">
      {/* Lamri & Lubart 5 Components */}
      <div>
        <h4 className="text-sm font-semibold text-[#1e3a5f] mb-1">Modèle Lamri & Lubart - 5 composantes</h4>
        <p className="text-xs text-slate-400 mb-3">Évaluez chaque composante de 0 (non développé) à 5 (maîtrisé)</p>
        <div className="space-y-4">
          {Object.entries(COMPONENT_LABELS).map(([key, cfg]) => {
            const Icon = cfg.icon;
            return (
              <div key={key}>
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center gap-2">
                    <Icon className="w-4 h-4" style={{ color: cfg.color }} />
                    <span className="text-sm font-medium text-slate-700">{cfg.label}</span>
                  </div>
                  <span className="text-sm font-bold" style={{ color: cfg.color }}>{components[key]}/5</span>
                </div>
                <Slider
                  value={[components[key]]}
                  onValueChange={([v]) => setComponents({...components, [key]: v})}
                  max={5}
                  step={1}
                  className="w-full"
                  data-testid={`eval-slider-${key}`}
                />
                <p className="text-xs text-slate-400 mt-0.5">{cfg.desc}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Radar Preview */}
      <div className="bg-slate-50 rounded-xl p-4">
        <h4 className="text-xs font-medium text-slate-500 mb-2 text-center">Profil de compétence</h4>
        <ResponsiveContainer width="100%" height={200}>
          <RadarChart data={radarData}>
            <PolarGrid stroke="#e2e8f0" />
            <PolarAngleAxis dataKey="component" tick={{ fontSize: 11, fill: "#64748b" }} />
            <PolarRadiusAxis angle={90} domain={[0, 5]} tick={false} axisLine={false} />
            <Radar dataKey="value" stroke="#1e3a5f" fill="#1e3a5f" fillOpacity={0.2} strokeWidth={2} />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* CCSP Classification */}
      <div className="border-t pt-4">
        <h4 className="text-sm font-semibold text-[#1e3a5f] mb-3 flex items-center gap-1">
          <CircleDot className="w-4 h-4" />Référentiel CCSP
        </h4>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-slate-500 mb-1 block">Pôle de compétence</label>
            <Select value={ccspPole || "none"} onValueChange={v => setCcspPole(v === "none" ? "" : v)}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="none">Non défini</SelectItem>
                <SelectItem value="realisation">Réalisation</SelectItem>
                <SelectItem value="interaction">Interaction</SelectItem>
                <SelectItem value="initiative">Initiative</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <label className="text-xs text-slate-500 mb-1 block">Degré de maîtrise</label>
            <Select value={ccspDegree || "none"} onValueChange={v => setCcspDegree(v === "none" ? "" : v)}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="none">Non défini</SelectItem>
                <SelectItem value="imitation">Imitation</SelectItem>
                <SelectItem value="adaptation">Adaptation</SelectItem>
                <SelectItem value="transposition">Transposition</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      <Button className="w-full" onClick={onSave} data-testid="save-evaluation-btn">
        <Save className="w-4 h-4 mr-2" />Enregistrer l'évaluation
      </Button>
    </div>
  );
};

// ============== EVALUATION TAB ==============

const EvaluationTab = ({ competences, diagnostic, loadingDiagnostic, onLoadDiagnostic, onEvaluate }) => {
  const evaluated = competences.filter(c => {
    const cmp = c.components || {};
    return Object.values(cmp).some(v => v > 0);
  });
  const notEvaluated = competences.filter(c => {
    const cmp = c.components || {};
    return !Object.values(cmp).some(v => v > 0);
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-[#1e3a5f] flex items-center gap-2">
            <Activity className="w-5 h-5" />Évaluation des compétences
          </h3>
          <p className="text-sm text-slate-500">Évaluez vos compétences selon le modèle Lamri & Lubart et le référentiel CCSP</p>
        </div>
        <Button onClick={onLoadDiagnostic} disabled={loadingDiagnostic} data-testid="load-diagnostic-btn">
          {loadingDiagnostic ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <TrendingUp className="w-4 h-4 mr-2" />}
          {loadingDiagnostic ? "Chargement..." : "Générer le diagnostic"}
        </Button>
      </div>

      {/* Diagnostic Results */}
      {diagnostic && <DiagnosticView diagnostic={diagnostic} />}

      {/* Frameworks Explanation */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="border-l-4 border-l-[#1e3a5f]">
          <CardContent className="p-4">
            <h4 className="font-semibold text-[#1e3a5f] mb-2 text-sm">Modèle Lamri & Lubart</h4>
            <p className="text-xs text-slate-500 mb-3">Chaque compétence se décompose en 5 composantes :</p>
            <div className="space-y-1.5">
              {Object.entries(COMPONENT_LABELS).map(([key, cfg]) => {
                const Icon = cfg.icon;
                return (
                  <div key={key} className="flex items-center gap-2 text-xs">
                    <Icon className="w-3.5 h-3.5 flex-shrink-0" style={{ color: cfg.color }} />
                    <span className="font-medium text-slate-700">{cfg.label}:</span>
                    <span className="text-slate-500">{cfg.desc}</span>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
        <Card className="border-l-4 border-l-emerald-600">
          <CardContent className="p-4">
            <h4 className="font-semibold text-emerald-700 mb-2 text-sm">Référentiel CCSP</h4>
            <p className="text-xs text-slate-500 mb-3">Classification en 3 pôles et 3 degrés de maîtrise :</p>
            <div className="mb-2">
              <p className="text-xs font-medium text-slate-600 mb-1">Pôles :</p>
              <div className="flex flex-wrap gap-1.5">
                {Object.entries(CCSP_POLES).map(([k, cfg]) => (
                  <Badge key={k} className={`text-xs ${cfg.bgLight} ${cfg.textColor}`}>{cfg.label}</Badge>
                ))}
              </div>
            </div>
            <div>
              <p className="text-xs font-medium text-slate-600 mb-1">Degrés :</p>
              <div className="flex gap-1.5">
                {Object.entries(CCSP_DEGREES).map(([k, cfg]) => (
                  <Badge key={k} variant="outline" className="text-xs">{cfg.label} (niv. {cfg.level})</Badge>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Competences to evaluate */}
      {notEvaluated.length > 0 && (
        <div>
          <h4 className="font-medium text-slate-700 mb-3">
            Compétences à évaluer ({notEvaluated.length})
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {notEvaluated.map(comp => (
              <Card key={comp.id} className="hover:shadow-md transition-shadow border-dashed" data-testid="unevaluated-comp-card">
                <CardContent className="p-4 flex items-center justify-between">
                  <div>
                    <p className="font-medium text-slate-800 text-sm">{comp.name}</p>
                    <p className="text-xs text-slate-400">Non évaluée</p>
                  </div>
                  <Button size="sm" variant="outline" onClick={() => onEvaluate(comp)} data-testid={`evaluate-btn-${comp.id}`}>
                    <Edit3 className="w-3.5 h-3.5 mr-1" />Évaluer
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Already evaluated */}
      {evaluated.length > 0 && (
        <div>
          <h4 className="font-medium text-slate-700 mb-3">
            Compétences évaluées ({evaluated.length})
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {evaluated.map(comp => (
              <EvaluatedCompCard key={comp.id} comp={comp} onEvaluate={onEvaluate} />
            ))}
          </div>
        </div>
      )}

      {competences.length === 0 && <EmptyState text="Ajoutez des compétences dans l'onglet 'Compétences' pour les évaluer ici" />}
    </div>
  );
};

// ============== DIAGNOSTIC VIEW ==============

const DiagnosticView = ({ diagnostic }) => {
  const { lamri_lubart_profile, ccsp_distribution, recommendations, evaluated_count, total_competences } = diagnostic;

  const radarData = Object.entries(COMPONENT_LABELS).map(([key, cfg]) => ({
    component: cfg.label,
    value: lamri_lubart_profile?.[key] || 0,
    fullMark: 5,
  }));

  const poleData = Object.entries(ccsp_distribution?.poles || {}).map(([key, value]) => ({
    name: CCSP_POLES[key]?.label || key,
    value,
    color: key === "realisation" ? "#3b82f6" : key === "interaction" ? "#10b981" : "#f59e0b",
  }));

  const degreeData = Object.entries(ccsp_distribution?.degrees || {}).map(([key, value]) => ({
    name: CCSP_DEGREES[key]?.label || key,
    value,
    color: key === "imitation" ? "#94a3b8" : key === "adaptation" ? "#3b82f6" : "#10b981",
  }));

  return (
    <div className="space-y-4">
      <Card className="bg-gradient-to-r from-[#1e3a5f] to-[#2d5a8e] text-white border-0">
        <CardContent className="p-5">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-semibold text-lg">Votre Diagnostic</h4>
              <p className="text-blue-200 text-sm">{evaluated_count}/{total_competences} compétences évaluées</p>
            </div>
            <div className="text-right">
              <Progress value={(evaluated_count / Math.max(total_competences, 1)) * 100} className="h-2 w-32 bg-white/20" />
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Radar - Lamri & Lubart Profile */}
        <Card className="md:col-span-1">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-[#1e3a5f]">Profil Lamri & Lubart</CardTitle>
          </CardHeader>
          <CardContent className="pb-4">
            <ResponsiveContainer width="100%" height={220}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="#e2e8f0" />
                <PolarAngleAxis dataKey="component" tick={{ fontSize: 10, fill: "#64748b" }} />
                <PolarRadiusAxis angle={90} domain={[0, 5]} tick={false} axisLine={false} />
                <Radar dataKey="value" stroke="#1e3a5f" fill="#1e3a5f" fillOpacity={0.25} strokeWidth={2} />
              </RadarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* CCSP Poles Distribution */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-emerald-700">Pôles CCSP</CardTitle>
          </CardHeader>
          <CardContent className="pb-4">
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={poleData} layout="vertical" margin={{ left: 10 }}>
                <XAxis type="number" tick={{ fontSize: 11 }} />
                <YAxis dataKey="name" type="category" tick={{ fontSize: 11 }} width={80} />
                <Tooltip />
                <Bar dataKey="value" radius={[0, 6, 6, 0]}>
                  {poleData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* CCSP Degrees Distribution */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-amber-700">Degrés CCSP</CardTitle>
          </CardHeader>
          <CardContent className="pb-4">
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={degreeData} layout="vertical" margin={{ left: 10 }}>
                <XAxis type="number" tick={{ fontSize: 11 }} />
                <YAxis dataKey="name" type="category" tick={{ fontSize: 11 }} width={90} />
                <Tooltip />
                <Bar dataKey="value" radius={[0, 6, 6, 0]}>
                  {degreeData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Recommendations */}
      {recommendations?.length > 0 && (
        <Card className="border-amber-200 bg-amber-50/30">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-amber-800 flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />Recommandations
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {recommendations.map((rec, i) => (
              <div key={i} className="flex items-start gap-2 p-2 rounded-lg bg-white/60" data-testid="recommendation-item">
                <ChevronRight className="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-sm text-slate-700">{rec.message}</p>
                  <Badge variant="outline" className="text-xs mt-1">{rec.type}</Badge>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

// ============== EVALUATED COMPETENCE CARD ==============

const EvaluatedCompCard = ({ comp, onEvaluate }) => {
  const cmp = comp.components || {};
  const radarData = Object.entries(COMPONENT_LABELS).map(([key, cfg]) => ({
    component: cfg.short,
    value: cmp[key] || 0,
    fullMark: 5,
  }));
  const poleConfig = CCSP_POLES[comp.ccsp_pole];
  const degreeConfig = CCSP_DEGREES[comp.ccsp_degree];

  return (
    <Card className="hover:shadow-md transition-shadow" data-testid="evaluated-comp-card">
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-2">
          <div>
            <h4 className="font-semibold text-slate-900 text-sm">{comp.name}</h4>
            <div className="flex items-center gap-1 mt-1 flex-wrap">
              {poleConfig && <Badge className={`text-xs ${poleConfig.bgLight} ${poleConfig.textColor}`}>{poleConfig.label}</Badge>}
              {degreeConfig && <Badge variant="outline" className="text-xs">{degreeConfig.label}</Badge>}
            </div>
          </div>
          <Button size="sm" variant="ghost" onClick={() => onEvaluate(comp)} className="text-slate-400 hover:text-[#1e3a5f]">
            <Edit3 className="w-3.5 h-3.5" />
          </Button>
        </div>
        <ResponsiveContainer width="100%" height={150}>
          <RadarChart data={radarData}>
            <PolarGrid stroke="#e2e8f0" />
            <PolarAngleAxis dataKey="component" tick={{ fontSize: 10, fill: "#94a3b8" }} />
            <PolarRadiusAxis angle={90} domain={[0, 5]} tick={false} axisLine={false} />
            <Radar dataKey="value" stroke="#1e3a5f" fill="#1e3a5f" fillOpacity={0.2} strokeWidth={1.5} />
          </RadarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

// ============== EXISTING SUB-COMPONENTS ==============

const StatCard = ({ icon: Icon, value, label, sublabel, color }) => (
  <Card>
    <CardContent className="p-4">
      <div className="flex items-center gap-3">
        <div className={`w-12 h-12 rounded-xl ${color} text-white flex items-center justify-center`}>
          <Icon className="w-6 h-6" />
        </div>
        <div>
          <p className="text-3xl font-bold text-slate-900">{value}</p>
          <p className="text-sm text-slate-600">{label}</p>
          {sublabel && <p className="text-xs text-slate-400">{sublabel}</p>}
        </div>
      </div>
    </CardContent>
  </Card>
);

const EmptyState = ({ text }) => (
  <div className="text-center py-10 text-slate-400 border-2 border-dashed border-slate-200 rounded-xl">
    <p className="text-sm">{text}</p>
  </div>
);

const ProfileSection = ({ passport, editing, profileEdit, setProfileEdit, onStartEdit, onSave, onCancel }) => (
  <Card>
    <CardHeader className="flex flex-row items-center justify-between">
      <div>
        <CardTitle className="flex items-center gap-2"><User className="w-5 h-5 text-[#1e3a5f]" />Profil professionnel</CardTitle>
        <CardDescription>Votre synthèse professionnelle et vos objectifs</CardDescription>
      </div>
      {!editing ? (
        <Button variant="outline" size="sm" onClick={onStartEdit} data-testid="edit-profile-btn"><Edit3 className="w-4 h-4 mr-1" />Modifier</Button>
      ) : (
        <div className="flex gap-2">
          <Button size="sm" onClick={onSave} data-testid="save-profile-btn"><Save className="w-4 h-4 mr-1" />Enregistrer</Button>
          <Button variant="outline" size="sm" onClick={onCancel}>Annuler</Button>
        </div>
      )}
    </CardHeader>
    <CardContent className="space-y-4">
      {editing ? (
        <>
          <ProfileField label="Synthèse professionnelle" value={profileEdit.professional_summary} onChange={v => setProfileEdit({...profileEdit, professional_summary: v})} testId="profile-summary-input" />
          <ProfileField label="Projet professionnel" value={profileEdit.career_project} onChange={v => setProfileEdit({...profileEdit, career_project: v})} testId="profile-project-input" />
          <ProfileField label="Motivations (séparées par des virgules)" value={profileEdit.motivations} onChange={v => setProfileEdit({...profileEdit, motivations: v})} />
          <ProfileField label="Environnements compatibles (séparés par des virgules)" value={profileEdit.compatible_environments} onChange={v => setProfileEdit({...profileEdit, compatible_environments: v})} />
          <ProfileField label="Secteurs cibles (séparés par des virgules)" value={profileEdit.target_sectors} onChange={v => setProfileEdit({...profileEdit, target_sectors: v})} />
        </>
      ) : (
        <>
          <ProfileDisplay label="Synthèse professionnelle" value={passport.professional_summary} icon={User} />
          <ProfileDisplay label="Projet professionnel" value={passport.career_project} icon={Target} />
          <ProfileDisplayList label="Motivations" items={passport.motivations} icon={Zap} />
          <ProfileDisplayList label="Environnements compatibles" items={passport.compatible_environments} icon={Compass} />
          <ProfileDisplayList label="Secteurs cibles" items={passport.target_sectors} icon={Briefcase} />
        </>
      )}
    </CardContent>
  </Card>
);

const ProfileField = ({ label, value, onChange, testId }) => (
  <div>
    <label className="text-sm font-medium text-slate-700 mb-1 block">{label}</label>
    <Input value={value} onChange={e => onChange(e.target.value)} data-testid={testId} />
  </div>
);

const ProfileDisplay = ({ label, value, icon: Icon }) => (
  <div className="flex items-start gap-3 p-3 rounded-lg bg-slate-50">
    <Icon className="w-4 h-4 text-[#1e3a5f] mt-0.5 flex-shrink-0" />
    <div>
      <p className="text-xs font-medium text-slate-500">{label}</p>
      <p className="text-sm text-slate-800">{value || <span className="italic text-slate-400">Non renseigné</span>}</p>
    </div>
  </div>
);

const ProfileDisplayList = ({ label, items, icon: Icon }) => (
  <div className="flex items-start gap-3 p-3 rounded-lg bg-slate-50">
    <Icon className="w-4 h-4 text-[#1e3a5f] mt-0.5 flex-shrink-0" />
    <div>
      <p className="text-xs font-medium text-slate-500">{label}</p>
      {items && items.length > 0 ? (
        <div className="flex flex-wrap gap-1 mt-1">
          {items.map((item, i) => <Badge key={i} variant="secondary" className="text-xs">{item}</Badge>)}
        </div>
      ) : <p className="text-sm italic text-slate-400">Non renseigné</p>}
    </div>
  </div>
);

const CompetenceCard = ({ comp, onDelete, onEvaluate, emerging }) => {
  const levelConfig = LEVEL_CONFIG[comp.level] || LEVEL_CONFIG.intermediaire;
  const catConfig = CATEGORY_CONFIG[comp.category] || CATEGORY_CONFIG.technique;
  const srcConfig = SOURCE_CONFIG[comp.source] || SOURCE_CONFIG.declaratif;
  const SrcIcon = srcConfig.icon;
  const poleConfig = CCSP_POLES[comp.ccsp_pole];
  const degreeConfig = CCSP_DEGREES[comp.ccsp_degree];
  const natureConfig = NATURE_CONFIG[comp.nature];
  const hasEval = comp.components && Object.values(comp.components).some(v => v > 0);

  return (
    <Card className={`hover:shadow-md transition-shadow ${emerging ? "border-violet-200 bg-violet-50/30" : ""} ${comp.nature === "savoir_faire" ? "border-l-4 border-l-sky-400" : comp.nature === "savoir_etre" ? "border-l-4 border-l-rose-400" : ""}`} data-testid="competence-card">
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-2">
          <div>
            <h4 className="font-semibold text-slate-900 text-sm">{comp.name}</h4>
            <div className="flex items-center gap-1 mt-1 flex-wrap">
              {natureConfig && <Badge className={`text-xs ${natureConfig.bgLight} border`}>{natureConfig.label}</Badge>}
              <Badge variant="outline" className={`text-xs ${catConfig.color}`}>{catConfig.label}</Badge>
              <Badge className={`text-xs ${srcConfig.color}`}><SrcIcon className="w-3 h-3 mr-0.5" />{srcConfig.label}</Badge>
              {poleConfig && <Badge className={`text-xs ${poleConfig.bgLight} ${poleConfig.textColor}`}>{poleConfig.label}</Badge>}
              {degreeConfig && <Badge variant="outline" className="text-xs">{degreeConfig.label}</Badge>}
            </div>
          </div>
          <div className="flex items-center gap-0.5">
            <Button variant="ghost" size="sm" className="h-7 w-7 p-0 text-slate-400 hover:text-[#1e3a5f]" onClick={() => onEvaluate(comp)} data-testid={`evaluate-comp-${comp.id}`}>
              <Activity className="w-3.5 h-3.5" />
            </Button>
            {comp.source === "declaratif" && (
              <Button variant="ghost" size="sm" className="h-7 w-7 p-0 text-slate-400 hover:text-red-500" onClick={() => onDelete(comp.id)}>
                <Trash2 className="w-3.5 h-3.5" />
              </Button>
            )}
          </div>
        </div>
        <div className="mt-3">
          <div className="flex items-center justify-between text-xs mb-1">
            <span className="text-slate-500">Niveau</span>
            <span className={`font-medium ${levelConfig.color} px-2 py-0.5 rounded-full`}>{levelConfig.label}</span>
          </div>
          <Progress value={levelConfig.width} className="h-1.5" />
        </div>
        {/* Mini component bars */}
        {hasEval && (
          <div className="mt-3 flex items-center gap-1">
            {Object.entries(COMPONENT_LABELS).map(([key, cfg]) => {
              const val = comp.components?.[key] || 0;
              return (
                <div key={key} className="flex-1" title={`${cfg.label}: ${val}/5`}>
                  <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                    <div className="h-full rounded-full" style={{ width: `${(val / 5) * 100}%`, backgroundColor: cfg.color }} />
                  </div>
                </div>
              );
            })}
          </div>
        )}
        {comp.proof && (
          <div className="mt-2 flex items-center gap-1 text-xs text-blue-600">
            <Award className="w-3 h-3" /><span>Preuve: {comp.proof}</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

const ExperienceCard = ({ exp, onDelete }) => {
  const typeLabels = { professionnel: "Professionnel", personnel: "Personnel", benevole: "Bénévole", projet: "Projet" };
  return (
    <Card className="hover:shadow-md transition-shadow" data-testid="experience-card">
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <h4 className="font-semibold text-slate-900">{exp.title}</h4>
              <Badge variant="outline" className="text-xs">{typeLabels[exp.experience_type] || "Autre"}</Badge>
              {exp.is_current && <Badge className="bg-emerald-100 text-emerald-700 text-xs">En cours</Badge>}
            </div>
            {exp.organization && <p className="text-sm text-slate-600">{exp.organization}</p>}
            {exp.description && <p className="text-sm text-slate-500 mt-1">{exp.description}</p>}
            {exp.skills_used?.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-2">
                {exp.skills_used.map((s, i) => <Badge key={i} className="bg-blue-50 text-blue-700 text-xs">{s}</Badge>)}
              </div>
            )}
            {exp.achievements?.length > 0 && (
              <div className="mt-2">
                {exp.achievements.map((a, i) => (
                  <div key={i} className="flex items-center gap-1 text-xs text-emerald-700">
                    <Check className="w-3 h-3" /><span>{a}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
          {exp.source === "declaratif" && (
            <Button variant="ghost" size="sm" className="h-7 w-7 p-0 text-slate-400 hover:text-red-500" onClick={() => onDelete(exp.id)}>
              <Trash2 className="w-3.5 h-3.5" />
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

const LearningCard = ({ item }) => {
  const statusConfig = { en_cours: { label: "En cours", color: "bg-blue-100 text-blue-700" }, termine: { label: "Terminé", color: "bg-emerald-100 text-emerald-700" }, valide: { label: "Validé", color: "bg-green-100 text-green-800" } };
  const sc = statusConfig[item.status] || statusConfig.en_cours;
  return (
    <Card data-testid="learning-card">
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-2">
          <h4 className="font-semibold text-slate-900 text-sm">{item.title}</h4>
          <Badge className={`text-xs ${sc.color}`}>{sc.label}</Badge>
        </div>
        {item.provider && <p className="text-xs text-slate-500 mb-2">{item.provider}</p>}
        {item.skills_acquired?.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {item.skills_acquired.map((s, i) => <Badge key={i} variant="secondary" className="text-xs">{s}</Badge>)}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

const PasserelleCard = ({ passerelle }) => {
  const accessConfig = {
    accessible: { label: "Accessible directement", color: "bg-emerald-100 text-emerald-700" },
    formation_courte: { label: "Formation courte requise", color: "bg-amber-100 text-amber-700" },
    formation_longue: { label: "Formation longue requise", color: "bg-rose-100 text-rose-700" },
  };
  const ac = accessConfig[passerelle.accessibility] || accessConfig.accessible;
  const score = Math.round((passerelle.compatibility_score || 0) * 100);

  return (
    <Card className="hover:shadow-md transition-shadow border-l-4 border-l-blue-500" data-testid="passerelle-card">
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-2">
          <div>
            <h4 className="font-semibold text-slate-900 text-base flex items-center gap-2">
              <ArrowRight className="w-4 h-4 text-blue-600" />{passerelle.job_name}
            </h4>
            {passerelle.sector && <p className="text-sm text-slate-500 ml-6">{passerelle.sector}</p>}
          </div>
          <div className="text-right">
            <span className="text-2xl font-bold text-blue-600">{score}%</span>
            <p className="text-xs text-slate-500">compatibilité</p>
          </div>
        </div>
        <Badge className={`text-xs ${ac.color} mb-3`}>{ac.label}</Badge>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-2">
          {passerelle.shared_skills?.length > 0 && (
            <div>
              <p className="text-xs font-medium text-emerald-700 mb-1">Compétences partagées</p>
              <div className="flex flex-wrap gap-1">
                {passerelle.shared_skills.map((s, i) => <Badge key={i} className="bg-emerald-50 text-emerald-700 text-xs">{s}</Badge>)}
              </div>
            </div>
          )}
          {passerelle.skills_to_acquire?.length > 0 && (
            <div>
              <p className="text-xs font-medium text-amber-700 mb-1">À acquérir</p>
              <div className="flex flex-wrap gap-1">
                {passerelle.skills_to_acquire.map((s, i) => <Badge key={i} className="bg-amber-50 text-amber-700 text-xs">{s}</Badge>)}
              </div>
            </div>
          )}
        </div>
        {passerelle.training_needed && (
          <p className="text-xs text-slate-600 mt-2 p-2 bg-slate-50 rounded"><GraduationCap className="w-3 h-3 inline mr-1" />{passerelle.training_needed}</p>
        )}
      </CardContent>
    </Card>
  );
};

// ============== ARCHÉOLOGIE TAB ==============

const VERTU_COLORS = {
  sagesse: { bg: "bg-blue-50", text: "text-blue-700", border: "border-blue-300", accent: "#3b82f6" },
  courage: { bg: "bg-red-50", text: "text-red-700", border: "border-red-300", accent: "#ef4444" },
  humanite: { bg: "bg-rose-50", text: "text-rose-700", border: "border-rose-300", accent: "#f43f5e" },
  justice: { bg: "bg-amber-50", text: "text-amber-700", border: "border-amber-300", accent: "#f59e0b" },
  temperance: { bg: "bg-teal-50", text: "text-teal-700", border: "border-teal-300", accent: "#14b8a6" },
  transcendance: { bg: "bg-violet-50", text: "text-violet-700", border: "border-violet-300", accent: "#8b5cf6" },
};

const ArcheologieTab = ({ archeologie, loading, onLoad, savoirFaire, savoirEtre, nonClassees }) => {
  const [referentiel, setReferentiel] = useState(null);
  const [loadingRef, setLoadingRef] = useState(false);

  const loadReferentiel = async () => {
    setLoadingRef(true);
    try {
      const res = await axios.get(`${API}/referentiel/archeologie`);
      setReferentiel(res.data);
    } catch (e) { toast.error("Erreur chargement référentiel"); }
    setLoadingRef(false);
  };

  useEffect(() => { loadReferentiel(); }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-[#1e3a5f] flex items-center gap-2">
            <Layers className="w-5 h-5" />Archéologie des Compétences
          </h3>
          <p className="text-sm text-slate-500">La chaîne hiérarchique : Métier → Savoir-faire → Savoir-être → Qualités → Valeurs → Vertus</p>
        </div>
        <Button onClick={onLoad} disabled={loading} data-testid="load-archeologie-btn">
          {loading ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Layers className="w-4 h-4 mr-2" />}
          {loading ? "Chargement..." : "Analyser mon profil"}
        </Button>
      </div>

      {/* Hierarchy Explanation */}
      <Card className="bg-gradient-to-r from-[#1e3a5f] to-[#2d5a8e] text-white border-0">
        <CardContent className="p-5">
          <h4 className="font-semibold mb-3">Le modèle RE'ACTIF PRO</h4>
          <div className="flex flex-wrap items-center gap-2 text-sm">
            <span className="bg-sky-400/30 px-3 py-1 rounded-full">Savoir-faire</span>
            <ChevronRight className="w-4 h-4 text-white/50" />
            <span className="bg-rose-400/30 px-3 py-1 rounded-full">Savoir-être</span>
            <ChevronRight className="w-4 h-4 text-white/50" />
            <span className="bg-amber-400/30 px-3 py-1 rounded-full">Qualités humaines</span>
            <ChevronRight className="w-4 h-4 text-white/50" />
            <span className="bg-emerald-400/30 px-3 py-1 rounded-full">Valeurs</span>
            <ChevronRight className="w-4 h-4 text-white/50" />
            <span className="bg-violet-400/30 px-3 py-1 rounded-full">Vertus</span>
          </div>
          <p className="text-blue-200 text-xs mt-3">L'orientation professionnelle part des compétences techniques vers les savoir-être, pour révéler les qualités humaines, les valeurs et les vertus qui vous animent.</p>
        </CardContent>
      </Card>

      {/* Summary stats */}
      {archeologie && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <Card><CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-sky-600">{archeologie.summary.savoir_faire}</div>
            <p className="text-xs text-slate-500">Savoir-faire</p>
          </CardContent></Card>
          <Card><CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-rose-500">{archeologie.summary.savoir_etre}</div>
            <p className="text-xs text-slate-500">Savoir-être</p>
          </CardContent></Card>
          <Card><CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-emerald-600">{archeologie.summary.valeurs_covered?.length || 0}</div>
            <p className="text-xs text-slate-500">Valeurs couvertes</p>
          </CardContent></Card>
          <Card><CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-violet-600">{archeologie.summary.vertus_covered?.length || 0}</div>
            <p className="text-xs text-slate-500">Vertus activées</p>
          </CardContent></Card>
        </div>
      )}

      {/* Chains: savoir-être traced to vertus */}
      {archeologie?.chains?.length > 0 && (
        <div>
          <h4 className="font-medium text-slate-700 mb-3">Chaînes identifiées (Savoir-être → Vertus)</h4>
          <div className="space-y-3">
            {archeologie.chains.map((chain, i) => (
              <Card key={i} className="border-l-4 border-l-rose-400" data-testid="archeologie-chain">
                <CardContent className="p-4">
                  <h5 className="font-semibold text-slate-900 text-sm mb-2">{chain.competence}</h5>
                  <div className="flex flex-wrap items-center gap-1.5">
                    <Badge className="bg-rose-100 text-rose-700 text-xs">{chain.competence}</Badge>
                    {chain.qualites?.length > 0 && (
                      <>
                        <ChevronRight className="w-3 h-3 text-slate-300" />
                        {chain.qualites.map((q, j) => <Badge key={j} variant="outline" className="text-xs text-amber-700 bg-amber-50">{q}</Badge>)}
                      </>
                    )}
                    {chain.valeurs?.length > 0 && (
                      <>
                        <ChevronRight className="w-3 h-3 text-slate-300" />
                        {chain.valeurs.map((v, j) => <Badge key={j} variant="outline" className="text-xs text-emerald-700 bg-emerald-50">{v}</Badge>)}
                      </>
                    )}
                    {chain.vertus?.length > 0 && (
                      <>
                        <ChevronRight className="w-3 h-3 text-slate-300" />
                        {chain.vertus.map((v, j) => <Badge key={j} variant="outline" className="text-xs text-violet-700 bg-violet-50">{v}</Badge>)}
                      </>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Non-classified competences warning */}
      {archeologie && archeologie.summary.non_classees > 0 && (
        <Card className="border-amber-200 bg-amber-50/50">
          <CardContent className="p-4">
            <p className="text-sm text-amber-800 font-medium">{archeologie.summary.non_classees} compétence(s) non classée(s)</p>
            <p className="text-xs text-amber-600">Précisez leur nature (savoir-faire ou savoir-être) dans l'onglet Compétences pour compléter l'archéologie.</p>
          </CardContent>
        </Card>
      )}

      {/* Referentiel: Les 6 Vertus */}
      {referentiel && (
        <div>
          <h4 className="font-medium text-slate-700 mb-3">Les 6 Vertus et leurs chaînes</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {referentiel.vertus.map(vertu => {
              const vc = VERTU_COLORS[vertu.id] || VERTU_COLORS.sagesse;
              const isCovered = archeologie?.summary?.vertus_covered?.includes(vertu.id);
              return (
                <Card key={vertu.id} className={`${vc.bg} border ${vc.border} ${isCovered ? "ring-2 ring-offset-1" : "opacity-60"}`} style={isCovered ? { ringColor: vc.accent } : {}} data-testid={`vertu-card-${vertu.id}`}>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h5 className={`font-semibold text-sm ${vc.text}`}>{vertu.name}</h5>
                      {isCovered && <Badge className="bg-emerald-500 text-white text-xs">Activée</Badge>}
                    </div>
                    <p className="text-xs text-slate-600 mb-2">{vertu.description}</p>
                    <div className="space-y-1.5">
                      <div>
                        <p className="text-xs font-medium text-slate-500">Qualités associées :</p>
                        <div className="flex flex-wrap gap-1 mt-0.5">
                          {vertu.qualites?.slice(0, 4).map((q, i) => <Badge key={i} variant="outline" className="text-xs">{q}</Badge>)}
                        </div>
                      </div>
                      <div>
                        <p className="text-xs font-medium text-slate-500">Savoir-être :</p>
                        <div className="flex flex-wrap gap-1 mt-0.5">
                          {vertu.savoirs_etre?.slice(0, 3).map((s, i) => <Badge key={i} className="text-xs bg-rose-50 text-rose-600">{s}</Badge>)}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      )}

      {!archeologie && !loading && (
        <EmptyState text="Cliquez sur 'Analyser mon profil' pour visualiser l'archéologie de vos compétences" />
      )}
    </div>
  );
};

export default PassportView;
