import React, { useState, useEffect, useMemo, useCallback } from "react";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Switch } from "@/components/ui/switch";
import {
  User, Target, TrendingUp, BookOpen, Briefcase, MapPin, Clock, Euro,
  Star, ChevronRight, Plus, Sparkles, Zap, Award, AlertCircle,
  Play, FolderLock, FileDown, FileText, LayoutList, Layers, Shield, BarChart3,
  ExternalLink, Upload, CheckCircle, Bell, CheckCircle2, Loader2,
  Route, Eye, EyeOff, Users, Building2, Handshake, GraduationCap,
  Trash2, Edit3, ChevronDown, ChevronUp, Lock, History, RefreshCw,
  Lightbulb, Compass, Heart, Brain, ArrowRight, Share2, Link2, Copy,
  Check, QrCode, Download, X, ShieldCheck, CalendarDays, PauseCircle,
  SlidersHorizontal
} from "lucide-react";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";
import CvAnalysisSection from "@/components/CvAnalysis/CvAnalysisSection";
import CentresInteretSection from "@/components/CentresInteretSection";
import JobMatchingSection from "@/components/JobMatchingSection";
import GpsDashboard from "@/components/GpsDashboard";
import { QRCodeSVG } from "qrcode.react";
import { toPng } from "html-to-image";
import { motion } from "framer-motion";

// ===== STEP TYPE CONFIG =====
const STEP_TYPES = {
  emploi:        { label: "Emploi",           color: "bg-blue-500",    bg: "bg-blue-50",    text: "text-blue-700",    border: "border-blue-200",    icon: Briefcase },
  formation:     { label: "Formation",        color: "bg-emerald-500", bg: "bg-emerald-50", text: "text-emerald-700", border: "border-emerald-200", icon: GraduationCap },
  stage:         { label: "Stage",            color: "bg-cyan-500",    bg: "bg-cyan-50",    text: "text-cyan-700",    border: "border-cyan-200",    icon: BookOpen },
  interim:       { label: "Mission intérim",  color: "bg-indigo-500",  bg: "bg-indigo-50",  text: "text-indigo-700",  border: "border-indigo-200",  icon: Clock },
  reconversion:  { label: "Reconversion",     color: "bg-violet-500",  bg: "bg-violet-50",  text: "text-violet-700",  border: "border-violet-200",  icon: RefreshCw },
  recherche:     { label: "Recherche emploi", color: "bg-amber-500",   bg: "bg-amber-50",   text: "text-amber-700",   border: "border-amber-200",   icon: Target },
  pause:         { label: "Pause / Personnel",color: "bg-slate-400",   bg: "bg-slate-50",   text: "text-slate-600",   border: "border-slate-200",   icon: Heart },
  benevolat:     { label: "Bénévolat",        color: "bg-rose-500",    bg: "bg-rose-50",    text: "text-rose-700",    border: "border-rose-200",    icon: Users },
  creation:      { label: "Création activité",color: "bg-orange-500",  bg: "bg-orange-50",  text: "text-orange-700",  border: "border-orange-200",  icon: Lightbulb },
  mobilite:      { label: "Mobilité géo.",    color: "bg-teal-500",    bg: "bg-teal-50",    text: "text-teal-700",    border: "border-teal-200",    icon: Compass },
  certification: { label: "Certification",    color: "bg-pink-500",    bg: "bg-pink-50",    text: "text-pink-700",    border: "border-pink-200",    icon: Award },
};

const VISIBILITY_OPTIONS = [
  { value: "private", label: "Moi uniquement", icon: Lock },
  { value: "accompagnateur", label: "Accompagnateurs autorisés", icon: Handshake },
  { value: "recruteur", label: "Recruteurs autorisés", icon: Building2 },
  { value: "public", label: "Version synthétique publique", icon: Eye },
];

