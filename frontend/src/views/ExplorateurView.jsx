import { useState, useEffect } from "react";
import axios from "axios";
import {
  Search, Building2, Briefcase, Target, Heart, ArrowRight,
  Layers, Sparkles, Shield, ChevronRight, Users, BookOpen,
  ArrowLeft, Star
} from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL + "/api";

const VALEURS_LABELS = {
  autonomie: "Autonomie", stimulation: "Stimulation", hedonisme: "Hédonisme",
  realisation_de_soi: "Réalisation de soi", pouvoir: "Pouvoir", securite: "Sécurité",
  conformite: "Conformité", tradition: "Tradition", bienveillance: "Bienveillance",
  universalisme: "Universalisme",
};

const VERTUS_LABELS = {
  sagesse: "Sagesse", courage: "Courage", humanite: "Humanité",
  justice: "Justice", temperance: "Tempérance", transcendance: "Transcendance",
};

/* ====== FICHE MÉTIER COMPLÈTE ====== */
const MetierFiche = ({ data, onBack, onSelectMetier }) => {
  const { filiere, secteur, metier, metiers_similaires } = data;

  return (
    <div className="space-y-5" data-testid="metier-fiche">
      <button onClick={onBack} className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800" data-testid="back-button">
        <ArrowLeft className="w-4 h-4" /> Nouvelle recherche
      </button>

      {/* 1. En-tête : Filière > Secteur > Métier */}
      <div className="bg-gradient-to-r from-slate-800 to-slate-700 rounded-xl p-6 text-white">
        <div className="flex items-center gap-2 text-slate-300 text-xs mb-3">
          <Building2 className="w-3.5 h-3.5" />
          <span>{filiere}</span>
          <ChevronRight className="w-3 h-3" />
          <Layers className="w-3.5 h-3.5" />
          <span>{secteur}</span>
        </div>
        <h2 className="text-2xl font-bold capitalize">{metier.name}</h2>
      </div>

      {/* 2. Mission */}
      {metier.mission && (
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-2">
            <Briefcase className="w-4 h-4 text-slate-400" /> Mission
          </h3>
          <p className="text-sm text-slate-700 leading-relaxed">{metier.mission}</p>
        </div>
      )}

      {/* 3. Métiers similaires */}
      {metiers_similaires?.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-3 flex items-center gap-2">
            <Users className="w-4 h-4 text-slate-400" /> Métiers similaires ({metiers_similaires.length})
          </h3>
          <div className="flex flex-wrap gap-2">
            {metiers_similaires.map((m, i) => (
              <button key={i} onClick={() => onSelectMetier(m)}
                className="text-sm px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg hover:bg-blue-50 hover:border-blue-300 hover:text-blue-700 transition-colors capitalize"
                data-testid={`similar-metier-${i}`}>
                {m}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 4. Savoir-faire / Capacités techniques */}
      {metier.savoirs_faire?.length > 0 && (
        <div className="bg-white rounded-xl border border-blue-100 p-5">
          <h3 className="text-sm font-semibold text-blue-700 uppercase tracking-wider mb-4 flex items-center gap-2">
            <Target className="w-4 h-4" /> Savoir-faire &mdash; Capacités techniques ({metier.savoirs_faire.length})
          </h3>
          <div className="space-y-3">
            {metier.savoirs_faire.map((sf, i) => (
              <div key={i} className="flex gap-3 items-start">
                <div className="w-6 h-6 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">{i + 1}</div>
                <div>
                  <div className="font-semibold text-sm text-slate-800">{sf.name}</div>
                  {sf.capacite_technique && (
                    <p className="text-xs text-slate-500 mt-0.5 leading-relaxed">{sf.capacite_technique}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 5. Chaîne complète : Savoir-être → Capacité pro → Qualités → Valeurs → Vertus */}
      {metier.savoirs_etre?.length > 0 && (
        <div className="bg-white rounded-xl border border-purple-100 p-5">
          <h3 className="text-sm font-semibold text-purple-700 uppercase tracking-wider mb-2 flex items-center gap-2">
            <Heart className="w-4 h-4" /> Chaîne archéologique des compétences
          </h3>
          <p className="text-xs text-slate-400 mb-4">Savoir-être &rarr; Capacité professionnelle &rarr; Qualité humaine &rarr; Valeur &rarr; Vertu</p>

          <div className="space-y-5">
            {metier.savoirs_etre.map((se, i) => (
              <div key={i} className="rounded-lg border border-slate-100 bg-slate-50/50 p-4 space-y-3" data-testid={`se-chain-${i}`}>
                {/* Savoir-être */}
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-purple-500" />
                  <span className="font-semibold text-sm text-purple-800">{se.name}</span>
                  <span className="text-[10px] uppercase bg-purple-100 text-purple-600 px-1.5 py-0.5 rounded font-medium">Savoir-être</span>
                </div>

                {/* Capacité professionnelle */}
                {se.capacite_professionnelle && (
                  <div className="ml-4 flex items-start gap-2">
                    <ArrowRight className="w-3.5 h-3.5 text-indigo-400 mt-0.5 flex-shrink-0" />
                    <div>
                      <span className="text-[10px] uppercase text-indigo-500 font-semibold">Capacité professionnelle</span>
                      <p className="text-xs text-slate-600 leading-relaxed">{se.capacite_professionnelle}</p>
                    </div>
                  </div>
                )}

                {/* Qualités humaines */}
                {se.qualites_humaines?.length > 0 && (
                  <div className="ml-8 flex items-center gap-2">
                    <ArrowRight className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />
                    <span className="text-[10px] uppercase text-amber-600 font-semibold">Qualités :</span>
                    {se.qualites_humaines.map((q, qi) => (
                      <span key={qi} className="text-xs px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 border border-amber-200 font-medium">{q}</span>
                    ))}
                  </div>
                )}

                {/* Valeurs */}
                {se.valeurs?.length > 0 && (
                  <div className="ml-12 flex items-center gap-2">
                    <ArrowRight className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                    <span className="text-[10px] uppercase text-emerald-600 font-semibold">Valeurs :</span>
                    {se.valeurs.map((v, vi) => (
                      <span key={vi} className="text-xs px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 font-medium">{VALEURS_LABELS[v] || v}</span>
                    ))}
                  </div>
                )}

                {/* Vertus */}
                {se.vertus?.length > 0 && (
                  <div className="ml-16 flex items-center gap-2">
                    <ArrowRight className="w-3.5 h-3.5 text-rose-400 flex-shrink-0" />
                    <span className="text-[10px] uppercase text-rose-600 font-semibold">Vertus :</span>
                    {se.vertus.map((vt, vti) => (
                      <span key={vti} className="text-xs px-2 py-0.5 rounded-full bg-rose-50 text-rose-700 border border-rose-200 font-medium">{VERTUS_LABELS[vt] || vt}</span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

/* ====== VUE PRINCIPALE ====== */
const ExplorateurView = ({ token }) => {
  const [stats, setStats] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [selectedMetier, setSelectedMetier] = useState(null);
  const [loading, setLoading] = useState(false);
  const [allMetiers, setAllMetiers] = useState([]);

  useEffect(() => {
    axios.get(`${API}/referentiel/explorer/stats`).then(r => setStats(r.data)).catch(() => {});
    // Load all metier names for autocomplete
    axios.get(`${API}/referentiel/explorer`).then(r => {
      const metiers = [];
      for (const f of r.data.filieres) {
        for (const s of f.secteurs) {
          metiers.push(...(s.metiers || []).map(m => ({ name: m, secteur: s.name, filiere: f.name })));
        }
      }
      setAllMetiers(metiers);
    }).catch(() => {});
  }, []);

  // Load metier names for secteurs that have metiers_count > 0
  useEffect(() => {
    if (allMetiers.length > 0) return;
    // fallback: use search API
  }, [allMetiers]);

  const handleSearch = (q) => {
    setSearchQuery(q);
    if (q.length < 2) { setSuggestions([]); return; }
    const qLow = q.toLowerCase();
    // Search in all metiers + also search via API
    const local = allMetiers.filter(m => {
      const name = typeof m === "string" ? m : m.name;
      return name.toLowerCase().includes(qLow);
    }).slice(0, 8);

    if (local.length > 0) {
      setSuggestions(local);
    } else {
      axios.get(`${API}/referentiel/explorer/search?q=${encodeURIComponent(q)}`).then(r => {
        setSuggestions(r.data.metiers?.slice(0, 8) || []);
      }).catch(() => {});
    }
  };

  const selectMetier = async (name) => {
    setLoading(true);
    setSuggestions([]);
    setSearchQuery(name);
    try {
      const res = await axios.get(`${API}/referentiel/explorer/metier/${encodeURIComponent(name)}`);
      setSelectedMetier(res.data);
    } catch {
      setSelectedMetier(null);
    }
    setLoading(false);
  };

  const handleBack = () => {
    setSelectedMetier(null);
    setSearchQuery("");
    setSuggestions([]);
  };

  if (selectedMetier) {
    return <MetierFiche data={selectedMetier} onBack={handleBack} onSelectMetier={selectMetier} />;
  }

  return (
    <div className="space-y-6" data-testid="explorateur-view">
      {/* Header */}
      <div className="text-center pt-4">
        <h2 className="text-xl font-bold text-slate-800 flex items-center justify-center gap-2">
          <Layers className="w-5 h-5 text-blue-600" /> Explorateur des Métiers
        </h2>
        <p className="text-sm text-slate-500 mt-2 max-w-xl mx-auto">
          Saisissez un métier pour découvrir sa filière, ses missions, ses compétences et remonter toute la chaîne archéologique jusqu'aux vertus fondamentales.
        </p>
      </div>

      {/* Search bar - Primary entry point */}
      <div className="relative max-w-2xl mx-auto">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
        <input
          type="text"
          value={searchQuery}
          onChange={e => handleSearch(e.target.value)}
          placeholder="Saisissez un métier : ingénieur, chef de projet, développeur..."
          className="w-full pl-12 pr-4 py-4 rounded-xl border-2 border-slate-200 text-base focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-400 shadow-sm"
          data-testid="explorer-search-input"
          autoFocus
        />

        {/* Suggestions dropdown */}
        {suggestions.length > 0 && (
          <div className="absolute top-full left-0 right-0 mt-1 bg-white rounded-xl border border-slate-200 shadow-lg z-20 overflow-hidden" data-testid="search-suggestions">
            {suggestions.map((s, i) => {
              const name = typeof s === "string" ? s : s.name;
              const filiere = typeof s === "object" ? s.filiere : "";
              return (
                <button key={i} onClick={() => selectMetier(name)}
                  className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-blue-50 transition-colors border-b border-slate-50 last:border-0"
                  data-testid={`suggestion-${i}`}>
                  <div className="flex items-center gap-2">
                    <Briefcase className="w-4 h-4 text-slate-400" />
                    <span className="text-sm font-medium text-slate-700 capitalize">{name}</span>
                  </div>
                  {filiere && <span className="text-xs text-slate-400">{filiere}</span>}
                </button>
              );
            })}
          </div>
        )}
      </div>

      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        </div>
      )}

      {/* Stats + Quick access */}
      {!loading && !selectedMetier && (
        <>
          {stats && (
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 max-w-3xl mx-auto">
              {[
                { icon: Building2, label: "Filières", value: stats.filieres, c: "blue" },
                { icon: Layers, label: "Secteurs", value: stats.secteurs, c: "indigo" },
                { icon: Briefcase, label: "Métiers", value: stats.metiers, c: "slate" },
                { icon: Target, label: "Savoir-faire", value: stats.savoirs_faire, c: "emerald" },
                { icon: Heart, label: "Savoir-être", value: stats.savoirs_etre, c: "purple" },
              ].map(({ icon: Icon, label, value, c }, i) => (
                <div key={i} className="flex items-center gap-2 bg-white rounded-xl p-3 border border-slate-100 shadow-sm">
                  <Icon className={`w-4 h-4 text-${c}-600`} />
                  <div>
                    <div className="text-lg font-bold text-slate-800">{value}</div>
                    <div className="text-[10px] text-slate-500">{label}</div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Quick access - sample métiers */}
          <div className="max-w-2xl mx-auto">
            <p className="text-xs text-slate-400 uppercase tracking-wider mb-2 font-semibold">Exemples de métiers</p>
            <div className="flex flex-wrap gap-2">
              {allMetiers.slice(0, 12).map((m, i) => {
                const name = typeof m === "string" ? m : m.name;
                return (
                  <button key={i} onClick={() => selectMetier(name)}
                    className="text-sm px-3 py-1.5 bg-white border border-slate-200 rounded-lg hover:bg-blue-50 hover:border-blue-300 hover:text-blue-700 transition-colors capitalize"
                    data-testid={`quick-metier-${i}`}>
                    {name}
                  </button>
                );
              })}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default ExplorateurView;
