import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";
import {
  Users,
  Building2,
  Handshake,
  ArrowRight,
  Target,
  Compass,
  Heart,
  Shield,
  Globe,
  Smartphone,
  CreditCard,
  GraduationCap,
  BarChart3,
  Sparkles,
  CheckCircle2,
  ChevronRight,
  Brain,
  Lightbulb,
  Network,
  Eye,
  Lock,
  TrendingUp,
  MapPin,
  Calendar,
  FileText,
  Zap,
  Users2,
  Award,
  Leaf,
  Infinity,
  HeartHandshake,
  Menu,
  X,
  ChevronDown
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// ============== NAVIGATION HEADER ==============
const NavHeader = () => {
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [presentationOpen, setPresentationOpen] = useState(false);

  return (
    <nav className="bg-white/95 backdrop-blur-md border-b border-stone-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/reactif" className="flex items-center gap-2">
            <span className="text-xl font-bold text-[#1C1917]" style={{ fontFamily: 'Fraunces, serif' }}>
              RE'ACTIF <span className="text-teal-600">PRO</span>
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-8">
            {/* Présentation dropdown */}
            <div className="relative">
              <button
                onClick={() => setPresentationOpen(!presentationOpen)}
                onBlur={() => setTimeout(() => setPresentationOpen(false), 200)}
                className="flex items-center gap-1 text-[#57534E] hover:text-[#1C1917] transition-colors font-medium"
              >
                Présentation
                <ChevronDown className={`w-4 h-4 transition-transform ${presentationOpen ? 'rotate-180' : ''}`} />
              </button>
              {presentationOpen && (
                <div className="absolute top-full left-0 mt-2 w-48 bg-white rounded-xl shadow-lg border border-stone-200 py-2 animate-fade-in-up">
                  <Link
                    to="/reactif"
                    className="block px-4 py-2 text-sm text-[#57534E] hover:bg-teal-50 hover:text-teal-700"
                  >
                    À propos
                  </Link>
                  <Link
                    to="/reactif/membres"
                    className="block px-4 py-2 text-sm text-[#57534E] hover:bg-teal-50 hover:text-teal-700"
                  >
                    Nos membres
                  </Link>
                </div>
              )}
            </div>

            <Link to="/reactif/accueil" className="text-[#57534E] hover:text-[#1C1917] transition-colors font-medium">
              Dispositif
            </Link>
            <Link to="/reactif/partenaires" className="text-[#57534E] hover:text-[#1C1917] transition-colors font-medium">
              Partenaires
            </Link>
            <Link to="/" className="text-[#57534E] hover:text-[#1C1917] transition-colors font-medium">
              VSI
            </Link>
            
            <Button
              onClick={() => navigate("/reactif/accueil")}
              className="bg-teal-600 hover:bg-teal-700 text-white rounded-full px-6"
            >
              Accéder
            </Button>
          </div>

          {/* Mobile menu button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 text-[#57534E]"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-stone-200 animate-fade-in-up">
            <div className="space-y-2">
              <p className="px-2 text-xs text-[#A8A29E] uppercase tracking-wider">Présentation</p>
              <Link
                to="/reactif"
                className="block px-4 py-2 text-[#57534E] hover:bg-teal-50 rounded-lg"
                onClick={() => setMobileMenuOpen(false)}
              >
                À propos
              </Link>
              <Link
                to="/reactif/membres"
                className="block px-4 py-2 text-[#57534E] hover:bg-teal-50 rounded-lg"
                onClick={() => setMobileMenuOpen(false)}
              >
                Nos membres
              </Link>
              <hr className="my-2 border-stone-200" />
              <Link
                to="/reactif/accueil"
                className="block px-4 py-2 text-[#57534E] hover:bg-teal-50 rounded-lg"
                onClick={() => setMobileMenuOpen(false)}
              >
                Dispositif
              </Link>
              <Link
                to="/reactif/partenaires"
                className="block px-4 py-2 text-[#57534E] hover:bg-teal-50 rounded-lg"
                onClick={() => setMobileMenuOpen(false)}
              >
                Partenaires
              </Link>
              <Link
                to="/"
                className="block px-4 py-2 text-[#57534E] hover:bg-teal-50 rounded-lg"
                onClick={() => setMobileMenuOpen(false)}
              >
                VSI
              </Link>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

// ============== PAGE D'ACCUEIL INSTITUTIONNELLE ==============
export const ReactifLanding = () => {
  const navigate = useNavigate();
  const [impact, setImpact] = useState(null);

  useEffect(() => {
    fetchImpact();
  }, []);

  const fetchImpact = async () => {
    try {
      const response = await axios.get(`${API}/reactif/impact`);
      setImpact(response.data);
    } catch (error) {
      console.error("Error fetching impact stats");
    }
  };

  return (
    <div className="min-h-screen bg-[#FAFAF9]" data-testid="reactif-landing">
      
      {/* ============== HERO SECTION ============== */}
      <section className="relative overflow-hidden bg-gradient-to-br from-teal-900 via-teal-800 to-emerald-900 text-white">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 left-10 w-72 h-72 bg-amber-400 rounded-full blur-3xl" />
          <div className="absolute bottom-20 right-10 w-96 h-96 bg-teal-400 rounded-full blur-3xl" />
        </div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-32">
          <div className="text-center">
            <Badge className="mb-6 bg-white/20 text-white hover:bg-white/30 text-sm px-4 py-1">
              <MapPin className="w-4 h-4 mr-2" />
              Grand Est • Dispositif territorial
            </Badge>
            
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold mb-6 tracking-tight" style={{ fontFamily: 'Fraunces, serif' }}>
              RE'ACTIF <span className="text-amber-400">PRO</span>
            </h1>
            
            <p className="text-xl md:text-2xl text-teal-100 max-w-4xl mx-auto mb-4 leading-relaxed">
              Un dispositif territorial pour une <strong className="text-white">insertion professionnelle durable</strong>
            </p>
            
            <p className="text-lg text-teal-200 max-w-3xl mx-auto mb-10">
              Porté par <strong className="text-amber-300">ALT&ACT</strong> — L'insertion sans barrières
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button 
                onClick={() => navigate("/reactif/accueil")}
                className="bg-amber-500 hover:bg-amber-600 text-white rounded-full px-8 py-6 text-lg"
              >
                Découvrir le dispositif <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
              <Button 
                onClick={() => navigate("/")}
                variant="outline"
                className="border-white/30 text-white hover:bg-white/10 rounded-full px-8 py-6 text-lg"
              >
                Commencer avec VSI
              </Button>
            </div>
          </div>
        </div>

        {/* Wave separator */}
        <div className="absolute bottom-0 left-0 right-0">
          <svg viewBox="0 0 1440 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M0 50L60 45C120 40 240 30 360 35C480 40 600 60 720 65C840 70 960 60 1080 50C1200 40 1320 30 1380 25L1440 20V100H1380C1320 100 1200 100 1080 100C960 100 840 100 720 100C600 100 480 100 360 100C240 100 120 100 60 100H0V50Z" fill="#FAFAF9"/>
          </svg>
        </div>
      </section>

      {/* ============== VISION - CONTRIBUTEURS SOCIÉTAUX ============== */}
      <section className="py-20 bg-[#FAFAF9]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <Badge className="mb-4 bg-amber-100 text-amber-800">Notre vision</Badge>
            <h2 className="text-3xl md:text-4xl font-bold text-[#1C1917] mb-6" style={{ fontFamily: 'Fraunces, serif' }}>
              Nous sommes tous des <span className="text-teal-600">contributeurs sociétaux</span>
            </h2>
            <p className="text-lg text-[#57534E] max-w-3xl mx-auto">
              RE'ACTIF PRO est une plateforme d'apprentissage tout au long de la vie qui révolutionne 
              l'approche traditionnelle de l'insertion professionnelle en plaçant <strong>l'humain au cœur du processus</strong>.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <Card className="vsi-card text-center border-t-4 border-t-teal-500">
              <CardContent className="pt-8">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-teal-100 flex items-center justify-center">
                  <HeartHandshake className="w-8 h-8 text-teal-600" />
                </div>
                <h3 className="text-xl font-semibold mb-2" style={{ fontFamily: 'Fraunces, serif' }}>
                  L'humain d'abord
                </h3>
                <p className="text-[#57534E]">
                  Valoriser les talents cachés et les potentiels inexploités des chercheurs d'emploi
                </p>
              </CardContent>
            </Card>

            <Card className="vsi-card text-center border-t-4 border-t-amber-500">
              <CardContent className="pt-8">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-amber-100 flex items-center justify-center">
                  <Infinity className="w-8 h-8 text-amber-600" />
                </div>
                <h3 className="text-xl font-semibold mb-2" style={{ fontFamily: 'Fraunces, serif' }}>
                  Apprentissage continu
                </h3>
                <p className="text-[#57534E]">
                  Une plateforme d'apprentissage tout au long de la vie, adaptée aux réalités d'aujourd'hui
                </p>
              </CardContent>
            </Card>

            <Card className="vsi-card text-center border-t-4 border-t-purple-500">
              <CardContent className="pt-8">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-purple-100 flex items-center justify-center">
                  <Globe className="w-8 h-8 text-purple-600" />
                </div>
                <h3 className="text-xl font-semibold mb-2" style={{ fontFamily: 'Fraunces, serif' }}>
                  Impact territorial
                </h3>
                <p className="text-[#57534E]">
                  Fédérer l'ensemble des acteurs locaux autour d'une ambition commune
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* ============== INTRODUCTION ============== */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <Badge className="mb-4 bg-teal-100 text-teal-800">Introduction</Badge>
              <h2 className="text-3xl md:text-4xl font-bold text-[#1C1917] mb-6" style={{ fontFamily: 'Fraunces, serif' }}>
                Transformer l'accompagnement vers l'emploi
              </h2>
              <p className="text-lg text-[#57534E] mb-6 leading-relaxed">
                Face aux défis d'un marché du travail en perpétuelle mutation, nous avons conçu une 
                <strong> réponse territoriale ambitieuse et novatrice</strong>.
              </p>
              <p className="text-[#57534E] mb-6">
                Dans un contexte où les <strong>compétences priment désormais sur les diplômes</strong>, 
                RE'ACTIF PRO révolutionne l'approche traditionnelle de l'insertion professionnelle.
              </p>
              <div className="bg-gradient-to-r from-teal-50 to-amber-50 p-6 rounded-xl border-l-4 border-l-teal-500">
                <p className="text-[#1C1917] italic">
                  "Plus qu'un simple accompagnement, RE'ACTIF PRO propose un parcours personnalisé 
                  qui fédère l'ensemble des acteurs locaux autour d'une ambition commune : 
                  <strong> construire des parcours d'insertion durables</strong>."
                </p>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-teal-50 p-6 rounded-2xl">
                <Target className="w-10 h-10 text-teal-600 mb-3" />
                <h4 className="font-semibold text-[#1C1917]">Mission claire</h4>
                <p className="text-sm text-[#57534E]">Insertion durable et adaptée</p>
              </div>
              <div className="bg-amber-50 p-6 rounded-2xl">
                <Users2 className="w-10 h-10 text-amber-600 mb-3" />
                <h4 className="font-semibold text-[#1C1917]">Approche humaine</h4>
                <p className="text-sm text-[#57534E]">L'individu au centre</p>
              </div>
              <div className="bg-purple-50 p-6 rounded-2xl">
                <Network className="w-10 h-10 text-purple-600 mb-3" />
                <h4 className="font-semibold text-[#1C1917]">Réseau territorial</h4>
                <p className="text-sm text-[#57534E]">Acteurs fédérés</p>
              </div>
              <div className="bg-green-50 p-6 rounded-2xl">
                <TrendingUp className="w-10 h-10 text-green-600 mb-3" />
                <h4 className="font-semibold text-[#1C1917]">Innovation</h4>
                <p className="text-sm text-[#57534E]">Technologie & éthique</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ============== AMBITIONS ============== */}
      <section className="py-20 bg-gradient-to-br from-teal-50 via-white to-amber-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <Badge className="mb-4 bg-purple-100 text-purple-800">Ambitions stratégiques</Badge>
            <h2 className="text-3xl md:text-4xl font-bold text-[#1C1917] mb-4" style={{ fontFamily: 'Fraunces, serif' }}>
              Cinq dimensions d'impact durable
            </h2>
            <p className="text-lg text-[#57534E] max-w-2xl mx-auto">
              En parfaite cohérence avec la philosophie d'ALT&ACT
            </p>
          </div>

          <div className="grid md:grid-cols-5 gap-6">
            {[
              { icon: Briefcase, title: "Insertion pérenne", desc: "Au-delà du simple placement, construire les conditions d'une intégration durable", color: "teal" },
              { icon: Heart, title: "Reconnaissance", desc: "Valorisation des identités professionnelles et personnelles", color: "pink" },
              { icon: Brain, title: "Développement", desc: "Mise en lumière des soft skills, vertus et valeurs universelles", color: "purple" },
              { icon: Globe, title: "Accessibilité", desc: "Accompagnement hybride : proximité humaine + agilité numérique", color: "amber" },
              { icon: Zap, title: "Simplification", desc: "Interface fluide avec France Travail pour une actualisation sans friction", color: "green" }
            ].map((item, idx) => {
              const Icon = item.icon;
              const colorClasses = {
                teal: "bg-teal-100 text-teal-600 border-teal-200",
                pink: "bg-pink-100 text-pink-600 border-pink-200",
                purple: "bg-purple-100 text-purple-600 border-purple-200",
                amber: "bg-amber-100 text-amber-600 border-amber-200",
                green: "bg-green-100 text-green-600 border-green-200"
              };
              return (
                <div key={idx} className={`p-6 rounded-2xl border-2 ${colorClasses[item.color]} text-center`}>
                  <Icon className="w-10 h-10 mx-auto mb-3" />
                  <h4 className="font-semibold text-[#1C1917] mb-2">{item.title}</h4>
                  <p className="text-sm text-[#57534E]">{item.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ============== PUBLICS ============== */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <Badge className="mb-4 bg-teal-100 text-teal-800">Nos publics</Badge>
            <h2 className="text-3xl md:text-4xl font-bold text-[#1C1917] mb-4" style={{ fontFamily: 'Fraunces, serif' }}>
              Au cœur du dispositif
            </h2>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            {[
              { icon: Users, title: "Demandeurs d'emploi", desc: "Accompagnement structuré pour valoriser l'existant et révéler les potentiels" },
              { icon: GraduationCap, title: "Jeunes en quête de sens", desc: "Éclairage précieux pour les parcours d'orientation (Parcoursup)" },
              { icon: TrendingUp, title: "Professionnels en transition", desc: "Soutien stratégique pour reconversion ou évolution de carrière" },
              { icon: Award, title: "Accompagnateurs", desc: "Outil innovant enrichissant la pratique des conseillers et formateurs" }
            ].map((item, idx) => {
              const Icon = item.icon;
              return (
                <Card key={idx} className="vsi-card hover:border-teal-300">
                  <CardContent className="pt-6">
                    <div className="w-12 h-12 rounded-full bg-teal-100 flex items-center justify-center mb-4">
                      <Icon className="w-6 h-6 text-teal-600" />
                    </div>
                    <h4 className="font-semibold text-[#1C1917] mb-2">{item.title}</h4>
                    <p className="text-sm text-[#57534E]">{item.desc}</p>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          {/* Publics vulnérables */}
          <div className="bg-gradient-to-r from-amber-50 to-teal-50 p-8 rounded-2xl">
            <h3 className="text-xl font-semibold text-[#1C1917] mb-4 text-center" style={{ fontFamily: 'Fraunces, serif' }}>
              Attention particulière aux publics vulnérables
            </h3>
            <p className="text-center text-[#57534E] mb-6">
              En cohérence avec la mission d'ALT&ACT — L'insertion sans barrières
            </p>
            <div className="flex flex-wrap justify-center gap-3">
              {["Demandeurs d'emploi longue durée", "Jeunes NEET", "Réfugiés & migrants", 
                "Personnes en situation de handicap", "Victimes de discriminations"].map((public_, idx) => (
                <Badge key={idx} variant="secondary" className="bg-white text-[#57534E] py-2 px-4">
                  {public_}
                </Badge>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ============== ARCHITECTURE DU DISPOSITIF ============== */}
      <section className="py-20 bg-gradient-to-b from-teal-900 to-teal-800 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <Badge className="mb-4 bg-white/20 text-white">Architecture innovante</Badge>
            <h2 className="text-3xl md:text-4xl font-bold mb-4" style={{ fontFamily: 'Fraunces, serif' }}>
              Trois piliers complémentaires
            </h2>
            <p className="text-teal-200 max-w-2xl mx-auto">
              Un écosystème cohérent d'accompagnement
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Pilier 1 - Apply VSI PRO */}
            <Card className="bg-white/10 backdrop-blur border-white/20 text-white">
              <CardHeader>
                <div className="w-14 h-14 rounded-2xl bg-amber-500 flex items-center justify-center mb-4">
                  <Smartphone className="w-7 h-7 text-white" />
                </div>
                <CardTitle className="text-white">Apply VSI PRO</CardTitle>
                <CardDescription className="text-teal-200">Application mobile/web</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {["Interface intuitive", "Analyse multidimensionnelle", "CV dynamique interactif",
                  "Matching intelligent", "Agenda intégré", "Recommandations personnalisées"].map((item, idx) => (
                  <div key={idx} className="flex items-center gap-2 text-sm">
                    <CheckCircle2 className="w-4 h-4 text-amber-400 flex-shrink-0" />
                    <span className="text-teal-100">{item}</span>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Pilier 2 - Carte Emploi */}
            <Card className="bg-white/10 backdrop-blur border-white/20 text-white">
              <CardHeader>
                <div className="w-14 h-14 rounded-2xl bg-purple-500 flex items-center justify-center mb-4">
                  <CreditCard className="w-7 h-7 text-white" />
                </div>
                <CardTitle className="text-white">Carte Emploi</CardTitle>
                <CardDescription className="text-teal-200">RE'ACTIF PRO</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {["Écran e-paper & puce de mise à jour", "Statut actualisé en temps réel",
                  "QR code multifonction", "Accès France Travail", "Profil compétences paramétrable",
                  "Symbole d'appartenance"].map((item, idx) => (
                  <div key={idx} className="flex items-center gap-2 text-sm">
                    <CheckCircle2 className="w-4 h-4 text-purple-400 flex-shrink-0" />
                    <span className="text-teal-100">{item}</span>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Pilier 3 - Parcours VSI */}
            <Card className="bg-white/10 backdrop-blur border-white/20 text-white">
              <CardHeader>
                <div className="w-14 h-14 rounded-2xl bg-teal-500 flex items-center justify-center mb-4">
                  <GraduationCap className="w-7 h-7 text-white" />
                </div>
                <CardTitle className="text-white">Parcours VSI</CardTitle>
                <CardDescription className="text-teal-200">Valoriser son Identité</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {["Modules hybrides (vidéo + outils)", "Chat d'accompagnement",
                  "Validation progressive soft skills", "6 vertus de Seligman",
                  "Valeurs de Schwartz", "Unité dans la diversité"].map((item, idx) => (
                  <div key={idx} className="flex items-center gap-2 text-sm">
                    <CheckCircle2 className="w-4 h-4 text-teal-400 flex-shrink-0" />
                    <span className="text-teal-100">{item}</span>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          <div className="mt-12 text-center">
            <div className="bg-white/10 backdrop-blur rounded-2xl p-6 max-w-3xl mx-auto border border-white/20">
              <p className="text-lg text-teal-100 italic">
                "Notre parcours VSI incarne la conviction fondamentale d'ALT&ACT : 
                <strong className="text-white"> révéler les potentiels invisibles</strong> et 
                transformer les parcours de vie en atouts professionnels."
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ============== OBSERVATOIRE PRÉDICTIF ============== */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <Badge className="mb-4 bg-purple-100 text-purple-800">Innovation majeure</Badge>
              <h2 className="text-3xl md:text-4xl font-bold text-[#1C1917] mb-6" style={{ fontFamily: 'Fraunces, serif' }}>
                Observatoire prédictif des compétences
              </h2>
              <p className="text-lg text-[#57534E] mb-6">
                Un dispositif vivant d'anticipation et de sécurisation des parcours professionnels, centré sur l'humain.
              </p>
              
              <div className="space-y-4">
                {[
                  { icon: Eye, title: "Anticiper", desc: "Évolutions des métiers et compétences transversales" },
                  { icon: Lightbulb, title: "Rendre visibles", desc: "Compétences réelles, y compris non reconnues par les diplômes" },
                  { icon: Shield, title: "Réduire", desc: "Les ruptures professionnelles et inadéquations" },
                  { icon: Compass, title: "Éclairer", desc: "Les décisions d'orientation sans jamais les prescrire" }
                ].map((item, idx) => {
                  const Icon = item.icon;
                  return (
                    <div key={idx} className="flex items-start gap-4">
                      <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center flex-shrink-0">
                        <Icon className="w-5 h-5 text-purple-600" />
                      </div>
                      <div>
                        <h4 className="font-semibold text-[#1C1917]">{item.title}</h4>
                        <p className="text-sm text-[#57534E]">{item.desc}</p>
                      </div>
                    </div>
                  );
                })}
              </div>

              <div className="mt-8 p-4 bg-amber-50 rounded-xl border-l-4 border-l-amber-500">
                <p className="text-[#1C1917] font-medium">
                  Logique centrale : <span className="text-amber-700">observer pour éclairer, jamais pour enfermer.</span>
                </p>
              </div>
            </div>

            <div className="space-y-6">
              <Card className="vsi-card border-l-4 border-l-purple-500">
                <CardHeader>
                  <CardTitle className="text-lg">Approche prédictive co-construite</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2 text-sm text-[#57534E]">
                    <li className="flex items-start gap-2">
                      <ChevronRight className="w-4 h-4 text-purple-500 mt-0.5" />
                      Prédictif mais pas descendant
                    </li>
                    <li className="flex items-start gap-2">
                      <ChevronRight className="w-4 h-4 text-purple-500 mt-0.5" />
                      Basé sur la donnée, ancré dans l'expérience vécue
                    </li>
                    <li className="flex items-start gap-2">
                      <ChevronRight className="w-4 h-4 text-purple-500 mt-0.5" />
                      Technologique mais piloté par une gouvernance éthique
                    </li>
                  </ul>
                </CardContent>
              </Card>

              <Card className="vsi-card border-l-4 border-l-teal-500">
                <CardHeader>
                  <CardTitle className="text-lg">Gouvernance éthique</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2 text-sm text-[#57534E]">
                    <li className="flex items-start gap-2">
                      <Lock className="w-4 h-4 text-teal-500 mt-0.5" />
                      Pilotage structuré via ALT&ACT
                    </li>
                    <li className="flex items-start gap-2">
                      <Lock className="w-4 h-4 text-teal-500 mt-0.5" />
                      IA non discriminante, non prescriptive, explicable
                    </li>
                    <li className="flex items-start gap-2">
                      <Lock className="w-4 h-4 text-teal-500 mt-0.5" />
                      La donnée sert le parcours, jamais l'inverse
                    </li>
                  </ul>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* ============== INDICATEURS D'IMPACT ============== */}
      <section className="py-20 bg-gradient-to-br from-amber-50 via-white to-teal-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <Badge className="mb-4 bg-green-100 text-green-800">Impact mesuré</Badge>
            <h2 className="text-3xl md:text-4xl font-bold text-[#1C1917] mb-4" style={{ fontFamily: 'Fraunces, serif' }}>
              Au-delà du simple retour à l'emploi
            </h2>
            <p className="text-[#57534E] max-w-2xl mx-auto">
              L'impact est qualitatif autant que quantitatif
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-12">
            {[
              { label: "Clarification projet", value: impact?.taux_clarification || 87, color: "teal" },
              { label: "Mise en action 30j", value: impact?.taux_mise_en_action_30j || 72, color: "amber" },
              { label: "Progression posture", value: impact?.progression_posture || 65, color: "purple" },
              { label: "Satisfaction", value: impact?.satisfaction || 92, color: "green" },
              { label: "Autonomie décisionnelle", value: 78, color: "blue" },
              { label: "Projection durable", value: 84, color: "pink" }
            ].map((stat, idx) => {
              const colorClasses = {
                teal: "text-teal-600",
                amber: "text-amber-600",
                purple: "text-purple-600",
                green: "text-green-600",
                blue: "text-blue-600",
                pink: "text-pink-600"
              };
              return (
                <Card key={idx} className="text-center p-4">
                  <div className={`text-3xl md:text-4xl font-bold ${colorClasses[stat.color]}`}>
                    {stat.value}%
                  </div>
                  <div className="text-xs text-[#57534E] mt-1">{stat.label}</div>
                </Card>
              );
            })}
          </div>

          <div className="bg-white rounded-2xl p-8 shadow-lg">
            <h3 className="text-xl font-semibold text-center mb-6" style={{ fontFamily: 'Fraunces, serif' }}>
              Indicateurs suivis
            </h3>
            <div className="grid md:grid-cols-3 gap-6">
              {[
                "Retour à l'emploi ou en formation",
                "Cohérence identité / activité",
                "Autonomie décisionnelle",
                "Progression des soft skills",
                "Satisfaction méthode d'accompagnement",
                "Capacité à se projeter durablement"
              ].map((indicator, idx) => (
                <div key={idx} className="flex items-center gap-3">
                  <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0" />
                  <span className="text-[#57534E]">{indicator}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ============== CTA FINAL ============== */}
      <section className="py-20 bg-gradient-to-r from-teal-600 to-emerald-600 text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6" style={{ fontFamily: 'Fraunces, serif' }}>
            Rejoignez le mouvement RE'ACTIF PRO
          </h2>
          <p className="text-xl text-teal-100 mb-10">
            Ensemble, construisons des parcours d'insertion durables et adaptés aux réalités du Grand Est
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button 
              onClick={() => navigate("/reactif/accueil")}
              className="bg-white text-teal-700 hover:bg-teal-50 rounded-full px-8 py-6 text-lg"
            >
              <Users className="w-5 h-5 mr-2" />
              Accéder au dispositif
            </Button>
            <Button 
              onClick={() => navigate("/reactif/partenaires")}
              variant="outline"
              className="border-white text-white hover:bg-white/10 rounded-full px-8 py-6 text-lg"
            >
              <Handshake className="w-5 h-5 mr-2" />
              Devenir partenaire
            </Button>
          </div>
        </div>
      </section>

      {/* ============== FOOTER ============== */}
      <footer className="bg-[#1C1917] text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-xl font-bold mb-4" style={{ fontFamily: 'Fraunces, serif' }}>
                RE'ACTIF <span className="text-amber-400">PRO</span>
              </h3>
              <p className="text-stone-400 text-sm">
                Un dispositif territorial pour une insertion professionnelle durable en Grand Est
              </p>
              <p className="text-stone-500 text-sm mt-2">
                Porté par ALT&ACT
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Le dispositif</h4>
              <ul className="space-y-2 text-stone-400 text-sm">
                <li><a href="/reactif/accueil" className="hover:text-white transition-colors">Accueil</a></li>
                <li><a href="/reactif/particuliers" className="hover:text-white transition-colors">Particuliers</a></li>
                <li><a href="/reactif/services-rh" className="hover:text-white transition-colors">Services RH</a></li>
                <li><a href="/reactif/partenaires" className="hover:text-white transition-colors">Partenaires</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Présentation</h4>
              <ul className="space-y-2 text-stone-400 text-sm">
                <li><a href="/reactif" className="hover:text-white transition-colors">À propos</a></li>
                <li><a href="/reactif/membres" className="hover:text-white transition-colors">Nos membres</a></li>
                <li><a href="/reactif/partenaires" className="hover:text-white transition-colors">Observatoire</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Outils</h4>
              <ul className="space-y-2 text-stone-400 text-sm">
                <li><a href="/" className="hover:text-white transition-colors">VSI - Diagnostic</a></li>
                <li><a href="/reactif/accueil" className="hover:text-white transition-colors">Apply VSI PRO</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Contact</h4>
              <ul className="space-y-2 text-stone-400 text-sm">
                <li>Grand Est, France</li>
                <li>contact@reactifpro.fr</li>
              </ul>
            </div>
          </div>
          <div className="border-t border-stone-800 mt-8 pt-8 text-center text-stone-500 text-sm">
            © 2026 RE'ACTIF PRO — ALT&ACT. Tous droits réservés.
          </div>
        </div>
      </footer>
    </div>
  );
};

// Import Briefcase for ambitions section
const Briefcase = ({ className }) => (
  <svg className={className} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect width="20" height="14" x="2" y="7" rx="2" ry="2"/>
    <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
  </svg>
);

export default ReactifLanding;
