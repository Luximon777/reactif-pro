import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, ArrowRight, CheckCircle, Copy, Check, Home, ChevronRight, Calendar, GraduationCap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";

const API = process.env.REACT_APP_BACKEND_URL + "/api";

// ============================================================================
// RESULTS SECTIONS
// ============================================================================

const SECTIONS = [
  { id: "archeologie", label: "Archéologie des Compétences" },
  { id: "boussole", label: "Boussole de Fonctionnement" },
  { id: "integrated", label: "Analyse Intégrée" },
  { id: "riasec", label: "Profil RIASEC" },
  { id: "vertus", label: "Profil de Vertus" },
  { id: "pistes", label: "Pistes d'Action" },
  { id: "cross", label: "Analyse Croisée" },
  { id: "ofman", label: "Cadran d'Ofman" },
  { id: "carte", label: "Carte d'Identité Pro" },
];

// Simple bar component
const Bar = ({ label, value, max = 100, color = "bg-indigo-500" }) => (
  <div className="space-y-1">
    <div className="flex justify-between text-xs"><span className="text-slate-600">{label}</span><span className="font-medium text-slate-700">{value}%</span></div>
    <div className="h-2.5 bg-slate-100 rounded-full overflow-hidden"><div className={`h-full rounded-full ${color}`} style={{ width: `${Math.min(value, 100)}%` }} /></div>
  </div>
);

// Compass axis component
const CompassAxis = ({ axis }) => {
  const pct = axis.dominant === axis.pole_a?.code ? 75 : 25;
  return (
    <div className="bg-white rounded-lg p-3 border">
      <p className="text-sm font-semibold text-slate-800 mb-2">{axis.name}</p>
      <div className="flex items-center gap-2 text-xs mb-1">
        <span className={`font-medium ${pct > 50 ? "text-indigo-700" : "text-slate-400"}`}>{axis.pole_a?.label}</span>
        <div className="flex-1 h-3 bg-slate-100 rounded-full relative">
          <div className="absolute h-3 bg-indigo-500 rounded-full" style={{ width: `${pct}%` }} />
        </div>
        <span className={`font-medium ${pct <= 50 ? "text-indigo-700" : "text-slate-400"}`}>{axis.pole_b?.label}</span>
      </div>
      <p className="text-xs text-slate-500 mt-1">{axis.insight}</p>
    </div>
  );
};

