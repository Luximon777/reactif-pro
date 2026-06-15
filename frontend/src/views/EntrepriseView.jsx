import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/App";
import { Button } from "@/components/ui/button";
import {
  LayoutDashboard, Users, GitBranch, Brain, Sparkles, Handshake,
  FileDown, Settings, Menu, X, ClipboardCheck, Calendar, Heart,
  Rocket, MessageSquare
} from "lucide-react";
import DashboardRH from "./entreprise/DashboardRH";
import CollaborateursView from "./entreprise/CollaborateursView";
import ParcoursPipeline from "./entreprise/ParcoursPipeline";
import CompetencesMap from "./entreprise/CompetencesMap";
import MatchingView from "./entreprise/MatchingView";
import PartenairesRH from "./entreprise/PartenairesRH";
import ExportConformite from "./entreprise/ExportConformite";
import ParametresRH from "./entreprise/ParametresRH";
import DiagnosticRH from "./entreprise/DiagnosticRH";
import EntretiensView from "./entreprise/EntretiensView";
import BarometreQVCT from "./entreprise/BarometreQVCT";
import OnboardingView from "./entreprise/OnboardingView";
import FeedbackView from "./entreprise/FeedbackView";

const NAV_SECTIONS = [
  {
    title: "Pilotage",
    items: [
      { key: "dashboard", label: "Tableau de bord", icon: LayoutDashboard },
      { key: "diagnostic", label: "Diagnostic RH", icon: ClipboardCheck },
      { key: "barometre", label: "Baromètre QVCT", icon: Heart },
    ],
  },
  {
    title: "Collaborateurs",
    items: [
      { key: "collaborateurs", label: "Collaborateurs", icon: Users },
      { key: "onboarding", label: "Onboarding", icon: Rocket },
      { key: "entretiens", label: "Entretiens & Suivi", icon: Calendar },
    ],
  },
  {
    title: "Développement",
    items: [
      { key: "parcours", label: "Parcours & transitions", icon: GitBranch },
      { key: "competences", label: "Compétences & cartographie", icon: Brain },
      { key: "matching", label: "Matching & opportunités", icon: Sparkles },
    ],
  },
  {
    title: "Organisation",
    items: [
      { key: "partenaires", label: "Partenaires de parcours", icon: Handshake },
      { key: "feedback", label: "Feedback & Communication", icon: MessageSquare },
      { key: "export", label: "Export & conformité", icon: FileDown },
      { key: "parametres", label: "Paramètres", icon: Settings },
    ],
  },
];

const EntrepriseView = ({ token }) => {
  const [activeSection, setActiveSection] = useState("dashboard");
  const [profile, setProfile] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    axios.get(`${API}/entreprise/profile?token=${token}`).then(r => setProfile(r.data)).catch(() => {});
    axios.post(`${API}/entreprise/seed-demo?token=${token}`).catch(() => {});
  }, [token]);

  const refresh = () => setRefreshKey(k => k + 1);

  const navigateTo = (section, opts) => {
    setActiveSection(section);
    setSidebarOpen(false);
    if (opts?.collabId) {
      window.__rh_select_collab = opts.collabId;
    }
  };

  const renderContent = () => {
    switch (activeSection) {
      case "dashboard": return <DashboardRH token={token} key={`d-${refreshKey}`} onNavigate={navigateTo} />;
      case "diagnostic": return <DiagnosticRH token={token} key={`dg-${refreshKey}`} />;
      case "barometre": return <BarometreQVCT token={token} key={`bq-${refreshKey}`} />;
      case "collaborateurs": return <CollaborateursView token={token} key={`c-${refreshKey}`} onRefresh={refresh} onNavigate={navigateTo} />;
      case "onboarding": return <OnboardingView token={token} key={`ob-${refreshKey}`} />;
      case "entretiens": return <EntretiensView token={token} key={`et-${refreshKey}`} />;
      case "parcours": return <ParcoursPipeline token={token} key={`p-${refreshKey}`} onRefresh={refresh} onNavigate={navigateTo} />;
      case "competences": return <CompetencesMap token={token} key={`cm-${refreshKey}`} />;
      case "matching": return <MatchingView token={token} key={`m-${refreshKey}`} onNavigate={navigateTo} />;
      case "partenaires": return <PartenairesRH token={token} key={`pt-${refreshKey}`} />;
      case "feedback": return <FeedbackView token={token} key={`fb-${refreshKey}`} />;
      case "export": return <ExportConformite token={token} key={`e-${refreshKey}`} />;
      case "parametres": return <ParametresRH token={token} profile={profile} />;
      default: return <DashboardRH token={token} key={`d-${refreshKey}`} onNavigate={navigateTo} />;
    }
  };

  return (
    <div className="flex min-h-[calc(100vh-120px)]" data-testid="entreprise-rh-view">
      {/* Mobile hamburger */}
      <Button variant="ghost" size="icon" className="fixed top-20 left-2 z-50 lg:hidden bg-white shadow-md"
        onClick={() => setSidebarOpen(!sidebarOpen)} data-testid="sidebar-toggle">
        {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
      </Button>

      {/* Sidebar */}
      <aside className={`
        fixed lg:sticky top-0 left-0 z-40 h-screen lg:h-auto w-64 shrink-0
        bg-white border-r border-slate-200 transition-transform duration-200 overflow-y-auto
        ${sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}
      `}>
        <div className="p-4 border-b border-slate-100">
          <h2 className="text-lg font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>Cockpit RH</h2>
          {profile?.company_name && (
            <p className="text-xs text-emerald-600 font-medium mt-0.5">{profile.company_name}</p>
          )}
        </div>
        <nav className="p-2" data-testid="rh-sidebar-nav">
          {NAV_SECTIONS.map(section => (
            <div key={section.title} className="mb-1">
              <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider px-3 pt-3 pb-1">{section.title}</p>
              {section.items.map(item => {
                const Icon = item.icon;
                const active = activeSection === item.key;
                return (
                  <button key={item.key}
                    className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all
                      ${active
                        ? "bg-emerald-50 text-emerald-700 font-semibold border border-emerald-200"
                        : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                      }`}
                    onClick={() => navigateTo(item.key)}
                    data-testid={`nav-${item.key}`}
                  >
                    <Icon className={`w-4 h-4 ${active ? "text-emerald-600" : "text-slate-400"}`} />
                    {item.label}
                  </button>
                );
              })}
            </div>
          ))}
        </nav>
      </aside>

      {/* Overlay for mobile */}
      {sidebarOpen && <div className="fixed inset-0 z-30 bg-black/20 lg:hidden" onClick={() => setSidebarOpen(false)} />}

      {/* Main content */}
      <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-[1200px]" data-testid="rh-main-content">
        {renderContent()}
      </main>
    </div>
  );
};

export default EntrepriseView;
