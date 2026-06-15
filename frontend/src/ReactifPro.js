import { useState, useEffect } from "react";
import { useNavigate, useParams, useLocation } from "react-router-dom";
import axios from "axios";
import { toast } from "sonner";
import {
  Users,
  Building2,
  Handshake,
  ArrowRight,
  ArrowLeft,
  Check,
  Target,
  Compass,
  TrendingUp,
  Calendar,
  FileText,
  Send,
  Loader2,
  ChevronRight,
  Star,
  Brain,
  Heart,
  Shield,
  Sun,
  Briefcase,
  Clock,
  CheckCircle2,
  Circle,
  BarChart3,
  Award,
  Sparkles
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Progress } from "@/components/ui/progress";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// ============== VERTU CONFIG ==============
const VERTU_CONFIG = {
  sagesse: { icon: Brain, color: "#D97706", label: "Sagesse et connaissance" },
  courage: { icon: Target, color: "#EF4444", label: "Courage" },
  humanite: { icon: Heart, color: "#EC4899", label: "Humanité" },
  justice: { icon: Shield, color: "#8B5CF6", label: "Justice" },
  temperance: { icon: Compass, color: "#0F766E", label: "Tempérance" },
  transcendance: { icon: Sun, color: "#3B82F6", label: "Transcendance" }
};

