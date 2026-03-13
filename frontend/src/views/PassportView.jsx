import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
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
  User,
  Briefcase,
  GraduationCap,
  Sparkles,
  Target,
  Plus,
  RefreshCw,
  Shield,
  FolderLock,
  Brain,
  MessageCircle,
  Compass,
  TrendingUp,
  ChevronRight,
  Star,
  Award,
  BookOpen,
  Share2,
  Trash2,
  Zap,
  Edit3,
  Save,
  Check,
  ArrowRight,
  Layers,
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
  relationnelle: { label: "Relationnelle", color: "text-emerald-700 bg-emerald-50 border-emerald-200" },
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

  const [newComp, setNewComp] = useState({ name: "", category: "technique", level: "intermediaire", experience_years: 0 });
  const [newExp, setNewExp] = useState({ title: "", organization: "", description: "", skills_used: "", achievements: "", experience_type: "professionnel" });
  const [profileEdit, setProfileEdit] = useState({ professional_summary: "", career_project: "", motivations: "", compatible_environments: "", target_sectors: "" });

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
      const res = await axios.post(`${API}/passport/competences?token=${token}`, newComp);
      toast.success("Compétence ajoutée");
      setAddCompDialogOpen(false);
      setNewComp({ name: "", category: "technique", level: "intermediaire", experience_years: 0 });
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

  if (loading) return <div className="flex items-center justify-center h-64"><RefreshCw className="w-8 h-8 animate-spin text-blue-600" /></div>;
  if (!passport) return <div className="text-center py-12 text-slate-500">Impossible de charger le passeport</div>;

  const { completeness_score = 0, competences = [], experiences = [], learning_path = [], passerelles = [], sources_count = {} } = passport;
  const mainCompetences = competences.filter(c => !c.is_emerging);
  const emergingCompetences = competences.filter(c => c.is_emerging);

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

        <StatCard icon={Layers} value={competences.length} label="Compétences" sublabel={`dont ${emergingCompetences.length} émergentes`} color="bg-blue-600" />
        <StatCard icon={Briefcase} value={experiences.length} label="Expériences" sublabel={`${learning_path.length} formations`} color="bg-emerald-600" />
      </div>

      {/* Main Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid grid-cols-3 md:grid-cols-6 gap-1 h-auto p-1 bg-slate-100">
          <TabsTrigger value="profile" className="text-xs sm:text-sm py-2" data-testid="passport-tab-profile">
            <User className="w-4 h-4 mr-1 hidden sm:inline" />
            Profil
          </TabsTrigger>
          <TabsTrigger value="competences" className="text-xs sm:text-sm py-2" data-testid="passport-tab-competences">
            <Star className="w-4 h-4 mr-1 hidden sm:inline" />
            Compétences
          </TabsTrigger>
          <TabsTrigger value="emerging" className="text-xs sm:text-sm py-2" data-testid="passport-tab-emerging">
            <Sparkles className="w-4 h-4 mr-1 hidden sm:inline" />
            Émergentes
          </TabsTrigger>
          <TabsTrigger value="experiences" className="text-xs sm:text-sm py-2" data-testid="passport-tab-experiences">
            <Briefcase className="w-4 h-4 mr-1 hidden sm:inline" />
            Expériences
          </TabsTrigger>
          <TabsTrigger value="learning" className="text-xs sm:text-sm py-2" data-testid="passport-tab-learning">
            <GraduationCap className="w-4 h-4 mr-1 hidden sm:inline" />
            Parcours
          </TabsTrigger>
          <TabsTrigger value="passerelles" className="text-xs sm:text-sm py-2" data-testid="passport-tab-passerelles">
            <Compass className="w-4 h-4 mr-1 hidden sm:inline" />
            Passerelles
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

        {/* Main Competences Tab */}
        <TabsContent value="competences" className="space-y-4 mt-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-slate-900">Compétences principales ({mainCompetences.length})</h3>
            <Dialog open={addCompDialogOpen} onOpenChange={setAddCompDialogOpen}>
              <DialogTrigger asChild>
                <Button size="sm" data-testid="add-competence-btn"><Plus className="w-4 h-4 mr-1" />Ajouter</Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader><DialogTitle>Ajouter une compétence</DialogTitle></DialogHeader>
                <div className="space-y-3">
                  <Input placeholder="Nom de la compétence" value={newComp.name} onChange={e => setNewComp({...newComp, name: e.target.value})} data-testid="comp-name-input" />
                  <Select value={newComp.category} onValueChange={v => setNewComp({...newComp, category: v})}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="technique">Technique</SelectItem>
                      <SelectItem value="transversale">Transversale</SelectItem>
                      <SelectItem value="relationnelle">Relationnelle</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={newComp.level} onValueChange={v => setNewComp({...newComp, level: v})}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="debutant">Débutant</SelectItem>
                      <SelectItem value="intermediaire">Intermédiaire</SelectItem>
                      <SelectItem value="avance">Avancé</SelectItem>
                      <SelectItem value="expert">Expert</SelectItem>
                    </SelectContent>
                  </Select>
                  <Button className="w-full" onClick={handleAddCompetence} data-testid="submit-competence-btn">
                    <Check className="w-4 h-4 mr-2" />Ajouter la compétence
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {mainCompetences.map(comp => (
              <CompetenceCard key={comp.id} comp={comp} onDelete={handleDeleteCompetence} />
            ))}
          </div>
          {mainCompetences.length === 0 && <EmptyState text="Ajoutez vos compétences pour enrichir votre passeport" />}
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
              <CompetenceCard key={comp.id} comp={comp} onDelete={handleDeleteCompetence} emerging />
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
    </div>
  );
};

