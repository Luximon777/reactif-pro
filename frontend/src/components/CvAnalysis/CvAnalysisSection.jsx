import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/App";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Target, Briefcase, Clock, Star, Sparkles, Zap, Award,
  CheckCircle2, AlertCircle, Play, FileDown, FileText, Shield, BarChart3,
  Link as LinkIcon, RefreshCw
} from "lucide-react";
import { toast } from "sonner";
import CvPreview from "./CvPreview";

const CV_MODELS_CONFIG = [
  { key: "classique", name: "CV Classique", desc: "Chronologique, sobre et professionnel", color: "bg-blue-50 border-blue-200 text-blue-700", icon: FileText },
  { key: "competences", name: "CV Competences", desc: "Axe sur les savoir-faire et savoir-etre", color: "bg-emerald-50 border-emerald-200 text-emerald-700", icon: Zap },
  { key: "transversale", name: "CV Transversal", desc: "Competences transferables et transversales", color: "bg-violet-50 border-violet-200 text-violet-700", icon: Target },
  { key: "nouvelle_generation", name: "CV Nouvelle Generation", desc: "Profil dynamique : intentions, preuves, potentiel, valeurs", color: "bg-amber-50 border-amber-200 text-amber-700", icon: Star },
];

const CvAnalysisSection = ({ token, onComplete }) => {
  const [uploading, setUploading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [cvModels, setCvModels] = useState(null);
  const [viewingModel, setViewingModel] = useState(null);
  const [elapsed, setElapsed] = useState(0);
  const [currentStep, setCurrentStep] = useState(0);
  const [uploadError, setUploadError] = useState(null);
  const [serverStep, setServerStep] = useState("");
  const [loadingPrevious, setLoadingPrevious] = useState(true);
  const [generatingModel, setGeneratingModel] = useState(null);
  const [selectedGenModels, setSelectedGenModels] = useState([]);
  const [genProgress, setGenProgress] = useState(null);
  const [jobOfferText, setJobOfferText] = useState("");
  const [scrapingOffer, setScrapingOffer] = useState(false);

  const STEPS = [
    { at: 0, label: "Envoi du fichier...", icon: FileText },
    { at: 3, label: "Extraction du contenu...", icon: FileText },
    { at: 8, label: "Identification des savoir-faire...", icon: Briefcase },
    { at: 15, label: "Détection des savoir-être...", icon: Star },
    { at: 22, label: "Analyse des compétences transversales...", icon: Target },
    { at: 30, label: "Suggestions d'offres d'emploi...", icon: Briefcase },
    { at: 38, label: "Remplissage du Passeport...", icon: Award },
    { at: 45, label: "Finalisation de l'analyse...", icon: CheckCircle2 },
  ];

  useEffect(() => {
    let timer;
    if (uploading) {
      setElapsed(0);
      setCurrentStep(0);
      timer = setInterval(() => {
        setElapsed(prev => {
          const next = prev + 1;
          const stepIdx = STEPS.filter(s => s.at <= next).length - 1;
          if (stepIdx >= 0) setCurrentStep(stepIdx);
          return next;
        });
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [uploading]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    const loadPrevious = async () => {
      try {
        const [analysisRes, modelsRes] = await Promise.all([
          axios.get(`${API}/cv/latest-analysis?token=${token}`),
          axios.get(`${API}/cv/models?token=${token}`)
        ]);
        if (analysisRes.data.has_analysis) {
          setAnalysisResult(analysisRes.data.result);
        }
        if (modelsRes.data.models && Object.keys(modelsRes.data.models).length > 0) {
          setCvModels(modelsRes.data);
        }
      } catch (err) {
        console.error("Error loading previous analysis:", err);
      }
      setLoadingPrevious(false);
    };
    loadPrevious();
  }, [token]);

  const pollForResult = async (jobId) => {
    const maxPolls = 120;
    for (let i = 0; i < maxPolls; i++) {
      await new Promise(r => setTimeout(r, 3000));
      try {
        const res = await axios.get(`${API}/cv/analyze/status?token=${token}&job_id=${jobId}`);
        if (res.data.step) setServerStep(res.data.step);
        if (res.data.status === "completed") return res.data.result;
        if (res.data.status === "failed") throw new Error(res.data.error || "L'analyse a échoué");
      } catch (err) {
        const status = err.response?.status;
        if (status === 404 || status === 502 || status === 503 || status === 504 || !err.response) {
          continue;
        }
        throw err;
      }
    }
    throw new Error("L'analyse a pris trop de temps. Réessayez.");
  };

  const extractTextFromFile = async (file) => {
    const ext = file.name.toLowerCase().split(".").pop();

    if (ext === "txt") {
      return await file.text();
    }

    if (ext === "docx" || ext === "doc") {
      const mammoth = await import("mammoth");
      const arrayBuffer = await file.arrayBuffer();
      const result = await mammoth.extractRawText({ arrayBuffer });
      return result.value;
    }

    if (ext === "pdf") {
      const arrayBuffer = await file.arrayBuffer();
      const bytes = new Uint8Array(arrayBuffer);
      let binary = "";
      for (let i = 0; i < bytes.length; i++) {
        binary += String.fromCharCode(bytes[i]);
      }
      const base64 = btoa(binary);
      for (let attempt = 0; attempt < 3; attempt++) {
        try {
          const res = await axios.post(`${API}/cv/extract-text-b64?token=${token}`, {
            data: base64,
            filename: file.name,
          }, { timeout: 30000 });
          return res.data.text;
        } catch (err) {
          const s = err.response?.status;
          if (attempt < 2 && (s === 502 || s === 503 || s === 504 || !err.response)) {
            await new Promise(r => setTimeout(r, 2000));
            continue;
          }
          throw err;
        }
      }
    }

    throw new Error("Format non supporté");
  };

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > 10 * 1024 * 1024) {
      toast.error("Fichier trop volumineux (max 10 Mo).");
      return;
    }

    const ext = file.name.toLowerCase().split(".").pop();
    if (!["pdf", "docx", "doc", "txt"].includes(ext)) {
      toast.error("Format non supporté. Utilisez PDF, DOCX ou TXT.");
      return;
    }

    setUploading(true);
    setAnalysisResult(null);
    setUploadError(null);
    setServerStep("Lecture du fichier...");

    try {
      const cvText = await extractTextFromFile(file);
      if (!cvText || cvText.trim().length < 50) {
        throw new Error("Le fichier ne contient pas assez de texte exploitable.");
      }

      setServerStep("Envoi du texte au serveur...");

      let jobId;
      for (let attempt = 0; attempt < 3; attempt++) {
        try {
          const startRes = await axios.post(`${API}/cv/analyze-text?token=${token}`, {
            text: cvText,
            filename: file.name,
          }, { timeout: 15000 });
          jobId = startRes.data.job_id;
          break;
        } catch (err) {
          const s = err.response?.status;
          if (attempt < 2 && (s === 502 || s === 503 || s === 504 || !err.response)) {
            await new Promise(r => setTimeout(r, 2000));
            continue;
          }
          throw err;
        }
      }

      setServerStep("Analyse IA en cours...");
      const result = await pollForResult(jobId);
      setAnalysisResult(result);
      if (result.modele_suggere && !selectedGenModels.includes(result.modele_suggere)) {
        setSelectedGenModels([result.modele_suggere]);
      }
      toast.success(`CV audite : score ${result.score_global_cv || 0}/100 — ${result.savoir_faire_count} savoir-faire, ${result.savoir_etre_count} savoir-etre detectes`);
      if (onComplete) onComplete();
    } catch (err) {
      let msg = err.response?.data?.detail || err.message || "Erreur lors de l'analyse du CV.";
      if (msg.toLowerCase().includes("budget")) {
        msg = "Le crédit d'analyse IA est temporairement épuisé. Rechargez votre clé dans Profil > Universal Key.";
      }
      setUploadError(msg);
      toast.error(msg);
    }
    setUploading(false);
    e.target.value = "";
  };

  const toggleGenModel = (key) => {
    setSelectedGenModels(prev =>
      prev.includes(key) ? prev.filter(k => k !== key) : [...prev, key]
    );
  };

  const generateSelectedModels = async () => {
    if (selectedGenModels.length === 0) return;
    setGeneratingModel(true);
    setGenProgress({ current: 0, total: selectedGenModels.length, currentModel: "" });
    try {
      const startRes = await axios.post(`${API}/cv/generate-models?token=${token}`, {
        model_types: selectedGenModels,
        job_offer: jobOfferText || undefined,
      }, { timeout: 15000 });
      const jobId = startRes.data.job_id;

      for (let i = 0; i < 120; i++) {
        await new Promise(r => setTimeout(r, 2000));
        try {
          const res = await axios.get(`${API}/cv/generate-models/status?token=${token}&job_id=${jobId}`);
          setGenProgress({ current: res.data.progress, total: res.data.total, currentModel: res.data.current_model || "" });
          if (res.data.status === "completed") {
            const modelsRes = await axios.get(`${API}/cv/models?token=${token}`);
            if (modelsRes.data.models) setCvModels(modelsRes.data);
            toast.success(`${selectedGenModels.length} CV optimise${selectedGenModels.length > 1 ? "s" : ""} par IA`);
            setSelectedGenModels([]);
            break;
          }
          if (res.data.status === "failed") {
            throw new Error(res.data.error || "La génération a échoué");
          }
        } catch (err) {
          if (err.response?.status === 502 || err.response?.status === 504 || !err.response) continue;
          throw err;
        }
      }
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || "Erreur lors de la génération.";
      toast.error(msg);
    }
    setGeneratingModel(false);
    setGenProgress(null);
  };

  const downloadModel = (key) => {
    window.open(`${API}/cv/download/${key}?token=${token}`, '_blank');
  };

  const downloadModelPdf = (key) => {
    window.open(`${API}/cv/download-pdf/${key}?token=${token}`, '_blank');
  };

  return (
    <div className="space-y-4">
      {loadingPrevious && (
        <div className="flex items-center justify-center py-4">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-sm text-slate-500">Chargement...</span>
        </div>
      )}
      {/* Upload Zone */}
      <div className={`relative border-2 border-dashed rounded-xl transition-all overflow-hidden ${uploading ? "border-blue-400 bg-gradient-to-br from-blue-50 to-indigo-50 p-0" : "border-slate-300 hover:border-[#1e3a5f] hover:bg-slate-50 p-6"}`}>
        {!uploading && (
          <input
            type="file"
            accept=".pdf,.docx,.doc,.txt"
            onChange={handleUpload}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            data-testid="cv-upload-input"
          />
        )}
        {uploading ? (
          <div className="p-6 space-y-4" data-testid="cv-upload-progress">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse" />
                <span className="text-sm font-semibold text-blue-800">Analyse IA en cours</span>
              </div>
              <div className="flex items-center gap-1.5 bg-white/80 px-3 py-1 rounded-full shadow-sm">
                <Clock className="w-4 h-4 text-blue-600" />
                <span className="text-lg font-mono font-bold text-blue-700" data-testid="cv-timer">
                  {Math.floor(elapsed / 60)}:{(elapsed % 60).toString().padStart(2, '0')}
                </span>
              </div>
            </div>
            <div className="w-full h-2 bg-blue-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full transition-all duration-1000 ease-out"
                style={{ width: `${Math.min((elapsed / 120) * 100, 95)}%` }}
              />
            </div>
            {serverStep && (
              <div className="text-xs text-indigo-600 font-medium bg-white/60 px-2 py-1 rounded">
                {serverStep}
              </div>
            )}
            <div className="space-y-1.5">
              {STEPS.map((step, idx) => {
                const StepIcon = step.icon;
                const isDone = idx < currentStep;
                const isCurrent = idx === currentStep;
                if (idx > currentStep + 1) return null;
                return (
                  <div key={idx} className={`flex items-center gap-2 py-1 px-2 rounded-lg transition-all ${isCurrent ? "bg-white/70 shadow-sm" : ""}`}>
                    <div className={`w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 ${isDone ? "bg-emerald-500" : isCurrent ? "bg-blue-500 animate-pulse" : "bg-slate-300"}`}>
                      {isDone ? (
                        <CheckCircle2 className="w-3 h-3 text-white" />
                      ) : (
                        <StepIcon className="w-3 h-3 text-white" />
                      )}
                    </div>
                    <span className={`text-xs ${isDone ? "text-emerald-700 font-medium" : isCurrent ? "text-blue-800 font-semibold" : "text-slate-400"}`}>
                      {step.label}
                    </span>
                    {isCurrent && <div className="ml-auto w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />}
                  </div>
                );
              })}
            </div>
          </div>
        ) : (
          <div>
            <FileDown className="w-8 h-8 mx-auto text-slate-400 mb-2" />
            <p className="text-sm font-medium text-slate-700">Chargez votre CV (PDF, DOCX, TXT)</p>
            <p className="text-xs text-slate-400">L'IA auditera votre CV selon 10 criteres professionnels et proposera une optimisation percutante</p>
          </div>
        )}
      </div>

      {/* Error display */}
      {uploadError && !uploading && !analysisResult && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4" data-testid="cv-upload-error">
          <div className="flex items-center gap-2 mb-2">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <h4 className="font-semibold text-red-800 text-sm">Erreur d'analyse</h4>
          </div>
          <p className="text-sm text-red-700">{uploadError}</p>
          <p className="text-xs text-red-500 mt-2">Cliquez sur la zone ci-dessus pour réessayer avec votre CV.</p>
        </div>
      )}

      {/* Analysis Result Summary */}
      {analysisResult && (
        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 space-y-3" data-testid="cv-analysis-result">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-600" />
            <h4 className="font-semibold text-emerald-800 text-sm">Analyse terminée — {analysisResult.filename}</h4>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-center">
            <div className="bg-white rounded-lg p-2">
              <p className="text-xl font-bold text-sky-600">{analysisResult.savoir_faire_count}</p>
              <p className="text-[10px] text-slate-500">Savoir-faire</p>
            </div>
            <div className="bg-white rounded-lg p-2">
              <p className="text-xl font-bold text-rose-500">{analysisResult.savoir_etre_count}</p>
              <p className="text-[10px] text-slate-500">Savoir-être</p>
            </div>
            <div className="bg-white rounded-lg p-2">
              <p className="text-xl font-bold text-blue-600">{analysisResult.experiences_count}</p>
              <p className="text-[10px] text-slate-500">Expériences</p>
            </div>
            <div className="bg-white rounded-lg p-2">
              <p className="text-xl font-bold text-emerald-600">{analysisResult.formations_suggestions?.length || 0}</p>
              <p className="text-[10px] text-slate-500">Formations suggérées</p>
            </div>
          </div>
          {analysisResult.competences_transversales?.length > 0 && (
            <div>
              <p className="text-xs font-medium text-violet-700 mb-1">Compétences transversales identifiées :</p>
              <div className="flex flex-wrap gap-1">
                {analysisResult.competences_transversales.map((c, i) => (
                  <span key={i} className="text-xs bg-violet-100 text-violet-700 px-2 py-0.5 rounded-full">{c}</span>
                ))}
              </div>
            </div>
          )}
          {analysisResult.formations_suggestions?.length > 0 && (
            <div>
              <p className="text-xs font-medium text-amber-700 mb-1">Besoins de formation identifiés :</p>
              <div className="space-y-1">
                {analysisResult.formations_suggestions.map((f, i) => (
                  <div key={i} className="flex items-start gap-2 text-xs bg-white rounded-lg p-2">
                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${f.priority === "haute" ? "bg-red-100 text-red-700" : f.priority === "moyenne" ? "bg-amber-100 text-amber-700" : "bg-slate-100 text-slate-600"}`}>{f.priority}</span>
                    <div>
                      <p className="font-medium text-slate-800">{f.title}</p>
                      <p className="text-slate-500">{f.reason}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          {analysisResult.offres_emploi_suggerees?.length > 0 && (
            <div data-testid="cv-suggested-jobs">
              <p className="text-xs font-medium text-blue-700 mb-1">Offres d'emploi suggérées :</p>
              <div className="space-y-1">
                {analysisResult.offres_emploi_suggerees.map((offre, i) => (
                  <div key={i} className="flex items-start gap-2 text-xs bg-white rounded-lg p-2 border border-blue-100">
                    <Briefcase className="w-4 h-4 text-blue-500 flex-shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <p className="font-medium text-slate-800">{offre.titre}</p>
                        {offre.type_contrat && (
                          <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-700">{offre.type_contrat}</span>
                        )}
                      </div>
                      {offre.secteur && <p className="text-slate-500">{offre.secteur}</p>}
                      {offre.description_courte && <p className="text-slate-400 mt-0.5">{offre.description_courte}</p>}
                      {offre.competences_requises?.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-1">
                          {offre.competences_requises.map((c, j) => (
                            <span key={j} className="text-[10px] bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded-full">{c}</span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          <p className="text-xs text-emerald-600 font-medium">Passeport automatiquement complete avec les donnees extraites</p>
        </div>
      )}

      {/* CV Audit - 10 Rules */}
      {analysisResult?.audit_cv?.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-xl p-4 space-y-3" data-testid="cv-audit-section">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Shield className="w-5 h-5 text-[#1e3a5f]" />
              <h4 className="font-semibold text-slate-800 text-sm">Audit CV — 10 criteres professionnels</h4>
            </div>
            {analysisResult.score_global_cv != null && (
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-500">Score global</span>
                <span className={`text-lg font-bold ${analysisResult.score_global_cv >= 70 ? "text-emerald-600" : analysisResult.score_global_cv >= 40 ? "text-amber-600" : "text-red-600"}`} data-testid="cv-audit-score">
                  {analysisResult.score_global_cv}/100
                </span>
              </div>
            )}
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {analysisResult.audit_cv.map((item, i) => {
              const statusColor = item.statut === "ok" ? "bg-emerald-50 border-emerald-200" : item.statut === "ameliorable" ? "bg-amber-50 border-amber-200" : "bg-red-50 border-red-200";
              const statusBadge = item.statut === "ok" ? "bg-emerald-100 text-emerald-700" : item.statut === "ameliorable" ? "bg-amber-100 text-amber-700" : "bg-red-100 text-red-700";
              const statusLabel = item.statut === "ok" ? "OK" : item.statut === "ameliorable" ? "A ameliorer" : "Absent";
              return (
                <div key={i} className={`p-2.5 rounded-lg border ${statusColor} space-y-1`} data-testid={`audit-rule-${i}`}>
                  <div className="flex items-center justify-between">
                    <p className="text-xs font-semibold text-slate-800">{item.regle}</p>
                    <div className="flex items-center gap-1.5">
                      <span className="text-[10px] font-bold text-slate-500">{item.score}/10</span>
                      <span className={`text-[9px] px-1.5 py-0.5 rounded-full font-medium ${statusBadge}`}>{statusLabel}</span>
                    </div>
                  </div>
                  <p className="text-[10px] text-slate-600">{item.diagnostic}</p>
                  {item.statut !== "ok" && item.recommandation && (
                    <p className="text-[10px] text-blue-700 font-medium">Conseil : {item.recommandation}</p>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Suggested model */}
      {analysisResult?.modele_suggere && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-3 flex items-start gap-3" data-testid="cv-model-suggestion">
          <BarChart3 className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-xs font-semibold text-blue-800">
              Modele recommande : <span className="text-blue-600">{CV_MODELS_CONFIG.find(c => c.key === analysisResult.modele_suggere)?.name || analysisResult.modele_suggere}</span>
            </p>
            {analysisResult.raison_modele && (
              <p className="text-[10px] text-blue-600 mt-0.5">{analysisResult.raison_modele}</p>
            )}
          </div>
        </div>
      )}

      {/* CV Models - Generate on demand */}
      {analysisResult && (
        <div className="space-y-3" data-testid="cv-models-section">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-blue-600" />
            <h4 className="text-sm font-semibold text-slate-800">Optimiser votre CV par IA</h4>
          </div>
          <p className="text-xs text-slate-500">Re'Actif Pro IA optimise et adapte votre CV pour passer les filtres ATS des recruteurs. Selectionnez un modele et collez une offre d'emploi pour une optimisation ciblee.</p>

          {/* Job offer input for ATS optimization */}
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-3 space-y-2" data-testid="job-offer-input">
            <label className="text-xs font-semibold text-slate-700 flex items-center gap-1.5">
              <Target className="w-3.5 h-3.5 text-[#1e3a5f]" />
              Offre d'emploi cible (optionnel — pour optimisation ATS ciblee)
            </label>
            <textarea
              className="w-full text-xs border border-slate-200 rounded-lg p-2 resize-none focus:ring-1 focus:ring-[#1e3a5f] focus:border-[#1e3a5f] placeholder:text-slate-400"
              rows={3}
              placeholder="Collez un lien (URL) vers l'offre ou le texte de l'offre d'emploi..."
              value={jobOfferText}
              onChange={(e) => setJobOfferText(e.target.value)}
              data-testid="job-offer-textarea"
            />
            {/* URL detection and scraping */}
            {jobOfferText && /^https?:\/\/\S+$/i.test(jobOfferText.trim()) && !scrapingOffer && (
              <button
                type="button"
                onClick={async () => {
                  setScrapingOffer(true);
                  try {
                    const res = await axios.get(`${API}/scrape/job-offer?url=${encodeURIComponent(jobOfferText.trim())}`);
                    if (res.data.success) {
                      setJobOfferText(res.data.text);
                      toast.success("Offre d'emploi importee depuis le lien !");
                    } else {
                      toast.error(res.data.error || "Impossible d'importer l'offre");
                    }
                  } catch { toast.error("Erreur lors de l'import"); }
                  setScrapingOffer(false);
                }}
                className="flex items-center gap-1.5 text-xs text-[#1e3a5f] font-medium hover:underline"
                data-testid="scrape-offer-btn"
              >
                <LinkIcon className="w-3 h-3" /> Importer le contenu de l'offre depuis ce lien
              </button>
            )}
            {scrapingOffer && (
              <p className="text-xs text-blue-600 flex items-center gap-1.5">
                <RefreshCw className="w-3 h-3 animate-spin" /> Import en cours...
              </p>
            )}
            {jobOfferText && !/^https?:\/\/\S+$/i.test(jobOfferText.trim()) && (
              <p className="text-[10px] text-emerald-600 font-medium flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3" /> L'IA integrera les mots-cles de cette offre pour optimiser le passage ATS
              </p>
            )}
          </div>

          {/* Generation progress */}
          {generatingModel && genProgress && (
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-3" data-testid="cv-gen-progress">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                <p className="text-xs font-medium text-blue-800">
                  Optimisation en cours ({genProgress.current}/{genProgress.total})
                  {genProgress.currentModel && ` — ${CV_MODELS_CONFIG.find(c => c.key === genProgress.currentModel)?.name || genProgress.currentModel}`}
                </p>
              </div>
              <div className="w-full bg-blue-200 rounded-full h-1.5">
                <div className="bg-blue-600 h-1.5 rounded-full transition-all" style={{ width: `${Math.max(5, (genProgress.current / genProgress.total) * 100)}%` }} />
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {CV_MODELS_CONFIG.map((cv) => {
              const hasModel = cvModels?.models?.[cv.key];
              const isSelected = selectedGenModels.includes(cv.key);
              const Icon = cv.icon;
              return (
                <div
                  key={cv.key}
                  role="button"
                  tabIndex={0}
                  onClick={() => !generatingModel && toggleGenModel(cv.key)}
                  className={`p-3 rounded-lg border-2 text-left transition-all cursor-pointer ${isSelected ? `${cv.color} border-current shadow-sm` : hasModel ? `${cv.color} border-current/30` : "bg-white border-slate-200 hover:border-slate-400"} ${generatingModel ? "opacity-60 cursor-not-allowed" : ""}`}
                  data-testid={`cv-model-${cv.key}`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 ${isSelected ? "border-current bg-current/20" : "border-slate-300"}`}>
                      {isSelected && <CheckCircle2 className="w-3.5 h-3.5" />}
                    </div>
                    <Icon className="w-4 h-4 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="text-xs font-semibold truncate">{cv.name}</p>
                        {hasModel && <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-emerald-100 text-emerald-700 font-medium flex-shrink-0">Optimise</span>}
                      </div>
                      <p className="text-[10px] opacity-70">{cv.desc}</p>
                    </div>
                  </div>
                  {hasModel && (
                    <div className="flex gap-1 mt-2 ml-8" onClick={(e) => e.stopPropagation()}>
                      <Button variant="outline" size="sm" className="text-[10px] h-6 px-2" onClick={() => setViewingModel(viewingModel === cv.key ? null : cv.key)} data-testid={`view-cv-${cv.key}`}>
                        <Play className="w-3 h-3 mr-0.5" /> Voir
                      </Button>
                      <Button variant="outline" size="sm" className="text-[10px] h-6 px-2" onClick={() => downloadModel(cv.key)} data-testid={`download-cv-${cv.key}`}>
                        <FileDown className="w-3 h-3 mr-0.5" /> Word
                      </Button>
                      <Button variant="outline" size="sm" className="text-[10px] h-6 px-2 text-red-600 border-red-200 hover:bg-red-50" onClick={() => downloadModelPdf(cv.key)} data-testid={`download-pdf-${cv.key}`}>
                        <FileDown className="w-3 h-3 mr-0.5" /> PDF
                      </Button>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Generate button */}
          {!generatingModel && (
            <div className="flex items-center justify-between pt-1">
              <p className="text-xs text-slate-500">
                {selectedGenModels.length === 0
                  ? "Selectionnez au moins un modele"
                  : `${selectedGenModels.length} modele${selectedGenModels.length > 1 ? "s" : ""} selectionne${selectedGenModels.length > 1 ? "s" : ""}`}
              </p>
              <Button
                size="sm"
                className="bg-[#1e3a5f] hover:bg-[#2a4a6f] text-white"
                onClick={generateSelectedModels}
                disabled={selectedGenModels.length === 0}
                data-testid="cv-generate-btn"
              >
                <Sparkles className="w-4 h-4 mr-1" />
                Optimiser {selectedGenModels.length > 0 ? `(${selectedGenModels.length})` : ""}
              </Button>
            </div>
          )}
        </div>
      )}

      {/* ATS Strategy Section */}
      {(cvModels?.models && Object.values(cvModels.models).some(v => v)) && (
        <div className="bg-gradient-to-r from-[#1e3a5f] to-[#2a5a8f] rounded-xl p-4 text-white space-y-3" data-testid="ats-strategy-section">
          <div className="flex items-center gap-2">
            <Shield className="w-5 h-5" />
            <h4 className="font-semibold text-sm">Strategie Re'Actif Pro — Optimisation ATS</h4>
          </div>
          <p className="text-xs text-white/80">Votre CV est optimise par l'IA pour passer les filtres automatiques (ATS) des recruteurs : mots-cles adaptes, format simple, intitules clairs, competences explicites.</p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
            <div className="bg-white/10 rounded-lg p-2.5 backdrop-blur-sm">
              <p className="text-[10px] font-bold text-white/60 uppercase tracking-wider">Canal ATS</p>
              <p className="text-xs text-white mt-1">CV optimise mots-cles</p>
              <p className="text-[10px] text-white/60 mt-0.5">Format Word/PDF simple, intitules exacts, competences explicites</p>
            </div>
            <div className="bg-white/10 rounded-lg p-2.5 backdrop-blur-sm">
              <p className="text-[10px] font-bold text-white/60 uppercase tracking-wider">Canal Reseau</p>
              <p className="text-xs text-white mt-1">Recommandations et contacts</p>
              <p className="text-[10px] text-white/60 mt-0.5">Activez votre reseau : l'ATS standardise, le reseau humanise</p>
            </div>
            <div className="bg-white/10 rounded-lg p-2.5 backdrop-blur-sm">
              <p className="text-[10px] font-bold text-white/60 uppercase tracking-wider">Approche directe</p>
              <p className="text-xs text-white mt-1">Mail, LinkedIn, appel</p>
              <p className="text-[10px] text-white/60 mt-0.5">Demarquez-vous au-dela des filtres automatiques</p>
            </div>
          </div>
        </div>
      )}
      {!analysisResult && cvModels?.models && Object.values(cvModels.models).some(v => v) && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {CV_MODELS_CONFIG.map((cv) => {
            const hasModel = cvModels?.models?.[cv.key];
            const Icon = cv.icon;
            if (!hasModel) return null;
            return (
              <div key={cv.key} className={`flex items-center justify-between p-3 rounded-lg border ${cv.color}`} data-testid={`cv-model-${cv.key}`}>
                <div className="flex items-center gap-3">
                  <Icon className="w-5 h-5 flex-shrink-0" />
                  <div>
                    <p className="text-sm font-semibold">{cv.name}</p>
                    <p className="text-xs opacity-70">{cv.desc}</p>
                  </div>
                </div>
                <div className="flex gap-1">
                  <Button variant="ghost" size="sm" onClick={() => setViewingModel(viewingModel === cv.key ? null : cv.key)} data-testid={`view-cv-${cv.key}`}>
                    <Play className="w-4 h-4" />
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => downloadModel(cv.key)} data-testid={`download-cv-${cv.key}`}>
                    <FileDown className="w-4 h-4" />
                  </Button>
                  <Button variant="ghost" size="sm" className="text-red-600" onClick={() => downloadModelPdf(cv.key)} data-testid={`download-pdf-${cv.key}`}>
                    <FileText className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* CV Preview */}
      {viewingModel && cvModels?.models?.[viewingModel] && (
        <div className="bg-white border rounded-xl p-4 max-h-96 overflow-y-auto" data-testid="cv-preview">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-semibold text-sm text-slate-800">{CV_MODELS_CONFIG.find(c => c.key === viewingModel)?.name}</h4>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={() => downloadModel(viewingModel)} data-testid="cv-preview-download-word">
                <FileDown className="w-3 h-3 mr-1" /> Word
              </Button>
              <Button variant="outline" size="sm" className="text-red-600 border-red-200 hover:bg-red-50" onClick={() => downloadModelPdf(viewingModel)} data-testid="cv-preview-download-pdf">
                <FileDown className="w-3 h-3 mr-1" /> PDF
              </Button>
              <Button variant="ghost" size="sm" onClick={() => setViewingModel(null)}>Fermer</Button>
            </div>
          </div>
          <CvPreview data={cvModels.models[viewingModel]} />
        </div>
      )}
    </div>
  );
};

export default CvAnalysisSection;