// ===== D'CLIC PRO BOOST VISUAL SECTION =====
const DclicBoostSection = ({ profile, token }) => {
  const [expanded, setExpanded] = useState(false);
  const dclicSkills = (profile.skills || []).filter(s => s.source === "dclic_pro");
  const competences = profile.dclic_competences || [];
  const dimensions = [
    profile.dclic_disc_label && { label: "Profil DISC", value: profile.dclic_disc_label, color: "from-blue-500 to-cyan-600", icon: Target, description: "Votre style comportemental" },
    profile.dclic_riasec_major && { label: "Intérêts RIASEC", value: profile.dclic_riasec_major, color: "from-emerald-500 to-teal-600", icon: TrendingUp, description: "Votre orientation professionnelle" },
    profile.dclic_vertu_dominante && { label: "Vertu dominante", value: profile.dclic_vertu_dominante, color: "from-amber-500 to-orange-600", icon: Award, description: "Votre force motrice" },
  ].filter(Boolean);

  const handleDownloadProfile = async () => {
    try {
      const res = await axios.get(`${API}/profile?token=${token}`);
      const p = res.data;
      const content = [
        "═══ PROFIL D'CLIC PRO ═══",
        "",
        `Pseudo: ${p.pseudo || ""}`,
        `Date: ${new Date().toLocaleDateString("fr-FR")}`,
        "",
        "── Dimensions analysées ──",
        p.dclic_mbti ? `Personnalité MBTI: ${p.dclic_mbti}` : "",
        p.dclic_disc_label ? `Profil DISC: ${p.dclic_disc_label}` : "",
        p.dclic_riasec_major ? `Intérêts RIASEC: ${p.dclic_riasec_major}` : "",
        p.dclic_vertu_dominante ? `Vertu dominante: ${p.dclic_vertu_dominante}` : "",
        "",
        "── Compétences identifiées ──",
        ...(p.dclic_competences || []).map(c => `• ${c}`),
        "",
        "── Skills D'CLIC ──",
        ...(p.skills || []).filter(s => s.source === "dclic_pro").map(s => `• ${s.name} — ${s.level}%`),
      ].filter(Boolean).join("\n");
      const blob = new Blob([content], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `profil-dclic-pro-${p.pseudo || "user"}.txt`;
      a.click();
      URL.revokeObjectURL(url);
      toast.success("Profil D'CLIC PRO téléchargé");
    } catch {
      toast.error("Erreur lors du téléchargement");
    }
  };

  const handleSaveToCoffre = async () => {
    try {
      const res = await axios.get(`${API}/profile?token=${token}`);
      const p = res.data;
      const content = [
        "PROFIL D'CLIC PRO",
        `Date: ${new Date().toLocaleDateString("fr-FR")}`,
        "",
        p.dclic_mbti ? `MBTI: ${p.dclic_mbti}` : "",
        p.dclic_disc_label ? `DISC: ${p.dclic_disc_label}` : "",
        p.dclic_riasec_major ? `RIASEC: ${p.dclic_riasec_major}` : "",
        p.dclic_vertu_dominante ? `Vertu: ${p.dclic_vertu_dominante}` : "",
        "",
        "Compétences:",
        ...(p.dclic_competences || []).map(c => `- ${c}`),
      ].filter(Boolean).join("\n");
      const blob = new Blob([content], { type: "text/plain" });
      const formData = new FormData();
      formData.append("file", blob, `profil-dclic-pro.txt`);
      formData.append("title", "Profil D'CLIC PRO");
      formData.append("document_type", "profil_dclic");
      await axios.post(`${API}/coffre/upload?token=${token}`, formData);
      toast.success("Profil D'CLIC PRO sauvegardé dans le coffre-fort");
    } catch (e) {
      if (e.response?.status === 409) toast.info("Déjà dans le coffre-fort");
      else toast.error("Erreur lors de la sauvegarde");
    }
  };

  return (
    <Card className="border-0 shadow-lg overflow-hidden" data-testid="dclic-boost-section">
      <div className="bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 p-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-xl bg-white/20 backdrop-blur-sm flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                Profil boosté avec D'CLIC PRO
                <CheckCircle className="w-4 h-4 text-emerald-200" />
              </h3>
              <p className="text-emerald-100 text-xs mt-0.5">
                {dimensions.length} dimensions analysées — {competences.length + dclicSkills.length} compétences identifiées
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" className="text-white hover:bg-white/10" onClick={handleDownloadProfile} data-testid="dclic-download-btn">
              <Download className="w-4 h-4" />
              <span className="ml-1 text-xs">Télécharger</span>
            </Button>
            <Button variant="ghost" size="sm" className="text-white hover:bg-white/10" onClick={handleSaveToCoffre} data-testid="dclic-coffre-btn">
              <FolderLock className="w-4 h-4" />
              <span className="ml-1 text-xs">Coffre-fort</span>
            </Button>
          </div>
        </div>
      </div>
      <CardContent className="p-5">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {dimensions.map((dim, idx) => {
            const DIcon = dim.icon;
            return (
              <div key={idx} className="relative overflow-hidden rounded-xl p-4 text-center" data-testid={`dclic-dim-${idx}`}>
                <div className={`absolute inset-0 bg-gradient-to-br ${dim.color} opacity-10`} />
                <DIcon className={`w-5 h-5 mx-auto mb-2 bg-gradient-to-br ${dim.color} bg-clip-text`} style={{color: 'inherit'}} />
                <p className="text-xs text-slate-500 mb-1">{dim.label}</p>
                <p className="text-lg font-bold text-slate-900">{dim.value}</p>
              </div>
            );
          })}
        </div>
        {(competences.length > 0 || dclicSkills.length > 0) && (
          <div className="mt-4 pt-4 border-t border-slate-100 space-y-3">
            {competences.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Compétences fortes</p>
                <div className="flex flex-wrap gap-1.5">
                  {competences.map((c, i) => (
                    <Badge key={i} className="bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs" data-testid={`dclic-comp-${i}`}>{c}</Badge>
                  ))}
                </div>
              </div>
            )}
            {dclicSkills.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Skills importés D'CLIC</p>
                <div className="flex flex-wrap gap-1.5">
                  {dclicSkills.map((s, i) => (
                    <Badge key={i} variant="outline" className="text-xs">{s.name} — {s.level}%</Badge>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// ===== TIMELINE STEP CARD (modèle chronologique détaillé) =====
const TimelineStepCard = ({ step, onEdit, onDelete, onVisibilityChange }) => {
  const config = STEP_TYPES[step.step_type] || STEP_TYPES.emploi;
  const StepIcon = config.icon;
  const visOpt = VISIBILITY_OPTIONS.find(v => v.value === step.visibility) || VISIBILITY_OPTIONS[0];
  const VisIcon = visOpt.icon;

  const period = step.start_date
    ? `${step.start_date}${step.end_date ? ` — ${step.end_date}` : step.is_ongoing ? " — Aujourd'hui" : ""}`
    : "";

  // Map step_type to gradient
  const gradientMap = {
    emploi: "from-blue-50 to-white", formation: "from-emerald-50 to-white", stage: "from-cyan-50 to-white",
    interim: "from-indigo-50 to-white", reconversion: "from-violet-50 to-white", recherche: "from-amber-50 to-white",
    pause: "from-slate-50 to-white", benevolat: "from-rose-50 to-white", creation: "from-orange-50 to-white",
    mobilite: "from-teal-50 to-white", certification: "from-pink-50 to-white"
  };
  const cardGradient = gradientMap[step.step_type] || "from-blue-50 to-white";

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className="relative pl-8"
      data-testid={`timeline-step-${step.id}`}
    >
      {/* Dot on timeline */}
      <div className={`absolute left-0 top-8 h-4 w-4 rounded-full ring-4 ring-white ${config.color} z-10`} />

      <Card className={`overflow-hidden rounded-2xl border-0 bg-gradient-to-br ${cardGradient} shadow-sm hover:shadow-md transition-shadow`}>
        <CardContent className="p-5">
          {/* Header: Type + Year + Dates */}
          <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
            <div className="space-y-2">
              <div className="flex flex-wrap items-center gap-2">
                <Badge className={`rounded-full border text-xs font-semibold ${config.bg} ${config.text} ${config.border}`}>{config.label}</Badge>
                {step.start_date && <Badge variant="outline" className="rounded-full text-xs">{step.start_date.substring(0, 4)}</Badge>}
              </div>
              <div>
                <h3 className="text-lg font-semibold text-slate-900">{step.title}</h3>
                {step.organization && (
                  <p className="mt-0.5 text-sm text-slate-500 flex items-center gap-1.5">
                    <Building2 className="w-3.5 h-3.5" />{step.organization}
                  </p>
                )}
              </div>
            </div>

            <div className="flex items-center gap-2">
              {period && (
                <div className="flex items-center gap-2 rounded-xl bg-white/80 px-3 py-1.5 text-sm text-slate-600 shadow-sm shrink-0">
                  <CalendarDays className="h-3.5 w-3.5" />
                  <span className="text-xs">{period}</span>
                </div>
              )}
              <Button variant="ghost" size="icon" className="h-7 w-7 shrink-0" onClick={() => onEdit(step)} data-testid={`edit-step-${step.id}`}>
                <Edit3 className="w-3.5 h-3.5 text-slate-400" />
              </Button>
              <Button variant="ghost" size="icon" className="h-7 w-7 shrink-0" onClick={() => onDelete(step.id)} data-testid={`delete-step-${step.id}`}>
                <Trash2 className="w-3.5 h-3.5 text-red-300" />
              </Button>
            </div>
          </div>

          {/* Body: Two columns */}
          <div className="mt-4 grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
            {/* Left: Details */}
            <div className="space-y-3">
              {/* Description / Summary */}
              {step.description && (
                <div>
                  <div className="flex items-center gap-2 text-sm font-medium text-slate-800 mb-1">
                    <StepIcon className="h-3.5 w-3.5" />
                    <span>Ce que comprend cette étape</span>
                  </div>
                  <p className="text-sm leading-relaxed text-slate-600">{step.description}</p>
                </div>
              )}

              {/* Missions */}
              {step.missions?.length > 0 && (
                <div>
                  <div className="mb-1.5 text-xs font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                    <Target className="w-3 h-3" />Missions principales
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {step.missions.map((m, i) => (
                      <span key={i} className="text-xs bg-slate-100 text-slate-700 rounded-full px-2.5 py-0.5">{m}</span>
                    ))}
                  </div>
                </div>
              )}

              {/* Competences */}
              {step.competences?.length > 0 && (
                <div>
                  <div className="mb-1.5 text-sm font-medium text-slate-800">Compétences mobilisées</div>
                  <div className="flex flex-wrap gap-1.5">
                    {step.competences.map((c, i) => (
                      <Badge key={i} variant="secondary" className="rounded-full bg-white text-slate-700 shadow-sm text-xs">{c}</Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Acquis / Gains */}
              {step.acquis && (
                <div>
                  <div className="mb-1 text-sm font-medium text-slate-800">Apport de l'étape</div>
                  <p className="text-sm leading-relaxed text-slate-600">{step.acquis}</p>
                </div>
              )}
            </div>

            {/* Right: Visibility */}
            <div className="rounded-xl bg-white/80 p-4 shadow-sm">
              <div className="flex items-center gap-2 text-sm font-medium text-slate-800">
                <VisIcon className="h-4 w-4" />
                <span>Visibilité actuelle</span>
              </div>
              <p className="mt-1.5 text-sm text-slate-600">{visOpt.label}</p>
              <div className="mt-3">
                <div className="mb-1.5 text-xs uppercase tracking-wide text-slate-500">Modifier</div>
                <Select value={step.visibility} onValueChange={v => onVisibilityChange && onVisibilityChange(step.id, v)}>
                  <SelectTrigger className="rounded-xl bg-white text-xs h-9" data-testid={`visibility-select-${step.id}`}>
                    <SelectValue placeholder="Choisir la visibilité" />
                  </SelectTrigger>
                  <SelectContent>
                    {VISIBILITY_OPTIONS.map(opt => {
                      const OI = opt.icon;
                      return <SelectItem key={opt.value} value={opt.value}><span className="flex items-center gap-1.5 text-xs"><OI className="w-3 h-3" />{opt.label}</span></SelectItem>;
                    })}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

// ===== CONSULTATION HISTORY =====
const ConsultationHistory = ({ token }) => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await axios.get(`${API}/trajectory/access-log?token=${token}`);
        setLogs(res.data);
      } catch {}
      setLoading(false);
    };
    load();
  }, [token]);

  if (loading || logs.length === 0) return null;

  return (
    <Card className="border border-slate-100" data-testid="consultation-history">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-sm">
          <History className="w-4 h-4 text-slate-500" />Consultations de mon parcours
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {logs.slice(0, 8).map((log, idx) => (
            <div key={idx} className="flex items-center justify-between py-1.5 px-2 rounded-lg bg-slate-50 text-xs" data-testid={`consult-log-${idx}`}>
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center">
                  <Eye className="w-3 h-3 text-blue-600" />
                </div>
                <div>
                  <span className="font-medium text-slate-700">
                    {log.audience === "accompagnateur" ? "Accompagnateur" : log.audience === "recruteur" ? "Recruteur" : "Consultation"}
                  </span>
                  <span className="text-slate-400 ml-2">via lien partagé</span>
                </div>
              </div>
              <span className="text-slate-400">{new Date(log.accessed_at).toLocaleDateString('fr-FR')}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

// ===== ADD/EDIT STEP DIALOG =====
const StepFormDialog = ({ open, onOpenChange, step, token, onSaved }) => {
  const isEdit = !!step?.id;
  const [form, setForm] = useState({
    step_type: "emploi", title: "", organization: "", start_date: "", end_date: "",
    is_ongoing: false, description: "", missions: "", competences: "", acquis: "",
    personal_note: "", visibility: "private"
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (step) {
      setForm({
        step_type: step.step_type || "emploi",
        title: step.title || "",
        organization: step.organization || "",
        start_date: step.start_date || "",
        end_date: step.end_date || "",
        is_ongoing: step.is_ongoing || false,
        description: step.description || "",
        missions: (step.missions || []).join(", "),
        competences: (step.competences || []).join(", "),
        acquis: step.acquis || "",
        personal_note: step.personal_note || "",
        visibility: step.visibility || "private"
      });
    } else {
      setForm({ step_type: "emploi", title: "", organization: "", start_date: "", end_date: "",
        is_ongoing: false, description: "", missions: "", competences: "", acquis: "",
        personal_note: "", visibility: "private" });
    }
  }, [step, open]);

  const save = async () => {
    if (!form.title.trim()) { toast.error("Le titre est obligatoire"); return; }
    setSaving(true);
    try {
      const payload = {
        ...form,
        missions: form.missions.split(",").map(s => s.trim()).filter(Boolean),
        competences: form.competences.split(",").map(s => s.trim()).filter(Boolean),
      };
      if (isEdit) {
        await axios.put(`${API}/trajectory/steps/${step.id}?token=${token}`, payload);
      } else {
        await axios.post(`${API}/trajectory/steps?token=${token}`, payload);
      }
      toast.success(isEdit ? "Étape modifiée" : "Étape ajoutée");
      onSaved();
      onOpenChange(false);
    } catch (e) {
      toast.error(e.response?.data?.detail || "Erreur");
    }
    setSaving(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{isEdit ? "Modifier l'étape" : "Ajouter une étape"}</DialogTitle>
          <DialogDescription>Décrivez cette étape de votre parcours professionnel</DialogDescription>
        </DialogHeader>
        <div className="space-y-4 mt-2">
          <div>
            <label className="text-sm font-medium text-slate-700 mb-1.5 block">Type d'étape</label>
            <Select value={form.step_type} onValueChange={v => setForm(p => ({...p, step_type: v}))}>
              <SelectTrigger data-testid="step-type-select"><SelectValue /></SelectTrigger>
              <SelectContent>
                {Object.entries(STEP_TYPES).map(([k, v]) => {
                  const I = v.icon;
                  return <SelectItem key={k} value={k}><span className="flex items-center gap-2"><I className="w-3.5 h-3.5" />{v.label}</span></SelectItem>;
                })}
              </SelectContent>
            </Select>
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700 mb-1.5 block">Titre / Fonction *</label>
            <Input value={form.title} onChange={e => setForm(p => ({...p, title: e.target.value}))} placeholder="Ex: Responsable RH" data-testid="step-title-input" />
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700 mb-1.5 block">Structure / Organisme</label>
            <Input value={form.organization} onChange={e => setForm(p => ({...p, organization: e.target.value}))} placeholder="Ex: Pôle emploi" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-sm font-medium text-slate-700 mb-1.5 block">Début</label>
              <Input value={form.start_date} onChange={e => setForm(p => ({...p, start_date: e.target.value}))} placeholder="Ex: 2022-03" />
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700 mb-1.5 block">Fin</label>
              <Input value={form.end_date} onChange={e => setForm(p => ({...p, end_date: e.target.value}))} placeholder="Ex: 2024-06" disabled={form.is_ongoing} />
              <label className="flex items-center gap-2 mt-1.5 cursor-pointer">
                <Switch checked={form.is_ongoing} onCheckedChange={v => setForm(p => ({...p, is_ongoing: v, end_date: v ? "" : p.end_date}))} />
                <span className="text-xs text-slate-500">En cours</span>
              </label>
            </div>
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700 mb-1.5 block">Description</label>
            <Textarea value={form.description} onChange={e => setForm(p => ({...p, description: e.target.value}))} rows={2} placeholder="Décrivez cette étape..." />
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700 mb-1.5 block">Compétences mobilisées (séparées par des virgules)</label>
            <Input value={form.competences} onChange={e => setForm(p => ({...p, competences: e.target.value}))} placeholder="Communication, Gestion, Excel..." />
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700 mb-1.5 block">Ce que j'ai développé / Acquis</label>
            <Input value={form.acquis} onChange={e => setForm(p => ({...p, acquis: e.target.value}))} placeholder="Adaptation, leadership..." />
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700 mb-1.5 block">Visibilité de cette étape</label>
            <Select value={form.visibility} onValueChange={v => setForm(p => ({...p, visibility: v}))}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                {VISIBILITY_OPTIONS.map(opt => {
                  const OI = opt.icon;
                  return <SelectItem key={opt.value} value={opt.value}><span className="flex items-center gap-2"><OI className="w-3.5 h-3.5" />{opt.label}</span></SelectItem>;
                })}
              </SelectContent>
            </Select>
          </div>
          <Button onClick={save} disabled={saving} className="w-full bg-[#1e3a5f] hover:bg-[#152a45]" data-testid="save-step-btn">
            {saving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : null}
            {isEdit ? "Modifier" : "Ajouter l'étape"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

// ===== VISIBILITY CARDS =====
const VisibilityCards = ({ settings, onUpdate }) => {
  const cards = [
    { key: "self", label: "Moi uniquement", desc: "Version complète de mon parcours", icon: User, status: "Toujours actif", active: true, locked: true, color: "emerald" },
    { key: "conseiller", label: "Conseiller / Accompagnateur", desc: "Accès sur autorisation", icon: Handshake, status: settings?.conseiller ? "Autorisé" : "Désactivé", active: !!settings?.conseiller, color: "blue" },
    { key: "recruteur", label: "Recruteurs / Employeurs", desc: "Version adaptée candidature", icon: Building2, status: settings?.recruteur ? "Autorisé" : "Désactivé", active: !!settings?.recruteur, color: "violet" },
    { key: "partenaire", label: "Services RH", desc: "Accès limité au suivi", icon: Building2, status: settings?.partenaire ? "Autorisé" : "Désactivé", active: !!settings?.partenaire, color: "amber" },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3" data-testid="visibility-cards">
      {cards.map(card => {
        const CIcon = card.icon;
        const bgColor = card.active ? `bg-${card.color}-50` : "bg-slate-50";
        const borderColor = card.active ? `border-${card.color}-200` : "border-slate-200";
        const textColor = card.active ? `text-${card.color}-700` : "text-slate-500";
        return (
          <Card key={card.key} className={`${bgColor} ${borderColor} border transition-all ${!card.locked ? "cursor-pointer hover:shadow-md" : ""}`}
            onClick={() => { if (!card.locked) onUpdate({ ...settings, [card.key]: !settings?.[card.key] }); }}
            data-testid={`visibility-card-${card.key}`}
          >
            <CardContent className="p-4 text-center">
              <div className={`w-10 h-10 rounded-full ${card.active ? `bg-${card.color}-100` : "bg-slate-100"} flex items-center justify-center mx-auto mb-2`}>
                <CIcon className={`w-5 h-5 ${textColor}`} />
              </div>
              <h4 className="text-sm font-semibold text-slate-800 mb-0.5">{card.label}</h4>
              <p className="text-[11px] text-slate-500 mb-2">{card.desc}</p>
              <Badge className={`text-[10px] ${card.active ? `bg-${card.color}-100 ${textColor}` : "bg-slate-100 text-slate-500"}`}>
                {card.status}
              </Badge>
              {!card.locked && (
                <div className="mt-2 flex items-center justify-center gap-1.5">
                  <Switch checked={card.active} onCheckedChange={() => onUpdate({ ...settings, [card.key]: !settings?.[card.key] })} />
                </div>
              )}
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
};

// ===== SYNTHESIS SECTION =====
const SynthesisSection = ({ synthesis, loading, token, onRefresh }) => {
  if (loading) {
    return (
      <Card className="rounded-2xl border-0 shadow-sm">
        <CardContent className="p-6 flex items-center gap-3">
          <Loader2 className="w-5 h-5 animate-spin text-violet-600" />
          <span className="text-sm text-violet-700">Analyse de votre parcours en cours...</span>
        </CardContent>
      </Card>
    );
  }
  if (!synthesis) return null;

  const scores = synthesis.scores || {};
  const dominantSkills = synthesis.competences_dominantes || synthesis.forces_recurrentes || [];

  return (
    <div className="space-y-5">
      {/* Ce que mon parcours révèle */}
      <Card className="rounded-2xl border-0 shadow-sm" data-testid="synthesis-insights">
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-lg text-slate-900">
            <Sparkles className="h-5 w-5" />
            Ce que mon parcours révèle
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 text-sm leading-6 text-slate-600">
          <p>{synthesis.analyse_narrative || synthesis.fil_conducteur}</p>
          {dominantSkills.length > 0 && (
            <div>
              <div className="mb-2 text-sm font-medium text-slate-900">Compétences les plus visibles</div>
              <div className="flex flex-wrap gap-2">
                {dominantSkills.map((skill, i) => (
                  <Badge key={i} className="rounded-full bg-[#1e3a5f] text-white hover:bg-[#1e3a5f] text-xs">{skill}</Badge>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Lecture de cohérence */}
      <Card className="rounded-2xl border-0 shadow-sm" data-testid="synthesis-scores">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base text-slate-900">Lecture de cohérence</CardTitle>
            <Button
              variant="outline"
              size="sm"
              className="text-[10px] h-7 px-2 text-indigo-600 border-indigo-200 hover:bg-indigo-50 rounded-lg"
              onClick={() => onRefresh && onRefresh()}
              data-testid="refresh-synthesis-btn"
            >
              <RefreshCw className="w-3 h-3 mr-1" />
              Actualiser
            </Button>
          </div>
        </CardHeader>
        <CardContent className="text-sm leading-6 text-slate-600">
          <div className="space-y-3">
            {[
              { label: "Cohérence", value: scores.coherence || 0 },
              { label: "Adaptabilité", value: scores.adaptabilite || 0 },
              { label: "Transférabilité", value: scores.transferabilite || 0 },
              { label: "Continuité", value: scores.continuite || 0 },
              { label: "Alignement métier", value: scores.alignement_metier || 0 },
            ].map((item, i) => (
              <div key={i}>
                <div className="mb-1 flex items-center justify-between text-sm text-slate-700">
                  <span>{item.label}</span>
                  <span className="font-semibold">{item.value}%</span>
                </div>
                <Progress value={item.value} className="h-2" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Détails de l'analyse */}
      {(synthesis.forces_recurrentes?.length > 0 || synthesis.competences_transferables?.length > 0) && (
        <Card className="rounded-2xl border-0 shadow-sm" data-testid="synthesis-details">
          <CardContent className="p-5 space-y-3">
            {synthesis.forces_recurrentes?.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-emerald-800 mb-2 flex items-center gap-1"><Zap className="w-3.5 h-3.5" /> Forces récurrentes</p>
                <div className="flex flex-wrap gap-1.5">
                  {synthesis.forces_recurrentes.map((f, i) => <Badge key={i} className="bg-emerald-100 text-emerald-700 text-xs rounded-full">{f}</Badge>)}
                </div>
              </div>
            )}
            {synthesis.competences_transferables?.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-violet-800 mb-2 flex items-center gap-1"><Sparkles className="w-3.5 h-3.5" /> Compétences transférables</p>
                <div className="flex flex-wrap gap-1.5">
                  {synthesis.competences_transferables.map((c, i) => <Badge key={i} className="bg-violet-100 text-violet-700 text-xs rounded-full">{c}</Badge>)}
                </div>
              </div>
            )}
            {synthesis.axes_evolution?.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-slate-700 mb-2 flex items-center gap-1"><TrendingUp className="w-3.5 h-3.5" /> Axes d'évolution</p>
                <div className="space-y-1">
                  {synthesis.axes_evolution.map((a, i) => (
                    <p key={i} className="text-sm text-slate-600 flex items-center gap-2"><ArrowRight className="w-3 h-3 text-blue-500 shrink-0" />{a}</p>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {synthesis.message_valorisant && (
        <div className="p-4 bg-gradient-to-r from-blue-50 to-violet-50 rounded-xl border border-blue-100 text-center">
          <p className="text-sm font-medium text-slate-800 italic">"{synthesis.message_valorisant}"</p>
        </div>
      )}
    </div>
  );
};

// ===== SHARE DIALOG =====
const ShareDialog = ({ open, onOpenChange, token }) => {
  const [audience, setAudience] = useState("accompagnateur");
  const [durationDays, setDurationDays] = useState("30");
  const [includeSynthesis, setIncludeSynthesis] = useState(true);
  const [includeCard, setIncludeCard] = useState(true);
  const [shareLink, setShareLink] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [copied, setCopied] = useState(false);
  const [existingShares, setExistingShares] = useState([]);

  useEffect(() => {
    if (open) {
      loadShares();
      setShareLink(null);
      setCopied(false);
    }
  }, [open]);

  const loadShares = async () => {
    try {
      const res = await axios.get(`${API}/trajectory/shares?token=${token}`);
      setExistingShares(res.data.filter(s => s.is_active));
    } catch {}
  };

  const generateLink = async () => {
    setGenerating(true);
    try {
      const res = await axios.post(`${API}/trajectory/share?token=${token}`, {
        audience,
        duration_days: parseInt(durationDays),
        include_synthesis: includeSynthesis,
        include_card: includeCard
      });
      const baseUrl = window.location.origin;
      setShareLink(`${baseUrl}/trajectoire/${res.data.share_id}`);
      loadShares();
      toast.success("Lien de partage créé !");
    } catch (e) {
      toast.error("Erreur lors de la création du lien");
    }
    setGenerating(false);
  };

  const copyLink = () => {
    if (shareLink) {
      navigator.clipboard.writeText(shareLink);
      setCopied(true);
      toast.success("Lien copié !");
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const revokeShare = async (shareId) => {
    try {
      await axios.delete(`${API}/trajectory/shares/${shareId}?token=${token}`);
      toast.success("Lien désactivé");
      loadShares();
    } catch { toast.error("Erreur"); }
  };

  const audienceOpts = [
    { value: "accompagnateur", label: "Accompagnateur / Conseiller", desc: "Vue complète du suivi", icon: Handshake },
    { value: "recruteur", label: "Recruteur / Employeur", desc: "Vue adaptée candidature", icon: Building2 },
    { value: "public", label: "Version synthétique", desc: "Vue minimale publique", icon: Eye },
  ];

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2"><Share2 className="w-5 h-5 text-[#1e3a5f]" />Partager ma trajectoire</DialogTitle>
          <DialogDescription>Créez un lien unique adapté à votre interlocuteur</DialogDescription>
        </DialogHeader>
        <div className="space-y-4 mt-2">
          {/* Audience selection */}
          <div>
            <label className="text-sm font-medium text-slate-700 mb-2 block">Destinataire</label>
            <div className="space-y-2">
              {audienceOpts.map(opt => {
                const OI = opt.icon;
                const active = audience === opt.value;
                return (
                  <div key={opt.value}
                    className={`flex items-center gap-3 p-3 rounded-lg border-2 cursor-pointer transition-all ${active ? "border-[#1e3a5f] bg-blue-50" : "border-slate-200 hover:border-slate-300"}`}
                    onClick={() => setAudience(opt.value)}
                    data-testid={`audience-${opt.value}`}
                  >
                    <div className={`w-9 h-9 rounded-full flex items-center justify-center ${active ? "bg-[#1e3a5f] text-white" : "bg-slate-100 text-slate-500"}`}>
                      <OI className="w-4 h-4" />
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-semibold text-slate-800">{opt.label}</p>
                      <p className="text-xs text-slate-500">{opt.desc}</p>
                    </div>
                    {active && <CheckCircle className="w-5 h-5 text-[#1e3a5f]" />}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Options */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-sm font-medium text-slate-700 mb-1.5 block">Durée de validité</label>
              <Select value={durationDays} onValueChange={setDurationDays}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="7">7 jours</SelectItem>
                  <SelectItem value="30">30 jours</SelectItem>
                  <SelectItem value="90">90 jours</SelectItem>
                  <SelectItem value="365">1 an</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-3 pt-6">
              <label className="flex items-center gap-2 cursor-pointer">
                <Switch checked={includeCard} onCheckedChange={setIncludeCard} />
                <span className="text-xs text-slate-600">Inclure carte D'CLIC</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <Switch checked={includeSynthesis} onCheckedChange={setIncludeSynthesis} />
                <span className="text-xs text-slate-600">Inclure compétences</span>
              </label>
            </div>
          </div>

          {/* Generate button */}
          <Button onClick={generateLink} disabled={generating} className="w-full bg-[#1e3a5f] hover:bg-[#152a45]" data-testid="generate-share-link-btn">
            {generating ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Link2 className="w-4 h-4 mr-2" />}
            Générer le lien de partage
          </Button>

          {/* Share Link Result */}
          {shareLink && (
            <div className="p-4 bg-emerald-50 rounded-xl border border-emerald-200 space-y-3 animate-in fade-in slide-in-from-top-2" data-testid="share-link-result">
              <div className="flex items-center gap-2">
                <Input value={shareLink} readOnly className="flex-1 text-xs bg-white" data-testid="share-link-input" />
                <Button size="icon" variant="outline" onClick={copyLink} data-testid="copy-share-link-btn">
                  {copied ? <Check className="w-4 h-4 text-emerald-600" /> : <Copy className="w-4 h-4" />}
                </Button>
              </div>
              <div className="flex justify-center">
                <div className="bg-white p-3 rounded-xl shadow-sm" data-testid="qr-code-container">
                  <QRCodeSVG value={shareLink} size={160} level="M" includeMargin={false}
                    fgColor="#1e3a5f" bgColor="#ffffff"
                  />
                  <p className="text-[10px] text-center text-slate-400 mt-2">Scannez pour accéder</p>
                </div>
              </div>
            </div>
          )}

          {/* Existing shares */}
          {existingShares.length > 0 && (
            <div className="pt-3 border-t border-slate-100">
              <p className="text-xs font-semibold text-slate-500 mb-2">Liens actifs ({existingShares.length})</p>
              <div className="space-y-2">
                {existingShares.slice(0, 5).map(share => (
                  <div key={share.share_id} className="flex items-center justify-between p-2 bg-slate-50 rounded-lg text-xs">
                    <div>
                      <span className="font-medium text-slate-700">{share.audience === "accompagnateur" ? "Accompagnateur" : share.audience === "recruteur" ? "Recruteur" : "Public"}</span>
                      <span className="text-slate-400 ml-2">{share.view_count} vue(s)</span>
                    </div>
                    <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => revokeShare(share.share_id)}>
                      <X className="w-3 h-3 text-red-400" />
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};

// ===== ACCESS REQUESTS NOTIFICATIONS =====
const AccessRequestsNotifications = ({ token }) => {
  const [requests, setRequests] = useState([]);
  const [responding, setResponding] = useState(null);

  useEffect(() => { loadRequests(); }, []);

  const loadRequests = async () => {
    try { const res = await axios.get(`${API}/notifications/access-requests?token=${token}`); setRequests(res.data); } catch {}
  };

  const respond = async (requestId, action) => {
    setResponding(requestId);
    try {
      await axios.post(`${API}/notifications/access-requests/${requestId}/respond?token=${token}`, { action }, { headers: { "Content-Type": "application/json" } });
      toast.success(action === "accept" ? "Accès autorisé" : "Demande refusée");
      loadRequests();
    } catch (err) { toast.error(err.response?.data?.detail || "Erreur"); }
    setResponding(null);
  };

  const pending = requests.filter(r => r.status === "en_attente");
  const past = requests.filter(r => r.status !== "en_attente");
  if (requests.length === 0) return null;

  // === Discreet mode: no pending requests → collapsible summary line ===
  if (pending.length === 0) {
    return (
      <details className="rounded-lg border border-slate-100 bg-slate-50/40 hover:bg-slate-50 transition-colors" data-testid="access-requests-discreet">
        <summary className="flex items-center justify-between gap-3 cursor-pointer px-3 py-1.5 text-xs text-slate-500 list-none">
          <span className="flex items-center gap-1.5">
            <Bell className="w-3 h-3 text-slate-400" />
            Historique des demandes d'accès
            <span className="text-slate-400">·</span>
            <span className="text-slate-400">{past.length}</span>
          </span>
          <span className="text-slate-300 text-[10px]">Détails</span>
        </summary>
        <div className="px-3 pb-2 pt-1 border-t border-slate-100 mt-1">
          {past.slice(0, 8).map(req => (
            <div key={req.id} className="flex items-center justify-between py-1 text-xs" data-testid={`access-history-${req.id}`}>
              <span className="text-slate-500">{req.partner_name}</span>
              <span className={`text-[10px] px-1.5 py-0.5 rounded ${req.status === "accepte" ? "bg-green-50 text-green-600" : "bg-red-50 text-red-500"}`}>
                {req.status === "accepte" ? "Accepté" : "Refusé"}
              </span>
            </div>
          ))}
        </div>
      </details>
    );
  }

  // === Full mode: pending requests need attention ===
  return (
    <Card className="border border-amber-200 bg-amber-50/30" data-testid="access-requests-notifications">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-base">
          <Bell className="w-4 h-4 text-amber-600" />Demandes d'accès à votre profil
          <Badge className="bg-amber-100 text-amber-700 text-xs ml-1">{pending.length} en attente</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {pending.map(req => (
          <div key={req.id} className="flex items-center justify-between p-3 rounded-lg border border-amber-200 bg-white" data-testid={`access-req-${req.id}`}>
            <div>
              <p className="text-sm font-semibold text-slate-800">{req.partner_name}</p>
              <p className="text-xs text-slate-500">Demande — {new Date(req.created_at).toLocaleDateString('fr-FR')}</p>
            </div>
            <div className="flex gap-2 shrink-0">
              <Button size="sm" className="bg-green-600 hover:bg-green-700 h-8 text-xs" onClick={() => respond(req.id, "accept")} disabled={responding === req.id} data-testid={`accept-req-${req.id}`}>
                {responding === req.id ? <Loader2 className="w-3 h-3 animate-spin" /> : <><CheckCircle2 className="w-3 h-3 mr-1" /> Accepter</>}
              </Button>
              <Button size="sm" variant="outline" className="text-red-500 hover:bg-red-50 h-8 text-xs border-red-200" onClick={() => respond(req.id, "reject")} disabled={responding === req.id} data-testid={`reject-req-${req.id}`}>
                <Shield className="w-3 h-3 mr-1" /> Refuser
              </Button>
            </div>
          </div>
        ))}
        {past.length > 0 && (
          <details className="pt-2 border-t border-slate-100">
            <summary className="text-xs font-medium text-slate-500 cursor-pointer">Historique ({past.length})</summary>
            <div className="mt-2">
              {past.slice(0, 5).map(req => (
                <div key={req.id} className="flex items-center justify-between py-1.5 text-xs" data-testid={`access-history-${req.id}`}>
                  <span className="text-slate-600">{req.partner_name}</span>
                  <Badge className={req.status === "accepte" ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"} variant="secondary">
                    {req.status === "accepte" ? "Accepté" : "Refusé"}
                  </Badge>
                </div>
              ))}
            </div>
          </details>
        )}
      </CardContent>
    </Card>
  );
};

// ===== MAIN COMPONENT =====
const ParticulierView = ({ token, section, onOpenDclic, viewMode, pseudo }) => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [passport, setPassport] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [learningModules, setLearningModules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(viewMode || "trajectoire");
  const [trajSubTab, setTrajSubTab] = useState("trajectoire");

  // Sync activeTab when viewMode changes (SPA navigation)
  useEffect(() => {
    if (viewMode) setActiveTab(viewMode);
  }, [viewMode]);
  const [steps, setSteps] = useState([]);
  const [synthesis, setSynthesis] = useState(null);
  const [loadingSynthesis, setLoadingSynthesis] = useState(false);
  const [visibilitySettings, setVisibilitySettings] = useState(null);
  const [stepDialogOpen, setStepDialogOpen] = useState(false);
  const [editingStep, setEditingStep] = useState(null);
  const [autoPopulating, setAutoPopulating] = useState(false);
  const [shareDialogOpen, setShareDialogOpen] = useState(false);
  const [newSkill, setNewSkill] = useState("");
  const [editingProfile, setEditingProfile] = useState(false);
  const [timelineViewMode, setTimelineViewMode] = useState("timeline");
  const [deletingCv, setDeletingCv] = useState(false);
  const [resettingProfile, setResettingProfile] = useState(false);
  const [refreshingTrajectory, setRefreshingTrajectory] = useState(false);
  const [showResetDialog, setShowResetDialog] = useState(false);
  const [resetSections, setResetSections] = useState("all");

  const handleDeleteCv = async () => {
    if (!window.confirm("Supprimer toutes les donnees CV ?\n\nCela supprimera :\n- Le texte CV stocke\n- Les resultats d'analyse\n- Les CV generes (classique, competences, etc.)\n- Les centres d'interet analyses\n- Les competences et experiences extraites du CV dans le passeport\n\nCette action est irreversible.")) return;
    setDeletingCv(true);
    try {
      await axios.delete(`${API}/cv/delete-all?token=${token}`);
      toast.success("Toutes les donnees CV ont ete supprimees");
      loadData(true);
      loadTrajectory();
    } catch (e) {
      toast.error(e.response?.data?.detail || "Erreur lors de la suppression");
    }
    setDeletingCv(false);
  };

  const handleResetProfile = async (sections = "all") => {
    const sectionLabels = {
      all: "TOUT le profil (competences, experiences, formations, resume, passerelles)",
      competences: "les competences",
      experiences: "les experiences (et la trajectoire associee)",
      formations: "les formations",
      profile: "le resume, projet pro, motivations, environnements",
      passerelles: "les passerelles metiers",
    };
    const label = sectionLabels[sections] || sections;
    if (!window.confirm(`Effacer ${label} ?\n\nCette action est irreversible.`)) return;
    setResettingProfile(true);
    try {
      await axios.delete(`${API}/passport/reset?token=${token}&sections=${sections}`);
      toast.success(`Profil reinitialise (${label})`);
      setShowResetDialog(false);
      loadData(true);
      loadTrajectory();
    } catch (e) {
      toast.error(e.response?.data?.detail || "Erreur lors de la reinitialisation");
    }
    setResettingProfile(false);
  };

  const handleRefreshTrajectory = async () => {
    if (!window.confirm("Actualiser la trajectoire ?\n\nCela va supprimer toutes les etapes actuelles et les recreer a partir de vos donnees du passeport.\n\nLes etapes ajoutees manuellement seront perdues.")) return;
    setRefreshingTrajectory(true);
    try {
      const res = await axios.post(`${API}/trajectory/refresh?token=${token}`);
      toast.success(res.data.message || "Trajectoire actualisee");
      loadTrajectory();
    } catch (e) {
      toast.error(e.response?.data?.detail || "Erreur lors de l'actualisation");
    }
    setRefreshingTrajectory(false);
  };

  const loadData = async (silent = false) => {
    if (!token) return;
    if (!silent) setLoading(true);
    try {
      const [profileRes, jobsRes, learningRes, passportRes] = await Promise.all([
        axios.get(`${API}/profile?token=${token}`),
        axios.get(`${API}/jobs/matching?token=${token}`),
        axios.get(`${API}/learning?token=${token}`),
        axios.get(`${API}/passport?token=${token}`).catch(() => ({ data: null })),
      ]);
      setProfile(profileRes.data);
      const jobsData = jobsRes.data;
      setJobs(Array.isArray(jobsData) ? jobsData : (jobsData.jobs || []));
      setLearningModules(learningRes.data);
      setPassport(passportRes.data);

      // Auto-enrich passport if fields are missing after CV analysis
      const pp = passportRes.data;
      if (pp && pp.competences?.length > 0) {
        const needsEnrich = !pp.career_project || !pp.motivations?.length || !pp.compatible_environments?.length || !pp.target_sectors?.length;
        if (needsEnrich) {
          try {
            const enrichRes = await axios.post(`${API}/passport/enrich?token=${token}`);
            if (enrichRes.data?.enriched_fields?.length > 0) {
              const refreshed = await axios.get(`${API}/passport?token=${token}`).catch(() => ({ data: pp }));
              setPassport(refreshed.data);
            }
          } catch (e) {
            console.warn("Auto-enrich skipped:", e.message);
          }
        }
      }
    } catch (error) {
      console.error("Error loading data:", error);
      if (!silent) toast.error("Erreur lors du chargement");
    }
    if (!silent) setLoading(false);
  };

  useEffect(() => { loadData(); }, [token]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadTrajectory = useCallback(async () => {
    try {
      const [stepsRes, visRes] = await Promise.all([
        axios.get(`${API}/trajectory/steps?token=${token}`),
        axios.get(`${API}/trajectory/visibility-settings?token=${token}`)
      ]);
      setSteps(stepsRes.data);
      setVisibilitySettings(visRes.data);
    } catch (e) {
      console.error("Trajectory load error:", e);
    }
  }, [token]);

  useEffect(() => { if (activeTab === "trajectoire" || viewMode === "accueil") loadTrajectory(); }, [activeTab, viewMode, loadTrajectory]);

  // Auto-load synthesis when steps are loaded
  useEffect(() => {
    if (steps.length > 0 && !synthesis && !loadingSynthesis) {
      loadSynthesis();
    }
  }, [steps]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadSynthesis = async () => {
    setLoadingSynthesis(true);
    try {
      const res = await axios.get(`${API}/trajectory/synthesis?token=${token}`);
      if (res.data.has_data) setSynthesis(res.data.synthesis);
    } catch (e) { console.error("Synthesis error:", e); }
    setLoadingSynthesis(false);
  };

  const autoPopulate = async () => {
    setAutoPopulating(true);
    try {
      const res = await axios.post(`${API}/trajectory/auto-populate?token=${token}`);
      toast.success(`${res.data.imported} étape(s) importée(s) depuis vos données`);
      loadTrajectory();
    } catch (e) { toast.error("Erreur lors de l'import"); }
    setAutoPopulating(false);
  };

  const deleteStep = async (stepId) => {
    try {
      await axios.delete(`${API}/trajectory/steps/${stepId}?token=${token}`);
      toast.success("Étape supprimée");
      loadTrajectory();
    } catch (e) { toast.error("Erreur"); }
  };

  const updateStepVisibility = async (stepId, newVisibility) => {
    try {
      await axios.put(`${API}/trajectory/steps/${stepId}?token=${token}`, { visibility: newVisibility });
      setSteps(prev => prev.map(s => s.id === stepId ? { ...s, visibility: newVisibility } : s));
      toast.success("Visibilité de l'étape mise à jour");
    } catch (e) { toast.error("Erreur"); }
  };

  const updateVisibility = async (newSettings) => {
    setVisibilitySettings(newSettings);
    try {
      await axios.put(`${API}/trajectory/visibility-settings?token=${token}`, newSettings);
      toast.success("Visibilité mise à jour");
    } catch (e) { toast.error("Erreur"); }
  };

  const addSkill = async () => {
    if (!newSkill.trim()) return;
    const updatedSkills = [...(profile?.skills || []), { name: newSkill, level: 50 }];
    try {
      const response = await axios.put(`${API}/profile?token=${token}`, { skills: updatedSkills });
      setProfile(response.data);
      setNewSkill("");
      setEditingProfile(false);
      toast.success("Compétence ajoutée !");
      loadData(true);
    } catch { toast.error("Erreur lors de l'ajout"); }
  };

  const updateLearningProgress = async (moduleId, newProgress) => {
    try {
      await axios.post(`${API}/learning/${moduleId}/progress?token=${token}&progress=${newProgress}`);
      setLearningModules(prev => prev.map(m => m.id === moduleId ? { ...m, progress: newProgress } : m));
      toast.success("Progression mise à jour !");
    } catch { toast.error("Erreur"); }
  };

  const displayProfile = profile || { name: "Utilisateur", profile_score: 0, skills: [], strengths: [], gaps: [], sectors: [] };

  const allSkills = useMemo(() => {
    const merged = [];
    const seen = new Set();
    for (const s of (displayProfile.skills || [])) {
      const key = (s.name || "").toLowerCase();
      if (key && !seen.has(key)) {
        seen.add(key);
        merged.push({ name: s.name, level: s.level ?? (s.declared_level ? s.declared_level * 20 : 50), source: s.source || "declaratif" });
      }
    }
    const validSources = new Set(["dclic_pro", "ia_detectee", "analyse_cv", "centres_interet"]);
    for (const c of (passport?.competences || [])) {
      const key = (c.name || "").toLowerCase();
      const src = c.source || "";
      if (key && !seen.has(key) && validSources.has(src)) {
        seen.add(key);
        const lvl = c.level === "expert" ? 90 : c.level === "avance" ? 70 : c.level === "intermediaire" ? 50 : 30;
        merged.push({ name: c.name, level: lvl, source: src, nature: c.nature });
      }
    }
    return merged;
  }, [displayProfile.skills, passport?.competences]);

  // Trajectory visibility stats
  const trajectoryStats = useMemo(() => {
    const total = steps.length;
    const recruiterVisible = steps.filter(s => s.visibility === "recruteur" || s.visibility === "public").length;
    const coachVisible = steps.filter(s => s.visibility === "accompagnateur" || s.visibility === "public").length;
    const privateOnly = steps.filter(s => s.visibility === "private").length;
    const coherenceScore = synthesis?.scores?.coherence || 0;
    return { total, recruiterVisible, coachVisible, privateOnly, coherenceScore };
  }, [steps, synthesis]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
      </div>
    );
  }

  if (section === "jobs") return <JobMatchingSection token={token} />;
  if (section === "learning") return <LearningSection modules={learningModules} updateProgress={updateLearningProgress} token={token} />;

  const metrics = [
    { title: "Identité Pro", value: `${displayProfile.profile_score ?? 0}%`, icon: Target, color: "blue", subtitle: "Complétude profil" },
    { title: "Job Matching", value: jobs.filter(j => (j.match_score || j.matching_score || 0) >= 60).length.toString(), icon: Briefcase, color: "emerald", subtitle: "Offres compatibles" },
    { title: "Compétences", value: allSkills.length.toString(), icon: Zap, color: "violet", subtitle: "Toutes sources" },
    { title: "Parcours", value: steps.length.toString(), icon: Route, color: "amber", subtitle: "Étapes tracées" }
  ];

  if (viewMode === "accueil") {
    return (
      <div className="animate-fade-in space-y-5" data-testid="particulier-dashboard">
        <AccessRequestsNotifications token={token} />
        <GpsDashboard
          token={token}
          pseudo={pseudo}
          profile={profile}
          passport={passport}
          steps={steps}
          jobs={jobs}
          allSkills={allSkills}
          onOpenDclic={onOpenDclic}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in" data-testid="particulier-dashboard">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>
            {viewMode === "accueil" ? "Mon Espace" : "Ma Trajectoire Professionnelle"}
          </h1>
          <p className="text-slate-500 mt-1 text-sm">{viewMode === "accueil" ? "Votre tableau de bord personnalisé" : "Visualisez votre parcours, valorisez vos acquis, contrôlez vos données"}</p>
        </div>
        <div className="flex items-center gap-2 self-start">
          <Badge className="bg-blue-100 text-[#1e3a5f] border-blue-200 px-3 py-1">
            <Shield className="w-3 h-3 mr-1" />Tiers de confiance numerique
          </Badge>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" className="text-red-600 border-red-200 hover:bg-red-50 rounded-xl" data-testid="reset-profile-menu-btn">
                <SlidersHorizontal className="w-3.5 h-3.5 mr-1.5" />Gestion
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-64">
              <DropdownMenuItem
                className="text-red-600 focus:text-red-700 focus:bg-red-50 cursor-pointer"
                onClick={() => handleResetProfile("all")}
                disabled={resettingProfile}
                data-testid="reset-all-btn"
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Effacer tout le profil
              </DropdownMenuItem>
              <DropdownMenuItem
                className="text-amber-600 focus:text-amber-700 focus:bg-amber-50 cursor-pointer"
                onClick={() => handleResetProfile("competences")}
                disabled={resettingProfile}
                data-testid="reset-competences-btn"
              >
                <Zap className="w-4 h-4 mr-2" />
                Effacer les competences
              </DropdownMenuItem>
              <DropdownMenuItem
                className="text-amber-600 focus:text-amber-700 focus:bg-amber-50 cursor-pointer"
                onClick={() => handleResetProfile("experiences")}
                disabled={resettingProfile}
                data-testid="reset-experiences-btn"
              >
                <Briefcase className="w-4 h-4 mr-2" />
                Effacer les experiences
              </DropdownMenuItem>
              <DropdownMenuItem
                className="text-amber-600 focus:text-amber-700 focus:bg-amber-50 cursor-pointer"
                onClick={() => handleResetProfile("formations")}
                disabled={resettingProfile}
                data-testid="reset-formations-btn"
              >
                <Award className="w-4 h-4 mr-2" />
                Effacer les formations
              </DropdownMenuItem>
              <DropdownMenuItem
                className="text-amber-600 focus:text-amber-700 focus:bg-amber-50 cursor-pointer"
                onClick={() => handleResetProfile("profile")}
                disabled={resettingProfile}
                data-testid="reset-summary-btn"
              >
                <Target className="w-4 h-4 mr-2" />
                Effacer resume et projet pro
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {/* Notifications */}
      <AccessRequestsNotifications token={token} />

      {/* Metrics */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3" data-testid="metrics-grid">
        {metrics.map((m, idx) => {
          const MIcon = m.icon;
          const colorClasses = { blue: "bg-blue-100 text-blue-600", emerald: "bg-emerald-100 text-emerald-600", amber: "bg-amber-100 text-amber-600", violet: "bg-violet-100 text-violet-600" };
          return (
            <Card key={idx} className="card-metric" data-testid={`metric-${idx}`}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-xs font-medium text-slate-500 mb-1">{m.title}</p>
                    <p className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>{m.value}</p>
                    <p className="text-[11px] text-slate-400 mt-0.5">{m.subtitle}</p>
                  </div>
                  <div className={`w-10 h-10 rounded-xl ${colorClasses[m.color]} flex items-center justify-center`}>
                    <MIcon className="w-5 h-5" />
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* TABS */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        {!viewMode && (
        <TabsList className="w-full grid grid-cols-4 h-11 bg-slate-100 rounded-xl p-1" data-testid="main-tabs">
          <TabsTrigger value="trajectoire" className="text-xs sm:text-sm font-medium data-[state=active]:bg-white data-[state=active]:shadow-sm rounded-lg" data-testid="tab-trajectoire">
            <Route className="w-4 h-4 mr-1.5 hidden sm:inline" />Trajectoire
          </TabsTrigger>
          <TabsTrigger value="competences" className="text-xs sm:text-sm font-medium data-[state=active]:bg-white data-[state=active]:shadow-sm rounded-lg" data-testid="tab-competences">
            <Zap className="w-4 h-4 mr-1.5 hidden sm:inline" />Compétences
          </TabsTrigger>
          <TabsTrigger value="documents" className="text-xs sm:text-sm font-medium data-[state=active]:bg-white data-[state=active]:shadow-sm rounded-lg" data-testid="tab-documents">
            <FolderLock className="w-4 h-4 mr-1.5 hidden sm:inline" />Documents
          </TabsTrigger>
          <TabsTrigger value="matching" className="text-xs sm:text-sm font-medium data-[state=active]:bg-white data-[state=active]:shadow-sm rounded-lg" data-testid="tab-matching">
            <Briefcase className="w-4 h-4 mr-1.5 hidden sm:inline" />Matching
          </TabsTrigger>
        </TabsList>
        )}

        {/* === TRAJECTOIRE TAB === */}
        <TabsContent value="trajectoire" className="space-y-4 mt-6">

          {/* Sub-navigation horizontale */}
          <div className="flex gap-2 overflow-x-auto pb-1" data-testid="traj-sub-nav">
            {[
              { key: "cv", label: "Mon CV", icon: Upload },
              { key: "trajectoire", label: "Ma trajectoire", icon: Route },
              { key: "centres", label: "Centres d'intérêt", icon: Heart },
              { key: "analyse", label: "Analyse IA", icon: Brain },
              { key: "audit", label: "Audit", icon: BarChart3 },
              { key: "generer", label: "Générer des CV", icon: Sparkles },
            ].map(tab => {
              const Icon = tab.icon;
              const isActive = trajSubTab === tab.key;
              return (
                <button key={tab.key} onClick={() => setTrajSubTab(tab.key)}
                  className={`flex items-center gap-1.5 px-4 py-2.5 rounded-xl text-sm font-medium whitespace-nowrap transition-all ${isActive ? "bg-[#1e3a5f] text-white shadow-md" : "bg-white text-slate-600 hover:bg-slate-100 border border-slate-200"}`}
                  data-testid={`traj-sub-${tab.key}`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              );
            })}
          </div>

          {/* SUB: Mon CV */}
          {trajSubTab === "cv" && (
            <div className="space-y-4">
              <Card className="card-base border-0 shadow-sm">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="flex items-center gap-2 text-lg"><Upload className="w-5 h-5 text-[#1e3a5f]" />{"Telecharger votre CV"}</CardTitle>
                      <CardDescription>{"Chargez votre CV pour alimenter automatiquement votre trajectoire et vos competences"}</CardDescription>
                    </div>
                    {(passport?.competences?.some(c => c.source === "ia_detectee" || c.source === "cv_analysis") || passport?.experiences?.some(e => e.source === "ia_detectee")) && (
                      <div className="flex items-center gap-2 shrink-0">
                        <Button
                          variant="outline"
                          size="sm"
                          className="text-[#1e3a5f] border-[#1e3a5f]/20 hover:bg-[#1e3a5f]/5 rounded-xl"
                          onClick={async () => {
                            try {
                              const res = await axios.get(`${API}/coffre/documents?token=${token}`);
                              const docs = res.data.documents || [];
                              const cvDoc = docs.find(d => d.title?.toLowerCase().includes("cv original"));
                              if (cvDoc) {
                                const link = document.createElement("a");
                                link.href = `${API}/coffre/download/${cvDoc.id}?token=${token}`;
                                link.download = cvDoc.filename || "mon_cv.pdf";
                                link.click();
                              } else {
                                toast.error("CV original non trouvé dans le coffre-fort");
                              }
                            } catch { toast.error("Erreur de téléchargement"); }
                          }}
                          data-testid="download-cv-btn"
                        >
                          <Download className="w-3.5 h-3.5 mr-1.5" />
                          Télécharger mon CV
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          className="text-red-600 border-red-200 hover:bg-red-50 hover:border-red-300 rounded-xl"
                          onClick={handleDeleteCv}
                          disabled={deletingCv}
                          data-testid="delete-cv-btn"
                        >
                          {deletingCv ? <Loader2 className="w-3.5 h-3.5 animate-spin mr-1.5" /> : <Trash2 className="w-3.5 h-3.5 mr-1.5" />}
                          Supprimer le CV
                        </Button>
                      </div>
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  <CvAnalysisSection token={token} onComplete={() => { loadData(true); loadTrajectory(); }} compact />
                </CardContent>
              </Card>

              {/* Expériences extraites du passeport */}
              {passport?.experiences?.length > 0 && (
                <Card className="card-base border-0 shadow-sm" data-testid="cv-experiences-section">
                  <CardHeader className="pb-2">
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <Briefcase className="w-5 h-5 text-[#1e3a5f]" />
                      Expériences professionnelles
                      <Badge variant="secondary" className="ml-auto text-xs">{passport.experiences.length}</Badge>
                    </CardTitle>
                  </CardHeader>

                  {/* Bandeau contributeur OPC */}
                  <div className="mx-4 mb-3 rounded-xl bg-gradient-to-r from-indigo-50 via-purple-50 to-violet-50 border border-indigo-200/60 p-4" data-testid="opc-contributor-banner">
                    <div className="flex items-start gap-3">
                      <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shrink-0 shadow-md">
                        <Users className="w-5 h-5 text-white" />
                      </div>
                      <div className="flex-1">
                        <h4 className="text-sm font-bold text-indigo-900">Prouvez vos compétences, devenez Contributeur Sociétal</h4>
                        <p className="text-xs text-indigo-700/80 mt-1 leading-relaxed">
                          Chaque compétence illustrée par un <strong>exemple concret</strong> (situation, action, résultat) renforce la crédibilité de votre profil
                          et enrichit l'<strong>Observatoire Prédictif des Compétences</strong>.
                          Vos contributions anonymisées aident à cartographier les métiers de demain.
                        </p>
                        <div className="flex items-center gap-4 mt-2.5">
                          <div className="flex items-center gap-1.5 text-[10px]">
                            <div className="w-2 h-2 rounded-full bg-emerald-500" />
                            <span className="text-indigo-600 font-semibold">
                              {passport.experiences.filter(e => e.proof || e.exemple_concret).length}/{passport.experiences.length} expériences documentées
                            </span>
                          </div>
                          <div className="flex items-center gap-1 text-[10px] text-purple-600">
                            <Award className="w-3 h-3" />
                            <span>Niveau : {
                              passport.experiences.filter(e => e.proof || e.exemple_concret).length >= passport.experiences.length * 0.8
                                ? "Contributeur Expert"
                                : passport.experiences.filter(e => e.proof || e.exemple_concret).length >= passport.experiences.length * 0.5
                                  ? "Contributeur Confirmé"
                                  : passport.experiences.filter(e => e.proof || e.exemple_concret).length > 0
                                    ? "Contributeur Actif"
                                    : "En attente de contribution"
                            }</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <CardContent className="space-y-3">
                    {passport.experiences.map((exp, i) => {
                      const hasProof = !!(exp.proof || exp.exemple_concret);
                      return (
                        <div key={exp.id || i} className={`flex gap-3 p-3 rounded-xl border ${hasProof ? "bg-emerald-50/30 border-emerald-200/60" : "bg-slate-50 border-slate-100"}`} data-testid={`cv-experience-${i}`}>
                          <div className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 mt-0.5 ${hasProof ? "bg-emerald-100" : "bg-[#1e3a5f]/10"}`}>
                            {hasProof ? <CheckCircle className="w-4 h-4 text-emerald-600" /> : <Briefcase className="w-4 h-4 text-[#1e3a5f]" />}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                              <h4 className="text-sm font-semibold text-slate-900">{exp.title}</h4>
                              {hasProof && <Badge className="bg-emerald-100 text-emerald-700 text-[9px]">Documentée</Badge>}
                            </div>
                            <p className="text-xs text-slate-600 mt-0.5">{exp.organization}</p>
                            {(exp.start_date || exp.end_date) && (
                              <p className="text-xs text-slate-400 mt-0.5">
                                {exp.start_date || "?"} — {exp.is_current ? "Aujourd'hui" : (exp.end_date || "?")}
                              </p>
                            )}
                            {exp.description && <p className="text-xs text-slate-500 mt-1.5 leading-relaxed">{exp.description}</p>}
                            {exp.skills_used?.length > 0 && (
                              <div className="flex flex-wrap gap-1 mt-2">
                                {exp.skills_used.map((s, j) => (
                                  <Badge key={j} variant="outline" className="text-[10px] rounded-full">{s}</Badge>
                                ))}
                              </div>
                            )}

                            {/* Exemple concret / Preuve */}
                            {hasProof ? (
                              <div className="mt-2.5 bg-white rounded-lg border border-emerald-200/60 p-2.5">
                                <div className="flex items-center gap-1.5 mb-1">
                                  <FileText className="w-3 h-3 text-emerald-600" />
                                  <span className="text-[10px] font-semibold text-emerald-700">Exemple concret</span>
                                </div>
                                <p className="text-xs text-slate-600 leading-relaxed">{exp.proof || exp.exemple_concret}</p>
                              </div>
                            ) : (
                              <div className="mt-2.5 bg-amber-50/60 rounded-lg border border-amber-200/40 border-dashed p-2.5 cursor-pointer hover:bg-amber-50 transition-colors"
                                onClick={() => {
                                  const proof = window.prompt(
                                    `Illustrez cette expérience par un exemple concret :\n\n"${exp.title}" chez ${exp.organization}\n\nDécrivez une situation précise, l'action que vous avez menée, et le résultat obtenu (méthode SAR).`
                                  );
                                  if (proof && proof.trim()) {
                                    axios.post(`${API}/passport/experience-proof?token=${token}`, {
                                      experience_id: exp.id, proof: proof.trim()
                                    }).then(() => {
                                      toast.success("Exemple ajouté — merci pour votre contribution à l'OPC !");
                                      loadData(true);
                                    }).catch(() => toast.error("Erreur lors de l'ajout"));
                                  }
                                }}
                                data-testid={`add-proof-${i}`}
                              >
                                <div className="flex items-center gap-2">
                                  <div className="w-5 h-5 rounded-full bg-amber-200/60 flex items-center justify-center shrink-0">
                                    <Plus className="w-3 h-3 text-amber-700" />
                                  </div>
                                  <div>
                                    <span className="text-[10px] font-semibold text-amber-800">Ajouter un exemple concret</span>
                                    <p className="text-[9px] text-amber-600 mt-0.5">Situation, Action, Résultat — votre contribution enrichit l'Observatoire</p>
                                  </div>
                                </div>
                              </div>
                            )}

                            {/* Document officiel / Certification */}
                            {exp.proof_document ? (
                              <div className="mt-2 bg-blue-50/60 rounded-lg border border-blue-200/60 p-2.5" data-testid={`proof-doc-display-${i}`}>
                                <div className="flex items-center justify-between">
                                  <div className="flex items-center gap-2">
                                    <div className="w-6 h-6 rounded-md bg-blue-100 flex items-center justify-center">
                                      <ShieldCheck className="w-3.5 h-3.5 text-blue-700" />
                                    </div>
                                    <div>
                                      <span className="text-[10px] font-semibold text-blue-800">Document officiel joint</span>
                                      <p className="text-[9px] text-blue-600 truncate max-w-[180px]">{exp.proof_document.original_filename}</p>
                                    </div>
                                    <Badge className="bg-blue-100 text-blue-700 text-[8px] border border-blue-200">Certifié</Badge>
                                  </div>
                                  <div className="flex items-center gap-1">
                                    <Button variant="ghost" size="sm" className="h-6 px-2 text-[10px] text-blue-700 hover:bg-blue-100"
                                      onClick={() => window.open(`${API}/passport/experiences/proof-file/${exp.proof_document.file_id}?token=${token}`, "_blank")}
                                      data-testid={`view-proof-doc-${i}`}
                                    >
                                      <Eye className="w-3 h-3 mr-1" />Voir
                                    </Button>
                                    <Button variant="ghost" size="sm" className="h-6 w-6 p-0 text-slate-400 hover:text-red-500"
                                      onClick={() => {
                                        if (window.confirm("Supprimer ce document justificatif ?")) {
                                          axios.delete(`${API}/passport/experiences/proof-file/${exp.proof_document.file_id}?token=${token}`)
                                            .then(() => { toast.success("Document supprimé"); loadData(true); })
                                            .catch(() => toast.error("Erreur lors de la suppression"));
                                        }
                                      }}
                                      data-testid={`delete-proof-doc-${i}`}
                                    >
                                      <Trash2 className="w-3 h-3" />
                                    </Button>
                                  </div>
                                </div>
                              </div>
                            ) : (
                              <div className="mt-2">
                                <label className="flex items-center gap-2 p-2 rounded-lg border border-dashed border-blue-200/60 bg-blue-50/30 cursor-pointer hover:bg-blue-50 transition-colors"
                                  data-testid={`upload-proof-doc-${i}`}
                                >
                                  <input type="file" accept=".pdf,.jpg,.jpeg,.png" className="hidden"
                                    onChange={async (e) => {
                                      const file = e.target.files?.[0];
                                      if (!file) return;
                                      if (file.size > 10 * 1024 * 1024) { toast.error("Fichier trop volumineux (max 10 Mo)"); return; }
                                      const allowed = ["application/pdf", "image/jpeg", "image/png", "image/jpg"];
                                      if (!allowed.includes(file.type)) { toast.error("Format non accepté. Utilisez PDF, JPG ou PNG"); return; }
                                      try {
                                        toast.info("Upload en cours...");
                                        const reader = new FileReader();
                                        reader.onload = async () => {
                                          const b64 = reader.result.split(",")[1];
                                          await axios.post(`${API}/passport/experiences/upload-proof?token=${token}`, {
                                            experience_id: exp.id, file_data: b64, file_name: file.name, mime_type: file.type
                                          });
                                          toast.success(`Document "${file.name}" rattaché avec succès`);
                                          loadData(true);
                                        };
                                        reader.readAsDataURL(file);
                                      } catch { toast.error("Erreur lors de l'upload"); }
                                    }}
                                  />
                                  <div className="w-5 h-5 rounded-full bg-blue-100 flex items-center justify-center shrink-0">
                                    <Upload className="w-3 h-3 text-blue-600" />
                                  </div>
                                  <div>
                                    <span className="text-[10px] font-semibold text-blue-700">Joindre un document officiel</span>
                                    <p className="text-[9px] text-blue-500">Contrat, attestation, certificat (PDF, JPG, PNG — max 10 Mo)</p>
                                  </div>
                                </label>
                              </div>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </CardContent>
                </Card>
              )}

              {/* Formations extraites du passeport */}
              {passport?.formations?.length > 0 && (
                <Card className="card-base border-0 shadow-sm" data-testid="cv-formations-section">
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <Award className="w-5 h-5 text-emerald-600" />
                      Formations & Certifications
                      <Badge variant="secondary" className="ml-auto text-xs">{passport.formations.length}</Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {passport.formations.map((f, i) => (
                      <div key={f.id || i} className="flex gap-3 p-3 rounded-xl bg-emerald-50/50 border border-emerald-100" data-testid={`cv-formation-${i}`}>
                        <div className="w-10 h-10 rounded-lg bg-emerald-100 flex items-center justify-center shrink-0 mt-0.5">
                          <Award className="w-4 h-4 text-emerald-700" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <h4 className="text-sm font-semibold text-slate-900">{f.diplome}</h4>
                          {f.etablissement && <p className="text-xs text-slate-600 mt-0.5">{f.etablissement}</p>}
                          <div className="flex items-center gap-2 mt-0.5">
                            {f.annee && <span className="text-xs text-slate-400">{f.annee}</span>}
                            {f.type && (
                              <Badge variant="outline" className="text-[10px] rounded-full capitalize">
                                {f.type === "diplome" ? "Diplôme" : f.type === "certification" ? "Certification" : f.type === "stage_formation" ? "Stage/Formation" : f.type}
                              </Badge>
                            )}
                          </div>
                          {f.domaine && <p className="text-xs text-slate-500 mt-1">{f.domaine}</p>}
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              )}
            </div>
          )}

          {/* SUB: Ma trajectoire */}
          {trajSubTab === "trajectoire" && (
            <div className="space-y-6">
              {steps.length > 0 && (
                <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
                  className="rounded-[24px] bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-5 text-white shadow-xl md:p-7" data-testid="trajectory-hero">
                  <div className="grid gap-5 lg:grid-cols-[1.2fr_0.8fr] lg:items-end">
                    <div>
                      <Badge className="rounded-full bg-white/10 text-white hover:bg-white/10 text-xs">{"Profil personnalité et compétences"}</Badge>
                      <h2 className="mt-3 text-2xl font-semibold tracking-tight md:text-3xl" style={{ fontFamily: 'Outfit, sans-serif' }}>{"Ma trajectoire professionnelle"}</h2>
                      <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-300">{"Visualisez votre parcours et choisissez qui peut consulter chaque étape."}</p>
                      <Button variant="outline" className="mt-4 rounded-xl border-white/20 bg-white/5 text-white hover:bg-white/10 text-sm" onClick={() => setShareDialogOpen(true)}>
                        <FileText className="mr-2 h-4 w-4" />{"Partager une version adaptée"}
                      </Button>
                    </div>
                    <Card className="rounded-2xl border-0 bg-white/10 text-white shadow-none backdrop-blur">
                      <CardContent className="grid gap-3 p-4 md:grid-cols-2">
                        <div><div className="text-xs text-slate-300">{"Cohérence"}</div><div className="mt-1 text-3xl font-semibold">{trajectoryStats.coherenceScore || "\u2014"}<span className="text-lg text-slate-400">/100</span></div></div>
                        <div><div className="text-xs text-slate-300">{"Étapes"}</div><div className="mt-1 text-3xl font-semibold">{trajectoryStats.total}</div></div>
                        <div className="md:col-span-2">
                          {trajectoryStats.coherenceScore > 0 && <Progress value={trajectoryStats.coherenceScore} className="h-2 bg-white/10" />}
                          <p className="mt-2 text-xs text-slate-300">{synthesis?.message_valorisant || "Allez dans Analyse IA pour générer une synthèse valorisante."}</p>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </motion.div>
              )}
              <Card className="rounded-2xl border-0 shadow-sm">
                <CardHeader>
                  <div className="flex items-center justify-between gap-3 flex-wrap">
                    <CardTitle className="text-lg text-slate-900">{"Ma frise de parcours"}</CardTitle>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm" className="rounded-xl text-amber-700 border-amber-200 hover:bg-amber-50" onClick={handleRefreshTrajectory} disabled={refreshingTrajectory} data-testid="refresh-trajectory-btn">
                        {refreshingTrajectory ? <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" /> : <RefreshCw className="w-3.5 h-3.5 mr-1.5" />}Actualiser
                      </Button>
                      <Button variant="outline" size="sm" className="rounded-xl" onClick={autoPopulate} disabled={autoPopulating}>
                        {autoPopulating ? <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" /> : <RefreshCw className="w-3.5 h-3.5 mr-1.5" />}Importer
                      </Button>
                      <Button size="sm" className="rounded-xl bg-[#1e3a5f] hover:bg-[#152a45]" onClick={() => { setEditingStep(null); setStepDialogOpen(true); }}>
                        <Plus className="w-3.5 h-3.5 mr-1.5" />{"Ajouter"}
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  {steps.length > 0 ? (
                    <>
                      <div className="flex items-center justify-between bg-slate-50 rounded-xl px-4 py-3 mb-5">
                        <div className="flex items-center gap-2"><Eye className="w-4 h-4 text-[#1e3a5f]" /><span className="text-sm font-medium text-slate-800">{"Visibilité totale"}</span></div>
                        <Switch checked={steps.every(s => s.visibility === "public")}
                          onCheckedChange={async (checked) => {
                            const nv = checked ? "public" : "private";
                            try { await Promise.all(steps.map(s => axios.put(`${API}/trajectory/steps/${s.id}?token=${token}`, { visibility: nv }))); setSteps(p => p.map(s => ({ ...s, visibility: nv }))); toast.success(checked ? "Toutes visibles" : "Toutes privées"); } catch { toast.error("Erreur"); }
                          }} />
                      </div>
                      <div className="relative space-y-5 before:absolute before:left-[7px] before:top-2 before:h-[calc(100%-12px)] before:w-px before:bg-slate-200">
                        {[...steps].sort((a, b) => (b.start_date || "0000").localeCompare(a.start_date || "0000")).map(step => (
                          <TimelineStepCard key={step.id} step={step} onEdit={s => { setEditingStep(s); setStepDialogOpen(true); }} onDelete={deleteStep} onVisibilityChange={updateStepVisibility} />
                        ))}
                      </div>
                    </>
                  ) : (
                    <div className="text-center py-8 space-y-6">
                      <div>
                        <Route className="w-10 h-10 text-slate-300 mx-auto mb-3" />
                        <p className="text-sm text-slate-500 mb-4">{"Votre frise est vide."}</p>
                        <div className="flex gap-2 justify-center">
                          <Button variant="outline" size="sm" className="rounded-xl" onClick={autoPopulate} disabled={autoPopulating}><RefreshCw className="w-3.5 h-3.5 mr-1.5" />Importer</Button>
                          <Button size="sm" className="rounded-xl bg-[#1e3a5f] hover:bg-[#152a45]" onClick={() => { setEditingStep(null); setStepDialogOpen(true); }}><Plus className="w-3.5 h-3.5 mr-1.5" />Ajouter</Button>
                        </div>
                      </div>

                      {/* Proposition de charger le CV */}
                      <div className="bg-gradient-to-r from-[#f0f4ff] to-[#e8f5e9] border border-[#c7d2fe] rounded-xl p-5" data-testid="cv-upload-prompt">
                        <div className="flex items-start gap-4">
                          <div className="bg-[#1e3a5f] rounded-xl p-3 shrink-0">
                            <Upload className="w-6 h-6 text-white" />
                          </div>
                          <div className="flex-1 text-left">
                            <h4 className="text-base font-semibold text-slate-800 mb-1">Chargez votre CV pour alimenter votre trajectoire</h4>
                            <p className="text-sm text-slate-600 mb-3">L'IA analysera votre CV et remplira automatiquement votre frise, vos compétences et votre profil professionnel.</p>
                            <Button size="sm" className="rounded-xl bg-[#1e3a5f] hover:bg-[#152a45]" onClick={() => setTrajSubTab("cv")} data-testid="go-upload-cv-btn">
                              <Upload className="w-3.5 h-3.5 mr-1.5" />Charger mon CV
                            </Button>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          )}

          {/* SUB: Centres d'intérêt */}
          {trajSubTab === "centres" && <CentresInteretSection token={token} />}

          {/* SUB: Analyse IA */}
          {trajSubTab === "analyse" && (
            <div className="space-y-4">
              {/* D'CLIC boost banner for Analyse IA */}
              {profile?.dclic_imported && (
                <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-100 rounded-lg px-3 py-2 text-xs text-emerald-700" data-testid="analyse-ia-dclic-boost">
                  <Sparkles className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
                  <span>D'CLIC PRO enrichit l'analyse IA : votre profil de personnalité {[profile.dclic_mbti && `MBTI: ${profile.dclic_mbti}`, profile.dclic_disc_label && `DISC: ${profile.dclic_disc_label}`, profile.dclic_riasec_major && `RIASEC: ${profile.dclic_riasec_major}`].filter(Boolean).join(", ") || ""} est intégré dans la synthèse pour une lecture de parcours plus complète et personnalisée.</span>
                </div>
              )}
              {!synthesis && !loadingSynthesis ? (
                <Card className="card-base border-0 shadow-sm">
                  <CardContent className="flex flex-col items-center text-center py-10 gap-4">
                    <Brain className="w-12 h-12 text-violet-300" />
                    <h3 className="text-lg font-semibold text-slate-800">{"Analyse IA de votre parcours"}</h3>
                    <p className="text-sm text-slate-500">{"Synthèse valorisante basée sur votre trajectoire et D'CLIC PRO"}</p>
                    <Button className="bg-violet-600 hover:bg-violet-700 rounded-xl" onClick={loadSynthesis}>
                      <Brain className="w-4 h-4 mr-2" />{"Générer l'analyse"}
                    </Button>
                  </CardContent>
                </Card>
              ) : (
                <SynthesisSection
                  synthesis={synthesis}
                  loading={loadingSynthesis}
                  token={token}
                  onRefresh={async () => {
                    try {
                      toast.info("Actualisation de l'analyse en cours...");
                      await axios.delete(`${API}/trajectory/synthesis/cache?token=${token}`);
                      const res = await axios.get(`${API}/trajectory/synthesis?token=${token}`);
                      const newSynth = res.data?.synthesis;
                      if (newSynth) {
                        setSynthesis(newSynth);
                        toast.success("Analyse actualisée");
                      }
                    } catch { toast.error("Erreur d'actualisation"); }
                  }}
                />
              )}
            </div>
          )}

          {/* SUB: Audit */}
          {trajSubTab === "audit" && (
            <div className="space-y-4">
              {profile?.dclic_imported && (
                <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-100 rounded-lg px-3 py-2 text-xs text-emerald-700" data-testid="audit-dclic-boost">
                  <Sparkles className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
                  <span>D'CLIC PRO optimise l'audit : vos compétences comportementales ({(profile.dclic_competences || []).slice(0, 3).join(", ")}{(profile.dclic_competences || []).length > 3 ? "..." : ""}) et votre profil {profile.dclic_mbti || ""} renforcent les critères de savoir-être et d'adaptabilité évalués.</span>
                </div>
              )}
              <Card className="card-base border-0 shadow-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-lg"><BarChart3 className="w-5 h-5 text-amber-600" />{"Audit de votre CV"}</CardTitle>
                  <CardDescription>{"Évaluation de 10 critères professionnels avec optimisations."}</CardDescription>
                </CardHeader>
                <CardContent>
                  <CvAnalysisSection token={token} onComplete={() => { loadData(true); loadTrajectory(); }} mode="audit" />
                </CardContent>
              </Card>
            </div>
          )}

          {/* SUB: Générer des CV */}
          {trajSubTab === "generer" && (
            <div className="space-y-4">
              {/* D'CLIC boost banner for CV generation */}
              {profile?.dclic_imported && (
                <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-100 rounded-lg px-3 py-2 text-xs text-emerald-700" data-testid="generer-cv-dclic-boost">
                  <Sparkles className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
                  <span>D'CLIC PRO booste la génération de CV : votre profil de personnalité {profile.dclic_mbti ? `(${profile.dclic_mbti})` : ""} et vos compétences comportementales sont intégrés pour des CV plus percutants et différenciants.</span>
                </div>
              )}
              {/* Checklist items existants / manquants */}
              {(() => {
                const hasCv = passport?.competences?.some(c => c.source === "cv_analysis" || c.source === "coffre_fort");
                const hasTrajectoire = steps?.length > 0;
                const hasCentresInteret = passport?.competences?.some(c => c.source === "centres_interet");
                const hasDclic = !!profile?.dclic_imported;
                const hasCompetences = (passport?.competences?.length || 0) > 0;
                const existing = [];
                const missing = [];
                if (hasCv) existing.push({ label: "CV analysé", detail: `${passport?.competences?.filter(c => c.source === "cv_analysis" || c.source === "coffre_fort")?.length || 0} compétences extraites` });
                if (hasTrajectoire) existing.push({ label: "Trajectoire", detail: `${steps.length} étape(s) de parcours` });
                if (hasCentresInteret) existing.push({ label: "Centres d'intérêt", detail: "Qualités identifiées" });
                if (hasDclic) existing.push({ label: "D'CLIC PRO", detail: [profile.dclic_results?.mbti, profile.dclic_results?.disc, profile.dclic_results?.riasec].filter(Boolean).join(", ") || "Profil enrichi" });
                if (hasCompetences) existing.push({ label: "Compétences", detail: `${passport.competences.length} au total (toutes sources)` });
                if (!hasDclic) missing.push({ label: "D'CLIC PRO", detail: "Test non effectué" });
                if (!hasTrajectoire) missing.push({ label: "Trajectoire", detail: "Aucune étape tracée" });

                const aiItems = [
                  { label: "Accroche professionnelle", detail: "Résumé percutant adapté au poste" },
                  { label: "Mise en page optimisée", detail: "Structure claire et professionnelle" },
                  { label: "Mots-clés ATS", detail: "Adaptation pour passer les filtres automatisés" },
                  { label: "Valorisation des compétences", detail: "Reformulation et hiérarchisation" },
                ];

                return (
                  <Card className="border-0 shadow-sm" data-testid="generer-checklist">
                    <CardContent className="p-4 space-y-4">
                      <div>
                        <h4 className="text-sm font-bold text-slate-800 mb-2 flex items-center gap-2">
                          <CheckCircle2 className="w-4 h-4 text-emerald-600" /> Données existantes pour la génération
                        </h4>
                        <div className="space-y-1.5">
                          {existing.map((item, i) => (
                            <div key={i} className="flex items-center gap-2 text-sm">
                              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 flex-shrink-0" />
                              <span className="font-medium text-slate-700">{item.label}</span>
                              <span className="text-slate-400">—</span>
                              <span className="text-slate-500 text-xs">{item.detail}</span>
                            </div>
                          ))}
                          {missing.map((item, i) => (
                            <div key={`m-${i}`} className="flex items-center gap-2 text-sm">
                              <AlertCircle className="w-3.5 h-3.5 text-amber-500 flex-shrink-0" />
                              <span className="font-medium text-slate-400">{item.label}</span>
                              <span className="text-slate-300">—</span>
                              <span className="text-amber-600 text-xs">{item.detail}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                      <div className="border-t border-slate-100 pt-3">
                        <h4 className="text-sm font-bold text-slate-800 mb-2 flex items-center gap-2">
                          <Sparkles className="w-4 h-4 text-blue-600" /> L'IA va compléter
                        </h4>
                        <div className="space-y-1.5">
                          {aiItems.map((item, i) => (
                            <div key={i} className="flex items-center gap-2 text-sm">
                              <Sparkles className="w-3.5 h-3.5 text-blue-400 flex-shrink-0" />
                              <span className="font-medium text-slate-700">{item.label}</span>
                              <span className="text-slate-400">—</span>
                              <span className="text-slate-500 text-xs">{item.detail}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })()}

              <Card className="card-base border-0 shadow-lg overflow-hidden">
                <CardHeader className="bg-gradient-to-r from-[#1e3a5f] to-[#2a5a8f] text-white">
                  <CardTitle className="flex items-center gap-2 text-lg"><Sparkles className="w-5 h-5" />{"Générer mes CV par IA"}</CardTitle>
                  <CardDescription className="text-white/70 text-sm">{"Les données ci-dessus alimentent la génération de vos CV"}</CardDescription>
                </CardHeader>
                <CardContent className="p-6">
                  <CvAnalysisSection token={token} onComplete={() => { loadData(true); loadTrajectory(); }} mode="generate" />
                </CardContent>
              </Card>
            </div>
          )}

        </TabsContent>

        {/* === COMPETENCES TAB === */}
        <TabsContent value="competences" className="space-y-6 mt-6">
          {/* D'CLIC Boost Section or "Booster mon profil" visual */}
          {profile?.dclic_imported ? (
            <DclicBoostSection profile={profile} token={token} />
          ) : (
            <Card className="border-0 shadow-lg overflow-hidden" data-testid="dclic-boost-invite">
              <div className="bg-gradient-to-br from-indigo-600 via-violet-600 to-purple-700 p-6 relative">
                <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0iTTM2IDM0djItSDI0di0yaDEyek0zNiAyNHYySDI0di0yaDEyeiIvPjwvZz48L2c+PC9zdmc+')] opacity-30" />
                <div className="relative flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                  <div className="flex items-start gap-4">
                    <div className="w-14 h-14 rounded-2xl bg-white/20 backdrop-blur-sm flex items-center justify-center shrink-0">
                      <Zap className="w-7 h-7 text-yellow-300" />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-white" style={{ fontFamily: 'Outfit, sans-serif' }}>Boostez votre profil avec D'CLIC PRO</h3>
                      <p className="text-indigo-100 text-sm mt-1 max-w-lg">
                        Découvrez votre personnalité professionnelle (version inspirée du MBTI, DISC, RIASEC) et valorisez vos compétences avec un profil crédibilisé par des tests reconnus.
                      </p>
                      <div className="flex flex-wrap gap-2 mt-3">
                        <Badge className="bg-white/15 text-white border-0 text-xs backdrop-blur-sm"><User className="w-3 h-3 mr-1" />Personnalité</Badge>
                        <Badge className="bg-white/15 text-white border-0 text-xs backdrop-blur-sm"><Target className="w-3 h-3 mr-1" />Orientation</Badge>
                        <Badge className="bg-white/15 text-white border-0 text-xs backdrop-blur-sm"><Award className="w-3 h-3 mr-1" />Compétences validées</Badge>
                        <Badge className="bg-white/15 text-white border-0 text-xs backdrop-blur-sm"><Sparkles className="w-3 h-3 mr-1" />Carte Pro</Badge>
                      </div>
                    </div>
                  </div>
                  <Button className="bg-white text-indigo-700 hover:bg-indigo-50 shrink-0 text-sm font-bold shadow-lg px-6 py-3 h-auto" data-testid="dclic-test-btn"
                    onClick={() => window.open('/test-dclic', '_blank', 'noopener,noreferrer')}>
                    <Play className="w-5 h-5 mr-2" />Passer le test
                  </Button>
                </div>
              </div>
            </Card>
          )}

          {/* CV Section */}
          <Card className="card-base" data-testid="cv-section">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg"><FileText className="w-5 h-5 text-[#1e3a5f]" />Mes CV</CardTitle>
              <CardDescription className="text-sm">Ré'Actif Pro IA audite, optimise et adapte votre CV pour passer les filtres ATS</CardDescription>
            </CardHeader>
            <CardContent>
              <CvAnalysisSection token={token} onComplete={() => loadData(true)} />
            </CardContent>
          </Card>

          {/* Skills Display */}
          <Card className="card-base" data-testid="skills-section">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2 text-lg"><Zap className="w-5 h-5 text-violet-600" />Compétences identifiées</CardTitle>
                <Button variant="outline" size="sm" onClick={() => setEditingProfile(true)}>
                  <Plus className="w-3.5 h-3.5 mr-1" />Ajouter
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {editingProfile && (
                <div className="flex gap-2 mb-4">
                  <Input value={newSkill} onChange={e => setNewSkill(e.target.value)} placeholder="Nouvelle compétence..." className="flex-1" onKeyDown={e => e.key === "Enter" && addSkill()} data-testid="new-skill-input" />
                  <Button size="sm" onClick={addSkill} className="bg-[#1e3a5f]">Ajouter</Button>
                  <Button size="sm" variant="ghost" onClick={() => setEditingProfile(false)}>Annuler</Button>
                </div>
              )}
              {allSkills.length > 0 && (
                <div className="flex flex-wrap gap-2 text-xs border border-slate-200 rounded-lg p-2.5 bg-slate-50 mb-4" data-testid="source-legend">
                  <span className="text-slate-500 font-medium mr-1">Sources :</span>
                  <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block" /> D'CLIC PRO</span>
                  <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-blue-500 inline-block" /> Analyse CV (IA)</span>
                  <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-pink-500 inline-block" /> Centres d'intérêt</span>
                  <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-slate-400 inline-block" /> Déclaratif</span>
                </div>
              )}
              {allSkills.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-3">
                  {allSkills.map((skill, idx) => {
                    const pct = skill.level || 0;
                    const src = skill.source || "";
                    const isDclic = src === "dclic_pro";
                    const isIA = src === "ia_detectee" || src === "analyse_cv";
                    const isCentres = src === "centres_interet";
                    const barColor = isDclic ? "[&>div]:bg-emerald-500" : isIA ? "[&>div]:bg-blue-500" : isCentres ? "[&>div]:bg-pink-500" : "";
                    const labelColor = isDclic ? "text-emerald-700" : isIA ? "text-blue-700" : isCentres ? "text-pink-700" : "text-slate-700";
                    const dotColor = isDclic ? "bg-emerald-500" : isIA ? "bg-blue-500" : isCentres ? "bg-pink-500" : "bg-slate-400";
                    return (
                      <div key={idx} className="space-y-1.5" data-testid={`skill-${idx}`}>
                        <div className="flex items-center justify-between">
                          <span className={`text-sm font-medium ${labelColor} flex items-center gap-1.5`}>
                            <span className={`w-2 h-2 rounded-full ${dotColor} inline-block shrink-0`} />
                            {skill.name}
                          </span>
                          <span className="text-sm text-slate-500">{pct}%</span>
                        </div>
                        <Progress value={pct} className={`h-2 ${barColor}`} />
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="text-center py-4 text-slate-400 text-sm">
                  <p>Chargez un CV ou passez le test D'CLIC PRO pour identifier vos compétences</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* === DOCUMENTS TAB === */}
        <TabsContent value="documents" className="space-y-6 mt-6">
          <Card className="bg-gradient-to-r from-[#1e3a5f] to-[#2d4a6f] border-0" data-testid="coffre-fort-banner">
            <CardContent className="p-6">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 rounded-xl bg-white/20 flex items-center justify-center">
                    <FolderLock className="w-7 h-7 text-white" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-white">Coffre-Fort Professionnel</h3>
                    <p className="text-blue-100 text-sm">Conservez et valorisez vos documents : diplômes, expériences, preuves de compétences</p>
                  </div>
                </div>
                <Button className="bg-white text-[#1e3a5f] hover:bg-blue-50 font-semibold" onClick={() => navigate('/dashboard/coffre-fort')} data-testid="goto-coffre-fort-btn">
                  <FolderLock className="w-4 h-4 mr-2" />Accéder au coffre-fort
                </Button>
              </div>
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="card-base cursor-pointer hover:border-blue-300 transition-colors" onClick={() => navigate('/dashboard/coffre-fort')} data-testid="doc-category-identite">
              <CardContent className="p-5 text-center">
                <div className="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center mx-auto mb-3"><FileText className="w-6 h-6 text-blue-600" /></div>
                <h4 className="text-sm font-semibold text-slate-800">Identité professionnelle</h4>
                <p className="text-xs text-slate-500 mt-1">CV, lettres de motivation</p>
              </CardContent>
            </Card>
            <Card className="card-base cursor-pointer hover:border-emerald-300 transition-colors" onClick={() => navigate('/dashboard/coffre-fort')} data-testid="doc-category-diplomes">
              <CardContent className="p-5 text-center">
                <div className="w-12 h-12 rounded-xl bg-emerald-100 flex items-center justify-center mx-auto mb-3"><GraduationCap className="w-6 h-6 text-emerald-600" /></div>
                <h4 className="text-sm font-semibold text-slate-800">Diplômes & Certifications</h4>
                <p className="text-xs text-slate-500 mt-1">Preuves de formation</p>
              </CardContent>
            </Card>
            <Card className="card-base cursor-pointer hover:border-violet-300 transition-colors" onClick={() => navigate('/dashboard/coffre-fort')} data-testid="doc-category-preuves">
              <CardContent className="p-5 text-center">
                <div className="w-12 h-12 rounded-xl bg-violet-100 flex items-center justify-center mx-auto mb-3"><Award className="w-6 h-6 text-violet-600" /></div>
                <h4 className="text-sm font-semibold text-slate-800">Preuves de compétences</h4>
                <p className="text-xs text-slate-500 mt-1">Attestations, évaluations</p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* === MATCHING TAB === */}
        <TabsContent value="matching" className="space-y-6 mt-6">
          <Card className="card-base" data-testid="jobs-preview">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2"><Briefcase className="w-5 h-5 text-[#1e3a5f]" />Job Matching</CardTitle>
                <CardDescription>Métiers compatibles avec vos compétences transférables</CardDescription>
              </div>
              <Button variant="outline" size="sm" onClick={() => navigate('/dashboard/jobs')}>
                Voir tout<ChevronRight className="w-4 h-4 ml-1" />
              </Button>
            </CardHeader>
            {jobs.length > 0 && (
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {jobs.slice(0, 3).map((job, idx) => {
                    const title = job.title || job.titre || "Offre";
                    const company = job.company || job.entreprise_type || "";
                    const score = job.match_score ?? job.matching_score;
                    const skills = job.required_skills || job.competences_requises || [];
                    return (
                      <Card key={idx} className="card-interactive group" data-testid={`job-card-${idx}`}>
                        <CardContent className="p-4">
                          <div className="flex items-start justify-between mb-2">
                            <h4 className="font-semibold text-sm text-slate-900 group-hover:text-blue-600 transition-colors truncate flex-1">{String(title)}</h4>
                            {score !== undefined && (
                              <Badge className={`ml-2 text-[10px] ${score >= 80 ? 'bg-emerald-100 text-emerald-700' : score >= 60 ? 'bg-blue-100 text-blue-700' : 'bg-slate-100 text-slate-600'}`}>{score}%</Badge>
                            )}
                          </div>
                          {company && <p className="text-xs text-slate-500 mb-2">{String(company)}</p>}
                          <div className="flex flex-wrap gap-1">
                            {skills.slice(0, 3).map((s, i) => <Badge key={i} variant="secondary" className="text-[10px]">{String(s)}</Badge>)}
                          </div>
                        </CardContent>
                      </Card>
                    );
                  })}
                </div>
              </CardContent>
            )}
          </Card>

          <Card className="card-base" data-testid="learning-preview">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2"><BookOpen className="w-5 h-5 text-[#1e3a5f]" />Parcours de Formation</CardTitle>
                <CardDescription>Développez vos compétences et sécurisez votre trajectoire</CardDescription>
              </div>
              <Button variant="outline" size="sm" onClick={() => navigate('/dashboard/learning')}>
                Voir tout<ChevronRight className="w-4 h-4 ml-1" />
              </Button>
            </CardHeader>
            {learningModules.length > 0 && (
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {learningModules.slice(0, 3).map((mod, idx) => (
                    <Card key={idx} className="card-interactive group" data-testid={`learning-preview-${idx}`}>
                      <CardContent className="p-4">
                        <Badge variant="secondary" className="text-xs mb-2">{mod.category}</Badge>
                        <h4 className="font-semibold text-sm text-slate-900 group-hover:text-blue-600 transition-colors mb-1">{mod.title}</h4>
                        <p className="text-xs text-slate-500 line-clamp-2 mb-2">{mod.description}</p>
                        <div className="flex items-center justify-between text-[11px] text-slate-400">
                          <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{mod.duration}</span>
                          <Badge variant="outline" className="text-[10px]">{mod.level}</Badge>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            )}
          </Card>
        </TabsContent>
      </Tabs>

      {/* Step Form Dialog */}
      <StepFormDialog open={stepDialogOpen} onOpenChange={setStepDialogOpen} step={editingStep} token={token} onSaved={loadTrajectory} />
      <ShareDialog open={shareDialogOpen} onOpenChange={setShareDialogOpen} token={token} />
    </div>
  );
};

// ===== LEARNING SECTION (full page) =====
const LearningSection = ({ modules, updateProgress, token }) => {
  const [recommendations, setRecommendations] = useState([]);
  const [loadingRecs, setLoadingRecs] = useState(false);

  useEffect(() => {
    const loadRecs = async () => {
      setLoadingRecs(true);
      try {
        const res = await axios.get(`${API}/learning/recommendations?token=${token}`);
        if (res.data.has_data) setRecommendations(res.data.recommendations || []);
      } catch (e) { console.error("Recs error:", e); }
      setLoadingRecs(false);
    };
    if (token) loadRecs();
  }, [token]);

  const priorityConfig = {
    haute: { color: "bg-rose-100 text-rose-700 border-rose-200", label: "Prioritaire" },
    moyenne: { color: "bg-amber-100 text-amber-700 border-amber-200", label: "Recommandée" },
    basse: { color: "bg-slate-100 text-slate-600 border-slate-200", label: "Optionnelle" },
  };
  const typeConfig = {
    certifiante: { color: "bg-blue-100 text-blue-700", label: "Certifiante" },
    courte: { color: "bg-emerald-100 text-emerald-700", label: "Formation courte" },
    mooc: { color: "bg-violet-100 text-violet-700", label: "MOOC" },
    diplome: { color: "bg-amber-100 text-amber-700", label: "Diplôme" },
  };

  return (
    <div className="space-y-6 animate-fade-in" data-testid="learning-section">
      <div>
        <h1 className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>Parcours de Formation</h1>
        <p className="text-slate-600 mt-1">Développez vos compétences et sécurisez votre trajectoire professionnelle</p>
        <div className="mt-3 p-3 bg-blue-50 rounded-lg border border-blue-100 flex items-start gap-2" data-testid="ai-disclaimer">
          <AlertCircle className="w-4 h-4 text-blue-500 mt-0.5 shrink-0" />
          <p className="text-xs text-blue-700">Ces suggestions sont générées par IA. Vérifiez les contenus directement auprès des organismes.</p>
        </div>
      </div>

      {(recommendations.length > 0 || loadingRecs) && (
        <div data-testid="ai-recommendations-section">
          <div className="flex items-center gap-2 mb-4">
            <Sparkles className="w-5 h-5 text-violet-600" />
            <h2 className="text-lg font-semibold text-slate-900">Formations recommandées</h2>
          </div>
          {loadingRecs ? (
            <div className="flex items-center gap-3 p-4 bg-violet-50 rounded-xl border border-violet-100">
              <div className="w-5 h-5 border-2 border-violet-300 border-t-violet-600 rounded-full animate-spin" />
              <span className="text-sm text-violet-700">Analyse en cours...</span>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {recommendations.map((rec, idx) => {
                const pConf = priorityConfig[rec.priority] || priorityConfig.moyenne;
                const tConf = typeConfig[rec.type] || typeConfig.courte;
                return (
                  <Card key={idx} className={`card-interactive group ${rec.priority === "haute" ? "ring-2 ring-violet-200" : ""}`} data-testid={`rec-card-${idx}`}>
                    <CardContent className="p-5">
                      <div className="flex items-center justify-between mb-2 flex-wrap gap-1">
                        <Badge className={`text-[10px] border ${pConf.color}`}>{pConf.label}</Badge>
                        <Badge className={`text-[10px] ${tConf.color}`}>{tConf.label}</Badge>
                      </div>
                      {rec.emerging_skills?.length > 0 && (
                        <div className="flex flex-wrap gap-1 mb-2" data-testid={`rec-emerging-${idx}`}>
                          {rec.emerging_skills.map((es, i) => (
                            <Badge key={i} className="text-[10px] bg-amber-50 text-amber-700 border border-amber-300"><Zap className="w-3 h-3 mr-0.5" />{es}</Badge>
                          ))}
                        </div>
                      )}
                      <h3 className="font-semibold text-slate-900 text-sm mb-1 group-hover:text-violet-600 transition-colors">
                        <a href={`https://www.google.com/search?q=${encodeURIComponent(rec.title + " formation")}`} target="_blank" rel="noopener noreferrer"
                          className="flex items-center gap-1.5 hover:underline underline-offset-2" data-testid={`rec-title-link-${idx}`}>
                          {rec.title}<ExternalLink className="w-3.5 h-3.5 text-slate-400 group-hover:text-violet-500 shrink-0" />
                        </a>
                      </h3>
                      <p className="text-xs text-slate-500 mb-2">{rec.provider} {rec.duration && <span>- {rec.duration}</span>}</p>
                      <p className="text-xs text-slate-600 mb-3 line-clamp-2">{rec.description}</p>
                      {rec.relevance_reason && (
                        <div className="p-2 bg-violet-50 rounded-lg mb-3 border border-violet-100">
                          <p className="text-[11px] text-violet-700"><Sparkles className="w-3 h-3 inline mr-1" />{rec.relevance_reason}</p>
                        </div>
                      )}
                      <div className="flex items-center justify-between text-[10px] text-slate-400 mt-2">
                        <span>{rec.level === "debutant" ? "Débutant" : rec.level === "intermediaire" ? "Intermédiaire" : "Avancé"}</span>
                        {rec.cpf_eligible && <Badge className="bg-emerald-50 text-emerald-600 text-[10px]">CPF</Badge>}
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}
        </div>
      )}

      {modules.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-2">
            <BookOpen className="w-5 h-5 text-[#1e3a5f]" />
            <h2 className="text-lg font-semibold text-slate-900">Modules de formation</h2>
          </div>
          <div className="mb-4 p-2.5 bg-amber-50 rounded-lg border border-amber-200 flex items-start gap-2" data-testid="formations-sample-data-banner">
            <AlertCircle className="w-4 h-4 text-amber-500 mt-0.5 shrink-0" />
            <p className="text-xs text-amber-700">Exemples initiaux. Enrichis avec des contenus personnalisés.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {modules.map((module, idx) => (
              <Card key={idx} className={`card-interactive group overflow-hidden ${module.emerging_match?.length > 0 ? "ring-2 ring-amber-400 border-amber-300" : module.relevance === "haute" ? "ring-2 ring-blue-200" : ""}`} data-testid={`learning-card-${module.id}`}>
                {module.emerging_match?.length > 0 && (
                  <div className="bg-gradient-to-r from-amber-500 to-orange-500 px-4 py-2 flex items-center gap-2">
                    <Zap className="w-4 h-4 text-white" /><span className="text-xs font-semibold text-white">Compétence émergente</span>
                  </div>
                )}
                <CardContent className="p-5">
                  <Badge variant="secondary" className="text-xs mb-2">{module.category}</Badge>
                  <h3 className="font-semibold text-slate-900 mb-1 group-hover:text-blue-600 transition-colors">
                    <a href={`https://www.google.com/search?q=${encodeURIComponent(module.title + " formation")}`} target="_blank" rel="noopener noreferrer"
                      className="flex items-center gap-1.5 hover:underline underline-offset-2" data-testid={`learning-title-link-${module.id}`}>
                      {module.title}<ExternalLink className="w-3.5 h-3.5 text-slate-400 group-hover:text-blue-500 shrink-0" />
                    </a>
                  </h3>
                  <p className="text-xs text-slate-500 mb-3 line-clamp-2">{module.description}</p>
                  <div className="flex items-center justify-between text-xs text-slate-500">
                    <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{module.duration}</span>
                    <Badge variant="outline">{module.level}</Badge>
                  </div>
                  <a href={`https://www.google.com/search?q=${encodeURIComponent(module.title + " formation")}`} target="_blank" rel="noopener noreferrer" className="block w-full mt-3">
                    <Button variant="outline" size="sm" className="w-full hover:bg-blue-50 hover:text-blue-600" data-testid={`learning-start-btn-${module.id}`}>
                      <ExternalLink className="w-3 h-3 mr-1" />Accéder
                    </Button>
                  </a>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ParticulierView;
