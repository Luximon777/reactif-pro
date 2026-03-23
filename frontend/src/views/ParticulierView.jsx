import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Input } from "@/components/ui/input";
import {
  User, Target, TrendingUp, BookOpen, Briefcase, MapPin, Clock, Euro,
  Star, ChevronRight, Plus, Sparkles, Zap, Award, CheckCircle2, AlertCircle,
  Play, FolderLock, FileDown, FileText, LayoutList, Layers, Shield, BarChart3
} from "lucide-react";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";
import CvAnalysisSection from "@/components/CvAnalysis/CvAnalysisSection";

const ParticulierView = ({ token, section }) => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [learningModules, setLearningModules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingProfile, setEditingProfile] = useState(false);
  const [newSkill, setNewSkill] = useState("");

  useEffect(() => {
    loadData();
  }, [token]);

  const loadData = async (silent = false) => {
    if (!silent) setLoading(true);
    try {
      const [profileRes, jobsRes, learningRes] = await Promise.all([
        axios.get(`${API}/profile?token=${token}`),
        axios.get(`${API}/jobs?token=${token}`),
        axios.get(`${API}/learning?token=${token}`)
      ]);
      setProfile(profileRes.data);
      setJobs(jobsRes.data);
      setLearningModules(learningRes.data);
    } catch (error) {
      console.error("Error loading data:", error);
      if (!silent) toast.error("Erreur lors du chargement des données");
    }
    if (!silent) setLoading(false);
  };

  const addSkill = async () => {
    if (!newSkill.trim()) return;
    const updatedSkills = [...(profile?.skills || []), { name: newSkill, level: 50 }];
    try {
      const response = await axios.put(`${API}/profile?token=${token}`, { skills: updatedSkills });
      setProfile(response.data);
      setNewSkill("");
      setEditingProfile(false);
      toast.success("Compétence ajoutée !");
      loadData();
    } catch (error) {
      toast.error("Erreur lors de l'ajout");
    }
  };

  const updateLearningProgress = async (moduleId, newProgress) => {
    try {
      await axios.post(`${API}/learning/${moduleId}/progress?token=${token}&progress=${newProgress}`);
      setLearningModules(prev => prev.map(m =>
        m.id === moduleId ? { ...m, progress: newProgress } : m
      ));
      toast.success("Progression mise à jour !");
    } catch (error) {
      toast.error("Erreur lors de la mise à jour");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const displayProfile = profile || {
    name: "Utilisateur",
    profile_score: 45,
    skills: [
      { name: "Communication", level: 75 },
      { name: "Organisation", level: 68 },
      { name: "Excel", level: 55 }
    ],
    strengths: ["Adaptabilité", "Travail d'équipe", "Rigueur"],
    gaps: ["Gestion de projet", "Langues étrangères"],
    sectors: ["Administration", "Commerce"]
  };

  const metrics = [
    { title: "Identité Professionnelle", value: `${displayProfile.profile_score || 45}%`, icon: Target, color: "blue", subtitle: "Complétude de votre profil" },
    { title: "Job Matching", value: jobs.filter(j => j.match_score >= 60).length.toString(), icon: Briefcase, color: "emerald", subtitle: "Offres compatibles" },
    { title: "Parcours Formation", value: learningModules.filter(m => m.progress > 0 && m.progress < 100).length.toString(), icon: BookOpen, color: "amber", subtitle: "Modules en cours" },
    { title: "Compétences Valorisées", value: displayProfile.skills?.length?.toString() || "0", icon: Zap, color: "violet", subtitle: "Dans votre coffre-fort" }
  ];

  if (section === "jobs") return <JobsSection jobs={jobs} token={token} />;
  if (section === "learning") return <LearningSection modules={learningModules} updateProgress={updateLearningProgress} token={token} />;

  return (
    <div className="space-y-8 animate-fade-in" data-testid="particulier-dashboard">
      {/* Welcome Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>
            Mon Espace Personnel
          </h1>
          <p className="text-slate-600 mt-1">Coffre-fort numérique de vos compétences</p>
        </div>
        <Badge className="self-start bg-blue-100 text-[#1e3a5f] border-blue-200 px-3 py-1">
          <Sparkles className="w-3 h-3 mr-1" />
          Tiers de confiance numérique
        </Badge>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4" data-testid="metrics-grid">
        {metrics.map((metric, idx) => {
          const Icon = metric.icon;
          const colorClasses = { blue: "bg-blue-100 text-blue-600", emerald: "bg-emerald-100 text-emerald-600", amber: "bg-amber-100 text-amber-600", violet: "bg-violet-100 text-violet-600" };
          return (
            <Card key={idx} className="card-metric card-hover" data-testid={`metric-${metric.title.toLowerCase().replace(/\s/g, '-')}`}>
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-500 mb-1">{metric.title}</p>
                    <p className="text-3xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>{metric.value}</p>
                    <p className="text-xs text-slate-400 mt-1">{metric.subtitle}</p>
                  </div>
                  <div className={`w-12 h-12 rounded-xl ${colorClasses[metric.color]} flex items-center justify-center`}>
                    <Icon className="w-6 h-6" />
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2 card-base" data-testid="skills-section">
          <CardHeader>
            <div>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-[#1e3a5f]" />Mes CV
              </CardTitle>
              <CardDescription>Re'Actif Pro IA audite, optimise et adapte votre CV pour passer les filtres ATS</CardDescription>
            </div>
          </CardHeader>
          <CardContent>
            <CvAnalysisSection token={token} onComplete={() => loadData(true)} />
            <div className="space-y-4 mt-6">
              <h4 className="text-sm font-semibold text-slate-700">Compétences identifiées</h4>
              {displayProfile.skills?.length > 0 ? (
                displayProfile.skills.map((skill, idx) => (
                  <div key={idx} className="space-y-2" data-testid={`skill-${idx}`}>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-slate-700">{skill.name}</span>
                      <span className="text-sm text-slate-500">{skill.level}%</span>
                    </div>
                    <Progress value={skill.level} className="h-2" />
                  </div>
                ))
              ) : (
                <div className="text-center py-4 text-slate-400 text-sm">
                  <p>Chargez un CV pour identifier vos compétences automatiquement</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        <div className="space-y-6">
          <Card className="card-base" data-testid="strengths-section">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <CheckCircle2 className="w-5 h-5 text-green-600" />Compétences Transversales
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {(displayProfile.strengths || ["Adaptabilité", "Travail d'équipe"]).map((strength, idx) => (
                  <Badge key={idx} className="badge-success">{strength}</Badge>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card className="card-base" data-testid="gaps-section">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <AlertCircle className="w-5 h-5 text-amber-600" />Besoins en Formation
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {(displayProfile.gaps || ["Gestion de projet", "Langues"]).map((gap, idx) => (
                  <Badge key={idx} className="badge-warning">{gap}</Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Coffre-Fort Banner */}
      <Card className="bg-gradient-to-r from-[#1e3a5f] to-[#2d4a6f] border-0" data-testid="coffre-fort-banner">
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-xl bg-white/20 flex items-center justify-center">
                <FolderLock className="w-7 h-7 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white">Coffre-Fort Professionnel</h3>
                <p className="text-blue-100 text-sm">Conservez et valorisez vos documents : diplômes, expériences, preuves de compétences</p>
              </div>
            </div>
            <Button className="bg-white text-[#1e3a5f] hover:bg-blue-50 font-semibold" onClick={() => navigate('/dashboard/coffre-fort')} data-testid="goto-coffre-fort-btn">
              <FolderLock className="w-4 h-4 mr-2" />Accéder au coffre-fort
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Jobs Preview */}
      <Card className="card-base" data-testid="jobs-preview">
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2"><Briefcase className="w-5 h-5 text-[#1e3a5f]" />Job Matching</CardTitle>
            <CardDescription>Métiers compatibles avec vos compétences transférables</CardDescription>
          </div>
          <Button variant="outline" size="sm" onClick={() => window.location.href = '/dashboard/jobs'}>
            Voir tout<ChevronRight className="w-4 h-4 ml-1" />
          </Button>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {jobs.slice(0, 3).map((job, idx) => <JobCard key={idx} job={job} />)}
          </div>
        </CardContent>
      </Card>

      {/* Learning Preview */}
      <Card className="card-base" data-testid="learning-preview">
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2"><BookOpen className="w-5 h-5 text-[#1e3a5f]" />Parcours de Formation</CardTitle>
            <CardDescription>Pour développer vos compétences et sécuriser votre trajectoire</CardDescription>
          </div>
          <Button variant="outline" size="sm" onClick={() => window.location.href = '/dashboard/learning'}>
            Voir tout<ChevronRight className="w-4 h-4 ml-1" />
          </Button>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {learningModules.slice(0, 3).map((module, idx) => <LearningCard key={idx} module={module} onUpdateProgress={updateLearningProgress} />)}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

const JobCard = ({ job }) => {
  const matchColor = job.match_score >= 80 ? "text-green-600 bg-green-50" : job.match_score >= 60 ? "text-blue-600 bg-blue-50" : "text-amber-600 bg-amber-50";
  return (
    <Card className="card-interactive group" data-testid={`job-card-${job.id}`}>
      <CardContent className="p-5">
        <div className="flex items-start justify-between mb-3">
          <div className={`px-2 py-1 rounded-lg text-sm font-semibold ${matchColor}`}>{job.match_score}% match</div>
          <Badge variant="outline" className="text-xs">{job.contract_type}</Badge>
        </div>
        <h3 className="font-semibold text-slate-900 mb-1 group-hover:text-blue-600 transition-colors">{job.title}</h3>
        <p className="text-sm text-slate-600 mb-3">{job.company}</p>
        <div className="space-y-1 text-xs text-slate-500">
          <div className="flex items-center gap-1"><MapPin className="w-3 h-3" />{job.location}</div>
          {job.salary_range && <div className="flex items-center gap-1"><Euro className="w-3 h-3" />{job.salary_range}</div>}
        </div>
        <div className="flex flex-wrap gap-1 mt-3">
          {job.required_skills?.slice(0, 3).map((skill, idx) => <Badge key={idx} variant="secondary" className="text-xs">{skill}</Badge>)}
        </div>
      </CardContent>
    </Card>
  );
};

const LearningCard = ({ module, onUpdateProgress }) => (
  <Card className={`card-interactive group overflow-hidden ${module.relevance === "haute" ? "ring-2 ring-amber-300" : ""}`} data-testid={`learning-card-${module.id}`}>
    {module.image_url && (
      <div className="h-32 overflow-hidden">
        <img src={module.image_url} alt={module.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
      </div>
    )}
    <CardContent className="p-5">
      <div className="flex items-center justify-between mb-2">
        <Badge variant="secondary" className="text-xs">{module.category}</Badge>
        {module.relevance === "haute" && (
          <Badge className="bg-amber-100 text-amber-700 text-[10px]" data-testid="relevance-badge-high">
            <Target className="w-3 h-3 mr-0.5" />
            Recommandé pour vous
          </Badge>
        )}
      </div>
      <h3 className="font-semibold text-slate-900 mb-1 group-hover:text-blue-600 transition-colors">{module.title}</h3>
      <p className="text-xs text-slate-500 mb-3 line-clamp-2">{module.description}</p>
      {module.gaps_addressed?.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-2">
          {module.gaps_addressed.map((gap, i) => (
            <Badge key={i} className="text-[10px] bg-amber-50 text-amber-600 border border-amber-200">Comble : {gap}</Badge>
          ))}
        </div>
      )}
      <div className="flex items-center justify-between text-xs text-slate-500 mb-3">
        <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{module.duration}</span>
        <Badge variant="outline">{module.level}</Badge>
      </div>
      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs">
          <span className="text-slate-600">Progression</span>
          <span className="font-medium text-slate-900">{module.progress}%</span>
        </div>
        <Progress value={module.progress} className="h-2" />
      </div>
      {module.progress < 100 && (
        <Button variant="outline" size="sm" className="w-full mt-3 group-hover:bg-blue-50 group-hover:text-blue-600" onClick={() => onUpdateProgress(module.id, Math.min(100, module.progress + 25))}>
          <Play className="w-3 h-3 mr-1" />{module.progress === 0 ? "Commencer" : "Continuer"}
        </Button>
      )}
      {module.progress === 100 && (
        <Badge className="w-full mt-3 justify-center badge-success"><Award className="w-3 h-3 mr-1" />Terminé</Badge>
      )}
    </CardContent>
  </Card>
);

const JobsSection = ({ jobs, token }) => {
  const [matching, setMatching] = useState(null);
  const [loadingMatch, setLoadingMatch] = useState(false);

  useEffect(() => {
    const loadMatching = async () => {
      setLoadingMatch(true);
      try {
        const res = await axios.get(`${API}/jobs/matching?token=${token}`);
        setMatching(res.data);
      } catch (e) { console.error("Job matching error:", e); }
      setLoadingMatch(false);
    };
    if (token) loadMatching();
  }, [token]);

  const getScoreColor = (score) => {
    if (score >= 80) return { bg: "bg-emerald-100", text: "text-emerald-700", ring: "ring-emerald-200", bar: "bg-emerald-500" };
    if (score >= 60) return { bg: "bg-blue-100", text: "text-blue-700", ring: "ring-blue-200", bar: "bg-blue-500" };
    if (score >= 40) return { bg: "bg-amber-100", text: "text-amber-700", ring: "ring-amber-200", bar: "bg-amber-500" };
    return { bg: "bg-slate-100", text: "text-slate-600", ring: "ring-slate-200", bar: "bg-slate-400" };
  };

  return (
    <div className="space-y-6 animate-fade-in" data-testid="jobs-section">
      <div>
        <h1 className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>Job Matching</h1>
        <p className="text-slate-600 mt-1">Offres d'emploi sélectionnées par l'IA selon votre profil et votre CV</p>
      </div>

      {loadingMatch && (
        <div className="flex items-center gap-3 p-6 bg-blue-50 rounded-xl border border-blue-100">
          <div className="w-6 h-6 border-2 border-blue-300 border-t-blue-600 rounded-full animate-spin" />
          <span className="text-sm text-blue-700">Analyse de votre profil et recherche d'offres compatibles...</span>
        </div>
      )}

      {!loadingMatch && matching && !matching.has_data && (
        <Card className="border-dashed border-2 border-slate-200 bg-slate-50/50">
          <CardContent className="p-6 text-center">
            <Target className="w-10 h-10 text-slate-300 mx-auto mb-3" />
            <h3 className="font-semibold text-slate-700">Analysez votre CV pour activer le Job Matching</h3>
            <p className="text-sm text-slate-500 mt-1">L'IA sélectionnera des offres d'emploi pertinentes selon votre profil</p>
          </CardContent>
        </Card>
      )}

      {!loadingMatch && matching?.has_data && matching.profile_summary && (
        <Card className="bg-gradient-to-r from-[#1e3a5f] to-[#2d5a8f] border-0" data-testid="matching-profile-banner">
          <CardContent className="p-4">
            <div className="flex flex-col sm:flex-row sm:items-center gap-3">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-white/20 flex items-center justify-center">
                  <Target className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-white">{matching.profile_summary.titre || "Profil analysé"}</h4>
                  <p className="text-[11px] text-blue-100">{matching.profile_summary.skills_count} compétences analysées</p>
                </div>
              </div>
              <div className="flex gap-2 sm:ml-auto">
                {matching.profile_summary.has_optimized_cv && <Badge className="bg-white/15 text-white text-[10px]">CV optimisé</Badge>}
                {matching.profile_summary.has_career_project && <Badge className="bg-white/15 text-white text-[10px]">Projet pro défini</Badge>}
                <Badge className="bg-emerald-400/20 text-emerald-200 text-[10px]">{matching.matches?.length || 0} offres trouvées</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {!loadingMatch && matching?.matches?.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {matching.matches.map((match, idx) => {
            const sc = getScoreColor(match.matching_score);
            return (
              <Card key={idx} className={`card-interactive group ${match.matching_score >= 80 ? "ring-2 " + sc.ring : ""}`} data-testid={`job-match-card-${idx}`}>
                <CardContent className="p-5">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-slate-900 group-hover:text-blue-600 transition-colors">{match.titre}</h3>
                      <div className="flex items-center gap-2 mt-1 flex-wrap">
                        {match.entreprise_type && <span className="text-xs text-slate-500">{match.entreprise_type}</span>}
                        <Badge variant="outline" className="text-[10px]">{match.type_contrat}</Badge>
                        <span className="text-xs text-slate-400">{match.secteur}</span>
                      </div>
                    </div>
                    <div className={`flex flex-col items-center ml-3 px-3 py-2 rounded-xl ${sc.bg}`} data-testid="matching-score">
                      <span className={`text-2xl font-bold ${sc.text}`}>{match.matching_score}%</span>
                      <span className={`text-[10px] ${sc.text}`}>match</span>
                    </div>
                  </div>

                  <p className="text-xs text-slate-600 mb-3">{match.description}</p>

                  {/* Matching bar */}
                  <div className="mb-3">
                    <div className="h-2 rounded-full bg-slate-100 overflow-hidden">
                      <div className={`h-full rounded-full ${sc.bar} transition-all duration-500`} style={{ width: `${match.matching_score}%` }} />
                    </div>
                  </div>

                  {match.pourquoi_ce_match && (
                    <div className="p-2 bg-blue-50 rounded-lg mb-3 border border-blue-100">
                      <p className="text-[11px] text-blue-700"><Sparkles className="w-3 h-3 inline mr-1" />{match.pourquoi_ce_match}</p>
                    </div>
                  )}

                  <div className="flex flex-wrap gap-1 mb-2">
                    {(match.competences_matchees || []).slice(0, 4).map((c, i) => (
                      <Badge key={i} className="text-[10px] bg-emerald-50 text-emerald-700 border border-emerald-200">{c}</Badge>
                    ))}
                  </div>

                  <div className="flex items-center justify-between text-[10px] text-slate-400 mt-2">
                    {match.localisation && <span>{match.localisation}</span>}
                    {match.salaire_indicatif && <span className="font-medium text-slate-600">{match.salaire_indicatif}</span>}
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

const LearningSection = ({ modules, updateProgress, token }) => {
  const [recommendations, setRecommendations] = useState([]);
  const [loadingRecs, setLoadingRecs] = useState(false);

  useEffect(() => {
    const loadRecs = async () => {
      setLoadingRecs(true);
      try {
        const res = await axios.get(`${API}/learning/recommendations?token=${token}`);
        if (res.data.has_data) setRecommendations(res.data.recommendations || []);
      } catch (e) { console.error("Recs error:", e); }
      setLoadingRecs(false);
    };
    if (token) loadRecs();
  }, [token]);

  const priorityConfig = {
    haute: { color: "bg-rose-100 text-rose-700 border-rose-200", label: "Prioritaire" },
    moyenne: { color: "bg-amber-100 text-amber-700 border-amber-200", label: "Recommandée" },
    basse: { color: "bg-slate-100 text-slate-600 border-slate-200", label: "Optionnelle" },
  };

  const typeConfig = {
    certifiante: { color: "bg-blue-100 text-blue-700", label: "Certifiante" },
    courte: { color: "bg-emerald-100 text-emerald-700", label: "Formation courte" },
    mooc: { color: "bg-violet-100 text-violet-700", label: "MOOC" },
    diplome: { color: "bg-amber-100 text-amber-700", label: "Diplôme" },
  };

  return (
    <div className="space-y-6 animate-fade-in" data-testid="learning-section">
      <div>
        <h1 className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>Parcours de Formation</h1>
        <p className="text-slate-600 mt-1">Développez vos compétences et sécurisez votre trajectoire professionnelle</p>
      </div>

      {/* AI Recommendations */}
      {(recommendations.length > 0 || loadingRecs) && (
        <div data-testid="ai-recommendations-section">
          <div className="flex items-center gap-2 mb-4">
            <Sparkles className="w-5 h-5 text-violet-600" />
            <h2 className="text-lg font-semibold text-slate-900">Formations recommandées pour votre profil</h2>
          </div>
          {loadingRecs ? (
            <div className="flex items-center gap-3 p-4 bg-violet-50 rounded-xl border border-violet-100">
              <div className="w-5 h-5 border-2 border-violet-300 border-t-violet-600 rounded-full animate-spin" />
              <span className="text-sm text-violet-700">Analyse de votre profil en cours...</span>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {recommendations.map((rec, idx) => {
                const pConf = priorityConfig[rec.priority] || priorityConfig.moyenne;
                const tConf = typeConfig[rec.type] || typeConfig.courte;
                return (
                  <Card key={idx} className={`card-interactive group ${rec.priority === "haute" ? "ring-2 ring-violet-200" : ""}`} data-testid={`rec-card-${idx}`}>
                    <CardContent className="p-5">
                      <div className="flex items-center justify-between mb-2 flex-wrap gap-1">
                        <Badge className={`text-[10px] border ${pConf.color}`}>{pConf.label}</Badge>
                        <Badge className={`text-[10px] ${tConf.color}`}>{tConf.label}</Badge>
                      </div>
                      <h3 className="font-semibold text-slate-900 text-sm mb-1 group-hover:text-violet-600 transition-colors">{rec.title}</h3>
                      <p className="text-xs text-slate-500 mb-2">{rec.provider} {rec.duration && <span>- {rec.duration}</span>}</p>
                      <p className="text-xs text-slate-600 mb-3 line-clamp-2">{rec.description}</p>
                      {rec.relevance_reason && (
                        <div className="p-2 bg-violet-50 rounded-lg mb-3 border border-violet-100">
                          <p className="text-[11px] text-violet-700"><Sparkles className="w-3 h-3 inline mr-1" />{rec.relevance_reason}</p>
                        </div>
                      )}
                      <div className="flex flex-wrap gap-1 mb-2">
                        {rec.skills_developed?.slice(0, 3).map((s, i) => (
                          <Badge key={i} variant="outline" className="text-[10px]">{s}</Badge>
                        ))}
                      </div>
                      <div className="flex items-center justify-between text-[10px] text-slate-400 mt-2">
                        <span>{rec.level === "debutant" ? "Débutant" : rec.level === "intermediaire" ? "Intermédiaire" : "Avancé"}</span>
                        {rec.cpf_eligible && <Badge className="bg-emerald-50 text-emerald-600 text-[10px]">Éligible CPF</Badge>}
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Static modules */}
      {modules.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-4">
            <BookOpen className="w-5 h-5 text-[#1e3a5f]" />
            <h2 className="text-lg font-semibold text-slate-900">Modules de formation</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 stagger-children">
            {modules.map((module, idx) => <LearningCard key={idx} module={module} onUpdateProgress={updateProgress} />)}
          </div>
        </div>
      )}
    </div>
  );
};

export default ParticulierView;
