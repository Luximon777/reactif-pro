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
  Sparkles,
  CheckCircle2,
  ChevronRight
} from "lucide-react";
import { toast } from "sonner";

const Landing = () => {
  const navigate = useNavigate();
  const { login, isAuthenticated } = useAuth();
  const [selectedRole, setSelectedRole] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleRoleSelect = async (role) => {
    setSelectedRole(role);
    setIsLoading(true);
    
    const success = await login(role);
    
    if (success) {
      toast.success("Connexion réussie !");
      navigate("/dashboard");
    } else {
      toast.error("Erreur de connexion");
    }
    
    setIsLoading(false);
  };

  if (isAuthenticated) {
    navigate("/dashboard");
    return null;
  }

  const roles = [
    {
      id: "particulier",
      title: "Particulier",
      description: "Développez votre carrière et trouvez votre prochaine opportunité",
      icon: Users,
      color: "blue",
      features: ["Analyse de profil IA", "Matching emplois", "Formations personnalisées"]
    },
    {
      id: "entreprise",
      title: "Entreprise / RH",
      description: "Recrutez les meilleurs talents et optimisez vos processus",
      icon: Building2,
      color: "emerald",
      features: ["Gestion des offres", "Candidats compatibles", "Tableau de bord RH"]
    },
    {
      id: "partenaire",
      title: "Partenaire Social",
      description: "Accompagnez vos bénéficiaires vers l'emploi durable",
      icon: Handshake,
      color: "violet",
      features: ["Suivi bénéficiaires", "Prescriptions", "Observations territoriales"]
    }
  ];

  const features = [
    {
      icon: Target,
      title: "Matching Intelligent",
      description: "Notre IA analyse vos compétences pour vous proposer les opportunités les plus pertinentes."
    },
    {
      icon: BookOpen,
      title: "Formations Adaptées",
      description: "Des parcours d'apprentissage personnalisés pour combler vos lacunes et renforcer vos atouts."
    },
    {
      icon: TrendingUp,
      title: "Progression Mesurable",
      description: "Suivez votre évolution avec des indicateurs clairs et des objectifs atteignables."
    },
    {
      icon: Shield,
      title: "Connexion Anonyme",
      description: "Accédez à la plateforme en toute confidentialité, sans création de compte obligatoire."
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 glass border-b border-slate-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-blue-500 flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>
                Ré'Actif Pro
              </span>
            </div>
            <Badge variant="secondary" className="bg-blue-50 text-blue-700 border-blue-200">
              Plateforme Carrière
            </Badge>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 gradient-hero">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-3xl mx-auto mb-16 animate-fade-in">
            <Badge className="mb-6 bg-blue-100 text-blue-700 border-blue-200 px-4 py-1">
              <Sparkles className="w-3 h-3 mr-1" />
              Propulsé par l'Intelligence Artificielle
            </Badge>
            <h1 className="heading-1 text-slate-900 mb-6">
              Votre carrière,{" "}
              <span className="gradient-text">réinventée</span>
            </h1>
            <p className="text-lg text-slate-600 leading-relaxed">
              Ré'Actif Pro connecte talents, entreprises et partenaires sociaux pour créer 
              des opportunités professionnelles durables grâce à l'intelligence artificielle.
            </p>
          </div>

          {/* Role Selection Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto stagger-children" data-testid="role-selection">
            {roles.map((role) => {
              const Icon = role.icon;
              const isSelected = selectedRole === role.id;
              const colorClasses = {
                blue: "border-blue-300 bg-blue-50/50",
                emerald: "border-emerald-300 bg-emerald-50/50",
                violet: "border-violet-300 bg-violet-50/50"
              };
              const iconColorClasses = {
                blue: "bg-blue-100 text-blue-600",
                emerald: "bg-emerald-100 text-emerald-600",
                violet: "bg-violet-100 text-violet-600"
              };
              
              return (
                <Card 
                  key={role.id}
                  data-testid={`role-card-${role.id}`}
                  className={`card-interactive cursor-pointer ${isSelected ? colorClasses[role.color] : ""}`}
                  onClick={() => !isLoading && handleRoleSelect(role.id)}
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
                  <CardContent>
                    <ul className="space-y-2 mb-6">
                      {role.features.map((feature, idx) => (
                        <li key={idx} className="flex items-center gap-2 text-sm text-slate-600">
                          <CheckCircle2 className="w-4 h-4 text-green-500 flex-shrink-0" />
                          {feature}
                        </li>
                      ))}
                    </ul>
                    <Button 
                      className="w-full btn-primary group"
                      disabled={isLoading && selectedRole === role.id}
                      data-testid={`login-btn-${role.id}`}
                    >
                      {isLoading && selectedRole === role.id ? (
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      ) : (
                        <>
                          Commencer
                          <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                        </>
                      )}
                    </Button>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 bg-slate-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="heading-2 text-slate-900 mb-4">
              Une plateforme complète
            </h2>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              Tous les outils nécessaires pour développer votre carrière, recruter les meilleurs talents 
              ou accompagner vos bénéficiaires.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, idx) => {
              const Icon = feature.icon;
              return (
                <Card key={idx} className="card-base p-6 card-hover" data-testid={`feature-card-${idx}`}>
                  <div className="w-12 h-12 rounded-xl bg-blue-100 text-blue-600 flex items-center justify-center mb-4">
                    <Icon className="w-6 h-6" />
                  </div>
                  <h3 className="text-lg font-semibold text-slate-900 mb-2" style={{ fontFamily: 'Outfit, sans-serif' }}>
                    {feature.title}
                  </h3>
                  <p className="text-sm text-slate-600">
                    {feature.description}
                  </p>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <Card className="p-12 bg-gradient-to-br from-blue-600 to-blue-700 border-0">
            <h2 className="text-3xl font-bold text-white mb-4" style={{ fontFamily: 'Outfit, sans-serif' }}>
              Prêt à démarrer ?
            </h2>
            <p className="text-blue-100 mb-8 text-lg">
              Rejoignez des milliers d'utilisateurs qui ont déjà transformé leur parcours professionnel.
            </p>
            <Button 
              size="lg"
              className="bg-white text-blue-600 hover:bg-blue-50 font-semibold px-8"
              onClick={() => handleRoleSelect("particulier")}
              data-testid="cta-start-btn"
            >
              Accéder à la plateforme
              <ChevronRight className="w-5 h-5 ml-2" />
            </Button>
          </Card>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 border-t border-slate-100">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <span className="font-semibold text-slate-900">Ré'Actif Pro</span>
          </div>
          <p className="text-sm text-slate-500">
            © 2026 Ré'Actif Pro - Plateforme de développement de carrière
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
