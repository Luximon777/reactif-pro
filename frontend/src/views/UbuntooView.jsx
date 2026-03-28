import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Users, User, Globe, Heart, Sparkles, MessageCircle, Award, Target, Lightbulb,
  TrendingUp, CheckCircle, ArrowRight, ExternalLink, Home, BarChart3, MessageSquare,
  ThumbsUp, Star, Send, Clock, HelpCircle, Reply, Hash
} from "lucide-react";

import LogoReactifPro from "@/components/LogoReactifPro";

const C = {
  bgDark: "#0d1117", bgCard: "rgba(255,255,255,0.03)", bgCardHover: "rgba(255,255,255,0.06)",
  textPrimary: "#f0f4fc", textSecondary: "rgba(240,244,252,0.65)",
  orange: "#f97316", yellow: "#eab308", green: "#22c55e", cyan: "#06b6d4",
  blue: "#3b82f6", purple: "#8b5cf6", border: "rgba(255,255,255,0.08)",
};

const LOGO = "https://customer-assets.emergentagent.com/job_keen-meitner-5/artifacts/t3wjk59k_logo_ubuntoo_transparent.png";

const initialUser = {
  name: "Marie Dupont", territory: "Grand Est", status: "Membre", trust: 62,
  badges: ["Pair-aidant (candidat)"], softskills: ["Empathie", "Adaptabilité", "Organisation"], contributions: 3,
};
const groups = [
  { id: "reconversion", title: "Reconversion", members: 1240, topics: 86, color: C.orange },
  { id: "handicap", title: "Handicap & Emploi", members: 640, topics: 41, color: C.cyan },
  { id: "numerique", title: "Métiers du Numérique", members: 980, topics: 63, color: C.purple },
  { id: "vsi", title: "Atelier VSI (Valoriser Son Identité pro)", members: 520, topics: 34, color: C.green },
];
const threads = [
  { id: "t1", type: "question", title: "Comment valoriser une expérience de bénévolat sur son CV ?", author: "Marie D.", group: "reconversion", views: 45, likes: 12, replies: 2, resolved: true, tags: ["CV", "Bénévolat"] },
  { id: "t2", type: "discussion", title: "Retour d'expérience : ma reconversion dans l'ESS", author: "Philippe R.", group: "reconversion", views: 234, likes: 67, replies: 2, resolved: false, tags: ["Témoignage", "ESS"] },
  { id: "t3", type: "aide", title: "Recherche mentor secteur numérique", author: "Lucas T.", group: "numerique", views: 28, likes: 4, replies: 0, resolved: false, tags: ["Mentorat", "Développement"] },
];
const mentors = [
  { id: "m1", name: "Jean-Pierre Martin", focus: "Reconversion", availability: "1h/sem", rating: 4.8 },
  { id: "m2", name: "Amina Benali", focus: "Entretien & confiance", availability: "1h/sem", rating: 4.9 },
];
const helpRequests = [
  { id: 1, group: "reconversion", title: "Besoin d'aide pour structurer mon projet", author: "Thomas L.", replies: 2 },
  { id: 2, group: "numerique", title: "Préparer un entretien dev junior", author: "Sarah M.", replies: 5 },
  { id: 3, group: "vsi", title: "Comment valoriser une reconversion ?", author: "Pierre D.", replies: 3 },
];

const cardStyle = { background: C.bgCard, border: `1px solid ${C.border}`, borderRadius: "12px" };
const hoverCard = "transition-all duration-200 hover:scale-[1.01]";

