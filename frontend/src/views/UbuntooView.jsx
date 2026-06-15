import { useState, useEffect, useCallback, useRef } from "react";
import {
  Users, User, Globe, Heart, Sparkles, MessageCircle, Award, Target, Lightbulb,
  TrendingUp, ExternalLink, Home, BarChart3, MessageSquare,
  ThumbsUp, Star, Clock, HelpCircle, Hash, Send, Radio, CheckCircle, RefreshCw, Zap, ArrowRight, Loader2,
  X, Info, MapPin, Briefcase, Trophy, Check, CheckCheck, CalendarDays,
  Search, SlidersHorizontal, Smile, Paperclip, Image as ImageIcon, FileText, Download, Mail
} from "lucide-react";
import { toast } from "sonner";
import LogoReactifPro from "@/components/LogoReactifPro";
import VsiGroupAgenda from "./ubuntoo/VsiGroupAgenda";
import VsiMeetingRoom from "./ubuntoo/VsiMeetingRoom";
import VsiGroupAdminPanel from "./ubuntoo/VsiGroupAdminPanel";
import DevPersoSpace from "./ubuntoo/DevPersoSpace";
import "./UbuntooView.css";

const API = `${process.env.REACT_APP_BACKEND_URL || ""}/api`;
const LOGO = "https://customer-assets.emergentagent.com/job_keen-meitner-5/artifacts/t3wjk59k_logo_ubuntoo_transparent.png";

// Tooltip descriptions for the 5 contribution levels (shown on hover)
const TRUST_LEVELS = {
  "Accompagné": {
    title: "Tu démarres ton parcours Ubuntoo",
    description: "Tu viens d'entrer dans la communauté. Tu reçois du soutien des pairs et tu explores l'écosystème Re'Actif Pro.",
    actions: [
      "Compléter ton profil D'CLIC PRO (Archéologie + Tendance comportementale)",
      "Renseigner ton passeport de compétences (3 expériences min.)",
      "Te présenter dans le Forum avec un post d'introduction",
      "Lire 5 conseils des pairs-aidants",
      "Rejoindre l'application au moins 3 jours différents (présence)",
    ],
    badge: "🌱 Bienvenue dans Ubuntoo",
  },
  "Membre actif": {
    title: "Tu participes régulièrement à la vie collective",
    description: "Tu interagis avec la communauté : tu poses des questions, tu réponds, tu rejoins des groupes et tu construis des liens.",
    actions: [
      "Rejoindre au moins 2 groupes thématiques différents",
      "Publier 5 messages argumentés dans le Forum",
      "Échanger en 1-to-1 avec 3 pairs différents",
      "Participer à 1 événement visio VSI complet",
      "Recevoir 5 réactions (👍❤️🎉) sur tes contributions",
      "Compléter ton trust score à 30 % minimum",
    ],
    badge: "🌿 Engagement régulier",
  },
  "Pair-aidant": {
    title: "Tu accompagnes activement d'autres pairs",
    description: "Ton expérience devient une ressource pour les autres. Tu donnes des conseils, partages tes apprentissages et soutiens les nouveaux arrivants.",
    actions: [
      "Aider 8 pairs via des messages 1-to-1 (avec retour positif)",
      "Donner 10 conseils argumentés dans le Forum (50 mots min.)",
      "Recevoir 15 réactions positives cumulées sur tes contributions",
      "Répondre à 3 demandes d'aide identifiées dans les groupes",
      "Participer activement à 3 événements visio VSI",
      "Partager 1 ressource ou retour d'expérience structuré",
      "Atteindre un trust score de 55 %",
    ],
    badge: "🤝 Pair-aidant reconnu",
  },
  "Mentor": {
    title: "Tu transmets, tu structures et tu créés du lien",
    description: "Tu accompagnes des parcours individuels, tu animes des groupes et tu fais grandir la communauté par tes mises en relation et tes recommandations.",
    actions: [
      "Accepter et mener à terme 3 mentorats (avec demandeur satisfait)",
      "Créer ou co-animer 1 groupe VSI thématique",
      "Programmer et animer 2 RDV visio en groupe",
      "Mettre en contact 5 pairs (recommandations qualifiées)",
      "Partager 5 conseils détaillés sur des sujets pointus",
      "Recevoir au moins 3 demandes de mentorat spontanées",
      "Maintenir un trust score ≥ 75 % pendant 30 jours",
    ],
    badge: "🌳 Mentor confirmé",
  },
  "Ambassadeur": {
    title: "Tu portes Ubuntoo au-delà de toi-même",
    description: "Tu incarnes les valeurs Ubuntoo : tu inities des projets, tu invites de nouveaux pairs, tu construis des ponts entre groupes et tu rayonnes la communauté à l'extérieur.",
    actions: [
      "Inviter et faire rejoindre 8 nouveaux pairs (qui restent actifs)",
      "Créer 1 événement inter-groupes (visio Google Meet, 2+ cohortes)",
      "Publier 5 contenus multi-groupes (cross-post)",
      "Animer 2 groupes VSI en parallèle avec régularité",
      "Mener 5 mentorats acceptés et terminés avec succès",
      "Recevoir 30+ réactions positives sur 3 mois",
      "Atteindre un trust score ≥ 90 % et le tenir 60 jours",
      "Représenter Ubuntoo sur 1 événement externe (témoignage, présentation)",
    ],
    badge: "🏆 Ambassadeur Ubuntoo",
  },
};