// Section: Archéologie des Compétences
const ArcheologieSection = ({ profile }) => {
  const vp = profile.vertus_profile || {};
  const vertuData = profile.vertu_data || {};
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-bold text-slate-800">Archéologie des Compétences</h3>
      <p className="text-sm text-slate-500">Vos compétences profondes à travers 3 dimensions fondamentales.</p>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {[
          { title: "Cognition", desc: "Comment vous pensez et apprenez", color: "bg-blue-50 border-blue-200", items: vp.qualites_dominantes || [] },
          { title: "Conation", desc: "Ce qui vous met en mouvement", color: "bg-amber-50 border-amber-200", items: vp.savoirs_etre_dominants || [] },
          { title: "Affection", desc: "Ce qui vous touche et vous motive", color: "bg-rose-50 border-rose-200", items: vertuData.qualites_humaines || vp.qualites_dominantes || [] },
        ].map((dim, i) => (
          <Card key={i} className={`${dim.color} border`}>
            <CardContent className="p-4">
              <h4 className="font-semibold text-sm text-slate-800">{dim.title}</h4>
              <p className="text-xs text-slate-500 mb-2">{dim.desc}</p>
              <div className="flex flex-wrap gap-1">
                {dim.items.slice(0, 5).map((item, j) => (
                  <Badge key={j} variant="outline" className="text-xs">{typeof item === "string" ? item : item.name || item.label || ""}</Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
      {(vp.competences_oms || []).length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-slate-700 mb-2">Compétences clés OMS</h4>
          <div className="flex flex-wrap gap-1.5">
            {vp.competences_oms.map((c, i) => <Badge key={i} className="bg-indigo-100 text-indigo-700 text-xs">{c}</Badge>)}
          </div>
        </div>
      )}
    </div>
  );
};

// Section: Boussole de Fonctionnement
const BoussoleSection = ({ profile }) => {
  const compass = profile.compass || {};
  const axes = compass.axes || [];
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-bold text-slate-800">Boussole de Fonctionnement</h3>
      <p className="text-sm text-slate-500">Vos préférences cognitives sur 4 axes fondamentaux.</p>
      <div className="bg-indigo-50 rounded-lg p-3 border border-indigo-200">
        <p className="text-sm font-semibold text-indigo-800">Profil global : {profile.mbti || "?"}</p>
        {compass.summary && <p className="text-xs text-indigo-600 mt-1">{compass.summary}</p>}
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {axes.map((axis, i) => <CompassAxis key={i} axis={axis} />)}
      </div>
    </div>
  );
};

// Section: Analyse Intégrée
const IntegratedSection = ({ profile }) => {
  const ia = profile.integrated_analysis || {};
  const n1 = ia.niveau_1_preuves || {};
  const n2 = ia.niveau_2_fonctionnement || {};
  const n3 = ia.niveau_3_regulation || {};
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-bold text-slate-800">Analyse Intégrée (3 niveaux)</h3>
      {/* Level 1 */}
      <Card className="border-blue-200 bg-blue-50/50">
        <CardContent className="p-4">
          <h4 className="font-semibold text-blue-800 mb-2">Niveau 1 — Compétences prouvées</h4>
          {n1.competences_prouvees?.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mb-2">
              {n1.competences_prouvees.map((c, i) => <Badge key={i} className="bg-blue-100 text-blue-700 text-xs">{c}</Badge>)}
            </div>
          )}
          {n1.forces_cles?.length > 0 && (
            <div><p className="text-xs font-medium text-slate-600 mb-1">Forces clés :</p>
              <div className="flex flex-wrap gap-1">{n1.forces_cles.map((f, i) => <Badge key={i} variant="outline" className="text-xs border-blue-300">{f}</Badge>)}</div>
            </div>
          )}
        </CardContent>
      </Card>
      {/* Level 2 */}
      <Card className="border-emerald-200 bg-emerald-50/50">
        <CardContent className="p-4">
          <h4 className="font-semibold text-emerald-800 mb-2">Niveau 2 — Style de travail</h4>
          {n2.style_travail && <p className="text-sm text-emerald-700 mb-2">{n2.style_travail}</p>}
          {n2.environnement_favorable?.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {n2.environnement_favorable.map((e, i) => <Badge key={i} className="bg-emerald-100 text-emerald-700 text-xs">{e}</Badge>)}
            </div>
          )}
        </CardContent>
      </Card>
      {/* Level 3 */}
      <Card className="border-amber-200 bg-amber-50/50">
        <CardContent className="p-4">
          <h4 className="font-semibold text-amber-800 mb-2">Niveau 3 — Régulation</h4>
          {n3.moteur_interne && <p className="text-sm text-amber-700"><strong>Moteur interne :</strong> {n3.moteur_interne}</p>}
          {n3.leviers_croissance?.length > 0 && (
            <div className="mt-2"><p className="text-xs font-medium text-slate-600 mb-1">Leviers de croissance :</p>
              <div className="flex flex-wrap gap-1">{n3.leviers_croissance.map((l, i) => <Badge key={i} variant="outline" className="text-xs border-amber-300">{l}</Badge>)}</div>
            </div>
          )}
          {n3.signaux_stress?.length > 0 && (
            <div className="mt-2"><p className="text-xs font-medium text-red-600 mb-1">Signaux de stress :</p>
              <div className="flex flex-wrap gap-1">{n3.signaux_stress.map((s, i) => <Badge key={i} className="bg-red-50 text-red-600 text-xs">{s}</Badge>)}</div>
            </div>
          )}
        </CardContent>
      </Card>
      {ia.synthese && <p className="text-sm text-slate-600 italic bg-slate-50 p-3 rounded-lg">{ia.synthese}</p>}
    </div>
  );
};

// Section: RIASEC
const RiasecSection = ({ profile }) => {
  const rp = profile.riasec_profile || {};
  const scores = rp.scores || {};
  const labels = { R: "Réaliste", I: "Investigateur", A: "Artistique", S: "Social", E: "Entreprenant", C: "Conventionnel" };
  const colors = { R: "bg-orange-500", I: "bg-blue-500", A: "bg-purple-500", S: "bg-emerald-500", E: "bg-red-500", C: "bg-slate-500" };
  const maxScore = Math.max(...Object.values(scores), 1);
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-bold text-slate-800">Profil RIASEC</h3>
      <div className="bg-indigo-50 rounded-lg p-3 border border-indigo-200">
        <p className="text-lg font-bold text-indigo-800">{rp.major_name || rp.major || "?"} / {rp.minor_name || rp.minor || "?"}</p>
        {rp.major_description && <p className="text-sm text-indigo-600 mt-1">{rp.major_description}</p>}
      </div>
      <div className="space-y-2">
        {Object.entries(scores).sort((a, b) => b[1] - a[1]).map(([key, val]) => (
          <Bar key={key} label={`${key} - ${labels[key] || key}`} value={Math.round((val / maxScore) * 100)} color={colors[key] || "bg-indigo-500"} />
        ))}
      </div>
      {rp.traits?.length > 0 && (
        <div><p className="text-sm font-semibold text-slate-700 mb-1">Traits dominants</p>
          <div className="flex flex-wrap gap-1.5">{rp.traits.map((t, i) => <Badge key={i} className="bg-violet-100 text-violet-700 text-xs">{t}</Badge>)}</div>
        </div>
      )}
      {rp.environnements_preferes?.length > 0 && (
        <div><p className="text-sm font-semibold text-slate-700 mb-1">Environnements préférés</p>
          <div className="flex flex-wrap gap-1.5">{rp.environnements_preferes.map((e, i) => <Badge key={i} variant="outline" className="text-xs">{e}</Badge>)}</div>
        </div>
      )}
    </div>
  );
};

