import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { 
  FolderLock,
  FileText,
  Upload,
  Search,
  Filter,
  Plus,
  Eye,
  Share2,
  Trash2,
  Clock,
  Shield,
  AlertTriangle,
  CheckCircle2,
  Award,
  Briefcase,
  GraduationCap,
  Users,
  Target,
  BookOpen,
  FileCheck,
  X,
  Link,
  Calendar,
  Lock,
  Unlock,
  ChevronRight,
  Download,
  Loader2,
  File as FileIcon
} from "lucide-react";
import { toast } from "sonner";

const CATEGORY_CONFIG = {
  identite_professionnelle: { 
    label: "Identité professionnelle", 
    icon: Users, 
    color: "blue",
    description: "CV, lettres de motivation, présentations"
  },
  diplomes_certifications: { 
    label: "Diplômes et certifications", 
    icon: GraduationCap, 
    color: "emerald",
    description: "Diplômes, titres, habilitations"
  },
  experiences_professionnelles: { 
    label: "Expériences professionnelles", 
    icon: Briefcase, 
    color: "violet",
    description: "Contrats, attestations, recommandations"
  },
  competences_preuves: { 
    label: "Compétences et preuves", 
    icon: Award, 
    color: "amber",
    description: "Réalisations, projets, badges"
  },
  accompagnement_insertion: { 
    label: "Accompagnement", 
    icon: Target, 
    color: "rose",
    description: "Bilans, diagnostics, plans d'action"
  },
  recherche_emploi: { 
    label: "Recherche d'emploi", 
    icon: Search, 
    color: "cyan",
    description: "Candidatures, entretiens, offres"
  },
  formation_apprentissages: { 
    label: "Formation", 
    icon: BookOpen, 
    color: "indigo",
    description: "Attestations, certificats, badges"
  },
  documents_administratifs: { 
    label: "Documents administratifs", 
    icon: FileCheck, 
    color: "slate",
    description: "Permis, justificatifs, conventions"
  }
};

const PRIVACY_LEVELS = {
  private: { label: "Privé", icon: Lock, color: "slate", description: "Visible uniquement par vous" },
  shared_conseiller: { label: "Partagé conseiller", icon: Users, color: "blue", description: "Visible par votre conseiller" },
  shared_recruteur: { label: "Partagé recruteur", icon: Briefcase, color: "emerald", description: "Visible temporairement par un recruteur" },
  public: { label: "Public", icon: Unlock, color: "amber", description: "Intégré à votre profil public" }
};

