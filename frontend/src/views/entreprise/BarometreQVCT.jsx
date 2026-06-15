import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Heart, TrendingUp, TrendingDown, Minus, Shield, Users, Brain, Sun, AlertTriangle, CheckCircle2, RefreshCw, BarChart3 } from "lucide-react";

const DIMENSIONS = [
  { key: "satisfaction", label: "Satisfaction globale", icon: Heart, color: "emerald" },
  { key: "engagement", label: "Engagement", icon: TrendingUp, color: "blue" },
  { key: "equilibre", label: "Équilibre vie pro/perso", icon: Sun, color: "amber" },
  { key: "management", label: "Qualité du management", icon: Users, color: "purple" },
  { key: "developpement", label: "Développement professionnel", icon: Brain, color: "teal" },
  { key: "reconnaissance", label: "Reconnaissance", icon: CheckCircle2, color: "orange" },
  { key: "securite", label: "Sécurité & conditions", icon: Shield, color: "red" },
];

const RISK_INDICATORS = [
  { key: "turnover", label: "Taux de turnover", unit: "%", seuil: 15, inverse: true },
  { key: "absenteisme", label: "Absentéisme", unit: "%", seuil: 5, inverse: true },
  { key: "rps", label: "Risques psychosociaux", unit: "/10", seuil: 6, inverse: true },
  { key: "nps", label: "eNPS (recommandation)", unit: "", seuil: 20, inverse: false },
];

