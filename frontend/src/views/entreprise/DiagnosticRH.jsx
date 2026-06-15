import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { ClipboardCheck, TrendingUp, AlertTriangle, CheckCircle2, ChevronRight, BarChart3, RefreshCw } from "lucide-react";

const AXES = [
  {
    key: "climat_social",
    label: "Climat social",
    questions: [
      "Les collaborateurs se sentent écoutés par leur hiérarchie",
      "Le climat de confiance au sein des équipes est satisfaisant",
      "Les conflits internes sont gérés de manière constructive",
    ],
  },
  {
    key: "gestion_competences",
    label: "Gestion des compétences",
    questions: [
      "Les compétences clés sont identifiées et cartographiées",
      "Des plans de formation individualisés existent",
      "Les entretiens professionnels sont réalisés régulièrement",
    ],
  },
  {
    key: "onboarding_integration",
    label: "Intégration & Onboarding",
    questions: [
      "Un parcours d'intégration structuré est en place",
      "Les nouveaux collaborateurs bénéficient d'un parrainage",
      "Un suivi post-intégration est réalisé à 1, 3 et 6 mois",
    ],
  },
  {
    key: "qvct",
    label: "QVCT & Bien-être",
    questions: [
      "Des actions concrètes de prévention des RPS sont en place",
      "L'équilibre vie pro / vie perso est favorisé",
      "Un dispositif d'écoute (cellule, médiateur) existe",
    ],
  },
  {
    key: "communication",
    label: "Communication & Transparence",
    questions: [
      "Les décisions RH sont communiquées de manière transparente",
      "Des canaux de feedback existent (enquêtes, boîte à idées)",
      "Les réussites individuelles et collectives sont valorisées",
    ],
  },
  {
    key: "pilotage",
    label: "Pilotage & Indicateurs",
    questions: [
      "Des KPIs RH sont suivis régulièrement (turnover, absentéisme)",
      "Les dispositifs RH sont ajustés selon les retours terrain",
      "La stratégie RH est alignée avec la stratégie globale",
    ],
  },
];

const LEVELS = [
  { value: 0, label: "Non évalué", color: "bg-slate-200" },
  { value: 1, label: "Inexistant", color: "bg-red-500" },
  { value: 2, label: "En émergence", color: "bg-orange-500" },
  { value: 3, label: "En place", color: "bg-amber-500" },
  { value: 4, label: "Maîtrisé", color: "bg-emerald-500" },
];

