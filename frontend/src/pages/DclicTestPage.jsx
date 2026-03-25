import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, ArrowRight, CheckCircle, Copy, Check, Home, ChevronRight, Calendar, GraduationCap, BookOpen, Sparkles, Info, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, Tooltip as RechartsTooltip } from "recharts";

const API = process.env.REACT_APP_BACKEND_URL + "/api";

// ============================================================================
// TOOLTIP COMPONENT (survol pour définitions)
// ============================================================================
const HoverTooltip = ({ children, content }) => (
  <span className="relative group inline-flex items-center gap-1 cursor-help">
    {children}
    <Info className="w-3.5 h-3.5 text-slate-500 group-hover:text-[#818cf8] transition-colors" />
    <span className="invisible group-hover:visible opacity-0 group-hover:opacity-100 transition-all duration-200 absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-72 md:w-96 p-3 bg-[#0f1d32] border border-white/20 rounded-lg text-xs text-slate-300 leading-relaxed shadow-xl z-50 pointer-events-none font-light">
      {content}
    </span>
  </span>
);

// Definitions for key terms
const DEFINITIONS = {
  archeologie: "L'Archéologie des Compétences est une approche originale qui identifie vos talents enfouis à travers 3 dimensions : Cognition (comment vous pensez), Conation (ce qui vous met en mouvement) et Affection (ce qui vous touche). Contrairement à un simple listing de compétences, cette méthode révèle les ressources profondes qui fondent votre identité professionnelle.",
  boussole: "La Boussole de Fonctionnement cartographie vos préférences cognitives sur 4 axes fondamentaux (MBTI). Elle révèle comment vous percevez le monde, prenez vos décisions et organisez votre vie.",
  mbti: (type) => `Le profil ${type} est un type de personnalité MBTI (Myers-Briggs Type Indicator). Il décrit vos préférences naturelles dans 4 dimensions : Énergie (E/I), Perception (S/N), Décision (T/F) et Organisation (J/P).`,
  disc: "Le modèle DISC identifie 4 styles comportementaux : Dominance (D - rouge), Influence (I - jaune), Stabilité (S - vert) et Conformité (C - bleu). Chaque personne possède un mélange unique de ces styles.",
  riasec: "Le modèle RIASEC (ou modèle de Holland) identifie 6 types d'intérêts professionnels : Réaliste, Investigateur, Artistique, Social, Entreprenant et Conventionnel. Votre profil révèle les environnements de travail qui vous correspondent le mieux.",
  vertus: "Le modèle des Vertus de Seligman & Peterson identifie 6 vertus fondamentales : Sagesse, Courage, Humanité, Justice, Tempérance et Transcendance. Chaque vertu regroupe des forces de caractère qui sont universellement valorisées.",
  ofman: "Le Cadran d'Ofman est un modèle créé par Daniel Ofman (années 1990) qui relie 4 éléments : votre Qualité fondamentale (force naturelle), le Piège (excès de cette qualité), le Challenge (ce que vous devez développer) et l'Allergie (ce qui vous irrite chez les autres). Il montre que chaque force a une faiblesse symétrique.",
  integrated: "L'Analyse Intégrée examine votre profil sur 3 niveaux : Niveau 1 (compétences prouvées), Niveau 2 (style de travail et environnement) et Niveau 3 (régulation, moteur interne et signaux de stress). Elle offre une vision complète et nuancée.",
  cross: "L'Analyse Croisée met en relation vos différents profils (DISC, Ennéagramme, MBTI) pour identifier les synergies naturelles et les tensions potentielles entre vos différentes facettes.",
};

// ============================================================================
// PROFIL COMPORTEMENTAL - Radar Charts (Tripartite, DISC, Archéologie)
// ============================================================================
const ProfilComportemental = ({ profile }) => {
  const vp = profile.vertus_profile || {};
  const rp = profile.riasec_profile || {};
  const compass = profile.compass || {};
  const disc = profile.disc_scores || {};

  // Tripartite data (Cognition, Conation, Affection)
  const tripartiteData = [
    { axis: "Cognition", value: vp.vertus_scores?.sagesse || 50 },
    { axis: "Conation", value: vp.vertus_scores?.courage || 50 },
    { axis: "Affection", value: vp.vertus_scores?.humanite || 50 },
  ];

  // DISC data
  const discData = [
    { axis: "D", value: disc.D || 40 },
    { axis: "I", value: disc.I || 40 },
    { axis: "S", value: disc.S || 40 },
    { axis: "C", value: disc.C || 40 },
  ];

  // Archéologie data (5 axes from RIASEC + Vertus)
  const scores = rp.scores || {};
  const archData = [
    { axis: "R", value: scores.R || 30 },
    { axis: "I", value: scores.I || 30 },
    { axis: "A", value: scores.A || 30 },
    { axis: "S", value: scores.S || 30 },
    { axis: "E", value: scores.E || 30 },
    { axis: "C", value: scores.C || 30 },
  ];

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-bold text-white flex items-center gap-2">
          Profil Comportemental
        </h3>
        <p className="text-sm text-slate-400">
          <HoverTooltip content={DEFINITIONS.archeologie}>Tripartite</HoverTooltip> x{" "}
          <HoverTooltip content={DEFINITIONS.disc}>DISC</HoverTooltip> x{" "}
          <HoverTooltip content={DEFINITIONS.archeologie}>Archéologie des Compétences</HoverTooltip>
        </p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Tripartite */}
        <div className="bg-[#152a45] border border-white/10 rounded-xl p-4">
          <p className="text-sm font-semibold text-white text-center mb-2">Tripartite</p>
          <ResponsiveContainer width="100%" height={200}>
            <RadarChart data={tripartiteData} cx="50%" cy="50%" outerRadius="70%">
              <PolarGrid stroke="rgba(255,255,255,0.1)" />
              <PolarAngleAxis dataKey="axis" tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <Radar dataKey="value" stroke="#c084fc" fill="#c084fc" fillOpacity={0.3} strokeWidth={2} />
              <Radar dataKey="value" stroke="#ec4899" fill="#ec4899" fillOpacity={0.15} strokeWidth={1} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
        {/* DISC */}
        <div className="bg-[#152a45] border border-white/10 rounded-xl p-4">
          <p className="text-sm font-semibold text-white text-center mb-2">DISC</p>
          <ResponsiveContainer width="100%" height={200}>
            <RadarChart data={discData} cx="50%" cy="50%" outerRadius="70%">
              <PolarGrid stroke="rgba(255,255,255,0.1)" />
              <PolarAngleAxis dataKey="axis" tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <Radar dataKey="value" stroke="#10b981" fill="#10b981" fillOpacity={0.25} strokeWidth={2} />
              <Radar dataKey="value" stroke="#eab308" fill="#eab308" fillOpacity={0.1} strokeWidth={1} />
            </RadarChart>
          </ResponsiveContainer>
          <div className="flex justify-center gap-2 mt-2">
            {[
              { letter: "D", label: "Dominance", color: "border-red-500 text-red-400" },
              { letter: "I", label: "Influence", color: "border-amber-500 text-amber-400" },
              { letter: "S", label: "Stabilité", color: "border-emerald-500 text-emerald-400" },
              { letter: "C", label: "Conformité", color: "border-cyan-500 text-cyan-400" },
            ].map(d => (
              <span key={d.letter} className={`text-[10px] px-2 py-0.5 rounded-full border ${d.color}`}>
                <strong>{d.letter}</strong> {d.label}
              </span>
            ))}
          </div>
        </div>
        {/* Archéologie */}
        <div className="bg-[#152a45] border border-white/10 rounded-xl p-4">
          <p className="text-sm font-semibold text-white text-center mb-2">Archéologie</p>
          <ResponsiveContainer width="100%" height={200}>
            <RadarChart data={archData} cx="50%" cy="50%" outerRadius="70%">
              <PolarGrid stroke="rgba(255,255,255,0.1)" />
              <PolarAngleAxis dataKey="axis" tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <Radar dataKey="value" stroke="#06b6d4" fill="#06b6d4" fillOpacity={0.25} strokeWidth={2} />
              <Radar dataKey="value" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.1} strokeWidth={1} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// D'CLIC PRO LOGO SVG (from original project)
