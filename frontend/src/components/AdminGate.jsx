import { useState, useEffect } from "react";
import axios from "axios";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  ShieldCheck, Code2, Eye, Lock, Users, Building2, Handshake,
  ChevronRight, Loader2, Compass, Briefcase, MapPin, Lightbulb, CheckCircle2,
  X, Check, LockKeyhole, BarChart3
} from "lucide-react";
import { toast } from "sonner";
import LogoReactifPro from "@/components/LogoReactifPro";
import AuthModal from "@/components/AuthModal";
import ProRegisterModal from "@/components/ProRegisterModal";

const API = `${process.env.REACT_APP_BACKEND_URL || ""}/api`;

const GATE_PASSWORDS = {
  admin: "Choukette@777",
  programmeur: "Reactif@pro2026!",
  invite: "Reactif@pro2026!",
};

const STATUSES = [
  { key: "admin", label: "Admin", fullLabel: "Administrateur principal", icon: ShieldCheck, color: "bg-emerald-600", text: "text-emerald-700", bg: "bg-emerald-50 border-emerald-200 hover:bg-emerald-100" },
  { key: "programmeur", label: "Dev", fullLabel: "Développeur", icon: Code2, color: "bg-blue-600", text: "text-blue-700", bg: "bg-blue-50 border-blue-200 hover:bg-blue-100" },
  { key: "invite", label: "Invité", fullLabel: "Invité (lecture seule)", icon: Eye, color: "bg-slate-500", text: "text-slate-600", bg: "bg-slate-50 border-slate-200 hover:bg-slate-100" },
];

const SPACES = [
  {
    key: "personnel",
    label: "Espace Personnel",
    description: "Révélez et valorisez vos compétences réelles pour construire des trajectoires professionnelles durables",
    icon: Users,
    iconColor: "bg-[#1e3a5f] text-white",
    btnColor: "bg-[#1e3a5f] hover:bg-[#2d5a8e] text-white",
    features: ["Portefeuille de Compétences Certifiées", "Identité professionnelle sécurisée", "Orientation personnalisée"],
    loginType: "pseudo",
    credentials: { pseudo: "reactif_admin", password: "Choukette@777" },
  },
  {
    key: "vsi",
    label: "Parcours VSI",
    description: "Valorisez votre Identité Professionnelle — Accompagnement hybride présentiel & distanciel pour révéler votre potentiel",
    icon: Compass,
    iconColor: "bg-amber-600 text-white",
    btnColor: "bg-amber-600 hover:bg-amber-700 text-white",
    features: ["Ateliers VSI en présentiel / visio", "Diagnostic identitaire approfondi", "Plan d'action personnalisé"],
    loginType: "pseudo",
    credentials: { pseudo: "reactif_admin", password: "Choukette@777" },
  },
  {
    key: "employeur",
    label: "Espace Employeurs",
    description: "Identifiez les talents et compétences en adéquation avec vos besoins économiques",
    icon: Building2,
    iconColor: "bg-emerald-600 text-white",
    btnColor: "bg-emerald-600 hover:bg-emerald-700 text-white",
    features: ["Cockpit RH complet", "Matching & opportunités", "Baromètre QVCT"],
    loginType: "pro",
    credentials: { pseudo: "rh@reactifpro.fr", password: "Reactif@pro2026!" },
  },
  {
    key: "partenaire",
    label: "Appui aux parcours",
    description: "Interface de coordination pour les acteurs de l'accompagnement — en complémentarité des dispositifs existants",
    icon: Handshake,
    iconColor: "bg-violet-600 text-white",
    btnColor: "bg-violet-600 hover:bg-violet-700 text-white",
    features: ["Diagnostic enrichi", "Coordination des parcours", "Contribution territoriale"],
    loginType: "pro",
    credentials: { pseudo: "admin@reactifpro.fr", password: "Choukette@777" },
  },
];

