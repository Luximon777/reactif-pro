import axios from "axios";
import { API } from "@/App";

export const token = () => localStorage.getItem("reactif_token");

const http = axios.create();
let redirecting = false;
http.interceptors.response.use(
  r => r,
  err => {
    if (err.response?.status === 401 && !redirecting) {
      redirecting = true;
      window.location.href = "/?session=expiree";
    }
    return Promise.reject(err);
  }
);

export const u2 = {
  get: (path, params = {}) => http.get(`${API}/ubuntoo2${path}`, { params: { token: token(), ...params } }),
  post: (path, body = {}, params = {}) => http.post(`${API}/ubuntoo2${path}`, body, { params: { token: token(), ...params } }),
  put: (path, body = {}) => http.put(`${API}/ubuntoo2${path}`, body, { params: { token: token() } }),
};

export const POST_TYPES = {
  question: { label: "Question", cls: "bg-amber-100 text-amber-900 border-amber-300" },
  experience: { label: "Expérience", cls: "bg-emerald-100 text-emerald-900 border-emerald-300" },
  information: { label: "Information", cls: "bg-blue-100 text-blue-900 border-blue-300" },
  ressource: { label: "Ressource", cls: "bg-purple-100 text-purple-900 border-purple-300" },
  opportunite: { label: "Opportunité", cls: "bg-orange-100 text-orange-900 border-orange-300" },
  aide: { label: "Demande d'aide", cls: "bg-rose-100 text-rose-900 border-rose-300" },
};

export const CATEGORIES = {
  metiers: "Métiers",
  situations: "Situations professionnelles",
  territoires: "Territoires",
  thematiques: "Thématiques",
};

export const HELP_OFFERS = ["Mentorat", "Partage d'expérience", "Conseil métier", "Découverte d'un secteur", "Préparation d'entretien", "Réseau", "Orientation"];

export const REPORT_REASONS = ["Comportement inapproprié", "Discrimination", "Harcèlement", "Spam", "Fraude", "Contenu commercial non autorisé", "Fausse information professionnelle", "Atteinte à la confidentialité"];

export const PRIVACY_LEVELS = [
  { value: "prive", label: "Privé", desc: "Visible uniquement par vous" },
  { value: "reseau", label: "Réseau UBUNTOO", desc: "Visible par vos contacts acceptés" },
  { value: "public", label: "Professionnel", desc: "Visible par tous les membres" },
];

export const BADGES_META = {
  bienvenue: { label: "Bienvenue UBUNTOO", icon: "Sprout", cls: "bg-emerald-50 text-emerald-700 border-emerald-200" },
  profil_pro: { label: "Profil professionnel", icon: "UserCheck", cls: "bg-teal-50 text-teal-700 border-teal-200" },
  premier_echange: { label: "Premier échange", icon: "MessageCircle", cls: "bg-sky-50 text-sky-700 border-sky-200" },
  explorateur: { label: "Explorateur", icon: "Compass", cls: "bg-blue-50 text-blue-700 border-blue-200" },
  coup_de_pouce: { label: "Coup de pouce", icon: "HandHeart", cls: "bg-orange-50 text-orange-700 border-orange-200" },
  partageur_experience: { label: "Partageur d'expérience", icon: "BookOpen", cls: "bg-amber-50 text-amber-800 border-amber-200" },
  eclaireur_metier: { label: "Éclaireur métier", icon: "Lightbulb", cls: "bg-yellow-50 text-yellow-800 border-yellow-300" },
  connecteur: { label: "Connecteur", icon: "Link2", cls: "bg-indigo-50 text-indigo-700 border-indigo-200" },
  partageur_opportunites: { label: "Partageur d'opportunités", icon: "Gift", cls: "bg-rose-50 text-rose-700 border-rose-200" },
  bienveillant: { label: "Bienveillant", icon: "Heart", cls: "bg-pink-50 text-pink-700 border-pink-200" },
  esprit_collectif: { label: "Esprit collectif", icon: "UsersRound", cls: "bg-violet-50 text-violet-700 border-violet-200" },
  passeport_pro: { label: "Passeport professionnel", icon: "ShieldCheck", cls: "bg-[#2E7D5B]/10 text-[#2E7D5B] border-[#2E7D5B]/30" },
};

export const RECOGNITION_TYPES = {
  partage_experience: "Partage d'expérience",
  conseil: "Conseil",
  information_metier: "Information métier",
  mise_en_relation: "Mise en relation",
  encouragement: "Encouragement",
  partage_opportunite: "Partage d'opportunité",
};

export const timeAgo = (iso) => {
  if (!iso) return "";
  const diff = (Date.now() - new Date(iso).getTime()) / 1000;
  if (diff < 60) return "à l'instant";
  if (diff < 3600) return `il y a ${Math.floor(diff / 60)} min`;
  if (diff < 86400) return `il y a ${Math.floor(diff / 3600)} h`;
  return `il y a ${Math.floor(diff / 86400)} j`;
};
