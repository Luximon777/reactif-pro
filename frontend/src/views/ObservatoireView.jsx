import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { 
  TrendingUp,
  TrendingDown,
  Zap,
  Target,
  BarChart3,
  PieChart,
  ArrowUpRight,
  ArrowDownRight,
  Lightbulb,
  Users,
  Building2,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Plus,
  Send,
  ThumbsUp,
  Eye,
  Sparkles,
  Compass,
  Globe,
  Brain,
  Layers,
  Radio,
  Shield,
  ExternalLink,
  MessageCircle,
  Link2,
  Loader2
} from "lucide-react";
import { toast } from "sonner";

const CONTRIBUTION_TYPES = {
  nouvelle_competence: { label: "Nouvelle compétence", icon: Zap, color: "blue" },
  evolution_competence: { label: "Évolution d'une compétence", icon: TrendingUp, color: "emerald" },
  nouvel_outil: { label: "Nouvel outil", icon: Layers, color: "violet" },
  evolution_metier: { label: "Évolution d'un métier", icon: Building2, color: "amber" },
  tendance_secteur: { label: "Tendance sectorielle", icon: Globe, color: "cyan" },
  competence_obsolete: { label: "Compétence en déclin", icon: TrendingDown, color: "rose" }
};

const STATUS_CONFIG = {
  emergente: { label: "Émergente", color: "bg-blue-100 text-blue-700", icon: Sparkles },
  en_croissance: { label: "En croissance", color: "bg-emerald-100 text-emerald-700", icon: TrendingUp },
  etablie: { label: "Établie", color: "bg-slate-100 text-slate-700", icon: CheckCircle2 },
  en_declin: { label: "En déclin", color: "bg-amber-100 text-amber-700", icon: TrendingDown }
};

