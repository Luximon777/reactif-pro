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
  FolderLock
} from "lucide-react";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";

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

  const loadData = async () => {
    setLoading(true);
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
      toast.error("Erreur lors du chargement des données");
    }
    setLoading(false);
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
        {/* Skills Section */}
        <Card className="lg:col-span-2 card-base" data-testid="skills-section">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Zap className="w-5 h-5 text-[#1e3a5f]" />
                Mes Compétences
              </CardTitle>
              <CardDescription>Votre coffre-fort numérique des compétences</CardDescription>
            </div>
            <Dialog open={editingProfile} onOpenChange={setEditingProfile}>
              <DialogTrigger asChild>
                <Button variant="outline" size="sm" data-testid="add-skill-btn">
                  <Plus className="w-4 h-4 mr-1" />
                  Ajouter
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Ajouter une compétence</DialogTitle>
                  <DialogDescription>
                    Ajoutez une nouvelle compétence à votre profil
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 mt-4">
                  <Input
                    placeholder="Nom de la compétence"
                    value={newSkill}
                    onChange={(e) => setNewSkill(e.target.value)}
                    data-testid="new-skill-input"
                  />
                  <Button onClick={addSkill} className="w-full btn-primary" data-testid="submit-skill-btn">
                    Ajouter la compétence
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
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
                <div className="text-center py-8 text-slate-500">
                  <Zap className="w-12 h-12 mx-auto mb-3 text-slate-300" />
                  <p>Aucune compétence ajoutée</p>
                  <p className="text-sm">Cliquez sur "Ajouter" pour commencer</p>
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

export default ParticulierView;
