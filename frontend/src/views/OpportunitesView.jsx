import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  FileEdit, Briefcase, MapPin, Clock, Trash2, ExternalLink,
  CheckCircle2, AlertCircle, Send, Target, Loader2
} from "lucide-react";
import { toast } from "sonner";
import JobMatchingSection from "@/components/JobMatchingSection";
import JobMatchingView from "@/views/JobMatchingView";

const STATUS_CONFIG = {
  en_preparation: { label: "En préparation", color: "bg-amber-100 text-amber-700 border-amber-200", icon: FileEdit },
  envoyee: { label: "Envoyée", color: "bg-blue-100 text-blue-700 border-blue-200", icon: Send },
  entretien: { label: "Entretien prévu", color: "bg-violet-100 text-violet-700 border-violet-200", icon: Target },
  acceptee: { label: "Acceptée", color: "bg-emerald-100 text-emerald-700 border-emerald-200", icon: CheckCircle2 },
  refusee: { label: "Refusée", color: "bg-red-100 text-red-700 border-red-200", icon: AlertCircle },
};

const OpportunitesView = ({ token }) => {
  const [activeTab, setActiveTab] = useState("offres");
  const [applications, setApplications] = useState([]);
  const [loadingApps, setLoadingApps] = useState(false);

  useEffect(() => {
    if (activeTab === "candidatures") loadApplications();
  }, [activeTab, token]);

  const loadApplications = async () => {
    setLoadingApps(true);
    try {
      const res = await axios.get(`${API}/jobs/applications?token=${token}`);
      setApplications(res.data.applications || res.data || []);
    } catch { }
    setLoadingApps(false);
  };

  const handleDelete = async (appId) => {
    if (!window.confirm("Supprimer cette candidature ?")) return;
    try {
      await axios.delete(`${API}/jobs/applications/${appId}?token=${token}`);
      setApplications(prev => prev.filter(a => a.id !== appId));
      toast.success("Candidature supprimée");
    } catch {
      toast.error("Erreur lors de la suppression");
    }
  };

  const handleStatusChange = async (appId, newStatus) => {
    try {
      await axios.put(`${API}/jobs/applications/${appId}/status?token=${token}`, { status: newStatus });
      setApplications(prev => prev.map(a => a.id === appId ? { ...a, status: newStatus } : a));
      toast.success(`Statut mis à jour : ${STATUS_CONFIG[newStatus]?.label || newStatus}`);
    } catch {
      toast.error("Erreur lors de la mise à jour");
    }
  };

  return (
    <div className="space-y-6" data-testid="opportunites-view">
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="w-full grid grid-cols-3 h-11 bg-slate-100 rounded-xl p-1" data-testid="opportunites-tabs">
          <TabsTrigger value="offres" className="text-xs sm:text-sm rounded-lg data-[state=active]:bg-white data-[state=active]:shadow-sm" data-testid="tab-offres">
            <Briefcase className="w-4 h-4 mr-1.5" /> Offres / Matching
          </TabsTrigger>
          <TabsTrigger value="analyse" className="text-xs sm:text-sm rounded-lg data-[state=active]:bg-white data-[state=active]:shadow-sm" data-testid="tab-analyse">
            <Target className="w-4 h-4 mr-1.5" /> Analyser une offre
          </TabsTrigger>
          <TabsTrigger value="candidatures" className="text-xs sm:text-sm rounded-lg data-[state=active]:bg-white data-[state=active]:shadow-sm" data-testid="tab-candidatures">
            <FileEdit className="w-4 h-4 mr-1.5" /> Mes Candidatures
            {applications.length > 0 && (
              <Badge className="ml-1.5 bg-blue-100 text-blue-700 text-[10px] h-5 min-w-[20px] flex items-center justify-center">
                {applications.length}
              </Badge>
            )}
          </TabsTrigger>
        </TabsList>

        <TabsContent value="offres">
          <JobMatchingSection token={token} />
        </TabsContent>

        <TabsContent value="analyse">
          <JobMatchingView token={token} />
        </TabsContent>

        <TabsContent value="candidatures">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-slate-900" style={{ fontFamily: "Outfit, sans-serif" }}>
                  Mes Candidatures
                </h2>
                <p className="text-sm text-slate-500 mt-0.5">Suivez l'avancement de vos candidatures</p>
              </div>
              <Button variant="outline" size="sm" onClick={loadApplications} data-testid="refresh-apps">
                Actualiser
              </Button>
            </div>

            {loadingApps ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
              </div>
            ) : applications.length === 0 ? (
              <Card className="border-dashed border-2 border-slate-200 bg-slate-50/50">
                <CardContent className="p-8 text-center">
                  <FileEdit className="w-12 h-12 text-slate-300 mx-auto mb-3" />
                  <h3 className="font-semibold text-slate-700">Aucune candidature enregistrée</h3>
                  <p className="text-sm text-slate-500 mt-1">
                    Allez dans l'onglet "Offres / Matching" et cliquez sur "Préparer votre candidature" pour commencer.
                  </p>
                  <Button className="mt-4" variant="outline" onClick={() => setActiveTab("offres")} data-testid="go-to-offres">
                    <Briefcase className="w-4 h-4 mr-2" /> Voir les offres
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-3" data-testid="candidatures-list">
                {applications.map((app) => {
                  const statusConf = STATUS_CONFIG[app.status] || STATUS_CONFIG.en_preparation;
                  const StatusIcon = statusConf.icon;
                  const jobData = app.job_data || {};
                  return (
                    <Card key={app.id} className="transition-all hover:shadow-md" data-testid={`candidature-card-${app.id}`}>
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between gap-3">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 flex-wrap">
                              <h3 className="font-semibold text-slate-900 text-sm">{app.job_title}</h3>
                              <Badge className={`text-[10px] border ${statusConf.color}`} data-testid={`status-badge-${app.id}`}>
                                <StatusIcon className="w-3 h-3 mr-0.5" />
                                {statusConf.label}
                              </Badge>
                            </div>
                            <div className="flex items-center gap-3 mt-1.5 text-xs text-slate-500 flex-wrap">
                              {jobData.secteur && <span className="flex items-center gap-1"><Briefcase className="w-3 h-3" />{jobData.secteur}</span>}
                              {jobData.localisation && <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{jobData.localisation}</span>}
                              {jobData.type_contrat && <Badge variant="outline" className="text-[10px]">{jobData.type_contrat}</Badge>}
                              {jobData.matching_score > 0 && (
                                <Badge className={`text-[10px] ${
                                  jobData.matching_score >= 70 ? "bg-emerald-100 text-emerald-700" : 
                                  jobData.matching_score >= 40 ? "bg-amber-100 text-amber-700" : "bg-slate-100 text-slate-600"
                                }`}>
                                  Match {jobData.matching_score}%
                                </Badge>
                              )}
                            </div>
                            <div className="flex items-center gap-1 mt-2 text-[10px] text-slate-400">
                              <Clock className="w-3 h-3" />
                              Enregistrée le {new Date(app.applied_at).toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" })}
                            </div>
                          </div>

                          <div className="flex flex-col items-end gap-2 shrink-0">
                            {/* Status selector */}
                            <select
                              value={app.status}
                              onChange={(e) => handleStatusChange(app.id, e.target.value)}
                              className="text-[11px] border border-slate-200 rounded-md px-2 py-1 bg-white text-slate-600 focus:ring-1 focus:ring-blue-500"
                              data-testid={`status-select-${app.id}`}
                            >
                              {Object.entries(STATUS_CONFIG).map(([key, conf]) => (
                                <option key={key} value={key}>{conf.label}</option>
                              ))}
                            </select>
                            <Button variant="ghost" size="sm" className="h-7 w-7 p-0 text-slate-400 hover:text-red-500"
                              onClick={() => handleDelete(app.id)}
                              data-testid={`delete-app-${app.id}`}
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default OpportunitesView;