// ============================================================================
const DclicProLogo = ({ size = 120, animated = true }) => (
  <svg width={size} height={size} viewBox="0 0 120 120">
    <defs>
      <linearGradient id="dclic-circleGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#4f6df5" />
        <stop offset="50%" stopColor="#84cc16" />
        <stop offset="100%" stopColor="#22c55e" />
      </linearGradient>
      <radialGradient id="dclic-centerGrad" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stopColor="#fde047" />
        <stop offset="50%" stopColor="#a3e635" />
        <stop offset="100%" stopColor="#4ade80" />
      </radialGradient>
      <filter id="dclic-glow">
        <feGaussianBlur stdDeviation="3" result="coloredBlur" />
        <feMerge><feMergeNode in="coloredBlur" /><feMergeNode in="SourceGraphic" /></feMerge>
      </filter>
    </defs>
    {animated && <circle cx="60" cy="60" r="52" fill="none" stroke="url(#dclic-circleGrad)" strokeWidth="2" opacity="0.3" className="animate-pulse" />}
    <circle cx="60" cy="60" r="48" fill="none" stroke="url(#dclic-circleGrad)" strokeWidth="2.5" />
    <circle cx="60" cy="60" r="22" fill="url(#dclic-centerGrad)" filter={animated ? "url(#dclic-glow)" : ""} />
    <g fill="rgba(255,255,255,0.8)">
      <path d="M 60 48 L 65 55 L 60 62 L 55 55 Z" />
      <path d="M 60 58 L 65 65 L 60 72 L 55 65 Z" />
    </g>
    <circle cx="60" cy="15" r="7" fill="#4f6df5" />
    <circle cx="25" cy="35" r="7" fill="#4f6df5" />
    <circle cx="95" cy="35" r="7" fill="#4f6df5" />
    <circle cx="25" cy="85" r="7" fill="#06b6d4" />
    <circle cx="95" cy="85" r="7" fill="#22c55e" />
    <circle cx="60" cy="105" r="7" fill="#22c55e" />
    <circle cx="60" cy="38" r="4" fill="white" />
    <circle cx="42" cy="47" r="4" fill="white" />
    <circle cx="78" cy="47" r="4" fill="white" />
    <circle cx="42" cy="73" r="4" fill="white" />
    <circle cx="78" cy="73" r="4" fill="white" />
    <circle cx="60" cy="82" r="4" fill="white" />
    <line x1="60" y1="15" x2="60" y2="38" stroke="#4f6df5" strokeWidth="2.5" strokeLinecap="round" />
    <line x1="25" y1="35" x2="42" y2="47" stroke="#4f6df5" strokeWidth="2.5" strokeLinecap="round" />
    <line x1="95" y1="35" x2="78" y2="47" stroke="#4f6df5" strokeWidth="2.5" strokeLinecap="round" />
    <line x1="25" y1="85" x2="42" y2="73" stroke="#06b6d4" strokeWidth="2.5" strokeLinecap="round" />
    <line x1="95" y1="85" x2="78" y2="73" stroke="#22c55e" strokeWidth="2.5" strokeLinecap="round" />
    <line x1="60" y1="105" x2="60" y2="82" stroke="#22c55e" strokeWidth="2.5" strokeLinecap="round" />
  </svg>
);

// ============================================================================
// RESULTS SECTIONS
// ============================================================================
const SECTIONS = [
  { id: "archeologie", label: "Archéologie des Compétences", icon: "1" },
  { id: "comportemental", label: "Profil Comportemental", icon: "2" },
  { id: "boussole", label: "Boussole de Fonctionnement", icon: "3" },
  { id: "integrated", label: "Analyse Intégrée", icon: "4" },
  { id: "riasec", label: "Profil RIASEC", icon: "5" },
  { id: "vertus", label: "Profil de Vertus", icon: "6" },
  { id: "pistes", label: "Pistes d'Action", icon: "7" },
  { id: "cross", label: "Analyse Croisée", icon: "8" },
  { id: "ofman", label: "Cadran d'Ofman", icon: "9" },
  { id: "carte", label: "Carte d'Identité Pro", icon: "10" },
];

const Bar = ({ label, value, max = 100, color = "bg-[#4f6df5]" }) => (
  <div className="space-y-1">
    <div className="flex justify-between text-xs"><span className="text-slate-300">{label}</span><span className="font-medium text-white">{value}%</span></div>
    <div className="h-2.5 bg-white/10 rounded-full overflow-hidden"><div className={`h-full rounded-full ${color}`} style={{ width: `${Math.min(value, 100)}%` }} /></div>
  </div>
);

const CompassAxis = ({ axis }) => {
  const pct = axis.dominant === axis.pole_a?.code ? 75 : 25;
  return (
    <div className="bg-[#152a45] rounded-lg p-3 border border-white/10">
      <p className="text-sm font-semibold text-white mb-2">{axis.name}</p>
      <div className="flex items-center gap-2 text-xs mb-1">
        <span className={`font-medium ${pct > 50 ? "text-[#4f6df5]" : "text-slate-400"}`}>{axis.pole_a?.label}</span>
        <div className="flex-1 h-3 bg-white/10 rounded-full relative"><div className="absolute h-3 bg-[#4f6df5] rounded-full" style={{ width: `${pct}%` }} /></div>
        <span className={`font-medium ${pct <= 50 ? "text-[#4f6df5]" : "text-slate-400"}`}>{axis.pole_b?.label}</span>
      </div>
      <p className="text-xs text-slate-400 mt-1">{axis.insight}</p>
    </div>
  );
};

