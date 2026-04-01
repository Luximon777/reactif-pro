import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { API } from "@/App";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  MessageCircle, X, ChevronRight, CheckCircle2, Circle,
  Sparkles, Target, Brain, Briefcase, Route, Upload,
  ArrowRight, Trophy, Star, Rocket, Hand
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";

const STEP_ICONS = {
  1: Sparkles,
  2: Route,
  3: Upload,
  4: Brain,
};

const STEP_COLORS = {
  1: { bg: "bg-violet-100", text: "text-violet-700", border: "border-violet-200", accent: "bg-violet-500" },
  2: { bg: "bg-amber-100", text: "text-amber-700", border: "border-amber-200", accent: "bg-amber-500" },
  3: { bg: "bg-emerald-100", text: "text-emerald-700", border: "border-emerald-200", accent: "bg-emerald-500" },
  4: { bg: "bg-blue-100", text: "text-blue-700", border: "border-blue-200", accent: "bg-blue-500" },
};

const EMOJI_ICONS = {
  wave: Hand,
  star: Star,
  rocket: Rocket,
  target: Target,
  trophy: Trophy,
};

const CoachVirtuel = ({ token, onOpenDclic }) => {
  const navigate = useNavigate();
  const [progress, setProgress] = useState(null);
  const [open, setOpen] = useState(false);
  const [dismissed, setDismissed] = useState(false);
  const [loading, setLoading] = useState(true);
  const [pulseHint, setPulseHint] = useState(false);

  const loadProgress = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/coach/progress?token=${token}`);
      setProgress(res.data);

      // Auto-show for users who haven't completed the journey
      const coachDismissed = localStorage.getItem(`coach_dismissed_${token}`);
      if (!coachDismissed && res.data.completed < 4) {
        setTimeout(() => setOpen(true), 1500);
      } else if (res.data.completed < 4) {
        setTimeout(() => setPulseHint(true), 3000);
      }
    } catch (e) {
      console.error("Coach progress error:", e);
    }
    setLoading(false);
  }, [token]);

  useEffect(() => {
    loadProgress();
  }, [loadProgress]);

  const handleDismiss = () => {
    setOpen(false);
    setDismissed(true);
    localStorage.setItem(`coach_dismissed_${token}`, "true");
  };

  const handleAction = (step) => {
    if (step.action_type === "dclic" && onOpenDclic) {
      onOpenDclic();
      setOpen(false);
    } else if (step.action_type === "navigate" && step.action_path) {
      navigate(step.action_path);
      setOpen(false);
    }
  };

  const handleReopen = () => {
    setOpen(true);
    setPulseHint(false);
    localStorage.removeItem(`coach_dismissed_${token}`);
  };

  if (loading || !progress) return null;

  const EmojiIcon = EMOJI_ICONS[progress.emoji] || Star;
  const currentStepData = progress.steps.find(s => s.id === progress.current_step);

  return (
    <>
      {/* Floating Coach Button */}
      <AnimatePresence>
        {!open && (
          <motion.div
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            className="fixed bottom-6 right-6 z-50"
          >
            <button
              onClick={handleReopen}
              className={`group relative w-14 h-14 rounded-full bg-gradient-to-br from-[#1e3a5f] to-[#4f6df5] text-white shadow-lg hover:shadow-xl transition-all hover:scale-105 flex items-center justify-center ${pulseHint ? "animate-bounce" : ""}`}
              data-testid="coach-bubble-btn"
            >
              <MessageCircle className="w-6 h-6" />
              {progress.completed < 4 && (
                <span className="absolute -top-1 -right-1 w-5 h-5 bg-amber-400 rounded-full text-[10px] font-bold flex items-center justify-center text-slate-900 shadow">
                  {progress.current_step}
                </span>
              )}
              {progress.completed === 4 && (
                <span className="absolute -top-1 -right-1 w-5 h-5 bg-emerald-400 rounded-full flex items-center justify-center shadow">
                  <CheckCircle2 className="w-3 h-3 text-white" />
                </span>
              )}
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Coach Panel */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
            className="fixed bottom-6 right-6 z-50 w-[380px] max-h-[520px] overflow-hidden rounded-2xl bg-white shadow-2xl border border-slate-200"
            data-testid="coach-panel"
          >
            {/* Header */}
            <div className="bg-gradient-to-r from-[#1e3a5f] to-[#2d5a8f] p-4 text-white">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center backdrop-blur-sm">
                    <EmojiIcon className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-sm">Votre Coach RE'ACTIF</h3>
                    <p className="text-[11px] text-white/70">Parcours guidé</p>
                  </div>
                </div>
                <button
                  onClick={handleDismiss}
                  className="w-7 h-7 rounded-full hover:bg-white/20 flex items-center justify-center transition-colors"
                  data-testid="coach-close-btn"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Progress bar */}
              <div className="mt-3">
                <div className="flex items-center justify-between text-[11px] text-white/80 mb-1.5">
                  <span>Progression</span>
                  <span className="font-semibold">{progress.completed}/4 étapes</span>
                </div>
                <div className="h-2 bg-white/20 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${progress.progress_pct}%` }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                    className="h-full bg-gradient-to-r from-amber-300 to-emerald-300 rounded-full"
                  />
                </div>
              </div>
            </div>

            {/* Coach Message */}
            <div className="p-4 bg-slate-50 border-b border-slate-100">
              <p className="text-sm text-slate-700 leading-relaxed" data-testid="coach-message">
                {progress.message}
              </p>
            </div>

            {/* Steps */}
            <div className="p-3 overflow-y-auto max-h-[280px] space-y-2">
              {progress.steps.map((step) => {
                const StepIcon = STEP_ICONS[step.id];
                const colors = STEP_COLORS[step.id];
                const isCurrent = step.id === progress.current_step;

                return (
                  <motion.div
                    key={step.id}
                    initial={false}
                    animate={isCurrent ? { scale: 1.02 } : { scale: 1 }}
                    className={`rounded-xl border p-3 transition-all ${
                      step.complete
                        ? "bg-emerald-50/50 border-emerald-200"
                        : isCurrent
                        ? `${colors.bg}/30 ${colors.border} border-2 shadow-sm`
                        : "bg-white border-slate-100"
                    }`}
                    data-testid={`coach-step-${step.id}`}
                  >
                    <div className="flex items-start gap-3">
                      {/* Status Icon */}
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
                        step.complete ? "bg-emerald-100" : isCurrent ? colors.bg : "bg-slate-100"
                      }`}>
                        {step.complete ? (
                          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                        ) : (
                          <StepIcon className={`w-4 h-4 ${isCurrent ? colors.text : "text-slate-400"}`} />
                        )}
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <h4 className={`text-sm font-semibold ${step.complete ? "text-emerald-700" : isCurrent ? "text-slate-900" : "text-slate-500"}`}>
                            {step.title}
                          </h4>
                          {step.complete && (
                            <Badge className="text-[9px] bg-emerald-100 text-emerald-700 px-1.5 py-0">Fait</Badge>
                          )}
                          {isCurrent && !step.complete && (
                            <Badge className={`text-[9px] ${colors.bg} ${colors.text} px-1.5 py-0`}>En cours</Badge>
                          )}
                        </div>

                        {(isCurrent || step.complete) && (
                          <p className="text-[11px] text-slate-500 mt-0.5 leading-relaxed">
                            {step.description}
                          </p>
                        )}

                        {/* Details for completed steps */}
                        {step.complete && step.id === 1 && step.details?.disc && (
                          <div className="flex flex-wrap gap-1 mt-1.5">
                            {step.details.disc && <Badge className="text-[9px] bg-blue-50 text-blue-600">DISC: {step.details.disc}</Badge>}
                            {step.details.vertu && <Badge className="text-[9px] bg-amber-50 text-amber-600">{step.details.vertu}</Badge>}
                          </div>
                        )}
                        {step.complete && step.id === 3 && step.details?.competences_count > 0 && (
                          <p className="text-[10px] text-emerald-600 mt-1">{step.details.competences_count} compétences identifiées</p>
                        )}

                        {/* Action button for current step */}
                        {isCurrent && !step.complete && step.action_label && (
                          <Button
                            size="sm"
                            className={`mt-2 h-7 text-xs ${colors.accent} hover:opacity-90 text-white`}
                            onClick={() => handleAction(step)}
                            data-testid={`coach-action-step-${step.id}`}
                          >
                            {step.action_label}
                            <ArrowRight className="w-3 h-3 ml-1" />
                          </Button>
                        )}
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>

            {/* Footer */}
            {progress.completed === 4 && (
              <div className="p-3 border-t border-slate-100 bg-gradient-to-r from-emerald-50 to-blue-50">
                <div className="flex items-center gap-2 text-sm text-emerald-700 font-medium">
                  <Trophy className="w-4 h-4" />
                  <span>Parcours complété ! Votre profil est riche et personnalisé.</span>
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default CoachVirtuel;