// ============ ACCUEIL ============
const AccueilTab = () => (
  <div className="space-y-10">
    {/* Hero */}
    <div className="flex flex-col md:flex-row items-center gap-8 py-8">
      <img src={LOGO} alt="Ubuntoo" className="h-32 md:h-40" style={{ filter: "drop-shadow(0 0 40px rgba(6,182,212,0.3))" }} />
      <div>
        <h1 className="text-3xl md:text-4xl font-bold mb-4" style={{ color: C.textPrimary, fontFamily: "Outfit, sans-serif" }}>
          "Je suis parce que nous sommes..."
        </h1>
        <p style={{ color: C.textSecondary }} className="leading-relaxed">
          <strong style={{ color: C.cyan }}>Ubuntoo</strong> est le réseau social solidaire d'ALT&ACT, inspiré de la philosophie Ubuntu.
          C'est un espace où chaque membre contribue à l'enrichissement collectif tout en bénéficiant du soutien de la communauté.
        </p>
      </div>
    </div>

    {/* Philosophie */}
    <div className="p-6 rounded-xl space-y-4 text-sm leading-relaxed" style={{ ...cardStyle, color: C.textSecondary }}>
      <h3 className="font-semibold text-base flex items-center gap-2" style={{ color: C.orange }}>
        <Sparkles className="w-5 h-5" /> La philosophie Ubuntu
      </h3>
      <p>« Un anthropologue a proposé un jeu à des enfants d'une tribu d'Afrique australe. Il a posé un panier plein de fruits sucrés près d'un arbre et a dit aux enfants que le premier arrivé remportait le panier. Quand il leur a dit de courir, ils se sont tous pris par la main et ont couru ensemble, puis se sont assis ensemble profitant de leurs friandises. Quand il leur a demandé pourquoi ils n'avaient pas fait la course, ils ont répondu « <strong style={{ color: C.orange }}>UBUNTU</strong> », comment peut-on être heureux si tous les autres sont tristes ? »</p>
      <p>« Ubuntu » dans la culture xhosa signifie : « Je suis parce que nous sommes ». L'ubuntu est une philosophie d'origine bantu qui existe dans plusieurs cultures africaines sous la dénomination du « Bomoto » en lingala, du « Kimuntu » en kikongo, du « Butu » en punu, et de « Ubuntu » en kirundi et kinyarwanda.</p>
      <p>Les Zoulous d'Afrique du Sud disent <em>"Umuntu ngumuntu ngabantu"</em> qui signifie « Je suis ce que je suis grâce à ce que nous sommes tous ».</p>
      <p>En 2013, <strong style={{ color: C.cyan }}>Obama</strong> parlait de cette philosophie lors des obsèques de Mandela : « Nelson Mandela comprenait les liens qui unissent l'esprit humain. Il y a un mot en Afrique du Sud – Ubuntu – un mot qui incarne le plus grand don de Mandela. »</p>
      <p><strong style={{ color: C.purple }}>Desmond Tutu</strong>, lauréat du prix Nobel de la paix, affirmait : « Quelqu'un d'ubuntu est ouvert et disponible pour les autres, dévoué aux autres, ne se sent pas menacé parce que les autres sont capables et bons car il ou elle possède sa propre estime de soi — qui vient de la connaissance qu'il ou elle a d'appartenir à quelque chose de plus grand. »</p>
    </div>

    {/* Valeurs */}
    <div>
      <h2 className="text-xl font-bold text-center mb-6" style={{ color: C.textPrimary, fontFamily: "Outfit, sans-serif" }}>Nos valeurs fondatrices</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          { icon: Users, label: "Ubuntu", desc: "\"Je suis parce que nous sommes\" - La force du collectif", color: C.orange },
          { icon: Heart, label: "Entraide", desc: "Chacun apporte et reçoit dans un esprit de réciprocité", color: C.cyan },
          { icon: TrendingUp, label: "Croissance", desc: "Grandir ensemble, personnellement et professionnellement", color: C.purple },
        ].map((v, i) => (
          <div key={i} className={`text-center p-6 rounded-xl ${hoverCard}`} style={cardStyle}>
            <div className="w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3" style={{ background: `${v.color}20` }}>
              <v.icon className="w-6 h-6" style={{ color: v.color }} />
            </div>
            <h3 className="font-semibold mb-1" style={{ color: C.textPrimary }}>{v.label}</h3>
            <p className="text-xs" style={{ color: C.textSecondary }}>{v.desc}</p>
          </div>
        ))}
      </div>
    </div>

    {/* KPIs */}
    <div className="flex flex-wrap justify-center gap-6">
      {[
        { value: "+35%", label: "de réussite vs parcours isolés", color: C.green },
        { value: "-40%", label: "de sentiment d'isolement", color: C.cyan },
        { value: "85%", label: "de satisfaction communauté", color: C.purple },
      ].map((k, i) => (
        <div key={i} className="text-center px-8 py-5 rounded-xl" style={cardStyle}>
          <div className="text-3xl font-bold" style={{ color: k.color }}>{k.value}</div>
          <div className="text-xs mt-1" style={{ color: C.textSecondary }}>{k.label}</div>
        </div>
      ))}
    </div>

    {/* Fonctionnalités */}
    <div>
      <h2 className="text-xl font-bold text-center mb-6" style={{ color: C.textPrimary, fontFamily: "Outfit, sans-serif" }}>Ce que vous offre Ubuntoo</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {[
          { icon: Users, title: "Communauté apprenante", desc: "Rejoignez une communauté de professionnels engagés dans le développement mutuel et l'entraide.", color: C.orange },
          { icon: Award, title: "Badges d'expérience", desc: "Valorisez vos compétences et votre parcours grâce à un système de reconnaissance par badges.", color: C.yellow },
          { icon: MessageCircle, title: "Échanges et partage", desc: "Partagez vos expériences, posez vos questions et bénéficiez de l'intelligence collective.", color: C.green },
          { icon: Target, title: "Accompagnement personnalisé", desc: "Accédez à des ressources et un accompagnement adapté à votre parcours professionnel.", color: C.cyan },
          { icon: Lightbulb, title: "Ressources et formations", desc: "Développez vos compétences grâce à des contenus exclusifs et des formations ciblées.", color: C.blue },
          { icon: Globe, title: "Réseau solidaire", desc: "Connectez-vous avec des acteurs engagés pour une insertion professionnelle inclusive.", color: C.purple },
        ].map((f, i) => (
          <div key={i} className={`p-5 rounded-xl ${hoverCard}`} style={cardStyle} data-testid={`ubuntoo-feature-${i}`}>
            <div className="w-10 h-10 rounded-lg flex items-center justify-center mb-3" style={{ background: `${f.color}20` }}>
              <f.icon className="w-5 h-5" style={{ color: f.color }} />
            </div>
            <h3 className="font-semibold text-sm mb-1" style={{ color: C.textPrimary }}>{f.title}</h3>
            <p className="text-xs leading-relaxed" style={{ color: C.textSecondary }}>{f.desc}</p>
          </div>
        ))}
      </div>
    </div>

    {/* Parcours */}
    <div>
      <h2 className="text-xl font-bold text-center mb-6" style={{ color: C.textPrimary, fontFamily: "Outfit, sans-serif" }}>Votre parcours de transformation</h2>
      <div className="flex flex-wrap items-center justify-center gap-3">
        {[
          { num: 1, label: "Accompagné", desc: "Vous recevez un soutien personnalisé", color: C.orange },
          { num: 2, label: "Pair-aidant", desc: "Vous partagez votre expérience", color: C.green },
          { num: 3, label: "Mentor", desc: "Vous structurez votre soutien", color: C.cyan },
          { num: 4, label: "Ambassadeur", desc: "Vous représentez l'insertion positive", color: C.purple },
        ].map((s, i) => (
          <div key={i} className="flex items-center gap-3">
            <div className="text-center p-4 rounded-xl min-w-[140px]" style={cardStyle}>
              <div className="w-10 h-10 rounded-full flex items-center justify-center mx-auto mb-2 text-lg font-bold" style={{ background: `${s.color}20`, color: s.color }}>{s.num}</div>
              <h4 className="font-semibold text-sm" style={{ color: C.textPrimary }}>{s.label}</h4>
              <p className="text-[11px] mt-1" style={{ color: C.textSecondary }}>{s.desc}</p>
            </div>
            {i < 3 && <span className="text-xl hidden sm:block" style={{ color: C.cyan }}>→</span>}
          </div>
        ))}
      </div>
    </div>

    {/* CTA */}
    <div className="text-center py-8 px-6 rounded-2xl" style={{ background: `linear-gradient(135deg, ${C.cyan}15, ${C.purple}15)`, border: `1px solid ${C.border}` }}>
      <h2 className="text-xl font-bold mb-2" style={{ color: C.textPrimary }}>Rejoignez la communauté Ubuntoo</h2>
      <p className="text-sm mb-4" style={{ color: C.textSecondary }}>Vous êtes connecté avec votre compte RE'ACTIF PRO. L'espace communautaire sera bientôt pleinement actif.</p>
      <div className="flex flex-wrap justify-center gap-3">
        <a href="https://declicpro-preview.preview.emergentagent.com/" target="_blank" rel="noopener noreferrer">
          <Button className="bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white gap-2">Accéder à D'CLIC PRO <ExternalLink className="w-4 h-4" /></Button>
        </a>
        <a href="https://www.alt-act.eu/" target="_blank" rel="noopener noreferrer">
          <Button variant="outline" className="text-white border-white/20 hover:bg-white/10 gap-2">En savoir plus sur ALT&ACT <ExternalLink className="w-4 h-4" /></Button>
        </a>
      </div>
      <p className="text-[11px] mt-4" style={{ color: C.textSecondary }}>* Plateforme en cours de déploiement - Disponible prochainement</p>
    </div>
  </div>
);

