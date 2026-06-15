import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import {
  Plus, Trash2, CalendarDays, MapPin, Briefcase, Building2,
  Monitor, Globe, Clock, Loader2, Users, Eye, Pencil, AlertTriangle,
  Star, ChevronDown, ChevronUp, UserCheck, ThumbsUp, ThumbsDown,
  MessageSquare, BarChart3
} from "lucide-react";
import { toast } from "sonner";

const EVENT_TYPES = [
  { value: "job_dating", label: "Job Dating" },
  { value: "e_job_dating", label: "E-Job Dating" },
  { value: "forum", label: "Forum Emploi" },
  { value: "recrutement_collectif", label: "Recrutement Collectif" },
  { value: "salon_emploi", label: "Salon Emploi" },
];

const MODES = [
  { value: "presentiel", label: "Présentiel" },
  { value: "distanciel", label: "En ligne" },
  { value: "hybride", label: "Hybride" },
];

const TYPE_COLORS = {
  job_dating: "bg-blue-100 text-blue-700",
  e_job_dating: "bg-violet-100 text-violet-700",
  forum: "bg-amber-100 text-amber-700",
  recrutement_collectif: "bg-emerald-100 text-emerald-700",
  salon_emploi: "bg-rose-100 text-rose-700",
};

const MODE_ICONS = { presentiel: MapPin, distanciel: Monitor, hybride: Globe };

const INITIAL_FORM = {
  title: "",
  description: "",
  event_type: "job_dating",
  start_datetime: "",
  end_datetime: "",
  mode: "presentiel",
  address: "",
  city: "",
  postal_code: "",
  registration_url: "",
  positions_count: 0,
  companies_count: 0,
  sectors: [],
  jobs_targeted: [],
  audience: "tout_public",
  experience_level: "",
  companies_list: [],
};

