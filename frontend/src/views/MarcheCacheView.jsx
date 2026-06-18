import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  EyeOff, Brain, Target, Shield, Users, TrendingUp, ArrowRight,
  Loader2, CheckCircle2, AlertTriangle, Sparkles, Network, Building2
} from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL + "/api";

const MarcheCacheView = ({ token }) => {
  const [diagnostic, setDiagnostic] = useState(null);
  const [loading, setLoading] = useState(false);

  // Auto-load diagnostic when user has a token
  useEffect(() => {
    if (!token) return;
    let cancelled = false;

    const doLoad = async () => {
      setLoading(true);
      try {
        const res = await axios.post(`${API}/marche-cache/diagnostic`, { token }, { timeout: 90000 });
        if (!cancelled) {
          if (res.data.error) {
            toast.error(res.data.error);
          } else {
            setDiagnostic(res.data.diagnostic);
          }
          setLoading(false);
        }
      } catch {
        if (!cancelled) {
          toast.error("Erreur lors de l'analyse");
          setLoading(false);
        }
      }
    };

    doLoad();
    return () => { cancelled = true; };
  }, [token]);

  const runDiagnostic = async () => {
    setDiagnostic(null);
    setLoading(true);
    try {
      const res = await axios.post(`${API}/marche-cache/diagnostic`, { token }, { timeout: 90000 });
      if (res.data.error) { toast.error(res.data.error); } else { setDiagnostic(res.data.diagnostic); }
    } catch { toast.error("Erreur lors de l'analyse"); }
    setLoading(false);
  };

  const scoreColor = (s) => s >= 7 ? "text-emerald-600" : s >= 4 ? "text-amber-600" : "text-red-600";
  const scoreBg = (s) => s >= 7 ? "bg-emerald-50 border-emerald-200" : s >= 4 ? "bg-amber-50 border-amber-200" : "bg-red-50 border-red-200";
  const prioColor = { haute: "bg-red-100 text-red-700", moyenne: "bg-amber-100 text-amber-700", basse: "bg-slate-100 text-slate-600" };

  return (
    <div className="space-y-6" data-testid="marche-cache-view">
      {/* Header explicatif */}
      <Card className="border-slate-200 bg-gradient-to-br from-slate-900 to-slate-800 text-white overflow-hidden">
        <CardContent className="p-6">
          <div className="flex items-start gap-4">
            <div className="w-14 h-14 rounded-2xl bg-white/10 flex items-center justify-center shrink-0">
              <EyeOff className="w-7 h-7 text-white" />
            </div>
            <div className="flex-1">
              <h2 className="text-xl font-bold mb-2" style={{ fontFamily: 'Outfit, sans-serif' }}>Le Marché Caché de l'Emploi</h2>
              <p className="text-slate-300 text-sm leading-relaxed mb-4">
                <span className="text-white font-bold">60 à 80% des postes</span> ne sont jamais publiés. Ils se pourvoient par le réseau, la cooptation, les candidatures spontanées et les recommandations internes. Accéder à ce marché invisible est un avantage stratégique majeur.
              </p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div className="bg-white/10 rounded-lg p-2.5 text-center">
                  <Network className="w-5 h-5 mx-auto mb-1 text-blue-300" />
                  <p className="text-xs font-semibold">Réseau pro</p>
                  <p className="text-[10px] text-slate-400">35% des postes</p>
                </div>
                <div className="bg-white/10 rounded-lg p-2.5 text-center">
                  <Users className="w-5 h-5 mx-auto mb-1 text-emerald-300" />
                  <p className="text-xs font-semibold">Cooptation</p>
                  <p className="text-[10px] text-slate-400">25% des postes</p>
                </div>
                <div className="bg-white/10 rounded-lg p-2.5 text-center">
                  <Target className="w-5 h-5 mx-auto mb-1 text-amber-300" />
                  <p className="text-xs font-semibold">Cand. spontanée</p>
                  <p className="text-[10px] text-slate-400">15% des postes</p>
                </div>
                <div className="bg-white/10 rounded-lg p-2.5 text-center">
                  <Building2 className="w-5 h-5 mx-auto mb-1 text-violet-300" />
                  <p className="text-xs font-semibold">Reco interne</p>
                  <p className="text-[10px] text-slate-400">10% des postes</p>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Loading state */}
      {loading && !diagnostic && (
        <Card className="border-[#4f6df5]/30 bg-gradient-to-r from-[#4f6df5]/5 to-[#10b981]/5" data-testid="marche-cache-loading">
          <CardContent className="p-6 text-center space-y-4">
            <Loader2 className="w-12 h-12 mx-auto text-[#4f6df5] animate-spin" />
            <div>
              <h3 className="text-lg font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>Analyse de votre profil en cours...</h3>
              <p className="text-sm text-slate-500 mt-1">L'IA croise vos compétences, expériences et personnalité pour évaluer votre accès au marché caché.</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* CTA Diagnostic - show only if not loading and no diagnostic */}
      {!diagnostic && !loading && (
        <Card className="border-[#4f6df5]/30 bg-gradient-to-r from-[#4f6df5]/5 to-[#10b981]/5" data-testid="marche-cache-cta">
          <CardContent className="p-6 text-center space-y-4">
            <Brain className="w-12 h-12 mx-auto text-[#4f6df5]" />
            <div>
              <h3 className="text-lg font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>Diagnostic personnalisé IA</h3>
              <p className="text-sm text-slate-500 mt-1">L'IA analyse votre profil (compétences, expériences, personnalité D'CLIC PRO) et évalue votre capacité à accéder au marché caché avec des recommandations concrètes.</p>
            </div>
            <Button className="bg-[#4f6df5] hover:bg-[#3d5bd9] text-white px-8" onClick={runDiagnostic} disabled={loading} data-testid="run-diagnostic-btn">
              {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Sparkles className="w-4 h-4 mr-2" />}
              {loading ? "Analyse en cours..." : "Analyser mon accès au marché caché"}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Résultats du diagnostic */}
      {diagnostic && (
        <div className="space-y-4" data-testid="marche-cache-results">
          {/* Score + Analyse */}
          <Card className={`border ${scoreBg(diagnostic.score_acces)}`}>
            <CardContent className="p-5">
              <div className="flex items-center gap-4">
                <div className={`w-20 h-20 rounded-2xl flex flex-col items-center justify-center ${scoreBg(diagnostic.score_acces)} border`}>
                  <p className={`text-3xl font-black ${scoreColor(diagnostic.score_acces)}`}>{diagnostic.score_acces}</p>
                  <p className="text-[9px] text-slate-500 font-semibold">/10</p>
                </div>
                <div className="flex-1">
                  <h3 className="font-bold text-slate-900 text-base">Score d'accès au marché caché</h3>
                  <p className="text-sm text-slate-600 mt-1 leading-relaxed">{diagnostic.analyse}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Forces et faiblesses */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardContent className="p-4">
                <h4 className="font-semibold text-emerald-700 text-sm flex items-center gap-2 mb-3"><CheckCircle2 className="w-4 h-4" />Vos atouts pour le marché caché</h4>
                <div className="space-y-2">
                  {(diagnostic.forces_marche_cache || []).map((f, i) => (
                    <div key={i} className="flex items-start gap-2 text-xs text-slate-700">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 shrink-0 mt-0.5" />
                      <span>{f}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <h4 className="font-semibold text-amber-700 text-sm flex items-center gap-2 mb-3"><AlertTriangle className="w-4 h-4" />Points à renforcer</h4>
                <div className="space-y-2">
                  {(diagnostic.faiblesses || []).map((f, i) => (
                    <div key={i} className="flex items-start gap-2 text-xs text-slate-700">
                      <AlertTriangle className="w-3.5 h-3.5 text-amber-500 shrink-0 mt-0.5" />
                      <span>{f}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recommandations */}
          <Card>
            <CardContent className="p-4">
              <h4 className="font-semibold text-slate-900 text-sm flex items-center gap-2 mb-3"><Target className="w-4 h-4 text-[#4f6df5]" />Recommandations personnalisées</h4>
              <div className="space-y-3">
                {(diagnostic.recommandations || []).map((r, i) => (
                  <div key={i} className="flex items-start gap-3 bg-slate-50 rounded-lg p-3 border border-slate-100" data-testid={`reco-${i}`}>
                    <ArrowRight className="w-4 h-4 text-[#4f6df5] shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-0.5">
                        <span className="text-sm font-semibold text-slate-800">{r.titre}</span>
                        <Badge className={`text-[9px] ${prioColor[r.priorite] || prioColor.moyenne}`}>{r.priorite}</Badge>
                      </div>
                      <p className="text-xs text-slate-600">{r.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Canaux + Entreprises + Stratégie */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardContent className="p-4">
                <h4 className="font-semibold text-slate-900 text-sm flex items-center gap-2 mb-3"><Network className="w-4 h-4 text-blue-500" />Canaux à privilégier</h4>
                <div className="space-y-1.5">
                  {(diagnostic.canaux_privilegier || []).map((c, i) => (
                    <div key={i} className="flex items-center gap-2 text-xs text-slate-700">
                      <div className="w-1.5 h-1.5 rounded-full bg-blue-500 shrink-0" />
                      {c}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <h4 className="font-semibold text-slate-900 text-sm flex items-center gap-2 mb-3"><Building2 className="w-4 h-4 text-violet-500" />Entreprises à cibler</h4>
                <div className="space-y-1.5">
                  {(diagnostic.types_entreprises || []).map((e, i) => (
                    <div key={i} className="flex items-center gap-2 text-xs text-slate-700">
                      <div className="w-1.5 h-1.5 rounded-full bg-violet-500 shrink-0" />
                      {e}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Stratégie réseau */}
          {diagnostic.strategie_reseau && (
            <Card className="border-blue-200 bg-blue-50">
              <CardContent className="p-4">
                <h4 className="font-semibold text-blue-900 text-sm flex items-center gap-2 mb-2"><TrendingUp className="w-4 h-4" />Stratégie réseau personnalisée</h4>
                <p className="text-sm text-blue-800 leading-relaxed">{diagnostic.strategie_reseau}</p>
              </CardContent>
            </Card>
          )}

          {/* Re-analyser */}
          <div className="text-center">
            <Button variant="outline" size="sm" onClick={runDiagnostic} disabled={loading} data-testid="rerun-diagnostic-btn">
              {loading ? <Loader2 className="w-3 h-3 animate-spin mr-1" /> : <Sparkles className="w-3 h-3 mr-1" />}
              Actualiser le diagnostic
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default MarcheCacheView;
