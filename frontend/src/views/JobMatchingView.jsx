import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Textarea } from "@/components/ui/textarea";
import {
  Search, FileText, Target, Download, ChevronRight, ChevronLeft,
  AlertTriangle, CheckCircle2, Lightbulb, Briefcase, GraduationCap,
  Users, MessageSquare, Loader2, ClipboardPaste, ArrowRight, Star,
  Info, Zap, Award, Clock, Link, BookmarkPlus
} from "lucide-react";
import { toast } from "sonner";

const ANALYSIS_CATEGORIES = [
  { icon: Clock, label: "Disponibilité de l'offre", desc: "Date de publication, nombre de postes" },
  { icon: Briefcase, label: "Descriptif de l'entreprise", desc: "Secteur, taille, localisation" },
  { icon: FileText, label: "Missions & responsabilités", desc: "Tâches concrètes du poste" },
  { icon: Award, label: "Type de contrat", desc: "CDI, CDD, intérim, durée" },
  { icon: Star, label: "Rémunération & avantages", desc: "Salaire, primes, avantages sociaux" },
  { icon: Target, label: "Profil recherché", desc: "Compétences, expérience, formations" },
  { icon: GraduationCap, label: "Perspectives d'évolution", desc: "Possibilités de carrière, formation" },
  { icon: Users, label: "Conditions de travail", desc: "Horaires, environnement, équipements" },
];

