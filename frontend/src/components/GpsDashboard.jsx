import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Input } from "@/components/ui/input";
import {
  User, Target, TrendingUp, Briefcase, Sparkles, Zap, Award,
  ChevronRight, CheckCircle2, Circle, Play, Brain, Route,
  FileText, Heart, Compass, Users, Send, Loader2, MessageSquare,
  ArrowRight, Shield, FolderLock, ExternalLink
} from "lucide-react";
import { toast } from "sonner";

const JOURNEY_STEPS = [
  {
    id: 1,
    title: "Comprendre qui je suis",
    subtitle: "Personnalité, valeurs et compétences",
    icon: User,
    color: "violet",
    items: [
      { label: "Importer et analyser mon CV", key: "cv", path: "/dashboard/trajectoire?sub=cv" },
      { label: "Passer le test D'CLIC PRO", key: "dclic", action: "dclic" },
      { label: "Identifier mes centres d'intérêt", key: "centres", path: "/dashboard/trajectoire?sub=centres" },
    ],
    cta: "Commencer",
    ctaActive: "Continuer",
    ctaDone: "Revoir",
  },
  {
    id: 2,
    title: "Me valoriser",
    subtitle: "Prouver mes soft skills par des exemples concrets",
    icon: Award,
    color: "emerald",
    items: [
      { label: "Prouver mes soft skills avec des exemples", key: "softskills", path: "/dashboard/profil" },
      { label: "Générer mon CV par IA", key: "cv_gen", path: "/dashboard/trajectoire?sub=generer" },
      { label: "Construire mon pitch pro", key: "pitch", path: "/dashboard/profil" },
    ],
    cta: "Prouver mes soft skills",
    ctaActive: "Illustrer mes expériences",
    ctaDone: "Enrichir mes preuves",
  },
  {
    id: 3,
    title: "Clarifier ma vision de mon profil compétences",
    subtitle: "Compétences, trajectoire et pistes métiers",
    icon: Target,
    color: "blue",
    items: [
      { label: "Explorer mes compétences", key: "competences", path: "/dashboard/competences" },
      { label: "Tracer ma trajectoire", key: "trajectoire", path: "/dashboard/trajectoire?sub=trajectoire" },
      { label: "Découvrir les métiers possibles", key: "passerelles", path: "/dashboard/profil" },
    ],
    cta: "Explorer mes pistes",
    ctaActive: "Continuer l'exploration",
    ctaDone: "Enrichir mes pistes",
  },
  {
    id: 4,
    title: "Passer a l'action",
    subtitle: "Opportunités, réseau et candidatures",
    icon: Briefcase,
    color: "amber",
    items: [
      { label: "Consulter les opportunités", key: "opportunites", path: "/dashboard/opportunites" },
      { label: "Participer au Job Dating", key: "jobdating", path: "/dashboard/job-dating" },
      { label: "Rejoindre le réseau UBUNTOO", key: "ubuntoo", action: "ubuntoo" },
    ],
    cta: "Trouver des opportunites",
    ctaActive: "Voir les offres",
    ctaDone: "Continuer",
  },
];

const COLOR_MAP = {
  violet: { bg: "bg-violet-50", border: "border-violet-200", text: "text-violet-700", iconBg: "bg-violet-100", gradient: "from-violet-600 to-purple-600", light: "bg-violet-500" },
  blue: { bg: "bg-blue-50", border: "border-blue-200", text: "text-blue-700", iconBg: "bg-blue-100", gradient: "from-blue-600 to-cyan-600", light: "bg-blue-500" },
  emerald: { bg: "bg-emerald-50", border: "border-emerald-200", text: "text-emerald-700", iconBg: "bg-emerald-100", gradient: "from-emerald-600 to-teal-600", light: "bg-emerald-500" },
  amber: { bg: "bg-amber-50", border: "border-amber-200", text: "text-amber-700", iconBg: "bg-amber-100", gradient: "from-amber-600 to-orange-600", light: "bg-amber-500" },
};

