import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Settings, Code, Eye, Compass, Building2, MapPin, Lightbulb, Users, Rocket, Briefcase, HeartHandshake } from "lucide-react";

const CARDS = [
  {
    key: "personnel",
    label: "Espace Personnel",
    desc: "Révélez et valorisez vos compétences réelles pour construire des trajectoires professionnelles durables",
    items: ["Portefeuille de Compétences Certifiées", "Identité professionnelle sécurisée", "Orientation personnalisée"],
    icon: Users,
    iconBg: "#378ADD",
    position: "top-left",
    route: "/observatoire?tab=particulier",
  },
  {
    key: "vsi",
    label: "Parcours VSI",
    desc: "Valorisez votre Identité Professionnelle — Accompagnement hybride présentiel & distanciel pour révéler votre potentiel",
    items: ["Ateliers VSI en présentiel / visio", "Diagnostic identitaire approfondi", "Plan d'action personnalisé"],
    icon: Rocket,
    iconBg: "#E8871E",
    position: "top-right",
    route: "/ubuntoo",
  },
  {
    key: "employeurs",
    label: "Espace Employeurs",
    desc: "Identifiez les talents et compétences en adéquation avec vos besoins économiques",
    items: ["Cockpit RH complet", "Matching & opportunités", "Baromètre QVCT"],
    icon: Briefcase,
    iconBg: "#1D9E75",
    position: "bottom-left",
    route: "/observatoire?tab=rh",
  },
  {
    key: "appui",
    label: "Appui aux parcours",
    desc: "Interface de coordination pour les acteurs de l'accompagnement — en complémentarité des dispositifs existants",
    items: ["Diagnostic enrichi", "Coordination des parcours", "Contribution territoriale"],
    icon: HeartHandshake,
    iconBg: "#7C3AED",
    position: "bottom-right",
    route: "/observatoire?tab=conseiller",
  },
];

function AccessCard({ card, onClick }) {
  const Icon = card.icon;
  return (
    <div
      className="bg-white rounded-xl border border-slate-200 p-5 flex flex-col cursor-pointer hover:shadow-lg hover:border-slate-300 transition-all duration-200 hover:-translate-y-0.5"
      onClick={onClick}
      data-testid={`access-card-${card.key}`}
    >
      <div className="flex items-start gap-3 mb-3">
        <div className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: card.iconBg }}>
          <Icon className="w-5 h-5 text-white" />
        </div>
        <div>
          <h3 className="font-bold text-slate-900 text-sm">{card.label}</h3>
          <p className="text-xs text-slate-500 leading-relaxed mt-0.5">{card.desc}</p>
        </div>
      </div>
      <ul className="space-y-1.5 mb-4 ml-1">
        {card.items.map((item, i) => (
          <li key={i} className="text-xs text-slate-600 flex items-start gap-1.5">
            <span className="w-1 h-1 rounded-full mt-1.5 flex-shrink-0" style={{ background: card.iconBg }} />
            {item}
          </li>
        ))}
      </ul>
      <button
        className="w-full py-2 rounded-lg text-sm font-semibold border-2 transition-colors mt-auto"
        style={{ borderColor: "#D4A843", color: "#D4A843", background: "transparent" }}
        onMouseEnter={(e) => { e.target.style.background = "#D4A843"; e.target.style.color = "#fff"; }}
        onMouseLeave={(e) => { e.target.style.background = "transparent"; e.target.style.color = "#D4A843"; }}
      >
        Accéder
      </button>
    </div>
  );
}

