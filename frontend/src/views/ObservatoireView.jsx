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
  Layers
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

const ObservatoireView = ({ token }) => {
  const [dashboard, setDashboard] = useState(null);
  const [contributions, setContributions] = useState([]);
  const [loading, setLoading] = useState(true);
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
      const [dashboardRes, contributionsRes] = await Promise.all([
        axios.get(`${API}/observatoire/dashboard`),
        axios.get(`${API}/observatoire/contributions?token=${token}`)
      ]);
      setDashboard(dashboardRes.data);
      setContributions(contributionsRes.data);
    } catch (error) {
      console.error("Error loading observatoire:", error);
    }
    setLoading(false);
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
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 flex items-center gap-3" style={{ fontFamily: 'Outfit, sans-serif' }}>
            <Brain className="w-8 h-8 text-[#1e3a5f]" />
            Observatoire Prédictif des Compétences
          </h1>
          <p className="text-slate-600 mt-1">
            Intelligence collective sur l'évolution du travail et des compétences
          </p>
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
        <TabsList className="grid grid-cols-2 md:grid-cols-5 gap-1 h-auto p-1 bg-slate-100">
          <TabsTrigger value="overview" className="text-xs sm:text-sm py-2" data-testid="tab-overview">
            <BarChart3 className="w-4 h-4 mr-1 hidden sm:inline" />
            Vue d'ensemble
          </TabsTrigger>
          <TabsTrigger value="emerging" className="text-xs sm:text-sm py-2" data-testid="tab-emerging">
            <Sparkles className="w-4 h-4 mr-1 hidden sm:inline" />
            Compétences émergentes
          </TabsTrigger>
          <TabsTrigger value="sectors" className="text-xs sm:text-sm py-2" data-testid="tab-sectors">
            <Building2 className="w-4 h-4 mr-1 hidden sm:inline" />
            Secteurs
          </TabsTrigger>
          <TabsTrigger value="predictions" className="text-xs sm:text-sm py-2" data-testid="tab-predictions">
            <Compass className="w-4 h-4 mr-1 hidden sm:inline" />
            Prédictions
          </TabsTrigger>
          <TabsTrigger value="contributions" className="text-xs sm:text-sm py-2" data-testid="tab-my-contributions">
            <Lightbulb className="w-4 h-4 mr-1 hidden sm:inline" />
            Mes contributions
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Top Emerging Skills */}
            <Card className="card-base">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-blue-600" />
                  Top Compétences Émergentes
                </CardTitle>
                <CardDescription>Les compétences qui transforment le marché du travail</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {emerging_skills.slice(0, 5).map((skill, idx) => (
                    <EmergingSkillCard key={idx} skill={skill} rank={idx + 1} />
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Sectors in Transformation */}
            <Card className="card-base">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Building2 className="w-5 h-5 text-violet-600" />
                  Secteurs en Transformation
                </CardTitle>
                <CardDescription>Dynamiques sectorielles et besoins en compétences</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {sector_trends.map((trend, idx) => (
                    <SectorTrendCard key={idx} trend={trend} />
                  ))}
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
                Cartographie des Compétences Émergentes
              </CardTitle>
              <CardDescription>
                Compétences nouvellement identifiées par l'intelligence collective
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {emerging_skills.map((skill, idx) => (
                  <EmergingSkillDetailCard key={idx} skill={skill} />
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Sectors Tab */}
        <TabsContent value="sectors" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {sector_trends.map((trend, idx) => (
              <SectorDetailCard key={idx} trend={trend} />
            ))}
          </div>
        </TabsContent>

        {/* Predictions Tab */}
        <TabsContent value="predictions" className="space-y-4">
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
            <CardContent>
              <div className="space-y-4">
                {sector_trends.flatMap(trend => 
                  (trend.predicted_skills_demand || []).map((pred, idx) => (
                    <PredictionCard 
                      key={`${trend.sector_name}-${idx}`} 
                      prediction={pred} 
                      sector={trend.sector_name} 
                    />
                  ))
                )}
              </div>
            </CardContent>
          </Card>
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
      </Tabs>
    </div>
  );
};

// Sub-components

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

export default ObservatoireView;
