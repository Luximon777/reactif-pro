import { Link } from "react-router-dom";
import { Sparkles, Heart, TrendingUp, Briefcase, ChevronRight, CheckCircle } from "lucide-react";

export const HomePage = () => {
  const features = [
    { icon: <Sparkles className="w-6 h-6" />, label: "Soft Skills", color: "from-blue-500 to-cyan-400" },
    { icon: <Heart className="w-6 h-6" />, label: "Valeurs", color: "from-pink-500 to-rose-400" },
    { icon: <TrendingUp className="w-6 h-6" />, label: "Potentiel", color: "from-purple-500 to-violet-400" },
    { icon: <Briefcase className="w-6 h-6" />, label: "Métiers", color: "from-amber-500 to-orange-400" },
  ];

  const steps = [
    {
      number: 1,
      title: "Questionnaire",
      description: "Répondez à des questions sur vos préférences, valeurs et comportements"
    },
    {
      number: 2,
      title: "Analyse",
      description: "Notre algorithme analyse vos réponses pour identifier vos forces"
    },
    {
      number: 3,
      title: "Carte d'identité Pro",
      description: "Découvrez votre profil complet : soft skills, valeurs, potentiel"
    },
    {
      number: 4,
      title: "Matching Métiers",
      description: "Explorez les métiers compatibles avec votre profil"
    }
  ];

  return (
    <div className="min-h-screen hero-bg" data-testid="home-page">
      {/* Floating Elements */}
      <div className="floating-element w-32 h-32 bg-purple-500/20 blur-3xl top-20 left-10" />
      <div className="floating-element w-48 h-48 bg-blue-500/20 blur-3xl top-40 right-20" />
      <div className="floating-element w-24 h-24 bg-pink-500/20 blur-3xl bottom-40 left-1/4" />

      {/* Hero Section */}
      <section className="relative z-10 px-6 pt-20 pb-16 max-w-6xl mx-auto">
        <div className="text-center space-y-8 animate-fade-in-up">
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight">
            <span className="gradient-text">DE'CLIC PRO</span>
            <br />
            <span className="text-white/90 text-3xl md:text-4xl font-medium mt-4 block">
              Découvrez votre potentiel professionnel
            </span>
          </h1>
          
          <p className="text-lg md:text-xl text-white/60 max-w-2xl mx-auto leading-relaxed">
            Un parcours personnalisé pour identifier vos soft skills, vos valeurs et les métiers qui vous correspondent.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
            <Link 
              to="/questionnaire" 
              className="btn-primary px-8 py-4 rounded-full font-semibold text-white inline-flex items-center justify-center gap-2"
              data-testid="start-questionnaire-btn"
            >
              Commencer le questionnaire
              <ChevronRight className="w-5 h-5" />
            </Link>
            <Link 
              to="/carte-identite" 
              className="btn-secondary px-8 py-4 rounded-full font-semibold text-white inline-flex items-center justify-center gap-2"
              data-testid="view-identity-card-btn"
            >
              Voir ma carte d'identité Pro
            </Link>
          </div>
        </div>

        {/* Feature Pills */}
        <div className="flex flex-wrap justify-center gap-4 mt-16" data-testid="feature-pills">
          {features.map((feature, index) => (
            <div 
              key={index}
              className="glass px-6 py-3 rounded-full flex items-center gap-3 card-hover"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className={`p-2 rounded-lg bg-gradient-to-br ${feature.color}`}>
                {feature.icon}
              </div>
              <span className="font-medium text-white/90">{feature.label}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Steps Section */}
      <section className="relative z-10 px-6 py-20 max-w-4xl mx-auto" data-testid="steps-section">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-16">
          <span className="gradient-text">Votre parcours</span> en 4 étapes
        </h2>

        <div className="space-y-8">
          {steps.map((step, index) => (
            <div 
              key={step.number}
              className="glass rounded-2xl p-6 flex items-start gap-6 card-hover relative"
              style={{ animationDelay: `${index * 0.15}s` }}
              data-testid={`step-${step.number}`}
            >
              {index < steps.length - 1 && <div className="step-line" />}
              
              <div className="step-number">
                {step.number}
              </div>
              
              <div className="flex-1">
                <h3 className="text-xl font-semibold text-white mb-2">{step.title}</h3>
                <p className="text-white/60">{step.description}</p>
              </div>
              
              <CheckCircle className="w-6 h-6 text-white/20" />
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative z-10 px-6 py-20 max-w-4xl mx-auto text-center" data-testid="cta-section">
        <div className="glass rounded-3xl p-12 animate-pulse-glow">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Prêt à découvrir votre potentiel ?
          </h2>
          <p className="text-white/60 text-lg mb-8">
            Le questionnaire prend environ 15 minutes. Vos réponses sont confidentielles.
          </p>
          <Link 
            to="/questionnaire" 
            className="btn-primary px-10 py-4 rounded-full font-semibold text-white inline-flex items-center justify-center gap-2 text-lg"
            data-testid="cta-start-btn"
          >
            Démarrer maintenant
            <ChevronRight className="w-5 h-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 px-6 py-8 text-center text-white/40 text-sm">
        <p>© 2026 DE'CLIC PRO - Intelligence Professionnelle</p>
      </footer>
    </div>
  );
};