// Section: Vertus
const VertusSection = ({ profile }) => {
  const vp = profile.vertus_profile || {};
  const scores = vp.vertus_scores || {};
  const labels = { sagesse: "Sagesse", courage: "Courage", humanite: "Humanité", justice: "Justice", temperance: "Tempérance", transcendance: "Transcendance" };
  const colors = { sagesse: "bg-blue-500", courage: "bg-red-500", humanite: "bg-rose-500", justice: "bg-emerald-500", temperance: "bg-amber-500", transcendance: "bg-purple-500" };
  const maxScore = Math.max(...Object.values(scores), 1);
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-bold text-slate-800">Profil de Vertus</h3>
      <p className="text-sm text-slate-500">Seligman & Peterson — Les 6 vertus fondamentales</p>
      <div className="bg-emerald-50 rounded-lg p-3 border border-emerald-200">
        <p className="text-sm font-semibold text-emerald-800">Vertu dominante : {vp.dominant_name || vp.vertu_dominante_name || labels[vp.dominant] || "?"}</p>
      </div>
      <div className="space-y-2">
        {Object.entries(scores).sort((a, b) => b[1] - a[1]).map(([key, val]) => (
          <Bar key={key} label={labels[key] || key} value={Math.round((val / maxScore) * 100)} color={colors[key] || "bg-indigo-500"} />
        ))}
      </div>
      {vp.qualites_dominantes?.length > 0 && (
        <div><p className="text-sm font-semibold text-slate-700 mb-1">Qualités humaines associées</p>
          <div className="flex flex-wrap gap-1.5">{vp.qualites_dominantes.map((q, i) => <Badge key={i} className="bg-emerald-100 text-emerald-700 text-xs">{typeof q === "string" ? q : q.name || ""}</Badge>)}</div>
        </div>
      )}
    </div>
  );
};

// Section: Pistes d'Action
const PistesSection = ({ profile }) => {
  const lp = profile.life_path || {};
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-bold text-slate-800">Pistes d'Action</h3>
      <div className="bg-violet-50 rounded-lg p-3 border border-violet-200">
        <p className="text-sm font-semibold text-violet-800">{lp.label || "Développement personnel"}</p>
      </div>
      {lp.strengths?.length > 0 && (
        <div><p className="text-sm font-semibold text-emerald-700 mb-1">Forces naturelles</p>
          <div className="flex flex-wrap gap-1.5">{lp.strengths.map((s, i) => <Badge key={i} className="bg-emerald-100 text-emerald-700 text-xs">{s}</Badge>)}</div>
        </div>
      )}
      {lp.watchouts?.length > 0 && (
        <div><p className="text-sm font-semibold text-amber-700 mb-1">Points de vigilance</p>
          <div className="flex flex-wrap gap-1.5">{lp.watchouts.map((w, i) => <Badge key={i} className="bg-amber-100 text-amber-700 text-xs">{w}</Badge>)}</div>
        </div>
      )}
      {lp.micro_actions?.length > 0 && (
        <div><p className="text-sm font-semibold text-slate-700 mb-2">Pistes pour progresser</p>
          <div className="space-y-2">
            {lp.micro_actions.map((ma, i) => (
              <div key={i} className="bg-white border rounded-lg p-3">
                <Badge className="bg-indigo-100 text-indigo-700 text-xs mb-1">{ma.focus}</Badge>
                <p className="text-sm text-slate-700">{ma.action}</p>
              </div>
            ))}
          </div>
        </div>
      )}
      {lp.work_preferences?.length > 0 && (
        <div><p className="text-sm font-semibold text-blue-700 mb-1">Environnements favorables</p>
          <div className="flex flex-wrap gap-1.5">{lp.work_preferences.map((wp, i) => <Badge key={i} variant="outline" className="text-xs border-blue-300">{wp}</Badge>)}</div>
        </div>
      )}
    </div>
  );
};