const AdminGate = ({ onAuthenticated }) => {
  const [selectedStatus, setSelectedStatus] = useState(null);
  const [authenticated, setAuthenticated] = useState(false);
  const [showPasswordFor, setShowPasswordFor] = useState(null);
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [proModalOpen, setProModalOpen] = useState(false);
  const [proModalRole, setProModalRole] = useState("entreprise");
  const [postAuthRedirect, setPostAuthRedirect] = useState(null);
  const [spacesOpen, setSpacesOpen] = useState(false);
  const [gateLoading, setGateLoading] = useState(true);
  const [opcSelectorOpen, setOpcSelectorOpen] = useState(false);
  const [togglingSpaces, setTogglingSpaces] = useState(false);

  // Fetch server-side gate state on mount
  useEffect(() => {
    axios.get(`${API}/admin/gate-state`)
      .then(res => setSpacesOpen(res.data.spaces_open === true))
      .catch(() => setSpacesOpen(false))
      .finally(() => setGateLoading(false));
  }, []);

  const toggleSpacesOpen = async () => {
    if (togglingSpaces) return; // anti double-click
    setTogglingSpaces(true);
    const next = !spacesOpen;
    try {
      const res = await axios.post(`${API}/admin/gate-state`, {
        password: GATE_PASSWORDS.admin,
        spaces_open: next,
      });
      setSpacesOpen(res.data.spaces_open === true);
      toast.success(res.data.spaces_open ? "Espaces ouverts au public" : "Espaces fermés");
    } catch (e) {
      const detail = e?.response?.data?.detail || e?.message || "réseau indisponible";
      toast.error(`Impossible de changer l'état : ${detail}`);
    } finally {
      setTogglingSpaces(false);
    }
  };

  const handleStatusClick = (status) => {
    if (authenticated && selectedStatus?.key === status.key) return;
    setShowPasswordFor(status);
    setPassword("");
    setError("");
  };

  const handlePasswordSubmit = (e) => {
    e.preventDefault();
    if (password === GATE_PASSWORDS[showPasswordFor.key]) {
      setSelectedStatus(showPasswordFor);
      setAuthenticated(true);
      setShowPasswordFor(null);
      setError("");
      toast.success(`Connexion ${showPasswordFor.fullLabel || showPasswordFor.label} réussie`);
    } else {
      setError("Mot de passe incorrect");
    }
  };

  const [authModalDefaultRole, setAuthModalDefaultRole] = useState("particulier");

  const handleSpaceSelect = async (space) => {
    if (!spacesOpen) {
      toast.info("Les accès sont actuellement fermés par l'administrateur.");
      return;
    }
    // Admin bypass for employer/partner only — personnel & vsi always shows auth modal
    if (authenticated && selectedStatus?.key === "admin" && space.key !== "personnel" && space.key !== "vsi" && space.key !== "observatoire") {
      setLoading(true);
      try {
        let loginData;
        if (space.key === "employeur") {
          const res = await axios.post(`${API}/auth/login-pro`, { pseudo: "rh@reactifpro.fr", password: "Reactif@pro2026!" });
          loginData = { ...res.data, role: "entreprise", authMode: "pseudo" };
        } else {
          const res = await axios.post(`${API}/auth/login-pro`, { pseudo: "admin@reactifpro.fr", password: "Choukette@777" });
          loginData = { ...res.data, role: "partenaire", authMode: "pseudo" };
        }
        const displayName = loginData.company_name || loginData.pseudo;
        localStorage.setItem("reactif_token", loginData.token);
        localStorage.setItem("reactif_role", loginData.role);
        localStorage.setItem("reactif_profile_id", loginData.profile_id || "");
        localStorage.setItem("reactif_auth_mode", loginData.authMode);
        if (displayName) localStorage.setItem("reactif_pseudo", displayName);
        if (postAuthRedirect) {
          localStorage.setItem("reactif_post_redirect", postAuthRedirect);
          setPostAuthRedirect(null);
        }
        onAuthenticated({
          token: loginData.token,
          role: loginData.role,
          profileId: loginData.profile_id,
          pseudo: displayName,
          authMode: loginData.authMode,
          adminStatus: "admin",
          isReadOnly: false,
        });
      } catch (err) {
        toast.error("Erreur de connexion automatique");
        console.error(err);
      }
      setLoading(false);
      return;
    }
    if (space.key === "personnel") {
      setAuthModalDefaultRole("particulier");
      setAuthModalOpen(true);
    } else if (space.key === "vsi") {
      setAuthModalDefaultRole("vsi");
      setAuthModalOpen(true);
    } else if (space.key === "observatoire") {
      window.location.href = "/observatoire";
      return;
    } else if (space.key === "employeur") {
      setProModalRole("entreprise");
      setProModalOpen(true);
    } else {
      setProModalRole("partenaire");
      setProModalOpen(true);
    }
  };

  const handleModalSuccess = () => {
    const token = localStorage.getItem("reactif_token");
    const role = localStorage.getItem("reactif_role");
    const profileId = localStorage.getItem("reactif_profile_id");
    const pseudo = localStorage.getItem("reactif_pseudo");
    const authMode = localStorage.getItem("reactif_auth_mode");
    if (postAuthRedirect) {
      localStorage.setItem("reactif_post_redirect", postAuthRedirect);
      setPostAuthRedirect(null);
    }
    onAuthenticated({
      token, role, profileId, pseudo, authMode,
      adminStatus: selectedStatus?.key || "user",
      isReadOnly: selectedStatus?.key === "invite",
    });
    setAuthModalOpen(false);
    setProModalOpen(false);
  };

  return (
    <div className="min-h-screen bg-white" data-testid="admin-gate">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-slate-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <LogoReactifPro size="sm" />
              <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-amber-50 border border-amber-200 text-amber-600 text-[10px] font-medium">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
                En construction
              </span>
            </div>

            {/* Status buttons - top right */}
            <div className="flex items-center gap-2 relative" data-testid="status-selector">
              {STATUSES.map((s) => {
                const Icon = s.icon;
                const isActive = authenticated && selectedStatus?.key === s.key;
                return (
                  <button
                    key={s.key}
                    onClick={() => handleStatusClick(s)}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border transition-all
                      ${isActive
                        ? `${s.bg} ${s.text} border-current ring-1 ring-current/20`
                        : "bg-white border-slate-200 text-slate-500 hover:border-slate-300 hover:text-slate-700"
                      }`}
                    data-testid={`status-${s.key}`}
                  >
                    <Icon className="w-3.5 h-3.5" />
                    <span className="hidden sm:inline">{s.label}</span>
                    {isActive && <CheckCircle2 className="w-3 h-3" />}
                  </button>
                );
              })}

              {/* Admin toggle - accès ouverts/fermés */}
              {authenticated && selectedStatus?.key === "admin" && (
                <button
                  onClick={toggleSpacesOpen}
                  disabled={togglingSpaces || gateLoading}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border transition-all ${
                    togglingSpaces ? "opacity-50 cursor-wait" : ""
                  } ${
                    spacesOpen
                      ? "bg-emerald-50 border-emerald-300 text-emerald-700 hover:bg-emerald-100"
                      : "bg-red-50 border-red-300 text-red-600 hover:bg-red-100"
                  }`}
                  data-testid="toggle-spaces-open"
                >
                  {togglingSpaces
                    ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    : (spacesOpen
                        ? <Check className="w-3.5 h-3.5" strokeWidth={3} />
                        : <X className="w-3.5 h-3.5" strokeWidth={3} />)
                  }
                  <span className="hidden sm:inline">{spacesOpen ? "Ouverts" : "Fermés"}</span>
                </button>
              )}

              {/* Password dropdown */}
              {showPasswordFor && (
                <div className="absolute top-full right-0 mt-2 w-72 bg-white rounded-xl shadow-xl border border-slate-200 p-4 z-[60]" data-testid="step-password">
                  <div className="flex items-center gap-2 mb-3">
                    <div className={`w-7 h-7 rounded-lg ${showPasswordFor.color} flex items-center justify-center`}>
                      {(() => { const I = showPasswordFor.icon; return <I className="w-3.5 h-3.5 text-white" />; })()}
                    </div>
                    <span className="text-sm font-semibold text-slate-900">{showPasswordFor.fullLabel}</span>
                  </div>
                  <form onSubmit={handlePasswordSubmit}>
                    <div className="flex gap-2">
                      <Input
                        type="password"
                        placeholder="Mot de passe..."
                        value={password}
                        onChange={(e) => { setPassword(e.target.value); setError(""); }}
                        className="h-9 text-sm"
                        autoFocus
                        data-testid="gate-password-input"
                      />
                      <Button type="submit" size="sm" className="bg-emerald-600 hover:bg-emerald-700 h-9 px-4" data-testid="gate-submit">
                        <Lock className="w-3.5 h-3.5" />
                      </Button>
                    </div>
                    {error && <p className="text-red-500 text-xs mt-1.5" data-testid="gate-error">{error}</p>}
                  </form>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="pt-24 pb-16 px-4 bg-[#1e3a5f] text-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-4xl mx-auto py-16">
            <div className="flex justify-center mb-8">
              <div className="bg-white/95 rounded-2xl shadow-lg p-8">
                <LogoReactifPro size="xl" />
              </div>
            </div>
            <p className="text-xl sm:text-2xl text-blue-100 mb-4 italic">
              Dispositif de réactivation rapide des parcours vers l'emploi
            </p>
            <div className="flex flex-wrap items-center justify-center gap-3 text-blue-200 mt-8">
              <span className="flex items-center gap-2"><Compass className="w-4 h-4" />Orientation</span>
              <span className="text-blue-400">•</span>
              <span className="flex items-center gap-2"><Briefcase className="w-4 h-4" />Emploi</span>
              <span className="text-blue-400">•</span>
              <span className="flex items-center gap-2"><MapPin className="w-4 h-4" />Mobilité</span>
              <span className="text-blue-400">•</span>
              <span className="flex items-center gap-2"><Lightbulb className="w-4 h-4" />Innovation sociale</span>
            </div>

            {!authenticated && (
              <p className="mt-8 text-blue-200/70 text-sm">
                Équipe RE'ACTIF PRO : sélectionnez votre statut en haut à droite
              </p>
            )}
          </div>
        </div>
      </section>

      {/* Hub Layout - OPC Center with Spaces */}
      <section className="py-16 px-4 bg-gradient-to-b from-slate-50 to-white">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-[#1e3a5f] mb-2" style={{ fontFamily: 'Outfit, sans-serif' }}>
              Vos accès
            </h2>
            <p className="text-sm text-slate-500">
              Choisissez votre espace pour accéder à vos outils personnalisés
            </p>
            {authenticated && selectedStatus && selectedStatus.key !== "admin" && (
              <div className="flex items-center justify-center gap-2 mt-3">
                <Badge className={`${selectedStatus.bg} ${selectedStatus.text} text-sm px-3 py-1`}>
                  {(() => { const I = selectedStatus.icon; return <I className="w-3.5 h-3.5 mr-1.5 inline" />; })()}
                  {selectedStatus.fullLabel}
                </Badge>
                {selectedStatus.key === "invite" && (
                  <Badge className="bg-amber-50 text-amber-700 border-amber-200">Mode lecture seule</Badge>
                )}
              </div>
            )}
          </div>

          {/* OPC Hub Layout with connectors */}
          <div className="relative" data-testid="step-spaces">
            {/* SVG Connector lines with dots */}
            <svg className="hidden md:block absolute inset-0 w-full h-full pointer-events-none" style={{zIndex: 5}} viewBox="0 0 1000 600" preserveAspectRatio="xMidYMid meet">
              {/* Top horizontal line */}
              <line x1="220" y1="210" x2="780" y2="210" stroke="#4f6df5" strokeWidth="1.5" opacity="0.35" />
              {/* Bottom horizontal line */}
              <line x1="220" y1="390" x2="780" y2="390" stroke="#4f6df5" strokeWidth="1.5" opacity="0.35" />
              {/* Left vertical line */}
              <line x1="220" y1="210" x2="220" y2="390" stroke="#4f6df5" strokeWidth="1.5" opacity="0.35" />
              {/* Right vertical line */}
              <line x1="780" y1="210" x2="780" y2="390" stroke="#4f6df5" strokeWidth="1.5" opacity="0.35" />
              {/* Diagonal from top-left corner to OPC circle */}
              <line x1="220" y1="210" x2="438" y2="248" stroke="#4f6df5" strokeWidth="1.5" opacity="0.3" />
              {/* Diagonal from top-right corner to OPC circle */}
              <line x1="780" y1="210" x2="562" y2="248" stroke="#4f6df5" strokeWidth="1.5" opacity="0.3" />
              {/* Diagonal from bottom-left corner to OPC circle */}
              <line x1="220" y1="390" x2="438" y2="352" stroke="#4f6df5" strokeWidth="1.5" opacity="0.3" />
              {/* Diagonal from bottom-right corner to OPC circle */}
              <line x1="780" y1="390" x2="562" y2="352" stroke="#4f6df5" strokeWidth="1.5" opacity="0.3" />
              {/* 4 corner dots */}
              <circle cx="220" cy="210" r="6" fill="#4f6df5" />
              <circle cx="780" cy="210" r="6" fill="#4f6df5" />
              <circle cx="220" cy="390" r="6" fill="#4f6df5" />
              <circle cx="780" cy="390" r="6" fill="#4f6df5" />
              {/* 4 dots touching OPC circle - endpoints of diagonals */}
              <circle cx="438" cy="248" r="6" fill="#4f6df5" />
              <circle cx="562" cy="248" r="6" fill="#4f6df5" />
              <circle cx="438" cy="352" r="6" fill="#4f6df5" />
              <circle cx="562" cy="352" r="6" fill="#4f6df5" />
            </svg>

            {/* Top row - 2 cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5 max-w-4xl mx-auto mb-0">
              {SPACES.filter((_, i) => i < 2).map((space, idx) => {
                const Icon = space.icon;
                const disabled = !spacesOpen;
                return (
                  <div key={space.key} className={`relative bg-white rounded-2xl border border-slate-200 p-5 transition-all ${disabled ? "opacity-60 cursor-not-allowed" : "cursor-pointer hover:shadow-lg hover:border-[#4f6df5]/40 hover:-translate-y-1"}`} onClick={() => handleSpaceSelect(space)} data-testid={`space-${space.key}`}>
                    <div className="relative">
                      <div className="flex items-start gap-3 mb-3">
                        <div className={`w-11 h-11 rounded-xl ${space.iconColor} flex items-center justify-center shrink-0`}><Icon className="w-5 h-5" /></div>
                        <div className="flex-1 min-w-0">
                          <h3 className="font-bold text-[#1e3a5f] text-base" style={{ fontFamily: 'Outfit, sans-serif' }}>{space.label}</h3>
                          <p className="text-[11px] text-slate-500 leading-snug mt-0.5">{space.description}</p>
                        </div>
                        {disabled && <LockKeyhole className="w-4 h-4 text-red-400 shrink-0 mt-1" />}
                      </div>
                      <ul className="space-y-1.5 mb-4 ml-1">{space.features.map((f, i) => (<li key={i} className="flex items-center gap-2 text-xs text-slate-600"><div className="w-1 h-1 rounded-full bg-[#4f6df5] shrink-0" />{f}</li>))}</ul>
                      <button data-testid={`access-cta-${space.key}`} className={`w-full py-2 rounded-lg text-sm font-semibold transition-colors ${disabled ? "bg-slate-100 text-slate-400 cursor-not-allowed" : "bg-[#4f6df5]/10 text-[#4f6df5] hover:bg-[#4f6df5] hover:text-white border border-[#4f6df5]/30"}`} disabled={disabled}>{disabled ? "Accès fermé" : "Accéder"}</button>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Center OPC Hub with halo */}
            <div className="flex justify-center my-2 relative z-10">
              {/* Outer halo */}
              <div className={`absolute w-52 h-52 rounded-full ${spacesOpen ? "bg-[#e0e0ff] opacity-20" : "bg-slate-300 opacity-10"}`} style={{top: '50%', left: '50%', transform: 'translate(-50%, -50%)'}} />
              <button
                type="button"
                disabled={!spacesOpen}
                onClick={() => {
                  if (!spacesOpen) {
                    toast.info("Les accès sont actuellement fermés par l'administrateur.");
                    return;
                  }
                  // Already authenticated? Skip the selector modal.
                  const existingToken = typeof window !== "undefined" ? localStorage.getItem("reactif_token") : null;
                  if (existingToken) {
                    window.location.assign("/opc");
                    return;
                  }
                  setOpcSelectorOpen(true);
                }}
                className={`relative w-44 h-44 rounded-full bg-white flex flex-col items-center justify-center text-center shadow-lg transition-all group ${
                  spacesOpen
                    ? "cursor-pointer hover:shadow-2xl hover:-translate-y-1"
                    : "cursor-not-allowed opacity-60 grayscale"
                }`}
                style={{border: spacesOpen ? '3px solid #5f47ff' : '3px solid #cbd5e1'}}
                data-testid="opc-hub"
                title={spacesOpen ? "Accéder à l'Observatoire Prédictif des Compétences" : "Accès fermé par l'administrateur"}
              >
                {/* Inner glow ring */}
                <div className={`absolute inset-1 rounded-full border ${spacesOpen ? "border-[#e0e0ff] group-hover:border-[#5f47ff]/40" : "border-slate-200"} transition-colors`} />
                {/* Lock icon when closed */}
                {!spacesOpen && (
                  <div className="absolute top-3 right-3 w-7 h-7 rounded-full bg-red-100 flex items-center justify-center">
                    <LockKeyhole className="w-4 h-4 text-red-500" />
                  </div>
                )}
                <p className="text-3xl font-black tracking-wider" style={{ fontFamily: 'Outfit, sans-serif' }}>
                  <span style={{color: '#20215c'}}>O</span><span style={{background: 'linear-gradient(90deg, #5f47ff, #4776ff)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent'}}>P</span><span style={{color: '#20215c'}}>C</span>
                </p>
                <p className="text-[9px] font-bold leading-tight mt-1 px-4 uppercase tracking-[0.12em]">
                  <span style={{color: '#20215c'}}>Observatoire </span><span style={{background: 'linear-gradient(90deg, #5f47ff, #4776ff)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent'}}>Prédictif</span><br/><span style={{color: '#20215c'}}>des </span><span style={{background: 'linear-gradient(90deg, #5f47ff, #4776ff)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent'}}>Compétences</span>
                </p>
                <div className={`mt-1.5 px-3 py-0.5 rounded-full transition-colors ${spacesOpen ? "bg-[#e0e0ff]/30 group-hover:bg-[#5f47ff]/15" : "bg-slate-100"}`}>
                  <p className={`text-[6px] font-semibold tracking-[0.2em] uppercase transition-colors ${spacesOpen ? "text-[#999] group-hover:text-[#5f47ff]" : "text-red-400"}`}>{spacesOpen ? "Intelligence Professionnelle" : "Accès fermé"}</p>
                </div>
              </button>
            </div>

            {/* Bottom row - 2 cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5 max-w-4xl mx-auto mt-0">
              {SPACES.filter((_, i) => i >= 2).map((space, idx) => {
                const Icon = space.icon;
                const disabled = !spacesOpen;
                return (
                  <div key={space.key} className={`relative bg-white rounded-2xl border border-slate-200 p-5 overflow-hidden transition-all ${disabled ? "opacity-60 cursor-not-allowed" : "cursor-pointer hover:shadow-lg hover:border-[#4f6df5]/40 hover:-translate-y-1"}`} onClick={() => handleSpaceSelect(space)} data-testid={`space-${space.key}`}>
                    <div className="relative">
                      <div className="flex items-start gap-3 mb-3">
                        <div className={`w-11 h-11 rounded-xl ${space.iconColor} flex items-center justify-center shrink-0`}><Icon className="w-5 h-5" /></div>
                        <div className="flex-1 min-w-0">
                          <h3 className="font-bold text-[#1e3a5f] text-base" style={{ fontFamily: 'Outfit, sans-serif' }}>{space.label}</h3>
                          <p className="text-[11px] text-slate-500 leading-snug mt-0.5">{space.description}</p>
                        </div>
                        {disabled && <LockKeyhole className="w-4 h-4 text-red-400 shrink-0 mt-1" />}
                      </div>
                      <ul className="space-y-1.5 mb-4 ml-1">{space.features.map((f, i) => (<li key={i} className="flex items-center gap-2 text-xs text-slate-600"><div className="w-1 h-1 rounded-full bg-[#4f6df5] shrink-0" />{f}</li>))}</ul>
                      <button data-testid={`access-cta-${space.key}`} className={`w-full py-2 rounded-lg text-sm font-semibold transition-colors ${disabled ? "bg-slate-100 text-slate-400 cursor-not-allowed" : "bg-[#4f6df5]/10 text-[#4f6df5] hover:bg-[#4f6df5] hover:text-white border border-[#4f6df5]/30"}`} disabled={disabled}>{disabled ? "Accès fermé" : "Accéder"}</button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      <footer className="py-6 text-center text-xs text-slate-400 border-t border-slate-100">
        RE'ACTIF PRO v2.0 — Accès sécurisé
      </footer>

      {/* Click-away overlay for password dropdown - below header only */}
      {showPasswordFor && <div className="fixed inset-0 top-16 z-30" onClick={() => setShowPasswordFor(null)} />}

      {/* Auth modals */}
      <AuthModal open={authModalOpen} onOpenChange={setAuthModalOpen} defaultRole={authModalDefaultRole} onSuccess={handleModalSuccess} />
      <ProRegisterModal open={proModalOpen} onOpenChange={setProModalOpen} roleType={proModalRole} onSuccess={handleModalSuccess} />

      {/* OPC space selector modal */}
      {opcSelectorOpen && (
        <div
          className="fixed inset-0 z-[60] bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in"
          onClick={() => setOpcSelectorOpen(false)}
          data-testid="opc-selector-modal"
        >
          <div
            onClick={(e) => e.stopPropagation()}
            className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full p-6 sm:p-8 relative"
          >
            <button
              onClick={() => setOpcSelectorOpen(false)}
              className="absolute top-4 right-4 p-1 rounded-full hover:bg-slate-100 transition-colors"
              data-testid="opc-selector-close"
            >
              <X className="w-5 h-5 text-slate-500" />
            </button>
            <div className="text-center mb-6">
              <div className="w-14 h-14 rounded-full mx-auto mb-3 flex items-center justify-center" style={{ background: "linear-gradient(135deg, #5f47ff, #4776ff)" }}>
                <span className="text-white font-black text-xl" style={{ fontFamily: 'Outfit, sans-serif' }}>OPC</span>
              </div>
              <h2 className="text-xl sm:text-2xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>
                Accéder à l'Observatoire Prédictif
              </h2>
              <p className="text-sm text-slate-500 mt-2">
                Sélectionnez votre espace pour vous connecter à RE'ACTIF PRO et explorer les données prédictives.
              </p>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3" data-testid="opc-selector-spaces">
              {SPACES.map((space) => {
                const Icon = space.icon;
                return (
                  <button
                    key={space.key}
                    type="button"
                    onClick={() => {
                      localStorage.setItem("reactif_post_redirect", "/opc");
                      setOpcSelectorOpen(false);
                      handleSpaceSelect(space);
                    }}
                    data-testid={`opc-selector-${space.key}`}
                    className="text-left p-4 rounded-xl border border-slate-200 hover:border-[#5f47ff] hover:shadow-md transition-all group"
                  >
                    <div className="flex items-start gap-3">
                      <div className={`w-10 h-10 rounded-lg ${space.iconColor} flex items-center justify-center shrink-0`}>
                        <Icon className="w-5 h-5" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-bold text-slate-900 text-sm" style={{ fontFamily: 'Outfit, sans-serif' }}>
                          {space.label}
                        </h3>
                        <p className="text-xs text-slate-500 mt-0.5 line-clamp-2">{space.description}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-1 mt-3 text-xs font-semibold text-[#5f47ff] opacity-0 group-hover:opacity-100 transition-opacity">
                      Se connecter <ChevronRight className="w-3 h-3" />
                    </div>
                  </button>
                );
              })}
            </div>
            <p className="text-[10px] text-center text-slate-400 mt-5">
              Une fois connecté, vous serez redirigé automatiquement vers l'OPC.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminGate;