const JobMatchingView = ({ token }) => {
  const [step, setStep] = useState(1);
  const [offerText, setOfferText] = useState("");
  const [offerUrl, setOfferUrl] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const [matching, setMatching] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [matchResult, setMatchResult] = useState(null);
  const [history, setHistory] = useState([]);

  const [analyzingUrl, setAnalyzingUrl] = useState(false);
  const [savingCandidature, setSavingCandidature] = useState(false);
  const [candidatureSaved, setCandidatureSaved] = useState(false);

  useEffect(() => {
    loadHistory();
  }, [token]);

  const loadHistory = async () => {
    try {
      const res = await axios.get(`${API}/matching/history?token=${token}`);
      setHistory(res.data.analyses || []);
    } catch {}
  };

  const handleAnalyzeUrl = async () => {
    if (!offerUrl.trim().startsWith("http")) {
      toast.error("Collez une URL valide (commençant par http)");
      return;
    }
    setAnalyzingUrl(true);
    try {
      const res = await axios.post(`${API}/matching/analyze-offer-url?token=${token}`, { url: offerUrl });
      setAnalysis(res.data);
      setStep(3);
      toast.success("Analyse de l'offre terminée !");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Impossible d'analyser cette URL. Collez le texte manuellement.");
    } finally {
      setAnalyzingUrl(false);
    }
  };

  const handleAnalyze = async () => {
    if (offerText.trim().length < 30) {
      toast.error("Collez au moins 30 caractères de l'offre d'emploi");
      return;
    }
    setAnalyzing(true);
    try {
      const res = await axios.post(`${API}/matching/analyze-offer?token=${token}`, {
        text: offerText,
        source: "paste",
      });
      setAnalysis(res.data);
      setStep(3);
      toast.success("Analyse terminée !");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Erreur lors de l'analyse");
    } finally {
      setAnalyzing(false);
    }
  };

  const handleMatch = async () => {
    if (!analysis?.analysis_id) return;
    setMatching(true);
    try {
      const res = await axios.post(`${API}/matching/match-profile?token=${token}`, {
        analysis_id: analysis.analysis_id,
      });
      setMatchResult(res.data);
      setStep(4);
      toast.success("Matching terminé !");
      loadHistory();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Erreur lors du matching");
    } finally {
      setMatching(false);
    }
  };

  const resetAll = () => {
    setStep(1);
    setOfferText("");
    setOfferUrl("");
    setAnalysis(null);
    setMatchResult(null);
    setCandidatureSaved(false);
  };

  const handleSaveCandidature = async () => {
    if (!analysis?.analyse) return;
    setSavingCandidature(true);
    try {
      const a = analysis.analyse;
      const res = await axios.post(`${API}/jobs/apply?token=${token}`, {
        job_title: a.titre_poste || "Offre analysée",
        job_data: {
          entreprise: a.entreprise || "",
          localisation: a.localisation || "",
          type_contrat: a.type_contrat || "",
          salaire: a.salaire || "",
          url: offerUrl || "",
          score_qualite: analysis.score_qualite_offre || 0,
          score_matching: matchResult?.score_global || 0,
          verdict: matchResult?.verdict || "",
          analysis_id: analysis.analysis_id || "",
          source: "analyse_offre",
        },
      });
      if (res.data.already_applied) {
        toast.info("Cette candidature est déjà enregistrée");
      } else {
        toast.success("Candidature sauvegardée dans 'Mes Candidatures'");
      }
      setCandidatureSaved(true);
    } catch (e) {
      toast.error(e.response?.data?.detail || "Erreur lors de la sauvegarde");
    }
    setSavingCandidature(false);
  };

  return (
    <div className="space-y-6" data-testid="job-matching-view">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>
            Matching Candidat / Offre
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">Analysez une offre et mesurez votre compatibilité</p>
        </div>
        {step > 1 && (
          <Button variant="outline" size="sm" onClick={resetAll} data-testid="matching-reset">
            Nouvelle analyse
          </Button>
        )}
      </div>

      {/* Step Indicator */}
      <div className="flex items-center gap-1 sm:gap-2">
        {[
          { num: 1, label: "Comprendre" },
          { num: 2, label: "Importer" },
          { num: 3, label: "Analyser" },
          { num: 4, label: "Matching" },
        ].map((s) => (
          <div key={s.num} className="flex items-center gap-1 sm:gap-2 flex-1">
            <div className={`w-7 h-7 sm:w-8 sm:h-8 rounded-full flex items-center justify-center text-xs font-bold shrink-0 transition-all ${
              step >= s.num ? "bg-amber-500 text-white" : "bg-slate-200 text-slate-400"
            }`}>{s.num}</div>
            <span className={`text-xs hidden sm:inline ${step >= s.num ? "text-amber-700 font-medium" : "text-slate-400"}`}>{s.label}</span>
            {s.num < 4 && <ChevronRight className="w-3 h-3 text-slate-300 shrink-0" />}
          </div>
        ))}
      </div>

      {/* STEP 1: Sensibilisation */}
      {step === 1 && (
        <div className="space-y-4" data-testid="matching-step-1">
          <Card className="border-amber-200 bg-amber-50/30">
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <Info className="w-5 h-5 text-amber-600" />
                Que faut-il analyser dans une offre d'emploi ?
              </CardTitle>
              <CardDescription>Avant de postuler, apprenez à décoder une offre pour maximiser vos chances</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                {ANALYSIS_CATEGORIES.map((cat, i) => {
                  const Icon = cat.icon;
                  return (
                    <div key={i} className="flex items-start gap-2.5 p-2.5 rounded-lg bg-white border border-slate-100">
                      <div className="w-8 h-8 rounded-lg bg-amber-100 flex items-center justify-center shrink-0">
                        <Icon className="w-4 h-4 text-amber-700" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-slate-800">{cat.label}</p>
                        <p className="text-xs text-slate-500">{cat.desc}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
          <Button onClick={() => setStep(2)} className="w-full bg-amber-600 hover:bg-amber-700 text-white" data-testid="matching-start-btn">
            <Search className="w-4 h-4 mr-2" /> Analyser une offre d'emploi
          </Button>
        </div>
      )}

      {/* STEP 2: Import offre */}
      {step === 2 && (
        <div className="space-y-4" data-testid="matching-step-2">
          {/* URL field with Analyze button */}
          <Card className="border-emerald-200 bg-emerald-50/30">
            <CardHeader className="pb-2">
              <CardTitle className="text-base flex items-center gap-2">
                <Link className="w-5 h-5 text-emerald-600" />
                Analyser depuis l'URL de l'annonce
              </CardTitle>
              <CardDescription>Collez le lien de l'offre et l'IA récupère et analyse automatiquement le contenu</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex gap-2">
                <input
                  type="url"
                  value={offerUrl}
                  onChange={(e) => setOfferUrl(e.target.value)}
                  placeholder="https://candidat.francetravail.fr/offres/recherche/detail/..."
                  className="flex-1 px-3 py-2.5 rounded-lg border border-slate-200 text-sm focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none"
                  data-testid="matching-offer-url"
                />
                <Button
                  onClick={handleAnalyzeUrl}
                  disabled={analyzingUrl || !offerUrl.trim().startsWith("http")}
                  className="bg-emerald-600 hover:bg-emerald-700 text-white shrink-0"
                  data-testid="matching-analyze-url-btn"
                >
                  {analyzingUrl ? (
                    <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Analyse...</>
                  ) : (
                    <><Zap className="w-4 h-4 mr-2" /> Analyser</>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>

          <div className="flex items-center gap-3">
            <div className="flex-1 h-px bg-slate-200" />
            <span className="text-xs text-slate-400 font-medium">OU copiez-collez le texte</span>
            <div className="flex-1 h-px bg-slate-200" />
          </div>

          {/* Text field */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <ClipboardPaste className="w-5 h-5 text-blue-600" />
                Coller le texte de l'offre d'emploi
              </CardTitle>
              <CardDescription>Copiez-collez le contenu complet de l'offre (depuis France Travail, Indeed, LinkedIn, etc.)</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <Textarea
                value={offerText}
                onChange={(e) => setOfferText(e.target.value)}
                placeholder="Collez ici le texte complet de l'offre d'emploi..."
                className="min-h-[200px] text-sm"
                data-testid="matching-offer-input"
              />
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-400">{offerText.length} caractères</span>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" onClick={() => setStep(1)}>
                    <ChevronLeft className="w-4 h-4 mr-1" /> Retour
                  </Button>
                  <Button
                    onClick={handleAnalyze}
                    disabled={analyzing || offerText.trim().length < 30}
                    className="bg-blue-600 hover:bg-blue-700 text-white"
                    data-testid="matching-analyze-btn"
                  >
                    {analyzing ? (
                      <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Analyse en cours...</>
                    ) : (
                      <><Zap className="w-4 h-4 mr-2" /> Analyser par IA</>
                    )}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* STEP 3: Analyse Results */}
      {step === 3 && analysis && (
        <div className="space-y-4" data-testid="matching-step-3">
          {/* Synthèse */}
          <Card className="border-blue-200 bg-blue-50/30">
            <CardContent className="pt-4">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center shrink-0">
                  <FileText className="w-5 h-5 text-blue-700" />
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900">{analysis.analyse?.titre_poste || "Offre analysée"}</h3>
                  <p className="text-sm text-slate-600 mt-0.5">{analysis.analyse?.entreprise} — {analysis.analyse?.localisation}</p>
                  <p className="text-sm text-slate-500 mt-1">{analysis.synthese}</p>
                  {offerUrl && (
                    <a href={offerUrl} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 text-xs text-blue-600 hover:underline mt-1" data-testid="matching-offer-link">
                      <Link className="w-3 h-3" /> Voir l'offre originale
                    </a>
                  )}
                  <div className="flex items-center gap-3 mt-2">
                    <Badge className="bg-blue-100 text-blue-800 text-xs">{analysis.analyse?.type_contrat}</Badge>
                    <Badge className="bg-emerald-100 text-emerald-800 text-xs">{analysis.analyse?.salaire || "Salaire non précisé"}</Badge>
                    <Badge className={`text-xs ${analysis.score_qualite_offre >= 70 ? "bg-emerald-100 text-emerald-800" : analysis.score_qualite_offre >= 40 ? "bg-amber-100 text-amber-800" : "bg-red-100 text-red-800"}`}>
                      Qualité: {analysis.score_qualite_offre}/100
                    </Badge>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Details */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {/* Missions */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-1.5"><Briefcase className="w-4 h-4 text-slate-500" /> Missions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-1">
                {(analysis.analyse?.missions || []).map((m, i) => (
                  <div key={i} className="flex items-start gap-2 text-sm text-slate-600">
                    <ChevronRight className="w-3 h-3 mt-1 text-slate-400 shrink-0" />{m}
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Compétences requises */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-1.5"><Target className="w-4 h-4 text-slate-500" /> Compétences requises</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-1.5">
                  {(analysis.analyse?.competences_requises || []).map((c, i) => (
                    <Badge key={i} variant="outline" className="text-xs">{c}</Badge>
                  ))}
                  {(analysis.analyse?.soft_skills_requis || []).map((s, i) => (
                    <Badge key={`s-${i}`} className="bg-violet-100 text-violet-700 text-xs">{s}</Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Infos manquantes */}
          {analysis.informations_manquantes?.length > 0 && (
            <Card className="border-amber-200">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-1.5 text-amber-700">
                  <AlertTriangle className="w-4 h-4" /> Informations manquantes ({analysis.informations_manquantes.length})
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {analysis.informations_manquantes.map((info, i) => (
                  <div key={i} className="p-2.5 rounded-lg bg-amber-50 border border-amber-100">
                    <p className="text-sm font-medium text-amber-800">{info.theme}</p>
                    <p className="text-xs text-amber-600 mt-0.5">{info.detail}</p>
                    <p className="text-xs text-slate-500 mt-0.5 italic">{info.importance}</p>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Recommandations */}
          {analysis.recommandations_candidat?.length > 0 && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-1.5"><Lightbulb className="w-4 h-4 text-amber-500" /> Recommandations</CardTitle>
              </CardHeader>
              <CardContent className="space-y-1.5">
                {analysis.recommandations_candidat.map((r, i) => (
                  <div key={i} className="flex items-start gap-2 text-sm text-slate-600">
                    <CheckCircle2 className="w-3.5 h-3.5 mt-0.5 text-emerald-500 shrink-0" />{r}
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Actions */}
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={() => setStep(2)}>
              <ChevronLeft className="w-4 h-4 mr-1" /> Modifier
            </Button>
            <Button onClick={handleMatch} disabled={matching} className="flex-1 bg-amber-600 hover:bg-amber-700 text-white" data-testid="matching-match-btn">
              {matching ? (
                <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Matching en cours...</>
              ) : (
                <><Target className="w-4 h-4 mr-2" /> Lancer le matching avec mon profil</>
              )}
            </Button>
          </div>
        </div>
      )}

      {/* STEP 4: Matching Results */}
      {step === 4 && matchResult && (
        <div className="space-y-4" data-testid="matching-step-4">
          {/* Score global */}
          <Card className={`border-2 ${matchResult.score_global >= 70 ? "border-emerald-300 bg-emerald-50/30" : matchResult.score_global >= 40 ? "border-amber-300 bg-amber-50/30" : "border-red-300 bg-red-50/30"}`}>
            <CardContent className="pt-5">
              <div className="flex items-center gap-4">
                <div className={`w-16 h-16 rounded-2xl flex items-center justify-center text-2xl font-bold ${
                  matchResult.score_global >= 70 ? "bg-emerald-100 text-emerald-700" : matchResult.score_global >= 40 ? "bg-amber-100 text-amber-700" : "bg-red-100 text-red-700"
                }`}>
                  {matchResult.score_global}%
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-slate-900">Score de compatibilité</h3>
                  <p className="text-sm text-slate-600 mt-0.5">{matchResult.verdict}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Detail scores */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[
              { key: "competences_techniques", label: "Compétences", icon: Target },
              { key: "soft_skills", label: "Soft Skills", icon: Users },
              { key: "experience", label: "Expérience", icon: Briefcase },
              { key: "formation", label: "Formation", icon: GraduationCap },
            ].map(({ key, label, icon: Icon }) => {
              const d = matchResult.details?.[key] || {};
              const score = d.score || 0;
              return (
                <Card key={key}>
                  <CardContent className="pt-3 pb-3 px-3 text-center">
                    <Icon className="w-5 h-5 mx-auto text-slate-400 mb-1" />
                    <div className={`text-xl font-bold ${score >= 70 ? "text-emerald-600" : score >= 40 ? "text-amber-600" : "text-red-500"}`}>
                      {score}%
                    </div>
                    <p className="text-xs text-slate-500">{label}</p>
                    <div className="mt-2 space-y-0.5">
                      {(d.forces || []).slice(0, 2).map((f, i) => (
                        <p key={i} className="text-[10px] text-emerald-600 truncate">+ {f}</p>
                      ))}
                      {(d.lacunes || []).slice(0, 1).map((l, i) => (
                        <p key={i} className="text-[10px] text-red-500 truncate">- {l}</p>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          {/* Recommandations */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-1.5"><Lightbulb className="w-4 h-4 text-amber-500" /> Recommandations personnalisées</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {(matchResult.recommandations || []).map((r, i) => {
                const typeColors = {
                  cv: "bg-blue-100 text-blue-700",
                  formation: "bg-violet-100 text-violet-700",
                  entretien: "bg-emerald-100 text-emerald-700",
                  profil: "bg-amber-100 text-amber-700",
                };
                return (
                  <div key={i} className="flex items-start gap-2.5 p-2.5 rounded-lg bg-slate-50 border border-slate-100">
                    <Badge className={`${typeColors[r.type] || "bg-slate-100 text-slate-700"} text-[10px] shrink-0 mt-0.5`}>
                      {r.type === "cv" ? "CV" : r.type === "formation" ? "Formation" : r.type === "entretien" ? "Entretien" : "Profil"}
                    </Badge>
                    <p className="text-sm text-slate-700">{r.conseil}</p>
                  </div>
                );
              })}
            </CardContent>
          </Card>

          {/* Message d'accroche */}
          {matchResult.message_accroche && (
            <Card className="border-blue-200 bg-blue-50/30">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-1.5"><MessageSquare className="w-4 h-4 text-blue-600" /> Message d'accroche suggéré</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-700 italic leading-relaxed">"{matchResult.message_accroche}"</p>
                <Button
                  variant="outline" size="sm" className="mt-2"
                  onClick={() => { navigator.clipboard.writeText(matchResult.message_accroche); toast.success("Copié !"); }}
                  data-testid="matching-copy-message"
                >
                  Copier le message
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Actions finales */}
          <div className="flex gap-2">
            <Button variant="outline" onClick={resetAll} className="flex-1" data-testid="matching-new-analysis">
              Nouvelle analyse
            </Button>
            <Button
              onClick={handleSaveCandidature}
              disabled={savingCandidature || candidatureSaved}
              className={`flex-1 ${candidatureSaved ? "bg-emerald-100 text-emerald-700 border border-emerald-300" : "bg-blue-600 hover:bg-blue-700 text-white"}`}
              data-testid="matching-save-candidature"
            >
              {savingCandidature ? (
                <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Sauvegarde...</>
              ) : candidatureSaved ? (
                <><CheckCircle2 className="w-4 h-4 mr-2" /> Sauvegardée</>
              ) : (
                <><BookmarkPlus className="w-4 h-4 mr-2" /> Sauvegarder dans Mes Candidatures</>
              )}
            </Button>
          </div>
        </div>
      )}

      {/* History */}
      {history.length > 0 && step === 1 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-slate-700">Analyses récentes</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {history.slice(0, 5).map((h) => (
              <div key={h.id} className="flex items-center justify-between p-2 rounded-lg bg-slate-50 border border-slate-100">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-800 truncate">{h.titre}</p>
                  <div className="flex items-center gap-3 text-xs text-slate-500">
                    <span>{h.entreprise}</span>
                    <span>Qualité: {h.score_qualite}/100</span>
                    {h.score_matching != null && (
                      <span className={`font-semibold ${h.score_matching >= 70 ? "text-emerald-600" : h.score_matching >= 40 ? "text-amber-600" : "text-red-500"}`}>
                        Match: {h.score_matching}%
                      </span>
                    )}
                  </div>
                </div>
                <span className="text-xs text-slate-400 shrink-0 ml-2">{new Date(h.created_at).toLocaleDateString('fr-FR')}</span>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default JobMatchingView;
