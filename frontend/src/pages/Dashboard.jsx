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
  Sparkles,
  Menu,
  X,
  Settings,
  FolderLock,
  Brain,
  Gauge,
  Shield,
  Layers,
  Upload,
  CheckCircle2,
  CheckCircle
} from "lucide-react";
import { toast } from "sonner";
import LogoReactifPro from "@/components/LogoReactifPro";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";

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
  const { token, role, profileId, switchRole, logout, authMode, pseudo } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [isSeeding, setIsSeeding] = useState(false);
  const [dataSeeded, setDataSeeded] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  const [dclicImported, setDclicImported] = useState(false);

  useEffect(() => {
    if (token) {
      axios.get(`${API}/profile?token=${token}`).then(r => {
        setDclicImported(!!r.data?.dclic_imported);
      }).catch(() => {});
    }
  }, [token, refreshKey]);

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
  const [dclicCode, setDclicCode] = useState("");
  const [dclicPreview, setDclicPreview] = useState(null);
  const [dclicProgress, setDclicProgress] = useState(0);
  const [dclicProgressLabel, setDclicProgressLabel] = useState("");

  const handleDclicRetrieve = async () => {
    if (!dclicCode.trim()) return;
    setDclicImporting(true);
    setDclicPreview(null);
    try {
      const res = await axios.post(`${API}/dclic/retrieve`, { access_code: dclicCode.trim() });
      setDclicPreview(res.data.profile);
    } catch (e) {
      toast.error(e.response?.data?.detail || "Code introuvable");
    }
    setDclicImporting(false);
  };

  const handleDclicImport = async () => {
    if (!dclicPreview) return;

    setDclicImporting(true);
    setDclicProgress(0);
    setDclicProgressLabel("Analyse du profil D'CLIC PRO...");

    const steps = [
      { pct: 15, label: "Lecture du profil comportemental...", delay: 800 },
      { pct: 30, label: "Import des compétences RIASEC...", delay: 700 },
      { pct: 45, label: "Intégration du profil MBTI / DISC...", delay: 600 },
      { pct: 60, label: "Chargement des vertus et valeurs...", delay: 700 },
      { pct: 75, label: "Enrichissement de l'espace personnel...", delay: 800 },
      { pct: 85, label: "Mise à jour du diagnostic...", delay: 600 },
    ];

    for (const step of steps) {
      await new Promise(r => setTimeout(r, step.delay));
      setDclicProgress(step.pct);
      setDclicProgressLabel(step.label);
    }

    const payload = {
      target_job: "",
      city: "",
      summary: "",
      mobility: "departement",
      contract_types: [],
      work_modes: [],
      skills:
        dclicPreview.competences_fortes?.map((c) => ({
          name: c,
          category: "comportementale",
          declared_level: 4,
          status: "declaree",
        })) || [],
      experiences: [],
      evidences: [
        {
          title: "Test D'CLIC PRO",
          kind: "attestation",
          source: `Code: ${dclicCode.trim()}`,
        },
      ],
      dclic_profile: dclicPreview,
    };

    try {
      setDclicProgress(90);
      setDclicProgressLabel("Sauvegarde des données...");

      const importRes = await axios.post(
        `${API}/profile/import-dclic?token=${encodeURIComponent(token)}`,
        payload
      );

      setDclicProgress(95);
      setDclicProgressLabel("Validation du code...");

      let claimError = null;

      try {
        await axios.post(
          `${API}/dclic/claim?access_code=${encodeURIComponent(dclicCode.trim())}&user_id=${encodeURIComponent(profileId || "")}`
        );
      } catch (e) {
        claimError = e?.response?.data?.detail || e.message || "Erreur de validation du code";
        console.error("Erreur claim D'CLIC PRO:", e);
      }

      setDclicProgress(100);
      setDclicProgressLabel("Import terminé !");
      await new Promise(r => setTimeout(r, 800));

      if (claimError) {
        toast.success(
          `Profil importé avec succès. Complétion : ${importRes.data.profile_completion}%`
        );
        toast.error(`Le profil a bien été importé, mais le code n'a pas pu être validé : ${claimError}`);
      } else {
        toast.success(
          `Profil D'CLIC PRO importé avec succès ! Complétion : ${importRes.data.profile_completion}%`
        );
      }

      setDclicOpen(false);
      setDclicCode("");
      setDclicPreview(null);
      setRefreshKey((prev) => prev + 1);
    } catch (e) {
      console.error("Erreur import D'CLIC PRO:", e);

      const detail =
        e?.response?.data?.detail ||
        e?.response?.data?.message ||
        e.message ||
        "Erreur lors de l'import";

      toast.error(detail);
    } finally {
      setDclicImporting(false);
      setDclicProgress(0);
      setDclicProgressLabel("");
    }
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
              <a href="https://github.com/Luximon777/ubuntoo" target="_blank" rel="noopener noreferrer"
                className="hidden sm:flex" data-testid="ubuntoo-link">
                <Button variant="outline" size="sm" className="border-teal-200 bg-teal-50 text-teal-700 hover:bg-teal-100 gap-1.5 text-xs">
                  <img src="https://customer-assets.emergentagent.com/job_keen-meitner-5/artifacts/t3wjk59k_logo_ubuntoo_transparent.png"
                    alt="Ubuntoo" className="h-4 w-auto" />
                  <span className="hidden lg:inline">Ubuntoo</span>
                </Button>
              </a>

              {/* D'CLIC PRO Import - Mise en valeur */}
              <Dialog open={dclicOpen} onOpenChange={(o) => { setDclicOpen(o); if (!o) { setDclicPreview(null); setDclicCode(""); } }}>
                {role === "particulier" && !dclicImported && (
                  <DialogTrigger asChild>
                    <Button className="bg-gradient-to-r from-[#4f6df5] to-[#10b981] hover:from-[#6366f1] hover:to-[#22c55e] text-white shadow-lg shadow-[#4f6df5]/20 animate-pulse hover:animate-none text-xs font-semibold" data-testid="dclic-import-btn">
                      <Upload className="w-4 h-4 mr-1.5" />
                      <span className="hidden md:inline">Boost mon profil avec D'CLIC PRO</span>
                      <span className="md:hidden">D'CLIC PRO</span>
                    </Button>
                  </DialogTrigger>
                )}
                {role === "particulier" && dclicImported && (
                  <Button className="bg-gradient-to-r from-emerald-500 to-teal-500 text-white text-xs font-semibold cursor-default" disabled data-testid="dclic-imported-badge">
                    <CheckCircle className="w-4 h-4 mr-1.5" />
                    <span className="hidden md:inline">Profil boosté</span>
                    <span className="md:hidden">Boosté</span>
                  </Button>
                )}
                <DialogContent className="sm:max-w-[500px]" data-testid="dclic-dialog">
                  <DialogHeader>
                    <DialogTitle className="flex items-center gap-2 text-[#1e3a5f]">
                      <Upload className="w-5 h-5" />Boost mon profil avec D'CLIC PRO
                    </DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4">
                    <p className="text-sm text-slate-500">Saisissez le code d'accès généré à la fin de votre test D'CLIC PRO pour importer votre profil personnalité et compétences.</p>

                    <div className="flex gap-2">
                      <Input 
                        placeholder="XXXX-XXXX" 
                        className="text-center text-lg font-mono tracking-widest uppercase" 
                        value={dclicCode} 
                        onChange={e => setDclicCode(e.target.value.toUpperCase())} 
                        maxLength={9} 
                        data-testid="dclic-code-input" 
                      />
                      <Button onClick={handleDclicRetrieve} disabled={dclicImporting || dclicCode.length < 9} data-testid="dclic-retrieve-btn">
                        {dclicImporting && !dclicPreview ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : "Vérifier"}
                      </Button>
                    </div>

                    {dclicPreview && (
                      <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4 space-y-3" data-testid="dclic-preview">
                        <div className="flex items-center gap-2">
                          <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                          <span className="font-semibold text-emerald-800">Profil trouvé !</span>
                        </div>
                        <div className="grid grid-cols-2 gap-2 text-sm">
                          <div className="bg-white rounded p-2 text-center">
                            <p className="text-xs text-slate-500">MBTI</p>
                            <p className="font-bold text-violet-700">{dclicPreview.mbti}</p>
                          </div>
                          <div className="bg-white rounded p-2 text-center">
                            <p className="text-xs text-slate-500">DISC</p>
                            <p className="font-bold text-blue-700">{dclicPreview.disc_dominant_name}</p>
                          </div>
                          <div className="bg-white rounded p-2 text-center">
                            <p className="text-xs text-slate-500">Vertu</p>
                            <p className="font-bold text-emerald-700">{dclicPreview.vertu_dominante_name}</p>
                          </div>
                          <div className="bg-white rounded p-2 text-center">
                            <p className="text-xs text-slate-500">RIASEC</p>
                            <p className="font-bold text-amber-700">{dclicPreview.riasec_major_name}</p>
                          </div>
                        </div>
                        {dclicPreview.competences_fortes?.length > 0 && (
                          <div>
                            <p className="text-xs font-medium text-slate-600 mb-1">Compétences :</p>
                            <div className="flex flex-wrap gap-1">
                              {dclicPreview.competences_fortes.map((c, i) => (
                                <Badge key={i} className="bg-indigo-100 text-indigo-700 text-xs">{c}</Badge>
                              ))}
                            </div>
                          </div>
                        )}
                        <Button className="w-full bg-[#1e3a5f] hover:bg-[#2d4a6f]" onClick={handleDclicImport} disabled={dclicImporting} data-testid="dclic-submit-btn">
                          {!dclicImporting && <Upload className="w-4 h-4 mr-2" />}
                          {!dclicImporting && "Importer dans mon profil Re'Actif Pro"}
                        </Button>
                        {dclicImporting && (
                          <div className="mt-4 space-y-3" data-testid="dclic-progress">
                            <div className="flex items-center justify-between text-sm">
                              <span className="text-slate-600 font-medium">{dclicProgressLabel}</span>
                              <span className="text-indigo-600 font-bold">{dclicProgress}%</span>
                            </div>
                            <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
                              <div className="h-full bg-gradient-to-r from-[#4f6df5] to-[#10b981] rounded-full transition-all duration-500 ease-out" style={{ width: `${dclicProgress}%` }} />
                            </div>
                            <div className="flex justify-center">
                              <div className="flex items-center gap-2 text-xs text-slate-500">
                                <div className="w-3 h-3 border-2 border-[#4f6df5]/30 border-t-[#4f6df5] rounded-full animate-spin" />
                                Veuillez patienter...
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                    <p className="text-xs text-slate-400 text-center">Pas encore de code ? <a href="/test-dclic" className="text-indigo-600 underline font-medium">Passez le test D'CLIC PRO</a></p>
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
                href="https://github.com/Luximon777/ubuntoo"
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
            <Route path="/" element={<DashboardHome role={role} token={token} refreshKey={refreshKey} onOpenDclic={() => setDclicOpen(true)} />} />
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

const DashboardHome = ({ role, token, refreshKey, onOpenDclic }) => {
  switch (role) {
    case "particulier":
      return <ParticulierView token={token} onOpenDclic={onOpenDclic} key={`particulier-${refreshKey}`} />;
    case "entreprise":
      return <EntrepriseView token={token} key={`entreprise-${refreshKey}`} />;
    case "partenaire":
      return <PartenaireView token={token} key={`partenaire-${refreshKey}`} />;
    default:
      return <ParticulierView token={token} onOpenDclic={onOpenDclic} key={`default-${refreshKey}`} />;
  }
};

export default Dashboard;