const DiagnosticRH = ({ token }) => {
  const [answers, setAnswers] = useState({});
  const [saved, setSaved] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${API}/entreprise/diagnostic?token=${token}`)
      .then(r => { setAnswers(r.data.answers || {}); setSaved(r.data); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [token]);

  const setAnswer = (axeKey, qIdx, value) => {
    setAnswers(prev => ({ ...prev, [`${axeKey}_${qIdx}`]: value }));
  };

  const getAxeScore = (axeKey, questions) => {
    let total = 0, count = 0;
    questions.forEach((_, i) => {
      const v = answers[`${axeKey}_${i}`];
      if (v && v > 0) { total += v; count++; }
    });
    return count > 0 ? Math.round((total / (count * 4)) * 100) : 0;
  };

  const globalScore = () => {
    let totalScore = 0, totalAxes = 0;
    AXES.forEach(axe => {
      const s = getAxeScore(axe.key, axe.questions);
      if (s > 0) { totalScore += s; totalAxes++; }
    });
    return totalAxes > 0 ? Math.round(totalScore / totalAxes) : 0;
  };

  const save = async () => {
    try {
      await axios.post(`${API}/entreprise/diagnostic?token=${token}`, { answers });
      setSaved({ answers, date: new Date().toISOString() });
    } catch {}
  };

  const scoreColor = (s) => s >= 75 ? "text-emerald-600" : s >= 50 ? "text-amber-600" : s >= 25 ? "text-orange-600" : "text-red-600";
  const scoreBg = (s) => s >= 75 ? "bg-emerald-100" : s >= 50 ? "bg-amber-100" : s >= 25 ? "bg-orange-100" : "bg-red-100";
  const scoreLabel = (s) => s >= 75 ? "Maîtrisé" : s >= 50 ? "En progrès" : s >= 25 ? "À renforcer" : "Prioritaire";

  const gs = globalScore();

  if (loading) return <div className="flex justify-center py-20"><RefreshCw className="w-6 h-6 animate-spin text-slate-400" /></div>;

  return (
    <div className="space-y-6" data-testid="diagnostic-rh">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>Diagnostic RH</h1>
          <p className="text-sm text-slate-500 mt-1">Évaluez la maturité de vos pratiques RH sur 6 axes stratégiques</p>
        </div>
        <Button onClick={save} className="bg-emerald-600 hover:bg-emerald-700" data-testid="save-diagnostic">
          <CheckCircle2 className="w-4 h-4 mr-2" />Enregistrer
        </Button>
      </div>

      {/* Score global */}
      <Card className="border-2 border-emerald-200 bg-gradient-to-r from-emerald-50 to-white">
        <CardContent className="p-6 flex items-center gap-6">
          <div className={`w-20 h-20 rounded-full flex items-center justify-center ${scoreBg(gs)}`}>
            <span className={`text-2xl font-black ${scoreColor(gs)}`}>{gs}%</span>
          </div>
          <div className="flex-1">
            <h3 className="font-bold text-lg text-slate-900">Score global de maturité RH</h3>
            <p className="text-sm text-slate-500">Basé sur {Object.keys(answers).filter(k => answers[k] > 0).length} / {AXES.reduce((a, ax) => a + ax.questions.length, 0)} critères évalués</p>
            <Progress value={gs} className="mt-2 h-2" />
          </div>
          <Badge className={`${scoreBg(gs)} ${scoreColor(gs)} text-sm px-3 py-1`}>{scoreLabel(gs)}</Badge>
        </CardContent>
      </Card>

      {/* Axes */}
      <div className="grid gap-4">
        {AXES.map(axe => {
          const score = getAxeScore(axe.key, axe.questions);
          return (
            <Card key={axe.key} data-testid={`axe-${axe.key}`}>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base flex items-center gap-2">
                    <BarChart3 className={`w-4 h-4 ${scoreColor(score)}`} />
                    {axe.label}
                  </CardTitle>
                  <Badge className={`${scoreBg(score)} ${scoreColor(score)} text-xs`}>{score}% — {scoreLabel(score)}</Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                {axe.questions.map((q, i) => (
                  <div key={i} className="flex items-center gap-3 p-2 rounded-lg hover:bg-slate-50">
                    <p className="flex-1 text-sm text-slate-700">{q}</p>
                    <div className="flex gap-1">
                      {LEVELS.filter(l => l.value > 0).map(level => (
                        <button key={level.value}
                          className={`w-7 h-7 rounded-full text-xs font-bold transition-all ${
                            answers[`${axe.key}_${i}`] === level.value
                              ? `${level.color} text-white scale-110 ring-2 ring-offset-1 ring-slate-300`
                              : "bg-slate-100 text-slate-400 hover:bg-slate-200"
                          }`}
                          onClick={() => setAnswer(axe.key, i, level.value)}
                          title={level.label}
                        >
                          {level.value}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Légende */}
      <Card>
        <CardContent className="p-4 flex flex-wrap gap-4 items-center">
          <span className="text-xs font-semibold text-slate-500">Légende :</span>
          {LEVELS.filter(l => l.value > 0).map(l => (
            <div key={l.value} className="flex items-center gap-1.5">
              <span className={`w-5 h-5 rounded-full ${l.color} text-white text-[10px] font-bold flex items-center justify-center`}>{l.value}</span>
              <span className="text-xs text-slate-600">{l.label}</span>
            </div>
          ))}
        </CardContent>
      </Card>

      {saved?.date && (
        <p className="text-xs text-slate-400 text-center">Dernière sauvegarde : {new Date(saved.date).toLocaleString("fr-FR")}</p>
      )}
    </div>
  );
};

export default DiagnosticRH;
