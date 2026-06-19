import { useState, useEffect, useCallback, useRef } from "react";
import axios from "axios";
import { API } from "@/App";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  MessageCircle, X, CheckCircle2, Minus,
  Sparkles, Target, Brain, Route, Upload, Award,
  ArrowRight, Trophy, Star, Rocket, Hand,
  Send, Loader2, ListChecks, Bot, ChevronRight,
  Lightbulb, Plus, Download, TrendingUp
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";

const STEP_ICONS = { 1: Upload, 2: Award, 3: Sparkles, 4: Route, 5: Brain };
const STEP_COLORS = {
  1: { bg: "bg-violet-100", text: "text-violet-700", border: "border-violet-200", accent: "bg-violet-500" },
  2: { bg: "bg-emerald-100", text: "text-emerald-700", border: "border-emerald-200", accent: "bg-emerald-500" },
  3: { bg: "bg-amber-100", text: "text-amber-700", border: "border-amber-200", accent: "bg-amber-500" },
  4: { bg: "bg-blue-100", text: "text-blue-700", border: "border-blue-200", accent: "bg-blue-500" },
  5: { bg: "bg-indigo-100", text: "text-indigo-700", border: "border-indigo-200", accent: "bg-indigo-500" },
};
const EMOJI_ICONS = { wave: Hand, star: Star, rocket: Rocket, target: Target, trophy: Trophy };

const STEP_NEXT_MESSAGES = {
  1: { msg: "CV analysé avec succès ! Passez à l'étape 2 : identifiez vos savoir-être et vos valeurs pour compléter votre profil.", icon: "star" },
  2: { msg: "Vos soft skills sont documentés ! Étape 3 : lancez le test D'CLIC PRO pour révéler votre personnalité.", icon: "rocket" },
  3: { msg: "D'CLIC PRO terminé ! Dernière étape : construisez votre trajectoire professionnelle complète.", icon: "target" },
  4: { msg: "Félicitations ! Toutes les étapes sont complétées. Votre profil RE'ACTIF PRO est complet !", icon: "trophy" },
};

const TIP_ICONS = { lightbulb: Lightbulb, rocket: Rocket, plus: Plus, target: Target, download: Download, shield: Award, calendar: Target, refresh: TrendingUp, compass: Target };

