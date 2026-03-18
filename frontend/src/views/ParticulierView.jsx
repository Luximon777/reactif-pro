import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { 
  User, 
  Target, 
  TrendingUp, 
  BookOpen, 
  Briefcase,
  MapPin,
  Clock,
  Euro,
  Star,
  ChevronRight,
  Plus,
  Sparkles,
  Zap,
  Award,
  CheckCircle2,
  AlertCircle,
  Play,
  FolderLock,
  FileDown,
  FileText,
  LayoutList,
  Layers
} from "lucide-react";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";

const CvPreview = ({ data }) => {
  let cv;
  try {
    cv = typeof data === "string" ? JSON.parse(data) : data;
  } catch {
    return <pre className="text-xs text-slate-700 whitespace-pre-wrap font-sans leading-relaxed">{data}</pre>;
  }
  return (
    <div className="bg-white border rounded-lg p-6 space-y-4 text-slate-800 max-h-[600px] overflow-y-auto" style={{ fontFamily: "Calibri, sans-serif" }}>
      <div className="text-center border-b pb-4">
        <h1 className="text-2xl font-bold tracking-wide" style={{ color: "#1e3a5f" }}>{cv.nom || "Candidat"}</h1>
        {cv.titre && <p className="text-sm text-slate-500 mt-1">{cv.titre}</p>}
        {cv.contact && (
          <p className="text-xs text-slate-400 mt-2">
            {[cv.contact.email, cv.contact.telephone, cv.contact.adresse].filter(Boolean).join(" | ")}
          </p>
        )}
      </div>
      {cv.profil && (
        <div>
          <h2 className="text-xs font-bold uppercase tracking-wider mb-1" style={{ color: "#1e3a5f" }}>Profil professionnel</h2>
          <p className="text-sm leading-relaxed">{cv.profil}</p>
        </div>
      )}
      {cv.competences_cles?.length > 0 && (
        <div>
          <h2 className="text-xs font-bold uppercase tracking-wider mb-1" style={{ color: "#1e3a5f" }}>Compétences clés</h2>
          <div className="flex flex-wrap gap-1.5">
            {cv.competences_cles.map((c, i) => (
              <span key={i} className="text-xs px-2 py-0.5 rounded-full" style={{ background: "#f1f5f9", color: "#334155" }}>{c}</span>
            ))}
          </div>
        </div>
      )}
      {cv.experiences?.length > 0 && (
        <div>
          <h2 className="text-xs font-bold uppercase tracking-wider mb-2" style={{ color: "#1e3a5f" }}>Expériences professionnelles</h2>
          {cv.experiences.map((exp, i) => (
            <div key={i} className="mb-3">
              <p className="text-sm font-semibold text-slate-900">{exp.poste}</p>
              <p className="text-xs text-slate-500">{exp.entreprise} — {exp.periode}</p>
              <ul className="mt-1 space-y-0.5">
                {exp.missions?.map((m, j) => (
                  <li key={j} className="text-xs text-slate-600 pl-3 relative before:content-['•'] before:absolute before:left-0 before:text-slate-400">{m}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
      {cv.formations?.length > 0 && (
        <div>
          <h2 className="text-xs font-bold uppercase tracking-wider mb-1" style={{ color: "#1e3a5f" }}>Formation</h2>
          {cv.formations.map((f, i) => (
            <div key={i} className="mb-1">
              <p className="text-sm font-semibold">{f.diplome}</p>
              <p className="text-xs text-slate-500">{[f.etablissement, f.annee].filter(Boolean).join(" — ")}</p>
            </div>
          ))}
        </div>
      )}
      {cv.competences_techniques && Object.keys(cv.competences_techniques).length > 0 && (
        <div>
          <h2 className="text-xs font-bold uppercase tracking-wider mb-1" style={{ color: "#1e3a5f" }}>Compétences techniques</h2>
          {Object.entries(cv.competences_techniques).map(([domain, skills]) => (
            <p key={domain} className="text-xs"><span className="font-semibold">{domain} :</span> {Array.isArray(skills) ? skills.join(", ") : skills}</p>
          ))}
        </div>
      )}
      {cv.langues?.length > 0 && (
        <div>
          <h2 className="text-xs font-bold uppercase tracking-wider mb-1" style={{ color: "#1e3a5f" }}>Langues</h2>
          <p className="text-xs">{cv.langues.map(l => `${l.langue} — ${l.niveau}`).join(" | ")}</p>
        </div>
      )}
    </div>
  );
};

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
      const response = await axios.put(`${API}/profile?token=${token}`, {
        skills: updatedSkills
      });
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

  // Demo profile data if empty
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
    {
      title: "Identité Professionnelle",
      value: `${displayProfile.profile_score || 45}%`,
      icon: Target,
      color: "blue",
      subtitle: "Complétude de votre profil"
    },
    {
      title: "Métiers Compatibles",
      value: jobs.filter(j => j.match_score >= 60).length.toString(),
      icon: Briefcase,
      color: "emerald",
      subtitle: "Passerelles identifiées"
    },
    {
      title: "Parcours Formation",
      value: learningModules.filter(m => m.progress > 0 && m.progress < 100).length.toString(),
      icon: BookOpen,
      color: "amber",
      subtitle: "Modules en cours"
    },
    {
      title: "Compétences Valorisées",
      value: displayProfile.skills?.length?.toString() || "0",
      icon: Zap,
      color: "violet",
      subtitle: "Dans votre coffre-fort"
    }
  ];

  if (section === "jobs") {
    return <JobsSection jobs={jobs} token={token} />;
  }

  if (section === "learning") {
    return <LearningSection modules={learningModules} updateProgress={updateLearningProgress} />;
  }

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
          const colorClasses = {
            blue: "bg-blue-100 text-blue-600",
            emerald: "bg-emerald-100 text-emerald-600",
            amber: "bg-amber-100 text-amber-600",
            violet: "bg-violet-100 text-violet-600"
          };
          return (
            <Card key={idx} className="card-metric card-hover" data-testid={`metric-${metric.title.toLowerCase().replace(/\s/g, '-')}`}>
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-500 mb-1">{metric.title}</p>
                    <p className="text-3xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>
                      {metric.value}
                    </p>
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
        {/* CV Section with AI Analysis */}
        <Card className="lg:col-span-2 card-base" data-testid="skills-section">
          <CardHeader>
            <div>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-[#1e3a5f]" />
                Mes CV
              </CardTitle>
              <CardDescription>Chargez votre CV pour que l'IA analyse vos compétences et génère les modèles de votre choix</CardDescription>
            </div>
          </CardHeader>
          <CardContent>
            <CvAnalysisSection token={token} onComplete={() => loadData(true)} />

            {/* Skills list */}
            <div className="space-y-4 mt-6">
              <h4 className="text-sm font-semibold text-slate-700">Compétences identifiées</h4>
              {displayProfile.skills?.length > 0 ? (
                displayProfile.skills.map((skill, idx) => (
                  <div key={idx} className="space-y-2" data-testid={`skill-${idx}`}>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-slate-700">{skill.name}</span>
                      <span className="text-sm text-slate-500">{skill.level}%</span>
                    </div>
                    <Progress 
                      value={skill.level} 
                      className="h-2"
                    />
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

        {/* Strengths & Gaps */}
        <div className="space-y-6">
          <Card className="card-base" data-testid="strengths-section">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <CheckCircle2 className="w-5 h-5 text-green-600" />
                Compétences Transversales
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {(displayProfile.strengths || ["Adaptabilité", "Travail d'équipe"]).map((strength, idx) => (
                  <Badge key={idx} className="badge-success">
                    {strength}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card className="card-base" data-testid="gaps-section">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <AlertCircle className="w-5 h-5 text-amber-600" />
                Besoins en Formation
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {(displayProfile.gaps || ["Gestion de projet", "Langues"]).map((gap, idx) => (
                  <Badge key={idx} className="badge-warning">
                    {gap}
                  </Badge>
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
            <Button 
              className="bg-white text-[#1e3a5f] hover:bg-blue-50 font-semibold"
              onClick={() => navigate('/dashboard/coffre-fort')}
              data-testid="goto-coffre-fort-btn"
            >
              <FolderLock className="w-4 h-4 mr-2" />
              Accéder au coffre-fort
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Jobs Preview */}
      <Card className="card-base" data-testid="jobs-preview">
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Briefcase className="w-5 h-5 text-[#1e3a5f]" />
              Passerelles Métiers
            </CardTitle>
            <CardDescription>Métiers compatibles avec vos compétences transférables</CardDescription>
          </div>
          <Button variant="outline" size="sm" onClick={() => window.location.href = '/dashboard/jobs'}>
            Voir tout
            <ChevronRight className="w-4 h-4 ml-1" />
          </Button>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {jobs.slice(0, 3).map((job, idx) => (
              <JobCard key={idx} job={job} />
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Learning Preview */}
      <Card className="card-base" data-testid="learning-preview">
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="w-5 h-5 text-[#1e3a5f]" />
              Parcours de Formation
            </CardTitle>
            <CardDescription>Pour développer vos compétences et sécuriser votre trajectoire</CardDescription>
          </div>
          <Button variant="outline" size="sm" onClick={() => window.location.href = '/dashboard/learning'}>
            Voir tout
            <ChevronRight className="w-4 h-4 ml-1" />
          </Button>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {learningModules.slice(0, 3).map((module, idx) => (
              <LearningCard key={idx} module={module} onUpdateProgress={updateLearningProgress} />
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

const JobCard = ({ job }) => {
  const matchColor = job.match_score >= 80 ? "text-green-600 bg-green-50" : 
                     job.match_score >= 60 ? "text-blue-600 bg-blue-50" : 
                     "text-amber-600 bg-amber-50";
  
  return (
    <Card className="card-interactive group" data-testid={`job-card-${job.id}`}>
      <CardContent className="p-5">
        <div className="flex items-start justify-between mb-3">
          <div className={`px-2 py-1 rounded-lg text-sm font-semibold ${matchColor}`}>
            {job.match_score}% match
          </div>
          <Badge variant="outline" className="text-xs">
            {job.contract_type}
          </Badge>
        </div>
        <h3 className="font-semibold text-slate-900 mb-1 group-hover:text-blue-600 transition-colors">
          {job.title}
        </h3>
        <p className="text-sm text-slate-600 mb-3">{job.company}</p>
        <div className="space-y-1 text-xs text-slate-500">
          <div className="flex items-center gap-1">
            <MapPin className="w-3 h-3" />
            {job.location}
          </div>
          {job.salary_range && (
            <div className="flex items-center gap-1">
              <Euro className="w-3 h-3" />
              {job.salary_range}
            </div>
          )}
        </div>
        <div className="flex flex-wrap gap-1 mt-3">
          {job.required_skills?.slice(0, 3).map((skill, idx) => (
            <Badge key={idx} variant="secondary" className="text-xs">
              {skill}
            </Badge>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

const LearningCard = ({ module, onUpdateProgress }) => {
  return (
    <Card className="card-interactive group overflow-hidden" data-testid={`learning-card-${module.id}`}>
      {module.image_url && (
        <div className="h-32 overflow-hidden">
          <img 
            src={module.image_url} 
            alt={module.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
        </div>
      )}
      <CardContent className="p-5">
        <Badge variant="secondary" className="text-xs mb-2">{module.category}</Badge>
        <h3 className="font-semibold text-slate-900 mb-1 group-hover:text-blue-600 transition-colors">
          {module.title}
        </h3>
        <p className="text-xs text-slate-500 mb-3 line-clamp-2">{module.description}</p>
        <div className="flex items-center justify-between text-xs text-slate-500 mb-3">
          <span className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {module.duration}
          </span>
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
          <Button 
            variant="outline" 
            size="sm" 
            className="w-full mt-3 group-hover:bg-blue-50 group-hover:text-blue-600"
            onClick={() => onUpdateProgress(module.id, Math.min(100, module.progress + 25))}
          >
            <Play className="w-3 h-3 mr-1" />
            {module.progress === 0 ? "Commencer" : "Continuer"}
          </Button>
        )}
        {module.progress === 100 && (
          <Badge className="w-full mt-3 justify-center badge-success">
            <Award className="w-3 h-3 mr-1" />
            Terminé
          </Badge>
        )}
      </CardContent>
    </Card>
  );
};

const JobsSection = ({ jobs, token }) => (
  <div className="space-y-6 animate-fade-in" data-testid="jobs-section">
    <div>
      <h1 className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>
        Passerelles Métiers
      </h1>
      <p className="text-slate-600 mt-1">Identifiez les métiers compatibles avec vos compétences transférables</p>
    </div>
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 stagger-children">
      {jobs.map((job, idx) => (
        <JobCard key={idx} job={job} />
      ))}
    </div>
  </div>
);

const LearningSection = ({ modules, updateProgress }) => (
  <div className="space-y-6 animate-fade-in" data-testid="learning-section">
    <div>
      <h1 className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>
        Parcours de Formation
      </h1>
      <p className="text-slate-600 mt-1">Développez vos compétences et sécurisez votre trajectoire professionnelle</p>
    </div>
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 stagger-children">
      {modules.map((module, idx) => (
        <LearningCard key={idx} module={module} onUpdateProgress={updateProgress} />
      ))}
    </div>
  </div>
);

// ============== CV ANALYSIS SECTION ==============

const CV_MODELS_CONFIG = [
  { key: "classique", name: "CV Classique", desc: "Chronologique, sobre et professionnel", color: "bg-blue-50 border-blue-200 text-blue-700", icon: FileText },
  { key: "competences", name: "CV Compétences", desc: "Axé sur les savoir-faire et savoir-être", color: "bg-emerald-50 border-emerald-200 text-emerald-700", icon: Zap },
  { key: "fonctionnel", name: "CV Fonctionnel", desc: "Par domaines de compétences transversales", color: "bg-violet-50 border-violet-200 text-violet-700", icon: Target },
  { key: "mixte", name: "CV Mixte", desc: "Parcours + compétences transférables", color: "bg-amber-50 border-amber-200 text-amber-700", icon: Briefcase },
];

const CvAnalysisSection = ({ token, onComplete }) => {
  const [uploading, setUploading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [cvModels, setCvModels] = useState(null);
  const [viewingModel, setViewingModel] = useState(null);
  const [elapsed, setElapsed] = useState(0);
  const [currentStep, setCurrentStep] = useState(0);
  const [uploadError, setUploadError] = useState(null);
  const [serverStep, setServerStep] = useState("");
  const [loadingPrevious, setLoadingPrevious] = useState(true);
  const [generatingModel, setGeneratingModel] = useState(null);
  const [selectedGenModels, setSelectedGenModels] = useState([]);
  const [genProgress, setGenProgress] = useState(null);

  const STEPS = [
    { at: 0, label: "Envoi du fichier...", icon: FileText },
    { at: 3, label: "Extraction du contenu...", icon: FileText },
    { at: 8, label: "Identification des savoir-faire...", icon: Briefcase },
    { at: 15, label: "Détection des savoir-être...", icon: Star },
    { at: 22, label: "Analyse des compétences transversales...", icon: Target },
    { at: 30, label: "Suggestions d'offres d'emploi...", icon: Briefcase },
    { at: 38, label: "Remplissage du Passeport...", icon: Award },
    { at: 45, label: "Finalisation de l'analyse...", icon: CheckCircle2 },
  ];

  useEffect(() => {
    let timer;
    if (uploading) {
      setElapsed(0);
      setCurrentStep(0);
      timer = setInterval(() => {
        setElapsed(prev => {
          const next = prev + 1;
          const stepIdx = STEPS.filter(s => s.at <= next).length - 1;
          if (stepIdx >= 0) setCurrentStep(stepIdx);
          return next;
        });
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [uploading]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    // Load previous analysis result AND CV models on mount
    const loadPrevious = async () => {
      try {
        const [analysisRes, modelsRes] = await Promise.all([
          axios.get(`${API}/cv/latest-analysis?token=${token}`),
          axios.get(`${API}/cv/models?token=${token}`)
        ]);
        if (analysisRes.data.has_analysis) {
          setAnalysisResult(analysisRes.data.result);
        }
        if (modelsRes.data.models && Object.keys(modelsRes.data.models).length > 0) {
          setCvModels(modelsRes.data);
        }
      } catch (err) {
        console.error("Error loading previous analysis:", err);
      }
      setLoadingPrevious(false);
    };
    loadPrevious();
  }, [token]);

  const pollForResult = async (jobId) => {
    const maxPolls = 120;
    for (let i = 0; i < maxPolls; i++) {
      await new Promise(r => setTimeout(r, 3000));
      try {
        const res = await axios.get(`${API}/cv/analyze/status?token=${token}&job_id=${jobId}`);
        if (res.data.step) setServerStep(res.data.step);
        if (res.data.status === "completed") return res.data.result;
        if (res.data.status === "failed") throw new Error(res.data.error || "L'analyse a échoué");
      } catch (err) {
        // Retry on transient errors (502, 503, 504, network errors, 404)
        const status = err.response?.status;
        if (status === 404 || status === 502 || status === 503 || status === 504 || !err.response) {
          continue; // Server restarting or not ready - keep polling
        }
        throw err;
      }
    }
    throw new Error("L'analyse a pris trop de temps. Réessayez.");
  };

  const extractTextFromFile = async (file) => {
    const ext = file.name.toLowerCase().split(".").pop();

    if (ext === "txt") {
      return await file.text();
    }

    if (ext === "docx" || ext === "doc") {
      const mammoth = await import("mammoth");
      const arrayBuffer = await file.arrayBuffer();
      const result = await mammoth.extractRawText({ arrayBuffer });
      return result.value;
    }

    if (ext === "pdf") {
      // Read as base64 and send to backend as JSON (avoids multipart proxy corruption)
      const arrayBuffer = await file.arrayBuffer();
      const bytes = new Uint8Array(arrayBuffer);
      let binary = "";
      for (let i = 0; i < bytes.length; i++) {
        binary += String.fromCharCode(bytes[i]);
      }
      const base64 = btoa(binary);
      // Retry up to 3 times on transient errors
      for (let attempt = 0; attempt < 3; attempt++) {
        try {
          const res = await axios.post(`${API}/cv/extract-text-b64?token=${token}`, {
            data: base64,
            filename: file.name,
          }, { timeout: 30000 });
          return res.data.text;
        } catch (err) {
          const s = err.response?.status;
          if (attempt < 2 && (s === 502 || s === 503 || s === 504 || !err.response)) {
            await new Promise(r => setTimeout(r, 2000));
            continue;
          }
          throw err;
        }
      }
    }

    throw new Error("Format non supporté");
  };

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > 10 * 1024 * 1024) {
      toast.error("Fichier trop volumineux (max 10 Mo).");
      return;
    }

    const ext = file.name.toLowerCase().split(".").pop();
    if (!["pdf", "docx", "doc", "txt"].includes(ext)) {
      toast.error("Format non supporté. Utilisez PDF, DOCX ou TXT.");
      return;
    }

    setUploading(true);
    setAnalysisResult(null);
    setUploadError(null);
    setServerStep("Lecture du fichier...");

    try {
      const cvText = await extractTextFromFile(file);
      if (!cvText || cvText.trim().length < 50) {
        throw new Error("Le fichier ne contient pas assez de texte exploitable.");
      }

      setServerStep("Envoi du texte au serveur...");

      let jobId;
      for (let attempt = 0; attempt < 3; attempt++) {
        try {
          const startRes = await axios.post(`${API}/cv/analyze-text?token=${token}`, {
            text: cvText,
            filename: file.name,
          }, { timeout: 15000 });
          jobId = startRes.data.job_id;
          break;
        } catch (err) {
          const s = err.response?.status;
          if (attempt < 2 && (s === 502 || s === 503 || s === 504 || !err.response)) {
            await new Promise(r => setTimeout(r, 2000));
            continue;
          }
          throw err;
        }
      }

      setServerStep("Analyse IA en cours...");
      const result = await pollForResult(jobId);
      setAnalysisResult(result);
      toast.success(`CV analysé : ${result.savoir_faire_count} savoir-faire, ${result.savoir_etre_count} savoir-être détectés`);
      if (onComplete) onComplete();
    } catch (err) {
      let msg = err.response?.data?.detail || err.message || "Erreur lors de l'analyse du CV.";
      if (msg.toLowerCase().includes("budget")) {
        msg = "Le crédit d'analyse IA est temporairement épuisé. Rechargez votre clé dans Profil > Universal Key.";
      }
      setUploadError(msg);
      toast.error(msg);
    }
    setUploading(false);
    e.target.value = "";
  };

  const toggleGenModel = (key) => {
    setSelectedGenModels(prev =>
      prev.includes(key) ? prev.filter(k => k !== key) : [...prev, key]
    );
  };

  const generateSelectedModels = async () => {
    if (selectedGenModels.length === 0) return;
    setGeneratingModel(true);
    setGenProgress({ current: 0, total: selectedGenModels.length, currentModel: "" });
    try {
      const startRes = await axios.post(`${API}/cv/generate-models?token=${token}`, {
        model_types: selectedGenModels,
      }, { timeout: 15000 });
      const jobId = startRes.data.job_id;

      for (let i = 0; i < 120; i++) {
        await new Promise(r => setTimeout(r, 2000));
        try {
          const res = await axios.get(`${API}/cv/generate-models/status?token=${token}&job_id=${jobId}`);
          setGenProgress({ current: res.data.progress, total: res.data.total, currentModel: res.data.current_model || "" });
          if (res.data.status === "completed") {
            const modelsRes = await axios.get(`${API}/cv/models?token=${token}`);
            if (modelsRes.data.models) setCvModels(modelsRes.data);
            toast.success(`${selectedGenModels.length} CV généré${selectedGenModels.length > 1 ? "s" : ""} par Claude IA`);
            setSelectedGenModels([]);
            break;
          }
          if (res.data.status === "failed") {
            throw new Error(res.data.error || "La génération a échoué");
          }
        } catch (err) {
          if (err.response?.status === 502 || err.response?.status === 504 || !err.response) continue;
          throw err;
        }
      }
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || "Erreur lors de la génération.";
      toast.error(msg);
    }
    setGeneratingModel(false);
    setGenProgress(null);
  };

  const downloadModel = (key) => {
    window.open(`${API}/cv/download/${key}?token=${token}`, '_blank');
  };

  const downloadModelPdf = (key) => {
    window.open(`${API}/cv/download-pdf/${key}?token=${token}`, '_blank');
  };

  return (
    <div className="space-y-4">
      {loadingPrevious && (
        <div className="flex items-center justify-center py-4">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-sm text-slate-500">Chargement...</span>
        </div>
      )}
      {/* Upload Zone */}
      <div className={`relative border-2 border-dashed rounded-xl transition-all overflow-hidden ${uploading ? "border-blue-400 bg-gradient-to-br from-blue-50 to-indigo-50 p-0" : "border-slate-300 hover:border-[#1e3a5f] hover:bg-slate-50 p-6"}`}>
        {!uploading && (
          <input
            type="file"
            accept=".pdf,.docx,.doc,.txt"
            onChange={handleUpload}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            data-testid="cv-upload-input"
          />
        )}
        {uploading ? (
          <div className="p-6 space-y-4" data-testid="cv-upload-progress">
            {/* Timer header */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse" />
                <span className="text-sm font-semibold text-blue-800">Analyse IA en cours</span>
              </div>
              <div className="flex items-center gap-1.5 bg-white/80 px-3 py-1 rounded-full shadow-sm">
                <Clock className="w-4 h-4 text-blue-600" />
                <span className="text-lg font-mono font-bold text-blue-700" data-testid="cv-timer">
                  {Math.floor(elapsed / 60)}:{(elapsed % 60).toString().padStart(2, '0')}
                </span>
              </div>
            </div>

            {/* Progress bar */}
            <div className="w-full h-2 bg-blue-100 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full transition-all duration-1000 ease-out"
                style={{ width: `${Math.min((elapsed / 120) * 100, 95)}%` }}
              />
            </div>

            {/* Server step info */}
            {serverStep && (
              <div className="text-xs text-indigo-600 font-medium bg-white/60 px-2 py-1 rounded">
                {serverStep}
              </div>
            )}

            {/* Steps timeline */}
            <div className="space-y-1.5">
              {STEPS.map((step, idx) => {
                const StepIcon = step.icon;
                const isDone = idx < currentStep;
                const isCurrent = idx === currentStep;
                if (idx > currentStep + 1) return null;
                return (
                  <div key={idx} className={`flex items-center gap-2 py-1 px-2 rounded-lg transition-all ${isCurrent ? "bg-white/70 shadow-sm" : ""}`}>
                    <div className={`w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 ${isDone ? "bg-emerald-500" : isCurrent ? "bg-blue-500 animate-pulse" : "bg-slate-300"}`}>
                      {isDone ? (
                        <CheckCircle2 className="w-3 h-3 text-white" />
                      ) : (
                        <StepIcon className="w-3 h-3 text-white" />
                      )}
                    </div>
                    <span className={`text-xs ${isDone ? "text-emerald-700 line-through" : isCurrent ? "text-blue-800 font-semibold" : "text-slate-400"}`}>
                      {step.label}
                    </span>
                    {isCurrent && <div className="ml-auto w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />}
                  </div>
                );
              })}
            </div>
          </div>
        ) : (
          <div>
            <FileDown className="w-8 h-8 mx-auto text-slate-400 mb-2" />
            <p className="text-sm font-medium text-slate-700">Chargez votre CV (PDF, DOCX, TXT)</p>
            <p className="text-xs text-slate-400">L'IA analysera vos compétences et vous pourrez choisir les modèles de CV à générer</p>
          </div>
        )}
      </div>

      {/* Error display */}
      {uploadError && !uploading && !analysisResult && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4" data-testid="cv-upload-error">
          <div className="flex items-center gap-2 mb-2">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <h4 className="font-semibold text-red-800 text-sm">Erreur d'analyse</h4>
          </div>
          <p className="text-sm text-red-700">{uploadError}</p>
          <p className="text-xs text-red-500 mt-2">Cliquez sur la zone ci-dessus pour réessayer avec votre CV.</p>
        </div>
      )}

      {/* Analysis Result Summary */}
      {analysisResult && (
        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 space-y-3" data-testid="cv-analysis-result">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-600" />
            <h4 className="font-semibold text-emerald-800 text-sm">Analyse terminée — {analysisResult.filename}</h4>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-center">
            <div className="bg-white rounded-lg p-2">
              <p className="text-xl font-bold text-sky-600">{analysisResult.savoir_faire_count}</p>
              <p className="text-[10px] text-slate-500">Savoir-faire</p>
            </div>
            <div className="bg-white rounded-lg p-2">
              <p className="text-xl font-bold text-rose-500">{analysisResult.savoir_etre_count}</p>
              <p className="text-[10px] text-slate-500">Savoir-être</p>
            </div>
            <div className="bg-white rounded-lg p-2">
              <p className="text-xl font-bold text-blue-600">{analysisResult.experiences_count}</p>
              <p className="text-[10px] text-slate-500">Expériences</p>
            </div>
            <div className="bg-white rounded-lg p-2">
              <p className="text-xl font-bold text-emerald-600">{analysisResult.formations_suggestions?.length || 0}</p>
              <p className="text-[10px] text-slate-500">Formations suggérées</p>
            </div>
          </div>
          {/* Transversal competences */}
          {analysisResult.competences_transversales?.length > 0 && (
            <div>
              <p className="text-xs font-medium text-violet-700 mb-1">Compétences transversales identifiées :</p>
              <div className="flex flex-wrap gap-1">
                {analysisResult.competences_transversales.map((c, i) => (
                  <span key={i} className="text-xs bg-violet-100 text-violet-700 px-2 py-0.5 rounded-full">{c}</span>
                ))}
              </div>
            </div>
          )}
          {/* Formation suggestions */}
          {analysisResult.formations_suggestions?.length > 0 && (
            <div>
              <p className="text-xs font-medium text-amber-700 mb-1">Besoins de formation identifiés :</p>
              <div className="space-y-1">
                {analysisResult.formations_suggestions.map((f, i) => (
                  <div key={i} className="flex items-start gap-2 text-xs bg-white rounded-lg p-2">
                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${f.priority === "haute" ? "bg-red-100 text-red-700" : f.priority === "moyenne" ? "bg-amber-100 text-amber-700" : "bg-slate-100 text-slate-600"}`}>{f.priority}</span>
                    <div>
                      <p className="font-medium text-slate-800">{f.title}</p>
                      <p className="text-slate-500">{f.reason}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          {/* Offres d'emploi suggérées */}
          {analysisResult.offres_emploi_suggerees?.length > 0 && (
            <div data-testid="cv-suggested-jobs">
              <p className="text-xs font-medium text-blue-700 mb-1">Offres d'emploi suggérées :</p>
              <div className="space-y-1">
                {analysisResult.offres_emploi_suggerees.map((offre, i) => (
                  <div key={i} className="flex items-start gap-2 text-xs bg-white rounded-lg p-2 border border-blue-100">
                    <Briefcase className="w-4 h-4 text-blue-500 flex-shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <p className="font-medium text-slate-800">{offre.titre}</p>
                        {offre.type_contrat && (
                          <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-700">{offre.type_contrat}</span>
                        )}
                      </div>
                      {offre.secteur && <p className="text-slate-500">{offre.secteur}</p>}
                      {offre.description_courte && <p className="text-slate-400 mt-0.5">{offre.description_courte}</p>}
                      {offre.competences_requises?.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-1">
                          {offre.competences_requises.map((c, j) => (
                            <span key={j} className="text-[10px] bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded-full">{c}</span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          <p className="text-xs text-emerald-600 font-medium">Passeport automatiquement complété avec les données extraites</p>
        </div>
      )}

      {/* CV Models - Generate on demand */}
      {analysisResult && (
        <div className="space-y-3" data-testid="cv-models-section">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-blue-600" />
            <h4 className="text-sm font-semibold text-slate-800">Générer vos CV avec Claude IA</h4>
          </div>
          <p className="text-xs text-slate-500">Sélectionnez le ou les modèles de CV à générer, puis cliquez sur "Générer".</p>

          {/* Generation progress */}
          {generatingModel && genProgress && (
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-3" data-testid="cv-gen-progress">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                <p className="text-xs font-medium text-blue-800">
                  Génération en cours ({genProgress.current}/{genProgress.total})
                  {genProgress.currentModel && ` — ${CV_MODELS_CONFIG.find(c => c.key === genProgress.currentModel)?.name || genProgress.currentModel}`}
                </p>
              </div>
              <div className="w-full bg-blue-200 rounded-full h-1.5">
                <div className="bg-blue-600 h-1.5 rounded-full transition-all" style={{ width: `${Math.max(5, (genProgress.current / genProgress.total) * 100)}%` }} />
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {CV_MODELS_CONFIG.map((cv) => {
              const hasModel = cvModels?.models?.[cv.key];
              const isSelected = selectedGenModels.includes(cv.key);
              const Icon = cv.icon;
              return (
                <div
                  key={cv.key}
                  role="button"
                  tabIndex={0}
                  onClick={() => !generatingModel && toggleGenModel(cv.key)}
                  className={`p-3 rounded-lg border-2 text-left transition-all cursor-pointer ${isSelected ? `${cv.color} border-current shadow-sm` : hasModel ? `${cv.color} border-current/30` : "bg-white border-slate-200 hover:border-slate-400"} ${generatingModel ? "opacity-60 cursor-not-allowed" : ""}`}
                  data-testid={`cv-model-${cv.key}`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 ${isSelected ? "border-current bg-current/20" : "border-slate-300"}`}>
                      {isSelected && <CheckCircle2 className="w-3.5 h-3.5" />}
                    </div>
                    <Icon className="w-4 h-4 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="text-xs font-semibold truncate">{cv.name}</p>
                        {hasModel && <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-emerald-100 text-emerald-700 font-medium flex-shrink-0">Généré</span>}
                      </div>
                      <p className="text-[10px] opacity-70">{cv.desc}</p>
                    </div>
                  </div>
                  {hasModel && (
                    <div className="flex gap-1 mt-2 ml-8" onClick={(e) => e.stopPropagation()}>
                      <Button variant="outline" size="sm" className="text-[10px] h-6 px-2" onClick={() => setViewingModel(viewingModel === cv.key ? null : cv.key)} data-testid={`view-cv-${cv.key}`}>
                        <Play className="w-3 h-3 mr-0.5" /> Voir
                      </Button>
                      <Button variant="outline" size="sm" className="text-[10px] h-6 px-2" onClick={() => downloadModel(cv.key)} data-testid={`download-cv-${cv.key}`}>
                        <FileDown className="w-3 h-3 mr-0.5" /> Word
                      </Button>
                      <Button variant="outline" size="sm" className="text-[10px] h-6 px-2 text-red-600 border-red-200 hover:bg-red-50" onClick={() => downloadModelPdf(cv.key)} data-testid={`download-pdf-${cv.key}`}>
                        <FileDown className="w-3 h-3 mr-0.5" /> PDF
                      </Button>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Generate button */}
          {!generatingModel && (
            <div className="flex items-center justify-between pt-1">
              <p className="text-xs text-slate-500">
                {selectedGenModels.length === 0
                  ? "Sélectionnez au moins un modèle"
                  : `${selectedGenModels.length} modèle${selectedGenModels.length > 1 ? "s" : ""} sélectionné${selectedGenModels.length > 1 ? "s" : ""}`}
              </p>
              <Button
                size="sm"
                className="bg-[#1e3a5f] hover:bg-[#2a4a6f] text-white"
                onClick={generateSelectedModels}
                disabled={selectedGenModels.length === 0}
                data-testid="cv-generate-btn"
              >
                <Sparkles className="w-4 h-4 mr-1" />
                Générer {selectedGenModels.length > 0 ? `(${selectedGenModels.length})` : ""}
              </Button>
            </div>
          )}
        </div>
      )}

      {/* CV Models - show if models exist but no current analysis displayed */}
      {!analysisResult && cvModels?.models && Object.values(cvModels.models).some(v => v) && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {CV_MODELS_CONFIG.map((cv) => {
            const hasModel = cvModels?.models?.[cv.key];
            const Icon = cv.icon;
            if (!hasModel) return null;
            return (
              <div key={cv.key} className={`flex items-center justify-between p-3 rounded-lg border ${cv.color}`} data-testid={`cv-model-${cv.key}`}>
                <div className="flex items-center gap-3">
                  <Icon className="w-5 h-5 flex-shrink-0" />
                  <div>
                    <p className="text-sm font-semibold">{cv.name}</p>
                    <p className="text-xs opacity-70">{cv.desc}</p>
                  </div>
                </div>
                <div className="flex gap-1">
                  <Button variant="ghost" size="sm" onClick={() => setViewingModel(viewingModel === cv.key ? null : cv.key)} data-testid={`view-cv-${cv.key}`}>
                    <Play className="w-4 h-4" />
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => downloadModel(cv.key)} data-testid={`download-cv-${cv.key}`}>
                    <FileDown className="w-4 h-4" />
                  </Button>
                  <Button variant="ghost" size="sm" className="text-red-600" onClick={() => downloadModelPdf(cv.key)} data-testid={`download-pdf-${cv.key}`}>
                    <FileText className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* CV Preview */}
      {viewingModel && cvModels?.models?.[viewingModel] && (
        <div className="bg-white border rounded-xl p-4 max-h-96 overflow-y-auto" data-testid="cv-preview">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-semibold text-sm text-slate-800">{CV_MODELS_CONFIG.find(c => c.key === viewingModel)?.name}</h4>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={() => downloadModel(viewingModel)} data-testid="cv-preview-download-word">
                <FileDown className="w-3 h-3 mr-1" /> Word
              </Button>
              <Button variant="outline" size="sm" className="text-red-600 border-red-200 hover:bg-red-50" onClick={() => downloadModelPdf(viewingModel)} data-testid="cv-preview-download-pdf">
                <FileDown className="w-3 h-3 mr-1" /> PDF
              </Button>
              <Button variant="ghost" size="sm" onClick={() => setViewingModel(null)}>Fermer</Button>
            </div>
          </div>
          <CvPreview data={cvModels.models[viewingModel]} />
        </div>
      )}
    </div>
  );
};

export default ParticulierView;
