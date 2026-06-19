import { useState, useEffect } from "react";
import { API } from "@/App";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Gauge, TrendingUp, TrendingDown, Building2, Briefcase,
  Target, AlertTriangle, CheckCircle2, ChevronRight,
  Sparkles, BookOpen, Zap, Info, RefreshCw
} from "lucide-react";

const INDEX_LEVELS = {
  stable: { label: "Très stable", range: "0-20", bgColor: "bg-emerald-500", textColor: "text-emerald-700", bgLight: "bg-emerald-50", borderColor: "border-emerald-200", icon: CheckCircle2 },
  evolutif: { label: "Évolutif", range: "20-50", bgColor: "bg-blue-500", textColor: "text-blue-700", bgLight: "bg-blue-50", borderColor: "border-blue-200", icon: TrendingUp },
  en_transformation: { label: "En transformation", range: "50-80", bgColor: "bg-amber-500", textColor: "text-amber-700", bgLight: "bg-amber-50", borderColor: "border-amber-200", icon: Zap },
  forte_mutation: { label: "Forte mutation", range: "80-100", bgColor: "bg-rose-500", textColor: "text-rose-700", bgLight: "bg-rose-50", borderColor: "border-rose-200", icon: AlertTriangle },
};

const getLevel = (index) => index < 20 ? "stable" : index < 50 ? "evolutif" : index < 80 ? "en_transformation" : "forte_mutation";