// ============ PROFIL ============
const ProfilTab = ({ user, setUser }) => {
  const statuses = ["Membre", "Membre actif", "Pair-aidant", "Mentor", "Ambassadeur"];
  const currentIdx = statuses.indexOf(user.status);

  const upgradeStatus = () => {
    if (currentIdx < statuses.length - 1) {
      setUser(prev => ({ ...prev, status: statuses[currentIdx + 1], trust: Math.min(100, prev.trust + 15), badges: [...prev.badges, statuses[currentIdx + 1]] }));
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold" style={{ color: C.textPrimary, fontFamily: "Outfit, sans-serif" }}>Profil Contributif</h1>

      <div className="p-6 rounded-xl flex flex-col md:flex-row items-start gap-6" style={cardStyle}>
        <div className="w-16 h-16 rounded-full flex items-center justify-center text-xl font-bold flex-shrink-0" style={{ background: `${C.cyan}30`, color: C.cyan }}>
          {user.name.split(" ").map(n => n[0]).join("")}
        </div>
        <div className="flex-1 space-y-3">
          <div>
            <h2 className="text-xl font-bold" style={{ color: C.textPrimary }}>{user.name}</h2>
            <p className="text-sm" style={{ color: C.textSecondary }}>{user.territory}</p>
          </div>
          <Badge style={{ background: `${C.green}20`, color: C.green, border: `1px solid ${C.green}40` }}>{user.status}</Badge>
          <div>
            <p className="text-xs mb-1" style={{ color: C.textSecondary }}>Indice de confiance</p>
            <div className="flex items-center gap-3">
              <div className="flex-1 h-2 rounded-full overflow-hidden" style={{ background: C.bgCardHover }}>
                <div className="h-full rounded-full" style={{ width: `${user.trust}%`, background: `linear-gradient(to right, ${C.cyan}, ${C.green})` }} />
              </div>
              <span className="text-sm font-bold" style={{ color: C.cyan }}>{user.trust}%</span>
            </div>
          </div>
          <Button size="sm" onClick={upgradeStatus} style={{ background: `${C.purple}20`, color: C.purple, border: `1px solid ${C.purple}40` }} data-testid="upgrade-status">
            Simuler progression de statut
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-5 rounded-xl" style={cardStyle}>
          <h3 className="font-semibold mb-3 flex items-center gap-2" style={{ color: C.textPrimary }}><Sparkles className="w-4 h-4" style={{ color: C.cyan }} /> Soft Skills</h3>
          <div className="flex flex-wrap gap-2">
            {user.softskills.map((s, i) => (
              <Badge key={i} style={{ background: `${C.blue}20`, color: C.blue, border: `1px solid ${C.blue}40` }}>{s}</Badge>
            ))}
          </div>
        </div>
        <div className="p-5 rounded-xl" style={cardStyle}>
          <h3 className="font-semibold mb-3 flex items-center gap-2" style={{ color: C.textPrimary }}><Award className="w-4 h-4" style={{ color: C.yellow }} /> Badges d'expérience</h3>
          <div className="flex flex-wrap gap-2">
            {user.badges.map((b, i) => (
              <Badge key={i} style={{ background: `${C.yellow}20`, color: C.yellow, border: `1px solid ${C.yellow}40` }}>{b}</Badge>
            ))}
          </div>
        </div>
        <div className="p-5 rounded-xl" style={cardStyle}>
          <h3 className="font-semibold mb-3" style={{ color: C.textPrimary }}>Contributions</h3>
          <div className="text-3xl font-bold" style={{ color: C.green }}>{user.contributions}</div>
          <p className="text-xs" style={{ color: C.textSecondary }}>aides apportées à la communauté</p>
        </div>
        <div className="p-5 rounded-xl" style={cardStyle}>
          <h3 className="font-semibold mb-3" style={{ color: C.textPrimary }}>Parcours de Progression</h3>
          <div className="flex flex-wrap gap-2">
            {statuses.map((s, i) => (
              <Badge key={i} style={{ background: i <= currentIdx ? `${C.green}20` : C.bgCard, color: i <= currentIdx ? C.green : C.textSecondary, border: `1px solid ${i <= currentIdx ? C.green : C.border}40` }}>{s}</Badge>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// ============ GROUPES ============
const GroupesTab = ({ user }) => {
  const [selected, setSelected] = useState(null);
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold" style={{ color: C.textPrimary, fontFamily: "Outfit, sans-serif" }}>Groupes Thématiques</h1>
      <p style={{ color: C.textSecondary }}>Rejoignez une communauté de professionnels engagés dans le développement mutuel et l'entraide.</p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {groups.map(g => (
          <div key={g.id} className={`p-5 rounded-xl cursor-pointer ${hoverCard}`} style={{ ...cardStyle, borderTopColor: g.color, borderTopWidth: "3px" }}
            onClick={() => setSelected(g.id)} data-testid={`group-${g.id}`}>
            <h3 className="font-semibold mb-2" style={{ color: C.textPrimary }}>{g.title}</h3>
            <div className="flex gap-4 text-xs mb-3" style={{ color: C.textSecondary }}>
              <span><Users className="w-3 h-3 inline mr-1" />{g.members} membres</span>
              <span><MessageCircle className="w-3 h-3 inline mr-1" />{g.topics} sujets</span>
            </div>
            <Button size="sm" style={{ background: `${g.color}20`, color: g.color, border: `1px solid ${g.color}40` }}>Rejoindre</Button>
          </div>
        ))}
      </div>

      {selected && (
        <div className="p-5 rounded-xl space-y-3" style={cardStyle}>
          <h3 className="font-semibold" style={{ color: C.textPrimary }}>Échanges - {groups.find(g => g.id === selected)?.title}</h3>
          {helpRequests.filter(r => r.group === selected).map(r => (
            <div key={r.id} className="p-3 rounded-lg" style={{ background: C.bgCardHover }}>
              <h4 className="font-medium text-sm" style={{ color: C.textPrimary }}>{r.title}</h4>
              <p className="text-xs mt-1" style={{ color: C.textSecondary }}>par {r.author} · {r.replies} réponses</p>
            </div>
          ))}
          {helpRequests.filter(r => r.group === selected).length === 0 && (
            <p className="text-sm" style={{ color: C.textSecondary }}>Aucun échange dans ce groupe pour le moment.</p>
          )}
        </div>
      )}
    </div>
  );
};

// ============ DISCUSSIONS ============
const DiscussionsTab = () => {
  const [filter, setFilter] = useState("all");
  const filtered = threads.filter(t => filter === "all" || t.type === filter);
  const typeIcon = (t) => t === "question" ? <HelpCircle className="w-4 h-4" /> : t === "aide" ? <Heart className="w-4 h-4" /> : <MessageSquare className="w-4 h-4" />;
  const typeColor = (t) => t === "question" ? C.blue : t === "aide" ? C.orange : C.green;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold" style={{ color: C.textPrimary, fontFamily: "Outfit, sans-serif" }}>Espace Discussions</h1>
      <p style={{ color: C.textSecondary }}>Forum d'entraide, questions-réponses et messagerie de la communauté Ubuntoo</p>

      <div className="flex gap-2 flex-wrap">
        {[{ k: "all", l: "Tous" }, { k: "question", l: "Questions" }, { k: "discussion", l: "Discussions" }, { k: "aide", l: "Entraide" }].map(f => (
          <Button key={f.k} size="sm" onClick={() => setFilter(f.k)}
            style={{ background: filter === f.k ? `${C.cyan}30` : C.bgCard, color: filter === f.k ? C.cyan : C.textSecondary, border: `1px solid ${filter === f.k ? C.cyan : C.border}` }}>
            {f.l}
          </Button>
        ))}
      </div>

      <div className="space-y-3">
        {filtered.map(t => (
          <div key={t.id} className={`p-4 rounded-xl ${hoverCard}`} style={cardStyle} data-testid={`thread-${t.id}`}>
            <div className="flex items-start gap-3">
              <div className="mt-1" style={{ color: typeColor(t.type) }}>{typeIcon(t.type)}</div>
              <div className="flex-1">
                <div className="flex items-center gap-2 flex-wrap">
                  <h3 className="font-semibold text-sm" style={{ color: C.textPrimary }}>{t.title}</h3>
                  {t.resolved && <Badge style={{ background: `${C.green}20`, color: C.green, fontSize: "10px" }}>Résolu</Badge>}
                </div>
                <div className="flex items-center gap-3 mt-1 text-xs" style={{ color: C.textSecondary }}>
                  <span>{t.author}</span>
                  <span><ThumbsUp className="w-3 h-3 inline mr-0.5" />{t.likes}</span>
                  <span><MessageCircle className="w-3 h-3 inline mr-0.5" />{t.replies}</span>
                  <span><Clock className="w-3 h-3 inline mr-0.5" />{t.views} vues</span>
                </div>
                <div className="flex gap-1 mt-2">
                  {t.tags.map((tag, i) => <Badge key={i} style={{ background: C.bgCardHover, color: C.textSecondary, fontSize: "10px" }}><Hash className="w-3 h-3 mr-0.5" />{tag}</Badge>)}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// ============ MENTORAT ============
const MentoratTab = () => (
  <div className="space-y-6">
    <h1 className="text-2xl font-bold" style={{ color: C.textPrimary, fontFamily: "Outfit, sans-serif" }}>Mentorat</h1>
    <p style={{ color: C.textSecondary }}>Trouvez un mentor pour vous accompagner dans votre parcours professionnel.</p>
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {mentors.map(m => (
        <div key={m.id} className={`p-5 rounded-xl ${hoverCard}`} style={cardStyle} data-testid={`mentor-${m.id}`}>
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-full flex items-center justify-center text-lg font-bold" style={{ background: `${C.purple}30`, color: C.purple }}>
              {m.name.split(" ").map(n => n[0]).join("")}
            </div>
            <div>
              <h3 className="font-semibold" style={{ color: C.textPrimary }}>{m.name}</h3>
              <p className="text-xs" style={{ color: C.textSecondary }}>Spécialité : {m.focus}</p>
              <p className="text-xs" style={{ color: C.textSecondary }}>Disponibilité : {m.availability}</p>
              <div className="flex items-center gap-1 mt-1">
                <Star className="w-3.5 h-3.5" style={{ color: C.yellow, fill: C.yellow }} />
                <span className="text-xs font-medium" style={{ color: C.yellow }}>{m.rating}</span>
              </div>
            </div>
          </div>
          <Button size="sm" className="mt-4 w-full" style={{ background: `${C.cyan}20`, color: C.cyan, border: `1px solid ${C.cyan}40` }}>
            Demander un mentorat
          </Button>
        </div>
      ))}
    </div>
  </div>
);

// ============ IMPACT ============
const ImpactTab = () => (
  <div className="space-y-6">
    <h1 className="text-2xl font-bold" style={{ color: C.textPrimary, fontFamily: "Outfit, sans-serif" }}>Impact Social</h1>
    <p style={{ color: C.textSecondary }}>Mesurer notre impact collectif sur l'insertion et l'inclusion professionnelle.</p>
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {[
        { label: "Membres actifs", value: "12 450", target: "Objectif 50 000 (3 ans)", pct: 25, color: C.cyan },
        { label: "Taux de réussite", value: "+35%", target: "vs parcours isolés", pct: 70, color: C.green },
        { label: "Réduction isolement", value: "-40%", target: "de sentiment d'isolement", pct: 60, color: C.blue },
        { label: "Satisfaction", value: "85%", target: "de la communauté", pct: 85, color: C.purple },
        { label: "Mentors actifs", value: "124", target: "sur la plateforme", pct: 45, color: C.orange },
        { label: "Groupes actifs", value: "4", target: "thématiques", pct: 80, color: C.yellow },
      ].map((s, i) => (
        <div key={i} className="p-5 rounded-xl" style={cardStyle} data-testid={`impact-${i}`}>
          <p className="text-xs mb-1" style={{ color: C.textSecondary }}>{s.label}</p>
          <div className="text-2xl font-bold mb-2" style={{ color: s.color }}>{s.value}</div>
          <div className="h-1.5 rounded-full overflow-hidden mb-1" style={{ background: C.bgCardHover }}>
            <div className="h-full rounded-full" style={{ width: `${s.pct}%`, background: s.color }} />
          </div>
          <p className="text-[11px]" style={{ color: C.textSecondary }}>{s.target}</p>
        </div>
      ))}
    </div>
  </div>
);

// ============ MAIN VIEW ============
const UbuntooView = ({ token }) => {
  const [tab, setTab] = useState("accueil");
  const [user, setUser] = useState(initialUser);

  const tabs = [
    { id: "accueil", label: "Accueil", icon: Home },
    { id: "profil", label: "Profil", icon: User },
    { id: "groupes", label: "Groupes", icon: Users },
    { id: "discussions", label: "Discussions", icon: MessageSquare },
    { id: "mentorat", label: "Mentorat", icon: Heart },
    { id: "impact", label: "Impact", icon: BarChart3 },
  ];

  return (
    <div data-testid="ubuntoo-view" style={{ background: C.bgDark, minHeight: "100vh", margin: "-1.5rem", padding: "0" }}>
      {/* Navigation */}
      <nav className="sticky top-0 z-10 flex items-center gap-1 px-4 py-2 overflow-x-auto" style={{ background: "rgba(13,17,23,0.95)", borderBottom: `1px solid ${C.border}`, backdropFilter: "blur(8px)" }}>
        <div className="flex items-center gap-2 mr-4 flex-shrink-0">
          <LogoReactifPro size="sm" />
          <span style={{ color: C.textSecondary, fontSize: "11px" }}>×</span>
          <img src={LOGO} alt="Ubuntoo" className="h-6" />
        </div>
        {tabs.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)} data-testid={`ubuntoo-tab-${t.id}`}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium whitespace-nowrap transition-all"
            style={{ background: tab === t.id ? `${C.cyan}20` : "transparent", color: tab === t.id ? C.cyan : C.textSecondary }}>
            <t.icon className="w-4 h-4" />
            {t.label}
          </button>
        ))}
      </nav>

      {/* Content */}
      <div className="p-4 md:p-6 max-w-5xl mx-auto">
        {tab === "accueil" && <AccueilTab />}
        {tab === "profil" && <ProfilTab user={user} setUser={setUser} />}
        {tab === "groupes" && <GroupesTab user={user} />}
        {tab === "discussions" && <DiscussionsTab />}
        {tab === "mentorat" && <MentoratTab />}
        {tab === "impact" && <ImpactTab />}
      </div>
    </div>
  );
};

export default UbuntooView;
