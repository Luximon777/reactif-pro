import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Target, Sparkles, ChevronDown, ChevronUp, Search,
  AlertTriangle, ShieldAlert, CheckCircle2, Star, MapPin,
  Filter, RotateCcw, Heart, Shield, Accessibility, Send, ExternalLink, FileEdit
} from "lucide-react";
import { toast } from "sonner";

const PRIORITY_OPTIONS = [
  { value: "1", label: "1 - Faible", color: "bg-slate-100 text-slate-600" },
  { value: "2", label: "2 - Mineure", color: "bg-blue-100 text-blue-600" },
  { value: "3", label: "3 - Moyenne", color: "bg-amber-100 text-amber-600" },
  { value: "4", label: "4 - Importante", color: "bg-orange-100 text-orange-700" },
  { value: "5", label: "5 - Bloquante", color: "bg-red-100 text-red-700" },
];

const CONTRAT_OPTIONS = ["CDI", "CDD", "Mission", "Freelance", "Alternance"];
const TEMPS_OPTIONS = ["temps plein", "temps partiel", "indifférent"];
const TELETRAVAIL_OPTIONS = [
  { value: "non prioritaire", label: "Non prioritaire" },
  { value: "souhaité", label: "Souhaité" },
  { value: "nécessaire", label: "Nécessaire" },
];
const AMENAGEMENT_OPTIONS = [
  { value: "aucun", label: "Aucun" },
  { value: "souhaitable", label: "Souhaitable" },
  { value: "nécessaire", label: "Nécessaire" },
  { value: "a_evaluer", label: "A évaluer avec l'employeur" },
];
const RQTH_STATUS_OPTIONS = [
  { value: "ne_souhaite_pas_repondre", label: "Ne souhaite pas répondre" },
  { value: "rqth", label: "RQTH (Reconnaissance)" },
  { value: "eqth", label: "EQTH (Équivalence)" },
  { value: "en_cours", label: "Demande en cours" },
  { value: "aucun", label: "Aucun" },
];
const DISCLOSURE_OPTIONS = [
  { value: "non", label: "Non" },
  { value: "oui", label: "Oui" },
  { value: "a_discuter", label: "A discuter" },
];

