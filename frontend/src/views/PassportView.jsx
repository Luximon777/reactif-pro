import { useState, useEffect, useCallback } from "react";
import { useSearchParams } from "react-router-dom";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";
import {
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell, PieChart, Pie
} from "recharts";
import {
  User, Briefcase, GraduationCap, Sparkles, Target, Plus, RefreshCw,
  Shield, FolderLock, Brain, MessageCircle, Compass, TrendingUp,
  ChevronRight, Star, Award, BookOpen, Share2, Trash2, Zap, Edit3,
  Save, Check, ArrowRight, Layers, Activity, Hexagon, CircleDot, Link2, Copy, X, Play,
  Eye, EyeOff, Loader2, CheckCircle2, FileDown, ShieldCheck, Upload
} from "lucide-react";
import EmergingCompetenceCard from "@/components/Passport/EmergingCompetenceCard";
import EmergingTab from "@/components/Passport/EmergingTab";
import {
  SOURCE_CONFIG, LEVEL_CONFIG, CATEGORY_CONFIG, NATURE_CONFIG,
  CCSP_POLES, CCSP_DEGREES, COMPONENT_LABELS, VERTU_COLORS
} from "@/components/Passport/passportConfig";

// Configs imported from @/components/Passport/passportConfig

const SimulationTrajectoireBlock = ({ token }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    axios.get(`${API}/activation/trajectory-simulation?token=${token}`).then(r => {
      if (r.data.trajectory_simulation) setData(r.data.trajectory_simulation);
    }).catch(() => {});
  }, [token]);

  const generate = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${API}/activation/simulate-trajectory?token=${token}`);
      if (!res.data.error) { setData(res.data); toast.success("Simulation générée"); }
      else toast.error(res.data.error);
    } catch { toast.error("Erreur"); }
    setLoading(false);
  };

  const probColor = (p) => p >= 0.7 ? "text-emerald-600" : p >= 0.5 ? "text-amber-600" : "text-rose-600";

  return (
    <Card className="border-slate-200" data-testid="simulation-block">
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full bg-violet-100 flex items-center justify-center text-violet-700 text-xs font-bold">S</div>
            <h4 className="text-sm font-semibold text-slate-800">Simulation de trajectoire</h4>
          </div>
          <Button variant="outline" size="sm" className="h-7 text-xs" onClick={generate} disabled={loading} data-testid="simulate-btn">
            {loading ? <Loader2 className="w-3 h-3 animate-spin mr-1" /> : <TrendingUp className="w-3 h-3 mr-1" />}
            {loading ? "Analyse..." : data ? "Régénérer" : "Simuler"}
          </Button>
        </div>
        {!data ? (
          <p className="text-xs text-slate-500 text-center py-4">Simulez vos trajectoires possibles : realiste, ambitieuse et reconversion</p>
        ) : (
          <div className="space-y-3">
            {(data.trajectoires || []).map((t, i) => (
              <div key={i} className="border border-slate-100 rounded-lg p-3" data-testid={`trajectory-${i}`}>
                <div className="flex items-center justify-between">
                  <h5 className="text-xs font-semibold text-slate-800">{t.metier_cible}</h5>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] text-slate-500">{t.duree_estimee}</span>
                    <span className={`text-xs font-bold ${probColor(t.probabilite)}`}>{Math.round(t.probabilite * 100)}%</span>
                  </div>
                </div>
                <p className="text-[10px] text-slate-500 mt-0.5">{t.secteur}</p>
                {t.etapes && (
                  <div className="mt-2 space-y-1">
                    {t.etapes.slice(0, 3).map((e, j) => (
                      <div key={j} className="flex items-center gap-1.5 text-[10px] text-slate-600">
                        <ArrowRight className="w-2.5 h-2.5 text-violet-400 shrink-0" />
                        <span><span className="font-medium">{e.action}</span> ({e.type} — {e.duree})</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {data.analyse_globale && <p className="text-[10px] text-slate-600 italic">{data.analyse_globale}</p>}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

const FormationRecoBlock = ({ token }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    axios.get(`${API}/activation/formation-recommendations?token=${token}`).then(r => {
      if (r.data.formation_recommendations) setData(r.data.formation_recommendations);
    }).catch(() => {});
  }, [token]);

  const generate = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${API}/activation/recommend-formations?token=${token}`);
      if (!res.data.error) { setData(res.data); toast.success("Recommandations générées"); }
      else toast.error(res.data.error);
    } catch { toast.error("Erreur"); }
    setLoading(false);
  };

  const prioColor = { haute: "bg-rose-50 text-rose-700 border-rose-200", moyenne: "bg-amber-50 text-amber-700 border-amber-200", faible: "bg-slate-50 text-slate-600 border-slate-200" };

  return (
    <Card className="border-slate-200" data-testid="formations-block">
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 text-xs font-bold">F</div>
            <h4 className="text-sm font-semibold text-slate-800">Formations recommandées</h4>
          </div>
          <Button variant="outline" size="sm" className="h-7 text-xs" onClick={generate} disabled={loading} data-testid="recommend-formations-btn">
            {loading ? <Loader2 className="w-3 h-3 animate-spin mr-1" /> : <GraduationCap className="w-3 h-3 mr-1" />}
            {loading ? "Analyse..." : data ? "Actualiser" : "Recommander"}
          </Button>
        </div>
        {!data ? (
          <p className="text-xs text-slate-500 text-center py-4">L'IA analyse vos lacunes et propose des formations adaptees</p>
        ) : (
          <div className="space-y-2">
            {(data.formations || []).map((f, i) => (
              <div key={i} className="flex items-start gap-2 border border-slate-100 rounded-lg p-2.5" data-testid={`formation-reco-${i}`}>
                <Badge className={`text-[9px] shrink-0 ${prioColor[f.priorite] || prioColor.moyenne}`}>{f.priorite}</Badge>
                <div className="flex-1">
                  <p className="text-xs font-medium text-slate-800">{f.intitule}</p>
                  <p className="text-[10px] text-slate-500">{f.objectif} — {f.duree}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <Badge variant="outline" className="text-[9px]">{f.type}</Badge>
                    <span className="text-[9px] text-emerald-600 font-medium">{f.financement_possible}</span>
                  </div>
                </div>
              </div>
            ))}
            {data.analyse && <p className="text-[10px] text-slate-600 italic mt-1">{data.analyse}</p>}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

const PartageSelectifBlock = ({ token }) => {
  const [shares, setShares] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ recipient_name: "", recipient_type: "employeur", sections: ["identite", "competences"], duration_days: 30 });
  const [creating, setCreating] = useState(false);

  const loadShares = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/shares?token=${token}`);
      setShares(res.data.shares || []);
    } catch { /* silent */ }
  }, [token]);

  useEffect(() => { loadShares(); }, [loadShares]);

  const createShare = async () => {
    setCreating(true);
    try {
      const res = await axios.post(`${API}/shares/create?token=${token}`, form);
      if (res.data.share_id) { toast.success("Lien de partage cree"); loadShares(); setShowForm(false); }
    } catch { toast.error("Erreur"); }
    setCreating(false);
  };

  const revokeShare = async (id) => {
    try {
      await axios.delete(`${API}/shares/${id}?token=${token}`);
      toast.success("Partage revoque");
      loadShares();
    } catch { toast.error("Erreur"); }
  };

  const sectionLabels = { identite: "Identite", experiences: "Experiences", competences: "Competences", formations: "Formations", soft_skills: "Soft Skills prouves", adn_pro: "ADN Pro" };
  const allSections = Object.keys(sectionLabels);

  return (
    <Card className="border-slate-200" data-testid="partage-block">
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full bg-amber-100 flex items-center justify-center text-amber-700 text-xs font-bold">P</div>
            <h4 className="text-sm font-semibold text-slate-800">Partage sélectif</h4>
            <Badge variant="outline" className="text-[10px]">{shares.filter(s => s.active).length} actif{shares.filter(s => s.active).length > 1 ? "s" : ""}</Badge>
          </div>
          <Button variant="outline" size="sm" className="h-7 text-xs" onClick={() => setShowForm(!showForm)} data-testid="create-share-btn">
            <Share2 className="w-3 h-3 mr-1" />{showForm ? "Annuler" : "Nouveau partage"}
          </Button>
        </div>

        {showForm && (
          <div className="space-y-2 mb-3 p-3 bg-slate-50 rounded-lg" data-testid="share-form">
            <Input placeholder="Nom du destinataire" value={form.recipient_name} onChange={e => setForm({...form, recipient_name: e.target.value})} className="h-8 text-xs" />
            <Select value={form.recipient_type} onValueChange={v => setForm({...form, recipient_type: v})}>
              <SelectTrigger className="h-8 text-xs"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="employeur">Employeur</SelectItem>
                <SelectItem value="conseiller">Conseiller</SelectItem>
                <SelectItem value="formation">Organisme de formation</SelectItem>
                <SelectItem value="autre">Autre</SelectItem>
              </SelectContent>
            </Select>
            <div>
              <p className="text-[10px] font-medium text-slate-600 mb-1">Sections a partager :</p>
              <div className="flex flex-wrap gap-1.5">
                {allSections.map(s => (
                  <button key={s} onClick={() => setForm({...form, sections: form.sections.includes(s) ? form.sections.filter(x => x !== s) : [...form.sections, s]})}
                    className={`text-[10px] px-2 py-1 rounded-full border transition-colors ${form.sections.includes(s) ? "bg-blue-100 text-blue-700 border-blue-300" : "bg-white text-slate-500 border-slate-200"}`}>
                    {sectionLabels[s]}
                  </button>
                ))}
              </div>
            </div>
            <Button size="sm" className="h-7 text-xs w-full bg-[#1e3a5f]" onClick={createShare} disabled={creating || !form.recipient_name} data-testid="submit-share-btn">
              {creating ? <Loader2 className="w-3 h-3 animate-spin mr-1" /> : <Share2 className="w-3 h-3 mr-1" />}Créer le lien de partage
            </Button>
          </div>
        )}

        {shares.filter(s => s.active).length === 0 && !showForm ? (
          <p className="text-xs text-slate-500 text-center py-3">Aucun partage actif. Partagez votre profil de manière sélective et traçable.</p>
        ) : (
          <div className="space-y-2">
            {shares.filter(s => s.active).map(s => (
              <div key={s.id} className="flex items-center justify-between bg-white border border-slate-100 rounded-lg px-3 py-2" data-testid={`share-${s.id}`}>
                <div>
                  <p className="text-xs font-medium text-slate-800">{s.recipient_name} <span className="text-slate-400">({s.recipient_type})</span></p>
                  <p className="text-[10px] text-slate-500">{s.sections.map(sec => sectionLabels[sec] || sec).join(", ")} — {s.views} vue{s.views > 1 ? "s" : ""}</p>
                </div>
                <Button variant="ghost" size="sm" className="h-6 text-[10px] text-rose-500 hover:text-rose-700" onClick={() => revokeShare(s.id)}>Révoquer</Button>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

const IdentityAdnBlock = ({ token, passport, setPassport }) => {
  const [loading, setLoading] = useState(false);
  const adn = passport?.identity_adn;

  const generate = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${API}/profile/identity-adn?token=${token}`);
      if (!res.data.error) {
        setPassport(prev => ({ ...prev, identity_adn: res.data, identity_adn_generated_at: new Date().toISOString() }));
        toast.success("ADN professionnel généré");
      } else {
        toast.error(res.data.error);
      }
    } catch { toast.error("Erreur generation ADN"); }
    setLoading(false);
  };

  if (!adn) {
    return (
      <Card className="border-dashed border-2 border-slate-200" data-testid="adn-pro-empty">
        <CardContent className="p-4 text-center">
          <Brain className="w-8 h-8 text-slate-300 mx-auto mb-2" />
          <h4 className="text-sm font-semibold text-slate-700">ADN Professionnel</h4>
          <p className="text-xs text-slate-500 mt-1 mb-3">Générez votre identité professionnelle augmentée : forces, style, potentiel d'évolution</p>
          <Button size="sm" onClick={generate} disabled={loading} className="bg-[#1e3a5f] hover:bg-[#2a5a8f]" data-testid="generate-adn-btn">
            {loading ? <Loader2 className="w-4 h-4 mr-1 animate-spin" /> : <Sparkles className="w-4 h-4 mr-1" />}
            {loading ? "Generation en cours..." : "Generer mon ADN Pro"}
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-[#1e3a5f]/20 overflow-hidden" data-testid="adn-pro-block">
      <div className="bg-gradient-to-r from-[#1e3a5f] to-[#2a5a8f] px-4 py-2.5 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Brain className="w-4 h-4 text-white" />
          <span className="text-sm font-semibold text-white">ADN Professionnel</span>
        </div>
        <Button variant="ghost" size="sm" className="h-6 text-[10px] text-white/80 hover:text-white hover:bg-white/10" onClick={generate} disabled={loading}>
          {loading ? <Loader2 className="w-3 h-3 animate-spin" /> : <RefreshCw className="w-3 h-3 mr-1" />}Régénérer
        </Button>
      </div>
      <CardContent className="p-4 space-y-3">
        <p className="text-xs text-slate-700 leading-relaxed italic">{adn.synthese_adn}</p>
        {adn.style_professionnel && (
          <div className="flex items-center gap-2 bg-blue-50 rounded-lg px-3 py-2">
            <User className="w-3.5 h-3.5 text-blue-600 shrink-0" />
            <span className="text-xs text-blue-800"><span className="font-semibold">Style :</span> {adn.style_professionnel}</span>
          </div>
        )}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div>
            <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-1.5">Forces principales</p>
            <div className="space-y-1">{(adn.forces_principales || []).map((f, i) => (
              <div key={i} className="flex items-center gap-1.5 text-xs text-slate-700"><CheckCircle2 className="w-3 h-3 text-emerald-500 shrink-0" />{f}</div>
            ))}</div>
          </div>
          <div>
            <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-1.5">Environnements favorables</p>
            <div className="space-y-1">{(adn.environnements_favorables || []).map((e, i) => (
              <div key={i} className="flex items-center gap-1.5 text-xs text-slate-700"><Compass className="w-3 h-3 text-blue-500 shrink-0" />{e}</div>
            ))}</div>
          </div>
          <div>
            <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-1.5">Axes de projection</p>
            <div className="space-y-1">{(adn.axes_projection || []).map((a, i) => (
              <div key={i} className="flex items-center gap-1.5 text-xs text-slate-700"><TrendingUp className="w-3 h-3 text-violet-500 shrink-0" />{a}</div>
            ))}</div>
          </div>
        </div>
        {adn.potentiel_evolution && (
          <div className="flex items-center gap-2 bg-emerald-50 rounded-lg px-3 py-2">
            <Zap className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
            <span className="text-xs text-emerald-800"><span className="font-semibold">Potentiel :</span> {adn.potentiel_evolution}</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

const ConfidenceScoreWidget = ({ token }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const res = await axios.get(`${API}/profile/confidence-scores/simple?token=${token}`);
        setData(res.data);
      } catch { /* silent */ }
      setLoading(false);
    })();
  }, [token]);

  if (loading || !data) return null;

  const colorMap = {
    eleve: { bg: "bg-emerald-50", border: "border-emerald-200", text: "text-emerald-700", bar: "[&>div]:bg-emerald-500" },
    moyen: { bg: "bg-amber-50", border: "border-amber-200", text: "text-amber-700", bar: "[&>div]:bg-amber-500" },
    faible: { bg: "bg-rose-50", border: "border-rose-200", text: "text-rose-700", bar: "[&>div]:bg-rose-500" },
  };
  const c = colorMap[data.level] || colorMap.moyen;

  return (
    <Card className={`${c.border} ${c.bg} border`} data-testid="confidence-score-widget">
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Shield className="w-4 h-4 text-slate-600" />
            <h4 className="text-sm font-semibold text-slate-800">Score de confiance du profil</h4>
          </div>
          <div className="flex items-center gap-2">
            <span className={`text-lg font-bold ${c.text}`}>{data.global_pct}%</span>
            <Badge className={`${c.bg} ${c.text} border ${c.border} text-[10px]`}>{data.label}</Badge>
          </div>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {data.dimensions.map((dim) => (
            <div key={dim.key} className="space-y-1">
              <div className="flex justify-between text-[10px]">
                <span className="text-slate-600">{dim.label}</span>
                <span className="font-semibold text-slate-700">{dim.pct}%</span>
              </div>
              <Progress value={dim.pct} className={`h-1.5 ${c.bar}`} />
            </div>
          ))}
        </div>
        {data.tips.length > 0 && (
          <div className="mt-3 space-y-1">
            {data.tips.map((tip, i) => (
              <div key={i} className="flex items-start gap-1.5 text-[10px] text-slate-600">
                <TrendingUp className="w-3 h-3 text-slate-400 shrink-0 mt-0.5" />
                <span>{tip}</span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

const PassportView = ({ token, viewMode }) => {
  const [passport, setPassport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [searchParams] = useSearchParams();
  const urlTab = searchParams.get("tab");
  const [activeTab, setActiveTab] = useState(
    urlTab || (viewMode === "profil" ? "profile" :
    viewMode === "competences" ? "competences" :
    "profile")
  );
  const [addCompDialogOpen, setAddCompDialogOpen] = useState(false);
  const [addExpDialogOpen, setAddExpDialogOpen] = useState(false);
  const [editingProfile, setEditingProfile] = useState(false);
  const [loadingPasserelles, setLoadingPasserelles] = useState(false);
  const [diagnostic, setDiagnostic] = useState(null);
  const [loadingDiagnostic, setLoadingDiagnostic] = useState(false);
  const [evaluatingComp, setEvaluatingComp] = useState(null);
  const [evalComponents, setEvalComponents] = useState({ connaissance: 0, cognition: 0, conation: 0, affection: 0, sensori_moteur: 0 });
  const [evalCcspPole, setEvalCcspPole] = useState("");
  const [evalCcspDegree, setEvalCcspDegree] = useState("");

  const [newComp, setNewComp] = useState({ name: "", nature: "", category: "technique", level: "intermediaire", experience_years: 0, components: null, ccsp_pole: "", ccsp_degree: "" });
  const [newExp, setNewExp] = useState({ title: "", organization: "", description: "", skills_used: "", achievements: "", experience_type: "professionnel" });
  const [profileEdit, setProfileEdit] = useState({ professional_summary: "", career_project: "", motivations: "", compatible_environments: "", target_sectors: "" });
  const [archeologie, setArcheologie] = useState(null);
  const [loadingArcheologie, setLoadingArcheologie] = useState(false);
  const [emergingFromApi, setEmergingFromApi] = useState([]);
  const [loadingEmerging, setLoadingEmerging] = useState(false);
  const [shareLinks, setShareLinks] = useState([]);
  const [sharingOpen, setSharingOpen] = useState(false);
  const [creatingShare, setCreatingShare] = useState(false);
  const [dclicProfile, setDclicProfile] = useState(null);
  const [refreshingDynamic, setRefreshingDynamic] = useState(false);
  const [expandedSkills, setExpandedSkills] = useState({ sf: false, se: false });
  const [illustrations, setIllustrations] = useState([]);

  const loadPassport = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/passport?token=${token}`);
      setPassport(res.data);
    } catch (error) {
      console.error("Error loading passport:", error);
    }
    setLoading(false);
  }, [token]);

  const loadEmerging = useCallback(async () => {
    setLoadingEmerging(true);
    try {
      const res = await axios.get(`${API}/emerging/competences?token=${token}`);
      setEmergingFromApi(res.data.competences || []);
    } catch (e) {
      console.error("Error loading emerging:", e);
    }
    setLoadingEmerging(false);
  }, [token]);

  const loadIllustrations = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/passport/illustrations?token=${token}`);
      setIllustrations(res.data.illustrations || []);
    } catch { /* silent */ }
  }, [token]);

  useEffect(() => {
    loadPassport();
    loadEmerging();
    loadIllustrations();
    axios.get(`${API}/profile?token=${token}`).then(r => setDclicProfile(r.data)).catch(() => {});
  }, [loadPassport, loadEmerging, loadIllustrations, token]);

  // Auto-refresh passport after initial load if data looks incomplete (CV just uploaded)
  useEffect(() => {
    if (passport && !loading) {
      const hasExperiences = (passport.experiences || []).length > 0;
      const hasCompetences = (passport.competences || []).length > 0;
      const hasSummary = !!passport.professional_summary || !!passport.resume_professionnel;
      if (!hasExperiences && !hasCompetences && !hasSummary) {
        // Data might still be propagating after CV upload - retry after 3s
        const retryTimer = setTimeout(() => {
          loadPassport();
        }, 3000);
        return () => clearTimeout(retryTimer);
      }
    }
  }, [passport, loading, loadPassport]);

  // Auto-refresh dynamic profile when D'CLIC PRO data exists but motivations are empty
  useEffect(() => {
    if (passport && dclicProfile?.dclic_imported &&
        (!passport.motivations || passport.motivations.length === 0) &&
        !refreshingDynamic) {
      (async () => {
        try {
          setRefreshingDynamic(true);
          const res = await axios.post(`${API}/passport/refresh-dynamic-profile?token=${token}`);
          if (res.data.success) {
            setPassport(prev => ({
              ...prev,
              motivations: res.data.motivations,
              compatible_environments: res.data.compatible_environments,
              professional_summary: res.data.professional_summary || prev.professional_summary,
              career_project: res.data.career_project || prev.career_project,
              dynamic_profile: {
                strengths_synthesis: res.data.strengths_synthesis,
                evolution_axes: res.data.evolution_axes,
                motivations: res.data.motivations,
                compatible_environments: res.data.compatible_environments,
                last_refreshed: new Date().toISOString(),
                source: "dclic_pro",
              }
            }));
            toast.success("Profil automatiquement enrichi par D'CLIC PRO");
          }
        } catch {
          // Silent fail - user can manually refresh via Profil Dynamique tab
        } finally {
          setRefreshingDynamic(false);
        }
      })();
    }
  }, [passport?.motivations?.length, dclicProfile?.dclic_imported, token]);


  const loadShareLinks = async () => {
    try {
      const res = await axios.get(`${API}/passport/shares?token=${token}`);
      setShareLinks(res.data);
    } catch (e) { console.error("Share links error:", e); }
  };

  const handleCreateShare = async () => {
    setCreatingShare(true);
    try {
      await axios.post(`${API}/passport/share/create?token=${token}`);
      toast.success("Lien de partage cree !");
      await loadShareLinks();
    } catch (e) { toast.error("Erreur lors de la creation du lien"); }
    setCreatingShare(false);
  };

  const handleRevokeShare = async (shareId) => {
    try {
      await axios.delete(`${API}/passport/shares/${shareId}?token=${token}`);
      toast.success("Lien revoque");
      setShareLinks((prev) => prev.filter((s) => s.id !== shareId));
    } catch (e) { toast.error("Erreur lors de la revocation"); }
  };

  const copyShareLink = (shareId) => {
    const url = `${window.location.origin}/passport/shared/${shareId}`;
    navigator.clipboard.writeText(url).then(() => toast.success("Lien copie !")).catch(() => toast.error("Impossible de copier"));
  };

  const loadDiagnostic = async () => {
    setLoadingDiagnostic(true);
    try {
      // Auto-evaluate via AI first
      await axios.post(`${API}/passport/diagnostic/auto-evaluate?token=${token}`);
      // Then load the diagnostic
      const res = await axios.get(`${API}/passport/diagnostic?token=${token}`);
      setDiagnostic(res.data);
      await loadPassport();
    } catch (e) { toast.error(e.response?.data?.detail || "Erreur lors du diagnostic"); }
    setLoadingDiagnostic(false);
  };

  const loadArcheologie = async () => {
    setLoadingArcheologie(true);
    try {
      const res = await axios.get(`${API}/passport/archeologie?token=${token}`);
      setArcheologie(res.data);
    } catch (e) { toast.error("Erreur lors du chargement de l'archéologie"); }
    setLoadingArcheologie(false);
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await axios.post(`${API}/passport/refresh?token=${token}`);
      await loadPassport();
      toast.success("Passeport actualisé depuis toutes les sources");
    } catch (e) { toast.error("Erreur lors de l'actualisation"); }
    setRefreshing(false);
  };

  const handleAddCompetence = async () => {
    if (!newComp.name.trim()) return;
    try {
      const payload = { ...newComp };
      if (!payload.ccsp_pole) delete payload.ccsp_pole;
      if (!payload.ccsp_degree) delete payload.ccsp_degree;
      await axios.post(`${API}/passport/competences?token=${token}`, payload);
      toast.success("Compétence ajoutée");
      setAddCompDialogOpen(false);
      setNewComp({ name: "", nature: "", category: "technique", level: "intermediaire", experience_years: 0, components: null, ccsp_pole: "", ccsp_degree: "" });
      await loadPassport();
    } catch (e) { toast.error("Erreur lors de l'ajout"); }
  };

  const handleAddExperience = async () => {
    if (!newExp.title.trim()) return;
    try {
      const payload = {
        ...newExp,
        skills_used: newExp.skills_used ? newExp.skills_used.split(",").map(s => s.trim()).filter(Boolean) : [],
        achievements: newExp.achievements ? newExp.achievements.split(",").map(s => s.trim()).filter(Boolean) : [],
      };
      await axios.post(`${API}/passport/experiences?token=${token}`, payload);
      toast.success("Expérience ajoutée");
      setAddExpDialogOpen(false);
      setNewExp({ title: "", organization: "", description: "", skills_used: "", achievements: "", experience_type: "professionnel" });
      await loadPassport();
    } catch (e) { toast.error("Erreur lors de l'ajout"); }
  };

  const handleDeleteCompetence = async (compId) => {
    try {
      await axios.delete(`${API}/passport/competences/${compId}?token=${token}`);
      toast.success("Compétence supprimée");
      await loadPassport();
    } catch (e) { toast.error("Erreur lors de la suppression"); }
  };

  const handleDeleteExperience = async (expId) => {
    try {
      await axios.delete(`${API}/passport/experiences/${expId}?token=${token}`);
      toast.success("Expérience supprimée");
      await loadPassport();
    } catch (e) { toast.error("Erreur lors de la suppression"); }
  };

  const handleStartEditProfile = () => {
    setProfileEdit({
      professional_summary: passport?.professional_summary || "",
      career_project: passport?.career_project || "",
      motivations: (passport?.motivations || []).join(", "),
      compatible_environments: (passport?.compatible_environments || []).join(", "),
      target_sectors: (passport?.target_sectors || []).join(", "),
    });
    setEditingProfile(true);
  };

  const handleSaveProfile = async () => {
    try {
      await axios.put(`${API}/passport/profile?token=${token}`, {
        professional_summary: profileEdit.professional_summary || null,
        career_project: profileEdit.career_project || null,
        motivations: profileEdit.motivations ? profileEdit.motivations.split(",").map(s => s.trim()).filter(Boolean) : null,
        compatible_environments: profileEdit.compatible_environments ? profileEdit.compatible_environments.split(",").map(s => s.trim()).filter(Boolean) : null,
        target_sectors: profileEdit.target_sectors ? profileEdit.target_sectors.split(",").map(s => s.trim()).filter(Boolean) : null,
      });
      toast.success("Profil mis à jour");
      setEditingProfile(false);
      await loadPassport();
    } catch (e) { toast.error("Erreur lors de la mise à jour"); }
  };

  const handleLoadPasserelles = async () => {
    setLoadingPasserelles(true);
    try {
      const res = await axios.get(`${API}/passport/passerelles?token=${token}`);
      await loadPassport();
      if (res.data.passerelles?.length > 0) {
        toast.success(`${res.data.passerelles.length} passerelles identifiées par l'IA`);
      } else {
        toast.info("Ajoutez plus de compétences pour obtenir des suggestions");
      }
    } catch (e) { toast.error("Erreur lors de l'analyse IA"); }
    setLoadingPasserelles(false);
  };

  // Auto-load passerelles when tab is opened and none exist
  useEffect(() => {
    if (activeTab === "passerelles" && passport && passport.competences?.length > 0 && (!passport.passerelles || passport.passerelles.length === 0) && !loadingPasserelles) {
      handleLoadPasserelles();
    }
  }, [activeTab, passport?.competences?.length]);

  const handleOpenEvaluation = (comp) => {
    setEvaluatingComp(comp);
    setEvalComponents(comp.components || { connaissance: 0, cognition: 0, conation: 0, affection: 0, sensori_moteur: 0 });
    setEvalCcspPole(comp.ccsp_pole || "");
    setEvalCcspDegree(comp.ccsp_degree || "");
  };

  const handleSaveEvaluation = async () => {
    if (!evaluatingComp) return;
    try {
      await axios.put(`${API}/passport/competences/${evaluatingComp.id}/evaluate?token=${token}`, {
        components: evalComponents,
        ccsp_pole: evalCcspPole || null,
        ccsp_degree: evalCcspDegree || null,
      });
      toast.success("Évaluation enregistrée");
      setEvaluatingComp(null);
      await loadPassport();
    } catch (e) { toast.error("Erreur lors de l'évaluation"); }
  };

  if (loading) return <div className="flex items-center justify-center h-64"><RefreshCw className="w-8 h-8 animate-spin text-blue-600" /></div>;
  if (!passport) return <div className="text-center py-12 text-slate-500">Impossible de charger le passeport</div>;

  const { completeness_score = 0, competences = [], experiences = [], learning_path = [], passerelles = [], sources_count = {} } = passport;
  const passportEmpty = competences.length === 0 && experiences.length === 0 && !passport.professional_summary && !passport.resume_professionnel;
  const mainCompetences = competences.filter(c => !c.is_emerging && c.source !== "ia_detectee");
  const emergingCompetences = competences.filter(c => c.is_emerging || c.source === "ia_detectee");
  const savoirFaire = competences.filter(c => c.nature === "savoir_faire");
  const dclic_comp_names = new Set((dclicProfile?.dclic_competences || []).map(n => n.toLowerCase()));
  const savoirEtre = competences.filter(c => c.nature === "savoir_etre" || (!c.nature && (c.category === "transversale" || dclic_comp_names.has((c.name || "").toLowerCase()))));
  const nonClassees = competences.filter(c => !c.nature && c.category !== "transversale" && !dclic_comp_names.has((c.name || "").toLowerCase()));

  return (
    <div className="space-y-6" data-testid="passport-view">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-[#1e3a5f] flex items-center gap-3">
            <Shield className="w-8 h-8" />
            Mon parcours professionnel
          </h1>
          <p className="text-slate-500 mt-1">Votre identité professionnelle numérique évolutive</p>
        </div>
        <div className="flex items-center gap-2">
          <Dialog open={sharingOpen} onOpenChange={(open) => { setSharingOpen(open); if (open) loadShareLinks(); }}>
            <DialogTrigger asChild>
              <Button variant="outline" data-testid="passport-share-btn">
                <Share2 className="w-4 h-4 mr-2" />Partager
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[480px]" data-testid="share-dialog">
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2">
                  <Link2 className="w-5 h-5 text-[#1e3a5f]" />Partager mon Passeport
                </DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <p className="text-sm text-slate-600">
                  Generez un lien anonymise pour partager votre passeport avec un recruteur. Le lien expire apres 30 jours et peut etre revoque a tout moment.
                </p>
                <Button onClick={handleCreateShare} disabled={creatingShare} className="w-full bg-[#1e3a5f] hover:bg-[#2d4a6f]" data-testid="create-share-link-btn">
                  {creatingShare ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Plus className="w-4 h-4 mr-2" />}
                  Générer un nouveau lien
                </Button>
                {shareLinks.length > 0 && (
                  <div className="space-y-2 max-h-60 overflow-y-auto">
                    <p className="text-xs font-medium text-slate-500">Liens actifs :</p>
                    {shareLinks.map((link) => (
                      <div key={link.id} className="flex items-center gap-2 p-3 rounded-lg bg-slate-50 border border-slate-200" data-testid={`share-link-${link.id}`}>
                        <div className="flex-1 min-w-0">
                          <p className="text-xs font-mono text-slate-700 truncate">{window.location.origin}/passport/shared/{link.id}</p>
                          <div className="flex items-center gap-2 mt-1 text-[10px] text-slate-400">
                            <span>{link.views || 0} vue(s)</span>
                            <span>Expire le {new Date(link.expires_at).toLocaleDateString("fr-FR")}</span>
                          </div>
                        </div>
                        <Button variant="ghost" size="sm" onClick={() => copyShareLink(link.id)} data-testid={`copy-link-${link.id}`}>
                          <Copy className="w-3.5 h-3.5" />
                        </Button>
                        <Button variant="ghost" size="sm" onClick={() => handleRevokeShare(link.id)} className="text-red-500 hover:text-red-700 hover:bg-red-50" data-testid={`revoke-link-${link.id}`}>
                          <X className="w-3.5 h-3.5" />
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </DialogContent>
          </Dialog>
          <Button variant="outline" onClick={handleRefresh} disabled={refreshing} data-testid="passport-refresh-btn">
            <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? "animate-spin" : ""}`} />
            Actualiser
          </Button>
        </div>
      </div>

      {/* D'CLIC PRO Section */}
      {viewMode === "profil" && (() => {
        if (dclicProfile?.dclic_imported) {
          // BOOST SECTION — D'CLIC PRO imported
          const dp = dclicProfile.dclic_profile || {};
          const vp = dp.vertus_profile || {};
          const vd = dp.vertu_data || {};
          const dimensions = [
            (vp.dominant_name || vd.name) && { label: "Vertu dominante", value: vp.dominant_name || vd.name, gradient: "from-amber-500 to-orange-600", icon: Award, desc: "Force motrice" },
            vp.secondary_name && { label: "Vertu secondaire", value: vp.secondary_name, gradient: "from-rose-500 to-pink-600", icon: Shield, desc: "Equilibre interieur" },
            (vd.valeurs_schwartz || []).length > 0 && { label: "Valeurs cles", value: vd.valeurs_schwartz.slice(0, 2).join(", "), gradient: "from-violet-500 to-purple-600", icon: Compass, desc: "Ce qui vous anime" },
          ].filter(Boolean);
          const dclicCompetences = dclicProfile.dclic_competences || [];
          const dclicSkills = (dclicProfile.skills || []).filter(s => s.source === "dclic_pro");
          const totalApports = dimensions.length + dclicCompetences.length + dclicSkills.length;

          return (
            <Card className="border-0 shadow-lg overflow-hidden" data-testid="dclic-boost-section">
              {/* Header gradient */}
              <div className="bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 p-5 relative">
                <div className="absolute inset-0 opacity-10" style={{backgroundImage: "url(\"data:image/svg+xml,%3Csvg width='20' height='20' viewBox='0 0 20 20' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23fff' fill-opacity='0.15'%3E%3Ccircle cx='3' cy='3' r='1.5'/%3E%3C/g%3E%3C/svg%3E\")"}} />
                <div className="relative flex items-center justify-between flex-wrap gap-3">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-xl bg-white/20 backdrop-blur-sm flex items-center justify-center">
                      <Sparkles className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-white flex items-center gap-2" data-testid="dclic-boost-title">
                        Profil boosté par D'CLIC PRO
                        <span className="inline-flex items-center gap-1 bg-white/20 text-white text-xs px-2 py-0.5 rounded-full"><Check className="w-3 h-3" />Actif</span>
                      </h3>
                      <p className="text-emerald-100 text-sm mt-0.5">
                        {dimensions.length} dimension{dimensions.length > 1 ? "s" : ""} analysée{dimensions.length > 1 ? "s" : ""} — {dclicCompetences.length + dclicSkills.length} compétence{(dclicCompetences.length + dclicSkills.length) > 1 ? "s" : ""} identifiée{(dclicCompetences.length + dclicSkills.length) > 1 ? "s" : ""}
                      </p>
                    </div>
                  </div>
                  <Badge className="bg-white/20 text-white border-0 text-sm px-3 py-1">
                    <Zap className="w-4 h-4 mr-1" />+{totalApports} apports au profil
                  </Badge>
                </div>
              </div>

              <CardContent className="p-5 space-y-5">
                {/* Dimensions grid */}
                {dimensions.length > 0 && (
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3" data-testid="dclic-dimensions-grid">
                    {dimensions.map((dim, idx) => {
                      const DIcon = dim.icon;
                      return (
                        <div key={idx} className="relative overflow-hidden rounded-xl border border-slate-100 p-4 text-center hover:shadow-md transition-shadow" data-testid={`dclic-dim-${idx}`}>
                          <div className={`absolute inset-0 bg-gradient-to-br ${dim.gradient} opacity-5`} />
                          <div className="relative">
                            <div className={`w-10 h-10 mx-auto mb-2 rounded-lg bg-gradient-to-br ${dim.gradient} flex items-center justify-center`}>
                              <DIcon className="w-5 h-5 text-white" />
                            </div>
                            <p className="text-xs text-slate-500 mb-1">{dim.label}</p>
                            <p className="text-xl font-bold text-slate-900">{dim.value}</p>
                            <p className="text-[10px] text-slate-400 mt-0.5">{dim.desc}</p>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}

                {/* Competences badges */}
                {dclicCompetences.length > 0 && (
                  <div>
                    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                      <Award className="w-3.5 h-3.5" />Compétences fortes révélées par D'CLIC
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {dclicCompetences.map((c, i) => (
                        <Badge key={i} className="bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs px-3 py-1" data-testid={`dclic-comp-${i}`}>
                          <Sparkles className="w-3 h-3 mr-1 opacity-60" />{c}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {/* Skills with levels */}
                {dclicSkills.length > 0 && (
                  <div>
                    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                      <Zap className="w-3.5 h-3.5" />Skills importés D'CLIC PRO
                    </p>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {dclicSkills.map((s, i) => (
                        <div key={i} className="flex items-center gap-3 bg-slate-50 rounded-lg px-3 py-2" data-testid={`dclic-skill-${i}`}>
                          <span className="text-sm font-medium text-slate-700 flex-1">{s.name}</span>
                          <div className="w-20">
                            <Progress value={(s.declared_level || s.level || 0) * 20} className="h-1.5 [&>div]:bg-emerald-500" />
                          </div>
                          <span className="text-xs text-slate-500 w-8 text-right">{(s.declared_level || s.level || 0) * 20}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Impact summary */}
                <div className="flex items-center gap-3 bg-emerald-50 border border-emerald-100 rounded-xl px-4 py-3" data-testid="dclic-impact-summary">
                  <div className="w-8 h-8 rounded-lg bg-emerald-100 flex items-center justify-center shrink-0">
                    <TrendingUp className="w-4 h-4 text-emerald-600" />
                  </div>
                  <p className="text-sm text-emerald-800">
                    <span className="font-semibold">Impact D'CLIC PRO :</span> Votre profil est enrichi de{" "}
                    {totalApports} élément{totalApports > 1 ? "s" : ""} supplémentaire{totalApports > 1 ? "s" : ""}. Les recruteurs et accompagnateurs voient un profil plus complet et crédibilisé.
                  </p>
                </div>
              </CardContent>
            </Card>
          );
        }

        // NOT imported — invite banner
        return (
          <Card className="border-0 shadow-lg overflow-hidden" data-testid="dclic-boost-invite-profil">
            <div className="bg-gradient-to-br from-indigo-600 via-violet-600 to-purple-700 p-5 relative">
              <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0iTTM2IDM0djItSDI0di0yaDEyek0zNiAyNHYySDI0di0yaDEyeiIvPjwvZz48L2c+PC9zdmc+')] opacity-30" />
              <div className="relative flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-2xl bg-white/20 backdrop-blur-sm flex items-center justify-center shrink-0">
                    <Zap className="w-6 h-6 text-yellow-300" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white" style={{ fontFamily: 'Outfit, sans-serif' }}>Boostez votre profil avec D'CLIC PRO</h3>
                    <p className="text-indigo-100 text-sm mt-1 max-w-lg">
                      Découvrez votre personnalité professionnelle et valorisez vos compétences avec un profil crédibilisé.
                    </p>
                    <div className="flex flex-wrap gap-2 mt-2">
                      <span className="inline-flex items-center gap-1 bg-white/15 text-white text-xs px-2 py-0.5 rounded-full backdrop-blur-sm"><User className="w-3 h-3" />Personnalité</span>
                      <span className="inline-flex items-center gap-1 bg-white/15 text-white text-xs px-2 py-0.5 rounded-full backdrop-blur-sm"><Target className="w-3 h-3" />Orientation</span>
                      <span className="inline-flex items-center gap-1 bg-white/15 text-white text-xs px-2 py-0.5 rounded-full backdrop-blur-sm"><Award className="w-3 h-3" />Compétences validées</span>
                      <span className="inline-flex items-center gap-1 bg-white/15 text-white text-xs px-2 py-0.5 rounded-full backdrop-blur-sm"><Sparkles className="w-3 h-3" />Carte Pro</span>
                    </div>
                  </div>
                </div>
                <Button className="bg-white text-indigo-700 hover:bg-indigo-50 shrink-0 text-sm font-bold shadow-lg px-6 py-3 h-auto" data-testid="dclic-test-btn-profil"
                  onClick={() => window.open('/test-dclic', '_blank', 'noopener,noreferrer')}>
                  <Play className="w-5 h-5 mr-2" />Passer le test
                </Button>
              </div>
            </div>
          </Card>
        );
      })()}

      {/* Completeness + Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        <Card className="lg:col-span-2 bg-gradient-to-br from-[#1e3a5f] to-[#2d5a8e] text-white border-0">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold">Complétude du passeport</h3>
                <p className="text-blue-200 text-sm">Enrichissez votre profil pour de meilleures recommandations</p>
              </div>
              <div className="text-4xl font-bold">{completeness_score}%</div>
            </div>
            <Progress value={completeness_score} className="h-3 bg-white/20" />
            <div className="flex flex-wrap gap-3 mt-4">
              {Object.entries(sources_count).map(([src, count]) => {
                const config = SOURCE_CONFIG[src] || SOURCE_CONFIG.declaratif;
                return (
                  <div key={src} className="flex items-center gap-1 text-sm text-blue-100">
                    <config.icon className="w-3 h-3" />
                    <span>{config.label}: {count}</span>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
        <StatCard icon={Layers} value={competences.length} label="Compétences" sublabel={`${savoirFaire.length} savoir-faire / ${savoirEtre.length} savoir-être`} color="bg-blue-600" />
        <StatCard icon={Briefcase} value={experiences.length} label="Expériences" sublabel={`${(passport?.formations || []).length} formations`} color="bg-emerald-600" />
      </div>

      {/* Main Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="flex flex-wrap gap-1 h-auto p-1 bg-slate-100">
          {(!viewMode || viewMode === "profil") && (
            <TabsTrigger value="profile" className="text-xs sm:text-sm py-2" data-testid="passport-tab-profile">
              <User className="w-4 h-4 mr-1 hidden sm:inline" />Profil
            </TabsTrigger>
          )}
          {(!viewMode || viewMode === "competences") && (
            <TabsTrigger value="competences" className="text-xs sm:text-sm py-2" data-testid="passport-tab-competences">
              <Star className="w-4 h-4 mr-1 hidden sm:inline" />Inventaire
            </TabsTrigger>
          )}
          {(!viewMode || viewMode === "competences") && (
            <TabsTrigger value="evaluation" className="text-xs sm:text-sm py-2" data-testid="passport-tab-evaluation">
              <Activity className="w-4 h-4 mr-1 hidden sm:inline" />Évaluation
            </TabsTrigger>
          )}
          {(!viewMode || viewMode === "competences") && (
            <TabsTrigger value="archeologie" className="text-xs sm:text-sm py-2" data-testid="passport-tab-archeologie">
              <Layers className="w-4 h-4 mr-1 hidden sm:inline" />Archéologie
            </TabsTrigger>
          )}
          {(!viewMode || viewMode === "competences") && (
            <TabsTrigger value="emerging" className="text-xs sm:text-sm py-2" data-testid="passport-tab-emerging">
              <Sparkles className="w-4 h-4 mr-1 hidden sm:inline" />Émergentes
            </TabsTrigger>
          )}
          {(!viewMode || viewMode === "profil") && (
            <TabsTrigger value="experiences" className="text-xs sm:text-sm py-2" data-testid="passport-tab-experiences">
              <Briefcase className="w-4 h-4 mr-1 hidden sm:inline" />Expériences
            </TabsTrigger>
          )}
          {(!viewMode || viewMode === "profil") && (
            <TabsTrigger value="formations" className="text-xs sm:text-sm py-2" data-testid="passport-tab-formations">
              <GraduationCap className="w-4 h-4 mr-1 hidden sm:inline" />Formations
            </TabsTrigger>
          )}
          {(!viewMode || viewMode === "profil") && (
            <TabsTrigger value="passerelles" className="text-xs sm:text-sm py-2" data-testid="passport-tab-passerelles">
              <Compass className="w-4 h-4 mr-1 hidden sm:inline" />Passerelles
            </TabsTrigger>
          )}
          {(!viewMode || viewMode === "profil") && (
            <TabsTrigger value="profil_dynamique" className="text-xs sm:text-sm py-2" data-testid="passport-tab-dynamique">
              <TrendingUp className="w-4 h-4 mr-1 hidden sm:inline" />Profil Dynamique
            </TabsTrigger>
          )}
        </TabsList>

        {/* Data loading indicator - shown when passport is empty (CV data still propagating) */}
        {passportEmpty && (
          <div className="mt-3 bg-blue-50 border border-blue-200 rounded-xl p-4 flex items-center gap-3 animate-pulse" data-testid="passport-data-loading">
            <Loader2 className="w-6 h-6 text-blue-600 animate-spin shrink-0" />
            <div>
              <p className="text-sm font-semibold text-blue-800">Chargement des données en cours...</p>
              <p className="text-xs text-blue-600">Vos expériences, compétences et savoir-être issus de l'analyse CV sont en cours d'intégration dans votre passeport. Veuillez patienter quelques instants.</p>
            </div>
          </div>
        )}

        {/* Profile Tab */}
        <TabsContent value="profile" className="space-y-4 mt-4">
          <ProfileSection
            passport={passport}
            editing={editingProfile}
            profileEdit={profileEdit}
            setProfileEdit={setProfileEdit}
            onStartEdit={handleStartEditProfile}
            onSave={handleSaveProfile}
            onCancel={() => setEditingProfile(false)}
            refreshingDynamic={refreshingDynamic}
            dclicProfile={dclicProfile}
            onRefreshProfile={async () => {
              try {
                setRefreshingDynamic(true);
                const res = await axios.post(`${API}/passport/refresh-dynamic-profile?token=${token}`);
                if (res.data.success) {
                  setPassport(prev => ({
                    ...prev,
                    motivations: res.data.motivations,
                    compatible_environments: res.data.compatible_environments,
                    professional_summary: res.data.professional_summary || prev.professional_summary,
                    career_project: res.data.career_project || prev.career_project,
                    dynamic_profile: {
                      strengths_synthesis: res.data.strengths_synthesis,
                      evolution_axes: res.data.evolution_axes,
                      motivations: res.data.motivations,
                      compatible_environments: res.data.compatible_environments,
                      last_refreshed: new Date().toISOString(),
                      source: "dclic_pro",
                    }
                  }));
                  setProfileEdit(prev => ({
                    ...prev,
                    motivations: (res.data.motivations || []).join(", "),
                    compatible_environments: (res.data.compatible_environments || []).join(", "),
                    professional_summary: res.data.professional_summary || prev.professional_summary,
                    career_project: res.data.career_project || prev.career_project,
                  }));
                  toast.success("Profil actualisé avec les données CV et D'CLIC PRO");
                }
              } catch (e) {
                toast.error(e?.response?.data?.detail || "Passez le test D'CLIC PRO d'abord");
              } finally { setRefreshingDynamic(false); }
            }}
          />
          {/* S.A.R.E Method Banner in Profile */}
          {savoirEtre.length > 0 && (() => {
            const illustratedSet = new Set(illustrations.map(i => i.soft_skill));
            const unproven = savoirEtre.filter(c => !illustratedSet.has(c.name));
            return unproven.length > 0 ? (
              <Card className="border-amber-200 bg-gradient-to-r from-amber-50 to-orange-50 shadow-sm" data-testid="sare-profile-banner">
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 rounded-xl bg-amber-100 flex items-center justify-center shrink-0">
                      <Award className="w-5 h-5 text-amber-700" />
                    </div>
                    <div className="flex-1">
                      <h4 className="text-sm font-bold text-amber-900">Prouvez vos savoir-être avec la méthode S.A.R.E</h4>
                      <p className="text-xs text-amber-700 mt-1 leading-relaxed">
                        Dire "je suis organisé" reste déclaratif. Ce qui fait la différence en recrutement : <span className="font-semibold">une situation concrète qui démontre votre compétence en action.</span> Rendez-vous dans l'onglet <span className="font-semibold">Expériences</span> pour prouver vos compétences (soft et hard skills).
                      </p>
                      <div className="flex items-center gap-4 mt-2">
                        <div className="flex items-center gap-1.5 text-xs text-amber-800">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                          <span className="font-medium">{illustrations.length} prouvé{illustrations.length > 1 ? "s" : ""}</span>
                        </div>
                        <div className="flex items-center gap-1.5 text-xs text-amber-800">
                          <Target className="w-3.5 h-3.5 text-amber-600" />
                          <span className="font-medium">{unproven.length} restant{unproven.length > 1 ? "s" : ""}</span>
                        </div>
                      </div>
                      <div className="flex flex-wrap gap-1 mt-2">
                        {unproven.slice(0, 5).map((c, i) => (
                          <Badge key={i} className="bg-amber-100 text-amber-800 text-[10px] border border-amber-200">{c.name}</Badge>
                        ))}
                        {unproven.length > 5 && <Badge className="bg-amber-100 text-amber-600 text-[10px]">+{unproven.length - 5}</Badge>}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <Card className="border-emerald-200 bg-emerald-50 shadow-sm" data-testid="sare-profile-complete">
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-emerald-100 flex items-center justify-center shrink-0">
                    <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-emerald-800">Tous vos savoir-être sont prouvés S.A.R.E</h4>
                    <p className="text-xs text-emerald-600">{illustrations.length} illustration{illustrations.length > 1 ? "s" : ""} concrète{illustrations.length > 1 ? "s" : ""} — Votre profil est crédibilisé pour les recruteurs.</p>
                  </div>
                </CardContent>
              </Card>
            );
          })()}
        </TabsContent>
        <TabsContent value="competences" className="space-y-6 mt-4">
          {/* ADN Professionnel - en haut de l'inventaire */}
          <IdentityAdnBlock token={token} passport={passport} setPassport={setPassport} />

          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-slate-900">Mes compétences ({competences.length})</h3>
            <Dialog open={addCompDialogOpen} onOpenChange={setAddCompDialogOpen}>
              <DialogTrigger asChild>
                <Button size="sm" data-testid="add-competence-btn"><Plus className="w-4 h-4 mr-1" />Ajouter</Button>
              </DialogTrigger>
              <DialogContent className="max-w-lg max-h-[85vh] overflow-y-auto">
                <DialogHeader><DialogTitle>Ajouter une compétence</DialogTitle></DialogHeader>
                <AddCompetenceForm newComp={newComp} setNewComp={setNewComp} onSubmit={handleAddCompetence} />
              </DialogContent>
            </Dialog>
          </div>

          {/* D'CLIC boost banner for competences */}
          {dclicProfile?.dclic_imported && (dclicProfile.dclic_competences?.length > 0) && (() => {
            const dclicNames = new Set((dclicProfile.dclic_competences || []).map(n => n.toLowerCase()));
            const dclicInPassport = competences.filter(c => dclicNames.has((c.name || "").toLowerCase()));
            return (
              <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-100 rounded-lg px-3 py-2 text-xs text-emerald-700" data-testid="inventaire-dclic-boost">
                <Sparkles className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
                <span>D'CLIC PRO a enrichi vos soft skills : {dclicInPassport.length > 0 ? `${dclicInPassport.length} compétence${dclicInPassport.length > 1 ? "s" : ""} comportementale${dclicInPassport.length > 1 ? "s" : ""} (${dclicProfile.dclic_competences.slice(0, 3).join(", ")}${dclicProfile.dclic_competences.length > 3 ? "..." : ""})` : `${dclicProfile.dclic_competences.length} compétence${dclicProfile.dclic_competences.length > 1 ? "s" : ""} identifiée${dclicProfile.dclic_competences.length > 1 ? "s" : ""}`} issues de votre profil D'CLIC PRO.</span>
              </div>
            );
          })()}

          {/* Nature distribution bar */}
          {competences.length > 0 && (
            <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-xl">
              <div className="flex items-center gap-2 text-sm">
                <Briefcase className="w-4 h-4 text-sky-600" />
                <span className="font-medium text-sky-700">Savoir-faire: {savoirFaire.length}</span>
              </div>
              <div className="flex-1 h-3 bg-slate-200 rounded-full overflow-hidden flex">
                <div className="h-full bg-sky-500 transition-all" style={{ width: `${competences.length ? (savoirFaire.length / competences.length) * 100 : 0}%` }} />
                <div className="h-full bg-rose-400 transition-all" style={{ width: `${competences.length ? (savoirEtre.length / competences.length) * 100 : 0}%` }} />
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Activity className="w-4 h-4 text-rose-500" />
                <span className="font-medium text-rose-600">Savoir-être: {savoirEtre.length}</span>
              </div>
              {nonClassees.length > 0 && (
                <Badge variant="outline" className="text-xs text-slate-500">{nonClassees.length} non classées</Badge>
              )}
            </div>
          )}

          {/* Savoir-faire section */}
          {savoirFaire.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-3">
                <Briefcase className="w-4 h-4 text-sky-600" />
                <h4 className="font-medium text-sky-700">Savoir-faire (Hard Skills)</h4>
                <Badge className="bg-sky-100 text-sky-700 text-xs">{savoirFaire.length}</Badge>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {savoirFaire.map(comp => (
                  <CompetenceCard key={comp.id} comp={comp} onDelete={handleDeleteCompetence} onEvaluate={handleOpenEvaluation} />
                ))}
              </div>
            </div>
          )}

          {/* Savoir-être section */}
          {savoirEtre.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-3">
                <Activity className="w-4 h-4 text-rose-500" />
                <h4 className="font-medium text-rose-600">Savoir-être (Soft Skills)</h4>
                <Badge className="bg-rose-100 text-rose-600 text-xs">{savoirEtre.length}</Badge>
                {dclicProfile?.dclic_imported && (() => {
                  const dclicNames = new Set((dclicProfile.dclic_competences || []).map(n => n.toLowerCase()));
                  const dclicSE = savoirEtre.filter(c => dclicNames.has((c.name || "").toLowerCase()));
                  return dclicSE.length > 0 ? (
                    <Badge className="bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs ml-auto" data-testid="soft-skills-dclic-badge">
                      <Sparkles className="w-3 h-3 mr-1" />+{dclicSE.length} via D'CLIC PRO
                    </Badge>
                  ) : null;
                })()}
              </div>
              {dclicProfile?.dclic_imported && (
                <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-100 rounded-lg px-3 py-2 mb-3 text-xs text-emerald-700" data-testid="soft-skills-dclic-boost">
                  <Sparkles className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
                  <span>D'CLIC PRO a enrichi vos soft skills en révélant des compétences comportementales issues de votre profil de personnalité.</span>
                </div>
              )}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {savoirEtre.map(comp => (
                  <CompetenceCard key={comp.id} comp={comp} onDelete={handleDeleteCompetence} onEvaluate={handleOpenEvaluation} />
                ))}
              </div>
            </div>
          )}

          {/* Non-classées */}
          {nonClassees.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-3">
                <CircleDot className="w-4 h-4 text-slate-400" />
                <h4 className="font-medium text-slate-500">Non classées</h4>
                <Badge variant="outline" className="text-xs">{nonClassees.length}</Badge>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {nonClassees.map(comp => (
                  <CompetenceCard key={comp.id} comp={comp} onDelete={handleDeleteCompetence} onEvaluate={handleOpenEvaluation} />
                ))}
              </div>
            </div>
          )}

          {competences.length === 0 && <EmptyState text="Ajoutez vos compétences pour enrichir votre passeport" />}
        </TabsContent>

        {/* Evaluation Tab (Lamri & Lubart + CCSP) */}
        <TabsContent value="evaluation" className="space-y-6 mt-4">
          <EvaluationTab
            competences={competences}
            diagnostic={diagnostic}
            loadingDiagnostic={loadingDiagnostic}
            onLoadDiagnostic={loadDiagnostic}
            onEvaluate={handleOpenEvaluation}
            dclicProfile={dclicProfile}
          />
        </TabsContent>

        {/* Archéologie Tab (NEW) */}
        <TabsContent value="archeologie" className="space-y-6 mt-4">
          <ArcheologieTab
            archeologie={archeologie}
            loading={loadingArcheologie}
            onLoad={loadArcheologie}
            savoirFaire={savoirFaire}
            savoirEtre={savoirEtre}
            nonClassees={nonClassees}
            dclicProfile={dclicProfile}
          />
        </TabsContent>

        {/* Emerging Competences Tab */}
        <TabsContent value="emerging" className="space-y-4 mt-4">
          <EmergingTab competences={emergingFromApi} loading={loadingEmerging} onRefresh={loadEmerging} token={token} />
        </TabsContent>

        {/* Experiences Tab */}
        <TabsContent value="experiences" className="space-y-4 mt-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-slate-900">Expériences et réalisations ({experiences.length})</h3>
            <Dialog open={addExpDialogOpen} onOpenChange={setAddExpDialogOpen}>
              <DialogTrigger asChild>
                <Button size="sm" data-testid="add-experience-btn"><Plus className="w-4 h-4 mr-1" />Ajouter</Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader><DialogTitle>Ajouter une expérience</DialogTitle></DialogHeader>
                <div className="space-y-3">
                  <Input placeholder="Titre du poste / mission" value={newExp.title} onChange={e => setNewExp({...newExp, title: e.target.value})} data-testid="exp-title-input" />
                  <Input placeholder="Organisation" value={newExp.organization} onChange={e => setNewExp({...newExp, organization: e.target.value})} />
                  <Input placeholder="Description" value={newExp.description} onChange={e => setNewExp({...newExp, description: e.target.value})} />
                  <Input placeholder="Compétences utilisées (séparées par des virgules)" value={newExp.skills_used} onChange={e => setNewExp({...newExp, skills_used: e.target.value})} />
                  <Input placeholder="Réalisations clés (séparées par des virgules)" value={newExp.achievements} onChange={e => setNewExp({...newExp, achievements: e.target.value})} />
                  <Select value={newExp.experience_type} onValueChange={v => setNewExp({...newExp, experience_type: v})}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="professionnel">Professionnel</SelectItem>
                      <SelectItem value="personnel">Personnel</SelectItem>
                      <SelectItem value="benevole">Bénévole</SelectItem>
                      <SelectItem value="projet">Projet</SelectItem>
                    </SelectContent>
                  </Select>
                  <Button className="w-full" onClick={handleAddExperience} data-testid="submit-experience-btn">
                    <Check className="w-4 h-4 mr-2" />Ajouter l'expérience
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
          {/* Soft skills progress tracker */}
          {(() => {
            const allSoftSkills = [...new Set([
              ...(dclicProfile?.dclic_competences || []),
              ...(competences || []).filter(c => c.nature === "savoir_etre").map(c => c.name),
            ])];
            const illustratedSet = new Set(illustrations.filter(i => i.skill_type !== "hard").map(i => i.soft_skill));
            const illustratedCount = allSoftSkills.filter(s => illustratedSet.has(s)).length;
            return allSoftSkills.length > 0 ? (
              <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-xl" data-testid="soft-skills-progress">
                <Sparkles className="w-4 h-4 text-emerald-600 shrink-0" />
                <div className="flex-1">
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="font-medium text-slate-700">Soft skills prouvés par la méthode S.A.R.E</span>
                    <span className={`font-bold ${illustratedCount === allSoftSkills.length ? "text-emerald-600" : "text-slate-500"}`}>{illustratedCount}/{allSoftSkills.length}</span>
                  </div>
                  <Progress value={(illustratedCount / allSoftSkills.length) * 100} className="h-1.5" />
                </div>
                {illustratedCount === allSoftSkills.length && <Badge className="bg-emerald-100 text-emerald-700 text-[10px]">Complet</Badge>}
              </div>
            ) : null;
          })()}
          {/* Hard skills progress tracker */}
          {(() => {
            const allHardSkills = [...new Set((competences || []).filter(c => c.nature === "savoir_faire").map(c => c.name))];
            const illustratedSet = new Set(illustrations.filter(i => i.skill_type === "hard").map(i => i.soft_skill));
            const illustratedCount = allHardSkills.filter(s => illustratedSet.has(s)).length;
            return allHardSkills.length > 0 ? (
              <div className="flex items-center gap-3 p-3 bg-sky-50 rounded-xl" data-testid="hard-skills-progress">
                <Target className="w-4 h-4 text-sky-600 shrink-0" />
                <div className="flex-1">
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="font-medium text-slate-700">Hard skills prouvés par la méthode S.A.R.E</span>
                    <span className={`font-bold ${illustratedCount === allHardSkills.length ? "text-sky-600" : "text-slate-500"}`}>{illustratedCount}/{allHardSkills.length}</span>
                  </div>
                  <Progress value={(illustratedCount / allHardSkills.length) * 100} className="h-1.5" />
                </div>
                {illustratedCount === allHardSkills.length && <Badge className="bg-sky-100 text-sky-700 text-[10px]">Complet</Badge>}
              </div>
            ) : null;
          })()}
          <div className="space-y-3">
            {experiences.map(exp => (
              <ExperienceCard
                key={exp.id}
                exp={exp}
                onDelete={handleDeleteExperience}
                softSkills={[...new Set([...(dclicProfile?.dclic_competences || []), ...(competences || []).filter(c => c.nature === "savoir_etre").map(c => c.name)])]}
                hardSkills={[...new Set((competences || []).filter(c => c.nature === "savoir_faire").map(c => c.name))]}
                illustrations={illustrations}
                token={token}
                onIllustrationSaved={loadIllustrations}
              />
            ))}
          </div>
          {experiences.length === 0 && <EmptyState text="Ajoutez vos expériences professionnelles et personnelles" />}
        </TabsContent>

        {/* Formations / Certifications Tab */}
        <TabsContent value="formations" className="space-y-4 mt-4">
          <h3 className="font-semibold text-slate-900">
            Formations et Certifications ({(passport?.formations || []).length + (dclicProfile?.dclic_imported ? 1 : 0)})
          </h3>

          {/* Toggle visibilité totale */}
          {(passport?.formations || []).length > 0 && (
            <div className="flex items-center justify-between bg-slate-50 rounded-xl px-4 py-3" data-testid="formations-visibility-toggle-all">
              <div className="flex items-center gap-2">
                <Eye className="w-4 h-4 text-[#1e3a5f]" />
                <span className="text-sm font-medium text-slate-800">Visibilité totale</span>
                <span className="text-xs text-slate-500">— Rendre toutes les formations visibles</span>
              </div>
              <Switch
                checked={(passport?.formations || []).length > 0 && (passport?.formations || []).every(f => f.visibility === "public")}
                onCheckedChange={async (checked) => {
                  const newVis = checked ? "public" : "private";
                  try {
                    await axios.put(`${API}/passport/formations/visibility-all?token=${token}`, { visibility: newVis });
                    setPassport(prev => ({
                      ...prev,
                      formations: (prev.formations || []).map(f => ({ ...f, visibility: newVis }))
                    }));
                    toast.success(checked ? "Toutes les formations sont visibles" : "Toutes les formations sont privées");
                  } catch { toast.error("Erreur de mise à jour"); }
                }}
                data-testid="toggle-all-formations-visibility"
              />
            </div>
          )}

          {/* D'CLIC PRO certification */}
          {dclicProfile?.dclic_imported && (
            <Card className="border-l-4 border-l-emerald-500" data-testid="dclic-certification-card">
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 rounded-xl bg-emerald-100 flex items-center justify-center shrink-0">
                      <Award className="w-5 h-5 text-emerald-600" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-slate-900">Test D'CLIC PRO</h4>
                      <p className="text-sm text-slate-500">Ré'Actif Pro — Certification complétée</p>
                      {dclicProfile.dclic_competences?.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-2">
                          {dclicProfile.dclic_competences.slice(0, 5).map((c, i) => (
                            <Badge key={i} className="bg-emerald-50 text-emerald-700 text-xs">{c}</Badge>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                  <Badge className="bg-emerald-100 text-emerald-700">Certification</Badge>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Formations from CV */}
          {(passport?.formations || []).map((f, idx) => {
            const typeConfig = {
              diplome: { color: "border-l-blue-400", bg: "bg-blue-100", icon: "text-blue-600", badge: "bg-blue-50 text-blue-700", label: "Diplôme" },
              certification: { color: "border-l-amber-400", bg: "bg-amber-100", icon: "text-amber-600", badge: "bg-amber-50 text-amber-700", label: "Certification" },
              stage_formation: { color: "border-l-purple-400", bg: "bg-purple-100", icon: "text-purple-600", badge: "bg-purple-50 text-purple-700", label: "Formation" },
            };
            const cfg = typeConfig[f.type] || typeConfig.diplome;
            const isVisible = f.visibility === "public";
            return (
            <Card key={f.id || idx} className={`border-l-4 ${cfg.color}`} data-testid={`formation-card-${idx}`}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    <div className={`w-10 h-10 rounded-xl ${cfg.bg} flex items-center justify-center shrink-0`}>
                      <GraduationCap className={`w-5 h-5 ${cfg.icon}`} />
                    </div>
                    <div>
                      <h4 className="font-semibold text-slate-900">{f.diplome}</h4>
                      <p className="text-sm text-slate-500">
                        {f.etablissement}{f.annee ? ` — ${f.annee}` : ""}
                      </p>
                      {f.domaine && <Badge variant="outline" className="text-xs mt-1">{f.domaine}</Badge>}
                    </div>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <Badge className={`${cfg.badge} text-xs`}>{cfg.label}</Badge>
                    <button
                      onClick={async (e) => {
                        e.stopPropagation();
                        const newVis = isVisible ? "private" : "public";
                        try {
                          await axios.put(`${API}/passport/formations/${f.id}/visibility?token=${token}`, { visibility: newVis });
                          setPassport(prev => ({
                            ...prev,
                            formations: prev.formations.map(fm => fm.id === f.id ? { ...fm, visibility: newVis } : fm)
                          }));
                        } catch { toast.error("Erreur"); }
                      }}
                      className={`p-1.5 rounded-full transition-colors ${isVisible ? "bg-emerald-100 text-emerald-600 hover:bg-emerald-200" : "bg-slate-100 text-slate-400 hover:bg-slate-200"}`}
                      title={isVisible ? "Visible" : "Privé"}
                      data-testid={`formation-visibility-${idx}`}
                    >
                      {isVisible ? <Eye className="w-3.5 h-3.5" /> : <EyeOff className="w-3.5 h-3.5" />}
                    </button>
                  </div>
                </div>
              </CardContent>
            </Card>
            );
          })}

          {(passport?.formations || []).length === 0 && !dclicProfile?.dclic_imported && (
            <EmptyState text="Vos formations et certifications apparaîtront ici après l'analyse de votre CV ou la complétion du test D'CLIC PRO" />
          )}
        </TabsContent>

        {/* Learning Path Tab */}
        <TabsContent value="learning" className="space-y-4 mt-4">
          <h3 className="font-semibold text-slate-900">Parcours d'apprentissage ({learning_path.length})</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {learning_path.map((item, idx) => (
              <LearningCard key={idx} item={item} />
            ))}
          </div>
          {learning_path.length === 0 && <EmptyState text="Les formations suivies apparaîtront ici automatiquement" />}
        </TabsContent>

        {/* Passerelles Tab */}
        <TabsContent value="passerelles" className="space-y-4 mt-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-slate-900">Passerelles professionnelles</h3>
              <p className="text-sm text-slate-500">Métiers compatibles avec votre profil, identifiés par l'IA</p>
            </div>
            <Button onClick={handleLoadPasserelles} disabled={loadingPasserelles} data-testid="load-passerelles-btn">
              {loadingPasserelles ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Brain className="w-4 h-4 mr-2" />}
              {loadingPasserelles ? "Analyse IA en cours..." : passerelles.length > 0 ? "Actualiser l'analyse" : "Analyser mon profil"}
            </Button>
          </div>

          {loadingPasserelles && passerelles.length === 0 && (
            <div className="flex items-center gap-3 p-6 bg-blue-50 rounded-xl border border-blue-100">
              <div className="w-6 h-6 border-2 border-blue-300 border-t-blue-600 rounded-full animate-spin" />
              <div>
                <span className="text-sm font-medium text-blue-700">L'IA analyse votre profil et votre CV...</span>
                <p className="text-xs text-blue-500 mt-0.5">Identification des passerelles professionnelles en cours</p>
              </div>
            </div>
          )}

          <div className="space-y-3">
            {passerelles.map((p, idx) => (
              <PasserelleCard key={idx} passerelle={p} />
            ))}
          </div>
          {passerelles.length === 0 && !loadingPasserelles && competences.length === 0 && (
            <EmptyState text="Analysez votre CV dans l'onglet 'Tableau de bord' pour générer automatiquement les passerelles professionnelles" />
          )}
          {passerelles.length === 0 && !loadingPasserelles && competences.length > 0 && (
            <EmptyState text="Cliquez sur 'Analyser mon profil' pour découvrir vos passerelles professionnelles" />
          )}
        </TabsContent>

        {/* Profil Dynamique Tab - 7 Dimensions */}
        <TabsContent value="profil_dynamique" className="space-y-4 mt-4">
          <div className="bg-gradient-to-r from-[#1e3a5f] to-[#2a5a8f] text-white rounded-xl p-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-bold text-base">Profil Dynamique — 7 Dimensions</h3>
                <p className="text-xs text-white/70 mt-1">Vision nouvelle generation : au-dela du CV classique, un profil base sur le potentiel, les preuves et les valeurs.</p>
                {passport?.dynamic_profile?.last_refreshed && (
                  <p className="text-[10px] text-white/50 mt-1">Dernière actualisation : {new Date(passport.dynamic_profile.last_refreshed).toLocaleDateString("fr-FR")}</p>
                )}
              </div>
              <button
                onClick={async () => {
                  try {
                    setRefreshingDynamic(true);
                    const res = await axios.post(`${API}/passport/refresh-dynamic-profile?token=${token}`);
                    if (res.data.success) {
                      setPassport(prev => ({
                        ...prev,
                        motivations: res.data.motivations,
                        compatible_environments: res.data.compatible_environments,
                        professional_summary: res.data.professional_summary,
                        career_project: res.data.career_project,
                        dynamic_profile: {
                          strengths_synthesis: res.data.strengths_synthesis,
                          evolution_axes: res.data.evolution_axes,
                          motivations: res.data.motivations,
                          compatible_environments: res.data.compatible_environments,
                          last_refreshed: new Date().toISOString(),
                          source: "dclic_pro",
                        }
                      }));
                      // Sync profileEdit so Profile tab inputs reflect new data
                      setProfileEdit(prev => ({
                        ...prev,
                        motivations: (res.data.motivations || []).join(", "),
                        compatible_environments: (res.data.compatible_environments || []).join(", "),
                        professional_summary: res.data.professional_summary || prev.professional_summary,
                        career_project: res.data.career_project || prev.career_project,
                      }));
                      toast.success("Profil dynamique actualisé avec les données D'CLIC PRO");
                    }
                  } catch (e) {
                    toast.error(e?.response?.data?.detail || "Passez le test D'CLIC PRO d'abord");
                  } finally { setRefreshingDynamic(false); }
                }}
                disabled={refreshingDynamic}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/20 hover:bg-white/30 text-white text-sm font-medium transition-all disabled:opacity-50 shrink-0"
                data-testid="refresh-dynamic-profile-btn"
              >
                <RefreshCw className={`w-4 h-4 ${refreshingDynamic ? "animate-spin" : ""}`} />
                {refreshingDynamic ? "Actualisation..." : "Actualiser"}
              </button>
            </div>
          </div>

          {/* Portfolio PDF Download */}
          {dclicProfile?.dclic_imported && (
            <div className="flex items-center justify-between bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 rounded-xl p-4" data-testid="portfolio-pdf-section">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-amber-100 flex items-center justify-center shrink-0">
                  <Award className="w-5 h-5 text-amber-700" />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-amber-900">Portfolio de Compétences Prouvées</h4>
                  <p className="text-xs text-amber-700">PDF professionnel : profil D'CLIC PRO + preuves S.A.R.E + compétences + parcours</p>
                </div>
              </div>
              <Button
                className="bg-[#1e3a5f] hover:bg-[#2a4a6f] text-white shrink-0"
                onClick={() => {
                  const url = `${API}/passport/portfolio-pdf?token=${token}`;
                  window.open(url, '_blank');
                }}
                data-testid="download-portfolio-pdf-btn"
              >
                <FileDown className="w-4 h-4 mr-2" />
                Télécharger le PDF
              </Button>
            </div>
          )}

          {/* Score de confiance multi-dimensionnel */}
          <ConfidenceScoreWidget token={token} />

          {/* ADN Professionnel */}
          <IdentityAdnBlock token={token} passport={passport} setPassport={setPassport} />
          <div className="border border-slate-200 rounded-xl p-4 space-y-2" data-testid="dim-identite">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 text-xs font-bold">1</div>
              <h4 className="font-semibold text-sm text-slate-800">Tendance comportementale</h4>
              <Badge variant="outline" className="text-[10px]">Anonymisable</Badge>
            </div>
            <p className="text-xs text-slate-600 ml-8">{passport?.professional_summary || "Complétez votre profil ou chargez un CV pour remplir cette section"}</p>
            {dclicProfile?.dclic_profile?.integrated_analysis?.synthese && (
              <div className="ml-8 bg-blue-50 border border-blue-100 rounded-lg p-2.5">
                <p className="text-[10px] font-semibold text-blue-700 mb-0.5">Synthèse D'CLIC PRO</p>
                <p className="text-xs text-slate-700 leading-relaxed">{dclicProfile.dclic_profile.integrated_analysis.synthese}</p>
              </div>
            )}
            {dclicProfile?.dclic_competences?.length > 0 && (
              <div className="flex flex-wrap gap-1.5 ml-8">
                {dclicProfile.dclic_competences.map((c, i) => <Badge key={i} className="bg-blue-50 text-blue-700 border-blue-200 text-[10px]">{c}</Badge>)}
              </div>
            )}
            {passport?.target_sectors?.length > 0 && (
              <div className="flex flex-wrap gap-1 ml-8">{passport.target_sectors.map((s, i) => <Badge key={i} variant="secondary" className="text-[10px]">{s}</Badge>)}</div>
            )}
          </div>

          {/* 2. Intentions professionnelles */}
          <div className="border border-slate-200 rounded-xl p-4 space-y-2" data-testid="dim-intentions">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-700 text-xs font-bold">2</div>
              <h4 className="font-semibold text-sm text-slate-800">Intentions professionnelles</h4>
              {passport?.dynamic_profile?.source === "dclic_pro" && <Badge className="bg-emerald-50 text-emerald-700 text-[10px]">D'CLIC PRO</Badge>}
            </div>
            <div className="ml-8 space-y-1">
              <p className="text-xs text-slate-600"><span className="font-medium text-slate-700">Projet :</span> {passport?.career_project || "Non renseigné"}</p>
              {passport?.motivations?.length > 0 && (
                <div>
                  <span className="font-medium text-slate-700 text-xs">Motivations :</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {passport.motivations.map((m, i) => <Badge key={i} className="text-[10px] bg-emerald-50 text-emerald-700 border-emerald-200">{m}</Badge>)}
                  </div>
                </div>
              )}
              {passport?.compatible_environments?.length > 0 && (
                <div>
                  <span className="font-medium text-slate-700 text-xs">Environnement idéal :</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {passport.compatible_environments.map((e, i) => <Badge key={i} className="text-[10px] bg-blue-50 text-blue-700 border-blue-200">{e}</Badge>)}
                  </div>
                </div>
              )}
              {(!passport?.motivations?.length && !passport?.compatible_environments?.length) && (
                <p className="text-xs text-slate-400">Cliquez sur "Actualiser" pour enrichir cette section via D'CLIC PRO</p>
              )}
            </div>
          </div>

          {/* 3. Compétences avec preuves */}
          <div className="border border-slate-200 rounded-xl p-4 space-y-2" data-testid="dim-competences">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-full bg-violet-100 flex items-center justify-center text-violet-700 text-xs font-bold">3</div>
              <h4 className="font-semibold text-sm text-slate-800">{"Compétences opérationnelles avec preuves"}</h4>
              <Badge variant="secondary" className="text-[10px]">{competences.length}{" compétences"}</Badge>
            </div>
            <div className="ml-8 grid grid-cols-1 sm:grid-cols-2 gap-2">
              {savoirFaire.length > 0 && (
                <div>
                  <p className="text-[10px] font-semibold text-sky-700 mb-1">{"Savoir-faire (" + savoirFaire.length + ")"}</p>
                  {(expandedSkills.sf ? savoirFaire : savoirFaire.slice(0, 5)).map((c, i) => (
                    <div key={i} className="text-xs py-0.5">
                      <span className="text-slate-700">{c.name}</span>
                    </div>
                  ))}
                  {savoirFaire.length > 5 && (
                    <button onClick={() => setExpandedSkills(p => ({ ...p, sf: !p.sf }))} className="text-[10px] text-sky-600 hover:text-sky-800 hover:underline cursor-pointer mt-0.5">
                      {expandedSkills.sf ? "Réduire" : "+ " + (savoirFaire.length - 5) + " autres"}
                    </button>
                  )}
                </div>
              )}
              {savoirEtre.length > 0 && (
                <div>
                  <p className="text-[10px] font-semibold text-rose-600 mb-1">{"Savoir-être (" + savoirEtre.length + ")"}</p>
                  {(expandedSkills.se ? savoirEtre : savoirEtre.slice(0, 5)).map((c, i) => (
                    <div key={i} className="text-xs py-0.5">
                      <span className="text-slate-700">{c.name}</span>
                    </div>
                  ))}
                  {savoirEtre.length > 5 && (
                    <button onClick={() => setExpandedSkills(p => ({ ...p, se: !p.se }))} className="text-[10px] text-rose-500 hover:text-rose-700 hover:underline cursor-pointer mt-0.5">
                      {expandedSkills.se ? "Réduire" : "+ " + (savoirEtre.length - 5) + " autres"}
                    </button>
                  )}
                </div>
              )}
              {savoirFaire.length === 0 && savoirEtre.length === 0 && competences.length > 0 && (
                <div className="col-span-2">
                  <p className="text-xs text-slate-500">{"Chargez un CV pour classifier vos " + competences.length + " compétences en savoir-faire et savoir-être"}</p>
                </div>
              )}
              {competences.length === 0 && (
                <div className="col-span-2">
                  <p className="text-xs text-slate-400">{"Passez le test D'CLIC PRO ou chargez un CV pour remplir cette section"}</p>
                </div>
              )}
            </div>
          </div>

          {/* 4. Expériences en situations */}
          <div className="border border-slate-200 rounded-xl p-4 space-y-2" data-testid="dim-experiences">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-full bg-amber-100 flex items-center justify-center text-amber-700 text-xs font-bold">4</div>
              <h4 className="font-semibold text-sm text-slate-800">Expériences en situations</h4>
              <Badge variant="secondary" className="text-[10px]">{experiences.length}{" expériences"}</Badge>
            </div>
            <div className="ml-8 space-y-2">
              {experiences.slice(0, 3).map((exp, i) => (
                <div key={i} className="bg-slate-50 rounded-lg p-2">
                  <p className="text-xs font-semibold text-slate-800">{exp.title} — {exp.organization}</p>
                  {exp.description && <p className="text-[10px] text-slate-500 mt-0.5">{exp.description}</p>}
                  {exp.achievements?.length > 0 && (
                    <div className="mt-1">{exp.achievements.map((a, j) => <p key={j} className="text-[10px] text-emerald-700">→ {a}</p>)}</div>
                  )}
                </div>
              ))}
              {experiences.length > 3 && <p className="text-[10px] text-slate-400">{"+ " + (experiences.length - 3) + " autres expériences"}</p>}
              {experiences.length === 0 && <p className="text-xs text-slate-400">Chargez un CV pour remplir cette section</p>}
            </div>
          </div>

          {/* 5. Potentiel & evolution */}
          <div className="border border-slate-200 rounded-xl p-4 space-y-2" data-testid="dim-potentiel">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-full bg-cyan-100 flex items-center justify-center text-cyan-700 text-xs font-bold">5</div>
              <h4 className="font-semibold text-sm text-slate-800">Potentiel et capacités d'évolution</h4>
            </div>
            <div className="ml-8 space-y-2">
              {passport?.dynamic_profile?.strengths_synthesis && (
                <p className="text-xs text-slate-700 bg-cyan-50 rounded-lg p-2 italic">{passport.dynamic_profile.strengths_synthesis}</p>
              )}
              {passport?.dynamic_profile?.evolution_axes?.length > 0 ? (
                passport.dynamic_profile.evolution_axes.map((ax, i) => (
                  <div key={i} className="flex items-start gap-2 text-xs text-slate-600">
                    <TrendingUp className="w-3.5 h-3.5 text-cyan-600 mt-0.5 shrink-0" />
                    <span>{ax}</span>
                  </div>
                ))
              ) : passport?.learning_path?.length > 0 ? (
                passport.learning_path.slice(0, 3).map((l, i) => (
                  <div key={i} className="text-xs text-slate-600">
                    <span className="font-medium text-slate-700">{l.title}</span>
                    {l.reason && <span className="text-slate-400"> — {l.reason}</span>}
                  </div>
                ))
              ) : (
                <p className="text-xs text-slate-400">Cliquez sur "Actualiser" pour découvrir vos axes d'évolution</p>
              )}
            </div>
          </div>

          {/* 6. Valeurs & environnement */}
          <div className="border border-slate-200 rounded-xl p-4 space-y-2" data-testid="dim-valeurs">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-full bg-rose-100 flex items-center justify-center text-rose-700 text-xs font-bold">6</div>
              <h4 className="font-semibold text-sm text-slate-800">Valeurs et environnement de travail</h4>
            </div>
            <div className="ml-8">
              {passport?.compatible_environments?.length > 0 || passport?.motivations?.length > 0 ? (
                <div className="flex flex-wrap gap-1">
                  {passport?.motivations?.map((m, i) => <Badge key={`m-${i}`} className="text-[10px] bg-rose-50 text-rose-700 border-rose-200">{m}</Badge>)}
                  {passport?.compatible_environments?.map((e, i) => <Badge key={`e-${i}`} className="text-[10px] bg-slate-50 text-slate-700 border-slate-200">{e}</Badge>)}
                </div>
              ) : (
                <p className="text-xs text-slate-400">{"Complétez votre profil pour renseigner vos valeurs"}</p>
              )}
            </div>
          </div>

          {/* 7. Validation - shown only when competences exist */}
          {competences.length > 0 && (
          <div className="border border-slate-200 rounded-xl p-4 space-y-2" data-testid="dim-validation">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-full bg-green-100 flex items-center justify-center text-green-700 text-xs font-bold">7</div>
              <h4 className="font-semibold text-sm text-slate-800">Niveaux de validation</h4>
            </div>
            <div className="ml-8 grid grid-cols-2 sm:grid-cols-4 gap-2">
              {competences.filter(c => c.source === "declaratif").length > 0 && (
              <div className="bg-slate-50 rounded-lg p-2 text-center">
                <User className="w-4 h-4 mx-auto text-slate-500" />
                <p className="text-[10px] font-medium text-slate-700 mt-1">{"Auto-déclaré"}</p>
                <p className="text-[10px] text-slate-400">{competences.filter(c => c.source === "declaratif").length}{" comp."}</p>
              </div>
              )}
              {competences.filter(c => c.source === "ia_detectee").length > 0 && (
              <div className="bg-violet-50 rounded-lg p-2 text-center">
                <Brain className="w-4 h-4 mx-auto text-violet-500" />
                <p className="text-[10px] font-medium text-violet-700 mt-1">{"Détecté IA"}</p>
                <p className="text-[10px] text-slate-400">{competences.filter(c => c.source === "ia_detectee").length}{" comp."}</p>
              </div>
              )}
              {competences.filter(c => ["dclic_pro", "profil"].includes(c.source)).length > 0 && (
              <div className="bg-emerald-50 rounded-lg p-2 text-center">
                <Award className="w-4 h-4 mx-auto text-emerald-500" />
                <p className="text-[10px] font-medium text-emerald-700 mt-1">{"D'CLIC PRO"}</p>
                <p className="text-[10px] text-slate-400">{competences.filter(c => ["dclic_pro", "profil"].includes(c.source)).length}{" comp."}</p>
              </div>
              )}
              {competences.filter(c => c.source === "coffre_fort").length > 0 && (
              <div className="bg-blue-50 rounded-lg p-2 text-center">
                <Shield className="w-4 h-4 mx-auto text-blue-500" />
                <p className="text-[10px] font-medium text-blue-700 mt-1">{"Coffre-fort"}</p>
                <p className="text-[10px] text-slate-400">{competences.filter(c => c.source === "coffre_fort").length}{" comp."}</p>
              </div>
              )}
              {competences.filter(c => ["ubuntoo", "contribution"].includes(c.source)).length > 0 && (
              <div className="bg-teal-50 rounded-lg p-2 text-center">
                <Shield className="w-4 h-4 mx-auto text-teal-500" />
                <p className="text-[10px] font-medium text-teal-700 mt-1">{"Validé humain"}</p>
                <p className="text-[10px] text-slate-400">{competences.filter(c => ["ubuntoo", "contribution"].includes(c.source)).length}{" comp."}</p>
              </div>
              )}
            </div>
          </div>
          )}

          {/* === SIMULATION TRAJECTOIRE === */}
          <SimulationTrajectoireBlock token={token} />

          {/* === RECOMMANDATION FORMATIONS === */}
          <FormationRecoBlock token={token} />

          {/* === PARTAGE SELECTIF === */}
          <PartageSelectifBlock token={token} />

        </TabsContent>
      </Tabs>

      {/* Evaluation Dialog */}
      <Dialog open={!!evaluatingComp} onOpenChange={(open) => { if (!open) setEvaluatingComp(null); }}>
        <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-[#1e3a5f]" />
              Évaluer : {evaluatingComp?.name}
            </DialogTitle>
          </DialogHeader>
          <EvaluationForm
            components={evalComponents}
            setComponents={setEvalComponents}
            ccspPole={evalCcspPole}
            setCcspPole={setEvalCcspPole}
            ccspDegree={evalCcspDegree}
            setCcspDegree={setEvalCcspDegree}
            onSave={handleSaveEvaluation}
          />
        </DialogContent>
      </Dialog>
    </div>
  );
};

// ============== ADD COMPETENCE FORM ==============

const AddCompetenceForm = ({ newComp, setNewComp, onSubmit }) => (
  <div className="space-y-4">
    <Input placeholder="Nom de la compétence" value={newComp.name} onChange={e => setNewComp({...newComp, name: e.target.value})} data-testid="comp-name-input" />

    {/* Nature: Savoir-faire vs Savoir-être */}
    <div>
      <label className="text-xs font-medium text-slate-500 mb-1.5 block">Nature de la compétence</label>
      <div className="grid grid-cols-2 gap-2">
        <button
          type="button"
          onClick={() => setNewComp({...newComp, nature: "savoir_faire"})}
          className={`flex items-center gap-2 p-3 rounded-lg border-2 transition-all text-sm font-medium ${
            newComp.nature === "savoir_faire"
              ? "border-sky-500 bg-sky-50 text-sky-700"
              : "border-slate-200 text-slate-500 hover:border-slate-300"
          }`}
          data-testid="nature-savoir-faire"
        >
          <Briefcase className="w-4 h-4" />
          <div className="text-left">
            <p>Savoir-faire</p>
            <p className="text-xs font-normal opacity-70">Hard Skill technique</p>
          </div>
        </button>
        <button
          type="button"
          onClick={() => setNewComp({...newComp, nature: "savoir_etre"})}
          className={`flex items-center gap-2 p-3 rounded-lg border-2 transition-all text-sm font-medium ${
            newComp.nature === "savoir_etre"
              ? "border-rose-500 bg-rose-50 text-rose-700"
              : "border-slate-200 text-slate-500 hover:border-slate-300"
          }`}
          data-testid="nature-savoir-etre"
        >
          <Activity className="w-4 h-4" />
          <div className="text-left">
            <p>Savoir-être</p>
            <p className="text-xs font-normal opacity-70">Soft Skill comportemental</p>
          </div>
        </button>
      </div>
    </div>

    <div>
      <label className="text-xs font-medium text-slate-500 mb-1.5 block">Catégorie</label>
      <div className="grid grid-cols-2 gap-2">
        {Object.entries(CATEGORY_CONFIG).map(([key, cfg]) => (
          <button
            key={key}
            type="button"
            onClick={() => setNewComp({...newComp, category: key})}
            className={`p-2.5 rounded-lg border-2 transition-all text-left ${
              newComp.category === key
                ? `${cfg.color} border-current`
                : "border-slate-200 text-slate-500 hover:border-slate-300"
            }`}
            data-testid={`category-${key}`}
          >
            <p className="text-xs font-semibold">{cfg.label}</p>
            <p className="text-[10px] opacity-70 leading-tight mt-0.5">{cfg.desc}</p>
          </button>
        ))}
      </div>
    </div>
    <div>
      <label className="text-xs font-medium text-slate-500 mb-1 block">Niveau</label>
      <Select value={newComp.level} onValueChange={v => setNewComp({...newComp, level: v})}>
        <SelectTrigger><SelectValue /></SelectTrigger>
        <SelectContent>
          <SelectItem value="debutant">Débutant</SelectItem>
          <SelectItem value="intermediaire">Intermédiaire</SelectItem>
          <SelectItem value="avance">Avancé</SelectItem>
          <SelectItem value="expert">Expert</SelectItem>
        </SelectContent>
      </Select>
    </div>

    {/* CCSP Classification */}
    <div className="border-t pt-3">
      <p className="text-sm font-medium text-slate-700 mb-2 flex items-center gap-1">
        <CircleDot className="w-4 h-4" />Classification CCSP (optionnel)
      </p>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="text-xs text-slate-500 mb-1 block">Pôle</label>
          <Select value={newComp.ccsp_pole || "none"} onValueChange={v => setNewComp({...newComp, ccsp_pole: v === "none" ? "" : v})}>
            <SelectTrigger><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="none">Non défini</SelectItem>
              <SelectItem value="realisation">Réalisation</SelectItem>
              <SelectItem value="interaction">Interaction</SelectItem>
              <SelectItem value="initiative">Initiative</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div>
          <label className="text-xs text-slate-500 mb-1 block">Degré</label>
          <Select value={newComp.ccsp_degree || "none"} onValueChange={v => setNewComp({...newComp, ccsp_degree: v === "none" ? "" : v})}>
            <SelectTrigger><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="none">Non défini</SelectItem>
              <SelectItem value="imitation">Imitation</SelectItem>
              <SelectItem value="adaptation">Adaptation</SelectItem>
              <SelectItem value="transposition">Transposition</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>

    <Button className="w-full" onClick={onSubmit} data-testid="submit-competence-btn">
      <Check className="w-4 h-4 mr-2" />Ajouter la compétence
    </Button>
  </div>
);

// ============== EVALUATION FORM ==============

const EvaluationForm = ({ components, setComponents, ccspPole, setCcspPole, ccspDegree, setCcspDegree, onSave }) => {
  const radarData = Object.entries(COMPONENT_LABELS).map(([key, cfg]) => ({
    component: cfg.short,
    fullName: cfg.label,
    value: components[key] || 0,
    fullMark: 5,
  }));

  return (
    <div className="space-y-5">
      {/* Lamri & Lubart 5 Components */}
      <div>
        <h4 className="text-sm font-semibold text-[#1e3a5f] mb-1">Modèle Lamri & Lubart - 5 composantes</h4>
        <p className="text-xs text-slate-400 mb-3">Évaluez chaque composante de 0 (non développé) à 5 (maîtrisé)</p>
        <div className="space-y-4">
          {Object.entries(COMPONENT_LABELS).map(([key, cfg]) => {
            const Icon = cfg.icon;
            return (
              <div key={key}>
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center gap-2">
                    <Icon className="w-4 h-4" style={{ color: cfg.color }} />
                    <span className="text-sm font-medium text-slate-700">{cfg.label}</span>
                  </div>
                  <span className="text-sm font-bold" style={{ color: cfg.color }}>{components[key]}/5</span>
                </div>
                <Slider
                  value={[components[key]]}
                  onValueChange={([v]) => setComponents({...components, [key]: v})}
                  max={5}
                  step={1}
                  className="w-full"
                  data-testid={`eval-slider-${key}`}
                />
                <p className="text-xs text-slate-400 mt-0.5">{cfg.desc}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Radar Preview */}
      <div className="bg-slate-50 rounded-xl p-4">
        <h4 className="text-xs font-medium text-slate-500 mb-2 text-center">Profil de compétence</h4>
        <ResponsiveContainer width="100%" height={200}>
          <RadarChart data={radarData}>
            <PolarGrid stroke="#e2e8f0" />
            <PolarAngleAxis dataKey="component" tick={{ fontSize: 11, fill: "#64748b" }} />
            <PolarRadiusAxis angle={90} domain={[0, 5]} tick={false} axisLine={false} />
            <Radar dataKey="value" stroke="#1e3a5f" fill="#1e3a5f" fillOpacity={0.2} strokeWidth={2} />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* CCSP Classification */}
      <div className="border-t pt-4">
        <h4 className="text-sm font-semibold text-[#1e3a5f] mb-3 flex items-center gap-1">
          <CircleDot className="w-4 h-4" />Référentiel CCSP
        </h4>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-slate-500 mb-1 block">Pôle de compétence</label>
            <Select value={ccspPole || "none"} onValueChange={v => setCcspPole(v === "none" ? "" : v)}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="none">Non défini</SelectItem>
                <SelectItem value="realisation">Réalisation</SelectItem>
                <SelectItem value="interaction">Interaction</SelectItem>
                <SelectItem value="initiative">Initiative</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <label className="text-xs text-slate-500 mb-1 block">Degré de maîtrise</label>
            <Select value={ccspDegree || "none"} onValueChange={v => setCcspDegree(v === "none" ? "" : v)}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="none">Non défini</SelectItem>
                <SelectItem value="imitation">Imitation</SelectItem>
                <SelectItem value="adaptation">Adaptation</SelectItem>
                <SelectItem value="transposition">Transposition</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      <Button className="w-full" onClick={onSave} data-testid="save-evaluation-btn">
        <Save className="w-4 h-4 mr-2" />Enregistrer l'évaluation
      </Button>
    </div>
  );
};

// ============== EVALUATION TAB ==============

const EvaluationTab = ({ competences, diagnostic, loadingDiagnostic, onLoadDiagnostic, onEvaluate, dclicProfile }) => {
  const evaluated = competences.filter(c => {
    const cmp = c.components || {};
    return Object.values(cmp).some(v => v > 0);
  });
  const notEvaluated = competences.filter(c => {
    const cmp = c.components || {};
    return !Object.values(cmp).some(v => v > 0);
  });
  const dclicCompNames = new Set((dclicProfile?.dclic_competences || []).map(n => n.toLowerCase()));
  const dclicEnrichedCount = competences.filter(c => dclicCompNames.has((c.name || "").toLowerCase())).length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-[#1e3a5f] flex items-center gap-2">
            <Activity className="w-5 h-5" />Évaluation des compétences
          </h3>
          <p className="text-sm text-slate-500">Évaluez vos compétences selon le modèle Lamri & Lubart et le référentiel CCSP</p>
        </div>
        <Button onClick={onLoadDiagnostic} disabled={loadingDiagnostic} data-testid="load-diagnostic-btn">
          {loadingDiagnostic ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <TrendingUp className="w-4 h-4 mr-2" />}
          {loadingDiagnostic ? "Chargement..." : "Générer le diagnostic"}
        </Button>
      </div>

      {/* D'CLIC boost banner */}
      {dclicProfile?.dclic_imported && (
        <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-100 rounded-lg px-3 py-2 text-xs text-emerald-700" data-testid="evaluation-dclic-boost">
          <Sparkles className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
          <span>D'CLIC PRO optimise l'évaluation : votre profil de personnalité {dclicEnrichedCount > 0 ? `enrichit ${dclicEnrichedCount} compétence${dclicEnrichedCount > 1 ? "s" : ""} comportementale${dclicEnrichedCount > 1 ? "s" : ""}` : "apporte une dimension comportementale"} au diagnostic Lamri & Lubart et CCSP.</span>
        </div>
      )}

      {/* Diagnostic Results */}
      {diagnostic && <DiagnosticView diagnostic={diagnostic} />}

      {/* Frameworks Explanation */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="border-l-4 border-l-[#1e3a5f]">
          <CardContent className="p-4">
            <h4 className="font-semibold text-[#1e3a5f] mb-2 text-sm">Modèle Lamri & Lubart</h4>
            <p className="text-xs text-slate-500 mb-3">Chaque compétence se décompose en 5 composantes :</p>
            <div className="space-y-1.5">
              {Object.entries(COMPONENT_LABELS).map(([key, cfg]) => {
                const Icon = cfg.icon;
                return (
                  <div key={key} className="flex items-center gap-2 text-xs">
                    <Icon className="w-3.5 h-3.5 flex-shrink-0" style={{ color: cfg.color }} />
                    <span className="font-medium text-slate-700">{cfg.label}:</span>
                    <span className="text-slate-500">{cfg.desc}</span>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
        <Card className="border-l-4 border-l-emerald-600">
          <CardContent className="p-4">
            <h4 className="font-semibold text-emerald-700 mb-2 text-sm">Référentiel CCSP</h4>
            <p className="text-xs text-slate-500 mb-3">Classification en 3 pôles et 3 degrés de maîtrise :</p>
            <div className="mb-2">
              <p className="text-xs font-medium text-slate-600 mb-1">Pôles :</p>
              <div className="flex flex-wrap gap-1.5">
                {Object.entries(CCSP_POLES).map(([k, cfg]) => (
                  <Badge key={k} className={`text-xs ${cfg.bgLight} ${cfg.textColor}`}>{cfg.label}</Badge>
                ))}
              </div>
            </div>
            <div>
              <p className="text-xs font-medium text-slate-600 mb-1">Degrés :</p>
              <div className="flex gap-1.5">
                {Object.entries(CCSP_DEGREES).map(([k, cfg]) => (
                  <Badge key={k} variant="outline" className="text-xs">{cfg.label} (niv. {cfg.level})</Badge>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="border-l-4 border-l-amber-500">
          <CardContent className="p-4">
            <h4 className="font-semibold text-amber-700 mb-2 text-sm">Transversale vs Transférable</h4>
            <p className="text-xs text-slate-500 mb-3">Distinction France Travail :</p>
            <div className="space-y-2">
              <div className="p-2 rounded bg-violet-50">
                <p className="text-xs font-semibold text-violet-700">Transversale</p>
                <p className="text-[10px] text-violet-600">Universelle, commune à différents métiers et secteurs (ex: communication, bureautique, langues)</p>
              </div>
              <div className="p-2 rounded bg-amber-50">
                <p className="text-xs font-semibold text-amber-700">Transférable</p>
                <p className="text-[10px] text-amber-600">Mobilisable dans différents métiers d'un même secteur ou entreprise (ex: rigueur, analyse dans le BTP)</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Competences to evaluate */}
      {notEvaluated.length > 0 && (
        <div>
          <h4 className="font-medium text-slate-700 mb-3">
            Compétences à évaluer ({notEvaluated.length})
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {notEvaluated.map(comp => (
              <Card key={comp.id} className="hover:shadow-md transition-shadow border-dashed" data-testid="unevaluated-comp-card">
                <CardContent className="p-4 flex items-center justify-between">
                  <div>
                    <p className="font-medium text-slate-800 text-sm">{comp.name}</p>
                    <p className="text-xs text-slate-400">Non évaluée</p>
                  </div>
                  <Button size="sm" variant="outline" onClick={() => onEvaluate(comp)} data-testid={`evaluate-btn-${comp.id}`}>
                    <Edit3 className="w-3.5 h-3.5 mr-1" />Évaluer
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Already evaluated */}
      {evaluated.length > 0 && (
        <div>
          <h4 className="font-medium text-slate-700 mb-3">
            Compétences évaluées ({evaluated.length})
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {evaluated.map(comp => (
              <EvaluatedCompCard key={comp.id} comp={comp} onEvaluate={onEvaluate} />
            ))}
          </div>
        </div>
      )}

      {competences.length === 0 && <EmptyState text="Ajoutez des compétences dans l'onglet 'Compétences' pour les évaluer ici" />}
    </div>
  );
};

// ============== DIAGNOSTIC VIEW ==============

const DiagnosticView = ({ diagnostic }) => {
  const { lamri_lubart_profile, ccsp_distribution, recommendations, evaluated_count, total_competences } = diagnostic;

  const radarData = Object.entries(COMPONENT_LABELS).map(([key, cfg]) => ({
    component: cfg.label,
    value: lamri_lubart_profile?.[key] || 0,
    fullMark: 5,
  }));

  const poleData = Object.entries(ccsp_distribution?.poles || {}).map(([key, value]) => ({
    name: CCSP_POLES[key]?.label || key,
    value,
    color: key === "realisation" ? "#3b82f6" : key === "interaction" ? "#10b981" : "#f59e0b",
  }));

  const degreeData = Object.entries(ccsp_distribution?.degrees || {}).map(([key, value]) => ({
    name: CCSP_DEGREES[key]?.label || key,
    value,
    color: key === "imitation" ? "#94a3b8" : key === "adaptation" ? "#3b82f6" : "#10b981",
  }));

  return (
    <div className="space-y-4">
      <Card className="bg-gradient-to-r from-[#1e3a5f] to-[#2d5a8e] text-white border-0">
        <CardContent className="p-5">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-semibold text-lg">Votre Diagnostic</h4>
              <p className="text-blue-200 text-sm">{evaluated_count}/{total_competences} compétences évaluées</p>
            </div>
            <div className="text-right">
              <Progress value={(evaluated_count / Math.max(total_competences, 1)) * 100} className="h-2 w-32 bg-white/20" />
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Radar - Lamri & Lubart Profile */}
        <Card className="md:col-span-1">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-[#1e3a5f]">Profil Lamri & Lubart</CardTitle>
          </CardHeader>
          <CardContent className="pb-4">
            <ResponsiveContainer width="100%" height={220}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="#e2e8f0" />
                <PolarAngleAxis dataKey="component" tick={{ fontSize: 10, fill: "#64748b" }} />
                <PolarRadiusAxis angle={90} domain={[0, 5]} tick={false} axisLine={false} />
                <Radar dataKey="value" stroke="#1e3a5f" fill="#1e3a5f" fillOpacity={0.25} strokeWidth={2} />
              </RadarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* CCSP Poles Distribution */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-emerald-700">Pôles CCSP</CardTitle>
          </CardHeader>
          <CardContent className="pb-4">
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={poleData} layout="vertical" margin={{ left: 10 }}>
                <XAxis type="number" tick={{ fontSize: 11 }} />
                <YAxis dataKey="name" type="category" tick={{ fontSize: 11 }} width={80} />
                <Tooltip />
                <Bar dataKey="value" radius={[0, 6, 6, 0]}>
                  {poleData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* CCSP Degrees Distribution */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-amber-700">Degrés CCSP</CardTitle>
          </CardHeader>
          <CardContent className="pb-4">
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={degreeData} layout="vertical" margin={{ left: 10 }}>
                <XAxis type="number" tick={{ fontSize: 11 }} />
                <YAxis dataKey="name" type="category" tick={{ fontSize: 11 }} width={90} />
                <Tooltip />
                <Bar dataKey="value" radius={[0, 6, 6, 0]}>
                  {degreeData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Recommendations */}
      {recommendations?.length > 0 && (
        <Card className="border-amber-200 bg-amber-50/30">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-amber-800 flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />Recommandations
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {recommendations.map((rec, i) => (
              <div key={i} className="flex items-start gap-2 p-2 rounded-lg bg-white/60" data-testid="recommendation-item">
                <ChevronRight className="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-sm text-slate-700">{rec.message}</p>
                  <Badge variant="outline" className="text-xs mt-1">{rec.type}</Badge>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

// ============== EVALUATED COMPETENCE CARD ==============

const EvaluatedCompCard = ({ comp, onEvaluate }) => {
  const cmp = comp.components || {};
  const radarData = Object.entries(COMPONENT_LABELS).map(([key, cfg]) => ({
    component: cfg.short,
    value: cmp[key] || 0,
    fullMark: 5,
  }));
  const poleConfig = CCSP_POLES[comp.ccsp_pole];
  const degreeConfig = CCSP_DEGREES[comp.ccsp_degree];

  return (
    <Card className="hover:shadow-md transition-shadow" data-testid="evaluated-comp-card">
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-2">
          <div>
            <h4 className="font-semibold text-slate-900 text-sm">{comp.name}</h4>
            <div className="flex items-center gap-1 mt-1 flex-wrap">
              {poleConfig && <Badge className={`text-xs ${poleConfig.bgLight} ${poleConfig.textColor}`}>{poleConfig.label}</Badge>}
              {degreeConfig && <Badge variant="outline" className="text-xs">{degreeConfig.label}</Badge>}
            </div>
          </div>
          <Button size="sm" variant="ghost" onClick={() => onEvaluate(comp)} className="text-slate-400 hover:text-[#1e3a5f]">
            <Edit3 className="w-3.5 h-3.5" />
          </Button>
        </div>
        <ResponsiveContainer width="100%" height={150}>
          <RadarChart data={radarData}>
            <PolarGrid stroke="#e2e8f0" />
            <PolarAngleAxis dataKey="component" tick={{ fontSize: 10, fill: "#94a3b8" }} />
            <PolarRadiusAxis angle={90} domain={[0, 5]} tick={false} axisLine={false} />
            <Radar dataKey="value" stroke="#1e3a5f" fill="#1e3a5f" fillOpacity={0.2} strokeWidth={1.5} />
          </RadarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

// ============== EXISTING SUB-COMPONENTS ==============

const StatCard = ({ icon: Icon, value, label, sublabel, color }) => (
  <Card>
    <CardContent className="p-4">
      <div className="flex items-center gap-3">
        <div className={`w-12 h-12 rounded-xl ${color} text-white flex items-center justify-center`}>
          <Icon className="w-6 h-6" />
        </div>
        <div>
          <p className="text-3xl font-bold text-slate-900">{value}</p>
          <p className="text-sm text-slate-600">{label}</p>
          {sublabel && <p className="text-xs text-slate-400">{sublabel}</p>}
        </div>
      </div>
    </CardContent>
  </Card>
);

const EmptyState = ({ text }) => (
  <div className="text-center py-10 text-slate-400 border-2 border-dashed border-slate-200 rounded-xl">
    <p className="text-sm">{text}</p>
  </div>
);

const ProfileSection = ({ passport, editing, profileEdit, setProfileEdit, onStartEdit, onSave, onCancel, refreshingDynamic, onRefreshProfile, dclicProfile }) => (
  <Card>
    <CardHeader className="flex flex-row items-center justify-between">
      <div>
        <CardTitle className="flex items-center gap-2"><User className="w-5 h-5 text-[#1e3a5f]" />Profil professionnel</CardTitle>
        <CardDescription>Votre synthèse professionnelle et vos objectifs</CardDescription>
      </div>
      <div className="flex gap-2">
        {onRefreshProfile && !editing && (
          <Button variant="outline" size="sm" onClick={onRefreshProfile} disabled={refreshingDynamic} data-testid="refresh-profile-btn" className="text-indigo-600 border-indigo-200 hover:bg-indigo-50">
            <RefreshCw className={`w-4 h-4 mr-1 ${refreshingDynamic ? "animate-spin" : ""}`} />{refreshingDynamic ? "Actualisation..." : "Actualiser"}
          </Button>
        )}
        {!editing ? (
          <Button variant="outline" size="sm" onClick={onStartEdit} data-testid="edit-profile-btn"><Edit3 className="w-4 h-4 mr-1" />Modifier</Button>
        ) : (
          <>
            <Button size="sm" onClick={onSave} data-testid="save-profile-btn"><Save className="w-4 h-4 mr-1" />Enregistrer</Button>
            <Button variant="outline" size="sm" onClick={onCancel}>Annuler</Button>
          </>
        )}
      </div>
    </CardHeader>
    <CardContent className="space-y-4">
      {dclicProfile?.dclic_imported && !editing && (
        <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-100 rounded-lg px-3 py-2 text-xs text-emerald-700" data-testid="profil-dclic-boost">
          <Sparkles className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
          <span>D'CLIC PRO a enrichi votre profil : motivations, environnements compatibles et synthèse sont alimentés par votre profil de personnalité.</span>
        </div>
      )}
      {editing ? (
        <>
          <ProfileField label="Synthèse professionnelle" value={profileEdit.professional_summary} onChange={v => setProfileEdit({...profileEdit, professional_summary: v})} testId="profile-summary-input" />
          <ProfileField label="Projet professionnel" value={profileEdit.career_project} onChange={v => setProfileEdit({...profileEdit, career_project: v})} testId="profile-project-input" />
          <ProfileField label="Motivations (séparées par des virgules)" value={profileEdit.motivations} onChange={v => setProfileEdit({...profileEdit, motivations: v})} />
          <ProfileField label="Environnements compatibles (séparés par des virgules)" value={profileEdit.compatible_environments} onChange={v => setProfileEdit({...profileEdit, compatible_environments: v})} />
          <ProfileField label="Secteurs cibles (séparés par des virgules)" value={profileEdit.target_sectors} onChange={v => setProfileEdit({...profileEdit, target_sectors: v})} />
        </>
      ) : (
        <>
          <ProfileDisplay label="Synthèse professionnelle" value={passport.professional_summary} icon={User} />
          <ProfileDisplay label="Projet professionnel" value={passport.career_project} icon={Target} />
          <ProfileDisplayList label="Motivations" items={passport.motivations} icon={Zap} />
          <ProfileDisplayList label="Environnements compatibles" items={passport.compatible_environments} icon={Compass} />
          <ProfileDisplayList label="Secteurs cibles" items={passport.target_sectors} icon={Briefcase} />
        </>
      )}
    </CardContent>
  </Card>
);

const ProfileField = ({ label, value, onChange, testId }) => (
  <div>
    <label className="text-sm font-medium text-slate-700 mb-1 block">{label}</label>
    <Input value={value} onChange={e => onChange(e.target.value)} data-testid={testId} />
  </div>
);

const ProfileDisplay = ({ label, value, icon: Icon }) => (
  <div className="flex items-start gap-3 p-3 rounded-lg bg-slate-50">
    <Icon className="w-4 h-4 text-[#1e3a5f] mt-0.5 flex-shrink-0" />
    <div>
      <p className="text-xs font-medium text-slate-500">{label}</p>
      <p className="text-sm text-slate-800">{value || <span className="italic text-slate-400">Non renseigné</span>}</p>
    </div>
  </div>
);

const ProfileDisplayList = ({ label, items, icon: Icon }) => (
  <div className="flex items-start gap-3 p-3 rounded-lg bg-slate-50">
    <Icon className="w-4 h-4 text-[#1e3a5f] mt-0.5 flex-shrink-0" />
    <div>
      <p className="text-xs font-medium text-slate-500">{label}</p>
      {items && items.length > 0 ? (
        <div className="flex flex-wrap gap-1 mt-1">
          {items.map((item, i) => <Badge key={i} variant="secondary" className="text-xs">{item}</Badge>)}
        </div>
      ) : <p className="text-sm italic text-slate-400">Non renseigné</p>}
    </div>
  </div>
);

const CompetenceCard = ({ comp, onDelete, onEvaluate, emerging }) => {
  const levelConfig = LEVEL_CONFIG[comp.level] || LEVEL_CONFIG.intermediaire;
  const catConfig = CATEGORY_CONFIG[comp.category] || CATEGORY_CONFIG.technique;
  const srcConfig = SOURCE_CONFIG[comp.source] || SOURCE_CONFIG.declaratif;
  const SrcIcon = srcConfig.icon;
  const poleConfig = CCSP_POLES[comp.ccsp_pole];
  const degreeConfig = CCSP_DEGREES[comp.ccsp_degree];
  const natureConfig = NATURE_CONFIG[comp.nature];
  const hasEval = comp.components && Object.values(comp.components).some(v => v > 0);

  return (
    <Card className={`hover:shadow-md transition-shadow ${emerging ? "border-violet-200 bg-violet-50/30" : ""} ${comp.nature === "savoir_faire" ? "border-l-4 border-l-sky-400" : comp.nature === "savoir_etre" ? "border-l-4 border-l-rose-400" : ""}`} data-testid="competence-card">
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-2">
          <div>
            <h4 className="font-semibold text-slate-900 text-sm">{comp.name}</h4>
            <div className="flex items-center gap-1 mt-1 flex-wrap">
              {natureConfig && <Badge className={`text-xs ${natureConfig.bgLight} border`}>{natureConfig.label}</Badge>}
              <Badge variant="outline" className={`text-xs ${catConfig.color}`}>{catConfig.label}</Badge>
              <Badge className={`text-xs ${srcConfig.color}`}><SrcIcon className="w-3 h-3 mr-0.5" />{srcConfig.label}</Badge>
              {poleConfig && <Badge className={`text-xs ${poleConfig.bgLight} ${poleConfig.textColor}`}>{poleConfig.label}</Badge>}
              {degreeConfig && <Badge variant="outline" className="text-xs">{degreeConfig.label}</Badge>}
            </div>
          </div>
          <div className="flex items-center gap-0.5">
            <Button variant="ghost" size="sm" className="h-7 w-7 p-0 text-slate-400 hover:text-[#1e3a5f]" onClick={() => onEvaluate(comp)} data-testid={`evaluate-comp-${comp.id}`}>
              <Activity className="w-3.5 h-3.5" />
            </Button>
            {comp.source === "declaratif" && (
              <Button variant="ghost" size="sm" className="h-7 w-7 p-0 text-slate-400 hover:text-red-500" onClick={() => onDelete(comp.id)}>
                <Trash2 className="w-3.5 h-3.5" />
              </Button>
            )}
          </div>
        </div>
        <div className="mt-3">
          <div className="flex items-center justify-between text-xs mb-1">
            <span className="text-slate-500">Niveau</span>
            <span className={`font-medium ${levelConfig.color} px-2 py-0.5 rounded-full`}>{levelConfig.label}</span>
          </div>
          <Progress value={levelConfig.width} className="h-1.5" />
        </div>
        {/* Mini component bars */}
        {hasEval && (
          <div className="mt-3 flex items-center gap-1">
            {Object.entries(COMPONENT_LABELS).map(([key, cfg]) => {
              const val = comp.components?.[key] || 0;
              return (
                <div key={key} className="flex-1" title={`${cfg.label}: ${val}/5`}>
                  <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                    <div className="h-full rounded-full" style={{ width: `${(val / 5) * 100}%`, backgroundColor: cfg.color }} />
                  </div>
                </div>
              );
            })}
          </div>
        )}
        {comp.proof && (
          <div className="mt-2 flex items-center gap-1 text-xs text-blue-600">
            <Award className="w-3 h-3" /><span>Preuve: {comp.proof}</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

const ExperienceCard = ({ exp, onDelete, softSkills, hardSkills, illustrations, token, onIllustrationSaved }) => {
  const [expanded, setExpanded] = useState(false);
  const [selectedSkill, setSelectedSkill] = useState("");
  const [selectedSkillType, setSelectedSkillType] = useState("soft");
  const [sareSituation, setSareSituation] = useState("");
  const [sareAction, setSareAction] = useState("");
  const [sareResultat, setSareResultat] = useState("");
  const [sareEnseignement, setSareEnseignement] = useState("");
  const [saving, setSaving] = useState(false);
  const [suggesting, setSuggesting] = useState(false);
  const [suggestions, setSuggestions] = useState(null);
  const [rewritingId, setRewritingId] = useState(null);
  const [editingId, setEditingId] = useState(null);
  const [opcConsent, setOpcConsent] = useState(false);
  const [collapsedProofs, setCollapsedProofs] = useState({});

  const toggleProof = (id) => setCollapsedProofs(prev => ({ ...prev, [id]: !prev[id] }));

  const expIllustrations = (illustrations || []).filter(i => i.experience_id === exp.id);
  const illustratedSkills = new Set(expIllustrations.map(i => i.soft_skill));

  const resetForm = () => {
    setSareSituation("");
    setSareAction("");
    setSareResultat("");
    setSareEnseignement("");
    setSelectedSkill("");
    setSelectedSkillType("soft");
    setEditingId(null);
    setOpcConsent(false);
  };

  const startEdit = (illus) => {
    setSelectedSkill(illus.soft_skill);
    setSelectedSkillType(illus.skill_type || "soft");
    setSareSituation(illus.sare_situation || "");
    setSareAction(illus.sare_action || "");
    setSareResultat(illus.sare_resultat || "");
    setSareEnseignement(illus.sare_enseignement || "");
    setEditingId(illus.id);
    setOpcConsent(!!illus.opc_consent);
  };

  const handleSave = async () => {
    if (!selectedSkill || (!sareSituation.trim() && !sareAction.trim())) return;
    setSaving(true);
    try {
      await axios.post(`${API}/passport/illustrations?token=${token}`, {
        experience_id: exp.id,
        soft_skill: selectedSkill,
        skill_type: selectedSkillType,
        sare_situation: sareSituation.trim(),
        sare_action: sareAction.trim(),
        sare_resultat: sareResultat.trim(),
        sare_enseignement: sareEnseignement.trim(),
        opc_consent: opcConsent,
      });
      resetForm();
      if (onIllustrationSaved) onIllustrationSaved();
      toast.success("Preuve S.A.R.E enregistrée");
    } catch { toast.error("Erreur de sauvegarde"); }
    setSaving(false);
  };

  const handleSuggest = async () => {
    setSuggesting(true);
    try {
      const res = await axios.post(`${API}/passport/illustrations/suggest?token=${token}`, { experience_id: exp.id });
      setSuggestions(res.data.suggestions || []);
    } catch { toast.error("Erreur IA"); }
    setSuggesting(false);
  };

  const handleSare = async (illusId) => {
    setRewritingId(illusId);
    try {
      const res = await axios.post(`${API}/passport/illustrations/sare?token=${token}`, { illustration_id: illusId });
      if (res.data.sare_text) {
        if (onIllustrationSaved) onIllustrationSaved();
        toast.success("Reformulé en méthode S.A.R.E");
      }
    } catch { toast.error("Erreur reformulation"); }
    setRewritingId(null);
  };

  const handleDeleteIllus = async (illusId) => {
    try {
      await axios.delete(`${API}/passport/illustrations/${illusId}?token=${token}`);
      if (onIllustrationSaved) onIllustrationSaved();
      toast.success("Illustration supprimée");
    } catch { toast.error("Erreur"); }
  };

  const typeLabels = { professionnel: "Professionnel", personnel: "Personnel", benevole: "Bénévole", projet: "Projet" };
  return (
    <Card className="hover:shadow-md transition-shadow" data-testid="experience-card">
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <h4 className="font-semibold text-slate-900">{exp.title}</h4>
              <Badge variant="outline" className="text-xs">{typeLabels[exp.experience_type] || "Autre"}</Badge>
              {exp.is_current && <Badge className="bg-emerald-100 text-emerald-700 text-xs">En cours</Badge>}
              {exp.is_certified && (
                <Badge className="bg-blue-100 text-blue-700 border border-blue-200 text-[10px] gap-1" data-testid={`certified-badge-${exp.id}`}>
                  <ShieldCheck className="w-3 h-3" />Certifié
                </Badge>
              )}
              {expIllustrations.length > 0 && (
                <Badge className="bg-emerald-50 text-emerald-700 border border-emerald-200 text-[10px]" data-testid={`illus-count-${exp.id}`}>
                  {expIllustrations.length} compétence{expIllustrations.length > 1 ? "s" : ""} prouvée{expIllustrations.length > 1 ? "s" : ""}
                </Badge>
              )}
            </div>
            {exp.organization && <p className="text-sm text-slate-600">{exp.organization}</p>}
            {exp.description && <p className="text-sm text-slate-500 mt-1">{exp.description}</p>}
            {exp.skills_used?.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-2">
                {exp.skills_used.map((s, i) => <Badge key={i} className="bg-blue-50 text-blue-700 text-xs">{s}</Badge>)}
              </div>
            )}
            {exp.achievements?.length > 0 && (
              <div className="mt-2">
                {exp.achievements.map((a, i) => (
                  <div key={i} className="flex items-center gap-1 text-xs text-emerald-700">
                    <Check className="w-3 h-3" /><span>{a}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Document officiel certifié */}
            {exp.proof_document && (
              <div className="mt-2.5 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200/60 p-2.5" data-testid={`passport-proof-doc-${exp.id}`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-7 h-7 rounded-lg bg-blue-100 flex items-center justify-center">
                      <ShieldCheck className="w-4 h-4 text-blue-700" />
                    </div>
                    <div>
                      <div className="flex items-center gap-1.5">
                        <span className="text-[11px] font-bold text-blue-800">Document officiel</span>
                        <Badge className="bg-blue-600 text-white text-[8px]">Certifié</Badge>
                      </div>
                      <p className="text-[10px] text-blue-600 truncate max-w-[200px]">{exp.proof_document.original_filename}</p>
                    </div>
                  </div>
                  <Button variant="outline" size="sm" className="h-7 px-2.5 text-[10px] text-blue-700 border-blue-200 hover:bg-blue-100 gap-1"
                    onClick={() => window.open(`${API}/passport/experiences/proof-file/${exp.proof_document.file_id}?token=${token}`, "_blank")}
                    data-testid={`passport-view-proof-${exp.id}`}
                  >
                    <Eye className="w-3 h-3" />Consulter
                  </Button>
                </div>
              </div>
            )}
          </div>
          <div className="flex items-center gap-1">
            <Button variant="ghost" size="sm" className={`h-9 px-3 gap-1.5 rounded-lg border ${expanded ? "text-emerald-700 bg-emerald-50 border-emerald-300" : "text-purple-600 bg-purple-50 border-purple-200 hover:bg-purple-100 hover:border-purple-300"}`} onClick={() => setExpanded(!expanded)} data-testid={`toggle-illus-${exp.id}`}>
              <Sparkles className="w-4 h-4" />
              <span className="text-xs font-semibold">{expanded ? "Masquer" : "Prouver vos compétences"}</span>
            </Button>
            {!exp.proof_document && (
              <Button
                variant="ghost"
                size="sm"
                className="h-9 px-3 gap-1.5 rounded-lg border border-blue-200 bg-blue-50 hover:bg-blue-100 hover:border-blue-300 text-blue-600 transition-colors"
                data-testid={`certify-coffre-${exp.id}`}
                onClick={async () => {
                  try {
                    const skills = exp.skills_detected || [];
                    const title = `Certification — ${exp.title}${exp.organization ? ` (${exp.organization})` : ""}`;
                    const description = [
                      `Expérience : ${exp.title}`,
                      exp.organization ? `Organisation : ${exp.organization}` : null,
                      exp.period ? `Période : ${exp.period}` : null,
                      skills.length > 0 ? `Compétences : ${skills.join(", ")}` : null,
                    ].filter(Boolean).join("\n");

                    await axios.post(`${API}/coffre/documents?token=${token}`, {
                      title,
                      category: "experience_prouvee",
                      document_type: "certification_competences",
                      trust_level: "auto_declare",
                      source_type: "utilisateur",
                      description,
                      competences_liees: skills,
                    });
                    toast.success("Expérience transférée dans le Coffre-fort et le Portefeuille de compétences");
                    if (onIllustrationSaved) onIllustrationSaved();
                  } catch (err) {
                    console.error(err);
                    toast.error("Erreur lors du transfert vers le Coffre-fort");
                  }
                }}
              >
                <ShieldCheck className="w-4 h-4" />
                <span className="text-xs font-semibold">Certifier</span>
              </Button>
            )}
            {exp.source === "declaratif" && (
              <Button variant="ghost" size="sm" className="h-7 w-7 p-0 text-slate-400 hover:text-red-500" onClick={() => onDelete(exp.id)}>
                <Trash2 className="w-3.5 h-3.5" />
              </Button>
            )}
          </div>
        </div>

        {/* Always-visible: Existing S.A.R.E proofs (collapsible) */}
        {expIllustrations.length > 0 && (
          <div className="mt-3 pt-3 border-t border-slate-100 space-y-2" data-testid={`proofs-visible-${exp.id}`}>
            {expIllustrations.map((illus) => {
              const isOpen = !collapsedProofs[illus.id];
              const preview = illus.sare_situation || illus.situation_text || "";
              return (
              <div key={illus.id} className="bg-emerald-50 border border-emerald-100 rounded-lg overflow-hidden" data-testid={`illustration-${illus.id}`}>
                {/* Header - always visible, clickable to toggle */}
                <div className="flex items-center justify-between px-3 py-2 cursor-pointer hover:bg-emerald-100/50 transition-colors" onClick={() => toggleProof(illus.id)} data-testid={`toggle-proof-${illus.id}`}>
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    <ChevronRight className={`w-3.5 h-3.5 text-emerald-500 shrink-0 transition-transform ${isOpen ? "rotate-90" : ""}`} />
                    <Badge className={`text-[10px] shrink-0 ${illus.skill_type === "hard" ? "bg-sky-100 text-sky-700" : "bg-emerald-100 text-emerald-700"}`}>{illus.soft_skill}</Badge>
                    {!isOpen && <span className="text-[10px] text-slate-500 truncate">{preview.substring(0, 60)}...</span>}
                  </div>
                  <div className="flex items-center gap-1 shrink-0" onClick={e => e.stopPropagation()}>
                    <Button variant="ghost" size="sm" className="h-5 text-[9px] px-1.5 text-blue-600 hover:text-blue-800 hover:bg-blue-50" onClick={() => { setExpanded(true); startEdit(illus); }} data-testid={`edit-illus-${illus.id}`}>
                      <Edit3 className="w-2.5 h-2.5 mr-0.5" />Modifier
                    </Button>
                    {!illus.sare_text && !illus.star_text && (
                      <Button variant="ghost" size="sm" className="h-5 text-[9px] px-1.5 text-amber-700 hover:text-amber-900 hover:bg-amber-50" onClick={() => handleSare(illus.id)} disabled={rewritingId === illus.id} data-testid={`sare-btn-${illus.id}`}>
                        {rewritingId === illus.id ? <Loader2 className="w-2.5 h-2.5 animate-spin" /> : <Sparkles className="w-2.5 h-2.5 mr-0.5" />}
                        S.A.R.E
                      </Button>
                    )}
                    <Button variant="ghost" size="sm" className="h-5 w-5 p-0 text-slate-400 hover:text-red-500" onClick={() => handleDeleteIllus(illus.id)}>
                      <Trash2 className="w-2.5 h-2.5" />
                    </Button>
                  </div>
                </div>
                {/* Body - collapsible */}
                {isOpen && (
                  <div className="px-3 pb-3 pt-0">
                    {(illus.sare_situation || illus.sare_action) ? (
                      <div className="space-y-1 text-xs">
                        {illus.sare_situation && <p className="text-slate-700"><span className="font-bold text-amber-800">S</span> {illus.sare_situation}</p>}
                        {illus.sare_action && <p className="text-slate-700"><span className="font-bold text-amber-800">A</span> {illus.sare_action}</p>}
                        {illus.sare_resultat && <p className="text-slate-700"><span className="font-bold text-amber-800">R</span> {illus.sare_resultat}</p>}
                        {illus.sare_enseignement && <p className="text-slate-700"><span className="font-bold text-amber-800">E</span> {illus.sare_enseignement}</p>}
                      </div>
                    ) : (
                      <p className="text-xs text-slate-700">{illus.situation_text}</p>
                    )}
                    {(illus.sare_text || illus.star_text) && (
                      <div className="mt-2 pt-2 border-t border-emerald-200">
                        <p className="text-[10px] font-semibold text-emerald-700 mb-0.5 flex items-center gap-1">
                          <Award className="w-3 h-3" />Reformulation S.A.R.E par l'IA :
                        </p>
                        <p className="text-xs text-emerald-800 leading-relaxed">{illus.sare_text || illus.star_text}</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
              );
            })}
          </div>
        )}

        {/* Expandable: S.A.R.E form for adding/editing */}
        {expanded && (
          <div className="mt-3 pt-3 border-t border-slate-100 space-y-3" data-testid={`illus-section-${exp.id}`}>
            {/* S.A.R.E Method Explainer */}
            <div className="bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 rounded-xl p-3 space-y-2" data-testid="sare-explainer">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-amber-100 flex items-center justify-center shrink-0">
                  <Award className="w-4 h-4 text-amber-700" />
                </div>
                <div>
                  <p className="text-xs font-bold text-amber-900">Méthode S.A.R.E — Prouvez vos compétences</p>
                  <p className="text-[10px] text-amber-700">Dire "je suis organisé" est insuffisant. Racontez une situation concrète pour le prouver.</p>
                </div>
              </div>
              <div className="grid grid-cols-4 gap-1.5">
                <div className="bg-white/70 rounded-lg px-2 py-1.5 text-center border border-amber-100">
                  <p className="text-sm font-black text-amber-800">S</p>
                  <p className="text-[9px] text-amber-600 leading-tight">Situation</p>
                </div>
                <div className="bg-white/70 rounded-lg px-2 py-1.5 text-center border border-amber-100">
                  <p className="text-sm font-black text-amber-800">A</p>
                  <p className="text-[9px] text-amber-600 leading-tight">Action</p>
                </div>
                <div className="bg-white/70 rounded-lg px-2 py-1.5 text-center border border-amber-100">
                  <p className="text-sm font-black text-amber-800">R</p>
                  <p className="text-[9px] text-amber-600 leading-tight">Résultat</p>
                </div>
                <div className="bg-white/70 rounded-lg px-2 py-1.5 text-center border border-amber-100">
                  <p className="text-sm font-black text-amber-800">E</p>
                  <p className="text-[9px] text-amber-600 leading-tight">Enseignement</p>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <p className="text-xs font-semibold text-slate-600 flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-emerald-500" />{editingId ? "Modifier la preuve" : "Ajouter une nouvelle preuve"}
              </p>
              <Button variant="outline" size="sm" className="h-6 text-[10px] px-2" onClick={handleSuggest} disabled={suggesting} data-testid={`suggest-btn-${exp.id}`}>
                {suggesting ? <Loader2 className="w-3 h-3 animate-spin mr-1" /> : <Brain className="w-3 h-3 mr-1" />}
                IA : suggérer
              </Button>
            </div>

            {/* AI Suggestions */}
            {suggestions && suggestions.length > 0 && (
              <div className="bg-blue-50 border border-blue-100 rounded-lg p-2.5 space-y-1.5">
                <p className="text-[10px] font-semibold text-blue-700">Suggestions du Coach IA :</p>
                {suggestions.map((s, i) => (
                  <button key={i} onClick={() => { setSelectedSkill(s.skill); setSuggestions(null); }} className="w-full text-left flex items-start gap-2 text-xs bg-white rounded-lg px-2 py-1.5 border border-blue-100 hover:border-blue-300 transition-colors" data-testid={`suggestion-${i}`}>
                    <Brain className="w-3 h-3 text-blue-500 mt-0.5 shrink-0" />
                    <div><span className="font-semibold text-blue-700">{s.skill}</span> <span className="text-slate-500">— {s.hint}</span></div>
                  </button>
                ))}
              </div>
            )}

            {/* S.A.R.E Guided Form */}
            <div className="space-y-2">
              <Select value={selectedSkill} onValueChange={(val) => {
                setSelectedSkill(val);
                // Determine skill type based on which list the skill belongs to
                if ((hardSkills || []).includes(val)) {
                  setSelectedSkillType("hard");
                } else {
                  setSelectedSkillType("soft");
                }
              }}>
                <SelectTrigger className="h-8 text-xs" data-testid={`skill-select-${exp.id}`}>
                  <SelectValue placeholder="Choisir une compétence à illustrer..." />
                </SelectTrigger>
                <SelectContent>
                  {(softSkills || []).filter(s => !illustratedSkills.has(s) || s === selectedSkill).length > 0 && (
                    <>
                      <div className="px-2 py-1.5 text-[10px] font-bold text-rose-600 uppercase tracking-wide">Soft skills (savoir-être)</div>
                      {(softSkills || []).filter(s => !illustratedSkills.has(s) || s === selectedSkill).map((s, i) => (
                        <SelectItem key={`soft-${i}`} value={s} className="text-xs">{s}</SelectItem>
                      ))}
                    </>
                  )}
                  {(hardSkills || []).filter(s => !illustratedSkills.has(s) || s === selectedSkill).length > 0 && (
                    <>
                      <div className="px-2 py-1.5 text-[10px] font-bold text-sky-600 uppercase tracking-wide border-t mt-1 pt-1.5">Hard skills (savoir-faire)</div>
                      {(hardSkills || []).filter(s => !illustratedSkills.has(s) || s === selectedSkill).map((s, i) => (
                        <SelectItem key={`hard-${i}`} value={s} className="text-xs">{s}</SelectItem>
                      ))}
                    </>
                  )}
                </SelectContent>
              </Select>
              {selectedSkill && (
                <div className="space-y-2 bg-slate-50 border border-slate-200 rounded-xl p-3" data-testid={`sare-form-${exp.id}`}>
                  <p className="text-xs font-semibold text-slate-700 flex items-center gap-1.5">
                    <Award className="w-3.5 h-3.5 text-amber-600" />
                    Décrivez une situation concrète illustrant « {selectedSkill} »
                    <Badge className={`text-[9px] ml-1 ${selectedSkillType === "hard" ? "bg-sky-100 text-sky-700" : "bg-rose-100 text-rose-700"}`}>
                      {selectedSkillType === "hard" ? "Hard skill" : "Soft skill"}
                    </Badge>
                  </p>
                  {/* S - Situation */}
                  <div>
                    <label className="flex items-center gap-1.5 text-[11px] font-bold text-amber-800 mb-0.5">
                      <span className="inline-flex items-center justify-center w-4 h-4 rounded bg-amber-100 text-[10px] font-black">S</span>
                      Situation — Le contexte
                    </label>
                    <textarea
                      value={sareSituation}
                      onChange={e => setSareSituation(e.target.value)}
                      placeholder="Dans mon poste de..., j'ai été confronté à... (Où ? Quand ? Quel contexte ?)"
                      className="w-full text-xs border border-slate-200 rounded-lg p-2 min-h-[48px] resize-y focus:outline-none focus:ring-2 focus:ring-amber-200 focus:border-amber-300 bg-white"
                      data-testid={`sare-situation-${exp.id}`}
                    />
                  </div>
                  {/* A - Action */}
                  <div>
                    <label className="flex items-center gap-1.5 text-[11px] font-bold text-amber-800 mb-0.5">
                      <span className="inline-flex items-center justify-center w-4 h-4 rounded bg-amber-100 text-[10px] font-black">A</span>
                      Action — Ce que vous avez fait
                    </label>
                    <textarea
                      value={sareAction}
                      onChange={e => setSareAction(e.target.value)}
                      placeholder="J'ai décidé de... / J'ai mis en place... / J'ai proposé..."
                      className="w-full text-xs border border-slate-200 rounded-lg p-2 min-h-[48px] resize-y focus:outline-none focus:ring-2 focus:ring-amber-200 focus:border-amber-300 bg-white"
                      data-testid={`sare-action-${exp.id}`}
                    />
                  </div>
                  {/* R - Résultat */}
                  <div>
                    <label className="flex items-center gap-1.5 text-[11px] font-bold text-amber-800 mb-0.5">
                      <span className="inline-flex items-center justify-center w-4 h-4 rounded bg-amber-100 text-[10px] font-black">R</span>
                      Résultat — L'impact obtenu
                    </label>
                    <textarea
                      value={sareResultat}
                      onChange={e => setSareResultat(e.target.value)}
                      placeholder="Cela a permis de... / Le résultat mesurable a été..."
                      className="w-full text-xs border border-slate-200 rounded-lg p-2 min-h-[48px] resize-y focus:outline-none focus:ring-2 focus:ring-amber-200 focus:border-amber-300 bg-white"
                      data-testid={`sare-resultat-${exp.id}`}
                    />
                  </div>
                  {/* E - Enseignement */}
                  <div>
                    <label className="flex items-center gap-1.5 text-[11px] font-bold text-amber-800 mb-0.5">
                      <span className="inline-flex items-center justify-center w-4 h-4 rounded bg-amber-100 text-[10px] font-black">E</span>
                      Enseignement — Ce que ça dit de vous
                    </label>
                    <textarea
                      value={sareEnseignement}
                      onChange={e => setSareEnseignement(e.target.value)}
                      placeholder="Cela montre que je suis capable de... / Cette situation démontre ma..."
                      className="w-full text-xs border border-slate-200 rounded-lg p-2 min-h-[48px] resize-y focus:outline-none focus:ring-2 focus:ring-amber-200 focus:border-amber-300 bg-white"
                      data-testid={`sare-enseignement-${exp.id}`}
                    />
                  </div>
                  {/* Example hint */}
                  <div className="bg-white border border-dashed border-amber-200 rounded-lg p-2">
                    <p className="text-[10px] text-amber-700 leading-relaxed">
                      <span className="font-bold">Exemple :</span> "Lors d'un pic d'activité, nous avions un retard important. J'ai priorisé les tâches et redistribué les missions. Nous avons rattrapé le retard en 3 jours sans erreur. Cela montre ma capacité à gérer le stress et rester efficace sous pression."
                    </p>
                  </div>
                  <Button size="sm" className="h-7 text-xs bg-emerald-600 hover:bg-emerald-700 w-full" onClick={handleSave} disabled={saving || (!sareSituation.trim() && !sareAction.trim())} data-testid={`save-illus-${exp.id}`}>
                    {saving ? <Loader2 className="w-3 h-3 animate-spin mr-1" /> : <Check className="w-3 h-3 mr-1" />}
                    {editingId ? "Mettre à jour la preuve S.A.R.E" : "Enregistrer la preuve S.A.R.E"}
                  </Button>
                  {editingId && (
                    <Button variant="outline" size="sm" className="h-7 text-xs w-full" onClick={resetForm} data-testid={`cancel-edit-${exp.id}`}>
                      <X className="w-3 h-3 mr-1" />Annuler la modification
                    </Button>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

const LearningCard = ({ item }) => {
  const statusConfig = { en_cours: { label: "En cours", color: "bg-blue-100 text-blue-700" }, termine: { label: "Terminé", color: "bg-emerald-100 text-emerald-700" }, valide: { label: "Validé", color: "bg-green-100 text-green-800" } };
  const sc = statusConfig[item.status] || statusConfig.en_cours;
  return (
    <Card data-testid="learning-card">
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-2">
          <h4 className="font-semibold text-slate-900 text-sm">{item.title}</h4>
          <Badge className={`text-xs ${sc.color}`}>{sc.label}</Badge>
        </div>
        {item.provider && <p className="text-xs text-slate-500 mb-2">{item.provider}</p>}
        {item.skills_acquired?.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {item.skills_acquired.map((s, i) => <Badge key={i} variant="secondary" className="text-xs">{s}</Badge>)}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

const PasserelleCard = ({ passerelle }) => {
  const accessConfig = {
    accessible: { label: "Accessible directement", color: "bg-emerald-100 text-emerald-700" },
    formation_courte: { label: "Formation courte requise", color: "bg-amber-100 text-amber-700" },
    formation_longue: { label: "Formation longue requise", color: "bg-rose-100 text-rose-700" },
  };
  const ac = accessConfig[passerelle.accessibility] || accessConfig.accessible;
  const score = Math.round((passerelle.compatibility_score || 0) * 100);

  return (
    <Card className="hover:shadow-md transition-shadow border-l-4 border-l-blue-500" data-testid="passerelle-card">
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-2">
          <div>
            <h4 className="font-semibold text-slate-900 text-base flex items-center gap-2">
              <ArrowRight className="w-4 h-4 text-blue-600" />{passerelle.job_name}
            </h4>
            {passerelle.sector && <p className="text-sm text-slate-500 ml-6">{passerelle.sector}</p>}
          </div>
          <div className="text-right">
            <span className="text-2xl font-bold text-blue-600">{score}%</span>
            <p className="text-xs text-slate-500">compatibilité</p>
          </div>
        </div>
        <Badge className={`text-xs ${ac.color} mb-3`}>{ac.label}</Badge>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-2">
          {passerelle.shared_skills?.length > 0 && (
            <div>
              <p className="text-xs font-medium text-emerald-700 mb-1">Compétences partagées</p>
              <div className="flex flex-wrap gap-1">
                {passerelle.shared_skills.map((s, i) => <Badge key={i} className="bg-emerald-50 text-emerald-700 text-xs">{s}</Badge>)}
              </div>
            </div>
          )}
          {passerelle.skills_to_acquire?.length > 0 && (
            <div>
              <p className="text-xs font-medium text-amber-700 mb-1">À acquérir</p>
              <div className="flex flex-wrap gap-1">
                {passerelle.skills_to_acquire.map((s, i) => <Badge key={i} className="bg-amber-50 text-amber-700 text-xs">{s}</Badge>)}
              </div>
            </div>
          )}
        </div>
        {passerelle.training_needed && (
          <p className="text-xs text-slate-600 mt-2 p-2 bg-slate-50 rounded"><GraduationCap className="w-3 h-3 inline mr-1" />{passerelle.training_needed}</p>
        )}
      </CardContent>
    </Card>
  );
};

// ============== ARCHÉOLOGIE TAB ==============

const ArcheologieTab = ({ archeologie, loading, onLoad, savoirFaire, savoirEtre, nonClassees, dclicProfile }) => {
  const [referentiel, setReferentiel] = useState(null);
  const [loadingRef, setLoadingRef] = useState(false);

  const loadReferentiel = async () => {
    setLoadingRef(true);
    try {
      const res = await axios.get(`${API}/referentiel/archeologie`);
      setReferentiel(res.data);
    } catch (e) { toast.error("Erreur chargement référentiel"); }
    setLoadingRef(false);
  };

  useEffect(() => { loadReferentiel(); }, []);

  const dclicSE = savoirEtre.filter(c => c.source === "dclic_pro");

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-[#1e3a5f] flex items-center gap-2">
            <Layers className="w-5 h-5" />Archéologie des Compétences
          </h3>
          <p className="text-sm text-slate-500">La chaîne hiérarchique : Métier → Savoir-faire → Savoir-être → Qualités → Valeurs → Vertus</p>
        </div>
        <Button onClick={onLoad} disabled={loading} data-testid="load-archeologie-btn">
          {loading ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Layers className="w-4 h-4 mr-2" />}
          {loading ? "Chargement..." : "Analyser mon profil"}
        </Button>
      </div>

      {/* D'CLIC boost banner */}
      {dclicProfile?.dclic_imported ? (
        <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-100 rounded-lg px-3 py-2 text-xs text-emerald-700" data-testid="archeologie-dclic-boost">
          <Sparkles className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
          <span>D'CLIC PRO enrichit l'archéologie : {dclicSE.length > 0 ? `${dclicSE.length} savoir-être issus de votre profil de personnalité` : "vos données de personnalité"} permettent de remonter plus profondément la chaîne des qualités, valeurs et vertus{dclicProfile.dclic_vertu_dominante ? ` (vertu dominante : ${dclicProfile.dclic_vertu_dominante})` : ""}.</span>
        </div>
      ) : (
        <div className="rounded-xl border-2 border-dashed border-amber-300 bg-gradient-to-r from-amber-50 to-orange-50 p-4" data-testid="archeologie-dclic-needed">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-xl bg-amber-100 flex items-center justify-center shrink-0">
              <Sparkles className="w-5 h-5 text-amber-600" />
            </div>
            <div className="flex-1">
              <h4 className="text-sm font-bold text-amber-900">Boostez votre Archéologie avec D'CLIC PRO</h4>
              <p className="text-xs text-amber-700 mt-1 leading-relaxed">
                Pour obtenir une Archéologie des Compétences personnalisée et complète, passez le test <strong>D'CLIC PRO</strong>.
                Il révélera votre personnalité, vos dimensions DISC et vos vertus dominantes — permettant de remonter la chaîne complète :
                Savoir-faire → Savoir-être → Qualités → Valeurs → Vertus.
              </p>
              <Button
                size="sm"
                className="mt-2.5 bg-amber-500 hover:bg-amber-600 text-white gap-1.5 shadow-sm"
                onClick={() => window.open('/test-dclic', '_blank')}
                data-testid="archeologie-launch-dclic-btn"
              >
                <Sparkles className="w-3.5 h-3.5" />
                Passer le test D'CLIC PRO
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Hierarchy Explanation */}
      <Card className="bg-gradient-to-r from-[#1e3a5f] to-[#2d5a8e] text-white border-0">
        <CardContent className="p-5">
          <h4 className="font-semibold mb-3">Le modèle RE'ACTIF PRO</h4>
          <div className="flex flex-wrap items-center gap-2 text-sm">
            <span className="bg-sky-400/30 px-3 py-1 rounded-full">Savoir-faire</span>
            <ChevronRight className="w-4 h-4 text-white/50" />
            <span className="bg-rose-400/30 px-3 py-1 rounded-full">Savoir-être</span>
            <ChevronRight className="w-4 h-4 text-white/50" />
            <span className="bg-amber-400/30 px-3 py-1 rounded-full">Qualités humaines</span>
            <ChevronRight className="w-4 h-4 text-white/50" />
            <span className="bg-emerald-400/30 px-3 py-1 rounded-full">Valeurs</span>
            <ChevronRight className="w-4 h-4 text-white/50" />
            <span className="bg-violet-400/30 px-3 py-1 rounded-full">Vertus</span>
          </div>
          <p className="text-blue-200 text-xs mt-3">L'orientation professionnelle part des compétences techniques vers les savoir-être, pour révéler les qualités humaines, les valeurs et les vertus qui vous animent.</p>
        </CardContent>
      </Card>

      {/* Summary stats */}
      {archeologie && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <Card><CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-sky-600">{archeologie.summary.savoir_faire}</div>
            <p className="text-xs text-slate-500">Savoir-faire</p>
          </CardContent></Card>
          <Card><CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-rose-500">{archeologie.summary.savoir_etre}</div>
            <p className="text-xs text-slate-500">Savoir-être</p>
          </CardContent></Card>
          <Card><CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-emerald-600">{archeologie.summary.valeurs_covered?.length || 0}</div>
            <p className="text-xs text-slate-500">Valeurs couvertes</p>
          </CardContent></Card>
          <Card><CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-violet-600">{archeologie.summary.vertus_covered?.length || 0}</div>
            <p className="text-xs text-slate-500">Vertus activées</p>
          </CardContent></Card>
        </div>
      )}

      {/* Chains: savoir-être traced to vertus */}
      {archeologie?.chains?.length > 0 && (
        <div>
          <h4 className="font-medium text-slate-700 mb-3">Chaînes identifiées (Savoir-être → Vertus)</h4>
          <div className="space-y-3">
            {archeologie.chains.map((chain, i) => (
              <Card key={i} className="border-l-4 border-l-rose-400" data-testid="archeologie-chain">
                <CardContent className="p-4">
                  <h5 className="font-semibold text-slate-900 text-sm mb-2">{chain.competence}</h5>
                  <div className="flex flex-wrap items-center gap-1.5">
                    <Badge className="bg-rose-100 text-rose-700 text-xs">{chain.competence}</Badge>
                    {chain.qualites?.length > 0 && (
                      <>
                        <ChevronRight className="w-3 h-3 text-slate-300" />
                        {chain.qualites.map((q, j) => <Badge key={j} variant="outline" className="text-xs text-amber-700 bg-amber-50">{q}</Badge>)}
                      </>
                    )}
                    {chain.valeurs?.length > 0 && (
                      <>
                        <ChevronRight className="w-3 h-3 text-slate-300" />
                        {chain.valeurs.map((v, j) => <Badge key={j} variant="outline" className="text-xs text-emerald-700 bg-emerald-50">{v}</Badge>)}
                      </>
                    )}
                    {chain.vertus?.length > 0 && (
                      <>
                        <ChevronRight className="w-3 h-3 text-slate-300" />
                        {chain.vertus.map((v, j) => <Badge key={j} variant="outline" className="text-xs text-violet-700 bg-violet-50">{v}</Badge>)}
                      </>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Non-classified competences warning */}
      {archeologie && archeologie.summary.non_classees > 0 && (
        <Card className="border-amber-200 bg-amber-50/50">
          <CardContent className="p-4">
            <p className="text-sm text-amber-800 font-medium">{archeologie.summary.non_classees} compétence(s) non classée(s)</p>
            <p className="text-xs text-amber-600">Précisez leur nature (savoir-faire ou savoir-être) dans l'onglet Compétences pour compléter l'archéologie.</p>
          </CardContent>
        </Card>
      )}

      {/* Referentiel: Les 6 Vertus */}
      {referentiel && (
        <div>
          <h4 className="font-medium text-slate-700 mb-3">Les 6 Vertus et leurs chaînes</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {referentiel.vertus.map(vertu => {
              const vc = VERTU_COLORS[vertu.id] || VERTU_COLORS.sagesse;
              const isCovered = archeologie?.summary?.vertus_covered?.includes(vertu.id);
              return (
                <Card key={vertu.id} className={`${vc.bg} border ${vc.border} ${isCovered ? "ring-2 ring-offset-1" : "opacity-60"}`} style={isCovered ? { ringColor: vc.accent } : {}} data-testid={`vertu-card-${vertu.id}`}>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h5 className={`font-semibold text-sm ${vc.text}`}>{vertu.name}</h5>
                      {isCovered && <Badge className="bg-emerald-500 text-white text-xs">Activée</Badge>}
                    </div>
                    <p className="text-xs text-slate-600 mb-2">{vertu.description}</p>
                    <div className="space-y-1.5">
                      <div>
                        <p className="text-xs font-medium text-slate-500">Qualités associées :</p>
                        <div className="flex flex-wrap gap-1 mt-0.5">
                          {vertu.qualites?.slice(0, 4).map((q, i) => <Badge key={i} variant="outline" className="text-xs">{q}</Badge>)}
                        </div>
                      </div>
                      <div>
                        <p className="text-xs font-medium text-slate-500">Savoir-être :</p>
                        <div className="flex flex-wrap gap-1 mt-0.5">
                          {vertu.savoirs_etre?.slice(0, 3).map((s, i) => <Badge key={i} className="text-xs bg-rose-50 text-rose-600">{s}</Badge>)}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      )}

      {!archeologie && !loading && (
        <EmptyState text="Cliquez sur 'Analyser mon profil' pour visualiser l'archéologie de vos compétences" />
      )}
    </div>
  );
};

export default PassportView;
;
