import { useState } from "react";
import {
  Users, User, Globe, Heart, Sparkles, MessageCircle, Award, Target, Lightbulb,
  TrendingUp, CheckCircle, ArrowRight, ExternalLink, Home, BarChart3, MessageSquare,
  ThumbsUp, Star, Send, Clock, HelpCircle, Hash
} from "lucide-react";
import LogoReactifPro from "@/components/LogoReactifPro";
import "./UbuntooView.css";

const LOGO = "https://customer-assets.emergentagent.com/job_keen-meitner-5/artifacts/t3wjk59k_logo_ubuntoo_transparent.png";

const initialUser = {
  name: "Marie Dupont", territory: "Grand Est", status: "Membre", trust: 62,
  badges: ["Pair-aidant (candidat)"], softskills: ["Empathie", "Adaptabilit\u00e9", "Organisation"], contributions: 3,
};
const groups = [
  { id: "reconversion", title: "Reconversion", members: 1240, topics: 86, colorClass: "orange" },
  { id: "handicap", title: "Handicap & Emploi", members: 640, topics: 41, colorClass: "cyan" },
  { id: "numerique", title: "M\u00e9tiers du Num\u00e9rique", members: 980, topics: 63, colorClass: "purple" },
  { id: "vsi", title: "Atelier VSI (Valoriser Son Identit\u00e9 pro)", members: 520, topics: 34, colorClass: "green" },
];
const threads = [
  { id: "t1", type: "question", title: "Comment valoriser une exp\u00e9rience de b\u00e9n\u00e9volat sur son CV ?", author: "Marie D.", group: "reconversion", views: 45, likes: 12, replies: 2, resolved: true, tags: ["CV", "B\u00e9n\u00e9volat"] },
  { id: "t2", type: "discussion", title: "Retour d'exp\u00e9rience : ma reconversion dans l'ESS", author: "Philippe R.", group: "reconversion", views: 234, likes: 67, replies: 2, resolved: false, tags: ["T\u00e9moignage", "ESS"] },
  { id: "t3", type: "aide", title: "Recherche mentor secteur num\u00e9rique", author: "Lucas T.", group: "numerique", views: 28, likes: 4, replies: 0, resolved: false, tags: ["Mentorat", "D\u00e9veloppement"] },
];
const mentors = [
  { id: "m1", name: "Jean-Pierre Martin", focus: "Reconversion", availability: "1h/sem", rating: 4.8 },
  { id: "m2", name: "Amina Benali", focus: "Entretien & confiance", availability: "1h/sem", rating: 4.9 },
];
const helpRequests = [
  { id: 1, group: "reconversion", title: "Besoin d'aide pour structurer mon projet", author: "Thomas L.", replies: 2 },
  { id: 2, group: "numerique", title: "Pr\u00e9parer un entretien dev junior", author: "Sarah M.", replies: 5 },
  { id: 3, group: "vsi", title: "Comment valoriser une reconversion ?", author: "Pierre D.", replies: 3 },
];

