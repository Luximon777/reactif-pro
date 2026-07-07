import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Search, MapPin, Calendar, Users, Briefcase, Building2,
  Clock, Zap, Star, Bookmark, BookmarkCheck, UserCheck, CheckCircle2,
  Loader2, Filter, Monitor, Globe, ExternalLink, History,
  Target, TrendingUp, Sparkles, RefreshCw, CalendarDays,
  AlertTriangle, MessageSquare, ThumbsUp, ThumbsDown, Bell,
  Handshake, Brain, ChevronRight
} from "lucide-react";
import { toast } from "sonner";
import { Textarea } from "@/components/ui/textarea";

const EVENT_TYPE_MAP = {
  job_dating: { label: "Job Dating", color: "bg-blue-100 text-blue-700" },
  e_job_dating: { label: "E-Job Dating", color: "bg-violet-100 text-violet-700" },
  forum: { label: "Forum Emploi", color: "bg-amber-100 text-amber-700" },
  recrutement_collectif: { label: "Recrutement Collectif", color: "bg-emerald-100 text-emerald-700" },
  salon_emploi: { label: "Salon Emploi", color: "bg-rose-100 text-rose-700" },
};

const MODE_MAP = {
  presentiel: { label: "Présentiel", icon: MapPin },
  distanciel: { label: "En ligne", icon: Monitor },
  hybride: { label: "Hybride", icon: Globe },
};