// ============== RE'ACTIF PRO HOME ==============
export const ReactifHome = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [profileId, setProfileId] = useState(null);

  useEffect(() => {
    // Check if coming from VSI with profile
    const params = new URLSearchParams(location.search);
    const id = params.get('profile');
    if (id) {
      setProfileId(id);
    }
  }, [location]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-teal-50 via-stone-50 to-amber-50" data-testid="reactif-home">
      {/* Hero */}
      <div className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24">
          {/* Header */}
          <div className="text-center mb-16 animate-fade-in-up">
            <Badge variant="secondary" className="mb-4 bg-teal-100 text-teal-800 hover:bg-teal-100">
              <Sparkles className="w-3 h-3 mr-1" />
              Étape 2 - Après VSI
            </Badge>
            <h1 className="text-4xl md:text-6xl font-bold text-[#1C1917] tracking-tight mb-6" style={{ fontFamily: 'Fraunces, serif' }}>
              RE'ACTIF<span className="text-teal-600"> PRO</span>
            </h1>
            <p className="text-lg md:text-xl text-[#57534E] max-w-3xl mx-auto leading-relaxed">
              Transformez votre diagnostic VSI en <strong>décisions concrètes</strong> et en <strong>actions durables</strong> 
              pour votre insertion professionnelle.
            </p>
          </div>

          {/* Transition message if from VSI */}
          {profileId && (
            <div className="max-w-2xl mx-auto mb-12 animate-fade-in-up">
              <Card className="bg-gradient-to-r from-amber-50 to-teal-50 border-2 border-teal-200">
                <CardContent className="p-6 text-center">
                  <CheckCircle2 className="w-12 h-12 text-teal-500 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold mb-2" style={{ fontFamily: 'Fraunces, serif' }}>
                    Votre diagnostic VSI est terminé !
                  </h3>
                  <p className="text-[#57534E] mb-4">
                    Passez maintenant à l'étape suivante pour transformer ces résultats en actions concrètes.
                  </p>
                  <Button 
                    onClick={() => navigate(`/reactif/particuliers?profile=${profileId}`)}
                    className="bg-teal-600 hover:bg-teal-700 text-white rounded-full"
                    data-testid="continue-with-profile-btn"
                  >
                    Continuer mon parcours <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </CardContent>
              </Card>
            </div>
          )}

          {/* 3 Entry Points */}
          <div className="text-center mb-8">
            <h2 className="text-2xl font-semibold text-[#1C1917]" style={{ fontFamily: 'Fraunces, serif' }}>
              Choisissez votre parcours
            </h2>
          </div>

          <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {/* Particuliers */}
            <Card 
              className="vsi-card cursor-pointer group hover:border-amber-300 transition-all animate-fade-in-up delay-100"
              onClick={() => navigate(profileId ? `/reactif/particuliers?profile=${profileId}` : "/reactif/particuliers")}
              data-testid="entry-particuliers"
            >
              <CardHeader className="text-center pb-4">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-amber-100 to-amber-200 flex items-center justify-center group-hover:scale-110 transition-transform">
                  <Users className="w-8 h-8 text-amber-600" />
                </div>
                <CardTitle style={{ fontFamily: 'Fraunces, serif' }}>Particuliers</CardTitle>
                <CardDescription>Emploi, reconversion, clarification</CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm text-[#57534E] mb-4">
                  <li className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-amber-500" />
                    Comprendre mon profil
                  </li>
                  <li className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-amber-500" />
                    Clarifier mon projet
                  </li>
                  <li className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-amber-500" />
                    Plan d'action 30/60/90j
                  </li>
                </ul>
                <div className="flex items-center justify-center text-amber-600 font-medium group-hover:translate-x-1 transition-transform">
                  Accéder <ArrowRight className="w-4 h-4 ml-1" />
                </div>
              </CardContent>
            </Card>

            {/* Services RH */}
            <Card 
              className="vsi-card cursor-pointer group hover:border-purple-300 transition-all animate-fade-in-up delay-200"
              onClick={() => navigate("/reactif/services-rh")}
              data-testid="entry-rh"
            >
              <CardHeader className="text-center pb-4">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-purple-100 to-purple-200 flex items-center justify-center group-hover:scale-110 transition-transform">
                  <Building2 className="w-8 h-8 text-purple-600" />
                </div>
                <CardTitle style={{ fontFamily: 'Fraunces, serif' }}>Services RH</CardTitle>
                <CardDescription>Mobilité, transition, sécurisation</CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm text-[#57534E] mb-4">
                  <li className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-purple-500" />
                    Mobilité interne
                  </li>
                  <li className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-purple-500" />
                    Accompagnement transitions
                  </li>
                  <li className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-purple-500" />
                    Prévention des ruptures
                  </li>
                </ul>
                <div className="flex items-center justify-center text-purple-600 font-medium group-hover:translate-x-1 transition-transform">
                  Accéder <ArrowRight className="w-4 h-4 ml-1" />
                </div>
              </CardContent>
            </Card>

            {/* Partenaires sociaux */}
            <Card 
              className="vsi-card cursor-pointer group hover:border-teal-300 transition-all animate-fade-in-up delay-300"
              onClick={() => navigate("/reactif/partenaires")}
              data-testid="entry-partenaires"
            >
              <CardHeader className="text-center pb-4">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-teal-100 to-teal-200 flex items-center justify-center group-hover:scale-110 transition-transform">
                  <Handshake className="w-8 h-8 text-teal-600" />
                </div>
                <CardTitle style={{ fontFamily: 'Fraunces, serif' }}>Partenaires sociaux</CardTitle>
                <CardDescription>Insertion, territoires, impact</CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm text-[#57534E] mb-4">
                  <li className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-teal-500" />
                    Dispositif structurant
                  </li>
                  <li className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-teal-500" />
                    Indicateurs d'impact
                  </li>
                  <li className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-teal-500" />
                    Déploiement territorial
                  </li>
                </ul>
                <div className="flex items-center justify-center text-teal-600 font-medium group-hover:translate-x-1 transition-transform">
                  Accéder <ArrowRight className="w-4 h-4 ml-1" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Process steps */}
          <div className="mt-20 max-w-4xl mx-auto animate-fade-in-up delay-400">
            <h3 className="text-center text-xl font-semibold mb-8 text-[#1C1917]" style={{ fontFamily: 'Fraunces, serif' }}>
              Le parcours RE'ACTIF PRO
            </h3>
            <div className="flex flex-col md:flex-row items-center justify-between gap-4">
              <div className="flex flex-col items-center text-center">
                <div className="w-12 h-12 rounded-full bg-amber-100 flex items-center justify-center mb-2">
                  <span className="font-bold text-amber-600">1</span>
                </div>
                <span className="text-sm font-medium">VSI</span>
                <span className="text-xs text-[#A8A29E]">Identifier</span>
              </div>
              <ArrowRight className="w-6 h-6 text-stone-300 hidden md:block" />
              <div className="flex flex-col items-center text-center">
                <div className="w-12 h-12 rounded-full bg-teal-100 flex items-center justify-center mb-2">
                  <span className="font-bold text-teal-600">2</span>
                </div>
                <span className="text-sm font-medium">RE'ACTIF PRO</span>
                <span className="text-xs text-[#A8A29E]">Structurer & Agir</span>
              </div>
              <ArrowRight className="w-6 h-6 text-stone-300 hidden md:block" />
              <div className="flex flex-col items-center text-center">
                <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center mb-2">
                  <span className="font-bold text-green-600">3</span>
                </div>
                <span className="text-sm font-medium">Impact</span>
                <span className="text-xs text-[#A8A29E]">Insertion durable</span>
              </div>
            </div>
          </div>

          {/* CTA to VSI */}
          {!profileId && (
            <div className="mt-16 text-center animate-fade-in-up delay-500">
              <p className="text-[#57534E] mb-4">Vous n'avez pas encore fait le diagnostic VSI ?</p>
              <Button 
                variant="outline" 
                onClick={() => navigate("/")}
                className="rounded-full"
              >
                Commencer par VSI <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// ============== PARTICULIERS PAGE ==============
export const ParticuliersPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [profile, setProfile] = useState(null);
  const [actionPlan, setActionPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generatingPlan, setGeneratingPlan] = useState(false);
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const profileId = params.get('profile');
    
    if (profileId) {
      fetchProfile(profileId);
    } else {
      setLoading(false);
    }
  }, [location]);

  const fetchProfile = async (id) => {
    try {
      const response = await axios.get(`${API}/reactif/profile/${id}`);
      setProfile(response.data);
      
      // Try to get existing action plan
      try {
        const planResponse = await axios.get(`${API}/reactif/plan-action/${id}`);
        setActionPlan(planResponse.data);
      } catch (e) {
        // No plan yet
      }
    } catch (error) {
      toast.error("Profil non trouvé");
    } finally {
      setLoading(false);
    }
  };

  const generateActionPlan = async () => {
    if (!profile) return;
    setGeneratingPlan(true);
    try {
      const response = await axios.post(`${API}/reactif/plan-action?profile_id=${profile.id}`);
      setActionPlan(response.data);
      toast.success("Plan d'action généré !");
      setActiveStep(3);
    } catch (error) {
      toast.error("Erreur lors de la génération du plan");
    } finally {
      setGeneratingPlan(false);
    }
  };

  const steps = [
    { title: "Comprendre", description: "Mon identité professionnelle", icon: Brain },
    { title: "Clarifier", description: "Mon projet", icon: Target },
    { title: "Consolider", description: "Ma posture", icon: Award },
    { title: "Agir", description: "Plan 30/60/90 jours", icon: Calendar }
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-[#FAFAF9] flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-teal-500" />
      </div>
    );
  }

  // If no profile, show intro
  if (!profile) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-stone-50 to-teal-50" data-testid="particuliers-intro">
        <div className="max-w-4xl mx-auto px-4 py-16">
          <Button variant="ghost" onClick={() => navigate("/reactif")} className="mb-8">
            <ArrowLeft className="w-4 h-4 mr-2" /> Retour
          </Button>
          
          <div className="text-center mb-12">
            <Badge className="mb-4 bg-amber-100 text-amber-800">Particuliers</Badge>
            <h1 className="text-3xl md:text-4xl font-bold mb-4" style={{ fontFamily: 'Fraunces, serif' }}>
              Clarifier – Se positionner – Passer à l'action
            </h1>
            <p className="text-lg text-[#57534E] max-w-2xl mx-auto">
              Transformez votre diagnostic VSI en projet professionnel clair, réaliste et actionnable.
            </p>
          </div>

          <Card className="vsi-card max-w-xl mx-auto">
            <CardHeader>
              <CardTitle>Ce que l'étape 2 vous apporte</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-teal-500 mt-0.5" />
                <span>Une lecture claire de votre identité professionnelle</span>
              </div>
              <div className="flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-teal-500 mt-0.5" />
                <span>Des pistes métiers, secteurs et environnements compatibles</span>
              </div>
              <div className="flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-teal-500 mt-0.5" />
                <span>Un travail sur la posture professionnelle</span>
              </div>
              <div className="flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-teal-500 mt-0.5" />
                <span>Un plan d'action concret et réaliste</span>
              </div>
              
              <div className="pt-4 border-t">
                <p className="text-sm text-[#57534E] mb-4">
                  Pour accéder à votre parcours personnalisé, vous devez d'abord réaliser le diagnostic VSI.
                </p>
                <Button 
                  onClick={() => navigate("/")}
                  className="w-full bg-amber-500 hover:bg-amber-600 text-white rounded-full"
                >
                  Faire le diagnostic VSI <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#FAFAF9]" data-testid="particuliers-page">
      {/* Header */}
      <div className="bg-gradient-to-r from-amber-500 to-teal-500 text-white py-8 px-4">
        <div className="max-w-5xl mx-auto">
          <Button variant="ghost" onClick={() => navigate("/reactif")} className="text-white hover:bg-white/20 mb-4">
            <ArrowLeft className="w-4 h-4 mr-2" /> RE'ACTIF PRO
          </Button>
          <h1 className="text-2xl md:text-3xl font-bold" style={{ fontFamily: 'Fraunces, serif' }}>
            Mon Parcours RE'ACTIF PRO
          </h1>
          <p className="text-white/80 mt-2">De l'identité professionnelle à l'action concrète</p>
        </div>
      </div>

      {/* Progress Steps */}
      <div className="max-w-5xl mx-auto px-4 py-8">
        <div className="flex justify-between mb-8">
          {steps.map((step, idx) => {
            const Icon = step.icon;
            const isActive = idx === activeStep;
            const isCompleted = idx < activeStep;
            
            return (
              <button
                key={idx}
                onClick={() => setActiveStep(idx)}
                className={`flex flex-col items-center text-center transition-all ${
                  isActive ? 'scale-105' : ''
                }`}
              >
                <div className={`w-12 h-12 rounded-full flex items-center justify-center mb-2 transition-all ${
                  isActive ? 'bg-teal-500 text-white shadow-lg' :
                  isCompleted ? 'bg-teal-100 text-teal-600' :
                  'bg-stone-100 text-stone-400'
                }`}>
                  {isCompleted ? <Check className="w-5 h-5" /> : <Icon className="w-5 h-5" />}
                </div>
                <span className={`text-sm font-medium ${isActive ? 'text-teal-600' : 'text-stone-500'}`}>
                  {step.title}
                </span>
                <span className="text-xs text-stone-400 hidden md:block">{step.description}</span>
              </button>
            );
          })}
        </div>

        {/* Step Content */}
        <div className="animate-fade-in-up">
          {/* Step 0: Comprendre */}
          {activeStep === 0 && (
            <div className="grid md:grid-cols-2 gap-6">
              <Card className="vsi-card">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="w-5 h-5 text-amber-500" />
                    Vertus Dominantes
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {profile.vertus_dominantes?.map((vertu) => {
                      const config = VERTU_CONFIG[vertu];
                      const Icon = config?.icon || Brain;
                      return (
                        <div key={vertu} className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full flex items-center justify-center"
                            style={{ backgroundColor: `${config?.color}20` }}>
                            <Icon className="w-5 h-5" style={{ color: config?.color }} />
                          </div>
                          <span className="font-medium">{config?.label}</span>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>

              <Card className="vsi-card">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Star className="w-5 h-5 text-amber-500" />
                    Valeurs & Qualités
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="mb-4">
                    <p className="text-sm text-[#57534E] mb-2">Valeurs</p>
                    <div className="flex flex-wrap gap-2">
                      {profile.valeurs?.slice(0, 4).map((v) => (
                        <Badge key={v} variant="secondary" className="bg-amber-50 text-amber-700">{v}</Badge>
                      ))}
                    </div>
                  </div>
                  <div>
                    <p className="text-sm text-[#57534E] mb-2">Qualités</p>
                    <div className="flex flex-wrap gap-2">
                      {profile.qualites_humaines?.slice(0, 4).map((q) => (
                        <Badge key={q} variant="secondary" className="bg-pink-50 text-pink-700">{q}</Badge>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="vsi-card md:col-span-2">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Brain className="w-5 h-5 text-purple-500" />
                    Compétences & Savoirs-être
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <p className="text-sm text-[#57534E] mb-3">Compétences psychosociales</p>
                      <ul className="space-y-2">
                        {profile.competences_psychosociales?.map((c) => (
                          <li key={c} className="flex items-center gap-2 text-sm">
                            <Check className="w-4 h-4 text-green-500" />
                            {c}
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <p className="text-sm text-[#57534E] mb-3">Savoirs-être professionnels</p>
                      <ul className="space-y-2">
                        {profile.savoirs_etre?.map((s) => (
                          <li key={s} className="flex items-center gap-2 text-sm">
                            <ChevronRight className="w-4 h-4 text-blue-500" />
                            {s}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <div className="md:col-span-2 text-center">
                <Button onClick={() => setActiveStep(1)} className="bg-teal-500 hover:bg-teal-600 rounded-full">
                  Continuer vers Clarifier <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </div>
            </div>
          )}

          {/* Step 1: Clarifier */}
          {activeStep === 1 && (
            <div>
              <Card className="vsi-card mb-6">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Briefcase className="w-5 h-5 text-teal-500" />
                    Filières Professionnelles Compatibles
                  </CardTitle>
                  <CardDescription>
                    Environnements où vos compétences et valeurs s'expriment le mieux
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-2 gap-4">
                    {profile.filieres_compatibles?.map((filiere, idx) => (
                      <div key={filiere.id} className="p-4 rounded-xl border border-stone-200 hover:border-teal-300 transition-all">
                        <div className="flex items-center justify-between mb-2">
                          <Badge variant="outline">{filiere.code}</Badge>
                          <span className="text-xs text-stone-400">#{idx + 1}</span>
                        </div>
                        <h4 className="font-semibold mb-1">{filiere.nom}</h4>
                        <p className="text-sm text-[#57534E] mb-3">{filiere.description}</p>
                        <div className="flex flex-wrap gap-1">
                          {filiere.metiers_types?.slice(0, 3).map((m) => (
                            <span key={m} className="text-xs bg-teal-50 text-teal-700 px-2 py-0.5 rounded">{m}</span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {profile.target_job && (
                <Card className="vsi-card mb-6 border-l-4 border-l-amber-500">
                  <CardHeader>
                    <CardTitle>Métier visé : {profile.target_job}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-[#57534E]">
                      Votre profil montre une bonne compatibilité avec ce métier. 
                      Les recommandations IA vous guideront sur les points d'attention.
                    </p>
                  </CardContent>
                </Card>
              )}

              <div className="flex justify-between">
                <Button variant="outline" onClick={() => setActiveStep(0)} className="rounded-full">
                  <ArrowLeft className="w-4 h-4 mr-2" /> Retour
                </Button>
                <Button onClick={() => setActiveStep(2)} className="bg-teal-500 hover:bg-teal-600 rounded-full">
                  Continuer vers Consolider <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </div>
            </div>
          )}

          {/* Step 2: Consolider */}
          {activeStep === 2 && (
            <div>
              <Card className="vsi-card mb-6">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Award className="w-5 h-5 text-purple-500" />
                    Posture Professionnelle
                  </CardTitle>
                  <CardDescription>
                    Ce qui vous caractérise dans un environnement de travail
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-3 gap-4 mb-6">
                    <div className="p-4 bg-purple-50 rounded-xl">
                      <h4 className="font-medium text-purple-700 mb-2">Communication</h4>
                      <p className="text-sm text-purple-600">
                        Votre style naturel de communication s'appuie sur vos qualités d'écoute et d'empathie.
                      </p>
                    </div>
                    <div className="p-4 bg-teal-50 rounded-xl">
                      <h4 className="font-medium text-teal-700 mb-2">Légitimité</h4>
                      <p className="text-sm text-teal-600">
                        Vos compétences psychosociales fondent votre légitimité professionnelle.
                      </p>
                    </div>
                    <div className="p-4 bg-amber-50 rounded-xl">
                      <h4 className="font-medium text-amber-700 mb-2">Alignement</h4>
                      <p className="text-sm text-amber-600">
                        Vos valeurs guident vos décisions et votre engagement professionnel.
                      </p>
                    </div>
                  </div>

                  {profile.recommandations_ia && (
                    <div className="bg-stone-50 rounded-xl p-4 border">
                      <h4 className="font-medium mb-2 flex items-center gap-2">
                        <Sparkles className="w-4 h-4 text-amber-500" />
                        Recommandations personnalisées
                      </h4>
                      <p className="text-sm text-[#57534E] whitespace-pre-wrap">
                        {profile.recommandations_ia}
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>

              <div className="flex justify-between">
                <Button variant="outline" onClick={() => setActiveStep(1)} className="rounded-full">
                  <ArrowLeft className="w-4 h-4 mr-2" /> Retour
                </Button>
                <Button onClick={() => setActiveStep(3)} className="bg-teal-500 hover:bg-teal-600 rounded-full">
                  Continuer vers Plan d'action <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </div>
            </div>
          )}

          {/* Step 3: Agir */}
          {activeStep === 3 && (
            <div>
              {!actionPlan ? (
                <Card className="vsi-card text-center py-12">
                  <CardContent>
                    <Calendar className="w-16 h-16 text-teal-500 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold mb-2" style={{ fontFamily: 'Fraunces, serif' }}>
                      Plan d'Action 30/60/90 jours
                    </h3>
                    <p className="text-[#57534E] mb-6 max-w-md mx-auto">
                      Générez votre plan d'action personnalisé basé sur votre profil et vos objectifs professionnels.
                    </p>
                    <Button 
                      onClick={generateActionPlan}
                      disabled={generatingPlan}
                      className="bg-teal-500 hover:bg-teal-600 rounded-full"
                      data-testid="generate-plan-btn"
                    >
                      {generatingPlan ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Génération en cours...
                        </>
                      ) : (
                        <>
                          <Sparkles className="w-4 h-4 mr-2" />
                          Générer mon plan d'action
                        </>
                      )}
                    </Button>
                  </CardContent>
                </Card>
              ) : (
                <div className="space-y-6">
                  {/* 30 days */}
                  <Card className="vsi-card border-l-4 border-l-green-500">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Clock className="w-5 h-5 text-green-500" />
                        30 premiers jours
                      </CardTitle>
                      <CardDescription>Actions prioritaires immédiates</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {actionPlan.actions_30j?.map((action, idx) => (
                          <div key={idx} className="flex items-start gap-3 p-3 bg-green-50 rounded-lg">
                            <Circle className="w-5 h-5 text-green-500 mt-0.5" />
                            <div>
                              <h4 className="font-medium">{action.titre}</h4>
                              <p className="text-sm text-[#57534E]">{action.description}</p>
                              <Badge variant="outline" className="mt-1 text-xs">
                                Priorité: {action.priorite}
                              </Badge>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  {/* 60 days */}
                  <Card className="vsi-card border-l-4 border-l-amber-500">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Clock className="w-5 h-5 text-amber-500" />
                        30 à 60 jours
                      </CardTitle>
                      <CardDescription>Consolidation et développement</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {actionPlan.actions_60j?.map((action, idx) => (
                          <div key={idx} className="flex items-start gap-3 p-3 bg-amber-50 rounded-lg">
                            <Circle className="w-5 h-5 text-amber-500 mt-0.5" />
                            <div>
                              <h4 className="font-medium">{action.titre}</h4>
                              <p className="text-sm text-[#57534E]">{action.description}</p>
                              <Badge variant="outline" className="mt-1 text-xs">
                                Priorité: {action.priorite}
                              </Badge>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  {/* 90 days */}
                  <Card className="vsi-card border-l-4 border-l-purple-500">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Clock className="w-5 h-5 text-purple-500" />
                        60 à 90 jours
                      </CardTitle>
                      <CardDescription>Évaluation et ajustement</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {actionPlan.actions_90j?.map((action, idx) => (
                          <div key={idx} className="flex items-start gap-3 p-3 bg-purple-50 rounded-lg">
                            <Circle className="w-5 h-5 text-purple-500 mt-0.5" />
                            <div>
                              <h4 className="font-medium">{action.titre}</h4>
                              <p className="text-sm text-[#57534E]">{action.description}</p>
                              <Badge variant="outline" className="mt-1 text-xs">
                                Priorité: {action.priorite}
                              </Badge>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )}

              <div className="flex justify-between mt-6">
                <Button variant="outline" onClick={() => setActiveStep(2)} className="rounded-full">
                  <ArrowLeft className="w-4 h-4 mr-2" /> Retour
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// ============== SERVICES RH PAGE ==============
export const ServicesRHPage = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    nom: "", email: "", telephone: "", organisation: "", message: ""
  });
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await axios.post(`${API}/reactif/contact`, {
        type: "rh",
        ...formData
      });
      toast.success("Demande envoyée avec succès !");
      setFormData({ nom: "", email: "", telephone: "", organisation: "", message: "" });
    } catch (error) {
      toast.error("Erreur lors de l'envoi");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-stone-50 to-teal-50" data-testid="services-rh-page">
      <div className="max-w-6xl mx-auto px-4 py-12">
        <Button variant="ghost" onClick={() => navigate("/reactif")} className="mb-8">
          <ArrowLeft className="w-4 h-4 mr-2" /> Retour
        </Button>

        <div className="grid md:grid-cols-2 gap-12">
          {/* Info */}
          <div>
            <Badge className="mb-4 bg-purple-100 text-purple-800">Services RH</Badge>
            <h1 className="text-3xl md:text-4xl font-bold mb-6" style={{ fontFamily: 'Fraunces, serif' }}>
              Sécuriser les trajectoires professionnelles
            </h1>
            
            <div className="space-y-6">
              <div>
                <h3 className="font-semibold text-lg mb-2">Vos enjeux</h3>
                <ul className="space-y-2 text-[#57534E]">
                  <li className="flex items-start gap-2">
                    <ChevronRight className="w-4 h-4 text-purple-500 mt-1" />
                    Mobilité interne et reclassement
                  </li>
                  <li className="flex items-start gap-2">
                    <ChevronRight className="w-4 h-4 text-purple-500 mt-1" />
                    Accompagnement des transitions
                  </li>
                  <li className="flex items-start gap-2">
                    <ChevronRight className="w-4 h-4 text-purple-500 mt-1" />
                    Prévention des ruptures professionnelles
                  </li>
                </ul>
              </div>

              <div>
                <h3 className="font-semibold text-lg mb-2">Ce que permet RE'ACTIF PRO</h3>
                <ul className="space-y-2 text-[#57534E]">
                  <li className="flex items-start gap-2">
                    <Check className="w-4 h-4 text-green-500 mt-1" />
                    Objectiver les profils au-delà du CV
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="w-4 h-4 text-green-500 mt-1" />
                    Identifier des environnements compatibles
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="w-4 h-4 text-green-500 mt-1" />
                    Accompagner sans formatage
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="w-4 h-4 text-green-500 mt-1" />
                    Réduire les risques de rupture
                  </li>
                </ul>
              </div>

              <Card className="bg-purple-50 border-purple-200">
                <CardContent className="p-4">
                  <h4 className="font-medium text-purple-700 mb-2">Cas d'usage principaux</h4>
                  <div className="flex flex-wrap gap-2">
                    <Badge variant="secondary" className="bg-white">Mobilité interne</Badge>
                    <Badge variant="secondary" className="bg-white">Transition externe</Badge>
                    <Badge variant="secondary" className="bg-white">Gestion des talents</Badge>
                    <Badge variant="secondary" className="bg-white">Prévention désengagement</Badge>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Form */}
          <Card className="vsi-card">
            <CardHeader>
              <CardTitle>Échanger avec un expert</CardTitle>
              <CardDescription>Découvrez comment intégrer RE'ACTIF PRO dans votre organisation</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="nom">Nom *</Label>
                    <Input 
                      id="nom" 
                      value={formData.nom}
                      onChange={(e) => setFormData({...formData, nom: e.target.value})}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="email">Email *</Label>
                    <Input 
                      id="email" 
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({...formData, email: e.target.value})}
                      required
                    />
                  </div>
                </div>
                <div>
                  <Label htmlFor="organisation">Organisation</Label>
                  <Input 
                    id="organisation"
                    value={formData.organisation}
                    onChange={(e) => setFormData({...formData, organisation: e.target.value})}
                  />
                </div>
                <div>
                  <Label htmlFor="telephone">Téléphone</Label>
                  <Input 
                    id="telephone"
                    value={formData.telephone}
                    onChange={(e) => setFormData({...formData, telephone: e.target.value})}
                  />
                </div>
                <div>
                  <Label htmlFor="message">Message *</Label>
                  <Textarea 
                    id="message"
                    rows={4}
                    value={formData.message}
                    onChange={(e) => setFormData({...formData, message: e.target.value})}
                    required
                  />
                </div>
                <Button 
                  type="submit" 
                  disabled={submitting}
                  className="w-full bg-purple-600 hover:bg-purple-700 rounded-full"
                >
                  {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4 mr-2" />}
                  Envoyer
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

// ============== PARTENAIRES PAGE ==============
export const PartenairesPage = () => {
  const navigate = useNavigate();
  const [impact, setImpact] = useState(null);
  const [formData, setFormData] = useState({
    nom: "", email: "", telephone: "", organisation: "", message: ""
  });
  const [submitting, setSubmitting] = useState(false);

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

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await axios.post(`${API}/reactif/contact`, {
        type: "partenaire",
        ...formData
      });
      toast.success("Demande envoyée avec succès !");
      setFormData({ nom: "", email: "", telephone: "", organisation: "", message: "" });
    } catch (error) {
      toast.error("Erreur lors de l'envoi");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-teal-50 via-stone-50 to-amber-50" data-testid="partenaires-page">
      <div className="max-w-6xl mx-auto px-4 py-12">
        <Button variant="ghost" onClick={() => navigate("/reactif")} className="mb-8">
          <ArrowLeft className="w-4 h-4 mr-2" /> Retour
        </Button>

        <div className="text-center mb-12">
          <Badge className="mb-4 bg-teal-100 text-teal-800">Partenaires sociaux</Badge>
          <h1 className="text-3xl md:text-4xl font-bold mb-4" style={{ fontFamily: 'Fraunces, serif' }}>
            Un dispositif structurant au service des parcours
          </h1>
          <p className="text-lg text-[#57534E] max-w-2xl mx-auto">
            RE'ACTIF PRO crée un lien structuré entre diagnostic, orientation et mise en action 
            pour sécuriser les trajectoires professionnelles.
          </p>
        </div>

        {/* Impact Stats */}
        {impact && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
            <Card className="text-center p-4">
              <div className="text-3xl font-bold text-teal-600">{impact.taux_clarification}%</div>
              <div className="text-sm text-[#57534E]">Clarification projet</div>
            </Card>
            <Card className="text-center p-4">
              <div className="text-3xl font-bold text-amber-600">{impact.taux_mise_en_action_30j}%</div>
              <div className="text-sm text-[#57534E]">Mise en action 30j</div>
            </Card>
            <Card className="text-center p-4">
              <div className="text-3xl font-bold text-purple-600">{impact.progression_posture}%</div>
              <div className="text-sm text-[#57534E]">Progression posture</div>
            </Card>
            <Card className="text-center p-4">
              <div className="text-3xl font-bold text-green-600">{impact.satisfaction}%</div>
              <div className="text-sm text-[#57534E]">Satisfaction</div>
            </Card>
          </div>
        )}

        <div className="grid md:grid-cols-2 gap-12">
          {/* Info */}
          <div className="space-y-6">
            <Card className="vsi-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-teal-500" />
                  Enjeux territoriaux
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-[#57534E]">
                  <li className="flex items-start gap-2">
                    <ChevronRight className="w-4 h-4 text-teal-500 mt-1" />
                    Publics en difficulté de projection
                  </li>
                  <li className="flex items-start gap-2">
                    <ChevronRight className="w-4 h-4 text-teal-500 mt-1" />
                    Multiplication des dispositifs sans continuité
                  </li>
                  <li className="flex items-start gap-2">
                    <ChevronRight className="w-4 h-4 text-teal-500 mt-1" />
                    Besoin d'indicateurs d'impact réels
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card className="vsi-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-amber-500" />
                  Valeur ajoutée institutionnelle
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-[#57534E]">
                  <li className="flex items-start gap-2">
                    <Check className="w-4 h-4 text-green-500 mt-1" />
                    Sécurisation des parcours
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="w-4 h-4 text-green-500 mt-1" />
                    Réduction des ruptures
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="w-4 h-4 text-green-500 mt-1" />
                    Meilleure orientation emploi/formation
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="w-4 h-4 text-green-500 mt-1" />
                    Données d'impact exploitables
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card className="bg-teal-50 border-teal-200">
              <CardContent className="p-4">
                <h4 className="font-medium text-teal-700 mb-2">Public cible</h4>
                <div className="flex flex-wrap gap-2">
                  <Badge variant="secondary" className="bg-white">France Travail</Badge>
                  <Badge variant="secondary" className="bg-white">Missions locales</Badge>
                  <Badge variant="secondary" className="bg-white">Organismes formation</Badge>
                  <Badge variant="secondary" className="bg-white">Associations insertion</Badge>
                  <Badge variant="secondary" className="bg-white">ESS</Badge>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Form */}
          <Card className="vsi-card">
            <CardHeader>
              <CardTitle>Devenir partenaire</CardTitle>
              <CardDescription>Déployez RE'ACTIF PRO sur votre territoire</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="nom">Nom *</Label>
                    <Input 
                      id="nom" 
                      value={formData.nom}
                      onChange={(e) => setFormData({...formData, nom: e.target.value})}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="email">Email *</Label>
                    <Input 
                      id="email" 
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({...formData, email: e.target.value})}
                      required
                    />
                  </div>
                </div>
                <div>
                  <Label htmlFor="organisation">Organisation *</Label>
                  <Input 
                    id="organisation"
                    value={formData.organisation}
                    onChange={(e) => setFormData({...formData, organisation: e.target.value})}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="telephone">Téléphone</Label>
                  <Input 
                    id="telephone"
                    value={formData.telephone}
                    onChange={(e) => setFormData({...formData, telephone: e.target.value})}
                  />
                </div>
                <div>
                  <Label htmlFor="message">Message *</Label>
                  <Textarea 
                    id="message"
                    rows={4}
                    placeholder="Décrivez votre projet de déploiement..."
                    value={formData.message}
                    onChange={(e) => setFormData({...formData, message: e.target.value})}
                    required
                  />
                </div>
                <Button 
                  type="submit" 
                  disabled={submitting}
                  className="w-full bg-teal-600 hover:bg-teal-700 rounded-full"
                >
                  {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Handshake className="w-4 h-4 mr-2" />}
                  Devenir partenaire
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default {
  ReactifHome,
  ParticuliersPage,
  ServicesRHPage,
  PartenairesPage
};