const CoffreFortView = ({ token }) => {
  const [documents, setDocuments] = useState([]);
  const [categories, setCategories] = useState({});
  const [stats, setStats] = useState(null);
  const [shares, setShares] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("documents");
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [shareDialogOpen, setShareDialogOpen] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState(null);

  const [newDocument, setNewDocument] = useState({
    title: "",
    category: "identite_professionnelle",
    document_type: "",
    file_name: "",
    date_document: "",
    metier_associe: "",
    secteur: "",
    competences_liees: "",
    description: "",
    privacy_level: "private",
    date_expiration: "",
    is_sensitive: false
  });
  const [uploadFile, setUploadFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [downloading, setDownloading] = useState(null);

  useEffect(() => {
    loadData();
  }, [token]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [docsRes, catsRes, statsRes, sharesRes] = await Promise.all([
        axios.get(`${API}/coffre/documents?token=${token}`),
        axios.get(`${API}/coffre/categories`),
        axios.get(`${API}/coffre/stats?token=${token}`),
        axios.get(`${API}/coffre/shares?token=${token}`)
      ]);
      setDocuments(docsRes.data);
      setCategories(catsRes.data);
      setStats(statsRes.data);
      setShares(sharesRes.data);
    } catch (error) {
      console.error("Error loading coffre-fort:", error);
    }
    setLoading(false);
  };

  const createDocument = async () => {
    if (!newDocument.title && !uploadFile) {
      toast.error("Veuillez remplir le titre ou joindre un fichier");
      return;
    }

    setUploading(true);
    try {
      if (uploadFile) {
        const formData = new FormData();
        formData.append("file", uploadFile);
        const params = new URLSearchParams({
          token,
          title: newDocument.title || uploadFile.name,
          category: newDocument.category,
          document_type: newDocument.document_type || "autre",
          description: newDocument.description || "",
          competences_liees: newDocument.competences_liees || ""
        });
        await axios.post(`${API}/coffre/upload?${params.toString()}`, formData, {
          headers: { "Content-Type": "multipart/form-data" }
        });
      } else {
        const docData = {
          ...newDocument,
          competences_liees: newDocument.competences_liees.split(",").map(c => c.trim()).filter(Boolean)
        };
        await axios.post(`${API}/coffre/documents?token=${token}`, docData);
      }
      toast.success("Document ajouté au coffre-fort !");
      setCreateDialogOpen(false);
      setUploadFile(null);
      setNewDocument({
        title: "", category: "identite_professionnelle", document_type: "", file_name: "",
        date_document: "", metier_associe: "", secteur: "", competences_liees: "",
        description: "", privacy_level: "private", date_expiration: "", is_sensitive: false
      });
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Erreur lors de l'ajout du document");
    }
    setUploading(false);
  };

  const downloadDocument = async (doc) => {
    if (!doc.storage_path) {
      toast.error("Aucun fichier associé à ce document");
      return;
    }
    setDownloading(doc.id);
    try {
      const response = await axios.get(`${API}/coffre/download/${doc.id}?token=${token}`, {
        responseType: "blob"
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", doc.file_name || doc.title || "document");
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      toast.success("Téléchargement lancé !");
    } catch (error) {
      toast.error("Erreur lors du téléchargement");
    }
    setDownloading(null);
  };

  const deleteDocument = async (docId) => {
    if (!confirm("Êtes-vous sûr de vouloir supprimer ce document ?")) return;
    
    try {
      await axios.delete(`${API}/coffre/documents/${docId}?token=${token}`);
      toast.success("Document supprimé");
      loadData();
    } catch (error) {
      toast.error("Erreur lors de la suppression");
    }
  };

  const shareDocument = async (docId) => {
    try {
      const response = await axios.post(`${API}/coffre/documents/${docId}/share?token=${token}&expires_in_days=7`);
      toast.success("Lien de partage créé !");
      setShareDialogOpen(false);
      loadData();
    } catch (error) {
      toast.error("Erreur lors du partage");
    }
  };

  const revokeShare = async (shareId) => {
    try {
      await axios.delete(`${API}/coffre/shares/${shareId}?token=${token}`);
      toast.success("Partage révoqué");
      loadData();
    } catch (error) {
      toast.error("Erreur lors de la révocation");
    }
  };

  const filteredDocuments = documents.filter(doc => {
    if (selectedCategory && doc.category !== selectedCategory) return false;
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return doc.title.toLowerCase().includes(query) ||
             doc.description?.toLowerCase().includes(query) ||
             doc.competences_liees?.some(c => c.toLowerCase().includes(query));
    }
    return true;
  });

  const expiringDocs = documents.filter(d => d.is_expiring_soon);
  const sensitiveDocs = documents.filter(d => d.is_sensitive);
  const sharedDocs = documents.filter(d => d.privacy_level !== "private");

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#1e3a5f]"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in" data-testid="coffre-fort-view">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 flex items-center gap-3" style={{ fontFamily: 'Outfit, sans-serif' }}>
            <FolderLock className="w-8 h-8 text-[#1e3a5f]" />
            Mon Coffre-Fort Professionnel
          </h1>
          <p className="text-slate-600 mt-1">
            Conservez, structurez et valorisez vos documents professionnels en toute sécurité
          </p>
        </div>
        <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button className="bg-[#1e3a5f] hover:bg-[#152a45]" data-testid="add-document-btn">
              <Plus className="w-4 h-4 mr-2" />
              Ajouter un document
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Ajouter un document au coffre-fort</DialogTitle>
              <DialogDescription>
                Indexez votre document pour faciliter sa recherche et sa valorisation
              </DialogDescription>
            </DialogHeader>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
              {/* File Upload Area */}
              <div className="md:col-span-2">
                <label className="text-sm font-medium text-slate-700 mb-2 block">Joindre un fichier</label>
                <div
                  className={`border-2 border-dashed rounded-lg p-4 text-center cursor-pointer transition-colors ${
                    uploadFile ? "border-emerald-400 bg-emerald-50" : "border-slate-300 hover:border-[#1e3a5f] hover:bg-slate-50"
                  }`}
                  onClick={() => document.getElementById("coffre-file-input").click()}
                  data-testid="file-upload-area"
                >
                  <input
                    id="coffre-file-input"
                    type="file"
                    className="hidden"
                    accept=".pdf,.docx,.doc,.txt,.jpg,.jpeg,.png,.xlsx,.csv"
                    onChange={(e) => {
                      const f = e.target.files[0];
                      if (f) {
                        if (f.size > 10 * 1024 * 1024) {
                          toast.error("Fichier trop volumineux (max 10 Mo)");
                          return;
                        }
                        setUploadFile(f);
                        if (!newDocument.title) {
                          setNewDocument(prev => ({ ...prev, title: f.name.replace(/\.[^.]+$/, "") }));
                        }
                      }
                    }}
                  />
                  {uploadFile ? (
                    <div className="flex items-center justify-center gap-2">
                      <FileIcon className="w-5 h-5 text-emerald-600" />
                      <span className="text-sm font-medium text-emerald-700">{uploadFile.name}</span>
                      <span className="text-xs text-slate-500">({(uploadFile.size / 1024).toFixed(0)} Ko)</span>
                      <Button
                        variant="ghost" size="icon" className="h-6 w-6"
                        onClick={(e) => { e.stopPropagation(); setUploadFile(null); }}
                      >
                        <X className="w-3 h-3 text-red-500" />
                      </Button>
                    </div>
                  ) : (
                    <div>
                      <Upload className="w-8 h-8 mx-auto text-slate-400 mb-2" />
                      <p className="text-sm text-slate-600">Cliquez pour sélectionner un fichier</p>
                      <p className="text-xs text-slate-400 mt-1">PDF, DOCX, TXT, Images — Max 10 Mo</p>
                    </div>
                  )}
                </div>
              </div>
              <div className="md:col-span-2 space-y-2">
                <label className="text-sm font-medium text-slate-700">Titre du document *</label>
                <Input
                  placeholder="Ex: CV Marketing Digital 2024"
                  value={newDocument.title}
                  onChange={(e) => setNewDocument({ ...newDocument, title: e.target.value })}
                  data-testid="doc-title-input"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Catégorie *</label>
                <Select 
                  value={newDocument.category} 
                  onValueChange={(v) => setNewDocument({ ...newDocument, category: v, document_type: "" })}
                >
                  <SelectTrigger data-testid="doc-category-select">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(CATEGORY_CONFIG).map(([key, config]) => (
                      <SelectItem key={key} value={key}>
                        <span className="flex items-center gap-2">
                          <config.icon className="w-4 h-4" />
                          {config.label}
                        </span>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Type de document *</label>
                <Select 
                  value={newDocument.document_type} 
                  onValueChange={(v) => setNewDocument({ ...newDocument, document_type: v })}
                >
                  <SelectTrigger data-testid="doc-type-select">
                    <SelectValue placeholder="Sélectionner..." />
                  </SelectTrigger>
                  <SelectContent>
                    {categories[newDocument.category]?.types.map((type) => (
                      <SelectItem key={type} value={type}>{type}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Date du document</label>
                <Input
                  type="date"
                  value={newDocument.date_document}
                  onChange={(e) => setNewDocument({ ...newDocument, date_document: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Date d'expiration</label>
                <Input
                  type="date"
                  value={newDocument.date_expiration}
                  onChange={(e) => setNewDocument({ ...newDocument, date_expiration: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Métier associé</label>
                <Input
                  placeholder="Ex: Assistant administratif"
                  value={newDocument.metier_associe}
                  onChange={(e) => setNewDocument({ ...newDocument, metier_associe: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Secteur</label>
                <Input
                  placeholder="Ex: Administration, Commerce..."
                  value={newDocument.secteur}
                  onChange={(e) => setNewDocument({ ...newDocument, secteur: e.target.value })}
                />
              </div>
              <div className="md:col-span-2 space-y-2">
                <label className="text-sm font-medium text-slate-700">Compétences liées</label>
                <Input
                  placeholder="Séparez par des virgules: Excel, Communication, Gestion de projet"
                  value={newDocument.competences_liees}
                  onChange={(e) => setNewDocument({ ...newDocument, competences_liees: e.target.value })}
                />
                <p className="text-xs text-slate-500">Ces compétences seront ajoutées à votre profil comme compétences prouvées</p>
              </div>
              <div className="md:col-span-2 space-y-2">
                <label className="text-sm font-medium text-slate-700">Description</label>
                <Textarea
                  placeholder="Décrivez brièvement le contenu du document..."
                  rows={3}
                  value={newDocument.description}
                  onChange={(e) => setNewDocument({ ...newDocument, description: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Niveau de confidentialité</label>
                <Select 
                  value={newDocument.privacy_level} 
                  onValueChange={(v) => setNewDocument({ ...newDocument, privacy_level: v })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(PRIVACY_LEVELS).map(([key, config]) => (
                      <SelectItem key={key} value={key}>
                        <span className="flex items-center gap-2">
                          <config.icon className="w-4 h-4" />
                          {config.label}
                        </span>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2 flex items-end">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={newDocument.is_sensitive}
                    onChange={(e) => setNewDocument({ ...newDocument, is_sensitive: e.target.checked })}
                    className="rounded border-slate-300"
                  />
                  <span className="text-sm text-slate-700">Document sensible (accès renforcé)</span>
                </label>
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <Button variant="outline" onClick={() => setCreateDialogOpen(false)}>
                Annuler
              </Button>
              <Button onClick={createDocument} className="bg-[#1e3a5f] hover:bg-[#152a45]" disabled={uploading} data-testid="submit-document-btn">
                {uploading ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Upload en cours...</> : "Ajouter au coffre-fort"}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4" data-testid="coffre-stats">
        <Card className="card-metric">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-[#1e3a5f] text-white flex items-center justify-center">
                <FileText className="w-5 h-5" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{stats?.total_documents || 0}</p>
                <p className="text-xs text-slate-500">Documents</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="card-metric">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-600 text-white flex items-center justify-center">
                <Award className="w-5 h-5" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{stats?.competences_prouvees?.length || 0}</p>
                <p className="text-xs text-slate-500">Compétences prouvées</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="card-metric">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-blue-600 text-white flex items-center justify-center">
                <Share2 className="w-5 h-5" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{stats?.documents_partages || 0}</p>
                <p className="text-xs text-slate-500">Documents partagés</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="card-metric">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-amber-600 text-white flex items-center justify-center">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{stats?.documents_expirants || 0}</p>
                <p className="text-xs text-slate-500">À renouveler</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid grid-cols-3 gap-1 h-auto p-1 bg-slate-100">
          <TabsTrigger value="documents" className="text-xs sm:text-sm py-2" data-testid="tab-documents">
            <FileText className="w-4 h-4 mr-1 hidden sm:inline" />
            Documents
          </TabsTrigger>
          <TabsTrigger value="candidatures" className="text-xs sm:text-sm py-2" data-testid="tab-candidatures">
            <Search className="w-4 h-4 mr-1 hidden sm:inline" />
            Candidatures
          </TabsTrigger>
          <TabsTrigger value="partages" className="text-xs sm:text-sm py-2" data-testid="tab-partages">
            <Share2 className="w-4 h-4 mr-1 hidden sm:inline" />
            Partages
          </TabsTrigger>
        </TabsList>

        {/* Documents Tab */}
        <TabsContent value="documents" className="space-y-4">
          {/* Filters */}
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <Input
                placeholder="Rechercher par titre, compétence, métier..."
                className="pl-10"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                data-testid="search-documents"
              />
            </div>
            <Select value={selectedCategory || "all"} onValueChange={(v) => setSelectedCategory(v === "all" ? null : v)}>
              <SelectTrigger className="w-full sm:w-60" data-testid="filter-category">
                <Filter className="w-4 h-4 mr-2" />
                <SelectValue placeholder="Toutes catégories" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Toutes catégories</SelectItem>
                {Object.entries(CATEGORY_CONFIG).map(([key, config]) => (
                  <SelectItem key={key} value={key}>
                    <span className="flex items-center gap-2">
                      <config.icon className="w-4 h-4" />
                      {config.label}
                    </span>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Category Quick Filters */}
          <div className="flex flex-wrap gap-2">
            {Object.entries(CATEGORY_CONFIG).map(([key, config]) => {
              const count = stats?.by_category?.[key] || 0;
              const Icon = config.icon;
              return (
                <Badge
                  key={key}
                  variant={selectedCategory === key ? "default" : "outline"}
                  className={`cursor-pointer transition-all ${selectedCategory === key ? 'bg-[#1e3a5f]' : 'hover:bg-slate-100'}`}
                  onClick={() => setSelectedCategory(selectedCategory === key ? null : key)}
                >
                  <Icon className="w-3 h-3 mr-1" />
                  {config.label} ({count})
                </Badge>
              );
            })}
          </div>

          {/* Documents Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredDocuments.length > 0 ? (
              filteredDocuments.map((doc) => (
                <DocumentCard 
                  key={doc.id} 
                  document={doc} 
                  onDelete={deleteDocument}
                  onShare={() => { setSelectedDocument(doc); setShareDialogOpen(true); }}
                  onDownload={() => downloadDocument(doc)}
                  downloading={downloading === doc.id}
                />
              ))
            ) : (
              <div className="col-span-full text-center py-12">
                <FolderLock className="w-16 h-16 mx-auto text-slate-300 mb-4" />
                <h3 className="text-lg font-semibold text-slate-600 mb-2">Aucun document</h3>
                <p className="text-slate-500 mb-4">Commencez par ajouter vos premiers documents professionnels</p>
                <Button onClick={() => setCreateDialogOpen(true)} className="bg-[#1e3a5f]">
                  <Plus className="w-4 h-4 mr-2" />
                  Ajouter un document
                </Button>
              </div>
            )}
          </div>
        </TabsContent>

        {/* Competences Tab */}
        <TabsContent value="competences" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Award className="w-5 h-5 text-[#1e3a5f]" />
                Compétences prouvées par vos documents
              </CardTitle>
              <CardDescription>
                Chaque document lié à une compétence renforce votre profil professionnel
              </CardDescription>
            </CardHeader>
            <CardContent>
              {stats?.competences_prouvees?.length > 0 ? (
                <div className="space-y-4">
                  {stats.competences_prouvees.map((comp, idx) => {
                    const relatedDocs = documents.filter(d => d.competences_liees?.includes(comp));
                    return (
                      <div key={idx} className="p-4 rounded-lg border border-slate-200 hover:border-[#1e3a5f] transition-colors">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-semibold text-slate-900">{comp}</h4>
                          <Badge className="bg-emerald-100 text-emerald-700">
                            {relatedDocs.length} preuve(s)
                          </Badge>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {relatedDocs.slice(0, 3).map((doc, didx) => (
                            <Badge key={didx} variant="secondary" className="text-xs">
                              <FileText className="w-3 h-3 mr-1" />
                              {doc.title}
                            </Badge>
                          ))}
                          {relatedDocs.length > 3 && (
                            <Badge variant="outline" className="text-xs">
                              +{relatedDocs.length - 3} autres
                            </Badge>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="text-center py-8 text-slate-500">
                  <Award className="w-12 h-12 mx-auto mb-3 text-slate-300" />
                  <p>Aucune compétence prouvée pour l'instant</p>
                  <p className="text-sm">Ajoutez des documents et liez-les à vos compétences</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Parcours Tab */}
        <TabsContent value="parcours" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Briefcase className="w-5 h-5 text-[#1e3a5f]" />
                Mon parcours professionnel
              </CardTitle>
              <CardDescription>
                Documents classés par expériences et périodes
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {["experiences_professionnelles", "diplomes_certifications", "formation_apprentissages"].map(cat => {
                  const catDocs = documents.filter(d => d.category === cat);
                  const config = CATEGORY_CONFIG[cat];
                  const Icon = config.icon;
                  return (
                    <div key={cat} className="border-l-4 border-[#1e3a5f] pl-4 py-2">
                      <h4 className="font-semibold text-slate-900 flex items-center gap-2 mb-2">
                        <Icon className="w-4 h-4" />
                        {config.label}
                      </h4>
                      {catDocs.length > 0 ? (
                        <div className="space-y-2">
                          {catDocs.map((doc, idx) => (
                            <div key={idx} className="flex items-center justify-between p-2 bg-slate-50 rounded">
                              <span className="text-sm text-slate-700">{doc.title}</span>
                              <span className="text-xs text-slate-500">{doc.date_document || "Non daté"}</span>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-sm text-slate-500">Aucun document dans cette catégorie</p>
                      )}
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Candidatures Tab */}
        <TabsContent value="candidatures" className="space-y-4">
          <DocumentCategoryView 
            documents={documents.filter(d => d.category === "recherche_emploi")}
            title="Recherche d'emploi et candidatures"
            description="Suivez vos candidatures et conservez vos échanges"
            icon={Search}
            onDelete={deleteDocument}
            onShare={(doc) => { setSelectedDocument(doc); setShareDialogOpen(true); }}
          />
        </TabsContent>

        {/* Partages Tab */}
        <TabsContent value="partages" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Share2 className="w-5 h-5 text-[#1e3a5f]" />
                Mes partages actifs
              </CardTitle>
              <CardDescription>
                Gérez qui a accès à vos documents et révoquez les partages à tout moment
              </CardDescription>
            </CardHeader>
            <CardContent>
              {shares.length > 0 ? (
                <div className="space-y-3">
                  {shares.map((share, idx) => (
                    <div key={idx} className="flex items-center justify-between p-4 rounded-lg border border-slate-200">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
                          <Link className="w-5 h-5 text-blue-600" />
                        </div>
                        <div>
                          <p className="font-medium text-slate-900">{share.document_title}</p>
                          <p className="text-xs text-slate-500">
                            Expire le {new Date(share.expires_at).toLocaleDateString('fr-FR')}
                          </p>
                        </div>
                      </div>
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        onClick={() => revokeShare(share.id)}
                      >
                        <X className="w-4 h-4 mr-1" />
                        Révoquer
                      </Button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-slate-500">
                  <Share2 className="w-12 h-12 mx-auto mb-3 text-slate-300" />
                  <p>Aucun partage actif</p>
                  <p className="text-sm">Vous gardez le contrôle total de vos documents</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Sensibles Tab */}
        <TabsContent value="sensibles" className="space-y-4">
          <DocumentCategoryView 
            documents={sensitiveDocs}
            title="Documents sensibles"
            description="Accès renforcé pour vos documents confidentiels"
            icon={Shield}
            onDelete={deleteDocument}
            onShare={(doc) => { setSelectedDocument(doc); setShareDialogOpen(true); }}
          />
        </TabsContent>

        {/* Expirants Tab */}
        <TabsContent value="expirants" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="w-5 h-5 text-amber-600" />
                Documents à renouveler
              </CardTitle>
              <CardDescription>
                Documents expirant dans les 30 prochains jours
              </CardDescription>
            </CardHeader>
            <CardContent>
              {expiringDocs.length > 0 ? (
                <div className="space-y-3">
                  {expiringDocs.map((doc, idx) => (
                    <div key={idx} className="flex items-center justify-between p-4 rounded-lg border border-amber-200 bg-amber-50">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-amber-100 flex items-center justify-center">
                          <AlertTriangle className="w-5 h-5 text-amber-600" />
                        </div>
                        <div>
                          <p className="font-medium text-slate-900">{doc.title}</p>
                          <p className="text-xs text-amber-700">
                            Expire dans {doc.days_until_expiry} jour(s)
                          </p>
                        </div>
                      </div>
                      <Badge className="bg-amber-100 text-amber-700">
                        {new Date(doc.date_expiration).toLocaleDateString('fr-FR')}
                      </Badge>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-slate-500">
                  <CheckCircle2 className="w-12 h-12 mx-auto mb-3 text-green-400" />
                  <p>Aucun document expirant prochainement</p>
                  <p className="text-sm">Vos documents sont à jour !</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Share Dialog */}
      <Dialog open={shareDialogOpen} onOpenChange={setShareDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Partager ce document</DialogTitle>
            <DialogDescription>
              Créez un lien de partage sécurisé avec une durée limitée
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 mt-4">
            <div className="p-4 bg-slate-50 rounded-lg">
              <p className="font-medium text-slate-900">{selectedDocument?.title}</p>
              <p className="text-sm text-slate-500">{CATEGORY_CONFIG[selectedDocument?.category]?.label}</p>
            </div>
            <div className="p-4 border border-blue-200 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-700">
                <Shield className="w-4 h-4 inline mr-1" />
                Le lien sera valide 7 jours et vous pourrez le révoquer à tout moment.
              </p>
            </div>
            <div className="flex justify-end gap-3">
              <Button variant="outline" onClick={() => setShareDialogOpen(false)}>
                Annuler
              </Button>
              <Button 
                className="bg-[#1e3a5f] hover:bg-[#152a45]"
                onClick={() => selectedDocument && shareDocument(selectedDocument.id)}
              >
                <Share2 className="w-4 h-4 mr-2" />
                Créer le lien de partage
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// Document Card Component
const DocumentCard = ({ document, onDelete, onShare, onDownload, downloading }) => {
  const config = CATEGORY_CONFIG[document.category] || CATEGORY_CONFIG.documents_administratifs;
  const Icon = config.icon;
  const privacyConfig = PRIVACY_LEVELS[document.privacy_level] || PRIVACY_LEVELS.private;
  const PrivacyIcon = privacyConfig.icon;
  const hasFile = !!document.storage_path;

  return (
    <Card className="card-interactive group" data-testid={`document-card-${document.id}`}>
      <CardContent className="p-5">
        <div className="flex items-start justify-between mb-3">
          <div className={`w-10 h-10 rounded-lg bg-${config.color}-100 flex items-center justify-center`}>
            <Icon className={`w-5 h-5 text-${config.color}-600`} />
          </div>
          <div className="flex items-center gap-1">
            {hasFile && (
              <Badge className="bg-emerald-50 text-emerald-700 border border-emerald-200 text-[10px]">
                <FileIcon className="w-3 h-3 mr-0.5" />Fichier
              </Badge>
            )}
            <Badge variant="outline" className="text-xs">
              <PrivacyIcon className="w-3 h-3 mr-1" />
              {privacyConfig.label}
            </Badge>
          </div>
        </div>
        
        <h3 className="font-semibold text-slate-900 mb-1 line-clamp-2 group-hover:text-[#1e3a5f] transition-colors">
          {document.title}
        </h3>
        <p className="text-xs text-slate-500 mb-3">{document.document_type}</p>
        
        {document.description && (
          <p className="text-sm text-slate-600 mb-3 line-clamp-2">{document.description}</p>
        )}
        
        {document.competences_liees?.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {document.competences_liees.slice(0, 3).map((comp, idx) => (
              <Badge key={idx} variant="secondary" className="text-xs">
                {comp}
              </Badge>
            ))}
            {document.competences_liees.length > 3 && (
              <Badge variant="outline" className="text-xs">
                +{document.competences_liees.length - 3}
              </Badge>
            )}
          </div>
        )}

        {document.file_name && document.file_size > 0 && (
          <p className="text-[10px] text-slate-400 mb-2">
            {document.file_name} — {(document.file_size / 1024).toFixed(0)} Ko
          </p>
        )}
        
        <div className="flex items-center justify-between pt-3 border-t border-slate-100">
          <span className="text-xs text-slate-400">
            {document.date_document || new Date(document.created_at).toLocaleDateString('fr-FR')}
          </span>
          <div className="flex items-center gap-1">
            {hasFile && (
              <Button
                variant="ghost" size="icon" className="h-8 w-8"
                onClick={() => onDownload && onDownload()}
                disabled={downloading}
                data-testid={`download-doc-${document.id}`}
              >
                {downloading ? <Loader2 className="w-4 h-4 animate-spin text-blue-600" /> : <Download className="w-4 h-4 text-emerald-600" />}
              </Button>
            )}
            <Button variant="ghost" size="icon" className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity" onClick={() => onShare(document)}>
              <Share2 className="w-4 h-4 text-blue-600" />
            </Button>
            <Button variant="ghost" size="icon" className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity" onClick={() => onDelete(document.id)}>
              <Trash2 className="w-4 h-4 text-red-500" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// Document Category View Component
const DocumentCategoryView = ({ documents, title, description, icon: Icon, onDelete, onShare }) => (
  <Card>
    <CardHeader>
      <CardTitle className="flex items-center gap-2">
        <Icon className="w-5 h-5 text-[#1e3a5f]" />
        {title}
      </CardTitle>
      <CardDescription>{description}</CardDescription>
    </CardHeader>
    <CardContent>
      {documents.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {documents.map((doc) => (
            <DocumentCard 
              key={doc.id} 
              document={doc} 
              onDelete={onDelete}
              onShare={onShare}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-8 text-slate-500">
          <Icon className="w-12 h-12 mx-auto mb-3 text-slate-300" />
          <p>Aucun document dans cette catégorie</p>
        </div>
      )}
    </CardContent>
  </Card>
);

export default CoffreFortView;
