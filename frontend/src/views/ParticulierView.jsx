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
import { Switch } from "@/components/ui/switch";
import {
  User, Target, TrendingUp, BookOpen, Briefcase, MapPin, Clock, Euro,
  Star, ChevronRight, Plus, Sparkles, Zap, Award, AlertCircle,
  Play, FolderLock, FileDown, FileText, LayoutList, Layers, Shield, BarChart3,
  ExternalLink, Upload, CheckCircle, Bell, CheckCircle2, Loader2,
  Route, Eye, EyeOff, Users, Building2, Handshake, GraduationCap,
  Trash2, Edit3, ChevronDown, ChevronUp, Lock, History, RefreshCw,
  Lightbulb, Compass, Heart, Brain, ArrowRight
} from "lucide-react";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";
import CvAnalysisSection from "@/components/CvAnalysis/CvAnalysisSection";
import JobMatchingSection from "@/components/JobMatchingSection";

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
const DclicBoostSection = ({ profile }) => {
  const [expanded, setExpanded] = useState(false);
  const dclicSkills = (profile.skills || []).filter(s => s.source === "dclic_pro");
  const competences = profile.dclic_competences || [];
  const dimensions = [
    profile.dclic_mbti && { label: "Personnalité MBTI", value: profile.dclic_mbti, color: "from-violet-500 to-purple-600", icon: User, description: "Votre type de personnalité" },
    profile.dclic_disc_label && { label: "Profil DISC", value: profile.dclic_disc_label, color: "from-blue-500 to-cyan-600", icon: Target, description: "Votre style comportemental" },
    profile.dclic_riasec_major && { label: "Intérêts RIASEC", value: profile.dclic_riasec_major, color: "from-emerald-500 to-teal-600", icon: TrendingUp, description: "Votre orientation professionnelle" },
    profile.dclic_vertu_dominante && { label: "Vertu dominante", value: profile.dclic_vertu_dominante, color: "from-amber-500 to-orange-600", icon: Award, description: "Votre force motrice" },
  ].filter(Boolean);

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
          <Button variant="ghost" size="sm" className="text-white hover:bg-white/10" onClick={() => setExpanded(!expanded)} data-testid="dclic-boost-toggle">
            {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            <span className="ml-1 text-xs">{expanded ? "Réduire" : "Voir le détail"}</span>
          </Button>
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
        {expanded && (
          <div className="mt-4 pt-4 border-t border-slate-100 space-y-3 animate-in fade-in slide-in-from-top-2 duration-300">
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

// ===== TIMELINE STEP CARD =====
const TimelineStepCard = ({ step, onEdit, onDelete }) => {
  const config = STEP_TYPES[step.step_type] || STEP_TYPES.emploi;
  const StepIcon = config.icon;
  const visOpt = VISIBILITY_OPTIONS.find(v => v.value === step.visibility) || VISIBILITY_OPTIONS[0];
  const VisIcon = visOpt.icon;

  return (
    <div className="relative pl-10 pb-8 group" data-testid={`timeline-step-${step.id}`}>
      {/* Timeline line */}
      <div className="absolute left-[15px] top-8 bottom-0 w-0.5 bg-slate-200 group-last:hidden" />
      {/* Step dot */}
      <div className={`absolute left-0 top-1 w-8 h-8 rounded-full ${config.color} flex items-center justify-center shadow-md z-10`}>
        <StepIcon className="w-4 h-4 text-white" />
      </div>
      <Card className={`${config.bg} ${config.border} border shadow-sm hover:shadow-md transition-shadow`}>
        <CardContent className="p-4">
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap mb-1">
                <Badge className={`text-[10px] ${config.bg} ${config.text} ${config.border} border`}>{config.label}</Badge>
                <span className="text-[11px] text-slate-400">
                  {step.start_date}{step.end_date ? ` — ${step.end_date}` : step.is_ongoing ? " — En cours" : ""}
                </span>
                <Badge variant="outline" className="text-[10px] gap-0.5">
                  <VisIcon className="w-2.5 h-2.5" />{visOpt.label}
                </Badge>
              </div>
              <h4 className="font-semibold text-slate-900 text-sm">{step.title}</h4>
              {step.organization && <p className="text-xs text-slate-500 mt-0.5">{step.organization}</p>}
              {step.description && <p className="text-xs text-slate-600 mt-2 line-clamp-2">{step.description}</p>}
              {step.competences?.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {step.competences.slice(0, 5).map((c, i) => (
                    <Badge key={i} variant="secondary" className="text-[10px]">{c}</Badge>
                  ))}
                </div>
              )}
              {step.acquis && (
                <p className="text-[11px] text-emerald-700 mt-2 bg-emerald-50 rounded px-2 py-1 inline-block">
                  <Lightbulb className="w-3 h-3 inline mr-1" />{step.acquis}
                </p>
              )}
            </div>
            <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
              <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => onEdit(step)} data-testid={`edit-step-${step.id}`}>
                <Edit3 className="w-3.5 h-3.5 text-slate-500" />
              </Button>
              <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => onDelete(step.id)} data-testid={`delete-step-${step.id}`}>
                <Trash2 className="w-3.5 h-3.5 text-red-400" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
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
      toast.success(isEdit ? "Etape modifiée" : "Etape ajoutée");
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
    { key: "partenaire", label: "Partenaires de parcours", desc: "Accès limité au suivi", icon: Users, status: settings?.partenaire ? "Autorisé" : "Désactivé", active: !!settings?.partenaire, color: "amber" },
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
const SynthesisSection = ({ synthesis, loading }) => {
  if (loading) {
    return (
      <Card className="border border-violet-100 bg-violet-50/30">
        <CardContent className="p-6 flex items-center gap-3">
          <Loader2 className="w-5 h-5 animate-spin text-violet-600" />
          <span className="text-sm text-violet-700">Analyse de votre parcours en cours...</span>
        </CardContent>
      </Card>
    );
  }
  if (!synthesis) return null;

  return (
    <Card className="border-0 shadow-lg overflow-hidden" data-testid="synthesis-section">
      <div className="bg-gradient-to-r from-[#1e3a5f] to-[#2d5a8e] p-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-white/15 flex items-center justify-center">
            <Brain className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">Ce que mon parcours révèle</h3>
            <p className="text-blue-200 text-xs">Analyse valorisante générée par IA</p>
          </div>
        </div>
      </div>
      <CardContent className="p-5 space-y-4">
        {synthesis.fil_conducteur && (
          <div className="p-3 bg-blue-50 rounded-lg border border-blue-100">
            <p className="text-xs font-semibold text-blue-800 mb-1 flex items-center gap-1"><Route className="w-3.5 h-3.5" /> Fil conducteur</p>
            <p className="text-sm text-slate-700">{synthesis.fil_conducteur}</p>
          </div>
        )}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {synthesis.forces_recurrentes?.length > 0 && (
            <div className="p-3 bg-emerald-50 rounded-lg border border-emerald-100">
              <p className="text-xs font-semibold text-emerald-800 mb-2 flex items-center gap-1"><Zap className="w-3.5 h-3.5" /> Forces récurrentes</p>
              <div className="flex flex-wrap gap-1">
                {synthesis.forces_recurrentes.map((f, i) => <Badge key={i} className="bg-emerald-100 text-emerald-700 text-xs">{f}</Badge>)}
              </div>
            </div>
          )}
          {synthesis.competences_transferables?.length > 0 && (
            <div className="p-3 bg-violet-50 rounded-lg border border-violet-100">
              <p className="text-xs font-semibold text-violet-800 mb-2 flex items-center gap-1"><Sparkles className="w-3.5 h-3.5" /> Compétences transférables</p>
              <div className="flex flex-wrap gap-1">
                {synthesis.competences_transferables.map((c, i) => <Badge key={i} className="bg-violet-100 text-violet-700 text-xs">{c}</Badge>)}
              </div>
            </div>
          )}
        </div>
        {synthesis.capacite_adaptation && (
          <div className="p-3 bg-amber-50 rounded-lg border border-amber-100">
            <p className="text-xs font-semibold text-amber-800 mb-1 flex items-center gap-1"><RefreshCw className="w-3.5 h-3.5" /> Capacité d'adaptation</p>
            <p className="text-sm text-slate-700">{synthesis.capacite_adaptation}</p>
          </div>
        )}
        {synthesis.axes_evolution?.length > 0 && (
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
            <p className="text-xs font-semibold text-slate-700 mb-2 flex items-center gap-1"><TrendingUp className="w-3.5 h-3.5" /> Axes d'évolution</p>
            <div className="space-y-1">
              {synthesis.axes_evolution.map((a, i) => (
                <p key={i} className="text-sm text-slate-600 flex items-center gap-2"><ArrowRight className="w-3 h-3 text-blue-500 shrink-0" />{a}</p>
              ))}
            </div>
          </div>
        )}
        {synthesis.message_valorisant && (
          <div className="p-4 bg-gradient-to-r from-blue-50 to-violet-50 rounded-xl border border-blue-100 text-center">
            <p className="text-sm font-medium text-slate-800 italic">"{synthesis.message_valorisant}"</p>
          </div>
        )}
      </CardContent>
    </Card>
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

  return (
    <Card className={`border ${pending.length > 0 ? "border-amber-200 bg-amber-50/30" : "border-slate-100"}`} data-testid="access-requests-notifications">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-base">
          <Bell className="w-4 h-4 text-amber-600" />Demandes d'accès à votre profil
          {pending.length > 0 && <Badge className="bg-amber-100 text-amber-700 text-xs ml-1">{pending.length} en attente</Badge>}
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
          <div className="pt-2 border-t border-slate-100">
            <p className="text-xs font-medium text-slate-500 mb-2">Historique</p>
            {past.slice(0, 5).map(req => (
              <div key={req.id} className="flex items-center justify-between py-1.5 text-xs" data-testid={`access-history-${req.id}`}>
                <span className="text-slate-600">{req.partner_name}</span>
                <Badge className={req.status === "accepte" ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"} variant="secondary">
                  {req.status === "accepte" ? "Accepté" : "Refusé"}
                </Badge>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// ===== MAIN COMPONENT =====
const ParticulierView = ({ token, section, onOpenDclic }) => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [passport, setPassport] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [learningModules, setLearningModules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("trajectoire");
  const [steps, setSteps] = useState([]);
  const [synthesis, setSynthesis] = useState(null);
  const [loadingSynthesis, setLoadingSynthesis] = useState(false);
  const [visibilitySettings, setVisibilitySettings] = useState(null);
  const [stepDialogOpen, setStepDialogOpen] = useState(false);
  const [editingStep, setEditingStep] = useState(null);
  const [autoPopulating, setAutoPopulating] = useState(false);
  const [newSkill, setNewSkill] = useState("");
  const [editingProfile, setEditingProfile] = useState(false);

  useEffect(() => { loadData(); }, [token]);

  const loadData = async (silent = false) => {
    if (!silent) setLoading(true);
    try {
      const [profileRes, jobsRes, learningRes, passportRes] = await Promise.all([
        axios.get(`${API}/profile?token=${token}`),
        axios.get(`${API}/jobs?token=${token}`),
        axios.get(`${API}/learning?token=${token}`),
        axios.get(`${API}/passport?token=${token}`).catch(() => ({ data: null })),
      ]);
      setProfile(profileRes.data);
      setJobs(jobsRes.data);
      setLearningModules(learningRes.data);
      setPassport(passportRes.data);
    } catch (error) {
      console.error("Error loading data:", error);
      if (!silent) toast.error("Erreur lors du chargement");
    }
    if (!silent) setLoading(false);
  };

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

  useEffect(() => { if (activeTab === "trajectoire") loadTrajectory(); }, [activeTab, loadTrajectory]);

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
      toast.success("Etape supprimée");
      loadTrajectory();
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
    { title: "Job Matching", value: jobs.length > 0 ? (jobs.filter(j => (j.match_score || j.matching_score || 0) >= 60).length || jobs.length).toString() : "0", icon: Briefcase, color: "emerald", subtitle: "Offres disponibles" },
    { title: "Compétences", value: allSkills.length.toString(), icon: Zap, color: "violet", subtitle: "Toutes sources" },
    { title: "Parcours", value: steps.length.toString(), icon: Route, color: "amber", subtitle: "Étapes tracées" }
  ];

  return (
    <div className="space-y-6 animate-fade-in" data-testid="particulier-dashboard">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>
            Ma Trajectoire Professionnelle
          </h1>
          <p className="text-slate-500 mt-1 text-sm">Visualisez votre parcours, valorisez vos acquis, contrôlez vos données</p>
        </div>
        <Badge className="self-start bg-blue-100 text-[#1e3a5f] border-blue-200 px-3 py-1">
          <Shield className="w-3 h-3 mr-1" />Tiers de confiance numérique
        </Badge>
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

        {/* === TRAJECTOIRE TAB === */}
        <TabsContent value="trajectoire" className="space-y-6 mt-6">
          {/* Trust Banner */}
          <Card className="bg-gradient-to-r from-slate-50 to-blue-50 border border-blue-100" data-testid="trust-banner">
            <CardContent className="p-4 flex items-start gap-3">
              <div className="w-10 h-10 rounded-full bg-[#1e3a5f] flex items-center justify-center shrink-0">
                <Lock className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-slate-800">Vous contrôlez votre parcours</h3>
                <p className="text-xs text-slate-600 mt-0.5">
                  Votre parcours est personnel. Vous choisissez quelles informations sont visibles, par qui, et dans quel contexte.
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Visibility Cards */}
          <div>
            <h3 className="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2">
              <Eye className="w-4 h-4 text-[#1e3a5f]" /> Qui peut voir mon parcours ?
            </h3>
            <VisibilityCards settings={visibilitySettings} onUpdate={updateVisibility} />
          </div>

          {/* Timeline Header */}
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-700 flex items-center gap-2">
              <Route className="w-4 h-4 text-[#1e3a5f]" /> Mon parcours en étapes
            </h3>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={autoPopulate} disabled={autoPopulating} data-testid="auto-populate-btn">
                {autoPopulating ? <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" /> : <RefreshCw className="w-3.5 h-3.5 mr-1.5" />}
                Importer depuis mes données
              </Button>
              <Button size="sm" className="bg-[#1e3a5f] hover:bg-[#152a45]" onClick={() => { setEditingStep(null); setStepDialogOpen(true); }} data-testid="add-step-btn">
                <Plus className="w-3.5 h-3.5 mr-1.5" />Ajouter une étape
              </Button>
            </div>
          </div>

          {/* Timeline */}
          {steps.length > 0 ? (
            <div data-testid="timeline-container">
              {steps.map(step => (
                <TimelineStepCard key={step.id} step={step} onEdit={s => { setEditingStep(s); setStepDialogOpen(true); }} onDelete={deleteStep} />
              ))}
            </div>
          ) : (
            <Card className="border-dashed border-2 border-slate-200">
              <CardContent className="p-8 text-center">
                <Route className="w-10 h-10 text-slate-300 mx-auto mb-3" />
                <h4 className="text-sm font-semibold text-slate-600 mb-1">Votre frise de parcours est vide</h4>
                <p className="text-xs text-slate-400 mb-4">Ajoutez vos étapes professionnelles ou importez-les depuis vos données existantes</p>
                <div className="flex gap-2 justify-center">
                  <Button variant="outline" size="sm" onClick={autoPopulate} disabled={autoPopulating} data-testid="auto-populate-empty-btn">
                    <RefreshCw className="w-3.5 h-3.5 mr-1.5" />Importer automatiquement
                  </Button>
                  <Button size="sm" className="bg-[#1e3a5f] hover:bg-[#152a45]" onClick={() => { setEditingStep(null); setStepDialogOpen(true); }}>
                    <Plus className="w-3.5 h-3.5 mr-1.5" />Ajouter manuellement
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* AI Synthesis */}
          {(steps.length > 0 || allSkills.length > 0) && (
            <div>
              {!synthesis && !loadingSynthesis ? (
                <Button variant="outline" className="w-full border-violet-200 text-violet-700 hover:bg-violet-50" onClick={loadSynthesis} data-testid="generate-synthesis-btn">
                  <Brain className="w-4 h-4 mr-2" /> Générer l'analyse de mon parcours
                </Button>
              ) : (
                <SynthesisSection synthesis={synthesis} loading={loadingSynthesis} />
              )}
            </div>
          )}
        </TabsContent>

        {/* === COMPETENCES TAB === */}
        <TabsContent value="competences" className="space-y-6 mt-6">
          {/* D'CLIC Banner or Boost */}
          {profile?.dclic_imported ? (
            <DclicBoostSection profile={profile} />
          ) : (
            <Card className="bg-gradient-to-r from-indigo-600 to-blue-600 border-0 shadow-md cursor-pointer hover:shadow-lg transition-shadow" data-testid="dclic-test-banner" onClick={() => window.open('/test-dclic', '_blank', 'noopener,noreferrer')}>
              <CardContent className="p-4">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-white/20 flex items-center justify-center shrink-0">
                      <Award className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <h3 className="text-base font-semibold text-white">Passe le test D'CLIC PRO et Boost ton profil !</h3>
                      <p className="text-indigo-100 text-sm">Crédibilise tes compétences avec un profil personnalité validé</p>
                    </div>
                  </div>
                  <Button className="bg-white text-indigo-700 hover:bg-indigo-50 shrink-0 text-sm font-semibold" data-testid="dclic-test-btn" onClick={e => { e.stopPropagation(); window.open('/test-dclic', '_blank', 'noopener,noreferrer'); }}>
                    <Play className="w-4 h-4 mr-1.5" />Passer le test
                  </Button>
                </div>
              </CardContent>
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
