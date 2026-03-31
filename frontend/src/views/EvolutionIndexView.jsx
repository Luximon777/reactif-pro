import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { 
  Gauge,
  TrendingUp,
  TrendingDown,
  Building2,
  Briefcase,
  Target,
  AlertTriangle,
  CheckCircle2,
  ArrowRight,
  ChevronRight,
  Sparkles,
  BookOpen,
  Users,
  Zap,
  Shield,
  Clock,
  BarChart3,
  PieChart,
  Info,
  RefreshCw
} from "lucide-react";

const INDEX_LEVELS = {
  stable: {
    label: "Très stable",
    range: "0-20",
    color: "emerald",
    bgColor: "bg-emerald-500",
    textColor: "text-emerald-700",
    bgLight: "bg-emerald-50",
    borderColor: "border-emerald-200",
    icon: CheckCircle2,
    description: "Évolution lente, formation initiale pertinente sur le long terme"
  },
  evolutif: {
    label: "Évolutif",
    range: "20-50",
    color: "blue",
    bgColor: "bg-blue-500",
    textColor: "text-blue-700",
    bgLight: "bg-blue-50",
    borderColor: "border-blue-200",
    icon: TrendingUp,
    description: "Évolutions modérées, formation continue recommandée"
  },
  en_transformation: {
    label: "En transformation",
    range: "50-80",
    color: "amber",
    bgColor: "bg-amber-500",
    textColor: "text-amber-700",
    bgLight: "bg-amber-50",
    borderColor: "border-amber-200",
    icon: Zap,
    description: "Évolutions significatives, adaptation nécessaire"
  },
  forte_mutation: {
    label: "Forte mutation",
    range: "80-100",
    color: "rose",
    bgColor: "bg-rose-500",
    textColor: "text-rose-700",
    bgLight: "bg-rose-50",
    borderColor: "border-rose-200",
    icon: AlertTriangle,
    description: "Impact fort des innovations, adaptation rapide requise"
  }
};