const StepCoach = ({ token, stepId, stepTitle }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);

  const sendMessage = async (text) => {
    if (!text.trim()) return;
    const userMsg = { role: "user", content: text };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    try {
      const res = await axios.post(`${API}/coach/step-chat?token=${token}`, {
        message: text,
        step_id: stepId,
        history: [...messages, userMsg].slice(-6),
      });
      setMessages(prev => [...prev, { role: "assistant", content: res.data.response }]);
    } catch {
      setMessages(prev => [...prev, { role: "assistant", content: "Désolé, je suis temporairement indisponible." }]);
    }
    setLoading(false);
  };

  const quickStart = () => {
    if (messages.length === 0) {
      sendMessage(`Explique-moi cette étape "${stepTitle}" : pourquoi c'est important et par où commencer ?`);
    }
    setOpen(true);
  };

  if (!open) {
    return (
      <button
        onClick={quickStart}
        className="w-full flex items-center gap-2 p-2.5 rounded-lg bg-slate-50 border border-slate-200 hover:border-blue-300 hover:bg-blue-50/50 transition-all text-left group"
        data-testid={`step-coach-trigger-${stepId}`}
      >
        <div className="w-7 h-7 rounded-lg bg-blue-100 flex items-center justify-center shrink-0 group-hover:bg-blue-200 transition-colors">
          <MessageSquare className="w-3.5 h-3.5 text-blue-600" />
        </div>
        <span className="text-xs text-slate-600 group-hover:text-blue-700 transition-colors">Coach IA : cliquez pour etre guide sur cette etape</span>
      </button>
    );
  }

  return (
    <div className="rounded-lg border border-blue-200 bg-blue-50/30 overflow-hidden" data-testid={`step-coach-panel-${stepId}`}>
      <div className="flex items-center justify-between px-3 py-2 bg-blue-100/50 border-b border-blue-200">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-3.5 h-3.5 text-blue-600" />
          <span className="text-xs font-semibold text-blue-700">Coach IA — {stepTitle}</span>
        </div>
        <button onClick={() => setOpen(false)} className="text-xs text-blue-500 hover:text-blue-700">Réduire</button>
      </div>
      <div className="max-h-48 overflow-y-auto p-3 space-y-2">
        {messages.map((msg, i) => (
          <div key={i} className={`text-xs leading-relaxed ${msg.role === "user" ? "text-slate-700 bg-white rounded-lg px-2.5 py-1.5 border border-slate-200" : "text-blue-800"}`}>
            {msg.role === "assistant" && <Brain className="w-3 h-3 text-blue-500 inline mr-1" />}
            {msg.content}
          </div>
        ))}
        {loading && (
          <div className="flex items-center gap-1.5 text-xs text-blue-500">
            <Loader2 className="w-3 h-3 animate-spin" />Le coach réfléchit...
          </div>
        )}
      </div>
      <div className="flex gap-1.5 p-2 border-t border-blue-200 bg-white">
        <Input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && !loading && sendMessage(input)}
          placeholder="Pose ta question au coach..."
          className="h-8 text-xs flex-1"
          disabled={loading}
          data-testid={`step-coach-input-${stepId}`}
        />
        <Button size="sm" className="h-8 px-2 bg-blue-600 hover:bg-blue-700" onClick={() => sendMessage(input)} disabled={loading || !input.trim()} data-testid={`step-coach-send-${stepId}`}>
          <Send className="w-3.5 h-3.5" />
        </Button>
      </div>
    </div>
  );
};

