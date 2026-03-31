import React, { useState, useEffect, useMemo } from "react";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Input } from "@/components/ui/input";
import {
  User, Target, TrendingUp, BookOpen, Briefcase, MapPin, Clock, Euro,
  Star, ChevronRight, Plus, Sparkles, Zap, Award, AlertCircle,
  Play, FolderLock, FileDown, FileText, LayoutList, Layers, Shield, BarChart3,
  ExternalLink, Upload, CheckCircle, Bell, CheckCircle2, Loader2
} from "lucide-react";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";
import CvAnalysisSection from "@/components/CvAnalysis/CvAnalysisSection";
import JobMatchingSection from "@/components/JobMatchingSection";

// ===== D'CLIC PRO BOOST VISUAL SECTION =====
const DclicBoostSection = ({ profile }) => {
  const [expanded, setExpanded] = useState(false);

  const dclicSkills = (profile.skills || []).filter(s => s.source === "dclic_pro");
  const competences = profile.dclic_competences || [];

  // Build dimension cards
  const dimensions = [
    profile.dclic_mbti && { label: "Personnalité MBTI", value: profile.dclic_mbti, color: "from-violet-500 to-purple-600", icon: User, description: "Votre type de personnalité" },
    profile.dclic_disc_label && { label: "Profil DISC", value: profile.dclic_disc_label, color: "from-blue-500 to-cyan-600", icon: Target, description: "Votre style comportemental" },
    profile.dclic_riasec_major && { label: "Intérêts RIASEC", value: profile.dclic_riasec_major, color: "from-emerald-500 to-teal-600", icon: TrendingUp, description: "Votre orientation professionnelle" },
    profile.dclic_vertu_dominante && { label: "Vertu dominante", value: profile.dclic_vertu_dominante, color: "from-amber-500 to-orange-600", icon: Award, description: "Votre force motrice" },
  ].filter(Boolean);

  return (
    <Card className="border-0 shadow-lg overflow-hidden" data-testid="dclic-boost-section">
      {/* Header */}
      <div className="bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 p-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-xl bg-white/20 backdrop-blur-sm flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                Profil boosté avec D'CLIC PRO
                <CheckCircle className="w-4 h-4 text-emerald-200" />
              </h3>
              <p className="text-emerald-100 text-xs mt-0.5">
                {dimensions.length} dimensions analysées — {competences.length + dclicSkills.length} compétences identifiées
              </p>
            </div>
          </div>
          <Button
            variant="ghost" size="sm"
            className="text-white/80 hover:text-white hover:bg-white/10 text-xs"
            onClick={() => setExpanded(!expanded)}
            data-testid="dclic-boost-toggle"
          >
            {expanded ? "Réduire" : "Voir le détail"}
            <ChevronRight className={`w-3.5 h-3.5 ml-1 transition-transform ${expanded ? "rotate-90" : ""}`} />
          </Button>
        </div>
      </div>

      {/* Dimension Cards — Always visible */}
      <CardContent className="p-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {dimensions.map((dim, i) => (
            <div key={i} className={`rounded-xl bg-gradient-to-br ${dim.color} p-3 text-white shadow-md`} data-testid={`dclic-dim-${i}`}>
              <dim.icon className="w-4 h-4 mb-1.5 opacity-80" />
              <p className="text-lg font-bold leading-tight">{dim.value}</p>
              <p className="text-[10px] opacity-80 mt-0.5">{dim.label}</p>
            </div>
          ))}
        </div>

        {/* Expanded: Competences + Skills */}
        {expanded && (
          <div className="mt-4 space-y-4 animate-in slide-in-from-top-2 duration-300">
            {/* Competences fortes */}
            {competences.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-slate-600 mb-2 flex items-center gap-1.5">
                  <Zap className="w-3.5 h-3.5 text-amber-500" /> Compétences fortes identifiées
                </p>
                <div className="flex flex-wrap gap-2">
                  {competences.map((c, i) => (
                    <Badge key={i} className="bg-amber-50 text-amber-700 border border-amber-200 text-xs font-medium px-2.5 py-1" data-testid={`dclic-comp-${i}`}>
                      <Star className="w-3 h-3 mr-1 text-amber-500" /> {typeof c === "string" ? c : c.name || c.nom || JSON.stringify(c)}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Skills importés */}
            {dclicSkills.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-slate-600 mb-2 flex items-center gap-1.5">
                  <BarChart3 className="w-3.5 h-3.5 text-indigo-500" /> Skills importés dans votre profil ({dclicSkills.length})
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {dclicSkills.map((s, i) => (
                    <Badge key={i} variant="outline" className="text-xs text-indigo-700 border-indigo-200 bg-indigo-50/50">
                      {s.name || s}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* What D'CLIC changed */}
            <div className="bg-slate-50 rounded-lg p-3 border border-slate-100">
              <p className="text-xs font-semibold text-slate-600 mb-2">Ce que D'CLIC PRO a apporté à votre espace :</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {[
                  profile.dclic_mbti && "Profil de personnalité MBTI",
                  profile.dclic_disc_label && "Analyse comportementale DISC",
                  profile.dclic_riasec_major && "Orientation professionnelle RIASEC",
                  profile.dclic_vertu_dominante && "Identification de votre vertu dominante",
                  competences.length > 0 && `${competences.length} compétences fortes identifiées`,
                  dclicSkills.length > 0 && `${dclicSkills.length} skills ajoutés à votre passeport`,
                  "Amélioration du score d'identité professionnelle",
                  "Meilleur ciblage du job matching",
                ].filter(Boolean).map((item, i) => (
                  <p key={i} className="text-xs text-slate-600 flex items-start gap-1.5">
                    <CheckCircle2 className="w-3 h-3 text-emerald-500 mt-0.5 shrink-0" /> {item}
                  </p>
                ))}
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

const ParticulierView = ({ token, section, onOpenDclic }) => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [passport, setPassport] = useState(null);
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
      const [profileRes, jobsRes, learningRes, passportRes] = await Promise.all([
        axios.get(`${API}/profile?token=${token}`),
        axios.get(`${API}/jobs?token=${token}`),
        axios.get(`${API}/learning?token=${token}`),
        axios.get(`${API}/passport?token=${token}`).catch(() => ({ data: null })),
      ]);
      setProfile(profileRes.data);
      setJobs(jobsRes.data);
      setLearningModules(learningRes.data);
      setPassport(passportRes.data);
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

  // Fusionner skills du profil + compétences du passeport avec la source
  const displayProfile = profile || { name: "Utilisateur", profile_score: 0, skills: [], strengths: [], gaps: [], sectors: [] };

  const allSkills = useMemo(() => {
    const merged = [];
    const seen = new Set();
    for (const s of (displayProfile.skills || [])) {
      const key = (s.name || "").toLowerCase();
      if (key && !seen.has(key)) {
        seen.add(key);
        merged.push({ name: s.name, level: s.level ?? (s.declared_level ? s.declared_level * 20 : 50), source: s.source || "declaratif" });
      }
    }
    // Only merge passport competences from actual analyses (prevents ghost skills on empty profiles)
    const validSources = new Set(["dclic_pro", "ia_detectee", "analyse_cv", "centres_interet"]);
    for (const c of (passport?.competences || [])) {
      const key = (c.name || "").toLowerCase();
      const src = c.source || "";
      if (key && !seen.has(key) && validSources.has(src)) {
        seen.add(key);
        const lvl = c.level === "expert" ? 90 : c.level === "avance" ? 70 : c.level === "intermediaire" ? 50 : 30;
        merged.push({ name: c.name, level: lvl, source: src, nature: c.nature });
      }
    }
    return merged;
  }, [displayProfile.skills, passport?.competences]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const metrics = [
    { title: "Identité Professionnelle", value: `${displayProfile.profile_score ?? 0}%`, icon: Target, color: "blue", subtitle: "Complétude de votre profil" },
    { title: "Job Matching", value: jobs.length > 0 ? (jobs.filter(j => (j.match_score || j.matching_score || 0) >= 60).length || jobs.length).toString() : "0", icon: Briefcase, color: "emerald", subtitle: jobs.filter(j => (j.match_score || j.matching_score || 0) >= 60).length > 0 ? "Offres compatibles" : "Offres disponibles" },
    { title: "Parcours Formation", value: learningModules.length > 0 ? (learningModules.filter(m => m.progress > 0 && m.progress < 100).length || learningModules.length).toString() : "0", icon: BookOpen, color: "amber", subtitle: learningModules.filter(m => m.progress > 0 && m.progress < 100).length > 0 ? "Modules en cours" : "Formations suggérées" },
    { title: "Compétences Valorisées", value: allSkills.length.toString(), icon: Zap, color: "violet", subtitle: "Toutes sources confondues" }
  ];

  if (section === "jobs") return <JobMatchingSection token={token} />;
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

      {/* Access Requests Notifications */}
      <AccessRequestsNotifications token={token} />

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4" data-testid="metrics-grid">

      {/* D'CLIC PRO Test Banner */}
      <Card className="sm:col-span-2 lg:col-span-4 bg-gradient-to-r from-indigo-600 to-blue-600 border-0 shadow-md cursor-pointer hover:shadow-lg transition-shadow" data-testid="dclic-test-banner" onClick={() => window.open('/test-dclic', '_blank', 'noopener,noreferrer')}>
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-white/20 flex items-center justify-center shrink-0">
                <Award className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="text-base font-semibold text-white">Passes le test D'CLIC PRO et Boost ton profil !</h3>
                <p className="text-indigo-100 text-sm">Pour améliorer et crédibiliser vos profils personnalités et compétences pro</p>
              </div>
            </div>
            <Button className="bg-white text-indigo-700 hover:bg-indigo-50 shrink-0 text-sm font-semibold" data-testid="dclic-test-btn" onClick={e => { e.stopPropagation(); window.open('/test-dclic', '_blank', 'noopener,noreferrer'); }}>
              <Play className="w-4 h-4 mr-1.5" />Passer le test
            </Button>
          </div>
        </CardContent>
      </Card>

        {metrics.map((metric, idx) => {
          const Icon = metric.icon;
          const colorClasses = { blue: "bg-blue-100 text-blue-600", emerald: "bg-emerald-100 text-emerald-600", amber: "bg-amber-100 text-amber-600", violet: "bg-violet-100 text-violet-600" };
          return (
            <Card key={idx} className="card-metric card-hover" data-testid={`metric-${metric.title.toLowerCase().replace(/\s/g, '-')}`}>
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-base font-medium text-slate-500 mb-1">{metric.title}</p>
                    <p className="text-3xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>{metric.value}</p>
                    <p className="text-sm text-slate-400 mt-1">{metric.subtitle}</p>
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

      {/* Main Content - CV Section Full Width */}
      <Card className="card-base" data-testid="skills-section">
        <CardHeader>
          <div>
            <CardTitle className="flex items-center gap-2 text-lg">
              <FileText className="w-5 h-5 text-[#1e3a5f]" />Mes CV
            </CardTitle>
            <CardDescription className="text-sm">Re'Actif Pro IA audite, optimise et adapte votre CV pour passer les filtres ATS</CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          <CvAnalysisSection token={token} onComplete={() => loadData(true)} />
          <div className="space-y-4 mt-6">
            <h4 className="text-base font-semibold text-slate-700">Compétences identifiées</h4>
            {/* Légende des sources */}
            {allSkills.length > 0 && (
              <div className="flex flex-wrap gap-3 text-xs border border-slate-200 rounded-lg p-2.5 bg-slate-50" data-testid="source-legend">
                <span className="text-slate-500 font-medium mr-1">Sources :</span>
                <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block"></span> D'CLIC PRO</span>
                <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-blue-500 inline-block"></span> Analyse CV (IA)</span>
                <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-pink-500 inline-block"></span> Centres d'intérêt</span>
                <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-slate-400 inline-block"></span> Déclaratif</span>
              </div>
            )}
            {allSkills.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-3">
                {allSkills.map((skill, idx) => {
                  const pct = skill.level || 0;
                  const src = skill.source || "";
                  const isDclic = src === "dclic_pro";
                  const isIA = src === "ia_detectee";
                  const isCentres = src === "centres_interet";
                  const barColor = isDclic ? "[&>div]:bg-emerald-500" : isIA ? "[&>div]:bg-blue-500" : isCentres ? "[&>div]:bg-pink-500" : "";
                  const labelColor = isDclic ? "text-emerald-700" : isIA ? "text-blue-700" : isCentres ? "text-pink-700" : "text-slate-700";
                  const dotColor = isDclic ? "bg-emerald-500" : isIA ? "bg-blue-500" : isCentres ? "bg-pink-500" : "bg-slate-400";
                  return (
                    <div key={idx} className="space-y-1.5" data-testid={`skill-${idx}`}>
                      <div className="flex items-center justify-between">
                        <span className={`text-sm font-medium ${labelColor} flex items-center gap-1.5`}>
                          <span className={`w-2 h-2 rounded-full ${dotColor} inline-block shrink-0`}></span>
                          {skill.name}
                        </span>
                        <span className="text-sm text-slate-500">{pct}%</span>
                      </div>
                      <Progress value={pct} className={`h-2 ${barColor}`} />
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-4 text-slate-400 text-sm">
                <p>Chargez un CV pour identifier vos compétences automatiquement</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* D'CLIC PRO Import Banner */}
      {profile?.dclic_imported ? (
        <DclicBoostSection profile={profile} />
      ) : (
        <Card className="bg-gradient-to-r from-emerald-600 to-teal-600 border-0 cursor-pointer hover:shadow-lg transition-shadow" data-testid="dclic-banner" onClick={() => onOpenDclic && onOpenDclic()}>
          <CardContent className="p-5">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center">
                  <Upload className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-base font-semibold text-white">Boost mon profil avec D'CLIC PRO</h3>
                  <p className="text-emerald-100 text-sm">Importez votre profil, compétences et preuves pour enrichir votre passeport</p>
                </div>
              </div>
              <Button className="bg-white text-emerald-700 hover:bg-emerald-50 shrink-0" onClick={e => { e.stopPropagation(); onOpenDclic && onOpenDclic(); }}>
                <Upload className="w-4 h-4 mr-2" />Boost mon profil
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

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
      </Card>
    </div>
  );
};

const JobCard = ({ job }) => {
  const title = job.title || job.titre || "Offre";
  const company = job.company || job.entreprise_type || "";
  const location = job.location || job.localisation || "";
  const contractType = job.contract_type || job.type_contrat || "";
  const skills = job.required_skills || job.competences_requises || [];
  const score = job.match_score ?? job.matching_score;

  return (
    <Card className="card-interactive group" data-testid={`job-card-${job.id || 'preview'}`}>
      <CardContent className="p-5">
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-slate-900 group-hover:text-blue-600 transition-colors truncate">
              {String(title)}
            </h3>
            <p className="text-sm text-slate-500 truncate">{String(company)}</p>
          </div>
          {score !== undefined && (
            <div className={`px-2 py-1 rounded-lg text-xs font-bold ${
              score >= 80 ? 'bg-emerald-100 text-emerald-700' :
              score >= 60 ? 'bg-blue-100 text-blue-700' :
              'bg-slate-100 text-slate-600'
            }`}>
              {score}%
            </div>
          )}
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-500 mb-3">
          {location && (
            <span className="flex items-center gap-1">
              <MapPin className="w-3 h-3" />
              {String(location)}
            </span>
          )}
          {contractType && (
            <Badge variant="outline" className="text-[10px]">{String(contractType)}</Badge>
          )}
        </div>
        {Array.isArray(skills) && skills.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {skills.slice(0, 3).map((skill, i) => (
              <Badge key={i} className="text-[10px] bg-slate-100 text-slate-600">{String(skill)}</Badge>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

const LearningCard = ({ module, onUpdateProgress }) => {
  const hasEmerging = module.emerging_match?.length > 0;
  return (
  <Card className={`card-interactive group overflow-hidden ${
    hasEmerging ? "ring-2 ring-amber-400 border-amber-300 bg-amber-50/30"
    : module.relevance === "haute" ? "ring-2 ring-blue-200" : ""
  }`} data-testid={`learning-card-${module.id}`}>
    {hasEmerging && (
      <div className="bg-gradient-to-r from-amber-500 to-orange-500 px-4 py-2 flex items-center gap-2" data-testid={`module-emerging-banner-${module.id}`}>
        <Zap className="w-4 h-4 text-white" />
        <span className="text-xs font-semibold text-white">Compétence émergente détectée</span>
      </div>
    )}
    {module.image_url && (
      <div className="h-32 overflow-hidden">
        <img src={module.image_url} alt={module.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
      </div>
    )}
    <CardContent className="p-5">
      <div className="flex items-center justify-between mb-2 flex-wrap gap-1">
        <Badge variant="secondary" className="text-xs">{module.category}</Badge>
        {module.provider && (
          <span className="text-[10px] text-slate-400">{module.provider}</span>
        )}
        {module.cpf_eligible && (
          <Badge className="bg-emerald-50 text-emerald-600 text-[10px]">CPF</Badge>
        )}
      </div>
      {hasEmerging && (
        <div className="flex flex-wrap gap-1 mb-2">
          {module.emerging_match.map((em, i) => (
            <Badge key={i} className="text-[10px] bg-amber-100 text-amber-800 border border-amber-400 font-semibold">
              <Zap className="w-3 h-3 mr-0.5" />{em}
            </Badge>
          ))}
        </div>
      )}
      <h3 className="font-semibold text-slate-900 mb-1 group-hover:text-blue-600 transition-colors">
        <a href={`https://www.google.com/search?q=${encodeURIComponent(module.title + (module.provider ? " " + module.provider : "") + " formation")}`}
          target="_blank" rel="noopener noreferrer"
          className="flex items-center gap-1.5 hover:underline underline-offset-2"
          data-testid={`learning-title-link-${module.id}`}>
          {module.title}
          <ExternalLink className="w-3.5 h-3.5 text-slate-400 group-hover:text-blue-500 transition-colors shrink-0" />
        </a>
      </h3>
      <p className="text-xs text-slate-500 mb-3 line-clamp-2">{module.description}</p>
      {module.skills_developed?.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-2">
          {module.skills_developed.slice(0, 4).map((s, i) => (
            <Badge key={i} variant="outline" className="text-[10px]">{s}</Badge>
          ))}
        </div>
      )}
      <div className="flex items-center justify-between text-xs text-slate-500 mb-3">
        <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{module.duration}</span>
        <Badge variant="outline">{module.level}</Badge>
      </div>
      {(() => {
        const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(module.title + (module.provider ? " " + module.provider : "") + " formation")}`;
        return (
          <a href={searchUrl} target="_blank" rel="noopener noreferrer" className="block w-full mt-3">
            <Button variant="outline" size="sm" className={`w-full ${hasEmerging ? "bg-amber-50 hover:bg-amber-100 text-amber-700 border-amber-300" : "hover:bg-blue-50 hover:text-blue-600"}`} data-testid={`learning-start-btn-${module.id}`}>
              <ExternalLink className="w-3 h-3 mr-1" />Accéder à la formation
            </Button>
          </a>
        );
      })()}
    </CardContent>
  </Card>
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
        <div className="mt-3 p-3 bg-blue-50 rounded-lg border border-blue-100 flex items-start gap-2" data-testid="ai-disclaimer">
          <AlertCircle className="w-4 h-4 text-blue-500 mt-0.5 shrink-0" />
          <p className="text-xs text-blue-700">Ces suggestions de formations sont générées par intelligence artificielle à partir de l'analyse de votre profil. Nous vous invitons à vérifier les informations (contenus, tarifs, disponibilités) directement auprès des organismes avant de vous engager.</p>
        </div>
      </div>

      {/* AI Recommendations */}
      {(recommendations.length > 0 || loadingRecs) && (
        <div data-testid="ai-recommendations-section">
          <div className="flex items-center gap-2 mb-4">
            <Sparkles className="w-5 h-5 text-violet-600" />
            <h2 className="text-lg font-semibold text-slate-900">Formations recommandées pour monter en compétence</h2>
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
                      {rec.emerging_skills?.length > 0 && (
                        <div className="flex flex-wrap gap-1 mb-2" data-testid={`rec-emerging-${idx}`}>
                          {rec.emerging_skills.map((es, i) => (
                            <Badge key={i} className="text-[10px] bg-amber-50 text-amber-700 border border-amber-300">
                              <Zap className="w-3 h-3 mr-0.5" />{es}
                            </Badge>
                          ))}
                        </div>
                      )}
                      <h3 className="font-semibold text-slate-900 text-sm mb-1 group-hover:text-violet-600 transition-colors">
                        <a href={`https://www.google.com/search?q=${encodeURIComponent(rec.title + (rec.provider ? " " + rec.provider : "") + " formation")}`}
                          target="_blank" rel="noopener noreferrer"
                          className="flex items-center gap-1.5 hover:underline underline-offset-2"
                          data-testid={`rec-title-link-${idx}`}>
                          {rec.title}
                          <ExternalLink className="w-3.5 h-3.5 text-slate-400 group-hover:text-violet-500 transition-colors shrink-0" />
                        </a>
                      </h3>
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
          <div className="flex items-center gap-2 mb-2">
            <BookOpen className="w-5 h-5 text-[#1e3a5f]" />
            <h2 className="text-lg font-semibold text-slate-900">Modules de formation</h2>
          </div>
          <div className="mb-4 p-2.5 bg-amber-50 rounded-lg border border-amber-200 flex items-start gap-2" data-testid="formations-sample-data-banner">
            <AlertCircle className="w-4 h-4 text-amber-500 mt-0.5 shrink-0" />
            <p className="text-xs text-amber-700">Ces modules sont des <strong>exemples initiaux</strong> pour illustrer le parcours de formation. Ils seront enrichis avec des contenus personnalisés en fonction de votre profil.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 stagger-children">
            {modules.map((module, idx) => <LearningCard key={idx} module={module} onUpdateProgress={updateProgress} />)}
          </div>
        </div>
      )}
    </div>
  );
};

// ===== NOTIFICATIONS DEMANDES D'ACCES =====
const AccessRequestsNotifications = ({ token }) => {
  const [requests, setRequests] = useState([]);
  const [responding, setResponding] = useState(null);

  useEffect(() => { loadRequests(); }, []);

  const loadRequests = async () => {
    try {
      const res = await axios.get(`${API}/notifications/access-requests?token=${token}`);
      setRequests(res.data);
    } catch {}
  };

  const respond = async (requestId, action) => {
    setResponding(requestId);
    try {
      await axios.post(`${API}/notifications/access-requests/${requestId}/respond?token=${token}`, { action }, { headers: { "Content-Type": "application/json" } });
      toast.success(action === "accept" ? "Accès autorisé" : "Demande refusée");
      loadRequests();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Erreur");
    }
    setResponding(null);
  };

  const pending = requests.filter(r => r.status === "en_attente");
  const past = requests.filter(r => r.status !== "en_attente");

  if (requests.length === 0) return null;

  return (
    <Card className={`border ${pending.length > 0 ? "border-amber-200 bg-amber-50/30" : "border-slate-100"}`} data-testid="access-requests-notifications">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-base">
          <Bell className="w-4 h-4 text-amber-600" />
          Demandes d'accès à votre profil
          {pending.length > 0 && <Badge className="bg-amber-100 text-amber-700 text-xs ml-1">{pending.length} en attente</Badge>}
        </CardTitle>
        <CardDescription>
          Vous avez choisi le mode "Limité" : les partenaires peuvent demander à consulter votre profil. Vous restez maître de vos données.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {pending.map(req => (
          <div key={req.id} className="flex items-center justify-between p-3 rounded-lg border border-amber-200 bg-white" data-testid={`access-req-${req.id}`}>
            <div>
              <p className="text-sm font-semibold text-slate-800">{req.partner_name}</p>
              <p className="text-xs text-slate-500">Demande d'accès à votre profil — {new Date(req.created_at).toLocaleDateString('fr-FR')}</p>
              <p className="text-xs text-amber-600 mt-1">En acceptant, votre nom et prénom seront communiqués à ce partenaire.</p>
            </div>
            <div className="flex gap-2 flex-shrink-0">
              <Button size="sm" className="bg-green-600 hover:bg-green-700 h-8 text-xs" onClick={() => respond(req.id, "accept")}
                disabled={responding === req.id} data-testid={`accept-req-${req.id}`}>
                {responding === req.id ? <Loader2 className="w-3 h-3 animate-spin" /> : <><CheckCircle2 className="w-3 h-3 mr-1" /> Accepter</>}
              </Button>
              <Button size="sm" variant="outline" className="text-red-500 hover:bg-red-50 h-8 text-xs border-red-200" onClick={() => respond(req.id, "reject")}
                disabled={responding === req.id} data-testid={`reject-req-${req.id}`}>
                <Shield className="w-3 h-3 mr-1" /> Refuser
              </Button>
            </div>
          </div>
        ))}
        {past.length > 0 && (
          <div className="pt-2 border-t border-slate-100">
            <p className="text-xs font-medium text-slate-500 mb-2">Historique</p>
            {past.slice(0, 5).map(req => (
              <div key={req.id} className="flex items-center justify-between py-1.5 text-xs" data-testid={`access-history-${req.id}`}>
                <span className="text-slate-600">{req.partner_name}</span>
                <div className="flex items-center gap-2">
                  <span className="text-slate-400">{new Date(req.responded_at || req.created_at).toLocaleDateString('fr-FR')}</span>
                  <Badge className={req.status === "accepte" ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"} variant="secondary">
                    {req.status === "accepte" ? "Accepté" : "Refusé"}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default ParticulierView;