function OpcCircle({ onClick }) {
  return (
    <div
      className="relative w-44 h-44 rounded-full flex flex-col items-center justify-center cursor-pointer transition-transform hover:scale-105"
      style={{
        background: "linear-gradient(135deg, #F0EDFF 0%, #E8E4FF 100%)",
        border: "3px solid #7C5CFC",
        boxShadow: "0 0 0 6px rgba(124,92,252,0.1)",
      }}
      onClick={onClick}
      data-testid="opc-circle"
    >
      <span className="text-3xl font-black tracking-wider" style={{ color: "#26215C" }}>OPC</span>
      <span className="text-[8px] font-bold tracking-widest text-center leading-tight mt-1" style={{ color: "#7C5CFC" }}>
        OBSERVATOIRE<br />PRÉDICTIF
      </span>
      <span className="text-[8px] font-bold tracking-widest text-center" style={{ color: "#D4A843" }}>
        DES COMPÉTENCES
      </span>
      <span className="text-[7px] text-slate-400 mt-0.5 italic">Intelligence Professionnelle</span>
    </div>
  );
}

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-white" data-testid="landing-page">
      {/* Header */}
      <header className="sticky top-0 z-50 flex items-center justify-between px-6 py-3 bg-white border-b border-slate-100">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <svg width="32" height="32" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="50" cy="50" r="46" stroke="#378ADD" strokeWidth="3" fill="#EBF4FF"/>
              <circle cx="50" cy="30" r="9" fill="#378ADD"/>
              <path d="M32 64 C32 51 68 51 68 64" stroke="#378ADD" strokeWidth="3" fill="none"/>
              <circle cx="28" cy="43" r="6" fill="#378ADD" opacity="0.55"/>
              <path d="M16 70 C16 60 40 60 40 70" stroke="#378ADD" strokeWidth="2" fill="none" opacity="0.55"/>
              <circle cx="72" cy="43" r="6" fill="#378ADD" opacity="0.55"/>
              <path d="M60 70 C60 60 84 60 84 70" stroke="#378ADD" strokeWidth="2" fill="none" opacity="0.55"/>
            </svg>
            <div className="leading-none">
              <span className="text-base font-bold" style={{ color: "#26215C" }}>
                RE'<span className="font-black">ACTIF</span> PRO
              </span>
              <p className="text-[8px] tracking-[0.2em] font-medium" style={{ color: "#378ADD" }}>
                INTELLIGENCE PROFESSIONNELLE
              </p>
            </div>
          </div>
          <span
            className="ml-2 px-3 py-1 text-[10px] font-semibold rounded-full border"
            style={{ color: "#D85A30", borderColor: "#F5C98A", background: "#FFF8EE" }}
          >
            En construction
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button className="flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-medium text-slate-600 bg-white border border-slate-200 rounded-full hover:bg-slate-50 transition" data-testid="admin-btn">
            <Settings className="w-3.5 h-3.5" /> Admin
          </button>
          <button className="flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-medium text-slate-600 bg-white border border-slate-200 rounded-full hover:bg-slate-50 transition" data-testid="dev-btn">
            <Code className="w-3.5 h-3.5" /> Dev
          </button>
          <button className="flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-medium text-slate-600 bg-white border border-slate-200 rounded-full hover:bg-slate-50 transition" data-testid="invite-btn">
            <Eye className="w-3.5 h-3.5" /> Invité
          </button>
        </div>
      </header>

      {/* Hero Section */}
      <section className="flex flex-col items-center justify-center py-16 px-4" style={{ background: "linear-gradient(180deg, #2D3A5C 0%, #3B4A6B 100%)", minHeight: "340px" }} data-testid="hero-section">
        {/* Logo Card */}
        <div className="bg-white/95 backdrop-blur rounded-2xl shadow-xl px-10 py-7 flex items-center gap-5 mb-7">
          <svg width="70" height="70" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="46" stroke="#378ADD" strokeWidth="2.5" fill="#EBF4FF"/>
            <circle cx="50" cy="28" r="10" fill="#378ADD"/>
            <path d="M30 66 C30 50 70 50 70 66" stroke="#378ADD" strokeWidth="3" fill="none"/>
            <circle cx="27" cy="43" r="7" fill="#378ADD" opacity="0.5"/>
            <path d="M14 73 C14 61 40 61 40 73" stroke="#378ADD" strokeWidth="2" fill="none" opacity="0.5"/>
            <circle cx="73" cy="43" r="7" fill="#378ADD" opacity="0.5"/>
            <path d="M60 73 C60 61 86 61 86 73" stroke="#378ADD" strokeWidth="2" fill="none" opacity="0.5"/>
          </svg>
          <div>
            <h1 className="text-4xl font-bold tracking-tight" style={{ color: "#26215C" }}>
              RE'<span className="font-black">ACTIF</span> PRO
            </h1>
            <p className="text-sm tracking-[0.3em] font-semibold mt-1" style={{ color: "#C49A2A" }}>
              INTELLIGENCE PROFESSIONNELLE
            </p>
          </div>
        </div>

        <p className="text-lg md:text-xl italic text-white/85 text-center max-w-xl mb-5" style={{ fontFamily: "Georgia, serif" }}>
          Dispositif de réactivation rapide des parcours vers l'emploi
        </p>

        <div className="flex flex-wrap items-center justify-center gap-x-5 gap-y-1 text-white/70 text-sm mb-6">
          <span className="flex items-center gap-1.5"><Compass className="w-4 h-4" /> Orientation</span>
          <span className="text-white/30">•</span>
          <span className="flex items-center gap-1.5"><Building2 className="w-4 h-4" /> Emploi</span>
          <span className="text-white/30">•</span>
          <span className="flex items-center gap-1.5"><MapPin className="w-4 h-4" /> Mobilité</span>
          <span className="text-white/30">•</span>
          <span className="flex items-center gap-1.5"><Lightbulb className="w-4 h-4" /> Innovation sociale</span>
        </div>

        <p className="text-xs" style={{ color: "#C49A2A" }}>
          Équipe RE'ACTIF PRO : sélectionnez votre statut en haut à droite
        </p>
      </section>

      {/* Vos accès */}
      <section className="py-14 px-4" data-testid="access-section">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-black text-center mb-2" style={{ color: "#26215C", fontFamily: "Georgia, serif" }}>Vos accès</h2>
          <p className="text-center text-slate-400 text-sm mb-10">Choisissez votre espace pour accéder à vos outils personnalisés</p>

          {/* Grid: 2 cards top, OPC center, 2 cards bottom */}
          <div className="relative">
            {/* Top Row */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-5">
              <AccessCard card={CARDS[0]} onClick={() => navigate(CARDS[0].route)} />
              <AccessCard card={CARDS[1]} onClick={() => navigate(CARDS[1].route)} />
            </div>

            {/* OPC Center with connecting lines */}
            <div className="relative flex justify-center py-4">
              {/* SVG connecting lines */}
              <svg className="absolute inset-0 w-full h-full pointer-events-none hidden md:block" viewBox="0 0 800 180" preserveAspectRatio="xMidYMid meet">
                {/* Top-left to center */}
                <line x1="200" y1="10" x2="370" y2="90" stroke="#7C5CFC" strokeWidth="1.5" strokeDasharray="0" opacity="0.3"/>
                <circle cx="200" cy="10" r="4" fill="#378ADD"/>
                {/* Top-right to center */}
                <line x1="600" y1="10" x2="430" y2="90" stroke="#7C5CFC" strokeWidth="1.5" strokeDasharray="0" opacity="0.3"/>
                <circle cx="600" cy="10" r="4" fill="#378ADD"/>
                {/* Bottom-left to center */}
                <line x1="200" y1="170" x2="370" y2="90" stroke="#7C5CFC" strokeWidth="1.5" strokeDasharray="0" opacity="0.3"/>
                <circle cx="200" cy="170" r="4" fill="#378ADD"/>
                {/* Bottom-right to center */}
                <line x1="600" y1="170" x2="430" y2="90" stroke="#7C5CFC" strokeWidth="1.5" strokeDasharray="0" opacity="0.3"/>
                <circle cx="600" cy="170" r="4" fill="#378ADD"/>
                {/* Arc top */}
                <path d="M200 10 Q400 -30 600 10" stroke="#7C5CFC" strokeWidth="1.5" fill="none" opacity="0.2"/>
                {/* Arc bottom */}
                <path d="M200 170 Q400 210 600 170" stroke="#7C5CFC" strokeWidth="1.5" fill="none" opacity="0.2"/>
              </svg>

              <OpcCircle onClick={() => navigate("/observatoire")} />
            </div>

            {/* Bottom Row */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mt-5">
              <AccessCard card={CARDS[2]} onClick={() => navigate(CARDS[2].route)} />
              <AccessCard card={CARDS[3]} onClick={() => navigate(CARDS[3].route)} />
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="text-center py-6 border-t border-slate-100">
        <p className="text-xs text-slate-400">RE'ACTIF PRO v2.0 — Accès sécurisé</p>
      </footer>
    </div>
  );
}
