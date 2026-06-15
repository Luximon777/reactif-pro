import { useNavigate } from "react-router-dom";
import { ShieldCheck, Code, Eye, Compass as CompassIcon, Building2, MapPin, Lightbulb, Users, Handshake } from "lucide-react";

/* ─── Logo SVG — exact DOM from reactif.pro ─── */
const LogoSvg = ({ size = 28 }) => (
  <svg width={size} height={size} viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg" className="flex-shrink-0">
    <circle cx="40" cy="40" r="38" stroke="#1e3a5f" strokeWidth="2" fill="#eef2f7"/>
    <circle cx="40" cy="40" r="28" fill="#1e3a5f" opacity="0.08"/>
    <circle cx="40" cy="30" r="8" fill="#4f6df5"/>
    <path d="M26 56 C26 44 34 40 40 40 C46 40 54 44 54 56" fill="#4f6df5" opacity="0.85"/>
    <circle cx="18" cy="28" r="4" fill="#6c5ce7" opacity="0.7"/>
    <circle cx="62" cy="28" r="4" fill="#6c5ce7" opacity="0.7"/>
    <circle cx="18" cy="54" r="3.5" fill="#4f6df5" opacity="0.5"/>
    <circle cx="62" cy="54" r="3.5" fill="#4f6df5" opacity="0.5"/>
    <line x1="24" y1="30" x2="32" y2="30" stroke="#6c5ce7" strokeWidth="1.5" opacity="0.4"/>
    <line x1="48" y1="30" x2="58" y2="30" stroke="#6c5ce7" strokeWidth="1.5" opacity="0.4"/>
    <line x1="20" y1="34" x2="28" y2="42" stroke="#4f6df5" strokeWidth="1" opacity="0.3"/>
    <line x1="60" y1="34" x2="52" y2="42" stroke="#4f6df5" strokeWidth="1" opacity="0.3"/>
  </svg>
);

/* ─── Logo Text — exact from reactif.pro DOM ─── */
const LogoText = ({ size = "sm" }) => {
  const isSm = size === "sm";
  return (
    <div className="flex flex-col leading-none">
      <span className={`font-bold tracking-tight ${isSm ? "text-sm" : "text-5xl"}`} style={{ fontFamily: "Outfit, sans-serif" }}>
        <span className="text-[#1e3a5f]">RE'</span>
        <span className="text-[#4f6df5]">ACTIF</span>
        <span className="text-[#1e3a5f]"> PRO</span>
      </span>
      {isSm ? (
        <span className="text-[6px] font-semibold tracking-[0.2em] text-[#6c5ce7] uppercase mt-0.5">Intelligence Professionnelle</span>
      ) : (
        <span className="text-lg font-bold tracking-[0.35em] text-[#d4a843] uppercase mt-1">Intelligence Professionnelle</span>
      )}
    </div>
  );
};

