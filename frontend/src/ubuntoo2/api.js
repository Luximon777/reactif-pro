import axios from "axios";
import { API } from "@/App";

export const token = () => localStorage.getItem("reactif_token");
export const u2 = {
  get: (path, params = {}) => axios.get(`${API}/ubuntoo2${path}`, { params: { token: token(), ...params } }),
  post: (path, body = {}, params = {}) => axios.post(`${API}/ubuntoo2${path}`, body, { params: { token: token(), ...params } }),
  put: (path, body = {}) => axios.put(`${API}/ubuntoo2${path}`, body, { params: { token: token() } }),
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

export const timeAgo = (iso) => {
  if (!iso) return "";
  const diff = (Date.now() - new Date(iso).getTime()) / 1000;
  if (diff < 60) return "à l'instant";
  if (diff < 3600) return `il y a ${Math.floor(diff / 60)} min`;
  if (diff < 86400) return `il y a ${Math.floor(diff / 3600)} h`;
  return `il y a ${Math.floor(diff / 86400)} j`;
};