const ObservatoireView = ({ token, embedded }) => {
  const [dashboard, setDashboard] = useState(null);
  const [contributions, setContributions] = useState([]);
  const [ubuntooDashboard, setUbuntooDashboard] = useState(null);
  const [cvDetectedData, setCvDetectedData] = useState(null);
  const [personalizedData, setPersonalizedData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingPersonalized, setLoadingPersonalized] = useState(false);
  const [activeTab, setActiveTab] = useState("overview");
  const [selectedSector, setSelectedSector] = useState(null);
  const [contributeDialogOpen, setContributeDialogOpen] = useState(false);

  const [newContribution, setNewContribution] = useState({
    contribution_type: "nouvelle_competence",
    skill_name: "",
    skill_description: "",
    related_job: "",
    related_sector: "",
    related_tools: "",
    context: ""
  });

  useEffect(() => {
    loadData();
  }, [token]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [dashboardRes, contributionsRes, ubuntooRes] = await Promise.all([
        axios.get(`${API}/observatoire/dashboard`),
        axios.get(`${API}/observatoire/contributions?token=${token}`),
        axios.get(`${API}/ubuntoo/dashboard`),
      ]);
      setDashboard(dashboardRes.data);
      setContributions(contributionsRes.data);
      setUbuntooDashboard(ubuntooRes.data);

      // Load cv-detected data non-blocking
      axios.get(`${API}/emerging/observatory?token=${token}`, { timeout: 10000 })
        .then(r => setCvDetectedData(r.data)).catch(() => {});
    } catch (error) {
      console.error("Error loading observatoire:", error);
    }
    setLoading(false);
  };

  const loadPersonalized = async () => {
    setLoadingPersonalized(true);
    try {
      const res = await axios.get(`${API}/observatoire/personalized?token=${token}`, { timeout: 60000 });
      setPersonalizedData(res.data);
    } catch (e) {
      console.error("Error loading personalized:", e);
    }
    setLoadingPersonalized(false);
  };

  const submitContribution = async () => {
    if (!newContribution.skill_name.trim()) {
      toast.error("Veuillez saisir le nom de la compétence");
      return;
    }

    try {
      const data = {
        ...newContribution,
        related_tools: newContribution.related_tools.split(",").map(t => t.trim()).filter(Boolean)
      };
      
      const response = await axios.post(`${API}/observatoire/contributions?token=${token}`, data);
      
      toast.success("Contribution enregistrée !");
      if (response.data.ai_analysis) {
        toast.info(`Analyse IA : ${response.data.ai_analysis.rationale}`);
      }
      
      setContributeDialogOpen(false);
      setNewContribution({
        contribution_type: "nouvelle_competence",
        skill_name: "",
        skill_description: "",
        related_job: "",
        related_sector: "",
        related_tools: "",
        context: ""
      });
      loadData();
    } catch (error) {
      toast.error("Erreur lors de l'envoi de la contribution");
    }
  };

  const upvoteContribution = async (contributionId) => {
    try {
      await axios.post(`${API}/observatoire/contributions/${contributionId}/upvote?token=${token}`);
      toast.success("Vote enregistré !");
    } catch (error) {
      toast.error("Erreur lors du vote");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#1e3a5f]"></div>
      </div>
    );
  }

  const { emerging_skills = [], sector_trends = [], indicators = {} } = dashboard || {};

  return (
    <div className="space-y-6 animate-fade-in" data-testid="observatoire-view">
      {/* Header */}
      {!embedded && (
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 flex items-center gap-3" style={{ fontFamily: 'Outfit, sans-serif' }}>
            <Brain className="w-8 h-8 text-[#1e3a5f]" />
            Observatoire Prédictif des Compétences
          </h1>
          <p className="text-slate-600 mt-1">
            Intelligence collective sur l'évolution du travail et des compétences
          </p>
          <div className="mt-2 p-2.5 bg-amber-50 rounded-lg border border-amber-200 flex items-start gap-2" data-testid="observatoire-sample-data-banner">
            <AlertTriangle className="w-4 h-4 text-amber-500 mt-0.5 shrink-0" />
            <p className="text-xs text-amber-700">Les données affichées sont des <strong>exemples initiaux</strong> pour illustrer le fonctionnement de l'observatoire. Elles seront enrichies et remplacées par les contributions réelles des utilisateurs de la plateforme.</p>
          </div>
        </div>
        <Dialog open={contributeDialogOpen} onOpenChange={setContributeDialogOpen}>
          <DialogTrigger asChild>
            <Button className="bg-[#1e3a5f] hover:bg-[#152a45]" data-testid="contribute-btn">
              <Plus className="w-4 h-4 mr-2" />
              Contribuer
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Lightbulb className="w-5 h-5 text-amber-500" />
                Signaler une évolution
              </DialogTitle>
              <DialogDescription>
                Partagez vos observations sur les transformations du travail. Votre contribution sera analysée par notre IA puis validée par des experts.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 mt-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Type de contribution</label>
                <Select 
                  value={newContribution.contribution_type} 
                  onValueChange={(v) => setNewContribution({ ...newContribution, contribution_type: v })}
                >
                  <SelectTrigger data-testid="contribution-type-select">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(CONTRIBUTION_TYPES).map(([key, config]) => (
                      <SelectItem key={key} value={key}>
                        <span className="flex items-center gap-2">
                          <config.icon className="w-4 h-4" />
                          {config.label}
                        </span>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Nom de la compétence / évolution *</label>
                <Input
                  placeholder="Ex: Prompt Engineering, No-Code, IA Générative..."
                  value={newContribution.skill_name}
                  onChange={(e) => setNewContribution({ ...newContribution, skill_name: e.target.value })}
                  data-testid="skill-name-input"
                />
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Description</label>
                <Textarea
                  placeholder="Décrivez cette compétence ou cette évolution..."
                  rows={3}
                  value={newContribution.skill_description}
                  onChange={(e) => setNewContribution({ ...newContribution, skill_description: e.target.value })}
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700">Métier associé</label>
                  <Input
                    placeholder="Ex: Développeur, RH, Commercial..."
                    value={newContribution.related_job}
                    onChange={(e) => setNewContribution({ ...newContribution, related_job: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700">Secteur d'activité</label>
                  <Select 
                    value={newContribution.related_sector} 
                    onValueChange={(v) => setNewContribution({ ...newContribution, related_sector: v })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Sélectionner..." />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Informatique">Informatique</SelectItem>
                      <SelectItem value="Administration">Administration</SelectItem>
                      <SelectItem value="Commerce">Commerce</SelectItem>
                      <SelectItem value="Santé">Santé</SelectItem>
                      <SelectItem value="Industrie">Industrie</SelectItem>
                      <SelectItem value="Finance">Finance</SelectItem>
                      <SelectItem value="Formation">Formation</SelectItem>
                      <SelectItem value="Communication">Communication</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Outils associés</label>
                <Input
                  placeholder="Séparez par des virgules: ChatGPT, Notion, Figma..."
                  value={newContribution.related_tools}
                  onChange={(e) => setNewContribution({ ...newContribution, related_tools: e.target.value })}
                />
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Contexte d'observation</label>
                <Textarea
                  placeholder="Dans quel contexte avez-vous observé cette évolution ?"
                  rows={2}
                  value={newContribution.context}
                  onChange={(e) => setNewContribution({ ...newContribution, context: e.target.value })}
                />
              </div>
              
              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <p className="text-sm text-blue-700">
                  <Brain className="w-4 h-4 inline mr-1" />
                  Votre contribution sera analysée par notre IA puis validée par un comité d'experts avant d'être intégrée à l'observatoire.
                </p>
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <Button variant="outline" onClick={() => setContributeDialogOpen(false)}>
                Annuler
              </Button>
              <Button onClick={submitContribution} className="bg-[#1e3a5f] hover:bg-[#152a45]" data-testid="submit-contribution-btn">
                <Send className="w-4 h-4 mr-2" />
                Envoyer ma contribution
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>
      )}

      {/* Key Indicators */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4" data-testid="observatoire-indicators">
        <Card className="card-metric">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-blue-600 text-white flex items-center justify-center">
                <Sparkles className="w-5 h-5" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{indicators.total_emerging_skills || 0}</p>
                <p className="text-xs text-slate-500">Compétences émergentes</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="card-metric">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-600 text-white flex items-center justify-center">
                <TrendingUp className="w-5 h-5" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{indicators.total_growing_skills || 0}</p>
                <p className="text-xs text-slate-500">En croissance</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="card-metric">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-amber-600 text-white flex items-center justify-center">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{indicators.skill_gap_alerts || 0}</p>
                <p className="text-xs text-slate-500">Alertes compétences</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="card-metric">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-violet-600 text-white flex items-center justify-center">
                <Building2 className="w-5 h-5" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{indicators.sectors_in_transformation || 0}</p>
                <p className="text-xs text-slate-500">Secteurs en mutation</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="card-metric">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-cyan-600 text-white flex items-center justify-center">
                <Users className="w-5 h-5" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{indicators.total_contributions || 0}</p>
                <p className="text-xs text-slate-500">Contributions</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="card-metric">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-rose-600 text-white flex items-center justify-center">
                <CheckCircle2 className="w-5 h-5" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{indicators.validated_contributions || 0}</p>
                <p className="text-xs text-slate-500">Validées</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid grid-cols-3 md:grid-cols-7 gap-1 h-auto p-1 bg-slate-100">
          <TabsTrigger value="overview" className="text-xs sm:text-sm py-2" data-testid="tab-overview">
            <BarChart3 className="w-4 h-4 mr-1 hidden sm:inline" />
            Vue d'ensemble
          </TabsTrigger>
          <TabsTrigger value="emerging" className="text-xs sm:text-sm py-2" data-testid="tab-emerging">
            <Sparkles className="w-4 h-4 mr-1 hidden sm:inline" />
            Compétences
          </TabsTrigger>
          <TabsTrigger value="sectors" className="text-xs sm:text-sm py-2" data-testid="tab-sectors">
            <Building2 className="w-4 h-4 mr-1 hidden sm:inline" />
            Secteurs
          </TabsTrigger>
          <TabsTrigger value="ubuntoo" className="text-xs sm:text-sm py-2" data-testid="tab-ubuntoo">
            <Radio className="w-4 h-4 mr-1 hidden sm:inline" />
            Signaux Ubuntoo
          </TabsTrigger>
          <TabsTrigger value="predictions" className="text-xs sm:text-sm py-2" data-testid="tab-predictions">
            <Compass className="w-4 h-4 mr-1 hidden sm:inline" />
            Prédictions
          </TabsTrigger>
          <TabsTrigger value="contributions" className="text-xs sm:text-sm py-2" data-testid="tab-my-contributions">
            <Lightbulb className="w-4 h-4 mr-1 hidden sm:inline" />
            Contributions
          </TabsTrigger>
          <TabsTrigger value="cv_detected" className="text-xs sm:text-sm py-2" data-testid="tab-cv-detected">
            <Target className="w-4 h-4 mr-1 hidden sm:inline" />
            Détectées CV
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          {/* Personalized Section */}
          {personalizedData ? (
            <PersonalizedObservatoireCard data={personalizedData} />
          ) : (
            <Card className="card-base border-dashed border-2">
              <CardContent className="p-6 flex flex-col items-center gap-3">
                <Sparkles className="w-8 h-8 text-indigo-400" />
                <p className="text-sm text-slate-500 text-center">Obtenez des prédictions personnalisées basées sur votre profil</p>
                <Button
                  onClick={loadPersonalized}
                  disabled={loadingPersonalized}
                  className="bg-gradient-to-r from-indigo-500 to-purple-500 text-white"
                  data-testid="load-personalized-btn"
                >
                  {loadingPersonalized ? <><Loader2 className="w-4 h-4 animate-spin mr-2" />Analyse en cours...</> : "Charger les prédictions IA"}
                </Button>
              </CardContent>
            </Card>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Top Emerging Skills - Personalized when available */}
            <Card className="card-base">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-blue-600" />
                  {personalizedData?.matches?.length > 0 ? "Vos Compétences Émergentes" : "Top Compétences Émergentes"}
                </CardTitle>
                <CardDescription>
                  {personalizedData?.matches?.length > 0
                    ? "Compétences de votre profil identifiées comme émergentes sur le marché"
                    : "Les compétences qui transforment le marché du travail"}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {personalizedData?.matches?.length > 0
                    ? personalizedData.matches.slice(0, 6).map((m, idx) => (
                        <div key={idx} className="flex items-center gap-3 p-3 rounded-lg border border-emerald-100 bg-emerald-50/50 hover:bg-emerald-50 transition-colors">
                          <div className="w-8 h-8 rounded-full bg-emerald-100 flex items-center justify-center text-sm font-bold text-emerald-700">{idx + 1}</div>
                          <div className="flex-1 min-w-0">
                            <p className="font-medium text-sm text-slate-900 truncate">{m.observatory_skill}</p>
                            <div className="flex items-center gap-2 mt-0.5">
                              <Badge className={`text-[10px] ${m.status === "emergente" ? "bg-blue-100 text-blue-700" : m.status === "en_croissance" ? "bg-emerald-100 text-emerald-700" : "bg-slate-100 text-slate-600"}`}>
                                {m.status === "emergente" ? "Émergente" : m.status === "en_croissance" ? "En croissance" : "Établie"}
                              </Badge>
                              <span className="text-[10px] text-emerald-600">+{Math.round((m.growth_rate || 0) * 100)}%</span>
                            </div>
                          </div>
                          <div className="text-right">
                            <span className="text-xl font-bold text-emerald-700">{Math.round((m.emergence_score || 0) * 100)}</span>
                            <p className="text-[10px] text-slate-400">score</p>
                          </div>
                        </div>
                      ))
                    : emerging_skills.slice(0, 5).map((skill, idx) => (
                        <EmergingSkillCard key={idx} skill={skill} rank={idx + 1} />
                      ))
                  }
                </div>
              </CardContent>
            </Card>

            {/* Sectors - Personalized when available */}
            <Card className="card-base">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Building2 className="w-5 h-5 text-violet-600" />
                  {personalizedData?.sector_relevance?.length > 0 ? "Secteurs de votre Profil" : "Secteurs en Transformation"}
                </CardTitle>
                <CardDescription>
                  {personalizedData?.sector_relevance?.length > 0
                    ? "Dynamiques des secteurs pertinents pour votre profil"
                    : "Dynamiques sectorielles et besoins en compétences"}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {personalizedData?.sector_relevance?.length > 0
                    ? personalizedData.sector_relevance.slice(0, 5).map((s, idx) => (
                        <div key={idx} className="p-3 rounded-lg border border-slate-200 hover:bg-slate-50/50 transition-colors">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-semibold text-sm text-slate-900">{s.sector}</h4>
                            <div className="flex items-center gap-2">
                              <Badge className={`text-[10px] ${s.hiring_trend === "croissance" ? "bg-emerald-100 text-emerald-700" : s.hiring_trend === "recul" ? "bg-rose-100 text-rose-700" : "bg-slate-100 text-slate-600"}`}>
                                {s.hiring_trend === "croissance" ? "En croissance" : s.hiring_trend === "recul" ? "En recul" : "Stable"}
                              </Badge>
                              {s.skill_gap_alert && <Badge className="bg-amber-100 text-amber-700 text-[10px]"><AlertTriangle className="w-3 h-3 mr-0.5" />Alerte</Badge>}
                            </div>
                          </div>
                          <div className="mb-2">
                            <div className="flex items-center justify-between text-[10px] text-slate-500 mb-1">
                              <span>Indice de transformation</span>
                              <span>{Math.round((s.transformation_index || 0) * 100)}%</span>
                            </div>
                            <Progress value={(s.transformation_index || 0) * 100} className="h-1.5" />
                          </div>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {(s.your_emerging_skills || []).slice(0, 3).map((sk, j) => (
                              <Badge key={`e-${j}`} className="text-[10px] bg-emerald-50 text-emerald-600 border border-emerald-200">{sk}</Badge>
                            ))}
                            {(s.your_declining_skills || []).slice(0, 2).map((sk, j) => (
                              <Badge key={`d-${j}`} className="text-[10px] bg-rose-50 text-rose-600 border border-rose-200">{sk}</Badge>
                            ))}
                          </div>
                        </div>
                      ))
                    : sector_trends.map((trend, idx) => (
                        <SectorTrendCard key={idx} trend={trend} />
                      ))
                  }
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Intelligence Collective Banner */}
          <Card className="bg-gradient-to-r from-[#1e3a5f] to-[#2d4a6f] border-0">
            <CardContent className="p-6">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 rounded-xl bg-white/20 flex items-center justify-center">
                    <Brain className="w-7 h-7 text-white" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-white">Intelligence Collective du Travail</h3>
                    <p className="text-blue-100 text-sm">
                      Les transformations du travail sont perçues d'abord par les professionnels eux-mêmes.
                      Contribuez à enrichir l'observatoire.
                    </p>
                  </div>
                </div>
                <Button 
                  className="bg-white text-[#1e3a5f] hover:bg-blue-50 font-semibold"
                  onClick={() => setContributeDialogOpen(true)}
                >
                  <Lightbulb className="w-4 h-4 mr-2" />
                  Signaler une évolution
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Emerging Skills Tab */}
        <TabsContent value="emerging" className="space-y-4">
          <Card className="card-base">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-[#1e3a5f]" />
                {personalizedData?.matches?.length > 0 ? "Compétences Émergentes de votre Profil" : "Cartographie des Compétences Émergentes"}
              </CardTitle>
              <CardDescription>
                {personalizedData?.matches?.length > 0
                  ? "Vos compétences identifiées comme émergentes ou en croissance sur le marché"
                  : "Compétences nouvellement identifiées par l'intelligence collective"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {personalizedData?.matches?.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {personalizedData.matches.map((m, idx) => (
                    <div key={idx} className="p-4 rounded-xl border border-emerald-200 bg-emerald-50/30 hover:shadow-md transition-all">
                      <div className="flex items-center justify-between mb-2">
                        <Badge className={`text-[10px] ${m.status === "emergente" ? "bg-blue-100 text-blue-700" : m.status === "en_croissance" ? "bg-emerald-100 text-emerald-700" : "bg-slate-100 text-slate-600"}`}>
                          {m.status === "emergente" ? "Émergente" : m.status === "en_croissance" ? "En croissance" : "Établie"}
                        </Badge>
                        <span className="text-lg font-bold text-emerald-700">{Math.round((m.emergence_score || 0) * 100)}</span>
                      </div>
                      <h4 className="font-semibold text-sm text-slate-900 mb-1">{m.observatory_skill}</h4>
                      <p className="text-[10px] text-slate-500 mb-2">Croissance : +{Math.round((m.growth_rate || 0) * 100)}%</p>
                      {m.related_sectors?.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {m.related_sectors.slice(0, 3).map((s, j) => (
                            <Badge key={j} variant="outline" className="text-[10px]">{s}</Badge>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {emerging_skills.map((skill, idx) => (
                    <EmergingSkillDetailCard key={idx} skill={skill} />
                  ))}
                </div>
              )}

              {/* Skill Gaps section */}
              {personalizedData?.skill_gaps?.length > 0 && (
                <div className="mt-6 pt-4 border-t border-slate-200">
                  <h3 className="font-semibold text-sm text-amber-700 flex items-center gap-2 mb-3">
                    <AlertTriangle className="w-4 h-4" />
                    Compétences à acquérir pour votre profil
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {personalizedData.skill_gaps.filter(g => g.priority === "haute").slice(0, 8).map((g, idx) => (
                      <div key={idx} className="flex items-center justify-between p-3 rounded-lg bg-amber-50 border border-amber-100">
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-slate-900 truncate">{g.skill_name}</p>
                          <div className="flex items-center gap-2 mt-0.5">
                            <Badge className="text-[10px] bg-amber-100 text-amber-700">Priorité haute</Badge>
                            <span className="text-[10px] text-amber-600">+{Math.round((g.growth_rate || 0) * 100)}%</span>
                          </div>
                        </div>
                        <span className="text-lg font-bold text-amber-700 ml-2">{Math.round((g.emergence_score || 0) * 100)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Sectors Tab */}
        <TabsContent value="sectors" className="space-y-4">
          {personalizedData?.sector_relevance?.length > 0 ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {personalizedData.sector_relevance.map((s, idx) => (
                <Card key={idx} className="card-base">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-base">{s.sector}</CardTitle>
                      <div className="flex gap-2">
                        <Badge className={`text-xs ${s.hiring_trend === "croissance" ? "bg-emerald-100 text-emerald-700" : s.hiring_trend === "recul" ? "bg-rose-100 text-rose-700" : "bg-slate-100 text-slate-600"}`}>
                          {s.hiring_trend === "croissance" ? "En croissance" : s.hiring_trend === "recul" ? "En recul" : "Stable"}
                        </Badge>
                        {s.skill_gap_alert && <Badge className="bg-amber-100 text-amber-700 text-xs"><AlertTriangle className="w-3 h-3 mr-0.5" />Alerte</Badge>}
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="mb-3">
                      <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
                        <span>Indice de transformation</span>
                        <span className="font-semibold">{Math.round((s.transformation_index || 0) * 100)}%</span>
                      </div>
                      <Progress value={(s.transformation_index || 0) * 100} className="h-2" />
                    </div>
                    {(s.your_emerging_skills || []).length > 0 && (
                      <div className="mb-2">
                        <p className="text-[10px] font-medium text-emerald-700 mb-1">Vos compétences émergentes dans ce secteur :</p>
                        <div className="flex flex-wrap gap-1">
                          {s.your_emerging_skills.map((sk, j) => (
                            <Badge key={j} className="text-[10px] bg-emerald-50 text-emerald-600 border border-emerald-200">{sk}</Badge>
                          ))}
                        </div>
                      </div>
                    )}
                    {(s.your_stable_skills || []).length > 0 && (
                      <div className="mb-2">
                        <p className="text-[10px] font-medium text-slate-500 mb-1">Compétences stables :</p>
                        <div className="flex flex-wrap gap-1">
                          {s.your_stable_skills.map((sk, j) => (
                            <Badge key={j} variant="outline" className="text-[10px]">{sk}</Badge>
                          ))}
                        </div>
                      </div>
                    )}
                    {(s.your_declining_skills || []).length > 0 && (
                      <div>
                        <p className="text-[10px] font-medium text-rose-600 mb-1">Compétences en déclin :</p>
                        <div className="flex flex-wrap gap-1">
                          {s.your_declining_skills.map((sk, j) => (
                            <Badge key={j} className="text-[10px] bg-rose-50 text-rose-600 border border-rose-200">{sk}</Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {sector_trends.map((trend, idx) => (
                <SectorDetailCard key={idx} trend={trend} />
              ))}
            </div>
          )}
        </TabsContent>

        {/* Ubuntoo Intelligence Tab */}
        <TabsContent value="ubuntoo" className="space-y-6" data-testid="ubuntoo-tab-content">
          <UbuntooIntelligenceTab data={ubuntooDashboard} />
        </TabsContent>

        {/* Predictions Tab - Personalized */}
        <TabsContent value="predictions" className="space-y-4">
          {personalizedData?.sector_relevance?.length > 0 ? (
            <>
              {/* Personalized predictions based on user profile */}
              <Card className="card-base border-indigo-200 bg-indigo-50/30">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-indigo-600" />
                    Prédictions personnalisées pour votre profil
                  </CardTitle>
                  <CardDescription>
                    Basées sur vos {personalizedData.user_skills_count} compétences analysées et {personalizedData.sector_relevance.length} secteurs identifiés
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* User's relevant sectors with their emerging skills */}
                  {personalizedData.sector_relevance.map((sr, idx) => (
                    <div key={idx} className="p-4 rounded-lg border border-indigo-100 bg-white space-y-3" data-testid={`personalized-sector-${idx}`}>
                      <div className="flex items-center justify-between">
                        <h4 className="font-semibold text-slate-900 text-sm">{sr.sector}</h4>
                        <div className="flex items-center gap-2">
                          <Badge className={`text-[10px] ${sr.hiring_trend === "croissance" ? "bg-emerald-100 text-emerald-700" : sr.hiring_trend === "stable" ? "bg-slate-100 text-slate-600" : "bg-amber-100 text-amber-700"}`}>
                            {sr.hiring_trend === "croissance" ? "Embauches en hausse" : sr.hiring_trend === "stable" ? "Stable" : "Recul"}
                          </Badge>
                          {sr.skill_gap_alert && (
                            <Badge className="text-[10px] bg-rose-100 text-rose-700">Alerte compétences</Badge>
                          )}
                        </div>
                      </div>
                      {(sr.your_emerging_skills || []).length > 0 && (
                        <div>
                          <p className="text-xs text-emerald-600 font-medium mb-1">Vos compétences émergentes dans ce secteur :</p>
                          <div className="flex flex-wrap gap-1">
                            {sr.your_emerging_skills.map((sk, j) => (
                              <Badge key={j} className="text-[10px] bg-emerald-50 text-emerald-700 border border-emerald-200">{sk}</Badge>
                            ))}
                          </div>
                        </div>
                      )}
                      {(sr.your_declining_skills || []).length > 0 && (
                        <div>
                          <p className="text-xs text-rose-600 font-medium mb-1">Compétences en déclin :</p>
                          <div className="flex flex-wrap gap-1">
                            {sr.your_declining_skills.map((sk, j) => (
                              <Badge key={j} className="text-[10px] bg-rose-50 text-rose-600 border border-rose-200">{sk}</Badge>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}

                  {/* Skill gaps with high priority */}
                  {personalizedData.skill_gaps?.filter(g => g.priority === "haute").length > 0 && (
                    <div className="mt-4 p-4 rounded-lg border border-amber-200 bg-amber-50/50">
                      <h4 className="text-sm font-semibold text-amber-800 mb-2 flex items-center gap-2">
                        <AlertTriangle className="w-4 h-4" />
                        Compétences prioritaires à acquérir
                      </h4>
                      <div className="space-y-2">
                        {personalizedData.skill_gaps.filter(g => g.priority === "haute").slice(0, 5).map((gap, idx) => (
                          <div key={idx} className="flex items-center justify-between p-2 bg-white rounded border border-amber-100">
                            <div>
                              <span className="text-sm font-medium text-slate-800">{gap.skill_name}</span>
                              <span className="text-xs text-slate-500 ml-2">{(gap.related_sectors || []).slice(0, 2).join(", ")}</span>
                            </div>
                            <Badge className="bg-amber-100 text-amber-700 text-xs">Priorité haute</Badge>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Global market predictions as reference */}
              <Card className="card-base">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-sm">
                    <Compass className="w-4 h-4 text-slate-500" />
                    Tendances globales du marché (référence)
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {sector_trends.flatMap((trend, ti) => 
                      (trend.predicted_skills_demand || []).map((pred, idx) => (
                        <PredictionCard key={`ref-${ti}-${idx}`} prediction={pred} sector={trend.sector_name} />
                      ))
                    )}
                  </div>
                </CardContent>
              </Card>
            </>
          ) : (
            <Card className="card-base">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Compass className="w-5 h-5 text-[#1e3a5f]" />
                  Prévisions de Demande en Compétences
                </CardTitle>
                <CardDescription>
                  Anticipez les besoins futurs du marché du travail
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Prompt to load personalized predictions */}
                <Card className="border-dashed border-2 border-indigo-200 bg-indigo-50/30">
                  <CardContent className="p-4 flex flex-col items-center gap-3">
                    <Sparkles className="w-8 h-8 text-indigo-400" />
                    <p className="text-sm text-slate-600 text-center">Chargez vos prédictions personnalisées pour voir les tendances adaptées à votre profil</p>
                    <Button
                      onClick={loadPersonalized}
                      disabled={loadingPersonalized}
                      className="bg-gradient-to-r from-indigo-500 to-purple-500 text-white"
                      data-testid="load-predictions-personalized-btn"
                    >
                      {loadingPersonalized ? <><Loader2 className="w-4 h-4 animate-spin mr-2" />Analyse en cours...</> : "Personnaliser mes prédictions"}
                    </Button>
                  </CardContent>
                </Card>

                {/* Global predictions as fallback */}
                <div className="space-y-3">
                  {sector_trends.flatMap((trend, ti) => 
                    (trend.predicted_skills_demand || []).map((pred, idx) => (
                      <PredictionCard key={`global-${ti}-${idx}`} prediction={pred} sector={trend.sector_name} />
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* My Contributions Tab */}
        <TabsContent value="contributions" className="space-y-4">
          <Card className="card-base">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <Lightbulb className="w-5 h-5 text-amber-500" />
                  Mes Contributions
                </CardTitle>
                <CardDescription>
                  Suivez le statut de vos signalements
                </CardDescription>
              </div>
              <Button onClick={() => setContributeDialogOpen(true)} className="bg-[#1e3a5f]">
                <Plus className="w-4 h-4 mr-2" />
                Nouvelle contribution
              </Button>
            </CardHeader>
            <CardContent>
              {contributions.length > 0 ? (
                <div className="space-y-4">
                  {contributions.map((contrib, idx) => (
                    <ContributionCard key={idx} contribution={contrib} />
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <Lightbulb className="w-16 h-16 mx-auto text-slate-300 mb-4" />
                  <h3 className="text-lg font-semibold text-slate-600 mb-2">Aucune contribution</h3>
                  <p className="text-slate-500 mb-4">
                    Partagez vos observations sur les évolutions du travail
                  </p>
                  <Button onClick={() => setContributeDialogOpen(true)} className="bg-[#1e3a5f]">
                    <Plus className="w-4 h-4 mr-2" />
                    Faire ma première contribution
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* CV-Detected Emerging Competences Tab */}
        <TabsContent value="cv_detected" className="space-y-4">
          <CvDetectedTab data={cvDetectedData} token={token} onRefresh={async () => {
            setCvDetectedData("loading");
            try {
              const res = await axios.get(`${API}/emerging/observatory?token=${token}`, { timeout: 45000 });
              setCvDetectedData(res.data);
            } catch { setCvDetectedData(null); }
          }} />
        </TabsContent>
      </Tabs>
    </div>
  );
};

// Sub-components

const PersonalizedObservatoireCard = ({ data }) => {
  if (!data || !data.has_cv) {
    return (
      <Card className="border-dashed border-2 border-slate-200 bg-slate-50/50" data-testid="observatoire-no-cv">
        <CardContent className="p-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-slate-200 flex items-center justify-center">
              <Target className="w-6 h-6 text-slate-400" />
            </div>
            <div>
              <h3 className="font-semibold text-slate-700">Personnalisez votre observatoire</h3>
              <p className="text-sm text-slate-500">
                Analysez votre CV dans l'onglet "Tableau de bord" pour voir les tendances qui vous concernent directement.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  const { matches = [], skill_gaps = [], declining_alerts = [], sector_relevance = [], emerging_from_cv = [], summary = {} } = data;

  return (
    <div className="space-y-4" data-testid="observatoire-personalized">
      {/* Summary Banner */}
      <Card className="bg-gradient-to-r from-[#1e3a5f] to-[#2d5a8f] border-0">
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row md:items-center gap-4">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-xl bg-white/20 flex items-center justify-center">
                <Target className="w-7 h-7 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white">Vos compétences vs. le marché</h3>
                <p className="text-blue-100 text-sm">
                  Analyse croisée de votre CV avec l'observatoire prédictif
                </p>
              </div>
            </div>
            <div className="flex flex-wrap gap-3 md:ml-auto">
              <div className="bg-white/15 rounded-lg px-3 py-2 text-center">
                <p className="text-xl font-bold text-white">{summary.total_skills_analyzed || 0}</p>
                <p className="text-[10px] text-blue-100">Compétences</p>
              </div>
              <div className="bg-white/15 rounded-lg px-3 py-2 text-center">
                <p className="text-xl font-bold text-emerald-300">{summary.skills_in_observatory || 0}</p>
                <p className="text-[10px] text-blue-100">Émergentes</p>
              </div>
              <div className="bg-white/15 rounded-lg px-3 py-2 text-center">
                <p className="text-xl font-bold text-amber-300">{summary.gaps_to_fill || 0}</p>
                <p className="text-[10px] text-blue-100">Lacunes</p>
              </div>
              {summary.skills_declining > 0 && (
                <div className="bg-white/15 rounded-lg px-3 py-2 text-center">
                  <p className="text-xl font-bold text-rose-300">{summary.skills_declining}</p>
                  <p className="text-[10px] text-blue-100">En déclin</p>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Matching skills */}
        {matches.length > 0 && (
          <Card className="card-base border-emerald-200">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-2 text-emerald-700">
                <Sparkles className="w-4 h-4" />
                Vos compétences émergentes
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {matches.slice(0, 5).map((m, i) => (
                  <div key={i} className="flex items-center justify-between p-2 rounded-lg bg-emerald-50 border border-emerald-100">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-slate-900 truncate">{m.observatory_skill}</p>
                      <div className="flex items-center gap-1.5 mt-0.5">
                        <Badge className={`text-[10px] ${m.status === "emergente" ? "bg-blue-100 text-blue-700" : m.status === "en_croissance" ? "bg-emerald-100 text-emerald-700" : "bg-slate-100 text-slate-600"}`}>
                          {m.status === "emergente" ? "Émergente" : m.status === "en_croissance" ? "En croissance" : "Établie"}
                        </Badge>
                        <span className="text-[10px] text-emerald-600">+{Math.round(m.growth_rate * 100)}%</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className="text-lg font-bold text-emerald-700">{Math.round(m.emergence_score * 100)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Skill Gaps */}
        {skill_gaps.length > 0 && (
          <Card className="card-base border-amber-200">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-2 text-amber-700">
                <AlertTriangle className="w-4 h-4" />
                Compétences à acquérir
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {skill_gaps.filter(g => g.priority === "haute").slice(0, 5).map((g, i) => (
                  <div key={i} className="flex items-center justify-between p-2 rounded-lg bg-amber-50 border border-amber-100">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-slate-900 truncate">{g.skill_name}</p>
                      <div className="flex items-center gap-1.5 mt-0.5">
                        <Badge className="text-[10px] bg-amber-100 text-amber-700">Priorité haute</Badge>
                        <span className="text-[10px] text-amber-600">+{Math.round(g.growth_rate * 100)}%</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className="text-lg font-bold text-amber-700">{Math.round(g.emergence_score * 100)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Sector Relevance */}
        {sector_relevance.length > 0 && (
          <Card className="card-base border-blue-200">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-2 text-blue-700">
                <Building2 className="w-4 h-4" />
                Secteurs qui vous concernent
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {sector_relevance.slice(0, 4).map((s, i) => (
                  <div key={i} className="p-2 rounded-lg bg-blue-50 border border-blue-100">
                    <div className="flex items-center justify-between mb-1">
                      <p className="text-sm font-medium text-slate-900">{s.sector}</p>
                      <Badge className={s.hiring_trend === "croissance" ? "bg-emerald-100 text-emerald-700 text-[10px]" : "bg-slate-100 text-slate-600 text-[10px]"}>
                        {s.hiring_trend === "croissance" ? "En croissance" : "Stable"}
                      </Badge>
                    </div>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {s.your_emerging_skills?.slice(0, 2).map((sk, j) => (
                        <Badge key={j} className="text-[10px] bg-emerald-50 text-emerald-600">{sk}</Badge>
                      ))}
                      {s.your_declining_skills?.slice(0, 1).map((sk, j) => (
                        <Badge key={j} className="text-[10px] bg-rose-50 text-rose-600">{sk}</Badge>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Declining Alerts */}
      {declining_alerts.length > 0 && (
        <Card className="border-rose-200 bg-rose-50/50">
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-rose-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-rose-800 text-sm">Compétences en déclin détectées dans votre CV</h4>
                <div className="flex flex-wrap gap-2 mt-2">
                  {declining_alerts.map((d, i) => (
                    <Badge key={i} className="bg-rose-100 text-rose-700">
                      {d.skill} <span className="opacity-60 ml-1">({d.sector})</span>
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

const EmergingSkillCard = ({ skill, rank }) => {
  const statusConfig = STATUS_CONFIG[skill.status] || STATUS_CONFIG.emergente;
  
  return (
    <div className="flex items-center gap-4 p-3 rounded-lg border border-slate-100 hover:border-blue-200 hover:bg-blue-50/30 transition-all">
      <div className="w-8 h-8 rounded-full bg-[#1e3a5f] text-white flex items-center justify-center font-bold text-sm">
        {rank}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <h4 className="font-semibold text-slate-900 truncate">{skill.skill_name}</h4>
          <Badge className={statusConfig.color}>{statusConfig.label}</Badge>
        </div>
        <div className="flex items-center gap-3 text-xs text-slate-500">
          <span className="flex items-center gap-1">
            <Users className="w-3 h-3" />
            {skill.contributor_count} contributeurs
          </span>
          <span className="flex items-center gap-1">
            <TrendingUp className="w-3 h-3 text-emerald-500" />
            +{Math.round(skill.growth_rate * 100)}%
          </span>
        </div>
      </div>
      <div className="text-right">
        <div className="text-lg font-bold text-[#1e3a5f]">{Math.round(skill.emergence_score * 100)}</div>
        <div className="text-xs text-slate-500">score</div>
      </div>
    </div>
  );
};

const EmergingSkillDetailCard = ({ skill }) => {
  const statusConfig = STATUS_CONFIG[skill.status] || STATUS_CONFIG.emergente;
  const StatusIcon = statusConfig.icon;
  
  return (
    <Card className="card-interactive">
      <CardContent className="p-5">
        <div className="flex items-start justify-between mb-3">
          <Badge className={statusConfig.color}>
            <StatusIcon className="w-3 h-3 mr-1" />
            {statusConfig.label}
          </Badge>
          <div className="text-right">
            <div className="text-xl font-bold text-[#1e3a5f]">{Math.round(skill.emergence_score * 100)}</div>
            <div className="text-xs text-slate-500">score</div>
          </div>
        </div>
        
        <h3 className="font-semibold text-slate-900 mb-2">{skill.skill_name}</h3>
        {skill.description && (
          <p className="text-sm text-slate-600 mb-3 line-clamp-2">{skill.description}</p>
        )}
        
        <div className="space-y-2 mb-3">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-600">Croissance</span>
            <span className="font-medium text-emerald-600">+{Math.round(skill.growth_rate * 100)}%</span>
          </div>
          <Progress value={skill.growth_rate * 100} className="h-1.5" />
        </div>
        
        {skill.related_sectors?.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-2">
            {skill.related_sectors.slice(0, 3).map((sector, idx) => (
              <Badge key={idx} variant="outline" className="text-xs">
                {sector}
              </Badge>
            ))}
          </div>
        )}
        
        {skill.related_tools?.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {skill.related_tools.slice(0, 3).map((tool, idx) => (
              <Badge key={idx} variant="secondary" className="text-xs">
                {tool}
              </Badge>
            ))}
          </div>
        )}
        
        <div className="flex items-center justify-between mt-3 pt-3 border-t border-slate-100 text-xs text-slate-500">
          <span>{skill.mention_count} mentions</span>
          <span>{skill.contributor_count} contributeurs</span>
        </div>
      </CardContent>
    </Card>
  );
};

const SectorTrendCard = ({ trend }) => {
  const hiringColors = {
    croissance: "text-emerald-600 bg-emerald-50",
    stable: "text-slate-600 bg-slate-50",
    declin: "text-red-600 bg-red-50"
  };
  
  return (
    <div className="p-4 rounded-lg border border-slate-100 hover:border-violet-200 transition-all">
      <div className="flex items-start justify-between mb-3">
        <div>
          <h4 className="font-semibold text-slate-900">{trend.sector_name}</h4>
          <Badge className={hiringColors[trend.hiring_trend] || hiringColors.stable}>
            {trend.hiring_trend === "croissance" ? "En croissance" : trend.hiring_trend === "declin" ? "En déclin" : "Stable"}
          </Badge>
        </div>
        {trend.skill_gap_alert && (
          <Badge className="bg-amber-100 text-amber-700">
            <AlertTriangle className="w-3 h-3 mr-1" />
            Alerte
          </Badge>
        )}
      </div>
      
      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs">
          <span className="text-slate-600">Indice de transformation</span>
          <span className="font-medium text-[#1e3a5f]">{Math.round(trend.transformation_index * 100)}%</span>
        </div>
        <Progress value={trend.transformation_index * 100} className="h-1.5" />
      </div>
      
      {trend.emerging_skills?.length > 0 && (
        <div className="mt-3">
          <p className="text-xs text-slate-500 mb-1">Compétences émergentes :</p>
          <div className="flex flex-wrap gap-1">
            {trend.emerging_skills.slice(0, 3).map((skill, idx) => (
              <Badge key={idx} className="bg-blue-50 text-blue-700 text-xs">{skill}</Badge>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

const SectorDetailCard = ({ trend }) => {
  return (
    <Card className="card-base">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Building2 className="w-5 h-5 text-[#1e3a5f]" />
              {trend.sector_name}
            </CardTitle>
            <CardDescription>
              Indice de transformation : {Math.round(trend.transformation_index * 100)}%
            </CardDescription>
          </div>
          {trend.skill_gap_alert && (
            <Badge className="bg-amber-100 text-amber-700">
              <AlertTriangle className="w-3 h-3 mr-1" />
              Alerte compétences
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <Progress value={trend.transformation_index * 100} className="h-2" />
        
        <div className="grid grid-cols-3 gap-4">
          <div>
            <p className="text-xs font-medium text-emerald-600 mb-2 flex items-center gap-1">
              <TrendingUp className="w-3 h-3" />
              Émergentes
            </p>
            <div className="space-y-1">
              {trend.emerging_skills?.map((skill, idx) => (
                <Badge key={idx} variant="secondary" className="text-xs block w-fit">{skill}</Badge>
              ))}
            </div>
          </div>
          <div>
            <p className="text-xs font-medium text-slate-600 mb-2 flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3" />
              Stables
            </p>
            <div className="space-y-1">
              {trend.stable_skills?.slice(0, 4).map((skill, idx) => (
                <Badge key={idx} variant="outline" className="text-xs block w-fit">{skill}</Badge>
              ))}
            </div>
          </div>
          <div>
            <p className="text-xs font-medium text-red-600 mb-2 flex items-center gap-1">
              <TrendingDown className="w-3 h-3" />
              En déclin
            </p>
            <div className="space-y-1">
              {trend.declining_skills?.map((skill, idx) => (
                <Badge key={idx} className="bg-red-50 text-red-700 text-xs block w-fit">{skill}</Badge>
              ))}
            </div>
          </div>
        </div>
        
        {trend.predicted_skills_demand?.length > 0 && (
          <div className="pt-4 border-t border-slate-100">
            <p className="text-xs font-medium text-slate-700 mb-2">Prévisions de demande :</p>
            <div className="space-y-2">
              {trend.predicted_skills_demand.map((pred, idx) => (
                <div key={idx} className="flex items-center justify-between text-sm">
                  <span className="text-slate-600">{pred.skill}</span>
                  <Badge className="bg-emerald-50 text-emerald-700">
                    {pred.demand_change} d'ici {pred.horizon}
                  </Badge>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

const PredictionCard = ({ prediction, sector }) => (
  <div className="flex items-center justify-between p-4 rounded-lg border border-slate-100 hover:border-emerald-200 transition-all">
    <div className="flex items-center gap-3">
      <div className="w-10 h-10 rounded-lg bg-emerald-100 flex items-center justify-center">
        <ArrowUpRight className="w-5 h-5 text-emerald-600" />
      </div>
      <div>
        <h4 className="font-semibold text-slate-900">{prediction.skill}</h4>
        <p className="text-xs text-slate-500">{sector}</p>
      </div>
    </div>
    <div className="text-right">
      <Badge className="bg-emerald-100 text-emerald-700 text-lg px-3">
        {prediction.demand_change}
      </Badge>
      <p className="text-xs text-slate-500 mt-1">Horizon {prediction.horizon}</p>
    </div>
  </div>
);

const ContributionCard = ({ contribution }) => {
  const typeConfig = CONTRIBUTION_TYPES[contribution.contribution_type] || CONTRIBUTION_TYPES.nouvelle_competence;
  const TypeIcon = typeConfig.icon;
  
  const statusColors = {
    en_attente: "bg-slate-100 text-slate-700",
    validee_ia: "bg-blue-100 text-blue-700",
    rejetee_ia: "bg-red-100 text-red-700",
    validee_humain: "bg-emerald-100 text-emerald-700",
    rejetee_humain: "bg-red-100 text-red-700",
    integree: "bg-green-100 text-green-700"
  };
  
  const statusLabels = {
    en_attente: "En attente d'analyse",
    validee_ia: "Validée par l'IA",
    rejetee_ia: "Rejetée par l'IA",
    validee_humain: "Validée par un expert",
    rejetee_humain: "Rejetée par un expert",
    integree: "Intégrée à l'observatoire"
  };
  
  return (
    <div className="p-4 rounded-lg border border-slate-200 hover:border-blue-200 transition-all">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className={`w-8 h-8 rounded-lg bg-${typeConfig.color}-100 flex items-center justify-center`}>
            <TypeIcon className={`w-4 h-4 text-${typeConfig.color}-600`} />
          </div>
          <div>
            <Badge variant="outline" className="text-xs">{typeConfig.label}</Badge>
          </div>
        </div>
        <Badge className={statusColors[contribution.status]}>
          {statusLabels[contribution.status]}
        </Badge>
      </div>
      
      <h4 className="font-semibold text-slate-900 mb-1">{contribution.skill_name}</h4>
      {contribution.skill_description && (
        <p className="text-sm text-slate-600 mb-2">{contribution.skill_description}</p>
      )}
      
      <div className="flex flex-wrap gap-2 text-xs text-slate-500">
        {contribution.related_job && (
          <span className="flex items-center gap-1">
            <Users className="w-3 h-3" />
            {contribution.related_job}
          </span>
        )}
        {contribution.related_sector && (
          <span className="flex items-center gap-1">
            <Building2 className="w-3 h-3" />
            {contribution.related_sector}
          </span>
        )}
        <span className="flex items-center gap-1">
          <Clock className="w-3 h-3" />
          {new Date(contribution.created_at).toLocaleDateString('fr-FR')}
        </span>
      </div>
      
      {contribution.ai_analysis && (
        <div className="mt-3 p-2 bg-blue-50 rounded text-xs text-blue-700">
          <Brain className="w-3 h-3 inline mr-1" />
          Score IA : {Math.round(contribution.ai_score * 100)}% - {contribution.ai_analysis.rationale}
        </div>
      )}
    </div>
  );
};


// ============== UBUNTOO INTELLIGENCE COMPONENTS ==============

const SIGNAL_TYPE_CONFIG = {
  competence_emergente: { label: "Compétence émergente", color: "bg-blue-100 text-blue-700", icon: Sparkles },
  nouvel_outil: { label: "Nouvel outil", color: "bg-violet-100 text-violet-700", icon: Layers },
  pratique_nouvelle: { label: "Nouvelle pratique", color: "bg-emerald-100 text-emerald-700", icon: Zap },
  transformation_metier: { label: "Transformation métier", color: "bg-amber-100 text-amber-700", icon: Building2 },
  difficulte_metier: { label: "Difficulté métier", color: "bg-rose-100 text-rose-700", icon: AlertTriangle }
};

const VALIDATION_STATUS_CONFIG = {
  detectee: { label: "Détecté", color: "bg-slate-100 text-slate-600", step: 1 },
  analysee_ia: { label: "Analysé par IA", color: "bg-blue-100 text-blue-700", step: 2 },
  validee_humain: { label: "Validé par expert", color: "bg-emerald-100 text-emerald-700", step: 3 },
  integree: { label: "Intégré", color: "bg-green-100 text-green-800", step: 4 },
  rejetee: { label: "Rejeté", color: "bg-red-100 text-red-700", step: 0 }
};

const UbuntooIntelligenceTab = ({ data }) => {
  if (!data) return null;
  const { stats = {}, by_type = {}, top_signals = [], recent_exchanges = [], insights = [] } = data;

  return (
    <div className="space-y-6">
      {/* Header with Ubuntoo branding */}
      <Card className="bg-gradient-to-r from-teal-600 to-teal-800 border-0">
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-xl bg-white/20 flex items-center justify-center">
                <img
                  src="https://customer-assets.emergentagent.com/job_keen-meitner-5/artifacts/t3wjk59k_logo_ubuntoo_transparent.png"
                  alt="Ubuntoo"
                  className="h-8 w-auto"
                />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white">Intelligence Collective Ubuntoo</h3>
                <p className="text-teal-100 text-sm">
                  Les échanges du réseau socio-professionnel analysés pour détecter les transformations du travail
                </p>
              </div>
            </div>
            <a
              href="/ubuntoo"
              target="_blank"
              rel="noopener noreferrer"
              data-testid="ubuntoo-open-link"
            >
              <Button className="bg-white text-teal-700 hover:bg-teal-50 font-semibold">
                <ExternalLink className="w-4 h-4 mr-2" />
                Ouvrir Ubuntoo
              </Button>
            </a>
          </div>
        </CardContent>
      </Card>

      {/* Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4" data-testid="ubuntoo-stats">
        <Card className="card-metric">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-teal-600 text-white flex items-center justify-center">
                <MessageCircle className="w-5 h-5" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{stats.total_exchanges_analyzed || 0}</p>
                <p className="text-xs text-slate-500">Échanges analysés</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="card-metric">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-blue-600 text-white flex items-center justify-center">
                <Radio className="w-5 h-5" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{stats.total_signals_detected || 0}</p>
                <p className="text-xs text-slate-500">Signaux détectés</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="card-metric">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-amber-600 text-white flex items-center justify-center">
                <Brain className="w-5 h-5" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{stats.signals_analyzed_ia || 0}</p>
                <p className="text-xs text-slate-500">Analysés par IA</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="card-metric">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-600 text-white flex items-center justify-center">
                <CheckCircle2 className="w-5 h-5" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{stats.signals_validated_human || 0}</p>
                <p className="text-xs text-slate-500">Validés humain</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="card-metric">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-green-600 text-white flex items-center justify-center">
                <Link2 className="w-5 h-5" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{stats.signals_integrated || 0}</p>
                <p className="text-xs text-slate-500">Intégrés observatoire</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="card-metric">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-slate-600 text-white flex items-center justify-center">
                <Eye className="w-5 h-5" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{stats.signals_detected || 0}</p>
                <p className="text-xs text-slate-500">En attente</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top Signals */}
        <div className="lg:col-span-2 space-y-6">
          <Card className="card-base">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Radio className="w-5 h-5 text-teal-600" />
                Signaux détectés dans les échanges
              </CardTitle>
              <CardDescription>
                Compétences, outils et pratiques émergentes identifiés par l'IA dans les discussions Ubuntoo
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {top_signals.map((signal, idx) => (
                  <UbuntooSignalCard key={idx} signal={signal} />
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Recent Exchanges */}
          <Card className="card-base">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageCircle className="w-5 h-5 text-teal-600" />
                Échanges récents analysés
              </CardTitle>
              <CardDescription>
                Extraits anonymisés des discussions du réseau (analyse automatique)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {recent_exchanges.map((exchange, idx) => (
                  <UbuntooExchangeCard key={idx} exchange={exchange} />
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Insights + Ethics */}
        <div className="space-y-6">
          {/* Insights */}
          <Card className="card-base">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lightbulb className="w-5 h-5 text-amber-500" />
                Insights croisés
              </CardTitle>
              <CardDescription>
                Conclusions issues du croisement Ubuntoo × Observatoire
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {insights.map((insight, idx) => (
                  <UbuntooInsightCard key={idx} insight={insight} />
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Validation Pipeline */}
          <Card className="card-base">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Target className="w-5 h-5 text-[#1e3a5f]" />
                Pipeline de validation
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  { step: 1, label: "Détection algorithmique", desc: "L'IA repère les signaux dans les échanges", icon: Brain, color: "bg-blue-500" },
                  { step: 2, label: "Analyse contextuelle", desc: "Vérification des métiers et secteurs concernés", icon: Compass, color: "bg-violet-500" },
                  { step: 3, label: "Validation humaine", desc: "Confirmation par un comité d'experts", icon: Users, color: "bg-emerald-500" },
                  { step: 4, label: "Intégration", desc: "Enrichissement de l'observatoire prédictif", icon: Link2, color: "bg-green-600" }
                ].map((step) => {
                  const Icon = step.icon;
                  return (
                    <div key={step.step} className="flex items-start gap-3">
                      <div className={`w-8 h-8 rounded-lg ${step.color} text-white flex items-center justify-center flex-shrink-0 text-sm font-bold`}>
                        {step.step}
                      </div>
                      <div>
                        <p className="text-sm font-medium text-slate-900">{step.label}</p>
                        <p className="text-xs text-slate-500">{step.desc}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          {/* Ethics Card */}
          <Card className="border-teal-200 bg-teal-50/50">
            <CardContent className="p-5">
              <div className="flex items-start gap-3">
                <Shield className="w-6 h-6 text-teal-700 flex-shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-teal-900 mb-2">Gouvernance éthique</h4>
                  <ul className="text-xs text-teal-700 space-y-1.5">
                    <li className="flex items-start gap-1.5">
                      <CheckCircle2 className="w-3 h-3 mt-0.5 flex-shrink-0" />
                      Données entièrement anonymisées
                    </li>
                    <li className="flex items-start gap-1.5">
                      <CheckCircle2 className="w-3 h-3 mt-0.5 flex-shrink-0" />
                      Analyse des tendances collectives uniquement
                    </li>
                    <li className="flex items-start gap-1.5">
                      <CheckCircle2 className="w-3 h-3 mt-0.5 flex-shrink-0" />
                      Aucune exploitation individuelle
                    </li>
                    <li className="flex items-start gap-1.5">
                      <CheckCircle2 className="w-3 h-3 mt-0.5 flex-shrink-0" />
                      Transparence sur l'usage des données
                    </li>
                    <li className="flex items-start gap-1.5">
                      <CheckCircle2 className="w-3 h-3 mt-0.5 flex-shrink-0" />
                      Droit de retrait pour les utilisateurs
                    </li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

const UbuntooSignalCard = ({ signal }) => {
  const typeConfig = SIGNAL_TYPE_CONFIG[signal.signal_type] || SIGNAL_TYPE_CONFIG.competence_emergente;
  const statusConfig = VALIDATION_STATUS_CONFIG[signal.validation_status] || VALIDATION_STATUS_CONFIG.detectee;
  const TypeIcon = typeConfig.icon;

  return (
    <div className="p-4 rounded-lg border border-slate-200 hover:border-teal-200 transition-all" data-testid="ubuntoo-signal-card">
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <Badge className={typeConfig.color}>
            <TypeIcon className="w-3 h-3 mr-1" />
            {typeConfig.label}
          </Badge>
        </div>
        <Badge className={statusConfig.color}>{statusConfig.label}</Badge>
      </div>
      <h4 className="font-semibold text-slate-900 mb-1">{signal.name}</h4>
      <p className="text-sm text-slate-600 mb-3 line-clamp-2">{signal.description}</p>
      <div className="flex items-center gap-4 text-xs text-slate-500">
        <span className="flex items-center gap-1">
          <MessageCircle className="w-3 h-3" />
          {signal.mention_count} mentions
        </span>
        <span className="flex items-center gap-1">
          <Users className="w-3 h-3" />
          {signal.source_exchanges_count} échanges
        </span>
        {signal.ai_confidence > 0 && (
          <span className="flex items-center gap-1">
            <Brain className="w-3 h-3" />
            IA: {Math.round(signal.ai_confidence * 100)}%
          </span>
        )}
        <span className="flex items-center gap-1 ml-auto">
          <TrendingUp className="w-3 h-3 text-emerald-500" />
          +{Math.round(signal.growth_rate * 100)}%
        </span>
      </div>
      {(signal.related_sectors?.length > 0 || signal.related_jobs?.length > 0) && (
        <div className="flex flex-wrap gap-1 mt-2 pt-2 border-t border-slate-100">
          {signal.related_sectors?.slice(0, 3).map((s, i) => (
            <Badge key={`s-${i}`} variant="outline" className="text-xs">{s}</Badge>
          ))}
          {signal.related_jobs?.slice(0, 2).map((j, i) => (
            <Badge key={`j-${i}`} variant="secondary" className="text-xs">{j}</Badge>
          ))}
        </div>
      )}
    </div>
  );
};

const UbuntooExchangeCard = ({ exchange }) => {
  const typeLabels = {
    discussion: "Discussion",
    mentorat: "Mentorat",
    conseil: "Conseil",
    retour_experience: "Retour d'expérience",
    question: "Question"
  };
  const typeColors = {
    discussion: "bg-blue-100 text-blue-700",
    mentorat: "bg-violet-100 text-violet-700",
    conseil: "bg-emerald-100 text-emerald-700",
    retour_experience: "bg-amber-100 text-amber-700",
    question: "bg-cyan-100 text-cyan-700"
  };

  return (
    <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
      <div className="flex items-center gap-2 mb-2">
        <Badge className={typeColors[exchange.exchange_type] || typeColors.discussion}>
          {typeLabels[exchange.exchange_type] || "Échange"}
        </Badge>
        <span className="text-xs text-slate-400">
          {new Date(exchange.timestamp).toLocaleDateString('fr-FR')}
        </span>
      </div>
      <p className="text-sm text-slate-700 mb-2 italic">"{exchange.content_summary}"</p>
      <div className="flex flex-wrap gap-1">
        {exchange.detected_skills?.slice(0, 3).map((s, i) => (
          <Badge key={i} className="bg-blue-50 text-blue-600 text-xs">{s}</Badge>
        ))}
        {exchange.detected_tools?.slice(0, 2).map((t, i) => (
          <Badge key={`t-${i}`} className="bg-violet-50 text-violet-600 text-xs">{t}</Badge>
        ))}
      </div>
    </div>
  );
};

const UbuntooInsightCard = ({ insight }) => {
  const priorityColors = {
    haute: "bg-rose-100 text-rose-700 border-rose-200",
    moyenne: "bg-amber-100 text-amber-700 border-amber-200",
    basse: "bg-slate-100 text-slate-600 border-slate-200"
  };
  const typeIcons = {
    tendance_emergente: TrendingUp,
    alerte_competence: AlertTriangle,
    opportunite_formation: Lightbulb,
    transformation_metier: Building2
  };
  const Icon = typeIcons[insight.insight_type] || Lightbulb;

  return (
    <div className={`p-3 rounded-lg border ${priorityColors[insight.priority] || priorityColors.moyenne}`}>
      <div className="flex items-start gap-2 mb-2">
        <Icon className="w-4 h-4 flex-shrink-0 mt-0.5" />
        <div>
          <h5 className="text-sm font-semibold">{insight.title}</h5>
          <p className="text-xs mt-1 opacity-80">{insight.description}</p>
          {insight.recommendation && (
            <p className="text-xs mt-2 font-medium">
              Recommandation : {insight.recommendation}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

const CvDetectedTab = ({ data, token, onRefresh }) => {
  if (data === "loading") return (
    <div className="flex items-center justify-center py-12 gap-3">
      <Loader2 className="w-5 h-5 animate-spin text-violet-500" />
      <p className="text-sm text-slate-500">Analyse IA en cours pour votre secteur...</p>
    </div>
  );

  if (!data) return (
    <div className="text-center py-12 space-y-4">
      <Target className="w-12 h-12 mx-auto mb-3 text-slate-300" />
      <p className="text-sm text-slate-400">Cliquez ci-dessous pour détecter les compétences émergentes dans votre profil</p>
      <Button
        onClick={onRefresh}
        className="bg-violet-600 hover:bg-violet-700 text-white"
        data-testid="detect-emerging-btn"
      >
        <Sparkles className="w-4 h-4 mr-2" />Lancer la détection IA
      </Button>
    </div>
  );

  const { top_emerging = [], by_category = [], by_level = [] } = data;

  return (
    <div className="space-y-6" data-testid="cv-detected-tab">
      <Card className="card-base">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="w-5 h-5 text-violet-600" />
            Compétences émergentes détectées
          </CardTitle>
          <CardDescription>Compétences en croissance identifiées dans votre profil et votre secteur</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <Card className="bg-violet-50 border-violet-200">
              <CardContent className="p-3 text-center">
                <p className="text-2xl font-bold text-violet-700">{top_emerging.length}</p>
                <p className="text-xs text-violet-500">Total détectées</p>
              </CardContent>
            </Card>
            <Card className="bg-blue-50 border-blue-200">
              <CardContent className="p-3 text-center">
                <p className="text-2xl font-bold text-blue-700">{by_category.length}</p>
                <p className="text-xs text-blue-500">Catégories</p>
              </CardContent>
            </Card>
            <Card className="bg-emerald-50 border-emerald-200">
              <CardContent className="p-3 text-center">
                <p className="text-2xl font-bold text-emerald-700">
                  {top_emerging.length > 0 ? Math.round(top_emerging.reduce((s, c) => s + (c.score_emergence || 0), 0) / top_emerging.length) : 0}
                </p>
                <p className="text-xs text-emerald-500">Score moyen</p>
              </CardContent>
            </Card>
          </div>

          {/* By Category */}
          {by_category.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-slate-700 mb-3">Répartition par catégorie</h4>
              <div className="space-y-2">
                {by_category.map((cat, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <span className="text-xs text-slate-600 w-32 truncate">{cat.categorie}</span>
                    <div className="flex-1 bg-slate-100 rounded-full h-3 overflow-hidden">
                      <div className="h-full bg-violet-500 rounded-full transition-all" style={{ width: `${Math.min(100, (cat.count / Math.max(...by_category.map(c => c.count))) * 100)}%` }} />
                    </div>
                    <span className="text-xs font-medium text-slate-700 w-12 text-right">{cat.count} ({cat.avg_score})</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* By Level */}
          {by_level.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-slate-700 mb-3">Répartition par niveau</h4>
              <div className="flex gap-3">
                {by_level.map((lvl, i) => {
                  const levelColors = {
                    signal_faible: "bg-slate-100 text-slate-700",
                    emergente: "bg-violet-100 text-violet-700",
                    en_croissance: "bg-amber-100 text-amber-700",
                    etablie: "bg-emerald-100 text-emerald-700"
                  };
                  return (
                    <Badge key={i} className={`${levelColors[lvl.level] || "bg-slate-100"} px-3 py-1.5`}>
                      {lvl.level}: {lvl.count}
                    </Badge>
                  );
                })}
              </div>
            </div>
          )}

          {/* Top Competences List */}
          {top_emerging.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-slate-700 mb-3">Top compétences émergentes (score &ge; 31)</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {top_emerging.map((comp, i) => {
                  const name = comp.nom_principal || comp.name || "";
                  const cat = comp.categorie || comp.category || "";
                  const level = comp.niveau_emergence || comp.level || comp.match_type || "";
                  const secteurs = comp.secteurs_porteurs || comp.sectors || [];
                  const matchColors = {
                    "direct": "bg-emerald-100 text-emerald-700",
                    "confirme": "bg-emerald-100 text-emerald-700",
                    "partiel": "bg-blue-100 text-blue-700",
                    "intermediaire": "bg-blue-100 text-blue-700",
                    "opportunite": "bg-amber-100 text-amber-700",
                    "a_developper": "bg-amber-100 text-amber-700",
                  };
                  return (
                    <div key={i} className="flex items-center gap-3 p-3 rounded-lg border border-violet-100 hover:bg-violet-50/30 transition-all" data-testid={`cv-emerging-${i}`}>
                      <div className="w-10 h-10 rounded-full bg-violet-100 flex items-center justify-center font-bold text-violet-700 text-sm shrink-0">
                        {comp.score_emergence}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-slate-900 truncate">{name}</p>
                        <div className="flex items-center gap-1.5 mt-0.5">
                          <Badge variant="outline" className="text-[10px]">{cat}</Badge>
                          <Badge className={`text-[10px] ${matchColors[level] || "bg-slate-100 text-slate-700"}`}>{level}</Badge>
                        </div>
                      </div>
                      {secteurs.length > 0 && (
                        <div className="hidden md:flex flex-wrap gap-1">
                          {secteurs.slice(0, 2).map((s, j) => (
                            <Badge key={j} className="bg-blue-50 text-blue-600 text-[10px]">{s}</Badge>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default ObservatoireView;