// Section components
const ArcheologieSection = ({ profile }) => {
  const vp = profile.vertus_profile || {};
  const vd = profile.vertu_data || {};
  const cognition = vd.cognition || [];
  const conation = vd.conation || [];
  const affection = vd.affection || [];
  const valeursSchwartz = vd.valeurs_schwartz || [];
  const forces = vd.forces || [];
  const savoirsEtre = vd.savoirs_etre || [];
  const vertuName = vd.name || vp.dominant_name || "?";

  return (
    <div className="space-y-6">
      {/* Title */}
      <div>
        <h3 className="text-lg font-bold text-white flex items-center gap-2">
          <HoverTooltip content={DEFINITIONS.archeologie}>Votre Identité & Compétences</HoverTooltip>
        </h3>
        <p className="text-sm text-slate-400 mt-1">
          Generic Skills Component Approach{" "}
          <HoverTooltip content="Approche générique des compétences qui catégorise les savoirs en composantes fondamentales.">x</HoverTooltip>{" "}
          <HoverTooltip content={DEFINITIONS.archeologie}>Archéologie des Compétences</HoverTooltip>
        </p>
      </div>

      {/* Cognition / Conation / Affection */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Cognition */}
        <div className="rounded-xl overflow-hidden border border-purple-500/30 bg-[#152a45]">
          <div className="bg-gradient-to-r from-[#6b21a8] to-[#9333ea] px-4 py-3 flex items-center gap-2">
            <svg className="w-5 h-5 text-white/80" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" /></svg>
            <div>
              <p className="font-bold text-white text-sm">Cognition</p>
              <p className="text-[10px] text-white/70">Ce que je pense & sais</p>
            </div>
          </div>
          <div className="p-4 space-y-3">
            <p className="text-xs text-slate-400">Forces cognitives qui favorisent l'acquisition et l'usage de la connaissance</p>
            <div className="flex flex-wrap gap-1.5">
              {cognition.map((c, i) => <span key={i} className="text-xs px-2.5 py-1 rounded-full border border-purple-400/40 text-purple-300">{c}</span>)}
            </div>
          </div>
        </div>

        {/* Conation */}
        <div className="rounded-xl overflow-hidden border border-red-500/30 bg-[#152a45]">
          <div className="bg-gradient-to-r from-[#dc2626] via-[#f97316] to-[#ec4899] px-4 py-3 flex items-center gap-2">
            <svg className="w-5 h-5 text-white/80" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" /></svg>
            <div>
              <p className="font-bold text-white text-sm">Conation</p>
              <p className="text-[10px] text-white/70">Ce que je fais & veux</p>
            </div>
          </div>
          <div className="p-4 space-y-3">
            <p className="text-xs text-slate-400">Forces émotionnelles impliquant l'exercice de la volonté pour atteindre ses buts</p>
            <div className="flex flex-wrap gap-1.5">
              {conation.map((c, i) => <span key={i} className="text-xs px-2.5 py-1 rounded-full border border-red-400/40 text-red-300">{c}</span>)}
            </div>
          </div>
        </div>

        {/* Affection */}
        <div className="rounded-xl overflow-hidden border border-pink-500/30 bg-[#152a45]">
          <div className="bg-gradient-to-r from-[#ec4899] to-[#f472b6] px-4 py-3 flex items-center gap-2">
            <svg className="w-5 h-5 text-white/80" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" /></svg>
            <div>
              <p className="font-bold text-white text-sm">Affection</p>
              <p className="text-[10px] text-white/70">Ce que je ressens & partage</p>
            </div>
          </div>
          <div className="p-4 space-y-3">
            <p className="text-xs text-slate-400">Forces interpersonnelles pour tendre vers les autres et leur venir en aide</p>
            <div className="flex flex-wrap gap-1.5">
              {affection.map((c, i) => <span key={i} className="text-xs px-2.5 py-1 rounded-full border border-pink-400/40 text-pink-300">{c}</span>)}
            </div>
          </div>
        </div>
      </div>

      {/* Separator */}
      <div className="border-t border-white/10" />

      {/* Valeurs Universelles / Forces de Caractère / Savoirs-être Pro */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Valeurs Universelles - Schwartz */}
        <div className="rounded-xl overflow-hidden border border-cyan-500/30 bg-[#152a45]">
          <div className="bg-gradient-to-r from-[#06b6d4] to-[#22d3ee] px-4 py-3">
            <p className="font-bold text-white text-sm flex items-center gap-1.5">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064" /></svg>
              Valeurs Universelles
            </p>
            <p className="text-[10px] text-white/70">Schwartz</p>
          </div>
          <div className="p-4">
            <div className="flex flex-wrap gap-1.5">
              {valeursSchwartz.map((v, i) => <span key={i} className="text-xs px-2.5 py-1 rounded-full border border-cyan-400/40 text-cyan-300">{v}</span>)}
            </div>
          </div>
        </div>

        {/* Forces de Caractère - Seligman & Peterson */}
        <div className="rounded-xl overflow-hidden border border-amber-500/30 bg-[#152a45]">
          <div className="bg-gradient-to-r from-[#f59e0b] via-[#a855f7] to-[#ec4899] px-4 py-3">
            <p className="font-bold text-white text-sm flex items-center gap-1.5">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" /></svg>
              Forces de Caractère
            </p>
            <p className="text-[10px] text-white/70">Seligman & Peterson</p>
          </div>
          <div className="p-4">
            <div className="flex flex-wrap gap-1.5">
              {forces.map((f, i) => <span key={i} className="text-xs px-2.5 py-1 rounded-full border border-amber-400/40 text-amber-300">{f}</span>)}
            </div>
          </div>
        </div>

        {/* Savoirs-être Pro - France Travail */}
        <div className="rounded-xl overflow-hidden border border-emerald-500/30 bg-[#152a45]">
          <div className="bg-gradient-to-r from-[#10b981] to-[#34d399] px-4 py-3">
            <p className="font-bold text-white text-sm flex items-center gap-1.5">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
              Savoirs-être Pro
            </p>
            <p className="text-[10px] text-white/70">France Travail</p>
          </div>
          <div className="p-4">
            <div className="flex flex-wrap gap-1.5">
              {savoirsEtre.map((s, i) => <span key={i} className="text-xs px-2.5 py-1 rounded-full border border-emerald-400/40 text-emerald-300">{s}</span>)}
            </div>
          </div>
        </div>
      </div>

      {/* Vertu dominante banner */}
      <div className="bg-gradient-to-r from-[#1e1b4b] via-[#312e81] to-[#4f46e5] rounded-xl px-6 py-4 flex items-center justify-center gap-3">
        <svg className="w-6 h-6 text-amber-400" fill="currentColor" viewBox="0 0 24 24"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z" /></svg>
        <span className="text-white font-bold text-lg">Vertu dominante : <span className="text-amber-400">{vertuName}</span></span>
      </div>
    </div>
  );
};

const BoussoleSection = ({ profile }) => {
  const compass = profile.compass || {};
  const axes = compass.axes || [];
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-bold text-white">
        <HoverTooltip content={DEFINITIONS.boussole}>Boussole de Fonctionnement</HoverTooltip>
      </h3>
      <p className="text-sm text-slate-400">Vos préférences cognitives sur 4 axes fondamentaux.</p>
      <div className="bg-[#4f6df5]/10 rounded-lg p-3 border border-[#4f6df5]/30">
        <p className="text-sm font-semibold text-[#818cf8]">Profil global : <HoverTooltip content={DEFINITIONS.mbti(profile.mbti || "?")}>{profile.mbti || "?"}</HoverTooltip></p>
        {compass.summary && <p className="text-xs text-[#a5b4fc] mt-1">{compass.summary}</p>}
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">{axes.map((axis, i) => <CompassAxis key={i} axis={axis} />)}</div>
    </div>
  );
};

