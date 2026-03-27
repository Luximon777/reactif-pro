import {
  User, Briefcase, GraduationCap, Sparkles, Brain, MessageCircle,
  TrendingUp, Activity, BookOpen, Zap, Hexagon, CircleDot, ArrowRight, FolderLock, Award, Flower2
} from "lucide-react";

export const SOURCE_CONFIG = {
  declaratif: { label: "Déclaré", color: "bg-slate-100 text-slate-600", icon: User },
  coffre_fort: { label: "Coffre-fort", color: "bg-blue-100 text-blue-700", icon: FolderLock },
  profil: { label: "Profil", color: "bg-indigo-100 text-indigo-700", icon: User },
  module: { label: "Formation", color: "bg-emerald-100 text-emerald-700", icon: GraduationCap },
  plateforme: { label: "RE'ACTIF PRO", color: "bg-blue-100 text-blue-700", icon: BookOpen },
  ubuntoo: { label: "Ubuntoo", color: "bg-teal-100 text-teal-700", icon: MessageCircle },
  ia_detectee: { label: "Détecté IA", color: "bg-violet-100 text-violet-700", icon: Brain },
  dclic_pro: { label: "D'CLIC PRO", color: "bg-emerald-100 text-emerald-700", icon: Award },
  centres_interet: { label: "Centres d'intérêt", color: "bg-pink-100 text-pink-700", icon: Flower2 },
  contribution: { label: "Contribution", color: "bg-amber-100 text-amber-700", icon: Sparkles },
};

export const LEVEL_CONFIG = {
  debutant: { label: "Débutant", color: "bg-slate-200 text-slate-700", width: 25 },
  intermediaire: { label: "Intermédiaire", color: "bg-blue-200 text-blue-700", width: 50 },
  avance: { label: "Avancé", color: "bg-emerald-200 text-emerald-700", width: 75 },
  expert: { label: "Expert", color: "bg-amber-200 text-amber-700", width: 100 },
};

export const CATEGORY_CONFIG = {
  technique: { label: "Technique", color: "text-blue-700 bg-blue-50 border-blue-200", desc: "Compétence spécifique à un métier" },
  transversale: { label: "Transversale", color: "text-violet-700 bg-violet-50 border-violet-200", desc: "Universelle, commune à différents métiers et secteurs" },
  transferable: { label: "Transférable", color: "text-amber-700 bg-amber-50 border-amber-200", desc: "Mobilisable dans un même secteur ou entreprise" },
  sectorielle: { label: "Sectorielle", color: "text-slate-700 bg-slate-50 border-slate-200", desc: "Propre à un secteur d'activité" },
};

export const NATURE_CONFIG = {
  savoir_faire: { label: "Savoir-faire", color: "bg-sky-600 text-white", icon: Briefcase, bgLight: "bg-sky-50 border-sky-200 text-sky-700" },
  savoir_etre: { label: "Savoir-être", color: "bg-rose-500 text-white", icon: Activity, bgLight: "bg-rose-50 border-rose-200 text-rose-700" },
};

export const CCSP_POLES = {
  realisation: { label: "Réalisation", color: "bg-blue-600", textColor: "text-blue-700", bgLight: "bg-blue-50" },
  interaction: { label: "Interaction", color: "bg-emerald-600", textColor: "text-emerald-700", bgLight: "bg-emerald-50" },
  initiative: { label: "Initiative", color: "bg-amber-600", textColor: "text-amber-700", bgLight: "bg-amber-50" },
};

export const CCSP_DEGREES = {
  imitation: { label: "Imitation", color: "bg-slate-500", level: 1 },
  adaptation: { label: "Adaptation", color: "bg-blue-500", level: 2 },
  transposition: { label: "Transposition", color: "bg-emerald-500", level: 3 },
};

export const COMPONENT_LABELS = {
  connaissance: { label: "Connaissance", short: "Sav.", desc: "Savoirs théoriques et factuels", icon: BookOpen, color: "#3b82f6" },
  cognition: { label: "Cognition", short: "Cog.", desc: "Analyse, raisonnement, résolution", icon: Brain, color: "#8b5cf6" },
  conation: { label: "Conation", short: "Con.", desc: "Motivation, volonté, engagement", icon: Zap, color: "#f59e0b" },
  affection: { label: "Affection", short: "Aff.", desc: "Gestion émotionnelle, empathie", icon: Activity, color: "#ef4444" },
  sensori_moteur: { label: "Sensori-moteur", short: "S-M.", desc: "Habiletés physiques et pratiques", icon: Hexagon, color: "#10b981" },
};

export const NIVEAU_CONFIG = {
  signal_faible: { label: "Signal faible", color: "bg-slate-100 text-slate-600", barColor: "#94a3b8", width: 20 },
  emergente: { label: "Émergente", color: "bg-violet-100 text-violet-700", barColor: "#8b5cf6", width: 45 },
  en_croissance: { label: "En croissance", color: "bg-amber-100 text-amber-700", barColor: "#f59e0b", width: 70 },
  etablie: { label: "Établie", color: "bg-emerald-100 text-emerald-700", barColor: "#10b981", width: 95 },
};

export const CATEGORIE_EMERGING_CONFIG = {
  tech_emergente: { label: "Tech émergente", color: "text-blue-700 bg-blue-50" },
  hybride: { label: "Hybride", color: "text-purple-700 bg-purple-50" },
  soft_skill_avancee: { label: "Soft skill avancée", color: "text-rose-700 bg-rose-50" },
  methodologique: { label: "Méthodologique", color: "text-teal-700 bg-teal-50" },
  sectorielle: { label: "Sectorielle", color: "text-orange-700 bg-orange-50" },
};

export const TENDANCE_CONFIG = {
  hausse: { label: "En hausse", icon: TrendingUp, color: "text-emerald-600" },
  stable: { label: "Stable", icon: ArrowRight, color: "text-slate-500" },
  nouvelle: { label: "Nouvelle", icon: Sparkles, color: "text-violet-600" },
};

export const VERTU_COLORS = {
  sagesse: { bg: "bg-blue-50", text: "text-blue-700", border: "border-blue-300", accent: "#3b82f6" },
  courage: { bg: "bg-red-50", text: "text-red-700", border: "border-red-300", accent: "#ef4444" },
  humanite: { bg: "bg-rose-50", text: "text-rose-700", border: "border-rose-300", accent: "#f43f5e" },
  justice: { bg: "bg-amber-50", text: "text-amber-700", border: "border-amber-300", accent: "#f59e0b" },
  temperance: { bg: "bg-teal-50", text: "text-teal-700", border: "border-teal-300", accent: "#14b8a6" },
  transcendance: { bg: "bg-violet-50", text: "text-violet-700", border: "border-violet-300", accent: "#8b5cf6" },
};
