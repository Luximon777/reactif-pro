import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import {
  Shield, Lock, Share2, FileText, GraduationCap, Briefcase, Award, Target,
  Users, BookOpen, Search, Upload, Download, Trash2, Plus, Eye, FolderLock,
  CheckCircle2, Clock, AlertTriangle, QrCode, ArrowRight, Sparkles, Brain,
  TrendingUp, Loader2, X, Zap, FileIcon, ExternalLink, History, Compass, Globe, MessageSquare,
  ChevronDown, Pencil
} from "lucide-react";
import { toast } from "sonner";
import { QRCodeSVG } from "qrcode.react";

// OPC Consent Toggle — visible in coffre-fort only when org is certified
const OpcConsentToggle = ({ token, organization, onUpdate }) => {
  const [consent, setConsent] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${API}/coffre/opc-consent?token=${token}&organization=${encodeURIComponent(organization)}`)
      .then(r => setConsent(r.data.opc_consent || false))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [token, organization]);

  const toggle = async () => {
    const newVal = !consent;
    setConsent(newVal);
    try {
      await axios.post(`${API}/coffre/opc-consent?token=${token}`, { organization, opc_consent: newVal });
      toast.success(newVal ? "Contribution OPC activée" : "Contribution OPC désactivée");
      if (onUpdate) onUpdate();
    } catch { toast.error("Erreur"); setConsent(!newVal); }
  };

  if (loading) return null;
  return (
    <label className="flex items-start gap-2 cursor-pointer bg-blue-50 border border-blue-200 rounded-lg p-2 mt-1" data-testid={`opc-consent-${organization}`}>
      <input type="checkbox" checked={consent} onChange={toggle} className="mt-0.5 rounded border-blue-300 text-blue-600 focus:ring-blue-500" />
      <div>
        <span className="text-[11px] font-semibold text-blue-800">Contribuer à l'Observatoire des Compétences</span>
        <p className="text-[9px] text-blue-600 leading-tight mt-0.5">J'autorise la diffusion anonyme de mes preuves certifiées chez {organization} dans l'Observatoire Prédictif pour enrichir les fiches métiers.</p>
      </div>
    </label>
  );
};

const CoffreFortView = ({ token }) => {
  const [documents, setDocuments] = useState([]);
  const [profile, setProfile] = useState(null);
  const [passport, setPassport] = useState(null);
  const [scores, setScores] = useState(null);
  const [shares, setShares] = useState([]);
  const [illustrations, setIllustrations] = useState([]);
  const [certStatus, setCertStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("wallet");
  const [showAdnDetails, setShowAdnDetails] = useState(false);
  const [viewingDoc, setViewingDoc] = useState(null);

  // Share form
  const [showShareForm, setShowShareForm] = useState(false);
  const [shareForm, setShareForm] = useState({ recipient_name: "", recipient_type: "employeur", sections: ["identite", "competences"], duration_days: 30 });
  const [creatingShare, setCreatingShare] = useState(false);
  const [generatedShareUrl, setGeneratedShareUrl] = useState(null);

  // Upload
  const [uploadOpen, setUploadOpen] = useState(false);
  const [uploadFile, setUploadFile] = useState(null);
  const [newDoc, setNewDoc] = useState({ title: "", category: "identite_professionnelle", document_type: "cv", description: "", trust_level: "auto_declare", source_type: "utilisateur", issued_by: "", date_expiration: "", competences_liees: "" });
  const [uploading, setUploading] = useState(false);

  const loadAll = useCallback(async () => {
    try {
      const [docsRes, profRes, passRes, scoreRes, sharesRes, illusRes, certRes] = await Promise.all([
        axios.get(`${API}/coffre/documents?token=${token}`),
        axios.get(`${API}/profile?token=${token}`),
        axios.get(`${API}/passport?token=${token}`),
        axios.get(`${API}/profile/confidence-scores/simple?token=${token}`).catch(() => ({ data: null })),
        axios.get(`${API}/shares?token=${token}`).catch(() => ({ data: { shares: [] } })),
        axios.get(`${API}/passport/illustrations?token=${token}`).catch(() => ({ data: { illustrations: [] } })),
        axios.get(`${API}/coffre/certification-status?token=${token}`).catch(() => ({ data: null })),
      ]);
      setDocuments(docsRes.data || []);
      setProfile(profRes.data);
      setPassport(passRes.data);
      setScores(scoreRes.data);
      setShares(sharesRes.data.shares || []);
      setIllustrations(illusRes.data.illustrations || []);
      setCertStatus(certRes.data);
    } catch { /* silent */ }
    setLoading(false);
  }, [token]);

  useEffect(() => { loadAll(); }, [loadAll]);

  const handleUpload = async () => {
    if (!newDoc.title) { toast.error("Titre requis"); return; }
    setUploading(true);
    try {
      if (uploadFile) {
        const formData = new FormData();
        formData.append("file", uploadFile);
        const params = new URLSearchParams({ token, title: newDoc.title, category: newDoc.category, document_type: newDoc.document_type, description: newDoc.description, competences_liees: newDoc.competences_liees, trust_level: newDoc.trust_level, source_type: newDoc.source_type });
        await axios.post(`${API}/coffre/upload?${params.toString()}`, formData, { headers: { "Content-Type": "multipart/form-data" } });
      } else {
        await axios.post(`${API}/coffre/documents?token=${token}`, { ...newDoc, competences_liees: newDoc.competences_liees.split(",").map(c => c.trim()).filter(Boolean) });
      }
      toast.success("Document ajouté");
      setUploadOpen(false);
      setUploadFile(null);
      setNewDoc({ title: "", category: "identite_professionnelle", document_type: "cv", description: "", trust_level: "auto_declare", source_type: "utilisateur", issued_by: "", date_expiration: "", competences_liees: "" });
      loadAll();
    } catch { toast.error("Erreur"); }
    setUploading(false);
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Supprimer ce document ?")) return;
    try { await axios.delete(`${API}/coffre/documents/${id}?token=${token}`); loadAll(); toast.success("Supprimé"); } catch { toast.error("Erreur"); }
  };

  const handleCreateShare = async () => {
    if (!shareForm.recipient_name) { toast.error("Nom du destinataire requis"); return; }
    setCreatingShare(true);
    try {
      const res = await axios.post(`${API}/shares/create?token=${token}`, shareForm);
      if (res.data.share_id) {
        setGeneratedShareUrl(`${window.location.origin}/shared/${res.data.share_id}`);
        toast.success("Lien de partage créé");
        loadAll();
      }
    } catch { toast.error("Erreur"); }
    setCreatingShare(false);
  };

  const handleRevoke = async (id) => {
    try { await axios.delete(`${API}/shares/${id}?token=${token}`); loadAll(); toast.success("Partage révoqué"); } catch { toast.error("Erreur"); }
  };

  if (loading) return <div className="flex items-center justify-center h-64"><Loader2 className="w-8 h-8 animate-spin text-slate-400" /></div>;

  const displayName = profile?.real_first_name || profile?.pseudo || "Utilisateur";
  const displayFullName = (profile?.real_first_name && profile?.real_last_name)
    ? `${profile.real_first_name} ${profile.real_last_name}`
    : profile?.pseudo || "Utilisateur";
  const avatarLetter = (profile?.real_first_name || profile?.pseudo || "U")[0].toUpperCase();
  const totalDocs = documents.length;
  const totalSkillsProved = illustrations.length;
  const activeShares = shares.filter(s => s.active).length;
  const expiringDocs = documents.filter(d => d.date_expiration && ((new Date(d.date_expiration) - new Date()) / 86400000) < 90 && ((new Date(d.date_expiration) - new Date()) / 86400000) > -30).length;
  const trustPct = scores?.global_pct || 0;
  const trustLevel = scores?.level || "faible";
  const trustColor = trustLevel === "eleve" ? "emerald" : trustLevel === "moyen" ? "amber" : "rose";

  const sectionLabels = { identite: "Identité", experiences: "Expériences", competences: "Compétences", formations: "Formations", soft_skills: "Soft Skills prouvés", adn_pro: "ADN Pro" };

  return (
    <div className="space-y-6" data-testid="portefeuille-view">
      {/* === HEADER === */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-[#0f2744] via-[#1e3a5f] to-[#0f2744] p-6" data-testid="wallet-header">
        <div className="absolute top-0 right-0 w-72 h-72 bg-white/3 rounded-full -translate-y-20 translate-x-20" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <FolderLock className="w-6 h-6 text-cyan-400" />
              <h1 className="text-xl font-bold text-white" style={{ fontFamily: 'Outfit, sans-serif' }}>Portefeuille de Compétences Certifiées</h1>
            </div>
            <p className="text-blue-200 text-sm">EUDI vérifie qui vous êtes — RE'ACTIF PRO révèle ce que vous pouvez devenir</p>
            <div className="flex items-center gap-2 mt-2">
              <Badge className="bg-cyan-500/20 text-cyan-300 border border-cyan-400/30 text-[10px]"><Shield className="w-3 h-3 mr-1" />Conforme EUDI</Badge>
              <Badge className="bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 text-[10px]"><Lock className="w-3 h-3 mr-1" />Chiffré</Badge>
              <Badge className="bg-violet-500/20 text-violet-300 border border-violet-400/30 text-[10px]"><Share2 className="w-3 h-3 mr-1" />Partage sélectif</Badge>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className={`text-center px-4 py-2 rounded-xl bg-${trustColor}-500/20 border border-${trustColor}-400/30`}>
              <p className={`text-2xl font-bold text-${trustColor}-300`}>{trustPct}%</p>
              <p className="text-[10px] text-blue-200">Score confiance</p>
            </div>
            <img src="/eudi_wallet_logo.png" alt="EUDI Wallet" className="h-16 w-auto rounded-xl" />
            <Dialog open={uploadOpen} onOpenChange={setUploadOpen}>
              <DialogTrigger asChild>
                <Button className="bg-white text-[#1e3a5f] hover:bg-blue-50 font-semibold" data-testid="add-doc-btn"><Plus className="w-4 h-4 mr-1" />Ajouter une preuve</Button>
              </DialogTrigger>
              <DialogContent className="max-w-lg max-h-[85vh] overflow-y-auto">
                <DialogHeader>
                  <DialogTitle>Ajouter une preuve au portefeuille</DialogTitle>
                  <DialogDescription>Chaque document est une preuve qui renforce votre identité professionnelle</DialogDescription>
                </DialogHeader>
                <div className="space-y-3 mt-3">
                  <div className="border-2 border-dashed rounded-lg p-3 text-center cursor-pointer transition-colors hover:border-[#1e3a5f] hover:bg-slate-50" onClick={() => document.getElementById("vault-file").click()} data-testid="file-upload-area">
                    <input id="vault-file" type="file" className="hidden" accept=".pdf,.docx,.doc,.txt,.jpg,.jpeg,.png,.xlsx,.csv" onChange={e => { const f = e.target.files[0]; if (f) { if (f.size > 10485760) { toast.error("Max 10 Mo"); return; } setUploadFile(f); if (!newDoc.title) setNewDoc(p => ({ ...p, title: f.name.replace(/\.[^.]+$/, "") })); } }} />
                    {uploadFile ? (
                      <div className="flex items-center justify-center gap-2"><FileIcon className="w-4 h-4 text-emerald-600" /><span className="text-sm text-emerald-700">{uploadFile.name}</span><Button variant="ghost" size="icon" className="h-5 w-5" onClick={e => { e.stopPropagation(); setUploadFile(null); }}><X className="w-3 h-3" /></Button></div>
                    ) : (<div><Upload className="w-6 h-6 mx-auto text-slate-400 mb-1" /><p className="text-xs text-slate-500">Cliquez pour sélectionner un fichier</p></div>)}
                  </div>
                  <Input placeholder="Titre de la preuve *" value={newDoc.title} onChange={e => setNewDoc({ ...newDoc, title: e.target.value })} data-testid="doc-title-input" />
                  <div className="grid grid-cols-2 gap-2">
                    <Select value={newDoc.trust_level} onValueChange={v => setNewDoc({ ...newDoc, trust_level: v })}>
                      <SelectTrigger className="text-xs" data-testid="doc-trust-select"><SelectValue placeholder="Niveau de fiabilité" /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="auto_declare">Auto-déclaré</SelectItem>
                        <SelectItem value="verifie">Vérifié</SelectItem>
                        <SelectItem value="valide">Validé</SelectItem>
                        <SelectItem value="certifie">Certifié</SelectItem>
                      </SelectContent>
                    </Select>
                    <Select value={newDoc.source_type} onValueChange={v => setNewDoc({ ...newDoc, source_type: v })}>
                      <SelectTrigger className="text-xs" data-testid="doc-source-select"><SelectValue placeholder="Source" /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="utilisateur">Utilisateur</SelectItem>
                        <SelectItem value="organisme">Organisme</SelectItem>
                        <SelectItem value="employeur">Employeur</SelectItem>
                        <SelectItem value="conseiller">Conseiller</SelectItem>
                        <SelectItem value="systeme">Système</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <Select value={newDoc.category} onValueChange={v => setNewDoc({ ...newDoc, category: v })}>
                      <SelectTrigger className="text-xs"><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="identite_professionnelle">Identité professionnelle</SelectItem>
                        <SelectItem value="diplomes_certifications">Diplômes & certifications</SelectItem>
                        <SelectItem value="experiences_professionnelles">Expériences professionnelles</SelectItem>
                        <SelectItem value="competences_preuves">Compétences & preuves</SelectItem>
                        <SelectItem value="formation_apprentissages">Formation & apprentissages</SelectItem>
                        <SelectItem value="accompagnement_insertion">Accompagnement & bilans</SelectItem>
                        <SelectItem value="documents_administratifs">Documents administratifs</SelectItem>
                      </SelectContent>
                    </Select>
                    <Input type="date" placeholder="Expiration" value={newDoc.date_expiration} onChange={e => setNewDoc({ ...newDoc, date_expiration: e.target.value })} className="text-xs" />
                  </div>
                  <Input placeholder="Émis par (organisme, employeur...)" value={newDoc.issued_by} onChange={e => setNewDoc({ ...newDoc, issued_by: e.target.value })} className="text-xs" />
                  <Input placeholder="Compétences liées (séparées par virgules)" value={newDoc.competences_liees} onChange={e => setNewDoc({ ...newDoc, competences_liees: e.target.value })} className="text-xs" />
                  <Textarea placeholder="Description..." rows={2} value={newDoc.description} onChange={e => setNewDoc({ ...newDoc, description: e.target.value })} className="text-xs" />
                  <Button className="w-full bg-[#1e3a5f]" onClick={handleUpload} disabled={uploading} data-testid="submit-doc-btn">
                    {uploading ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : <Plus className="w-4 h-4 mr-1" />}Ajouter au portefeuille
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </div>
      </div>

      {/* ═══ ADN PROFESSIONNEL (dans le bandeau) ═══ */}
      {passport?.identity_adn && (
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-[#0f2744] via-[#1e3a5f] to-[#0f2744] px-6 py-4 -mt-4" data-testid="adn-pro-banner">
          <div className="relative z-10">
            <button
              onClick={() => setShowAdnDetails(!showAdnDetails)}
              className="w-full text-left"
              data-testid="adn-pro-toggle"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <h4 className="text-sm font-bold text-cyan-400 uppercase tracking-wide flex items-center gap-1.5 mb-1.5">
                    <Compass className="w-4 h-4" />ADN Professionnel
                  </h4>
                  <p className={`text-sm text-slate-300 leading-relaxed ${!showAdnDetails ? "line-clamp-2" : ""}`}>
                    {passport.identity_adn.synthese_adn}
                  </p>
                </div>
                <div className="flex items-center gap-1 text-cyan-400 shrink-0 mt-0.5">
                  <span className="text-xs font-medium">{showAdnDetails ? "Réduire" : "Voir plus"}</span>
                  <ChevronDown className={`w-3.5 h-3.5 transition-transform duration-200 ${showAdnDetails ? "rotate-180" : ""}`} />
                </div>
              </div>
            </button>
            {showAdnDetails && (
              <div className="grid grid-cols-3 gap-4 mt-3 pt-3 border-t border-white/10">
                <div>
                  <p className="text-xs font-bold text-emerald-400 uppercase mb-1.5">Forces</p>
                  {(passport.identity_adn.forces_principales || []).slice(0, 4).map((f, i) => (
                    <div key={i} className="flex items-start gap-1.5 text-xs text-slate-300 mb-1"><CheckCircle2 className="w-3 h-3 text-emerald-400 shrink-0 mt-0.5" />{f}</div>
                  ))}
                </div>
                <div>
                  <p className="text-xs font-bold text-blue-400 uppercase mb-1.5">Environnements</p>
                  {(passport.identity_adn.environnements_favorables || []).slice(0, 3).map((e, i) => (
                    <div key={i} className="flex items-start gap-1.5 text-xs text-slate-300 mb-1"><Target className="w-3 h-3 text-blue-400 shrink-0 mt-0.5" />{e}</div>
                  ))}
                </div>
                <div>
                  <p className="text-xs font-bold text-violet-400 uppercase mb-1.5">Projection</p>
                  {(passport.identity_adn.axes_projection || []).slice(0, 3).map((a, i) => (
                    <div key={i} className="flex items-start gap-1.5 text-xs text-slate-300 mb-1"><TrendingUp className="w-3 h-3 text-violet-400 shrink-0 mt-0.5" />{a}</div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* === 3 LAYERS TABS === */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid grid-cols-3 h-auto p-1 bg-slate-100">
          <TabsTrigger value="wallet" className="py-2.5 text-xs sm:text-sm gap-1.5" data-testid="tab-wallet">
            <Shield className="w-4 h-4" /><span className="hidden sm:inline">Couche 1 :</span> Confiance
          </TabsTrigger>
          <TabsTrigger value="intelligence" className="py-2.5 text-xs sm:text-sm gap-1.5" data-testid="tab-intelligence">
            <Brain className="w-4 h-4" /><span className="hidden sm:inline">Couche 2 :</span> Intelligence
          </TabsTrigger>
          <TabsTrigger value="actions" className="py-2.5 text-xs sm:text-sm gap-1.5" data-testid="tab-actions">
            <Zap className="w-4 h-4" /><span className="hidden sm:inline">Couche 3 :</span> Actions
          </TabsTrigger>
        </TabsList>

        {/* ============ COUCHE 1 : CONFIANCE (Wallet) ============ */}
        <TabsContent value="wallet" className="space-y-4">
          {/* Identity card */}
          <Card className="border-0 bg-gradient-to-r from-blue-50 to-cyan-50 overflow-hidden" data-testid="identity-card">
            <CardContent className="p-5">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 rounded-xl bg-[#1e3a5f] flex items-center justify-center text-white text-xl font-bold">{avatarLetter}</div>
                <div className="flex-1">
                  <h3 className="text-base font-bold text-slate-900">{displayFullName}</h3>
                  <p className="text-xs text-slate-500">Identifiant RE'ACTIF PRO : {profile?.pseudo}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <Badge className={`bg-${trustColor}-50 text-${trustColor}-700 border border-${trustColor}-200 text-[10px]`}>
                      <Shield className="w-3 h-3 mr-0.5" />Confiance : {trustPct}%
                    </Badge>
                    {profile?.dclic_imported && <Badge className="bg-emerald-50 text-emerald-700 border border-emerald-200 text-[10px]"><Sparkles className="w-3 h-3 mr-0.5" />D'CLIC PRO</Badge>}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Score de confiance 4D */}
          {scores && (
            <Card data-testid="trust-scores">
              <CardContent className="p-4">
                <h4 className="text-sm font-semibold text-slate-800 mb-3 flex items-center gap-2"><Shield className="w-4 h-4 text-blue-600" />Niveaux de confiance</h4>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  {scores.dimensions.map(dim => (
                    <div key={dim.key} className="bg-slate-50 rounded-lg p-3 text-center">
                      <p className="text-[10px] text-slate-500">{dim.label}</p>
                      <p className="text-xl font-bold text-slate-800 my-1">{dim.pct}%</p>
                      <Progress value={dim.pct} className="h-1" />
                    </div>
                  ))}
                </div>
                {scores.tips.length > 0 && (
                  <div className="mt-3 space-y-1">{scores.tips.map((t, i) => (
                    <div key={i} className="flex items-start gap-1.5 text-[10px] text-slate-500"><AlertTriangle className="w-3 h-3 text-amber-500 shrink-0 mt-0.5" />{t}</div>
                  ))}</div>
                )}
              </CardContent>
            </Card>
          )}

          {/* ═══ MANIFESTE & BADGES À GAGNER ═══ */}
          {certStatus && certStatus.workplaces && certStatus.workplaces.length > 0 && (
            <Card data-testid="certification-schema-couche1" className="overflow-hidden">
              <CardContent className="p-0">

                {/* ── MANIFESTE ── */}
                <div className="bg-gradient-to-br from-slate-800 via-[#1a2e4a] to-slate-900 p-6 text-white space-y-4">
                  <h3 className="text-base font-bold tracking-wide uppercase text-amber-400">Pourquoi prouver ses compétences ?</h3>
                  <p className="text-sm leading-relaxed text-slate-200">
                    Aujourd'hui, <span className="text-white font-bold">le diplôme ne suffit plus</span>. Les recruteurs veulent des <span className="text-amber-300 font-bold">preuves concrètes</span> : ce que tu as fait, comment tu l'as fait, et quel impact tu as eu. Ce sont tes <span className="text-emerald-300 font-bold">compétences prouvées par l'action</span> qui font la différence.
                  </p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
                    <div className="bg-white/10 rounded-xl p-4 backdrop-blur-sm border border-white/10">
                      <p className="text-sm font-bold text-emerald-300 mb-2 flex items-center gap-2"><Target className="w-4 h-4" />Pour toi</p>
                      <p className="text-xs text-slate-300 leading-relaxed">Valorise tes acquis auprès des recruteurs grâce à des exemples concrets (méthode S.A.R.E). Un CV qui raconte des actions vaut <span className="text-white font-semibold">10x plus</span> qu'une simple liste de diplômes.</p>
                    </div>
                    <div className="bg-white/10 rounded-xl p-4 backdrop-blur-sm border border-white/10">
                      <p className="text-sm font-bold text-blue-300 mb-2 flex items-center gap-2"><Globe className="w-4 h-4" />Pour la société</p>
                      <p className="text-xs text-slate-300 leading-relaxed">En partageant tes preuves certifiées, tu contribues à cartographier les <span className="text-white font-semibold">compétences réelles</span> du marché de l'emploi. Tu deviens un <span className="text-blue-300 font-semibold">contributeur sociétal</span>.</p>
                    </div>
                  </div>
                </div>

                {/* ── BADGES À GAGNER ── */}
                <div className="p-6 space-y-5">
                  <div className="text-center">
                    <h3 className="text-base font-bold text-slate-800">Badges à gagner</h3>
                    <p className="text-xs text-slate-500 mt-1">Complète les étapes pour débloquer tes badges et renforcer ta crédibilité</p>
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    {/* Badge 1 — Contributeur */}
                    <div className={`relative rounded-2xl p-5 text-center space-y-3 transition-all ${certStatus.badge.level >= 1 ? "bg-emerald-50 border-2 border-emerald-400 shadow-md shadow-emerald-100" : "bg-slate-50 border-2 border-dashed border-slate-200"}`}>
                      {certStatus.badge.level >= 1 && <div className="absolute -top-2 -right-2 w-6 h-6 bg-emerald-500 rounded-full flex items-center justify-center"><CheckCircle2 className="w-4 h-4 text-white" /></div>}
                      <div className={`w-14 h-14 rounded-full mx-auto flex items-center justify-center ${certStatus.badge.level >= 1 ? "bg-emerald-500 shadow-lg shadow-emerald-200" : "bg-slate-200"}`}>
                        <MessageSquare className={`w-7 h-7 ${certStatus.badge.level >= 1 ? "text-white" : "text-slate-400"}`} />
                      </div>
                      <p className={`text-sm font-bold ${certStatus.badge.level >= 1 ? "text-emerald-800" : "text-slate-500"}`}>Contributeur</p>
                      <p className={`text-xs leading-snug ${certStatus.badge.level >= 1 ? "text-emerald-700" : "text-slate-400"}`}>Prouve <strong>3 soft skills</strong> par la méthode S.A.R.E</p>
                      <div className={`rounded-lg p-2 ${certStatus.badge.level >= 1 ? "bg-emerald-100" : "bg-slate-100"}`}>
                        <p className={`text-[11px] font-semibold ${certStatus.badge.level >= 1 ? "text-emerald-700" : "text-slate-500"}`}>Situation — Action</p>
                        <p className={`text-[11px] font-semibold ${certStatus.badge.level >= 1 ? "text-emerald-700" : "text-slate-500"}`}>Résultat — Enseignement</p>
                      </div>
                      <p className={`text-xs font-bold ${certStatus.badge.level >= 1 ? "text-emerald-600" : "text-slate-400"}`}>{certStatus.stats.total_proved}/3</p>
                    </div>

                    {/* Badge 2 — Certifié */}
                    <div className={`relative rounded-2xl p-5 text-center space-y-3 transition-all ${certStatus.badge.level >= 2 ? "bg-blue-50 border-2 border-blue-400 shadow-md shadow-blue-100" : "bg-slate-50 border-2 border-dashed border-slate-200"}`}>
                      {certStatus.badge.level >= 2 && <div className="absolute -top-2 -right-2 w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center"><CheckCircle2 className="w-4 h-4 text-white" /></div>}
                      <div className={`w-14 h-14 rounded-full mx-auto flex items-center justify-center ${certStatus.badge.level >= 2 ? "bg-blue-500 shadow-lg shadow-blue-200" : "bg-slate-200"}`}>
                        <Shield className={`w-7 h-7 ${certStatus.badge.level >= 2 ? "text-white" : "text-slate-400"}`} />
                      </div>
                      <p className={`text-sm font-bold ${certStatus.badge.level >= 2 ? "text-blue-800" : "text-slate-500"}`}>Certifié</p>
                      <p className={`text-xs leading-snug ${certStatus.badge.level >= 2 ? "text-blue-700" : "text-slate-400"}`}>Uploade <strong>au moins 1 contrat</strong> de travail ou attestation</p>
                      <div className={`rounded-lg p-2 ${certStatus.badge.level >= 2 ? "bg-blue-100" : "bg-slate-100"}`}>
                        <p className={`text-[11px] font-semibold ${certStatus.badge.level >= 2 ? "text-blue-700" : "text-slate-500"}`}>Contrat, attestation,</p>
                        <p className={`text-[11px] font-semibold ${certStatus.badge.level >= 2 ? "text-blue-700" : "text-slate-500"}`}>certificat de travail</p>
                      </div>
                      <p className={`text-xs font-bold ${certStatus.badge.level >= 2 ? "text-blue-600" : "text-slate-400"}`}>{certStatus.stats.total_with_contract} contrat(s)</p>
                    </div>

                    {/* Badge 3 — Expert Certifié */}
                    <div className={`relative rounded-2xl p-5 text-center space-y-3 transition-all ${certStatus.badge.level >= 3 ? "bg-amber-50 border-2 border-amber-400 shadow-md shadow-amber-100" : "bg-slate-50 border-2 border-dashed border-slate-200"}`}>
                      {certStatus.badge.level >= 3 && <div className="absolute -top-2 -right-2 w-6 h-6 bg-amber-500 rounded-full flex items-center justify-center"><CheckCircle2 className="w-4 h-4 text-white" /></div>}
                      <div className={`w-14 h-14 rounded-full mx-auto flex items-center justify-center ${certStatus.badge.level >= 3 ? "bg-gradient-to-br from-amber-400 to-amber-600 shadow-lg shadow-amber-200" : "bg-slate-200"}`}>
                        <Award className={`w-7 h-7 ${certStatus.badge.level >= 3 ? "text-white" : "text-slate-400"}`} />
                      </div>
                      <p className={`text-sm font-bold ${certStatus.badge.level >= 3 ? "text-amber-800" : "text-slate-500"}`}>Expert Certifié</p>
                      <p className={`text-xs leading-snug ${certStatus.badge.level >= 3 ? "text-amber-700" : "text-slate-400"}`}><strong>100% prouvé</strong> + tous les contrats + Contributeur OPC</p>
                      <div className={`rounded-lg p-2 ${certStatus.badge.level >= 3 ? "bg-amber-100" : "bg-slate-100"}`}>
                        <p className={`text-[11px] font-semibold ${certStatus.badge.level >= 3 ? "text-amber-700" : "text-slate-500"}`}>Profil complet certifié</p>
                        <p className={`text-[11px] font-semibold ${certStatus.badge.level >= 3 ? "text-amber-700" : "text-slate-500"}`}>+ Impact sociétal</p>
                      </div>
                      <p className={`text-xs font-bold ${certStatus.badge.level >= 3 ? "text-amber-600" : "text-slate-400"}`}>
                        {certStatus.stats.total_proved === certStatus.stats.total_experiences && certStatus.stats.total_with_contract === certStatus.stats.total_experiences ? "Atteint !" : `${certStatus.stats.total_proved}/${certStatus.stats.total_experiences} + ${certStatus.stats.total_with_contract}/${certStatus.stats.total_experiences}`}
                      </p>
                    </div>
                  </div>

                  {/* Stats */}
                  <div className="grid grid-cols-3 gap-3 text-center">
                    <div className="bg-emerald-50 rounded-xl p-3"><p className="text-2xl font-black text-emerald-700">{certStatus.stats.total_proved}</p><p className="text-xs text-slate-500">Exp. prouvées</p></div>
                    <div className="bg-blue-50 rounded-xl p-3"><p className="text-2xl font-black text-blue-700">{certStatus.stats.total_with_contract}</p><p className="text-xs text-slate-500">Avec contrat</p></div>
                    <div className="bg-amber-50 rounded-xl p-3"><p className="text-2xl font-black text-amber-700">{certStatus.stats.total_experiences}</p><p className="text-xs text-slate-500">Total exp.</p></div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Mes preuves */}
          <Card data-testid="proofs-section">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2"><FileText className="w-4 h-4 text-blue-600" />Mes preuves ({totalDocs})</CardTitle>
              <CardDescription className="text-xs">Documents certifiés qui fondent votre identité professionnelle</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              {documents.length === 0 ? (
                <p className="text-xs text-slate-500 text-center py-6">Aucune preuve déposée. Ajoutez vos diplômes, attestations et certificats.</p>
              ) : documents.map(doc => {
                const trustLabels = { auto_declare: { l: "Auto-déclaré", c: "slate" }, verifie: { l: "Vérifié", c: "blue" }, valide: { l: "Validé RE'ACTIF PRO", c: "amber" }, certifie: { l: "Certifié", c: "emerald" } };
                const sourceLabels = { utilisateur: "Utilisateur", organisme: "Organisme", employeur: "Employeur", conseiller: "Conseiller", systeme: "RE'ACTIF PRO" };
                const tl = trustLabels[doc.trust_level] || trustLabels.auto_declare;
                return (
                  <div key={doc.id} className="flex items-center gap-3 p-3 bg-white border border-slate-100 rounded-xl hover:shadow-sm transition-shadow" data-testid={`proof-${doc.id}`}>
                    <div className="w-9 h-9 rounded-lg bg-blue-50 flex items-center justify-center shrink-0"><FileText className="w-4 h-4 text-blue-600" /></div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-slate-900 truncate">{doc.title}</p>
                      <div className="flex items-center gap-1.5 mt-0.5 flex-wrap">
                        <Badge className={`bg-${tl.c}-50 text-${tl.c}-700 border border-${tl.c}-200 text-[9px]`}>
                          {doc.trust_level === "valide" && <CheckCircle2 className="w-2.5 h-2.5 mr-0.5" />}
                          {tl.l}
                        </Badge>
                        <Badge variant="outline" className="text-[9px]">{sourceLabels[doc.source_type] || "Utilisateur"}</Badge>
                        {doc.storage_path && <Badge className="bg-emerald-50 text-emerald-700 text-[9px]">Fichier</Badge>}
                        {doc.issued_by && <Badge className="bg-blue-50 text-blue-700 text-[9px]"><Shield className="w-2.5 h-2.5 mr-0.5" />{doc.issued_by}</Badge>}
                        {doc.competences_liees?.length > 0 && doc.competences_liees.slice(0, 2).map((c, i) => <span key={i} className="text-[9px] text-blue-600 bg-blue-50 px-1 py-0.5 rounded">{c}</span>)}
                      </div>
                      {doc.description && doc.trust_level === "valide" && (
                        <p className="text-[10px] text-emerald-600 mt-1">{doc.description}</p>
                      )}
                    </div>
                    <div className="flex items-center gap-0.5 shrink-0">
                      <Button variant="ghost" size="icon" className="h-7 w-7" data-testid={`view-doc-${doc.id}`} onClick={() => setViewingDoc(doc)}><Eye className="w-3.5 h-3.5 text-blue-600" /></Button>
                      <Button variant="ghost" size="icon" className="h-7 w-7" data-testid={`edit-doc-${doc.id}`} onClick={() => {
                        window.location.href = "/dashboard/profil?tab=experiences";
                      }}><Pencil className="w-3.5 h-3.5 text-amber-600" /></Button>
                      <label className="inline-flex items-center h-7 w-7 justify-center cursor-pointer" data-testid={`validate-doc-${doc.id}`}>
                        <input
                          type="checkbox"
                          checked={doc.trust_level === "valide"}
                          onChange={async (e) => {
                            const newLevel = e.target.checked ? "valide" : "auto_declare";
                            try {
                              await axios.patch(`${API}/coffre/documents/${doc.id}?token=${token}`, { trust_level: newLevel });
                              toast.success(e.target.checked ? "Preuve validée" : "Validation retirée");
                              loadAll();
                            } catch { toast.error("Erreur"); }
                          }}
                          className="w-3.5 h-3.5 rounded border-emerald-300 text-emerald-600 focus:ring-emerald-500 cursor-pointer"
                        />
                      </label>
                      <Button variant="ghost" size="icon" className="h-7 w-7 hover:bg-red-50" onClick={() => handleDelete(doc.id)} data-testid={`delete-doc-${doc.id}`}><Trash2 className="w-3.5 h-3.5 text-red-500" /></Button>
                    </div>
                  </div>
                );
              })}
            </CardContent>
          </Card>

          {/* Dialog visualisation preuve */}
          <Dialog open={!!viewingDoc} onOpenChange={(open) => { if (!open) setViewingDoc(null); }}>
            <DialogContent className="max-w-lg">
              <DialogHeader>
                <DialogTitle className="text-sm">{viewingDoc?.title}</DialogTitle>
                <DialogDescription className="text-xs">{viewingDoc?.description}</DialogDescription>
              </DialogHeader>
              {viewingDoc && (() => {
                const matchedIllus = illustrations.find(il =>
                  il.experience_id === viewingDoc.linked_experience_id &&
                  il.soft_skill === viewingDoc.linked_soft_skill
                );
                if (matchedIllus) {
                  return (
                    <div className="space-y-3 mt-2">
                      <div className="flex items-center gap-2">
                        <Badge className="bg-emerald-100 text-emerald-700 text-xs font-bold">{matchedIllus.soft_skill}</Badge>
                        <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                      </div>
                      <div className="space-y-2">
                        {matchedIllus.sare_situation && (
                          <div className="flex gap-2"><span className="inline-flex items-center justify-center w-6 h-6 rounded bg-amber-100 text-[10px] font-black text-amber-800 shrink-0">S</span><p className="text-sm text-slate-700">{matchedIllus.sare_situation}</p></div>
                        )}
                        {matchedIllus.sare_action && (
                          <div className="flex gap-2"><span className="inline-flex items-center justify-center w-6 h-6 rounded bg-amber-100 text-[10px] font-black text-amber-800 shrink-0">A</span><p className="text-sm text-slate-700">{matchedIllus.sare_action}</p></div>
                        )}
                        {matchedIllus.sare_resultat && (
                          <div className="flex gap-2"><span className="inline-flex items-center justify-center w-6 h-6 rounded bg-amber-100 text-[10px] font-black text-amber-800 shrink-0">R</span><p className="text-sm text-slate-700">{matchedIllus.sare_resultat}</p></div>
                        )}
                        {matchedIllus.sare_enseignement && (
                          <div className="flex gap-2"><span className="inline-flex items-center justify-center w-6 h-6 rounded bg-amber-100 text-[10px] font-black text-amber-800 shrink-0">E</span><p className="text-sm text-slate-700">{matchedIllus.sare_enseignement}</p></div>
                        )}
                      </div>
                      {(matchedIllus.sare_text || matchedIllus.star_text) && (
                        <div className="bg-emerald-50 rounded-lg p-3 border border-emerald-100">
                          <p className="text-[10px] font-semibold text-emerald-700 mb-1 flex items-center gap-1"><Award className="w-3 h-3" />Reformulation IA</p>
                          <p className="text-xs text-emerald-800 leading-relaxed">{matchedIllus.sare_text || matchedIllus.star_text}</p>
                        </div>
                      )}
                    </div>
                  );
                }
                return <p className="text-sm text-slate-500 py-4 text-center">Aucun contenu S.A.R.E disponible pour ce document.</p>;
              })()}
            </DialogContent>
          </Dialog>

          {/* ═══ CERTIFICATION PAR LIEU DE TRAVAIL (Couche 1) ═══ */}
          {certStatus && certStatus.workplaces && certStatus.workplaces.length > 0 && (
            <Card data-testid="certification-workplaces-couche1">
              <CardContent className="p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-semibold text-slate-800 flex items-center gap-2">
                    <Briefcase className="w-4 h-4 text-blue-600" />Certification par lieu de travail
                  </h4>
                  {certStatus.badge && (
                    <Badge className={`text-[10px] font-bold ${
                      certStatus.badge.level === 3 ? "bg-amber-100 text-amber-800 border border-amber-300" :
                      certStatus.badge.level === 2 ? "bg-blue-100 text-blue-800 border border-blue-300" :
                      certStatus.badge.level === 1 ? "bg-emerald-100 text-emerald-800 border border-emerald-300" :
                      "bg-slate-100 text-slate-600 border border-slate-200"
                    }`}>
                      {certStatus.badge.label}
                    </Badge>
                  )}
                </div>
                <div className="space-y-3">
                  {certStatus.workplaces.map((wp, wi) => {
                    const orgProved = wp.experiences.filter(e => e.proofs_count > 0).length;
                    const orgCertified = wp.has_contract;
                    return (
                      <div key={wi} className={`rounded-xl border p-3 space-y-2 ${
                        orgCertified ? "bg-blue-50 border-blue-200" : orgProved > 0 ? "bg-emerald-50 border-emerald-200" : "bg-slate-50 border-slate-200"
                      }`} data-testid={`workplace-c1-${wi}`}>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Briefcase className={`w-4 h-4 ${orgCertified ? "text-blue-600" : orgProved > 0 ? "text-emerald-600" : "text-slate-400"}`} />
                            <h5 className="text-xs font-bold text-slate-800">{wp.organization}</h5>
                          </div>
                          <div className="flex items-center gap-1.5">
                            {orgCertified && <Badge className="bg-blue-100 text-blue-700 text-[9px]"><Shield className="w-2.5 h-2.5 mr-0.5" />Contrat</Badge>}
                            <Badge className={`text-[9px] ${orgProved > 0 ? "bg-emerald-100 text-emerald-700" : "bg-slate-100 text-slate-500"}`}>
                              {orgProved}/{wp.experiences.length} prouvée{orgProved > 1 ? "s" : ""}
                            </Badge>
                          </div>
                        </div>
                        <div className="space-y-1">
                          {wp.experiences.map((exp, ei) => (
                            <div key={ei} className="flex items-center justify-between py-1 px-2 rounded bg-white/60 text-[11px]">
                              <span className="text-slate-700">{exp.title}</span>
                              <div className="flex items-center gap-1">
                                {exp.proofs_count > 0 && (
                                  <span className="flex items-center gap-0.5 text-emerald-600"><CheckCircle2 className="w-3 h-3" />{exp.proofs_count} S.A.R.E</span>
                                )}
                                {exp.has_contract && <Shield className="w-3 h-3 text-blue-500" />}
                              </div>
                            </div>
                          ))}
                        </div>
                        {orgCertified && orgProved > 0 && (
                          <OpcConsentToggle token={token} organization={wp.organization} onUpdate={loadAll} />
                        )}
                        {!orgCertified && (
                          <button
                            onClick={() => window.location.href = "/dashboard/profil?tab=experiences"}
                            className="w-full text-center text-[10px] text-blue-600 hover:text-blue-800 py-1 rounded bg-white/50 hover:bg-white border border-dashed border-blue-200"
                            data-testid={`upload-contract-c1-${wi}`}
                          >
                            <Upload className="w-3 h-3 inline mr-1" />Ajouter un contrat de travail pour certifier
                          </button>
                        )}
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Roadmap EUDI */}
          <Card className="border-dashed border-2 border-blue-200 bg-blue-50/30" data-testid="eudi-roadmap">
            <CardContent className="p-4">
              <h4 className="text-sm font-semibold text-slate-800 mb-1 flex items-center gap-2">
                <Shield className="w-4 h-4 text-blue-600" />Évolution : connexion au wallet européen (EUDI)
              </h4>
              <p className="text-[10px] text-slate-500 mb-3">RE'ACTIF PRO se prépare à devenir compatible avec l'identité numérique européenne</p>
              <div className="space-y-2">
                {[
                  { step: "1", label: "Architecture prête", desc: "Modèle compatible credentials, logique consentement, API ready", status: "done" },
                  { step: "2", label: "Intégration sandbox EUDI", desc: "Connexion pilote via OpenID4VP + Verifiable Credentials (W3C)", status: "next" },
                  { step: "3", label: "Connexion wallet officielle", desc: "Bouton 'Se connecter avec mon identité européenne' + vérification automatique", status: "future" },
                  { step: "4", label: "Interopérabilité Europass", desc: "Import/export de credentials certifiés, compatibilité multi-pays", status: "future" },
                ].map(item => (
                  <div key={item.step} className={`flex items-center gap-3 rounded-lg px-3 py-2 ${item.status === "done" ? "bg-emerald-50 border border-emerald-200" : item.status === "next" ? "bg-amber-50 border border-amber-200" : "bg-slate-50 border border-slate-200"}`}>
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold ${item.status === "done" ? "bg-emerald-200 text-emerald-700" : item.status === "next" ? "bg-amber-200 text-amber-700" : "bg-slate-200 text-slate-500"}`}>{item.status === "done" ? "✓" : item.step}</div>
                    <div className="flex-1">
                      <p className={`text-xs font-medium ${item.status === "future" ? "text-slate-500" : "text-slate-800"}`}>{item.label}</p>
                      <p className="text-[10px] text-slate-400">{item.desc}</p>
                    </div>
                    <Badge className={`text-[9px] ${item.status === "done" ? "bg-emerald-100 text-emerald-700" : item.status === "next" ? "bg-amber-100 text-amber-700" : "bg-slate-100 text-slate-500"}`}>
                      {item.status === "done" ? "Fait" : item.status === "next" ? "Prochaine étape" : "À venir"}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ============ COUCHE 2 : INTELLIGENCE (RE'ACTIF PRO) ============ */}
        <TabsContent value="intelligence" className="space-y-4">
          {/* Profil augmenté */}
          <Card className="border-0 bg-gradient-to-r from-violet-50 to-purple-50" data-testid="augmented-profile">
            <CardContent className="p-5">
              <h4 className="text-sm font-semibold text-slate-800 mb-3 flex items-center gap-2"><Brain className="w-4 h-4 text-violet-600" />Profil augmenté RE'ACTIF PRO</h4>
              <p className="text-xs text-slate-600 mb-3">L'UE vérifie qui vous êtes. RE'ACTIF PRO révèle ce que vous pouvez devenir.</p>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="bg-white rounded-lg p-3 text-center border border-violet-100">
                  <Award className="w-5 h-5 text-violet-600 mx-auto mb-1" />
                  <p className="text-lg font-bold text-slate-900">{passport?.competences?.length || 0}</p>
                  <p className="text-[10px] text-slate-500">Compétences</p>
                </div>
                <div className="bg-white rounded-lg p-3 text-center border border-violet-100">
                  <Sparkles className="w-5 h-5 text-emerald-600 mx-auto mb-1" />
                  <p className="text-lg font-bold text-slate-900">{totalSkillsProved}</p>
                  <p className="text-[10px] text-slate-500">Soft skills prouvés</p>
                </div>
                <div className="bg-white rounded-lg p-3 text-center border border-violet-100">
                  <Briefcase className="w-5 h-5 text-blue-600 mx-auto mb-1" />
                  <p className="text-lg font-bold text-slate-900">{passport?.experiences?.length || 0}</p>
                  <p className="text-[10px] text-slate-500">Expériences</p>
                </div>
                <div className="bg-white rounded-lg p-3 text-center border border-violet-100">
                  <GraduationCap className="w-5 h-5 text-amber-600 mx-auto mb-1" />
                  <p className="text-lg font-bold text-slate-900">{passport?.formations?.length || 0}</p>
                  <p className="text-[10px] text-slate-500">Formations</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* ═══ OPC INTRODUCTION + TABLEAU RÉCAPITULATIF ═══ */}
          {certStatus && certStatus.workplaces && certStatus.workplaces.length > 0 && (() => {
            // Build per-experience summary
            const allExps = certStatus.workplaces.flatMap(wp =>
              wp.experiences.map(exp => ({
                ...exp,
                organization: wp.organization,
                orgHasContract: wp.has_contract,
              }))
            );
            const pending_proof = allExps.filter(e => e.proofs_count === 0);
            const proved_no_contract = allExps.filter(e => e.proofs_count > 0 && !e.has_contract);
            const fully_certified = allExps.filter(e => e.proofs_count > 0 && e.has_contract);

            return (
              <Card data-testid="opc-recap-table" className="overflow-hidden">
                <CardContent className="p-0">
                  {/* ── Introduction OPC ── */}
                  <div className="bg-gradient-to-br from-[#0f2744] via-[#1a3558] to-[#0f2744] p-5 space-y-3">
                    <div className="flex items-center gap-2">
                      <Globe className="w-5 h-5 text-cyan-400" />
                      <h3 className="text-lg font-bold text-white tracking-wide uppercase" data-testid="opc-intro-title">
                        Observatoire Prédictif des Compétences (OPC)
                      </h3>
                    </div>
                    <p className="text-sm leading-relaxed text-slate-300">
                      L'<span className="text-cyan-300 font-semibold">OPC</span> est un dispositif collectif qui cartographie les compétences réelles du marché de l'emploi, à partir de <span className="text-white font-semibold">preuves concrètes fournies par les acteurs de la vie socio-professionnelle (VOUS)</span>. Contrairement aux référentiels théoriques (ROME, RNCP), l'OPC s'appuie sur des données terrain : tes expériences, tes preuves S.A.R.E et tes contrats de travail.
                    </p>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
                      <div className="bg-white/8 rounded-lg p-3 border border-white/10">
                        <p className="text-xs font-bold text-emerald-300 mb-1 flex items-center gap-1"><Target className="w-3.5 h-3.5" />Fiabilité</p>
                        <p className="text-xs text-slate-300 leading-relaxed">Seules les compétences prouvées et certifiées alimentent l'Observatoire. Pas de déclaratif.</p>
                      </div>
                      <div className="bg-white/8 rounded-lg p-3 border border-white/10">
                        <p className="text-xs font-bold text-blue-300 mb-1 flex items-center gap-1"><TrendingUp className="w-3.5 h-3.5" />Prédictif</p>
                        <p className="text-xs text-slate-300 leading-relaxed">L'OPC permet d'anticiper les compétences émergentes et les besoins réels des employeurs par secteur.</p>
                      </div>
                      <div className="bg-white/8 rounded-lg p-3 border border-white/10">
                        <p className="text-xs font-bold text-amber-300 mb-1 flex items-center gap-1"><Users className="w-3.5 h-3.5" />Collectif</p>
                        <p className="text-xs text-slate-300 leading-relaxed">Chaque contributeur renforce la connaissance collective du marché. Ton parcours a de la valeur pour tous.</p>
                      </div>
                    </div>
                  </div>

                  {/* ── Tableau récapitulatif ── */}
                  <div className="p-5 space-y-4">
                    <div className="flex items-center justify-between">
                      <h4 className="text-sm font-bold text-slate-800 flex items-center gap-2" data-testid="recap-table-title">
                        <Search className="w-4 h-4 text-violet-600" />Récapitulatif de tes compétences
                      </h4>
                      <Badge className="bg-violet-100 text-violet-700 text-[10px]">{allExps.length} expérience{allExps.length > 1 ? "s" : ""}</Badge>
                    </div>

                    {/* Tableau */}
                    <div className="overflow-x-auto rounded-xl border border-slate-200" data-testid="skills-recap-table">
                      <table className="w-full text-xs">
                        <thead>
                          <tr className="bg-slate-100">
                            <th className="text-left px-3 py-2.5 font-semibold text-slate-700 border-b border-slate-200">Expérience</th>
                            <th className="text-left px-3 py-2.5 font-semibold text-slate-700 border-b border-slate-200">Lieu</th>
                            <th className="text-center px-3 py-2.5 font-semibold text-slate-700 border-b border-slate-200">
                              <span className="inline-flex items-center gap-1"><MessageSquare className="w-3 h-3 text-emerald-600" />S.A.R.E</span>
                            </th>
                            <th className="text-center px-3 py-2.5 font-semibold text-slate-700 border-b border-slate-200">
                              <span className="inline-flex items-center gap-1"><Shield className="w-3 h-3 text-blue-600" />Contrat</span>
                            </th>
                            <th className="text-center px-3 py-2.5 font-semibold text-slate-700 border-b border-slate-200">
                              <span className="inline-flex items-center gap-1"><Award className="w-3 h-3 text-amber-600" />Statut</span>
                            </th>
                          </tr>
                        </thead>
                        <tbody>
                          {allExps.map((exp, idx) => {
                            const hasProof = exp.proofs_count > 0;
                            const hasContract = exp.has_contract;
                            let statusLabel, statusClass;
                            if (hasProof && hasContract) {
                              statusLabel = "Expert";
                              statusClass = "bg-amber-100 text-amber-800 border-amber-300";
                            } else if (hasProof && !hasContract) {
                              statusLabel = "Contributeur";
                              statusClass = "bg-emerald-100 text-emerald-800 border-emerald-300";
                            } else {
                              statusLabel = "En attente";
                              statusClass = "bg-slate-100 text-slate-600 border-slate-200";
                            }
                            return (
                              <tr key={exp.id || idx} className={`border-b border-slate-100 ${idx % 2 === 0 ? "bg-white" : "bg-slate-50/50"}`} data-testid={`recap-row-${idx}`}>
                                <td className="px-3 py-2.5 font-medium text-slate-800">{exp.title || "Sans titre"}</td>
                                <td className="px-3 py-2.5 text-slate-600">{exp.organization}</td>
                                <td className="px-3 py-2.5 text-center">
                                  {hasProof ? (
                                    <span className="inline-flex items-center gap-0.5 text-emerald-600 font-semibold"><CheckCircle2 className="w-3.5 h-3.5" />{exp.proofs_count}</span>
                                  ) : (
                                    <span className="inline-flex items-center gap-0.5 text-slate-400"><Clock className="w-3.5 h-3.5" />0</span>
                                  )}
                                </td>
                                <td className="px-3 py-2.5 text-center">
                                  {hasContract ? (
                                    <CheckCircle2 className="w-3.5 h-3.5 text-blue-600 mx-auto" />
                                  ) : (
                                    <Clock className="w-3.5 h-3.5 text-slate-400 mx-auto" />
                                  )}
                                </td>
                                <td className="px-3 py-2.5 text-center">
                                  <span className={`inline-block px-2 py-0.5 rounded-full text-[10px] font-bold border ${statusClass}`}>{statusLabel}</span>
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>

                    {/* Légende 3 niveaux */}
                    <div className="grid grid-cols-3 gap-3">
                      <div className={`rounded-xl p-3 text-center border-2 ${pending_proof.length > 0 ? "bg-slate-50 border-slate-300" : "bg-emerald-50 border-emerald-200"}`}>
                        <Clock className={`w-5 h-5 mx-auto mb-1 ${pending_proof.length > 0 ? "text-slate-500" : "text-emerald-500"}`} />
                        <p className="text-lg font-black text-slate-800">{pending_proof.length}</p>
                        <p className="text-[10px] text-slate-500 font-medium">En attente de preuve S.A.R.E</p>
                        <p className="text-[9px] text-slate-400 mt-0.5">Niveau Contributeur non atteint</p>
                      </div>
                      <div className={`rounded-xl p-3 text-center border-2 ${proved_no_contract.length > 0 ? "bg-emerald-50 border-emerald-300" : "bg-blue-50 border-blue-200"}`}>
                        <ArrowRight className={`w-5 h-5 mx-auto mb-1 ${proved_no_contract.length > 0 ? "text-emerald-600" : "text-blue-500"}`} />
                        <p className="text-lg font-black text-slate-800">{proved_no_contract.length}</p>
                        <p className="text-[10px] text-slate-500 font-medium">Prouvées, en attente de contrat</p>
                        <p className="text-[9px] text-slate-400 mt-0.5">Niveau Certifié non atteint</p>
                      </div>
                      <div className={`rounded-xl p-3 text-center border-2 ${fully_certified.length > 0 ? "bg-amber-50 border-amber-300" : "bg-slate-50 border-slate-200"}`}>
                        <Award className={`w-5 h-5 mx-auto mb-1 ${fully_certified.length > 0 ? "text-amber-600" : "text-slate-400"}`} />
                        <p className="text-lg font-black text-slate-800">{fully_certified.length}</p>
                        <p className="text-[10px] text-slate-500 font-medium">Entièrement certifiées</p>
                        <p className="text-[9px] text-slate-400 mt-0.5">Prêtes pour l'OPC</p>
                      </div>
                    </div>

                    {/* Call to action si des actions restent */}
                    {(pending_proof.length > 0 || proved_no_contract.length > 0) && (
                      <div className="flex items-start gap-3 bg-blue-50 border border-blue-200 rounded-xl p-3" data-testid="opc-cta">
                        <Sparkles className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
                        <div className="space-y-1">
                          <p className="text-xs font-semibold text-blue-800">Actions recommandées pour contribuer à l'OPC</p>
                          {pending_proof.length > 0 && (
                            <p className="text-[11px] text-blue-700">
                              <span className="font-semibold">{pending_proof.length} expérience{pending_proof.length > 1 ? "s" : ""}</span> {pending_proof.length > 1 ? "n'ont" : "n'a"} pas encore de preuve S.A.R.E — rends-toi dans <button onClick={() => window.location.href = "/dashboard/profil?tab=experiences"} className="underline font-bold hover:text-blue-900">Mon Passeport</button> pour les illustrer.
                            </p>
                          )}
                          {proved_no_contract.length > 0 && (
                            <p className="text-[11px] text-blue-700">
                              <span className="font-semibold">{proved_no_contract.length} expérience{proved_no_contract.length > 1 ? "s" : ""}</span> {proved_no_contract.length > 1 ? "sont prouvées mais n'ont" : "est prouvée mais n'a"} pas de contrat — uploade un contrat de travail pour atteindre le niveau <span className="font-bold">Certifié</span>.
                            </p>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            );
          })()}
        </TabsContent>

        {/* ============ COUCHE 3 : ACTIONS ============ */}
        <TabsContent value="actions" className="space-y-4">
          {/* Partager en 1 clic */}
          <Card className="border-0 bg-gradient-to-r from-amber-50 to-orange-50" data-testid="share-section">
            <CardContent className="p-5">
              <h4 className="text-sm font-semibold text-slate-800 mb-1 flex items-center gap-2"><Share2 className="w-4 h-4 text-amber-600" />Partager mon profil en 1 clic</h4>
              <p className="text-xs text-slate-500 mb-3">Choisissez quoi partager, avec qui et pour combien de temps</p>

              {generatedShareUrl && (
                <div className="bg-white border border-amber-200 rounded-xl p-4 mb-3 flex items-center gap-4" data-testid="share-qr">
                  <QRCodeSVG value={generatedShareUrl} size={80} />
                  <div className="flex-1">
                    <p className="text-xs font-semibold text-slate-800">Lien de partage créé</p>
                    <p className="text-[10px] text-slate-500 break-all mt-1">{generatedShareUrl}</p>
                    <Button variant="outline" size="sm" className="h-6 text-[10px] mt-2" onClick={() => { navigator.clipboard.writeText(generatedShareUrl); toast.success("Lien copié"); }}>Copier le lien</Button>
                  </div>
                </div>
              )}

              {!showShareForm ? (
                <Button className="bg-amber-600 hover:bg-amber-700 text-white" onClick={() => { setShowShareForm(true); setGeneratedShareUrl(null); }} data-testid="new-share-btn">
                  <QrCode className="w-4 h-4 mr-1" />Créer un partage sélectif
                </Button>
              ) : (
                <div className="bg-white border border-amber-200 rounded-xl p-4 space-y-2" data-testid="share-form">
                  <Input placeholder="Nom du destinataire *" value={shareForm.recipient_name} onChange={e => setShareForm({ ...shareForm, recipient_name: e.target.value })} className="h-8 text-xs" />
                  <div className="grid grid-cols-2 gap-2">
                    <Select value={shareForm.recipient_type} onValueChange={v => setShareForm({ ...shareForm, recipient_type: v })}>
                      <SelectTrigger className="h-8 text-xs"><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="employeur">Employeur</SelectItem>
                        <SelectItem value="conseiller">Conseiller</SelectItem>
                        <SelectItem value="formation">Formation</SelectItem>
                        <SelectItem value="autre">Autre</SelectItem>
                      </SelectContent>
                    </Select>
                    <Select value={String(shareForm.duration_days)} onValueChange={v => setShareForm({ ...shareForm, duration_days: parseInt(v) })}>
                      <SelectTrigger className="h-8 text-xs"><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="7">7 jours</SelectItem>
                        <SelectItem value="30">30 jours</SelectItem>
                        <SelectItem value="90">90 jours</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <p className="text-[10px] font-medium text-slate-600 mb-1">Sections à partager :</p>
                    <div className="flex flex-wrap gap-1.5">
                      {Object.entries(sectionLabels).map(([k, v]) => (
                        <button key={k} onClick={() => setShareForm({ ...shareForm, sections: shareForm.sections.includes(k) ? shareForm.sections.filter(x => x !== k) : [...shareForm.sections, k] })}
                          className={`text-[10px] px-2 py-1 rounded-full border transition-colors ${shareForm.sections.includes(k) ? "bg-amber-100 text-amber-700 border-amber-300" : "bg-white text-slate-500 border-slate-200"}`}>{v}</button>
                      ))}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" className="h-7 text-xs flex-1 bg-amber-600 hover:bg-amber-700" onClick={handleCreateShare} disabled={creatingShare}>
                      {creatingShare ? <Loader2 className="w-3 h-3 animate-spin mr-1" /> : <QrCode className="w-3 h-3 mr-1" />}Générer le lien + QR Code
                    </Button>
                    <Button variant="outline" size="sm" className="h-7 text-xs" onClick={() => setShowShareForm(false)}>Annuler</Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Partages actifs */}
          <Card data-testid="active-shares">
            <CardContent className="p-4">
              <h4 className="text-sm font-semibold text-slate-800 mb-2 flex items-center gap-2"><Eye className="w-4 h-4 text-blue-600" />Partages actifs ({activeShares})</h4>
              {activeShares === 0 ? (
                <p className="text-xs text-slate-500 text-center py-3">Aucun partage actif. Vous contrôlez qui voit vos données.</p>
              ) : shares.filter(s => s.active).map(s => (
                <div key={s.id} className="flex items-center justify-between bg-slate-50 rounded-lg px-3 py-2 mb-1.5" data-testid={`active-share-${s.id}`}>
                  <div>
                    <p className="text-xs font-medium text-slate-800">{s.recipient_name} <span className="text-slate-400">({s.recipient_type})</span></p>
                    <p className="text-[10px] text-slate-500">{(s.sections || []).map(sec => sectionLabels[sec] || sec).join(", ")} — {s.views || 0} vue{(s.views || 0) > 1 ? "s" : ""}</p>
                  </div>
                  <Button variant="ghost" size="sm" className="h-6 text-[10px] text-rose-500" onClick={() => handleRevoke(s.id)}>Révoquer</Button>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Actions rapides */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2" data-testid="quick-actions">
            {[
              { label: "Générer mon CV", icon: FileText, path: "/dashboard/trajectoire", color: "blue" },
              { label: "Prouver mes soft skills", icon: Award, path: "/dashboard/profil", color: "emerald" },
              { label: "Voir mes opportunités", icon: Briefcase, path: "/dashboard/opportunites", color: "violet" },
              { label: "Rejoindre Ubuntoo", icon: Users, action: () => window.open("/ubuntoo", "_blank"), color: "amber" },
            ].map((a, i) => {
              const AIcon = a.icon;
              return (
                <button key={i} onClick={() => a.action ? a.action() : (window.location.href = a.path)}
                  className={`flex flex-col items-center gap-1.5 p-3 rounded-xl border border-transparent bg-${a.color}-50 hover:bg-${a.color}-100 text-${a.color}-700 transition-all`} data-testid={`action-${i}`}>
                  <AIcon className="w-5 h-5" /><span className="text-[10px] font-medium text-center">{a.label}</span>
                </button>
              );
            })}
          </div>

          {/* À renouveler */}
          {expiringDocs > 0 && (
            <Card className="border-amber-200" data-testid="expiring-docs">
              <CardContent className="p-4">
                <h4 className="text-sm font-semibold text-slate-800 mb-2 flex items-center gap-2"><Clock className="w-4 h-4 text-amber-600" />Preuves à renouveler ({expiringDocs})</h4>
                {documents.filter(d => d.date_expiration && ((new Date(d.date_expiration) - new Date()) / 86400000) < 90).map(d => {
                  const days = Math.ceil((new Date(d.date_expiration) - new Date()) / 86400000);
                  return (
                    <div key={d.id} className={`flex items-center justify-between rounded-lg px-3 py-2 mb-1 ${days < 0 ? "bg-rose-50 border border-rose-200" : "bg-amber-50 border border-amber-200"}`}>
                      <span className="text-xs text-slate-700">{d.title}</span>
                      <Badge className={days < 0 ? "bg-rose-100 text-rose-700" : "bg-amber-100 text-amber-700"}>{days < 0 ? `Expiré ${Math.abs(days)}j` : `${days}j restants`}</Badge>
                    </div>
                  );
                })}
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default CoffreFortView;