// Section: Analyse Croisée
const CrossSection = ({ profile }) => {
  const ca = profile.cross_analysis || {};
  if (!ca.has_cross_analysis) return <p className="text-sm text-slate-400">Renseignez votre date de naissance pour accéder à l'analyse croisée.</p>;
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-bold text-slate-800">Analyse Croisée</h3>
      <Card className="border-blue-200 bg-blue-50/50"><CardContent className="p-4">
        <h4 className="text-sm font-semibold text-blue-800 mb-1">Synergie - Style de travail</h4>
        <p className="text-sm text-blue-700">{ca.synergy_disc}</p>
      </CardContent></Card>
      <Card className="border-emerald-200 bg-emerald-50/50"><CardContent className="p-4">
        <h4 className="text-sm font-semibold text-emerald-800 mb-1">Synergie - Moteur intérieur</h4>
        <p className="text-sm text-emerald-700">{ca.synergy_ennea}</p>
      </CardContent></Card>
      {ca.tension && <Card className="border-amber-200 bg-amber-50/50"><CardContent className="p-4">
        <h4 className="text-sm font-semibold text-amber-800 mb-1">Tension à transformer</h4>
        <p className="text-sm text-amber-700">{ca.tension}</p>
      </CardContent></Card>}
      {ca.integration_insight && <p className="text-sm text-violet-700 italic bg-violet-50 p-3 rounded-lg">{ca.integration_insight}</p>}
    </div>
  );
};

