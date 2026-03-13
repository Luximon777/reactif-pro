import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { 
  Building2,
  Users,
  Briefcase,
  TrendingUp,
  Plus,
  MapPin,
  Euro,
  Clock,
  Eye,
  UserCheck,
  ChevronRight,
  Search,
  Filter,
  Sparkles
} from "lucide-react";
import { toast } from "sonner";

const EntrepriseView = ({ token, section }) => {
  const [offers, setOffers] = useState([]);
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newOffer, setNewOffer] = useState({
    title: "",
    company: "",
    location: "",
    contract_type: "CDI",
    salary_range: "",
    required_skills: "",
    description: "",
    sector: "Administration"
  });

  useEffect(() => {
    loadData();
  }, [token]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [offersRes, candidatesRes, allJobsRes] = await Promise.all([
        axios.get(`${API}/rh/offers?token=${token}`),
        axios.get(`${API}/rh/candidates?token=${token}`),
        axios.get(`${API}/jobs?token=${token}`)
      ]);
      setOffers(offersRes.data.length > 0 ? offersRes.data : allJobsRes.data);
      setCandidates(candidatesRes.data);
    } catch (error) {
      console.error("Error loading data:", error);
    }
    setLoading(false);
  };

  const createOffer = async () => {
    if (!newOffer.title || !newOffer.company || !newOffer.location || !newOffer.description) {
      toast.error("Veuillez remplir tous les champs obligatoires");
      return;
    }

    try {
      const offerData = {
        ...newOffer,
        required_skills: newOffer.required_skills.split(",").map(s => s.trim()).filter(Boolean)
      };
      
      await axios.post(`${API}/jobs?token=${token}`, offerData);
      toast.success("Offre créée avec succès !");
      setCreateDialogOpen(false);
      setNewOffer({
        title: "",
        company: "",
        location: "",
        contract_type: "CDI",
        salary_range: "",
        required_skills: "",
        description: "",
        sector: "Administration"
      });
      loadData();
    } catch (error) {
      toast.error("Erreur lors de la création de l'offre");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600"></div>
      </div>
    );
  }

  const metrics = [
    {
      title: "Offres Actives",
      value: offers.length.toString(),
      icon: Briefcase,
      color: "emerald",
      subtitle: "Publiées sur la plateforme"
    },
    {
      title: "Profils Compatibles",
      value: "12",
      icon: Users,
      color: "blue",
      subtitle: "Compétences transférables"
    },
    {
      title: "Taux d'Adéquation",
      value: "78%",
      icon: TrendingUp,
      color: "amber",
      subtitle: "Correspondance compétences"
    },
    {
      title: "Consultations",
      value: "156",
      icon: Eye,
      color: "violet",
      subtitle: "Ce mois-ci"
    }
  ];

  if (section === "jobs") {
    return <OffersManagement offers={offers} onCreateOffer={() => setCreateDialogOpen(true)} />;
  }

  return (
    <div className="space-y-8 animate-fade-in" data-testid="entreprise-dashboard">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>
            Espace Employeurs
          </h1>
          <p className="text-slate-600 mt-1">Identifiez les compétences en adéquation avec vos besoins</p>
        </div>
        <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button className="btn-primary bg-emerald-600 hover:bg-emerald-700" data-testid="create-offer-btn">
              <Plus className="w-4 h-4 mr-2" />
              Nouvelle Offre
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Créer une nouvelle offre</DialogTitle>
              <DialogDescription>
                Publiez une offre d'emploi pour trouver le candidat idéal
              </DialogDescription>
            </DialogHeader>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Titre du poste *</label>
                <Input
                  placeholder="Ex: Développeur Web"
                  value={newOffer.title}
                  onChange={(e) => setNewOffer({ ...newOffer, title: e.target.value })}
                  data-testid="offer-title-input"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Entreprise *</label>
                <Input
                  placeholder="Nom de l'entreprise"
                  value={newOffer.company}
                  onChange={(e) => setNewOffer({ ...newOffer, company: e.target.value })}
                  data-testid="offer-company-input"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Localisation *</label>
                <Input
                  placeholder="Ex: Paris, France"
                  value={newOffer.location}
                  onChange={(e) => setNewOffer({ ...newOffer, location: e.target.value })}
                  data-testid="offer-location-input"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Type de contrat</label>
                <Select 
                  value={newOffer.contract_type} 
                  onValueChange={(v) => setNewOffer({ ...newOffer, contract_type: v })}
                >
                  <SelectTrigger data-testid="offer-contract-select">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="CDI">CDI</SelectItem>
                    <SelectItem value="CDD">CDD</SelectItem>
                    <SelectItem value="Stage">Stage</SelectItem>
                    <SelectItem value="Alternance">Alternance</SelectItem>
                    <SelectItem value="Freelance">Freelance</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Fourchette salariale</label>
                <Input
                  placeholder="Ex: 35 000€ - 45 000€"
                  value={newOffer.salary_range}
                  onChange={(e) => setNewOffer({ ...newOffer, salary_range: e.target.value })}
                  data-testid="offer-salary-input"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Secteur</label>
                <Select 
                  value={newOffer.sector} 
                  onValueChange={(v) => setNewOffer({ ...newOffer, sector: v })}
                >
                  <SelectTrigger data-testid="offer-sector-select">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Administration">Administration</SelectItem>
                    <SelectItem value="Commerce">Commerce</SelectItem>
                    <SelectItem value="Informatique">Informatique</SelectItem>
                    <SelectItem value="Comptabilité">Comptabilité</SelectItem>
                    <SelectItem value="Formation">Formation</SelectItem>
                    <SelectItem value="Santé">Santé</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="md:col-span-2 space-y-2">
                <label className="text-sm font-medium text-slate-700">Compétences requises</label>
                <Input
                  placeholder="Séparez par des virgules: Excel, Communication, Organisation"
                  value={newOffer.required_skills}
                  onChange={(e) => setNewOffer({ ...newOffer, required_skills: e.target.value })}
                  data-testid="offer-skills-input"
                />
              </div>
              <div className="md:col-span-2 space-y-2">
                <label className="text-sm font-medium text-slate-700">Description *</label>
                <Textarea
                  placeholder="Décrivez le poste et les missions..."
                  rows={4}
                  value={newOffer.description}
                  onChange={(e) => setNewOffer({ ...newOffer, description: e.target.value })}
                  data-testid="offer-description-input"
                />
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <Button variant="outline" onClick={() => setCreateDialogOpen(false)}>
                Annuler
              </Button>
              <Button onClick={createOffer} className="bg-emerald-600 hover:bg-emerald-700" data-testid="submit-offer-btn">
                Publier l'offre
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4" data-testid="rh-metrics">
        {metrics.map((metric, idx) => {
          const Icon = metric.icon;
          const colorClasses = {
            emerald: "bg-emerald-100 text-emerald-600",
            blue: "bg-blue-100 text-blue-600",
            amber: "bg-amber-100 text-amber-600",
            violet: "bg-violet-100 text-violet-600"
          };
          return (
            <Card key={idx} className="card-metric card-hover" data-testid={`rh-metric-${idx}`}>
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
        {/* Offers List */}
        <Card className="lg:col-span-2 card-base" data-testid="offers-list">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Briefcase className="w-5 h-5 text-emerald-600" />
                Mes Offres
              </CardTitle>
              <CardDescription>Gérez vos offres d'emploi actives</CardDescription>
            </div>
            <Button variant="outline" size="sm">
              Voir tout
              <ChevronRight className="w-4 h-4 ml-1" />
            </Button>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {offers.slice(0, 5).map((offer, idx) => (
                <div 
                  key={idx} 
                  className="p-4 rounded-xl border border-slate-100 hover:border-emerald-200 hover:bg-emerald-50/30 transition-all cursor-pointer"
                  data-testid={`offer-item-${idx}`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-semibold text-slate-900">{offer.title}</h3>
                        <Badge variant="outline" className="text-xs">{offer.contract_type}</Badge>
                      </div>
                      <p className="text-sm text-slate-600">{offer.company}</p>
                      <div className="flex items-center gap-4 mt-2 text-xs text-slate-500">
                        <span className="flex items-center gap-1">
                          <MapPin className="w-3 h-3" />
                          {offer.location}
                        </span>
                        {offer.salary_range && (
                          <span className="flex items-center gap-1">
                            <Euro className="w-3 h-3" />
                            {offer.salary_range}
                          </span>
                        )}
                      </div>
                    </div>
                    <Badge className="bg-emerald-100 text-emerald-700 border-emerald-200">
                      Actif
                    </Badge>
                  </div>
                </div>
              ))}
              {offers.length === 0 && (
                <div className="text-center py-8 text-slate-500">
                  <Briefcase className="w-12 h-12 mx-auto mb-3 text-slate-300" />
                  <p>Aucune offre publiée</p>
                  <p className="text-sm">Créez votre première offre d'emploi</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Candidates Preview */}
        <Card className="card-base" data-testid="candidates-preview">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <UserCheck className="w-5 h-5 text-[#1e3a5f]" />
              Profils & Compétences
            </CardTitle>
            <CardDescription>Compétences transférables identifiées</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {candidates.slice(0, 5).map((candidate, idx) => (
                <div 
                  key={idx}
                  className="p-3 rounded-lg border border-slate-100 hover:border-blue-200 hover:bg-blue-50/30 transition-all cursor-pointer"
                  data-testid={`candidate-${idx}`}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                      <Users className="w-5 h-5 text-blue-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-slate-900 truncate">{candidate.name}</p>
                      <p className="text-xs text-slate-500">{candidate.skills?.length || 0} compétences</p>
                    </div>
                    {candidate.match_score && (
                      <Badge className={`${candidate.match_score >= 70 ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'}`}>
                        {candidate.match_score}%
                      </Badge>
                    )}
                  </div>
                </div>
              ))}
              {candidates.length === 0 && (
                <div className="text-center py-6 text-slate-500">
                  <Users className="w-10 h-10 mx-auto mb-2 text-slate-300" />
                  <p className="text-sm">Aucun candidat pour le moment</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* AI Matching Banner */}
      <Card className="bg-[#1e3a5f]" data-testid="ai-banner">
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white">Intelligence Professionnelle</h3>
                <p className="text-blue-100 text-sm">Analyse des compétences transférables et passerelles métiers</p>
              </div>
            </div>
            <Button className="bg-white text-[#1e3a5f] hover:bg-blue-50">
              Paramétrer l'analyse
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

const OffersManagement = ({ offers, onCreateOffer }) => (
  <div className="space-y-6 animate-fade-in" data-testid="offers-management">
    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>
          Gestion des Offres
        </h1>
        <p className="text-slate-600 mt-1">Créez et gérez vos offres d'emploi</p>
      </div>
      <div className="flex items-center gap-3">
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <Input placeholder="Rechercher..." className="pl-10 w-64" />
        </div>
        <Button variant="outline">
          <Filter className="w-4 h-4 mr-2" />
          Filtrer
        </Button>
        <Button onClick={onCreateOffer} className="bg-emerald-600 hover:bg-emerald-700">
          <Plus className="w-4 h-4 mr-2" />
          Nouvelle Offre
        </Button>
      </div>
    </div>

    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 stagger-children">
      {offers.map((offer, idx) => (
        <Card key={idx} className="card-interactive" data-testid={`manage-offer-${idx}`}>
          <CardContent className="p-5">
            <div className="flex items-start justify-between mb-3">
              <Badge variant="outline">{offer.contract_type}</Badge>
              <Badge className="bg-emerald-100 text-emerald-700">Actif</Badge>
            </div>
            <h3 className="font-semibold text-slate-900 mb-1">{offer.title}</h3>
            <p className="text-sm text-slate-600 mb-3">{offer.company}</p>
            <div className="space-y-1 text-xs text-slate-500 mb-3">
              <div className="flex items-center gap-1">
                <MapPin className="w-3 h-3" />
                {offer.location}
              </div>
              {offer.salary_range && (
                <div className="flex items-center gap-1">
                  <Euro className="w-3 h-3" />
                  {offer.salary_range}
                </div>
              )}
            </div>
            <div className="flex flex-wrap gap-1 mb-4">
              {offer.required_skills?.slice(0, 3).map((skill, sidx) => (
                <Badge key={sidx} variant="secondary" className="text-xs">
                  {skill}
                </Badge>
              ))}
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" className="flex-1">
                <Eye className="w-3 h-3 mr-1" />
                Voir
              </Button>
              <Button size="sm" className="flex-1 bg-emerald-600 hover:bg-emerald-700">
                <Users className="w-3 h-3 mr-1" />
                Candidats
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  </div>
);

export default EntrepriseView;
