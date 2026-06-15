import { useState, useEffect } from "react";
import axios from "axios";
import { LockKeyhole, Home, Loader2 } from "lucide-react";
import OpcView from "@/views/OpcView";

const API = `${process.env.REACT_APP_BACKEND_URL || ""}/api`;

const OpcPublicPage = () => {
  const [spacesOpen, setSpacesOpen] = useState(null); // null = loading

  useEffect(() => {
    axios.get(`${API}/admin/gate-state`)
      .then(res => setSpacesOpen(res.data.spaces_open === true))
      .catch(() => setSpacesOpen(false));
  }, []);

  if (spacesOpen === null) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <Loader2 className="w-8 h-8 text-slate-400 animate-spin" />
      </div>
    );
  }

  if (!spacesOpen) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 px-6" data-testid="opc-closed">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-xl border border-slate-200 p-8 text-center">
          <div className="w-16 h-16 rounded-full bg-red-50 flex items-center justify-center mx-auto mb-4">
            <LockKeyhole className="w-8 h-8 text-red-500" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900 mb-2" style={{ fontFamily: "Outfit, sans-serif" }}>
            Accès fermé temporairement
          </h1>
          <p className="text-sm text-slate-500 leading-relaxed mb-6">
            L'Observatoire Prédictif des Compétences n'est pas accessible pour le moment.<br />
            L'administrateur de la plateforme RE'ACTIF PRO a temporairement clôturé les espaces.<br />
            Reviens un peu plus tard !
          </p>
          <button
            onClick={() => { window.location.href = "/"; }}
            className="inline-flex items-center gap-2 px-5 py-2 rounded-full bg-[#1e3a5f] hover:bg-[#2d5a8e] text-white font-semibold text-sm transition-colors"
            data-testid="opc-back-home"
          >
            <Home className="w-4 h-4" /> Retour à l'accueil
          </button>
        </div>
      </div>
    );
  }

  return <OpcView token={null} isPublic={true} />;
};

export default OpcPublicPage;
