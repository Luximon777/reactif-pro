import { useState, useMemo } from "react";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Slider } from "@/components/ui/slider";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle
} from "@/components/ui/dialog";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue
} from "@/components/ui/select";
import {
  Brain, RefreshCw, Zap, TrendingUp, ArrowRight, Sparkles,
  Filter, ArrowUpDown, BarChart3, ChevronRight, Award, Shield,
  CheckCircle2, XCircle, Edit3
} from "lucide-react";
import { toast } from "sonner";
import EmergingCompetenceCard from "./EmergingCompetenceCard";
import { NIVEAU_CONFIG, CATEGORIE_EMERGING_CONFIG, TENDANCE_CONFIG } from "./passportConfig";

const CATEGORIES = [
  { value: "all", label: "Toutes les catégories" },
  { value: "tech_emergente", label: "Tech émergente" },
  { value: "hybride", label: "Hybride" },
  { value: "soft_skill_avancee", label: "Soft skill avancée" },
  { value: "methodologique", label: "Méthodologique" },
  { value: "sectorielle", label: "Sectorielle" },
];

const SORT_OPTIONS = [
  { value: "score_desc", label: "Score (plus haut)" },
  { value: "score_asc", label: "Score (plus bas)" },
  { value: "name_asc", label: "Nom (A-Z)" },
  { value: "tendance", label: "Tendance" },
];

const TENDANCE_SORT_ORDER = { hausse: 0, nouvelle: 1, stable: 2 };