// ============ ACCUEIL ============
const AccueilTab = () => (
  <div>
    {/* Hero */}
    <div className="ub-hero">
      <div className="ub-hero-content">
        <img src={LOGO} alt="Ubuntoo" className="ub-hero-logo" style={{ filter: "drop-shadow(0 0 40px rgba(6,182,212,0.3))" }} />
        <div className="ub-hero-text">
          <h1 className="ub-hero-title">{'"'}Je suis parce que nous sommes...{'"'}</h1>
          <p className="ub-hero-subtitle">
            <span className="ub-tooltip">
              <strong>Ubuntoo</strong>
              <span className="ub-tooltip-content">
                <strong>La philosophie Ubuntu</strong>
                {`Un anthropologue a propos\u00e9 un jeu \u00e0 des enfants d'une tribu d'Afrique australe. Il a pos\u00e9 un panier plein de fruits sucr\u00e9s pr\u00e8s d'un arbre et a dit aux enfants que le premier arriv\u00e9 remportait le panier. Quand il leur a dit de courir, ils se sont tous pris par la main et ont couru ensemble, puis se sont assis ensemble profitant de leurs friandises.`}
                <br /><br />
                {`Quand il leur a demand\u00e9 pourquoi ils n'avaient pas fait la course, ils ont r\u00e9pondu `}<em>{'"'}UBUNTU{'"'}</em>{`, comment peut-on \u00eatre heureux si tous les autres sont tristes ?`}
                <br /><br />
                <em>{`\u00ab Ubuntu \u00bb`}</em>{` dans la culture xhosa signifie : \u00ab Je suis parce que nous sommes \u00bb.`}
                <br /><br />
                {`En 2013, `}<em>Obama</em>{` parlait de cette philosophie lors des obs\u00e8ques de Mandela : \u00ab Nelson Mandela comprenait les liens qui unissent l'esprit humain. \u00bb`}
                <br /><br />
                <em>Desmond Tutu</em>{`, laur\u00e9at du prix Nobel de la paix, affirmait : \u00ab Quelqu'un d'ubuntu est ouvert et disponible pour les autres. \u00bb`}
              </span>
            </span>{" "}
            {`est le r\u00e9seau social solidaire d'ALT&ACT, inspir\u00e9 de la philosophie Ubuntu. C'est un espace o\u00f9 chaque membre contribue \u00e0 l'enrichissement collectif tout en b\u00e9n\u00e9ficiant du soutien de la communaut\u00e9.`}
          </p>
        </div>
      </div>
    </div>

    {/* Valeurs */}
    <div className="ub-values">
      <h2>Nos valeurs fondatrices</h2>
      <div className="ub-values-grid">
        {[
          { icon: Users, label: "Ubuntu", desc: `"Je suis parce que nous sommes" - La force du collectif`, colorClass: "orange" },
          { icon: Heart, label: "Entraide", desc: `Chacun apporte et re\u00e7oit dans un esprit de r\u00e9ciprocit\u00e9`, colorClass: "cyan" },
          { icon: TrendingUp, label: "Croissance", desc: "Grandir ensemble, personnellement et professionnellement", colorClass: "purple" },
        ].map((v, i) => (
          <div key={i} className={`ub-value-card ${v.colorClass}`} data-testid={`ubuntoo-value-${i}`}>
            <v.icon size={32} />
            <h3>{v.label}</h3>
            <p>{v.desc}</p>
          </div>
        ))}
      </div>
    </div>

    {/* KPIs */}
    <div className="ub-kpi-grid">
      {[
        { value: "+35%", label: `de r\u00e9ussite vs parcours isol\u00e9s`, colorClass: "orange", icon: TrendingUp },
        { value: "-40%", label: "de sentiment d'isolement", colorClass: "cyan", icon: Heart },
        { value: "85%", label: `de satisfaction communaut\u00e9`, colorClass: "purple", icon: Star },
      ].map((k, i) => (
        <div key={i} className={`ub-kpi-card ${k.colorClass}`} data-testid={`ubuntoo-kpi-${i}`}>
          <k.icon size={28} />
          <div className="ub-kpi-value">{k.value}</div>
          <div className="ub-kpi-label">{k.label}</div>
        </div>
      ))}
    </div>

    {/* Fonctionnalités */}
    <div className="ub-offers">
      <h2>Ce que vous offre Ubuntoo</h2>
      <div className="ub-offers-grid">
        {[
          { icon: Users, title: "Communaut\u00e9 apprenante", desc: `Rejoignez une communaut\u00e9 de professionnels engag\u00e9s dans le d\u00e9veloppement mutuel et l'entraide.` },
          { icon: Award, title: "Badges d'exp\u00e9rience", desc: `Valorisez vos comp\u00e9tences et votre parcours gr\u00e2ce \u00e0 un syst\u00e8me de reconnaissance par badges.` },
          { icon: MessageCircle, title: "\u00c9changes et partage", desc: `Partagez vos exp\u00e9riences, posez vos questions et b\u00e9n\u00e9ficiez de l'intelligence collective.` },
          { icon: Target, title: "Accompagnement personnalis\u00e9", desc: `Acc\u00e9dez \u00e0 des ressources et un accompagnement adapt\u00e9 \u00e0 votre parcours professionnel.` },
          { icon: Lightbulb, title: "Ressources et formations", desc: `D\u00e9veloppez vos comp\u00e9tences gr\u00e2ce \u00e0 des contenus exclusifs et des formations cibl\u00e9es.` },
          { icon: Globe, title: "R\u00e9seau solidaire", desc: `Connectez-vous avec des acteurs engag\u00e9s pour une insertion professionnelle inclusive.` },
        ].map((f, i) => (
          <div key={i} className="ub-offer-card" data-testid={`ubuntoo-feature-${i}`}>
            <f.icon size={28} />
            <h3>{f.title}</h3>
            <p>{f.desc}</p>
          </div>
        ))}
      </div>
    </div>

    {/* Parcours de transformation */}
    <div className="ub-transform">
      <h2>Votre parcours de transformation</h2>
      <div className="ub-transform-path">
        {[
          { num: 1, label: "Accompagn\u00e9", desc: `Vous recevez un soutien personnalis\u00e9`, colorClass: "orange" },
          { num: 2, label: "Pair-aidant", desc: `Vous partagez votre exp\u00e9rience`, colorClass: "green" },
          { num: 3, label: "Mentor", desc: "Vous structurez votre soutien", colorClass: "cyan" },
          { num: 4, label: "Ambassadeur", desc: "Vous repr\u00e9sentez l'insertion positive", colorClass: "purple" },
        ].map((s, i) => (
          <div key={i} style={{ display: "flex", alignItems: "center", gap: "16px" }}>
            <div className={`ub-transform-step ${s.colorClass}`}>
              <div className="ub-step-number">{s.num}</div>
              <h4>{s.label}</h4>
              <p>{s.desc}</p>
            </div>
            {i < 3 && <span className="ub-transform-arrow">{"\u2192"}</span>}
          </div>
        ))}
      </div>
    </div>

    {/* CTA */}
    <div className="ub-cta">
      <div className="ub-cta-card">
        <h2>{`Rejoignez la communaut\u00e9 Ubuntoo`}</h2>
        <p>{`Vous \u00eates connect\u00e9 avec votre compte RE'ACTIF PRO. L'espace communautaire sera bient\u00f4t pleinement actif.`}</p>
        <div className="ub-cta-buttons">
          <a href="https://coffre-fort-pro.preview.emergentagent.com/" target="_blank" rel="noopener noreferrer" className="ub-btn-primary">
            {`Acc\u00e9der \u00e0 D'CLIC PRO`} <ExternalLink size={16} />
          </a>
          <a href="https://www.alt-act.eu/" target="_blank" rel="noopener noreferrer" className="ub-btn-secondary">
            En savoir plus sur ALT&ACT <ExternalLink size={16} />
          </a>
        </div>
        <p style={{ fontSize: "11px", marginTop: "16px", color: "var(--ub-text-secondary)" }}>{`* Plateforme en cours de d\u00e9ploiement - Disponible prochainement`}</p>
      </div>
    </div>
  </div>
);

