import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Users, Globe, Heart, Sparkles, MessageCircle, Award, Target, Lightbulb,
  TrendingUp, CheckCircle, ArrowRight, ExternalLink
} from "lucide-react";

const UBUNTOO_COLORS = {
  bgDark: "#0d1117",
  bgCard: "rgba(255, 255, 255, 0.03)",
  bgCardHover: "rgba(255, 255, 255, 0.06)",
  textPrimary: "#f0f4fc",
  textSecondary: "rgba(240, 244, 252, 0.65)",
  orange: "#f97316",
  yellow: "#eab308",
  green: "#22c55e",
  cyan: "#06b6d4",
  blue: "#3b82f6",
  purple: "#8b5cf6",
  border: "rgba(255, 255, 255, 0.08)",
};

const fonctionnalites = [
  { icon: Users, title: "Communaut\u00e9 apprenante", description: "Rejoignez une communaut\u00e9 de professionnels engag\u00e9s dans le d\u00e9veloppement mutuel et l'entraide.", color: UBUNTOO_COLORS.orange },
  { icon: Award, title: "Badges d'exp\u00e9rience", description: "Valorisez vos comp\u00e9tences et votre parcours gr\u00e2ce \u00e0 un syst\u00e8me de reconnaissance par badges.", color: UBUNTOO_COLORS.yellow },
  { icon: MessageCircle, title: "\u00c9changes et partage", description: "Partagez vos exp\u00e9riences, posez vos questions et b\u00e9n\u00e9ficiez de l'intelligence collective.", color: UBUNTOO_COLORS.green },
  { icon: Target, title: "Accompagnement personnalis\u00e9", description: "Acc\u00e9dez \u00e0 des ressources et un accompagnement adapt\u00e9 \u00e0 votre parcours professionnel.", color: UBUNTOO_COLORS.cyan },
  { icon: Lightbulb, title: "Ressources et formations", description: "D\u00e9veloppez vos comp\u00e9tences gr\u00e2ce \u00e0 des contenus exclusifs et des formations cibl\u00e9es.", color: UBUNTOO_COLORS.blue },
  { icon: Globe, title: "R\u00e9seau solidaire", description: "Connectez-vous avec des acteurs engag\u00e9s pour une insertion professionnelle inclusive.", color: UBUNTOO_COLORS.purple },
];

const valeurs = [
  { icon: Users, label: "Ubuntu", description: "\"Je suis parce que nous sommes\" - La force du collectif", color: UBUNTOO_COLORS.orange },
  { icon: Heart, label: "Entraide", description: "Chacun apporte et re\u00e7oit dans un esprit de r\u00e9ciprocit\u00e9", color: UBUNTOO_COLORS.cyan },
  { icon: TrendingUp, label: "Croissance", description: "Grandir ensemble, personnellement et professionnellement", color: UBUNTOO_COLORS.purple },
];

const kpis = [
  { value: "+35%", label: "de r\u00e9ussite vs parcours isol\u00e9s", color: UBUNTOO_COLORS.green },
  { value: "-40%", label: "de sentiment d'isolement", color: UBUNTOO_COLORS.cyan },
  { value: "85%", label: "de satisfaction communaut\u00e9", color: UBUNTOO_COLORS.purple },
];

const parcours = [
  { num: 1, label: "Accompagn\u00e9", desc: "Vous recevez un soutien personnalis\u00e9", color: UBUNTOO_COLORS.orange },
  { num: 2, label: "Pair-aidant", desc: "Vous partagez votre exp\u00e9rience", color: UBUNTOO_COLORS.green },
  { num: 3, label: "Mentor", desc: "Vous structurez votre soutien", color: UBUNTOO_COLORS.cyan },
  { num: 4, label: "Ambassadeur", desc: "Vous repr\u00e9sentez l'insertion positive", color: UBUNTOO_COLORS.purple },
];