const IntegratedSection = ({ profile }) => {
  const ia = profile.integrated_analysis || {};
  const n1 = ia.niveau_1_preuves || {};
  const n2 = ia.niveau_2_fonctionnement || {};
  const n3 = ia.niveau_3_regulation || {};
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-bold text-white">
        <HoverTooltip content={DEFINITIONS.integrated}>Analyse Intégrée (3 niveaux)</HoverTooltip>
      </h3>
      <div className="rounded-xl border border-blue-400/20 bg-blue-500/5 p-4">
        <h4 className="font-semibold text-blue-300 mb-2">Niveau 1 - Compétences prouvées</h4>
        {n1.competences_prouvees?.length > 0 && <div className="flex flex-wrap gap-1.5 mb-2">{n1.competences_prouvees.map((c, i) => <Badge key={i} className="bg-blue-500/20 text-blue-300 text-xs border-0">{c}</Badge>)}</div>}
        {n1.forces_cles?.length > 0 && <div><p className="text-xs font-medium text-slate-400 mb-1">Forces clés :</p><div className="flex flex-wrap gap-1">{n1.forces_cles.map((f, i) => <Badge key={i} variant="outline" className="text-xs border-blue-400/30 text-blue-300">{f}</Badge>)}</div></div>}
      </div>
      <div className="rounded-xl border border-emerald-400/20 bg-emerald-500/5 p-4">
        <h4 className="font-semibold text-emerald-300 mb-2">Niveau 2 - Style de travail</h4>
        {n2.style_travail && <p className="text-sm text-emerald-200 mb-2">{n2.style_travail}</p>}
        {n2.environnement_favorable?.length > 0 && <div className="flex flex-wrap gap-1.5">{n2.environnement_favorable.map((e, i) => <Badge key={i} className="bg-emerald-500/20 text-emerald-300 text-xs border-0">{e}</Badge>)}</div>}
      </div>
      <div className="rounded-xl border border-amber-400/20 bg-amber-500/5 p-4">
        <h4 className="font-semibold text-amber-300 mb-2">Niveau 3 - Régulation</h4>
        {n3.moteur_interne && <p className="text-sm text-amber-200"><strong>Moteur interne :</strong> {n3.moteur_interne}</p>}
        {n3.leviers_croissance?.length > 0 && <div className="mt-2"><p className="text-xs font-medium text-slate-400 mb-1">Leviers de croissance :</p><div className="flex flex-wrap gap-1">{n3.leviers_croissance.map((l, i) => <Badge key={i} variant="outline" className="text-xs border-amber-400/30 text-amber-300">{l}</Badge>)}</div></div>}
        {n3.signaux_stress?.length > 0 && <div className="mt-2"><p className="text-xs font-medium text-red-400 mb-1">Signaux de stress :</p><div className="flex flex-wrap gap-1">{n3.signaux_stress.map((s, i) => <Badge key={i} className="bg-red-500/10 text-red-400 text-xs border-0">{s}</Badge>)}</div></div>}
      </div>
      {ia.synthese && <p className="text-sm text-slate-300 italic bg-white/5 p-3 rounded-lg">{ia.synthese}</p>}
    </div>
  );
};

const RiasecSection = ({ profile }) => {
  const rp = profile.riasec_profile || {};
  const scores = rp.scores || {};
  const labels = { R: "Réaliste", I: "Investigateur", A: "Artistique", S: "Social", E: "Entreprenant", C: "Conventionnel" };
  const colors = { R: "bg-orange-500", I: "bg-blue-500", A: "bg-purple-500", S: "bg-emerald-500", E: "bg-red-500", C: "bg-slate-500" };
  const maxScore = Math.max(...Object.values(scores), 1);
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-bold text-white">
        <HoverTooltip content={DEFINITIONS.riasec}>Profil RIASEC</HoverTooltip>
      </h3>
      <div className="bg-[#4f6df5]/10 rounded-lg p-3 border border-[#4f6df5]/30">
        <p className="text-lg font-bold text-[#818cf8]">{rp.major_name || rp.major || "?"} / {rp.minor_name || rp.minor || "?"}</p>
        {rp.major_description && <p className="text-sm text-[#a5b4fc] mt-1">{rp.major_description}</p>}
      </div>
      <div className="space-y-2">{Object.entries(scores).sort((a, b) => b[1] - a[1]).map(([key, val]) => <Bar key={key} label={`${key} - ${labels[key] || key}`} value={Math.round((val / maxScore) * 100)} color={colors[key] || "bg-[#4f6df5]"} />)}</div>
      {rp.traits?.length > 0 && <div><p className="text-sm font-semibold text-slate-300 mb-1">Traits dominants</p><div className="flex flex-wrap gap-1.5">{rp.traits.map((t, i) => <Badge key={i} className="bg-violet-500/20 text-violet-300 text-xs border-0">{t}</Badge>)}</div></div>}
      {rp.environnements_preferes?.length > 0 && <div><p className="text-sm font-semibold text-slate-300 mb-1">Environnements préférés</p><div className="flex flex-wrap gap-1.5">{rp.environnements_preferes.map((e, i) => <Badge key={i} variant="outline" className="text-xs border-white/20 text-slate-300">{e}</Badge>)}</div></div>}
    </div>
  );
};

const VertusSection = ({ profile }) => {
  const vp = profile.vertus_profile || {};
  const scores = vp.vertus_scores || {};
  const labels = { sagesse: "Sagesse", courage: "Courage", humanite: "Humanite", justice: "Justice", temperance: "Temperance", transcendance: "Transcendance" };
  const colors = { sagesse: "bg-blue-500", courage: "bg-red-500", humanite: "bg-rose-500", justice: "bg-emerald-500", temperance: "bg-amber-500", transcendance: "bg-purple-500" };
  const maxScore = Math.max(...Object.values(scores), 1);
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-bold text-white">
        <HoverTooltip content={DEFINITIONS.vertus}>Profil de Vertus</HoverTooltip>
      </h3>
      <p className="text-sm text-slate-400">Seligman & Peterson - Les 6 vertus fondamentales</p>
      <div className="bg-emerald-500/10 rounded-lg p-3 border border-emerald-400/30">
        <p className="text-sm font-semibold text-emerald-300">Vertu dominante : {vp.dominant_name || vp.vertu_dominante_name || labels[vp.dominant] || "?"}</p>
      </div>
      <div className="space-y-2">{Object.entries(scores).sort((a, b) => b[1] - a[1]).map(([key, val]) => <Bar key={key} label={labels[key] || key} value={Math.round((val / maxScore) * 100)} color={colors[key] || "bg-[#4f6df5]"} />)}</div>
      {vp.qualites_dominantes?.length > 0 && <div><p className="text-sm font-semibold text-slate-300 mb-1">Qualités humaines associées</p><div className="flex flex-wrap gap-1.5">{vp.qualites_dominantes.map((q, i) => <Badge key={i} className="bg-emerald-500/20 text-emerald-300 text-xs border-0">{typeof q === "string" ? q : q.name || ""}</Badge>)}</div></div>}
    </div>
  );
};

const PistesSection = ({ profile }) => {
  const lp = profile.life_path || {};
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-bold text-white">Pistes d'Action</h3>
      <div className="bg-violet-500/10 rounded-lg p-3 border border-violet-400/30"><p className="text-sm font-semibold text-violet-300">{lp.label || "Développement personnel"}</p></div>
      {lp.strengths?.length > 0 && <div><p className="text-sm font-semibold text-emerald-300 mb-1">Forces naturelles</p><div className="flex flex-wrap gap-1.5">{lp.strengths.map((s, i) => <Badge key={i} className="bg-emerald-500/20 text-emerald-300 text-xs border-0">{s}</Badge>)}</div></div>}
      {lp.watchouts?.length > 0 && <div><p className="text-sm font-semibold text-amber-300 mb-1">Points de vigilance</p><div className="flex flex-wrap gap-1.5">{lp.watchouts.map((w, i) => <Badge key={i} className="bg-amber-500/20 text-amber-300 text-xs border-0">{w}</Badge>)}</div></div>}
      {lp.micro_actions?.length > 0 && <div><p className="text-sm font-semibold text-slate-300 mb-2">Pistes pour progresser</p><div className="space-y-2">{lp.micro_actions.map((ma, i) => (
        <div key={i} className="bg-[#152a45] border border-white/10 rounded-lg p-3"><Badge className="bg-[#4f6df5]/20 text-[#818cf8] text-xs border-0 mb-1">{ma.focus}</Badge><p className="text-sm text-slate-300">{ma.action}</p></div>
      ))}</div></div>}
      {lp.work_preferences?.length > 0 && <div><p className="text-sm font-semibold text-blue-300 mb-1">Environnements favorables</p><div className="flex flex-wrap gap-1.5">{lp.work_preferences.map((wp, i) => <Badge key={i} variant="outline" className="text-xs border-blue-400/30 text-blue-300">{wp}</Badge>)}</div></div>}
    </div>
  );
};

