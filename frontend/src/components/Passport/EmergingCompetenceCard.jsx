import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Zap, TrendingUp, TrendingDown, Minus } from "lucide-react";
import { NIVEAU_CONFIG, CATEGORIE_EMERGING_CONFIG, TENDANCE_CONFIG } from "./passportConfig";

const MARKET_POSITION_CONFIG = {
  en_demande: { label: "En demande", color: "bg-emerald-100 text-emerald-700 border-emerald-200", icon: TrendingUp },
  en_declin: { label: "En déclin", color: "bg-rose-100 text-rose-700 border-rose-200", icon: TrendingDown },
  neutre: { label: "Neutre", color: "bg-slate-100 text-slate-600 border-slate-200", icon: Minus },
};

const EmergingCompetenceCard = ({ comp, marketCorrelation }) => {
  const niveau = NIVEAU_CONFIG[comp.niveau_emergence] || NIVEAU_CONFIG.emergente;
  const cat = CATEGORIE_EMERGING_CONFIG[comp.categorie] || CATEGORIE_EMERGING_CONFIG.hybride;
  const tendance = TENDANCE_CONFIG[comp.tendance] || TENDANCE_CONFIG.hausse;
  const TendanceIcon = tendance.icon;
  const score = comp.score_emergence || 0;
  const mc = marketCorrelation;
  const positionCfg = mc ? MARKET_POSITION_CONFIG[mc.market_position] || MARKET_POSITION_CONFIG.neutre : null;

  return (
    <Card className={`border-violet-200 bg-gradient-to-br from-white to-violet-50/40 hover:shadow-lg transition-all ${mc?.has_market_data ? "ring-1 ring-emerald-200" : ""}`} data-testid="emerging-competence-card">
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1">
            <h4 className="font-bold text-slate-900 text-sm" data-testid="emerging-comp-name">{comp.nom_principal}</h4>
            <div className="flex items-center gap-1.5 mt-1.5 flex-wrap">
              <Badge className={`text-xs ${cat.color}`}>{cat.label}</Badge>
              <Badge className={`text-xs ${niveau.color}`}>{niveau.label}</Badge>
              <span className={`flex items-center gap-0.5 text-xs font-medium ${tendance.color}`}>
                <TendanceIcon className="w-3 h-3" />{tendance.label}
              </span>
              {positionCfg && mc.market_position !== "neutre" && (
                <Badge className={`text-[10px] border ${positionCfg.color}`} data-testid="market-position-badge">
                  {(() => { const Icon = positionCfg.icon; return <Icon className="w-2.5 h-2.5 mr-0.5" />; })()}
                  {positionCfg.label}
                </Badge>
              )}
            </div>
          </div>
          <div className="flex flex-col items-center ml-3">
            <div className="relative w-12 h-12">
              <svg viewBox="0 0 36 36" className="w-12 h-12 -rotate-90">
                <circle cx="18" cy="18" r="15" fill="none" stroke="#e2e8f0" strokeWidth="3" />
                <circle cx="18" cy="18" r="15" fill="none" stroke={niveau.barColor} strokeWidth="3"
                  strokeDasharray={`${(score / 100) * 94.2} 94.2`} strokeLinecap="round" />
              </svg>
              <span className="absolute inset-0 flex items-center justify-center text-xs font-bold text-slate-700">{score}</span>
            </div>
            <span className="text-[10px] text-slate-400 mt-0.5">Score</span>
          </div>
        </div>

        {/* Market correlation info */}
        {mc?.market_match && (
          <div className="mb-3 p-2 rounded-lg bg-emerald-50/60 border border-emerald-100" data-testid="market-match-info">
            <p className="text-[10px] uppercase tracking-wider text-emerald-500 font-semibold mb-1">Tendance marché</p>
            <div className="flex items-center gap-2 text-xs text-slate-700">
              <span className="font-medium">{mc.market_match.skill_name}</span>
              <Badge className="text-[10px] bg-emerald-100 text-emerald-700">
                +{Math.round((mc.market_match.growth_rate || 0) * 100)}% croissance
              </Badge>
              <Badge className="text-[10px] bg-blue-100 text-blue-700">
                Score marché: {Math.round((mc.market_match.emergence_score || 0) * 100)}
              </Badge>
            </div>
          </div>
        )}

        {comp.justification && (
          <p className="text-xs text-slate-600 mb-3 leading-relaxed">{comp.justification}</p>
        )}

        {comp.indicateurs_cles?.length > 0 && (
          <div className="mb-3">
            <p className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold mb-1">Indicateurs clés</p>
            <div className="space-y-1">
              {comp.indicateurs_cles.map((ind, i) => (
                <div key={i} className="flex items-start gap-1.5 text-xs text-slate-600">
                  <Zap className="w-3 h-3 text-amber-500 mt-0.5 shrink-0" />
                  <span>{ind}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="flex flex-wrap gap-3 text-xs">
          {comp.secteurs_porteurs?.length > 0 && (
            <div>
              <p className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold mb-1">Secteurs porteurs</p>
              <div className="flex flex-wrap gap-1">
                {comp.secteurs_porteurs.map((s, i) => (
                  <Badge key={i} variant="outline" className="text-[10px] border-blue-200 text-blue-600">{s}</Badge>
                ))}
              </div>
            </div>
          )}
          {comp.metiers_associes?.length > 0 && (
            <div>
              <p className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold mb-1">Métiers associés</p>
              <div className="flex flex-wrap gap-1">
                {comp.metiers_associes.map((m, i) => (
                  <Badge key={i} variant="outline" className="text-[10px] border-emerald-200 text-emerald-600">{m}</Badge>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Sector matches from market */}
        {mc?.sector_matches?.length > 0 && (
          <div className="mt-2 pt-2 border-t border-slate-100">
            <p className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold mb-1">Secteurs en transformation</p>
            <div className="flex flex-wrap gap-1">
              {mc.sector_matches.map((sm, i) => (
                <Badge key={i} className={`text-[10px] ${sm.hiring_trend === "croissance" ? "bg-emerald-50 text-emerald-700 border-emerald-200" : "bg-slate-50 text-slate-600 border-slate-200"} border`}>
                  {sm.sector} {sm.hiring_trend === "croissance" && <TrendingUp className="w-2.5 h-2.5 ml-0.5" />}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default EmergingCompetenceCard;