/* ───── Steps View (compact) ───── */
const StepsView = ({ progress, onAction }) => {
  const nextStep = progress.steps.find(s => s.id === progress.current_step && !s.complete);
  const tips = progress.tips || [];
  const nextInfo = progress.next_step;
  const allComplete = progress.completed >= progress.total;

  return (
    <div className="p-3 space-y-2">
      {/* Achievements summary */}
      {progress.achievements?.length > 0 && (
        <div className="rounded-lg bg-emerald-50/60 border border-emerald-100 px-3 py-2" data-testid="coach-achievements">
          <div className="flex items-center gap-1.5 mb-1">
            <TrendingUp className="w-3 h-3 text-emerald-600" />
            <span className="text-[10px] font-bold text-emerald-800">Vos acquis</span>
          </div>
          <div className="space-y-0.5">
            {progress.achievements.map((a, i) => (
              <div key={i} className="flex items-center gap-1.5">
                <CheckCircle2 className="w-2.5 h-2.5 text-emerald-500 shrink-0" />
                <span className="text-[11px] text-emerald-700">{a}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Proactive Next Step Banner with detailed hint */}
      {nextStep && nextInfo && (
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-xl bg-gradient-to-r from-amber-50 to-orange-50 border-2 border-amber-300/60 p-3 mb-1"
          data-testid="next-step-banner"
        >
          <div className="flex items-center gap-1.5 mb-1.5">
            <ArrowRight className="w-3.5 h-3.5 text-amber-600" />
            <span className="text-[11px] font-bold text-amber-800">Prochaine étape à réaliser</span>
          </div>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              {(() => { const Icon = STEP_ICONS[nextStep.id] || Target; return <Icon className="w-4 h-4 text-amber-700" />; })()}
              <span className="text-xs font-semibold text-slate-800">{nextStep.title}</span>
            </div>
            {nextStep.action_label && (
              <Button
                size="sm"
                className="h-7 text-[11px] px-3 bg-amber-500 hover:bg-amber-600 text-white shadow-sm"
                onClick={() => onAction(nextStep)}
                data-testid="next-step-action-btn"
              >
                {nextStep.action_label}
                <ArrowRight className="w-3 h-3 ml-1" />
              </Button>
            )}
          </div>
          {nextInfo.hint && (
            <p className="text-[11px] text-amber-800 leading-relaxed">{nextInfo.hint}</p>
          )}
          {nextInfo.impact && (
            <p className="text-[10px] text-amber-600 mt-1 italic">{nextInfo.impact}</p>
          )}
        </motion.div>
      )}

      {/* Advanced continuation banner when ALL 4 steps are complete */}
      {allComplete && nextInfo && (
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-xl bg-gradient-to-r from-emerald-50 to-teal-50 border-2 border-emerald-300/60 p-3 mb-1"
          data-testid="advanced-next-step-banner"
        >
          <div className="flex items-center gap-1.5 mb-1.5">
            <Trophy className="w-3.5 h-3.5 text-emerald-600" />
            <span className="text-[11px] font-bold text-emerald-800">Continuez à enrichir votre profil</span>
          </div>
          {nextInfo.hint && (
            <p className="text-[11px] text-emerald-800 leading-relaxed">{nextInfo.hint}</p>
          )}
          {nextInfo.impact && (
            <p className="text-[10px] text-emerald-600 mt-1 italic">{nextInfo.impact}</p>
          )}
          {nextInfo.path && (
            <Button
              size="sm"
              className="mt-2 h-7 text-[11px] px-3 bg-emerald-500 hover:bg-emerald-600 text-white shadow-sm"
              onClick={() => onAction({ action_type: "navigate", action_path: nextInfo.path, id: 5 })}
              data-testid="advanced-next-step-action-btn"
            >
              Découvrir
              <ArrowRight className="w-3 h-3 ml-1" />
            </Button>
          )}
        </motion.div>
      )}

      {/* Steps list */}
      {progress.steps.map((step) => {
      const StepIcon = STEP_ICONS[step.id] || Target;
      const colors = STEP_COLORS[step.id] || { bg: "bg-slate-100", text: "text-slate-700", border: "border-slate-200", accent: "bg-slate-500" };
      const isCurrent = step.id === progress.current_step;
      const isInBanner = isCurrent && !step.complete && nextStep;
      return (
        <div
          key={step.id}
          className={`rounded-xl border p-2.5 transition-all ${
            step.complete ? "bg-emerald-50/50 border-emerald-200"
            : isCurrent ? `${colors.bg}/30 ${colors.border} border-2 shadow-sm`
            : "bg-white border-slate-100"
          }`}
          data-testid={`coach-step-${step.id}`}
        >
          <div className="flex items-center gap-2.5">
            <div className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 ${
              step.complete ? "bg-emerald-100" : isCurrent ? colors.bg : "bg-slate-100"
            }`}>
              {step.complete
                ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                : <StepIcon className={`w-3.5 h-3.5 ${isCurrent ? colors.text : "text-slate-400"}`} />
              }
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-1.5">
                <span className={`text-xs font-semibold ${step.complete ? "text-emerald-700" : isCurrent ? "text-slate-900" : "text-slate-500"}`}>
                  {step.title}
                </span>
                {step.complete && <Badge className="text-[8px] bg-emerald-100 text-emerald-700 px-1 py-0">Fait</Badge>}
                {isCurrent && !step.complete && <Badge className={`text-[8px] ${colors.bg} ${colors.text} px-1 py-0`}>En cours</Badge>}
              </div>
              {/* Show details for completed steps */}
              {step.complete && step.details && (
                <div className="flex gap-1.5 mt-0.5 flex-wrap">
                  {step.details.skills > 0 && <span className="text-[9px] text-emerald-600">{step.details.skills} compétences</span>}
                  {step.details.experiences > 0 && <span className="text-[9px] text-emerald-600">{step.details.experiences} exp.</span>}
                  {step.details.savoir_etre_count > 0 && <span className="text-[9px] text-emerald-600">{step.details.savoir_etre_count} savoir-être</span>}
                  {step.details.experiences_count > 0 && <span className="text-[9px] text-emerald-600">{step.details.experiences_count} expériences tracées</span>}
                </div>
              )}
            </div>
            {/* Show action button only if NOT already shown in the banner above */}
            {isCurrent && !step.complete && step.action_label && !isInBanner && (
              <Button
                size="sm"
                className={`h-6 text-[10px] px-2 ${colors.accent} text-white`}
                onClick={() => onAction(step)}
                data-testid={`coach-action-step-${step.id}`}
              >
                {step.action_label}
                <ArrowRight className="w-2.5 h-2.5 ml-0.5" />
              </Button>
            )}
          </div>
        </div>
      );
    })}

      {/* Personalized tips */}
      {tips.length > 0 && (
        <div className="pt-1 space-y-1.5" data-testid="coach-tips">
          <div className="flex items-center gap-1.5 px-1">
            <Lightbulb className="w-3 h-3 text-blue-500" />
            <span className="text-[10px] font-bold text-slate-600">Conseils personnalisés</span>
          </div>
          {tips.map((tip, i) => {
            const TipIcon = TIP_ICONS[tip.icon] || Lightbulb;
            return (
              <div key={i} className={`rounded-lg border px-2.5 py-2 ${
                tip.priority === "high" ? "bg-blue-50/70 border-blue-200" : "bg-slate-50 border-slate-100"
              }`} data-testid={`coach-tip-${i}`}>
                <div className="flex items-start gap-2">
                  <TipIcon className={`w-3 h-3 mt-0.5 shrink-0 ${tip.priority === "high" ? "text-blue-500" : "text-slate-400"}`} />
                  <p className="text-[11px] text-slate-700 leading-relaxed">{tip.text}</p>
                </div>
              </div>
            );
          })}
        </div>
      )}
  </div>
  );
};

/* ───── Chat View ───── */
const ChatView = ({ messages, sending, onSend, onActionClick, inputRef }) => {
  const scrollRef = useRef(null);
  const [input, setInput] = useState("");

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, sending]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || sending) return;
    onSend(input.trim());
    setInput("");
  };

  return (
    <div className="flex flex-col h-[360px]">
      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-3 space-y-3">
        {messages.length === 0 && (
          <div className="text-center py-6">
            <Bot className="w-8 h-8 text-slate-300 mx-auto mb-2" />
            <p className="text-xs text-slate-400">Posez-moi une question sur la plateforme !</p>
            <div className="mt-3 space-y-1.5">
              {["Comment déposer mon CV ?", "Qu'est-ce que D'CLIC PRO ?", "Comment voir mes opportunités ?"].map((q, i) => (
                <button
                  key={i}
                  onClick={() => { setInput(""); onSend(q); }}
                  className="block w-full text-left text-[11px] text-slate-500 hover:text-[#1e3a5f] hover:bg-slate-50 rounded-lg px-3 py-1.5 transition-colors border border-slate-100"
                  data-testid={`coach-suggestion-${i}`}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[85%] rounded-2xl px-3 py-2 ${
              msg.role === "user"
                ? "bg-[#1e3a5f] text-white rounded-br-sm"
                : "bg-slate-100 text-slate-800 rounded-bl-sm"
            }`}>
              <p className="text-xs leading-relaxed whitespace-pre-wrap">{msg.content}</p>
              {msg.actions?.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {msg.actions.map((action, j) => (
                    <button
                      key={j}
                      onClick={() => onActionClick(action)}
                      className="text-[10px] font-medium bg-white/90 text-[#1e3a5f] rounded-full px-2.5 py-1 hover:bg-white transition-colors flex items-center gap-1 shadow-sm"
                      data-testid={`coach-chat-action-${j}`}
                    >
                      <ChevronRight className="w-2.5 h-2.5" />
                      {action.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {sending && (
          <div className="flex justify-start">
            <div className="bg-slate-100 rounded-2xl rounded-bl-sm px-3 py-2">
              <div className="flex items-center gap-1.5">
                <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-2 border-t border-slate-100 flex gap-2">
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Posez votre question..."
          className="flex-1 text-xs bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#1e3a5f]/20 focus:border-[#1e3a5f]"
          disabled={sending}
          data-testid="coach-chat-input"
        />
        <button
          type="submit"
          disabled={!input.trim() || sending}
          className="w-8 h-8 rounded-xl bg-[#1e3a5f] text-white flex items-center justify-center hover:bg-[#2d5a8f] disabled:opacity-40 transition-colors shrink-0"
          data-testid="coach-chat-send-btn"
        >
          {sending ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
        </button>
      </form>
    </div>
  );
};

/* ───── Main CoachVirtuel ───── */
const CoachVirtuel = ({ token, onOpenDclic, refreshKey }) => {
  const navigate = useNavigate();
  const inputRef = useRef(null);
  const [progress, setProgress] = useState(null);
  const [open, setOpen] = useState(false);
  const [minimized, setMinimized] = useState(false);
  const [loading, setLoading] = useState(true);
  const [pulseHint, setPulseHint] = useState(false);
  const [view, setView] = useState("steps"); // "steps" | "chat"
  const [messages, setMessages] = useState([]);
  const [sending, setSending] = useState(false);
  const [stepTransition, setStepTransition] = useState(null);
  const prevCompleted = useRef(null);

  const loadProgress = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/coach/progress?token=${token}`);
      const newProgress = res.data;

      // Detect step completion transition
      if (prevCompleted.current !== null && newProgress.completed > prevCompleted.current) {
        const justCompleted = newProgress.completed;
        const transition = STEP_NEXT_MESSAGES[justCompleted] || {};
        setStepTransition({
          completedStep: justCompleted,
          message: transition.msg || "Étape complétée !",
          icon: transition.icon || "star",
        });
        // Auto-open coach if closed, switch to steps view
        setOpen(true);
        setMinimized(false);
        setView("steps");
        // Clear transition after 8 seconds
        setTimeout(() => setStepTransition(null), 8000);
      }
      prevCompleted.current = newProgress.completed;

      setProgress(newProgress);
      const coachDismissed = localStorage.getItem(`coach_dismissed_${token}`);
      if (!coachDismissed && newProgress.completed < 4) {
        setTimeout(() => setOpen(true), 1500);
      } else if (newProgress.completed < 4) {
        setTimeout(() => setPulseHint(true), 3000);
      }
    } catch (e) {
      console.error("Coach progress error:", e);
    }
    setLoading(false);
  }, [token]);

  useEffect(() => { loadProgress(); }, [loadProgress, refreshKey]);

  // Auto-refresh every 15s to detect completed steps
  useEffect(() => {
    const interval = setInterval(() => {
      if (progress && progress.completed < 4) {
        loadProgress();
      }
    }, 15000);
    return () => clearInterval(interval);
  }, [loadProgress, progress]);

  const handleDismiss = () => {
    setOpen(false);
    localStorage.setItem(`coach_dismissed_${token}`, "true");
  };

  const handleAction = (step) => {
    if (step.action_type === "dclic") {
      window.open('/test-dclic', '_blank');
      setOpen(false);
    } else if (step.action_type === "navigate") {
      // Map step IDs to correct paths with sub-tabs (resilient to backend version)
      const STEP_PATHS = {
        1: "/dashboard/trajectoire?sub=cv",
        2: "/dashboard/competences",
        4: "/dashboard/trajectoire?sub=trajectoire",
      };
      const path = STEP_PATHS[step.id] || step.action_path || "/dashboard";
      navigate(path);
      setOpen(false);
    }
  };

  const handleReopen = () => {
    setOpen(true);
    setPulseHint(false);
    localStorage.removeItem(`coach_dismissed_${token}`);
  };

  const handleChatAction = (action) => {
    if (action.path === "dclic") {
      window.open('/test-dclic', '_blank');
      setOpen(false);
    } else if (action.path.startsWith("/")) {
      navigate(action.path);
      setOpen(false);
    }
  };

  const handleSend = async (text) => {
    const userMsg = { role: "user", content: text };
    setMessages(prev => [...prev, userMsg]);
    setSending(true);

    try {
      const res = await axios.post(
        `${API}/coach/chat?token=${encodeURIComponent(token)}`,
        {
          message: text,
          history: [...messages, userMsg].slice(-6).map(m => ({ role: m.role, content: m.content })),
        }
      );
      setMessages(prev => [
        ...prev,
        { role: "assistant", content: res.data.response, actions: res.data.actions },
      ]);
    } catch (e) {
      setMessages(prev => [
        ...prev,
        { role: "assistant", content: "Désolé, je rencontre un problème. Réessayez dans un instant.", actions: [] },
      ]);
    }
    setSending(false);
  };

  if (loading || !progress) return null;

  const EmojiIcon = EMOJI_ICONS[progress.emoji] || Star;

  return (
    <>
      {/* Floating Bubble */}
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
            className={`fixed bottom-6 right-6 z-50 rounded-2xl bg-white shadow-2xl border border-slate-200 overflow-hidden flex flex-col ${minimized ? "w-[280px]" : "w-[380px]"}`}
            style={{ maxHeight: minimized ? "auto" : (view === "chat" ? "520px" : "480px") }}
            data-testid="coach-panel"
          >
            {/* Header */}
            <div className={`bg-gradient-to-r from-[#1e3a5f] to-[#2d5a8f] ${minimized ? "p-2.5 cursor-pointer" : "p-3"} text-white shrink-0`}
              onClick={minimized ? () => setMinimized(false) : undefined}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <div className={`${minimized ? "w-7 h-7" : "w-9 h-9"} rounded-full bg-white/20 flex items-center justify-center backdrop-blur-sm`}>
                    {view === "chat" ? <Bot className={`${minimized ? "w-3.5 h-3.5" : "w-4.5 h-4.5"}`} /> : <EmojiIcon className={`${minimized ? "w-3.5 h-3.5" : "w-4.5 h-4.5"}`} />}
                  </div>
                  <div>
                    <h3 className={`font-semibold ${minimized ? "text-xs" : "text-sm"}`}>Coach RE'ACTIF</h3>
                    {!minimized && <p className="text-[10px] text-white/70">{view === "chat" ? "Assistant IA" : `${progress.completed}/4 étapes`}</p>}
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  {minimized ? (
                    <button
                      onClick={(e) => { e.stopPropagation(); setMinimized(false); }}
                      className="w-6 h-6 rounded-full hover:bg-white/20 flex items-center justify-center transition-colors"
                      data-testid="coach-expand-btn"
                      title="Agrandir"
                    >
                      <ChevronRight className="w-3.5 h-3.5 -rotate-90" />
                    </button>
                  ) : (
                    <>
                  {/* Toggle view */}
                  <button
                    onClick={() => {
                      setView(v => v === "steps" ? "chat" : "steps");
                      if (view === "steps") setTimeout(() => inputRef.current?.focus(), 200);
                    }}
                    className="w-7 h-7 rounded-full hover:bg-white/20 flex items-center justify-center transition-colors"
                    data-testid="coach-toggle-view-btn"
                    title={view === "steps" ? "Ouvrir le chat" : "Voir les étapes"}
                  >
                    {view === "steps" ? <Bot className="w-4 h-4" /> : <ListChecks className="w-4 h-4" />}
                  </button>
                  <button
                    onClick={() => setMinimized(true)}
                    className="w-7 h-7 rounded-full hover:bg-white/20 flex items-center justify-center transition-colors"
                    data-testid="coach-minimize-btn"
                    title="Réduire"
                  >
                    <Minus className="w-4 h-4" />
                  </button>
                  <button
                    onClick={handleDismiss}
                    className="w-7 h-7 rounded-full hover:bg-white/20 flex items-center justify-center transition-colors"
                    data-testid="coach-close-btn"
                  >
                    <X className="w-4 h-4" />
                  </button>
                    </>
                  )}
                </div>
              </div>

              {/* Progress bar (only in steps view, not minimized) */}
              {!minimized && view === "steps" && (
                <div className="mt-2">
                  <div className="h-1.5 bg-white/20 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${progress.progress_pct}%` }}
                      transition={{ duration: 0.8, ease: "easeOut" }}
                      className="h-full bg-gradient-to-r from-amber-300 to-emerald-300 rounded-full"
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Content - hidden when minimized */}
            {!minimized && (view === "steps" ? (
              <>
                {/* Step Transition Banner */}
                {stepTransition && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="bg-gradient-to-r from-emerald-500 to-teal-500 px-3 py-3 text-white shrink-0"
                  >
                    <div className="flex items-start gap-2">
                      <div className="w-7 h-7 rounded-full bg-white/20 flex items-center justify-center shrink-0">
                        <CheckCircle2 className="w-4 h-4" />
                      </div>
                      <div className="flex-1">
                        <p className="text-xs font-semibold">Étape {stepTransition.completedStep} terminée !</p>
                        <p className="text-[11px] text-white/90 mt-0.5 leading-relaxed">{stepTransition.message}</p>
                      </div>
                      <button onClick={() => setStepTransition(null)} className="text-white/60 hover:text-white shrink-0">
                        <X className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </motion.div>
                )}

                {/* Coach Message */}
                <div className="px-3 py-2.5 bg-slate-50 border-b border-slate-100 shrink-0">
                  <p className="text-xs text-slate-700 leading-relaxed" data-testid="coach-message">
                    {progress.message}
                  </p>
                </div>
                <div className="overflow-y-auto flex-1">
                  <StepsView progress={progress} onAction={handleAction} />
                </div>
                {/* Chat prompt at bottom */}
                <div className="p-2 border-t border-slate-100 shrink-0">
                  <button
                    onClick={() => { setView("chat"); setTimeout(() => inputRef.current?.focus(), 200); }}
                    className="w-full flex items-center gap-2 text-xs text-slate-500 hover:text-[#1e3a5f] bg-slate-50 hover:bg-slate-100 rounded-xl px-3 py-2 transition-colors"
                    data-testid="coach-open-chat-btn"
                  >
                    <Bot className="w-3.5 h-3.5" />
                    <span>Besoin d'aide ? Posez-moi une question...</span>
                  </button>
                </div>
              </>
            ) : (
              <ChatView
                messages={messages}
                sending={sending}
                onSend={handleSend}
                onActionClick={handleChatAction}
                inputRef={inputRef}
              />
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default CoachVirtuel;