const CrossSection = ({ profile }) => {
  const ca = profile.cross_analysis || {};
  if (!ca.has_cross_analysis) return <p className="text-sm text-slate-500">Renseignez votre date de naissance pour accéder à l'analyse croisée.</p>;
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-bold text-white">
        <HoverTooltip content={DEFINITIONS.cross}>Analyse Croisée</HoverTooltip>
      </h3>
      <div className="rounded-xl border border-blue-400/20 bg-blue-500/5 p-4"><h4 className="text-sm font-semibold text-blue-300 mb-1">Synergie - Style de travail</h4><p className="text-sm text-blue-200">{ca.synergy_disc}</p></div>
      <div className="rounded-xl border border-emerald-400/20 bg-emerald-500/5 p-4"><h4 className="text-sm font-semibold text-emerald-300 mb-1">Synergie - Moteur intérieur</h4><p className="text-sm text-emerald-200">{ca.synergy_ennea}</p></div>
      {ca.tension && <div className="rounded-xl border border-amber-400/20 bg-amber-500/5 p-4"><h4 className="text-sm font-semibold text-amber-300 mb-1">Tension à transformer</h4><p className="text-sm text-amber-200">{ca.tension}</p></div>}
      {ca.integration_insight && <p className="text-sm text-violet-300 italic bg-violet-500/5 p-3 rounded-lg">{ca.integration_insight}</p>}
    </div>
  );
};

const OfmanSection = ({ profile }) => {
  const zones = profile.ofman_quadrant || [];
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-bold text-white">
        <HoverTooltip content={DEFINITIONS.ofman}>Cadran d'Ofman - Zones de vigilance</HoverTooltip>
      </h3>
      <p className="text-sm text-slate-400">Vos qualités peuvent devenir des pièges si elles sont poussées à l'extrême.</p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {zones.map((z, i) => (
          <div key={i} className="bg-[#152a45] border border-white/10 rounded-xl p-4 space-y-2">
            <div className="flex items-center justify-between">
              <Badge className="bg-emerald-500/20 text-emerald-300 text-xs border-0">{z.qualite}</Badge>
              <span className="text-[10px] text-slate-500">{z.source}</span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="bg-red-500/10 rounded p-2"><p className="font-semibold text-red-400">Pièges</p><p className="text-red-300">{z.piege}</p></div>
              <div className="bg-blue-500/10 rounded p-2"><p className="font-semibold text-blue-400">Défi</p><p className="text-blue-300">{z.defi}</p></div>
            </div>
            <div className="bg-amber-500/10 rounded p-2 text-xs"><p className="font-semibold text-amber-400">Allergie</p><p className="text-amber-300">{z.allergie}</p></div>
            {z.recommandation && <p className="text-xs text-slate-400 italic">{z.recommandation}</p>}
          </div>
        ))}
      </div>
    </div>
  );
};

const CarteSection = ({ profile, accessCode }) => {
  const vp = profile.vertus_profile || {};
  const rp = profile.riasec_profile || {};
  const ia = profile.integrated_analysis || {};
  const lp = profile.life_path || {};
  const n1 = ia.niveau_1_preuves || {};
  const n3 = ia.niveau_3_regulation || {};
  const compass = profile.compass || {};
  const today = new Date().toLocaleDateString("fr-FR");
  return (
    <div className="space-y-6">
      <div><h3 className="text-lg font-bold text-white">Carte d'Identité Professionnelle</h3><p className="text-sm text-slate-400">Synthèse de votre profil - 4 dimensions</p></div>
      <div className="bg-gradient-to-br from-[#1e1b4b] to-[#312e81] rounded-2xl overflow-hidden shadow-xl text-white">
        <div className="px-6 pt-5 pb-3 flex items-center justify-between">
          <h2 className="text-2xl font-bold tracking-wide">PROFIL D'CLIC PRO</h2>
          <div className="text-right text-xs"><p className="font-bold text-indigo-300">RE'ACTIF PRO</p></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2">
          <div className="px-6 py-4 border-r border-b border-white/10">
            <h4 className="text-sm font-bold text-purple-400 uppercase tracking-wider mb-3">Identité Personnelle</h4>
            <div className="space-y-3">
              <div><p className="text-[10px] uppercase tracking-wider text-slate-400 mb-1">Qualités Humaines</p><div className="flex flex-wrap gap-1.5">{(vp.qualites_dominantes || []).slice(0, 4).map((q, i) => <span key={i} className="text-xs bg-white/10 rounded-full px-2.5 py-0.5 text-slate-200">{typeof q === "string" ? q : q.name || ""}</span>)}</div></div>
              <div><p className="text-[10px] uppercase tracking-wider text-slate-400 mb-1">Valeurs</p><div className="flex flex-wrap gap-1.5">{(vp.valeurs_dominantes || []).slice(0, 3).map((v, i) => <span key={i} className="text-xs bg-white/10 rounded-full px-2.5 py-0.5 text-slate-200">{typeof v === "string" ? v : v.name || ""}</span>)}</div></div>
              <div><p className="text-[10px] uppercase tracking-wider text-slate-400">Ce qui me rend unique</p><p className="text-base font-bold text-white">{vp.dominant_name || vp.vertu_dominante_name || "?"}</p></div>
            </div>
          </div>
          <div className="px-6 py-4 border-b border-white/10">
            <h4 className="text-sm font-bold text-amber-400 uppercase tracking-wider mb-3">Identité Professionnelle</h4>
            <div className="space-y-3">
              <div><p className="text-[10px] uppercase tracking-wider text-slate-400 mb-1">Savoir-être</p><div className="flex flex-wrap gap-1.5">{(vp.savoirs_etre_dominants || n1.competences_prouvees || []).slice(0, 4).map((s, i) => <span key={i} className="text-xs bg-white/10 rounded-full px-2.5 py-0.5 text-slate-200">{typeof s === "string" ? s : s.name || ""}</span>)}</div></div>
              <div><p className="text-[10px] uppercase tracking-wider text-slate-400 mb-1">Compétences clés</p><div className="flex flex-wrap gap-1.5">{(vp.competences_oms || n1.forces_cles || []).slice(0, 4).map((c, i) => <span key={i} className="text-xs bg-white/10 rounded-full px-2.5 py-0.5 text-slate-200">{c}</span>)}</div></div>
            </div>
          </div>
          <div className="px-6 py-4 border-r border-white/10">
            <h4 className="text-sm font-bold text-emerald-400 uppercase tracking-wider mb-3">Identité Sociale</h4>
            <div className="space-y-3">
              <div><p className="text-[10px] uppercase tracking-wider text-slate-400 mb-1">Mes rôles</p><div className="flex flex-wrap gap-1.5">{(rp.traits || ["Contributeur", "Collaborateur"]).slice(0, 3).map((r, i) => <span key={i} className="text-xs bg-white/10 rounded-full px-2.5 py-0.5 text-slate-200">{r}</span>)}</div></div>
              <div><p className="text-[10px] uppercase tracking-wider text-slate-400 mb-1">Impact social</p><div className="flex flex-wrap gap-1.5">{(lp.work_preferences || rp.environnements_preferes || []).slice(0, 3).map((w, i) => <span key={i} className="text-xs bg-white/10 rounded-full px-2.5 py-0.5 text-slate-200">{w}</span>)}</div></div>
            </div>
          </div>
          <div className="px-6 py-4">
            <h4 className="text-sm font-bold text-blue-400 uppercase tracking-wider mb-3">Identité Profonde</h4>
            <div className="space-y-3">
              <div><p className="text-[10px] uppercase tracking-wider text-slate-400">Ce qui donne du sens</p><p className="text-base font-bold text-white">{lp.label || n3.moteur_interne || "Développement"}</p></div>
              <div><p className="text-[10px] uppercase tracking-wider text-slate-400 mb-1">Ma mission</p><div className="flex flex-wrap gap-1.5">{(lp.strengths || []).slice(0, 3).map((s, i) => <span key={i} className="text-xs bg-white/10 rounded-full px-2.5 py-0.5 text-slate-200">{s}</span>)}</div></div>
            </div>
          </div>
        </div>
        <div className="px-6 py-3 bg-white/5 flex items-center justify-between border-t border-white/10">
          <div className="flex items-center gap-3">
            <div className="flex gap-1">{[...Array(4)].map((_, i) => <div key={i} className="w-2.5 h-2.5 rounded-full bg-indigo-400" />)}</div>
            <div><p className="text-[10px] text-slate-400">PROFIL</p><p className="text-sm font-bold">{profile.mbti || "?"} - {profile.disc_label || profile.disc || "?"}</p></div>
          </div>
          <div className="text-right"><p className="text-[10px] text-emerald-400 font-bold">Profil vérifié</p><p className="text-[10px] text-slate-400">ID {accessCode || "---"} - {today}</p></div>
        </div>
      </div>
      {compass.summary && (
        <div className="bg-[#152a45] border border-white/10 rounded-xl p-5">
          <h4 className="text-sm font-bold text-white mb-2">Synthèse Professionnelle</h4>
          <p className="text-sm text-slate-300 leading-relaxed">{compass.summary}</p>
        </div>
      )}
    </div>
  );
};

