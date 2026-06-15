import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Compass, CheckCircle2, Circle, Clock, ChevronRight,
  Users, Target, Briefcase, FileText, MessageSquare,
  Calendar, ArrowRight, Lightbulb, Zap, Award
} from "lucide-react";
import { toast } from "sonner";

const VSI_PHASES = [
  {
    id: 1,
    title: "Atelier VSI",
    subtitle: "Prise de conscience identitaire",
    description: "Atelier collectif en présentiel ou visio pour explorer les fondements de votre identité professionnelle : valeurs, moteurs, freins.",
    icon: Users,
    color: "amber",
    tasks: [
      "Cartographier vos valeurs professionnelles",
      "Identifier vos moteurs de motivation",
      "Analyser vos freins et leviers de changement",
    ],
  },
  {
    id: 2,
    title: "Diagnostic",
    subtitle: "Bilan approfondi",
    description: "Diagnostic individuel avec un conseiller VSI : analyse de votre parcours, vos compétences transférables et votre positionnement sur le marché.",
    icon: Target,
    color: "blue",
    tasks: [
      "Entretien diagnostic individuel",
      "Analyse des compétences transférables",
      "Cartographie de votre positionnement marché",
    ],
  },
  {
    id: 3,
    title: "Projection Métier",
    subtitle: "Explorer les possibles",
    description: "Confrontation de votre identité professionnelle aux réalités du marché. Enquêtes métiers, immersions, et validation de pistes.",
    icon: Compass,
    color: "emerald",
    tasks: [
      "Enquêtes métiers ciblées",
      "Immersions professionnelles",
      "Validation des pistes identifiées",
    ],
  },
  {
    id: 4,
    title: "Plan d'Action",
    subtitle: "Mise en mouvement",
    description: "Construction d'un plan d'action concret et réaliste : objectifs, étapes, échéances, ressources mobilisables.",
    icon: Zap,
    color: "violet",
    tasks: [
      "Définir des objectifs SMART",
      "Planifier les étapes clés",
      "Identifier les ressources et appuis",
    ],
  },
];

const colorMap = {
  amber: { bg: "bg-amber-50", border: "border-amber-200", text: "text-amber-700", iconBg: "bg-amber-100", badge: "bg-amber-100 text-amber-800", progress: "bg-amber-500" },
  blue: { bg: "bg-blue-50", border: "border-blue-200", text: "text-blue-700", iconBg: "bg-blue-100", badge: "bg-blue-100 text-blue-800", progress: "bg-blue-500" },
  emerald: { bg: "bg-emerald-50", border: "border-emerald-200", text: "text-emerald-700", iconBg: "bg-emerald-100", badge: "bg-emerald-100 text-emerald-800", progress: "bg-emerald-500" },
  violet: { bg: "bg-violet-50", border: "border-violet-200", text: "text-violet-700", iconBg: "bg-violet-100", badge: "bg-violet-100 text-violet-800", progress: "bg-violet-500" },
};

