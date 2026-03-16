import { useState, useEffect } from "react";
import axios from "axios";
import {
  ChevronRight, ChevronDown, Search, Building2, Briefcase,
  Target, Users, ArrowLeft, Layers, Sparkles, Heart, Shield,
  BookOpen
} from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL + "/api";

const StatCard = ({ icon: Icon, label, value, color }) => (
  <div className={`flex items-center gap-3 bg-white rounded-xl p-4 border border-${color}-100 shadow-sm`}>
    <div className={`w-10 h-10 rounded-lg bg-${color}-50 flex items-center justify-center`}>
      <Icon className={`w-5 h-5 text-${color}-600`} />
    </div>
    <div>
      <div className="text-2xl font-bold text-slate-800">{value}</div>
      <div className="text-xs text-slate-500">{label}</div>
    </div>
  </div>
);

const ChainBadge = ({ items, color, label }) => {
  if (!items || items.length === 0) return null;
  return (
    <div className="flex flex-wrap items-center gap-1 mt-1">
      <span className={`text-[10px] font-semibold text-${color}-600 uppercase tracking-wider`}>{label}:</span>
      {items.map((item, i) => (
        <span key={i} className={`text-xs px-2 py-0.5 rounded-full bg-${color}-50 text-${color}-700 border border-${color}-200`}>
          {item}
        </span>
      ))}
    </div>
  );
};

const MetierDetail = ({ filiere, secteur, metier, onBack }) => (
  <div className="space-y-4" data-testid="metier-detail">
    <button onClick={onBack} className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800 transition-colors" data-testid="back-button">
      <ArrowLeft className="w-4 h-4" /> Retour
    </button>

    <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
      <div className="flex items-center gap-2 text-xs text-slate-400 mb-2">
        <Building2 className="w-3 h-3" />{filiere}
        <ChevronRight className="w-3 h-3" />{secteur}
      </div>
      <h2 className="text-xl font-bold text-slate-800 mb-1">{metier.name}</h2>
      {metier.mission && <p className="text-sm text-slate-600 leading-relaxed">{metier.mission}</p>}
    </div>

    {metier.savoirs_faire?.length > 0 && (
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
        <h3 className="font-semibold text-slate-700 mb-3 flex items-center gap-2">
          <Target className="w-4 h-4 text-blue-600" /> Savoir-faire ({metier.savoirs_faire.length})
        </h3>
        <div className="space-y-3">
          {metier.savoirs_faire.map((sf, i) => (
            <div key={i} className="border-l-2 border-blue-300 pl-3">
              <div className="font-medium text-sm text-slate-800">{sf.name}</div>
              {sf.capacite_technique && (
                <p className="text-xs text-slate-500 mt-0.5 leading-relaxed">{sf.capacite_technique}</p>
              )}
            </div>
          ))}
        </div>
      </div>
    )}

    {metier.savoirs_etre?.length > 0 && (
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
        <h3 className="font-semibold text-slate-700 mb-3 flex items-center gap-2">
          <Heart className="w-4 h-4 text-purple-600" /> Savoir-être ({metier.savoirs_etre.length})
        </h3>
        <div className="space-y-4">
          {metier.savoirs_etre.map((se, i) => (
            <div key={i} className="border-l-2 border-purple-300 pl-3 space-y-1">
              <div className="font-medium text-sm text-slate-800">{se.name}</div>
              {se.capacite_professionnelle && (
                <p className="text-xs text-slate-500 leading-relaxed">{se.capacite_professionnelle}</p>
              )}
              <ChainBadge items={se.qualites_humaines} color="amber" label="Qualités" />
              <ChainBadge items={se.valeurs} color="emerald" label="Valeurs" />
              <ChainBadge items={se.vertus} color="rose" label="Vertus" />
            </div>
          ))}
        </div>
      </div>
    )}
  </div>
);

