import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/App";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Users, 
  Building2, 
  Handshake, 
  ArrowRight, 
  Target, 
  BookOpen, 
  TrendingUp,
  Shield,
  CheckCircle2,
  ChevronRight,
  Briefcase,
  MapPin,
  Compass,
  Lightbulb,
  Lock,
  Eye,
  Heart,
  Scale,
  FileCheck,
  UserPlus
} from "lucide-react";
import { toast } from "sonner";
import LogoReactifPro from "@/components/LogoReactifPro";
import AuthModal from "@/components/AuthModal";
import ProRegisterModal from "@/components/ProRegisterModal";

const Landing = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [proModalOpen, setProModalOpen] = useState(false);
  const [proModalRole, setProModalRole] = useState("entreprise");

  const handlePersonalAuth = () => {
    setAuthModalOpen(true);
  };

  const handleProAuth = (role) => {
    setProModalRole(role);
    setProModalOpen(true);
  };

  const handleAuthSuccess = () => {
    setAuthModalOpen(false);
    setProModalOpen(false);
    navigate("/dashboard");
  };

  const handleGoToDashboard = () => {
    if (isAuthenticated) {
      navigate("/dashboard");
    }
  };

  const roles = [
    {
      id: "particulier",
      title: "Espace Personnel",
      description: "Révélez et valorisez vos compétences réelles pour construire des trajectoires professionnelles durables",
      icon: Users,
      color: "blue",
      features: ["Coffre-fort numérique des compétences", "Identité professionnelle sécurisée", "Orientation personnalisée"]
    },
    {
      id: "entreprise",
      title: "Espace Employeurs",
      description: "Identifiez les talents et compétences en adéquation avec vos besoins économiques",
      icon: Building2,
      color: "emerald",
      features: ["Profils compatibles", "Compétences transférables", "Passerelles métiers"]
    },
    {
      id: "partenaire",
      title: "Appui aux parcours",
      description: "Interface de coordination pour les acteurs de l'accompagnement — en complementarite des dispositifs existants",
      icon: Handshake,
      color: "violet",
      features: ["Diagnostic enrichi", "Coordination des parcours", "Contribution territoriale"]
    }
  ];

  const missions = [
    {
      icon: Eye,
      title: "Révéler les compétences",
      description: "Identifier, structurer et valoriser l'identité professionnelle de chacun, au-delà des diplômes et intitulés de poste."
    },
    {
      icon: Shield,
      title: "Sécuriser les trajectoires",
      description: "Conserver une mémoire professionnelle numérique tout au long de la vie pour construire une sécurité sociale des compétences."
    },
    {
      icon: Compass,
      title: "Faciliter les transitions",
      description: "Identifier les passerelles entre métiers, les compétences transférables et les opportunités de formation."
    },
    {
      icon: Lightbulb,
      title: "Intelligence collective",
      description: "Produire une meilleure compréhension des transformations du travail grâce à l'analyse de données anonymisées."
    }
  ];

  const ethicsPoints = [
    { icon: Lock, title: "Souveraineté des données", desc: "L'usager reste propriétaire de ses données" },
    { icon: Eye, title: "Transparence", desc: "Algorithmes explicables et compréhensibles" },
    { icon: Heart, title: "Au service de l'humain", desc: "L'IA comme outil d'assistance, pas de décision" },
    { icon: Scale, title: "Conformité AI Act", desc: "Respect du Règlement européen 2024/1689" }
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 glass border-b border-slate-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <LogoReactifPro size="sm" />
            </div>
            <Badge variant="secondary" className="bg-blue-50 text-[#1e3a5f] border-blue-200">
              Région Grand Est
            </Badge>
          </div>
        </div>
      </header>

      {/* Hero Section - Style officiel */}
      <section className="pt-24 pb-16 px-4 bg-[#1e3a5f] text-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-4xl mx-auto py-16 animate-fade-in">
            <div className="flex justify-center mb-8">
              <div className="bg-white/95 rounded-2xl shadow-lg p-8">
                <LogoReactifPro size="xl" />
              </div>
            </div>
            <p className="text-xl sm:text-2xl text-blue-100 mb-4 italic">
              Dispositif de réactivation rapide des parcours vers l'emploi
            </p>
            <div className="flex flex-wrap items-center justify-center gap-3 text-blue-200 mt-8">
              <span className="flex items-center gap-2">
                <Compass className="w-4 h-4" />
                Orientation
              </span>
              <span className="text-blue-400">•</span>
              <span className="flex items-center gap-2">
                <Briefcase className="w-4 h-4" />
                Emploi
              </span>
              <span className="text-blue-400">•</span>
              <span className="flex items-center gap-2">
                <MapPin className="w-4 h-4" />
                Mobilité
              </span>
              <span className="text-blue-400">•</span>
              <span className="flex items-center gap-2">
                <Lightbulb className="w-4 h-4" />
                Innovation sociale
              </span>
            </div>
            {isAuthenticated && (
              <div className="mt-8">
                <Button size="lg" onClick={handleGoToDashboard} className="bg-white text-[#1e3a5f] hover:bg-blue-50 font-semibold px-8" data-testid="go-to-dashboard-btn">
                  <ArrowRight className="w-5 h-5 mr-2" />
                  Accéder à mon espace
                </Button>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Présentation */}
      <section className="py-16 px-4 bg-slate-50">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-[#1e3a5f] mb-4" style={{ fontFamily: 'Outfit, sans-serif' }}>
              Un dispositif d'innovation sociale et numérique
            </h2>
            <p className="text-lg text-slate-600 leading-relaxed">
              RE'ACTIF PRO est un dispositif développé pour répondre aux transformations profondes du monde du travail. 
              Les trajectoires professionnelles deviennent plus complexes : reconversions, mobilités, évolution rapide des métiers. 
              Les outils traditionnels d'orientation montrent leurs limites car ils reposent encore sur une logique centrée sur le diplôme.
            </p>
          </div>
          
          <Card className="bg-blue-50 border-l-4 border-l-[#1e3a5f] border-slate-200">
            <CardContent className="p-6">
              <p className="text-[#1e3a5f] font-medium text-lg">
                <strong>Notre approche :</strong> Révéler et valoriser les compétences réelles des personnes 
                afin de leur permettre de construire des trajectoires professionnelles cohérentes et durables.
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Role Selection Cards */}
      <section className="py-16 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-[#1e3a5f] mb-4" style={{ fontFamily: 'Outfit, sans-serif' }}>
              Vos accès
            </h2>
            <p className="text-lg text-slate-600">
              Choisissez votre espace pour accéder à vos outils personnalisés
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto stagger-children" data-testid="role-selection">
            {roles.map((role) => {
              const Icon = role.icon;
              const iconColorClasses = {
                blue: "bg-[#1e3a5f] text-white",
                emerald: "bg-emerald-600 text-white",
                violet: "bg-violet-600 text-white"
              };
              
              const handleClick = () => {
                if (role.id === "particulier") handlePersonalAuth();
                else handleProAuth(role.id);
              };

              const btnLabel = role.id === "particulier"
                ? "Compte confidentiel"
                : role.id === "entreprise"
                  ? "Inscription employeur"
                  : "Inscription partenaire";
              
              return (
                <Card 
                  key={role.id}
                  data-testid={`role-card-${role.id}`}
                  className="card-interactive cursor-pointer hover:border-[#1e3a5f]/30 transition-all flex flex-col"
                  onClick={handleClick}
                >
                  <CardHeader>
                    <div className={`w-14 h-14 rounded-2xl ${iconColorClasses[role.color]} flex items-center justify-center mb-4`}>
                      <Icon className="w-7 h-7" />
                    </div>
                    <CardTitle className="text-xl font-semibold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>
                      {role.title}
                    </CardTitle>
                    <CardDescription className="text-slate-600">
                      {role.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="flex flex-col flex-1">
                    <ul className="space-y-2 mb-6 flex-1">
                      {role.features.map((feature, idx) => (
                        <li key={idx} className="flex items-center gap-2 text-sm text-slate-600">
                          <CheckCircle2 className="w-4 h-4 text-green-500 flex-shrink-0" />
                          {feature}
                        </li>
                      ))}
                    </ul>
                    <Button 
                      className="w-full bg-[#1e3a5f] hover:bg-[#152a45] text-white group mt-auto"
                      onClick={(e) => { e.stopPropagation(); handleClick(); }}
                      data-testid={`register-btn-${role.id}`}
                    >
                      {btnLabel}
                      <ArrowRight className="w-4 h-4 ml-1 flex-shrink-0 group-hover:translate-x-1 transition-transform" />
                    </Button>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      {/* Missions Section */}
      <section className="py-16 px-4 bg-slate-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-[#1e3a5f] mb-4" style={{ fontFamily: 'Outfit, sans-serif' }}>
              Nos missions
            </h2>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              RE'ACTIF PRO poursuit plusieurs missions complémentaires au service des citoyens, des entreprises et des territoires.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {missions.map((mission, idx) => {
              const Icon = mission.icon;
              return (
                <Card key={idx} className="card-base p-6 card-hover" data-testid={`mission-card-${idx}`}>
                  <div className="w-12 h-12 rounded-xl bg-[#1e3a5f] text-white flex items-center justify-center mb-4">
                    <Icon className="w-6 h-6" />
                  </div>
                  <h3 className="text-lg font-semibold text-slate-900 mb-2" style={{ fontFamily: 'Outfit, sans-serif' }}>
                    {mission.title}
                  </h3>
                  <p className="text-sm text-slate-600">
                    {mission.description}
                  </p>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      {/* Coffre-fort numérique */}
      <section className="py-16 px-4">
        <div className="max-w-4xl mx-auto">
          <Card className="overflow-hidden">
            <div className="grid md:grid-cols-2">
              <div className="p-8 bg-[#1e3a5f] text-white">
                <h3 className="text-2xl font-bold mb-4" style={{ fontFamily: 'Outfit, sans-serif' }}>
                  Coffre-fort numérique des compétences
                </h3>
                <p className="text-blue-100 mb-6">
                  Chaque utilisateur dispose d'un espace personnel sécurisé dans lequel il peut conserver et gérer l'ensemble de ses informations professionnelles.
                </p>
                <ul className="space-y-3 text-blue-100">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-blue-300" />
                    Compétences & Expériences
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-blue-300" />
                    Certifications & Formations
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-blue-300" />
                    Projets professionnels
                  </li>
                </ul>
              </div>
              <div className="p-8 bg-white">
                <h4 className="text-lg font-semibold text-[#1e3a5f] mb-4">Principe fondamental</h4>
                <p className="text-slate-600 mb-6">
                  L'usager reste propriétaire de ses données et de son identité professionnelle. 
                  Il décide lui-même des conditions d'accès à ses informations.
                </p>
                <div className="p-4 bg-blue-50 rounded-lg border-l-4 border-l-[#1e3a5f]">
                  <p className="text-sm text-[#1e3a5f] font-medium">
                    RE'ACTIF PRO agit comme un <strong>tiers de confiance numérique</strong> permettant de sécuriser les données professionnelles tout en facilitant les transitions.
                  </p>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </section>

      {/* Charte IA */}
      <section className="py-16 px-4 bg-slate-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <Badge className="mb-4 bg-[#1e3a5f] text-white">
              <FileCheck className="w-3 h-3 mr-1" />
              Conforme AI Act - Règlement (UE) 2024/1689
            </Badge>
            <h2 className="text-3xl font-bold text-[#1e3a5f] mb-4" style={{ fontFamily: 'Outfit, sans-serif' }}>
              Technologie éthique au service de l'humain
            </h2>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              RE'ACTIF PRO s'engage à ce que les technologies numériques et l'intelligence artificielle restent au service de l'humain et de l'intérêt général.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {ethicsPoints.map((point, idx) => {
              const Icon = point.icon;
              return (
                <Card key={idx} className="p-5 bg-white">
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 rounded-lg bg-blue-100 text-[#1e3a5f] flex items-center justify-center flex-shrink-0">
                      <Icon className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-slate-900 mb-1">{point.title}</h4>
                      <p className="text-sm text-slate-600">{point.desc}</p>
                    </div>
                  </div>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <Card className="p-12 bg-[#1e3a5f] border-0">
            <h2 className="text-3xl font-bold text-white mb-4" style={{ fontFamily: 'Outfit, sans-serif' }}>
              Prêt à valoriser vos compétences ?
            </h2>
            <p className="text-blue-100 mb-8 text-lg">
              Rejoignez RE'ACTIF PRO et construisez une trajectoire professionnelle cohérente et durable.
            </p>
            <Button 
              size="lg"
              className="bg-white text-[#1e3a5f] hover:bg-blue-50 font-semibold px-8"
              onClick={() => handlePersonalAuth()}
              data-testid="cta-start-btn"
            >
              Accéder à mon espace
              <ChevronRight className="w-5 h-5 ml-2" />
            </Button>
          </Card>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 border-t border-slate-100 bg-slate-50">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <img 
              src="/logo-reactif-pro-hd.png?v=2" 
              alt="RE'ACTIF PRO" 
              className="h-10 w-auto"
            />
            <span className="text-slate-400 mx-2">|</span>
            <span className="text-sm text-slate-500">Un dispositif ALT&ACT</span>
          </div>
          <div className="flex items-center gap-4 text-sm text-slate-500">
            <span>Région Grand Est</span>
            <span className="text-slate-300">•</span>
            <span>Innovation sociale et numérique</span>
          </div>
        </div>
      </footer>

      {/* Auth Modal (Personal) */}
      <AuthModal
        open={authModalOpen}
        onOpenChange={setAuthModalOpen}
        defaultRole="particulier"
        onSuccess={handleAuthSuccess}
      />

      {/* Pro Register Modal (Entreprise/Partenaire) */}
      <ProRegisterModal
        open={proModalOpen}
        onOpenChange={setProModalOpen}
        roleType={proModalRole}
        onSuccess={handleAuthSuccess}
      />
    </div>
  );
};

export default Landing;