// Section: Cadran d'Ofman
const OfmanSection = ({ profile }) => {
  const zones = profile.ofman_quadrant || [];
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-bold text-slate-800">Cadran d'Ofman — Zones de vigilance</h3>
      <p className="text-sm text-slate-500">Vos qualités peuvent devenir des pièges si elles sont poussées à l'extrême.</p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {zones.map((z, i) => (
          <Card key={i} className="border">
            <CardContent className="p-4 space-y-2">
              <div className="flex items-center justify-between">
                <Badge className="bg-emerald-100 text-emerald-700 text-xs">{z.qualite}</Badge>
                <span className="text-[10px] text-slate-400">{z.source}</span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="bg-red-50 rounded p-2"><p className="font-semibold text-red-700">Piège</p><p className="text-red-600">{z.piege}</p></div>
                <div className="bg-blue-50 rounded p-2"><p className="font-semibold text-blue-700">Défi</p><p className="text-blue-600">{z.defi}</p></div>
              </div>
              <div className="bg-amber-50 rounded p-2 text-xs"><p className="font-semibold text-amber-700">Allergie</p><p className="text-amber-600">{z.allergie}</p></div>
              {z.recommandation && <p className="text-xs text-slate-600 italic">{z.recommandation}</p>}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

// Section: Carte d'Identité Pro
const CarteSection = ({ profile, accessCode }) => {
  const vp = profile.vertus_profile || {};
  const rp = profile.riasec_profile || {};
  const ia = profile.integrated_analysis || {};
  const lp = profile.life_path || {};
  const n1 = ia.niveau_1_preuves || {};
  const n3 = ia.niveau_3_regulation || {};
  const compass = profile.compass || {};
  const today = new Date().toLocaleDateString("fr-FR");

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-slate-800">Carte d'Identité Professionnelle</h3>
          <p className="text-sm text-slate-500">Synthèse de votre profil — 4 dimensions</p>
        </div>
      </div>

      {/* Main Card */}
      <div className="bg-[#1a1a2e] rounded-2xl overflow-hidden shadow-xl text-white">
        {/* Header */}
        <div className="px-6 pt-5 pb-3 flex items-center justify-between">
          <h2 className="text-2xl font-bold tracking-wide">PROFIL D'CLIC PRO</h2>
          <div className="text-right text-xs">
            <p className="font-bold text-indigo-300">RE'ACTIF PRO</p>
          </div>
        </div>

        {/* 4 Quadrants */}
        <div className="grid grid-cols-1 md:grid-cols-2">
          {/* Identité Personnelle */}
          <div className="px-6 py-4 border-r border-b border-white/10">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-purple-400 text-lg">&#9734;</span>
              <h4 className="text-sm font-bold text-purple-400 uppercase tracking-wider">Identité Personnelle</h4>
            </div>
            <div className="space-y-3">
              <div>
                <p className="text-[10px] uppercase tracking-wider text-slate-400 mb-1">Qualités Humaines</p>
                <div className="flex flex-wrap gap-1.5">
                  {(vp.qualites_dominantes || []).slice(0, 4).map((q, i) => (
                    <span key={i} className="text-xs bg-white/10 rounded-full px-2.5 py-0.5 text-slate-200">{typeof q === "string" ? q : q.name || ""}</span>
                  ))}
                </div>
              </div>
              <div>
                <p className="text-[10px] uppercase tracking-wider text-slate-400 mb-1">Valeurs</p>
                <div className="flex flex-wrap gap-1.5">
                  {(vp.valeurs_dominantes || []).slice(0, 3).map((v, i) => (
                    <span key={i} className="text-xs bg-white/10 rounded-full px-2.5 py-0.5 text-slate-200">{typeof v === "string" ? v : v.name || ""}</span>
                  ))}
                </div>
              </div>
              <div>
                <p className="text-[10px] uppercase tracking-wider text-slate-400">Ce qui me rend unique</p>
                <p className="text-base font-bold text-white">{vp.dominant_name || vp.vertu_dominante_name || "?"}</p>
              </div>
            </div>
          </div>

          {/* Identité Professionnelle */}
          <div className="px-6 py-4 border-b border-white/10">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-amber-400 text-lg">&#9960;</span>
              <h4 className="text-sm font-bold text-amber-400 uppercase tracking-wider">Identité Professionnelle</h4>
            </div>
            <div className="space-y-3">
              <div>
                <p className="text-[10px] uppercase tracking-wider text-slate-400 mb-1">Savoir-être</p>
                <div className="flex flex-wrap gap-1.5">
                  {(vp.savoirs_etre_dominants || n1.competences_prouvees || []).slice(0, 4).map((s, i) => (
                    <span key={i} className="text-xs bg-white/10 rounded-full px-2.5 py-0.5 text-slate-200">{typeof s === "string" ? s : s.name || ""}</span>
                  ))}
                </div>
              </div>
              <div>
                <p className="text-[10px] uppercase tracking-wider text-slate-400 mb-1">Compétences clés</p>
                <div className="flex flex-wrap gap-1.5">
                  {(vp.competences_oms || n1.forces_cles || []).slice(0, 4).map((c, i) => (
                    <span key={i} className="text-xs bg-white/10 rounded-full px-2.5 py-0.5 text-slate-200">{c}</span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Identité Sociale */}
          <div className="px-6 py-4 border-r border-white/10">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-emerald-400 text-lg">&#9825;</span>
              <h4 className="text-sm font-bold text-emerald-400 uppercase tracking-wider">Identité Sociale</h4>
            </div>
            <div className="space-y-3">
              <div>
                <p className="text-[10px] uppercase tracking-wider text-slate-400 mb-1">Mes rôles</p>
                <div className="flex flex-wrap gap-1.5">
                  {(rp.traits || ["Contributeur", "Collaborateur"]).slice(0, 3).map((r, i) => (
                    <span key={i} className="text-xs bg-white/10 rounded-full px-2.5 py-0.5 text-slate-200">{r}</span>
                  ))}
                </div>
              </div>
              <div>
                <p className="text-[10px] uppercase tracking-wider text-slate-400 mb-1">Impact social</p>
                <div className="flex flex-wrap gap-1.5">
                  {(lp.work_preferences || rp.environnements_preferes || []).slice(0, 3).map((w, i) => (
                    <span key={i} className="text-xs bg-white/10 rounded-full px-2.5 py-0.5 text-slate-200">{w}</span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Identité Profonde */}
          <div className="px-6 py-4">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-blue-400 text-lg">&#9788;</span>
              <h4 className="text-sm font-bold text-blue-400 uppercase tracking-wider">Identité Profonde</h4>
            </div>
            <div className="space-y-3">
              <div>
                <p className="text-[10px] uppercase tracking-wider text-slate-400">Ce qui donne du sens</p>
                <p className="text-base font-bold text-white">{lp.label || n3.moteur_interne || "Développement"}</p>
              </div>
              <div>
                <p className="text-[10px] uppercase tracking-wider text-slate-400 mb-1">Ma mission</p>
                <div className="flex flex-wrap gap-1.5">
                  {(lp.strengths || []).slice(0, 3).map((s, i) => (
                    <span key={i} className="text-xs bg-white/10 rounded-full px-2.5 py-0.5 text-slate-200">{s}</span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-white/5 flex items-center justify-between border-t border-white/10">
          <div className="flex items-center gap-3">
            <div className="flex gap-1">
              {[...Array(4)].map((_, i) => <div key={i} className="w-2.5 h-2.5 rounded-full bg-indigo-400" />)}
            </div>
            <div>
              <p className="text-[10px] text-slate-400">PROFIL</p>
              <p className="text-sm font-bold">{profile.mbti || "?"} · {profile.disc_label || profile.disc || "?"}</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-[10px] text-emerald-400 font-bold">Profil vérifié</p>
            <p className="text-[10px] text-slate-400">ID {accessCode || "---"} · {today}</p>
          </div>
        </div>
      </div>

      {/* Synthesis */}
      {compass.summary && (
        <Card className="border border-slate-200">
          <CardContent className="p-5">
            <h4 className="text-sm font-bold text-slate-800 mb-2 flex items-center gap-2">
              <span>&#127760;</span> Synthèse Professionnelle
            </h4>
            <p className="text-sm text-slate-600 leading-relaxed">{compass.summary}</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

// ============================================================================
// MAIN COMPONENT
// ============================================================================

const DclicTestPage = () => {
  const navigate = useNavigate();
  const [questions, setQuestions] = useState([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [answers, setAnswers] = useState({});
  const [rankingSelections, setRankingSelections] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [codeCopied, setCodeCopied] = useState(false);
  const [activeSection, setActiveSection] = useState("archeologie");
  // Pre-questionnaire
  const [step, setStep] = useState("intro"); // intro, birthdate, education, questionnaire, results
  const [birthDate, setBirthDate] = useState("");
  const [educationLevel, setEducationLevel] = useState("");
  const sectionRefs = useRef({});

  useEffect(() => {
    fetch(`${API}/dclic/questionnaire`).then(r => r.json()).then(d => setQuestions(d.questions || []));
  }, []);

  const q = questions[currentIdx];
  const progress = questions.length ? ((currentIdx + 1) / questions.length) * 100 : 0;
  const isRanking = q?.type === "ranking";
  const currentRanking = rankingSelections[q?.id] || [];
  const maxRank = isRanking ? Math.min(4, q.choices?.length || 4) : 0;
  const canProceed = isRanking ? currentRanking.length === maxRank : !!answers[q?.id];

  const handleAnswer = (val) => setAnswers(prev => ({ ...prev, [q.id]: val }));

  const handleRankingSelect = (choice) => {
    const qid = q.id;
    const sels = rankingSelections[qid] || [];
    const existIdx = sels.findIndex(s => s.value === choice.value);
    if (existIdx !== -1) {
      const next = sels.filter(s => s.value !== choice.value).map((s, i) => ({ ...s, rank: i + 1 }));
      setRankingSelections(p => ({ ...p, [qid]: next }));
      if (answers[qid]) setAnswers(p => { const c = { ...p }; delete c[qid]; return c; });
    } else if (sels.length < maxRank) {
      const next = [...sels, { ...choice, rank: sels.length + 1 }];
      setRankingSelections(p => ({ ...p, [qid]: next }));
      if (next.length === maxRank) setAnswers(p => ({ ...p, [qid]: next.map(s => s.value).join(",") }));
    }
  };

  const getRank = (val) => { const s = (rankingSelections[q?.id] || []).find(x => x.value === val); return s ? s.rank : null; };

  const handleNext = async () => {
    if (currentIdx < questions.length - 1) { setCurrentIdx(i => i + 1); return; }
    setIsSubmitting(true);
    setStep("loading");
    try {
      const res = await fetch(`${API}/dclic/submit`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answers, birth_date: birthDate || null, education_level: educationLevel || null })
      });
      const data = await res.json();
      setResult(data);
      setStep("results");
    } catch (e) { console.error(e); setStep("questionnaire"); }
    setIsSubmitting(false);
  };

  const copyCode = () => { if (result?.access_code) { navigator.clipboard.writeText(result.access_code); setCodeCopied(true); setTimeout(() => setCodeCopied(false), 3000); } };

  // INTRO SCREEN
  if (step === "intro") return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-blue-50 flex items-center justify-center p-4">
      <Card className="max-w-lg w-full" data-testid="dclic-intro">
        <CardContent className="p-8 text-center space-y-6">
          <h1 className="text-2xl font-bold text-[#1e3a5f]">Test D'CLIC PRO</h1>
          <p className="text-slate-600">Découvrez votre profil de personnalité et compétences professionnelles en répondant à {questions.length || "~26"} questions visuelles.</p>
          <p className="text-sm text-slate-400">Durée estimée : 5-10 minutes</p>
          <Button className="w-full bg-indigo-600 hover:bg-indigo-700" onClick={() => setStep("birthdate")} data-testid="start-test-btn">Commencer le test <ArrowRight className="w-4 h-4 ml-2" /></Button>
          <Button variant="ghost" className="w-full" onClick={() => navigate(-1)}>Retour</Button>
        </CardContent>
      </Card>
    </div>
  );

  // BIRTHDATE
  if (step === "birthdate") return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-blue-50 flex items-center justify-center p-4">
      <Card className="max-w-lg w-full" data-testid="dclic-birthdate">
        <CardContent className="p-8 space-y-6">
          <div className="flex items-center gap-2 text-slate-400 text-sm"><Calendar className="w-4 h-4" />Étape 1/2</div>
          <h2 className="text-xl font-bold text-slate-900">Quelle est votre date de naissance ?</h2>
          <p className="text-sm text-slate-500">Optionnel — permet une analyse croisée plus approfondie.</p>
          <Input type="date" value={birthDate} onChange={e => setBirthDate(e.target.value)} className="text-lg" data-testid="birth-date-input" />
          <div className="flex gap-3">
            <Button variant="outline" className="flex-1" onClick={() => setStep("intro")}>Retour</Button>
            <Button className="flex-1 bg-indigo-600" onClick={() => setStep("education")}>Suivant <ArrowRight className="w-4 h-4 ml-1" /></Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  // EDUCATION
  if (step === "education") return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-blue-50 flex items-center justify-center p-4">
      <Card className="max-w-lg w-full" data-testid="dclic-education">
        <CardContent className="p-8 space-y-6">
          <div className="flex items-center gap-2 text-slate-400 text-sm"><GraduationCap className="w-4 h-4" />Étape 2/2</div>
          <h2 className="text-xl font-bold text-slate-900">Quel est votre niveau d'études ?</h2>
          <div className="grid grid-cols-2 gap-3">
            {[
              { value: "cap", label: "Sans diplôme / CAP / BEP" },
              { value: "bac", label: "Bac / Bac Pro" },
              { value: "bac2", label: "Bac+2 (BTS, DUT)" },
              { value: "bac3", label: "Bac+3 (Licence)" },
              { value: "bac5", label: "Bac+5 (Master)" },
              { value: "bac8", label: "Bac+8 (Doctorat)" },
            ].map(opt => (
              <button key={opt.value} className={`p-3 rounded-lg border-2 text-left transition-all ${educationLevel === opt.value ? "border-indigo-500 bg-indigo-50" : "border-slate-200 hover:border-slate-300"}`}
                onClick={() => setEducationLevel(opt.value)} data-testid={`edu-${opt.value}`}>
                <p className="text-sm font-medium text-slate-800">{opt.label}</p>
              </button>
            ))}
          </div>
          <div className="flex gap-3">
            <Button variant="outline" className="flex-1" onClick={() => setStep("birthdate")}>Retour</Button>
            <Button className="flex-1 bg-indigo-600" onClick={() => setStep("questionnaire")} data-testid="start-questions-btn">Démarrer les questions <ArrowRight className="w-4 h-4 ml-1" /></Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  // LOADING
  if (step === "loading") return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-blue-50 flex items-center justify-center p-4">
      <Card className="max-w-lg w-full" data-testid="dclic-loading">
        <CardContent className="p-8 text-center space-y-6">
          <div className="w-16 h-16 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mx-auto" />
          <h2 className="text-xl font-bold text-slate-900">Analyse de votre profil en cours...</h2>
          <p className="text-sm text-slate-500">Notre IA analyse vos réponses et génère votre rapport personnalisé. Cette opération peut prendre quelques secondes.</p>
        </CardContent>
      </Card>
    </div>
  );

  // RESULTS
  if (step === "results" && result) {
    const p = result.profile || {};
    const renderSection = () => {
      switch (activeSection) {
        case "archeologie": return <ArcheologieSection profile={p} />;
        case "boussole": return <BoussoleSection profile={p} />;
        case "integrated": return <IntegratedSection profile={p} />;
        case "riasec": return <RiasecSection profile={p} />;
        case "vertus": return <VertusSection profile={p} />;
        case "pistes": return <PistesSection profile={p} />;
        case "cross": return <CrossSection profile={p} />;
        case "ofman": return <OfmanSection profile={p} />;
        case "carte": return <CarteSection profile={p} accessCode={result.access_code} />;
        default: return null;
      }
    };
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-blue-50">
        <div className="max-w-6xl mx-auto px-4 py-6">
          {/* Header */}
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between mb-6 gap-4">
            <div>
              <h1 className="text-2xl font-bold text-[#1e3a5f]">Résultats D'CLIC PRO</h1>
              <p className="text-sm text-slate-500">Votre profil de personnalité et compétences professionnelles</p>
            </div>
            <div className="flex items-center gap-3">
              <div className="bg-indigo-100 rounded-lg px-4 py-2 flex items-center gap-2" data-testid="dclic-code-display">
                <span className="text-xs text-indigo-600">Code :</span>
                <span className="font-mono font-bold text-indigo-800 text-lg" data-testid="dclic-code">{result.access_code}</span>
                <button onClick={copyCode} className="text-indigo-500 hover:text-indigo-700">{codeCopied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}</button>
              </div>
              <Button className="bg-[#1e3a5f]" onClick={() => navigate("/dashboard")} data-testid="go-dashboard-btn"><Home className="w-4 h-4 mr-1" />Dashboard</Button>
            </div>
          </div>

          <div className="flex flex-col lg:flex-row gap-6">
            {/* Sidebar navigation */}
            <nav className="lg:w-64 shrink-0">
              <div className="bg-white rounded-xl border shadow-sm p-2 lg:sticky lg:top-4 space-y-0.5">
                {SECTIONS.map((s, i) => (
                  <button key={s.id} onClick={() => setActiveSection(s.id)}
                    className={`w-full text-left px-3 py-2 rounded-lg text-sm flex items-center gap-2 transition-all ${activeSection === s.id ? "bg-indigo-50 text-indigo-700 font-semibold" : "text-slate-600 hover:bg-slate-50"}`}
                    data-testid={`nav-${s.id}`}>
                    <span className={`w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold ${activeSection === s.id ? "bg-indigo-600 text-white" : "bg-slate-200 text-slate-500"}`}>{i + 1}</span>
                    {s.label}
                  </button>
                ))}
              </div>
            </nav>
            {/* Content */}
            <main className="flex-1 bg-white rounded-xl border shadow-sm p-6" data-testid="results-content">
              {renderSection()}
            </main>
          </div>
        </div>
      </div>
    );
  }

  // QUESTIONNAIRE
  if (step !== "questionnaire" || !q) return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-white flex items-center justify-center">
      <p className="text-slate-500 animate-pulse text-lg">Chargement...</p>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-blue-50">
      <div className="max-w-2xl mx-auto px-4 py-6 space-y-6">
        <div className="flex items-center justify-between">
          <Button variant="ghost" size="sm" onClick={() => currentIdx > 0 ? setCurrentIdx(i => i - 1) : setStep("education")} data-testid="back-btn"><ArrowLeft className="w-4 h-4 mr-1" />Retour</Button>
          <span className="text-sm text-slate-500 font-medium">Question {currentIdx + 1} / {questions.length}</span>
        </div>
        <Progress value={progress} className="h-2" />
        <div className="space-y-2 text-center">
          <Badge variant="outline" className="text-xs">{q.category === "energie" ? "Énergie" : q.category === "perception" ? "Perception" : q.category === "decision" ? "Décision" : q.category === "structure" ? "Organisation" : q.category === "disc" ? "Style DISC" : q.category === "ennea" ? "Motivations" : q.category === "riasec" ? "Intérêts RIASEC" : q.category === "vertus" ? "Vertus" : q.category === "valeurs" ? "Valeurs" : q.category}</Badge>
          <h2 className="text-xl font-bold text-slate-900">{q.question}</h2>
          {q.instruction && <p className="text-sm text-slate-500">{q.instruction}</p>}
        </div>
        {isRanking ? (
          <div className="space-y-3">
            <div className="flex justify-center gap-2 mb-2">
              {Array.from({ length: maxRank }, (_, n) => (
                <span key={n} className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${currentRanking.length > n ? "bg-indigo-600 text-white" : "bg-slate-200 text-slate-400"}`}>{n + 1}</span>
              ))}
            </div>
            <div className={`grid ${q.choices[0]?.image ? "grid-cols-2" : "grid-cols-1"} gap-3`}>
              {q.choices.map(choice => {
                const rank = getRank(choice.value);
                const sel = rank !== null;
                return (
                  <button key={choice.id} disabled={!sel && currentRanking.length >= maxRank}
                    className={`relative rounded-xl border-2 p-3 text-left transition-all ${sel ? "border-indigo-500 bg-indigo-50 shadow-md" : "border-slate-200 hover:border-slate-300 bg-white"} ${!sel && currentRanking.length >= maxRank ? "opacity-40" : "cursor-pointer"}`}
                    onClick={() => handleRankingSelect(choice)} data-testid={`choice-${choice.id}`}>
                    {sel && <span className="absolute -top-2 -right-2 w-7 h-7 rounded-full bg-indigo-600 text-white text-sm font-bold flex items-center justify-center">{rank}</span>}
                    {choice.image && <img src={choice.image} alt={choice.alt || ""} className="w-full h-28 object-cover rounded-lg mb-2" loading="lazy" />}
                    <p className="text-sm font-medium text-slate-800">{choice.label}</p>
                  </button>
                );
              })}
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-4">
            {q.choices.map(choice => {
              const sel = answers[q.id] === choice.value;
              return (
                <button key={choice.id}
                  className={`relative rounded-xl border-2 p-4 transition-all ${sel ? "border-indigo-500 bg-indigo-50 shadow-lg ring-2 ring-indigo-200" : "border-slate-200 hover:border-indigo-300 bg-white hover:shadow-md"} cursor-pointer`}
                  onClick={() => handleAnswer(choice.value)} data-testid={`choice-${choice.id}`}>
                  {choice.image && <img src={choice.image} alt={choice.alt || ""} className="w-full h-36 object-cover rounded-lg mb-3" loading="lazy" />}
                  <p className="text-sm font-semibold text-slate-800 text-center">{choice.label}</p>
                  {sel && <CheckCircle className="absolute top-2 right-2 w-6 h-6 text-indigo-600" />}
                </button>
              );
            })}
          </div>
        )}
        <Button className="w-full bg-indigo-600 hover:bg-indigo-700 text-white" disabled={!canProceed || isSubmitting}
          onClick={handleNext} data-testid="next-btn">
          {isSubmitting ? "Analyse en cours..." : currentIdx === questions.length - 1 ? "Voir mes résultats" : (<>Suivant <ArrowRight className="w-4 h-4 ml-1" /></>)}
        </Button>
      </div>
    </div>
  );
};

export default DclicTestPage;