const EvolutionIndexView = ({ token, embedded }) => {
  const [dashboard, setDashboard] = useState(null);
  const [userAnalysis, setUserAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      setLoading(true);
      try {
        const [dashRes, userRes] = await Promise.all([
          fetch(`${API}/evolution-index/dashboard`).then(r => r.ok ? r.json() : null),
          token ? fetch(`${API}/evolution-index/user-profile?token=${token}`).then(r => r.ok ? r.json() : null) : Promise.resolve(null)
        ]);
        if (!cancelled) {
          if (dashRes) setDashboard(dashRes);
          if (userRes) setUserAnalysis(userRes);
          setLoading(false);
        }
      } catch { if (!cancelled) setLoading(false); }
    };
    load();
    return () => { cancelled = true; };
  }, [token]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-48 gap-3">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-[#1e3a5f]" />
        <p className="text-sm text-slate-500">Analyse en cours...</p>
      </div>
    );
  }

  const { sectors = [], top_transforming_jobs = [], most_stable_jobs = [] } = dashboard || {};
  const hasUserData = userAnalysis && (userAnalysis.relevant_jobs?.length > 0 || userAnalysis.has_cv);

  const personalTopTransforming = hasUserData && userAnalysis.relevant_jobs?.length > 0
    ? [...userAnalysis.relevant_jobs].sort((a, b) => (b.evolution_index || 0) - (a.evolution_index || 0))
    : top_transforming_jobs;
  const personalMostStable = hasUserData && userAnalysis.relevant_jobs?.length > 0
    ? [...userAnalysis.relevant_jobs].sort((a, b) => (a.evolution_index || 0) - (b.evolution_index || 0))
    : most_stable_jobs;

  return (
    <div className="space-y-5 animate-fade-in" data-testid="evolution-index-view">
      {/* Exposition Card */}
      {userAnalysis && <ExposureCard analysis={userAnalysis} />}

      {/* Tabs: Vue d'ensemble, Par secteur, Guide */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid grid-cols-3 gap-1 h-auto p-1 bg-slate-100">
          <TabsTrigger value="overview" className="text-xs sm:text-sm py-2">
            <Gauge className="w-4 h-4 mr-1 hidden sm:inline" /> Vue d'ensemble
          </TabsTrigger>
          <TabsTrigger value="sectors" className="text-xs sm:text-sm py-2">
            <Building2 className="w-4 h-4 mr-1 hidden sm:inline" /> Par secteur
          </TabsTrigger>
          <TabsTrigger value="guide" className="text-xs sm:text-sm py-2">
            <Info className="w-4 h-4 mr-1 hidden sm:inline" /> Guide
          </TabsTrigger>
        </TabsList>

        {/* Overview */}
        <TabsContent value="overview" className="space-y-5">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            {/* Métiers en mutation */}
            <Card className="card-base">
              <CardHeader className="pb-3">
                <CardTitle className="text-base flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-rose-600" />
                  {hasUserData ? "Métiers en mutation (votre profil)" : "Métiers en forte mutation"}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {personalTopTransforming.slice(0, 5).map((job, idx) => (
                    <JobRow key={idx} job={job} />
                  ))}
                  {personalTopTransforming.length === 0 && <p className="text-sm text-slate-400 py-4 text-center">Aucun métier détecté</p>}
                </div>
              </CardContent>
            </Card>

            {/* Métiers stables */}
            <Card className="card-base">
              <CardHeader className="pb-3">
                <CardTitle className="text-base flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  {hasUserData ? "Métiers les plus stables (votre profil)" : "Métiers les plus stables"}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {personalMostStable.slice(0, 5).map((job, idx) => (
                    <JobRow key={idx} job={job} />
                  ))}
                  {personalMostStable.length === 0 && <p className="text-sm text-slate-400 py-4 text-center">Aucun métier détecté</p>}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Secteurs overview */}
          {sectors.length > 0 && (
            <Card className="card-base">
              <CardHeader className="pb-3">
                <CardTitle className="text-base flex items-center gap-2">
                  <Building2 className="w-4 h-4 text-[#1e3a5f]" /> Aperçu par secteur
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {sectors.slice(0, 8).map((s, idx) => {
                    const lvl = INDEX_LEVELS[getLevel(s.evolution_index || 0)];
                    return (
                      <div key={idx} className={`p-3 rounded-xl ${lvl.bgLight} border ${lvl.borderColor}`}>
                        <p className="font-medium text-sm text-slate-900 truncate">{s.sector_name}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <span className={`text-lg font-bold ${lvl.textColor}`}>{Math.round(s.evolution_index || 0)}</span>
                          <Badge className={`${lvl.bgLight} ${lvl.textColor} text-[10px]`}>{lvl.label}</Badge>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Sectors Tab */}
        <TabsContent value="sectors" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            {sectors.map((sector, idx) => {
              const lvl = INDEX_LEVELS[getLevel(sector.evolution_index || 0)];
              const Icon = lvl.icon;
              return (
                <Card key={idx} className="card-base">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div>
                        <CardTitle className="text-base">{sector.sector_name}</CardTitle>
                        <CardDescription>{sector.jobs_count} métiers analysés</CardDescription>
                      </div>
                      <div className={`w-12 h-12 rounded-xl ${lvl.bgColor} text-white flex items-center justify-center font-bold text-lg`}>
                        {Math.round(sector.evolution_index || 0)}
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex items-center justify-between text-xs mb-1">
                      <Badge className={`${lvl.bgLight} ${lvl.textColor}`}><Icon className="w-3 h-3 mr-1" />{lvl.label}</Badge>
                      {sector.predicted_evolution_12m && <span className="text-slate-500">Prévision: {sector.predicted_evolution_12m}</span>}
                    </div>
                    <Progress value={sector.evolution_index || 0} className="h-2" />
                    <div className="grid grid-cols-3 gap-2 text-center text-xs">
                      <div className="p-2 bg-emerald-50 rounded-lg">
                        <span className="font-bold text-emerald-700">{sector.jobs_stable || 0}</span> <span className="text-emerald-600">stables</span>
                      </div>
                      <div className="p-2 bg-amber-50 rounded-lg">
                        <span className="font-bold text-amber-700">{sector.jobs_in_transformation || 0}</span> <span className="text-amber-600">en transfo.</span>
                      </div>
                      <div className="p-2 bg-blue-50 rounded-lg">
                        <span className="font-bold text-blue-700">{sector.jobs_emerging || 0}</span> <span className="text-blue-600">émergents</span>
                      </div>
                    </div>
                    {sector.top_emerging_skills?.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {sector.top_emerging_skills.slice(0, 4).map((sk, j) => (
                          <Badge key={j} className="bg-emerald-50 text-emerald-700 text-[10px]">{sk.skill || sk}</Badge>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>

        {/* Guide */}
        <TabsContent value="guide">
          <Card className="card-base">
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Info className="w-4 h-4 text-[#1e3a5f]" /> Comprendre l'indice d'évolution
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-slate-600">
                L'indice mesure la vitesse à laquelle les compétences d'un métier ou d'un secteur se transforment.
              </p>
              <div className="space-y-2">
                {Object.entries(INDEX_LEVELS).map(([key, config]) => {
                  const Icon = config.icon;
                  return (
                    <div key={key} className={`flex items-center gap-3 p-3 rounded-lg ${config.bgLight} border ${config.borderColor}`}>
                      <div className={`w-10 h-10 rounded-lg ${config.bgColor} text-white flex items-center justify-center shrink-0`}>
                        <Icon className="w-5 h-5" />
                      </div>
                      <div>
                        <span className={`font-semibold ${config.textColor}`}>{config.label}</span>
                        <span className="text-xs text-slate-500 ml-2">({config.range})</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

/* ── Exposure Card (simplified) ── */
const ExposureCard = ({ analysis }) => {
  const exposure = analysis.evolution_exposure || 0;
  const interp = analysis.exposure_interpretation || {};
  const lvl = INDEX_LEVELS[interp.level] || INDEX_LEVELS.evolutif;
  const Icon = lvl.icon;

  return (
    <Card className={`${lvl.bgLight} border ${lvl.borderColor}`} data-testid="evolution-exposure-card">
      <CardContent className="p-5">
        <div className="flex flex-col md:flex-row md:items-center gap-5">
          {/* Score */}
          <div className="flex items-center gap-3 shrink-0">
            <div className={`w-14 h-14 rounded-xl ${lvl.bgColor} text-white flex items-center justify-center`}>
              <Gauge className="w-7 h-7" />
            </div>
            <div>
              <p className="text-xs text-slate-600">Votre exposition aux transformations</p>
              <div className="flex items-baseline gap-1">
                <span className="text-3xl font-bold text-slate-900">{exposure}</span>
                <span className="text-slate-400 text-sm">/100</span>
              </div>
              <Badge className={`${lvl.bgLight} ${lvl.textColor} ${lvl.borderColor} border text-xs`}>
                <Icon className="w-3 h-3 mr-1" />{lvl.label}
              </Badge>
            </div>
          </div>

          {/* Interpretation */}
          <div className="flex-1 md:border-l md:pl-5 border-slate-200/60">
            <p className="text-sm text-slate-700">{interp.description}</p>
            {interp.recommendation && <p className="text-sm font-medium text-slate-900 mt-1">{interp.recommendation}</p>}
          </div>

          {/* Skills badges */}
          <div className="flex flex-col gap-2 md:border-l md:pl-5 border-slate-200/60 shrink-0">
            {analysis.recommended_skills_to_acquire?.length > 0 && (
              <div>
                <p className="text-[10px] font-medium text-blue-600 mb-1 flex items-center gap-1"><Target className="w-3 h-3" />À acquérir</p>
                <div className="flex flex-wrap gap-1">
                  {analysis.recommended_skills_to_acquire.slice(0, 3).map((s, i) => (
                    <Badge key={i} className="bg-blue-100 text-blue-700 text-[10px]">{s}</Badge>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Trainings */}
        {analysis.recommended_trainings?.length > 0 && (
          <div className="mt-3 pt-3 border-t border-slate-200/60 flex items-center gap-2 flex-wrap">
            <BookOpen className="w-3.5 h-3.5 text-blue-500 shrink-0" />
            <span className="text-[10px] font-medium text-slate-600">Formations :</span>
            {analysis.recommended_trainings.slice(0, 5).map((t, i) => (
              <Badge key={i} variant="outline" className="text-[10px]">{t}</Badge>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

/* ── Job Row (compact) ── */
const JobRow = ({ job }) => {
  const index = job.evolution_index || 0;
  const lvl = INDEX_LEVELS[getLevel(index)];

  return (
    <div className="flex items-center gap-3 p-2.5 rounded-lg border border-slate-100 hover:border-blue-200 transition-all">
      <div className={`w-10 h-10 rounded-lg ${lvl.bgColor} text-white flex items-center justify-center font-bold text-sm shrink-0`}>
        {Math.round(index)}
      </div>
      <div className="flex-1 min-w-0">
        <p className="font-medium text-sm text-slate-900 truncate">{job.job_name}</p>
        <p className="text-[11px] text-slate-500">{job.sector}</p>
      </div>
      <Badge className={`${lvl.bgLight} ${lvl.textColor} text-[10px] shrink-0`}>{lvl.label}</Badge>
    </div>
  );
};

export default EvolutionIndexView;