const PrioritySelect = ({ value, onChange }) => (
  <Select value={String(value || 3)} onValueChange={(v) => onChange(parseInt(v))}>
    <SelectTrigger className="w-[130px] h-8 text-xs" data-testid="priority-select">
      <SelectValue />
    </SelectTrigger>
    <SelectContent>
      {PRIORITY_OPTIONS.map((opt) => (
        <SelectItem key={opt.value} value={opt.value}>
          <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${opt.color}`}>
            {opt.label}
          </span>
        </SelectItem>
      ))}
    </SelectContent>
  </Select>
);

const FilterRow = ({ label, children, priority, onPriorityChange, showPriority = true }) => (
  <div className="flex items-start gap-3 py-3 border-b border-slate-100 last:border-0">
    <div className="flex-1 min-w-0">
      <Label className="text-xs font-medium text-slate-700 mb-1.5 block">{label}</Label>
      {children}
    </div>
    {showPriority && (
      <div className="pt-5">
        <PrioritySelect value={priority} onChange={onPriorityChange} />
      </div>
    )}
  </div>
);

const DEFAULT_FILTERS = {
  metier: { value: "", priority: 3 },
  secteur: { value: "", priority: 3 },
  contrat: { value: [], priority: 3 },
  temps_travail: { value: "indifférent", priority: 2 },
  trajet_max_minutes: { value: 60, priority: 3 },
  teletravail: { value: "non prioritaire", priority: 2 },
  amenagement_poste: { value: "aucun", priority: 2 },
  rqth_eqth: { status: "ne_souhaite_pas_repondre", disclosure: "non" },
  ciblage_inclusif: { value: false, priority: 3 },
  accessibilite_handicap: { value: false, priority: 4 },
  restrictions: {
    port_charges_impossible: false,
    station_debout_prolongee_limitee: false,
    travail_nuit_impossible: false,
    environnement_calme_recherche: false,
    horaires_stables_recherches: false,
    accessibilite_necessaire: false,
    deplacements_frequents_difficiles: false,
    cadence_elevee_difficile: false,
    priority: 5,
  },
};

const JobMatchingSection = ({ token }) => {
  const [matching, setMatching] = useState(null);
  const [loadingMatch, setLoadingMatch] = useState(false);
  const [filtersOpen, setFiltersOpen] = useState(false);
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  const [hasSearched, setHasSearched] = useState(false);
  const [loadingPrefs, setLoadingPrefs] = useState(true);
  const [expandedCard, setExpandedCard] = useState(null);
  const [appliedJobs, setAppliedJobs] = useState(new Set());
  const [applyingJob, setApplyingJob] = useState(null);

  useEffect(() => {
    if (token) {
      loadPreferences();
      loadApplications();
    }
  }, [token]);

  const loadApplications = async () => {
    try {
      const res = await axios.get(`${API}/jobs/applications?token=${token}`);
      const titles = new Set(res.data.map((a) => a.job_title));
      setAppliedJobs(titles);
    } catch (e) {
      console.error("Load applications error:", e);
    }
  };

  const handleApply = async (match) => {
    const title = match.titre || match.title || "";
    if (appliedJobs.has(title)) return;
    setApplyingJob(title);
    try {
      const res = await axios.post(`${API}/jobs/apply?token=${token}`, {
        job_title: title,
        job_data: {
          secteur: match.secteur || "",
          type_contrat: match.type_contrat || "",
          localisation: match.localisation || "",
          entreprise_type: match.entreprise_type || "",
          matching_score: match.matching_score || 0,
        },
      });
      if (res.data.already_applied) {
        toast.info("Vous avez déjà postulé à cette offre");
      } else {
        toast.success("Candidature enregistrée !");
      }
      setAppliedJobs((prev) => new Set([...prev, title]));
    } catch (e) {
      console.error("Apply error:", e);
      toast.error("Erreur lors de la candidature");
    }
    setApplyingJob(null);
  };

  const loadPreferences = async () => {
    setLoadingPrefs(true);
    try {
      const res = await axios.get(`${API}/jobs/matching/preferences?token=${token}`);
      if (res.data.has_preferences && res.data.filters) {
        const saved = res.data.filters;
        setFilters((prev) => ({
          ...prev,
          metier: saved.metier || prev.metier,
          secteur: saved.secteur || prev.secteur,
          contrat: saved.contrat || prev.contrat,
          temps_travail: saved.temps_travail || prev.temps_travail,
          trajet_max_minutes: saved.trajet_max_minutes || prev.trajet_max_minutes,
          teletravail: saved.teletravail || prev.teletravail,
          amenagement_poste: saved.amenagement_poste || prev.amenagement_poste,
          rqth_eqth: saved.rqth_eqth || prev.rqth_eqth,
          ciblage_inclusif: saved.ciblage_employeurs_inclusifs
            ? { value: saved.ciblage_employeurs_inclusifs.value, priority: saved.ciblage_employeurs_inclusifs.priority }
            : prev.ciblage_inclusif,
          accessibilite_handicap: saved.accessibilite_metier_handicap
            ? { value: saved.accessibilite_metier_handicap.value, priority: saved.accessibilite_metier_handicap.priority }
            : prev.accessibilite_handicap,
          restrictions: saved.restrictions_fonctionnelles
            ? { ...prev.restrictions, ...saved.restrictions_fonctionnelles.value, priority: saved.restrictions_fonctionnelles.priority || 5 }
            : prev.restrictions,
        }));
        loadInitialMatching();
      } else {
        loadInitialMatching();
      }
    } catch {
      loadInitialMatching();
    }
    setLoadingPrefs(false);
  };

  const loadInitialMatching = async () => {
    setLoadingMatch(true);
    try {
      const res = await axios.get(`${API}/jobs/matching?token=${token}`);
      setMatching(res.data);
    } catch (e) {
      console.error("Job matching error:", e);
    }
    setLoadingMatch(false);
  };

  const buildSearchPayload = () => {
    const payload = {};
    if (filters.metier.value) {
      payload.metier = { value: filters.metier.value.split(",").map((s) => s.trim()).filter(Boolean), priority: filters.metier.priority };
    }
    if (filters.secteur.value) {
      payload.secteur = { value: filters.secteur.value.split(",").map((s) => s.trim()).filter(Boolean), priority: filters.secteur.priority };
    }
    if (filters.contrat.value?.length > 0) {
      payload.contrat = { value: filters.contrat.value, priority: filters.contrat.priority };
    }
    if (filters.temps_travail.value && filters.temps_travail.value !== "indifférent") {
      payload.temps_travail = { value: filters.temps_travail.value, priority: filters.temps_travail.priority };
    }
    if (filters.trajet_max_minutes.value) {
      payload.trajet_max_minutes = { value: parseInt(filters.trajet_max_minutes.value) || 60, priority: filters.trajet_max_minutes.priority };
    }
    if (filters.teletravail.value && filters.teletravail.value !== "non prioritaire") {
      payload.teletravail = { value: filters.teletravail.value, priority: filters.teletravail.priority };
    }
    if (filters.amenagement_poste.value && filters.amenagement_poste.value !== "aucun") {
      payload.amenagement_poste = { value: filters.amenagement_poste.value, priority: filters.amenagement_poste.priority };
    }
    // RQTH/EQTH context
    if (filters.rqth_eqth.status !== "ne_souhaite_pas_repondre") {
      payload.rqth_eqth = { status: filters.rqth_eqth.status, disclosure: filters.rqth_eqth.disclosure, priority: 1 };
    }
    // Ciblage employeurs inclusifs
    if (filters.ciblage_inclusif.value) {
      payload.ciblage_employeurs_inclusifs = { value: true, priority: filters.ciblage_inclusif.priority };
    }
    // Accessibilité métier handicap
    if (filters.accessibilite_handicap.value) {
      payload.accessibilite_metier_handicap = { value: true, priority: filters.accessibilite_handicap.priority };
    }
    // Restrictions
    const restrictions = {};
    const restrictionKeys = [
      "port_charges_impossible", "station_debout_prolongee_limitee", "travail_nuit_impossible",
      "environnement_calme_recherche", "horaires_stables_recherches", "accessibilite_necessaire",
      "deplacements_frequents_difficiles", "cadence_elevee_difficile"
    ];
    for (const key of restrictionKeys) {
      if (filters.restrictions[key]) restrictions[key] = true;
    }
    if (Object.keys(restrictions).length > 0) {
      payload.restrictions_fonctionnelles = { value: restrictions, priority: filters.restrictions.priority };
    }
    return payload;
  };

  const handleSearch = async () => {
    setLoadingMatch(true);
    setHasSearched(true);
    try {
      const payload = buildSearchPayload();
      const res = await axios.post(`${API}/jobs/matching/search?token=${token}`, payload);
      setMatching(res.data);
      setFiltersOpen(false);
      toast.success("Recherche effectuée avec scoring avancé");
    } catch (e) {
      console.error("Search error:", e);
      toast.error("Erreur lors de la recherche");
    }
    setLoadingMatch(false);
  };

  const handleReset = () => {
    setFilters(DEFAULT_FILTERS);
    setHasSearched(false);
    toast.info("Filtres réinitialisés");
  };

  const updateFilter = (key, field, value) => {
    setFilters((prev) => ({ ...prev, [key]: { ...prev[key], [field]: value } }));
  };

  const toggleContrat = (type) => {
    setFilters((prev) => {
      const current = prev.contrat.value || [];
      const updated = current.includes(type) ? current.filter((c) => c !== type) : [...current, type];
      return { ...prev, contrat: { ...prev.contrat, value: updated } };
    });
  };

  const toggleRestriction = (key) => {
    setFilters((prev) => ({
      ...prev,
      restrictions: { ...prev.restrictions, [key]: !prev.restrictions[key] },
    }));
  };

  const getScoreColor = (score) => {
    if (score >= 80) return { bg: "bg-emerald-100", text: "text-emerald-700", ring: "ring-emerald-200", bar: "bg-emerald-500" };
    if (score >= 60) return { bg: "bg-blue-100", text: "text-blue-700", ring: "ring-blue-200", bar: "bg-blue-500" };
    if (score >= 40) return { bg: "bg-amber-100", text: "text-amber-700", ring: "ring-amber-200", bar: "bg-amber-500" };
    return { bg: "bg-slate-100", text: "text-slate-600", ring: "ring-slate-200", bar: "bg-slate-400" };
  };

  const getStatutBadge = (statut) => {
    const config = {
      "Excellent match": "bg-emerald-100 text-emerald-700 border-emerald-200",
      "Match pertinent": "bg-blue-100 text-blue-700 border-blue-200",
      "Match moyen": "bg-amber-100 text-amber-700 border-amber-200",
      "Faible compatibilité": "bg-slate-100 text-slate-600 border-slate-200",
      "Incompatible": "bg-red-100 text-red-700 border-red-200",
    };
    return config[statut] || "bg-slate-100 text-slate-600 border-slate-200";
  };

  const getInclusionLabel = (score) => {
    if (score >= 70) return { text: "Très inclusif", color: "text-emerald-600 bg-emerald-50" };
    if (score >= 40) return { text: "Partiellement inclusif", color: "text-amber-600 bg-amber-50" };
    return { text: "Non renseigné", color: "text-slate-500 bg-slate-50" };
  };

  if (loadingPrefs) {
    return (
      <div className="flex items-center justify-center h-40">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in" data-testid="jobs-section">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900" style={{ fontFamily: "Outfit, sans-serif" }}>
            Job Matching
          </h1>
          <p className="text-slate-600 mt-1">
            Offres analysées et scorées selon vos critères — RQTH/EQTH jamais discriminant
          </p>
        </div>
        <Button
          variant={filtersOpen ? "default" : "outline"}
          onClick={() => setFiltersOpen(!filtersOpen)}
          className={filtersOpen ? "bg-[#1e3a5f] hover:bg-[#2d4a6f]" : ""}
          data-testid="toggle-filters-btn"
        >
          <Filter className="w-4 h-4 mr-2" />
          {filtersOpen ? "Masquer les filtres" : "Filtres de recherche"}
          {filtersOpen ? <ChevronUp className="w-4 h-4 ml-1" /> : <ChevronDown className="w-4 h-4 ml-1" />}
        </Button>
      </div>

      {/* Filter Panel */}
      {filtersOpen && (
        <Card className="border-[#1e3a5f]/20 shadow-lg animate-fade-in" data-testid="filter-panel">
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center gap-2">
              <Target className="w-4 h-4 text-[#1e3a5f]" />
              Critères de recherche
              <span className="text-[10px] text-slate-400 font-normal ml-2">
                Priorité 5 = critère bloquant
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-0">
            {/* Métier */}
            <FilterRow label="Métier(s) visé(s)" priority={filters.metier.priority} onPriorityChange={(v) => updateFilter("metier", "priority", v)}>
              <Input placeholder="Ex: Conseiller insertion, Formateur (séparés par virgule)" value={filters.metier.value}
                onChange={(e) => updateFilter("metier", "value", e.target.value)} className="h-9 text-sm" data-testid="filter-metier" />
            </FilterRow>

            {/* Secteur */}
            <FilterRow label="Secteur(s) d'activité" priority={filters.secteur.priority} onPriorityChange={(v) => updateFilter("secteur", "priority", v)}>
              <Input placeholder="Ex: Formation, Insertion, Social (séparés par virgule)" value={filters.secteur.value}
                onChange={(e) => updateFilter("secteur", "value", e.target.value)} className="h-9 text-sm" data-testid="filter-secteur" />
            </FilterRow>

            {/* Contrat */}
            <FilterRow label="Type(s) de contrat" priority={filters.contrat.priority} onPriorityChange={(v) => updateFilter("contrat", "priority", v)}>
              <div className="flex flex-wrap gap-2">
                {CONTRAT_OPTIONS.map((type) => (
                  <button key={type} onClick={() => toggleContrat(type)} data-testid={`filter-contrat-${type.toLowerCase()}`}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                      (filters.contrat.value || []).includes(type) ? "bg-[#1e3a5f] text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                    }`}>{type}</button>
                ))}
              </div>
            </FilterRow>

            {/* Temps */}
            <FilterRow label="Temps de travail" priority={filters.temps_travail.priority} onPriorityChange={(v) => updateFilter("temps_travail", "priority", v)}>
              <div className="flex gap-2">
                {TEMPS_OPTIONS.map((opt) => (
                  <button key={opt} onClick={() => updateFilter("temps_travail", "value", opt)} data-testid={`filter-temps-${opt.replace(/\s/g, "-")}`}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                      filters.temps_travail.value === opt ? "bg-[#1e3a5f] text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                    }`}>{opt.charAt(0).toUpperCase() + opt.slice(1)}</button>
                ))}
              </div>
            </FilterRow>

            {/* Mobilité */}
            <FilterRow label="Trajet maximum (minutes)" priority={filters.trajet_max_minutes.priority} onPriorityChange={(v) => updateFilter("trajet_max_minutes", "priority", v)}>
              <div className="flex items-center gap-3">
                <Input type="number" min={5} max={180} value={filters.trajet_max_minutes.value}
                  onChange={(e) => updateFilter("trajet_max_minutes", "value", e.target.value)} className="h-9 text-sm w-24" data-testid="filter-trajet" />
                <span className="text-xs text-slate-500">min</span>
                <input type="range" min={5} max={120} value={filters.trajet_max_minutes.value}
                  onChange={(e) => updateFilter("trajet_max_minutes", "value", e.target.value)} className="flex-1 accent-[#1e3a5f]" />
              </div>
            </FilterRow>

            {/* Télétravail */}
            <FilterRow label="Télétravail" priority={filters.teletravail.priority} onPriorityChange={(v) => updateFilter("teletravail", "priority", v)}>
              <div className="flex gap-2">
                {TELETRAVAIL_OPTIONS.map((opt) => (
                  <button key={opt.value} onClick={() => updateFilter("teletravail", "value", opt.value)} data-testid={`filter-teletravail-${opt.value.replace(/\s/g, "-")}`}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                      filters.teletravail.value === opt.value ? "bg-[#1e3a5f] text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                    }`}>{opt.label}</button>
                ))}
              </div>
            </FilterRow>

            {/* SECTION RQTH / EQTH */}
            <div className="pt-4 pb-2">
              <div className="flex items-center gap-2 mb-1">
                <Shield className="w-4 h-4 text-violet-600" />
                <span className="text-sm font-semibold text-slate-800">Situation de handicap (contexte)</span>
              </div>
              <p className="text-[10px] text-slate-500 mb-2">
                Ces informations sont contextuelles et ne sont <span className="font-semibold">jamais utilisées comme critère discriminant</span>.
                Elles permettent d'affiner la compatibilité fonctionnelle et de cibler les employeurs inclusifs.
              </p>
            </div>

            {/* RQTH Status */}
            <FilterRow label="Statut RQTH / EQTH" showPriority={false}>
              <div className="flex flex-wrap gap-2">
                {RQTH_STATUS_OPTIONS.map((opt) => (
                  <button key={opt.value} onClick={() => setFilters(prev => ({ ...prev, rqth_eqth: { ...prev.rqth_eqth, status: opt.value } }))}
                    data-testid={`filter-rqth-${opt.value}`}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                      filters.rqth_eqth.status === opt.value ? "bg-violet-600 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                    }`}>{opt.label}</button>
                ))}
              </div>
            </FilterRow>

            {/* Disclosure */}
            {filters.rqth_eqth.status !== "ne_souhaite_pas_repondre" && filters.rqth_eqth.status !== "aucun" && (
              <FilterRow label="Souhaitez-vous le mentionner à l'employeur ?" showPriority={false}>
                <div className="flex gap-2">
                  {DISCLOSURE_OPTIONS.map((opt) => (
                    <button key={opt.value} onClick={() => setFilters(prev => ({ ...prev, rqth_eqth: { ...prev.rqth_eqth, disclosure: opt.value } }))}
                      data-testid={`filter-disclosure-${opt.value}`}
                      className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                        filters.rqth_eqth.disclosure === opt.value ? "bg-violet-600 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                      }`}>{opt.label}</button>
                  ))}
                </div>
              </FilterRow>
            )}

            {/* Aménagement */}
            <FilterRow label="Aménagement de poste" priority={filters.amenagement_poste.priority} onPriorityChange={(v) => updateFilter("amenagement_poste", "priority", v)}>
              <div className="flex flex-wrap gap-2">
                {AMENAGEMENT_OPTIONS.map((opt) => (
                  <button key={opt.value} onClick={() => updateFilter("amenagement_poste", "value", opt.value)}
                    data-testid={`filter-amenagement-${opt.value.replace(/\s/g, "-")}`}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                      filters.amenagement_poste.value === opt.value ? "bg-[#1e3a5f] text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                    }`}>{opt.label}</button>
                ))}
              </div>
            </FilterRow>

            {/* Restrictions fonctionnelles */}
            <FilterRow label="Restrictions fonctionnelles" priority={filters.restrictions.priority}
              onPriorityChange={(v) => setFilters((prev) => ({ ...prev, restrictions: { ...prev.restrictions, priority: v } }))}>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {[
                  { key: "port_charges_impossible", label: "Port de charges impossible" },
                  { key: "station_debout_prolongee_limitee", label: "Station debout prolongée limitée" },
                  { key: "travail_nuit_impossible", label: "Travail de nuit impossible" },
                  { key: "environnement_calme_recherche", label: "Environnement calme recherché" },
                  { key: "horaires_stables_recherches", label: "Horaires stables recherchés" },
                  { key: "accessibilite_necessaire", label: "Accessibilité nécessaire" },
                  { key: "deplacements_frequents_difficiles", label: "Déplacements fréquents difficiles" },
                  { key: "cadence_elevee_difficile", label: "Cadence élevée difficile" },
                ].map((item) => (
                  <label key={item.key} className={`flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition-all ${
                    filters.restrictions[item.key] ? "bg-red-50 border border-red-200" : "bg-slate-50 border border-slate-200 hover:bg-slate-100"
                  }`}>
                    <input type="checkbox" checked={filters.restrictions[item.key]} onChange={() => toggleRestriction(item.key)}
                      className="accent-red-600" data-testid={`filter-restriction-${item.key}`} />
                    <span className="text-xs text-slate-700">{item.label}</span>
                  </label>
                ))}
              </div>
            </FilterRow>

            {/* Ciblage employeurs inclusifs */}
            <FilterRow label="Cibler les employeurs inclusifs" priority={filters.ciblage_inclusif.priority}
              onPriorityChange={(v) => updateFilter("ciblage_inclusif", "priority", v)}>
              <label className={`flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition-all w-fit ${
                filters.ciblage_inclusif.value ? "bg-violet-50 border border-violet-200" : "bg-slate-50 border border-slate-200 hover:bg-slate-100"
              }`}>
                <input type="checkbox" checked={filters.ciblage_inclusif.value}
                  onChange={() => setFilters(prev => ({ ...prev, ciblage_inclusif: { ...prev.ciblage_inclusif, value: !prev.ciblage_inclusif.value } }))}
                  className="accent-violet-600" data-testid="filter-ciblage-inclusif" />
                <Heart className="w-3 h-3 text-violet-500" />
                <span className="text-xs text-slate-700">Privilégier les entreprises engagées (Cap Emploi, référent handicap, etc.)</span>
              </label>
            </FilterRow>

            {/* Accessibilité métier handicap */}
            <FilterRow label="Accessibilité du poste" priority={filters.accessibilite_handicap.priority}
              onPriorityChange={(v) => updateFilter("accessibilite_handicap", "priority", v)}>
              <label className={`flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition-all w-fit ${
                filters.accessibilite_handicap.value ? "bg-blue-50 border border-blue-200" : "bg-slate-50 border border-slate-200 hover:bg-slate-100"
              }`}>
                <input type="checkbox" checked={filters.accessibilite_handicap.value}
                  onChange={() => setFilters(prev => ({ ...prev, accessibilite_handicap: { ...prev.accessibilite_handicap, value: !prev.accessibilite_handicap.value } }))}
                  className="accent-blue-600" data-testid="filter-accessibilite-handicap" />
                <Accessibility className="w-3 h-3 text-blue-500" />
                <span className="text-xs text-slate-700">Vérifier l'accessibilité et l'adaptabilité du poste</span>
              </label>
            </FilterRow>

            {/* Actions */}
            <div className="flex items-center justify-between pt-4">
              <Button variant="ghost" size="sm" onClick={handleReset} data-testid="reset-filters-btn">
                <RotateCcw className="w-3 h-3 mr-1" /> Réinitialiser
              </Button>
              <Button onClick={handleSearch} disabled={loadingMatch} className="bg-[#1e3a5f] hover:bg-[#2d4a6f]" data-testid="search-btn">
                {loadingMatch ? (
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
                ) : (
                  <Search className="w-4 h-4 mr-2" />
                )}
                Rechercher avec scoring
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Loading */}
      {loadingMatch && (
        <div className="flex items-center gap-3 p-6 bg-blue-50 rounded-xl border border-blue-100" data-testid="loading-indicator">
          <div className="w-6 h-6 border-2 border-blue-300 border-t-blue-600 rounded-full animate-spin" />
          <span className="text-sm text-blue-700">
            {hasSearched ? "Recherche et scoring de vos critères en cours..." : "Analyse de votre profil et recherche d'offres compatibles..."}
          </span>
        </div>
      )}

      {/* No data */}
      {!loadingMatch && matching && !matching.has_data && (
        <Card className="border-dashed border-2 border-slate-200 bg-slate-50/50">
          <CardContent className="p-6 text-center">
            <Target className="w-10 h-10 text-slate-300 mx-auto mb-3" />
            <h3 className="font-semibold text-slate-700">Analysez votre CV pour activer le Job Matching</h3>
            <p className="text-sm text-slate-500 mt-1">L'IA sélectionnera des offres d'emploi pertinentes selon votre profil</p>
          </CardContent>
        </Card>
      )}

      {/* Profile Banner */}
      {!loadingMatch && matching?.has_data && matching.profile_summary && (
        <Card className="bg-gradient-to-r from-[#1e3a5f] to-[#2d5a8f] border-0" data-testid="matching-profile-banner">
          <CardContent className="p-4">
            <div className="flex flex-col sm:flex-row sm:items-center gap-3">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-white/20 flex items-center justify-center">
                  <Target className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-white">{matching.profile_summary.titre || "Profil analysé"}</h4>
                  <p className="text-[11px] text-blue-100">{matching.profile_summary.skills_count} compétences analysées</p>
                </div>
              </div>
              <div className="flex gap-2 sm:ml-auto flex-wrap">
                {matching.profile_summary.has_optimized_cv && <Badge className="bg-white/15 text-white text-[10px]">CV optimisé</Badge>}
                {matching.profile_summary.has_career_project && <Badge className="bg-white/15 text-white text-[10px]">Projet pro défini</Badge>}
                {matching.has_filters && <Badge className="bg-amber-400/25 text-amber-200 text-[10px]">Scoring avancé actif</Badge>}
                <Badge className="bg-emerald-400/20 text-emerald-200 text-[10px]">{matching.matches?.length || 0} offres trouvées</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Results */}
      {!loadingMatch && matching?.matches?.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4" data-testid="results-grid">
          {matching.matches.map((match, idx) => {
            const sc = getScoreColor(match.matching_score);
            const scoring = match.scoring;
            const isExpanded = expandedCard === idx;
            const inclusionScore = scoring?.score_inclusion;
            const inclusionInfo = inclusionScore !== undefined ? getInclusionLabel(inclusionScore) : null;

            return (
              <Card key={idx} className={`group transition-all duration-200 ${
                scoring?.statut === "Incompatible" ? "border-red-200 bg-slate-50/50"
                  : match.matching_score >= 80 ? "ring-2 " + sc.ring : ""
              }`} data-testid={`job-match-card-${idx}`}>
                <CardContent className="p-5">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1 min-w-0">
                      {(() => {
                        const searchQuery = [match.titre, match.localisation || match.secteur, "offre emploi"]
                          .filter(Boolean).join(" ");
                        const searchUrl = match.url_offre || `https://www.google.com/search?q=${encodeURIComponent(searchQuery)}`;
                        return (
                          <a href={searchUrl} target="_blank" rel="noopener noreferrer"
                            className="font-semibold text-slate-900 hover:text-blue-600 underline-offset-2 hover:underline transition-colors flex items-center gap-1.5 group/link"
                            data-testid={`job-title-link-${idx}`}>
                            {match.titre}
                            <ExternalLink className="w-3.5 h-3.5 text-slate-400 group-hover/link:text-blue-500 transition-colors shrink-0" />
                          </a>
                        );
                      })()}
                      <div className="flex items-center gap-2 mt-1 flex-wrap">
                        {match.entreprise_type && <span className="text-xs text-slate-500">{match.entreprise_type}</span>}
                        <Badge variant="outline" className="text-[10px]">{match.type_contrat}</Badge>
                        <span className="text-xs text-slate-400">{match.secteur}</span>
                      </div>
                    </div>
                    <div className={`flex flex-col items-center ml-3 px-3 py-2 rounded-xl ${sc.bg}`} data-testid="matching-score">
                      <span className={`text-2xl font-bold ${sc.text}`}>{match.matching_score}%</span>
                      <span className={`text-[10px] ${sc.text}`}>match</span>
                    </div>
                  </div>

                  {/* Status + Inclusion badges */}
                  <div className="flex flex-wrap gap-1.5 mb-2">
                    {scoring?.statut && (
                      <Badge className={`text-[10px] border ${getStatutBadge(scoring.statut)}`} data-testid="statut-badge">
                        {scoring.statut === "Incompatible" && <ShieldAlert className="w-3 h-3 mr-0.5" />}
                        {scoring.statut === "Excellent match" && <Star className="w-3 h-3 mr-0.5" />}
                        {scoring.statut}
                      </Badge>
                    )}
                    {inclusionInfo && inclusionScore > 0 && (
                      <Badge className={`text-[10px] border ${inclusionInfo.color}`} data-testid="inclusion-badge">
                        <Heart className="w-3 h-3 mr-0.5" /> Inclusion {inclusionScore}% — {inclusionInfo.text}
                      </Badge>
                    )}
                  </div>

                  {/* Description */}
                  <p className="text-xs text-slate-600 mb-3">{match.description}</p>

                  {/* Score bar */}
                  <div className="mb-3">
                    <div className="h-2 rounded-full bg-slate-100 overflow-hidden">
                      <div className={`h-full rounded-full ${sc.bar} transition-all duration-500`} style={{ width: `${match.matching_score}%` }} />
                    </div>
                    {scoring?.score_detail && (
                      <p className="text-[10px] text-slate-400 mt-1">Score : {scoring.score_detail.obtenu} / {scoring.score_detail.maximum} points</p>
                    )}
                  </div>

                  {/* Blocages */}
                  {scoring?.blocages?.length > 0 && (
                    <div className="space-y-1 mb-2">
                      {scoring.blocages.map((b, i) => (
                        <div key={i} className="flex items-start gap-1.5 p-1.5 bg-red-50 rounded border border-red-100">
                          <ShieldAlert className="w-3 h-3 text-red-600 mt-0.5 shrink-0" />
                          <div>
                            <span className="text-[10px] font-medium text-red-700">{b.critere}</span>
                            <span className="text-[10px] text-red-600 ml-1">{b.raison}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Vigilances */}
                  {scoring?.vigilances?.length > 0 && (
                    <div className="space-y-1 mb-2">
                      {scoring.vigilances.map((v, i) => (
                        <div key={i} className="flex items-start gap-1.5 p-1.5 bg-amber-50 rounded border border-amber-100">
                          <AlertTriangle className="w-3 h-3 text-amber-600 mt-0.5 shrink-0" />
                          <div>
                            <span className="text-[10px] font-medium text-amber-700">{v.critere}</span>
                            <span className="text-[10px] text-amber-600 ml-1">{v.message}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Points forts */}
                  {scoring?.points_forts?.length > 0 && !isExpanded && (
                    <div className="flex flex-wrap gap-1 mb-2">
                      {scoring.points_forts.slice(0, 3).map((p, i) => (
                        <Badge key={i} className="text-[10px] bg-emerald-50 text-emerald-700 border border-emerald-200">
                          <CheckCircle2 className="w-2.5 h-2.5 mr-0.5" />{p.critere}
                        </Badge>
                      ))}
                    </div>
                  )}

                  {/* AI explanation (non-scored) */}
                  {!scoring && match.pourquoi_ce_match && (
                    <div className="p-2 bg-blue-50 rounded-lg mb-3 border border-blue-100">
                      <p className="text-[11px] text-blue-700"><Sparkles className="w-3 h-3 inline mr-1" />{match.pourquoi_ce_match}</p>
                    </div>
                  )}

                  {/* Skills */}
                  <div className="flex flex-wrap gap-1 mb-2">
                    {(match.competences_matchees || []).slice(0, 4).map((c, i) => (
                      <Badge key={i} className="text-[10px] bg-emerald-50 text-emerald-700 border border-emerald-200">{c}</Badge>
                    ))}
                  </div>

                  {/* Meta info */}
                  <div className="flex items-center justify-between text-[10px] text-slate-400 mt-2">
                    {match.localisation && <span className="flex items-center gap-0.5"><MapPin className="w-3 h-3" />{match.localisation}</span>}
                    {match.salaire_indicatif && <span className="font-medium text-slate-600">{match.salaire_indicatif}</span>}
                  </div>

                  {/* Expand for details */}
                  {scoring && (
                    <button onClick={() => setExpandedCard(isExpanded ? null : idx)} data-testid={`expand-details-${idx}`}
                      className="w-full mt-3 py-1.5 text-[11px] text-[#1e3a5f] hover:bg-slate-50 rounded-lg transition-colors flex items-center justify-center gap-1">
                      {isExpanded ? <><ChevronUp className="w-3 h-3" /> Masquer le détail</> : <><ChevronDown className="w-3 h-3" /> Voir le détail du scoring</>}
                    </button>
                  )}

                  {/* Expanded detail */}
                  {isExpanded && scoring?.evaluations && (
                    <div className="mt-3 pt-3 border-t border-slate-100 space-y-2" data-testid="scoring-detail">
                      {scoring.evaluations.map((ev, i) => (
                        <div key={i} className="flex items-center gap-2 text-[11px]">
                          <div className="w-28 truncate font-medium text-slate-600">{ev.label}</div>
                          <div className="flex-1 h-1.5 rounded-full bg-slate-100 overflow-hidden">
                            <div className={`h-full rounded-full transition-all ${
                              ev.compatibility === 1 ? "bg-emerald-500" : ev.compatibility > 0 ? "bg-amber-400" : "bg-red-400"
                            }`} style={{ width: `${ev.compatibility * 100}%` }} />
                          </div>
                          <span className="w-10 text-right text-slate-500">{Math.round(ev.compatibility * 100)}%</span>
                          <Badge className={`text-[9px] w-5 h-5 flex items-center justify-center p-0 ${
                            PRIORITY_OPTIONS.find((p) => p.value === String(ev.priority))?.color || ""
                          }`}>{ev.priority}</Badge>
                        </div>
                      ))}
                      {/* Inclusion score detail */}
                      {scoring.score_inclusion !== undefined && scoring.score_inclusion > 0 && (
                        <div className="flex items-center gap-2 text-[11px] pt-1">
                          <div className="w-28 truncate font-medium text-violet-600">Inclusion employeur</div>
                          <div className="flex-1 h-1.5 rounded-full bg-slate-100 overflow-hidden">
                            <div className="h-full rounded-full bg-violet-400 transition-all" style={{ width: `${scoring.score_inclusion}%` }} />
                          </div>
                          <span className="w-10 text-right text-violet-500">{scoring.score_inclusion}%</span>
                        </div>
                      )}
                      {/* Points forts expanded */}
                      {scoring.points_forts?.length > 0 && (
                        <div className="mt-2 pt-2 border-t border-slate-100">
                          <p className="text-[10px] font-medium text-emerald-700 mb-1">Points forts :</p>
                          {scoring.points_forts.map((p, i) => (
                            <p key={i} className="text-[10px] text-emerald-600 flex items-center gap-1">
                              <CheckCircle2 className="w-3 h-3 shrink-0" />
                              <span className="font-medium">{p.critere}</span> — {p.message}
                            </p>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Apply Button */}
                  {(() => {
                    const jobTitle = match.titre || match.title || "";
                    const isApplied = appliedJobs.has(jobTitle);
                    const isApplying = applyingJob === jobTitle;
                    return (
                      <Button
                        className={`w-full mt-4 ${
                          isApplied
                            ? "bg-emerald-600 hover:bg-emerald-700"
                            : "bg-[#1e3a5f] hover:bg-[#2d4a6f]"
                        }`}
                        disabled={isApplied || isApplying}
                        onClick={() => handleApply(match)}
                        data-testid={`apply-btn-${idx}`}
                      >
                        {isApplying ? (
                          <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
                        ) : isApplied ? (
                          <CheckCircle2 className="w-4 h-4 mr-2" />
                        ) : (
                          <FileEdit className="w-4 h-4 mr-2" />
                        )}
                        {isApplied ? "Candidature en préparation" : isApplying ? "Enregistrement..." : "Préparer votre candidature"}
                      </Button>
                    );
                  })()}
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default JobMatchingSection;