const EventCard = ({ event, saved, onSave, compact, showAiReason }) => {
  const typeInfo = EVENT_TYPE_MAP[event.event_type] || EVENT_TYPE_MAP.job_dating;
  const modeInfo = MODE_MAP[event.mode] || MODE_MAP.presentiel;
  const ModeIcon = modeInfo.icon;
  const startDate = new Date(event.start_datetime);
  const dayName = startDate.toLocaleDateString("fr-FR", { weekday: "short" });
  const dayNum = startDate.getDate();
  const month = startDate.toLocaleDateString("fr-FR", { month: "short" });
  const time = startDate.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" });
  const hasUrl = !!event.registration_url;

  const handleCardClick = () => {
    if (hasUrl) window.open(event.registration_url, "_blank", "noopener,noreferrer");
    else toast.info("Aucun lien source disponible pour cet événement");
  };

  return (
    <Card
      className={`group hover:shadow-lg transition-all border-slate-200 hover:border-[#1e3a5f]/30 ${hasUrl ? "cursor-pointer" : "cursor-default"}`}
      onClick={handleCardClick}
      data-testid={`event-card-${event.title?.slice(0, 20)}`}
    >
      <CardContent className="p-4">
        <div className="flex gap-4">
          {/* Date Column */}
          <div className="shrink-0 w-16 text-center">
            <div className={`rounded-xl p-2 ${event.is_urgent ? "bg-red-50 border border-red-200" : event.is_soon ? "bg-amber-50 border border-amber-200" : "bg-slate-50 border border-slate-200"}`}>
              <p className="text-[10px] uppercase text-slate-500 font-medium">{dayName}</p>
              <p className={`text-2xl font-black ${event.is_urgent ? "text-red-600" : "text-slate-800"}`}>{dayNum}</p>
              <p className="text-xs text-slate-500">{month}</p>
            </div>
            <p className="text-[10px] text-slate-400 mt-1">{time}</p>
            {event.match_score > 0 && showAiReason && (
              <div className="mt-1.5">
                <div className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full ${
                  event.match_score >= 60 ? "bg-emerald-100 text-emerald-700" :
                  event.match_score >= 30 ? "bg-blue-100 text-blue-700" :
                  "bg-slate-100 text-slate-600"
                }`}>{event.match_score}%</div>
              </div>
            )}
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2 mb-1.5">
              <div className="flex items-center gap-1.5">
                <h3 className="text-sm font-bold text-slate-900 line-clamp-2 group-hover:text-[#1e3a5f] transition-colors">{event.title}</h3>
                {hasUrl && <ExternalLink className="w-3.5 h-3.5 text-slate-400 group-hover:text-[#1e3a5f] shrink-0 transition-colors" />}
              </div>
              {onSave && (
                <label
                  className="flex items-center gap-1.5 shrink-0 cursor-pointer select-none"
                  onClick={(e) => e.stopPropagation()}
                  data-testid="save-event-checkbox"
                >
                  <input
                    type="checkbox"
                    checked={saved}
                    onChange={() => onSave(event)}
                    className="w-4 h-4 rounded border-slate-300 text-[#1e3a5f] focus:ring-[#1e3a5f] cursor-pointer"
                  />
                  <span className="text-[10px] text-slate-500">{saved ? "Sauvegardé" : "Sauvegarder"}</span>
                </label>
              )}
            </div>

            {/* Badges row */}
            <div className="flex flex-wrap gap-1.5 mb-2">
              <Badge className={`text-[10px] ${typeInfo.color}`}>{typeInfo.label}</Badge>
              <Badge className="text-[10px] bg-slate-100 text-slate-600"><ModeIcon className="w-2.5 h-2.5 mr-0.5" />{modeInfo.label}</Badge>
              {event.source === "france_travail" && (
                <Badge className="text-[10px] bg-sky-50 text-sky-700 border border-sky-200" data-testid="source-badge">
                  <Globe className="w-2.5 h-2.5 mr-0.5" />France Travail
                </Badge>
              )}
              {event.source === "groupe_actu" && (
                <Badge className="text-[10px] bg-orange-50 text-orange-700 border border-orange-200" data-testid="source-badge">
                  <Globe className="w-2.5 h-2.5 mr-0.5" />Groupe Actu
                </Badge>
              )}
              {event.source === "24h_emploi" && (
                <Badge className="text-[10px] bg-teal-50 text-teal-700 border border-teal-200" data-testid="source-badge">
                  <Clock className="w-2.5 h-2.5 mr-0.5" />24h Emploi
                </Badge>
              )}
              {event.source === "salon_taf" && (
                <Badge className="text-[10px] bg-rose-50 text-rose-700 border border-rose-200" data-testid="source-badge">
                  <Users className="w-2.5 h-2.5 mr-0.5" />Salon TAF
                </Badge>
              )}
              {event.source === "village_recruteurs" && (
                <Badge className="text-[10px] bg-violet-50 text-violet-700 border border-violet-200" data-testid="source-badge">
                  <Handshake className="w-2.5 h-2.5 mr-0.5" />Village Recruteurs
                </Badge>
              )}
              {event.source === "jeunes_avenirs" && (
                <Badge className="text-[10px] bg-lime-50 text-lime-700 border border-lime-200" data-testid="source-badge">
                  <Sparkles className="w-2.5 h-2.5 mr-0.5" />Jeunes d'Avenirs
                </Badge>
              )}
              {(event.source === "cci_paris" || event.source === "cidj") && (
                <Badge className="text-[10px] bg-cyan-50 text-cyan-700 border border-cyan-200" data-testid="source-badge">
                  <Building2 className="w-2.5 h-2.5 mr-0.5" />{event.source === "cci_paris" ? "CCI Paris" : "CIDJ"}
                </Badge>
              )}
              {event.is_urgent && <Badge className="text-[10px] bg-red-100 text-red-700">Urgent</Badge>}
              {event.is_soon && !event.is_urgent && <Badge className="text-[10px] bg-amber-100 text-amber-700">Bientôt</Badge>}
              {event.match_level === "fort" && <Badge className="text-[10px] bg-emerald-100 text-emerald-700"><Target className="w-2.5 h-2.5 mr-0.5" />Recommandé</Badge>}
              {event.is_partner_event && (
                <Badge className="text-[10px] bg-purple-100 text-purple-700 border border-purple-200" data-testid="partner-badge">
                  <Handshake className="w-2.5 h-2.5 mr-0.5" />{event.partner_name || "Partenaire"}
                </Badge>
              )}
              {event.has_profile_access && (
                <Badge className="text-[10px] bg-amber-50 text-amber-700 border border-amber-300 font-semibold" data-testid="profile-access-badge">
                  <UserCheck className="w-2.5 h-2.5 mr-0.5" />Accès profil
                </Badge>
              )}
            </div>

            {event.description && <p className="text-xs text-slate-500 line-clamp-1 mb-1.5">{event.description}</p>}

            {/* AI recommendation reason */}
            {showAiReason && event.ai_reason && (
              <div className="bg-indigo-50 border border-indigo-100 rounded-lg px-2.5 py-1.5 mb-1.5" data-testid="ai-reason">
                <p className="text-[11px] text-indigo-700 flex items-start gap-1">
                  <Brain className="w-3 h-3 mt-0.5 shrink-0" />
                  <span>{event.ai_reason}</span>
                </p>
              </div>
            )}

            <div className="flex items-center gap-3 text-xs text-slate-500">
              <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{event.city}</span>
              {event.companies_count > 0 && <span className="flex items-center gap-1"><Building2 className="w-3 h-3" />{event.companies_count} entreprises</span>}
              {event.positions_count > 0 && <span className="flex items-center gap-1"><Briefcase className="w-3 h-3" />{event.positions_count} postes</span>}
            </div>

            {!compact && event.jobs_targeted?.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-2">
                {event.jobs_targeted.slice(0, 4).map((j, i) => (
                  <span key={i} className="text-[10px] bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full">{j}</span>
                ))}
                {event.jobs_targeted.length > 4 && <span className="text-[10px] text-slate-400">+{event.jobs_targeted.length - 4}</span>}
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

const NO_SHOW_REASONS = [
  { value: "empechement", label: "Empêchement personnel" },
  { value: "autre_opportunite", label: "Autre opportunité trouvée" },
  { value: "plus_interesse", label: "Plus intéressé par le poste" },
  { value: "transport", label: "Problème de transport" },
  { value: "sante", label: "Problème de santé" },
  { value: "oubli", label: "Oubli" },
  { value: "autre", label: "Autre" },
];

const StarRating = ({ value, onChange, label }) => (
  <div className="flex items-center gap-2">
    <span className="text-xs text-slate-600 w-28 shrink-0">{label}</span>
    <div className="flex gap-0.5">
      {[1, 2, 3, 4, 5].map(s => (
        <button key={s} type="button" onClick={() => onChange(s)} className="p-0.5">
          <Star className={`w-5 h-5 transition-colors ${s <= value ? "text-amber-400 fill-amber-400" : "text-slate-200"}`} />
        </button>
      ))}
    </div>
  </div>
);

const HistoryPanel = ({ token }) => {
  const [history, setHistory] = useState({ upcoming: [], past: [] });
  const [loading, setLoading] = useState(true);
  const [evalForms, setEvalForms] = useState({});
  const [noShowForms, setNoShowForms] = useState({});
  const [submitting, setSubmitting] = useState(null);

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    axios.get(`${API}/jobdating/history`, { params: { token }, timeout: 15000 })
      .then(res => setHistory(res.data || { upcoming: [], past: [] }))
      .catch(() => toast.error("Erreur chargement historique"))
      .finally(() => setLoading(false));
  }, [token]);

  const handleParticipated = async (eventId, participated) => {
    setSubmitting(eventId);
    try {
      await axios.post(`${API}/jobdating/events/${encodeURIComponent(eventId)}/participated`, null, {
        params: { token, participated }
      });
      setHistory(h => ({
        ...h,
        past: h.past.map(e => e.title === eventId ? { ...e, participated } : e)
      }));
      toast.success(participated ? "Participation confirmée" : "Non-participation enregistrée");
    } catch { toast.error("Erreur"); }
    finally { setSubmitting(null); }
  };

  const submitEval = async (eventId) => {
    const f = evalForms[eventId] || {};
    setSubmitting(eventId);
    try {
      await axios.post(`${API}/jobdating/events/${encodeURIComponent(eventId)}/evaluate`, null, {
        params: { token, rating: f.rating || 3, organization: f.organization || 3, usefulness: f.usefulness || 3, would_recommend: f.would_recommend !== false, comment: f.comment || "" }
      });
      setHistory(h => ({
        ...h,
        past: h.past.map(e => e.title === eventId ? { ...e, participated: true, evaluation: { ...f, evaluated_at: new Date().toISOString() } } : e)
      }));
      toast.success("Merci pour votre évaluation !");
    } catch { toast.error("Erreur"); }
    finally { setSubmitting(null); }
  };

  const submitNoShow = async (eventId) => {
    const f = noShowForms[eventId] || {};
    if (!f.reason) { toast.error("Veuillez sélectionner un motif"); return; }
    setSubmitting(eventId);
    try {
      await axios.post(`${API}/jobdating/events/${encodeURIComponent(eventId)}/no-show`, null, {
        params: { token, reason: f.reason, details: f.details || "" }
      });
      setHistory(h => ({
        ...h,
        past: h.past.map(e => e.title === eventId ? { ...e, participated: false, non_participation_reason: { reason: f.reason, details: f.details } } : e)
      }));
      toast.success("Motif enregistré");
    } catch { toast.error("Erreur"); }
    finally { setSubmitting(null); }
  };

  const updateEval = (eventId, field, value) => {
    setEvalForms(prev => ({ ...prev, [eventId]: { ...(prev[eventId] || { rating: 3, organization: 3, usefulness: 3, would_recommend: true, comment: "" }), [field]: value } }));
  };

  const updateNoShow = (eventId, field, value) => {
    setNoShowForms(prev => ({ ...prev, [eventId]: { ...(prev[eventId] || {}), [field]: value } }));
  };

  const formatDate = (iso) => {
    try { return new Date(iso).toLocaleDateString("fr-FR", { weekday: "long", day: "numeric", month: "long", hour: "2-digit", minute: "2-digit" }); }
    catch { return iso; }
  };

  if (loading) return <div className="flex justify-center py-10"><Loader2 className="w-6 h-6 animate-spin text-[#1e3a5f]" /></div>;

  const total = history.upcoming.length + history.past.length;
  if (total === 0) {
    return (
      <Card className="border-dashed border-2 border-slate-200">
        <CardContent className="p-8 text-center">
          <History className="w-8 h-8 text-slate-300 mx-auto mb-2" />
          <p className="text-sm text-slate-500">Aucun historique</p>
          <p className="text-xs text-slate-400 mt-1">Inscrivez-vous à un événement pour commencer votre suivi</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6" data-testid="history-panel">
      {/* Upcoming registrations */}
      {history.upcoming.length > 0 && (
        <div>
          <h3 className="text-sm font-bold text-slate-800 flex items-center gap-2 mb-3">
            <Bell className="w-4 h-4 text-[#1e3a5f]" />
            Inscriptions en cours ({history.upcoming.length})
          </h3>
          <div className="space-y-3">
            {history.upcoming.map((evt, i) => (
              <Card key={i} className="border-blue-200 bg-blue-50/20" data-testid={`history-upcoming-${i}`}>
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    <div className="w-12 h-12 rounded-xl bg-[#1e3a5f] flex items-center justify-center shrink-0">
                      <CalendarDays className="w-5 h-5 text-white" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="text-sm font-bold text-slate-900">{evt.title}</h4>
                        <Badge className="text-[10px] bg-blue-100 text-blue-700">
                          {evt.days_until === 0 ? "Aujourd'hui" : evt.days_until === 1 ? "Demain" : `Dans ${evt.days_until} jours`}
                        </Badge>
                      </div>
                      <p className="text-xs text-slate-500">{formatDate(evt.start_datetime)} — {evt.city}</p>

                      {/* Preparation tips */}
                      <div className="mt-3 bg-amber-50 border border-amber-200 rounded-lg p-3">
                        <p className="text-xs font-semibold text-amber-800 mb-1.5 flex items-center gap-1">
                          <Sparkles className="w-3.5 h-3.5" /> Conseils de préparation
                        </p>
                        <ul className="text-[11px] text-amber-700 space-y-1">
                          <li>• Préparez votre CV à jour et une lettre de motivation</li>
                          <li>• Renseignez-vous sur les entreprises présentes ({(evt.companies_list || []).slice(0, 3).map(c => c.name).join(", ")}...)</li>
                          <li>• {evt.mode === "distanciel" ? "Vérifiez votre connexion internet et votre micro/caméra" : `Repérez le lieu : ${evt.address || evt.city}`}</li>
                          <li>• Arrivez 15 minutes en avance pour vous préparer</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Past events */}
      {history.past.length > 0 && (
        <div>
          <h3 className="text-sm font-bold text-slate-800 flex items-center gap-2 mb-3">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            Événements passés ({history.past.length})
          </h3>
          <div className="space-y-3">
            {history.past.map((evt, i) => (
              <Card key={i} className="border-slate-200" data-testid={`history-past-${i}`}>
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 ${
                      evt.participated === true ? "bg-emerald-100" : evt.participated === false ? "bg-red-100" : "bg-slate-100"
                    }`}>
                      {evt.participated === true ? <ThumbsUp className="w-5 h-5 text-emerald-600" /> :
                       evt.participated === false ? <ThumbsDown className="w-5 h-5 text-red-500" /> :
                       <CalendarDays className="w-5 h-5 text-slate-400" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="text-sm font-bold text-slate-900 mb-0.5">{evt.title}</h4>
                      <p className="text-xs text-slate-500 mb-2">{formatDate(evt.start_datetime)} — {evt.city}</p>

                      {/* Participation not yet declared */}
                      {evt.participated === null && (
                        <div className="bg-slate-50 border border-slate-200 rounded-lg p-3">
                          <p className="text-xs font-semibold text-slate-700 mb-2">Avez-vous participé à cet événement ?</p>
                          <div className="flex gap-2">
                            <Button size="sm" onClick={() => handleParticipated(evt.title, true)} disabled={submitting === evt.title}
                              className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs" data-testid={`participated-yes-${i}`}>
                              <ThumbsUp className="w-3.5 h-3.5 mr-1" /> Oui, j'ai participé
                            </Button>
                            <Button size="sm" variant="outline" onClick={() => handleParticipated(evt.title, false)} disabled={submitting === evt.title}
                              className="text-xs border-red-200 text-red-600 hover:bg-red-50" data-testid={`participated-no-${i}`}>
                              <ThumbsDown className="w-3.5 h-3.5 mr-1" /> Non
                            </Button>
                          </div>
                        </div>
                      )}

                      {/* Participated → Evaluation form */}
                      {evt.participated === true && !evt.evaluation && (
                        <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-3 space-y-3" data-testid={`eval-form-${i}`}>
                          <p className="text-xs font-semibold text-emerald-800 flex items-center gap-1">
                            <Star className="w-3.5 h-3.5" /> Évaluez cet événement
                          </p>
                          <StarRating label="Note globale" value={(evalForms[evt.title] || {}).rating || 3} onChange={(v) => updateEval(evt.title, "rating", v)} />
                          <StarRating label="Organisation" value={(evalForms[evt.title] || {}).organization || 3} onChange={(v) => updateEval(evt.title, "organization", v)} />
                          <StarRating label="Utilité" value={(evalForms[evt.title] || {}).usefulness || 3} onChange={(v) => updateEval(evt.title, "usefulness", v)} />
                          <div className="flex items-center gap-2">
                            <span className="text-xs text-slate-600 w-28 shrink-0">Recommander ?</span>
                            <div className="flex gap-2">
                              <button onClick={() => updateEval(evt.title, "would_recommend", true)}
                                className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors ${(evalForms[evt.title] || {}).would_recommend !== false ? "bg-emerald-600 text-white" : "bg-slate-100 text-slate-500"}`}>
                                Oui
                              </button>
                              <button onClick={() => updateEval(evt.title, "would_recommend", false)}
                                className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors ${(evalForms[evt.title] || {}).would_recommend === false ? "bg-red-500 text-white" : "bg-slate-100 text-slate-500"}`}>
                                Non
                              </button>
                            </div>
                          </div>
                          <Textarea placeholder="Commentaire (optionnel)" rows={2} className="text-xs"
                            value={(evalForms[evt.title] || {}).comment || ""}
                            onChange={(e) => updateEval(evt.title, "comment", e.target.value)} data-testid={`eval-comment-${i}`} />
                          <Button size="sm" onClick={() => submitEval(evt.title)} disabled={submitting === evt.title}
                            className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs" data-testid={`submit-eval-${i}`}>
                            {submitting === evt.title ? <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" /> : <CheckCircle2 className="w-3.5 h-3.5 mr-1" />}
                            Envoyer mon évaluation
                          </Button>
                        </div>
                      )}

                      {/* Evaluation already submitted */}
                      {evt.evaluation && (
                        <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-3">
                          <p className="text-xs font-semibold text-emerald-700 flex items-center gap-1 mb-1">
                            <CheckCircle2 className="w-3.5 h-3.5" /> Évaluation envoyée
                          </p>
                          <div className="flex gap-3 text-xs text-emerald-600">
                            <span>Note : {"★".repeat(evt.evaluation.rating)}{"☆".repeat(5 - evt.evaluation.rating)}</span>
                            <span>Organisation : {evt.evaluation.organization}/5</span>
                            <span>Utilité : {evt.evaluation.usefulness}/5</span>
                          </div>
                          {evt.evaluation.comment && <p className="text-[11px] text-slate-500 mt-1 italic">"{evt.evaluation.comment}"</p>}
                        </div>
                      )}

                      {/* Not participated → Reason form */}
                      {evt.participated === false && !evt.non_participation_reason && (
                        <div className="bg-red-50 border border-red-200 rounded-lg p-3 space-y-2" data-testid={`noshow-form-${i}`}>
                          <p className="text-xs font-semibold text-red-700 flex items-center gap-1">
                            <AlertTriangle className="w-3.5 h-3.5" /> Motif de non-participation
                          </p>
                          <Select value={(noShowForms[evt.title] || {}).reason || ""} onValueChange={(v) => updateNoShow(evt.title, "reason", v)}>
                            <SelectTrigger className="text-xs h-8" data-testid={`noshow-reason-${i}`}><SelectValue placeholder="Sélectionner un motif" /></SelectTrigger>
                            <SelectContent>
                              {NO_SHOW_REASONS.map(r => <SelectItem key={r.value} value={r.value}>{r.label}</SelectItem>)}
                            </SelectContent>
                          </Select>
                          <Textarea placeholder="Détails (optionnel)" rows={2} className="text-xs"
                            value={(noShowForms[evt.title] || {}).details || ""}
                            onChange={(e) => updateNoShow(evt.title, "details", e.target.value)} data-testid={`noshow-details-${i}`} />
                          <Button size="sm" onClick={() => submitNoShow(evt.title)} disabled={submitting === evt.title}
                            className="bg-red-600 hover:bg-red-700 text-white text-xs" data-testid={`submit-noshow-${i}`}>
                            Enregistrer le motif
                          </Button>
                        </div>
                      )}

                      {/* Reason already submitted */}
                      {evt.non_participation_reason && (
                        <div className="bg-slate-50 border border-slate-200 rounded-lg p-3">
                          <p className="text-xs text-slate-500">
                            Motif : <span className="font-medium text-slate-700">{NO_SHOW_REASONS.find(r => r.value === evt.non_participation_reason.reason)?.label || evt.non_participation_reason.reason}</span>
                          </p>
                          {evt.non_participation_reason.details && <p className="text-[11px] text-slate-400 mt-0.5 italic">"{evt.non_participation_reason.details}"</p>}
                        </div>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

const JobDatingView = ({ token }) => {
  const [tab, setTab] = useState("discover");
  const [events, setEvents] = useState([]);
  const [recommended, setRecommended] = useState([]);
  const [savedEvents, setSavedEvents] = useState([]);
  const [savedIds, setSavedIds] = useState(new Set());
  const [registeredIds, setRegisteredIds] = useState(new Set());
  const [sectors, setSectors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingRecommended, setLoadingRecommended] = useState(false);
  const [aiSummary, setAiSummary] = useState(null);
  const [searchQ, setSearchQ] = useState("");
  const [filterPeriod, setFilterPeriod] = useState("");
  const [filterMode, setFilterMode] = useState("");
  const [matchingNotifs, setMatchingNotifs] = useState([]);
  const [bannerDismissed, setBannerDismissed] = useState(false);
  const [searching, setSearching] = useState(false);
  const [webSearchResults, setWebSearchResults] = useState([]);
  const [webSearching, setWebSearching] = useState(false);
  const [webSearchCity, setWebSearchCity] = useState("");
  const [recoCity, setRecoCity] = useState("");
  const [recoCityInput, setRecoCityInput] = useState("");

  useEffect(() => {
    if (!token) return;
    let cancelled = false;

    const loadData = async () => {
      setLoading(true);
      try {
        const [eventsRes, sectorsRes] = await Promise.all([
          axios.get(`${API}/jobdating/events`, { params: { token }, timeout: 15000 }),
          axios.get(`${API}/jobdating/sectors`, { timeout: 15000 }),
        ]);
        if (cancelled) return;
        setEvents(eventsRes.data?.events || []);
        setSectors(sectorsRes.data?.sectors || []);
      } catch (e) {
        console.error("Job dating load error:", e);
        if (!cancelled) toast.error("Erreur de chargement des événements");
      } finally {
        if (!cancelled) setLoading(false);
      }

      // Secondary data + notifications (non-blocking)
      try {
        const [savedRes, regRes, notifsRes] = await Promise.all([
          axios.get(`${API}/jobdating/saved`, { params: { token }, timeout: 15000 }).catch(() => ({ data: {} })),
          axios.get(`${API}/jobdating/registrations`, { params: { token }, timeout: 15000 }).catch(() => ({ data: {} })),
          axios.get(`${API}/notifications`, { params: { token, unread_only: true }, timeout: 10000 }).catch(() => ({ data: {} })),
        ]);
        if (cancelled) return;
        const saved = savedRes.data?.events || [];
        setSavedEvents(saved);
        setSavedIds(new Set(saved.map(e => e.event_id || e.title)));
        setRegisteredIds(new Set((regRes.data?.registrations || []).map(r => r.event_id)));
        const unreadNotifs = (notifsRes.data?.notifications || []).filter(n => n.type === "job_dating_new");
        setMatchingNotifs(unreadNotifs);
      } catch (_) {}

      // AI Recommendations (separate, may be slow)
      try {
        setLoadingRecommended(true);
        const recRes = await axios.get(`${API}/jobdating/recommended`, { params: { token }, timeout: 30000 });
        if (cancelled) return;
        setRecommended(recRes.data?.events || []);
        setAiSummary(recRes.data?.ai_summary || null);
      } catch (_) {
      } finally {
        if (!cancelled) setLoadingRecommended(false);
      }
    };

    loadData();
    return () => { cancelled = true; };
  }, [token]);

  // Reload recommendations with a specific city
  const loadRecoForCity = async (city) => {
    if (!token || !city.trim()) return;
    setLoadingRecommended(true);
    setRecommended([]);
    setWebSearchResults([]);
    setRecoCity(city.trim());
    try {
      // First get recommended from existing events
      const recRes = await axios.get(`${API}/jobdating/recommended`, { params: { token, city: city.trim() }, timeout: 30000 });
      setRecommended(recRes.data?.events || []);
      setAiSummary(recRes.data?.ai_summary || null);
      // Then search web for more events in this city
      setWebSearching(true);
      const webRes = await axios.get(`${API}/jobdating/web-search`, { params: { token, city: city.trim() }, timeout: 60000 });
      setWebSearchResults(webRes.data?.events || []);
    } catch (_) {
      toast.error("Erreur de recherche");
    } finally {
      setLoadingRecommended(false);
      setWebSearching(false);
    }
  };

  const handleSave = async (event) => {
    const eid = event.id || event.title;
    try {
      if (savedIds.has(eid)) {
        await axios.delete(`${API}/jobdating/events/${encodeURIComponent(eid)}/save`, { params: { token } });
        setSavedIds(prev => { const s = new Set(prev); s.delete(eid); return s; });
        toast.info("Événement retiré des favoris");
      } else {
        await axios.post(`${API}/jobdating/events/${encodeURIComponent(eid)}/save`, null, { params: { token } });
        setSavedIds(prev => new Set(prev).add(eid));
        toast.success("Événement sauvegardé !");
      }
    } catch (e) {
      toast.error("Erreur lors de la sauvegarde");
    }
  };

  const handleRegister = async (event) => {
    const eid = event.id || event.title;
    if (registeredIds.has(eid)) return;
    try {
      await axios.post(`${API}/jobdating/events/${encodeURIComponent(eid)}/register`, null, { params: { token } });
      setRegisteredIds(prev => new Set(prev).add(eid));
      toast.success("Inscription confirmée !");
    } catch (e) {
      toast.error("Erreur lors de l'inscription");
    }
  };

  const handleRefresh = () => {
    toast.info("Actualisation en cours...");
    if (!token) return;
    setLoading(true);
    Promise.all([
      axios.get(`${API}/jobdating/events`, { params: { token }, timeout: 15000 }),
      axios.get(`${API}/jobdating/sectors`, { timeout: 15000 }),
    ]).then(([eventsRes, sectorsRes]) => {
      setEvents(eventsRes.data?.events || []);
      setSectors(sectorsRes.data?.sectors || []);
    }).catch(() => {
      toast.error("Erreur de chargement");
    }).finally(() => {
      setLoading(false);
    });
  };

  const handleSearch = async () => {
    if (!token) return;
    setSearching(true);
    setWebSearchResults([]);
    setWebSearchCity("");
    try {
      const params = { token };
      if (searchQ.trim()) params.q = searchQ.trim();
      if (filterPeriod && filterPeriod !== "all") params.days = filterPeriod;
      if (filterMode && filterMode !== "all") params.mode = filterMode;
      const res = await axios.get(`${API}/jobdating/events`, { params, timeout: 15000 });
      const localEvents = res.data?.events || [];
      setEvents(localEvents);

      // If few local results and search looks like a city, launch IA web search
      const q = (searchQ || "").trim();
      if (q && localEvents.length < 5) {
        setWebSearching(true);
        setWebSearchCity(q);
        try {
          const webRes = await axios.get(`${API}/jobdating/web-search`, { params: { token, city: q }, timeout: 60000 });
          setWebSearchResults(webRes.data?.events || []);
        } catch { /* silent */ }
        setWebSearching(false);
      }
    } catch {
      toast.error("Erreur de recherche");
    } finally {
      setSearching(false);
    }
  };

  const filteredEvents = events.filter(e => {
    if (searchQ) {
      const q = searchQ.toLowerCase();
      const match = e.title?.toLowerCase().includes(q) ||
        (e.jobs_targeted || []).some(j => j.toLowerCase().includes(q)) ||
        e.city?.toLowerCase().includes(q) ||
        e.description?.toLowerCase().includes(q) ||
        e.postal_code?.startsWith(q) ||
        (e.sectors || []).some(s => s.toLowerCase().includes(q)) ||
        e.address?.toLowerCase().includes(q);
      if (!match) return false;
    }
    if (filterPeriod && filterPeriod !== "all") {
      const days = parseInt(filterPeriod);
      const cutoff = new Date(Date.now() + days * 86400000).toISOString();
      if (e.start_datetime > cutoff) return false;
    }
    if (filterMode && filterMode !== "all" && e.mode !== filterMode) return false;
    return true;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-[#1e3a5f]" />
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="jobdating-view">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#1e3a5f] to-[#4f6df5] flex items-center justify-center">
              <CalendarDays className="w-5 h-5 text-white" />
            </div>
            Job Dating
          </h2>
          <p className="text-sm text-slate-500 mt-1">
            {events.length} événements de {new Set(events.map(e => e.source || "france_travail")).size} sources
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => window.open("https://mesevenementsemploi.francetravail.fr/mes-evenements-emploi/evenements", "_blank")}
            data-testid="browse-all-ft-btn"
            className="text-sky-700 border-sky-200 hover:bg-sky-50"
          >
            <Globe className="w-4 h-4 mr-1" />Tous les événements
          </Button>
          <Button variant="outline" size="sm" onClick={handleRefresh} data-testid="refresh-jobdating-btn">
            <RefreshCw className="w-4 h-4 mr-1" />Actualiser
          </Button>
        </div>
      </div>

      {/* Matching Notifications Banner */}
      {matchingNotifs.length > 0 && !bannerDismissed && (
        <div className="relative bg-gradient-to-r from-emerald-50 via-blue-50 to-violet-50 border border-emerald-200 rounded-xl p-4" data-testid="matching-banner">
          <button
            onClick={() => setBannerDismissed(true)}
            className="absolute top-2 right-2 text-slate-400 hover:text-slate-600 p-1"
            data-testid="dismiss-banner"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
          </button>
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-blue-500 flex items-center justify-center shrink-0">
              <Target className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-bold text-slate-900">
                {matchingNotifs.length} nouveau{matchingNotifs.length > 1 ? "x" : ""} Job Dating{matchingNotifs.length > 1 ? "s" : ""} correspond{matchingNotifs.length > 1 ? "ent" : ""} à votre profil !
              </p>
              <div className="flex flex-wrap gap-2 mt-2">
                {matchingNotifs.slice(0, 3).map((n, i) => (
                  <Badge
                    key={i}
                    className={`text-[11px] cursor-pointer hover:opacity-80 ${
                      n.match_level === "fort" ? "bg-emerald-100 text-emerald-700 border-emerald-200" :
                      n.match_level === "moyen" ? "bg-blue-100 text-blue-700 border-blue-200" :
                      "bg-slate-100 text-slate-600 border-slate-200"
                    }`}
                    data-testid={`matching-badge-${i}`}
                  >
                    <Target className="w-3 h-3 mr-1" />{n.match_score}% — {n.event_title}
                  </Badge>
                ))}
                {matchingNotifs.length > 3 && (
                  <Badge className="bg-slate-100 text-slate-500 text-[11px]">
                    +{matchingNotifs.length - 3} autres
                  </Badge>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      <Tabs value={tab} onValueChange={setTab}>
        <TabsList className="bg-slate-100">
          <TabsTrigger value="discover" data-testid="tab-discover">
            <Search className="w-3.5 h-3.5 mr-1" />Découvrir
          </TabsTrigger>
          <TabsTrigger value="recommended" data-testid="tab-recommended">
            <Sparkles className="w-3.5 h-3.5 mr-1" />Recommandés
          </TabsTrigger>
          <TabsTrigger value="saved" data-testid="tab-saved">
            <Bookmark className="w-3.5 h-3.5 mr-1" />Sauvegardés ({savedIds.size})
          </TabsTrigger>
          <TabsTrigger value="history" data-testid="tab-history">
            <History className="w-3.5 h-3.5 mr-1" />Historique ({registeredIds.size})
          </TabsTrigger>
        </TabsList>

        {/* ── Discover Tab ── */}
        <TabsContent value="discover" className="space-y-4">
          {/* Search & Filters */}
          <Card className="border-slate-200">
            <CardContent className="p-4">
              <div className="flex flex-col md:flex-row gap-3">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <Input
                    placeholder="Rechercher un métier, une ville..."
                    value={searchQ}
                    onChange={(e) => setSearchQ(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                    className="pl-9"
                    data-testid="search-input"
                  />
                </div>
                <Button
                  onClick={handleSearch}
                  disabled={searching}
                  data-testid="search-btn"
                  className="bg-[#1e3a5f] hover:bg-[#2a4a6f] text-white"
                >
                  {searching ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : <Search className="w-4 h-4 mr-1" />}
                  Rechercher
                </Button>
                <Select value={filterPeriod} onValueChange={(val) => { setFilterPeriod(val); }}>
                  <SelectTrigger className="w-full md:w-[180px]" data-testid="filter-period">
                    <Clock className="w-3.5 h-3.5 mr-1" />
                    <SelectValue placeholder="Période" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Toutes les dates</SelectItem>
                    <SelectItem value="7">1 semaine</SelectItem>
                    <SelectItem value="15">15 jours</SelectItem>
                    <SelectItem value="30">1 mois</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={filterMode} onValueChange={setFilterMode}>
                  <SelectTrigger className="w-full md:w-[160px]" data-testid="filter-mode">
                    <SelectValue placeholder="Format" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Tous formats</SelectItem>
                    <SelectItem value="presentiel">Présentiel</SelectItem>
                    <SelectItem value="distanciel">En ligne</SelectItem>
                    <SelectItem value="hybride">Hybride</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* Quick stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="bg-red-50 border border-red-100 rounded-xl p-3 text-center">
              <Zap className="w-5 h-5 text-red-500 mx-auto mb-1" />
              <p className="text-xl font-black text-red-700">{events.filter(e => e.is_urgent).length}</p>
              <p className="text-[10px] text-red-500 font-medium">Dans 3 jours</p>
            </div>
            <div className="bg-amber-50 border border-amber-100 rounded-xl p-3 text-center">
              <Clock className="w-5 h-5 text-amber-500 mx-auto mb-1" />
              <p className="text-xl font-black text-amber-700">{events.filter(e => e.is_soon).length}</p>
              <p className="text-[10px] text-amber-500 font-medium">Cette semaine</p>
            </div>
            <div className="bg-blue-50 border border-blue-100 rounded-xl p-3 text-center">
              <Building2 className="w-5 h-5 text-blue-500 mx-auto mb-1" />
              <p className="text-xl font-black text-blue-700">{events.reduce((s, e) => s + (e.companies_count || 0), 0)}</p>
              <p className="text-[10px] text-blue-500 font-medium">Entreprises</p>
            </div>
            <div className="bg-emerald-50 border border-emerald-100 rounded-xl p-3 text-center">
              <Briefcase className="w-5 h-5 text-emerald-500 mx-auto mb-1" />
              <p className="text-xl font-black text-emerald-700">{events.reduce((s, e) => s + (e.positions_count || 0), 0)}</p>
              <p className="text-[10px] text-emerald-500 font-medium">Postes à pourvoir</p>
            </div>
          </div>

          {/* Events list */}
          <div className="space-y-3">
            {filteredEvents.length === 0 ? (
              <Card className="border-dashed border-2 border-slate-200">
                <CardContent className="p-8 text-center">
                  <Search className="w-8 h-8 text-slate-300 mx-auto mb-2" />
                  <p className="text-sm text-slate-500 mb-3">Aucun événement trouvé pour ces critères</p>
                  {searchQ.trim() && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => window.open(`https://mesevenementsemploi.francetravail.fr/mes-evenements-emploi/evenements`, "_blank")}
                      className="text-sky-700 border-sky-200 hover:bg-sky-50"
                      data-testid="ft-search-link"
                    >
                      <Globe className="w-4 h-4 mr-1" />Rechercher sur France Travail
                    </Button>
                  )}
                </CardContent>
              </Card>
            ) : (
              <>
                {filteredEvents.map((e, i) => (
                  <EventCard
                    key={i}
                    event={e}
                    saved={savedIds.has(e.id || e.title)}
                    registered={registeredIds.has(e.id || e.title)}
                    onSave={handleSave}
                    onRegister={handleRegister}
                  />
                ))}
                {searchQ.trim() && filteredEvents.length <= 5 && (
                  <Card className="border-sky-200 bg-sky-50/50">
                    <CardContent className="p-4">
                      {webSearching ? (
                        <div className="flex items-center justify-center gap-2 py-3">
                          <Loader2 className="w-4 h-4 animate-spin text-indigo-600" />
                          <p className="text-sm text-indigo-600">Recherche IA d'événements emploi à {searchQ}...</p>
                        </div>
                      ) : webSearchResults.length > 0 ? (
                        <div className="space-y-3">
                          <div className="flex items-center gap-2 mb-2">
                            <Brain className="w-4 h-4 text-indigo-600" />
                            <p className="text-sm font-semibold text-indigo-800">
                              {webSearchResults.length} événements trouvés par l'IA à {webSearchCity}
                            </p>
                            <Badge className="text-[9px] bg-indigo-100 text-indigo-700">Recherche web IA</Badge>
                          </div>
                          <div className="grid gap-2">
                            {webSearchResults.map((e, i) => (
                              <div key={i} className="bg-white rounded-lg border border-indigo-100 p-3 hover:border-indigo-300 transition" data-testid={`web-event-${i}`}>
                                <div className="flex items-start justify-between gap-2">
                                  <div className="flex-1 min-w-0">
                                    <p className="text-sm font-semibold text-slate-800">{e.title}</p>
                                    <div className="flex items-center gap-2 mt-1 text-[10px] text-slate-500 flex-wrap">
                                      <span className="flex items-center gap-0.5"><MapPin className="w-3 h-3" />{e.city}{e.address ? ` — ${e.address}` : ''}</span>
                                      {e.start_datetime && <span className="flex items-center gap-0.5"><CalendarDays className="w-3 h-3" />{new Date(e.start_datetime).toLocaleDateString('fr-FR', {day: 'numeric', month: 'short', year: 'numeric'})}</span>}
                                      {e.organizer && <span className="text-indigo-600">{e.organizer}</span>}
                                    </div>
                                    {e.description && <p className="text-[10px] text-slate-500 mt-1 line-clamp-2">{e.description}</p>}
                                    <div className="flex flex-wrap gap-1 mt-1.5">
                                      {(e.sectors || []).map((s, j) => <Badge key={j} variant="outline" className="text-[8px] text-indigo-600 border-indigo-200">{s}</Badge>)}
                                      {(e.jobs_targeted || []).slice(0, 3).map((j, k) => <Badge key={k} className="text-[8px] bg-slate-100 text-slate-600">{j}</Badge>)}
                                    </div>
                                  </div>
                                  <Badge className="text-[8px] bg-indigo-50 text-indigo-600 border border-indigo-200 shrink-0">{e.event_type || 'forum'}</Badge>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      ) : (
                        <div className="text-center py-2">
                          <p className="text-sm text-sky-700 mb-2">
                            {filteredEvents.length} résultat{filteredEvents.length > 1 ? 's' : ''} trouvé{filteredEvents.length > 1 ? 's' : ''}. Consultez plus d'événements :
                          </p>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => window.open(`https://mesevenementsemploi.francetravail.fr/mes-evenements-emploi/evenements`, "_blank")}
                            className="text-sky-700 border-sky-200 hover:bg-sky-50"
                            data-testid="ft-more-link"
                          >
                            <Globe className="w-4 h-4 mr-1" />Voir tous les événements sur France Travail
                          </Button>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                )}
              </>
            )}
          </div>
        </TabsContent>

        {/* ── Recommended Tab ── */}
        <TabsContent value="recommended" className="space-y-4">
          {/* City input + AI Summary */}
          <Card className="border-indigo-200 bg-gradient-to-r from-indigo-50 via-purple-50 to-blue-50">
            <CardContent className="p-4">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shrink-0">
                  <Brain className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1 min-w-0 space-y-2">
                  <p className="text-sm font-bold text-slate-900 flex items-center gap-1.5">
                    Recommandations IA
                    <Badge className="text-[10px] bg-indigo-100 text-indigo-700">Personnalisé</Badge>
                    {recoCity && <Badge className="text-[10px] bg-emerald-100 text-emerald-700">{recoCity}</Badge>}
                  </p>
                  <div className="flex items-center gap-2">
                    <div className="flex items-center gap-1.5 flex-1 max-w-sm">
                      <MapPin className="w-4 h-4 text-indigo-400 shrink-0" />
                      <input
                        type="text"
                        value={recoCityInput}
                        onChange={e => setRecoCityInput(e.target.value)}
                        onKeyDown={e => { if (e.key === "Enter" && recoCityInput.trim()) loadRecoForCity(recoCityInput); }}
                        placeholder="Votre ville (ex: Strasbourg, Lyon...)"
                        className="flex-1 h-8 text-xs border border-indigo-200 rounded-lg px-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-300 bg-white"
                        data-testid="reco-city-input"
                      />
                    </div>
                    <Button
                      size="sm"
                      className="h-8 text-xs bg-indigo-600 hover:bg-indigo-700"
                      onClick={() => recoCityInput.trim() && loadRecoForCity(recoCityInput)}
                      disabled={loadingRecommended || !recoCityInput.trim()}
                      data-testid="reco-city-btn"
                    >
                      {loadingRecommended ? <Loader2 className="w-3 h-3 animate-spin mr-1" /> : <Search className="w-3 h-3 mr-1" />}
                      Rechercher
                    </Button>
                  </div>
                  {loadingRecommended ? (
                    <p className="text-xs text-indigo-600 flex items-center gap-1.5">
                      <Loader2 className="w-3 h-3 animate-spin" />
                      Recherche d'événements à {recoCityInput || recoCity}...
                    </p>
                  ) : aiSummary ? (
                    <p className="text-xs text-slate-600 leading-relaxed">{aiSummary}</p>
                  ) : (
                    <p className="text-xs text-slate-500">Saisissez votre ville pour des recommandations locales basées sur votre profil</p>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Partner events highlight */}
          {recommended.filter(e => e.is_partner_event).length > 0 && (
            <div className="flex items-center gap-2 px-1" data-testid="partner-events-info">
              <Handshake className="w-4 h-4 text-purple-500" />
              <p className="text-xs text-slate-600">
                <span className="font-semibold text-purple-700">{recommended.filter(e => e.is_partner_event).length}</span> événement{recommended.filter(e => e.is_partner_event).length > 1 ? "s" : ""} proposé{recommended.filter(e => e.is_partner_event).length > 1 ? "s" : ""} par vos partenaires
                {recommended.filter(e => e.has_profile_access).length > 0 && (
                  <span className="text-amber-700 font-semibold ml-1">
                    dont {recommended.filter(e => e.has_profile_access).length} avec accès à votre profil
                  </span>
                )}
              </p>
            </div>
          )}

          {loadingRecommended ? (
            <div className="flex flex-col items-center justify-center py-10 gap-3">
              <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
              <p className="text-sm text-slate-500">Génération des recommandations personnalisées...</p>
            </div>
          ) : recommended.length === 0 ? (
            <Card className="border-dashed border-2 border-slate-200">
              <CardContent className="p-8 text-center">
                <Target className="w-8 h-8 text-slate-300 mx-auto mb-2" />
                <p className="text-sm text-slate-500">Enrichissez votre profil pour recevoir des recommandations personnalisées</p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-3">
              {recommended.map((e, i) => (
                <EventCard
                  key={i}
                  event={e}
                  saved={savedIds.has(e.id || e.title)}
                  registered={registeredIds.has(e.id || e.title)}
                  onSave={handleSave}
                  onRegister={handleRegister}
                  showAiReason={true}
                />
              ))}
            </div>
          )}

          {/* Web search results for city */}
          {recoCity && webSearchResults.length > 0 && (
            <Card className="border-sky-200 bg-sky-50/50">
              <CardContent className="p-4 space-y-3">
                <div className="flex items-center gap-2">
                  <Brain className="w-4 h-4 text-indigo-600" />
                  <p className="text-sm font-semibold text-indigo-800">{webSearchResults.length} événements trouvés par l'IA à {recoCity}</p>
                  <Badge className="text-[9px] bg-indigo-100 text-indigo-700">Recherche web IA</Badge>
                </div>
                <div className="grid gap-2">
                  {webSearchResults.map((e, i) => (
                    <div key={i} className="bg-white rounded-lg border border-indigo-100 p-3 hover:border-indigo-300 transition">
                      <p className="text-sm font-semibold text-slate-800">{e.title}</p>
                      <div className="flex items-center gap-2 mt-1 text-[10px] text-slate-500 flex-wrap">
                        <span className="flex items-center gap-0.5"><MapPin className="w-3 h-3" />{e.city}{e.address ? ` — ${e.address}` : ''}</span>
                        {e.start_datetime && <span><CalendarDays className="w-3 h-3 inline mr-0.5" />{new Date(e.start_datetime).toLocaleDateString('fr-FR', {day: 'numeric', month: 'short', year: 'numeric'})}</span>}
                        {e.organizer && <span className="text-indigo-600">{e.organizer}</span>}
                      </div>
                      {e.description && <p className="text-[10px] text-slate-500 mt-1 line-clamp-2">{e.description}</p>}
                      <div className="flex flex-wrap gap-1 mt-1.5">
                        {(e.sectors || []).map((s, j) => <Badge key={j} variant="outline" className="text-[8px] text-indigo-600 border-indigo-200">{s}</Badge>)}
                        {(e.jobs_targeted || []).slice(0, 3).map((j, k) => <Badge key={k} className="text-[8px] bg-slate-100 text-slate-600">{j}</Badge>)}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
          {recoCity && webSearching && (
            <div className="flex items-center justify-center gap-2 py-4">
              <Loader2 className="w-4 h-4 animate-spin text-indigo-600" />
              <p className="text-sm text-indigo-600">Recherche d'événements supplémentaires à {recoCity}...</p>
            </div>
          )}
        </TabsContent>

        {/* ── Saved Tab ── */}
        <TabsContent value="saved" className="space-y-4">
          {savedIds.size === 0 ? (
            <Card className="border-dashed border-2 border-slate-200">
              <CardContent className="p-8 text-center">
                <Bookmark className="w-8 h-8 text-slate-300 mx-auto mb-2" />
                <p className="text-sm text-slate-500">Aucun événement sauvegardé</p>
                <p className="text-xs text-slate-400 mt-1">Cliquez sur le signet pour sauvegarder un événement</p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-3">
              {events.filter(e => savedIds.has(e.id || e.title)).map((e, i) => (
                <EventCard
                  key={i}
                  event={e}
                  saved={true}
                  registered={registeredIds.has(e.id || e.title)}
                  onSave={handleSave}
                  onRegister={handleRegister}
                />
              ))}
            </div>
          )}
        </TabsContent>

        {/* ── History Tab ── */}
        <TabsContent value="history" className="space-y-4">
          <HistoryPanel token={token} />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default JobDatingView;
