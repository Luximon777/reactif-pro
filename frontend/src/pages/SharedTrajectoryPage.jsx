import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Route, Briefcase, GraduationCap, Clock, Target, Heart, Users,
  Lightbulb, Compass, Award, RefreshCw, BookOpen, Shield, Zap,
  User, Building2, MapPin, Star, CheckCircle
} from "lucide-react";

const STEP_TYPES = {
  emploi:        { label: "Emploi",           color: "bg-blue-500",    bg: "bg-blue-50",    text: "text-blue-700",    icon: Briefcase },
  formation:     { label: "Formation",        color: "bg-emerald-500", bg: "bg-emerald-50", text: "text-emerald-700", icon: GraduationCap },
  stage:         { label: "Stage",            color: "bg-cyan-500",    bg: "bg-cyan-50",    text: "text-cyan-700",    icon: BookOpen },
  interim:       { label: "Mission intérim",  color: "bg-indigo-500",  bg: "bg-indigo-50",  text: "text-indigo-700",  icon: Clock },
  reconversion:  { label: "Reconversion",     color: "bg-violet-500",  bg: "bg-violet-50",  text: "text-violet-700",  icon: RefreshCw },
  recherche:     { label: "Recherche emploi", color: "bg-amber-500",   bg: "bg-amber-50",   text: "text-amber-700",   icon: Target },
  pause:         { label: "Pause / Personnel",color: "bg-slate-400",   bg: "bg-slate-50",   text: "text-slate-600",   icon: Heart },
  benevolat:     { label: "Bénévolat",        color: "bg-rose-500",    bg: "bg-rose-50",    text: "text-rose-700",    icon: Users },
  creation:      { label: "Création activité",color: "bg-orange-500",  bg: "bg-orange-50",  text: "text-orange-700",  icon: Lightbulb },
  mobilite:      { label: "Mobilité géo.",    color: "bg-teal-500",    bg: "bg-teal-50",    text: "text-teal-700",    icon: Compass },
  certification: { label: "Certification",    color: "bg-pink-500",    bg: "bg-pink-50",    text: "text-pink-700",    icon: Award },
};

const AUDIENCE_LABELS = {
  accompagnateur: { label: "Vue Accompagnateur", color: "bg-blue-100 text-blue-700", icon: Users },
  recruteur: { label: "Vue Recruteur", color: "bg-violet-100 text-violet-700", icon: Building2 },
  public: { label: "Vue Publique", color: "bg-emerald-100 text-emerald-700", icon: MapPin },
};