const groups = [
  { id: "reconversion", title: "Reconversion", members: 1240, topics: 86, colorClass: "indigo" },
  { id: "handicap", title: "Handicap & Emploi", members: 640, topics: 41, colorClass: "green" },
  { id: "numerique", title: "M\u00e9tiers du Num\u00e9rique", members: 980, topics: 63, colorClass: "purple" },
  { id: "vsi", title: "Atelier VSI (Valoriser Son Identit\u00e9 pro)", members: 520, topics: 34, colorClass: "cyan" },
];
// ============ SYNC BANNER ============
const SyncBanner = ({ onSync, syncing }) => (
  <div className="ub-sync-banner" data-testid="sync-banner">
    <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
      <div style={{ background: "var(--ub-indigo-bg)", borderRadius: "50%", width: "48px", height: "48px", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
        <Zap size={24} style={{ color: "var(--ub-indigo)" }} />
      </div>
      <div>
        <h3 style={{ fontSize: "16px", fontWeight: 700, color: "var(--ub-navy)", marginBottom: "4px" }}>{`Actualise ton espace sur Ubuntoo`}</h3>
        <p style={{ fontSize: "13px", color: "var(--ub-text-secondary)", lineHeight: 1.5 }}>
          {`L'IA va analyser tes donn\u00e9es Re'Actif Pro (comp\u00e9tences, r\u00e9sultats D'CLIC PRO, CV) pour cr\u00e9er ton profil communautaire personnalis\u00e9.`}
        </p>
      </div>
    </div>
    <button className="ub-btn-primary" onClick={onSync} disabled={syncing} data-testid="sync-profile-btn"
      style={{ marginTop: "16px", width: "100%", justifyContent: "center", opacity: syncing ? 0.7 : 1 }}>
      {syncing ? <><Loader2 size={16} className="ub-spin" /> Synchronisation en cours...</> : <>{`Actualiser mon profil Ubuntoo`} <ArrowRight size={16} /></>}
    </button>
  </div>
);

// ============ ACCUEIL ============
const AccueilTab = ({ ubProfile, onSync, syncing, isLoggedIn }) => (
  <div>
    {/* ===== HERO — Unité dans la diversité (connotation européenne + ubuntu) ===== */}
    <section className="ub-eu-hero" data-testid="ubuntoo-hero">
      <div className="ub-eu-hero-content">
        <div className="ub-eu-hero-left">
          <img src={LOGO} alt="Ubuntoo" className="ub-eu-hero-logo" />
          <span className="ub-eu-eyebrow">Réseau social solidaire d'ALT&amp;ACT</span>
          <h1 className="ub-eu-hero-title">
            Unité dans la diversité.
            <br />
            <span className="ub-eu-hero-accent">Ensemble, nous avançons.</span>
          </h1>
        </div>
        <p className="ub-eu-hero-subtitle">
          <span className="ub-tooltip">
            <strong>Ubuntoo</strong>
            <span className="ub-tooltip-content">
              <strong>{`La philosophie Ubuntu`}</strong><br /><br />
              {`Un anthropologue a propos\u00e9 un jeu \u00e0 des enfants d'une tribu d'Afrique australe. Quand il leur a dit de courir, ils se sont tous pris par la main et ont couru ensemble.`}
              <br /><br />
              {`Ils ont r\u00e9pondu `}<em>{'"'}UBUNTU{'"'}</em>{` \u2014 comment peut-on \u00eatre heureux si tous les autres sont tristes ?`}
              <br /><br />
              <em>{`\u00ab Ubuntu \u00bb`}</em>{` signifie : \u00ab Je suis parce que nous sommes \u00bb.`}
            </span>
          </span>{" "}
          élargit la diversité des individus dans un espace inspiré de la philosophie Ubuntu&nbsp;:
          <em>{` \u00ab Je suis parce que nous sommes \u00bb`}</em>.
        </p>
      </div>
      {/* Arc d'étoiles européennes formant un quart de cercle dans l'angle bas-droite */}
      <div className="ub-eu-arc" aria-hidden="true">
        {Array.from({ length: 8 }).map((_, i) => {
          // Quart de cercle ancré dans le coin bas-droite : de 180° (haut-gauche) à 270° (haut)
          const startAngle = Math.PI;
          const endAngle = 1.5 * Math.PI;
          const t = i / 7;
          const angle = startAngle + t * (endAngle - startAngle);
          const radius = 100;
          const x = Math.cos(angle) * radius;
          const y = Math.sin(angle) * radius;
          return (
            <span
              key={i}
              className="ub-eu-arc-star"
              style={{ transform: `translate(${x}px, ${y}px)`, animationDelay: `${i * 0.2}s` }}
            />
          );
        })}
      </div>
      <div className="ub-eu-hero-credit" data-testid="hero-credit">
        <em>Diversité culturelle</em><br />
        Photo : iStock
      </div>
    </section>

    {isLoggedIn && !ubProfile && <SyncBanner onSync={onSync} syncing={syncing} />}

    {/* ===== VALEURS ===== */}
    <section className="ub-section">
      <h2 className="ub-section-h2">Nos valeurs fondatrices</h2>
      <p className="ub-section-lede">Trois piliers qui font la force d'Ubuntoo, hérités d'Ubuntu et portés par l'esprit européen.</p>
      <div className="ub-values-grid ub-stagger">
        {[
          { icon: Users, label: "Ubuntu", desc: `"Je suis parce que nous sommes" \u2014 La force du collectif.`, accent: "terracotta" },
          { icon: Heart, label: "Entraide", desc: `Chacun apporte et re\u00e7oit dans un esprit de r\u00e9ciprocit\u00e9.`, accent: "sage" },
          { icon: Globe, label: "Diversité", desc: `Unis dans nos diff\u00e9rences \u2014 inspir\u00e9s par l'Europe.`, accent: "gold" },
        ].map((v, i) => (
          <div key={i} className={`ub-value-card ${v.accent}`} data-testid={`ubuntoo-value-${i}`}>
            <div className="ub-value-icon"><v.icon size={22} /></div>
            <h3>{v.label}</h3>
            <p>{v.desc}</p>
          </div>
        ))}
      </div>
    </section>

    {/* ===== KPIs ===== */}
    <section className="ub-section">
      <div className="ub-stat-grid">
        {[
          { value: "+35%", label: `de r\u00e9ussite vs parcours isol\u00e9s`, icon: TrendingUp, accent: "terracotta" },
          { value: "-40%", label: "de sentiment d'isolement", icon: Heart, accent: "sage" },
          { value: "85%", label: `de satisfaction communaut\u00e9`, icon: Star, accent: "gold" },
        ].map((k, i) => (
          <div key={i} className={`ub-stat-card ub-card-hover accent-${k.accent}`} data-testid={`ubuntoo-kpi-${i}`}>
            <div className="ub-stat-icon"><k.icon size={20} /></div>
            <div className="ub-stat-value">{k.value}</div>
            <div className="ub-stat-label">{k.label}</div>
          </div>
        ))}
      </div>
    </section>

    {/* ===== CE QUE OFFRE UBUNTOO ===== */}
    <section className="ub-section">
      <h2 className="ub-section-h2">Ce que vous offre Ubuntoo</h2>
      <p className="ub-section-lede">Une plateforme conçue pour l'inclusion, la valorisation des compétences et la mise en relation des professionnels tous secteurs d'activités confondus.</p>
      <div className="ub-offer-bento ub-stagger">
        {[
          { icon: Users, title: "Communauté apprenante", desc: `Rejoignez des professionnels engag\u00e9s, de Lille \u00e0 Lisbonne.` },
          { icon: Award, title: "Badges d'expérience", desc: `Valorisez vos comp\u00e9tences par des badges v\u00e9rifiables.` },
          { icon: MessageCircle, title: "Échanges et partage", desc: `B\u00e9n\u00e9ficiez de l'intelligence collective entre pairs.` },
          { icon: Target, title: "Accompagnement personnalisé", desc: `Ressources adapt\u00e9es \u00e0 votre parcours individuel.` },
          { icon: Lightbulb, title: "Ressources et formations", desc: `Contenus exclusifs et formations cibl\u00e9es.` },
          { icon: Globe, title: "Réseau solidaire européen", desc: `Insertion professionnelle inclusive sans fronti\u00e8res.` },
        ].map((f, i) => (
          <div key={i} className="ub-offer-tile" data-testid={`ubuntoo-feature-${i}`}>
            <div className="ub-offer-tile-icon"><f.icon size={18} /></div>
            <h3>{f.title}</h3>
            <p>{f.desc}</p>
          </div>
        ))}
      </div>
    </section>

    {/* ===== PARCOURS DE TRANSFORMATION ===== */}
    <section className="ub-section">
      <h2 className="ub-section-h2">Votre parcours de transformation</h2>
      <p className="ub-section-lede">D'accompagné à ambassadeur — chaque étape contribue à la communauté et vous fait monter en compétence.</p>
      <div className="ub-eu-path">
        {[
          { num: 1, label: "Accompagné", desc: `Soutien personnalis\u00e9` },
          { num: 2, label: "Pair-aidant", desc: `Partage d'exp\u00e9rience` },
          { num: 3, label: "Mentor", desc: "Soutien structuré" },
          { num: 4, label: "Ambassadeur", desc: "Insertion positive" },
        ].map((s, i, arr) => (
          <div key={i} className="ub-eu-path-step">
            <div className="ub-eu-path-num">{s.num}</div>
            <h4>{s.label}</h4>
            <p>{s.desc}</p>
            {i < arr.length - 1 && <span className="ub-eu-path-arrow"><ArrowRight size={16} /></span>}
          </div>
        ))}
      </div>
    </section>

    {/* ===== CTA ===== */}
    <section className="ub-eu-cta" data-testid="ubuntoo-cta">
      <div className="ub-eu-cta-bg" aria-hidden="true" />
      <div className="ub-eu-cta-inner">
        <h2>Rejoignez la communauté Ubuntoo</h2>
        <p>{`Un espace o\u00f9 chaque parcours compte, o\u00f9 nos diff\u00e9rences font notre force.`}</p>
        <div className="ub-cta-buttons">
          <a href="/" className="ub-btn-primary">
            Accéder à RE'ACTIF PRO <ExternalLink size={14} />
          </a>
          <a href="https://www.alt-act.eu/" target="_blank" rel="noopener noreferrer" className="ub-btn-small" style={{ background: "rgba(255,255,255,0.95)" }}>
            En savoir plus sur ALT&ACT <ExternalLink size={14} />
          </a>
        </div>
      </div>
    </section>
  </div>
);

// ============ CONTACT MODAL — Envoyer un premier message à un pair ============
const ContactPeerModal = ({ peer, token, onClose }) => {
  const [body, setBody] = useState("");
  const [sending, setSending] = useState(false);
  const [sent, setSent] = useState(false);

  if (!peer) return null;

  const send = async () => {
    if (!body.trim() || !token) return;
    setSending(true);
    try {
      const res = await fetch(`${API}/ubuntoo/messages?token=${token}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ peer_token_id: peer.token_id, body: body.trim() }),
      });
      if (res.ok) { setSent(true); setTimeout(onClose, 1500); }
    } catch (_) {} finally { setSending(false); }
  };

  return (
    <div data-testid="contact-peer-modal" style={{
      position: "fixed", inset: 0, background: "rgba(15,23,42,0.55)", zIndex: 1000,
      display: "flex", alignItems: "center", justifyContent: "center", padding: "20px"
    }} onClick={onClose}>
      <div onClick={(e) => e.stopPropagation()} style={{
        background: "white", borderRadius: "var(--ub-radius)", padding: "24px", maxWidth: "520px", width: "100%",
        boxShadow: "0 20px 60px rgba(0,0,0,0.25)"
      }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "12px" }}>
          <h3 style={{ fontSize: "17px", fontWeight: 700, color: "var(--ub-navy)" }}>Contacter {peer.name || peer.pseudo}</h3>
          <button onClick={onClose} style={{ background: "transparent", border: "none", cursor: "pointer", color: "var(--ub-text-muted)" }}><X size={18} /></button>
        </div>
        <p style={{ fontSize: "12px", color: "var(--ub-text-secondary)", marginBottom: "14px" }}>
          {peer.title || "—"} · {peer.status} · Compatibilité {peer.compatibility}%
        </p>
        {sent ? (
          <div style={{ padding: "20px", textAlign: "center", color: "var(--ub-green, #16a34a)" }}>
            <CheckCircle size={32} style={{ marginBottom: "8px" }} />
            <p style={{ fontSize: "14px", fontWeight: 600 }}>Message envoyé !</p>
          </div>
        ) : (
          <>
            <textarea
              data-testid="contact-message-body"
              value={body}
              onChange={(e) => setBody(e.target.value)}
              placeholder="Bonjour, j'ai vu sur Ubuntoo qu'on partage des centres d'intérêt similaires. Tu serais ouvert·e à un échange court sur…"
              rows={5}
              style={{
                width: "100%", padding: "10px", borderRadius: "var(--ub-radius-sm)",
                border: "1px solid var(--ub-border)", fontSize: "13px", color: "var(--ub-text-primary)",
                fontFamily: "inherit", resize: "vertical"
              }}
            />
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "12px" }}>
              <span style={{ fontSize: "11px", color: "var(--ub-text-muted)" }}>{body.length} / 2000</span>
              <button
                data-testid="contact-send-btn"
                className="ub-btn-primary"
                disabled={!body.trim() || sending}
                onClick={send}
                style={{ display: "inline-flex", alignItems: "center", gap: "6px", opacity: (!body.trim() || sending) ? 0.5 : 1 }}
              >
                {sending ? <><Loader2 size={14} className="ub-spin" /> Envoi…</> : <><Send size={14} /> Envoyer</>}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

// ============ MATCH DETAIL MODAL — Pourquoi ce pair est compatible (IA) ============
const PeerMatchModal = ({ peer, token, onClose, onContact }) => {
  const [narrative, setNarrative] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!peer || !token) return;
    setLoading(true);
    fetch(`${API}/ubuntoo/peer-compatibility/${peer.token_id}?token=${token}`)
      .then(r => r.ok ? r.json() : null)
      .then(d => setNarrative(d?.narrative || ""))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [peer, token]);

  if (!peer) return null;

  return (
    <div data-testid="peer-match-modal" style={{
      position: "fixed", inset: 0, background: "rgba(15,23,42,0.55)", zIndex: 1000,
      display: "flex", alignItems: "center", justifyContent: "center", padding: "20px"
    }} onClick={onClose}>
      <div onClick={(e) => e.stopPropagation()} style={{
        background: "white", borderRadius: "var(--ub-radius)", padding: "24px", maxWidth: "560px", width: "100%",
        boxShadow: "0 20px 60px rgba(0,0,0,0.25)"
      }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "12px" }}>
          <h3 style={{ fontSize: "17px", fontWeight: 700, color: "var(--ub-navy)", display: "flex", alignItems: "center", gap: "8px" }}>
            <Sparkles size={18} style={{ color: "var(--ub-indigo)" }} />
            Pourquoi {peer.name || peer.pseudo} ?
          </h3>
          <button onClick={onClose} style={{ background: "transparent", border: "none", cursor: "pointer", color: "var(--ub-text-muted)" }}><X size={18} /></button>
        </div>
        <p style={{ fontSize: "12px", color: "var(--ub-text-secondary)", marginBottom: "14px" }}>
          Compatibilité <strong>{peer.compatibility}%</strong> · {peer.status}
        </p>
        <div style={{
          background: "linear-gradient(135deg, rgba(79,109,245,0.08), rgba(168,85,247,0.06))",
          borderLeft: "3px solid var(--ub-indigo)",
          padding: "14px", borderRadius: "var(--ub-radius-sm)",
          fontSize: "14px", lineHeight: 1.7, color: "var(--ub-text-primary)",
          fontStyle: "italic", minHeight: "100px",
        }} data-testid="peer-match-narrative">
          {loading ? (
            <><Loader2 size={14} className="ub-spin" style={{ display: "inline", verticalAlign: "middle", marginRight: "6px" }} />Génération de l'analyse IA…</>
          ) : (
            narrative || "Aucune analyse disponible pour l'instant."
          )}
        </div>
        <div style={{ display: "flex", gap: "8px", marginTop: "16px", justifyContent: "flex-end" }}>
          <button className="ub-btn-small" onClick={onClose}>Fermer</button>
          <button
            className="ub-btn-primary"
            data-testid="peer-match-contact-btn"
            onClick={() => { onClose(); onContact && onContact(peer); }}
            style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}
          >
            <Send size={14} /> Contacter
          </button>
        </div>
      </div>
    </div>
  );
};

// ============ PROFIL (DYNAMIC) ============
const ProfilTab = ({ ubProfile, onSync, syncing, hasDclic, token }) => {
  const [adnExpanded, setAdnExpanded] = useState(false);
  if (!ubProfile) {
    return (
      <div>
        <h1 className="ub-page-title">Profil Contributif</h1>
        <p className="ub-page-intro">{`Synchronisez vos donn\u00e9es Re'Actif Pro pour acc\u00e9der \u00e0 votre profil.`}</p>
        {hasDclic && (
          <div className="ub-notice" data-testid="dclic-available-banner" style={{
            background: "linear-gradient(135deg, rgba(79,109,245,0.12), rgba(168,85,247,0.12))",
            borderColor: "rgba(79,109,245,0.35)",
            color: "var(--ub-navy)",
            display: "flex", alignItems: "center", gap: "12px",
            marginBottom: "16px"
          }}>
            <Sparkles size={20} style={{ color: "var(--ub-indigo)", flexShrink: 0 }} />
            <div style={{ flex: 1 }}>
              <strong>Ta carte d'identité pro D'CLIC est prête.</strong>
              <p style={{ fontSize: "13px", marginTop: "2px", color: "var(--ub-text-secondary)" }}>
                Synchronise pour générer ton ADN professionnel sur Ubuntoo et découvrir tes pairs compatibles.
              </p>
            </div>
          </div>
        )}
        <SyncBanner onSync={onSync} syncing={syncing} />
      </div>
    );
  }

  const statuses = ["Accompagn\u00e9", "Membre actif", "Pair-aidant", "Mentor", "Ambassadeur"];
  const currentIdx = Math.max(0, statuses.indexOf(ubProfile.status));
  const colorMap = ["green", "cyan", "indigo", "purple", "orange"];

  const card = ubProfile.dclic_card;
  const arche = ubProfile.archeologie_card;

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "16px" }}>
        <div>
          <h1 className="ub-page-title">Profil Contributif</h1>
          <p className="ub-page-intro">{`Votre identit\u00e9 au sein de la communaut\u00e9 Ubuntoo`}</p>
        </div>
        <button className="ub-btn-small" onClick={onSync} disabled={syncing} data-testid="resync-btn">
          <RefreshCw size={14} className={syncing ? "ub-spin" : ""} /> Re-synchroniser
        </button>
      </div>

      {/* ===== IDENTITÉ (header utilisateur) ===== */}
      <div className="ub-identity ub-fade-in">
        <div className="ub-identity-row">
          <div className="ub-avatar">{(ubProfile.name || "?").split(" ").map(n => n[0]).join("").slice(0, 2).toUpperCase()}</div>
          <div style={{ flex: 1, minWidth: "260px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap", marginBottom: "4px" }}>
              <h2 className="ub-identity-name">{ubProfile.name || ubProfile.pseudo}</h2>
              <span className="ub-status-badge"><Trophy size={12} /> {ubProfile.status}</span>
            </div>
            <p className="ub-identity-meta" style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
              {ubProfile.territory && <><MapPin size={13} style={{ color: "var(--ub-primary)" }} /> {ubProfile.territory}</>}
              {ubProfile.title && <>{ubProfile.territory && <span style={{ opacity: 0.4 }}>·</span>}<Briefcase size={13} style={{ color: "var(--ub-secondary)" }} /> {ubProfile.title}</>}
            </p>
            {ubProfile.status_reason && (
              <p style={{ fontSize: "12px", color: "var(--ub-text-muted)", marginTop: "6px", fontStyle: "italic" }}>{ubProfile.status_reason}</p>
            )}
            <div className="ub-trust">
              <div className="ub-trust-label">
                <span>Indice de confiance</span>
                <span className="ub-trust-value">{ubProfile.trust}%</span>
              </div>
              <div className="ub-trust-bar">
                <div className="ub-trust-fill" style={{ width: `${ubProfile.trust}%` }} />
              </div>
            </div>
            {ubProfile.synced_from && (
              <div style={{ display: "flex", gap: "6px", marginTop: "14px", flexWrap: "wrap" }}>
                {ubProfile.synced_from.dclic_pro && <span className="ub-badge orange"><Target size={11} /> Carte d'identité pro</span>}
                {ubProfile.synced_from.cv_analysis && <span className="ub-badge indigo">CV Analysé</span>}
                {ubProfile.synced_from.passport && <span className="ub-badge green">Passeport</span>}
              </div>
            )}
          </div>
        </div>
      </div>

      {ubProfile.ai_summary && (
        <div className="ub-notice" data-testid="ai-summary">
          <Sparkles size={14} style={{ marginTop: "2px", flexShrink: 0 }} />
          <span>{ubProfile.ai_summary}</span>
        </div>
      )}

      {/* ===== MON ADN PROFESSIONNEL — Pyramide d'identité ===== */}
      {arche && (
        <div data-testid="adn-pro-section" style={{ marginBottom: "22px" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "12px", flexWrap: "wrap", marginBottom: "12px" }}>
            <h3 className="ub-section-title" style={{ margin: 0 }}>
              <span className="ub-section-title-icon"><Sparkles size={16} /></span>
              Mon ADN professionnel
              <span className="ub-badge orange" style={{ fontSize: "10px" }}>RE'ACTIF PRO</span>
            </h3>
            <button
              className="ub-btn-small"
              onClick={() => setAdnExpanded(v => !v)}
              data-testid="adn-toggle-btn"
            >
              {adnExpanded ? "Réduire" : "Voir tout"}
              <ArrowRight size={12} style={{ transform: adnExpanded ? "rotate(-90deg)" : "rotate(90deg)", transition: "transform 0.2s" }} />
            </button>
          </div>

          <div className={`ub-dna-collapse ${adnExpanded ? "expanded" : ""}`}>
            <p className="ub-pyramid-intro">
              De la base au sommet : <strong>de qui je suis</strong> (vertus, valeurs) jusqu'à <strong>ce que je sais faire</strong> (compétences).
            </p>

            <div className="ub-pyramid" data-testid="adn-pyramid">
              {/* === Niveau 1 (haut / RACINE) — Vertus === */}
              {(arche.vertus_couvertes || []).length > 0 && (
                <div className="ub-pyramid-row level-1 is-root" data-testid="pyramid-vertus">
                  <div className="ub-pyramid-label">
                    <span className="ub-pyramid-num">1</span>
                    <span>Vertus</span>
                    <small className="ub-pyramid-count">{arche.vertus_couvertes.length}</small>
                    <span className="ub-pyramid-root-badge" title="Fondations de qui tu es">🌱 RACINE</span>
                  </div>
                  <div className="ub-pill-row">
                    {arche.vertus_couvertes.map((v, i) => <span key={i} className="ub-pill ub-pill-vertu">{v}</span>)}
                  </div>
                </div>
              )}

              {/* Connector 1→2 */}
              {(arche.vertus_couvertes || []).length > 0 && (arche.valeurs_couvertes || []).length > 0 && (
                <div className="ub-pyramid-connector" aria-hidden="true">
                  <span className="ub-pyramid-arrow">▼</span>
                  <em className="ub-pyramid-link">nourrissent les</em>
                </div>
              )}

              {/* === Niveau 2 — Valeurs === */}
              {(arche.valeurs_couvertes || []).length > 0 && (
                <div className="ub-pyramid-row level-2" data-testid="pyramid-valeurs">
                  <div className="ub-pyramid-label">
                    <span className="ub-pyramid-num">2</span>
                    <span>Valeurs</span>
                    <small className="ub-pyramid-count">{arche.valeurs_couvertes.length}</small>
                  </div>
                  <div className="ub-pill-row">
                    {arche.valeurs_couvertes.map((v, i) => <span key={i} className="ub-pill ub-pill-valeur">{v}</span>)}
                  </div>
                </div>
              )}

              {/* Connector 2→3 */}
              {(arche.valeurs_couvertes || []).length > 0 && (arche.qualites_couvertes || []).length > 0 && (
                <div className="ub-pyramid-connector" aria-hidden="true">
                  <span className="ub-pyramid-arrow">▼</span>
                  <em className="ub-pyramid-link">incarnent les</em>
                </div>
              )}

              {/* === Niveau 3 — Qualités humaines === */}
              {(arche.qualites_couvertes || []).length > 0 && (
                <div className="ub-pyramid-row level-3" data-testid="pyramid-qualites">
                  <div className="ub-pyramid-label">
                    <span className="ub-pyramid-num">3</span>
                    <span>Qualités humaines</span>
                    <small className="ub-pyramid-count">{arche.qualites_couvertes.length}</small>
                  </div>
                  <div className="ub-pill-row">
                    {arche.qualites_couvertes.map((q, i) => <span key={i} className="ub-pill ub-pill-qualite">{q}</span>)}
                  </div>
                </div>
              )}

              {/* Connector 3→4 */}
              {(arche.qualites_couvertes || []).length > 0 && (arche.savoir_etre || []).length > 0 && (
                <div className="ub-pyramid-connector" aria-hidden="true">
                  <span className="ub-pyramid-arrow">▼</span>
                  <em className="ub-pyramid-link">se manifestent en</em>
                </div>
              )}

              {/* === Niveau 4 — Savoir-être === */}
              {(arche.savoir_etre || []).length > 0 && (
                <div className="ub-pyramid-row level-4" data-testid="pyramid-savoir-etre">
                  <div className="ub-pyramid-label">
                    <span className="ub-pyramid-num">4</span>
                    <span>Savoir-être</span>
                    <small className="ub-pyramid-count">{arche.savoir_etre.length}</small>
                  </div>
                  <div className="ub-pill-row">
                    {arche.savoir_etre.map((s, i) => <span key={i} className="ub-pill ub-pill-savoir-etre">{s}</span>)}
                  </div>
                </div>
              )}

              {/* Connector 4→5 */}
              {(arche.savoir_etre || []).length > 0 && (arche.savoir_faire || []).length > 0 && (
                <div className="ub-pyramid-connector" aria-hidden="true">
                  <span className="ub-pyramid-arrow">▼</span>
                  <em className="ub-pyramid-link">permettent les</em>
                </div>
              )}

              {/* === Niveau 5 (bas) — Savoir-faire === */}
              {(arche.savoir_faire || []).length > 0 && (
                <div className="ub-pyramid-row level-5" data-testid="pyramid-savoir-faire">
                  <div className="ub-pyramid-label">
                    <span className="ub-pyramid-num">5</span>
                    <span>Savoir-faire</span>
                    <small className="ub-pyramid-count">{arche.savoir_faire.length}</small>
                  </div>
                  <div className="ub-pill-row">
                    {arche.savoir_faire.map((s, i) => <span key={i} className="ub-pill ub-pill-savoir-faire">{s}</span>)}
                  </div>
                </div>
              )}
              <p className="ub-pyramid-foot">Tout part d'en haut — les vertus, fondations de qui tu es</p>
            </div>
          </div>
        </div>
      )}

      {/* ===== CARTE D'IDENTITÉ PRO — supprimée (doublon avec le bloc Profil Comportemental dans Mon ADN professionnel) ===== */}

      {/* ===== MES CONTRIBUTIONS — Timeline gamifiée ===== */}
      <div className="ub-profile-card ub-card-accent" data-testid="contributions-section" style={{ marginBottom: "20px" }}>
        <h3 className="ub-section-title">
          <span className="ub-section-title-icon"><Trophy size={16} /></span>
          Mes contributions
        </h3>
        <div className="ub-timeline">
          {statuses.map((s, i) => {
            const tip = TRUST_LEVELS[s] || null;
            const state = i < currentIdx ? "done" : i === currentIdx ? "current" : "future";
            return (
              <div key={i} className={`ub-timeline-step ${state}`} data-testid={`trust-step-${s.toLowerCase()}`}>
                <div className="ub-timeline-dot">
                  {i < currentIdx ? <CheckCircle size={16} /> : i + 1}
                </div>
                <span className="ub-timeline-label">{s}</span>
                {tip && (
                  <div className="ub-trust-tooltip" role="tooltip">
                    <p className="ub-trust-tooltip-title">
                      {state === "done" ? "✓ " : state === "current" ? "● " : ""}{tip.title}
                    </p>
                    <p className="ub-trust-tooltip-desc">{tip.description}</p>
                    {tip.actions && tip.actions.length > 0 && (
                      <>
                        <p className="ub-trust-tooltip-section">Pour passer ce palier :</p>
                        <ul className="ub-trust-tooltip-list">
                          {tip.actions.map((a, idx) => <li key={idx}>{a}</li>)}
                        </ul>
                      </>
                    )}
                    {tip.badge && <p className="ub-trust-tooltip-badge">🏅 {tip.badge}</p>}
                  </div>
                )}
              </div>
            );
          })}
        </div>
        <p style={{ textAlign: "center", fontSize: "12px", color: "var(--ub-text-muted)", marginTop: "16px" }}>
          {currentIdx < statuses.length - 1
            ? `Prochaine étape : devenir ${statuses[currentIdx + 1]}`
            : "Tu es au sommet de ton parcours Ubuntoo — merci pour ta contribution !"}
        </p>
        <p style={{ textAlign: "center", fontSize: "11px", color: "var(--ub-text-muted)", marginTop: "4px", fontStyle: "italic" }}>
          💡 Survole chaque palier pour découvrir comment y accéder
        </p>
      </div>

      {/* ===== ESPACE DE DÉVELOPPEMENT PERSONNEL ===== */}
      <DevPersoSpace token={token} />

      {/* ===== Section 'Pairs compatibles' supprimée — voir l'onglet Groupes ===== */}

      {ubProfile.synced_at && (
        <p style={{ color: "var(--ub-text-muted)", fontSize: "11px", marginTop: "16px", textAlign: "right" }}>
          {`Derni\u00e8re synchronisation : ${new Date(ubProfile.synced_at).toLocaleString("fr-FR")}`}
        </p>
      )}
    </div>
  );
};

// ============ MESSAGES TAB — Conversations 1-to-1 ============
const formatLastSeen = (iso) => {
  if (!iso) return null;
  try {
    const date = new Date(iso);
    const diffMs = Date.now() - date.getTime();
    const diffMin = Math.floor(diffMs / 60000);
    if (diffMin < 2) return "à l'instant";
    if (diffMin < 60) return `il y a ${diffMin} min`;
    const diffH = Math.floor(diffMin / 60);
    if (diffH < 24) return `il y a ${diffH} h`;
    const diffD = Math.floor(diffH / 24);
    if (diffD < 7) return `il y a ${diffD} j`;
    return date.toLocaleDateString("fr-FR", { day: "2-digit", month: "short" });
  } catch (_) { return null; }
};

const MessagesTab = ({ token, openPeerTokenId, onConsumed }) => {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activePeer, setActivePeer] = useState(null);
  const [activePeerOnline, setActivePeerOnline] = useState(false);
  const [activePeerLastSeen, setActivePeerLastSeen] = useState(null);
  const [thread, setThread] = useState([]);
  const [reply, setReply] = useState("");
  const [sending, setSending] = useState(false);
  const [pendingAttachments, setPendingAttachments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [showEmojis, setShowEmojis] = useState(false);
  const [peerTyping, setPeerTyping] = useState(false);
  const [reactionPickerFor, setReactionPickerFor] = useState(null);
  const fileInputRef = useRef(null);
  const audioRef = useRef(null);
  const lastMsgIdRef = useRef(null);
  const typingTimeoutRef = useRef(null);

  const QUICK_EMOJIS = ["😊", "👍", "❤️", "🎉", "🙏", "🔥", "💡", "👏", "🤔", "😅", "🚀", "🇪🇺"];
  const REACTION_EMOJIS = ["👍", "❤️", "😊", "🎉", "🙏", "🔥"];

  const loadConversations = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API}/ubuntoo/messages/conversations?token=${token}`);
      if (res.ok) {
        const data = await res.json();
        setConversations(data);
        setLoading(false);
      }
    } catch (_) { setLoading(false); }
  }, [token]);

  useEffect(() => { loadConversations(); }, [loadConversations]);

  // Poll conversations list every 10s (refresh unread + last message)
  useEffect(() => {
    if (!token) return;
    const id = setInterval(loadConversations, 10000);
    return () => clearInterval(id);
  }, [token, loadConversations]);

  const openConversation = useCallback(async (conv) => {
    setActivePeer(conv);
    setActivePeerOnline(!!conv.online);
    setActivePeerLastSeen(conv.last_seen || null);
    if (!token) return;
    try {
      const res = await fetch(`${API}/ubuntoo/messages/${conv.peer_token_id}?token=${token}`);
      if (res.ok) {
        const data = await res.json();
        setThread(data.messages || []);
        lastMsgIdRef.current = data.messages?.length ? data.messages[data.messages.length - 1].id : null;
        setActivePeerOnline(!!data.online);
        setActivePeerLastSeen(data.last_seen || null);
        loadConversations();
      }
    } catch (_) {}
  }, [token, loadConversations]);

  // Open a peer requested by another tab (e.g. après clic sur un résultat de recherche)
  useEffect(() => {
    if (!openPeerTokenId || !token) return;
    (async () => {
      // Try to find conversation in list first
      const existing = conversations.find(c => c.peer_token_id === openPeerTokenId);
      if (existing) {
        await openConversation(existing);
      } else {
        // Build a minimal conv stub from peer profile
        try {
          const res = await fetch(`${API}/ubuntoo/messages/${openPeerTokenId}?token=${token}`);
          if (res.ok) {
            const data = await res.json();
            setActivePeer({ peer_token_id: openPeerTokenId, peer_name: "Pair", online: data.online });
            setActivePeerOnline(!!data.online);
            setActivePeerLastSeen(data.last_seen);
            setThread(data.messages || []);
            loadConversations();
          }
        } catch (_) {}
      }
      onConsumed && onConsumed();
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [openPeerTokenId, token]);

  // Poll active thread every 5s for new messages + typing indicator
  useEffect(() => {
    if (!activePeer || !token) return;
    const tick = async () => {
      try {
        const [tRes, typRes] = await Promise.all([
          fetch(`${API}/ubuntoo/messages/${activePeer.peer_token_id}?token=${token}`),
          fetch(`${API}/ubuntoo/typing/${activePeer.peer_token_id}?token=${token}`),
        ]);
        if (tRes.ok) {
          const data = await tRes.json();
          const msgs = data.messages || [];
          const lastIncoming = [...msgs].reverse().find(m => m.to_token_id !== activePeer.peer_token_id);
          // Detect new incoming
          if (msgs.length) {
            const newest = msgs[msgs.length - 1];
            if (lastMsgIdRef.current && newest.id !== lastMsgIdRef.current && newest.from_token_id === activePeer.peer_token_id) {
              // Play sound
              try { audioRef.current && audioRef.current.play(); } catch (_) {}
              toast.message(`Nouveau message de ${activePeer.peer_name || "ton pair"}`, {
                description: newest.body?.slice(0, 80) || "📎 Pièce jointe",
              });
            }
            lastMsgIdRef.current = newest.id;
          }
          setThread(msgs);
          setActivePeerOnline(!!data.online);
          setActivePeerLastSeen(data.last_seen);
        }
        if (typRes.ok) {
          const tData = await typRes.json();
          setPeerTyping(!!tData.typing);
        }
        // refresh sidebar unread counters quietly too
        if (lastIncomingShouldRefreshSidebar) loadConversations();
      } catch (_) {}
    };
    // eslint-disable-next-line no-unused-vars
    const lastIncomingShouldRefreshSidebar = true;
    tick();
    const id = setInterval(tick, 5000);
    return () => clearInterval(id);
  }, [activePeer, token, loadConversations]);

  // Notify when typing — debounced (signal once every 3s)
  const signalTyping = useCallback(() => {
    if (!activePeer || !token) return;
    if (typingTimeoutRef.current) return; // already signaled recently
    fetch(`${API}/ubuntoo/typing?token=${token}`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ peer_token_id: activePeer.peer_token_id }),
    }).catch(() => {});
    typingTimeoutRef.current = setTimeout(() => { typingTimeoutRef.current = null; }, 3000);
  }, [activePeer, token]);

  const handleFilePick = async (e) => {
    const files = Array.from(e.target.files || []);
    if (!files.length || !token) return;
    setUploading(true);
    try {
      for (const file of files.slice(0, 5)) {
        if (file.size > 3 * 1024 * 1024) {
          toast.error(`${file.name} dépasse 3 Mo`);
          continue;
        }
        const dataUrl = await new Promise((resolve, reject) => {
          const r = new FileReader();
          r.onload = () => resolve(r.result);
          r.onerror = reject;
          r.readAsDataURL(file);
        });
        const res = await fetch(`${API}/ubuntoo/upload?token=${token}`, {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ data_url: dataUrl, name: file.name }),
        });
        if (res.ok) {
          const meta = await res.json();
          setPendingAttachments(prev => [...prev, meta]);
        } else {
          toast.error("Upload impossible : " + ((await res.json()).detail || "erreur"));
        }
      }
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const removePending = (id) => setPendingAttachments(prev => prev.filter(a => a.id !== id));

  const insertEmoji = (e) => {
    setReply(prev => prev + e);
    setShowEmojis(false);
  };

  const sendReply = async () => {
    if ((!reply.trim() && pendingAttachments.length === 0) || !activePeer || !token) return;
    setSending(true);
    try {
      const res = await fetch(`${API}/ubuntoo/messages?token=${token}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          peer_token_id: activePeer.peer_token_id,
          body: reply.trim(),
          attachments: pendingAttachments.map(a => ({
            id: a.id, name: a.name, content_type: a.content_type,
            size: a.size, is_image: a.is_image,
          })),
        }),
      });
      if (res.ok) {
        setReply("");
        setPendingAttachments([]);
        await openConversation(activePeer);
      }
    } catch (_) {} finally { setSending(false); }
  };

  const toggleReaction = async (messageId, emoji) => {
    if (!token) return;
    try {
      const res = await fetch(`${API}/ubuntoo/messages/${messageId}/react?token=${token}`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ emoji }),
      });
      if (res.ok) {
        const data = await res.json();
        setThread(prev => prev.map(m => m.id === messageId ? { ...m, reactions: data.reactions } : m));
      }
    } catch (_) {}
    setReactionPickerFor(null);
  };

  if (!token) {
    return (
      <div>
        <h1 className="ub-page-title">Messages</h1>
        <p className="ub-page-intro">Connecte-toi à Re'Actif Pro pour accéder à tes conversations Ubuntoo.</p>
      </div>
    );
  }

  return (
    <div data-testid="messages-tab">
      <audio ref={audioRef} src="https://cdn.jsdelivr.net/gh/akx/Notifier@main/notification.mp3" preload="auto" />
      <h1 className="ub-page-title">Messages</h1>
      <p className="ub-page-intro">Tes conversations 1-to-1 avec les pairs Ubuntoo.</p>

      <div style={{ display: "grid", gridTemplateColumns: "minmax(240px, 320px) 1fr", gap: "16px", alignItems: "stretch" }}>
        {/* Conversations list */}
        <div className="ub-profile-card" data-testid="conversations-list" style={{ padding: "0", overflow: "hidden" }}>
          <div style={{ padding: "14px 16px", borderBottom: "1px solid var(--ub-border)", background: "var(--ub-bg-soft, #fafafa)" }}>
            <p style={{ fontSize: "13px", fontWeight: 600, color: "var(--ub-navy)" }}>
              {conversations.length} conversation{conversations.length > 1 ? "s" : ""}
            </p>
          </div>
          {loading ? (
            <div style={{ padding: "20px", textAlign: "center" }}>
              <Loader2 size={16} className="ub-spin" style={{ color: "var(--ub-text-muted)" }} />
            </div>
          ) : conversations.length === 0 ? (
            <div style={{ padding: "24px", textAlign: "center", color: "var(--ub-text-muted)", fontSize: "13px" }}>
              <MessageSquare size={28} style={{ margin: "0 auto 8px", display: "block", opacity: 0.4 }} />
              Aucun message pour l'instant.<br />Découvre tes pairs compatibles sur ton profil.
            </div>
          ) : (
            <div style={{ maxHeight: "560px", overflowY: "auto" }}>
              {conversations.map((c) => {
                const isActive = activePeer?.peer_token_id === c.peer_token_id;
                return (
                  <button
                    key={c.peer_token_id}
                    data-testid={`conversation-${c.peer_token_id}`}
                    onClick={() => openConversation(c)}
                    style={{
                      width: "100%", textAlign: "left", padding: "12px 16px",
                      background: isActive ? "var(--ub-indigo-bg)" : "transparent",
                      border: "none", borderBottom: "1px solid var(--ub-border-light, #f1f5f9)",
                      cursor: "pointer", display: "flex", gap: "10px", alignItems: "flex-start"
                    }}
                  >
                    <div style={{ position: "relative", flexShrink: 0 }}>
                      <div className="ub-avatar-sm" style={{ width: "32px", height: "32px", fontSize: "12px" }}>
                        {(c.peer_name || "?").split(" ").map(n => n[0]).join("").slice(0, 2).toUpperCase()}
                      </div>
                      <span
                        data-testid={`presence-${c.peer_token_id}`}
                        title={c.online ? "En ligne" : "Hors ligne"}
                        style={{
                          position: "absolute", bottom: -1, right: -1,
                          width: "10px", height: "10px", borderRadius: "50%",
                          background: c.online ? "#22c55e" : "#cbd5e1",
                          boxShadow: c.online ? "0 0 0 2px white, 0 0 0 4px rgba(34,197,94,0.25)" : "0 0 0 2px white",
                        }}
                      />
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "6px" }}>
                        <p style={{ fontSize: "13px", fontWeight: c.unread > 0 ? 700 : 600, color: "var(--ub-navy)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                          {c.peer_name}
                        </p>
                        {c.unread > 0 && (
                          <span style={{ background: "var(--ub-indigo)", color: "white", fontSize: "10px", fontWeight: 700, padding: "1px 6px", borderRadius: "10px" }}>
                            {c.unread}
                          </span>
                        )}
                      </div>
                      <p style={{ fontSize: "11px", color: "var(--ub-text-muted)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis", marginTop: "2px" }}>
                        {c.last_message}
                      </p>
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </div>

        {/* Thread view */}
        <div className="ub-profile-card" data-testid="conversation-thread" style={{ padding: "0", display: "flex", flexDirection: "column", minHeight: "560px" }}>
          {!activePeer ? (
            <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", color: "var(--ub-text-muted)", fontSize: "13px", padding: "40px" }}>
              <div style={{ textAlign: "center" }}>
                <Send size={32} style={{ margin: "0 auto 12px", display: "block", opacity: 0.3 }} />
                Sélectionne une conversation pour lire les messages
              </div>
            </div>
          ) : (
            <>
              <div style={{ padding: "14px 16px", borderBottom: "1px solid var(--ub-border)", background: "var(--ub-bg-soft, #fafafa)" }}>
                <p style={{ fontSize: "14px", fontWeight: 700, color: "var(--ub-navy)", display: "flex", alignItems: "center", gap: "8px" }}>
                  {activePeer.peer_name}
                  <span
                    data-testid="thread-presence"
                    title={activePeerOnline ? "En ligne" : (activePeerLastSeen ? `Vu ${formatLastSeen(activePeerLastSeen)}` : "Hors ligne")}
                    style={{
                      display: "inline-flex", alignItems: "center", gap: "4px",
                      fontSize: "11px", fontWeight: 600,
                      color: activePeerOnline ? "#16a34a" : "#64748b",
                      padding: "2px 8px", borderRadius: "999px",
                      background: activePeerOnline ? "rgba(34,197,94,0.10)" : "rgba(203,213,225,0.30)",
                    }}
                  >
                    <span style={{
                      width: "6px", height: "6px", borderRadius: "50%",
                      background: activePeerOnline ? "#22c55e" : "#cbd5e1",
                    }} />
                    {activePeerOnline
                      ? "En ligne"
                      : (activePeerLastSeen ? `Vu ${formatLastSeen(activePeerLastSeen)}` : "Hors ligne")}
                  </span>
                </p>
                {activePeer.peer_title && <p style={{ fontSize: "11px", color: "var(--ub-text-muted)" }}>{activePeer.peer_title}{activePeer.peer_status ? ` · ${activePeer.peer_status}` : ""}</p>}
              </div>
              <div style={{ flex: 1, overflowY: "auto", padding: "16px", display: "flex", flexDirection: "column", gap: "10px" }}>
                {thread.length === 0 ? (
                  <p style={{ color: "var(--ub-text-muted)", fontSize: "13px", textAlign: "center" }}>Aucun message dans cette conversation. Lance la conversation !</p>
                ) : (
                  thread.map((m, i) => {
                    const mine = m.to_token_id === activePeer.peer_token_id;
                    const reactions = m.reactions || {};
                    const reactionEntries = Object.entries(reactions);
                    return (
                      <div key={m.id || i} data-testid={`thread-msg-${i}`} style={{
                        alignSelf: mine ? "flex-end" : "flex-start",
                        maxWidth: "78%",
                        display: "flex", flexDirection: "column",
                        alignItems: mine ? "flex-end" : "flex-start",
                        position: "relative",
                      }}>
                        <div
                          style={{
                            background: mine ? "linear-gradient(135deg, #1a4ba8 0%, #1E2A4F 100%)" : "var(--ub-border-light, #f1f5f9)",
                            color: mine ? "white" : "var(--ub-text-primary)",
                            padding: "8px 12px", borderRadius: "14px",
                            fontSize: "13px", lineHeight: 1.5,
                            boxShadow: mine ? "0 3px 10px rgba(26,75,168,0.25)" : "none",
                            position: "relative",
                          }}
                          onDoubleClick={() => setReactionPickerFor(reactionPickerFor === m.id ? null : m.id)}
                        >
                          {m.body && <div style={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }}>{m.body}</div>}
                          {(m.attachments || []).length > 0 && (
                            <div style={{ marginTop: m.body ? "8px" : 0, display: "flex", flexDirection: "column", gap: "6px" }}>
                              {(m.attachments || []).map((a) => {
                                const url = `${process.env.REACT_APP_BACKEND_URL || ""}/api/ubuntoo/attachments/${a.id}`;
                                if (a.is_image) {
                                  return (
                                    <a key={a.id} href={url} target="_blank" rel="noreferrer" data-testid={`thread-attach-img-${a.id}`}>
                                      <img src={url} alt={a.name}
                                        style={{ maxWidth: "260px", maxHeight: "200px", borderRadius: "10px", display: "block", border: mine ? "1px solid rgba(255,255,255,0.2)" : "1px solid var(--ub-border)" }}
                                      />
                                    </a>
                                  );
                                }
                                return (
                                  <a key={a.id} href={url} target="_blank" rel="noreferrer" download={a.name}
                                    data-testid={`thread-attach-doc-${a.id}`}
                                    style={{
                                      display: "inline-flex", alignItems: "center", gap: "8px",
                                      background: mine ? "rgba(255,255,255,0.15)" : "rgba(0,0,0,0.05)",
                                      padding: "8px 10px", borderRadius: "10px", textDecoration: "none",
                                      color: mine ? "white" : "var(--ub-navy)", fontSize: "12px", fontWeight: 600,
                                      maxWidth: "240px",
                                    }}
                                  >
                                    <FileText size={16} />
                                    <span style={{ flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{a.name}</span>
                                    <Download size={14} />
                                  </a>
                                );
                              })}
                            </div>
                          )}
                          <p style={{ fontSize: "10px", opacity: 0.85, marginTop: "4px", textAlign: mine ? "right" : "left", display: "flex", justifyContent: mine ? "flex-end" : "flex-start", alignItems: "center", gap: "4px" }}>
                            <span>{new Date(m.created_at).toLocaleString("fr-FR", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" })}</span>
                            {mine && (
                              <span data-testid={`thread-msg-${i}-check`} className="ub-msg-checkmark" title={m.read ? "Lu" : "Envoyé"}>
                                {m.read ? <CheckCheck size={12} /> : <Check size={12} />}
                              </span>
                            )}
                          </p>
                          {/* Reaction trigger on hover */}
                          <button
                            className="ub-react-trigger"
                            data-testid={`react-trigger-${m.id}`}
                            onClick={() => setReactionPickerFor(reactionPickerFor === m.id ? null : m.id)}
                            title="Réagir"
                          >
                            <Smile size={12} />
                          </button>
                        </div>
                        {reactionPickerFor === m.id && (
                          <div className="ub-react-picker" data-testid={`react-picker-${m.id}`}>
                            {REACTION_EMOJIS.map(e => (
                              <button key={e} onClick={() => toggleReaction(m.id, e)} data-testid={`react-${m.id}-${e}`}>
                                <span style={{ fontSize: "18px" }}>{e}</span>
                              </button>
                            ))}
                          </div>
                        )}
                        {reactionEntries.length > 0 && (
                          <div className="ub-msg-reactions" data-testid={`msg-reactions-${m.id}`}>
                            {reactionEntries.map(([emoji, users]) => (
                              <button
                                key={emoji}
                                className="ub-msg-reaction-chip"
                                onClick={() => toggleReaction(m.id, emoji)}
                                data-testid={`chip-${m.id}-${emoji}`}
                              >
                                <span>{emoji}</span>
                                <span className="ub-msg-reaction-count">{users.length}</span>
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    );
                  })
                )}
                {peerTyping && (
                  <div data-testid="peer-typing" style={{ alignSelf: "flex-start", display: "flex", alignItems: "center", gap: "6px", color: "var(--ub-text-muted)", fontSize: "12px", fontStyle: "italic", marginTop: "4px" }}>
                    <span className="ub-typing-dots"><span></span><span></span><span></span></span>
                    {activePeer.peer_name} est en train d'écrire…
                  </div>
                )}
              </div>

              {/* Pending attachments preview */}
              {pendingAttachments.length > 0 && (
                <div className="ub-pending-attachments" data-testid="pending-attachments">
                  {pendingAttachments.map((a) => (
                    <div key={a.id} className="ub-pending-chip" data-testid={`pending-${a.id}`}>
                      {a.is_image ? <ImageIcon size={12} /> : <FileText size={12} />}
                      <span style={{ maxWidth: "120px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{a.name}</span>
                      <button onClick={() => removePending(a.id)} data-testid={`pending-remove-${a.id}`}><X size={10} /></button>
                    </div>
                  ))}
                </div>
              )}

              <div style={{ borderTop: "1px solid var(--ub-border)", padding: "10px 12px", display: "flex", gap: "6px", position: "relative", alignItems: "flex-end" }}>
                {/* Emoji picker */}
                <button
                  className="ub-icon-btn"
                  data-testid="emoji-btn"
                  onClick={() => setShowEmojis(v => !v)}
                  title="Insérer un emoji"
                >
                  <Smile size={18} />
                </button>
                {showEmojis && (
                  <div className="ub-emoji-popover" data-testid="emoji-popover">
                    {QUICK_EMOJIS.map(e => (
                      <button key={e} onClick={() => insertEmoji(e)} data-testid={`emoji-${e}`}>
                        <span style={{ fontSize: "22px" }}>{e}</span>
                      </button>
                    ))}
                  </div>
                )}

                {/* Attachment */}
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  accept="image/*,application/pdf,.doc,.docx,.txt,.csv,.zip"
                  onChange={handleFilePick}
                  style={{ display: "none" }}
                  data-testid="attach-input"
                />
                <button
                  className="ub-icon-btn"
                  data-testid="attach-btn"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={uploading}
                  title="Joindre un fichier ou une image"
                >
                  {uploading ? <Loader2 size={18} className="ub-spin" /> : <Paperclip size={18} />}
                </button>

                <textarea
                  data-testid="reply-textarea"
                  value={reply}
                  onChange={(e) => { setReply(e.target.value); signalTyping(); }}
                  placeholder="Ta réponse…"
                  rows={2}
                  onKeyDown={(e) => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) { e.preventDefault(); sendReply(); } }}
                  style={{
                    flex: 1, padding: "8px 10px", borderRadius: "var(--ub-radius-sm)",
                    border: "1px solid var(--ub-border)", fontSize: "13px", resize: "none",
                    fontFamily: "inherit",
                  }}
                />
                <button
                  className="ub-btn-primary"
                  data-testid="reply-send-btn"
                  disabled={(!reply.trim() && pendingAttachments.length === 0) || sending}
                  onClick={sendReply}
                  style={{ display: "inline-flex", alignItems: "center", gap: "6px", opacity: ((!reply.trim() && pendingAttachments.length === 0) || sending) ? 0.5 : 1 }}
                >
                  {sending ? <Loader2 size={14} className="ub-spin" /> : <><Send size={14} /> Envoyer</>}
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

// ============ GROUPES ============
// ============ VSI GROUP DETAIL — Chat collectif + participants ============
const VsiGroupDetail = ({ groupId, token, onClose, onPrivateMessage }) => {
  const [group, setGroup] = useState(null);
  const [messages, setMessages] = useState([]);
  const [reply, setReply] = useState("");
  const [sending, setSending] = useState(false);
  const [loadingMsgs, setLoadingMsgs] = useState(true);
  const [showRequestsPanel, setShowRequestsPanel] = useState(false);
  const [pendingRequests, setPendingRequests] = useState([]);
  const [showMentorModal, setShowMentorModal] = useState(false);
  const [mentorCandidates, setMentorCandidates] = useState([]);
  const [mentorSearch, setMentorSearch] = useState("");
  const [pendingAttachments, setPendingAttachments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [showEmojis, setShowEmojis] = useState(false);
  const groupFileInputRef = useRef(null);

  // Sub-view: "chat" (default) | "agenda" | "meeting"
  const [subView, setSubView] = useState("chat");
  const [activeEvent, setActiveEvent] = useState(null);

  const QUICK_EMOJIS = ["😊", "👍", "❤️", "🎉", "🙏", "🔥", "💡", "👏", "🤔", "😅", "🚀", "🇪🇺"];

  const loadGroup = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API}/vsi-groups/${groupId}?token=${token}`);
      if (res.ok) setGroup(await res.json());
    } catch (_) {}
  }, [token, groupId]);

  const loadMessages = useCallback(async () => {
    if (!token) return;
    setLoadingMsgs(true);
    try {
      const res = await fetch(`${API}/vsi-groups/${groupId}/messages?token=${token}`);
      if (res.ok) {
        const data = await res.json();
        setMessages(data.messages || []);
      }
    } catch (_) {} finally { setLoadingMsgs(false); }
  }, [token, groupId]);

  useEffect(() => { loadGroup(); loadMessages(); }, [loadGroup, loadMessages]);
  // Poll messages every 12s
  useEffect(() => {
    const id = setInterval(loadMessages, 12000);
    return () => clearInterval(id);
  }, [loadMessages]);

  const handleGroupFilePick = async (e) => {
    const files = Array.from(e.target.files || []);
    if (!files.length || !token) return;
    setUploading(true);
    try {
      for (const file of files.slice(0, 5)) {
        if (file.size > 3 * 1024 * 1024) {
          toast.error(`${file.name} dépasse 3 Mo`);
          continue;
        }
        const dataUrl = await new Promise((resolve, reject) => {
          const r = new FileReader();
          r.onload = () => resolve(r.result);
          r.onerror = reject;
          r.readAsDataURL(file);
        });
        const res = await fetch(`${API}/ubuntoo/upload?token=${token}`, {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ data_url: dataUrl, name: file.name }),
        });
        if (res.ok) {
          const meta = await res.json();
          setPendingAttachments(prev => [...prev, meta]);
        } else {
          toast.error("Upload impossible : " + ((await res.json()).detail || "erreur"));
        }
      }
    } finally {
      setUploading(false);
      if (groupFileInputRef.current) groupFileInputRef.current.value = "";
    }
  };

  const removePending = (id) => setPendingAttachments(prev => prev.filter(a => a.id !== id));
  const insertEmoji = (e) => { setReply(prev => prev + e); setShowEmojis(false); };

  const send = async () => {
    if ((!reply.trim() && pendingAttachments.length === 0) || !token) return;
    setSending(true);
    try {
      const res = await fetch(`${API}/vsi-groups/${groupId}/messages?token=${token}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          body: reply.trim(),
          attachments: pendingAttachments.map(a => ({
            id: a.id, name: a.name, content_type: a.content_type,
            size: a.size, is_image: a.is_image,
          })),
        }),
      });
      if (res.ok) {
        setReply("");
        setPendingAttachments([]);
        loadMessages();
      }
    } catch (_) {} finally { setSending(false); }
  };

  if (!group) {
    return <div className="ub-profile-card" style={{ marginTop: "16px", textAlign: "center", padding: "30px" }}>
      <Loader2 size={20} className="ub-spin" />
    </div>;
  }

  return (
    <div className="ub-vsi-detail" data-testid="vsi-group-detail">
      <div className="ub-vsi-detail-header">
        <button className="ub-btn-small" onClick={onClose} data-testid="vsi-close-btn">
          <ArrowRight size={14} style={{ transform: "rotate(180deg)" }} /> Retour aux groupes
        </button>
        <div style={{ flex: 1 }}>
          <h2 className="ub-vsi-detail-title">{group.name}</h2>
          <p className="ub-vsi-detail-meta">
            <CalendarDays size={13} /> Session du {new Date(group.session_date).toLocaleDateString("fr-FR")}
            {group.session_end_date && ` au ${new Date(group.session_end_date).toLocaleDateString("fr-FR")}`}
            {group.location && <> · <MapPin size={13} /> {group.location}</>}
          </p>
          {group.theme && <p className="ub-vsi-detail-theme">{group.theme}</p>}
        </div>
        {group.is_admin && (
          <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
            <button
              className="ub-btn-small"
              onClick={async () => {
                setShowRequestsPanel(v => !v);
                if (!showRequestsPanel) {
                  try {
                    const res = await fetch(`${API}/vsi-groups/${groupId}/requests?token=${token}`);
                    if (res.ok) setPendingRequests((await res.json()).requests || []);
                  } catch (_) {}
                }
              }}
              data-testid="vsi-admin-requests-btn"
              style={{ position: "relative" }}
            >
              <Hash size={12} /> Demandes
              {group.pending_requests_count > 0 && (
                <span style={{
                  position: "absolute", top: "-4px", right: "-4px",
                  background: "#ef4444", color: "white", fontSize: "10px", fontWeight: 700,
                  padding: "1px 5px", borderRadius: "10px", minWidth: "16px", textAlign: "center"
                }}>{group.pending_requests_count}</span>
              )}
            </button>
            <button
              className="ub-btn-primary"
              onClick={() => { setShowMentorModal(true); setMentorSearch(""); }}
              data-testid="vsi-admin-invite-mentor-btn"
            >
              <Award size={12} /> Inviter un mentor
            </button>
          </div>
        )}
      </div>

      {/* === Sub-tabs (Chat / Agenda / Admin (admin only) / [Meeting]) === */}
      {subView !== "meeting" && (
        <div className="ub-vsi-subtabs" data-testid="vsi-subtabs">
          <button
            className={`ub-vsi-subtab ${subView === "chat" ? "active" : ""}`}
            onClick={() => setSubView("chat")}
            data-testid="vsi-subtab-chat"
          >
            <MessageCircle size={14} /> Discussion
          </button>
          <button
            className={`ub-vsi-subtab ${subView === "agenda" ? "active" : ""}`}
            onClick={() => setSubView("agenda")}
            data-testid="vsi-subtab-agenda"
          >
            <CalendarDays size={14} /> Agenda
          </button>
          {group.is_admin && (
            <button
              className={`ub-vsi-subtab ${subView === "admin" ? "active" : ""}`}
              onClick={() => setSubView("admin")}
              data-testid="vsi-subtab-admin"
            >
              <Sparkles size={14} /> Pilotage
            </button>
          )}
        </div>
      )}

      {/* === Admin panel === */}
      {subView === "admin" && group.is_admin && (
        <VsiGroupAdminPanel group={group} token={token} onChanged={loadGroup} />
      )}

      {/* === Meeting room view (full screen of the detail) === */}
      {subView === "meeting" && activeEvent && (
        <VsiMeetingRoom
          event={activeEvent}
          groupId={groupId}
          group={group}
          token={token}
          onBack={() => { setSubView("agenda"); setActiveEvent(null); }}
        />
      )}

      {/* === Agenda view === */}
      {subView === "agenda" && (
        <VsiGroupAgenda
          groupId={groupId}
          token={token}
          group={group}
          onJoinMeeting={(ev) => { setActiveEvent(ev); setSubView("meeting"); }}
        />
      )}

      {/* === Demandes admin panel (only on chat view) === */}
      {subView === "chat" && group.is_admin && showRequestsPanel && (
        <div className="ub-vsi-requests-panel" data-testid="vsi-requests-panel">
          <h3 className="ub-vsi-side-title">
            <Hash size={15} /> Demandes en attente ({pendingRequests.length})
          </h3>
          {pendingRequests.length === 0 ? (
            <p style={{ fontSize: "13px", color: "var(--ub-text-muted)", padding: "12px 0" }}>Aucune demande en attente.</p>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              {pendingRequests.map((r) => (
                <div key={r.id} data-testid={`vsi-request-${r.id}`} className="ub-vsi-request-card">
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <p style={{ fontSize: "14px", fontWeight: 600, color: "var(--ub-navy)", margin: 0 }}>
                      {r.requester_name}
                      <span className="ub-badge indigo" style={{ fontSize: "10px", marginLeft: "8px" }}>
                        Souhaite : {r.requested_type === "invite_provisoire" ? "invité provisoire" : "membre régulier"}
                      </span>
                    </p>
                    {r.requester_title && <p style={{ fontSize: "11px", color: "var(--ub-text-muted)", margin: "2px 0" }}>{r.requester_title}</p>}
                    {r.message && <p style={{ fontSize: "12px", fontStyle: "italic", color: "var(--ub-text-secondary)", margin: "4px 0" }}>« {r.message} »</p>}
                  </div>
                  <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
                    <button className="ub-btn-small" onClick={async () => {
                      await fetch(`${API}/vsi-groups/${groupId}/requests/${r.id}/respond?token=${token}`, {
                        method: "POST", headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ action: "accept", member_type: "invite_provisoire" })
                      });
                      loadGroup();
                      const res = await fetch(`${API}/vsi-groups/${groupId}/requests?token=${token}`);
                      if (res.ok) setPendingRequests((await res.json()).requests || []);
                    }} data-testid={`vsi-req-accept-invite-${r.id}`}>
                      Inviter
                    </button>
                    <button className="ub-btn-primary" onClick={async () => {
                      await fetch(`${API}/vsi-groups/${groupId}/requests/${r.id}/respond?token=${token}`, {
                        method: "POST", headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ action: "accept", member_type: "regular" })
                      });
                      loadGroup();
                      const res = await fetch(`${API}/vsi-groups/${groupId}/requests?token=${token}`);
                      if (res.ok) setPendingRequests((await res.json()).requests || []);
                    }} data-testid={`vsi-req-accept-regular-${r.id}`}>
                      Accepter
                    </button>
                    <button className="ub-btn-small" style={{ color: "#dc2626" }} onClick={async () => {
                      await fetch(`${API}/vsi-groups/${groupId}/requests/${r.id}/respond?token=${token}`, {
                        method: "POST", headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ action: "reject" })
                      });
                      loadGroup();
                      const res = await fetch(`${API}/vsi-groups/${groupId}/requests?token=${token}`);
                      if (res.ok) setPendingRequests((await res.json()).requests || []);
                    }} data-testid={`vsi-req-reject-${r.id}`}>
                      Refuser
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <div className="ub-vsi-layout" style={{ display: subView === "chat" ? undefined : "none" }}>
        {/* Participants */}
        <div className="ub-vsi-participants" data-testid="vsi-participants">
          <h3 className="ub-vsi-side-title">
            <Users size={15} /> Participants
            <span className="ub-badge indigo" style={{ fontSize: "10px" }}>{(group.participants_detail || []).length}</span>
          </h3>
          <ul className="ub-vsi-participants-list">
            {(group.participants_detail || []).map((p, i) => (
              <li key={i} data-testid={`vsi-participant-${i}`} className="ub-vsi-participant">
                <div className="ub-vsi-participant-avatar">
                  <div className="ub-avatar-sm" style={{ width: "32px", height: "32px", fontSize: "12px" }}>
                    {(p.name || "?").split(" ").map(n => n[0]).join("").slice(0, 2).toUpperCase()}
                  </div>
                  <span
                    className={`ub-vsi-presence-dot ${p.online ? "on" : "off"}`}
                    title={p.online ? "En ligne" : "Hors ligne"}
                  />
                </div>
                <div className="ub-vsi-participant-body">
                  <p className="ub-vsi-participant-name">
                    {p.name}
                    {p.is_me && <span className="ub-badge green" style={{ fontSize: "9px", marginLeft: "6px" }}>Toi</span>}
                    {p.role === "admin" && <span className="ub-badge orange" style={{ fontSize: "9px", marginLeft: "6px" }}>Admin</span>}
                    {p.role === "mentor" && p.role !== "admin" && <span className="ub-badge purple" style={{ fontSize: "9px", marginLeft: "6px" }}>Mentor</span>}
                    {p.role === "invite_provisoire" && <span className="ub-badge indigo" style={{ fontSize: "9px", marginLeft: "6px" }}>Invité</span>}
                  </p>
                  {p.title && <p className="ub-vsi-participant-title">{p.title}</p>}
                </div>
                {!p.is_me && (
                  <button
                    className="ub-btn-small ub-vsi-priv-btn"
                    data-testid={`vsi-priv-msg-${i}`}
                    title="Message privé"
                    onClick={() => onPrivateMessage && onPrivateMessage(p)}
                  >
                    <MessageCircle size={12} />
                  </button>
                )}
              </li>
            ))}
          </ul>
        </div>

        {/* Group chat */}
        <div className="ub-vsi-chat" data-testid="vsi-group-chat">
          <h3 className="ub-vsi-side-title">
            <MessageSquare size={15} /> Discussion de groupe
          </h3>
          <div className="ub-vsi-thread">
            {loadingMsgs ? (
              <p style={{ color: "var(--ub-text-muted)", fontSize: "13px", textAlign: "center", padding: "20px" }}>
                <Loader2 size={14} className="ub-spin" />
              </p>
            ) : messages.length === 0 ? (
              <div style={{ padding: "40px 20px", textAlign: "center", color: "var(--ub-text-muted)" }}>
                <MessageCircle size={28} style={{ opacity: 0.4, marginBottom: "8px" }} />
                <p style={{ fontSize: "13px" }}>Lance la conversation !</p>
              </div>
            ) : messages.map((m, i) => (
              <div key={i} data-testid={`vsi-group-msg-${i}`} className="ub-vsi-msg">
                <div className="ub-avatar-sm" style={{ width: "28px", height: "28px", fontSize: "10px", flexShrink: 0 }}>
                  {(m.from_name || "?").split(" ").map(n => n[0]).join("").slice(0, 2).toUpperCase()}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", gap: "8px" }}>
                    <span className="ub-vsi-msg-author">{m.from_name}</span>
                    <span className="ub-vsi-msg-time">
                      {new Date(m.created_at).toLocaleString("fr-FR", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" })}
                    </span>
                  </div>
                  {m.body && <p className="ub-vsi-msg-body">{m.body}</p>}
                  {(m.attachments || []).length > 0 && (
                    <div style={{ marginTop: m.body ? "6px" : "2px", display: "flex", flexDirection: "column", gap: "6px" }}>
                      {(m.attachments || []).map((a) => {
                        const url = `${process.env.REACT_APP_BACKEND_URL || ""}/api/ubuntoo/attachments/${a.id}`;
                        if (a.is_image) {
                          return (
                            <a key={a.id} href={url} target="_blank" rel="noreferrer" data-testid={`vsi-attach-img-${a.id}`}>
                              <img src={url} alt={a.name}
                                style={{ maxWidth: "260px", maxHeight: "180px", borderRadius: "10px", display: "block", border: "1px solid var(--ub-border)" }}
                              />
                            </a>
                          );
                        }
                        return (
                          <a key={a.id} href={url} target="_blank" rel="noreferrer" download={a.name}
                            data-testid={`vsi-attach-doc-${a.id}`}
                            style={{
                              display: "inline-flex", alignItems: "center", gap: "8px",
                              background: "rgba(0,0,0,0.05)",
                              padding: "8px 10px", borderRadius: "10px", textDecoration: "none",
                              color: "var(--ub-navy)", fontSize: "12px", fontWeight: 600,
                              maxWidth: "240px",
                            }}
                          >
                            <FileText size={16} />
                            <span style={{ flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{a.name}</span>
                            <Download size={14} />
                          </a>
                        );
                      })}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
          {group.is_member && (
            <>
              {pendingAttachments.length > 0 && (
                <div className="ub-pending-attachments" data-testid="vsi-pending-attachments">
                  {pendingAttachments.map((a) => (
                    <div key={a.id} className="ub-pending-chip" data-testid={`vsi-pending-${a.id}`}>
                      {a.is_image ? <ImageIcon size={12} /> : <FileText size={12} />}
                      <span style={{ maxWidth: "120px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{a.name}</span>
                      <button onClick={() => removePending(a.id)} data-testid={`vsi-pending-remove-${a.id}`}><X size={10} /></button>
                    </div>
                  ))}
                </div>
              )}
              <div className="ub-vsi-composer" style={{ position: "relative" }}>
                {/* Emoji button */}
                <button
                  className="ub-icon-btn"
                  data-testid="vsi-emoji-btn"
                  onClick={() => setShowEmojis(v => !v)}
                  title="Insérer un emoji"
                >
                  <Smile size={18} />
                </button>
                {showEmojis && (
                  <div className="ub-emoji-popover" data-testid="vsi-emoji-popover" style={{ left: "12px", bottom: "auto", top: "-160px" }}>
                    {QUICK_EMOJIS.map(e => (
                      <button key={e} onClick={() => insertEmoji(e)} data-testid={`vsi-emoji-${e}`}>
                        <span style={{ fontSize: "22px" }}>{e}</span>
                      </button>
                    ))}
                  </div>
                )}

                {/* Attach */}
                <input
                  ref={groupFileInputRef}
                  type="file"
                  multiple
                  accept="image/*,application/pdf,.doc,.docx,.txt,.csv,.zip"
                  onChange={handleGroupFilePick}
                  style={{ display: "none" }}
                  data-testid="vsi-attach-input"
                />
                <button
                  className="ub-icon-btn"
                  data-testid="vsi-attach-btn"
                  onClick={() => groupFileInputRef.current?.click()}
                  disabled={uploading}
                  title="Joindre un fichier ou une image"
                >
                  {uploading ? <Loader2 size={18} className="ub-spin" /> : <Paperclip size={18} />}
                </button>

                <textarea
                  data-testid="vsi-group-reply"
                  value={reply}
                  onChange={(e) => setReply(e.target.value)}
                  placeholder="Écris un message au groupe…"
                  rows={2}
                  onKeyDown={(e) => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) { e.preventDefault(); send(); } }}
                />
                <button
                  className="ub-btn-primary"
                  data-testid="vsi-group-send"
                  disabled={(!reply.trim() && pendingAttachments.length === 0) || sending}
                  onClick={send}
                  style={{ opacity: ((!reply.trim() && pendingAttachments.length === 0) || sending) ? 0.5 : 1 }}
                >
                  {sending ? <Loader2 size={14} className="ub-spin" /> : <><Send size={14} /> Envoyer</>}
                </button>
              </div>
            </>
          )}
        </div>
      </div>

      {/* === Modal d'invitation de mentor === */}
      {showMentorModal && (
        <div className="ub-vsi-modal-overlay" onClick={() => setShowMentorModal(false)} data-testid="vsi-mentor-modal">
          <div className="ub-vsi-modal" onClick={(e) => e.stopPropagation()}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "16px" }}>
              <h3 style={{ fontSize: "18px", fontWeight: 700, color: "var(--ub-navy)", fontFamily: "'Outfit', sans-serif" }}>
                <Award size={18} style={{ display: "inline", marginRight: "6px", color: "var(--ub-primary)" }} />
                Inviter un mentor au groupe
              </h3>
              <button onClick={() => setShowMentorModal(false)} style={{ background: "none", border: "none", cursor: "pointer", color: "var(--ub-text-muted)" }}>
                <X size={18} />
              </button>
            </div>
            <p style={{ fontSize: "13px", color: "var(--ub-text-secondary)", marginBottom: "12px" }}>
              Sélectionne un pair Ubuntoo. La priorité est donnée aux profils Mentor / Ambassadeur / Pair-aidant.
            </p>
            <input
              type="text"
              value={mentorSearch}
              onChange={(e) => setMentorSearch(e.target.value)}
              placeholder="Rechercher par nom, pseudo ou titre…"
              className="ub-input"
              data-testid="vsi-mentor-search"
              onKeyDown={async (e) => {
                if (e.key === "Enter") {
                  const params = new URLSearchParams({ token });
                  if (mentorSearch.trim()) params.set("search", mentorSearch.trim());
                  const res = await fetch(`${API}/vsi-groups/${groupId}/mentor-candidates?${params.toString()}`);
                  if (res.ok) setMentorCandidates((await res.json()).candidates || []);
                }
              }}
              style={{ marginBottom: "10px" }}
            />
            <button
              className="ub-btn-small"
              data-testid="vsi-mentor-search-btn"
              onClick={async () => {
                const params = new URLSearchParams({ token });
                if (mentorSearch.trim()) params.set("search", mentorSearch.trim());
                const res = await fetch(`${API}/vsi-groups/${groupId}/mentor-candidates?${params.toString()}`);
                if (res.ok) setMentorCandidates((await res.json()).candidates || []);
              }}
              style={{ marginBottom: "14px" }}
            >
              <Sparkles size={12} /> Chercher
            </button>
            <div style={{ maxHeight: "340px", overflowY: "auto", display: "flex", flexDirection: "column", gap: "8px" }}>
              {mentorCandidates.length === 0 ? (
                <p style={{ fontSize: "13px", color: "var(--ub-text-muted)", padding: "16px 0", textAlign: "center" }}>
                  Lance une recherche pour découvrir les pairs disponibles.
                </p>
              ) : mentorCandidates.map((c, i) => (
                <div key={i} data-testid={`vsi-mentor-cand-${i}`} className="ub-vsi-mentor-cand">
                  <div className="ub-avatar-sm" style={{ width: "32px", height: "32px", fontSize: "12px" }}>
                    {(c.name || "?").split(" ").map(n => n[0]).join("").slice(0, 2).toUpperCase()}
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <p style={{ fontSize: "13px", fontWeight: 600, color: "var(--ub-navy)", margin: 0 }}>
                      {c.name}
                      {c.status && <span className="ub-badge purple" style={{ fontSize: "9px", marginLeft: "6px" }}>{c.status}</span>}
                    </p>
                    {c.title && <p style={{ fontSize: "11px", color: "var(--ub-text-muted)", margin: 0 }}>{c.title}</p>}
                  </div>
                  <button
                    className="ub-btn-primary"
                    data-testid={`vsi-mentor-invite-${i}`}
                    onClick={async () => {
                      const res = await fetch(`${API}/vsi-groups/${groupId}/invite-mentor?token=${token}`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ peer_token_id: c.token_id })
                      });
                      if (res.ok) {
                        setMentorCandidates(prev => prev.filter(x => x.token_id !== c.token_id));
                      }
                    }}
                  >
                    Inviter
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
// ============ GROUPES (avec Atelier VSI en premier) ============
const GroupesTab = ({ exchanges, token, onPrivateMessage }) => {
  const [activeVsiGroup, setActiveVsiGroup] = useState(null);
  const [showVsiList, setShowVsiList] = useState(false);
  const [vsiGroups, setVsiGroups] = useState([]);
  const [loadingVsi, setLoadingVsi] = useState(false);
  const [vsiSearch, setVsiSearch] = useState("");
  const [vsiDate, setVsiDate] = useState("");
  const [myVsiGroupId, setMyVsiGroupId] = useState(null);
  const [seedDone, setSeedDone] = useState(false);
  const [selected, setSelected] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newGroup, setNewGroup] = useState({ name: "", session_date: "", session_end_date: "", location: "", theme: "" });
  const [creating, setCreating] = useState(false);
  const [pendingInvites, setPendingInvites] = useState([]);
  const groupExchanges = selected ? exchanges.filter(e => e.group === selected) : [];

  const loadPendingInvites = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API}/vsi-groups/invitations/mine?token=${token}&role=received`);
      if (res.ok) {
        const data = await res.json();
        setPendingInvites((data.invitations || []).filter(i => i.status === "pending"));
      }
    } catch (_) {}
  }, [token]);

  useEffect(() => { loadPendingInvites(); }, [loadPendingInvites]);

  const respondInvite = async (invId, answer) => {
    try {
      const res = await fetch(`${API}/vsi-groups/invitations/${invId}/respond?token=${token}`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answer }),
      });
      if (res.ok) {
        toast.success(answer === "accepted" ? "Tu as rejoint le groupe !" : "Invitation déclinée");
        loadPendingInvites();
        loadVsiGroups();
      } else {
        const err = await res.json();
        toast.error(err.detail || "Échec");
      }
    } catch (_) {}
  };

  const otherGroups = groups.filter(g => g.id !== "vsi");

  const loadVsiGroups = useCallback(async () => {
    if (!token) return;
    setLoadingVsi(true);
    try {
      const params = new URLSearchParams({ token });
      if (vsiSearch.trim()) params.set("search", vsiSearch.trim());
      if (vsiDate) params.set("session_date", vsiDate);
      const res = await fetch(`${API}/vsi-groups?${params.toString()}`);
      if (res.ok) {
        const data = await res.json();
        setVsiGroups(data.groups || []);
        setMyVsiGroupId(data.my_group_id || null);
      }
    } catch (_) {} finally { setLoadingVsi(false); }
  }, [token, vsiSearch, vsiDate]);

  useEffect(() => {
    if (showVsiList) loadVsiGroups();
  }, [showVsiList, loadVsiGroups]);

  const handleSeedDemo = async () => {
    if (!token) return;
    try {
      await fetch(`${API}/vsi-groups/seed-demo?token=${token}`, { method: "POST" });
      setSeedDone(true);
      loadVsiGroups();
    } catch (_) {}
  };

  // If we are inside a specific VSI group, show its detail
  if (activeVsiGroup) {
    return <VsiGroupDetail
      groupId={activeVsiGroup}
      token={token}
      onClose={() => setActiveVsiGroup(null)}
      onPrivateMessage={onPrivateMessage}
    />;
  }

  return (
    <div>
      <h1 className="ub-page-title">{`Groupes Th\u00e9matiques`}</h1>
      <p className="ub-page-intro">{`Rejoignez une communaut\u00e9 de professionnels engag\u00e9s.`}</p>

      {/* === Invitations VSI en attente === */}
      {pendingInvites.length > 0 && (
        <div className="ub-invite-banner" data-testid="pending-invites-banner">
          <div className="ub-invite-banner-head">
            <Mail size={16} style={{ color: "var(--ub-primary)" }} />
            <h3 style={{ fontSize: "14px", fontWeight: 700, color: "var(--ub-navy)", margin: 0 }}>
              {pendingInvites.length} invitation{pendingInvites.length > 1 ? "s" : ""} à un groupe VSI
            </h3>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "8px", marginTop: "8px" }}>
            {pendingInvites.map(inv => (
              <div key={inv.id} className="ub-invite-row" data-testid={`pending-invite-${inv.id}`}>
                <div style={{ flex: 1 }}>
                  <p style={{ fontSize: "13px", fontWeight: 600, color: "var(--ub-navy)", margin: 0 }}>
                    « {inv.group_name} » — {inv.inviter_name} t'invite à rejoindre
                  </p>
                  {inv.message && <p style={{ fontSize: "12px", color: "var(--ub-text-muted)", margin: "2px 0 0", fontStyle: "italic" }}>« {inv.message} »</p>}
                </div>
                <div style={{ display: "flex", gap: "6px" }}>
                  <button className="ub-btn-primary" onClick={() => respondInvite(inv.id, "accepted")} data-testid={`invite-accept-${inv.id}`}>
                    <Check size={12} /> Accepter
                  </button>
                  <button className="ub-btn-small" onClick={() => respondInvite(inv.id, "declined")} data-testid={`invite-decline-${inv.id}`}>
                    <X size={12} /> Décliner
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* === ATELIER VSI — Mis en avant en premier === */}
      <div className="ub-vsi-featured" data-testid="vsi-featured-card">
        <div className="ub-vsi-featured-content">
          <div className="ub-vsi-featured-icon">
            <Target size={28} />
          </div>
          <div style={{ flex: 1 }}>
            <span className="ub-badge orange" style={{ fontSize: "10px", marginBottom: "8px", display: "inline-block" }}>Atelier signature</span>
            <h2 className="ub-vsi-featured-title">Atelier VSI</h2>
            <p className="ub-vsi-featured-subtitle">Valoriser Son Identité professionnelle</p>
            <p className="ub-vsi-featured-desc">
              Retrouve la cohorte VSI à laquelle tu as participé et reste en contact avec tes pairs.
              Chaque cohorte porte un nom unique (Les Mange Tout, Les Intouchables, Les Visionnaires…) et conserve son espace d'échanges.
            </p>
            <div style={{ display: "flex", gap: "10px", marginTop: "14px", flexWrap: "wrap" }}>
              <button
                className="ub-btn-primary"
                onClick={() => setShowVsiList(v => !v)}
                data-testid="vsi-join-btn"
              >
                {showVsiList ? "Masquer les groupes VSI" : "Rejoindre un groupe VSI"} <ArrowRight size={14} />
              </button>
              <button
                className="ub-btn-small"
                onClick={() => setShowCreateModal(true)}
                data-testid="vsi-create-btn"
                style={{ background: "white" }}
              >
                <Sparkles size={12} /> Créer un nouveau groupe
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* === LISTE VSI (recherche par nom + date) === */}
      {showVsiList && (
        <div className="ub-vsi-list-wrap" data-testid="vsi-list-wrap">
          <div className="ub-vsi-filters">
            <div style={{ flex: 1, minWidth: "200px", position: "relative" }}>
              <input
                type="text"
                value={vsiSearch}
                onChange={(e) => setVsiSearch(e.target.value)}
                placeholder="Rechercher par nom (ex: Les Mange Tout)"
                data-testid="vsi-search-name"
                className="ub-input"
              />
            </div>
            <div>
              <input
                type="date"
                value={vsiDate}
                onChange={(e) => setVsiDate(e.target.value)}
                data-testid="vsi-search-date"
                className="ub-input"
                style={{ minWidth: "160px" }}
              />
            </div>
            {(vsiSearch || vsiDate) && (
              <button className="ub-btn-small" onClick={() => { setVsiSearch(""); setVsiDate(""); }} data-testid="vsi-clear-filters">
                <X size={12} /> Effacer
              </button>
            )}
          </div>

          {loadingVsi ? (
            <p style={{ color: "var(--ub-text-muted)", textAlign: "center", padding: "20px" }}>
              <Loader2 size={16} className="ub-spin" />
            </p>
          ) : vsiGroups.length === 0 ? (
            <div className="ub-profile-card" style={{ textAlign: "center", padding: "30px 20px" }}>
              <p style={{ fontSize: "14px", color: "var(--ub-text-secondary)", marginBottom: "12px" }}>
                {(vsiSearch || vsiDate) ? "Aucun groupe VSI ne correspond à ta recherche." : "Aucun groupe VSI pour l'instant."}
              </p>
              {!seedDone && !vsiSearch && !vsiDate && (
                <button className="ub-btn-small" onClick={handleSeedDemo} data-testid="vsi-seed-btn">
                  <Sparkles size={12} /> Charger les groupes de démo
                </button>
              )}
            </div>
          ) : (
            <div className="ub-vsi-cards ub-stagger">
              {vsiGroups.map((g) => (
                <div key={g.id} className="ub-vsi-card" data-testid={`vsi-card-${g.id}`}>
                  <div className="ub-vsi-card-head">
                    <h3 className="ub-vsi-card-name">{g.name}</h3>
                    {g.is_member && <span className="ub-badge green" style={{ fontSize: "10px" }}>Membre</span>}
                  </div>
                  <p className="ub-vsi-card-meta">
                    <CalendarDays size={12} /> Session du {new Date(g.session_date).toLocaleDateString("fr-FR")}
                    {g.session_end_date && ` au ${new Date(g.session_end_date).toLocaleDateString("fr-FR")}`}
                  </p>
                  {g.location && <p className="ub-vsi-card-meta"><MapPin size={12} /> {g.location}</p>}
                  {g.theme && <p className="ub-vsi-card-theme">{g.theme}</p>}
                  <div className="ub-vsi-card-footer">
                    <span style={{ fontSize: "12px", color: "var(--ub-text-muted)" }}>
                      <Users size={12} style={{ verticalAlign: "middle", marginRight: "4px" }} />
                      {g.participant_count} participants
                    </span>
                    {g.is_member ? (
                      <button
                        className="ub-btn-primary"
                        data-testid={`vsi-open-${g.id}`}
                        onClick={() => setActiveVsiGroup(g.id)}
                      >
                        Ouvrir <ArrowRight size={12} />
                      </button>
                    ) : (
                      <button
                        className="ub-btn-primary"
                        data-testid={`vsi-request-${g.id}`}
                        onClick={async () => {
                          const memberType = window.confirm(
                            "Souhaitez-vous rejoindre en tant que :\n\n• OK : Membre régulier\n• Annuler : Invité provisoire"
                          ) ? "regular" : "invite_provisoire";
                          const message = window.prompt("Message à l'administrateur du groupe (facultatif) :", "") || "";
                          try {
                            const res = await fetch(`${API}/vsi-groups/${g.id}/request-join?token=${token}`, {
                              method: "POST",
                              headers: { "Content-Type": "application/json" },
                              body: JSON.stringify({ requested_type: memberType, message })
                            });
                            if (res.ok) {
                              alert("✓ Demande envoyée à l'administrateur du groupe.");
                            } else {
                              const err = await res.json();
                              alert("Erreur : " + (err.detail || "Impossible d'envoyer la demande"));
                            }
                          } catch (_) {}
                        }}
                      >
                        Demander à rejoindre
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* === Autres groupes thématiques === */}
      <h2 className="ub-section-h2" style={{ marginTop: "32px" }}>Autres groupes thématiques</h2>
      <div className="ub-groups-grid">
        {otherGroups.map(g => {
          const count = exchanges.filter(e => e.group === g.id).length;
          return (
            <div key={g.id} className="ub-group-card" onClick={() => setSelected(g.id)} data-testid={`group-${g.id}`}
              style={{ borderTop: `3px solid var(--ub-${g.colorClass})` }}>
              <h3 style={{ fontSize: "16px", fontWeight: 600, marginBottom: "8px", color: "var(--ub-navy)" }}>{g.title}</h3>
              <div style={{ display: "flex", gap: "16px", fontSize: "13px", color: "var(--ub-text-secondary)", marginBottom: "12px" }}>
                <span style={{ display: "flex", alignItems: "center", gap: "4px" }}><Users size={14} />{g.members} membres</span>
                <span style={{ display: "flex", alignItems: "center", gap: "4px" }}><MessageCircle size={14} />{count || g.topics} sujets</span>
              </div>
              <button className={`ub-badge ${g.colorClass}`} style={{ cursor: "pointer" }}>Rejoindre</button>
            </div>
          );
        })}
      </div>
      {selected && (
        <div className="ub-profile-card" style={{ marginTop: "8px" }}>
          <h3 style={{ fontSize: "16px", fontWeight: 600, marginBottom: "16px", color: "var(--ub-navy)" }}>{`\u00c9changes \u2014 ${otherGroups.find(g => g.id === selected)?.title}`}</h3>
          {groupExchanges.length > 0 ? groupExchanges.map(e => (
            <div key={e.id} style={{ background: "var(--ub-border-light)", padding: "12px 16px", borderRadius: "var(--ub-radius-sm)", marginBottom: "8px" }}>
              <h4 style={{ fontSize: "14px", fontWeight: 500, color: "var(--ub-text-primary)" }}>{e.title || e.content_summary?.slice(0, 60)}</h4>
              <p style={{ fontSize: "12px", color: "var(--ub-text-secondary)", marginTop: "4px" }}>{`par ${e.author || "Anonyme"} \u00b7 ${e.exchange_type}`}</p>
            </div>
          )) : <p style={{ color: "var(--ub-text-secondary)", fontSize: "14px" }}>{`Aucun \u00e9change dans ce groupe.`}</p>}
        </div>
      )}

      {/* === Modal création d'un nouveau groupe VSI === */}
      {showCreateModal && (
        <div className="ub-vsi-modal-overlay" data-testid="vsi-create-modal" onClick={() => setShowCreateModal(false)}>
          <div className="ub-vsi-modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: "560px" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "16px" }}>
              <h3 style={{ fontSize: "18px", fontWeight: 700, color: "var(--ub-navy)", fontFamily: "'Outfit', sans-serif" }}>
                <Sparkles size={18} style={{ display: "inline", marginRight: "6px", color: "var(--ub-primary)" }} />
                Créer un nouveau groupe VSI
              </h3>
              <button onClick={() => setShowCreateModal(false)} style={{ background: "none", border: "none", cursor: "pointer", color: "var(--ub-text-muted)" }}>
                <X size={18} />
              </button>
            </div>
            <p style={{ fontSize: "12px", color: "var(--ub-text-muted)", marginBottom: "16px", padding: "10px 14px", background: "var(--ub-gold-bg)", borderRadius: "10px", border: "1px solid var(--ub-gold-light)" }}>
              <Trophy size={12} style={{ display: "inline", marginRight: "4px", verticalAlign: "middle" }} />
              Tu seras automatiquement <strong>admin</strong> et ton statut Ubuntoo passera à <strong>Mentor</strong>.
            </p>
            <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
              <div>
                <label style={{ fontSize: "11px", color: "var(--ub-text-muted)", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em" }}>Nom de la cohorte *</label>
                <input
                  className="ub-input"
                  data-testid="vsi-create-name"
                  value={newGroup.name}
                  onChange={(e) => setNewGroup({ ...newGroup, name: e.target.value })}
                  placeholder="Ex: Les Pionniers du Sud"
                />
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
                <div>
                  <label style={{ fontSize: "11px", color: "var(--ub-text-muted)", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em" }}>Début *</label>
                  <input
                    className="ub-input"
                    data-testid="vsi-create-date-start"
                    type="date"
                    value={newGroup.session_date}
                    onChange={(e) => setNewGroup({ ...newGroup, session_date: e.target.value })}
                  />
                </div>
                <div>
                  <label style={{ fontSize: "11px", color: "var(--ub-text-muted)", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em" }}>Fin (facultatif)</label>
                  <input
                    className="ub-input"
                    data-testid="vsi-create-date-end"
                    type="date"
                    value={newGroup.session_end_date}
                    onChange={(e) => setNewGroup({ ...newGroup, session_end_date: e.target.value })}
                  />
                </div>
              </div>
              <div>
                <label style={{ fontSize: "11px", color: "var(--ub-text-muted)", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em" }}>Lieu</label>
                <input
                  className="ub-input"
                  data-testid="vsi-create-location"
                  value={newGroup.location}
                  onChange={(e) => setNewGroup({ ...newGroup, location: e.target.value })}
                  placeholder="Ex: Paris, En ligne…"
                />
              </div>
              <div>
                <label style={{ fontSize: "11px", color: "var(--ub-text-muted)", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em" }}>Thème</label>
                <input
                  className="ub-input"
                  data-testid="vsi-create-theme"
                  value={newGroup.theme}
                  onChange={(e) => setNewGroup({ ...newGroup, theme: e.target.value })}
                  placeholder="Ex: Reconversion & transition pro"
                />
              </div>
              <div style={{ display: "flex", gap: "8px", justifyContent: "flex-end", marginTop: "8px" }}>
                <button className="ub-btn-small" onClick={() => setShowCreateModal(false)}>Annuler</button>
                <button
                  className="ub-btn-primary"
                  disabled={!newGroup.name.trim() || !newGroup.session_date || creating}
                  data-testid="vsi-create-submit"
                  onClick={async () => {
                    setCreating(true);
                    try {
                      const res = await fetch(`${API}/vsi-groups?token=${token}`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(newGroup)
                      });
                      if (res.ok) {
                        const created = await res.json();
                        setShowCreateModal(false);
                        setNewGroup({ name: "", session_date: "", session_end_date: "", location: "", theme: "" });
                        if (!showVsiList) setShowVsiList(true);
                        loadVsiGroups();
                        // Ouvrir le groupe créé directement
                        setActiveVsiGroup(created.id);
                      }
                    } catch (_) {} finally { setCreating(false); }
                  }}
                >
                  {creating ? <Loader2 size={14} className="ub-spin" /> : "Créer"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// ============ DISCUSSIONS ============
const DiscussionsTab = ({ exchanges, onPost }) => {
  const [filter, setFilter] = useState("all");
  const [showForm, setShowForm] = useState(false);
  const [posting, setPosting] = useState(false);
  const [posted, setPosted] = useState(false);
  const [form, setForm] = useState({ title: "", content: "", exchange_type: "discussion", group: "reconversion", author: "Anonyme" });
  const filtered = exchanges.filter(t => filter === "all" || t.exchange_type === filter);

  const handleSubmit = async () => {
    if (!form.title.trim() || !form.content.trim()) return;
    setPosting(true);
    try {
      const res = await fetch(`${API}/ubuntoo/community/exchanges`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(form) });
      if (res.ok) {
        const data = await res.json();
        onPost(data.exchange);
        setForm({ title: "", content: "", exchange_type: "discussion", group: "reconversion", author: "Anonyme" });
        setShowForm(false);
        setPosted(true);
        setTimeout(() => setPosted(false), 4000);
      }
    } catch (e) { console.error(e); } finally { setPosting(false); }
  };

  const inputStyle = { background: "var(--ub-bg)", border: "1px solid var(--ub-border)", borderRadius: "var(--ub-radius-sm)", padding: "10px 14px", color: "var(--ub-text-primary)", fontSize: "14px", outline: "none", width: "100%" };
  const selectStyle = { ...inputStyle, width: "auto", fontSize: "13px", padding: "8px 12px" };

  return (
    <div>
      <h1 className="ub-page-title">Forum d'échanges</h1>
      <p className="ub-page-intro">{`Forum d'entraide de la communaut\u00e9 Ubuntoo`}</p>
      {posted && <div className="ub-notice" data-testid="post-success-notice"><CheckCircle size={16} style={{ display: "inline", verticalAlign: "middle", marginRight: "6px" }} />{`\u00c9change publi\u00e9 ! Les signaux d\u00e9tect\u00e9s apparaitront dans l'Observatoire.`}</div>}
      <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", marginBottom: "24px", alignItems: "center" }}>
        {[{ k: "all", l: "Tous" }, { k: "question", l: "Questions" }, { k: "discussion", l: "Discussions" }, { k: "aide", l: "Entraide" }, { k: "retour_experience", l: "Retours" }].map(f => (
          <button key={f.k} className={`ub-filter-btn ${filter === f.k ? "active" : ""}`} onClick={() => setFilter(f.k)}>{f.l}</button>
        ))}
        <button className="ub-btn-primary" style={{ marginLeft: "auto", padding: "8px 16px", fontSize: "13px" }} onClick={() => setShowForm(!showForm)} data-testid="new-exchange-btn"><Send size={14} /> Publier</button>
      </div>
      {showForm && (
        <div className="ub-profile-card" style={{ marginBottom: "24px" }} data-testid="new-exchange-form">
          <h3 style={{ fontSize: "15px", fontWeight: 600, marginBottom: "16px", color: "var(--ub-navy)" }}>{`Nouvel \u00e9change`}</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            <input type="text" placeholder="Titre" value={form.title} onChange={e => setForm(p => ({ ...p, title: e.target.value }))} data-testid="exchange-title-input" style={inputStyle} />
            <textarea placeholder={`D\u00e9crivez votre question ou exp\u00e9rience...`} value={form.content} onChange={e => setForm(p => ({ ...p, content: e.target.value }))} rows={3} data-testid="exchange-content-input" style={{ ...inputStyle, resize: "vertical" }} />
            <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
              <select value={form.exchange_type} onChange={e => setForm(p => ({ ...p, exchange_type: e.target.value }))} data-testid="exchange-type-select" style={selectStyle}>
                <option value="discussion">Discussion</option><option value="question">Question</option><option value="aide">Entraide</option><option value="retour_experience">Retour d'exp.</option>
              </select>
              <select value={form.group} onChange={e => setForm(p => ({ ...p, group: e.target.value }))} data-testid="exchange-group-select" style={selectStyle}>
                {groups.map(g => <option key={g.id} value={g.id}>{g.title}</option>)}
              </select>
              <input type="text" placeholder="Pseudonyme" value={form.author} onChange={e => setForm(p => ({ ...p, author: e.target.value }))} data-testid="exchange-author-input" style={{ ...selectStyle, flex: 1, minWidth: "100px" }} />
            </div>
            <div style={{ display: "flex", gap: "8px", justifyContent: "flex-end" }}>
              <button className="ub-btn-small" onClick={() => setShowForm(false)}>Annuler</button>
              <button className="ub-btn-primary" style={{ padding: "8px 16px", fontSize: "13px", opacity: posting ? 0.6 : 1 }} onClick={handleSubmit} disabled={posting || !form.title.trim() || !form.content.trim()} data-testid="submit-exchange-btn">{posting ? "Analyse IA..." : "Publier"} <Send size={14} /></button>
            </div>
            <p style={{ fontSize: "11px", color: "var(--ub-text-muted)", display: "flex", alignItems: "center", gap: "4px" }}><Radio size={12} />{`Analys\u00e9 par l'IA \u2192 signaux dans l'Observatoire Pr\u00e9dictif.`}</p>
          </div>
        </div>
      )}
      <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
        {filtered.length === 0 && <p style={{ color: "var(--ub-text-secondary)", textAlign: "center", padding: "32px" }}>{`Aucun \u00e9change pour ce filtre.`}</p>}
        {filtered.map(t => (
          <div key={t.id} className="ub-thread-card" data-testid={`thread-${t.id}`}>
            <div style={{ display: "flex", alignItems: "flex-start", gap: "12px" }}>
              <div style={{ marginTop: "2px", color: t.exchange_type === "question" ? "var(--ub-indigo)" : t.exchange_type === "aide" ? "var(--ub-orange)" : "var(--ub-green)" }}>
                {t.exchange_type === "question" ? <HelpCircle size={18} /> : t.exchange_type === "aide" ? <Heart size={18} /> : <MessageSquare size={18} />}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
                  <h3 style={{ fontSize: "14px", fontWeight: 600, color: "var(--ub-text-primary)" }}>{t.title || t.content_summary?.slice(0, 80)}</h3>
                  <span className={`ub-badge ${t.exchange_type === "question" ? "indigo" : t.exchange_type === "aide" ? "orange" : "green"}`} style={{ fontSize: "10px", padding: "2px 8px" }}>
                    {t.exchange_type === "retour_experience" ? "Retour" : t.exchange_type}
                  </span>
                </div>
                <p style={{ fontSize: "13px", color: "var(--ub-text-secondary)", marginTop: "4px", lineHeight: 1.5 }}>{t.content_summary}</p>
                <div style={{ display: "flex", alignItems: "center", gap: "12px", marginTop: "8px", fontSize: "12px", color: "var(--ub-text-muted)" }}>
                  <span style={{ fontWeight: 500, color: "var(--ub-text-secondary)" }}>{t.author || "Anonyme"}</span>
                  {t.likes > 0 && <span style={{ display: "flex", alignItems: "center", gap: "3px" }}><ThumbsUp size={12} />{t.likes}</span>}
                  {t.replies_count > 0 && <span style={{ display: "flex", alignItems: "center", gap: "3px" }}><MessageCircle size={12} />{t.replies_count}</span>}
                  <span style={{ display: "flex", alignItems: "center", gap: "3px" }}><Clock size={12} />{t.timestamp ? new Date(t.timestamp).toLocaleDateString("fr-FR") : ""}</span>
                </div>
                {(t.detected_skills?.length > 0 || t.detected_tools?.length > 0) && (
                  <div style={{ display: "flex", gap: "4px", marginTop: "8px", flexWrap: "wrap" }}>
                    {t.detected_skills?.slice(0, 4).map((s, i) => <span key={i} className="ub-badge blue" style={{ fontSize: "10px", padding: "2px 8px" }}>{s}</span>)}
                    {t.detected_tools?.slice(0, 2).map((tool, i) => <span key={`t-${i}`} className="ub-badge purple" style={{ fontSize: "10px", padding: "2px 8px" }}>{tool}</span>)}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// ============ MENTORAT ============
// ============ MENTORAT (réel — connecté au backend) ============
const MentoratTab = ({ token }) => {
  const [mentors, setMentors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [focusFilter, setFocusFilter] = useState("");
  const [sentRequests, setSentRequests] = useState([]);
  const [showRequestModal, setShowRequestModal] = useState(false);
  const [requestMentor, setRequestMentor] = useState(null);
  const [motivation, setMotivation] = useState("");
  const [objectives, setObjectives] = useState("");
  const [cadence, setCadence] = useState("1h / semaine");
  const [sending, setSending] = useState(false);

  const loadMentors = useCallback(async (silent = true) => {
    if (!token) return;
    setLoading(true);
    try {
      const params = new URLSearchParams({ token, limit: "30" });
      if (focusFilter.trim()) params.set("focus", focusFilter.trim());
      const res = await fetch(`${API}/ubuntoo/mentors?${params.toString()}`);
      if (res.ok) {
        const data = await res.json();
        setMentors(data.mentors || []);
        if (!silent) {
          const n = (data.mentors || []).length;
          if (n === 0) toast.info(`Aucun mentor pour « ${focusFilter.trim() || "tous"} »`);
          else toast.success(`${n} mentor${n > 1 ? "s" : ""} trouvé${n > 1 ? "s" : ""}`);
        }
      }
    } catch (_) {} finally { setLoading(false); }
  }, [token, focusFilter]);

  const loadSent = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API}/ubuntoo/mentors/requests?token=${token}&role=sent`);
      if (res.ok) {
        const data = await res.json();
        setSentRequests(data.requests || []);
      }
    } catch (_) {}
  }, [token]);

  useEffect(() => { loadMentors(); loadSent(); }, [loadMentors, loadSent]);

  const openRequestModal = (mentor) => {
    if (mentor.request_pending) {
      toast.info("Tu as déjà une demande en attente avec ce mentor.");
      return;
    }
    setRequestMentor(mentor);
    setMotivation("");
    setObjectives("");
    setCadence("1h / semaine");
    setShowRequestModal(true);
  };

  const sendRequest = async () => {
    if (motivation.trim().length < 20) {
      toast.error("Décris ta motivation (20 caractères minimum).");
      return;
    }
    setSending(true);
    try {
      const res = await fetch(`${API}/ubuntoo/mentors/${requestMentor.token_id}/request?token=${token}`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          motivation: motivation.trim(),
          objectives: objectives.trim(),
          cadence: cadence.trim(),
        }),
      });
      if (res.ok) {
        toast.success(`Demande envoyée à ${requestMentor.name}`);
        setShowRequestModal(false);
        setRequestMentor(null);
        loadMentors();
        loadSent();
      } else {
        const err = await res.json();
        toast.error(err.detail || "Impossible d'envoyer la demande");
      }
    } catch (_) {
      toast.error("Erreur réseau");
    } finally { setSending(false); }
  };

  if (!token) {
    return (
      <div>
        <h1 className="ub-page-title">Mentorat</h1>
        <p className="ub-page-intro">Connecte-toi à Re'Actif Pro pour solliciter un mentor.</p>
      </div>
    );
  }

  const statusOf = (rq) => {
    if (rq.status === "accepted") return { label: "Acceptée", cls: "green" };
    if (rq.status === "declined") return { label: "Déclinée", cls: "red" };
    return { label: "En attente", cls: "orange" };
  };

  return (
    <div data-testid="mentorat-tab">
      <h1 className="ub-page-title">Mentorat</h1>
      <p className="ub-page-intro">
        Sollicite un <strong>pair Ubuntoo expérimenté</strong> (8 ans+ d'expérience) pour t'accompagner sur un objectif précis.
      </p>

      {/* Search/filter */}
      <div className="ub-mentor-filter-bar" data-testid="mentor-filter-bar">
        <Search size={14} style={{ color: "var(--ub-text-muted)" }} />
        <input
          type="text"
          value={focusFilter}
          onChange={(e) => setFocusFilter(e.target.value)}
          placeholder="Filtrer : compétence, secteur, métier… (ex: reconversion, RH, communication)"
          data-testid="mentor-filter-input"
          onKeyDown={(e) => { if (e.key === "Enter") loadMentors(false); }}
        />
        <button className="ub-btn-small" onClick={() => loadMentors(false)} data-testid="mentor-filter-apply">
          Filtrer
        </button>
      </div>

      {/* Sent requests overview */}
      {sentRequests.length > 0 && (
        <div className="ub-mentor-sent" data-testid="mentor-sent">
          <h3 style={{ fontSize: "13px", fontWeight: 700, color: "var(--ub-navy)", marginBottom: "8px" }}>
            Mes demandes envoyées ({sentRequests.length})
          </h3>
          <div className="ub-pill-row" style={{ flexWrap: "wrap" }}>
            {sentRequests.slice(0, 6).map((rq) => {
              const st = statusOf(rq);
              return (
                <span key={rq.id} className={`ub-badge ${st.cls}`} style={{ fontSize: "11px" }} data-testid={`mentor-sent-${rq.id}`}>
                  {rq.to_name} · {st.label}
                </span>
              );
            })}
          </div>
        </div>
      )}

      {/* Mentors list */}
      {loading ? (
        <div className="ub-search-empty"><Loader2 size={20} className="ub-spin" style={{ color: "var(--ub-primary)" }} /></div>
      ) : mentors.length === 0 ? (
        <div className="ub-search-empty" data-testid="mentors-empty">
          <Heart size={32} style={{ color: "var(--ub-text-muted)", opacity: 0.4 }} />
          <p style={{ marginTop: "10px", color: "var(--ub-text-muted)", fontSize: "13px" }}>
            Aucun mentor disponible pour ces critères. Élargis ta recherche !
          </p>
        </div>
      ) : (
        <div className="ub-mentor-grid" data-testid="mentor-grid">
          {mentors.map((m) => (
            <div key={m.token_id} className="ub-mentor-card-real" data-testid={`mentor-card-${m.token_id}`}>
              <div className="ub-mentor-avatar">{(m.name || "?").split(" ").map(n => n[0]).join("").slice(0, 2).toUpperCase()}</div>
              <h3 style={{ fontSize: "15px", fontWeight: 700, marginBottom: "2px", color: "var(--ub-navy)", fontFamily: "'Outfit', sans-serif" }}>{m.name}</h3>
              {m.title && <p className="ub-mentor-title"><Briefcase size={11} /> {m.title}</p>}
              {m.territory && <p className="ub-mentor-meta"><MapPin size={11} /> {m.territory}</p>}
              <p className="ub-mentor-focus">
                <Sparkles size={11} /> Spécialité : <strong>{m.focus}</strong>
              </p>
              <p className="ub-mentor-meta">
                <Clock size={11} /> {m.experience_years} ans d'expérience · {m.availability}
              </p>
              {(m.softskills || []).length > 0 && (
                <div className="ub-pill-row" style={{ marginTop: "6px" }}>
                  {m.softskills.slice(0, 3).map((s, i) => (
                    <span key={i} className="ub-pill ub-pill-savoir-etre">{s}</span>
                  ))}
                </div>
              )}
              <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "4px", marginTop: "10px" }}>
                <Star size={14} style={{ color: "#f59e0b", fill: "#f59e0b" }} />
                <span style={{ color: "#92400e", fontSize: "13px", fontWeight: 600 }}>{m.rating}</span>
              </div>
              <button
                className={`ub-btn-${m.request_pending ? "small" : "primary"}`}
                style={{ marginTop: "14px", width: "100%", justifyContent: "center" }}
                onClick={() => openRequestModal(m)}
                disabled={m.request_pending}
                data-testid={`mentor-request-btn-${m.token_id}`}
              >
                {m.request_pending ? <><CheckCircle size={13} /> Demande envoyée</> : <><Heart size={13} /> Demander un mentorat</>}
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Request modal */}
      {showRequestModal && requestMentor && (
        <div className="ub-vsi-modal-overlay" data-testid="mentor-request-modal" onClick={() => setShowRequestModal(false)}>
          <div className="ub-vsi-modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: "540px" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "12px" }}>
              <h3 style={{ fontSize: "17px", fontWeight: 700, color: "var(--ub-navy)", fontFamily: "'Outfit', sans-serif", display: "flex", alignItems: "center", gap: "8px" }}>
                <Heart size={16} style={{ color: "var(--ub-primary)" }} />
                Demande de mentorat → {requestMentor.name}
              </h3>
              <button onClick={() => setShowRequestModal(false)} style={{ background: "none", border: "none", cursor: "pointer", color: "var(--ub-text-muted)" }}>
                <X size={18} />
              </button>
            </div>

            <p style={{ fontSize: "12px", color: "var(--ub-text-muted)", marginBottom: "14px" }}>
              {requestMentor.name} pourra accepter ou décliner ta demande. Tu seras notifié·e dès réponse.
            </p>

            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              <div>
                <label className="ub-form-label">Pourquoi ce mentorat ? *</label>
                <textarea
                  className="ub-input"
                  value={motivation}
                  onChange={(e) => setMotivation(e.target.value)}
                  placeholder="Présente-toi en quelques lignes : ton parcours, ton défi actuel, ce qui t'a attiré chez ce mentor…"
                  rows={4}
                  maxLength={1000}
                  data-testid="mentor-motivation"
                  style={{ resize: "vertical", fontFamily: "inherit" }}
                />
                <p style={{ fontSize: "10px", color: motivation.length < 20 ? "#dc2626" : "var(--ub-text-muted)", marginTop: "2px" }}>
                  {motivation.length}/1000 caractères {motivation.length < 20 && "— 20 minimum"}
                </p>
              </div>

              <div>
                <label className="ub-form-label">Tes objectifs (optionnel)</label>
                <textarea
                  className="ub-input"
                  value={objectives}
                  onChange={(e) => setObjectives(e.target.value)}
                  placeholder="Ex: clarifier mon projet d'évolution, préparer un entretien stratégique, structurer ma reconversion…"
                  rows={2}
                  data-testid="mentor-objectives"
                  style={{ resize: "vertical", fontFamily: "inherit" }}
                />
              </div>

              <div>
                <label className="ub-form-label">Rythme souhaité</label>
                <select
                  className="ub-input"
                  value={cadence}
                  onChange={(e) => setCadence(e.target.value)}
                  data-testid="mentor-cadence"
                >
                  <option value="30 min ponctuel">30 min ponctuel</option>
                  <option value="1h / semaine">1h / semaine</option>
                  <option value="1h / 2 semaines">1h / 2 semaines</option>
                  <option value="1h / mois">1h / mois</option>
                  <option value="À convenir ensemble">À convenir ensemble</option>
                </select>
              </div>
            </div>

            <div style={{ display: "flex", gap: "8px", justifyContent: "flex-end", marginTop: "16px" }}>
              <button className="ub-btn-small" onClick={() => setShowRequestModal(false)} data-testid="mentor-cancel">
                Annuler
              </button>
              <button
                className="ub-btn-primary"
                disabled={sending || motivation.trim().length < 20}
                onClick={sendRequest}
                data-testid="mentor-send"
              >
                {sending ? <Loader2 size={14} className="ub-spin" /> : <><Send size={14} /> Envoyer la demande</>}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// ============ IMPACT ============
const ImpactTab = () => (
  <div>
    <h1 className="ub-page-title">Impact Social</h1>
    <p className="ub-page-intro">{`Impact collectif sur l'insertion professionnelle.`}</p>
    <div className="ub-impact-grid">
      {[
        { label: "Membres actifs", value: "12 450", target: "Objectif 50 000", pct: 25, colorClass: "indigo" },
        { label: `Taux de r\u00e9ussite`, value: "+35%", target: `vs parcours isol\u00e9s`, pct: 70, colorClass: "green" },
        { label: `R\u00e9duction isolement`, value: "-40%", target: "sentiment d'isolement", pct: 60, colorClass: "purple" },
        { label: "Satisfaction", value: "85%", target: `communaut\u00e9`, pct: 85, colorClass: "orange" },
        { label: "Mentors actifs", value: "124", target: "plateforme", pct: 45, colorClass: "cyan" },
        { label: "Groupes actifs", value: "4", target: `th\u00e9matiques`, pct: 80, colorClass: "indigo" },
      ].map((s, i) => (
        <div key={i} className={`ub-impact-card ${s.colorClass}`} data-testid={`impact-${i}`}>
          <p style={{ color: "var(--ub-text-secondary)", fontSize: "13px", marginBottom: "2px" }}>{s.label}</p>
          <div className="ub-impact-value">{s.value}</div>
          <div className="ub-progress"><div className="ub-progress-fill" style={{ width: `${s.pct}%` }} /></div>
          <p style={{ color: "var(--ub-text-muted)", fontSize: "12px" }}>{s.target}</p>
        </div>
      ))}
    </div>
  </div>
);

// ============ RECHERCHE PAR MÉTIER / SECTEUR / RÉGION ============
const SearchTab = ({ token, onMessagePeer }) => {
  const [filters, setFilters] = useState({
    q: "", metier: "", secteur: "", region: "", experience: "", tendance: "", skills: "",
  });
  const [facets, setFacets] = useState({ metiers: [], secteurs: [], regions: [], tendances: [], experience_levels: [] });
  const [results, setResults] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  useEffect(() => {
    if (!token) return;
    fetch(`${API}/ubuntoo/search/facets?token=${token}`)
      .then(r => r.ok ? r.json() : null)
      .then(data => { if (data) setFacets(data); })
      .catch(() => {});
  }, [token]);

  const runSearch = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setHasSearched(true);
    try {
      const params = new URLSearchParams({ token, limit: "30" });
      Object.entries(filters).forEach(([k, v]) => { if (v && String(v).trim()) params.set(k, v); });
      const res = await fetch(`${API}/ubuntoo/search?${params.toString()}`);
      if (res.ok) {
        const data = await res.json();
        setResults(data.peers || []);
        setTotal(data.total || 0);
      }
    } catch (_) {} finally { setLoading(false); }
  }, [token, filters]);

  const resetFilters = () => {
    setFilters({ q: "", metier: "", secteur: "", region: "", experience: "", tendance: "", skills: "" });
    setResults([]); setTotal(0); setHasSearched(false);
  };

  const activeFiltersCount = Object.values(filters).filter(v => v && String(v).trim()).length;

  if (!token) {
    return (
      <div>
        <h1 className="ub-page-title">Rechercher</h1>
        <p className="ub-page-intro">Connecte-toi à Re'Actif Pro pour rechercher des pairs Ubuntoo.</p>
      </div>
    );
  }

  return (
    <div data-testid="search-tab">
      <h1 className="ub-page-title">Rechercher un pair</h1>
      <p className="ub-page-intro">
        Filtre la communauté Ubuntoo par <strong>métier &amp; secteur</strong>, région, niveau d'expérience,
        compétences ou tendance comportementale.
      </p>

      {/* Search bar */}
      <div className="ub-search-card" data-testid="search-form">
        <div className="ub-search-bar">
          <Search size={16} style={{ color: "var(--ub-text-muted)" }} />
          <input
            type="text"
            value={filters.q}
            onChange={(e) => setFilters({ ...filters, q: e.target.value })}
            placeholder="Recherche libre (nom, métier, mots-clés…)"
            data-testid="search-q"
            onKeyDown={(e) => { if (e.key === "Enter") runSearch(); }}
          />
          <button
            className="ub-btn-primary"
            onClick={runSearch}
            disabled={loading}
            data-testid="search-submit"
          >
            {loading ? <Loader2 size={14} className="ub-spin" /> : <><Search size={14} /> Rechercher</>}
          </button>
        </div>

        <div className="ub-search-filters">
          <div className="ub-search-filter">
            <label><Briefcase size={12} /> Métier</label>
            <input
              type="text"
              list="ub-fac-metiers"
              value={filters.metier}
              onChange={(e) => setFilters({ ...filters, metier: e.target.value })}
              placeholder="Ex: Coach, Développeur…"
              data-testid="search-metier"
            />
            <datalist id="ub-fac-metiers">
              {facets.metiers.map((m) => <option key={m} value={m} />)}
            </datalist>
          </div>

          <div className="ub-search-filter">
            <label><Hash size={12} /> Secteur</label>
            <input
              type="text"
              list="ub-fac-secteurs"
              value={filters.secteur}
              onChange={(e) => setFilters({ ...filters, secteur: e.target.value })}
              placeholder="Ex: Formation, Santé…"
              data-testid="search-secteur"
            />
            <datalist id="ub-fac-secteurs">
              {facets.secteurs.map((m) => <option key={m} value={m} />)}
            </datalist>
          </div>

          <div className="ub-search-filter">
            <label><MapPin size={12} /> Région / Ville</label>
            <input
              type="text"
              list="ub-fac-regions"
              value={filters.region}
              onChange={(e) => setFilters({ ...filters, region: e.target.value })}
              placeholder="Ex: Lyon, Paris…"
              data-testid="search-region"
            />
            <datalist id="ub-fac-regions">
              {facets.regions.map((m) => <option key={m} value={m} />)}
            </datalist>
          </div>

          <div className="ub-search-filter">
            <label><TrendingUp size={12} /> Niveau d'expérience</label>
            <select
              value={filters.experience}
              onChange={(e) => setFilters({ ...filters, experience: e.target.value })}
              data-testid="search-experience"
            >
              <option value="">Tous</option>
              {facets.experience_levels.map(l => <option key={l.value} value={l.value}>{l.label}</option>)}
            </select>
          </div>

          <div className="ub-search-filter">
            <label><Heart size={12} /> Tendance comportementale</label>
            <input
              type="text"
              list="ub-fac-tendances"
              value={filters.tendance}
              onChange={(e) => setFilters({ ...filters, tendance: e.target.value })}
              placeholder="Ex: Inspirant, Stratégique…"
              data-testid="search-tendance"
            />
            <datalist id="ub-fac-tendances">
              {facets.tendances.map((m) => <option key={m} value={m} />)}
            </datalist>
          </div>

          <div className="ub-search-filter" style={{ gridColumn: "1 / -1" }}>
            <label><Sparkles size={12} /> Compétences (séparées par des virgules)</label>
            <input
              type="text"
              value={filters.skills}
              onChange={(e) => setFilters({ ...filters, skills: e.target.value })}
              placeholder="Ex: pédagogie, animation, gestion de projet"
              data-testid="search-skills"
            />
          </div>
        </div>

        <div className="ub-search-actions">
          {activeFiltersCount > 0 && (
            <span className="ub-badge indigo" style={{ fontSize: "11px" }}>
              <SlidersHorizontal size={10} /> {activeFiltersCount} filtre{activeFiltersCount > 1 ? "s" : ""}
            </span>
          )}
          <button className="ub-btn-small" onClick={resetFilters} data-testid="search-reset">
            <X size={12} /> Réinitialiser
          </button>
        </div>
      </div>

      {/* Results */}
      <div data-testid="search-results" style={{ marginTop: "20px" }}>
        {!hasSearched ? (
          <div className="ub-search-empty">
            <Search size={36} style={{ color: "var(--ub-text-muted)", opacity: 0.4 }} />
            <p style={{ marginTop: "12px", color: "var(--ub-text-muted)", fontSize: "14px" }}>
              Choisis tes filtres et lance une recherche pour découvrir des pairs Ubuntoo.
            </p>
          </div>
        ) : loading ? (
          <div className="ub-search-empty">
            <Loader2 size={28} className="ub-spin" style={{ color: "var(--ub-primary)" }} />
            <p style={{ marginTop: "10px", color: "var(--ub-text-muted)" }}>Recherche en cours…</p>
          </div>
        ) : results.length === 0 ? (
          <div className="ub-search-empty">
            <Info size={36} style={{ color: "var(--ub-text-muted)", opacity: 0.5 }} />
            <p style={{ marginTop: "12px", fontSize: "14px", color: "var(--ub-text-secondary)" }}>
              Aucun pair ne correspond à tes critères. Élargis ta recherche !
            </p>
          </div>
        ) : (
          <>
            <p style={{ fontSize: "12px", color: "var(--ub-text-muted)", marginBottom: "12px" }}>
              {total} pair{total > 1 ? "s" : ""} trouvé{total > 1 ? "s" : ""}
            </p>
            <div className="ub-search-grid">
              {results.map((p) => (
                <div key={p.token_id} className="ub-search-card-peer" data-testid={`search-peer-${p.token_id}`}>
                  <div className="ub-search-peer-head">
                    <div className="ub-avatar-sm" style={{ width: "44px", height: "44px", fontSize: "14px", flexShrink: 0 }}>
                      {(p.name || "?").split(" ").map(n => n[0]).join("").slice(0, 2).toUpperCase()}
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <h3 className="ub-search-peer-name">
                        {p.name}
                        {p.status && <span className="ub-badge purple" style={{ fontSize: "9px", marginLeft: "6px" }}>{p.status}</span>}
                      </h3>
                      {p.title && <p className="ub-search-peer-title"><Briefcase size={11} /> {p.title}</p>}
                      <p className="ub-search-peer-meta">
                        {p.territory && <><MapPin size={11} /> {p.territory}</>}
                        {p.experience_band && <span className="ub-badge green" style={{ fontSize: "9px", marginLeft: "6px" }}>{p.experience_band === "junior" ? "Junior" : p.experience_band === "confirme" ? "Confirmé" : "Senior"}</span>}
                      </p>
                    </div>
                  </div>

                  {p.tendance_comportementale && (
                    <p className="ub-search-peer-tend">
                      <Heart size={11} /> Tendance : <strong>{p.tendance_comportementale}</strong>
                    </p>
                  )}

                  {(p.sectors || []).length > 0 && (
                    <div className="ub-pill-row" style={{ marginTop: "6px" }}>
                      {p.sectors.slice(0, 3).map((s, i) => <span key={i} className="ub-pill ub-pill-savoir-faire">{s}</span>)}
                    </div>
                  )}

                  {(p.softskills || []).length > 0 && (
                    <div className="ub-pill-row" style={{ marginTop: "4px" }}>
                      {p.softskills.slice(0, 4).map((s, i) => <span key={i} className="ub-pill ub-pill-savoir-etre">{s}</span>)}
                    </div>
                  )}

                  {(p.reasons || []).length > 0 && (
                    <ul className="ub-search-peer-reasons">
                      {p.reasons.map((r, i) => <li key={i}>{r}</li>)}
                    </ul>
                  )}

                  <button
                    className="ub-btn-primary ub-search-peer-cta"
                    data-testid={`search-msg-${p.token_id}`}
                    onClick={() => onMessagePeer && onMessagePeer(p)}
                  >
                    <MessageSquare size={13} /> Envoyer un message
                  </button>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

// ============ MAIN VIEW ============
const UbuntooView = () => {
  const [tab, setTab] = useState("accueil");
  const [exchanges, setExchanges] = useState([]);
  const [ubProfile, setUbProfile] = useState(null);
  const [syncing, setSyncing] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [hasDclic, setHasDclic] = useState(null);
  const [peers, setPeers] = useState([]);
  const [loadingPeers, setLoadingPeers] = useState(false);
  const [groupFilter, setGroupFilter] = useState(null);
  const [contactPeer, setContactPeer] = useState(null);
  const [matchPeer, setMatchPeer] = useState(null);
  const [unreadMessages, setUnreadMessages] = useState(0);
  const [openMessagesPeer, setOpenMessagesPeer] = useState(null);

  const token = typeof window !== "undefined" ? localStorage.getItem("reactif_token") : null;

  const loadPeers = useCallback(async () => {
    if (!token) return;
    setLoadingPeers(true);
    try {
      const url = `${API}/ubuntoo/compatible-peers?token=${token}&limit=6${groupFilter ? `&group=${groupFilter}` : ""}`;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setPeers(data.peers || []);
      }
    } catch (_) {} finally { setLoadingPeers(false); }
  }, [token, groupFilter]);

  useEffect(() => {
    fetch(`${API}/ubuntoo/community/exchanges`).then(r => r.ok ? r.json() : []).then(setExchanges).catch(() => {});
    if (token) {
      setIsLoggedIn(true);
      fetch(`${API}/ubuntoo/profile?token=${token}`)
        .then(r => r.ok ? r.json() : null)
        .then(data => {
          if (data?.synced) setUbProfile(data.profile);
          setHasDclic(!!data?.has_dclic);
        })
        .catch(() => {});
    }
  }, [token]);

  // Gate D'CLIC : utilisateur connecté mais sans test D'CLIC -> afficher écran d'incitation
  const showDclicGate = isLoggedIn && hasDclic === false && ubProfile === null;

  useEffect(() => {
    if (ubProfile && tab === "profil") loadPeers();
  }, [ubProfile, tab, loadPeers]);

  // Poll unread message count regularly
  useEffect(() => {
    if (!token) return;
    const fetchUnread = async () => {
      try {
        const res = await fetch(`${API}/ubuntoo/messages/conversations?token=${token}`);
        if (res.ok) {
          const data = await res.json();
          setUnreadMessages((data || []).reduce((sum, c) => sum + (c.unread || 0), 0));
        }
      } catch (_) {}
    };
    fetchUnread();
    const id = setInterval(fetchUnread, 30000);
    return () => clearInterval(id);
  }, [token, tab]);

  // Heartbeat: signal presence every 60 seconds while Ubuntoo is open
  useEffect(() => {
    if (!token) return;
    const ping = () => {
      fetch(`${API}/ubuntoo/heartbeat?token=${token}`, { method: "POST" }).catch(() => {});
    };
    ping();
    const id = setInterval(ping, 60000);
    return () => clearInterval(id);
  }, [token]);

  const handleSync = useCallback(async () => {
    if (!token) return;
    setSyncing(true);
    try {
      const res = await fetch(`${API}/ubuntoo/sync-profile?token=${token}`, { method: "POST" });
      if (res.ok) {
        const data = await res.json();
        setUbProfile(data.profile);
        if (!tab || tab === "accueil") setTab("profil");
        loadPeers();
      }
    } catch (e) { console.error(e); } finally { setSyncing(false); }
  }, [token, tab, loadPeers]);

  const handleNewExchange = (exchange) => setExchanges(prev => [exchange, ...prev]);

  const tabs = [
    { id: "accueil", label: "Accueil", icon: Home },
    { id: "profil", label: "Profil", icon: User },
    { id: "groupes", label: "Groupes", icon: Users },
    { id: "messages", label: "Messages", icon: MessageSquare, badge: unreadMessages },
    { id: "discussions", label: "Forum", icon: MessageCircle },
    { id: "mentorat", label: "Mentorat", icon: Heart },
    { id: "rechercher", label: "Rechercher", icon: Search },
  ];

  return (
    <div className="ubuntoo-page" data-testid="ubuntoo-view">
      <nav className="ub-nav">
        <div className="ub-nav-brand">
          <a href="/dashboard" title={`Retour \u00e0 Re'Actif Pro`} style={{ display: "flex", alignItems: "center" }}>
            <LogoReactifPro size="sm" />
          </a>
          <img src={LOGO} alt="Ubuntoo" style={{ height: "42px", opacity: 0.95 }} />
        </div>
        <div className="ub-nav-links">
          {tabs.map(t => (
            <button key={t.id} onClick={() => setTab(t.id)} data-testid={`ubuntoo-tab-${t.id}`}
              className={`ub-nav-link ${tab === t.id ? "active" : ""}`}
              style={{ position: "relative" }}>
              <t.icon size={16} />{t.label}
              {t.badge > 0 && (
                <span data-testid={`tab-badge-${t.id}`} style={{
                  position: "absolute", top: "-4px", right: "-6px",
                  background: "#ef4444", color: "white", fontSize: "10px", fontWeight: 700,
                  padding: "1px 5px", borderRadius: "10px", minWidth: "16px", textAlign: "center"
                }}>{t.badge}</span>
              )}
            </button>
          ))}
        </div>
      </nav>
      <div className="ub-content">
        {showDclicGate ? (
          <div className="ub-dclic-gate" data-testid="dclic-gate">
            <div className="ub-dclic-gate-card">
              <div className="ub-dclic-gate-icon"><Target size={32} /></div>
              <span className="ub-eu-eyebrow" style={{ background: "rgba(220,164,61,0.18)", color: "var(--ub-gold-dark)", borderColor: "rgba(220,164,61,0.35)" }}>
                Test requis
              </span>
              <h2 className="ub-dclic-gate-title">
                Pour rejoindre Ubuntoo, passe d'abord ton test D'CLIC&nbsp;PRO
              </h2>
              <p className="ub-dclic-gate-desc">
                Ubuntoo personnalise ton profil contributif à partir de ta <strong>carte d'identité pro D'CLIC</strong> :
                tendance comportementale, valeurs cardinales, forces, motivations…
                <br /><br />
                Une fois le test passé, ton ADN professionnel est généré automatiquement et tu accèdes à tes pairs compatibles.
              </p>
              <div style={{ display: "flex", gap: "12px", justifyContent: "center", flexWrap: "wrap", marginTop: "24px" }}>
                <a href="/test-dclic" className="ub-btn-primary" data-testid="dclic-gate-cta">
                  <Sparkles size={14} /> Passer le test D'CLIC PRO
                </a>
                <a href="/dashboard" className="ub-btn-small" data-testid="dclic-gate-back">
                  Retour à RE'ACTIF PRO
                </a>
              </div>
              <p style={{ fontSize: "11px", color: "var(--ub-text-muted)", marginTop: "20px" }}>
                ⏱️ Le test dure environ 12-15 minutes.
              </p>
            </div>
          </div>
        ) : (
          <>
            {tab === "accueil" && <AccueilTab ubProfile={ubProfile} onSync={handleSync} syncing={syncing} isLoggedIn={isLoggedIn} />}
            {tab === "profil" && <ProfilTab
              ubProfile={ubProfile}
              onSync={handleSync}
              syncing={syncing}
              hasDclic={hasDclic}
              token={token}
            />}
            {tab === "groupes" && <GroupesTab exchanges={exchanges} token={token} onPrivateMessage={(p) => setContactPeer({ token_id: p.token_id, name: p.name, pseudo: p.pseudo, title: p.title, status: p.status, compatibility: 100 })} />}
            {tab === "messages" && <MessagesTab token={token} openPeerTokenId={openMessagesPeer} onConsumed={() => setOpenMessagesPeer(null)} />}
            {tab === "rechercher" && <SearchTab token={token} onMessagePeer={(p) => { setOpenMessagesPeer(p.token_id); setTab("messages"); }} />}
            {tab === "discussions" && <DiscussionsTab exchanges={exchanges} onPost={handleNewExchange} />}
        {tab === "mentorat" && <MentoratTab token={token} />}
          </>
        )}
      </div>
      {contactPeer && <ContactPeerModal peer={contactPeer} token={token} onClose={() => setContactPeer(null)} />}
      {matchPeer && <PeerMatchModal peer={matchPeer} token={token} onClose={() => setMatchPeer(null)} onContact={(p) => setContactPeer(p)} />}
    </div>
  );
};

export default UbuntooView;