/* ─── Access Card — exact classes from reactif.pro DOM ─── */
const AccessCard = ({ testId, icon: Icon, iconBg, title, desc, items, ctaTestId, onClick }) => (
  <div
    className="relative bg-white rounded-2xl border border-slate-200 p-5 transition-all cursor-pointer hover:shadow-lg hover:border-[#4f6df5]/40 hover:-translate-y-1"
    data-testid={testId}
    onClick={onClick}
  >
    <div className="relative">
      <div className="flex items-start gap-3 mb-3">
        <div className={`w-11 h-11 rounded-xl ${iconBg} text-white flex items-center justify-center shrink-0`}>
          <Icon className="w-5 h-5" />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-bold text-[#1e3a5f] text-base" style={{ fontFamily: "Outfit, sans-serif" }}>{title}</h3>
          <p className="text-[11px] text-slate-500 leading-snug mt-0.5">{desc}</p>
        </div>
      </div>
      <ul className="space-y-1.5 mb-4 ml-1">
        {items.map((item, i) => (
          <li key={i} className="flex items-center gap-2 text-xs text-slate-600">
            <div className="w-1 h-1 rounded-full bg-[#4f6df5] shrink-0" />
            {item}
          </li>
        ))}
      </ul>
      <button
        data-testid={ctaTestId}
        className="w-full py-2 rounded-lg text-sm font-semibold transition-colors bg-[#4f6df5]/10 text-[#4f6df5] hover:bg-[#4f6df5] hover:text-white border border-[#4f6df5]/30"
      >
        Accéder
      </button>
    </div>
  </div>
);

/* ─── OPC Hub Circle — exact from reactif.pro DOM ─── */
const OpcHub = ({ onClick }) => (
  <div className="flex justify-center my-2 relative z-10">
    <div className="absolute w-52 h-52 rounded-full bg-[#e0e0ff] opacity-20" style={{ top: "50%", left: "50%", transform: "translate(-50%, -50%)" }} />
    <button
      type="button"
      className="relative w-44 h-44 rounded-full bg-white flex flex-col items-center justify-center text-center shadow-lg transition-all group cursor-pointer hover:shadow-2xl hover:-translate-y-1"
      data-testid="opc-hub"
      title="Accéder à l'Observatoire Prédictif des Compétences"
      style={{ border: "3px solid rgb(95, 71, 255)" }}
      onClick={onClick}
    >
      <div className="absolute inset-1 rounded-full border border-[#e0e0ff] group-hover:border-[#5f47ff]/40 transition-colors" />
      <p className="text-3xl font-black tracking-wider" style={{ fontFamily: "Outfit, sans-serif" }}>
        <span style={{ color: "rgb(32, 33, 92)" }}>O</span>
        <span style={{ background: "linear-gradient(90deg, rgb(95, 71, 255), rgb(71, 118, 255))", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>P</span>
        <span style={{ color: "rgb(32, 33, 92)" }}>C</span>
      </p>
      <p className="text-[9px] font-bold leading-tight mt-1 px-4 uppercase tracking-[0.12em]">
        <span style={{ color: "rgb(32, 33, 92)" }}>Observatoire </span>
        <span style={{ background: "linear-gradient(90deg, rgb(95, 71, 255), rgb(71, 118, 255))", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>Prédictif</span>
        <br />
        <span style={{ color: "rgb(32, 33, 92)" }}>des </span>
        <span style={{ background: "linear-gradient(90deg, rgb(95, 71, 255), rgb(71, 118, 255))", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>Compétences</span>
      </p>
      <div className="mt-1.5 px-3 py-0.5 rounded-full transition-colors bg-[#e0e0ff]/30 group-hover:bg-[#5f47ff]/15">
        <p className="text-[6px] font-semibold tracking-[0.2em] uppercase transition-colors text-[#999] group-hover:text-[#5f47ff]">Intelligence Professionnelle</p>
      </div>
    </button>
  </div>
);

/* ─── Connecting Lines SVG — exact from reactif.pro DOM ─── */
const ConnectingLines = () => (
  <svg className="hidden md:block absolute inset-0 w-full h-full pointer-events-none" viewBox="0 0 1000 600" preserveAspectRatio="xMidYMid meet" style={{ zIndex: 5 }}>
    <line x1="220" y1="210" x2="780" y2="210" stroke="#4f6df5" strokeWidth="1.5" opacity="0.35"/>
    <line x1="220" y1="390" x2="780" y2="390" stroke="#4f6df5" strokeWidth="1.5" opacity="0.35"/>
    <line x1="220" y1="210" x2="220" y2="390" stroke="#4f6df5" strokeWidth="1.5" opacity="0.35"/>
    <line x1="780" y1="210" x2="780" y2="390" stroke="#4f6df5" strokeWidth="1.5" opacity="0.35"/>
    <line x1="220" y1="210" x2="438" y2="248" stroke="#4f6df5" strokeWidth="1.5" opacity="0.3"/>
    <line x1="780" y1="210" x2="562" y2="248" stroke="#4f6df5" strokeWidth="1.5" opacity="0.3"/>
    <line x1="220" y1="390" x2="438" y2="352" stroke="#4f6df5" strokeWidth="1.5" opacity="0.3"/>
    <line x1="780" y1="390" x2="562" y2="352" stroke="#4f6df5" strokeWidth="1.5" opacity="0.3"/>
    <circle cx="220" cy="210" r="6" fill="#4f6df5"/>
    <circle cx="780" cy="210" r="6" fill="#4f6df5"/>
    <circle cx="220" cy="390" r="6" fill="#4f6df5"/>
    <circle cx="780" cy="390" r="6" fill="#4f6df5"/>
    <circle cx="438" cy="248" r="6" fill="#4f6df5"/>
    <circle cx="562" cy="248" r="6" fill="#4f6df5"/>
    <circle cx="438" cy="352" r="6" fill="#4f6df5"/>
    <circle cx="562" cy="352" r="6" fill="#4f6df5"/>
  </svg>
);

/* ═══════ MAIN LANDING PAGE — exact copy from reactif.pro DOM ═══════ */
export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-white" data-testid="admin-gate">

      {/* ═══ HEADER — exact from reactif.pro ═══ */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-slate-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1.5" data-testid="logo-reactif-pro">
                <LogoSvg size={28} />
                <LogoText size="sm" />
              </div>
              <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-amber-50 border border-amber-200 text-amber-600 text-[10px] font-medium">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
                En construction
              </span>
            </div>
            <div className="flex items-center gap-2 relative" data-testid="status-selector">
              <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border transition-all bg-white border-slate-200 text-slate-500 hover:border-slate-300 hover:text-slate-700" data-testid="status-admin">
                <ShieldCheck className="w-3.5 h-3.5" /> Admin
              </button>
              <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border transition-all bg-white border-slate-200 text-slate-500 hover:border-slate-300 hover:text-slate-700" data-testid="status-dev">
                <Code className="w-3.5 h-3.5" /> Dev
              </button>
              <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border transition-all bg-white border-slate-200 text-slate-500 hover:border-slate-300 hover:text-slate-700" data-testid="status-invite">
                <Eye className="w-3.5 h-3.5" /> Invité
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* ═══ HERO — exact from reactif.pro ═══ */}
      <section className="relative overflow-hidden pt-16" style={{ background: "linear-gradient(135deg, #1e3a5f 0%, #20215c 100%)" }}>
        <div className="max-w-5xl mx-auto px-4 py-20 flex flex-col items-center text-center">
          {/* Logo card */}
          <div className="bg-white/95 backdrop-blur rounded-2xl shadow-xl px-10 py-6 flex items-center gap-5 mb-8">
            <LogoSvg size={80} />
            <LogoText size="lg" />
          </div>
          {/* Tagline */}
          <p className="text-xl md:text-2xl italic text-white/70 max-w-xl mb-6" style={{ fontFamily: "Georgia, serif" }}>
            Dispositif de réactivation rapide des parcours vers l'emploi
          </p>
          {/* Features */}
          <div className="flex flex-wrap items-center justify-center gap-x-4 gap-y-1 text-white/50 text-sm mb-6">
            <span className="flex items-center gap-1.5"><CompassIcon className="w-4 h-4" /> Orientation</span>
            <span className="text-white/25">•</span>
            <span className="flex items-center gap-1.5"><Building2 className="w-4 h-4" /> Emploi</span>
            <span className="text-white/25">•</span>
            <span className="flex items-center gap-1.5"><MapPin className="w-4 h-4" /> Mobilité</span>
            <span className="text-white/25">•</span>
            <span className="flex items-center gap-1.5"><Lightbulb className="w-4 h-4" /> Innovation sociale</span>
          </div>
          {/* Instruction */}
          <p className="text-xs text-white/40">
            Équipe RE'ACTIF PRO : sélectionnez votre statut en haut à droite
          </p>
        </div>
      </section>

      {/* ═══ VOS ACCÈS — exact from reactif.pro ═══ */}
      <section className="py-16 px-4 bg-gradient-to-b from-slate-50 to-white">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-[#1e3a5f] mb-2" style={{ fontFamily: "Outfit, sans-serif" }}>Vos accès</h2>
            <p className="text-sm text-slate-500">Choisissez votre espace pour accéder à vos outils personnalisés</p>
          </div>

          <div className="relative" data-testid="step-spaces">
            <ConnectingLines />

            {/* Top Row */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5 max-w-4xl mx-auto mb-0">
              <AccessCard
                testId="space-personnel"
                icon={Users}
                iconBg="bg-[#1e3a5f]"
                title="Espace Personnel"
                desc="Révélez et valorisez vos compétences réelles pour construire des trajectoires professionnelles durables"
                items={["Portefeuille de Compétences Certifiées", "Identité professionnelle sécurisée", "Orientation personnalisée"]}
                ctaTestId="access-cta-personnel"
                onClick={() => navigate("/observatoire?tab=particulier")}
              />
              <AccessCard
                testId="space-vsi"
                icon={CompassIcon}
                iconBg="bg-amber-600"
                title="Parcours VSI"
                desc="Valorisez votre Identité Professionnelle — Accompagnement hybride présentiel & distanciel pour révéler votre potentiel"
                items={["Ateliers VSI en présentiel / visio", "Diagnostic identitaire approfondi", "Plan d'action personnalisé"]}
                ctaTestId="access-cta-vsi"
                onClick={() => navigate("/ubuntoo")}
              />
            </div>

            {/* OPC Hub */}
            <OpcHub onClick={() => navigate("/observatoire")} />

            {/* Bottom Row */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5 max-w-4xl mx-auto mt-0">
              <AccessCard
                testId="space-employeur"
                icon={Building2}
                iconBg="bg-emerald-600"
                title="Espace Employeurs"
                desc="Identifiez les talents et compétences en adéquation avec vos besoins économiques"
                items={["Cockpit RH complet", "Matching & opportunités", "Baromètre QVCT"]}
                ctaTestId="access-cta-employeur"
                onClick={() => navigate("/observatoire?tab=rh")}
              />
              <AccessCard
                testId="space-partenaire"
                icon={Handshake}
                iconBg="bg-violet-600"
                title="Appui aux parcours"
                desc="Interface de coordination pour les acteurs de l'accompagnement — en complémentarité des dispositifs existants"
                items={["Diagnostic enrichi", "Coordination des parcours", "Contribution territoriale"]}
                ctaTestId="access-cta-partenaire"
                onClick={() => navigate("/observatoire?tab=conseiller")}
              />
            </div>
          </div>
        </div>
      </section>

      {/* ═══ FOOTER — exact from reactif.pro ═══ */}
      <footer className="py-6 text-center text-xs text-slate-400 border-t border-slate-100">
        RE'ACTIF PRO v2.0 — Accès sécurisé
      </footer>
    </div>
  );
}
