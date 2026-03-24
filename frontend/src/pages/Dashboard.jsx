import { useState, useEffect } from "react";
import { Routes, Route, Navigate, useNavigate, useLocation } from "react-router-dom";
import { useAuth, API } from "@/App";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { 
  Users, 
  Building2, 
  Handshake, 
  Home,
  Briefcase,
  BookOpen,
  LogOut,
  ChevronDown,
  Sparkles,
  Menu,
  X,
  Settings,
  FolderLock,
  Brain,
  Gauge,
  Shield,
  Layers,
  Upload
} from "lucide-react";
import { toast } from "sonner";
import LogoReactifPro from "@/components/LogoReactifPro";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

// Dashboard Views
import ParticulierView from "@/views/ParticulierView";
import EntrepriseView from "@/views/EntrepriseView";
import PartenaireView from "@/views/PartenaireView";
import CoffreFortView from "@/views/CoffreFortView";
import ObservatoireView from "@/views/ObservatoireView";
import EvolutionIndexView from "@/views/EvolutionIndexView";
import PassportView from "@/views/PassportView";
import ExplorateurView from "@/views/ExplorateurView";
import PrivacySettingsView from "@/views/PrivacySettingsView";

const Dashboard = () => {
  const { token, role, switchRole, logout, authMode, pseudo } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [isSeeding, setIsSeeding] = useState(false);
  const [dataSeeded, setDataSeeded] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    // Seed database on first load
    const seedData = async () => {
      const seededBefore = sessionStorage.getItem('reactif_seeded');
      if (!seededBefore) {
        try {
          await axios.post(`${API}/seed`);
          sessionStorage.setItem('reactif_seeded', 'true');
          setRefreshKey(prev => prev + 1);
        } catch (error) {
          console.log("Seed completed or already seeded");
        }
      }
      setDataSeeded(true);
    };
    seedData();
  }, []);

  const handleSwitchRole = async (newRole) => {
    const success = await switchRole(newRole);
    if (success) {
      toast.success(`Rôle changé: ${getRoleLabel(newRole)}`);
    }
  };

  const handleLogout = () => {
    logout();
    navigate("/");
    toast.info("Déconnexion réussie");
  };

  const [dclicOpen, setDclicOpen] = useState(false);
  const [dclicImporting, setDclicImporting] = useState(false);
  const [dclicForm, setDclicForm] = useState({
    target_job: "", summary: "", city: "", mobility: "departement",
    contract_types: [], work_modes: [],
    skills: [{ name: "", category: "technique", declared_level: 3, status: "declaree" }],
    experiences: [{ title: "", organization: "", description: "", start_date: "", end_date: "" }],
    evidences: [{ title: "", kind: "diplome", source: "" }],
  });

  const handleDclicImport = async () => {
    setDclicImporting(true);
    try {
      const payload = {
        ...dclicForm,
        skills: dclicForm.skills.filter(s => s.name.trim()),
        experiences: dclicForm.experiences.filter(e => e.title.trim()),
        evidences: dclicForm.evidences.filter(e => e.title.trim()),
      };
      const res = await axios.post(`${API}/profile/import-dclic?token=${token}`, payload);
      toast.success(`${res.data.message} - Score: ${res.data.profile_completion}%`);
      setDclicOpen(false);
      setRefreshKey(prev => prev + 1);
    } catch (e) {
      toast.error("Erreur lors de l'import");
    }
    setDclicImporting(false);
  };

  const handleSeedDatabase = async () => {
    setIsSeeding(true);
    try {
      await axios.post(`${API}/seed`);
      toast.success("Données de démonstration chargées !");
      window.location.reload();
    } catch (error) {
      toast.error("Erreur lors du chargement des données");
    }
    setIsSeeding(false);
  };

  const getRoleLabel = (r) => {
    const labels = {
      particulier: "Espace Personnel",
      entreprise: "Espace Employeurs",
      partenaire: "Espace Partenaires"
    };
    return labels[r] || r;
  };

  const getRoleIcon = (r) => {
    const icons = {
      particulier: Users,
      entreprise: Building2,
      partenaire: Handshake
    };
    return icons[r] || Users;
  };

  const getRoleColor = (r) => {
    const colors = {
      particulier: "bg-blue-100 text-blue-700 border-blue-200",
      entreprise: "bg-emerald-100 text-emerald-700 border-emerald-200",
      partenaire: "bg-violet-100 text-violet-700 border-violet-200"
    };
    return colors[r] || colors.particulier;
  };

  const RoleIcon = getRoleIcon(role);

  const navItems = [
    { label: "Tableau de bord", shortLabel: "Accueil", icon: Home, path: "/dashboard" },
    { label: "Passeport", shortLabel: "Passeport", icon: Shield, path: "/dashboard/passeport", roles: ["particulier"] },
    { label: "Coffre-fort", shortLabel: "Coffre-fort", icon: FolderLock, path: "/dashboard/coffre-fort", roles: ["particulier"] },
    { label: "Observatoire", shortLabel: "Observatoire", icon: Brain, path: "/dashboard/observatoire" },
    { label: "Explorateur", shortLabel: "Explorateur", icon: Layers, path: "/dashboard/explorateur" },
    { label: "Évolution", shortLabel: "Évolution", icon: Gauge, path: "/dashboard/evolution" },
    { label: "Job Matching", shortLabel: "Matching", icon: Briefcase, path: "/dashboard/jobs", roles: ["particulier", "entreprise"] },
    { label: "Formations", shortLabel: "Formations", icon: BookOpen, path: "/dashboard/learning", roles: ["particulier"] },
    { label: "Confidentialité", shortLabel: "Confidentialité", icon: Settings, path: "/dashboard/confidentialite" },
  ];

  const filteredNavItems = navItems.filter(item => !item.roles || item.roles.includes(role));

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Top Navigation */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-white border-b border-slate-100 shadow-sm">
        <div className="max-w-[1600px] mx-auto px-4 sm:px-6">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center cursor-pointer flex-shrink-0" onClick={() => navigate("/dashboard")}>
              <LogoReactifPro size="md" />
            </div>

            {/* Right Side */}
            <div className="flex items-center gap-2">
              {/* Auth Mode Badge */}
              {authMode === "pseudo" && pseudo && (
                <Badge className="hidden sm:inline-flex bg-green-50 text-green-700 border-green-200 text-xs" data-testid="pseudo-badge">
                  <Shield className="w-3 h-3 mr-1" />
                  {pseudo}
                </Badge>
              )}
              {authMode === "anonymous" && (
                <Badge className="hidden sm:inline-flex bg-amber-50 text-amber-700 border-amber-200 text-xs" data-testid="anonymous-badge">
                  Anonyme
                </Badge>
              )}

              {/* Ubuntoo Link */}
              <a href="https://job-matching-ai.preview.emergentagent.com/" target="_blank" rel="noopener noreferrer"
                className="hidden sm:flex" data-testid="ubuntoo-link">
                <Button variant="outline" size="sm" className="border-teal-200 bg-teal-50 text-teal-700 hover:bg-teal-100 gap-1.5 text-xs">
                  <img src="https://customer-assets.emergentagent.com/job_keen-meitner-5/artifacts/t3wjk59k_logo_ubuntoo_transparent.png"
                    alt="Ubuntoo" className="h-4 w-auto" />
                  <span className="hidden lg:inline">Ubuntoo</span>
                </Button>
              </a>

              {/* Role Switcher */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" className={`${getRoleColor(role)} border`} data-testid="role-switcher">
                    <RoleIcon className="w-4 h-4 mr-2" />
                    <span className="hidden sm:inline">{getRoleLabel(role)}</span>
                    <ChevronDown className="w-4 h-4 ml-2" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56">
                  <DropdownMenuItem onClick={() => handleSwitchRole("particulier")} data-testid="switch-particulier">
                    <Users className="w-4 h-4 mr-2 text-[#1e3a5f]" />
                    Espace Personnel
                    {role === "particulier" && <Badge className="ml-auto bg-blue-100 text-[#1e3a5f]">Actif</Badge>}
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => handleSwitchRole("entreprise")} data-testid="switch-entreprise">
                    <Building2 className="w-4 h-4 mr-2 text-emerald-600" />
                    Espace Employeurs
                    {role === "entreprise" && <Badge className="ml-auto bg-emerald-100 text-emerald-700">Actif</Badge>}
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => handleSwitchRole("partenaire")} data-testid="switch-partenaire">
                    <Handshake className="w-4 h-4 mr-2 text-violet-600" />
                    Espace Partenaires
                    {role === "partenaire" && <Badge className="ml-auto bg-violet-100 text-violet-700">Actif</Badge>}
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleSeedDatabase} disabled={isSeeding} data-testid="seed-data-btn">
                    <Settings className="w-4 h-4 mr-2" />
                    {isSeeding ? "Chargement..." : "Recharger données démo"}
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>

              {/* Logout */}
              <Dialog open={dclicOpen} onOpenChange={setDclicOpen}>
                {role === "particulier" && (
                  <DialogTrigger asChild>
                    <Button variant="outline" className="text-[#1e3a5f] border-[#1e3a5f]/30 hover:bg-[#1e3a5f]/5 text-xs" data-testid="dclic-import-btn">
                      <Upload className="w-4 h-4 mr-1.5" />
                      <span className="hidden md:inline">Charger mon profil D'CLIC PRO</span>
                      <span className="md:hidden">D'CLIC PRO</span>
                    </Button>
                  </DialogTrigger>
                )}
                <DialogContent className="sm:max-w-[600px] max-h-[80vh] overflow-y-auto" data-testid="dclic-dialog">
                  <DialogHeader>
                    <DialogTitle className="flex items-center gap-2 text-[#1e3a5f]">
                      <Upload className="w-5 h-5" />Charger mon profil D'CLIC PRO
                    </DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4 text-sm">
                    <p className="text-xs text-slate-500">Renseignez vos informations pour enrichir votre profil Re'Actif Pro.</p>

                    {/* Identity */}
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="text-xs font-medium text-slate-700">Poste cible</label>
                        <Input placeholder="Ex: Developpeur Web" value={dclicForm.target_job} onChange={e => setDclicForm(p => ({...p, target_job: e.target.value}))} data-testid="dclic-target-job" />
                      </div>
                      <div>
                        <label className="text-xs font-medium text-slate-700">Ville</label>
                        <Input placeholder="Ex: Strasbourg" value={dclicForm.city} onChange={e => setDclicForm(p => ({...p, city: e.target.value}))} data-testid="dclic-city" />
                      </div>
                    </div>
                    <div>
                      <label className="text-xs font-medium text-slate-700">Resume professionnel</label>
                      <Textarea placeholder="Votre parcours en quelques lignes..." value={dclicForm.summary} onChange={e => setDclicForm(p => ({...p, summary: e.target.value}))} className="h-16" data-testid="dclic-summary" />
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="text-xs font-medium text-slate-700">Mobilite</label>
                        <select className="w-full border rounded-md px-3 py-2 text-sm" value={dclicForm.mobility} onChange={e => setDclicForm(p => ({...p, mobility: e.target.value}))} data-testid="dclic-mobility">
                          <option value="commune">Commune</option>
                          <option value="departement">Departement</option>
                          <option value="region">Region</option>
                          <option value="france">France entiere</option>
                          <option value="international">International</option>
                        </select>
                      </div>
                      <div>
                        <label className="text-xs font-medium text-slate-700">Types de contrat</label>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {["CDI","CDD","Interim","Freelance","Alternance","Stage"].map(ct => (
                            <Badge key={ct} variant={dclicForm.contract_types.includes(ct) ? "default" : "outline"} className={`cursor-pointer text-[10px] ${dclicForm.contract_types.includes(ct) ? "bg-[#1e3a5f]" : ""}`}
                              onClick={() => setDclicForm(p => ({...p, contract_types: p.contract_types.includes(ct) ? p.contract_types.filter(x => x !== ct) : [...p.contract_types, ct]}))}>
                              {ct}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </div>
                    <div>
                      <label className="text-xs font-medium text-slate-700">Modes de travail</label>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {["Presentiel","Teletravail","Hybride"].map(wm => (
                          <Badge key={wm} variant={dclicForm.work_modes.includes(wm) ? "default" : "outline"} className={`cursor-pointer text-[10px] ${dclicForm.work_modes.includes(wm) ? "bg-[#1e3a5f]" : ""}`}
                            onClick={() => setDclicForm(p => ({...p, work_modes: p.work_modes.includes(wm) ? p.work_modes.filter(x => x !== wm) : [...p.work_modes, wm]}))}>
                            {wm}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    {/* Skills */}
                    <div>
                      <label className="text-xs font-semibold text-slate-700">Competences</label>
                      {dclicForm.skills.map((sk, i) => (
                        <div key={i} className="flex gap-2 mt-1 items-center">
                          <Input placeholder="Nom" className="flex-1 text-xs" value={sk.name} onChange={e => { const s=[...dclicForm.skills]; s[i].name=e.target.value; setDclicForm(p=>({...p,skills:s})); }} />
                          <select className="border rounded px-2 py-1.5 text-xs w-28" value={sk.category} onChange={e => { const s=[...dclicForm.skills]; s[i].category=e.target.value; setDclicForm(p=>({...p,skills:s})); }}>
                            <option value="technique">Technique</option>
                            <option value="transversale">Transversale</option>
                            <option value="comportementale">Comportementale</option>
                          </select>
                          <select className="border rounded px-2 py-1.5 text-xs w-16" value={sk.declared_level} onChange={e => { const s=[...dclicForm.skills]; s[i].declared_level=parseInt(e.target.value); setDclicForm(p=>({...p,skills:s})); }}>
                            {[1,2,3,4,5].map(l => <option key={l} value={l}>{l}/5</option>)}
                          </select>
                        </div>
                      ))}
                      <Button variant="ghost" size="sm" className="mt-1 text-xs text-[#1e3a5f]" onClick={() => setDclicForm(p => ({...p, skills: [...p.skills, {name:"",category:"technique",declared_level:3,status:"declaree"}]}))}>+ Ajouter</Button>
                    </div>

                    {/* Experiences */}
                    <div>
                      <label className="text-xs font-semibold text-slate-700">Experiences</label>
                      {dclicForm.experiences.map((exp, i) => (
                        <div key={i} className="border rounded-lg p-2 mt-1 space-y-1">
                          <div className="grid grid-cols-2 gap-2">
                            <Input placeholder="Poste" className="text-xs" value={exp.title} onChange={e => { const x=[...dclicForm.experiences]; x[i].title=e.target.value; setDclicForm(p=>({...p,experiences:x})); }} />
                            <Input placeholder="Entreprise" className="text-xs" value={exp.organization} onChange={e => { const x=[...dclicForm.experiences]; x[i].organization=e.target.value; setDclicForm(p=>({...p,experiences:x})); }} />
                          </div>
                          <Input placeholder="Description" className="text-xs" value={exp.description} onChange={e => { const x=[...dclicForm.experiences]; x[i].description=e.target.value; setDclicForm(p=>({...p,experiences:x})); }} />
                        </div>
                      ))}
                      <Button variant="ghost" size="sm" className="mt-1 text-xs text-[#1e3a5f]" onClick={() => setDclicForm(p => ({...p, experiences: [...p.experiences, {title:"",organization:"",description:"",start_date:"",end_date:""}]}))}>+ Ajouter</Button>
                    </div>

                    {/* Evidences */}
                    <div>
                      <label className="text-xs font-semibold text-slate-700">Preuves / Certifications</label>
                      {dclicForm.evidences.map((ev, i) => (
                        <div key={i} className="flex gap-2 mt-1 items-center">
                          <Input placeholder="Titre" className="flex-1 text-xs" value={ev.title} onChange={e => { const v=[...dclicForm.evidences]; v[i].title=e.target.value; setDclicForm(p=>({...p,evidences:v})); }} />
                          <select className="border rounded px-2 py-1.5 text-xs w-28" value={ev.kind} onChange={e => { const v=[...dclicForm.evidences]; v[i].kind=e.target.value; setDclicForm(p=>({...p,evidences:v})); }}>
                            <option value="diplome">Diplome</option>
                            <option value="certificat">Certificat</option>
                            <option value="attestation">Attestation</option>
                            <option value="portfolio">Portfolio</option>
                            <option value="recommandation">Recommandation</option>
                          </select>
                        </div>
                      ))}
                      <Button variant="ghost" size="sm" className="mt-1 text-xs text-[#1e3a5f]" onClick={() => setDclicForm(p => ({...p, evidences: [...p.evidences, {title:"",kind:"attestation",source:""}]}))}>+ Ajouter</Button>
                    </div>

                    <Button className="w-full bg-[#1e3a5f] hover:bg-[#2d4a6f]" onClick={handleDclicImport} disabled={dclicImporting} data-testid="dclic-submit-btn">
                      {dclicImporting ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" /> : <Upload className="w-4 h-4 mr-2" />}
                      {dclicImporting ? "Import en cours..." : "Importer mon profil"}
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>
              <Button 
                variant="ghost" 
                size="icon" 
                onClick={handleLogout}
                className="text-slate-500 hover:text-red-600"
                data-testid="logout-btn"
              >
                <LogOut className="w-5 h-5" />
              </Button>

              {/* Mobile Menu Toggle */}
              <Button
                variant="ghost"
                size="icon"
                className="md:hidden"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              >
                {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </Button>
            </div>
          </div>
        </div>

        {/* Desktop Sub-Nav Bar */}
        <div className="hidden md:block border-t border-slate-100 bg-slate-50/80">
          <div className="max-w-[1600px] mx-auto px-4 sm:px-6">
            <nav className="flex items-center gap-0.5 overflow-x-auto scrollbar-hide py-1" style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}>
              {filteredNavItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                return (
                  <button
                    key={item.path}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium whitespace-nowrap transition-colors flex-shrink-0 ${
                      isActive 
                        ? "bg-[#1e3a5f] text-white" 
                        : "text-slate-600 hover:bg-white hover:text-slate-900"
                    }`}
                    onClick={() => navigate(item.path)}
                    data-testid={`nav-${item.label.toLowerCase().replace(/\s/g, '-')}`}
                  >
                    <Icon className="w-3.5 h-3.5" />
                    {item.shortLabel}
                  </button>
                );
              })}
            </nav>
          </div>
        </div>

        {/* Mobile Nav */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-slate-100 bg-white">
            <nav className="p-4 space-y-2">
              {filteredNavItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                return (
                  <Button
                    key={item.path}
                    variant="ghost"
                    className={`w-full justify-start ${isActive ? "bg-blue-50 text-blue-700" : "text-slate-600"}`}
                    onClick={() => {
                      navigate(item.path);
                      setMobileMenuOpen(false);
                    }}
                  >
                    <Icon className="w-4 h-4 mr-2" />
                    {item.label}
                  </Button>
                );
              })}
              <a
                href="https://job-matching-ai.preview.emergentagent.com/"
                target="_blank"
                rel="noopener noreferrer"
                className="block"
                data-testid="ubuntoo-link-mobile"
              >
                <Button variant="ghost" className="w-full justify-start text-teal-700 hover:bg-teal-50">
                  <img
                    src="https://customer-assets.emergentagent.com/job_keen-meitner-5/artifacts/t3wjk59k_logo_ubuntoo_transparent.png"
                    alt="Ubuntoo"
                    className="h-4 w-auto mr-2"
                  />
                  Espace Ubuntoo
                </Button>
              </a>
            </nav>
          </div>
        )}
      </header>

      {/* Main Content */}
      <main className="pt-28 pb-8">
        <div className="max-w-[1600px] mx-auto px-4 sm:px-6">
          <Routes>
            <Route path="/" element={<DashboardHome role={role} token={token} refreshKey={refreshKey} />} />
            <Route path="/passeport" element={<PassportView token={token} key={`passport-${refreshKey}`} />} />
            <Route path="/coffre-fort" element={<CoffreFortView token={token} key={`coffre-${refreshKey}`} />} />
            <Route path="/observatoire" element={<ObservatoireView token={token} key={`observatoire-${refreshKey}`} />} />
            <Route path="/explorateur" element={<ExplorateurView token={token} key={`explorateur-${refreshKey}`} />} />
            <Route path="/evolution" element={<EvolutionIndexView token={token} key={`evolution-${refreshKey}`} />} />
            <Route path="/confidentialite" element={<PrivacySettingsView token={token} key={`privacy-${refreshKey}`} />} />
            <Route path="/jobs" element={role === "particulier" ? <ParticulierView token={token} section="jobs" key={`jobs-${refreshKey}`} /> : <EntrepriseView token={token} section="jobs" key={`rh-jobs-${refreshKey}`} />} />
            <Route path="/learning" element={<ParticulierView token={token} section="learning" key={`learning-${refreshKey}`} />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </div>
      </main>
    </div>
  );
};

const DashboardHome = ({ role, token, refreshKey }) => {
  switch (role) {
    case "particulier":
      return <ParticulierView token={token} key={`particulier-${refreshKey}`} />;
    case "entreprise":
      return <EntrepriseView token={token} key={`entreprise-${refreshKey}`} />;
    case "partenaire":
      return <PartenaireView token={token} key={`partenaire-${refreshKey}`} />;
    default:
      return <ParticulierView token={token} key={`default-${refreshKey}`} />;
  }
};

export default Dashboard;
