import { useNavigate } from "react-router-dom";
import { Settings, Code, Eye, Compass, Building2, MapPin, Lightbulb, Users, Rocket, Briefcase, HeartHandshake } from "lucide-react";

/* ─── Logo image (original from reactif.pro — contains icon + text) ─── */
const LogoImg = ({ height = 40 }) => (
  <img src="/logo-reactif-pro-hd.png" alt="RE'ACTIF PRO" style={{ height, objectFit: "contain" }} />
);

/* ─── Access Card Component ─── */
const AccessCard = ({ icon: Icon, iconBg, title, desc, items, onClick }) => (
  <div
    className="bg-white rounded-xl border border-slate-200 p-6 flex flex-col cursor-pointer hover:shadow-lg hover:border-slate-300 transition-all duration-200"
    onClick={onClick}
  >
    <div className="flex items-start gap-3.5 mb-4">
      <div className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: iconBg }}>
        <Icon className="w-5 h-5 text-white" />
      </div>
      <div>
        <h3 className="font-bold text-slate-900 text-[15px] mb-1">{title}</h3>
        <p className="text-[13px] text-slate-500 leading-relaxed">{desc}</p>
      </div>
    </div>
    <ul className="space-y-1.5 mb-5 pl-1">
      {items.map((item, i) => (
        <li key={i} className="text-[13px] text-slate-600 flex items-start gap-2">
          <span className="mt-[7px] w-1.5 h-1.5 rounded-full bg-slate-400 flex-shrink-0" />
          {item}
        </li>
      ))}
    </ul>
    <button
      className="w-full py-2.5 rounded-lg text-sm font-semibold border transition-colors mt-auto"
      style={{ borderColor: "#CBD5E1", color: "#64748B", background: "transparent" }}
      onMouseEnter={(e) => { e.target.style.background = "#3B82F6"; e.target.style.color = "#fff"; e.target.style.borderColor = "#3B82F6"; }}
      onMouseLeave={(e) => { e.target.style.background = "transparent"; e.target.style.color = "#64748B"; e.target.style.borderColor = "#CBD5E1"; }}
    >
      Accéder
    </button>
  </div>
);

/* ─── OPC Circle with connecting lines ─── */
const OpcSection = ({ onClick }) => (
  <div className="relative py-2">
    {/* SVG connecting lines */}
    <svg className="absolute inset-0 w-full h-full pointer-events-none" viewBox="0 0 1000 220" preserveAspectRatio="xMidYMid meet">
      {/* Top arc */}
      <path d="M180 50 Q500 -20 820 50" stroke="#7C5CFC" strokeWidth="1.5" fill="none" opacity="0.25"/>
      {/* Bottom arc */}
      <path d="M180 170 Q500 240 820 170" stroke="#7C5CFC" strokeWidth="1.5" fill="none" opacity="0.25"/>
      {/* Top-left to center */}
      <line x1="180" y1="50" x2="430" y2="110" stroke="#7C5CFC" strokeWidth="1.2" opacity="0.2"/>
      {/* Top-right to center */}
      <line x1="820" y1="50" x2="570" y2="110" stroke="#7C5CFC" strokeWidth="1.2" opacity="0.2"/>
      {/* Bottom-left to center */}
      <line x1="180" y1="170" x2="430" y2="110" stroke="#7C5CFC" strokeWidth="1.2" opacity="0.2"/>
      {/* Bottom-right to center */}
      <line x1="820" y1="170" x2="570" y2="110" stroke="#7C5CFC" strokeWidth="1.2" opacity="0.2"/>
      {/* Blue dots */}
      <circle cx="180" cy="50" r="5" fill="#3B82F6"/>
      <circle cx="820" cy="50" r="5" fill="#3B82F6"/>
      <circle cx="180" cy="170" r="5" fill="#3B82F6"/>
      <circle cx="820" cy="170" r="5" fill="#3B82F6"/>
    </svg>

    {/* OPC Circle */}
    <div className="flex justify-center relative z-10">
      <div
        className="w-48 h-48 rounded-full flex flex-col items-center justify-center cursor-pointer transition-transform hover:scale-105"
        style={{
          background: "linear-gradient(180deg, #F5F3FF 0%, #EDE9FE 100%)",
          border: "3px solid #7C5CFC",
          boxShadow: "0 0 0 8px rgba(124,92,252,0.08)",
        }}
        onClick={onClick}
      >
        <span className="text-[36px] font-black tracking-[0.15em] leading-none" style={{ color: "#1E1B4B" }}>OPC</span>
        <span className="text-[9px] font-bold tracking-[0.2em] text-center mt-1.5" style={{ color: "#7C5CFC" }}>
          OBSERVATOIRE
        </span>
        <span className="text-[9px] font-bold tracking-[0.2em] text-center" style={{ color: "#7C5CFC" }}>
          PRÉDICTIF
        </span>
        <span className="text-[9px] font-bold tracking-[0.2em] text-center" style={{ color: "#D4A843" }}>
          DES COMPÉTENCES
        </span>
        <span className="text-[8px] text-slate-400 mt-1 italic">Intelligence Professionnelle</span>
      </div>
    </div>
  </div>
);

