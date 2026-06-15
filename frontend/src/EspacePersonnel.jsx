import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth, API } from "@/App";
import {
  Home, User, Route, Sparkles, Globe, DoorOpen, CalendarDays,
  FolderOpen, Shield, Bell, LogOut, ChevronRight, Play,
  Upload, Award, Compass, Target, MessageSquare, X, Minus,
  Trash2, HelpCircle, CheckCircle2, Circle
} from "lucide-react";

const TABS = [
  { id: "accueil", label: "Accueil", icon: Home },
  { id: "profil", label: "Profil", icon: User },
  { id: "trajectoire", label: "Trajectoire", icon: Route },
  { id: "competences", label: "Compétences", icon: Sparkles },
  { id: "marche", label: "Marché", icon: Globe },
  { id: "opportunites", label: "Opportunités", icon: DoorOpen },
  { id: "jobdating", label: "Job Dating", icon: CalendarDays },
  { id: "portefeuille", label: "Portefeuille", icon: FolderOpen },
  { id: "confidentialite", label: "Confidentialité", icon: Shield },
];

const ETAPES = [
  {
    num: 1,
    title: "Comprendre qui je suis",
    subtitle: "Personnalité, valeurs et compétences",
    icon: User,
    color: "text-indigo-600",
    bgColor: "bg-indigo-50",
    tasks: [
      { id: "cv", label: "Importer et analyser mon CV" },
      { id: "dclic", label: "Passer le test D'CLIC PRO" },
      { id: "interets", label: "Identifier mes centres d'intérêt" },
    ],
  },
  {
    num: 2,
    title: "Me valoriser",
    subtitle: "Prouver mes soft skills par des exemples concrets",
    icon: Award,
    color: "text-violet-600",
    bgColor: "bg-violet-50",
    tasks: [
      { id: "softskills", label: "Documenter mes soft skills" },
      { id: "exemples", label: "Ajouter des exemples concrets" },
    ],
  },
  {
    num: 3,
    title: "Clarifier ma vision de mon profil compétences",
    subtitle: "Synthèse et projection professionnelle",
    icon: Target,
    color: "text-blue-600",
    bgColor: "bg-blue-50",
    tasks: [
      { id: "synthese", label: "Générer ma synthèse de compétences" },
      { id: "projection", label: "Définir mon projet professionnel" },
    ],
  },
  {
    num: 4,
    title: "Construire ma trajectoire",
    subtitle: "Plan d'action et mise en mouvement",
    icon: Compass,
    color: "text-emerald-600",
    bgColor: "bg-emerald-50",
    tasks: [
      { id: "plan", label: "Créer mon plan d'action" },
      { id: "candidatures", label: "Lancer mes candidatures" },
    ],
  },
];

const COACH_ACTIONS = [
  { id: "cv", icon: Upload, label: "Importer votre CV", badge: "En cours", link: "Aller dans Trajectoire > Mon CV", primary: true },
  { id: "valoriser", icon: Award, label: "Me valoriser — Prouver mes soft skills" },
  { id: "boost", icon: Sparkles, label: "Booster avec D'CLIC PRO" },
  { id: "trajectoire", icon: Compass, label: "Tracer votre trajectoire" },
];