// ============== SUB-COMPONENTS ==============

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

const CompetenceCard = ({ comp, onDelete, emerging }) => {
  const levelConfig = LEVEL_CONFIG[comp.level] || LEVEL_CONFIG.intermediaire;
  const catConfig = CATEGORY_CONFIG[comp.category] || CATEGORY_CONFIG.technique;
  const srcConfig = SOURCE_CONFIG[comp.source] || SOURCE_CONFIG.declaratif;
  const SrcIcon = srcConfig.icon;

  return (
    <Card className={`hover:shadow-md transition-shadow ${emerging ? "border-violet-200 bg-violet-50/30" : ""}`} data-testid="competence-card">
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-2">
          <div>
            <h4 className="font-semibold text-slate-900 text-sm">{comp.name}</h4>
            <div className="flex items-center gap-1 mt-1">
              <Badge variant="outline" className={`text-xs ${catConfig.color}`}>{catConfig.label}</Badge>
              <Badge className={`text-xs ${srcConfig.color}`}><SrcIcon className="w-3 h-3 mr-0.5" />{srcConfig.label}</Badge>
            </div>
          </div>
          {comp.source === "declaratif" && (
            <Button variant="ghost" size="sm" className="h-7 w-7 p-0 text-slate-400 hover:text-red-500" onClick={() => onDelete(comp.id)}>
              <Trash2 className="w-3.5 h-3.5" />
            </Button>
          )}
        </div>
        <div className="mt-3">
          <div className="flex items-center justify-between text-xs mb-1">
            <span className="text-slate-500">Niveau</span>
            <span className={`font-medium ${levelConfig.color} px-2 py-0.5 rounded-full`}>{levelConfig.label}</span>
          </div>
          <Progress value={levelConfig.width} className="h-1.5" />
        </div>
        {comp.proof && (
          <div className="mt-2 flex items-center gap-1 text-xs text-blue-600">
            <Award className="w-3 h-3" />
            <span>Preuve: {comp.proof}</span>
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
              <ArrowRight className="w-4 h-4 text-blue-600" />
              {passerelle.job_name}
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

export default PassportView;