const PartenaireJobDating = ({ token }) => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);
  const [deleting, setDeleting] = useState(null);
  const [form, setForm] = useState({ ...INITIAL_FORM });
  const [submitting, setSubmitting] = useState(false);
  const [jobsInput, setJobsInput] = useState("");
  const [sectorsInput, setSectorsInput] = useState("");
  const [companiesInput, setCompaniesInput] = useState("");
  const [detailOpen, setDetailOpen] = useState(false);
  const [detailData, setDetailData] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const loadEvents = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/jobdating/partner/events`, { params: { token }, timeout: 15000 });
      setEvents(res.data?.events || []);
    } catch (e) {
      console.error("Erreur chargement événements:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { if (token) loadEvents(); }, [token]);

  const handleCreate = async () => {
    if (!form.title.trim()) { toast.error("Le titre est obligatoire"); return; }
    if (!form.start_datetime) { toast.error("La date de début est obligatoire"); return; }
    if (!form.city.trim()) { toast.error("La ville est obligatoire"); return; }

    setSubmitting(true);
    try {
      const payload = {
        ...form,
        start_datetime: new Date(form.start_datetime).toISOString(),
        end_datetime: form.end_datetime ? new Date(form.end_datetime).toISOString() : "",
        jobs_targeted: jobsInput ? jobsInput.split(",").map(j => j.trim()).filter(Boolean) : [],
        sectors: sectorsInput ? sectorsInput.split(",").map(s => s.trim()).filter(Boolean) : [],
        companies_list: companiesInput ? companiesInput.split(",").map(c => ({ name: c.trim(), positions: 0 })).filter(c => c.name) : [],
        companies_count: companiesInput ? companiesInput.split(",").filter(c => c.trim()).length : form.companies_count,
      };
      await axios.post(`${API}/jobdating/partner/events`, payload, { params: { token } });
      toast.success("Événement créé avec succès !");
      setCreateOpen(false);
      setForm({ ...INITIAL_FORM });
      setJobsInput("");
      setSectorsInput("");
      setCompaniesInput("");
      loadEvents();
    } catch (e) {
      toast.error(e.response?.data?.detail || "Erreur lors de la création");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (eventTitle) => {
    setDeleting(eventTitle);
    try {
      await axios.delete(`${API}/jobdating/partner/events/${encodeURIComponent(eventTitle)}`, { params: { token } });
      toast.success("Événement supprimé");
      loadEvents();
    } catch (e) {
      toast.error("Erreur lors de la suppression");
    } finally {
      setDeleting(null);
    }
  };

  const loadDetail = async (eventTitle) => {
    setDetailLoading(true);
    setDetailOpen(true);
    try {
      const res = await axios.get(`${API}/jobdating/partner/events/${encodeURIComponent(eventTitle)}/details`, { params: { token }, timeout: 15000 });
      setDetailData(res.data);
    } catch (e) {
      toast.error("Erreur chargement détails");
      setDetailOpen(false);
    } finally {
      setDetailLoading(false);
    }
  };

  const formatDate = (iso) => {
    if (!iso) return "—";
    try {
      return new Date(iso).toLocaleDateString("fr-FR", { weekday: "short", day: "numeric", month: "long", hour: "2-digit", minute: "2-digit" });
    } catch { return iso; }
  };

  return (
    <div className="space-y-4" data-testid="partenaire-jobdating">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
            <CalendarDays className="w-5 h-5 text-[#1e3a5f]" />
            Gestion des événements Job Dating
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Les événements créés sont automatiquement visibles par les bénéficiaires
          </p>
        </div>
        <Button onClick={() => setCreateOpen(true)} className="bg-[#1e3a5f] hover:bg-[#2d5a8f]" data-testid="create-event-btn">
          <Plus className="w-4 h-4 mr-1.5" /> Créer un événement
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <div className="bg-blue-50 border border-blue-100 rounded-xl p-3 text-center">
          <CalendarDays className="w-5 h-5 text-blue-500 mx-auto mb-1" />
          <p className="text-xl font-black text-blue-700">{events.length}</p>
          <p className="text-[10px] text-blue-500 font-medium">Événements</p>
        </div>
        <div className="bg-emerald-50 border border-emerald-100 rounded-xl p-3 text-center">
          <Briefcase className="w-5 h-5 text-emerald-500 mx-auto mb-1" />
          <p className="text-xl font-black text-emerald-700">{events.reduce((s, e) => s + (e.positions_count || 0), 0)}</p>
          <p className="text-[10px] text-emerald-500 font-medium">Postes proposés</p>
        </div>
        <div className="bg-violet-50 border border-violet-100 rounded-xl p-3 text-center">
          <UserCheck className="w-5 h-5 text-violet-500 mx-auto mb-1" />
          <p className="text-xl font-black text-violet-700">{events.reduce((s, e) => s + (e.stats?.total_registered || 0), 0)}</p>
          <p className="text-[10px] text-violet-500 font-medium">Inscrits</p>
        </div>
        <div className="bg-amber-50 border border-amber-100 rounded-xl p-3 text-center">
          <ThumbsUp className="w-5 h-5 text-amber-500 mx-auto mb-1" />
          <p className="text-xl font-black text-amber-700">{events.reduce((s, e) => s + (e.stats?.participated || 0), 0)}</p>
          <p className="text-[10px] text-amber-500 font-medium">Participations</p>
        </div>
        <div className="bg-rose-50 border border-rose-100 rounded-xl p-3 text-center">
          <Star className="w-5 h-5 text-rose-500 mx-auto mb-1" />
          <p className="text-xl font-black text-rose-700">
            {(() => {
              const ratings = events.filter(e => e.stats?.avg_rating).map(e => e.stats.avg_rating);
              return ratings.length > 0 ? (ratings.reduce((a, b) => a + b, 0) / ratings.length).toFixed(1) : "—";
            })()}
          </p>
          <p className="text-[10px] text-rose-500 font-medium">Note moyenne</p>
        </div>
      </div>

      {/* Events List */}
      {loading ? (
        <div className="flex items-center justify-center py-10">
          <Loader2 className="w-6 h-6 animate-spin text-[#1e3a5f]" />
        </div>
      ) : events.length === 0 ? (
        <Card className="border-dashed border-2 border-slate-200">
          <CardContent className="py-10 text-center">
            <CalendarDays className="w-10 h-10 text-slate-300 mx-auto mb-3" />
            <p className="text-sm text-slate-500 font-medium">Aucun événement créé</p>
            <p className="text-xs text-slate-400 mt-1">Créez votre premier événement Job Dating pour vos bénéficiaires</p>
            <Button onClick={() => setCreateOpen(true)} className="mt-4 bg-[#1e3a5f] hover:bg-[#2d5a8f]" data-testid="create-event-empty-btn">
              <Plus className="w-4 h-4 mr-1.5" /> Créer un événement
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {events.map((event, i) => {
            const ModeIcon = MODE_ICONS[event.mode] || MapPin;
            return (
              <Card key={i} className="border-slate-200 hover:shadow-sm transition-shadow" data-testid={`partner-event-${i}`}>
                <CardContent className="p-4">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1.5">
                        <h4 className="text-sm font-bold text-slate-900">{event.title}</h4>
                        <Badge className={`text-[10px] ${TYPE_COLORS[event.event_type] || "bg-slate-100 text-slate-600"}`}>
                          {EVENT_TYPES.find(t => t.value === event.event_type)?.label || event.event_type}
                        </Badge>
                        <Badge className={`text-[10px] ${event.status === "published" ? "bg-green-100 text-green-700" : "bg-slate-100 text-slate-600"}`}>
                          {event.status === "published" ? "Publié" : event.status}
                        </Badge>
                      </div>
                      {event.description && (
                        <p className="text-xs text-slate-500 line-clamp-2 mb-2">{event.description}</p>
                      )}
                      <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500">
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" /> {formatDate(event.start_datetime)}
                        </span>
                        <span className="flex items-center gap-1">
                          <ModeIcon className="w-3 h-3" /> {MODES.find(m => m.value === event.mode)?.label || event.mode}
                        </span>
                        {event.city && (
                          <span className="flex items-center gap-1"><MapPin className="w-3 h-3" /> {event.city}</span>
                        )}
                      </div>

                      {/* Registration stats inline */}
                      {event.stats && event.stats.total_registered > 0 && (
                        <div className="flex flex-wrap gap-2 mt-2.5 pt-2.5 border-t border-slate-100">
                          <Badge className="text-[10px] bg-violet-50 text-violet-700 border-violet-200">
                            <UserCheck className="w-2.5 h-2.5 mr-0.5" />{event.stats.total_registered} inscrit{event.stats.total_registered > 1 ? "s" : ""}
                          </Badge>
                          {event.stats.participated > 0 && (
                            <Badge className="text-[10px] bg-emerald-50 text-emerald-700 border-emerald-200">
                              <ThumbsUp className="w-2.5 h-2.5 mr-0.5" />{event.stats.participated} participé
                            </Badge>
                          )}
                          {event.stats.evaluations_count > 0 && (
                            <Badge className="text-[10px] bg-amber-50 text-amber-700 border-amber-200">
                              <Star className="w-2.5 h-2.5 mr-0.5" />{event.stats.avg_rating}/5 ({event.stats.evaluations_count} avis)
                            </Badge>
                          )}
                          {event.stats.not_participated > 0 && (
                            <Badge className="text-[10px] bg-red-50 text-red-600 border-red-200">
                              <ThumbsDown className="w-2.5 h-2.5 mr-0.5" />{event.stats.not_participated} absent{event.stats.not_participated > 1 ? "s" : ""}
                            </Badge>
                          )}
                        </div>
                      )}
                    </div>
                    <div className="flex flex-col gap-1.5 shrink-0">
                      {event.stats && event.stats.total_registered > 0 && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => loadDetail(event.title)}
                          className="text-[#1e3a5f] border-[#1e3a5f]/30 hover:bg-[#1e3a5f]/5 text-xs"
                          data-testid={`detail-event-${i}`}
                        >
                          <BarChart3 className="w-3.5 h-3.5 mr-1" /> Suivi
                        </Button>
                      )}
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(event.title)}
                        disabled={deleting === event.title}
                        className="text-red-500 hover:text-red-700 hover:bg-red-50"
                        data-testid={`delete-event-${i}`}
                      >
                        {deleting === event.title ? <Loader2 className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />}
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Create Event Dialog */}
      <Dialog open={createOpen} onOpenChange={setCreateOpen}>
        <DialogContent className="max-w-xl max-h-[85vh] overflow-y-auto" data-testid="create-event-dialog">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-[#1e3a5f]">
              <Plus className="w-5 h-5" /> Créer un événement Job Dating
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            {/* Title */}
            <div className="space-y-1">
              <label className="text-xs font-medium text-slate-600">Titre de l'événement *</label>
              <Input
                value={form.title}
                onChange={(e) => setForm(f => ({ ...f, title: e.target.value }))}
                placeholder="Ex: Job Dating Logistique - Strasbourg"
                data-testid="event-title-input"
              />
            </div>
            {/* Description */}
            <div className="space-y-1">
              <label className="text-xs font-medium text-slate-600">Description</label>
              <Textarea
                value={form.description}
                onChange={(e) => setForm(f => ({ ...f, description: e.target.value }))}
                placeholder="Décrivez l'événement, les postes, les conditions..."
                rows={3}
                data-testid="event-description-input"
              />
            </div>
            {/* Type + Mode */}
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-600">Type d'événement</label>
                <Select value={form.event_type} onValueChange={(v) => setForm(f => ({ ...f, event_type: v }))}>
                  <SelectTrigger data-testid="event-type-select"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {EVENT_TYPES.map(t => <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-600">Format</label>
                <Select value={form.mode} onValueChange={(v) => setForm(f => ({ ...f, mode: v }))}>
                  <SelectTrigger data-testid="event-mode-select"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {MODES.map(m => <SelectItem key={m.value} value={m.value}>{m.label}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
            </div>
            {/* Dates */}
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-600">Date et heure de début *</label>
                <Input
                  type="datetime-local"
                  value={form.start_datetime}
                  onChange={(e) => setForm(f => ({ ...f, start_datetime: e.target.value }))}
                  data-testid="event-start-input"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-600">Date et heure de fin</label>
                <Input
                  type="datetime-local"
                  value={form.end_datetime}
                  onChange={(e) => setForm(f => ({ ...f, end_datetime: e.target.value }))}
                  data-testid="event-end-input"
                />
              </div>
            </div>
            {/* Location */}
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-600">Ville *</label>
                <Input
                  value={form.city}
                  onChange={(e) => setForm(f => ({ ...f, city: e.target.value }))}
                  placeholder="Strasbourg"
                  data-testid="event-city-input"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-600">Code postal</label>
                <Input
                  value={form.postal_code}
                  onChange={(e) => setForm(f => ({ ...f, postal_code: e.target.value }))}
                  placeholder="67000"
                  data-testid="event-postal-input"
                />
              </div>
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium text-slate-600">Adresse</label>
              <Input
                value={form.address}
                onChange={(e) => setForm(f => ({ ...f, address: e.target.value }))}
                placeholder="Parc des Expositions, Hall 3"
                data-testid="event-address-input"
              />
            </div>
            {/* Counts */}
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-600">Nombre de postes</label>
                <Input
                  type="number"
                  value={form.positions_count}
                  onChange={(e) => setForm(f => ({ ...f, positions_count: parseInt(e.target.value) || 0 }))}
                  min={0}
                  data-testid="event-positions-input"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-600">Niveau d'expérience</label>
                <Input
                  value={form.experience_level}
                  onChange={(e) => setForm(f => ({ ...f, experience_level: e.target.value }))}
                  placeholder="Débutant accepté"
                  data-testid="event-experience-input"
                />
              </div>
            </div>
            {/* Jobs / Sectors / Companies */}
            <div className="space-y-1">
              <label className="text-xs font-medium text-slate-600">Métiers recherchés (séparés par des virgules)</label>
              <Input
                value={jobsInput}
                onChange={(e) => setJobsInput(e.target.value)}
                placeholder="Cariste, Préparateur de commandes, Agent logistique"
                data-testid="event-jobs-input"
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium text-slate-600">Secteurs (séparés par des virgules)</label>
              <Input
                value={sectorsInput}
                onChange={(e) => setSectorsInput(e.target.value)}
                placeholder="logistique, commerce, industrie"
                data-testid="event-sectors-input"
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium text-slate-600">Entreprises participantes (séparées par des virgules)</label>
              <Input
                value={companiesInput}
                onChange={(e) => setCompaniesInput(e.target.value)}
                placeholder="Amazon, DHL, Kuehne+Nagel"
                data-testid="event-companies-input"
              />
            </div>
            {/* URL */}
            <div className="space-y-1">
              <label className="text-xs font-medium text-slate-600">Lien d'inscription externe</label>
              <Input
                value={form.registration_url}
                onChange={(e) => setForm(f => ({ ...f, registration_url: e.target.value }))}
                placeholder="https://..."
                data-testid="event-url-input"
              />
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 text-blue-500 mt-0.5 shrink-0" />
              <p className="text-xs text-blue-700">
                L'événement sera immédiatement visible par tous les bénéficiaires dans leur espace Job Dating. La synchronisation est automatique.
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCreateOpen(false)}>Annuler</Button>
            <Button onClick={handleCreate} disabled={submitting} className="bg-[#1e3a5f] hover:bg-[#2d5a8f]" data-testid="submit-event-btn">
              {submitting ? <><Loader2 className="w-4 h-4 mr-1.5 animate-spin" /> Création...</> : <><Plus className="w-4 h-4 mr-1.5" /> Créer l'événement</>}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Detail/Stats Dialog */}
      <Dialog open={detailOpen} onOpenChange={setDetailOpen}>
        <DialogContent className="max-w-xl max-h-[85vh] overflow-y-auto" data-testid="event-detail-dialog">
          {detailLoading ? (
            <div className="flex items-center justify-center py-10">
              <Loader2 className="w-6 h-6 animate-spin text-[#1e3a5f]" />
            </div>
          ) : detailData ? (
            <>
              <DialogHeader>
                <DialogTitle className="text-[#1e3a5f] flex items-center gap-2">
                  <BarChart3 className="w-5 h-5" />
                  Suivi — {detailData.event?.title}
                </DialogTitle>
              </DialogHeader>

              {/* Summary Stats */}
              <div className="grid grid-cols-4 gap-2 my-3">
                <div className="bg-violet-50 rounded-lg p-2 text-center">
                  <p className="text-lg font-black text-violet-700">{detailData.stats?.total_registered || 0}</p>
                  <p className="text-[9px] text-violet-500">Inscrits</p>
                </div>
                <div className="bg-emerald-50 rounded-lg p-2 text-center">
                  <p className="text-lg font-black text-emerald-700">{detailData.stats?.participated || 0}</p>
                  <p className="text-[9px] text-emerald-500">Participés</p>
                </div>
                <div className="bg-red-50 rounded-lg p-2 text-center">
                  <p className="text-lg font-black text-red-600">{detailData.stats?.not_participated || 0}</p>
                  <p className="text-[9px] text-red-500">Absents</p>
                </div>
                <div className="bg-slate-50 rounded-lg p-2 text-center">
                  <p className="text-lg font-black text-slate-600">{detailData.stats?.pending || 0}</p>
                  <p className="text-[9px] text-slate-500">En attente</p>
                </div>
              </div>

              {/* Evaluation Summary */}
              {detailData.eval_summary && (
                <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 space-y-2">
                  <h4 className="text-xs font-bold text-amber-800 flex items-center gap-1.5">
                    <Star className="w-4 h-4 fill-amber-400 text-amber-400" />
                    Évaluations ({detailData.eval_summary.count} avis)
                  </h4>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <p className="text-[10px] text-amber-600">Note globale</p>
                      <p className="text-lg font-black text-amber-700">
                        {"★".repeat(Math.round(detailData.eval_summary.avg_rating))}{"☆".repeat(5 - Math.round(detailData.eval_summary.avg_rating))}
                        <span className="text-sm ml-1">{detailData.eval_summary.avg_rating}/5</span>
                      </p>
                    </div>
                    <div>
                      <p className="text-[10px] text-amber-600">Recommandation</p>
                      <p className="text-lg font-black text-amber-700">{detailData.eval_summary.recommend_pct}%</p>
                    </div>
                    <div>
                      <p className="text-[10px] text-amber-600">Organisation</p>
                      <p className="text-sm font-bold text-amber-700">{detailData.eval_summary.avg_organization}/5</p>
                    </div>
                    <div>
                      <p className="text-[10px] text-amber-600">Utilité</p>
                      <p className="text-sm font-bold text-amber-700">{detailData.eval_summary.avg_usefulness}/5</p>
                    </div>
                  </div>
                  {/* Comments */}
                  {detailData.eval_summary.comments?.length > 0 && (
                    <div className="pt-2 border-t border-amber-200">
                      <p className="text-[10px] text-amber-600 font-semibold mb-1.5 flex items-center gap-1">
                        <MessageSquare className="w-3 h-3" /> Commentaires
                      </p>
                      <div className="space-y-1.5">
                        {detailData.eval_summary.comments.map((c, i) => (
                          <div key={i} className="bg-white rounded-lg px-3 py-2 text-xs text-slate-600 italic">
                            "{c}"
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* No-show reasons */}
              {Object.keys(detailData.no_show_reasons || {}).length > 0 && (
                <div className="bg-red-50 border border-red-200 rounded-xl p-4 space-y-2">
                  <h4 className="text-xs font-bold text-red-700 flex items-center gap-1.5">
                    <ThumbsDown className="w-4 h-4" />
                    Motifs de non-participation
                  </h4>
                  <div className="space-y-1">
                    {Object.entries(detailData.no_show_reasons).map(([reason, count]) => {
                      const labels = { empechement: "Empêchement", autre_opportunite: "Autre opportunité", plus_interesse: "Plus intéressé", transport: "Transport", sante: "Santé", oubli: "Oubli", autre: "Autre" };
                      return (
                        <div key={reason} className="flex items-center justify-between bg-white rounded-lg px-3 py-1.5">
                          <span className="text-xs text-slate-600">{labels[reason] || reason}</span>
                          <Badge className="text-[10px] bg-red-100 text-red-600">{count}</Badge>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Participants list */}
              {detailData.participants?.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
                    <Users className="w-4 h-4" />
                    Participants ({detailData.participants.length})
                  </h4>
                  <div className="space-y-1.5 max-h-[200px] overflow-y-auto">
                    {detailData.participants.map((p, i) => (
                      <div key={i} className="flex items-center justify-between bg-slate-50 rounded-lg px-3 py-2" data-testid={`participant-${i}`}>
                        <div className="flex items-center gap-2">
                          <div className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold text-white ${
                            p.participated === true ? "bg-emerald-500" : p.participated === false ? "bg-red-400" : "bg-slate-400"
                          }`}>
                            {i + 1}
                          </div>
                          <div>
                            <p className="text-xs text-slate-700 font-medium">Participant #{i + 1}</p>
                            <p className="text-[10px] text-slate-400">
                              {p.city && `${p.city} · `}
                              {p.target_job && `${p.target_job} · `}
                              Inscrit le {p.registered_at ? new Date(p.registered_at).toLocaleDateString("fr-FR", { day: "numeric", month: "short" }) : "—"}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-1.5">
                          {p.participated === true && (
                            <Badge className="text-[9px] bg-emerald-100 text-emerald-700">Participé</Badge>
                          )}
                          {p.participated === false && (
                            <Badge className="text-[9px] bg-red-100 text-red-600">Absent</Badge>
                          )}
                          {p.participated === null && (
                            <Badge className="text-[9px] bg-slate-100 text-slate-500">En attente</Badge>
                          )}
                          {p.evaluation && (
                            <Badge className="text-[9px] bg-amber-100 text-amber-700">
                              {"★".repeat(p.evaluation.rating)} {p.evaluation.rating}/5
                            </Badge>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Empty state */}
              {(!detailData.participants || detailData.participants.length === 0) && (
                <div className="text-center py-6">
                  <Users className="w-8 h-8 text-slate-200 mx-auto mb-2" />
                  <p className="text-xs text-slate-400">Aucun inscrit pour le moment</p>
                </div>
              )}
            </>
          ) : null}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default PartenaireJobDating;
