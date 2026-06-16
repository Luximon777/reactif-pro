import React, { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { toast } from "sonner";
import {
  BarChart3, BookOpen, Map, ArrowRightLeft, TrendingUp, GraduationCap,
  MapPin, Brain, Search, ChevronRight, Loader2, FileText, Target,
  Layers, Building2, AlertTriangle, CheckCircle2, ArrowLeft, RefreshCw,
  Sparkles, Clock, Award, Filter, X, ExternalLink, Zap,
  ArrowUpRight, ArrowDownRight, Minus
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Input } from "../components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { Progress } from "../components/ui/progress";

const API = process.env.REACT_APP_BACKEND_URL + "/api";

const MODULES = [
  { key: "dashboard", label: "Tableau de bord", icon: BarChart3, color: "#1e3a5f" },
  { key: "referentiel", label: "Référentiel vivant", icon: BookOpen, color: "#2563eb" },
  { key: "cartographie", label: "Cartographie métiers", icon: Map, color: "#7c3aed" },
  { key: "transitions", label: "Transitions", icon: ArrowRightLeft, color: "#059669" },
  { key: "emergentes", label: "Compétences émergentes", icon: TrendingUp, color: "#d97706" },
  { key: "certifications", label: "Certifications RNCP", icon: GraduationCap, color: "#dc2626" },
  { key: "territorial", label: "Intelligence territoriale", icon: MapPin, color: "#0891b2" },
  { key: "predictif", label: "Moteur prédictif", icon: Brain, color: "#9333ea" },
];

export default function OpcDediePage({ token, onBack }) {
  const [activeModule, setActiveModule] = useState("dashboard");
  const [loading, setLoading] = useState({});
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Data states
  const [rncpStats, setRncpStats] = useState(null);
  const [dashStats, setDashStats] = useState(null);
  const [searchResults, setSearchResults] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [emergentes, setEmergentes] = useState(null);
  const [trajectoires, setTrajectoires] = useState(null);
  const [correlations, setCorrelations] = useState(null);
  const [predictions, setPredictions] = useState(null);
  const [recommandation, setRecommandation] = useState(null);
  const [rncpSearchResults, setRncpSearchResults] = useState(null);
  const [rncpSearchQ, setRncpSearchQ] = useState("");
  const [selectedCert, setSelectedCert] = useState(null);
  const [tensionCerts, setTensionCerts] = useState(null);
  const [metierContext, setMetierContext] = useState("");
  const [cartographie, setCartographie] = useState(null);

  const tokenParam = token ? `token=${token}` : "";

  // Load dashboard stats on mount
  useEffect(() => {
    loadDashboardStats();
    loadRncpStats();
  }, []);

  const loadDashboardStats = async () => {
    try {
      const res = await axios.get(`${API}/observatory/dashboard?${tokenParam}`);
      setDashStats(res.data);
    } catch { /* ignore */ }
  };

  const loadRncpStats = async () => {
    try {
      const res = await axios.get(`${API}/referentiel/rncp/stats`);
      setRncpStats(res.data);
    } catch { /* ignore */ }
  };

  const runIa = async (endpoint, setter, label) => {
    setLoading(l => ({ ...l, [endpoint]: true }));
    try {
      const body = metierContext ? { contexte_metier: metierContext } : {};
      const res = await axios.post(`${API}/observatory/ia/${endpoint}?${tokenParam}`, body, { timeout: 90000 });
      if (res.data && !res.data.error) {
        setter(res.data);
        toast.success(`${label} terminé${metierContext ? ` (${metierContext})` : ""}`);
      } else {
        toast.error(res.data?.error || "Erreur");
      }
    } catch (e) {
      toast.error(`Erreur: ${e.message}`);
    }
    setLoading(l => ({ ...l, [endpoint]: false }));
  };

  const searchReferentiel = async () => {
    if (!searchQuery.trim()) return;
    setLoading(l => ({ ...l, referentiel: true }));
    try {
      const res = await axios.get(`${API}/referentiel/search?q=${encodeURIComponent(searchQuery)}&${tokenParam}`);
      setSearchResults(res.data);
    } catch { toast.error("Erreur de recherche"); }
    setLoading(l => ({ ...l, referentiel: false }));
  };

  const searchRncp = async () => {
    if (!rncpSearchQ.trim()) return;
    setLoading(l => ({ ...l, rncp: true }));
    try {
      const res = await axios.get(`${API}/referentiel/rncp/search?q=${encodeURIComponent(rncpSearchQ)}&limit=20`);
      setRncpSearchResults(res.data);
    } catch { toast.error("Erreur de recherche RNCP"); }
    setLoading(l => ({ ...l, rncp: false }));
  };

  const loadCertDetail = async (code) => {
    setLoading(l => ({ ...l, certDetail: true }));
    try {
      const res = await axios.get(`${API}/referentiel/rncp/fiche/${code}`);
      setSelectedCert(res.data);
    } catch { toast.error("Erreur chargement fiche"); }
    setLoading(l => ({ ...l, certDetail: false }));
  };

  const loadTension = async () => {
    setLoading(l => ({ ...l, tension: true }));
    try {
      const res = await axios.get(`${API}/referentiel/rncp/tension?limit=15`);
      setTensionCerts(res.data);
    } catch { /* ignore */ }
    setLoading(l => ({ ...l, tension: false }));
  };

  const loadPredictions = async () => {
    setLoading(l => ({ ...l, predict: true }));
    try {
      const body = metierContext ? { contexte_metier: metierContext } : {};
      const res = await axios.post(`${API}/observatory/predict-competences?${tokenParam}`, body, { timeout: 90000 });
      setPredictions(res.data);
      toast.success("Prédictions générées");
    } catch { toast.error("Erreur prédictions"); }
    setLoading(l => ({ ...l, predict: false }));
  };

  const loadCartographieExhaustive = async () => {
    if (!metierContext.trim()) {
      toast.error("Saisissez un domaine métier dans le champ « Contexte métier »");
      return;
    }
    setLoading(l => ({ ...l, cartographie: true }));
    try {
      const res = await axios.post(`${API}/observatory/ia/cartographie-exhaustive?${tokenParam}`, { contexte_metier: metierContext }, { timeout: 120000 });
      if (res.data && !res.data.error) {
        setCartographie(res.data);
        toast.success(`Cartographie exhaustive générée : ${res.data.total_metiers || 0} métiers identifiés`);
        setActiveModule("predictif");
      } else {
        toast.error(res.data?.error || "Erreur de génération");
      }
    } catch (e) {
      toast.error(`Erreur: ${e.message}`);
    }
    setLoading(l => ({ ...l, cartographie: false }));
  };

  const ActiveIcon = MODULES.find(m => m.key === activeModule)?.icon || BarChart3;
  const activeColor = MODULES.find(m => m.key === activeModule)?.color || "#1e3a5f";

  return (
    <div className="min-h-screen bg-slate-50 flex" data-testid="opc-standalone">
      {/* ─── Sidebar ─── */}
      <aside className={`${sidebarOpen ? "w-64" : "w-16"} bg-[#1e3a5f] text-white flex flex-col transition-all duration-300 shrink-0`}>
        <div className="p-4 border-b border-white/10">
          <div className="flex items-center gap-2">
            <BarChart3 className="w-6 h-6 text-emerald-400 shrink-0" />
            {sidebarOpen && (
              <div>
                <div className="font-bold text-sm tracking-wide">OPC</div>
                <div className="text-[10px] text-slate-300">RE'ACTIF PRO</div>
              </div>
            )}
          </div>
        </div>
        <nav className="flex-1 py-2 overflow-y-auto">
          {MODULES.map(mod => {
            const Icon = mod.icon;
            const isActive = activeModule === mod.key;
            return (
              <button
                key={mod.key}
                data-testid={`opc-nav-${mod.key}`}
                onClick={() => setActiveModule(mod.key)}
                className={`w-full flex items-center gap-3 px-4 py-3 text-left text-sm transition-all ${isActive ? "bg-white/15 border-r-2 border-emerald-400 text-white" : "text-slate-300 hover:bg-white/5 hover:text-white"}`}
              >
                <Icon className="w-4.5 h-4.5 shrink-0" style={{ color: isActive ? "#6ee7b7" : undefined }} />
                {sidebarOpen && <span className="truncate">{mod.label}</span>}
              </button>
            );
          })}
        </nav>
        <div className="p-3 border-t border-white/10">
          {onBack && (
            <button onClick={onBack} className="flex items-center gap-2 text-xs text-slate-400 hover:text-white w-full" data-testid="opc-back">
              <ArrowLeft className="w-3.5 h-3.5" />
              {sidebarOpen && "Retour"}
            </button>
          )}
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="mt-2 flex items-center gap-2 text-xs text-slate-500 hover:text-white w-full">
            <ChevronRight className={`w-3.5 h-3.5 transition-transform ${sidebarOpen ? "rotate-180" : ""}`} />
            {sidebarOpen && "Réduire"}
          </button>
        </div>
      </aside>

      {/* ─── Main content ─── */}
      <main className="flex-1 overflow-y-auto">
        {/* Header */}
        <header className="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between sticky top-0 z-10">
          <div className="flex items-center gap-3">
            <ActiveIcon className="w-5 h-5" style={{ color: activeColor }} />
            <div>
              <h1 className="text-lg font-bold text-slate-800" data-testid="opc-module-title">
                {MODULES.find(m => m.key === activeModule)?.label}
              </h1>
              <p className="text-xs text-slate-500">Observatoire Prédictif des Compétences — RE'ACTIF PRO</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {/* Contexte métier global */}
            <div className="flex items-center gap-2 bg-slate-50 rounded-lg px-3 py-1.5 border border-slate-200">
              <Search className="w-3.5 h-3.5 text-slate-400" />
              <input
                className="bg-transparent text-sm w-40 outline-none placeholder:text-slate-400"
                placeholder="Contexte métier..."
                value={metierContext}
                onChange={e => setMetierContext(e.target.value)}
                data-testid="opc-metier-context"
              />
              {metierContext && (
                <button onClick={() => setMetierContext("")} className="text-slate-400 hover:text-slate-600">
                  <X className="w-3 h-3" />
                </button>
              )}
            </div>
            <Button
              variant="outline"
              size="sm"
              className="text-xs text-emerald-700 border-emerald-200 bg-emerald-50 hover:bg-emerald-100"
              disabled={loading["analyse-complete"]}
              data-testid="opc-ia-predictive-btn"
              onClick={async () => {
                setLoading(l => ({ ...l, "analyse-complete": true }));
                try {
                  const body = metierContext ? { contexte_metier: metierContext } : {};
                  const res = await axios.post(`${API}/observatory/ia/analyse-complete?${tokenParam}`, body, { timeout: 120000 });
                  if (res.data.emergentes) setEmergentes(res.data.emergentes);
                  if (res.data.correlations) setCorrelations(res.data.correlations);
                  if (res.data.trajectoires) setTrajectoires(res.data.trajectoires);
                  if (res.data.recommandation) setRecommandation(res.data.recommandation);
                  toast.success("Analyse IA complète terminée — consultez chaque module pour les résultats");
                } catch { toast.error("Erreur lors de l'analyse IA"); }
                setLoading(l => ({ ...l, "analyse-complete": false }));
              }}
            >
              {loading["analyse-complete"] ? <Loader2 className="w-3 h-3 mr-1 animate-spin" /> : <Zap className="w-3 h-3 mr-1" />}
              {loading["analyse-complete"] ? "Analyse en cours..." : "Lancer l'analyse IA"}
            </Button>
          </div>
        </header>

        {/* Content */}
        <div className="p-6 max-w-7xl mx-auto">
          {activeModule === "dashboard" && <DashboardModule stats={dashStats} rncpStats={rncpStats} onRefresh={async () => {
            setLoading(l => ({ ...l, dashRefresh: true }));
            await Promise.all([loadDashboardStats(), loadRncpStats()]);
            setLoading(l => ({ ...l, dashRefresh: false }));
            toast.success("Tableau de bord actualisé");
          }} refreshLoading={loading.dashRefresh} />}
          {activeModule === "referentiel" && <ReferentielModule query={searchQuery} setQuery={setSearchQuery} results={searchResults} onSearch={searchReferentiel} loading={loading.referentiel} />}
          {activeModule === "cartographie" && <CartographieModule />}
          {activeModule === "transitions" && <TransitionsModule trajectoires={trajectoires} correlations={correlations} loading={loading} metier={metierContext} onRunTrajectoires={() => runIa("trajectoires", setTrajectoires, "Trajectoires")} onRunCorrelations={() => runIa("correlations", setCorrelations, "Corrélations")} />}
          {activeModule === "emergentes" && <EmergentesModule emergentes={emergentes} loading={loading["detect-emergentes"]} metier={metierContext} onRun={() => runIa("detect-emergentes", setEmergentes, "Compétences émergentes")} />}
          {activeModule === "certifications" && <CertificationsModule searchQ={rncpSearchQ} setSearchQ={setRncpSearchQ} results={rncpSearchResults} onSearch={searchRncp} loading={loading} selectedCert={selectedCert} onSelectCert={loadCertDetail} onClearCert={() => setSelectedCert(null)} tensionCerts={tensionCerts} onLoadTension={loadTension} />}
          {activeModule === "territorial" && <TerritorialModule rncpStats={rncpStats} tensionCerts={tensionCerts} onLoadTension={loadTension} loading={loading.tension} />}
          {activeModule === "predictif" && <PredictifModule predictions={predictions} recommandation={recommandation} cartographie={cartographie} loading={loading} metier={metierContext} onRunPredictions={loadPredictions} onRunRecommandation={() => runIa("recommandation", setRecommandation, "Recommandation")} onRunCartographie={loadCartographieExhaustive} onRunAnalyseComplete={async () => {
            setLoading(l => ({ ...l, "analyse-complete": true }));
            try {
              const body = metierContext ? { contexte_metier: metierContext } : {};
              const res = await axios.post(`${API}/observatory/ia/analyse-complete?${tokenParam}`, body, { timeout: 120000 });
              if (res.data.emergentes) setEmergentes(res.data.emergentes);
              if (res.data.correlations) setCorrelations(res.data.correlations);
              if (res.data.trajectoires) setTrajectoires(res.data.trajectoires);
              if (res.data.recommandation) setRecommandation(res.data.recommandation);
              toast.success("Analyse complète terminée");
            } catch { toast.error("Erreur analyse complète"); }
            setLoading(l => ({ ...l, "analyse-complete": false }));
          }} />}
        </div>
      </main>
    </div>
  );
}


// ═══════════════════════════════════════════════════════════════════════════════
// Module 0: TABLEAU DE BORD
// ═══════════════════════════════════════════════════════════════════════════════
function DashboardModule({ stats, rncpStats, onRefresh, refreshLoading }) {
  const now = new Date();
  const dateStr = now.toLocaleDateString("fr-FR", { weekday: "long", day: "numeric", month: "long", year: "numeric" });
  const timeStr = now.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" });

  const kpis = [
    { label: "Certifications RNCP", value: rncpStats?.rncp_actives || "—", sub: "actives", icon: GraduationCap, color: "text-red-600 bg-red-50" },
    { label: "Certifications RS", value: rncpStats?.rs_actives || "—", sub: "actives", icon: Award, color: "text-amber-600 bg-amber-50" },
    { label: "Blocs de compétences", value: rncpStats?.blocs_competences?.toLocaleString() || "—", sub: "enregistrés", icon: Layers, color: "text-blue-600 bg-blue-50" },
    { label: "Mappings ROME", value: rncpStats?.mappings_rome?.toLocaleString() || "—", sub: "liens", icon: ArrowRightLeft, color: "text-emerald-600 bg-emerald-50" },
    { label: "Fiches ROME", value: stats?.rome_count || "1 911", sub: "France Travail", icon: FileText, color: "text-violet-600 bg-violet-50" },
    { label: "Métiers OPC", value: stats?.metiers_count || "289", sub: "base interne", icon: Building2, color: "text-cyan-600 bg-cyan-50" },
  ];

  return (
    <div className="space-y-6" data-testid="opc-mod-dashboard">
      {/* En-tête avec date et bouton Actualiser */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm text-slate-500">
          <Clock className="w-4 h-4" />
          <span>Situation au <strong className="text-slate-700">{dateStr}</strong> — {timeStr}</span>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={onRefresh}
          disabled={refreshLoading}
          className="text-xs border-blue-200 text-blue-700 bg-blue-50 hover:bg-blue-100"
          data-testid="opc-dashboard-refresh"
        >
          {refreshLoading ? <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" /> : <RefreshCw className="w-3.5 h-3.5 mr-1.5" />}
          Actualiser les données
        </Button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {kpis.map((kpi, i) => {
          const Icon = kpi.icon;
          return (
            <Card key={i} className="border-slate-200">
              <CardContent className="p-4 text-center">
                <div className={`w-10 h-10 rounded-lg ${kpi.color} flex items-center justify-center mx-auto mb-2`}>
                  <Icon className="w-5 h-5" />
                </div>
                <div className="text-2xl font-bold text-slate-800">{kpi.value}</div>
                <div className="text-[10px] text-slate-500 mt-0.5">{kpi.label}</div>
                <div className="text-[9px] text-slate-400">{kpi.sub}</div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Sources de données */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm flex items-center gap-2"><Layers className="w-4 h-4 text-blue-600" />Sources de données connectées</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {[
              { name: "France Compétences (RNCP/RS)", status: "connecté", count: `${rncpStats?.total_certifications?.toLocaleString() || "30 022"} fiches`, color: "emerald" },
              { name: "France Travail (ROME 4.0)", status: "connecté", count: "1 911 fiches", color: "emerald" },
              { name: "Base RE'ACTIF PRO", status: "connecté", count: "20 filières, 289 métiers", color: "emerald" },
            ].map((src, i) => (
              <div key={i} className={`flex items-center gap-3 p-3 rounded-lg border border-${src.color}-200 bg-${src.color}-50/30`}>
                <CheckCircle2 className={`w-4 h-4 text-${src.color}-600 shrink-0`} />
                <div>
                  <div className="text-xs font-semibold text-slate-700">{src.name}</div>
                  <div className="text-[10px] text-slate-500">{src.count}</div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Répartition par niveau */}
      {rncpStats?.par_niveau && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2"><BarChart3 className="w-4 h-4 text-violet-600" />Répartition des certifications RNCP actives par niveau</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {Object.entries(rncpStats.par_niveau).sort((a,b) => b[1] - a[1]).map(([level, count]) => {
                const max = Math.max(...Object.values(rncpStats.par_niveau));
                return (
                  <div key={level} className="flex items-center gap-3">
                    <span className="text-xs text-slate-600 w-32 text-right shrink-0">{level || "Non renseigné"}</span>
                    <div className="flex-1 bg-slate-100 rounded-full h-5 overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-blue-500 to-violet-500 rounded-full flex items-center justify-end pr-2" style={{ width: `${(count / max) * 100}%` }}>
                        <span className="text-[10px] font-bold text-white">{count}</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {rncpStats?.derniere_importation && (
        <div className="text-xs text-slate-400 flex items-center gap-1">
          <Clock className="w-3 h-3" />
          Dernière importation RNCP : {new Date(rncpStats.derniere_importation).toLocaleString("fr-FR")}
        </div>
      )}
    </div>
  );
}


// ═══════════════════════════════════════════════════════════════════════════════
// Module 1: RÉFÉRENTIEL VIVANT DES COMPÉTENCES
// ═══════════════════════════════════════════════════════════════════════════════
function ReferentielModule({ query, setQuery, results, onSearch, loading }) {
  // Flatten all result categories into sections for display
  const sections = [];
  if (results) {
    if (results.rome?.length > 0) sections.push({ title: "Fiches ROME", badge: "ROME", color: "blue", items: results.rome.map(r => ({ name: r.nom || r.libelle, sub: `${r.code_rome || ""} — ${r.grand_domaine || ""}`, source: "ROME" })) });
    if (results.metiers?.length > 0) sections.push({ title: "Métiers OPC", badge: "OPC", color: "violet", items: results.metiers.map(m => ({ name: m.nom || m.metier, sub: `${m.filiere_nom || ""} — ${m.sector_name || m.secteur_code || ""}`, detail: m.missions, source: "OPC" })) });
    if (results.capacites_techniques?.length > 0) sections.push({ title: "Compétences techniques", badge: "Technique", color: "amber", items: results.capacites_techniques.map(c => ({ name: c.nom, sub: c.description || "", source: "Compétence" })) });
    if (results.savoir_etre?.length > 0) sections.push({ title: "Savoir-être", badge: "Soft Skill", color: "emerald", items: results.savoir_etre.map(s => ({ name: s.nom, sub: s.description || "", source: "Savoir-être" })) });
    if (results.filieres?.length > 0) sections.push({ title: "Filières", badge: "Filière", color: "cyan", items: results.filieres.map(f => ({ name: f.nom, sub: `${f.secteurs?.length || 0} secteurs`, source: "Filière" })) });
    // Also check if there's a flat "results" key (from RNCP search)
    if (results.results?.length > 0) sections.push({ title: "Résultats", badge: "Résultat", color: "slate", items: results.results.map(r => ({ name: r.metier || r.nom || r.libelle || r.intitule, sub: `${r.filiere_nom || r.grand_domaine_nom || r.secteur || ""} ${r.code_rome ? `(${r.code_rome})` : ""}`, detail: r.mission, source: r.source === "france_travail_rome_4" ? "ROME" : "OPC" })) });
  }

  return (
    <div className="space-y-4" data-testid="opc-mod-referentiel">
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-xs text-blue-700">
        <strong>Module 1 — Référentiel vivant des compétences</strong> : Recherchez dans la base fusionnée RE'ACTIF PRO + ROME France Travail. Le référentiel s'enrichit automatiquement des données terrain et des analyses IA.
      </div>
      <div className="flex gap-2">
        <Input placeholder="Rechercher un métier, une compétence, un savoir-être..." value={query} onChange={e => setQuery(e.target.value)} onKeyDown={e => e.key === "Enter" && onSearch()} className="flex-1" data-testid="opc-ref-search" />
        <Button onClick={onSearch} disabled={loading} data-testid="opc-ref-search-btn">
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
          Rechercher
        </Button>
      </div>
      {results && (
        <div className="space-y-4">
          <div className="text-xs text-slate-500">{results.total ?? 0} résultat(s)</div>
          {sections.map((sec, si) => (
            <div key={si}>
              <h3 className="text-xs font-semibold text-slate-600 mb-1.5 flex items-center gap-2">
                <Badge className={`bg-${sec.color}-100 text-${sec.color}-700 text-[9px]`}>{sec.badge}</Badge>
                {sec.title} ({sec.items.length})
              </h3>
              <div className="space-y-1.5">
                {sec.items.map((item, i) => (
                  <Card key={i} className="border-slate-200 hover:border-blue-300 transition-colors">
                    <CardContent className="p-3">
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <div className="text-sm font-semibold text-slate-800">{item.name}</div>
                          {item.sub && <div className="text-xs text-slate-500 mt-0.5">{item.sub}</div>}
                          {item.detail && <div className="text-xs text-slate-600 mt-1 line-clamp-2">{item.detail}</div>}
                        </div>
                        <Badge variant="outline" className="text-[10px] shrink-0">{item.source}</Badge>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          ))}
          {sections.length === 0 && <div className="text-sm text-slate-500 text-center py-4">Aucun résultat trouvé</div>}
        </div>
      )}
    </div>
  );
}


// ═══════════════════════════════════════════════════════════════════════════════
// Module 2: CARTOGRAPHIE DES MÉTIERS
// ═══════════════════════════════════════════════════════════════════════════════
function CartographieModule() {
  const [filieres, setFilieres] = useState([]);
  const [selectedFiliere, setSelectedFiliere] = useState(null);
  const [metiers, setMetiers] = useState([]);
  const [loadingMetiers, setLoadingMetiers] = useState(false);

  useEffect(() => {
    axios.get(`${API}/referentiel/filieres`)
      .then(r => setFilieres(r.data?.filieres || r.data || []))
      .catch(() => {});
  }, []);

  const loadMetiersByFiliere = async (code) => {
    setSelectedFiliere(code);
    setLoadingMetiers(true);
    try {
      const res = await axios.get(`${API}/referentiel/search?filiere=${code}&limit=50`);
      setMetiers(res.data?.metiers || res.data?.results || []);
    } catch { setMetiers([]); }
    setLoadingMetiers(false);
  };

  return (
    <div className="space-y-4" data-testid="opc-mod-cartographie">
      <div className="bg-violet-50 border border-violet-200 rounded-lg p-3 text-xs text-violet-700">
        <strong>Module 2 — Cartographie des métiers</strong> : Explorez les métiers par filière professionnelle et secteur d'activité. Visualisez les compétences techniques et transversales associées.
      </div>
      {filieres.length === 0 ? (
        <div className="text-sm text-slate-500 text-center py-4">Chargement des filières...</div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-2">
          {filieres.map((f, i) => (
            <button key={i} onClick={() => loadMetiersByFiliere(f.code)} className={`p-3 rounded-lg border text-left text-xs transition-colors ${selectedFiliere === f.code ? "bg-violet-100 border-violet-400 text-violet-800" : "bg-white border-slate-200 hover:border-violet-300 text-slate-700"}`}>
              <div className="font-semibold truncate">{f.nom}</div>
              <div className="text-[10px] text-slate-500 mt-0.5">{f.secteurs?.length || 0} secteurs</div>
            </button>
          ))}
        </div>
      )}
      {loadingMetiers && <div className="text-sm text-slate-500 text-center py-4 flex items-center justify-center gap-2"><Loader2 className="w-4 h-4 animate-spin" />Chargement...</div>}
      {!loadingMetiers && metiers.length > 0 && (
        <div className="space-y-1">
          <div className="text-xs text-slate-500 font-medium">{metiers.length} métier(s)</div>
          {metiers.map((m, i) => (
            <div key={i} className="p-2.5 bg-white rounded border border-slate-200 text-xs">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-slate-700">{m.nom || m.metier || m.libelle}</span>
                <span className="text-slate-400 text-[10px]">{m.sector_name || m.secteur_code || ""}</span>
              </div>
              {m.missions && <div className="text-[10px] text-slate-500 mt-1 line-clamp-1">{m.missions}</div>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}


// ═══════════════════════════════════════════════════════════════════════════════
// Module 3: TRANSITIONS PROFESSIONNELLES
// ═══════════════════════════════════════════════════════════════════════════════
function TransitionsModule({ trajectoires, correlations, loading, metier, onRunTrajectoires, onRunCorrelations }) {
  return (
    <div className="space-y-4" data-testid="opc-mod-transitions">
      <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-3 text-xs text-emerald-700">
        <strong>Module 3 — Cartographie des transitions</strong> : Identifie les passerelles réalistes entre métiers et analyse les corrélations compétences techniques / savoir-être.
        {metier && <span className="font-bold ml-1">Contexte : {metier}</span>}
      </div>
      <div className="flex gap-2">
        <Button onClick={onRunTrajectoires} disabled={loading.trajectoires} variant="outline" className="border-emerald-300 text-emerald-700 hover:bg-emerald-50" data-testid="opc-run-trajectoires">
          {loading.trajectoires ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : <ArrowRightLeft className="w-4 h-4 mr-1" />}
          Analyser les trajectoires
        </Button>
        <Button onClick={onRunCorrelations} disabled={loading.correlations} variant="outline" className="border-blue-300 text-blue-700 hover:bg-blue-50" data-testid="opc-run-correlations">
          {loading.correlations ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : <Target className="w-4 h-4 mr-1" />}
          Corrélations Hard/Soft Skills
        </Button>
      </div>

      {Array.isArray(trajectoires) && trajectoires.length > 0 && (
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Trajectoires professionnelles identifiées</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {trajectoires.map((t, i) => (
              <div key={i} className="flex items-center gap-3 p-2 bg-slate-50 rounded-lg">
                <div className="text-xs font-semibold text-slate-700 w-28 truncate">{t.metier_source}</div>
                <ChevronRight className="w-4 h-4 text-emerald-500 shrink-0" />
                <div className="flex-1">
                  <div className="text-xs font-semibold text-emerald-700">{t.metier_cible}</div>
                  <div className="text-[10px] text-slate-500">{t.justification}</div>
                </div>
                <Badge className={`text-[10px] shrink-0 ${t.probabilite >= 70 ? "bg-emerald-100 text-emerald-700" : "bg-amber-100 text-amber-700"}`}>{t.probabilite}%</Badge>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {Array.isArray(correlations) && correlations.length > 0 && (
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Corrélations compétences techniques ↔ savoir-être</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {correlations.map((c, i) => (
              <div key={i} className="p-2 bg-blue-50/50 rounded-lg">
                <div className="text-xs font-semibold text-slate-700 mb-1">{c.competence_technique}</div>
                <div className="flex flex-wrap gap-1">
                  {(c.savoir_etre || []).map((se, j) => (
                    <Badge key={j} variant="outline" className="text-[9px]" style={{ borderColor: se.importance >= 4 ? "#059669" : "#d97706" }}>
                      {se.nom} ({se.importance}/5)
                    </Badge>
                  ))}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}


// ═══════════════════════════════════════════════════════════════════════════════
// Module 4: COMPÉTENCES ÉMERGENTES
// ═══════════════════════════════════════════════════════════════════════════════
function EmergentesModule({ emergentes, loading, metier, onRun }) {
  return (
    <div className="space-y-4" data-testid="opc-mod-emergentes">
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-xs text-amber-700">
        <strong>Module 4 — Détection des compétences émergentes</strong> : Analyse IA des tendances du marché pour identifier les compétences en progression.
        {metier && <span className="font-bold ml-1">Contexte : {metier}</span>}
      </div>
      <Button onClick={onRun} disabled={loading} data-testid="opc-run-emergentes">
        {loading ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : <TrendingUp className="w-4 h-4 mr-1" />}
        Détecter les compétences émergentes
      </Button>
      {Array.isArray(emergentes) && emergentes.length > 0 && (
        <div className="space-y-2">
          {emergentes.map((e, i) => (
            <div key={i} className="flex items-center gap-3 p-3 bg-white rounded-lg border border-slate-200">
              <Badge className={`text-[9px] shrink-0 ${e.tendance === "en forte hausse" ? "bg-red-100 text-red-700" : e.tendance === "en hausse" ? "bg-amber-100 text-amber-700" : e.tendance === "émergente" ? "bg-violet-100 text-violet-700" : "bg-slate-100 text-slate-600"}`}>{e.tendance}</Badge>
              <div className="flex-1">
                <div className="text-sm font-medium text-slate-800">{e.competence}</div>
                <div className="text-[10px] text-slate-500">{(e.secteurs || []).join(", ")}</div>
              </div>
              <div className="text-right">
                <div className="text-lg font-bold" style={{ color: e.score_emergence >= 80 ? "#dc2626" : e.score_emergence >= 60 ? "#d97706" : "#6b7280" }}>{e.score_emergence}</div>
                <div className="text-[9px] text-slate-400">score</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}


// ═══════════════════════════════════════════════════════════════════════════════
// Module 5: CERTIFICATIONS RNCP
// ═══════════════════════════════════════════════════════════════════════════════
function CertificationsModule({ searchQ, setSearchQ, results, onSearch, loading, selectedCert, onSelectCert, onClearCert, tensionCerts, onLoadTension }) {
  if (selectedCert) {
    return (
      <div className="space-y-4" data-testid="opc-cert-detail">
        <Button variant="ghost" size="sm" onClick={onClearCert}><ArrowLeft className="w-4 h-4 mr-1" />Retour</Button>
        <Card>
          <CardHeader>
            <div className="flex items-start justify-between">
              <div>
                <Badge className="bg-red-100 text-red-700 text-xs mb-2">{selectedCert.code}</Badge>
                <CardTitle className="text-base">{selectedCert.intitule}</CardTitle>
                <div className="text-xs text-slate-500 mt-1">{selectedCert.niveau_libelle} — {selectedCert.abrege_intitule || selectedCert.abrege_libelle}</div>
              </div>
              <Badge className={selectedCert.statut === "ACTIVE" ? "bg-emerald-100 text-emerald-700" : "bg-slate-100 text-slate-500"}>{selectedCert.statut}</Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {selectedCert.blocs_competences?.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-slate-700 mb-2 flex items-center gap-1"><Layers className="w-4 h-4" />{selectedCert.blocs_competences.length} Blocs de compétences</h3>
                {selectedCert.blocs_competences.map((b, i) => (
                  <div key={i} className="p-2 bg-slate-50 rounded mb-1 text-xs">
                    <span className="font-mono text-slate-400 mr-2">{b.code_bloc}</span>
                    <span className="text-slate-700">{b.intitule}</span>
                  </div>
                ))}
              </div>
            )}
            {selectedCert.codes_rome?.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-slate-700 mb-2">Codes ROME associés</h3>
                <div className="flex flex-wrap gap-1">
                  {selectedCert.codes_rome.map((r, i) => (
                    <Badge key={i} variant="outline" className="text-[10px]">{r.code_rome} — {r.libelle_rome}</Badge>
                  ))}
                </div>
              </div>
            )}
            {selectedCert.certificateurs?.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-slate-700 mb-2">Certificateur(s)</h3>
                {selectedCert.certificateurs.map((c, i) => (
                  <div key={i} className="text-xs text-slate-600">{c.nom}</div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-4" data-testid="opc-mod-certifications">
      <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-xs text-red-700">
        <strong>Module 5 — Intelligence formation / Certifications RNCP</strong> : Explorez les 30 000+ certifications RNCP/RS de France Compétences, leurs blocs de compétences et les codes ROME associés.
      </div>
      <div className="flex gap-2">
        <Input placeholder="Rechercher une certification (ex: comptable, développeur, RH...)" value={searchQ} onChange={e => setSearchQ(e.target.value)} onKeyDown={e => e.key === "Enter" && onSearch()} className="flex-1" data-testid="opc-rncp-search" />
        <Button onClick={onSearch} disabled={loading.rncp} data-testid="opc-rncp-search-btn">
          {loading.rncp ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
        </Button>
        <Button variant="outline" onClick={onLoadTension} disabled={loading.tension}>
          {loading.tension ? <Loader2 className="w-4 h-4 animate-spin" /> : <AlertTriangle className="w-4 h-4" />}
          En tension
        </Button>
      </div>

      {results && (
        <div className="space-y-1.5">
          <div className="text-xs text-slate-500">{results.total} certification(s) trouvée(s)</div>
          {(results.results || []).map((r, i) => (
            <button key={i} onClick={() => onSelectCert(r.code)} className="w-full text-left p-3 bg-white rounded-lg border border-slate-200 hover:border-red-300 transition-colors" data-testid={`opc-rncp-result-${i}`}>
              <div className="flex items-center justify-between">
                <div>
                  <Badge variant="outline" className="text-[9px] mr-2">{r.code}</Badge>
                  <span className="text-sm font-medium text-slate-800">{r.intitule}</span>
                </div>
                <div className="flex items-center gap-2">
                  {r.niveau_libelle && <Badge className="bg-blue-100 text-blue-700 text-[10px]">{r.niveau_libelle}</Badge>}
                  <ChevronRight className="w-4 h-4 text-slate-400" />
                </div>
              </div>
            </button>
          ))}
        </div>
      )}

      {tensionCerts?.certifications_en_tension?.length > 0 && (
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm flex items-center gap-2"><AlertTriangle className="w-4 h-4 text-amber-600" />Certifications en tension — {tensionCerts.territoire}</CardTitle></CardHeader>
          <CardContent className="space-y-1.5">
            {tensionCerts.certifications_en_tension.map((c, i) => (
              <button key={i} onClick={() => onSelectCert(c.code)} className="w-full text-left p-2 bg-amber-50/50 rounded border border-amber-100 hover:border-amber-300 transition-colors text-xs flex items-center justify-between">
                <div>
                  <span className="font-semibold text-slate-700">{c.intitule}</span>
                  <span className="text-slate-400 ml-2">{c.niveau_libelle}</span>
                </div>
                <Badge className="bg-amber-100 text-amber-700 text-[9px]">{c.nb_metiers_associes} métiers</Badge>
              </button>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}


// ═══════════════════════════════════════════════════════════════════════════════
// Module 6: INTELLIGENCE TERRITORIALE
// ═══════════════════════════════════════════════════════════════════════════════
function TerritorialModule({ rncpStats, tensionCerts, onLoadTension, loading }) {
  const [territorialData, setTerritorialData] = useState(null);
  const [loadingTerr, setLoadingTerr] = useState(false);

  const loadTerritorialAnalysis = async () => {
    setLoadingTerr(true);
    try {
      // Load tension certs if not loaded yet
      if (!tensionCerts) onLoadTension();
      // Load stats by level for territorial insight
      const res = await axios.get(`${API}/referentiel/rncp/stats`);
      setTerritorialData(res.data);
    } catch { /* ignore */ }
    setLoadingTerr(false);
  };

  useEffect(() => {
    loadTerritorialAnalysis();
  }, []);

  const bassins = [
    { ville: "Strasbourg", dep: "67", desc: "Pôle métropolitain, numérique, santé, finance" },
    { ville: "Mulhouse", dep: "68", desc: "Industrie, automobile, chimie, textile" },
    { ville: "Colmar", dep: "68", desc: "Tourisme, viticulture, agroalimentaire" },
    { ville: "Haguenau", dep: "67", desc: "Industrie manufacturière, logistique" },
    { ville: "Metz", dep: "57", desc: "Services, numérique, tertiaire supérieur" },
    { ville: "Nancy", dep: "54", desc: "Recherche, santé, enseignement, BTP" },
  ];

  return (
    <div className="space-y-4" data-testid="opc-mod-territorial">
      <div className="bg-cyan-50 border border-cyan-200 rounded-lg p-3 text-xs text-cyan-700">
        <strong>Module 6 — Intelligence territoriale</strong> : Indicateurs par territoire, tensions de recrutement et besoins de formation à l'échelle du Grand Est.
      </div>

      {/* KPIs territoriaux */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <Card className="border-cyan-200"><CardContent className="p-3 text-center">
          <div className="text-2xl font-bold text-cyan-700">{rncpStats?.rncp_actives?.toLocaleString() || "—"}</div>
          <div className="text-[10px] text-slate-500">Certifications RNCP actives</div>
        </CardContent></Card>
        <Card className="border-cyan-200"><CardContent className="p-3 text-center">
          <div className="text-2xl font-bold text-cyan-700">{rncpStats?.rs_actives?.toLocaleString() || "—"}</div>
          <div className="text-[10px] text-slate-500">Certifications RS actives</div>
        </CardContent></Card>
        <Card className="border-cyan-200"><CardContent className="p-3 text-center">
          <div className="text-2xl font-bold text-cyan-700">{rncpStats?.blocs_competences?.toLocaleString() || "—"}</div>
          <div className="text-[10px] text-slate-500">Blocs de compétences</div>
        </CardContent></Card>
        <Card className="border-cyan-200"><CardContent className="p-3 text-center">
          <div className="text-2xl font-bold text-cyan-700">6</div>
          <div className="text-[10px] text-slate-500">Bassins d'emploi couverts</div>
        </CardContent></Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Bassins d'emploi */}
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm flex items-center gap-2"><MapPin className="w-4 h-4 text-cyan-600" />Bassins d'emploi — Grand Est</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {bassins.map((b, i) => (
              <div key={i} className="flex items-start gap-3 py-2 border-b border-slate-100 last:border-0">
                <div className="w-8 h-8 rounded-lg bg-cyan-100 flex items-center justify-center shrink-0">
                  <span className="text-[10px] font-bold text-cyan-700">{b.dep}</span>
                </div>
                <div className="flex-1">
                  <div className="text-sm font-semibold text-slate-700">{b.ville}</div>
                  <div className="text-[10px] text-slate-500">{b.desc}</div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Certifications en tension */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-600" />
              Certifications les plus transversales
            </CardTitle>
            <p className="text-[10px] text-slate-500 mt-0.5">Classées par nombre de codes ROME associés (proxy de demande)</p>
          </CardHeader>
          <CardContent>
            {!tensionCerts ? (
              <Button variant="outline" size="sm" onClick={onLoadTension} disabled={loading}>
                {loading ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : <RefreshCw className="w-4 h-4 mr-1" />}
                Charger le classement
              </Button>
            ) : (
              <div className="space-y-1.5">
                {(tensionCerts.certifications_en_tension || []).slice(0, 10).map((c, i) => (
                  <div key={i} className="p-2 bg-amber-50/50 rounded border border-amber-100 text-xs">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1">
                        <div className="font-semibold text-slate-700 leading-tight">{c.intitule}</div>
                        <div className="text-[10px] text-slate-500 mt-0.5 flex items-center gap-2">
                          <Badge variant="outline" className="text-[9px]">{c.code}</Badge>
                          {c.niveau_libelle && <span>{c.niveau_libelle}</span>}
                        </div>
                      </div>
                      <div className="text-right shrink-0">
                        <div className="text-sm font-bold text-amber-700">{c.nb_metiers_associes}</div>
                        <div className="text-[9px] text-slate-400">codes ROME</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Répartition par niveau */}
      {territorialData?.par_niveau && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2"><BarChart3 className="w-4 h-4 text-cyan-600" />Répartition des certifications actives par niveau de qualification</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {Object.entries(territorialData.par_niveau).sort((a,b) => b[1] - a[1]).map(([level, count]) => {
                const max = Math.max(...Object.values(territorialData.par_niveau));
                return (
                  <div key={level} className="flex items-center gap-3">
                    <span className="text-xs text-slate-600 w-40 text-right shrink-0">{level || "Non renseigné"}</span>
                    <div className="flex-1 bg-slate-100 rounded-full h-5 overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-cyan-500 to-teal-500 rounded-full flex items-center justify-end pr-2 transition-all" style={{ width: `${(count / max) * 100}%`, minWidth: "40px" }}>
                        <span className="text-[10px] font-bold text-white">{count}</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}


// ═══════════════════════════════════════════════════════════════════════════════
// Module 7: MOTEUR PRÉDICTIF
// ═══════════════════════════════════════════════════════════════════════════════
// ═══════════════════════════════════════════════════════════════════════════════
// Module 7: MOTEUR PRÉDICTIF + CARTOGRAPHIE EXHAUSTIVE
// ═══════════════════════════════════════════════════════════════════════════════

const ICON_MAP = {
  "shopping-cart": Target, "users": Building2, "globe": MapPin,
  "chart-bar": BarChart3, "briefcase": FileText, "cog": Layers,
  "lightbulb": Sparkles, "building": Building2, "truck": ArrowRightLeft,
  "graduation-cap": GraduationCap, "target": Target, "trending-up": TrendingUp,
};

function CartographieExhaustiveDisplay({ data }) {
  const [openCats, setOpenCats] = useState({});
  const toggleCat = (idx) => setOpenCats(prev => ({ ...prev, [idx]: !prev[idx] }));

  if (!data || !data.categories) return null;

  const catColors = [
    "border-blue-300 bg-blue-50/40", "border-emerald-300 bg-emerald-50/40",
    "border-violet-300 bg-violet-50/40", "border-amber-300 bg-amber-50/40",
    "border-rose-300 bg-rose-50/40", "border-cyan-300 bg-cyan-50/40",
    "border-indigo-300 bg-indigo-50/40", "border-teal-300 bg-teal-50/40",
    "border-orange-300 bg-orange-50/40", "border-pink-300 bg-pink-50/40",
  ];
  const catTextColors = [
    "text-blue-800", "text-emerald-800", "text-violet-800", "text-amber-800",
    "text-rose-800", "text-cyan-800", "text-indigo-800", "text-teal-800",
    "text-orange-800", "text-pink-800",
  ];
  const catBadgeColors = [
    "bg-blue-100 text-blue-700", "bg-emerald-100 text-emerald-700",
    "bg-violet-100 text-violet-700", "bg-amber-100 text-amber-700",
    "bg-rose-100 text-rose-700", "bg-cyan-100 text-cyan-700",
    "bg-indigo-100 text-indigo-700", "bg-teal-100 text-teal-700",
    "bg-orange-100 text-orange-700", "bg-pink-100 text-pink-700",
  ];

  return (
    <div className="space-y-4" data-testid="cartographie-exhaustive-results">
      {/* Header with stats */}
      <div className="flex items-center justify-between bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl px-5 py-4">
        <div>
          <h2 className="text-base font-bold">Cartographie exhaustive : {data.domaine}</h2>
          <p className="text-xs text-purple-200 mt-1 max-w-2xl">{data.synthese}</p>
        </div>
        <div className="text-right shrink-0 ml-4">
          <div className="text-3xl font-black">{data.total_metiers}</div>
          <div className="text-[10px] text-purple-200">métiers identifiés</div>
        </div>
      </div>

      {/* Source stats */}
      {data.source_stats && (
        <div className="flex gap-3 text-[10px]">
          <span className="bg-blue-50 text-blue-700 px-2 py-1 rounded-full border border-blue-200">{data.source_stats.rome_matches} fiches ROME</span>
          <span className="bg-violet-50 text-violet-700 px-2 py-1 rounded-full border border-violet-200">{data.source_stats.opc_matches} métiers OPC</span>
          <span className="bg-red-50 text-red-700 px-2 py-1 rounded-full border border-red-200">{data.source_stats.rncp_matches} certifications RNCP</span>
        </div>
      )}

      {/* Categories */}
      <div className="space-y-3">
        {data.categories.map((cat, ci) => {
          const isOpen = openCats[ci] !== false; // default open
          const CatIcon = ICON_MAP[cat.icone] || Target;
          const colorClass = catColors[ci % catColors.length];
          const textColor = catTextColors[ci % catTextColors.length];
          const badgeColor = catBadgeColors[ci % catBadgeColors.length];

          return (
            <div key={ci} className={`border rounded-xl overflow-hidden ${colorClass}`} data-testid={`carto-cat-${ci}`}>
              <button
                onClick={() => toggleCat(ci)}
                className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-white/30 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <CatIcon className={`w-5 h-5 ${textColor} shrink-0`} />
                  <div>
                    <span className={`font-bold text-sm ${textColor}`}>{cat.nom}</span>
                    {cat.description && <p className="text-[10px] text-slate-500 mt-0.5">{cat.description}</p>}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge className={`text-[10px] ${badgeColor}`}>{(cat.metiers || []).length} métiers</Badge>
                  <ChevronRight className={`w-4 h-4 text-slate-400 transition-transform ${isOpen ? "rotate-90" : ""}`} />
                </div>
              </button>
              {isOpen && (
                <div className="px-4 pb-3">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-1.5">
                    {(cat.metiers || []).map((m, mi) => {
                      const tensionColor = m.niveau_tension === "fort" ? "bg-red-100 text-red-700" : m.niveau_tension === "modéré" ? "bg-amber-100 text-amber-700" : "bg-slate-100 text-slate-600";
                      const TendIcon = m.tendance === "hausse" ? ArrowUpRight : m.tendance === "baisse" ? ArrowDownRight : Minus;
                      const tendColor = m.tendance === "hausse" ? "text-emerald-600" : m.tendance === "baisse" ? "text-red-500" : "text-slate-400";
                      return (
                        <div key={mi} className="flex items-center gap-2 bg-white/70 rounded-lg px-3 py-2 border border-white/80">
                          <TendIcon className={`w-4 h-4 ${tendColor} shrink-0`} />
                          <div className="flex-1 min-w-0">
                            <div className="text-xs font-semibold text-slate-800 truncate">{m.nom}</div>
                            <div className="flex items-center gap-1.5 mt-0.5">
                              {m.code_rome && m.code_rome !== "null" && <span className="text-[9px] font-mono text-slate-400">{m.code_rome}</span>}
                              {m.salaire_median && <span className="text-[9px] text-slate-500">{m.salaire_median}</span>}
                              {m.acces && <span className="text-[9px] text-slate-400">{m.acces}</span>}
                            </div>
                          </div>
                          <Badge className={`text-[8px] shrink-0 ${tensionColor}`}>{m.niveau_tension}</Badge>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Métiers émergents */}
      {data.metiers_emergents?.length > 0 && (
        <Card className="border-violet-200">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-violet-600" />
              Métiers émergents liés à « {data.domaine} »
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {data.metiers_emergents.map((m, i) => (
              <div key={i} className="flex items-center gap-3 py-2 border-b border-slate-100 last:border-0">
                <Zap className="w-4 h-4 text-amber-500 shrink-0" />
                <div className="flex-1">
                  <div className="text-sm font-semibold text-slate-800">{m.nom}</div>
                  <div className="text-[10px] text-slate-500">{m.raison}</div>
                </div>
                <Badge variant="outline" className="text-[9px]">{m.horizon}</Badge>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Certifications clés */}
      {data.certifications_cles?.length > 0 && (
        <Card className="border-red-200">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <GraduationCap className="w-4 h-4 text-red-600" />
              Certifications clés pour le domaine « {data.domaine} »
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-1.5">
            {data.certifications_cles.map((c, i) => (
              <div key={i} className="flex items-start gap-2 py-1.5 border-b border-slate-100 last:border-0">
                <Badge variant="outline" className="text-[9px] shrink-0 mt-0.5">{c.code}</Badge>
                <div className="flex-1">
                  <div className="text-xs font-semibold text-slate-700">{c.intitule}</div>
                  <div className="text-[10px] text-slate-500">{c.debouches}</div>
                </div>
                {c.niveau && <Badge className="bg-blue-100 text-blue-700 text-[9px] shrink-0">{c.niveau}</Badge>}
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function PredictifModule({ predictions, recommandation, cartographie, loading, metier, onRunPredictions, onRunRecommandation, onRunCartographie, onRunAnalyseComplete }) {
  return (
    <div className="space-y-4" data-testid="opc-mod-predictif">
      <div className="bg-purple-50 border border-purple-200 rounded-lg p-3 text-xs text-purple-700">
        <strong>Module 7 — Moteur prédictif</strong> : Génère des prévisions IA sur l'évolution des compétences, recommandations personnalisées et analyse complète multi-dimensions.
        {metier && <span className="font-bold ml-1">Contexte : {metier}</span>}
      </div>
      <div className="flex flex-wrap gap-2">
        <Button onClick={onRunCartographie} disabled={loading.cartographie} className="bg-purple-700 hover:bg-purple-800" data-testid="opc-run-cartographie">
          {loading.cartographie ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : <Map className="w-4 h-4 mr-1" />}
          {loading.cartographie ? "Cartographie en cours..." : "Cartographie exhaustive"}
        </Button>
        <Button onClick={onRunPredictions} disabled={loading.predict} className="bg-indigo-600 hover:bg-indigo-700" data-testid="opc-run-predictions">
          {loading.predict ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : <Brain className="w-4 h-4 mr-1" />}
          Prédictions globales
        </Button>
        <Button onClick={onRunRecommandation} disabled={loading.recommandation} className="bg-emerald-600 hover:bg-emerald-700" data-testid="opc-run-reco">
          {loading.recommandation ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : <Target className="w-4 h-4 mr-1" />}
          Recommandation personnalisée
        </Button>
        <Button onClick={onRunAnalyseComplete} disabled={loading["analyse-complete"]} className="bg-rose-600 hover:bg-rose-700" data-testid="opc-run-complete">
          {loading["analyse-complete"] ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : <Sparkles className="w-4 h-4 mr-1" />}
          Analyse complète
        </Button>
      </div>

      {/* Cartographie exhaustive */}
      <CartographieExhaustiveDisplay data={cartographie} />

      {predictions && (
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Synthèse prédictive</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            <p className="text-sm text-slate-700 bg-indigo-50 p-3 rounded-lg">{predictions.synthese}</p>
            {predictions.tendances_competences?.length > 0 && (
              <div>
                <h4 className="text-xs font-semibold text-slate-600 mb-2">Tendances des compétences</h4>
                {predictions.tendances_competences.map((t, i) => {
                  const isHausse = t.direction === "hausse";
                  const isBaisse = t.direction === "baisse";
                  const DirIcon = isHausse ? ArrowUpRight : isBaisse ? ArrowDownRight : Minus;
                  const dirColor = isHausse ? "text-emerald-600" : isBaisse ? "text-red-600" : "text-slate-400";
                  const bgColor = isHausse ? "bg-emerald-50" : isBaisse ? "bg-red-50" : "bg-slate-50";
                  return (
                    <div key={i} className={`flex items-start gap-3 py-2.5 px-2 rounded-lg ${bgColor} border-b border-white last:border-0`}>
                      <DirIcon className={`w-5 h-5 ${dirColor} shrink-0 mt-0.5`} />
                      <span className="text-sm font-medium text-slate-700 w-1/3 shrink-0">{t.competence}</span>
                      <span className="text-sm text-slate-500">{t.explication}</span>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {recommandation && recommandation.plan_action && (
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Recommandation personnalisée</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            <p className="text-sm text-slate-700 bg-emerald-50 p-3 rounded-lg">{recommandation.plan_action}</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {recommandation.metiers_accessibles?.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold text-slate-600 mb-1">Métiers accessibles</h4>
                  {recommandation.metiers_accessibles.map((m, i) => (
                    <div key={i} className="text-xs flex items-center justify-between py-1">
                      <span className="text-slate-700">{m.metier}</span>
                      <Progress value={m.adequation} className="w-16 h-1.5" />
                    </div>
                  ))}
                </div>
              )}
              {recommandation.competences_prioritaires?.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold text-slate-600 mb-1">Compétences prioritaires</h4>
                  {recommandation.competences_prioritaires.map((c, i) => (
                    <div key={i} className="text-xs flex items-center gap-1 py-1">
                      <Badge className={`text-[9px] ${c.urgence === "haute" ? "bg-red-100 text-red-700" : "bg-amber-100 text-amber-700"}`}>{c.urgence}</Badge>
                      <span className="text-slate-700">{c.competence}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
            {recommandation.certifications_conseillees?.length > 0 && (
              <div>
                <h4 className="text-xs font-semibold text-slate-600 mb-1 flex items-center gap-1"><GraduationCap className="w-3.5 h-3.5" />Certifications RNCP conseillées</h4>
                {recommandation.certifications_conseillees.map((c, i) => (
                  <div key={i} className="text-xs flex items-center gap-2 py-1.5 border-b border-slate-100 last:border-0">
                    <Badge variant="outline" className="text-[9px]">{c.code_rncp}</Badge>
                    <span className="font-medium text-slate-700">{c.intitule}</span>
                    <Badge className="bg-blue-100 text-blue-700 text-[9px]">{c.niveau}</Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
