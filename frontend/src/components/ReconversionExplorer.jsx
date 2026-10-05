import React, { useState, useEffect, useRef, useCallback } from "react";
import axios from "axios";
import { API } from "@/App";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Compass, Sparkles, Loader2, ArrowRight, CheckCircle2, Plus,
  GraduationCap, ExternalLink, Lightbulb, TrendingUp, Shuffle, Telescope, RefreshCw
} from "lucide-react";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";

const CHAIN = ["Mes expériences", "Mes acquis", "Compétences transférables", "Métiers possibles", "Écart à combler", "Nouvelle trajectoire"];

const NIVEAUX = [
  { key: "evoluer", label: "Évoluer", sub: "Métiers proches du même univers", icon: TrendingUp, color: "bg-emerald-600", light: "bg-emerald-50 text-emerald-700 border-emerald-200" },
  { key: "reconvertir", label: "Me reconvertir", sub: "Métiers différents, compétences transférables", icon: Shuffle, color: "bg-blue-600", light: "bg-blue-50 text-blue-700 border-blue-200" },
  { key: "explorer", label: "Explorer autrement", sub: "Hypothèses en rupture, à explorer", icon: Telescope, color: "bg-violet-600", light: "bg-violet-50 text-violet-700 border-violet-200" },
];

const FicheMetier = ({ metier, niveau, token, onAdded }) => {
  const [adding, setAdding] = useState(false);
  const [added, setAdded] = useState(false);

  const addToTrajectory = async () => {
    setAdding(true);
    try {
      await axios.post(`${API}/trajectory/steps?token=${token}`, {
        title: `Projet : ${metier.metier}`,
        step_type: "projet", type: "projet",
        description: metier.pourquoi || "",
        skills: metier.sf_mobilisables || [],
        organization: "",
        visibility: "private",
      });
      setAdded(true);
      toast.success(`« ${metier.metier} » ajouté à votre trajectoire`);
      onAdded?.();
    } catch {
      toast.error("Erreur lors de l'ajout");
    } finally {
      setAdding(false);
    }
  };

  return (
    <Card className="rounded-2xl border border-slate-100 shadow-sm" data-testid={`fiche-metier-${niveau.key}`}>
      <CardContent className="p-5 space-y-4">
        <div className="flex items-start justify-between gap-3 flex-wrap">
          <div>
            <h4 className="text-base font-semibold text-slate-900">{metier.metier}</h4>
            {metier.rome_code && (
              <a href={`https://candidat.francetravail.fr/metierscope/fiche-metier/${metier.rome_code}`} target="_blank" rel="noreferrer"
                className="text-xs text-blue-600 hover:underline inline-flex items-center gap-1 mt-0.5">
                ROME {metier.rome_code}<ExternalLink className="w-3 h-3" />
              </a>
            )}
          </div>
          <Badge className={`rounded-full border text-xs ${niveau.light}`}>
            {metier.transferables_count || (metier.sf_mobilisables?.length || 0)} compétences transférables possédées
          </Badge>
        </div>

        <p className="text-sm text-slate-600 leading-relaxed">{metier.pourquoi}</p>

        <div className="grid gap-3 md:grid-cols-2">
          <div className="rounded-xl bg-emerald-50/70 p-3">
            <div className="text-xs font-semibold text-emerald-700 uppercase tracking-wide mb-1.5 flex items-center gap-1"><CheckCircle2 className="w-3.5 h-3.5" />Vous possédez déjà</div>
            <div className="flex flex-wrap gap-1.5">
              {(metier.sf_mobilisables || []).map((s, i) => <Badge key={i} variant="outline" className="rounded-full text-[11px] bg-white border-emerald-200 text-emerald-800">{s}</Badge>)}
              {(metier.se_mobilisables || []).map((s, i) => <Badge key={`se${i}`} variant="outline" className="rounded-full text-[11px] bg-white border-teal-200 text-teal-700">{s}</Badge>)}
            </div>
          </div>
          <div className="rounded-xl bg-amber-50/70 p-3">
            <div className="text-xs font-semibold text-amber-700 uppercase tracking-wide mb-1.5 flex items-center gap-1"><GraduationCap className="w-3.5 h-3.5" />Ce qu'il vous manque</div>
            <div className="flex flex-wrap gap-1.5">
              {(metier.manquantes || []).map((s, i) => <Badge key={i} variant="outline" className="rounded-full text-[11px] bg-white border-amber-200 text-amber-800">{s}</Badge>)}
            </div>
          </div>
        </div>

        {metier.reduire_ecart?.length > 0 && (
          <div>
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">Comment réduire l'écart</div>
            <ul className="space-y-1">
              {metier.reduire_ecart.map((a, i) => (
                <li key={i} className="text-sm text-slate-600 flex items-start gap-2"><ArrowRight className="w-3.5 h-3.5 mt-0.5 text-slate-400 shrink-0" />{a}</li>
              ))}
            </ul>
          </div>
        )}

        <div className="flex justify-end pt-1">
          <Button size="sm" className="rounded-xl bg-[#1e3a5f] hover:bg-[#152a45]" onClick={addToTrajectory} disabled={adding || added} data-testid="add-metier-trajectoire-btn">
            {adding ? <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" /> : added ? <CheckCircle2 className="w-3.5 h-3.5 mr-1.5" /> : <Plus className="w-3.5 h-3.5 mr-1.5" />}
            {added ? "Ajouté à ma trajectoire" : "Ajouter à ma trajectoire"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default function ReconversionExplorer({ open, onOpenChange, token, profile, onStepAdded }) {
  const [screen, setScreen] = useState("gateway");
  const [result, setResult] = useState(null);
  const [progress, setProgress] = useState(5);
  const [stepLabel, setStepLabel] = useState("");
  const [niveau, setNiveau] = useState("evoluer");
  const pollRef = useRef(null);
  const navigate = useNavigate();
  const hasDclic = !!profile?.dclic_imported;

  useEffect(() => {
    if (!open) return;
    axios.get(`${API}/trajectoire/explorer/latest?token=${token}`).then(res => {
      if (res.data?.has_data) { setResult(res.data.result); setScreen("result"); }
      else setScreen("gateway");
    }).catch(() => setScreen("gateway"));
    return () => clearInterval(pollRef.current);
  }, [open, token]);

  const poll = useCallback((jobId) => {
    clearInterval(pollRef.current);
    pollRef.current = setInterval(async () => {
      try {
        const res = await axios.get(`${API}/trajectoire/explorer/status/${jobId}?token=${token}`);
        const job = res.data;
        setProgress(job.progress || 10);
        setStepLabel(job.step_label || "");
        if (job.status === "completed") {
          clearInterval(pollRef.current);
          setResult(job.result);
          setScreen("result");
        } else if (job.status === "failed") {
          clearInterval(pollRef.current);
          toast.error("L'analyse a échoué. Réessayez.");
          setScreen("gateway");
        }
      } catch { /* retry next tick */ }
    }, 3000);
  }, [token]);

  const launch = async () => {
    setScreen("loading"); setProgress(5); setStepLabel("Initialisation…");
    try {
      const res = await axios.post(`${API}/trajectoire/explorer?token=${token}`);
      poll(res.data.job_id);
    } catch (e) {
      toast.error(e.response?.data?.detail || "Impossible de lancer l'exploration");
      setScreen("gateway");
    }
  };

  const activeNiveau = NIVEAUX.find(n => n.key === niveau);
  const metiers = result?.niveaux?.[niveau] || [];

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto rounded-2xl" data-testid="reconversion-dialog">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-xl">
            <Compass className="w-5 h-5 text-violet-600" />Explorer une nouvelle trajectoire
          </DialogTitle>
          <DialogDescription>La reconversion n'est pas une rupture : c'est une nouvelle lecture de votre expérience acquise.</DialogDescription>
        </DialogHeader>

        {/* Chaîne de cohérence */}
        <div className="flex flex-wrap items-center gap-1.5 rounded-xl bg-slate-50 px-3 py-2.5" data-testid="chaine-coherence">
          {CHAIN.map((c, i) => (
            <React.Fragment key={c}>
              <span className="text-[11px] font-medium text-slate-600">{c}</span>
              {i < CHAIN.length - 1 && <ArrowRight className="w-3 h-3 text-slate-300" />}
            </React.Fragment>
          ))}
        </div>

        {screen === "gateway" && (
          <div className="space-y-4 py-2" data-testid="reconversion-gateway">
            {hasDclic ? (
              <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-100 rounded-xl px-4 py-3 text-sm text-emerald-700">
                <Sparkles className="w-4 h-4 shrink-0" />
                Votre profil D'CLIC PRO {profile?.dclic_mbti ? `(${profile.dclic_mbti})` : ""} sera intégré à l'exploration pour des recommandations plus personnalisées.
              </div>
            ) : (
              <div className="bg-gradient-to-r from-violet-50 to-indigo-50 border border-violet-100 rounded-xl p-4" data-testid="dclic-gateway-banner">
                <div className="flex items-start gap-3">
                  <Lightbulb className="w-5 h-5 text-violet-600 shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-semibold text-slate-800">Avant d'explorer… nous vous recommandons D'CLIC PRO</p>
                    <p className="text-sm text-slate-600 mt-1">Le test D'CLIC PRO affine l'exploration en croisant votre personnalité, vos savoir-être et vos aspirations. C'est recommandé, mais pas obligatoire.</p>
                    <div className="flex gap-2 mt-3 flex-wrap">
                      <Button size="sm" className="rounded-xl bg-violet-600 hover:bg-violet-700" onClick={() => { onOpenChange(false); navigate("/test-dclic"); }} data-testid="go-dclic-btn">
                        Faire D'CLIC PRO
                      </Button>
                      <Button size="sm" variant="outline" className="rounded-xl" onClick={launch} data-testid="continue-without-dclic-btn">
                        Continuer sans D'CLIC PRO
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div className="text-sm text-slate-600 leading-relaxed">
              L'IA croisera vos <strong>expériences</strong>, vos <strong>savoir-faire</strong>, vos <strong>savoir-être</strong>{hasDclic ? ", votre profil D'CLIC PRO" : ""} et vos aspirations pour vous proposer des métiers sur 3 niveaux : <strong>Évoluer</strong> (proche), <strong>Me reconvertir</strong> (compétences transférables) et <strong>Explorer autrement</strong> (rupture).
            </div>
            {(hasDclic || true) && (
              <div className="flex justify-end">
                <Button className="rounded-xl bg-[#1e3a5f] hover:bg-[#152a45]" onClick={launch} data-testid="launch-exploration-btn">
                  <Compass className="w-4 h-4 mr-2" />Lancer l'exploration
                </Button>
              </div>
            )}
          </div>
        )}

        {screen === "loading" && (
          <div className="py-10 text-center space-y-4" data-testid="reconversion-loading">
            <Loader2 className="w-10 h-10 text-violet-500 animate-spin mx-auto" />
            <p className="text-sm font-medium text-slate-700">{stepLabel || "Analyse en cours…"}</p>
            <div className="max-w-sm mx-auto"><Progress value={progress} className="h-2" /></div>
            <p className="text-xs text-slate-400">L'analyse prend 30 à 60 secondes. Vos expériences, acquis et compétences transférables sont croisés avec les référentiels métiers.</p>
          </div>
        )}

        {screen === "result" && result && (
          <div className="space-y-5" data-testid="reconversion-result">
            {/* Ligne de cohérence */}
            {result.ligne_coherence && (
              <div className="rounded-2xl bg-gradient-to-br from-slate-900 to-slate-800 p-5 text-white" data-testid="ligne-coherence">
                <div className="text-xs uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1.5"><Sparkles className="w-3.5 h-3.5" />Votre ligne de cohérence</div>
                <p className="text-sm leading-relaxed text-slate-100 italic">« {result.ligne_coherence} »</p>
                {result.invariants?.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mt-3">
                    {result.invariants.map((inv, i) => <Badge key={i} className="rounded-full bg-white/10 text-white hover:bg-white/10 text-xs">{inv}</Badge>)}
                  </div>
                )}
              </div>
            )}

            {/* Acquis + transférables */}
            <div className="grid gap-3 md:grid-cols-2">
              {result.acquis?.length > 0 && (
                <div className="rounded-xl border border-slate-100 p-4">
                  <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Mes acquis</div>
                  <ul className="space-y-1">{result.acquis.slice(0, 6).map((a, i) => <li key={i} className="text-sm text-slate-600 flex items-start gap-1.5"><CheckCircle2 className="w-3.5 h-3.5 mt-0.5 text-emerald-500 shrink-0" />{a}</li>)}</ul>
                </div>
              )}
              {result.competences_transferables?.length > 0 && (
                <div className="rounded-xl border border-slate-100 p-4">
                  <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Mes compétences transférables</div>
                  <div className="flex flex-wrap gap-1.5">{result.competences_transferables.map((c, i) => <Badge key={i} variant="outline" className="rounded-full text-xs">{c}</Badge>)}</div>
                </div>
              )}
            </div>

            {/* Curseur 3 niveaux */}
            <div>
              <div className="flex items-center justify-between text-xs text-slate-400 mb-2 px-1">
                <span>Proche</span><span>Rupture</span>
              </div>
              <div className="grid grid-cols-3 gap-2" data-testid="curseur-niveaux">
                {NIVEAUX.map(n => {
                  const Icon = n.icon;
                  const active = niveau === n.key;
                  return (
                    <button key={n.key} onClick={() => setNiveau(n.key)} data-testid={`niveau-${n.key}-btn`}
                      className={`rounded-xl border p-3 text-left transition-colors ${active ? `${n.color} text-white border-transparent shadow` : "bg-white border-slate-200 text-slate-700 hover:bg-slate-50"}`}>
                      <Icon className="w-4 h-4 mb-1.5" />
                      <div className="text-sm font-semibold">{n.label}</div>
                      <div className={`text-[11px] mt-0.5 leading-tight ${active ? "text-white/80" : "text-slate-400"}`}>{n.sub}</div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Fiches passerelles */}
            <div className="space-y-3">
              {metiers.length > 0 ? metiers.map((m, i) => (
                <FicheMetier key={`${niveau}-${i}`} metier={m} niveau={activeNiveau} token={token} onAdded={onStepAdded} />
              )) : <p className="text-sm text-slate-400 text-center py-4">Aucun métier proposé pour ce niveau.</p>}
            </div>

            <div className="flex justify-between items-center pt-1">
              <p className="text-xs text-slate-400">{result.dclic_utilise ? "Analyse enrichie par votre profil D'CLIC PRO" : "Astuce : passez D'CLIC PRO pour affiner ces recommandations"}</p>
              <Button variant="outline" size="sm" className="rounded-xl" onClick={launch} data-testid="relaunch-exploration-btn">
                <RefreshCw className="w-3.5 h-3.5 mr-1.5" />Relancer l'exploration
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
