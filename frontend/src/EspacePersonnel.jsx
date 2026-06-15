import { useNavigate } from "react-router-dom";
import { LogOut, FileText, Target, Briefcase, GraduationCap, User } from "lucide-react";
import { useState } from "react";

export default function EspacePersonnel() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user") || "null");
  const [activeTab, setActiveTab] = useState("profil");

  if (!user) {
    navigate("/");
    return null;
  }

  const handleLogout = () => {
    localStorage.removeItem("user");
    navigate("/");
  };

  const tabs = [
    { key: "profil", label: "Mon Profil", icon: User },
    { key: "cv", label: "Analyse CV", icon: FileText },
    { key: "competences", label: "Compétences", icon: Target },
    { key: "offres", label: "Offres", icon: Briefcase },
    { key: "formations", label: "Formations", icon: GraduationCap },
  ];

  return (
    <div className="min-h-screen bg-slate-50" data-testid="espace-personnel">
      {/* Header */}
      <header className="bg-white border-b border-slate-100 px-6 py-3 flex items-center justify-between">
        <button onClick={() => navigate("/")} className="flex items-center gap-2">
          <svg width="28" height="28" viewBox="0 0 80 80" fill="none">
            <circle cx="40" cy="40" r="38" stroke="#1e3a5f" strokeWidth="2" fill="#eef2f7"/>
            <circle cx="40" cy="40" r="28" fill="#1e3a5f" opacity="0.08"/>
            <circle cx="40" cy="30" r="8" fill="#4f6df5"/>
            <path d="M26 56 C26 44 34 40 40 40 C46 40 54 44 54 56" fill="#4f6df5" opacity="0.85"/>
          </svg>
          <div className="leading-none">
            <span className="text-sm font-bold" style={{ fontFamily: "Outfit, sans-serif" }}>
              <span className="text-[#1e3a5f]">RE'</span><span className="text-[#4f6df5]">ACTIF</span><span className="text-[#1e3a5f]"> PRO</span>
            </span>
          </div>
        </button>
        <div className="flex items-center gap-3">
          <span className="text-sm text-slate-600 font-medium">{user.pseudonyme}</span>
          <button onClick={handleLogout} className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-500 border border-slate-200 rounded-full hover:bg-red-50 hover:text-red-500 hover:border-red-200 transition" data-testid="logout-btn">
            <LogOut className="w-3.5 h-3.5" /> Déconnexion
          </button>
        </div>
      </header>

      {/* Content */}
      <div className="max-w-6xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-[#1e3a5f] mb-6" style={{ fontFamily: "Outfit, sans-serif" }}>
          Espace Personnel
        </h1>

        {/* Tabs */}
        <div className="flex gap-1 bg-white rounded-xl p-1 border border-slate-200 mb-6">
          {tabs.map((t) => {
            const Icon = t.icon;
            return (
              <button key={t.key} onClick={() => setActiveTab(t.key)}
                className={`flex items-center gap-1.5 px-4 py-2.5 rounded-lg text-xs font-medium transition-all ${activeTab === t.key ? "bg-[#4f6df5] text-white shadow-sm" : "text-slate-500 hover:bg-slate-50"}`}
                data-testid={`tab-${t.key}`}>
                <Icon className="w-3.5 h-3.5" /> {t.label}
              </button>
            );
          })}
        </div>

        {/* Tab Content */}
        <div className="bg-white rounded-xl border border-slate-200 p-8">
          {activeTab === "profil" && (
            <div className="text-center py-12">
              <User className="w-16 h-16 mx-auto text-[#4f6df5] mb-4" />
              <h2 className="text-xl font-bold text-[#1e3a5f] mb-2">Bienvenue, {user.pseudonyme}</h2>
              <p className="text-sm text-slate-500">Votre espace personnel est en cours de construction.<br/>Commencez par analyser votre CV dans l'onglet "Analyse CV".</p>
            </div>
          )}
          {activeTab === "cv" && (
            <div className="text-center py-12">
              <FileText className="w-16 h-16 mx-auto text-[#4f6df5] mb-4" />
              <h2 className="text-xl font-bold text-[#1e3a5f] mb-2">Analyse de CV</h2>
              <p className="text-sm text-slate-500">Déposez votre CV pour une analyse complète de vos compétences.</p>
            </div>
          )}
          {activeTab === "competences" && (
            <div className="text-center py-12">
              <Target className="w-16 h-16 mx-auto text-[#4f6df5] mb-4" />
              <h2 className="text-xl font-bold text-[#1e3a5f] mb-2">Portefeuille de Compétences</h2>
              <p className="text-sm text-slate-500">Visualisez et gérez vos compétences certifiées.</p>
            </div>
          )}
          {activeTab === "offres" && (
            <div className="text-center py-12">
              <Briefcase className="w-16 h-16 mx-auto text-[#4f6df5] mb-4" />
              <h2 className="text-xl font-bold text-[#1e3a5f] mb-2">Offres Compatibles</h2>
              <p className="text-sm text-slate-500">Offres d'emploi correspondant à votre profil.</p>
            </div>
          )}
          {activeTab === "formations" && (
            <div className="text-center py-12">
              <GraduationCap className="w-16 h-16 mx-auto text-[#4f6df5] mb-4" />
              <h2 className="text-xl font-bold text-[#1e3a5f] mb-2">Formations Accessibles</h2>
              <p className="text-sm text-slate-500">Formations recommandées pour votre parcours.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
