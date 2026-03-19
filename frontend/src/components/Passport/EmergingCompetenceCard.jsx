import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Zap } from "lucide-react";
import { NIVEAU_CONFIG, CATEGORIE_EMERGING_CONFIG, TENDANCE_CONFIG } from "./passportConfig";

const EmergingCompetenceCard = ({ comp }) => {
  const niveau = NIVEAU_CONFIG[comp.niveau_emergence] || NIVEAU_CONFIG.emergente;
  const cat = CATEGORIE_EMERGING_CONFIG[comp.categorie] || CATEGORIE_EMERGING_CONFIG.hybride;
  const tendance = TENDANCE_CONFIG[comp.tendance] || TENDANCE_CONFIG.hausse;
  const TendanceIcon = tendance.icon;
  const score = comp.score_emergence || 0;

  return (
    <Card className="border-violet-200 bg-gradient-to-br from-white to-violet-50/40 hover:shadow-lg transition-all" data-testid="emerging-competence-card">
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
      </CardContent>
    </Card>
  );
};

export default EmergingCompetenceCard;