const ExplorateurView = ({ token }) => {
  const [filieres, setFilieres] = useState([]);
  const [stats, setStats] = useState(null);
  const [expandedFiliere, setExpandedFiliere] = useState(null);
  const [expandedSecteur, setExpandedSecteur] = useState(null);
  const [secteurData, setSecteurData] = useState({});
  const [selectedMetier, setSelectedMetier] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      axios.get(`${API}/referentiel/explorer`),
      axios.get(`${API}/referentiel/explorer/stats`),
    ]).then(([filRes, statsRes]) => {
      setFilieres(filRes.data.filieres);
      setStats(statsRes.data);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const loadSecteur = async (name) => {
    if (secteurData[name]) return;
    try {
      const res = await axios.get(`${API}/referentiel/explorer/secteur/${encodeURIComponent(name)}`);
      setSecteurData(prev => ({ ...prev, [name]: res.data }));
    } catch {}
  };

  const loadMetier = async (name) => {
    try {
      const res = await axios.get(`${API}/referentiel/explorer/metier/${encodeURIComponent(name)}`);
      setSelectedMetier(res.data);
    } catch {}
  };

  const handleSearch = async (q) => {
    setSearchQuery(q);
    if (q.length < 2) { setSearchResults(null); return; }
    try {
      const res = await axios.get(`${API}/referentiel/explorer/search?q=${encodeURIComponent(q)}`);
      setSearchResults(res.data);
    } catch {}
  };

  if (loading) {
    return <div className="flex items-center justify-center h-40"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" /></div>;
  }

  if (selectedMetier) {
    return <MetierDetail filiere={selectedMetier.filiere} secteur={selectedMetier.secteur} metier={selectedMetier.metier} onBack={() => setSelectedMetier(null)} />;
  }

  return (
    <div className="space-y-5" data-testid="explorateur-view">
      <div>
        <h2 className="text-lg font-bold text-slate-800 flex items-center gap-2">
          <Layers className="w-5 h-5 text-blue-600" /> Explorateur des Filières Professionnelles
        </h2>
        <p className="text-sm text-slate-500 mt-1">Naviguez dans la chaîne : Filière &rarr; Secteur &rarr; Métier &rarr; Compétences &rarr; Qualités &rarr; Valeurs &rarr; Vertus</p>
      </div>

      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
          <StatCard icon={Building2} label="Filières" value={stats.filieres} color="blue" />
          <StatCard icon={Layers} label="Secteurs" value={stats.secteurs} color="indigo" />
          <StatCard icon={Briefcase} label="Métiers" value={stats.metiers} color="slate" />
          <StatCard icon={Target} label="Savoir-faire" value={stats.savoirs_faire} color="emerald" />
          <StatCard icon={Heart} label="Savoir-être" value={stats.savoirs_etre} color="purple" />
        </div>
      )}

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
        <input
          type="text"
          value={searchQuery}
          onChange={e => handleSearch(e.target.value)}
          placeholder="Rechercher un métier, une compétence, une filière..."
          className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-400"
          data-testid="explorer-search-input"
        />
      </div>

      {/* Search Results */}
      {searchResults && searchQuery.length >= 2 && (
        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm space-y-3" data-testid="search-results">
          {Object.entries(searchResults).map(([type, items]) => items.length > 0 && (
            <div key={type}>
              <div className="text-xs font-semibold text-slate-400 uppercase mb-1">
                {type === "filieres" ? "Filières" : type === "secteurs" ? "Secteurs" : type === "metiers" ? "Métiers" : type === "savoirs_faire" ? "Savoir-faire" : "Savoir-être"}
              </div>
              {items.slice(0, 5).map((item, i) => (
                <button key={i} onClick={() => item.type === "metier" ? loadMetier(item.name) : null}
                  className="block w-full text-left px-3 py-1.5 text-sm hover:bg-blue-50 rounded-lg transition-colors">
                  <span className="font-medium text-slate-700">{item.name}</span>
                  {item.filiere && <span className="text-xs text-slate-400 ml-2">{item.filiere}</span>}
                  {item.metier && <span className="text-xs text-slate-400 ml-2">{item.metier}</span>}
                </button>
              ))}
            </div>
          ))}
          {Object.values(searchResults).every(v => v.length === 0) && (
            <p className="text-sm text-slate-400 text-center py-2">Aucun résultat pour "{searchQuery}"</p>
          )}
        </div>
      )}

      {/* Filières Tree */}
      {!searchResults && (
        <div className="space-y-2" data-testid="filieres-tree">
          {filieres.map((filiere) => (
            <div key={filiere.id} className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
              <button
                onClick={() => setExpandedFiliere(expandedFiliere === filiere.id ? null : filiere.id)}
                className="w-full flex items-center justify-between px-4 py-3 hover:bg-slate-50 transition-colors"
                data-testid={`filiere-${filiere.id}`}
              >
                <div className="flex items-center gap-2">
                  {expandedFiliere === filiere.id ? <ChevronDown className="w-4 h-4 text-blue-600" /> : <ChevronRight className="w-4 h-4 text-slate-400" />}
                  <Building2 className="w-4 h-4 text-blue-600" />
                  <span className="font-medium text-sm text-slate-800">{filiere.name}</span>
                </div>
                <span className="text-xs text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">{filiere.secteurs.length} secteurs</span>
              </button>

              {expandedFiliere === filiere.id && (
                <div className="border-t border-slate-100 bg-slate-50/50 px-4 py-2 space-y-1">
                  {filiere.secteurs.map((secteur, si) => (
                    <div key={si}>
                      <button
                        onClick={() => {
                          const key = secteur.name;
                          setExpandedSecteur(expandedSecteur === key ? null : key);
                          loadSecteur(key);
                        }}
                        className="w-full flex items-center justify-between px-3 py-2 hover:bg-white rounded-lg transition-colors"
                        data-testid={`secteur-${secteur.name}`}
                      >
                        <div className="flex items-center gap-2">
                          {expandedSecteur === secteur.name ? <ChevronDown className="w-3.5 h-3.5 text-indigo-600" /> : <ChevronRight className="w-3.5 h-3.5 text-slate-400" />}
                          <Layers className="w-3.5 h-3.5 text-indigo-500" />
                          <span className="text-sm text-slate-700">{secteur.name}</span>
                        </div>
                        {secteur.metiers_count > 0 && (
                          <span className="text-xs text-slate-400">{secteur.metiers_count} métiers</span>
                        )}
                      </button>

                      {expandedSecteur === secteur.name && secteurData[secteur.name] && (
                        <div className="ml-8 py-1 space-y-0.5">
                          {secteurData[secteur.name].metiers.map((metier, mi) => (
                            <button
                              key={mi}
                              onClick={() => loadMetier(metier.name)}
                              className="w-full flex items-center gap-2 px-3 py-2 text-left hover:bg-blue-50 rounded-lg transition-colors group"
                              data-testid={`metier-${metier.name}`}
                            >
                              <Briefcase className="w-3.5 h-3.5 text-slate-400 group-hover:text-blue-600 flex-shrink-0" />
                              <div className="min-w-0">
                                <div className="text-sm text-slate-700 group-hover:text-blue-700 font-medium truncate">{metier.name}</div>
                                {metier.mission && <div className="text-xs text-slate-400 truncate">{metier.mission.substring(0, 80)}...</div>}
                              </div>
                              <ChevronRight className="w-3.5 h-3.5 text-slate-300 group-hover:text-blue-400 ml-auto flex-shrink-0" />
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ExplorateurView;
