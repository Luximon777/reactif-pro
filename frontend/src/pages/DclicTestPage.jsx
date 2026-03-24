import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, ArrowRight, CheckCircle, Copy, Check, Home } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";

const API = process.env.REACT_APP_BACKEND_URL + "/api";

const DclicTestPage = () => {
  const navigate = useNavigate();
  const [questions, setQuestions] = useState([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [answers, setAnswers] = useState({});
  const [rankingSelections, setRankingSelections] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [codeCopied, setCodeCopied] = useState(false);

  useEffect(() => {
    fetch(`${API}/dclic/questionnaire`).then(r => r.json()).then(d => setQuestions(d.questions || []));
  }, []);

  if (!questions.length) return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-white flex items-center justify-center">
      <p className="text-slate-500 animate-pulse text-lg">Chargement du questionnaire...</p>
    </div>
  );

  const q = questions[currentIdx];
  const progress = ((currentIdx + 1) / questions.length) * 100;
  const isRanking = q?.type === "ranking";
  const currentRanking = rankingSelections[q?.id] || [];
  const canProceed = isRanking ? currentRanking.length === 4 : !!answers[q?.id];

  const handleAnswer = (val) => setAnswers(prev => ({ ...prev, [q.id]: val }));

  const handleRankingSelect = (choice) => {
    const qid = q.id;
    const sels = rankingSelections[qid] || [];
    const existIdx = sels.findIndex(s => s.value === choice.value);
    if (existIdx !== -1) {
      const next = sels.filter(s => s.value !== choice.value).map((s, i) => ({ ...s, rank: i + 1 }));
      setRankingSelections(p => ({ ...p, [qid]: next }));
      if (answers[qid]) setAnswers(p => { const c = { ...p }; delete c[qid]; return c; });
    } else if (sels.length < 4) {
      const next = [...sels, { ...choice, rank: sels.length + 1 }];
      setRankingSelections(p => ({ ...p, [qid]: next }));
      if (next.length === 4) setAnswers(p => ({ ...p, [qid]: next.map(s => s.value).join(",") }));
    }
  };

  const getRank = (val) => {
    const s = (rankingSelections[q?.id] || []).find(x => x.value === val);
    return s ? s.rank : null;
  };

  const handleNext = async () => {
    if (currentIdx < questions.length - 1) {
      setCurrentIdx(i => i + 1);
    } else {
      setIsSubmitting(true);
      try {
        const res = await fetch(`${API}/dclic/submit`, {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ answers })
        });
        const data = await res.json();
        setResult(data);
      } catch (e) {
        console.error(e);
      }
      setIsSubmitting(false);
    }
  };

  const copyCode = () => {
    if (result?.access_code) {
      navigator.clipboard.writeText(result.access_code);
      setCodeCopied(true);
      setTimeout(() => setCodeCopied(false), 3000);
    }
  };

  // RESULTS SCREEN
  if (result) {
    const p = result.profile || {};
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-blue-50">
        <div className="max-w-2xl mx-auto px-4 py-8 space-y-6">
          <div className="text-center space-y-2">
            <CheckCircle className="w-12 h-12 text-emerald-500 mx-auto" />
            <h1 className="text-2xl font-bold text-slate-900">Test D'CLIC PRO terminé !</h1>
            <p className="text-slate-500">Votre profil de personnalité et compétences a été généré</p>
          </div>

          {/* Access Code */}
          <Card className="border-2 border-indigo-200 bg-indigo-50" data-testid="dclic-access-code-card">
            <CardContent className="p-6 text-center space-y-3">
              <p className="text-sm font-semibold text-indigo-700">Votre code d'accès RE'ACTIF PRO</p>
              <div className="flex items-center justify-center gap-3">
                <span className="text-3xl font-mono font-bold text-indigo-900 tracking-widest" data-testid="dclic-code">{result.access_code}</span>
                <Button variant="outline" size="sm" onClick={copyCode} data-testid="copy-code-btn">
                  {codeCopied ? <Check className="w-4 h-4 text-emerald-500" /> : <Copy className="w-4 h-4" />}
                </Button>
              </div>
              <p className="text-xs text-indigo-600">Conservez ce code pour récupérer votre profil dans Re'Actif Pro via "Charger mon profil D'CLIC PRO"</p>
            </CardContent>
          </Card>

          {/* Profile Summary */}
          <Card data-testid="dclic-profile-summary">
            <CardContent className="p-6 space-y-4">
              <h2 className="text-lg font-bold text-slate-800">Aperçu de votre profil</h2>
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-violet-50 rounded-lg p-3 text-center">
                  <p className="text-xs text-violet-500 font-medium">Personnalité (MBTI)</p>
                  <p className="text-xl font-bold text-violet-800">{p.mbti}</p>
                </div>
                <div className="bg-blue-50 rounded-lg p-3 text-center">
                  <p className="text-xs text-blue-500 font-medium">Style (DISC)</p>
                  <p className="text-xl font-bold text-blue-800">{p.disc_dominant} - {p.disc_dominant_name}</p>
                </div>
                <div className="bg-emerald-50 rounded-lg p-3 text-center">
                  <p className="text-xs text-emerald-500 font-medium">Vertu dominante</p>
                  <p className="text-lg font-bold text-emerald-800">{p.vertu_dominante_name}</p>
                </div>
                <div className="bg-amber-50 rounded-lg p-3 text-center">
                  <p className="text-xs text-amber-500 font-medium">Intérêts (RIASEC)</p>
                  <p className="text-lg font-bold text-amber-800">{p.riasec_major_name} / {p.riasec_minor_name}</p>
                </div>
              </div>

              {p.competences_fortes?.length > 0 && (
                <div>
                  <p className="text-sm font-semibold text-slate-700 mb-2">Compétences fortes</p>
                  <div className="flex flex-wrap gap-2">
                    {p.competences_fortes.map((c, i) => (
                      <Badge key={i} className="bg-indigo-100 text-indigo-700">{c}</Badge>
                    ))}
                  </div>
                </div>
              )}

              {p.forces?.length > 0 && (
                <div>
                  <p className="text-sm font-semibold text-slate-700 mb-2">Forces de caractère</p>
                  <div className="flex flex-wrap gap-2">
                    {p.forces.map((f, i) => (
                      <Badge key={i} variant="outline" className="border-emerald-300 text-emerald-700">{f}</Badge>
                    ))}
                  </div>
                </div>
              )}

              {p.qualites?.length > 0 && (
                <div>
                  <p className="text-sm font-semibold text-slate-700 mb-2">Qualités humaines</p>
                  <div className="flex flex-wrap gap-2">
                    {p.qualites.map((q, i) => (
                      <Badge key={i} variant="outline" className="border-violet-300 text-violet-700">{q}</Badge>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* CTA */}
          <div className="flex flex-col sm:flex-row gap-3">
            <Button className="flex-1 bg-[#1e3a5f] hover:bg-[#15304f]" onClick={() => navigate("/dashboard")} data-testid="go-dashboard-btn">
              <Home className="w-4 h-4 mr-2" />Retour au dashboard
            </Button>
            <Button variant="outline" className="flex-1" onClick={() => { setResult(null); setCurrentIdx(0); setAnswers({}); setRankingSelections({}); }} data-testid="retake-test-btn">
              Repasser le test
            </Button>
          </div>
        </div>
      </div>
    );
  }

  // QUESTIONNAIRE SCREEN
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-blue-50">
      <div className="max-w-2xl mx-auto px-4 py-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <Button variant="ghost" size="sm" onClick={() => currentIdx > 0 ? setCurrentIdx(i => i - 1) : navigate(-1)} data-testid="back-btn">
            <ArrowLeft className="w-4 h-4 mr-1" />Retour
          </Button>
          <span className="text-sm text-slate-500 font-medium">Question {currentIdx + 1} / {questions.length}</span>
        </div>

        <Progress value={progress} className="h-2" />

        {/* Question */}
        <div className="space-y-2 text-center">
          <Badge variant="outline" className="text-xs">{q.category === "energie" ? "Énergie" : q.category === "perception" ? "Perception" : q.category === "decision" ? "Décision" : q.category === "structure" ? "Organisation" : q.category === "disc" ? "Style DISC" : q.category === "ennea" ? "Motivations" : q.category === "riasec" ? "Intérêts RIASEC" : q.category === "vertus" ? "Vertus" : q.category === "valeurs" ? "Valeurs" : q.category}</Badge>
          <h2 className="text-xl font-bold text-slate-900">{q.question}</h2>
          {q.instruction && <p className="text-sm text-slate-500">{q.instruction}</p>}
        </div>

        {/* Ranking choices */}
        {isRanking && (
          <div className="space-y-3">
            <div className="flex justify-center gap-2 mb-2">
              {[1,2,3,4].map(n => (
                <span key={n} className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${currentRanking.length >= n ? "bg-indigo-600 text-white" : "bg-slate-200 text-slate-400"}`}>{n}</span>
              ))}
            </div>
            <p className="text-center text-sm text-slate-500">
              {currentRanking.length < 4 ? `Sélectionnez votre choix n°${currentRanking.length + 1}` : "Classement complet ! Cliquez pour modifier."}
            </p>
            <div className={`grid ${q.choices[0]?.image ? "grid-cols-2" : "grid-cols-1"} gap-3`}>
              {q.choices.map(choice => {
                const rank = getRank(choice.value);
                const sel = rank !== null;
                return (
                  <button key={choice.id} disabled={!sel && currentRanking.length >= 4}
                    className={`relative rounded-xl border-2 p-3 text-left transition-all ${sel ? "border-indigo-500 bg-indigo-50 shadow-md" : "border-slate-200 hover:border-slate-300 bg-white"} ${!sel && currentRanking.length >= 4 ? "opacity-40" : "cursor-pointer"}`}
                    onClick={() => handleRankingSelect(choice)} data-testid={`choice-${choice.id}`}>
                    {sel && <span className="absolute -top-2 -right-2 w-7 h-7 rounded-full bg-indigo-600 text-white text-sm font-bold flex items-center justify-center">{rank}</span>}
                    {choice.image && <img src={choice.image} alt={choice.alt || ""} className="w-full h-28 object-cover rounded-lg mb-2" loading="lazy" />}
                    <p className="text-sm font-medium text-slate-800">{choice.label}</p>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* Visual choices */}
        {!isRanking && (
          <div className={`grid ${q.choices.length <= 2 ? "grid-cols-2" : "grid-cols-2"} gap-4`}>
            {q.choices.map(choice => {
              const sel = answers[q.id] === choice.value;
              return (
                <button key={choice.id}
                  className={`relative rounded-xl border-2 p-4 transition-all ${sel ? "border-indigo-500 bg-indigo-50 shadow-lg ring-2 ring-indigo-200" : "border-slate-200 hover:border-indigo-300 bg-white hover:shadow-md"} cursor-pointer`}
                  onClick={() => handleAnswer(choice.value)} data-testid={`choice-${choice.id}`}>
                  {choice.image && <img src={choice.image} alt={choice.alt || ""} className="w-full h-36 object-cover rounded-lg mb-3" loading="lazy" />}
                  <p className="text-sm font-semibold text-slate-800 text-center">{choice.label}</p>
                  {sel && <CheckCircle className="absolute top-2 right-2 w-6 h-6 text-indigo-600" />}
                </button>
              );
            })}
          </div>
        )}

        {/* Navigation */}
        <Button className="w-full bg-indigo-600 hover:bg-indigo-700 text-white" disabled={!canProceed || isSubmitting}
          onClick={handleNext} data-testid="next-btn">
          {isSubmitting ? "Analyse en cours..." : currentIdx === questions.length - 1 ? "Voir mes résultats" : (<>Suivant <ArrowRight className="w-4 h-4 ml-1" /></>)}
        </Button>
      </div>
    </div>
  );
};

export default DclicTestPage;