const SharedTrajectoryPage = () => {
  const { shareId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await axios.get(`${API}/trajectory/shared/${shareId}`);
        setData(res.data);
      } catch (e) {
        setError(e.response?.data?.detail || "Lien non trouvé ou expiré");
      }
      setLoading(false);
    };
    load();
  }, [shareId]);

  if (loading) return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center">
      <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-[#1e3a5f]" />
    </div>
  );

  if (error) return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <Card className="max-w-md w-full text-center">
        <CardContent className="p-8">
          <Shield className="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <h2 className="text-lg font-bold text-slate-800 mb-2">Lien indisponible</h2>
          <p className="text-sm text-slate-500">{error}</p>
        </CardContent>
      </Card>
    </div>
  );

  const aud = AUDIENCE_LABELS[data.audience] || AUDIENCE_LABELS.accompagnateur;
  const AudIcon = aud.icon;

  return (
    <div className="min-h-screen bg-slate-50" data-testid="shared-trajectory-page">
      {/* Header */}
      <div className="bg-gradient-to-r from-[#1e3a5f] to-[#2d5a8e] text-white">
        <div className="max-w-4xl mx-auto px-4 py-8">
          <div className="flex items-center gap-2 mb-3">
            <Badge className={`${aud.color} text-xs`}><AudIcon className="w-3 h-3 mr-1" />{aud.label}</Badge>
            <Badge className="bg-white/10 text-white/70 text-xs"><Shield className="w-3 h-3 mr-1" />Partagé via Ré'Actif Pro</Badge>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold" style={{ fontFamily: 'Outfit, sans-serif' }}>
            Trajectoire de {data.display_name}
          </h1>
          <p className="text-blue-200 mt-2 text-sm">{data.step_count} étape(s) — {data.skills_count} compétences identifiées</p>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
        {/* D'CLIC Card */}
        {data.card && (
          <Card className="border-0 shadow-lg overflow-hidden" data-testid="shared-dclic-card">
            <div className="bg-gradient-to-r from-indigo-600 to-violet-600 p-4">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Star className="w-4 h-4" /> Profil D'CLIC PRO vérifié
              </h3>
            </div>
            <CardContent className="p-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {[
                  { label: "MBTI", value: data.card.mbti },
                  { label: "DISC", value: data.card.disc },
                  { label: "RIASEC", value: data.card.riasec },
                  { label: "Vertu", value: data.card.vertu },
                ].filter(d => d.value).map((dim, idx) => (
                  <div key={idx} className="text-center p-3 rounded-lg bg-slate-50">
                    <p className="text-[10px] text-slate-400 uppercase">{dim.label}</p>
                    <p className="text-lg font-bold text-slate-900">{dim.value}</p>
                  </div>
                ))}
              </div>
              {data.card.competences?.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {data.card.competences.map((c, i) => <Badge key={i} className="bg-indigo-50 text-indigo-700 text-xs">{c}</Badge>)}
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Timeline */}
        {data.steps?.length > 0 && (
          <div>
            <h2 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
              <Route className="w-5 h-5 text-[#1e3a5f]" /> Parcours professionnel
            </h2>
            <div>
              {data.steps.map((step, idx) => {
                const config = STEP_TYPES[step.step_type] || STEP_TYPES.emploi;
                const StepIcon = config.icon;
                return (
                  <div key={idx} className="relative pl-10 pb-6" data-testid={`shared-step-${idx}`}>
                    <div className="absolute left-[15px] top-8 bottom-0 w-0.5 bg-slate-200 last:hidden" />
                    <div className={`absolute left-0 top-1 w-8 h-8 rounded-full ${config.color} flex items-center justify-center shadow-md z-10`}>
                      <StepIcon className="w-4 h-4 text-white" />
                    </div>
                    <Card className={`${config.bg} border ${config.border} shadow-sm`}>
                      <CardContent className="p-4">
                        <div className="flex items-center gap-2 mb-1">
                          <Badge className={`text-[10px] ${config.bg} ${config.text} ${config.border} border`}>{config.label}</Badge>
                          <span className="text-[11px] text-slate-400">
                            {step.start_date}{step.end_date ? ` — ${step.end_date}` : step.is_ongoing ? " — En cours" : ""}
                          </span>
                        </div>
                        <h4 className="font-semibold text-slate-900 text-sm">{step.title}</h4>
                        {step.organization && <p className="text-xs text-slate-500 mt-0.5">{step.organization}</p>}
                        {step.description && <p className="text-xs text-slate-600 mt-2">{step.description}</p>}
                        {step.competences?.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-2">
                            {step.competences.map((c, i) => <Badge key={i} variant="secondary" className="text-[10px]">{c}</Badge>)}
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Skills Preview */}
        {data.skills_preview?.length > 0 && (
          <Card className="card-base" data-testid="shared-skills">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base"><Zap className="w-4 h-4 text-violet-600" /> Compétences identifiées</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {data.skills_preview.map((s, i) => <Badge key={i} variant="outline" className="text-xs">{s}</Badge>)}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Footer */}
        <div className="text-center pt-6 border-t border-slate-200">
          <p className="text-xs text-slate-400">Partagé via <strong className="text-[#1e3a5f]">Ré'Actif Pro</strong> — Tiers de confiance numérique</p>
          <p className="text-[10px] text-slate-300 mt-1">Ce lien a été créé volontairement par la personne concernée</p>
        </div>
      </div>
    </div>
  );
};

export default SharedTrajectoryPage;