// ============================================================================
// MAIN COMPONENT
// ============================================================================
const DclicTestPage = () => {
  const navigate = useNavigate();
  const [questions, setQuestions] = useState([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [answers, setAnswers] = useState({});
  const [rankingSelections, setRankingSelections] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [codeCopied, setCodeCopied] = useState(false);
  const [activeSection, setActiveSection] = useState("archeologie");
  const [step, setStep] = useState("intro");
  const [birthDate, setBirthDate] = useState("");
  const [educationLevel, setEducationLevel] = useState("");
  const [reportValidated, setReportValidated] = useState(false);

  useEffect(() => {
    fetch(`${API}/dclic/questionnaire`)
      .then(r => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then(d => setQuestions(d.questions || []))
      .catch(e => console.error("Erreur chargement questionnaire:", e));
  }, []);

  const q = questions[currentIdx];
  const progress = questions.length ? ((currentIdx + 1) / questions.length) * 100 : 0;
  const isRanking = q?.type === "ranking";
  const currentRanking = rankingSelections[q?.id] || [];
  const maxRank = isRanking ? Math.min(4, q.choices?.length || 4) : 0;
  const canProceed = isRanking ? currentRanking.length === maxRank : !!answers[q?.id];

  const handleAnswer = (val) => setAnswers(prev => ({ ...prev, [q.id]: val }));

  const handleRankingSelect = (choice) => {
    const qid = q.id;
    const sels = rankingSelections[qid] || [];
    const existIdx = sels.findIndex(s => s.value === choice.value);
    if (existIdx !== -1) {
      const next = sels.filter(s => s.value !== choice.value).map((s, i) => ({ ...s, rank: i + 1 }));
      setRankingSelections(p => ({ ...p, [qid]: next }));
      if (answers[qid]) setAnswers(p => { const c = { ...p }; delete c[qid]; return c; });
    } else if (sels.length < maxRank) {
      const next = [...sels, { ...choice, rank: sels.length + 1 }];
      setRankingSelections(p => ({ ...p, [qid]: next }));
      if (next.length === maxRank) setAnswers(p => ({ ...p, [qid]: next.map(s => s.value).join(",") }));
    }
  };

  const getRank = (val) => { const s = (rankingSelections[q?.id] || []).find(x => x.value === val); return s ? s.rank : null; };

  const handleNext = async () => {
    if (currentIdx < questions.length - 1) { setCurrentIdx(i => i + 1); return; }
    setIsSubmitting(true);
    setStep("loading");
    try {
      const res = await fetch(`${API}/dclic/submit`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answers, birth_date: birthDate || null, education_level: educationLevel || null })
      });
      const data = await res.json();
      setResult(data);
      setStep("results");
    } catch (e) { console.error(e); setStep("questionnaire"); }
    setIsSubmitting(false);
  };

  const copyCode = () => { if (result?.access_code) { navigator.clipboard.writeText(result.access_code); setCodeCopied(true); setTimeout(() => setCodeCopied(false), 3000); } };

  const getCategoryLabel = (cat) => {
    const labels = { energie: "Énergie", perception: "Perception", decision: "Décision", structure: "Organisation", disc: "Style DISC", ennea: "Motivations", riasec: "Intérêts RIASEC", vertus: "Vertus", valeurs: "Valeurs" };
    return labels[cat] || cat;
  };

  // ===================== INTRO SCREEN =====================
  if (step === "intro") return (
    <div className="min-h-screen bg-[#1e3a5f] relative overflow-hidden flex items-center justify-center p-4" data-testid="dclic-intro">
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-[20%] left-[30%] w-[500px] h-[500px] rounded-full bg-[#4f6df5]/10 blur-[120px]" />
        <div className="absolute bottom-[20%] right-[30%] w-[400px] h-[400px] rounded-full bg-[#6c5ce7]/8 blur-[100px]" />
      </div>
      <div className="relative z-10 text-center space-y-8 max-w-lg w-full">
        <div className="flex justify-center"><DclicProLogo size={140} animated={true} /></div>
        <div>
          <h1 className="text-4xl font-black tracking-wider">
            <span className="bg-gradient-to-r from-[#4f6df5] via-[#6c5ce7] to-[#10b981] bg-clip-text text-transparent">D'CLIC PRO</span>
          </h1>
          <p className="text-sm text-slate-400 font-medium tracking-[3px] uppercase mt-2">L'APPLY RE'ACTIF PRO</p>
        </div>
        <p className="text-white/60 text-base">Découvrez votre profil de personnalité et compétences professionnelles en répondant à {questions.length || "~26"} questions visuelles.</p>
        <p className="text-sm text-slate-500">Durée estimée : 5-10 minutes</p>
        <button
          className="w-full bg-gradient-to-r from-[#4f6df5] to-[#10b981] hover:from-[#6366f1] hover:to-[#22c55e] text-white font-semibold py-4 px-8 rounded-full transition-all flex items-center justify-center gap-2 shadow-lg shadow-[#4f6df5]/25"
          onClick={() => setStep("birthdate")} data-testid="start-test-btn"
        >
          Commencer le test <ArrowRight className="w-5 h-5" />
        </button>
        <button className="text-white/40 hover:text-white/60 transition-colors text-sm" onClick={() => navigate(-1)}>Retour</button>
      </div>
    </div>
  );

  // ===================== BIRTHDATE =====================
  if (step === "birthdate") return (
    <div className="min-h-screen bg-[#1e3a5f] relative overflow-hidden flex items-center justify-center p-4" data-testid="dclic-birthdate">
      <div className="absolute inset-0 pointer-events-none"><div className="absolute top-[30%] left-[20%] w-[400px] h-[400px] rounded-full bg-[#4f6df5]/10 blur-[100px]" /></div>
      <div className="relative z-10 max-w-lg w-full bg-[#152a45] rounded-2xl border border-white/10 p-8 space-y-6 shadow-2xl">
        <div className="flex items-center gap-2 text-slate-400 text-sm"><Calendar className="w-4 h-4" />Étape 1/2</div>
        <h2 className="text-xl font-bold text-white">Quelle est votre date de naissance ?</h2>
        <p className="text-sm text-slate-400">Optionnel - permet une analyse croisée plus approfondie.</p>
        <input
          type="date" value={birthDate} onChange={e => setBirthDate(e.target.value)}
          className="w-full h-14 text-lg text-center bg-white/10 border-2 border-white/20 rounded-xl text-white focus:border-[#4f6df5] focus:outline-none transition-all [color-scheme:dark]"
          data-testid="birth-date-input"
        />
        <div className="flex gap-3">
          <button className="flex-1 py-3 px-6 rounded-full border border-white/20 text-white/60 hover:text-white hover:border-white/40 transition-all" onClick={() => setStep("intro")}>Retour</button>
          <button className="flex-1 py-3 px-6 rounded-full bg-gradient-to-r from-[#4f6df5] to-[#10b981] text-white font-semibold transition-all flex items-center justify-center gap-1" onClick={() => setStep("education")}>Suivant <ArrowRight className="w-4 h-4" /></button>
        </div>
      </div>
    </div>
  );

  // ===================== EDUCATION =====================
  if (step === "education") return (
    <div className="min-h-screen bg-[#1e3a5f] relative overflow-hidden flex items-center justify-center p-4" data-testid="dclic-education">
      <div className="absolute inset-0 pointer-events-none"><div className="absolute bottom-[30%] right-[20%] w-[400px] h-[400px] rounded-full bg-[#6c5ce7]/10 blur-[100px]" /></div>
      <div className="relative z-10 max-w-lg w-full bg-[#152a45] rounded-2xl border border-white/10 p-8 space-y-6 shadow-2xl">
        <div className="flex items-center gap-2 text-slate-400 text-sm"><GraduationCap className="w-4 h-4" />Étape 2/2</div>
        <h2 className="text-xl font-bold text-white">Quel est votre niveau d'études ?</h2>
        <div className="grid grid-cols-2 gap-3">
          {[
            { value: "cap", label: "Sans diplôme / CAP / BEP" },
            { value: "bac", label: "Bac / Bac Pro" },
            { value: "bac2", label: "Bac+2 (BTS, DUT)" },
            { value: "bac3", label: "Bac+3 (Licence)" },
            { value: "bac5", label: "Bac+5 (Master)" },
            { value: "bac8", label: "Bac+8 (Doctorat)" },
          ].map(opt => (
            <button key={opt.value}
              className={`p-3 rounded-xl text-left transition-all border-2 ${educationLevel === opt.value ? "border-[#4f6df5] bg-[#4f6df5]/15 shadow-lg shadow-[#4f6df5]/10" : "border-white/15 bg-white/5 hover:border-white/30 hover:bg-white/10"}`}
              onClick={() => setEducationLevel(opt.value)} data-testid={`edu-${opt.value}`}>
              <p className={`text-sm font-medium ${educationLevel === opt.value ? "text-[#818cf8]" : "text-white/80"}`}>{opt.label}</p>
            </button>
          ))}
        </div>
        <div className="flex gap-3">
          <button className="flex-1 py-3 px-6 rounded-full border border-white/20 text-white/60 hover:text-white hover:border-white/40 transition-all" onClick={() => setStep("birthdate")}>Retour</button>
          <button className="flex-1 py-3 px-6 rounded-full bg-gradient-to-r from-[#4f6df5] to-[#10b981] text-white font-semibold transition-all flex items-center justify-center gap-1" onClick={() => setStep("questionnaire")} data-testid="start-questions-btn">Démarrer <ArrowRight className="w-4 h-4" /></button>
        </div>
      </div>
    </div>
  );

  // ===================== LOADING =====================
  if (step === "loading") return (
    <div className="min-h-screen bg-[#1e3a5f] flex items-center justify-center p-4" data-testid="dclic-loading">
      <div className="text-center space-y-6">
        <div className="w-16 h-16 border-4 border-[#4f6df5]/30 border-t-[#4f6df5] rounded-full animate-spin mx-auto" />
        <h2 className="text-xl font-bold text-white">Analyse de votre profil en cours...</h2>
        <p className="text-sm text-slate-400 max-w-sm">Notre IA analyse vos réponses et génère votre rapport personnalisé. Cette opération peut prendre quelques secondes.</p>
      </div>
    </div>
  );

  // ===================== RESULTS =====================
  if (step === "results" && result) {
    const p = result.profile || {};
    const renderSection = () => {
      switch (activeSection) {
        case "comportemental": return <ProfilComportemental profile={p} />;
        case "archeologie": return <ArcheologieSection profile={p} />;
        case "boussole": return <BoussoleSection profile={p} />;
        case "integrated": return <IntegratedSection profile={p} />;
        case "riasec": return <RiasecSection profile={p} />;
        case "vertus": return <VertusSection profile={p} />;
        case "pistes": return <PistesSection profile={p} />;
        case "cross": return <CrossSection profile={p} />;
        case "ofman": return <OfmanSection profile={p} />;
        case "carte": return <CarteSection profile={p} accessCode={result.access_code} />;
        default: return null;
      }
    };
    return (
      <div className="min-h-screen bg-[#1e3a5f]">
        <div className="max-w-6xl mx-auto px-4 py-6">
          {/* Header */}
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between mb-6 gap-4">
            <div className="flex items-center gap-3">
              <DclicProLogo size={50} animated={false} />
              <div>
                <h1 className="text-2xl font-bold text-white">Résultats D'CLIC PRO</h1>
                <p className="text-sm text-slate-400">Votre profil de personnalité et compétences professionnelles</p>
              </div>
            </div>
            <div className="flex items-center gap-3 flex-wrap">
              <div className="bg-[#152a45] border border-white/10 rounded-lg px-4 py-2 flex items-center gap-2" data-testid="dclic-code-display">
                <span className="text-xs text-[#818cf8]">Code :</span>
                <span className="font-mono font-bold text-white text-lg" data-testid="dclic-code">{result.access_code}</span>
                <button onClick={copyCode} className="text-[#818cf8] hover:text-white transition-colors">{codeCopied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}</button>
              </div>
              {!reportValidated ? (
                <button className="bg-emerald-600 hover:bg-emerald-500 text-white font-semibold py-2 px-4 rounded-lg transition-colors flex items-center gap-1.5" onClick={() => setReportValidated(true)} data-testid="validate-report-btn"><CheckCircle className="w-4 h-4" />Valider le rapport</button>
              ) : (
                <button className="bg-gradient-to-r from-[#4f6df5] to-[#10b981] hover:from-[#6366f1] hover:to-[#22c55e] text-white font-semibold py-2 px-4 rounded-lg transition-colors flex items-center gap-1.5 shadow-lg shadow-[#4f6df5]/20" onClick={() => navigate("/dashboard")} data-testid="go-dashboard-btn"><Sparkles className="w-4 h-4" />Générer dans votre espace personnel</button>
              )}
              <button className="border border-white/20 text-white/60 hover:text-white hover:border-white/40 font-medium py-2 px-4 rounded-lg transition-colors flex items-center gap-1.5 text-sm" onClick={() => { setResult(null); setAnswers({}); setRankingSelections({}); setCurrentIdx(0); setStep("intro"); setReportValidated(false); }} data-testid="redo-test-btn"><ArrowLeft className="w-4 h-4" />Refaire le test</button>
            </div>
          </div>

          {/* Disclaimer */}
          <div className="bg-[#152a45]/60 border border-amber-500/20 rounded-xl px-5 py-3 flex items-start gap-3 mb-6" data-testid="results-disclaimer">
            <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <p className="text-sm text-slate-400 font-light leading-relaxed">Cette restitution repose sur des méthodes d'analyse de la personnalité et des compétences. Elle a une valeur indicative et ne constitue pas une évaluation certifiée ou officielle.</p>
              <p className="text-sm text-slate-400 font-light leading-relaxed">L'IA reste un outil d'aide à la décision, jamais un substitut au conseiller. Pour une évaluation approfondie, un accompagnement personnalisé est disponible via la plateforme <strong className="text-white font-medium">RE'ACTIF PRO</strong>.</p>
            </div>
          </div>

          <div className="flex flex-col lg:flex-row gap-6">
            {/* Sidebar */}
            <nav className="lg:w-64 shrink-0">
              <div className="bg-[#152a45] rounded-xl border border-white/10 p-2 lg:sticky lg:top-4 space-y-0.5">
                <div className="flex items-center gap-2 px-3 py-2 text-sm font-semibold text-slate-400 border-b border-white/10 mb-1"><BookOpen className="w-4 h-4" />Navigation</div>
                {SECTIONS.map((s) => (
                  <button key={s.id} onClick={() => setActiveSection(s.id)}
                    className={`w-full text-left px-3 py-2 rounded-lg text-sm flex items-center gap-2 transition-all ${activeSection === s.id ? "bg-[#4f6df5]/15 text-[#818cf8] font-semibold" : "text-slate-400 hover:bg-white/5 hover:text-white"}`}
                    data-testid={`nav-${s.id}`}>
                    <span className={`w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold ${activeSection === s.id ? "bg-[#4f6df5] text-white" : "bg-white/10 text-slate-500"}`}>{s.icon}</span>
                    {s.label}
                  </button>
                ))}
              </div>
            </nav>
            {/* Content */}
            <main className="flex-1 bg-[#152a45] rounded-xl border border-white/10 p-6" data-testid="results-content">
              {renderSection()}
            </main>
          </div>
        </div>
      </div>
    );
  }

  // ===================== QUESTIONNAIRE =====================
  if (step !== "questionnaire" || !q) return (
    <div className="min-h-screen bg-[#1e3a5f] flex items-center justify-center">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 border-3 border-[#4f6df5]/30 border-t-[#4f6df5] rounded-full animate-spin" />
        <p className="text-slate-400 text-lg">Chargement...</p>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-[#1e3a5f] relative overflow-hidden">
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-[10%] left-[20%] w-[400px] h-[400px] rounded-full bg-[#4f6df5]/8 blur-[100px]" />
        <div className="absolute bottom-[10%] right-[15%] w-[300px] h-[300px] rounded-full bg-[#6c5ce7]/6 blur-[80px]" />
      </div>
      <div className="relative z-10 max-w-3xl mx-auto px-4 py-6">
        {/* Header */}
        <header className="flex items-center justify-between mb-6">
          <button className="flex items-center gap-2 text-white/50 hover:text-white transition-colors text-sm"
            onClick={() => currentIdx > 0 ? setCurrentIdx(i => i - 1) : setStep("education")} data-testid="back-btn">
            <ArrowLeft className="w-5 h-5" />Retour
          </button>
          <span className="text-white/50 text-sm font-medium">Question {currentIdx + 1} sur {questions.length}</span>
        </header>

        {/* Progress Bar */}
        <div className="h-2 bg-white/10 rounded-full overflow-hidden mb-10">
          <div className="h-full rounded-full bg-gradient-to-r from-[#4f6df5] to-[#10b981] transition-all duration-500" style={{ width: `${progress}%` }} data-testid="progress-bar" />
        </div>

        {/* Question Card */}
        <div className="bg-[#152a45]/80 backdrop-blur-xl rounded-2xl border border-white/10 p-8 shadow-2xl" data-testid={`question-${q.id}`}>
          <div className="mb-8 text-center">
            <span className="text-sm text-[#818cf8] font-medium uppercase tracking-wider">{getCategoryLabel(q.category)}</span>
            <h2 className="text-2xl md:text-3xl font-bold text-white mt-3">{q.question}</h2>
            {q.instruction && <p className="text-sm text-slate-400 mt-2">{q.instruction}</p>}
          </div>

          {isRanking ? (
            <div className="space-y-4">
              <div className="flex justify-center gap-2 mb-4">
                {Array.from({ length: maxRank }, (_, n) => (
                  <span key={n} className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-all ${currentRanking.length > n ? "bg-[#4f6df5] text-white shadow-lg shadow-[#4f6df5]/30" : "bg-white/10 text-slate-500"}`}>{n + 1}</span>
                ))}
              </div>
              <div className={`grid ${q.choices[0]?.image ? "grid-cols-2" : "grid-cols-1"} gap-3`}>
                {q.choices.map(choice => {
                  const rank = getRank(choice.value);
                  const sel = rank !== null;
                  return (
                    <button key={choice.id} disabled={!sel && currentRanking.length >= maxRank}
                      className={`relative rounded-xl border-2 p-3 text-left transition-all ${sel ? "border-[#4f6df5] bg-[#4f6df5]/10 shadow-lg shadow-[#4f6df5]/10" : "border-white/10 hover:border-white/20 bg-white/5"} ${!sel && currentRanking.length >= maxRank ? "opacity-30" : "cursor-pointer"}`}
                      onClick={() => handleRankingSelect(choice)} data-testid={`choice-${choice.id}`}>
                      {sel && <span className="absolute -top-2 -right-2 w-7 h-7 rounded-full bg-[#4f6df5] text-white text-sm font-bold flex items-center justify-center shadow-lg">{rank}</span>}
                      {choice.image && <img src={choice.image} alt={choice.alt || ""} className="w-full h-28 object-cover rounded-lg mb-2" loading="lazy" />}
                      <p className="text-sm font-medium text-white/90">{choice.label}</p>
                    </button>
                  );
                })}
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-4">
              {q.choices.map(choice => {
                const sel = answers[q.id] === choice.value;
                return (
                  <button key={choice.id}
                    className={`relative rounded-xl border-2 p-4 transition-all ${sel ? "border-[#4f6df5] bg-[#4f6df5]/10 shadow-lg shadow-[#4f6df5]/15" : "border-white/10 hover:border-white/20 bg-white/5 hover:bg-white/8"} cursor-pointer group`}
                    onClick={() => handleAnswer(choice.value)} data-testid={`choice-${choice.id}`}>
                    {choice.image && <img src={choice.image} alt={choice.alt || ""} className="w-full h-36 object-cover rounded-lg mb-3" loading="lazy" />}
                    <p className="text-sm font-semibold text-white/90 text-center">{choice.label}</p>
                    {sel && <CheckCircle className="absolute top-2 right-2 w-6 h-6 text-[#4f6df5]" />}
                  </button>
                );
              })}
            </div>
          )}

          {/* Navigation */}
          <div className="flex justify-end mt-8 pt-6 border-t border-white/10">
            <button
              className={`px-8 py-3 rounded-full font-semibold text-white flex items-center gap-2 transition-all ${canProceed && !isSubmitting ? "bg-gradient-to-r from-[#4f6df5] to-[#10b981] hover:shadow-lg hover:shadow-[#4f6df5]/25" : "bg-white/10 text-white/30 cursor-not-allowed"}`}
              disabled={!canProceed || isSubmitting}
              onClick={handleNext} data-testid="next-btn">
              {isSubmitting ? "Analyse en cours..." : currentIdx === questions.length - 1 ? (<>Terminer <CheckCircle className="w-4 h-4" /></>) : (<>Suivant <ArrowRight className="w-4 h-4" /></>)}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DclicTestPage;