const UbuntooView = ({ token }) => {
  const [showPhilosophy, setShowPhilosophy] = useState(false);

  return (
    <div className="animate-fade-in" data-testid="ubuntoo-view" style={{ background: UBUNTOO_COLORS.bgDark, minHeight: "100vh", margin: "-1.5rem", padding: "2rem" }}>

      {/* Hero */}
      <div className="text-center py-12" data-testid="ubuntoo-hero">
        <img
          src="https://customer-assets.emergentagent.com/job_keen-meitner-5/artifacts/t3wjk59k_logo_ubuntoo_transparent.png"
          alt="Ubuntoo" className="h-20 mx-auto mb-6" style={{ filter: "drop-shadow(0 0 30px rgba(6, 182, 212, 0.3))" }}
        />
        <h1 className="text-3xl sm:text-4xl font-bold mb-4" style={{ color: UBUNTOO_COLORS.textPrimary, fontFamily: "Outfit, sans-serif" }}>
          "Je suis parce que nous sommes..."
        </h1>
        <p className="max-w-2xl mx-auto text-base leading-relaxed" style={{ color: UBUNTOO_COLORS.textSecondary }}>
          <strong style={{ color: UBUNTOO_COLORS.cyan }}>Ubuntoo</strong> est le r\u00e9seau social solidaire d'ALT&ACT, inspir\u00e9 de la philosophie Ubuntu.
          C'est un espace o\u00f9 chaque membre contribue \u00e0 l'enrichissement collectif
          tout en b\u00e9n\u00e9ficiant du soutien de la communaut\u00e9.
        </p>

        {/* KPIs */}
        <div className="flex flex-wrap justify-center gap-6 mt-8">
          {kpis.map((kpi, i) => (
            <div key={i} className="text-center px-6 py-4 rounded-xl" style={{ background: UBUNTOO_COLORS.bgCard, border: `1px solid ${UBUNTOO_COLORS.border}` }}>
              <div className="text-3xl font-bold" style={{ color: kpi.color }}>{kpi.value}</div>
              <div className="text-xs mt-1" style={{ color: UBUNTOO_COLORS.textSecondary }}>{kpi.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Philosophie Ubuntu (toggle) */}
      <div className="max-w-3xl mx-auto mb-10">
        <button
          onClick={() => setShowPhilosophy(!showPhilosophy)}
          className="w-full text-left px-6 py-4 rounded-xl transition-all"
          style={{ background: UBUNTOO_COLORS.bgCard, border: `1px solid ${UBUNTOO_COLORS.border}`, color: UBUNTOO_COLORS.textPrimary }}
          data-testid="ubuntoo-philosophy-toggle"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Sparkles className="w-5 h-5" style={{ color: UBUNTOO_COLORS.orange }} />
              <span className="font-semibold">Avez-vous d\u00e9j\u00e0 entendu parler de Ubuntu ?</span>
            </div>
            <ArrowRight className={`w-5 h-5 transition-transform ${showPhilosophy ? "rotate-90" : ""}`} style={{ color: UBUNTOO_COLORS.cyan }} />
          </div>
        </button>
        {showPhilosophy && (
          <div className="mt-2 px-6 py-5 rounded-xl text-sm leading-relaxed space-y-4" style={{ background: UBUNTOO_COLORS.bgCard, border: `1px solid ${UBUNTOO_COLORS.border}`, color: UBUNTOO_COLORS.textSecondary }}>
            <p>\u00ab Un anthropologue a propos\u00e9 un jeu \u00e0 des enfants d'une tribu d'Afrique australe. Il a pos\u00e9 un panier plein de fruits sucr\u00e9s pr\u00e8s d'un arbre et a dit aux enfants que le premier arriv\u00e9 remportait le panier. Quand il leur a dit de courir, ils se sont tous pris par la main et ont couru ensemble, puis se sont assis ensemble profitant de leurs friandises. Quand il leur a demand\u00e9 pourquoi ils n'avaient pas fait la course, ils ont r\u00e9pondu \u00ab <strong style={{ color: UBUNTOO_COLORS.orange }}>UBUNTU</strong> \u00bb, comment peut-on \u00eatre heureux si tous les autres sont tristes ? \u00bb</p>
            <p>\u00ab Ubuntu \u00bb dans la culture xhosa signifie : \u00ab Je suis parce que nous sommes \u00bb. Les Zoulous d'Afrique du Sud disent <em>"Umuntu ngumuntu ngabantu"</em> qui signifie \u00ab Je suis ce que je suis gr\u00e2ce \u00e0 ce que nous sommes tous \u00bb.</p>
            <p>En 2013, <strong style={{ color: UBUNTOO_COLORS.cyan }}>Obama</strong> parlait de cette philosophie lors des obs\u00e8ques de Mandela : \u00ab Nelson Mandela comprenait les liens qui unissent l'esprit humain. Il y a un mot en Afrique du Sud \u2013 Ubuntu \u2013 un mot qui incarne le plus grand don de Mandela. \u00bb</p>
            <p><strong style={{ color: UBUNTOO_COLORS.purple }}>Desmond Tutu</strong>, laur\u00e9at du prix Nobel de la paix, affirmait : \u00ab Quelqu'un d'ubuntu est ouvert et disponible pour les autres, d\u00e9vou\u00e9 aux autres, ne se sent pas menac\u00e9 parce que les autres sont capables et bons. \u00bb</p>
          </div>
        )}
      </div>

      {/* Valeurs */}
      <div className="max-w-4xl mx-auto mb-12">
        <h2 className="text-xl font-bold text-center mb-6" style={{ color: UBUNTOO_COLORS.textPrimary, fontFamily: "Outfit, sans-serif" }}>
          Nos valeurs fondatrices
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {valeurs.map((v, i) => {
            const Icon = v.icon;
            return (
              <div key={i} className="text-center p-6 rounded-xl transition-all hover:scale-[1.02]" style={{ background: UBUNTOO_COLORS.bgCard, border: `1px solid ${UBUNTOO_COLORS.border}` }}>
                <div className="w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3" style={{ background: `${v.color}20` }}>
                  <Icon className="w-6 h-6" style={{ color: v.color }} />
                </div>
                <h3 className="font-semibold mb-1" style={{ color: UBUNTOO_COLORS.textPrimary }}>{v.label}</h3>
                <p className="text-xs" style={{ color: UBUNTOO_COLORS.textSecondary }}>{v.description}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Fonctionnalit\u00e9s */}
      <div className="max-w-5xl mx-auto mb-12">
        <h2 className="text-xl font-bold text-center mb-6" style={{ color: UBUNTOO_COLORS.textPrimary, fontFamily: "Outfit, sans-serif" }}>
          Ce que vous offre Ubuntoo
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {fonctionnalites.map((item, i) => {
            const Icon = item.icon;
            return (
              <div key={i} className="p-5 rounded-xl transition-all hover:scale-[1.02] group" data-testid={`ubuntoo-feature-${i}`}
                style={{ background: UBUNTOO_COLORS.bgCard, border: `1px solid ${UBUNTOO_COLORS.border}` }}>
                <div className="w-10 h-10 rounded-lg flex items-center justify-center mb-3" style={{ background: `${item.color}20` }}>
                  <Icon className="w-5 h-5" style={{ color: item.color }} />
                </div>
                <h3 className="font-semibold text-sm mb-1" style={{ color: UBUNTOO_COLORS.textPrimary }}>{item.title}</h3>
                <p className="text-xs leading-relaxed" style={{ color: UBUNTOO_COLORS.textSecondary }}>{item.description}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Parcours de transformation */}
      <div className="max-w-4xl mx-auto mb-12">
        <h2 className="text-xl font-bold text-center mb-6" style={{ color: UBUNTOO_COLORS.textPrimary, fontFamily: "Outfit, sans-serif" }}>
          Votre parcours de transformation
        </h2>
        <div className="flex flex-wrap items-center justify-center gap-3">
          {parcours.map((step, i) => (
            <div key={i} className="flex items-center gap-3" data-testid={`ubuntoo-step-${i}`}>
              <div className="text-center p-4 rounded-xl min-w-[140px]" style={{ background: UBUNTOO_COLORS.bgCard, border: `1px solid ${UBUNTOO_COLORS.border}` }}>
                <div className="w-10 h-10 rounded-full flex items-center justify-center mx-auto mb-2 text-lg font-bold" style={{ background: `${step.color}20`, color: step.color }}>
                  {step.num}
                </div>
                <h4 className="font-semibold text-sm" style={{ color: UBUNTOO_COLORS.textPrimary }}>{step.label}</h4>
                <p className="text-[11px] mt-1" style={{ color: UBUNTOO_COLORS.textSecondary }}>{step.desc}</p>
              </div>
              {i < 3 && <span className="text-xl hidden sm:block" style={{ color: UBUNTOO_COLORS.cyan }}>\u2192</span>}
            </div>
          ))}
        </div>
      </div>

      {/* CTA */}
      <div className="max-w-2xl mx-auto text-center py-8 px-6 rounded-2xl mb-8" style={{ background: `linear-gradient(135deg, ${UBUNTOO_COLORS.cyan}15, ${UBUNTOO_COLORS.purple}15)`, border: `1px solid ${UBUNTOO_COLORS.border}` }}>
        <h2 className="text-xl font-bold mb-2" style={{ color: UBUNTOO_COLORS.textPrimary, fontFamily: "Outfit, sans-serif" }}>
          Rejoignez la communaut\u00e9 Ubuntoo
        </h2>
        <p className="text-sm mb-4" style={{ color: UBUNTOO_COLORS.textSecondary }}>
          Vous \u00eates connect\u00e9 avec votre compte RE'ACTIF PRO. L'espace communautaire Ubuntoo sera bient\u00f4t pleinement actif.
        </p>
        <div className="flex flex-wrap justify-center gap-3">
          <a href="https://declicpro-preview.preview.emergentagent.com/" target="_blank" rel="noopener noreferrer">
            <Button className="bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white gap-2" data-testid="ubuntoo-dclic-link">
              Acc\u00e9der \u00e0 D'CLIC PRO <ExternalLink className="w-4 h-4" />
            </Button>
          </a>
          <a href="https://www.alt-act.eu/" target="_blank" rel="noopener noreferrer">
            <Button variant="outline" className="text-white border-white/20 hover:bg-white/10 gap-2" data-testid="ubuntoo-altact-link">
              En savoir plus sur ALT&ACT <ExternalLink className="w-4 h-4" />
            </Button>
          </a>
        </div>
        <p className="text-[11px] mt-4" style={{ color: UBUNTOO_COLORS.textSecondary }}>
          * Plateforme en cours de d\u00e9ploiement - Disponible prochainement
        </p>
      </div>
    </div>
  );
};

export default UbuntooView;