const GpsDashboard = ({ token, pseudo, profile, passport, steps, jobs, allSkills, onOpenDclic }) => {
  const [journeyData, setJourneyData] = useState(null);
  const [loadingJourney, setLoadingJourney] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const res = await axios.get(`${API}/coach/progress?token=${token}`);
        setJourneyData(res.data);
      } catch { /* silent */ }
      setLoadingJourney(false);
    })();
  }, [token]);

  const getStepStatus = (stepId) => {
    if (!journeyData) return "locked";
    const s = journeyData.steps?.find(x => x.id === stepId);
    if (!s) return "locked";
    if (s.complete) return "done";
    if (s.partial) return "active";
    if (stepId <= journeyData.current_step) return "active";
    return "locked";
  };

  const displayName = pseudo || profile?.pseudo || "Utilisateur";
  const currentStep = journeyData?.current_step || 1;
  const progressPct = journeyData?.progress_pct || 0;
  const coachMessage = journeyData?.message || "";

  const phaseLabels = ["Découverte de ton potentiel", "Clarification de ton projet", "Mise en valeur de ton profil", "Passage à l'action"];
  const currentPhaseLabel = phaseLabels[Math.min(currentStep - 1, 3)];

  return (
    <div className="space-y-5" data-testid="gps-dashboard">
      {/* === 1. HEADER PERSONNALISE === */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-[#1e3a5f] via-[#2a5a8f] to-[#1e3a5f] p-6" data-testid="gps-header">
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -translate-y-20 translate-x-20" />
        <div className="absolute bottom-0 left-0 w-32 h-32 bg-white/3 rounded-full translate-y-12 -translate-x-8" />
        <div className="relative z-10">
          <h1 className="text-2xl sm:text-3xl font-bold text-white" style={{ fontFamily: 'Outfit, sans-serif' }} data-testid="gps-greeting">
            Bonjour {displayName}
          </h1>
          <p className="text-blue-200 text-sm mt-1">
            Tu es en phase : <span className="font-semibold text-white">{currentPhaseLabel}</span>
          </p>
          <div className="mt-4 max-w-md">
            <div className="flex justify-between text-xs text-blue-200 mb-1.5">
              <span>Progression de ton parcours</span>
              <span className="font-bold text-white">{progressPct}%</span>
            </div>
            <div className="h-2.5 bg-white/15 rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-emerald-400 to-cyan-400 rounded-full transition-all duration-700" style={{ width: `${progressPct}%` }} />
            </div>
          </div>
          {journeyData && !journeyData.steps?.[currentStep - 1]?.complete && (
            <div className="mt-3 flex items-center gap-2 bg-white/10 rounded-lg px-3 py-2 backdrop-blur-sm" data-testid="gps-next-action">
              <Play className="w-4 h-4 text-emerald-300 shrink-0" />
              <span className="text-xs text-blue-100">Prochaine action : <span className="font-semibold text-white">{journeyData.steps?.[currentStep - 1]?.action_label || JOURNEY_STEPS[currentStep - 1]?.cta}</span></span>
            </div>
          )}
        </div>
      </div>

      {/* === 2. PARCOURS GUIDE (4 ETAPES) === */}
      <div className="space-y-3" data-testid="gps-journey-steps">
        {JOURNEY_STEPS.map((step) => {
          const status = getStepStatus(step.id);
          const c = COLOR_MAP[step.color];
          const Icon = step.icon;
          const isDone = status === "done";
          const isActive = status === "active";
          const isLocked = status === "locked";

          return (
            <Card key={step.id} className={`border overflow-hidden transition-all ${isDone ? "border-emerald-200 bg-emerald-50/30" : isActive ? `${c.border} ${c.bg}` : "border-slate-200 bg-slate-50/50 opacity-75"}`} data-testid={`gps-step-${step.id}`}>
              <CardContent className="p-4">
                <div className="flex items-start gap-3">
                  {/* Step number + icon */}
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${isDone ? "bg-emerald-100" : isActive ? c.iconBg : "bg-slate-100"}`}>
                    {isDone ? <CheckCircle2 className="w-5 h-5 text-emerald-600" /> : <Icon className={`w-5 h-5 ${isActive ? c.text : "text-slate-400"}`} />}
                  </div>

                  <div className="flex-1 min-w-0">
                    {/* Title row */}
                    <div className="flex items-center justify-between gap-2">
                      <div>
                        <div className="flex items-center gap-2">
                          <Badge className={`text-[10px] px-1.5 py-0 ${isDone ? "bg-emerald-100 text-emerald-700" : isActive ? `${c.bg} ${c.text}` : "bg-slate-100 text-slate-500"}`}>
                            Étape {step.id}
                          </Badge>
                          {isDone && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />}
                        </div>
                        <h3 className={`text-sm font-semibold mt-1 ${isDone ? "text-emerald-800" : isActive ? "text-slate-900" : "text-slate-500"}`}>{step.title}</h3>
                        <p className="text-xs text-slate-400 mt-0.5">{step.subtitle}</p>
                      </div>
                      {!isLocked && (
                        <Button
                          size="sm"
                          className={`shrink-0 text-xs h-8 ${isDone ? "bg-emerald-600 hover:bg-emerald-700" : `bg-gradient-to-r ${c.gradient} hover:opacity-90`} text-white`}
                          onClick={() => {
                            const firstItem = step.items[0];
                            if (firstItem.action === "dclic") window.open('/test-dclic', '_blank');
                            else if (firstItem.path) window.location.href = firstItem.path;
                          }}
                          data-testid={`gps-step-cta-${step.id}`}
                        >
                          {isDone ? step.ctaDone : isActive ? step.ctaActive : step.cta}
                          <ChevronRight className="w-3.5 h-3.5 ml-1" />
                        </Button>
                      )}
                    </div>

                    {/* Sub-items */}
                    {!isLocked && (
                      <div className="mt-2.5 space-y-1">
                        {step.items.map((item, i) => {
                          const itemDone = isDone || (isActive && journeyData?.steps?.[step.id - 1]?.details && (
                            (item.key === "cv" && journeyData.steps[step.id - 1].details.has_cv) ||
                            (item.key === "dclic" && profile?.dclic_imported) ||
                            (item.key === "competences" && (passport?.competences?.length || 0) > 5) ||
                            (item.key === "trajectoire" && steps?.length > 0) ||
                            (item.key === "cv_gen" && false) ||
                            (item.key === "softskills" && profile?.dclic_competences?.length > 0)
                          ));
                          return (
                            <button
                              key={i}
                              className="w-full flex items-center gap-2 text-left text-xs group"
                              onClick={() => {
                                if (item.action === "dclic") window.open('/test-dclic', '_blank');
                                else if (item.action === "ubuntoo") window.open("/ubuntoo", "_blank");
                                else if (item.path) window.location.href = item.path;
                              }}
                              data-testid={`gps-item-${item.key}`}
                            >
                              {itemDone ? (
                                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
                              ) : (
                                <Circle className={`w-3.5 h-3.5 shrink-0 ${isActive ? "text-slate-300" : "text-slate-200"}`} />
                              )}
                              <span className={`${itemDone ? "text-emerald-700" : "text-slate-600 group-hover:text-slate-900"} transition-colors`}>{item.label}</span>
                              <ArrowRight className="w-3 h-3 text-slate-300 ml-auto opacity-0 group-hover:opacity-100 transition-opacity" />
                            </button>
                          );
                        })}
                      </div>
                    )}

                    {/* Step Coach */}
                    {isActive && (
                      <div className="mt-3">
                        <StepCoach token={token} stepId={step.id} stepTitle={step.title} />
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* === 3. COACH INTELLIGENT === */}
      {coachMessage && (
        <Card className="border-blue-200 bg-gradient-to-r from-blue-50 to-indigo-50 overflow-hidden" data-testid="gps-coach-block">
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center shrink-0">
                <Brain className="w-5 h-5 text-blue-600" />
              </div>
              <div className="flex-1">
                <p className="text-xs font-semibold text-blue-700 mb-1">Coach RE'ACTIF</p>
                <p className="text-sm text-slate-700 leading-relaxed">{coachMessage}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* === 4. IDENTITE PRO === */}
      {profile?.dclic_imported && (
        <Card className="border-0 shadow-sm overflow-hidden cursor-pointer hover:shadow-md transition-shadow" onClick={() => window.location.href = "/dashboard/profil"} data-testid="gps-identity-block">
          <div className="bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 px-4 py-3">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-white" />
              <span className="text-sm font-semibold text-white">Mon Identité Professionnelle</span>
              <Badge className="bg-white/20 text-white border-0 text-[10px] ml-auto">D'CLIC PRO</Badge>
            </div>
          </div>
          <CardContent className="p-4">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {(() => {
                const dp = profile.dclic_profile || {};
                const vp = dp.vertus_profile || {};
                const vd = dp.vertu_data || {};
                const vertuDom = vp.dominant_name || vd.name || "";
                const vertuSec = vp.secondary_name || "";
                const valeurs = (vd.valeurs_schwartz || []).slice(0, 2).join(", ") || (Object.keys(vp.valeurs_scores || {}).slice(0, 2).join(", "));
                return (
                  <>
                    <div className="text-center">
                      <p className="text-xs text-slate-500">Vertus</p>
                      <p className="text-base font-bold text-slate-900">{vertuDom || "—"}</p>
                      {vertuSec && <p className="text-[10px] text-slate-400">{vertuSec}</p>}
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-slate-500">Valeurs</p>
                      <p className="text-sm font-bold text-slate-900">{valeurs || "—"}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-slate-500">Compétences</p>
                      <p className="text-lg font-bold text-slate-900">{allSkills?.length || 0}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-slate-500">Profil</p>
                      <p className="text-lg font-bold text-slate-900">{profile.profile_score || 0}%</p>
                    </div>
                  </>
                );
              })()}
            </div>
            <div className="flex items-center gap-1 mt-2 text-xs text-emerald-600">
              <span>Voir mon profil complet</span>
              <ChevronRight className="w-3 h-3" />
            </div>
          </CardContent>
        </Card>
      )}

      {/* === 5. ACTIONS RAPIDES === */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2" data-testid="gps-quick-actions">
        {[
          { label: "Mettre à jour mon CV", icon: FileText, path: "/dashboard/trajectoire?sub=cv", color: "text-blue-600 bg-blue-50 hover:bg-blue-100" },
          { label: "Modifier mon profil", icon: User, path: "/dashboard/profil", color: "text-violet-600 bg-violet-50 hover:bg-violet-100" },
          { label: "Ajouter une expérience", icon: Route, path: "/dashboard/trajectoire?sub=trajectoire", color: "text-emerald-600 bg-emerald-50 hover:bg-emerald-100" },
          { label: "Mon portefeuille", icon: FolderLock, path: "/dashboard/coffre-fort", color: "text-rose-600 bg-rose-50 hover:bg-rose-100" },
        ].map((a, i) => {
          const AIcon = a.icon;
          return (
            <button key={i} onClick={() => window.location.href = a.path} className={`flex flex-col items-center gap-1.5 p-3 rounded-xl border border-transparent transition-all ${a.color}`} data-testid={`gps-quick-${i}`}>
              <AIcon className="w-5 h-5" />
              <span className="text-[11px] font-medium text-center leading-tight">{a.label}</span>
            </button>
          );
        })}
      </div>

      {/* === 6. UBUNTOO === */}
      <Card className="border-0 shadow-sm overflow-hidden cursor-pointer hover:shadow-md transition-shadow" onClick={() => window.open("/ubuntoo", "_blank")} data-testid="gps-ubuntoo-block">
        <CardContent className="p-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-amber-100 flex items-center justify-center shrink-0">
              <Users className="w-6 h-6 text-amber-700" />
            </div>
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-slate-900">Tu n'es pas seul — Reseau UBUNTOO</h3>
              <p className="text-xs text-slate-500 mt-0.5">Mentors, groupes métiers et entraide entre pairs</p>
            </div>
            <Badge className="bg-amber-50 text-amber-700 border border-amber-200 text-xs shrink-0">
              Communaute
              <ExternalLink className="w-3 h-3 ml-1" />
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* === 7. NAVIGATION CLASSIQUE === */}
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-3" data-testid="gps-nav-grid">
        {[
          { title: "Le Marché", desc: "Observatoire et tendances métiers", icon: Brain, path: "/dashboard/marche", color: "bg-amber-600" },
          { title: "Opportunités", desc: "Offres d'emploi compatibles", icon: Briefcase, path: "/dashboard/opportunites", color: "bg-violet-600", stat: `${(jobs || []).filter(j => (j.match_score || j.matching_score || 0) >= 60).length} offres` },
          { title: "Job Dating", desc: "Événements de recrutement", icon: Users, path: "/dashboard/job-dating", color: "bg-rose-600" },
        ].map((item) => {
          const NavIcon = item.icon;
          return (
            <Card key={item.path} className="group cursor-pointer hover:shadow-md transition-all hover:-translate-y-0.5 border-0 shadow-sm" onClick={() => window.location.href = item.path} data-testid={`gps-nav-${item.path.split('/').pop()}`}>
              <CardContent className="p-4">
                <div className="flex items-start gap-3">
                  <div className={`w-9 h-9 rounded-lg ${item.color} flex items-center justify-center shadow-sm group-hover:scale-105 transition-transform`}>
                    <NavIcon className="w-4 h-4 text-white" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-slate-900">{item.title}</h3>
                    <p className="text-[11px] text-slate-500 mt-0.5">{item.desc}</p>
                    {item.stat && <span className="inline-block mt-1 text-[10px] font-medium text-[#1e3a5f] bg-blue-50 px-1.5 py-0.5 rounded-full">{item.stat}</span>}
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
};

export default GpsDashboard;