// ============ PROFIL ============
const ProfilTab = ({ user, setUser }) => {
  const statuses = ["Membre", "Membre actif", "Pair-aidant", "Mentor", "Ambassadeur"];
  const currentIdx = statuses.indexOf(user.status);
  const colorMap = ["green", "cyan", "orange", "purple", "yellow"];

  const upgradeStatus = () => {
    if (currentIdx < statuses.length - 1) {
      setUser(prev => ({ ...prev, status: statuses[currentIdx + 1], trust: Math.min(100, prev.trust + 15), badges: [...prev.badges, statuses[currentIdx + 1]] }));
    }
  };

  return (
    <div>
      <h1 className="ub-page-title">Profil Contributif</h1>
      <p className="ub-page-intro">{`Votre identit\u00e9 au sein de la communaut\u00e9 Ubuntoo`}</p>

      {/* Main profile card */}
      <div className="ub-profile-card" style={{ display: "flex", gap: "24px", alignItems: "flex-start", marginBottom: "24px" }}>
        <div className="ub-avatar">{user.name.split(" ").map(n => n[0]).join("")}</div>
        <div style={{ flex: 1 }}>
          <h2 style={{ fontSize: "22px", fontWeight: 700, marginBottom: "4px" }}>{user.name}</h2>
          <p style={{ color: "var(--ub-text-secondary)", fontSize: "14px", marginBottom: "12px" }}>{user.territory}</p>
          <span className="ub-badge green">{user.status}</span>
          <div style={{ marginTop: "16px" }}>
            <p style={{ color: "var(--ub-text-secondary)", fontSize: "12px", marginBottom: "6px" }}>Indice de confiance</p>
            <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
              <div className="ub-trust-bar" style={{ flex: 1 }}>
                <div className="ub-trust-fill" style={{ width: `${user.trust}%` }} />
              </div>
              <span style={{ fontSize: "14px", fontWeight: 700, color: "var(--ub-cyan)" }}>{user.trust}%</span>
            </div>
          </div>
          <button className="ub-btn-small" style={{ marginTop: "16px" }} onClick={upgradeStatus} data-testid="upgrade-status">
            Simuler progression de statut
          </button>
        </div>
      </div>

      {/* Grid cards */}
      <div className="ub-profile-grid">
        <div className="ub-profile-card">
          <h3 style={{ fontSize: "16px", fontWeight: 600, marginBottom: "12px", display: "flex", alignItems: "center", gap: "8px" }}>
            <Sparkles size={16} style={{ color: "var(--ub-cyan)" }} /> Soft Skills
          </h3>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
            {user.softskills.map((s, i) => <span key={i} className="ub-badge blue">{s}</span>)}
          </div>
        </div>
        <div className="ub-profile-card">
          <h3 style={{ fontSize: "16px", fontWeight: 600, marginBottom: "12px", display: "flex", alignItems: "center", gap: "8px" }}>
            <Award size={16} style={{ color: "var(--ub-yellow)" }} /> {`Badges d'exp\u00e9rience`}
          </h3>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
            {user.badges.map((b, i) => <span key={i} className="ub-badge yellow">{b}</span>)}
          </div>
        </div>
        <div className="ub-profile-card">
          <h3 style={{ fontSize: "16px", fontWeight: 600, marginBottom: "12px" }}>Contributions</h3>
          <div className="ub-stat-value">{user.contributions}</div>
          <p style={{ color: "var(--ub-text-secondary)", fontSize: "13px" }}>{`aides apport\u00e9es \u00e0 la communaut\u00e9`}</p>
        </div>
        <div className="ub-profile-card">
          <h3 style={{ fontSize: "16px", fontWeight: 600, marginBottom: "12px" }}>Parcours de Progression</h3>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
            {statuses.map((s, i) => (
              <span key={i} className={`ub-badge ${i <= currentIdx ? colorMap[i] : ""}`}
                style={i > currentIdx ? { background: "var(--ub-bg-card)", border: "1px solid var(--ub-border)", color: "var(--ub-text-secondary)" } : undefined}>
                {s}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// ============ GROUPES ============
const GroupesTab = () => {
  const [selected, setSelected] = useState(null);
  return (
    <div>
      <h1 className="ub-page-title">{`Groupes Th\u00e9matiques`}</h1>
      <p className="ub-page-intro">{`Rejoignez une communaut\u00e9 de professionnels engag\u00e9s dans le d\u00e9veloppement mutuel et l'entraide.`}</p>
      <div className="ub-groups-grid">
        {groups.map(g => (
          <div key={g.id} className="ub-group-card" onClick={() => setSelected(g.id)} data-testid={`group-${g.id}`}
            style={{ borderTopWidth: "3px", borderTopStyle: "solid", borderTopColor: `var(--ub-${g.colorClass})` }}>
            <h3 style={{ fontSize: "17px", fontWeight: 600, marginBottom: "8px" }}>{g.title}</h3>
            <div style={{ display: "flex", gap: "16px", fontSize: "13px", color: "var(--ub-text-secondary)", marginBottom: "12px" }}>
              <span><Users size={14} style={{ display: "inline", verticalAlign: "middle", marginRight: "4px" }} />{g.members} membres</span>
              <span><MessageCircle size={14} style={{ display: "inline", verticalAlign: "middle", marginRight: "4px" }} />{g.topics} sujets</span>
            </div>
            <button className={`ub-badge ${g.colorClass}`} style={{ cursor: "pointer" }}>Rejoindre</button>
          </div>
        ))}
      </div>

      {selected && (
        <div className="ub-profile-card" style={{ marginTop: "24px" }}>
          <h3 style={{ fontSize: "17px", fontWeight: 600, marginBottom: "12px" }}>{`\u00c9changes - ${groups.find(g => g.id === selected)?.title}`}</h3>
          {helpRequests.filter(r => r.group === selected).map(r => (
            <div key={r.id} style={{ background: "var(--ub-bg-card-hover)", padding: "12px", borderRadius: "var(--ub-radius)", marginBottom: "8px" }}>
              <h4 style={{ fontSize: "14px", fontWeight: 500 }}>{r.title}</h4>
              <p style={{ fontSize: "12px", color: "var(--ub-text-secondary)", marginTop: "4px" }}>{`par ${r.author} \u00b7 ${r.replies} r\u00e9ponses`}</p>
            </div>
          ))}
          {helpRequests.filter(r => r.group === selected).length === 0 && (
            <p style={{ color: "var(--ub-text-secondary)", fontSize: "14px" }}>{`Aucun \u00e9change dans ce groupe pour le moment.`}</p>
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

  return (
    <div>
      <h1 className="ub-page-title">Espace Discussions</h1>
      <p className="ub-page-intro">{`Forum d'entraide, questions-r\u00e9ponses et messagerie de la communaut\u00e9 Ubuntoo`}</p>

      <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", marginBottom: "24px" }}>
        {[{ k: "all", l: "Tous" }, { k: "question", l: "Questions" }, { k: "discussion", l: "Discussions" }, { k: "aide", l: "Entraide" }].map(f => (
          <button key={f.k} className={`ub-filter-btn ${filter === f.k ? "active" : ""}`} onClick={() => setFilter(f.k)}>
            {f.l}
          </button>
        ))}
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
        {filtered.map(t => (
          <div key={t.id} className={`ub-thread-card ${t.resolved ? "resolved" : ""}`} data-testid={`thread-${t.id}`}>
            <div style={{ display: "flex", alignItems: "flex-start", gap: "12px" }}>
              <div style={{ marginTop: "2px", color: t.type === "question" ? "var(--ub-blue)" : t.type === "aide" ? "var(--ub-orange)" : "var(--ub-green)" }}>
                {t.type === "question" ? <HelpCircle size={18} /> : t.type === "aide" ? <Heart size={18} /> : <MessageSquare size={18} />}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
                  <h3 style={{ fontSize: "14px", fontWeight: 600 }}>{t.title}</h3>
                  {t.resolved && <span className="ub-badge green" style={{ fontSize: "10px", padding: "2px 8px" }}>{`R\u00e9solu`}</span>}
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "12px", marginTop: "6px", fontSize: "12px", color: "var(--ub-text-secondary)" }}>
                  <span>{t.author}</span>
                  <span><ThumbsUp size={12} style={{ display: "inline", verticalAlign: "middle", marginRight: "2px" }} />{t.likes}</span>
                  <span><MessageCircle size={12} style={{ display: "inline", verticalAlign: "middle", marginRight: "2px" }} />{t.replies}</span>
                  <span><Clock size={12} style={{ display: "inline", verticalAlign: "middle", marginRight: "2px" }} />{t.views} vues</span>
                </div>
                <div style={{ display: "flex", gap: "4px", marginTop: "8px" }}>
                  {t.tags.map((tag, i) => (
                    <span key={i} style={{ background: "var(--ub-bg-card-hover)", color: "var(--ub-text-secondary)", fontSize: "10px", padding: "2px 8px", borderRadius: "12px", display: "inline-flex", alignItems: "center", gap: "2px" }}>
                      <Hash size={10} />{tag}
                    </span>
                  ))}
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
  <div>
    <h1 className="ub-page-title">Mentorat</h1>
    <p className="ub-page-intro">Trouvez un mentor pour vous accompagner dans votre parcours professionnel.</p>
    <div className="ub-groups-grid">
      {mentors.map(m => (
        <div key={m.id} className="ub-mentor-card" data-testid={`mentor-${m.id}`}>
          <div className="ub-mentor-avatar">{m.name.split(" ").map(n => n[0]).join("")}</div>
          <h3 style={{ fontSize: "17px", fontWeight: 600, marginBottom: "4px" }}>{m.name}</h3>
          <p style={{ color: "var(--ub-text-secondary)", fontSize: "13px" }}>{`Sp\u00e9cialit\u00e9 : ${m.focus}`}</p>
          <p style={{ color: "var(--ub-text-secondary)", fontSize: "13px" }}>{`Disponibilit\u00e9 : ${m.availability}`}</p>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "4px", marginTop: "8px" }}>
            <Star size={14} style={{ color: "var(--ub-yellow)", fill: "var(--ub-yellow)" }} />
            <span style={{ color: "var(--ub-yellow)", fontSize: "13px", fontWeight: 600 }}>{m.rating}</span>
          </div>
          <button className="ub-btn-small" style={{ marginTop: "16px", width: "100%" }}>
            Demander un mentorat
          </button>
        </div>
      ))}
    </div>
  </div>
);

// ============ IMPACT ============
const ImpactTab = () => (
  <div>
    <h1 className="ub-page-title">Impact Social</h1>
    <p className="ub-page-intro">{`Mesurer notre impact collectif sur l'insertion et l'inclusion professionnelle.`}</p>
    <div className="ub-impact-grid">
      {[
        { label: "Membres actifs", value: "12 450", target: "Objectif 50 000 (3 ans)", pct: 25, colorClass: "cyan" },
        { label: `Taux de r\u00e9ussite`, value: "+35%", target: `vs parcours isol\u00e9s`, pct: 70, colorClass: "orange" },
        { label: `R\u00e9duction isolement`, value: "-40%", target: "de sentiment d'isolement", pct: 60, colorClass: "purple" },
        { label: "Satisfaction", value: "85%", target: `de la communaut\u00e9`, pct: 85, colorClass: "purple" },
        { label: "Mentors actifs", value: "124", target: "sur la plateforme", pct: 45, colorClass: "orange" },
        { label: "Groupes actifs", value: "4", target: `th\u00e9matiques`, pct: 80, colorClass: "cyan" },
      ].map((s, i) => (
        <div key={i} className={`ub-impact-card ${s.colorClass}`} data-testid={`impact-${i}`}>
          <p style={{ color: "var(--ub-text-secondary)", fontSize: "13px", marginBottom: "4px" }}>{s.label}</p>
          <div className="ub-impact-value">{s.value}</div>
          <div className="ub-progress">
            <div className="ub-progress-fill" style={{ width: `${s.pct}%` }} />
          </div>
          <p style={{ color: "var(--ub-text-secondary)", fontSize: "12px" }}>{s.target}</p>
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
    <div className="ubuntoo-page" data-testid="ubuntoo-view">
      {/* Navigation */}
      <nav className="ub-nav">
        <div className="ub-nav-brand">
          <a href="/dashboard" title={`Retour \u00e0 Re'Actif Pro`} style={{ display: "flex", alignItems: "center" }}>
            <LogoReactifPro size="sm" />
          </a>
          <span className="ub-brand-tag">x Ubuntoo</span>
          <img src={LOGO} alt="Ubuntoo" style={{ height: "32px" }} />
        </div>
        <div className="ub-nav-links">
          {tabs.map(t => (
            <button key={t.id} onClick={() => setTab(t.id)} data-testid={`ubuntoo-tab-${t.id}`}
              className={`ub-nav-link ${tab === t.id ? "active" : ""}`}>
              <t.icon size={16} />
              {t.label}
            </button>
          ))}
        </div>
      </nav>

      {/* Content */}
      <div className="ub-content">
        {tab === "accueil" && <AccueilTab />}
        {tab === "profil" && <ProfilTab user={user} setUser={setUser} />}
        {tab === "groupes" && <GroupesTab />}
        {tab === "discussions" && <DiscussionsTab />}
        {tab === "mentorat" && <MentoratTab />}
        {tab === "impact" && <ImpactTab />}
      </div>
    </div>
  );
};

export default UbuntooView;