const EvolutionIndexView = ({ token, embedded }) => {
  const [dashboard, setDashboard] = useState(null);
  const [userAnalysis, setUserAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");
  const [selectedJob, setSelectedJob] = useState(null);

  useEffect(() => {
    loadData();
  }, [token]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [dashboardRes, userRes] = await Promise.all([
        axios.get(`${API}/evolution-index/dashboard`),
        axios.get(`${API}/evolution-index/user-profile?token=${token}`)
      ]);
      setDashboard(dashboardRes.data);
      setUserAnalysis(userRes.data);
    } catch (error) {
      console.error("Error loading evolution index:", error);
    }
    setLoading(false);
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-3">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#1e3a5f]"></div>
        <p className="text-sm text-slate-500">Analyse de l'évolution de vos compétences...</p>
        <p className="text-xs text-slate-400">Première analyse : quelques secondes</p>
      </div>
    );
  }

  const { summary = {}, distribution = {}, top_transforming_jobs = [], most_stable_jobs = [], sectors = [] } = dashboard || {};

  // Personalized summary: prefer user data over global data
  const hasUserData = userAnalysis && (userAnalysis.relevant_jobs?.length > 0 || userAnalysis.has_cv);
  const personalSummary = hasUserData ? {
    total_jobs_analyzed: userAnalysis.relevant_jobs?.length || 0,
    total_sectors_analyzed: userAnalysis.profile_sectors?.length || 0,
    average_job_evolution_index: userAnalysis.evolution_exposure || 0,
    average_sector_evolution_index: userAnalysis.relevant_jobs?.length > 0
      ? Math.round(userAnalysis.relevant_jobs.reduce((s, j) => s + (j.evolution_index || 0), 0) / userAnalysis.relevant_jobs.length)
      : 0
  } : summary;

  // Personalized distribution when user has relevant jobs
  const personalDistribution = hasUserData && userAnalysis.relevant_jobs?.length > 0
    ? (() => {
        const jobs = userAnalysis.relevant_jobs;
        const total = jobs.length;
        const stable = jobs.filter(j => (j.evolution_index || 0) < 20).length;
        const evolving = jobs.filter(j => (j.evolution_index || 0) >= 20 && (j.evolution_index || 0) < 50).length;
        const transforming = jobs.filter(j => (j.evolution_index || 0) >= 50 && (j.evolution_index || 0) < 80).length;
        const highly_impacted = jobs.filter(j => (j.evolution_index || 0) >= 80).length;
        return {
          stable: { count: stable, percentage: total ? Math.round(stable / total * 100) : 0 },
          evolving: { count: evolving, percentage: total ? Math.round(evolving / total * 100) : 0 },
          transforming: { count: transforming, percentage: total ? Math.round(transforming / total * 100) : 0 },
          highly_impacted: { count: highly_impacted, percentage: total ? Math.round(highly_impacted / total * 100) : 0 },
        };
      })()
    : distribution;

  // Personalized jobs for overview tab
  const personalTopTransforming = hasUserData && userAnalysis.relevant_jobs?.length > 0
    ? [...userAnalysis.relevant_jobs].sort((a, b) => (b.evolution_index || 0) - (a.evolution_index || 0))
    : top_transforming_jobs;
  const personalMostStable = hasUserData && userAnalysis.relevant_jobs?.length > 0
    ? [...userAnalysis.relevant_jobs].sort((a, b) => (a.evolution_index || 0) - (b.evolution_index || 0))
    : most_stable_jobs;

  const handleRefresh = async () => {
    try {
      await axios.post(`${API}/evolution-index/refresh?token=${token}`);
      setLoading(true);
      await loadData();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in" data-testid="evolution-index-view">
      {/* Header */}
      {!embedded && (
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 flex items-center gap-3" style={{ fontFamily: 'Outfit, sans-serif' }}>
            <Gauge className="w-8 h-8 text-[#1e3a5f]" />
            Indice d'Évolution des Compétences
          </h1>
          <p className="text-slate-600 mt-1">
            Mesurez la vitesse à laquelle les compétences d'un métier ou d'un secteur évoluent
          </p>
        </div>
        <button
          onClick={handleRefresh}
          className="flex items-center gap-2 text-sm text-[#1e3a5f] hover:bg-blue-50 px-3 py-2 rounded-lg transition-colors border border-blue-200"
          data-testid="evolution-refresh-btn"
        >
          <RefreshCw className="w-4 h-4" /> Actualiser l'analyse
        </button>
      </div>
      )}

      {/* Personal Exposure Alert */}
      {userAnalysis && (
        <EvolutionExposureCard analysis={userAnalysis} />
      )}

      {/* Summary Cards - Personalized when user has data */}
      {hasUserData && (
        <div className="flex items-center gap-2 px-3 py-1.5 bg-blue-50 border border-blue-200 rounded-lg">
          <Sparkles className="w-4 h-4 text-blue-600" />
          <p className="text-xs text-blue-700 font-medium">Données personnalisées basées sur votre CV et profil</p>
        </div>
      )}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4" data-testid="evolution-summary">
        <Card className="card-metric">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-[#1e3a5f] text-white flex items-center justify-center">
                <Briefcase className="w-5 h-5" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{personalSummary.total_jobs_analyzed || 0}</p>
                <p className="text-xs text-slate-500">{hasUserData ? "Métiers liés à votre profil" : "Métiers analysés"}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="card-metric">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-blue-600 text-white flex items-center justify-center">
                <Building2 className="w-5 h-5" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{personalSummary.total_sectors_analyzed || 0}</p>
                <p className="text-xs text-slate-500">{hasUserData ? "Vos secteurs d'activité" : "Secteurs analysés"}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="card-metric">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-amber-600 text-white flex items-center justify-center">
                <Gauge className="w-5 h-5" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{personalSummary.average_job_evolution_index || 0}</p>
                <p className="text-xs text-slate-500">{hasUserData ? "Votre indice d'évolution" : "Indice moyen métiers"}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="card-metric">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-violet-600 text-white flex items-center justify-center">
                <TrendingUp className="w-5 h-5" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{personalSummary.average_sector_evolution_index || 0}</p>
                <p className="text-xs text-slate-500">{hasUserData ? "Indice moyen vos secteurs" : "Indice moyen secteurs"}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Distribution Chart */}
      <Card className="card-base">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <PieChart className="w-5 h-5 text-[#1e3a5f]" />
            Répartition des métiers par niveau d'évolution
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {Object.entries(INDEX_LEVELS).map(([key, config]) => {
              const data = personalDistribution[key === "stable" ? "stable" : key === "evolutif" ? "evolving" : key === "en_transformation" ? "transforming" : "highly_impacted"] || { count: 0, percentage: 0 };
              const Icon = config.icon;
              return (
                <div key={key} className={`p-4 rounded-xl ${config.bgLight} border ${config.borderColor}`}>
                  <div className="flex items-center gap-2 mb-2">
                    <Icon className={`w-5 h-5 ${config.textColor}`} />
                    <span className={`font-semibold ${config.textColor}`}>{config.label}</span>
                  </div>
                  <div className="flex items-end gap-2">
                    <span className="text-3xl font-bold text-slate-900">{data.count}</span>
                    <span className="text-sm text-slate-500 mb-1">métiers ({data.percentage}%)</span>
                  </div>
                  <p className="text-xs text-slate-500 mt-2">Indice {config.range}</p>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Main Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid grid-cols-2 md:grid-cols-4 gap-1 h-auto p-1 bg-slate-100">
          <TabsTrigger value="overview" className="text-xs sm:text-sm py-2" data-testid="tab-overview">
            <BarChart3 className="w-4 h-4 mr-1 hidden sm:inline" />
            Vue d'ensemble
          </TabsTrigger>
          <TabsTrigger value="jobs" className="text-xs sm:text-sm py-2" data-testid="tab-jobs">
            <Briefcase className="w-4 h-4 mr-1 hidden sm:inline" />
            Par métier
          </TabsTrigger>
          <TabsTrigger value="sectors" className="text-xs sm:text-sm py-2" data-testid="tab-sectors">
            <Building2 className="w-4 h-4 mr-1 hidden sm:inline" />
            Par secteur
          </TabsTrigger>
          <TabsTrigger value="guide" className="text-xs sm:text-sm py-2" data-testid="tab-guide">
            <Info className="w-4 h-4 mr-1 hidden sm:inline" />
            Guide
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Top Transforming Jobs */}
            <Card className="card-base">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-rose-600" />
                  {hasUserData ? "Métiers en mutation liés à votre profil" : "Métiers en forte mutation"}
                </CardTitle>
                <CardDescription>{hasUserData ? "Les métiers proches de votre profil les plus impactés" : "Les métiers les plus impactés par les transformations"}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {personalTopTransforming.map((job, idx) => (
                    <JobIndexCard key={idx} job={job} />
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Most Stable Jobs */}
            <Card className="card-base">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                  {hasUserData ? "Métiers les plus stables de votre profil" : "Métiers les plus stables"}
                </CardTitle>
                <CardDescription>{hasUserData ? "Les métiers proches de votre profil avec le moins de transformations" : "Les métiers dont les compétences évoluent peu"}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {personalMostStable.map((job, idx) => (
                    <JobIndexCard key={idx} job={job} />
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sectors Overview */}
          <Card className="card-base">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building2 className="w-5 h-5 text-[#1e3a5f]" />
                Indice par secteur d'activité
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {sectors.map((sector, idx) => (
                  <SectorIndexCard key={idx} sector={sector} />
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Jobs Tab */}
        <TabsContent value="jobs" className="space-y-4">
          <Card className="card-base">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Briefcase className="w-5 h-5 text-[#1e3a5f]" />
                Fiches métiers avec indice d'évolution
              </CardTitle>
              <CardDescription>
                Explorez l'indice d'évolution de chaque métier et ses compétences associées
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[...top_transforming_jobs, ...most_stable_jobs].map((job, idx) => (
                  <JobDetailCard key={idx} job={job} />
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Sectors Tab */}
        <TabsContent value="sectors" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {sectors.map((sector, idx) => (
              <SectorDetailCard key={idx} sector={sector} />
            ))}
          </div>
        </TabsContent>

        {/* Guide Tab */}
        <TabsContent value="guide" className="space-y-4">
          <Card className="card-base">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Info className="w-5 h-5 text-[#1e3a5f]" />
                Comprendre l'indice d'évolution des compétences
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="prose prose-slate max-w-none">
                <p className="text-slate-600">
                  L'indice d'évolution des compétences mesure la vitesse à laquelle les compétences 
                  d'un métier ou d'un secteur se transforment. Il prend en compte :
                </p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
                  <Sparkles className="w-6 h-6 text-blue-600 mb-2" />
                  <h4 className="font-semibold text-slate-900 mb-1">Nouvelles compétences</h4>
                  <p className="text-sm text-slate-600">Nombre et fréquence d'apparition de nouvelles compétences</p>
                </div>
                <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
                  <Zap className="w-6 h-6 text-amber-600 mb-2" />
                  <h4 className="font-semibold text-slate-900 mb-1">Évolution des tâches</h4>
                  <p className="text-sm text-slate-600">Modification des activités et missions du métier</p>
                </div>
                <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
                  <Target className="w-6 h-6 text-violet-600 mb-2" />
                  <h4 className="font-semibold text-slate-900 mb-1">Nouveaux outils</h4>
                  <p className="text-sm text-slate-600">Introduction de nouvelles technologies</p>
                </div>
                <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
                  <BarChart3 className="w-6 h-6 text-emerald-600 mb-2" />
                  <h4 className="font-semibold text-slate-900 mb-1">Offres d'emploi</h4>
                  <p className="text-sm text-slate-600">Évolution des compétences demandées</p>
                </div>
                <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
                  <TrendingDown className="w-6 h-6 text-rose-600 mb-2" />
                  <h4 className="font-semibold text-slate-900 mb-1">Compétences en déclin</h4>
                  <p className="text-sm text-slate-600">Compétences devenant moins pertinentes</p>
                </div>
                <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
                  <Users className="w-6 h-6 text-cyan-600 mb-2" />
                  <h4 className="font-semibold text-slate-900 mb-1">Intelligence collective</h4>
                  <p className="text-sm text-slate-600">Contributions des professionnels du terrain</p>
                </div>
              </div>

              <div className="mt-6">
                <h4 className="font-semibold text-slate-900 mb-4">Échelle d'interprétation</h4>
                <div className="space-y-3">
                  {Object.entries(INDEX_LEVELS).map(([key, config]) => {
                    const Icon = config.icon;
                    return (
                      <div key={key} className={`p-4 rounded-lg ${config.bgLight} border ${config.borderColor}`}>
                        <div className="flex items-start gap-3">
                          <div className={`w-12 h-12 rounded-lg ${config.bgColor} text-white flex items-center justify-center flex-shrink-0`}>
                            <Icon className="w-6 h-6" />
                          </div>
                          <div>
                            <div className="flex items-center gap-2 mb-1">
                              <h5 className={`font-semibold ${config.textColor}`}>{config.label}</h5>
                              <Badge variant="outline">{config.range}</Badge>
                            </div>
                            <p className="text-sm text-slate-600">{config.description}</p>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

// Sub-components

const EvolutionExposureCard = ({ analysis }) => {
  const exposure = analysis.evolution_exposure || 50;
  const interpretation = analysis.exposure_interpretation || {};
  const levelConfig = INDEX_LEVELS[interpretation.level] || INDEX_LEVELS.evolutif;
  const Icon = levelConfig.icon;
  const hasCv = analysis.has_cv;

  return (
    <Card className={`${levelConfig.bgLight} border ${levelConfig.borderColor}`} data-testid="evolution-exposure-card">
      <CardContent className="p-6">
        <div className="flex flex-col md:flex-row md:items-center gap-6">
          <div className="flex items-center gap-4">
            <div className={`w-16 h-16 rounded-xl ${levelConfig.bgColor} text-white flex items-center justify-center`}>
              <Gauge className="w-8 h-8" />
            </div>
            <div>
              <p className="text-sm text-slate-600 mb-1">Votre exposition aux transformations</p>
              <div className="flex items-baseline gap-2">
                <span className="text-4xl font-bold text-slate-900">{exposure}</span>
                <span className="text-slate-500">/100</span>
              </div>
              <Badge className={`${levelConfig.bgLight} ${levelConfig.textColor} ${levelConfig.borderColor} border mt-1`}>
                <Icon className="w-3 h-3 mr-1" />
                {levelConfig.label}
              </Badge>
            </div>
          </div>
          
          <div className="flex-1 md:border-l md:pl-6 border-slate-200">
            <p className="text-sm text-slate-700 mb-3">{interpretation.description}</p>
            <p className="text-sm font-medium text-slate-900">
              {interpretation.recommendation}
            </p>
            {!hasCv && (
              <p className="text-xs text-amber-600 mt-2 flex items-center gap-1">
                <AlertTriangle className="w-3 h-3" />
                Analysez votre CV pour une évaluation personnalisée basée sur vos compétences réelles
              </p>
            )}
            {hasCv && analysis.data_sources && (
              <div className="flex gap-2 mt-2">
                {analysis.data_sources.cv_analysis && <Badge variant="outline" className="text-[10px] border-emerald-300 text-emerald-600">CV analysé</Badge>}
                {analysis.data_sources.passport && <Badge variant="outline" className="text-[10px] border-blue-300 text-blue-600">Passeport enrichi</Badge>}
              </div>
            )}
          </div>

          <div className="flex flex-col gap-3 md:border-l md:pl-6 border-slate-200">
            {analysis.skills_at_risk?.length > 0 && (
              <div>
                <p className="text-xs font-medium text-rose-600 mb-1 flex items-center gap-1">
                  <AlertTriangle className="w-3 h-3" />
                  Compétences à risque
                </p>
                <div className="flex flex-wrap gap-1">
                  {analysis.skills_at_risk.slice(0, 3).map((s, idx) => (
                    <Badge key={idx} className="bg-rose-100 text-rose-700">{s.skill}</Badge>
                  ))}
                </div>
              </div>
            )}

            {analysis.skills_in_demand?.length > 0 && (
              <div>
                <p className="text-xs font-medium text-emerald-600 mb-1 flex items-center gap-1">
                  <TrendingUp className="w-3 h-3" />
                  Compétences en demande
                </p>
                <div className="flex flex-wrap gap-1">
                  {analysis.skills_in_demand.slice(0, 3).map((s, idx) => (
                    <Badge key={idx} className="bg-emerald-100 text-emerald-700">{s.skill}</Badge>
                  ))}
                </div>
              </div>
            )}

            {analysis.recommended_skills_to_acquire?.length > 0 && (
              <div>
                <p className="text-xs font-medium text-blue-600 mb-1 flex items-center gap-1">
                  <Target className="w-3 h-3" />
                  À acquérir
                </p>
                <div className="flex flex-wrap gap-1">
                  {analysis.recommended_skills_to_acquire.slice(0, 3).map((s, idx) => (
                    <Badge key={idx} className="bg-blue-100 text-blue-700">{s}</Badge>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* CV Emerging competences section */}
        {analysis.emerging_from_cv?.length > 0 && (
          <div className="mt-4 pt-4 border-t border-slate-200">
            <p className="text-xs font-medium text-slate-700 mb-2 flex items-center gap-1">
              <Sparkles className="w-3 h-3 text-violet-500" />
              Compétences émergentes détectées dans votre CV
            </p>
            <div className="flex flex-wrap gap-2">
              {analysis.emerging_from_cv.slice(0, 5).map((ec, idx) => (
                <Badge key={idx} className="bg-violet-100 text-violet-700 border border-violet-200">
                  {ec.name} <span className="opacity-60 ml-1">({ec.score})</span>
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Recommended trainings */}
        {analysis.recommended_trainings?.length > 0 && (
          <div className="mt-3 pt-3 border-t border-slate-200">
            <p className="text-xs font-medium text-slate-700 mb-2 flex items-center gap-1">
              <BookOpen className="w-3 h-3 text-blue-500" />
              Formations recommandées
            </p>
            <div className="flex flex-wrap gap-2">
              {analysis.recommended_trainings.map((t, idx) => (
                <Badge key={idx} variant="outline" className="text-xs">{t}</Badge>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

const JobIndexCard = ({ job }) => {
  const index = job.evolution_index || 0;
  const levelKey = index < 20 ? "stable" : index < 50 ? "evolutif" : index < 80 ? "en_transformation" : "forte_mutation";
  const config = INDEX_LEVELS[levelKey];
  const Icon = config.icon;

  return (
    <div className="flex items-center gap-4 p-3 rounded-lg border border-slate-100 hover:border-blue-200 transition-all cursor-pointer">
      <div className={`w-12 h-12 rounded-lg ${config.bgColor} text-white flex items-center justify-center font-bold`}>
        {Math.round(index)}
      </div>
      <div className="flex-1 min-w-0">
        <h4 className="font-semibold text-slate-900 truncate">{job.job_name}</h4>
        <div className="flex items-center gap-2">
          <Badge className={`${config.bgLight} ${config.textColor} text-xs`}>
            <Icon className="w-3 h-3 mr-1" />
            {config.label}
          </Badge>
          <span className="text-xs text-slate-500">{job.sector}</span>
        </div>
      </div>
      <ChevronRight className="w-5 h-5 text-slate-400" />
    </div>
  );
};

const JobDetailCard = ({ job }) => {
  const index = job.evolution_index || 0;
  const levelKey = index < 20 ? "stable" : index < 50 ? "evolutif" : index < 80 ? "en_transformation" : "forte_mutation";
  const config = INDEX_LEVELS[levelKey];
  const Icon = config.icon;

  return (
    <Card className="card-interactive">
      <CardContent className="p-5">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div>
            <h3 className="font-semibold text-slate-900">{job.job_name}</h3>
            <p className="text-sm text-slate-500">{job.sector}</p>
          </div>
          <div className="text-right">
            <div className={`w-14 h-14 rounded-xl ${config.bgColor} text-white flex items-center justify-center font-bold text-xl`}>
              {Math.round(index)}
            </div>
          </div>
        </div>

        {/* Progress bar */}
        <div className="mb-4">
          <div className="flex items-center justify-between text-xs mb-1">
            <span className="text-slate-600">Indice d'évolution</span>
            <Badge className={`${config.bgLight} ${config.textColor}`}>
              <Icon className="w-3 h-3 mr-1" />
              {config.label}
            </Badge>
          </div>
          <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
            <div 
              className={`h-full ${config.bgColor} transition-all duration-500`}
              style={{ width: `${index}%` }}
            />
          </div>
        </div>

        {/* Skills sections */}
        <div className="space-y-3">
          {job.emerging_skills?.length > 0 && (
            <div>
              <p className="text-xs font-medium text-emerald-600 mb-1 flex items-center gap-1">
                <TrendingUp className="w-3 h-3" />
                Compétences émergentes
              </p>
              <div className="flex flex-wrap gap-1">
                {job.emerging_skills.slice(0, 4).map((skill, idx) => (
                  <Badge key={idx} className="bg-emerald-50 text-emerald-700 text-xs">{skill}</Badge>
                ))}
              </div>
            </div>
          )}
          
          {job.declining_skills?.length > 0 && (
            <div>
              <p className="text-xs font-medium text-rose-600 mb-1 flex items-center gap-1">
                <TrendingDown className="w-3 h-3" />
                En déclin
              </p>
              <div className="flex flex-wrap gap-1">
                {job.declining_skills.map((skill, idx) => (
                  <Badge key={idx} className="bg-rose-50 text-rose-700 text-xs">{skill}</Badge>
                ))}
              </div>
            </div>
          )}

          {job.recommended_skills?.length > 0 && (
            <div>
              <p className="text-xs font-medium text-blue-600 mb-1 flex items-center gap-1">
                <Target className="w-3 h-3" />
                À acquérir
              </p>
              <div className="flex flex-wrap gap-1">
                {job.recommended_skills.slice(0, 3).map((skill, idx) => (
                  <Badge key={idx} className="bg-blue-50 text-blue-700 text-xs">{skill}</Badge>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Passerelles */}
        {job.job_passerelles?.length > 0 && (
          <div className="mt-4 pt-3 border-t border-slate-100">
            <p className="text-xs text-slate-500 mb-2">Passerelles métiers :</p>
            <div className="flex flex-wrap gap-1">
              {job.job_passerelles.map((p, idx) => (
                <Badge key={idx} variant="outline" className="text-xs">{p}</Badge>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

const SectorIndexCard = ({ sector }) => {
  const index = sector.evolution_index || 0;
  const levelKey = index < 20 ? "stable" : index < 50 ? "evolutif" : index < 80 ? "en_transformation" : "forte_mutation";
  const config = INDEX_LEVELS[levelKey];
  const Icon = config.icon;

  return (
    <div className={`p-4 rounded-xl ${config.bgLight} border ${config.borderColor}`}>
      <div className="flex items-center justify-between mb-3">
        <h4 className="font-semibold text-slate-900">{sector.sector_name}</h4>
        <div className={`w-10 h-10 rounded-lg ${config.bgColor} text-white flex items-center justify-center font-bold`}>
          {Math.round(index)}
        </div>
      </div>
      <Badge className={`${config.bgLight} ${config.textColor} ${config.borderColor} border mb-2`}>
        <Icon className="w-3 h-3 mr-1" />
        {config.label}
      </Badge>
      <div className="mt-2 text-xs text-slate-600">
        <span>{sector.jobs_count} métiers • {sector.jobs_in_transformation} en transformation</span>
      </div>
    </div>
  );
};

const SectorDetailCard = ({ sector }) => {
  const index = sector.evolution_index || 0;
  const levelKey = index < 20 ? "stable" : index < 50 ? "evolutif" : index < 80 ? "en_transformation" : "forte_mutation";
  const config = INDEX_LEVELS[levelKey];
  const Icon = config.icon;

  return (
    <Card className="card-base">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Building2 className="w-5 h-5 text-[#1e3a5f]" />
              {sector.sector_name}
            </CardTitle>
            <CardDescription>
              {sector.jobs_count} métiers analysés
            </CardDescription>
          </div>
          <div className={`w-16 h-16 rounded-xl ${config.bgColor} text-white flex flex-col items-center justify-center`}>
            <span className="text-2xl font-bold">{Math.round(index)}</span>
            <span className="text-xs opacity-80">/ 100</span>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Progress */}
        <div>
          <div className="flex items-center justify-between text-sm mb-2">
            <Badge className={`${config.bgLight} ${config.textColor}`}>
              <Icon className="w-3 h-3 mr-1" />
              {config.label}
            </Badge>
            <span className="text-slate-500">
              Prévision 12 mois: {sector.predicted_evolution_12m}
            </span>
          </div>
          <Progress value={index} className="h-3" />
        </div>

        {/* Jobs distribution */}
        <div className="grid grid-cols-3 gap-2 text-center">
          <div className="p-2 bg-emerald-50 rounded-lg">
            <div className="text-lg font-bold text-emerald-700">{sector.jobs_stable}</div>
            <div className="text-xs text-emerald-600">Stables</div>
          </div>
          <div className="p-2 bg-amber-50 rounded-lg">
            <div className="text-lg font-bold text-amber-700">{sector.jobs_in_transformation}</div>
            <div className="text-xs text-amber-600">En transfo.</div>
          </div>
          <div className="p-2 bg-blue-50 rounded-lg">
            <div className="text-lg font-bold text-blue-700">{sector.jobs_emerging}</div>
            <div className="text-xs text-blue-600">Émergents</div>
          </div>
        </div>

        {/* Top skills */}
        {sector.top_emerging_skills?.length > 0 && (
          <div>
            <p className="text-xs font-medium text-slate-700 mb-2">Top compétences émergentes</p>
            <div className="space-y-1">
              {sector.top_emerging_skills.map((skill, idx) => (
                <div key={idx} className="flex items-center justify-between text-sm">
                  <span className="text-slate-600">{skill.skill}</span>
                  <Badge className="bg-emerald-100 text-emerald-700">{skill.growth}</Badge>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Skill gaps */}
        {sector.skill_gap_areas?.length > 0 && (
          <div className="p-3 bg-amber-50 rounded-lg border border-amber-200">
            <p className="text-xs font-medium text-amber-700 mb-1 flex items-center gap-1">
              <AlertTriangle className="w-3 h-3" />
              Zones de tension compétences
            </p>
            <div className="flex flex-wrap gap-1">
              {sector.skill_gap_areas.map((area, idx) => (
                <Badge key={idx} className="bg-amber-100 text-amber-700 text-xs">{area}</Badge>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default EvolutionIndexView;