const VsiView = ({ token, section = "accueil" }) => {
  const [vsiData, setVsiData] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadVsiData = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/vsi/progress?token=${token}`);
      setVsiData(res.data);
    } catch {
      // No VSI data yet — initialize
      setVsiData({
        current_phase: 1,
        phases: VSI_PHASES.map(p => ({ id: p.id, status: p.id === 1 ? "en_cours" : "a_venir", tasks_done: [] })),
        next_appointment: null,
        objectives: [],
        messages: [],
      });
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { loadVsiData(); }, [loadVsiData]);

  const getPhaseStatus = (phaseId) => {
    if (!vsiData) return "a_venir";
    const p = vsiData.phases?.find(x => x.id === phaseId);
    return p?.status || "a_venir";
  };

  const getTasksDone = (phaseId) => {
    if (!vsiData) return [];
    const p = vsiData.phases?.find(x => x.id === phaseId);
    return p?.tasks_done || [];
  };

  const totalProgress = () => {
    if (!vsiData?.phases) return 0;
    const completed = vsiData.phases.filter(p => p.status === "termine").length;
    const inProgress = vsiData.phases.filter(p => p.status === "en_cours").length;
    return Math.round((completed * 100 + inProgress * 50) / 4);
  };

  const toggleTask = async (phaseId, taskIndex) => {
    try {
      await axios.post(`${API}/vsi/toggle-task?token=${token}`, {
        phase_id: phaseId,
        task_index: taskIndex,
      });
      await loadVsiData();
    } catch {
      toast.error("Erreur lors de la mise a jour");
    }
  };

  const markPhaseComplete = async (phaseId) => {
    try {
      await axios.post(`${API}/vsi/complete-phase?token=${token}`, { phase_id: phaseId });
      toast.success("Phase validee !");
      await loadVsiData();
    } catch {
      toast.error("Erreur");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin w-8 h-8 border-3 border-amber-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  if (section === "accueil") return <VsiAccueil vsiData={vsiData} totalProgress={totalProgress} getPhaseStatus={getPhaseStatus} />;
  if (section === "diagnostic") return <VsiDiagnostic vsiData={vsiData} getPhaseStatus={getPhaseStatus} getTasksDone={getTasksDone} toggleTask={toggleTask} markPhaseComplete={markPhaseComplete} />;
  if (section === "plan") return <VsiPlanAction vsiData={vsiData} getPhaseStatus={getPhaseStatus} getTasksDone={getTasksDone} toggleTask={toggleTask} markPhaseComplete={markPhaseComplete} />;

  return (
    <VsiParcours
      vsiData={vsiData}
      getPhaseStatus={getPhaseStatus}
      getTasksDone={getTasksDone}
      toggleTask={toggleTask}
      markPhaseComplete={markPhaseComplete}
      totalProgress={totalProgress}
    />
  );
};

// === ACCUEIL VSI ===
const VsiAccueil = ({ vsiData, totalProgress, getPhaseStatus }) => {
  const currentPhase = VSI_PHASES.find(p => getPhaseStatus(p.id) === "en_cours") || VSI_PHASES[0];
  const c = colorMap[currentPhase.color];
  const PhaseIcon = currentPhase.icon;

  return (
    <div className="space-y-6" data-testid="vsi-accueil">
      {/* Hero */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-amber-600 via-amber-500 to-orange-500 p-6 sm:p-8">
        <div className="absolute top-0 right-0 w-48 h-48 bg-white/5 rounded-full -translate-y-12 translate-x-12" />
        <div className="relative z-10">
          <div className="flex items-center gap-2 mb-2">
            <Compass className="w-6 h-6 text-amber-200" />
            <span className="text-amber-200 text-sm font-medium tracking-wide uppercase">Parcours VSI</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white mb-2" style={{ fontFamily: 'Outfit, sans-serif' }}>
            Valorisez votre Identite Professionnelle
          </h1>
          <p className="text-amber-100 text-sm max-w-xl">
            Accompagnement hybride pour reveler votre potentiel, clarifier votre projet et passer a l'action.
          </p>
          <div className="mt-5 flex items-center gap-4">
            <div className="flex-1 max-w-xs">
              <div className="flex justify-between text-xs text-amber-200 mb-1">
                <span>Progression globale</span>
                <span className="font-semibold">{totalProgress()}%</span>
              </div>
              <div className="h-2.5 bg-white/20 rounded-full overflow-hidden">
                <div className="h-full bg-white rounded-full transition-all duration-500" style={{ width: `${totalProgress()}%` }} />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Current Phase Card */}
      <Card className={`border ${c.border} ${c.bg}`} data-testid="vsi-current-phase">
        <CardHeader className="pb-3">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-xl ${c.iconBg} flex items-center justify-center`}>
              <PhaseIcon className={`w-5 h-5 ${c.text}`} />
            </div>
            <div>
              <Badge className={`${c.badge} text-xs mb-1`}>Phase en cours</Badge>
              <CardTitle className={`text-lg ${c.text}`}>{currentPhase.title} — {currentPhase.subtitle}</CardTitle>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-slate-600">{currentPhase.description}</p>
        </CardContent>
      </Card>

      {/* 4 Phases Summary */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {VSI_PHASES.map((phase) => {
          const status = getPhaseStatus(phase.id);
          const col = colorMap[phase.color];
          const Icon = phase.icon;
          return (
            <Card key={phase.id} className={`border ${status === "termine" ? "border-emerald-300 bg-emerald-50/50" : status === "en_cours" ? `${col.border} ${col.bg}` : "border-slate-200 bg-white"} transition-all`} data-testid={`vsi-phase-${phase.id}`}>
              <CardContent className="pt-4 pb-4 px-4">
                <div className="flex items-center gap-2 mb-2">
                  {status === "termine" ? (
                    <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                  ) : status === "en_cours" ? (
                    <Clock className={`w-5 h-5 ${col.text}`} />
                  ) : (
                    <Circle className="w-5 h-5 text-slate-300" />
                  )}
                  <span className="text-xs font-semibold text-slate-500">Phase {phase.id}</span>
                </div>
                <h3 className={`text-sm font-semibold ${status === "termine" ? "text-emerald-700" : status === "en_cours" ? col.text : "text-slate-500"}`}>
                  {phase.title}
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">{phase.subtitle}</p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Next Appointment */}
      {vsiData?.next_appointment && (
        <Card className="border-amber-200 bg-amber-50/50" data-testid="vsi-next-appointment">
          <CardContent className="pt-4 pb-4 flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-amber-100 flex items-center justify-center">
              <Calendar className="w-6 h-6 text-amber-700" />
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-900">Prochain rendez-vous</p>
              <p className="text-xs text-slate-500">{vsiData.next_appointment.date} — {vsiData.next_appointment.type}</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

// === PARCOURS VSI (full phases view) ===
const VsiParcours = ({ vsiData, getPhaseStatus, getTasksDone, toggleTask, markPhaseComplete, totalProgress }) => (
  <div className="space-y-6" data-testid="vsi-parcours">
    <div className="flex items-center justify-between">
      <div>
        <h2 className="text-xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>Mon Parcours VSI</h2>
        <p className="text-sm text-slate-500 mt-0.5">4 phases pour valoriser votre identite professionnelle</p>
      </div>
      <Badge className="bg-amber-100 text-amber-800 text-sm px-3 py-1">{totalProgress()}%</Badge>
    </div>

    <div className="space-y-4">
      {VSI_PHASES.map((phase) => {
        const status = getPhaseStatus(phase.id);
        const tasksDone = getTasksDone(phase.id);
        const col = colorMap[phase.color];
        const Icon = phase.icon;
        const allTasksDone = phase.tasks.every((_, i) => tasksDone.includes(i));

        return (
          <Card key={phase.id} className={`border ${status === "termine" ? "border-emerald-300" : status === "en_cours" ? col.border : "border-slate-200"} transition-all`} data-testid={`vsi-phase-detail-${phase.id}`}>
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-xl ${status === "termine" ? "bg-emerald-100" : status === "en_cours" ? col.iconBg : "bg-slate-100"} flex items-center justify-center`}>
                    {status === "termine" ? <CheckCircle2 className="w-5 h-5 text-emerald-600" /> : <Icon className={`w-5 h-5 ${status === "en_cours" ? col.text : "text-slate-400"}`} />}
                  </div>
                  <div>
                    <CardTitle className="text-base">{phase.title}</CardTitle>
                    <CardDescription className="text-xs">{phase.subtitle}</CardDescription>
                  </div>
                </div>
                <Badge className={`text-xs ${status === "termine" ? "bg-emerald-100 text-emerald-800" : status === "en_cours" ? col.badge : "bg-slate-100 text-slate-500"}`}>
                  {status === "termine" ? "Termine" : status === "en_cours" ? "En cours" : "A venir"}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-sm text-slate-600">{phase.description}</p>

              {/* Tasks checklist */}
              {status !== "a_venir" && (
                <div className="space-y-2">
                  {phase.tasks.map((task, i) => {
                    const done = tasksDone.includes(i);
                    return (
                      <button
                        key={i}
                        onClick={() => toggleTask(phase.id, i)}
                        className={`w-full flex items-center gap-3 p-2.5 rounded-lg border transition-all text-left ${done ? "bg-emerald-50 border-emerald-200" : "bg-white border-slate-200 hover:border-amber-300"}`}
                        data-testid={`vsi-task-${phase.id}-${i}`}
                      >
                        {done ? <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" /> : <Circle className="w-4 h-4 text-slate-300 shrink-0" />}
                        <span className={`text-sm ${done ? "text-emerald-700 line-through" : "text-slate-700"}`}>{task}</span>
                      </button>
                    );
                  })}
                </div>
              )}

              {/* Complete phase button */}
              {status === "en_cours" && allTasksDone && (
                <Button onClick={() => markPhaseComplete(phase.id)} className="w-full bg-amber-600 hover:bg-amber-700 text-white mt-2" data-testid={`vsi-complete-phase-${phase.id}`}>
                  <CheckCircle2 className="w-4 h-4 mr-2" /> Valider cette phase
                </Button>
              )}
            </CardContent>
          </Card>
        );
      })}
    </div>
  </div>
);

// === DIAGNOSTIC ===
const VsiDiagnostic = ({ vsiData, getPhaseStatus, getTasksDone, toggleTask, markPhaseComplete }) => {
  const phase = VSI_PHASES[1]; // Phase 2
  const status = getPhaseStatus(2);
  const tasksDone = getTasksDone(2);

  return (
    <div className="space-y-6" data-testid="vsi-diagnostic">
      <div>
        <h2 className="text-xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>Diagnostic VSI</h2>
        <p className="text-sm text-slate-500 mt-0.5">Bilan approfondi de votre identite professionnelle</p>
      </div>

      <Card className="border-blue-200 bg-blue-50/30">
        <CardContent className="pt-5 space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center">
              <Target className="w-6 h-6 text-blue-700" />
            </div>
            <div>
              <h3 className="text-base font-semibold text-slate-900">{phase.title} — {phase.subtitle}</h3>
              <p className="text-sm text-slate-500">{phase.description}</p>
            </div>
          </div>

          {status === "a_venir" ? (
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-center">
              <p className="text-sm text-slate-500">Cette phase sera accessible apres la validation de l'Atelier VSI (Phase 1).</p>
            </div>
          ) : (
            <div className="space-y-2">
              {phase.tasks.map((task, i) => {
                const done = tasksDone.includes(i);
                return (
                  <button
                    key={i}
                    onClick={() => toggleTask(2, i)}
                    className={`w-full flex items-center gap-3 p-3 rounded-lg border transition-all text-left ${done ? "bg-emerald-50 border-emerald-200" : "bg-white border-slate-200 hover:border-blue-300"}`}
                    data-testid={`vsi-diag-task-${i}`}
                  >
                    {done ? <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" /> : <Circle className="w-4 h-4 text-slate-300 shrink-0" />}
                    <span className={`text-sm ${done ? "text-emerald-700 line-through" : "text-slate-700"}`}>{task}</span>
                  </button>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

// === PLAN D'ACTION ===
const VsiPlanAction = ({ vsiData, getPhaseStatus, getTasksDone, toggleTask, markPhaseComplete }) => {
  const phase = VSI_PHASES[3]; // Phase 4
  const status = getPhaseStatus(4);
  const tasksDone = getTasksDone(4);

  return (
    <div className="space-y-6" data-testid="vsi-plan-action">
      <div>
        <h2 className="text-xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>Plan d'Action</h2>
        <p className="text-sm text-slate-500 mt-0.5">Construisez votre feuille de route concrete</p>
      </div>

      <Card className="border-violet-200 bg-violet-50/30">
        <CardContent className="pt-5 space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-violet-100 flex items-center justify-center">
              <Zap className="w-6 h-6 text-violet-700" />
            </div>
            <div>
              <h3 className="text-base font-semibold text-slate-900">{phase.title} — {phase.subtitle}</h3>
              <p className="text-sm text-slate-500">{phase.description}</p>
            </div>
          </div>

          {status === "a_venir" ? (
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-center">
              <p className="text-sm text-slate-500">Cette phase sera accessible apres la validation de la Projection Metier (Phase 3).</p>
            </div>
          ) : (
            <div className="space-y-2">
              {phase.tasks.map((task, i) => {
                const done = tasksDone.includes(i);
                return (
                  <button
                    key={i}
                    onClick={() => toggleTask(4, i)}
                    className={`w-full flex items-center gap-3 p-3 rounded-lg border transition-all text-left ${done ? "bg-emerald-50 border-emerald-200" : "bg-white border-slate-200 hover:border-violet-300"}`}
                    data-testid={`vsi-plan-task-${i}`}
                  >
                    {done ? <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" /> : <Circle className="w-4 h-4 text-slate-300 shrink-0" />}
                    <span className={`text-sm ${done ? "text-emerald-700 line-through" : "text-slate-700"}`}>{task}</span>
                  </button>
                );
              })}
            </div>
          )}

          {/* Objectives */}
          {vsiData?.objectives?.length > 0 && (
            <div className="mt-4">
              <h4 className="text-sm font-semibold text-slate-700 mb-2">Mes objectifs</h4>
              {vsiData.objectives.map((obj, i) => (
                <div key={i} className="flex items-center gap-2 text-sm text-slate-600 mb-1">
                  <Lightbulb className="w-3.5 h-3.5 text-amber-500" />
                  {obj}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default VsiView;
