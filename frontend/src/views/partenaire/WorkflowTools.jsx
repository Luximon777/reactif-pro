import React, { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";
import {
  FileText, Brain, ClipboardCheck, Target, Zap, AlertTriangle, CheckCircle2, Clock, Copy,
  Loader2, ChevronDown, ChevronUp, Download, Shield, TrendingUp, ArrowRight
} from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL + "/api";

// ===== SYNTHESE PRE-ENTRETIEN =====
export const SynthesePreEntretien = ({ beneficiaryId, token, existingSynthese }) => {
  const [synthese, setSynthese] = useState(existingSynthese || null);
  const [loading, setLoading] = useState(false);

  const generate = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${API}/partenaires/beneficiaires/${beneficiaryId}/synthese-pre-entretien?token=${token}`);
      setSynthese(res.data);
      toast.success("Synthèse pré-entretien générée");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Erreur de génération");
    }
    setLoading(false);
  };

  const urgenceColors = { immediat: "bg-red-100 text-red-700", "3_mois": "bg-orange-100 text-orange-700", "6_mois": "bg-yellow-100 text-yellow-700", non_urgent: "bg-green-100 text-green-700" };
  const autonomieColors = { fort: "bg-green-100 text-green-700", moyen: "bg-yellow-100 text-yellow-700", faible: "bg-orange-100 text-orange-700", tres_faible: "bg-red-100 text-red-700" };

  if (!synthese) {
    return (
      <Card data-testid="synthese-empty">
        <CardContent className="py-10 text-center">
          <Brain className="w-12 h-12 mx-auto mb-3 text-slate-300" />
          <p className="text-sm text-slate-500 mb-4">Générez une synthèse pré-entretien pour préparer le rendez-vous en 2 minutes</p>
          <Button onClick={generate} disabled={loading} className="bg-indigo-600 hover:bg-indigo-700" data-testid="generate-synthese-btn">
            {loading ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Analyse en cours...</> : <><Brain className="w-4 h-4 mr-2" /> Générer la synthèse</>}
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4" data-testid="synthese-content">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Badge className={urgenceColors[synthese.niveau_urgence] || "bg-slate-100"}>{synthese.niveau_urgence?.replace("_", " ")}</Badge>
          <Badge className={autonomieColors[synthese.niveau_autonomie] || "bg-slate-100"}>Autonomie: {synthese.niveau_autonomie?.replace("_", " ")}</Badge>
        </div>
        <Button variant="outline" size="sm" onClick={generate} disabled={loading} data-testid="regenerate-synthese-btn">
          {loading ? <Loader2 className="w-3 h-3 animate-spin" /> : <Brain className="w-3 h-3" />}
          <span className="ml-1">Régénérer</span>
        </Button>
      </div>

      <Card>
        <CardHeader className="pb-2"><CardTitle className="text-sm">Résumé du parcours</CardTitle></CardHeader>
        <CardContent><p className="text-sm text-slate-600">{synthese.resume_parcours}</p></CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <Card className="border-green-200">
          <CardHeader className="pb-1"><CardTitle className="text-sm text-green-700 flex items-center gap-1"><TrendingUp className="w-3.5 h-3.5" /> Points forts</CardTitle></CardHeader>
          <CardContent>{(synthese.points_forts || []).map((p, i) => <p key={i} className="text-xs text-slate-600 mb-1 flex items-start gap-1"><CheckCircle2 className="w-3 h-3 text-green-500 mt-0.5 shrink-0" /> {p}</p>)}</CardContent>
        </Card>
        <Card className="border-orange-200">
          <CardHeader className="pb-1"><CardTitle className="text-sm text-orange-700 flex items-center gap-1"><AlertTriangle className="w-3.5 h-3.5" /> Points de vigilance</CardTitle></CardHeader>
          <CardContent>{(synthese.points_vigilance || []).map((p, i) => <p key={i} className="text-xs text-slate-600 mb-1 flex items-start gap-1"><AlertTriangle className="w-3 h-3 text-orange-500 mt-0.5 shrink-0" /> {p}</p>)}</CardContent>
        </Card>
      </div>

      {synthese.freins_identifies?.length > 0 && (
        <Card className="border-red-200">
          <CardHeader className="pb-1"><CardTitle className="text-sm text-red-700">Freins identifiés</CardTitle></CardHeader>
          <CardContent>{synthese.freins_identifies.map((f, i) => <p key={i} className="text-xs text-slate-600 mb-1">- {f}</p>)}</CardContent>
        </Card>
      )}

      <Card>
        <CardHeader className="pb-1"><CardTitle className="text-sm">Hypothèse de projet</CardTitle></CardHeader>
        <CardContent><p className="text-sm text-slate-600">{synthese.hypotheses_projet}</p></CardContent>
      </Card>

      <Card className="border-indigo-200 bg-indigo-50/30">
        <CardHeader className="pb-1"><CardTitle className="text-sm text-indigo-700">Questions à explorer en entretien</CardTitle></CardHeader>
        <CardContent>{(synthese.questions_a_explorer || []).map((q, i) => <p key={i} className="text-xs text-slate-700 mb-1 font-medium">{i + 1}. {q}</p>)}</CardContent>
      </Card>

      {synthese.dispositifs_a_envisager?.length > 0 && (
        <Card>
          <CardHeader className="pb-1"><CardTitle className="text-sm">Dispositifs à envisager</CardTitle></CardHeader>
          <CardContent className="flex gap-2 flex-wrap">{synthese.dispositifs_a_envisager.map((d, i) => <Badge key={i} variant="outline" className="text-xs">{d}</Badge>)}</CardContent>
        </Card>
      )}

      {synthese.recommandation_entretien && (
        <Card className="border-blue-200 bg-blue-50/30">
          <CardHeader className="pb-1"><CardTitle className="text-sm text-blue-700">Recommandation pour l'entretien</CardTitle></CardHeader>
          <CardContent><p className="text-sm text-slate-600">{synthese.recommandation_entretien}</p></CardContent>
        </Card>
      )}
    </div>
  );
};


// ===== COMPTE RENDU =====
export const CompteRenduPanel = ({ beneficiaryId, token }) => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [expandedReport, setExpandedReport] = useState(null);
  const [form, setForm] = useState({ type_entretien: "diagnostic", notes_conseiller: "", points_abordes: "", decisions_prises: "", prochaine_etape: "" });

  useEffect(() => { loadReports(); }, [beneficiaryId]);

  const loadReports = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/partenaires/beneficiaires/${beneficiaryId}/comptes-rendus?token=${token}`);
      setReports(res.data);
    } catch { /* ignore */ }
    setLoading(false);
  };

  const generate = async () => {
    setGenerating(true);
    try {
      const payload = {
        type_entretien: form.type_entretien,
        notes_conseiller: form.notes_conseiller || null,
        points_abordes: form.points_abordes ? form.points_abordes.split("\n").filter(Boolean) : null,
        decisions_prises: form.decisions_prises ? form.decisions_prises.split("\n").filter(Boolean) : null,
        prochaine_etape: form.prochaine_etape || null,
      };
      const res = await axios.post(`${API}/partenaires/beneficiaires/${beneficiaryId}/compte-rendu?token=${token}`, payload);
      toast.success("Compte rendu généré");
      setShowForm(false);
      setForm({ type_entretien: "diagnostic", notes_conseiller: "", points_abordes: "", decisions_prises: "", prochaine_etape: "" });
      loadReports();
      setExpandedReport(res.data.id);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Erreur");
    }
    setGenerating(false);
  };

  const validate = async (reportId) => {
    try {
      await axios.put(`${API}/partenaires/comptes-rendus/${reportId}/valider?token=${token}`);
      toast.success("Compte rendu validé");
      loadReports();
    } catch { toast.error("Erreur"); }
  };

  const copyText = (text) => {
    navigator.clipboard.writeText(text);
    toast.success("Texte copié dans le presse-papier");
  };

  const typeLabels = { diagnostic: "Diagnostic", intermediaire: "Intermédiaire", final: "Clôture" };
  const typeColors = { diagnostic: "bg-blue-100 text-blue-700", intermediaire: "bg-yellow-100 text-yellow-700", final: "bg-purple-100 text-purple-700" };

  return (
    <div className="space-y-4" data-testid="compte-rendu-panel">
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-500">{reports.length} compte(s) rendu(s)</p>
        <Button size="sm" onClick={() => setShowForm(!showForm)} className="bg-indigo-600 hover:bg-indigo-700" data-testid="new-cr-btn">
          <FileText className="w-3.5 h-3.5 mr-1" /> Nouveau compte rendu
        </Button>
      </div>

      {showForm && (
        <Card className="border-indigo-200" data-testid="cr-form">
          <CardHeader className="pb-2"><CardTitle className="text-sm">Préparer le compte rendu</CardTitle><CardDescription className="text-xs">Ajoutez vos notes — l'IA génère un compte rendu professionnel</CardDescription></CardHeader>
          <CardContent className="space-y-3">
            <div>
              <label className="text-xs text-slate-600 block mb-1">Type d'entretien</label>
              <Select value={form.type_entretien} onValueChange={(v) => setForm({ ...form, type_entretien: v })}>
                <SelectTrigger className="h-8 text-xs" data-testid="cr-type-select"><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="diagnostic">Diagnostic</SelectItem>
                  <SelectItem value="intermediaire">Intermédiaire</SelectItem>
                  <SelectItem value="final">Clôture</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-xs text-slate-600 block mb-1">Notes du conseiller (facultatif)</label>
              <Textarea className="text-xs h-20" placeholder="Notes libres de l'entretien..." value={form.notes_conseiller} onChange={(e) => setForm({ ...form, notes_conseiller: e.target.value })} data-testid="cr-notes" />
            </div>
            <div>
              <label className="text-xs text-slate-600 block mb-1">Points abordés (un par ligne)</label>
              <Textarea className="text-xs h-16" placeholder="Point 1&#10;Point 2" value={form.points_abordes} onChange={(e) => setForm({ ...form, points_abordes: e.target.value })} data-testid="cr-points" />
            </div>
            <div>
              <label className="text-xs text-slate-600 block mb-1">Décisions prises (un par ligne)</label>
              <Textarea className="text-xs h-16" placeholder="Décision 1&#10;Décision 2" value={form.decisions_prises} onChange={(e) => setForm({ ...form, decisions_prises: e.target.value })} data-testid="cr-decisions" />
            </div>
            <div>
              <label className="text-xs text-slate-600 block mb-1">Prochaine étape</label>
              <Textarea className="text-xs h-12" placeholder="Prochaine action ou rendez-vous..." value={form.prochaine_etape} onChange={(e) => setForm({ ...form, prochaine_etape: e.target.value })} data-testid="cr-next" />
            </div>
            <div className="flex gap-2">
              <Button size="sm" onClick={generate} disabled={generating} className="bg-indigo-600 hover:bg-indigo-700" data-testid="generate-cr-btn">
                {generating ? <><Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" /> Génération en cours...</> : <><Zap className="w-3.5 h-3.5 mr-1" /> Générer le compte rendu</>}
              </Button>
              <Button size="sm" variant="outline" onClick={() => setShowForm(false)}>Annuler</Button>
            </div>
          </CardContent>
        </Card>
      )}

      {loading ? <div className="flex justify-center py-6"><Loader2 className="w-6 h-6 animate-spin text-slate-400" /></div> : (
        <div className="space-y-3">
          {reports.map((r) => (
            <Card key={r.id} className={`cursor-pointer transition-all ${expandedReport === r.id ? "ring-1 ring-indigo-200" : ""}`} data-testid={`cr-${r.id}`}>
              <CardHeader className="pb-1" onClick={() => setExpandedReport(expandedReport === r.id ? null : r.id)}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Badge className={`text-xs ${typeColors[r.type] || "bg-slate-100"}`}>{typeLabels[r.type] || r.type}</Badge>
                    <span className="text-xs text-slate-500">{r.date}</span>
                    {r.validated && <Badge className="bg-green-100 text-green-700 text-xs">Validé</Badge>}
                    {r.ai_generated && <Badge variant="outline" className="text-xs">IA</Badge>}
                  </div>
                  {expandedReport === r.id ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
                </div>
              </CardHeader>
              {expandedReport === r.id && (
                <CardContent className="space-y-3">
                  {r.content && Object.entries(r.content).filter(([k]) => k !== "texte_complet" && k !== "titre" && k !== "date").map(([key, val]) => (
                    <div key={key}>
                      <p className="text-xs font-medium text-slate-500 mb-0.5">{key.replace(/_/g, " ").replace(/^\w/, c => c.toUpperCase())}</p>
                      <p className="text-xs text-slate-700">{val}</p>
                    </div>
                  ))}
                  {r.content?.texte_complet && (
                    <Card className="bg-slate-50">
                      <CardHeader className="pb-1"><CardTitle className="text-xs text-slate-600 flex items-center justify-between">
                        Texte copiable (compatible outil métier)
                        <Button variant="ghost" size="sm" className="h-6 text-xs" onClick={() => copyText(r.content.texte_complet)} data-testid={`copy-cr-${r.id}`}><Copy className="w-3 h-3 mr-1" /> Copier</Button>
                      </CardTitle></CardHeader>
                      <CardContent><p className="text-xs text-slate-700 whitespace-pre-line">{r.content.texte_complet}</p></CardContent>
                    </Card>
                  )}
                  <div className="flex gap-2">
                    {!r.validated && <Button size="sm" variant="outline" className="h-7 text-xs text-green-600 hover:text-green-700" onClick={() => validate(r.id)} data-testid={`validate-cr-${r.id}`}><CheckCircle2 className="w-3 h-3 mr-1" /> Valider</Button>}
                    <Button size="sm" variant="ghost" className="h-7 text-xs" onClick={() => copyText(r.content?.texte_complet || "")} data-testid={`copy2-cr-${r.id}`}><Copy className="w-3 h-3 mr-1" /> Copier le texte</Button>
                  </div>
                </CardContent>
              )}
            </Card>
          ))}
          {reports.length === 0 && !showForm && (
            <div className="text-center py-6 text-sm text-slate-400">Aucun compte rendu — cliquez sur "Nouveau" pour commencer</div>
          )}
        </div>
      )}
    </div>
  );
};


// ===== PLAN D'ACTION =====
export const PlanActionPanel = ({ beneficiaryId, token }) => {
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  useEffect(() => { loadPlan(); }, [beneficiaryId]);

  const loadPlan = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/partenaires/beneficiaires/${beneficiaryId}/plan-action?token=${token}`);
      setPlan(res.data);
    } catch { /* ignore */ }
    setLoading(false);
  };

  const generate = async () => {
    setGenerating(true);
    try {
      const res = await axios.post(`${API}/partenaires/beneficiaires/${beneficiaryId}/plan-action/generer?token=${token}`);
      setPlan(res.data);
      toast.success("Plan d'action généré");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Erreur");
    }
    setGenerating(false);
  };

  const updateActionStatus = async (actionId, status) => {
    try {
      await axios.put(`${API}/partenaires/plan-action/${plan.id}/actions/${actionId}?token=${token}`, { status });
      toast.success("Action mise à jour");
      loadPlan();
    } catch { toast.error("Erreur"); }
  };

  const catColors = { formation: "bg-blue-100 text-blue-700", emploi: "bg-green-100 text-green-700", administratif: "bg-yellow-100 text-yellow-700", personnel: "bg-purple-100 text-purple-700", accompagnement: "bg-indigo-100 text-indigo-700", reseau: "bg-teal-100 text-teal-700" };
  const prioIcons = { haute: "text-red-500", moyenne: "text-yellow-500", basse: "text-slate-400" };
  const statusMap = { a_faire: { label: "À faire", cls: "bg-slate-100 text-slate-600" }, en_cours: { label: "En cours", cls: "bg-blue-100 text-blue-700" }, termine: { label: "Terminé", cls: "bg-green-100 text-green-700" }, annule: { label: "Annulé", cls: "bg-red-100 text-red-600" } };

  if (loading) return <div className="flex justify-center py-8"><Loader2 className="w-6 h-6 animate-spin text-slate-400" /></div>;

  if (!plan) {
    return (
      <Card data-testid="plan-empty">
        <CardContent className="py-10 text-center">
          <Target className="w-12 h-12 mx-auto mb-3 text-slate-300" />
          <p className="text-sm text-slate-500 mb-4">Générez un plan d'action intelligent basé sur le diagnostic du bénéficiaire</p>
          <Button onClick={generate} disabled={generating} className="bg-indigo-600 hover:bg-indigo-700" data-testid="generate-plan-btn">
            {generating ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Analyse en cours...</> : <><Target className="w-4 h-4 mr-2" /> Générer le plan d'action</>}
          </Button>
        </CardContent>
      </Card>
    );
  }

  const actions = plan.actions || [];
  const done = actions.filter(a => a.status === "termine").length;
  const progress = actions.length > 0 ? Math.round((done / actions.length) * 100) : 0;

  return (
    <div className="space-y-4" data-testid="plan-content">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-slate-800">{plan.objectif_principal}</p>
          <div className="flex items-center gap-2 mt-1">
            <Progress value={progress} className="h-2 w-32" />
            <span className="text-xs text-slate-500">{done}/{actions.length} actions terminées</span>
          </div>
        </div>
        <Button variant="outline" size="sm" onClick={generate} disabled={generating} data-testid="regenerate-plan-btn">
          {generating ? <Loader2 className="w-3 h-3 animate-spin" /> : <Target className="w-3 h-3" />}
          <span className="ml-1">Régénérer</span>
        </Button>
      </div>

      <div className="space-y-2">
        {actions.map((a) => {
          const s = statusMap[a.status] || statusMap.a_faire;
          const isOverdue = a.status === "a_faire" && a.echeance && new Date(a.echeance) < new Date();
          return (
            <Card key={a.id} className={`${isOverdue ? "border-red-200 bg-red-50/30" : ""}`} data-testid={`action-${a.id}`}>
              <CardContent className="py-3 px-4">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <Target className={`w-3.5 h-3.5 shrink-0 ${prioIcons[a.priorite] || prioIcons.moyenne}`} />
                      <span className="text-sm font-medium text-slate-800">{a.titre}</span>
                      <Badge className={`text-xs ${catColors[a.categorie] || "bg-slate-100"}`}>{a.categorie}</Badge>
                      {isOverdue && <Badge className="text-xs bg-red-100 text-red-700">En retard</Badge>}
                    </div>
                    {a.description && <p className="text-xs text-slate-500 mb-1 ml-5">{a.description}</p>}
                    <div className="flex items-center gap-3 ml-5 text-xs text-slate-400">
                      {a.echeance && <span><Clock className="w-3 h-3 inline mr-0.5" /> {new Date(a.echeance).toLocaleDateString('fr-FR')}</span>}
                      {a.dispositif && <span>{a.dispositif}</span>}
                    </div>
                  </div>
                  <Select value={a.status} onValueChange={(v) => updateActionStatus(a.id, v)}>
                    <SelectTrigger className={`h-7 w-28 text-xs ${s.cls}`} data-testid={`action-status-${a.id}`}><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="a_faire">À faire</SelectItem>
                      <SelectItem value="en_cours">En cours</SelectItem>
                      <SelectItem value="termine">Terminé</SelectItem>
                      <SelectItem value="annule">Annulé</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {plan.dispositifs_recommandes?.length > 0 && (
        <Card>
          <CardHeader className="pb-1"><CardTitle className="text-sm">Dispositifs recommandés</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {plan.dispositifs_recommandes.map((d, i) => (
              <div key={i} className="flex items-start gap-2 text-xs">
                <ArrowRight className="w-3 h-3 text-indigo-500 mt-0.5 shrink-0" />
                <div><span className="font-medium">{d.nom}</span> <span className="text-slate-400">({d.acteur})</span><p className="text-slate-500">{d.raison}</p></div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {plan.risques?.length > 0 && (
        <Card className="border-orange-200">
          <CardHeader className="pb-1"><CardTitle className="text-sm text-orange-700 flex items-center gap-1"><AlertTriangle className="w-3.5 h-3.5" /> Risques identifiés</CardTitle></CardHeader>
          <CardContent>{plan.risques.map((r, i) => <p key={i} className="text-xs text-slate-600 mb-1">- {r}</p>)}</CardContent>
        </Card>
      )}
    </div>
  );
};


// ===== LECTURE RAPIDE =====
export const LectureRapide = ({ beneficiaryId, token }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { load(); }, [beneficiaryId]);

  const load = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/partenaires/beneficiaires/${beneficiaryId}/lecture-rapide?token=${token}`);
      setData(res.data);
    } catch { /* ignore */ }
    setLoading(false);
  };

  if (loading) return <div className="flex justify-center py-8"><Loader2 className="w-6 h-6 animate-spin text-slate-400" /></div>;
  if (!data) return <div className="text-center py-6 text-sm text-slate-400">Données indisponibles</div>;

  const risk = data.risque_decrochage || {};
  const riskColors = { critique: "bg-red-100 text-red-700 border-red-300", eleve: "bg-orange-100 text-orange-700 border-orange-300", moyen: "bg-yellow-100 text-yellow-700 border-yellow-300", faible: "bg-green-100 text-green-700 border-green-300" };

  return (
    <div className="space-y-4" data-testid="lecture-rapide">
      {/* Top bar: Identity + Risk */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <Card className="md:col-span-2">
          <CardContent className="py-3">
            <div className="flex items-center justify-between mb-2">
              <div>
                <p className="font-medium text-slate-800">{data.identite.nom}</p>
                <p className="text-xs text-slate-500">{data.identite.secteur} — {data.identite.statut}</p>
              </div>
              <div className="text-right">
                <p className="text-lg font-bold text-indigo-600">{data.identite.progression}%</p>
                <p className="text-xs text-slate-400">Progression</p>
              </div>
            </div>
            <Progress value={data.identite.progression} className="h-2" />
          </CardContent>
        </Card>
        <Card className={`border ${riskColors[risk.niveau] || "bg-slate-50"}`}>
          <CardContent className="py-3 text-center">
            <Shield className="w-6 h-6 mx-auto mb-1" />
            <p className="text-lg font-bold">{risk.score || 0}</p>
            <p className="text-xs">Risque: {risk.niveau || "non évalué"}</p>
          </CardContent>
        </Card>
      </div>

      {/* Risk factors */}
      {risk.facteurs?.length > 0 && (
        <Card className="border-orange-200">
          <CardContent className="py-2">
            <div className="flex gap-2 flex-wrap">
              {risk.facteurs.map((f, i) => <Badge key={i} variant="outline" className="text-xs text-orange-700 border-orange-300">{f}</Badge>)}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Quick diagnostic */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
        {[
          { label: "Motivation", value: data.diagnostic_resume?.motivation },
          { label: "Posture", value: data.diagnostic_resume?.posture },
          { label: "Autonomie", value: data.diagnostic_resume?.autonomie },
          { label: "Compétences", value: `${data.competences_count || 0} validées` },
        ].map((item, i) => (
          <Card key={i}><CardContent className="py-2 text-center"><p className="text-xs text-slate-400">{item.label}</p><p className="text-sm font-medium text-slate-700">{item.value || "—"}</p></CardContent></Card>
        ))}
      </div>

      {/* Freins */}
      {data.freins?.length > 0 && (
        <Card>
          <CardHeader className="pb-1"><CardTitle className="text-sm">Freins actifs ({data.freins.length})</CardTitle></CardHeader>
          <CardContent className="flex gap-2 flex-wrap">
            {data.freins.map((f, i) => {
              const sevColors = { critique: "bg-red-100 text-red-700", eleve: "bg-orange-100 text-orange-700", moyen: "bg-yellow-100 text-yellow-700" };
              return <Badge key={i} className={`text-xs ${sevColors[f.severite] || "bg-slate-100"}`}>{f.categorie}</Badge>;
            })}
          </CardContent>
        </Card>
      )}

      {/* Plan action summary */}
      {data.plan_action && (
        <Card>
          <CardContent className="py-3">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium">Plan d'action</p>
              <div className="flex items-center gap-3 text-xs">
                <span className="text-green-600">{data.plan_action.terminees} terminées</span>
                <span className="text-blue-600">{data.plan_action.en_cours} en cours</span>
                {data.plan_action.en_retard > 0 && <span className="text-red-600">{data.plan_action.en_retard} en retard</span>}
                <span className="text-slate-400">{data.plan_action.total} total</span>
              </div>
            </div>
            <Progress value={data.plan_action.total > 0 ? (data.plan_action.terminees / data.plan_action.total) * 100 : 0} className="h-1.5 mt-2" />
          </CardContent>
        </Card>
      )}

      {/* Last report */}
      {data.dernier_compte_rendu && (
        <Card>
          <CardContent className="py-2 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-slate-400" />
              <span className="text-xs text-slate-600">Dernier entretien: {data.dernier_compte_rendu.date} ({data.dernier_compte_rendu.type})</span>
            </div>
            {data.dernier_compte_rendu.valide ? <Badge className="text-xs bg-green-100 text-green-700">Validé</Badge> : <Badge className="text-xs bg-yellow-100 text-yellow-700">Non validé</Badge>}
          </CardContent>
        </Card>
      )}
    </div>
  );
};


// ===== EXPORT PANEL =====
export const ExportPanel = ({ beneficiaryId, token, benName }) => {
  const [exportData, setExportData] = useState(null);
  const [loading, setLoading] = useState(false);

  const exportDossier = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/partenaires/beneficiaires/${beneficiaryId}/export?token=${token}&format=text`);
      setExportData(res.data);
      toast.success("Dossier exporté");
    } catch (err) {
      toast.error("Erreur d'export");
    }
    setLoading(false);
  };

  const copyAll = () => {
    if (exportData?.content) {
      navigator.clipboard.writeText(exportData.content);
      toast.success("Dossier copié dans le presse-papier");
    }
  };

  const downloadTxt = () => {
    if (exportData?.content) {
      const blob = new Blob([exportData.content], { type: "text/plain;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `dossier_${benName?.replace(/\s+/g, "_") || "beneficiaire"}_${new Date().toISOString().slice(0, 10)}.txt`;
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  return (
    <div className="space-y-4" data-testid="export-panel">
      <Card>
        <CardContent className="py-6 text-center">
          <Download className="w-10 h-10 mx-auto mb-3 text-slate-300" />
          <p className="text-sm text-slate-500 mb-1">Exportez le dossier complet dans un format directement exploitable</p>
          <p className="text-xs text-slate-400 mb-4">Optimisé pour le copié/collé dans les outils métier (France Travail, SI conseiller)</p>
          <Button onClick={exportDossier} disabled={loading} className="bg-indigo-600 hover:bg-indigo-700" data-testid="export-btn">
            {loading ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Export en cours...</> : <><Download className="w-4 h-4 mr-2" /> Exporter le dossier</>}
          </Button>
        </CardContent>
      </Card>

      {exportData && (
        <Card data-testid="export-result">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm">Dossier exporté</CardTitle>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" className="h-7 text-xs" onClick={copyAll} data-testid="copy-export-btn"><Copy className="w-3 h-3 mr-1" /> Copier tout</Button>
                <Button variant="outline" size="sm" className="h-7 text-xs" onClick={downloadTxt} data-testid="download-export-btn"><Download className="w-3 h-3 mr-1" /> Télécharger .txt</Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <pre className="text-xs text-slate-700 whitespace-pre-wrap bg-slate-50 p-4 rounded-lg border max-h-96 overflow-y-auto font-mono">{exportData.content}</pre>
          </CardContent>
        </Card>
      )}
    </div>
  );
};


// ===== BILAN FINAL =====
export const BilanFinalPanel = ({ beneficiaryId, token }) => {
  const [bilan, setBilan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  useEffect(() => { load(); }, [beneficiaryId]);

  const load = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/partenaires/beneficiaires/${beneficiaryId}/bilan-final?token=${token}`);
      setBilan(res.data);
    } catch { /* ignore */ }
    setLoading(false);
  };

  const generate = async () => {
    setGenerating(true);
    try {
      const res = await axios.post(`${API}/partenaires/beneficiaires/${beneficiaryId}/bilan-final?token=${token}`);
      setBilan(res.data);
      toast.success("Bilan de fin de parcours généré");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Erreur");
    }
    setGenerating(false);
  };

  const copyText = (text) => {
    navigator.clipboard.writeText(text);
    toast.success("Texte copié");
  };

  if (loading) return <div className="flex justify-center py-8"><Loader2 className="w-6 h-6 animate-spin text-slate-400" /></div>;

  if (!bilan) {
    return (
      <Card data-testid="bilan-empty">
        <CardContent className="py-10 text-center">
          <ClipboardCheck className="w-12 h-12 mx-auto mb-3 text-slate-300" />
          <p className="text-sm text-slate-500 mb-1">Générez un bilan de fin de parcours</p>
          <p className="text-xs text-slate-400 mb-4">Synthèse complète: compétences développées, actions réalisées, recommandations</p>
          <Button onClick={generate} disabled={generating} className="bg-indigo-600 hover:bg-indigo-700" data-testid="generate-bilan-btn">
            {generating ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Analyse en cours...</> : <><ClipboardCheck className="w-4 h-4 mr-2" /> Générer le bilan final</>}
          </Button>
        </CardContent>
      </Card>
    );
  }

  const c = bilan.content || {};

  return (
    <div className="space-y-4" data-testid="bilan-content">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-slate-700">{c.titre || "Bilan de fin de parcours"}</p>
        <Button variant="outline" size="sm" onClick={generate} disabled={generating} data-testid="regenerate-bilan-btn">
          {generating ? <Loader2 className="w-3 h-3 animate-spin" /> : <ClipboardCheck className="w-3 h-3" />}
          <span className="ml-1">Régénérer</span>
        </Button>
      </div>

      <Card>
        <CardHeader className="pb-1"><CardTitle className="text-sm">Synthèse globale</CardTitle></CardHeader>
        <CardContent><p className="text-sm text-slate-600">{c.synthese_globale}</p></CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-1"><CardTitle className="text-sm">Évolution observée</CardTitle></CardHeader>
        <CardContent><p className="text-sm text-slate-600">{c.evolution_observee}</p></CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <Card className="border-green-200">
          <CardHeader className="pb-1"><CardTitle className="text-sm text-green-700">Compétences développées</CardTitle></CardHeader>
          <CardContent>
            {(c.competences_developpees || []).map((comp, i) => <p key={i} className="text-xs text-slate-600 mb-1 flex items-start gap-1"><CheckCircle2 className="w-3 h-3 text-green-500 mt-0.5 shrink-0" /> {comp}</p>)}
            {(c.competences_transversales || []).map((comp, i) => <p key={`t${i}`} className="text-xs text-slate-500 mb-1 flex items-start gap-1"><TrendingUp className="w-3 h-3 text-blue-400 mt-0.5 shrink-0" /> {comp}</p>)}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-1"><CardTitle className="text-sm">Actions réalisées</CardTitle></CardHeader>
          <CardContent>{(c.actions_realisees || []).map((a, i) => <p key={i} className="text-xs text-slate-600 mb-1">- {a}</p>)}</CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {c.freins_leves?.length > 0 && (
          <Card className="border-green-200">
            <CardHeader className="pb-1"><CardTitle className="text-xs text-green-700">Freins levés</CardTitle></CardHeader>
            <CardContent>{c.freins_leves.map((f, i) => <p key={i} className="text-xs text-slate-600 mb-1">- {f}</p>)}</CardContent>
          </Card>
        )}
        {c.freins_restants?.length > 0 && (
          <Card className="border-orange-200">
            <CardHeader className="pb-1"><CardTitle className="text-xs text-orange-700">Freins restants</CardTitle></CardHeader>
            <CardContent>{c.freins_restants.map((f, i) => <p key={i} className="text-xs text-slate-600 mb-1">- {f}</p>)}</CardContent>
          </Card>
        )}
      </div>

      {c.recommandations_suite?.length > 0 && (
        <Card className="border-indigo-200 bg-indigo-50/30">
          <CardHeader className="pb-1"><CardTitle className="text-sm text-indigo-700">Recommandations pour la suite</CardTitle></CardHeader>
          <CardContent>{c.recommandations_suite.map((r, i) => <p key={i} className="text-xs text-slate-700 mb-1 font-medium">{i + 1}. {r}</p>)}</CardContent>
        </Card>
      )}

      {c.texte_bilan_complet && (
        <Card className="bg-slate-50">
          <CardHeader className="pb-1"><CardTitle className="text-xs text-slate-600 flex items-center justify-between">
            Texte copiable (compatible outil métier)
            <Button variant="ghost" size="sm" className="h-6 text-xs" onClick={() => copyText(c.texte_bilan_complet)} data-testid="copy-bilan-btn"><Copy className="w-3 h-3 mr-1" /> Copier</Button>
          </CardTitle></CardHeader>
          <CardContent><p className="text-xs text-slate-700 whitespace-pre-line">{c.texte_bilan_complet}</p></CardContent>
        </Card>
      )}
    </div>
  );
};