const EmergingTab = ({ competences, loading, onRefresh, token }) => {
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [sortBy, setSortBy] = useState("score_desc");
  const [minScore, setMinScore] = useState(0);
  const [selectedComp, setSelectedComp] = useState(null);
  const [showFilters, setShowFilters] = useState(false);

  const filtered = useMemo(() => {
    let result = [...competences];

    if (categoryFilter !== "all") {
      result = result.filter(c => c.categorie === categoryFilter);
    }
    if (minScore > 0) {
      result = result.filter(c => (c.score_emergence || 0) >= minScore);
    }

    switch (sortBy) {
      case "score_desc": result.sort((a, b) => (b.score_emergence || 0) - (a.score_emergence || 0)); break;
      case "score_asc": result.sort((a, b) => (a.score_emergence || 0) - (b.score_emergence || 0)); break;
      case "name_asc": result.sort((a, b) => (a.nom_principal || "").localeCompare(b.nom_principal || "")); break;
      case "tendance": result.sort((a, b) => (TENDANCE_SORT_ORDER[a.tendance] ?? 9) - (TENDANCE_SORT_ORDER[b.tendance] ?? 9)); break;
    }
    return result;
  }, [competences, categoryFilter, sortBy, minScore]);

  // Stats
  const stats = useMemo(() => {
    if (competences.length === 0) return null;
    const avgScore = Math.round(competences.reduce((s, c) => s + (c.score_emergence || 0), 0) / competences.length);
    const byCat = {};
    const byLevel = {};
    competences.forEach(c => {
      byCat[c.categorie] = (byCat[c.categorie] || 0) + 1;
      byLevel[c.niveau_emergence] = (byLevel[c.niveau_emergence] || 0) + 1;
    });
    const topCat = Object.entries(byCat).sort((a, b) => b[1] - a[1])[0];
    const hausse = competences.filter(c => c.tendance === "hausse").length;
    return { avgScore, byCat, byLevel, topCat, hausse, total: competences.length };
  }, [competences]);

  const isFiltered = categoryFilter !== "all" || minScore > 0;

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-slate-900" data-testid="emerging-title">
          Compétences émergentes ({competences.length})
        </h3>
        <div className="flex items-center gap-2">
          <Badge className="bg-violet-100 text-violet-700"><Brain className="w-3 h-3 mr-1" />Détection IA</Badge>
          <Button variant="outline" size="sm" onClick={() => setShowFilters(!showFilters)} data-testid="toggle-filters-btn">
            <Filter className={`w-3 h-3 mr-1 ${isFiltered ? "text-violet-600" : ""}`} />Filtres{isFiltered && ` (${filtered.length})`}
          </Button>
          <Button variant="outline" size="sm" onClick={onRefresh} disabled={loading} data-testid="refresh-emerging-btn">
            <RefreshCw className={`w-3 h-3 mr-1 ${loading ? "animate-spin" : ""}`} />Actualiser
          </Button>
        </div>
      </div>
      <p className="text-sm text-slate-500">Compétences rares, en forte croissance ou atypiques détectées dans votre CV par l'IA</p>

      {/* Stats Summary */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3" data-testid="emerging-stats">
          <Card className="bg-violet-50 border-violet-200">
            <CardContent className="p-3 text-center">
              <p className="text-2xl font-bold text-violet-700">{stats.total}</p>
              <p className="text-[10px] text-violet-500">Détectées</p>
            </CardContent>
          </Card>
          <Card className="bg-blue-50 border-blue-200">
            <CardContent className="p-3 text-center">
              <p className="text-2xl font-bold text-blue-700">{stats.avgScore}</p>
              <p className="text-[10px] text-blue-500">Score moyen</p>
            </CardContent>
          </Card>
          <Card className="bg-emerald-50 border-emerald-200">
            <CardContent className="p-3 text-center">
              <p className="text-2xl font-bold text-emerald-700">{stats.hausse}</p>
              <p className="text-[10px] text-emerald-500">En hausse</p>
            </CardContent>
          </Card>
          <Card className="bg-amber-50 border-amber-200">
            <CardContent className="p-3 text-center">
              <p className="text-2xl font-bold text-amber-700">
                {stats.topCat ? CATEGORIE_EMERGING_CONFIG[stats.topCat[0]]?.label || stats.topCat[0] : "-"}
              </p>
              <p className="text-[10px] text-amber-500">Top catégorie</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters Panel */}
      {showFilters && (
        <Card className="border-violet-200 bg-violet-50/30" data-testid="emerging-filters-panel">
          <CardContent className="p-4 space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="text-xs font-medium text-slate-600 mb-1.5 block">Catégorie</label>
                <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                  <SelectTrigger data-testid="filter-category"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {CATEGORIES.map(c => <SelectItem key={c.value} value={c.value}>{c.label}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="text-xs font-medium text-slate-600 mb-1.5 block">Tri</label>
                <Select value={sortBy} onValueChange={setSortBy}>
                  <SelectTrigger data-testid="filter-sort"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {SORT_OPTIONS.map(s => <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="text-xs font-medium text-slate-600 mb-1.5 block">Score min : {minScore}</label>
                <Slider
                  value={[minScore]}
                  onValueChange={([v]) => setMinScore(v)}
                  max={100}
                  step={5}
                  className="mt-2"
                  data-testid="filter-min-score"
                />
              </div>
            </div>
            {isFiltered && (
              <div className="flex items-center justify-between">
                <p className="text-xs text-violet-600">{filtered.length} résultat{filtered.length !== 1 ? "s" : ""} sur {competences.length}</p>
                <Button variant="ghost" size="sm" className="text-xs" onClick={() => { setCategoryFilter("all"); setMinScore(0); }} data-testid="clear-filters-btn">
                  Réinitialiser
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Level Distribution Bar */}
      {stats && (
        <div className="flex items-center gap-1 h-2 rounded-full overflow-hidden" data-testid="level-distribution-bar">
          {Object.entries(stats.byLevel).map(([level, count]) => {
            const cfg = NIVEAU_CONFIG[level];
            if (!cfg) return null;
            const pct = (count / stats.total) * 100;
            return (
              <div
                key={level}
                className="h-full rounded-full transition-all"
                style={{ width: `${pct}%`, backgroundColor: cfg.barColor, minWidth: pct > 0 ? "4px" : "0" }}
                title={`${cfg.label}: ${count} (${Math.round(pct)}%)`}
              />
            );
          })}
        </div>
      )}
      {stats && (
        <div className="flex flex-wrap gap-3 text-[10px]">
          {Object.entries(stats.byLevel).map(([level, count]) => {
            const cfg = NIVEAU_CONFIG[level];
            if (!cfg) return null;
            return (
              <span key={level} className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: cfg.barColor }} />
                {cfg.label} ({count})
              </span>
            );
          })}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-8">
          <RefreshCw className="w-6 h-6 animate-spin text-violet-500" />
        </div>
      )}

      {/* Cards Grid */}
      {!loading && filtered.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filtered.map(ec => (
            <div key={ec.id} className="cursor-pointer" onClick={() => setSelectedComp(ec)} data-testid="emerging-card-wrapper">
              <EmergingCompetenceCard comp={ec} />
            </div>
          ))}
        </div>
      )}

      {!loading && filtered.length === 0 && competences.length > 0 && (
        <div className="text-center py-10 text-slate-400 border-2 border-dashed border-slate-200 rounded-xl">
          <Filter className="w-8 h-8 mx-auto mb-2 text-slate-300" />
          <p className="text-sm">Aucune compétence ne correspond aux filtres actuels</p>
          <Button variant="ghost" size="sm" className="mt-2 text-xs" onClick={() => { setCategoryFilter("all"); setMinScore(0); }}>Réinitialiser les filtres</Button>
        </div>
      )}

      {!loading && competences.length === 0 && (
        <div className="text-center py-10 text-slate-400 border-2 border-dashed border-slate-200 rounded-xl">
          <p className="text-sm">Analysez votre CV pour détecter automatiquement les compétences émergentes</p>
        </div>
      )}

      {/* Detail Modal */}
      <Dialog open={!!selectedComp} onOpenChange={(open) => { if (!open) setSelectedComp(null); }}>
        <DialogContent className="max-w-lg max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-violet-600" />
              {selectedComp?.nom_principal}
            </DialogTitle>
          </DialogHeader>
          {selectedComp && <CompetenceDetail comp={selectedComp} token={token} onValidated={() => { setSelectedComp(null); onRefresh(); }} />}
        </DialogContent>
      </Dialog>
    </div>
  );
};

const CompetenceDetail = ({ comp, token, onValidated }) => {
  const niveau = NIVEAU_CONFIG[comp.niveau_emergence] || NIVEAU_CONFIG.emergente;
  const cat = CATEGORIE_EMERGING_CONFIG[comp.categorie] || CATEGORIE_EMERGING_CONFIG.hybride;
  const tendance = TENDANCE_CONFIG[comp.tendance] || TENDANCE_CONFIG.hausse;
  const TendanceIcon = tendance.icon;
  const score = comp.score_emergence || 0;
  const [validating, setValidating] = useState(false);
  const [showModify, setShowModify] = useState(false);
  const [newLabel, setNewLabel] = useState(comp.nom_principal || "");
  const [comment, setComment] = useState("");

  const handleValidate = async (decision) => {
    setValidating(true);
    try {
      await axios.post(`${API}/emerging/validate/${comp.id}?token=${token}`, {
        decision,
        commentaire: comment,
        nouveau_libelle: decision === "modifie" ? newLabel : "",
      });
      toast.success(decision === "valide" ? "Compétence validée" : decision === "rejete" ? "Compétence rejetée" : "Compétence modifiée");
      onValidated();
    } catch (err) {
      toast.error("Erreur lors de la validation");
    }
    setValidating(false);
  };

  return (
    <div className="space-y-5" data-testid="emerging-detail-modal">
      {/* Score Circle + Badges */}
      <div className="flex items-center gap-4">
        <div className="relative w-20 h-20 shrink-0">
          <svg viewBox="0 0 36 36" className="w-20 h-20 -rotate-90">
            <circle cx="18" cy="18" r="15" fill="none" stroke="#e2e8f0" strokeWidth="2.5" />
            <circle cx="18" cy="18" r="15" fill="none" stroke={niveau.barColor} strokeWidth="2.5"
              strokeDasharray={`${(score / 100) * 94.2} 94.2`} strokeLinecap="round" />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-lg font-bold text-slate-800">{score}</span>
            <span className="text-[9px] text-slate-400">/ 100</span>
          </div>
        </div>
        <div className="space-y-2">
          <div className="flex flex-wrap gap-1.5">
            <Badge className={`text-xs ${cat.color}`}>{cat.label}</Badge>
            <Badge className={`text-xs ${niveau.color}`}>{niveau.label}</Badge>
          </div>
          <div className={`flex items-center gap-1 text-sm font-medium ${tendance.color}`}>
            <TendanceIcon className="w-4 h-4" />
            <span>Tendance : {tendance.label}</span>
          </div>
          {comp.valide && (
            <Badge className="bg-emerald-100 text-emerald-700 text-xs"><Shield className="w-3 h-3 mr-1" />Validée</Badge>
          )}
        </div>
      </div>

      {/* Justification */}
      {comp.justification && (
        <div className="bg-slate-50 rounded-lg p-3">
          <p className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold mb-1">Justification</p>
          <p className="text-sm text-slate-700 leading-relaxed">{comp.justification}</p>
        </div>
      )}

      {/* Indicateurs clés */}
      {comp.indicateurs_cles?.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-slate-600 mb-2 flex items-center gap-1">
            <Zap className="w-3.5 h-3.5 text-amber-500" />Indicateurs clés
          </p>
          <div className="space-y-1.5">
            {comp.indicateurs_cles.map((ind, i) => (
              <div key={i} className="flex items-start gap-2 text-sm text-slate-600 bg-amber-50 rounded-lg px-3 py-2">
                <ChevronRight className="w-3.5 h-3.5 text-amber-500 mt-0.5 shrink-0" />
                <span>{ind}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Secteurs porteurs */}
      {comp.secteurs_porteurs?.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-slate-600 mb-2 flex items-center gap-1">
            <BarChart3 className="w-3.5 h-3.5 text-blue-500" />Secteurs porteurs
          </p>
          <div className="flex flex-wrap gap-2">
            {comp.secteurs_porteurs.map((s, i) => (
              <Badge key={i} className="bg-blue-50 text-blue-700 border border-blue-200 text-xs px-3 py-1">{s}</Badge>
            ))}
          </div>
        </div>
      )}

      {/* Métiers associés */}
      {comp.metiers_associes?.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-slate-600 mb-2 flex items-center gap-1">
            <Award className="w-3.5 h-3.5 text-emerald-500" />Métiers associés
          </p>
          <div className="flex flex-wrap gap-2">
            {comp.metiers_associes.map((m, i) => (
              <Badge key={i} className="bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs px-3 py-1">{m}</Badge>
            ))}
          </div>
        </div>
      )}

      {/* Detection metadata */}
      <div className="border-t pt-3 text-[10px] text-slate-400 space-y-0.5">
        {comp.date_detection && <p>Détectée le : {new Date(comp.date_detection).toLocaleDateString("fr-FR")}</p>}
        {comp.source_type && <p>Source : {comp.source_type === "cv_analysis" ? "Analyse CV" : comp.source_type}</p>}
        {comp.validation_humaine && <p>Validation : {comp.validation_humaine}</p>}
      </div>

      {/* Validation Interface (Phase 3) */}
      <div className="border-t pt-4 space-y-3" data-testid="validation-section">
        <p className="text-xs font-semibold text-slate-700 flex items-center gap-1.5">
          <Shield className="w-3.5 h-3.5 text-blue-500" />Validation humaine
        </p>

        {comp.validation_humaine ? (
          <Badge className={`text-xs ${comp.validation_humaine === "valide" ? "bg-emerald-100 text-emerald-700" : comp.validation_humaine === "rejete" ? "bg-red-100 text-red-700" : "bg-amber-100 text-amber-700"}`}>
            {comp.validation_humaine === "valide" ? "Validée" : comp.validation_humaine === "rejete" ? "Rejetée" : "Modifiée"}
          </Badge>
        ) : (
          <>
            <textarea
              className="w-full text-xs border border-slate-200 rounded-lg p-2 resize-none focus:ring-1 focus:ring-violet-400 placeholder:text-slate-400"
              rows={2}
              placeholder="Commentaire optionnel..."
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              data-testid="validation-comment"
            />

            {showModify && (
              <Input
                value={newLabel}
                onChange={(e) => setNewLabel(e.target.value)}
                placeholder="Nouveau libellé..."
                className="text-sm"
                data-testid="validation-new-label"
              />
            )}

            <div className="flex gap-2">
              <Button
                size="sm"
                className="bg-emerald-600 hover:bg-emerald-700 text-white flex-1"
                onClick={() => handleValidate("valide")}
                disabled={validating}
                data-testid="validate-btn"
              >
                <CheckCircle2 className="w-3.5 h-3.5 mr-1" />Valider
              </Button>
              <Button
                size="sm"
                variant="outline"
                className="flex-1 border-amber-300 text-amber-700 hover:bg-amber-50"
                onClick={() => { setShowModify(!showModify); if (!showModify) return; handleValidate("modifie"); }}
                disabled={validating}
                data-testid="modify-btn"
              >
                <Edit3 className="w-3.5 h-3.5 mr-1" />{showModify ? "Confirmer" : "Modifier"}
              </Button>
              <Button
                size="sm"
                variant="outline"
                className="flex-1 border-red-300 text-red-600 hover:bg-red-50"
                onClick={() => handleValidate("rejete")}
                disabled={validating}
                data-testid="reject-btn"
              >
                <XCircle className="w-3.5 h-3.5 mr-1" />Rejeter
              </Button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default EmergingTab;
