import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { 
  Handshake,
  Users,
  TrendingUp,
  MapPin,
  Plus,
  Eye,
  CheckCircle2,
  Clock,
  AlertTriangle,
  BarChart3,
  Target,
  FileText,
  ArrowUpRight,
  Calendar
} from "lucide-react";
import { toast } from "sonner";

const PartenaireView = ({ token }) => {
  const [beneficiaires, setBeneficiaires] = useState([]);
  const [loading, setLoading] = useState(true);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newBeneficiaire, setNewBeneficiaire] = useState({
    name: "",
    sector: "Administration"
  });

  useEffect(() => {
    loadData();
  }, [token]);

  const loadData = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/partenaires/beneficiaires?token=${token}`);
      setBeneficiaires(response.data);
    } catch (error) {
      console.error("Error loading beneficiaires:", error);
      // Use demo data if empty
      setBeneficiaires(demoBeneficiaires);
    }
    setLoading(false);
  };

  const createBeneficiaire = async () => {
    if (!newBeneficiaire.name) {
      toast.error("Veuillez saisir le nom du bénéficiaire");
      return;
    }

    try {
      await axios.post(
        `${API}/partenaires/beneficiaires?token=${token}&name=${encodeURIComponent(newBeneficiaire.name)}&sector=${encodeURIComponent(newBeneficiaire.sector)}`
      );
      toast.success("Bénéficiaire ajouté !");
      setCreateDialogOpen(false);
      setNewBeneficiaire({ name: "", sector: "Administration" });
      loadData();
    } catch (error) {
      toast.error("Erreur lors de l'ajout");
    }
  };

  const updateBeneficiaireStatus = async (id, newStatus) => {
    try {
      await axios.put(`${API}/partenaires/beneficiaires/${id}?token=${token}&status=${encodeURIComponent(newStatus)}`);
      setBeneficiaires(prev => prev.map(b => 
        b.id === id ? { ...b, status: newStatus } : b
      ));
      toast.success("Statut mis à jour !");
    } catch (error) {
      toast.error("Erreur lors de la mise à jour");
    }
  };

  const demoBeneficiaires = [
    { id: "1", name: "Marie Dupont", status: "En accompagnement", progress: 65, sector: "Administration", skills_acquired: ["Excel", "Communication"], last_activity: new Date().toISOString() },
    { id: "2", name: "Jean Martin", status: "Formation en cours", progress: 45, sector: "Commerce", skills_acquired: ["Relation client"], last_activity: new Date().toISOString() },
    { id: "3", name: "Sophie Bernard", status: "Recherche d'emploi", progress: 85, sector: "Informatique", skills_acquired: ["HTML/CSS", "JavaScript", "Git"], last_activity: new Date().toISOString() },
    { id: "4", name: "Pierre Leroy", status: "En emploi", progress: 100, sector: "Comptabilité", skills_acquired: ["Paie", "SILAE", "Excel avancé"], last_activity: new Date().toISOString() },
    { id: "5", name: "Claire Moreau", status: "En attente", progress: 20, sector: "Formation", skills_acquired: [], last_activity: new Date().toISOString() }
  ];

  const displayBeneficiaires = beneficiaires.length > 0 ? beneficiaires : demoBeneficiaires;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-violet-600"></div>
      </div>
    );
  }

  const statusCounts = {
    total: displayBeneficiaires.length,
    enAccompagnement: displayBeneficiaires.filter(b => b.status === "En accompagnement").length,
    enFormation: displayBeneficiaires.filter(b => b.status === "Formation en cours").length,
    enEmploi: displayBeneficiaires.filter(b => b.status === "En emploi").length,
    enRecherche: displayBeneficiaires.filter(b => b.status === "Recherche d'emploi").length
  };

  const metrics = [
    {
      title: "Personnes Accompagnées",
      value: statusCounts.total.toString(),
      icon: Users,
      color: "violet",
      subtitle: "Parcours en cours"
    },
    {
      title: "En Transition",
      value: statusCounts.enAccompagnement.toString(),
      icon: Handshake,
      color: "blue",
      subtitle: "Accompagnement actif"
    },
    {
      title: "Insertions Réussies",
      value: statusCounts.enEmploi.toString(),
      icon: CheckCircle2,
      color: "emerald",
      subtitle: "Trajectoires sécurisées"
    },
    {
      title: "Taux de Réussite",
      value: `${Math.round((statusCounts.enEmploi / Math.max(statusCounts.total, 1)) * 100)}%`,
      icon: TrendingUp,
      color: "amber",
      subtitle: "Transitions professionnelles"
    }
  ];

  const getStatusBadge = (status) => {
    const statusConfig = {
      "En accompagnement": { color: "bg-blue-100 text-blue-700 border-blue-200", icon: Clock },
      "Formation en cours": { color: "bg-amber-100 text-amber-700 border-amber-200", icon: Target },
      "Recherche d'emploi": { color: "bg-violet-100 text-violet-700 border-violet-200", icon: Eye },
      "En emploi": { color: "bg-green-100 text-green-700 border-green-200", icon: CheckCircle2 },
      "En attente": { color: "bg-slate-100 text-slate-700 border-slate-200", icon: AlertTriangle }
    };
    return statusConfig[status] || statusConfig["En attente"];
  };

  return (
    <div className="space-y-8 animate-fade-in" data-testid="partenaire-dashboard">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>
            Espace Partenaires
          </h1>
          <p className="text-slate-600 mt-1">Observatoire des compétences et accompagnement des transitions</p>
        </div>
        <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button className="btn-primary bg-violet-600 hover:bg-violet-700" data-testid="add-beneficiaire-btn">
              <Plus className="w-4 h-4 mr-2" />
              Nouveau Bénéficiaire
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Ajouter un bénéficiaire</DialogTitle>
              <DialogDescription>
                Créez un nouveau suivi pour accompagner un bénéficiaire
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 mt-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Nom du bénéficiaire *</label>
                <Input
                  placeholder="Prénom Nom"
                  value={newBeneficiaire.name}
                  onChange={(e) => setNewBeneficiaire({ ...newBeneficiaire, name: e.target.value })}
                  data-testid="beneficiaire-name-input"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Secteur visé</label>
                <Select 
                  value={newBeneficiaire.sector} 
                  onValueChange={(v) => setNewBeneficiaire({ ...newBeneficiaire, sector: v })}
                >
                  <SelectTrigger data-testid="beneficiaire-sector-select">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Administration">Administration</SelectItem>
                    <SelectItem value="Commerce">Commerce</SelectItem>
                    <SelectItem value="Informatique">Informatique</SelectItem>
                    <SelectItem value="Comptabilité">Comptabilité</SelectItem>
                    <SelectItem value="Formation">Formation</SelectItem>
                    <SelectItem value="Santé">Santé</SelectItem>
                    <SelectItem value="Industrie">Industrie</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button onClick={createBeneficiaire} className="w-full bg-violet-600 hover:bg-violet-700" data-testid="submit-beneficiaire-btn">
                Créer le suivi
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4" data-testid="partenaire-metrics">
        {metrics.map((metric, idx) => {
          const Icon = metric.icon;
          const colorClasses = {
            violet: "bg-violet-100 text-violet-600",
            blue: "bg-blue-100 text-blue-600",
            emerald: "bg-emerald-100 text-emerald-600",
            amber: "bg-amber-100 text-amber-600"
          };
          return (
            <Card key={idx} className="card-metric card-hover" data-testid={`partenaire-metric-${idx}`}>
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-500 mb-1">{metric.title}</p>
                    <p className="text-3xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>
                      {metric.value}
                    </p>
                    <p className="text-xs text-slate-400 mt-1">{metric.subtitle}</p>
                  </div>
                  <div className={`w-12 h-12 rounded-xl ${colorClasses[metric.color]} flex items-center justify-center`}>
                    <Icon className="w-6 h-6" />
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Beneficiaires List */}
        <Card className="lg:col-span-2 card-base" data-testid="beneficiaires-list">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="w-5 h-5 text-[#1e3a5f]" />
              Parcours Accompagnés
            </CardTitle>
            <CardDescription>Suivi des transitions professionnelles</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {displayBeneficiaires.map((beneficiaire, idx) => {
                const statusConfig = getStatusBadge(beneficiaire.status);
                const StatusIcon = statusConfig.icon;
                return (
                  <div 
                    key={idx}
                    className="p-4 rounded-xl border border-slate-100 hover:border-violet-200 hover:bg-violet-50/30 transition-all"
                    data-testid={`beneficiaire-${idx}`}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-violet-100 flex items-center justify-center">
                          <Users className="w-5 h-5 text-violet-600" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-slate-900">{beneficiaire.name}</h3>
                          <p className="text-xs text-slate-500">Secteur: {beneficiaire.sector}</p>
                        </div>
                      </div>
                      <Badge className={`${statusConfig.color} flex items-center gap-1`}>
                        <StatusIcon className="w-3 h-3" />
                        {beneficiaire.status}
                      </Badge>
                    </div>
                    <div className="space-y-2 mb-3">
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-slate-600">Progression du parcours</span>
                        <span className="font-medium text-slate-900">{beneficiaire.progress}%</span>
                      </div>
                      <Progress value={beneficiaire.progress} className="h-2" />
                    </div>
                    {beneficiaire.skills_acquired?.length > 0 && (
                      <div className="flex flex-wrap gap-1 mb-3">
                        {beneficiaire.skills_acquired.map((skill, sidx) => (
                          <Badge key={sidx} variant="secondary" className="text-xs">
                            {skill}
                          </Badge>
                        ))}
                      </div>
                    )}
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-slate-400 flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        Dernière activité: {new Date(beneficiaire.last_activity).toLocaleDateString('fr-FR')}
                      </span>
                      <div className="flex items-center gap-2">
                        <Select 
                          value={beneficiaire.status}
                          onValueChange={(v) => updateBeneficiaireStatus(beneficiaire.id, v)}
                        >
                          <SelectTrigger className="h-8 text-xs w-40">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="En attente">En attente</SelectItem>
                            <SelectItem value="En accompagnement">En accompagnement</SelectItem>
                            <SelectItem value="Formation en cours">Formation en cours</SelectItem>
                            <SelectItem value="Recherche d'emploi">Recherche d'emploi</SelectItem>
                            <SelectItem value="En emploi">En emploi</SelectItem>
                          </SelectContent>
                        </Select>
                        <Button variant="outline" size="sm">
                          <Eye className="w-3 h-3 mr-1" />
                          Détails
                        </Button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Stats & Observations */}
        <div className="space-y-6">
          {/* Status Distribution */}
          <Card className="card-base" data-testid="status-distribution">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <BarChart3 className="w-5 h-5 text-violet-600" />
                Répartition
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600 flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                    En accompagnement
                  </span>
                  <span className="font-medium text-slate-900">{statusCounts.enAccompagnement}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600 flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-amber-500"></div>
                    En formation
                  </span>
                  <span className="font-medium text-slate-900">{statusCounts.enFormation}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600 flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-violet-500"></div>
                    Recherche d'emploi
                  </span>
                  <span className="font-medium text-slate-900">{statusCounts.enRecherche}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600 flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-green-500"></div>
                    En emploi
                  </span>
                  <span className="font-medium text-slate-900">{statusCounts.enEmploi}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Observations Territoriales */}
          <Card className="card-base" data-testid="territorial-observations">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <MapPin className="w-5 h-5 text-[#1e3a5f]" />
                Intelligence Territoriale
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="p-3 rounded-lg bg-blue-50 border border-blue-100">
                  <div className="flex items-center gap-2 text-sm text-[#1e3a5f] font-medium mb-1">
                    <ArrowUpRight className="w-4 h-4" />
                    Compétences émergentes
                  </div>
                  <p className="text-xs text-blue-600">Numérique: +15% de besoins ce trimestre</p>
                </div>
                <div className="p-3 rounded-lg bg-amber-50 border border-amber-100">
                  <div className="flex items-center gap-2 text-sm text-amber-700 font-medium mb-1">
                    <AlertTriangle className="w-4 h-4" />
                    Besoin formation identifié
                  </div>
                  <p className="text-xs text-amber-600">Compétences transversales très demandées</p>
                </div>
                <div className="p-3 rounded-lg bg-green-50 border border-green-100">
                  <div className="flex items-center gap-2 text-sm text-green-700 font-medium mb-1">
                    <CheckCircle2 className="w-4 h-4" />
                    Tendance positive
                  </div>
                  <p className="text-xs text-green-600">Transitions sécurisées +8% vs trimestre dernier</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card className="card-base" data-testid="quick-actions">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <FileText className="w-5 h-5 text-violet-600" />
                Actions Rapides
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button variant="outline" className="w-full justify-start">
                <FileText className="w-4 h-4 mr-2" />
                Générer un rapport
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <Calendar className="w-4 h-4 mr-2" />
                Planifier un RDV
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <Target className="w-4 h-4 mr-2" />
                Créer une prescription
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default PartenaireView;