export default function EspacePersonnel() {
  const navigate = useNavigate();
  const { pseudonyme, token, logout } = useAuth();
  const [activeTab, setActiveTab] = useState("accueil");
  const [completedTasks, setCompletedTasks] = useState({});
  const [coachOpen, setCoachOpen] = useState(true);
  const [coachMinimized, setCoachMinimized] = useState(false);
  const userName = pseudonyme || "utilisateur";

  const totalTasks = ETAPES.reduce((sum, e) => sum + e.tasks.length, 0);
  const doneTasks = Object.values(completedTasks).filter(Boolean).length;
  const progress = totalTasks > 0 ? Math.round((doneTasks / totalTasks) * 100) : 0;
  const currentPhase = progress < 25 ? "Découverte de ton potentiel" : progress < 50 ? "Valorisation de tes compétences" : progress < 75 ? "Clarification de ton profil" : "Construction de ta trajectoire";
  const completedSteps = ETAPES.filter(e => e.tasks.every(t => completedTasks[t.id])).length;

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  const toggleTask = (taskId) => {
    setCompletedTasks(prev => ({ ...prev, [taskId]: !prev[taskId] }));
  };

  return (
    <div className="min-h-screen bg-slate-50" data-testid="espace-personnel">
      {/* ═══ HEADER ═══ */}
      <header className="sticky top-0 z-50 bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-[1400px] mx-auto px-4 sm:px-6 flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate("/")} data-testid="header-logo">
            <div className="w-9 h-9 rounded-full bg-indigo-50 flex items-center justify-center border border-indigo-100">
              <svg width="20" height="20" viewBox="0 0 80 80" fill="none"><circle cx="40" cy="40" r="38" stroke="#1e3a5f" strokeWidth="2" fill="#eef2f7"/><circle cx="40" cy="30" r="8" fill="#4f6df5"/><path d="M26 56 C26 44 34 40 40 40 C46 40 54 44 54 56" fill="#4f6df5" opacity="0.85"/></svg>
            </div>
            <div className="flex flex-col leading-none">
              <span className="font-bold text-sm tracking-tight" style={{ fontFamily: "Outfit, sans-serif" }}>
                <span className="text-[#1e3a5f]">RE'</span><span className="text-[#4f6df5]">ACTIF</span><span className="text-[#1e3a5f]"> PRO</span>
              </span>
              <span className="text-[6px] font-semibold tracking-[0.2em] text-[#6c5ce7] uppercase">Intelligence Professionnelle</span>
            </div>
          </div>

          {/* Right side */}
          <div className="flex items-center gap-3">
            <span className="text-sm font-medium text-slate-700" data-testid="header-username">{userName}</span>
            <button className="p-2 rounded-full hover:bg-slate-100 text-slate-400 relative" data-testid="header-notifications">
              <Bell className="w-5 h-5" />
            </button>
            <button
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-700 text-sm font-medium hover:bg-emerald-100 transition-colors"
              onClick={() => navigate("/ubuntoo")}
              data-testid="header-ubuntoo"
            >
              <img src="https://customer-assets.emergentagent.com/job_keen-meitner-5/artifacts/t3wjk59k_logo_ubuntoo_transparent.png" alt="" className="h-4 w-auto" />
              Ubuntoo
            </button>
            <button
              className="flex items-center gap-2 px-4 py-1.5 rounded-lg text-white text-sm font-semibold transition-colors"
              style={{ background: "linear-gradient(135deg, #6c5ce7, #4f6df5)" }}
              data-testid="header-boost"
            >
              <Sparkles className="w-4 h-4" />
              Boost mon profil avec D'CLIC PRO
            </button>
            <button className="p-2 rounded-full hover:bg-slate-100 text-slate-400" onClick={handleLogout} data-testid="header-logout">
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      {/* ═══ NAVIGATION TABS ═══ */}
      <nav className="bg-white border-b border-slate-200" data-testid="nav-tabs">
        <div className="max-w-[1400px] mx-auto px-4 sm:px-6">
          <div className="flex items-center gap-0.5 overflow-x-auto py-1" style={{ scrollbarWidth: "none" }}>
            {TABS.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  data-testid={`tab-${tab.id}`}
                  className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${
                    isActive
                      ? "bg-indigo-50 text-indigo-700 border border-indigo-200"
                      : "text-slate-500 hover:text-slate-700 hover:bg-slate-50"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>
      </nav>

      {/* ═══ WELCOME BANNER ═══ */}
      <div className="relative overflow-hidden" style={{ background: "linear-gradient(135deg, #1e3a5f 0%, #20215c 60%, #2d1b69 100%)" }} data-testid="welcome-banner">
        <div className="max-w-[1400px] mx-auto px-6 py-8">
          <h1 className="text-3xl font-bold text-white mb-1" style={{ fontFamily: "Outfit, sans-serif" }} data-testid="welcome-title">
            Bonjour {userName}
          </h1>
          <p className="text-blue-200 text-base mb-5">
            Tu es en phase : <strong className="text-white">{currentPhase}</strong>
          </p>
          <div className="flex items-center gap-4 mb-3">
            <span className="text-blue-200 text-sm font-medium">Progression de ton parcours</span>
            <span className="text-white font-bold text-sm">{progress}%</span>
          </div>
          <div className="w-full max-w-md h-2.5 bg-white/20 rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{ width: `${Math.max(progress, 2)}%`, background: "linear-gradient(90deg, #4f6df5, #6c5ce7)" }}
              data-testid="progress-bar"
            />
          </div>
          <div className="mt-4 flex items-center gap-2 bg-white/10 rounded-lg px-4 py-2.5 w-fit">
            <Play className="w-4 h-4 text-blue-300" fill="currentColor" />
            <span className="text-blue-100 text-sm">
              Prochaine action : <strong className="text-white">Aller dans Trajectoire &gt; Mon CV</strong>
            </span>
          </div>
        </div>
      </div>

      {/* ═══ MAIN CONTENT ═══ */}
      <div className="max-w-[1400px] mx-auto px-4 sm:px-6 py-8">
        <div className="flex gap-6">
          {/* Steps Column */}
          <div className="flex-1 space-y-5">
            {ETAPES.map((etape) => {
              const Icon = etape.icon;
              const allDone = etape.tasks.every(t => completedTasks[t.id]);
              return (
                <div
                  key={etape.num}
                  className={`bg-white rounded-2xl border shadow-sm overflow-hidden transition-all ${allDone ? "border-green-200" : "border-slate-200"}`}
                  data-testid={`etape-${etape.num}`}
                >
                  <div className="p-6">
                    <div className="flex items-start gap-4">
                      <div className={`w-10 h-10 rounded-xl ${etape.bgColor} flex items-center justify-center flex-shrink-0`}>
                        <Icon className={`w-5 h-5 ${etape.color}`} />
                      </div>
                      <div className="flex-1">
                        <p className={`text-xs font-bold uppercase tracking-wider ${etape.color} mb-1`}>Étape {etape.num}</p>
                        <h3 className="text-lg font-bold text-slate-900">{etape.title}</h3>
                        <p className="text-sm text-slate-500 mt-0.5">{etape.subtitle}</p>

                        <div className="mt-4 space-y-2.5">
                          {etape.tasks.map((task) => (
                            <button
                              key={task.id}
                              onClick={() => toggleTask(task.id)}
                              className="flex items-center gap-3 w-full text-left group"
                              data-testid={`task-${task.id}`}
                            >
                              {completedTasks[task.id] ? (
                                <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0" />
                              ) : (
                                <Circle className="w-5 h-5 text-slate-300 group-hover:text-indigo-400 flex-shrink-0" />
                              )}
                              <span className={`text-sm ${completedTasks[task.id] ? "text-green-700 line-through" : "text-slate-700 group-hover:text-slate-900"}`}>
                                {task.label}
                              </span>
                            </button>
                          ))}
                        </div>

                        <button
                          className="mt-4 flex items-center gap-2 text-sm text-indigo-500 hover:text-indigo-700 transition-colors"
                          data-testid={`coach-hint-${etape.num}`}
                        >
                          <MessageSquare className="w-4 h-4" />
                          Coach IA : cliquez pour etre guidé sur cette etape
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* ═══ COACH RE'ACTIF WIDGET ═══ */}
      {coachOpen && (
        <div
          className={`fixed right-6 z-40 bg-white rounded-2xl shadow-2xl border border-slate-200 transition-all ${coachMinimized ? "bottom-6 w-72" : "bottom-6 w-96"}`}
          style={{ maxHeight: coachMinimized ? "auto" : "80vh" }}
          data-testid="coach-widget"
        >
          {/* Coach Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center">
                <MessageSquare className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="font-bold text-sm text-slate-900">Coach RE'ACTIF</p>
                <p className="text-xs text-slate-500">{completedSteps}/4 étapes</p>
              </div>
            </div>
            <div className="flex items-center gap-1">
              <button className="p-1.5 rounded hover:bg-slate-100 text-slate-400" data-testid="coach-clear">
                <Trash2 className="w-4 h-4" />
              </button>
              <button className="p-1.5 rounded hover:bg-slate-100 text-slate-400" onClick={() => setCoachMinimized(!coachMinimized)} data-testid="coach-minimize">
                <Minus className="w-4 h-4" />
              </button>
              <button className="p-1.5 rounded hover:bg-slate-100 text-slate-400" onClick={() => setCoachOpen(false)} data-testid="coach-close">
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Progress bar */}
          <div className="px-4 pt-2">
            <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
              <div className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-violet-500 transition-all" style={{ width: `${(completedSteps / 4) * 100}%` }} />
            </div>
          </div>

          {!coachMinimized && (
            <div className="px-4 py-4 space-y-4 overflow-y-auto" style={{ maxHeight: "60vh" }}>
              {/* Welcome message */}
              <div className="bg-slate-50 rounded-xl p-4 text-sm text-slate-700 leading-relaxed" data-testid="coach-message">
                Bienvenue ! Pour commencer, rendez-vous dans l'onglet <strong>Trajectoire</strong> puis cliquez sur le sous-onglet <strong>Mon CV</strong> pour déposer votre fichier. L'IA analysera vos expériences et construira automatiquement votre profil.
              </div>

              {/* Quick Actions */}
              <div className="space-y-2">
                {COACH_ACTIONS.map((action) => {
                  const Icon = action.icon;
                  return (
                    <button
                      key={action.id}
                      className={`w-full flex items-center gap-3 p-3 rounded-xl text-left transition-all ${
                        action.primary
                          ? "bg-indigo-50 border border-indigo-200 hover:bg-indigo-100"
                          : "bg-white border border-slate-100 hover:bg-slate-50 hover:border-slate-200"
                      }`}
                      data-testid={`coach-action-${action.id}`}
                      onClick={() => {
                        if (action.id === "cv") setActiveTab("trajectoire");
                      }}
                    >
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${action.primary ? "bg-indigo-100" : "bg-slate-50"}`}>
                        <Icon className={`w-4 h-4 ${action.primary ? "text-indigo-600" : "text-slate-500"}`} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className={`text-sm font-medium ${action.primary ? "text-indigo-900" : "text-slate-700"}`}>{action.label}</p>
                        {action.badge && (
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-100 text-amber-700 font-medium">{action.badge}</span>
                            {action.link && (
                              <span className="text-xs text-indigo-500 flex items-center gap-1">
                                {action.link} <ChevronRight className="w-3 h-3" />
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    </button>
                  );
                })}
              </div>

              {/* Help input */}
              <div className="flex items-center gap-2 p-3 bg-slate-50 rounded-xl border border-slate-100">
                <HelpCircle className="w-4 h-4 text-slate-400 flex-shrink-0" />
                <input
                  type="text"
                  placeholder="Besoin d'aide ? Posez-moi une question..."
                  className="flex-1 bg-transparent text-sm text-slate-600 placeholder:text-slate-400 outline-none"
                  data-testid="coach-input"
                />
              </div>
            </div>
          )}
        </div>
      )}

      {/* Coach toggle button (when closed) */}
      {!coachOpen && (
        <button
          className="fixed bottom-6 right-6 w-14 h-14 rounded-full shadow-lg flex items-center justify-center z-40 transition-transform hover:scale-110"
          style={{ background: "linear-gradient(135deg, #4f6df5, #6c5ce7)" }}
          onClick={() => setCoachOpen(true)}
          data-testid="coach-toggle"
        >
          <MessageSquare className="w-6 h-6 text-white" />
        </button>
      )}
    </div>
  );
}