const BarometreQVCT = ({ token }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${API}/entreprise/barometre?token=${token}`)
      .then(r => setData(r.data))
      .catch(() => setData(generateDemo()))
      .finally(() => setLoading(false));
  }, [token]);

  const generateDemo = () => ({
    dimensions: {
      satisfaction: { score: 72, trend: "up", prev: 68 },
      engagement: { score: 65, trend: "stable", prev: 64 },
      equilibre: { score: 58, trend: "down", prev: 63 },
      management: { score: 70, trend: "up", prev: 66 },
      developpement: { score: 55, trend: "up", prev: 50 },
      reconnaissance: { score: 48, trend: "down", prev: 52 },
      securite: { score: 82, trend: "stable", prev: 81 },
    },
    risks: {
      turnover: 12,
      absenteisme: 4.2,
      rps: 3.5,
      nps: 32,
    },
    participation: 78,
    last_survey: new Date().toISOString(),
    alerts: [
      { level: "warning", text: "La reconnaissance est en baisse — envisager des actions de valorisation" },
      { level: "warning", text: "L'équilibre vie pro/perso recule — surveiller la charge de travail" },
      { level: "success", text: "Le développement professionnel progresse grâce aux formations récentes" },
    ],
  });

  const TrendIcon = ({ trend }) => {
    if (trend === "up") return <TrendingUp className="w-3.5 h-3.5 text-emerald-500" />;
    if (trend === "down") return <TrendingDown className="w-3.5 h-3.5 text-red-500" />;
    return <Minus className="w-3.5 h-3.5 text-slate-400" />;
  };

  const scoreColor = (s) => s >= 70 ? "text-emerald-600" : s >= 50 ? "text-amber-600" : "text-red-600";
  const scoreBg = (s) => s >= 70 ? "bg-emerald-500" : s >= 50 ? "bg-amber-500" : "bg-red-500";

  const riskStatus = (indicator, value) => {
    if (indicator.inverse) return value <= indicator.seuil ? "ok" : "risk";
    return value >= indicator.seuil ? "ok" : "risk";
  };

  if (loading) return <div className="flex justify-center py-20"><RefreshCw className="w-6 h-6 animate-spin text-slate-400" /></div>;
  if (!data) return null;

  const globalScore = Math.round(DIMENSIONS.reduce((acc, d) => acc + (data.dimensions[d.key]?.score || 0), 0) / DIMENSIONS.length);

  return (
    <div className="space-y-6" data-testid="barometre-qvct">
      <div>
        <h1 className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>Baromètre QVCT</h1>
        <p className="text-sm text-slate-500 mt-1">Qualité de vie et conditions de travail — indicateurs et tendances</p>
      </div>

      {/* Score global + Participation */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="border-2 border-emerald-200">
          <CardContent className="p-6 flex items-center gap-6">
            <div className="relative w-24 h-24">
              <svg viewBox="0 0 100 100" className="w-24 h-24 -rotate-90">
                <circle cx="50" cy="50" r="42" stroke="#e2e8f0" strokeWidth="8" fill="none" />
                <circle cx="50" cy="50" r="42" stroke={globalScore >= 70 ? "#10b981" : globalScore >= 50 ? "#f59e0b" : "#ef4444"} strokeWidth="8" fill="none"
                  strokeDasharray={`${globalScore * 2.64} 264`} strokeLinecap="round" />
              </svg>
              <span className={`absolute inset-0 flex items-center justify-center text-2xl font-black ${scoreColor(globalScore)}`}>{globalScore}</span>
            </div>
            <div>
              <h3 className="font-bold text-lg text-slate-900">Score QVCT global</h3>
              <p className="text-sm text-slate-500">Moyenne des 7 dimensions</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6 flex items-center gap-6">
            <div className={`w-16 h-16 rounded-full flex items-center justify-center ${data.participation >= 70 ? "bg-emerald-100" : "bg-amber-100"}`}>
              <Users className={`w-7 h-7 ${data.participation >= 70 ? "text-emerald-600" : "text-amber-600"}`} />
            </div>
            <div>
              <h3 className="font-bold text-lg text-slate-900">{data.participation}%</h3>
              <p className="text-sm text-slate-500">Taux de participation au dernier sondage</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 7 Dimensions */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2"><BarChart3 className="w-4 h-4 text-emerald-600" />Dimensions QVCT</CardTitle>
          <CardDescription>Score sur 100 et tendance par rapport à la période précédente</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {DIMENSIONS.map(dim => {
            const d = data.dimensions[dim.key] || { score: 0, trend: "stable", prev: 0 };
            const Icon = dim.icon;
            const diff = d.score - d.prev;
            return (
              <div key={dim.key} className="flex items-center gap-4" data-testid={`dim-${dim.key}`}>
                <div className={`w-9 h-9 rounded-lg flex items-center justify-center bg-${dim.color}-100`}>
                  <Icon className={`w-4.5 h-4.5 text-${dim.color}-600`} />
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-slate-700">{dim.label}</span>
                    <div className="flex items-center gap-2">
                      <span className={`text-sm font-bold ${scoreColor(d.score)}`}>{d.score}%</span>
                      <TrendIcon trend={d.trend} />
                      <span className={`text-xs ${diff >= 0 ? "text-emerald-500" : "text-red-500"}`}>{diff >= 0 ? "+" : ""}{diff}</span>
                    </div>
                  </div>
                  <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                    <div className={`h-full rounded-full ${scoreBg(d.score)} transition-all`} style={{ width: `${d.score}%` }} />
                  </div>
                </div>
              </div>
            );
          })}
        </CardContent>
      </Card>

      {/* Indicateurs de risque */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2"><AlertTriangle className="w-4 h-4 text-amber-600" />Indicateurs de risque</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {RISK_INDICATORS.map(ind => {
              const value = data.risks[ind.key] ?? 0;
              const status = riskStatus(ind, value);
              return (
                <div key={ind.key} className={`p-4 rounded-xl border ${status === "ok" ? "border-emerald-200 bg-emerald-50" : "border-red-200 bg-red-50"}`}>
                  <p className="text-xs font-medium text-slate-500">{ind.label}</p>
                  <p className={`text-2xl font-black mt-1 ${status === "ok" ? "text-emerald-700" : "text-red-700"}`}>{value}{ind.unit}</p>
                  <p className="text-[10px] text-slate-400 mt-0.5">Seuil : {ind.seuil}{ind.unit}</p>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Alertes & Recommandations */}
      {data.alerts?.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Alertes & Recommandations</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {data.alerts.map((a, i) => (
              <div key={i} className={`p-3 rounded-lg flex items-start gap-3 ${a.level === "success" ? "bg-emerald-50 border border-emerald-200" : "bg-amber-50 border border-amber-200"}`}>
                {a.level === "success" ? <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5" /> : <AlertTriangle className="w-4 h-4 text-amber-600 mt-0.5" />}
                <p className={`text-sm ${a.level === "success" ? "text-emerald-700" : "text-amber-700"}`}>{a.text}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {data.last_survey && <p className="text-xs text-slate-400 text-center">Dernier sondage : {new Date(data.last_survey).toLocaleDateString("fr-FR")}</p>}
    </div>
  );
};

export default BarometreQVCT;
