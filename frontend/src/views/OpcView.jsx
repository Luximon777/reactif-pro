import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  BarChart3, TrendingUp, TrendingDown, Users, Brain, Sparkles, Award, Target,
  Briefcase, GraduationCap, Loader2, ArrowRight, Zap, Globe,
  CheckCircle2, AlertTriangle, RefreshCw, Compass, Shield, Search,
  Eye, Activity, Minus
} from "lucide-react";
import { toast } from "sonner";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar, CartesianGrid, RadarChart, PolarGrid, PolarAngleAxis, Radar } from "recharts";
import ActualisationOPC from "@/components/ActualisationOPC";
import { useAuth } from "@/App";

const CorrelationsBlock = ({ correlations, compact = false }) => {
  if (!correlations || correlations.length === 0) return null;
  const items = compact ? correlations.slice(0, 4) : correlations;
  return (
    <Card data-testid="correlations-block">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm flex items-center gap-2"><Zap className="w-4 h-4 text-blue-600" />Hard Skills liés aux Savoir-être</CardTitle>
        {!compact && <CardDescription className="text-[10px]">Pour chaque compétence technique, les savoir-être professionnels nécessaires</CardDescription>}
      </CardHeader>
      <CardContent className="space-y-2">
        {items.map((c, i) => (
          <div key={i} className="p-2.5 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-100">
            <div className="flex items-center gap-2 mb-1.5">
              <Briefcase className="w-3.5 h-3.5 text-blue-600 shrink-0" />
              <p className="text-xs font-semibold text-blue-900">{c.competence_technique}</p>
            </div>
            <div className={`grid ${compact ? "grid-cols-2" : "grid-cols-1 sm:grid-cols-2 lg:grid-cols-3"} gap-1`}>
              {(c.savoir_etre || []).map((se, j) => (
                <div key={j} className="flex items-center gap-1.5 bg-white rounded px-2 py-1 border border-blue-100">
                  <Award className="w-2.5 h-2.5 text-rose-500 shrink-0" />
                  <span className="text-[9px] text-slate-800 flex-1">{se.nom}</span>
                  <div className="flex gap-px">{[1,2,3,4,5].map(n => <div key={n} className={`w-1 h-1 rounded-full ${n <= se.importance ? "bg-blue-500" : "bg-slate-200"}`} />)}</div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
};

const ReferentielSearch = ({ token, onContextUpdate, onSearchActive }) => {
  const [query, setQuery] = useState("");
  const [selectedFiliere, setSelectedFiliere] = useState("all");
  const [selectedSecteur, setSelectedSecteur] = useState("all");
  const [selectedMetier, setSelectedMetier] = useState("all");
  const [selectedGrandDomaine, setSelectedGrandDomaine] = useState("all");
  const [selectedDomaine, setSelectedDomaine] = useState("all");
  const [filieres, setFilieres] = useState([]);
  const [secteurs, setSecteurs] = useState([]);
  const [metiers, setMetiers] = useState([]);
  const [grandDomaines, setGrandDomaines] = useState([]);
  const [romeDomainesList, setRomeDomainesList] = useState([]);
  const [romeResults, setRomeResults] = useState([]);
  const [results, setResults] = useState(null);
  const [searching, setSearching] = useState(false);
  const [searchMode, setSearchMode] = useState("interne"); // "interne" or "rome"

  useEffect(() => {
    axios.get(`${API}/referentiel/filieres?${token ? 'token='+token : ''}`).then(r => {
      setFilieres(r.data.filieres || []);
    }).catch(() => {});
    // Load ROME grand domaines
    axios.get(`${API}/referentiel/rome/domaines`).then(r => {
      setGrandDomaines(r.data.grand_domaines || []);
    }).catch(() => {});
  }, [token]);

  useEffect(() => {
    if (selectedFiliere && selectedFiliere !== "all") {
      const f = filieres.find(f => f.code === selectedFiliere);
      setSecteurs(f?.secteurs || []);
    } else {
      setSecteurs([]);
    }
    setSelectedSecteur("all");
    setSelectedMetier("all");
    setMetiers([]);
  }, [selectedFiliere, filieres]);

  // Load metiers when secteur changes
  useEffect(() => {
    if (selectedSecteur && selectedSecteur !== "all") {
      const params = new URLSearchParams();
      if (token) params.append("token", token);
      if (selectedFiliere !== "all") params.append("filiere", selectedFiliere);
      params.append("secteur", selectedSecteur);
      axios.get(`${API}/referentiel/metiers?${params.toString()}`).then(r => {
        setMetiers(r.data.metiers || []);
      }).catch(() => {});
    } else {
      setMetiers([]);
    }
    setSelectedMetier("all");
  }, [selectedSecteur, selectedFiliere, token]);

  // Auto-search when metier is selected
  useEffect(() => {
    if (selectedMetier && selectedMetier !== "all") {
      const metier = metiers.find(m => m.nom === selectedMetier);
      if (metier) {
        handleSearch(metier.nom);
      }
    } else if (selectedSecteur && selectedSecteur !== "all" && (!selectedMetier || selectedMetier === "all")) {
      // When secteur is selected but no specific metier, search by secteur
      handleSearch();
    }
  }, [selectedMetier]);

  // When ROME grand domaine changes
  useEffect(() => {
    if (selectedGrandDomaine && selectedGrandDomaine !== "all") {
      const gd = grandDomaines.find(g => g.code === selectedGrandDomaine);
      setRomeDomainesList(gd?.domaines || []);
    } else {
      setRomeDomainesList([]);
    }
    setSelectedDomaine("all");
    setRomeResults([]);
  }, [selectedGrandDomaine, grandDomaines]);

  // Auto-load ROME metiers when domaine changes
  useEffect(() => {
    if (selectedDomaine && selectedDomaine !== "all") {
      if (onSearchActive) onSearchActive(true);
      axios.get(`${API}/referentiel/rome/metiers?domaine=${selectedDomaine}`).then(r => {
        setRomeResults(r.data.metiers || []);
      }).catch(() => {});
    } else if (selectedGrandDomaine && selectedGrandDomaine !== "all") {
      if (onSearchActive) onSearchActive(true);
      axios.get(`${API}/referentiel/rome/metiers?grand_domaine=${selectedGrandDomaine}`).then(r => {
        setRomeResults(r.data.metiers || []);
      }).catch(() => {});
    }
  }, [selectedDomaine, selectedGrandDomaine]);

  // When filiere or secteur changes, notify parent to hide generic data
  useEffect(() => {
    if (selectedFiliere !== "all" || selectedSecteur !== "all") {
      if (onSearchActive) onSearchActive(true);
    }
  }, [selectedFiliere, selectedSecteur]);

  const handleSearch = async (searchTerm = null) => {
    const q = searchTerm || query.trim();
    if (!q && selectedFiliere === "all" && selectedGrandDomaine === "all") return;
    setSearching(true);
    try {
      const params = new URLSearchParams();
      if (token) params.append("token", token);
      if (q) params.append("q", q);
      if (selectedFiliere && selectedFiliere !== "all") params.append("filiere", selectedFiliere);
      if (selectedSecteur && selectedSecteur !== "all") params.append("secteur", selectedSecteur);

      const promises = [
        axios.get(`${API}/referentiel/search?${params.toString()}`),
        q ? axios.get(`${API}/referentiel/contexte?${token ? 'token='+token : ''}&q=${encodeURIComponent(q)}`).catch(() => ({ data: null })) : Promise.resolve({ data: null }),
        q ? axios.get(`${API}/referentiel/rome/metiers?q=${encodeURIComponent(q)}`).catch(() => ({ data: { metiers: [] } })) : Promise.resolve({ data: { metiers: [] } }),
      ];

      const [searchRes, contexteRes, romeRes] = await Promise.all(promises);
      setResults(searchRes.data);
      setRomeResults(romeRes.data.metiers || []);
      if (onSearchActive) onSearchActive(true);
      if (contexteRes.data && onContextUpdate) {
        onContextUpdate(contexteRes.data);
      }
    } catch { toast.error("Erreur recherche"); }
    setSearching(false);
  };

  const handleClear = () => {
    setQuery("");
    setSelectedFiliere("all");
    setSelectedSecteur("all");
    setSelectedMetier("all");
    setSelectedGrandDomaine("all");
    setSelectedDomaine("all");
    setMetiers([]);
    setRomeResults([]);
    setResults(null);
    setSearchMode("interne");
    if (onContextUpdate) onContextUpdate(null);
    if (onSearchActive) onSearchActive(false);
  };

  return (
    <Card data-testid="referentiel-search">
      <CardContent className="p-4">
        <h4 className="text-sm font-semibold text-slate-800 mb-3 flex items-center gap-2"><Search className="w-4 h-4 text-indigo-600" />Rechercher dans le référentiel des compétences</h4>
        <div className="flex items-center gap-2 flex-wrap mb-2">
          <input
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleSearch()}
            placeholder="Rechercher un métier, une compétence, un savoir-être..."
            className="flex-1 min-w-[200px] max-w-[500px] h-9 text-xs border border-slate-200 rounded-lg px-3 focus:outline-none focus:ring-2 focus:ring-indigo-200 focus:border-indigo-300"
            data-testid="search-input"
          />
          <Button size="sm" className="h-9 bg-indigo-600 hover:bg-indigo-700" onClick={() => handleSearch()} disabled={searching} data-testid="search-btn">
            {searching ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Search className="w-3.5 h-3.5" />}
          </Button>
          {(results || query || selectedFiliere !== "all" || selectedGrandDomaine !== "all" || romeResults.length > 0) && (
            <Button variant="ghost" size="sm" className="h-9 text-xs text-slate-500" onClick={handleClear}>Réinitialiser</Button>
          )}
        </div>
        {/* Mode tabs */}
        <div className="flex gap-1 mb-3">
          <button onClick={() => setSearchMode("interne")} className={`px-3 py-1 text-[10px] font-medium rounded-lg transition ${searchMode === "interne" ? "bg-indigo-600 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"}`} data-testid="mode-interne">Base RE'ACTIF PRO ({filieres.length} filières)</button>
          <button onClick={() => setSearchMode("rome")} className={`px-3 py-1 text-[10px] font-medium rounded-lg transition ${searchMode === "rome" ? "bg-blue-600 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"}`} data-testid="mode-rome">ROME France Travail (1 584 fiches)</button>
        </div>
        {/* Filtres en cascade - Base interne */}
        {searchMode === "interne" && (
        <div className="flex items-center gap-2 flex-wrap mb-3">
          <Select value={selectedFiliere} onValueChange={setSelectedFiliere}>
            <SelectTrigger className="h-8 text-[11px] w-52" data-testid="filter-filiere"><SelectValue placeholder="1. Filière professionnelle" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Toutes les filières</SelectItem>
              {filieres.map(f => <SelectItem key={f.code} value={f.code}>{f.nom}</SelectItem>)}
            </SelectContent>
          </Select>
          {secteurs.length > 0 && (
            <Select value={selectedSecteur} onValueChange={setSelectedSecteur}>
              <SelectTrigger className="h-8 text-[11px] w-48" data-testid="filter-secteur"><SelectValue placeholder="2. Secteur d'activité" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tous les secteurs</SelectItem>
                {secteurs.map(s => <SelectItem key={s.code || s.nom} value={s.code || s.nom}>{s.nom}</SelectItem>)}
              </SelectContent>
            </Select>
          )}
          {metiers.length > 0 && (
            <Select value={selectedMetier} onValueChange={setSelectedMetier}>
              <SelectTrigger className="h-8 text-[11px] w-52" data-testid="filter-metier"><SelectValue placeholder="3. Métier" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tous les métiers</SelectItem>
                {metiers.map(m => <SelectItem key={m.nom} value={m.nom}>{m.nom}</SelectItem>)}
              </SelectContent>
            </Select>
          )}
        </div>
        )}
        {/* Filtres en cascade - ROME */}
        {searchMode === "rome" && (
        <div className="flex items-center gap-2 flex-wrap mb-3">
          <Select value={selectedGrandDomaine} onValueChange={setSelectedGrandDomaine}>
            <SelectTrigger className="h-8 text-[11px] w-64" data-testid="filter-grand-domaine"><SelectValue placeholder="1. Grand domaine ROME" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Tous les grands domaines (14)</SelectItem>
              {grandDomaines.map(gd => <SelectItem key={gd.code} value={gd.code}>{gd.code} - {gd.nom} ({gd.metiers_count})</SelectItem>)}
            </SelectContent>
          </Select>
          {romeDomainesList.length > 0 && (
            <Select value={selectedDomaine} onValueChange={setSelectedDomaine}>
              <SelectTrigger className="h-8 text-[11px] w-52" data-testid="filter-domaine-rome"><SelectValue placeholder="2. Domaine" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tous les domaines</SelectItem>
                {romeDomainesList.map(d => <SelectItem key={d.code} value={d.code}>{d.code} - {d.nom}</SelectItem>)}
              </SelectContent>
            </Select>
          )}
        </div>
        )}

        {/* Résultats */}
        {results && (
          <div className="space-y-3">
            <p className="text-[10px] text-slate-500">{results.total} résultat{results.total > 1 ? "s" : ""}</p>

            {results.filieres?.length > 0 && (
              <div>
                <p className="text-[10px] font-semibold text-slate-500 uppercase mb-1">Filières</p>
                {results.filieres.map((f, i) => (
                  <div key={i} className="p-2 bg-indigo-50 rounded-lg mb-1.5">
                    <p className="text-xs font-semibold text-indigo-800">{f.nom} <Badge variant="outline" className="text-[8px] ml-1">{f.code}</Badge></p>
                    <div className="flex flex-wrap gap-1 mt-1">{(f.secteurs || []).map((s, j) => <Badge key={j} className="text-[8px] bg-white border border-indigo-200 text-indigo-600">{s.nom}</Badge>)}</div>
                  </div>
                ))}
              </div>
            )}

            {results.metiers?.length > 0 && (
              <div>
                <p className="text-[10px] font-semibold text-slate-500 uppercase mb-1">Métiers</p>
                <div className="space-y-1">
                  {results.metiers.map((m, i) => (
                    <div key={i} className="flex items-start gap-2 p-2 bg-blue-50 rounded-lg">
                      <Briefcase className="w-3.5 h-3.5 text-blue-500 shrink-0 mt-0.5" />
                      <div>
                        <p className="text-xs font-medium text-slate-800">{m.nom}</p>
                        <p className="text-[10px] text-slate-500">{m.missions}</p>
                        <div className="flex gap-1 mt-0.5">
                          <Badge variant="outline" className="text-[8px]">{m.filiere_code}</Badge>
                          <Badge variant="outline" className="text-[8px]">{m.secteur_code}</Badge>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {results.savoir_etre?.length > 0 && (
              <div>
                <p className="text-[10px] font-semibold text-slate-500 uppercase mb-1">Savoir-être professionnels</p>
                <div className="space-y-1">
                  {results.savoir_etre.map((se, i) => (
                    <div key={i} className="p-2.5 bg-rose-50 rounded-lg">
                      <div className="flex items-start gap-2">
                        <Award className="w-3.5 h-3.5 text-rose-500 shrink-0 mt-0.5" />
                        <div className="flex-1">
                          <p className="text-xs font-medium text-slate-800">{se.nom}</p>
                          <p className="text-[10px] text-slate-500">{se.description}</p>
                          {se.qualites_humaines?.length > 0 && (
                            <div className="flex flex-wrap gap-1 mt-1">
                              <span className="text-[9px] text-rose-600 font-medium">Qualités humaines :</span>
                              {se.qualites_humaines.map((qh, j) => <Badge key={j} className="text-[8px] bg-white border border-rose-200 text-rose-600">{qh}</Badge>)}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {results.capacites_techniques?.length > 0 && (
              <div>
                <p className="text-[10px] font-semibold text-slate-500 uppercase mb-1">Capacités techniques</p>
                <div className="space-y-1">
                  {results.capacites_techniques.map((ct, i) => (
                    <div key={i} className="flex items-start gap-2 p-2 bg-indigo-50 rounded-lg">
                      <GraduationCap className="w-3.5 h-3.5 text-indigo-500 shrink-0 mt-0.5" />
                      <p className="text-[10px] text-slate-700">{ct.nom}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {results.total === 0 && !romeResults.length && <p className="text-xs text-slate-400 text-center py-4">Aucun résultat trouvé</p>}
          </div>
        )}

        {/* Résultats ROME France Travail */}
        {romeResults.length > 0 && (
          <div className="mt-3">
            <div className="flex items-center justify-between mb-2">
              <p className="text-[10px] font-semibold text-blue-600 uppercase flex items-center gap-1"><Briefcase className="w-3.5 h-3.5" />ROME France Travail — {romeResults.length} fiche{romeResults.length > 1 ? "s" : ""}</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-h-96 overflow-y-auto">
              {romeResults.map((m, i) => (
                <div key={i} className="p-2.5 bg-blue-50/50 border border-blue-100 rounded-lg hover:bg-blue-50 transition-colors">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-slate-800 truncate">{m.nom}</p>
                      <p className="text-[9px] text-blue-600">{m.code_rome} — {m.domaine_nom}</p>
                    </div>
                    <div className="flex gap-1 shrink-0">
                      {m.transition_ecologique && m.transition_ecologique !== "Emploi Blanc" && <span className="text-[7px] bg-emerald-100 text-emerald-700 px-1 py-0.5 rounded" title={m.transition_ecologique}>ECO</span>}
                      {m.transition_numerique === "Oui" && <span className="text-[7px] bg-violet-100 text-violet-700 px-1 py-0.5 rounded">NUM</span>}
                      {m.transition_demographique === "Oui" && <span className="text-[7px] bg-amber-100 text-amber-700 px-1 py-0.5 rounded">DEMO</span>}
                      {m.emploi_cadre && <span className="text-[7px] bg-slate-200 text-slate-700 px-1 py-0.5 rounded">CADRE</span>}
                    </div>
                  </div>
                  <p className="text-[8px] text-slate-500 mt-0.5">{m.grand_domaine_nom}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

const OpcView = ({ token, isPublic = false }) => {
  const auth = useAuth();
  const isAdminUser = (() => {
    const p = (auth?.pseudo || "").toLowerCase();
    const r = (auth?.role || "").toLowerCase();
    const adm = auth?.adminStatus;
    if (r === "admin") return true;
    if (adm === "admin" || adm === "true") return true;
    return ["reactif_admin", "solerys", "admin@reactifpro.fr"].includes(p);
  })();
  const [data, setData] = useState(null);
  const [emergentes, setEmergentes] = useState([]);
  const [metiersTension, setMetiersTension] = useState([]);
  const [trajectoires, setTrajectoires] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("observer");
  const [showLoginModal, setShowLoginModal] = useState(false);

  // IA results
  const [iaEmergentes, setIaEmergentes] = useState([]);
  const [iaCorrelations, setIaCorrelations] = useState([]);
  const [iaTrajectoires, setIaTrajectoires] = useState([]);
  const [iaReco, setIaReco] = useState(null);
  const [predictions, setPredictions] = useState(null);
  const [iaLoading, setIaLoading] = useState("");

  // Search context
  const [searchContext, setSearchContext] = useState(null);
  const [isSearchActive, setIsSearchActive] = useState(false);
  const [opcFilieres, setOpcFilieres] = useState([]);
  const [terrainProofs, setTerrainProofs] = useState([]);

  // Load filieres for ActualisationOPC
  useEffect(() => {
    axios.get(`${API}/referentiel/filieres`).then(r => setOpcFilieres(r.data.filieres || [])).catch(() => {});
  }, []);

  // Clear IA results when search context changes
  const searchQuery = searchContext?.query || "";
  useEffect(() => {
    setIaEmergentes([]);
    setIaCorrelations([]);
    setIaTrajectoires([]);
    setIaReco(null);
    setPredictions(null);
  }, [searchQuery, isSearchActive]);

  // Fetch terrain proofs when search context has savoir-être
  useEffect(() => {
    if (searchContext?.savoir_etre?.length > 0) {
      // Fetch all terrain proofs — frontend does partial matching with métier savoir-être
      axios.get(`${API}/observatory/sare-terrain?limit=3`)
        .then(r => setTerrainProofs(r.data.terrain_proofs || []))
        .catch(() => setTerrainProofs([]));
    } else {
      setTerrainProofs([]);
    }
  }, [searchContext]);

  const loadData = useCallback(async () => {
    try {
      const tokenParam = token ? `token=${token}` : "";
      const [dashRes, emergRes, metiersRes, trajRes, predRes] = await Promise.all([
        axios.get(`${API}/observatory/dashboard?${tokenParam}`),
        axios.get(`${API}/competences/emergentes?${tokenParam}`).catch(() => ({ data: [] })),
        axios.get(`${API}/metiers/tension?${tokenParam}`).catch(() => ({ data: [] })),
        axios.get(`${API}/trajectoires?${tokenParam}`).catch(() => ({ data: [] })),
        axios.get(`${API}/observatory/predictions?${tokenParam}`).catch(() => ({ data: {} })),
      ]);
      setData(dashRes.data);
      setEmergentes(emergRes.data || []);
      setMetiersTension(metiersRes.data || []);
      setTrajectoires(trajRes.data || []);
      if (predRes.data?.synthese) setPredictions(predRes.data);
    } catch { /* silent */ }
    setLoading(false);
  }, [token]);

  useEffect(() => { loadData(); }, [loadData]);

  const runIa = async (endpoint, setter, label) => {
    setIaLoading(endpoint);
    try {
      const tokenParam = token ? `token=${token}` : "";
      const contextQuery = searchContext?.query || (isSearchActive ? query : "");
      const body = contextQuery ? { contexte_metier: contextQuery } : {};
      const res = await axios.post(`${API}/observatory/ia/${endpoint}?${tokenParam}`, body, { timeout: 60000 });
      if (res.data && !res.data.error) {
        setter(res.data);
        toast.success(`${label} terminé${contextQuery ? ` (${contextQuery})` : ""}`);
      } else {
        toast.error(res.data?.error || "Erreur IA");
      }
    } catch (e) {
      console.error("IA error:", e);
      toast.error("Erreur IA — réessayez");
    }
    setIaLoading("");
  };

  if (loading) return <div className="flex items-center justify-center h-64"><Loader2 className="w-8 h-8 animate-spin text-slate-400" /></div>;

  const stats = data?.stats || {};
  const tensionRate = metiersTension.length > 0 ? Math.round(metiersTension.filter(m => m.tension > 50).length / metiersTension.length * 100) : 0;
  const validationRate = stats.soft_skills_prouves > 0 ? Math.round(stats.soft_skills_prouves / (stats.total_profils || 1) * 100) : 0;

  return (
    <div className="space-y-5" data-testid="opc-view">
      {/* === HEADER === */}
      <div className="relative rounded-2xl bg-gradient-to-br from-indigo-900 via-violet-900 to-purple-900 p-6">
        <div className="absolute top-0 right-0 w-72 h-72 bg-white/3 rounded-full -translate-y-20 translate-x-20" />
        <div className="relative z-10 flex items-start justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <BarChart3 className="w-6 h-6 text-violet-300" />
              <h1 className="text-xl font-bold text-white" style={{ fontFamily: 'Outfit, sans-serif' }}>Observatoire Prédictif des Compétences</h1>
            </div>
            <p className="text-violet-200 text-sm max-w-2xl">Infrastructure d'intelligence de l'emploi — collecte, analyse et transforme les données multi-sources pour anticiper les évolutions et orienter les parcours</p>
            <div className="flex items-center gap-2 mt-2 flex-wrap">
              <Badge className="bg-violet-500/20 text-violet-200 border border-violet-400/30 text-[10px]"><Eye className="w-3 h-3 mr-1" />Données vivantes</Badge>
              <Badge className="bg-cyan-500/20 text-cyan-200 border border-cyan-400/30 text-[10px]"><Brain className="w-3 h-3 mr-1" />IA Prédictive</Badge>
              <Badge className="bg-emerald-500/20 text-emerald-200 border border-emerald-400/30 text-[10px]"><Users className="w-3 h-3 mr-1" />Multi-sources</Badge>
              <Badge className="bg-amber-500/20 text-amber-200 border border-amber-400/30 text-[10px]"><Shield className="w-3 h-3 mr-1" />Anonymisé</Badge>
            </div>
          </div>
          <div className="flex flex-col items-end gap-2 shrink-0">
            {/* Connexion / Déconnexion */}
            {auth?.isAuthenticated ? (
              <button
                onClick={() => { auth.logout(); window.location.reload(); }}
                className="flex items-center gap-1.5 bg-white/10 hover:bg-white/20 border border-white/15 rounded-lg px-3 py-1.5 transition"
                data-testid="logout-btn"
              >
                <Users className="w-3.5 h-3.5 text-violet-300" />
                <span className="text-[11px] text-white font-medium">{auth.pseudo || "Utilisateur"}</span>
                <span className="text-[10px] text-violet-300 ml-1">Déconnexion</span>
              </button>
            ) : (
              <button
                onClick={() => setShowLoginModal(true)}
                className="flex items-center gap-1.5 bg-white/10 hover:bg-white/20 border border-white/15 rounded-lg px-3 py-1.5 transition"
                data-testid="login-btn"
              >
                <Users className="w-3.5 h-3.5 text-violet-300" />
                <span className="text-[11px] text-white font-medium">Connexion</span>
              </button>
            )}
            <ActualisationOPC token={token} filieres={opcFilieres} />
          </div>
        </div>
      </div>

      {/* === INDICATEURS CLÉS === */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2" data-testid="opc-kpis">
        {[
          { label: "Profils actifs", value: stats.total_profils, icon: Users, color: "blue" },
          { label: "CV analysés", value: stats.profils_avec_cv, icon: Briefcase, color: "emerald" },
          { label: "D'CLIC PRO", value: stats.profils_avec_dclic, icon: Sparkles, color: "violet" },
          { label: "Expériences", value: stats.total_experiences, icon: Target, color: "amber" },
          { label: "Formations", value: stats.total_formations, icon: GraduationCap, color: "indigo" },
          { label: "Soft skills prouvés", value: stats.soft_skills_prouves, icon: Award, color: "rose" },
          { label: "Taux tension", value: `${tensionRate}%`, icon: AlertTriangle, color: "orange" },
          { label: "Taux validation", value: `${validationRate}%`, icon: CheckCircle2, color: "cyan" },
        ].map((s, i) => {
          const SIcon = s.icon;
          return (
            <Card key={i} className="border-0 shadow-sm">
              <CardContent className="p-2.5 text-center">
                <SIcon className={`w-4 h-4 text-${s.color}-600 mx-auto mb-0.5`} />
                <p className="text-lg font-bold text-slate-900">{s.value || 0}</p>
                <p className="text-[9px] text-slate-500 leading-tight">{s.label}</p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* === 4 MISSIONS === */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid grid-cols-4 h-auto p-1 bg-slate-100">
          <TabsTrigger value="observer" className="text-xs py-2.5 gap-1" data-testid="tab-observer"><Eye className="w-3.5 h-3.5" />Observer</TabsTrigger>
          <TabsTrigger value="analyser" className="text-xs py-2.5 gap-1" data-testid="tab-analyser"><Activity className="w-3.5 h-3.5" />Analyser</TabsTrigger>
          <TabsTrigger value="anticiper" className="text-xs py-2.5 gap-1" data-testid="tab-anticiper"><Brain className="w-3.5 h-3.5" />Anticiper</TabsTrigger>
          <TabsTrigger value="orienter" className="text-xs py-2.5 gap-1" data-testid="tab-orienter"><Compass className="w-3.5 h-3.5" />Orienter</TabsTrigger>
        </TabsList>

        {/* ============ MISSION 1 : OBSERVER ============ */}
        <TabsContent value="observer" className="space-y-4 mt-4">
          <div className="flex items-center gap-2 bg-blue-50 border border-blue-100 rounded-lg px-3 py-2 text-xs text-blue-700">
            <Eye className="w-4 h-4 shrink-0" />
            <span><strong>Observer</strong> — Données vivantes collectées en continu depuis les 4 sources : profils utilisateurs, espace RH, partenaires de parcours, réseau UBUNTOO</span>
          </div>

          {/* MOTEUR DE RECHERCHE RÉFÉRENTIEL */}
          <ReferentielSearch token={token} onContextUpdate={setSearchContext} onSearchActive={setIsSearchActive} />

          {/* CONTEXTE DE RECHERCHE (s'affiche quand une recherche est active) */}
          {searchContext && searchContext.metier && (
            <Card className="border-indigo-200 bg-indigo-50/30" data-testid="search-context">
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-sm font-semibold text-indigo-800 flex items-center gap-2"><Target className="w-4 h-4" />{searchContext.metier.nom}</h4>
                  <div className="flex gap-1.5 flex-wrap">
                    {searchContext.filiere_nom && <Badge className="bg-indigo-100 text-indigo-700 text-[9px]">{searchContext.filiere_nom}</Badge>}
                    <Badge className="bg-blue-100 text-blue-700 text-[9px]">{searchContext.secteur_nom}</Badge>
                    {searchContext.code_liaison && <Badge variant="outline" className="text-[8px] text-slate-500">{searchContext.code_liaison}</Badge>}
                  </div>
                </div>
                <p className="text-xs text-slate-600 mb-3">{searchContext.metier.missions}</p>

                {/* Scores */}
                <div className="grid grid-cols-3 gap-3 mb-3">
                  <div className="text-center p-2 bg-white rounded-lg border">
                    <div className="text-lg font-bold text-amber-600">{searchContext.tension_score}%</div>
                    <div className="text-[9px] text-slate-500">Tension marché</div>
                  </div>
                  <div className="text-center p-2 bg-white rounded-lg border">
                    <div className="text-lg font-bold text-violet-600">{searchContext.emergence_score}%</div>
                    <div className="text-[9px] text-slate-500">Émergence</div>
                  </div>
                  <div className="text-center p-2 bg-white rounded-lg border">
                    <div className="text-lg font-bold text-blue-600">{searchContext.profiles_concernes}</div>
                    <div className="text-[9px] text-slate-500">Profils</div>
                  </div>
                </div>

                {/* CHAÎNE COMPLÈTE : SF → CT → SE → CP */}
                <div className="space-y-3">
                  {/* 1. Savoir-faire / Compétences techniques */}
                  {(searchContext.savoir_faire_details?.length > 0 || searchContext.metier?.savoir_faire_details?.length > 0) && (
                  <div className="bg-white rounded-lg border p-3">
                    <p className="text-[10px] font-semibold text-blue-700 uppercase mb-2 flex items-center gap-1"><Briefcase className="w-3.5 h-3.5" />Savoir-faire / Compétences techniques ({(searchContext.savoir_faire_details || searchContext.metier?.savoir_faire_details || []).length})</p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-1">{(searchContext.savoir_faire_details || searchContext.metier?.savoir_faire_details || []).map((sf, i) => (
                      <div key={i} className="flex items-start gap-1.5 text-[10px] text-slate-700"><CheckCircle2 className="w-3 h-3 text-blue-400 shrink-0 mt-0.5" />{sf}</div>
                    ))}</div>
                  </div>
                  )}

                  {/* 2. Capacités techniques (détails) */}
                  {(searchContext.capacites_techniques_details?.length > 0 || searchContext.capacites_techniques?.length > 0) && (
                  <div className="bg-white rounded-lg border p-3">
                    <p className="text-[10px] font-semibold text-cyan-700 uppercase mb-2 flex items-center gap-1"><CheckCircle2 className="w-3.5 h-3.5" />Capacités techniques ({(searchContext.capacites_techniques_details || searchContext.capacites_techniques || []).length})</p>
                    <div className="space-y-1.5">{(searchContext.capacites_techniques_details || searchContext.capacites_techniques || []).map((ct, i) => (
                      <div key={i} className="text-[9px] text-slate-600 pl-4 border-l-2 border-cyan-200">{ct}</div>
                    ))}</div>
                  </div>
                  )}

                  {/* 3. Savoir-être professionnels → Qualités humaines + Preuves terrain */}
                  <div className="bg-white rounded-lg border p-3">
                    <p className="text-[10px] font-semibold text-rose-600 uppercase mb-2 flex items-center gap-1"><Award className="w-3.5 h-3.5" />Savoir-être professionnels ({(searchContext.savoir_etre || []).length})</p>
                    <div className="space-y-2">{(searchContext.savoir_etre || []).slice(0, 12).map((se, i) => {
                      const proofData = terrainProofs.find(tp => {
                        const tpLower = (tp.soft_skill || "").toLowerCase();
                        const seLower = (se.nom || "").toLowerCase();
                        return tpLower === seLower || tpLower.includes(seLower) || seLower.includes(tpLower);
                      });
                      return (
                      <div key={i}>
                        <div className="flex items-center gap-1.5 text-[10px] text-slate-800 font-medium">
                          <Award className="w-3 h-3 text-rose-400 shrink-0" />{se.nom}
                          {proofData && (
                            <span className="text-[8px] bg-amber-100 text-amber-700 px-1.5 py-0.5 rounded-full font-semibold">{proofData.count} preuve{proofData.count > 1 ? "s" : ""} terrain</span>
                          )}
                        </div>
                        {se.qualites_humaines?.length > 0 && (
                          <div className="ml-5 mt-0.5 space-y-0.5">{se.qualites_humaines.map((qh, j) => (
                            <div key={j} className="text-[8px] text-rose-600 bg-rose-50 px-2 py-0.5 rounded">{qh}</div>
                          ))}</div>
                        )}
                        {/* Inline terrain proof */}
                        {proofData && proofData.proofs?.[0] && (
                          <div className="ml-5 mt-1 bg-amber-50 border border-amber-100 rounded-lg p-2 space-y-0.5" data-testid={`terrain-proof-inline-${i}`}>
                            <p className="text-[8px] font-bold text-amber-800 flex items-center gap-1"><Shield className="w-2.5 h-2.5" />Preuve terrain anonymisée — {proofData.proofs[0].poste}</p>
                            {proofData.proofs[0].sare_situation ? (
                              <div className="text-[8px] text-amber-900 space-y-0.5">
                                <p><span className="font-bold">S</span> {proofData.proofs[0].sare_situation}</p>
                                {proofData.proofs[0].sare_action && <p><span className="font-bold">A</span> {proofData.proofs[0].sare_action}</p>}
                                {proofData.proofs[0].sare_resultat && <p><span className="font-bold">R</span> {proofData.proofs[0].sare_resultat}</p>}
                                {proofData.proofs[0].sare_enseignement && <p><span className="font-bold">E</span> {proofData.proofs[0].sare_enseignement}</p>}
                              </div>
                            ) : proofData.proofs[0].sare_text ? (
                              <p className="text-[8px] text-amber-900 leading-relaxed">{proofData.proofs[0].sare_text.substring(0, 200)}...</p>
                            ) : proofData.proofs[0].texte_brut ? (
                              <p className="text-[8px] text-amber-900">{proofData.proofs[0].texte_brut.substring(0, 150)}...</p>
                            ) : null}
                          </div>
                        )}
                      </div>
                      );
                    })}</div>
                  </div>

                  {/* Preuves terrain dédiées — Toutes les preuves S.A.R.E pour ce métier */}
                  {terrainProofs.length > 0 && (
                    <div className="bg-white rounded-lg border border-amber-200 p-3" data-testid="terrain-proofs-section">
                      <p className="text-[10px] font-semibold text-amber-700 uppercase mb-2 flex items-center gap-1">
                        <Shield className="w-3.5 h-3.5" />
                        Preuves terrain — Soft skills illustrés par la communauté ({terrainProofs.reduce((s, t) => s + t.count, 0)})
                      </p>
                      <p className="text-[8px] text-amber-600 mb-2">Exemples concrets et anonymisés issus d'expériences réelles de professionnels</p>
                      <div className="space-y-2">
                        {terrainProofs.map((tp, i) => (
                          <div key={i} className="space-y-1.5">
                            <div className="flex items-center gap-1.5">
                              <Award className="w-3 h-3 text-amber-600 shrink-0" />
                              <span className="text-[10px] font-bold text-amber-900">{tp.soft_skill}</span>
                              <span className="text-[8px] bg-amber-100 text-amber-700 px-1.5 py-0.5 rounded-full">{tp.count} témoignage{tp.count > 1 ? "s" : ""}</span>
                            </div>
                            {tp.proofs.map((proof, j) => (
                              <div key={j} className="ml-5 bg-amber-50 border border-amber-100 rounded-lg p-2" data-testid={`terrain-proof-${i}-${j}`}>
                                <p className="text-[8px] font-semibold text-slate-500 mb-0.5">Contexte : {proof.poste}</p>
                                {proof.sare_situation ? (
                                  <div className="text-[8px] text-slate-700 space-y-0.5">
                                    <p><span className="font-bold text-amber-800">S</span> {proof.sare_situation}</p>
                                    {proof.sare_action && <p><span className="font-bold text-amber-800">A</span> {proof.sare_action}</p>}
                                    {proof.sare_resultat && <p><span className="font-bold text-amber-800">R</span> {proof.sare_resultat}</p>}
                                    {proof.sare_enseignement && <p><span className="font-bold text-amber-800">E</span> {proof.sare_enseignement}</p>}
                                  </div>
                                ) : proof.sare_text ? (
                                  <p className="text-[8px] text-slate-700 leading-relaxed">{proof.sare_text}</p>
                                ) : proof.texte_brut ? (
                                  <p className="text-[8px] text-slate-700">{proof.texte_brut}</p>
                                ) : null}
                              </div>
                            ))}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* 4. Capacités professionnelles */}
                  {(searchContext.capacites_professionnelles?.length > 0) && (
                  <div className="bg-white rounded-lg border p-3">
                    <p className="text-[10px] font-semibold text-emerald-700 uppercase mb-2 flex items-center gap-1"><TrendingUp className="w-3.5 h-3.5" />Capacités professionnelles ({searchContext.capacites_professionnelles.length})</p>
                    <div className="space-y-1.5">{searchContext.capacites_professionnelles.map((cp, i) => (
                      <div key={i} className="text-[9px] text-slate-600 pl-4 border-l-2 border-emerald-200">{cp}</div>
                    ))}</div>
                  </div>
                  )}
                </div>

                {/* Métiers liés et Passerelles */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3">
                  <div className="bg-white rounded-lg border p-3">
                    <p className="text-[10px] font-semibold text-slate-600 uppercase mb-2 flex items-center gap-1"><Briefcase className="w-3.5 h-3.5" />Métiers du secteur {searchContext.secteur_nom} ({(searchContext.related_metiers || []).length})</p>
                    <div className="space-y-1">{(searchContext.related_metiers || []).slice(0, 6).map((m, i) => (
                      <div key={i} className="text-[10px] text-slate-700"><Briefcase className="w-2.5 h-2.5 text-slate-400 inline mr-1" /><span className="font-medium">{m.nom}</span></div>
                    ))}</div>
                  </div>
                  {searchContext.passerelles_metiers?.length > 0 && (
                    <div className="bg-white rounded-lg border p-3">
                      <p className="text-[10px] font-semibold text-amber-600 uppercase mb-2 flex items-center gap-1"><TrendingUp className="w-3.5 h-3.5" />Passerelles métiers ({searchContext.passerelles_metiers.length})</p>
                      <div className="space-y-1">{searchContext.passerelles_metiers.slice(0, 6).map((m, i) => (
                        <div key={i} className="text-[10px] text-slate-700"><TrendingUp className="w-2.5 h-2.5 text-amber-400 inline mr-1" /><span className="font-medium">{m.nom}</span> <span className="text-[8px] text-slate-400">({m.secteur})</span></div>
                      ))}</div>
                    </div>
                  )}
                </div>

                {/* Filière */}
                {searchContext.filiere_secteurs?.length > 0 && (
                  <div className="mt-3 p-2 bg-white rounded-lg border">
                    <p className="text-[10px] font-semibold text-slate-500 uppercase mb-1">Filière {searchContext.filiere_nom} — Secteurs</p>
                    <div className="flex flex-wrap gap-1">{searchContext.filiere_secteurs.map((s, i) => (
                      <Badge key={i} className={`text-[8px] ${s === searchContext.secteur_nom ? 'bg-indigo-100 text-indigo-700 border-indigo-300' : 'bg-slate-50 text-slate-600 border-slate-200'} border`}>{s}</Badge>
                    ))}</div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Données globales masquées quand une recherche est active */}
          {!searchContext && !isSearchActive && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Top compétences techniques */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2"><Briefcase className="w-4 h-4 text-blue-600" />Compétences techniques observées</CardTitle>
                <CardDescription className="text-[10px]">Source : CV analysés + déclaratif utilisateurs</CardDescription>
              </CardHeader>
              <CardContent className="space-y-1.5">
                {(data?.top_hard_skills || []).slice(0, 8).map((c, i) => (
                  <div key={i} className="flex items-center gap-2">
                    <span className="text-[10px] text-slate-400 w-4">{i + 1}</span>
                    <span className="text-xs text-slate-700 flex-1 truncate">{c.name}</span>
                    <div className="w-16"><Progress value={Math.min(100, c.count * 10)} className="h-1.5 [&>div]:bg-blue-500" /></div>
                    <span className="text-[10px] text-slate-500 w-5 text-right">{c.count}</span>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Top savoir-être */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2"><Award className="w-4 h-4 text-rose-600" />Savoir-être observés</CardTitle>
                <CardDescription className="text-[10px]">Source : D'CLIC PRO + observations terrain + UBUNTOO</CardDescription>
              </CardHeader>
              <CardContent className="space-y-1.5">
                {(data?.top_soft_skills || []).slice(0, 8).map((c, i) => (
                  <div key={i} className="flex items-center gap-2">
                    <span className="text-[10px] text-slate-400 w-4">{i + 1}</span>
                    <span className="text-xs text-slate-700 flex-1 truncate">{c.name}</span>
                    <div className="w-16"><Progress value={Math.min(100, c.count * 3)} className="h-1.5 [&>div]:bg-rose-500" /></div>
                    <span className="text-[10px] text-slate-500 w-5 text-right">{c.count}</span>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
          )}

          {/* === ANALYSE IA DES ÉCHANGES UBUNTOO — Admin uniquement === */}
          {!searchContext && !isSearchActive && isAdminUser && (
            <Card className="border-amber-200 bg-gradient-to-r from-amber-50/60 to-orange-50/60" data-testid="ubuntoo-signals-analyzer">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-amber-600" />
                  Analyse IA des échanges Ubuntoo
                  <Badge className="bg-amber-100 text-amber-700 text-[9px]">Admin · Claude Sonnet 4.5</Badge>
                </CardTitle>
                <CardDescription className="text-[10px]">
                  Lance la détection des signaux émergents à partir des conversations Ubuntoo récentes (forum, groupes VSI, messages 1-to-1).
                </CardDescription>
              </CardHeader>
              <CardContent>
                <UbuntooAnalyzeBlock token={token} />
              </CardContent>
            </Card>
          )}

          {/* Graphique compétences émergentes — masqué quand recherche active */}
          {!searchContext && !isSearchActive && emergentes.length > 0 && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2"><TrendingUp className="w-4 h-4 text-violet-600" />Signaux faibles — Score d'émergence</CardTitle>
                <CardDescription className="text-[10px]">Fréquence d'apparition des compétences sur la plateforme</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={emergentes.slice(0, 10)}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis dataKey="nom" tick={{ fontSize: 9 }} angle={-20} textAnchor="end" height={55} />
                    <YAxis tick={{ fontSize: 10 }} />
                    <Tooltip contentStyle={{ fontSize: 11, borderRadius: 8 }} />
                    <Line type="monotone" dataKey="score_emergence" stroke="#7c3aed" strokeWidth={2} dot={{ fill: "#7c3aed", r: 3 }} name="Score" />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          )}

          {/* Secteurs & Métiers observés — masqué quand recherche active */}
          {!searchContext && !isSearchActive && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {(data?.top_sectors || []).length > 0 && (
              <Card>
                <CardHeader className="pb-2"><CardTitle className="text-sm flex items-center gap-2"><Globe className="w-4 h-4 text-amber-600" />Secteurs représentés</CardTitle></CardHeader>
                <CardContent><div className="flex flex-wrap gap-1.5">{data.top_sectors.map((s, i) => <Badge key={i} className="bg-amber-50 text-amber-700 border border-amber-200 text-[10px]">{s.name} ({s.count})</Badge>)}</div></CardContent>
              </Card>
            )}
            {metiersTension.length > 0 && (
              <Card>
                <CardHeader className="pb-2"><CardTitle className="text-sm flex items-center gap-2"><AlertTriangle className="w-4 h-4 text-amber-600" />Métiers en tension</CardTitle></CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={200}>
                    <BarChart data={metiersTension.slice(0, 6)}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                      <XAxis dataKey="nom" tick={{ fontSize: 8 }} angle={-15} textAnchor="end" height={50} />
                      <YAxis tick={{ fontSize: 10 }} />
                      <Tooltip contentStyle={{ fontSize: 11, borderRadius: 8 }} />
                      <Bar dataKey="tension" fill="#f59e0b" radius={[3, 3, 0, 0]} name="Tension" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            )}
          </div>
          )}

          {/* Corrélations Hard/Soft dans Observer — masqué quand recherche active */}
          {!searchContext && !isSearchActive && <CorrelationsBlock correlations={iaCorrelations} compact={true} />}
        </TabsContent>

        {/* ============ MISSION 2 : ANALYSER ============ */}
        <TabsContent value="analyser" className="space-y-4 mt-4">
          <div className="flex items-center gap-2 bg-violet-50 border border-violet-100 rounded-lg px-3 py-2 text-xs text-violet-700">
            <Activity className="w-4 h-4 shrink-0" />
            <span><strong>Analyser</strong> — Transforme les données brutes en lecture intelligente : corrélations, écarts profils/besoins, indicateurs de fiabilité</span>
          </div>

          {/* Scores moyens plateforme */}
          {data?.avg_trust_scores && (
            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm flex items-center gap-2"><Shield className="w-4 h-4 text-emerald-600" />Indicateurs de confiance (moyenne plateforme)</CardTitle></CardHeader>
              <CardContent>
                <div className="grid grid-cols-4 gap-3">
                  {[
                    { label: "Fiabilité preuves", value: data.avg_trust_scores.confidence, color: "blue" },
                    { label: "Complétude profils", value: data.avg_trust_scores.completeness, color: "emerald" },
                    { label: "Cohérence parcours", value: data.avg_trust_scores.coherence, color: "violet" },
                    { label: "Fraîcheur données", value: data.avg_trust_scores.freshness, color: "amber" },
                  ].map((d, i) => (
                    <div key={i} className="text-center bg-slate-50 rounded-lg p-3">
                      <p className={`text-xl font-bold text-${d.color}-600`}>{d.value}%</p>
                      <p className="text-[9px] text-slate-500">{d.label}</p>
                      <Progress value={d.value} className={`h-1 mt-1 [&>div]:bg-${d.color}-500`} />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Corrélations Hard/Soft IA */}
          <Card>
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm flex items-center gap-2"><Zap className="w-4 h-4 text-blue-600" />Corrélations compétences techniques ↔ savoir-être</CardTitle>
                <Button variant="outline" size="sm" className="h-7 text-xs" onClick={() => runIa("correlations", setIaCorrelations, "Corrélations")} disabled={!!iaLoading}>
                  {iaLoading === "correlations" ? <Loader2 className="w-3 h-3 animate-spin mr-1" /> : <Brain className="w-3 h-3 mr-1" />}Analyser
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {iaCorrelations.length === 0 ? (
                <p className="text-xs text-slate-400 text-center py-6">Lancez l'analyse IA pour identifier les liens entre compétences techniques et savoir-être</p>
              ) : iaCorrelations.slice(0, 6).map((c, i) => (
                <div key={i} className="p-2.5 bg-blue-50 rounded-lg mb-2">
                  <p className="text-xs font-semibold text-blue-800 mb-1">{c.competence_technique}</p>
                  <div className="flex flex-wrap gap-1">{(c.savoir_etre || []).map((se, j) => (
                    <Badge key={j} className="text-[8px] bg-white border border-blue-200 text-blue-700">{se.nom} <span className="ml-0.5 font-bold">{se.importance}/5</span></Badge>
                  ))}</div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Soft skills prouvés vs déclarés */}
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-600" />Écart : soft skills déclarés vs prouvés</CardTitle></CardHeader>
            <CardContent>
              <div className="space-y-1.5">
                {(data?.proved_soft_skills || []).length > 0 ? data.proved_soft_skills.map((s, i) => (
                  <div key={i} className="flex items-center gap-2 p-2 bg-emerald-50 rounded-lg">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
                    <span className="text-xs font-medium text-slate-800 flex-1">{s.name}</span>
                    <Badge className="bg-emerald-100 text-emerald-700 text-[9px]">{s.count} preuve{s.count > 1 ? "s" : ""}</Badge>
                    {s.star_count > 0 && <Badge className="bg-blue-100 text-blue-700 text-[9px]">{s.star_count} STAR</Badge>}
                  </div>
                )) : <p className="text-xs text-slate-400 text-center py-4">Aucun soft skill prouvé par des exemples concrets — les profils sont déclaratifs</p>}
              </div>
            </CardContent>
          </Card>

        </TabsContent>

        {/* ============ MISSION 3 : ANTICIPER ============ */}
        <TabsContent value="anticiper" className="space-y-4 mt-4">
          <div className="flex items-center gap-2 bg-amber-50 border border-amber-100 rounded-lg px-3 py-2 text-xs text-amber-700">
            <Brain className="w-4 h-4 shrink-0" />
            <span><strong>Anticiper</strong> — Projette le futur du marché : compétences émergentes, métiers en tension, mutations sectorielles, opportunités futures</span>
          </div>

          {/* Boutons IA */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {[
              { label: "Compétences émergentes", endpoint: "detect-emergentes", setter: setIaEmergentes, icon: TrendingUp, color: "violet" },
              { label: "Trajectoires IA", endpoint: "trajectoires", setter: setIaTrajectoires, icon: Compass, color: "emerald" },
              { label: "Prédictions globales", endpoint: "predict", setter: null, icon: Brain, color: "indigo" },
              { label: "Analyse complète", endpoint: "analyse-complete", setter: null, icon: Sparkles, color: "rose" },
            ].map((action, i) => {
              const AIcon = action.icon;
              return (
                <Button key={i} variant="outline" className={`h-auto py-3 flex-col gap-1 border-${action.color}-200 hover:bg-${action.color}-50`}
                  disabled={!!iaLoading}
                  onClick={async () => {
                    const contextBody = (searchContext?.query || isSearchActive) ? { contexte_metier: searchContext?.query || "" } : {};
                    if (action.endpoint === "predict") {
                      setIaLoading("predict");
                      try {
                        const res = await axios.post(`${API}/observatory/predict-competences?${token ? 'token='+token : ''}`, contextBody);
                        setPredictions(res.data);
                        toast.success("Prédictions générées" + (contextBody.contexte_metier ? ` (${contextBody.contexte_metier})` : ""));
                      } catch { toast.error("Erreur"); }
                      setIaLoading("");
                    } else if (action.endpoint === "analyse-complete") {
                      setIaLoading("analyse-complete");
                      try {
                        const res = await axios.post(`${API}/observatory/ia/analyse-complete?${token ? 'token='+token : ''}`, contextBody);
                        if (res.data.emergentes) setIaEmergentes(res.data.emergentes);
                        if (res.data.correlations) setIaCorrelations(res.data.correlations);
                        if (res.data.trajectoires) setIaTrajectoires(res.data.trajectoires);
                        if (res.data.recommandation) setIaReco(res.data.recommandation);
                        toast.success("Analyse complète terminée" + (contextBody.contexte_metier ? ` (${contextBody.contexte_metier})` : ""));
                      } catch { toast.error("Erreur"); }
                      setIaLoading("");
                    } else {
                      runIa(action.endpoint, action.setter, action.label);
                    }
                  }}
                >
                  {iaLoading === action.endpoint ? <Loader2 className="w-5 h-5 animate-spin" /> : <AIcon className={`w-5 h-5 text-${action.color}-600`} />}
                  <span className="text-[10px] font-medium">{action.label}</span>
                </Button>
              );
            })}
          </div>

          {/* Prédictions */}
          {predictions?.synthese && (
            <Card className="border-indigo-200 bg-indigo-50/30">
              <CardContent className="p-4">
                <p className="text-[10px] font-semibold text-indigo-700 mb-1">Synthèse prédictive IA</p>
                <p className="text-xs text-indigo-800 italic">{predictions.synthese}</p>
              </CardContent>
            </Card>
          )}

          {/* Tendances + Métiers tension */}
          {predictions?.tendances_competences && (
            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm flex items-center gap-2"><TrendingUp className="w-4 h-4 text-blue-600" />Tendances compétences anticipées</CardTitle></CardHeader>
              <CardContent className="space-y-1.5">
                {predictions.tendances_competences.map((t, i) => {
                  const DirIcon = t.direction === "hausse" ? TrendingUp : t.direction === "baisse" ? TrendingDown : Minus;
                  return (
                    <div key={i} className="flex items-center gap-2 p-2 bg-slate-50 rounded-lg">
                      <DirIcon className={`w-3.5 h-3.5 shrink-0 ${t.direction === "hausse" ? "text-emerald-500" : t.direction === "baisse" ? "text-rose-500" : "text-slate-400"}`} />
                      <span className="text-xs font-medium text-slate-800 flex-1">{t.competence}</span>
                      <span className="text-[10px] text-slate-500">{t.explication}</span>
                    </div>
                  );
                })}
              </CardContent>
            </Card>
          )}

          {/* Compétences émergentes IA */}
          {iaEmergentes.length > 0 && (
            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm flex items-center gap-2"><Sparkles className="w-4 h-4 text-violet-600" />Compétences émergentes détectées par l'IA</CardTitle></CardHeader>
              <CardContent className="space-y-1.5">
                {iaEmergentes.map((c, i) => (
                  <div key={i} className="flex items-center gap-2 p-2 bg-violet-50 rounded-lg">
                    <Badge className={`text-[9px] ${(c.tendance || "").includes("hausse") ? "bg-emerald-100 text-emerald-700" : (c.tendance || "").includes("baisse") ? "bg-rose-100 text-rose-700" : (c.tendance || "").includes("mergent") ? "bg-violet-100 text-violet-700" : "bg-slate-100 text-slate-600"}`}>{c.tendance || "stable"}</Badge>
                    <span className="text-xs font-medium text-slate-800 flex-1">{c.competence}</span>
                    <span className="text-xs font-bold text-violet-600">{c.score_emergence}</span>
                    {(c.secteurs || []).length > 0 && <span className="text-[9px] text-slate-400">{c.secteurs.slice(0, 2).join(", ")}</span>}
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Trajectoires IA */}
          {iaTrajectoires.length > 0 && (
            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm flex items-center gap-2"><Compass className="w-4 h-4 text-emerald-600" />Passerelles métiers anticipées</CardTitle></CardHeader>
              <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {iaTrajectoires.map((t, i) => (
                  <div key={i} className="p-2.5 border border-slate-100 rounded-lg">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-medium text-slate-800">{t.metier_source}</span>
                      <ArrowRight className="w-3 h-3 text-emerald-500" />
                      <span className="text-xs font-medium text-emerald-700">{t.metier_cible}</span>
                      <span className="text-[10px] font-bold text-emerald-600 ml-auto">{t.probabilite}%</span>
                    </div>
                    <p className="text-[10px] text-slate-500">{t.justification}</p>
                    {t.competences_manquantes?.length > 0 && <div className="flex gap-1 mt-1">{t.competences_manquantes.slice(0, 3).map((c, j) => <Badge key={j} variant="outline" className="text-[8px]">{c}</Badge>)}</div>}
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* ============ MISSION 4 : ORIENTER ============ */}
        <TabsContent value="orienter" className="space-y-4 mt-4">
          <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-100 rounded-lg px-3 py-2 text-xs text-emerald-700">
            <Compass className="w-4 h-4 shrink-0" />
            <span><strong>Orienter</strong> — Transforme l'intelligence en action : recommandations personnalisées pour chaque public (utilisateurs, conseillers, RH, institutions)</span>
          </div>

          {/* Recommandation personnalisée (uniquement si connecté) */}
          {!isPublic && token && (
          <Card className="border-amber-200">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm flex items-center gap-2"><Target className="w-4 h-4 text-amber-600" />Ma recommandation personnalisée</CardTitle>
                <Button variant="outline" size="sm" className="h-7 text-xs" onClick={() => runIa("recommandation", setIaReco, "Recommandation")} disabled={!!iaLoading}>
                  {iaLoading === "recommandation" ? <Loader2 className="w-3 h-3 animate-spin mr-1" /> : <Brain className="w-3 h-3 mr-1" />}Analyser mon profil
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {!iaReco || !iaReco.plan_action ? (
                <p className="text-xs text-slate-400 text-center py-6">Lancez l'analyse pour recevoir des recommandations personnalisées basées sur votre profil</p>
              ) : (
                <div className="space-y-3">
                  <p className="text-xs text-slate-700 italic bg-amber-50 rounded-lg p-3">{iaReco.plan_action}</p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {iaReco.metiers_accessibles && (
                      <div>
                        <p className="text-[10px] font-semibold text-slate-500 uppercase mb-1.5">Métiers accessibles</p>
                        {iaReco.metiers_accessibles.map((m, i) => (
                          <div key={i} className="flex items-center gap-1.5 text-xs text-slate-700 mb-1"><CheckCircle2 className="w-3 h-3 text-emerald-500 shrink-0" />{m.metier} <span className="text-[9px] text-emerald-600 font-bold">({m.adequation}%)</span></div>
                        ))}
                      </div>
                    )}
                    {iaReco.metiers_evolution && (
                      <div>
                        <p className="text-[10px] font-semibold text-slate-500 uppercase mb-1.5">Métiers avec montée en compétences</p>
                        {iaReco.metiers_evolution.map((m, i) => (
                          <div key={i} className="text-xs text-slate-700 mb-1"><ArrowRight className="w-3 h-3 text-blue-500 inline mr-1" />{m.metier} <span className="text-[9px] text-slate-400">({m.duree})</span></div>
                        ))}
                      </div>
                    )}
                    {iaReco.competences_prioritaires && (
                      <div>
                        <p className="text-[10px] font-semibold text-slate-500 uppercase mb-1.5">Compétences prioritaires</p>
                        {iaReco.competences_prioritaires.map((c, i) => (
                          <div key={i} className="flex items-center gap-1.5 text-xs text-slate-700 mb-1">
                            <Badge className={`text-[8px] ${c.urgence === "haute" ? "bg-rose-100 text-rose-700" : "bg-amber-100 text-amber-700"}`}>{c.urgence}</Badge>{c.competence}
                          </div>
                        ))}
                      </div>
                    )}
                    {iaReco.savoir_etre_a_renforcer && (
                      <div>
                        <p className="text-[10px] font-semibold text-slate-500 uppercase mb-1.5">Savoir-être à renforcer</p>
                        {iaReco.savoir_etre_a_renforcer.map((s, i) => (
                          <div key={i} className="text-xs text-slate-700 mb-1"><Award className="w-3 h-3 text-amber-500 inline mr-1" />{s.savoir_etre} <span className="text-[9px] text-slate-400">— {s.contexte}</span></div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
          )}

          {/* Corrélations Hard/Soft dans Orienter */}
          <CorrelationsBlock correlations={iaCorrelations} compact={true} />

          {/* Recommandations par public */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {[
              { public: "Utilisateurs", icon: Users, color: "blue", recos: ["Comprendre sa position sur le marché", "Identifier les compétences à développer", "Découvrir les opportunités compatibles", "Prouver ses soft skills avec des exemples concrets"] },
              { public: "Conseillers / Partenaires", icon: Briefcase, color: "violet", recos: ["Affiner l'accompagnement avec des données terrain", "Orienter efficacement grâce aux tendances", "Détecter les leviers de progression", "Valider les compétences via UBUNTOO"] },
              { public: "Employeurs RH", icon: Target, color: "emerald", recos: ["Identifier des profils pertinents et vérifiés", "Anticiper les besoins en compétences", "Réduire le temps de matching", "Accéder à des preuves de savoir-être"] },
              { public: "Institutions publiques", icon: Globe, color: "amber", recos: ["Piloter les politiques d'emploi avec des données vivantes", "Adapter les offres de formation au terrain", "Anticiper les mutations économiques", "Mesurer l'adéquation offre/demande compétences"] },
            ].map((p, i) => {
              const PIcon = p.icon;
              return (
                <Card key={i}>
                  <CardContent className="p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <PIcon className={`w-4 h-4 text-${p.color}-600`} />
                      <h4 className="text-xs font-semibold text-slate-800">{p.public}</h4>
                    </div>
                    <div className="space-y-1">
                      {p.recos.map((r, j) => (
                        <div key={j} className="flex items-start gap-1.5 text-[10px] text-slate-600"><ArrowRight className={`w-3 h-3 text-${p.color}-400 shrink-0 mt-0.5`} />{r}</div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          {/* Trajectoires observées */}
          {trajectoires.length > 0 && (
            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm flex items-center gap-2"><ArrowRight className="w-4 h-4 text-emerald-600" />Trajectoires observées sur la plateforme</CardTitle></CardHeader>
              <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {trajectoires.slice(0, 6).map((t, i) => (
                  <div key={i} className="flex items-center gap-2 p-2.5 border border-slate-100 rounded-lg">
                    <span className="text-xs text-slate-800 font-medium">{t.source}</span>
                    <ArrowRight className="w-3 h-3 text-emerald-500 shrink-0" />
                    <span className="text-xs text-emerald-700 font-medium">{t.cible}</span>
                    <Badge className="ml-auto bg-emerald-50 text-emerald-700 text-[9px]">{t.probabilite}%</Badge>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>

      {/* Modal de connexion */}
      {showLoginModal && <LoginModal onClose={() => setShowLoginModal(false)} auth={auth} />}
    </div>
  );
};

const LoginModal = ({ onClose, auth }) => {
  const [pseudo, setPseudo] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!pseudo.trim() || !password) return;
    setLoading(true);
    setError("");
    const result = await auth.loginPseudo(pseudo.trim(), password);
    if (result.success) {
      toast.success("Connecté !");
      onClose();
      window.location.reload();
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6 space-y-4" onClick={e => e.stopPropagation()} data-testid="login-modal">
        <div className="text-center">
          <h3 className="text-lg font-bold text-slate-800">Connexion</h3>
          <p className="text-xs text-slate-500 mt-1">Accédez à votre espace RE'ACTIF PRO</p>
        </div>
        <form onSubmit={handleLogin} className="space-y-3">
          <div>
            <label className="text-[10px] text-slate-500 mb-1 block">Identifiant</label>
            <input
              type="text" value={pseudo} onChange={e => setPseudo(e.target.value)}
              placeholder="Votre pseudo" autoFocus
              className="w-full h-9 text-sm border border-slate-200 rounded-lg px-3 focus:outline-none focus:ring-2 focus:ring-indigo-200"
              data-testid="login-pseudo"
            />
          </div>
          <div>
            <label className="text-[10px] text-slate-500 mb-1 block">Mot de passe</label>
            <input
              type="password" value={password} onChange={e => setPassword(e.target.value)}
              placeholder="Votre mot de passe"
              className="w-full h-9 text-sm border border-slate-200 rounded-lg px-3 focus:outline-none focus:ring-2 focus:ring-indigo-200"
              data-testid="login-password"
            />
          </div>
          {error && <p className="text-xs text-red-500 text-center">{error}</p>}
          <Button type="submit" className="w-full h-9 bg-indigo-600 hover:bg-indigo-700 text-sm" disabled={loading} data-testid="login-submit">
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Se connecter"}
          </Button>
        </form>
        <button onClick={onClose} className="w-full text-center text-xs text-slate-400 hover:text-slate-600 transition">Annuler</button>
      </div>
    </div>
  );
};

// ============================================================================
// === Inline analyzer block (admin-triggered Ubuntoo signals detection) =====
// ============================================================================
const UbuntooAnalyzeBlock = ({ token }) => {
  const [days, setDays] = useState(30);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const run = async () => {
    if (!token) { setError("Connecte-toi en admin pour lancer l'analyse."); return; }
    setAnalyzing(true);
    setError(null);
    setResult(null);
    try {
      const res = await axios.post(
        `${API}/ubuntoo/signals/analyze?token=${token}`,
        { days },
        { timeout: 120000 }
      );
      setResult(res.data);
    } catch (e) {
      setError(e?.response?.data?.detail || e?.message || "Erreur réseau");
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex items-end gap-3 flex-wrap">
        <div>
          <label className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider block mb-1">Période</label>
          <select
            className="border border-slate-200 rounded-lg px-3 py-1.5 text-sm bg-white"
            value={days}
            onChange={(e) => setDays(parseInt(e.target.value, 10))}
            disabled={analyzing}
            data-testid="signals-period"
          >
            <option value={7}>7 derniers jours</option>
            <option value={14}>14 derniers jours</option>
            <option value={30}>30 derniers jours</option>
            <option value={60}>60 derniers jours</option>
            <option value={90}>3 derniers mois</option>
          </select>
        </div>
        <Button
          onClick={run}
          disabled={analyzing}
          className="bg-amber-600 hover:bg-amber-700 text-white"
          data-testid="signals-analyze-btn"
        >
          {analyzing
            ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Analyse en cours…</>
            : <><Sparkles className="w-4 h-4 mr-2" /> Lancer l'analyse maintenant</>}
        </Button>
      </div>

      {error && (
        <div className="text-xs text-red-700 bg-red-50 border border-red-200 rounded-lg p-2" data-testid="signals-error">
          ⚠️ {error}
        </div>
      )}

      {result && (
        <div className="text-sm bg-white border border-amber-200 rounded-lg p-3 space-y-2" data-testid="signals-result">
          <p className="font-semibold text-slate-900 text-xs">✅ Analyse terminée</p>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center">
            <div className="bg-slate-50 rounded-md p-2">
              <p className="text-xl font-bold text-slate-900">{result.analyzed_messages}</p>
              <p className="text-[9px] text-slate-500 uppercase">Messages scannés</p>
            </div>
            <div className="bg-blue-50 rounded-md p-2">
              <p className="text-xl font-bold text-blue-700">{result.detected}</p>
              <p className="text-[9px] text-blue-600 uppercase">Détectés</p>
            </div>
            <div className="bg-emerald-50 rounded-md p-2">
              <p className="text-xl font-bold text-emerald-700">{result.created}</p>
              <p className="text-[9px] text-emerald-600 uppercase">Nouveaux</p>
            </div>
            <div className="bg-indigo-50 rounded-md p-2">
              <p className="text-xl font-bold text-indigo-700">{result.updated}</p>
              <p className="text-[9px] text-indigo-600 uppercase">Mis à jour</p>
            </div>
          </div>
          {(result.signals_preview || []).length > 0 && (
            <div className="flex flex-wrap gap-1 pt-1">
              {result.signals_preview.map((s, i) => (
                <Badge key={i} className="text-[10px] bg-amber-100 text-amber-700">{s.name}</Badge>
              ))}
            </div>
          )}
          {result.note && <p className="text-[10px] text-slate-500 italic">{result.note}</p>}
        </div>
      )}
    </div>
  );
};

export default OpcView;