/* ─── Main Landing Page ─── */
export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-white" data-testid="landing-page">

      {/* ═══════ HEADER ═══════ */}
      <header className="sticky top-0 z-50 flex items-center justify-between px-6 py-2.5 bg-white border-b border-slate-100" data-testid="landing-header">
        <div className="flex items-center gap-3">
          <LogoImg height={36} />
          <span className="ml-2 flex items-center gap-1 px-3 py-1 text-[11px] font-semibold rounded-full border"
            style={{ color: "#D97706", borderColor: "#FCD34D", background: "#FFFBEB" }}>
            <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
            En construction
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button className="flex items-center gap-1.5 px-4 py-2 text-[13px] font-medium text-slate-600 bg-white border border-slate-200 rounded-full hover:bg-slate-50 transition" data-testid="admin-btn">
            <Settings className="w-4 h-4" /> Admin
          </button>
          <button className="flex items-center gap-1.5 px-4 py-2 text-[13px] font-medium text-slate-600 bg-white border border-slate-200 rounded-full hover:bg-slate-50 transition" data-testid="dev-btn">
            <Code className="w-4 h-4" /> Dev
          </button>
          <button className="flex items-center gap-1.5 px-4 py-2 text-[13px] font-medium text-slate-600 bg-white border border-slate-200 rounded-full hover:bg-slate-50 transition" data-testid="invite-btn">
            <Eye className="w-4 h-4" /> Invité
          </button>
        </div>
      </header>

      {/* ═══════ HERO ═══════ */}
      <section className="flex flex-col items-center justify-center py-16 px-4" style={{ background: "#2D3A5C", minHeight: "380px" }} data-testid="hero-section">
        {/* White logo card */}
        <div className="bg-white rounded-2xl shadow-xl px-10 py-6 flex items-center justify-center mb-8">
          <LogoImg height={90} />
        </div>

        {/* Tagline */}
        <p className="text-xl italic text-white/80 text-center max-w-lg mb-6" style={{ fontFamily: "Georgia, 'Times New Roman', serif" }}>
          Dispositif de réactivation rapide des parcours vers l'emploi
        </p>

        {/* Feature pills */}
        <div className="flex flex-wrap items-center justify-center gap-x-4 gap-y-1 text-white/60 text-[14px] mb-7">
          <span className="flex items-center gap-1.5"><Compass className="w-4 h-4" /> Orientation</span>
          <span className="text-white/25">•</span>
          <span className="flex items-center gap-1.5"><Building2 className="w-4 h-4" /> Emploi</span>
          <span className="text-white/25">•</span>
          <span className="flex items-center gap-1.5"><MapPin className="w-4 h-4" /> Mobilité</span>
          <span className="text-white/25">•</span>
          <span className="flex items-center gap-1.5"><Lightbulb className="w-4 h-4" /> Innovation sociale</span>
        </div>

        {/* Team instruction */}
        <p className="text-[13px]" style={{ color: "#D4A843" }}>
          Équipe RE'ACTIF PRO : sélectionnez votre statut en haut à droite
        </p>
      </section>

      {/* ═══════ VOS ACCÈS ═══════ */}
      <section className="py-16 px-4" data-testid="access-section">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-[34px] font-black text-center mb-2" style={{ color: "#1E293B", fontFamily: "Georgia, 'Times New Roman', serif" }}>
            Vos accès
          </h2>
          <p className="text-center text-slate-400 text-sm mb-10">
            Choisissez votre espace pour accéder à vos outils personnalisés
          </p>

          {/* Top Row: Espace Personnel + Parcours VSI */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <AccessCard
              icon={Users}
              iconBg="#3B82F6"
              title="Espace Personnel"
              desc="Révélez et valorisez vos compétences réelles pour construire des trajectoires professionnelles durables"
              items={["Portefeuille de Compétences Certifiées", "Identité professionnelle sécurisée", "Orientation personnalisée"]}
              onClick={() => navigate("/observatoire?tab=particulier")}
            />
            <AccessCard
              icon={Rocket}
              iconBg="#EA8B1E"
              title="Parcours VSI"
              desc="Valorisez votre Identité Professionnelle — Accompagnement hybride présentiel & distanciel pour révéler votre potentiel"
              items={["Ateliers VSI en présentiel / visio", "Diagnostic identitaire approfondi", "Plan d'action personnalisé"]}
              onClick={() => navigate("/ubuntoo")}
            />
          </div>

          {/* OPC Center */}
          <OpcSection onClick={() => navigate("/observatoire")} />

          {/* Bottom Row: Espace Employeurs + Appui aux parcours */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <AccessCard
              icon={Briefcase}
              iconBg="#059669"
              title="Espace Employeurs"
              desc="Identifiez les talents et compétences en adéquation avec vos besoins économiques"
              items={["Cockpit RH complet", "Matching & opportunités", "Baromètre QVCT"]}
              onClick={() => navigate("/observatoire?tab=rh")}
            />
            <AccessCard
              icon={HeartHandshake}
              iconBg="#7C3AED"
              title="Appui aux parcours"
              desc="Interface de coordination pour les acteurs de l'accompagnement — en complémentarité des dispositifs existants"
              items={["Diagnostic enrichi", "Coordination des parcours", "Contribution territoriale"]}
              onClick={() => navigate("/observatoire?tab=conseiller")}
            />
          </div>
        </div>
      </section>

      {/* ═══════ FOOTER ═══════ */}
      <footer className="text-center py-6 border-t border-slate-100">
        <p className="text-sm text-slate-400">RE'ACTIF PRO v2.0 — Accès sécurisé</p>
      </footer>
    </div>
  );
}
