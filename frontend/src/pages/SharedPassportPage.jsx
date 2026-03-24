import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { useParams } from "react-router-dom";
import {
  User, Briefcase, GraduationCap, Target, Shield, Award,
  Sparkles, Clock, Eye, AlertCircle, Layers
} from "lucide-react";
import LogoReactifPro from "@/components/LogoReactifPro";

const LEVEL_LABELS = {
  debutant: "Debutant",
  intermediaire: "Intermediaire",
  avance: "Avance",
  expert: "Expert",
};

const NATURE_LABELS = {
  savoir_faire: "Savoir-faire",
  savoir_etre: "Savoir-etre",
};

const SharedPassportPage = () => {
  const { shareId } = useParams();
  const [passport, setPassport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await axios.get(`${API}/passport/shared/${shareId}`);
        setPassport(res.data);
      } catch (e) {
        const status = e.response?.status;
        if (status === 410) setError("Ce lien de partage a expire.");
        else if (status === 404) setError("Lien de partage invalide.");
        else setError("Erreur lors du chargement du passeport.");
      }
      setLoading(false);
    };
    if (shareId) load();
  }, [shareId]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#1e3a5f] mx-auto" />
          <p className="text-slate-600 text-sm">Chargement du passeport...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <Card className="max-w-md w-full mx-4">
          <CardContent className="p-8 text-center">
            <AlertCircle className="w-12 h-12 text-amber-500 mx-auto mb-4" />
            <h2 className="text-lg font-semibold text-slate-900 mb-2">Lien indisponible</h2>
            <p className="text-slate-600 text-sm">{error}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const comps = passport.competences || [];
  const exps = passport.experiences || [];

  return (
    <div className="min-h-screen bg-slate-50" data-testid="shared-passport-page">
      {/* Header */}
      <div className="bg-gradient-to-r from-[#1e3a5f] to-[#2d5a8f] text-white">
        <div className="max-w-4xl mx-auto px-4 py-8">
          {/* Logo */}
          <div className="flex items-center justify-between mb-6">
            <div className="bg-white/95 rounded-xl px-4 py-2.5 shadow-lg" data-testid="shared-logo">
              <LogoReactifPro size="sm" />
            </div>
            <Badge className="bg-white/15 text-blue-200 text-xs border border-white/20">
              Region Grand Est
            </Badge>
          </div>
          {/* Title */}
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center">
              <Shield className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold" style={{ fontFamily: "Outfit, sans-serif" }}>
                Passeport de Competences
              </h1>
              <p className="text-blue-200 text-sm">Partage anonymise via Re'Actif Pro</p>
            </div>
          </div>
          <div className="flex flex-wrap gap-3">
            <Badge className="bg-white/15 text-white text-xs">
              <Target className="w-3 h-3 mr-1" />{passport.completeness_score}% complete
            </Badge>
            <Badge className="bg-white/15 text-white text-xs">
              <Layers className="w-3 h-3 mr-1" />{comps.length} competences
            </Badge>
            <Badge className="bg-white/15 text-white text-xs">
              <Briefcase className="w-3 h-3 mr-1" />{exps.length} experiences
            </Badge>
            {passport.share_info && (
              <Badge className="bg-white/10 text-blue-200 text-xs">
                <Eye className="w-3 h-3 mr-1" />{passport.share_info.views} vue(s)
              </Badge>
            )}
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
        {/* Professional Summary */}
        {passport.professional_summary && (
          <Card data-testid="shared-summary">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <User className="w-5 h-5 text-[#1e3a5f]" />Resume Professionnel
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-slate-700 leading-relaxed">{passport.professional_summary}</p>
            </CardContent>
          </Card>
        )}

        {/* Career Project & Sectors */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {passport.career_project && (
            <Card data-testid="shared-career-project">
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-base">
                  <Target className="w-4 h-4 text-[#1e3a5f]" />Projet Professionnel
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-600">{passport.career_project}</p>
              </CardContent>
            </Card>
          )}
          {passport.target_sectors?.length > 0 && (
            <Card data-testid="shared-sectors">
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-base">
                  <Briefcase className="w-4 h-4 text-[#1e3a5f]" />Secteurs Vises
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {passport.target_sectors.map((s, i) => (
                    <Badge key={i} className="bg-blue-50 text-[#1e3a5f] border border-blue-200">{s}</Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Competences */}
        {comps.length > 0 && (
          <Card data-testid="shared-competences">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <Sparkles className="w-5 h-5 text-[#1e3a5f]" />Competences ({comps.length})
              </CardTitle>
              <CardDescription>Repertoire des competences identifiees et evaluees</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {comps.map((c, idx) => (
                  <div
                    key={idx}
                    className={`p-3 rounded-lg border ${
                      c.is_emerging ? "bg-amber-50 border-amber-200" : "bg-white border-slate-200"
                    }`}
                    data-testid={`shared-comp-${idx}`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-slate-900">{c.name}</span>
                      {c.is_emerging && (
                        <Badge className="text-[10px] bg-amber-100 text-amber-700">Emergente</Badge>
                      )}
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {c.nature && (
                        <Badge variant="outline" className="text-[10px]">
                          {NATURE_LABELS[c.nature] || c.nature}
                        </Badge>
                      )}
                      {c.level && (
                        <Badge variant="outline" className="text-[10px]">
                          {LEVEL_LABELS[c.level] || c.level}
                        </Badge>
                      )}
                      {c.category && (
                        <Badge variant="outline" className="text-[10px] text-slate-500">
                          {c.category}
                        </Badge>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Experiences */}
        {exps.length > 0 && (
          <Card data-testid="shared-experiences">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <Award className="w-5 h-5 text-[#1e3a5f]" />Experiences ({exps.length})
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {exps.map((e, idx) => (
                <div key={idx} className="p-4 rounded-lg border border-slate-200 bg-white" data-testid={`shared-exp-${idx}`}>
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h4 className="font-medium text-slate-900 text-sm">{e.title}</h4>
                      {e.organization && (
                        <p className="text-xs text-slate-500">{e.organization}</p>
                      )}
                    </div>
                    <div className="flex items-center gap-1 text-[10px] text-slate-400">
                      <Clock className="w-3 h-3" />
                      {e.start_date && <span>{e.start_date}</span>}
                      {e.end_date && <span> - {e.end_date}</span>}
                      {e.is_current && <Badge className="text-[10px] bg-emerald-50 text-emerald-600">En cours</Badge>}
                    </div>
                  </div>
                  {e.description && (
                    <p className="text-xs text-slate-600 mb-2">{e.description}</p>
                  )}
                  {e.skills_used?.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {e.skills_used.map((s, i) => (
                        <Badge key={i} className="text-[10px] bg-slate-100 text-slate-600">{s}</Badge>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        {/* Expiry notice */}
        {passport.share_info?.expires_at && (
          <div className="text-center text-xs text-slate-400 py-4" data-testid="share-expiry-notice">
            Ce lien expire le {new Date(passport.share_info.expires_at).toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" })}
          </div>
        )}

        {/* Footer */}
        <div className="flex flex-col items-center gap-3 py-6 border-t border-slate-200">
          <LogoReactifPro size="sm" />
          <p className="text-xs text-slate-400">
            Tiers de confiance numerique - Region Grand Est
          </p>
        </div>
      </div>
    </div>
  );
};

export default SharedPassportPage;
