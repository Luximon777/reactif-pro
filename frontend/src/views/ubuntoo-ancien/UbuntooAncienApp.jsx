import { useState } from "react";
import "./ubuntoo-ancien.css";
import { Routes, Route, Link, useLocation } from "react-router-dom";
import { Users, User, MessageCircle, Heart, BarChart3, Home, Award, TrendingUp, UserCheck, BookOpen, Share2, Compass, Shield, Sparkles, LogIn, Download, RefreshCw, CheckCircle, MessageSquare, ThumbsUp, Star, Send, Hash, Lock, Bell, Search, Filter, ChevronDown, ChevronUp, Clock, CheckCircle2, HelpCircle, Lightbulb, Reply, Mail, Eye, EyeOff, X, ArrowRight } from "lucide-react";
import axios from "axios";

// Logo Ubuntoo officiel (fond transparent)
const UBUNTOO_LOGO = "https://customer-assets.emergentagent.com/job_keen-meitner-5/artifacts/t3wjk59k_logo_ubuntoo_transparent.png";

// API Backend
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Données fictives (seed)
const initialState = {
  user: {
    name: "Marie Dupont",
    territory: "Grand Est",
    status: "Membre",
    trust: 62,
    badges: ["Pair-aidant (candidat)"],
    softskills: ["Empathie", "Adaptabilité", "Organisation"],
    contributions: 3
  },
  groups: [
    { id: "reconversion", title: "Reconversion", members: 1240, topics: 86, color: "#f97316" },
    { id: "handicap", title: "Handicap & Emploi", members: 640, topics: 41, color: "#06b6d4" },
    { id: "numerique", title: "Métiers du Numérique", members: 980, topics: 63, color: "#8b5cf6" },
    { id: "vsi", title: "Atelier VSI (Valoriser Son Identité pro)", members: 520, topics: 34, color: "#22c55e" }
  ],
  helpRequests: [
    { id: 1, group: "reconversion", title: "Besoin d'aide pour structurer mon projet", author: "Thomas L.", replies: 2 },
    { id: 2, group: "numerique", title: "Préparer un entretien dev junior", author: "Sarah M.", replies: 5 },
    { id: 3, group: "vsi", title: "Comment valoriser une reconversion ?", author: "Pierre D.", replies: 3 }
  ],
  // Données pour l'espace discussion hybride
  discussions: {
    threads: [
      {
        id: "t1",
        type: "question",
        title: "Comment valoriser une expérience de bénévolat sur son CV ?",
        content: "J'ai fait 2 ans de bénévolat dans une association. Comment le mettre en avant lors d'un entretien ?",
        author: { name: "Marie D.", status: "Pair-aidant", avatar: "MD" },
        group: "reconversion",
        createdAt: "Il y a 2 heures",
        views: 45,
        likes: 12,
        replies: [
          { id: "r1", author: { name: "Jean-Pierre M.", status: "Mentor", avatar: "JP" }, content: "Le bénévolat développe des compétences transversales très recherchées : gestion de projet, travail en équipe, adaptabilité. Mettez en avant les résultats concrets !", likes: 8, isAnswer: true, createdAt: "Il y a 1 heure" },
          { id: "r2", author: { name: "Sophie L.", status: "Membre actif", avatar: "SL" }, content: "J'ai vécu la même situation. J'ai créé une rubrique 'Engagement associatif' sur mon CV, ça a très bien fonctionné.", likes: 5, createdAt: "Il y a 45 min" }
        ],
        resolved: true,
        tags: ["CV", "Bénévolat", "Entretien"]
      },
      {
        id: "t2",
        type: "discussion",
        title: "Retour d'expérience : ma reconversion dans l'ESS",
        content: "Après 15 ans dans la finance, j'ai fait le grand saut vers l'économie sociale et solidaire. Je partage mon parcours et mes conseils.",
        author: { name: "Philippe R.", status: "Ambassadeur", avatar: "PR" },
        group: "reconversion",
        createdAt: "Il y a 1 jour",
        views: 234,
        likes: 67,
        replies: [
          { id: "r3", author: { name: "Amina B.", status: "Membre", avatar: "AB" }, content: "Merci pour ce témoignage inspirant ! Comment avez-vous géré la baisse de salaire ?", likes: 12, createdAt: "Il y a 20 heures" },
          { id: "r4", author: { name: "Philippe R.", status: "Ambassadeur", avatar: "PR" }, content: "La question du salaire est importante. J'ai préparé cette transition pendant 2 ans, en réduisant progressivement mes dépenses.", likes: 18, createdAt: "Il y a 18 heures" }
        ],
        resolved: false,
        tags: ["Témoignage", "ESS", "Reconversion"]
      },
      {
        id: "t3",
        type: "aide",
        title: "Recherche mentor secteur numérique",
        content: "Je souhaite me reconvertir dans le développement web. Quelqu'un peut-il m'accompagner dans cette démarche ?",
        author: { name: "Lucas T.", status: "Membre", avatar: "LT" },
        group: "numerique",
        createdAt: "Il y a 3 heures",
        views: 28,
        likes: 4,
        replies: [],
        resolved: false,
        tags: ["Mentorat", "Développement", "Reconversion"]
      }
    ],
    chatRooms: [
      { id: "chat1", name: "Entraide Reconversion", members: 156, lastMessage: "Merci pour vos conseils !", unread: 3 },
      { id: "chat2", name: "Café virtuel ☕", members: 89, lastMessage: "Bonne journée à tous !", unread: 0 },
      { id: "chat3", name: "Atelier CV", members: 45, lastMessage: "RDV demain 14h", unread: 1 }
    ],
    privateMessages: [
      { id: "pm1", with: { name: "Jean-Pierre M.", status: "Mentor", avatar: "JP" }, lastMessage: "D'accord pour un appel mardi ?", unread: 1, time: "10:32" },
      { id: "pm2", with: { name: "Sophie L.", status: "Pair-aidant", avatar: "SL" }, lastMessage: "Merci pour le document !", unread: 0, time: "Hier" }
    ]
  },
  mentors: [
    { id: "m1", name: "Jean-Pierre Martin", focus: "Reconversion", availability: "1h/sem", rating: 4.8 },
    { id: "m2", name: "Amina Benali", focus: "Entretien & confiance", availability: "1h/sem", rating: 4.9 }
  ],
  impact: {
    membersGoalYear3: 50000,
    currentMembers: 12450,
    successLift: 35,
    isolationDrop: 40,
    satisfaction: 85
  }
};

// URL DE'CLIC PRO
const DECLIC_PRO_URL = "https://declicpro-preview.preview.emergentagent.com/";

// Modal de connexion
const LoginModal = ({ isOpen, onClose, onLogin }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");
    
    // Simulation de connexion
    setTimeout(() => {
      if (email && password) {
        onLogin({ email, name: email.split('@')[0] });
        onClose();
      } else {
        setError("Veuillez remplir tous les champs");
      }
      setIsLoading(false);
    }, 1000);
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="login-modal" onClick={e => e.stopPropagation()} data-testid="login-modal">
        <button className="modal-close" onClick={onClose}>
          <X size={24} />
        </button>
        
        <div className="login-header">
          <div className="login-icon">
            <ArrowRight size={32} />
          </div>
          <h2>Connexion Ubuntoo</h2>
          <p>Utilisez vos identifiants RE'ACTIF PRO</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          {error && <div className="login-error">{error}</div>}
          
          <div className="form-group">
            <label>Identifiant ou Email</label>
            <div className="input-wrapper">
              <Mail size={20} />
              <input
                type="email"
                placeholder="votre.email@exemple.com"
                value={email}
                onChange={e => setEmail(e.target.value)}
                data-testid="login-email"
              />
            </div>
          </div>

          <div className="form-group">
            <label>Mot de passe</label>
            <div className="input-wrapper">
              <Lock size={20} />
              <input
                type={showPassword ? "text" : "password"}
                placeholder="••••••••"
                value={password}
                onChange={e => setPassword(e.target.value)}
                data-testid="login-password"
              />
              <button 
                type="button" 
                className="password-toggle"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
          </div>

          <div className="form-options">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={e => setRememberMe(e.target.checked)}
              />
              <span className="checkmark"></span>
              Se souvenir de moi
            </label>
            <a href="#" className="forgot-link">Mot de passe oublié ?</a>
          </div>

          <button 
            type="submit" 
            className="btn-login"
            disabled={isLoading}
            data-testid="login-submit"
          >
            {isLoading ? (
              <RefreshCw size={20} className="spin" />
            ) : (
              <>
                <ArrowRight size={20} />
                Se connecter
              </>
            )}
          </button>
        </form>

        <div className="login-footer">
          <p>Pas encore de compte ?</p>
          <a href="https://declicpro-preview.preview.emergentagent.com" target="_blank" rel="noopener noreferrer">
            Créer un compte RE'ACTIF PRO
          </a>
        </div>
      </div>
    </div>
  );
};

// Navigation
const Navigation = ({ isLoggedIn, user, onLogout }) => {
  const location = useLocation();
  const navItems = [
    { path: "/ubuntoo-ancien", icon: Home, label: "Accueil" },
    { path: "/ubuntoo-ancien/profile", icon: User, label: "Profil" },
    { path: "/ubuntoo-ancien/groups", icon: Users, label: "Groupes" },
    { path: "/ubuntoo-ancien/discussions", icon: MessageSquare, label: "Discussions" },
    { path: "/ubuntoo-ancien/mentoring", icon: Heart, label: "Mentorat" },
    { path: "/ubuntoo-ancien/impact", icon: BarChart3, label: "Impact" }
  ];

  return (
    <header className="nav-header" data-testid="main-navigation">
      <div className="nav-brand">
        <img src={UBUNTOO_LOGO} alt="Ubuntoo" className="brand-logo" />
        <span className="brand-tag">Prototype</span>
      </div>
      <nav className="nav-links">
        {navItems.map(item => (
          <Link
            key={item.path}
            to={item.path}
            className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
            data-testid={`nav-${item.label.toLowerCase()}`}
          >
            <item.icon size={18} />
            <span>{item.label}</span>
          </Link>
        ))}
      </nav>
      <div className="nav-auth">
        {isLoggedIn ? (
          <div className="user-menu">
            <div className="user-avatar-small">{user?.name?.charAt(0).toUpperCase() || 'U'}</div>
            <span className="user-name">{user?.name || 'Utilisateur'}</span>
            <button className="btn-logout" onClick={onLogout}>Déconnexion</button>
          </div>
        ) : (
          <a 
            href="https://career-path-qa.preview.emergentagent.com/" 
            target="_blank" 
            rel="noopener noreferrer"
            className="btn-access" 
            data-testid="access-ubuntoo-btn"
          >
            <LogIn size={18} />
            Accéder à Ubuntoo
          </a>
        )}
      </div>
    </header>
  );
};

// Page Accueil
const HomePage = ({ state, setState }) => {
  const [notice, setNotice] = useState("");
  const [showLogin, setShowLogin] = useState(false);

  const handleJoin = () => {
    setState(prev => ({
      ...prev,
      user: { ...prev.user, status: "Membre actif", badges: ["Membre actif"] }
    }));
    setNotice("Inscription communautaire simulée ✓");
    setTimeout(() => setNotice(""), 3000);
  };

  return (
    <main className="page-content" data-testid="home-page">
      {notice && <div className="notice" data-testid="notice">{notice}</div>}
      
      <section className="hero-section">
        <div className="hero-content">
          <img src={UBUNTOO_LOGO} alt="Ubuntoo" className="hero-logo" />
          <div className="hero-text">
            <h1 className="hero-title">"Je suis parce que nous sommes..."</h1>
            <p className="hero-subtitle">
              <span className="ubuntoo-tooltip" data-testid="ubuntoo-tooltip">
                <strong>Ubuntoo</strong>
                <span className="tooltip-content">
                  <strong>Avez-vous déjà entendu parler de Ubuntu?</strong>
                  <br /><br />
                  Peut être avez-vous lu une histoire troublante à ce sujet :
                  <br /><br />
                  « Un anthropologue a proposé un jeu à des enfants d'une tribu d'Afrique australe. Il a posé un panier plein de fruits sucrés près d'un arbre et a dit aux enfants que le premier arrivé remportait le panier. Quand il leur a dit de courir, ils se sont tous pris par la main et ont couru ensemble, puis se sont assis ensemble profitant de leurs friandises. Quand il leur a demandé pourquoi ils n'avaient pas fait la course, ils ont répondu « UBUNTU », comment peut-on être heureux si tous les autres sont tristes ? »
                  <br /><br />
                  « Ubuntu » dans la culture xhosa signifie : « Je suis parce que nous sommes ». L'ubuntu est une philosophie d'origine bantu qui existe dans plusieurs cultures africaines sous la dénomination du « Bomoto » en lingala, du « Kimuntu » en kikongo, du « Butu » en punu, et de « Ubuntu » en kirundi et kinyarwanda.
                  <br /><br />
                  Les Zoulous d'Afrique du Sud disent "Umuntu ngumuntu ngabantu" qui signifie « Je suis ce que je suis grâce à ce que nous sommes tous ». Cette phrase laconique permet de comprendre la pensée ubuntiste. En effet, cette philosophie trouve sa clé de voûte sur la relation à autrui car nous avons tous un lien qui nous unit et c'est dans ce système d'interaction et d'interconnexion que nous pouvons découvrir qui nous sommes, que nous pouvons découvrir notre propre humanité. Le « je » se comprend uniquement en passant par le « nous ».
                  <br /><br />
                  Jean-Paul Sartre disait : « l'enfer c'est les autres » mais la philosophie ubuntiste dirait plutôt que le paradis réside chez les autres qui représentent la source même de notre force, "l'union fait la force" qui est la devise de la Belgique, illustre bien cette idée. Ubuntu parle d'humanité, d'entraide, de compassion, de partage, et d'union.
                  <br /><br />
                  En 2013, Obama, parlait de cette philosophie lors des obsèques de Mandela, en disant : « (…) Nelson Mandela comprenait les liens qui unissent l'esprit humain. Il y a un mot en Afrique du Sud – Ubuntu – un mot qui incarne le plus grand don de Mandela, celui d'avoir reconnu que nous sommes tous unis par des liens invisibles, que l'humanité repose sur un même fondement, que nous nous réalisons en donnant de nous-mêmes aux autres et en veillant à leurs besoins. (…) Non seulement il incarnait l'Ubuntu, mais il avait aussi appris à des millions d'autres à découvrir cette vérité en eux. »
                  <br /><br />
                  Lors d'une interview il a été demandé à Mandela d'expliquer ce qu'était l'Ubuntu et il répondit ceci : "À l'époque lorsqu'un voyageur passait dans un pays et s'arrêtait dans un village, il n'avait pas besoin de demander de la nourriture ou de l'eau, les gens lui donnaient de la nourriture et s'occupaient de lui. C'est l'un des aspects de l'Ubuntu."
                  <br /><br />
                  Desmond Mpilo Tutu qui est un archevêque anglican sud-africain, lauréat du prix Nobel de la paix en 1984 et auteur d'une théologie ubuntiste de la réconciliation affirmait : « Quelqu'un d'ubuntu est ouvert et disponible pour les autres, dévoué aux autres, ne se sent pas menacé parce que les autres sont capables et bons car il ou elle possède sa propre estime de soi — qui vient de la connaissance qu'il ou elle a d'appartenir à quelque chose de plus grand. »
                  <br /><br />
                  <em>Nous sommes ensemble comme le dirait certains parents africains. « Il ne faut pas s'en faire pour les épreuves futures car on est ensemble ».</em>
                </span>
              </span>
              {" "}est le réseau social solidaire d'ALT&ACT, inspiré de la philosophie Ubuntu.
              C'est un espace où chaque membre contribue à l'enrichissement collectif 
              tout en bénéficiant du soutien de la communauté.
            </p>
          </div>
        </div>
      </section>

      {/* Valeurs fondatrices */}
      <section className="values-section">
        <h2>Nos valeurs fondatrices</h2>
        <div className="values-grid">
          <div className="value-card orange">
            <Users size={32} />
            <h3>Ubuntu</h3>
            <p>"Je suis parce que nous sommes" - La force du collectif</p>
          </div>
          <div className="value-card cyan">
            <Heart size={32} />
            <h3>Entraide</h3>
            <p>Chacun apporte et reçoit dans un esprit de réciprocité</p>
          </div>
          <div className="value-card purple">
            <TrendingUp size={32} />
            <h3>Croissance</h3>
            <p>Grandir ensemble, personnellement et professionnellement</p>
          </div>
        </div>
      </section>

      {/* KPIs */}
      <section className="kpi-grid">
        <div className="kpi-card orange" data-testid="kpi-success">
          <TrendingUp size={32} />
          <div className="kpi-value">+35%</div>
          <div className="kpi-label">de réussite vs parcours isolés</div>
        </div>
        <div className="kpi-card cyan" data-testid="kpi-isolation">
          <Users size={32} />
          <div className="kpi-value">-40%</div>
          <div className="kpi-label">de sentiment d'isolement</div>
        </div>
        <div className="kpi-card purple" data-testid="kpi-satisfaction">
          <Heart size={32} />
          <div className="kpi-value">85%</div>
          <div className="kpi-label">de satisfaction communauté</div>
        </div>
      </section>

      {/* Ce que vous offre Ubuntoo */}
      <section className="offers-section">
        <h2>Ce que vous offre Ubuntoo</h2>
        <div className="offers-grid">
          <div className="offer-card">
            <BookOpen size={28} />
            <h3>Communauté apprenante</h3>
            <p>Rejoignez une communauté de professionnels engagés dans le développement mutuel et l'entraide.</p>
          </div>
          <div className="offer-card">
            <Award size={28} />
            <h3>Badges d'expérience</h3>
            <p>Valorisez vos compétences et votre parcours grâce à un système de reconnaissance par badges.</p>
          </div>
          <div className="offer-card">
            <Share2 size={28} />
            <h3>Échanges et partage</h3>
            <p>Partagez vos expériences, posez vos questions et bénéficiez de l'intelligence collective.</p>
          </div>
          <div className="offer-card">
            <Compass size={28} />
            <h3>Accompagnement personnalisé</h3>
            <p>Accédez à des ressources et un accompagnement adapté à votre parcours professionnel.</p>
          </div>
          <div className="offer-card">
            <Sparkles size={28} />
            <h3>Ressources et formations</h3>
            <p>Développez vos compétences grâce à des contenus exclusifs et des formations ciblées.</p>
          </div>
          <div className="offer-card">
            <Shield size={28} />
            <h3>Réseau solidaire</h3>
            <p>Connectez-vous avec des acteurs engagés pour une insertion professionnelle inclusive.</p>
          </div>
        </div>
      </section>

      {/* Call to action */}
      <section className="cta-section">
        <div className="cta-card">
          <h2>Rejoignez la communauté Ubuntoo</h2>
          <p>Connectez-vous avec vos identifiants RE'ACTIF PRO pour accéder à l'espace Ubuntoo et commencer votre aventure au sein de notre communauté apprenante.</p>
          <div className="cta-buttons">
            <a href="https://declicpro-preview.preview.emergentagent.com/" target="_blank" rel="noopener noreferrer" className="btn-primary" data-testid="join-btn">
              <LogIn size={20} />
              Accéder à DE'CLIC PRO
            </a>
            <a href="https://www.alt-act.eu" target="_blank" rel="noopener noreferrer" className="btn-secondary">
              En savoir plus sur ALT&ACT
            </a>
          </div>
        </div>
      </section>

      {/* Parcours de transformation */}
      <section className="transformation-section">
        <h2>Votre parcours de transformation</h2>
        <div className="transformation-path">
          <div className="transform-step orange">
            <div className="step-number">1</div>
            <h4>Accompagné</h4>
            <p>Vous recevez un soutien personnalisé</p>
          </div>
          <div className="transform-arrow">→</div>
          <div className="transform-step green">
            <div className="step-number">2</div>
            <h4>Pair-aidant</h4>
            <p>Vous partagez votre expérience</p>
          </div>
          <div className="transform-arrow">→</div>
          <div className="transform-step cyan">
            <div className="step-number">3</div>
            <h4>Mentor</h4>
            <p>Vous structurez votre soutien</p>
          </div>
          <div className="transform-arrow">→</div>
          <div className="transform-step purple">
            <div className="step-number">4</div>
            <h4>Ambassadeur</h4>
            <p>Vous représentez l'insertion positive</p>
          </div>
        </div>
      </section>
    </main>
  );
};

// Page Profil
const ProfilePage = ({ state, setState }) => {
  const { user } = state;
  const statuses = ["Membre", "Membre actif", "Pair-aidant", "Mentor", "Ambassadeur"];
  const currentIndex = statuses.indexOf(user.status);
  const [importing, setImporting] = useState(false);
  const [importSuccess, setImportSuccess] = useState(false);
  const [importError, setImportError] = useState("");

  const upgradeStatus = () => {
    if (currentIndex < statuses.length - 1) {
      const newStatus = statuses[currentIndex + 1];
      setState(prev => ({
        ...prev,
        user: {
          ...prev.user,
          status: newStatus,
          badges: [...prev.user.badges, newStatus],
          trust: Math.min(100, prev.user.trust + 15)
        }
      }));
    }
  };

  const importFromReactifPro = async () => {
    setImporting(true);
    setImportError("");
    setImportSuccess(false);
    
    try {
      const response = await axios.post(`${API}/social/legacy/import-reactif-pro`, {
        user_id: "demo-user-001",
        email: "demo@ubuntoo.eu"
      });
      
      if (response.data.status === "success") {
        const profile = response.data.profile;
        
        // Update local state with imported data
        setState(prev => ({
          ...prev,
          user: {
            ...prev.user,
            name: profile.name || prev.user.name,
            territory: profile.territory || prev.user.territory,
            status: profile.status || "Membre actif",
            trust: profile.trust_score || prev.user.trust,
            badges: profile.badges || [...prev.user.badges, "Profil RE'ACTIF PRO"],
            softskills: profile.soft_skills ? profile.soft_skills.map(s => s.name) : prev.user.softskills,
            softskillsDetails: profile.soft_skills || [],
            values: profile.values || [],
            professionalSector: profile.professional_sector || "",
            targetJobs: profile.target_jobs || [],
            potentialScore: profile.potential_score || 0,
            adaptationPotential: profile.adaptation_potential || 0,
            trajectory: profile.trajectory || "",
            contributions: prev.user.contributions,
            reactifProSynced: true
          }
        }));
        
        setImportSuccess(true);
        setTimeout(() => setImportSuccess(false), 5000);
      }
    } catch (error) {
      console.error("Import error:", error);
      setImportError("Erreur lors de l'import. Réessayez plus tard.");
      setTimeout(() => setImportError(""), 5000);
    } finally {
      setImporting(false);
    }
  };

  return (
    <main className="page-content" data-testid="profile-page">
      <h1 className="page-title">Profil Contributif</h1>
      
      {/* Import RE'ACTIF PRO Banner */}
      <div className="import-banner" data-testid="import-banner">
        <div className="import-banner-content">
          <div className="import-banner-text">
            <h3>Connecter votre profil RE'ACTIF PRO</h3>
            <p>Importez automatiquement vos soft skills, valeurs et données de la carte d'identité professionnelle.</p>
          </div>
          <button 
            className={`btn-import ${importing ? 'loading' : ''} ${importSuccess ? 'success' : ''}`}
            onClick={importFromReactifPro}
            disabled={importing}
            data-testid="import-reactif-btn"
          >
            {importing ? (
              <>
                <RefreshCw size={20} className="spin" />
                Import en cours...
              </>
            ) : importSuccess ? (
              <>
                <CheckCircle size={20} />
                Profil importé !
              </>
            ) : (
              <>
                <Download size={20} />
                Importer mon profil RE'ACTIF PRO
              </>
            )}
          </button>
        </div>
        {importError && <div className="import-error">{importError}</div>}
        {importSuccess && (
          <div className="import-success">
            Données importées avec succès depuis RE'ACTIF PRO !
          </div>
        )}
      </div>
      
      <div className="profile-grid">
        <div className="profile-card main-profile">
          <div className="avatar-section">
            <div className="avatar">
              <User size={48} />
            </div>
            <div className="user-info">
              <h2>{user.name}</h2>
              <span className="territory">{user.territory}</span>
              {user.reactifProSynced && (
                <span className="synced-badge">
                  <CheckCircle size={14} />
                  Synchronisé RE'ACTIF PRO
                </span>
              )}
            </div>
          </div>
          
          <div className="status-section">
            <div className="status-badge" data-testid="user-status">
              <Award size={18} />
              {user.status}
            </div>
            <div className="trust-meter">
              <span>Indice de confiance</span>
              <div className="trust-bar">
                <div className="trust-fill" style={{ width: `${user.trust}%` }}></div>
              </div>
              <span className="trust-value">{user.trust}%</span>
            </div>
          </div>

          <button className="btn-secondary" onClick={upgradeStatus} data-testid="upgrade-btn">
            Simuler progression de statut
          </button>
        </div>

        <div className="profile-card">
          <h3>Soft Skills Certifiées</h3>
          <div className="skills-list">
            {user.softskillsDetails && user.softskillsDetails.length > 0 ? (
              user.softskillsDetails.map((skill, i) => (
                <div key={i} className="skill-badge-detailed">
                  <span className="skill-name">{skill.name}</span>
                  <div className="skill-bar">
                    <div className="skill-fill" style={{ width: `${skill.level}%` }}></div>
                  </div>
                  <span className="skill-level">{skill.level}%</span>
                  {skill.certified && <CheckCircle size={14} className="certified-icon" />}
                </div>
              ))
            ) : (
              user.softskills.map((skill, i) => (
                <span key={i} className="skill-badge">{skill}</span>
              ))
            )}
          </div>
        </div>

        <div className="profile-card">
          <h3>Badges d'expérience</h3>
          <div className="badges-list">
            {user.badges.map((badge, i) => (
              <span key={i} className="badge-item">
                <Award size={16} />
                {badge}
              </span>
            ))}
          </div>
        </div>

        <div className="profile-card stats-card">
          <h3>Contributions</h3>
          <div className="stat-value">{user.contributions}</div>
          <p>aides apportées à la communauté</p>
        </div>

        {/* New cards for RE'ACTIF PRO data */}
        {user.values && user.values.length > 0 && (
          <div className="profile-card">
            <h3>Valeurs dominantes</h3>
            <div className="values-list">
              {user.values.map((value, i) => (
                <span key={i} className="value-badge">{value}</span>
              ))}
            </div>
          </div>
        )}

        {user.professionalSector && (
          <div className="profile-card">
            <h3>Secteur professionnel</h3>
            <p className="sector-text">{user.professionalSector}</p>
            {user.trajectory && (
              <p className="trajectory-text">{user.trajectory}</p>
            )}
          </div>
        )}

        {user.targetJobs && user.targetJobs.length > 0 && (
          <div className="profile-card">
            <h3>Métiers visés</h3>
            <div className="jobs-list">
              {user.targetJobs.map((job, i) => (
                <span key={i} className="job-badge">{job}</span>
              ))}
            </div>
          </div>
        )}

        {user.potentialScore > 0 && (
          <div className="profile-card potential-card">
            <h3>Score de potentiel</h3>
            <div className="potential-scores">
              <div className="potential-item">
                <span className="potential-label">Potentiel global</span>
                <div className="potential-bar">
                  <div className="potential-fill" style={{ width: `${user.potentialScore}%` }}></div>
                </div>
                <span className="potential-value">{user.potentialScore}%</span>
              </div>
              {user.adaptationPotential > 0 && (
                <div className="potential-item">
                  <span className="potential-label">Capacité d'adaptation</span>
                  <div className="potential-bar adaptation">
                    <div className="potential-fill" style={{ width: `${user.adaptationPotential}%` }}></div>
                  </div>
                  <span className="potential-value">{user.adaptationPotential}%</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      <div className="progression-section">
        <h3>Parcours de Progression</h3>
        <div className="progression-timeline">
          {statuses.map((status, i) => (
            <div key={status} className={`timeline-step ${i <= currentIndex ? 'completed' : ''}`}>
              <div className="step-dot"></div>
              <span>{status}</span>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
};

// Page Groupes
const GroupsPage = ({ state, setState }) => {
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [newRequest, setNewRequest] = useState("");

  const addHelpRequest = () => {
    if (newRequest && selectedGroup) {
      setState(prev => ({
        ...prev,
        helpRequests: [
          ...prev.helpRequests,
          { id: Date.now(), group: selectedGroup, title: newRequest, author: prev.user.name, replies: 0 }
        ],
        user: { ...prev.user, contributions: prev.user.contributions + 1 }
      }));
      setNewRequest("");
    }
  };

  return (
    <main className="page-content" data-testid="groups-page">
      <h1 className="page-title">Groupes Thématiques</h1>
      <p className="page-intro">Rejoignez une communauté de professionnels engagés dans le développement mutuel et l'entraide.</p>
      
      <div className="groups-grid">
        {state.groups.map(group => (
          <div
            key={group.id}
            className={`group-card ${selectedGroup === group.id ? 'selected' : ''}`}
            style={{ borderColor: group.color }}
            onClick={() => setSelectedGroup(group.id)}
            data-testid={`group-${group.id}`}
          >
            <div className="group-icon" style={{ backgroundColor: group.color }}>
              <Users size={24} />
            </div>
            <h3>{group.title}</h3>
            <div className="group-stats">
              <span>{group.members} membres</span>
              <span>{group.topics} sujets</span>
            </div>
            <button className="btn-small">Rejoindre</button>
          </div>
        ))}
      </div>

      {selectedGroup && (
        <div className="group-detail">
          <h2>Échanges et partage - {state.groups.find(g => g.id === selectedGroup)?.title}</h2>
          
          <div className="help-requests">
            {state.helpRequests.filter(r => r.group === selectedGroup).map(request => (
              <div key={request.id} className="request-card">
                <MessageCircle size={20} />
                <div className="request-content">
                  <h4>{request.title}</h4>
                  <span>par {request.author} • {request.replies} réponses</span>
                </div>
                <button className="btn-small">Répondre</button>
              </div>
            ))}
          </div>

          <div className="new-request">
            <input
              type="text"
              placeholder="Posez votre question à la communauté..."
              value={newRequest}
              onChange={e => setNewRequest(e.target.value)}
              data-testid="new-request-input"
            />
            <button className="btn-primary" onClick={addHelpRequest} data-testid="post-request-btn">
              Publier
            </button>
          </div>
        </div>
      )}

      <div className="group-cta">
        <p>Pour des discussions plus approfondies, visitez l'</p>
        <Link to="/ubuntoo-ancien/discussions" className="btn-primary">
          <MessageSquare size={20} />
          Espace Discussions
        </Link>
      </div>
    </main>
  );
};

// Page Discussions Hybride
const DiscussionsPage = ({ state, setState }) => {
  const [activeTab, setActiveTab] = useState("forum");
  const [selectedThread, setSelectedThread] = useState(null);
  const [newMessage, setNewMessage] = useState("");
  const [newThreadTitle, setNewThreadTitle] = useState("");
  const [newThreadContent, setNewThreadContent] = useState("");
  const [showNewThread, setShowNewThread] = useState(false);
  const [filterType, setFilterType] = useState("all");
  const [selectedChat, setSelectedChat] = useState(null);
  const [selectedPM, setSelectedPM] = useState(null);
  const [chatMessage, setChatMessage] = useState("");

  const { discussions } = state;

  const filteredThreads = discussions.threads.filter(t => 
    filterType === "all" || t.type === filterType
  );

  const handleLikeThread = (threadId) => {
    setState(prev => ({
      ...prev,
      discussions: {
        ...prev.discussions,
        threads: prev.discussions.threads.map(t =>
          t.id === threadId ? { ...t, likes: t.likes + 1 } : t
        )
      }
    }));
  };

  const handleLikeReply = (threadId, replyId) => {
    setState(prev => ({
      ...prev,
      discussions: {
        ...prev.discussions,
        threads: prev.discussions.threads.map(t =>
          t.id === threadId ? {
            ...t,
            replies: t.replies.map(r =>
              r.id === replyId ? { ...r, likes: r.likes + 1 } : r
            )
          } : t
        )
      }
    }));
  };

  const addReply = (threadId) => {
    if (!newMessage.trim()) return;
    
    setState(prev => ({
      ...prev,
      discussions: {
        ...prev.discussions,
        threads: prev.discussions.threads.map(t =>
          t.id === threadId ? {
            ...t,
            replies: [...t.replies, {
              id: `r${Date.now()}`,
              author: { name: prev.user.name, status: prev.user.status, avatar: prev.user.name.split(' ').map(n => n[0]).join('') },
              content: newMessage,
              likes: 0,
              createdAt: "À l'instant"
            }]
          } : t
        )
      },
      user: { ...prev.user, contributions: prev.user.contributions + 1 }
    }));
    setNewMessage("");
  };

  const createThread = () => {
    if (!newThreadTitle.trim() || !newThreadContent.trim()) return;

    const newThread = {
      id: `t${Date.now()}`,
      type: "question",
      title: newThreadTitle,
      content: newThreadContent,
      author: { name: state.user.name, status: state.user.status, avatar: state.user.name.split(' ').map(n => n[0]).join('') },
      group: "reconversion",
      createdAt: "À l'instant",
      views: 0,
      likes: 0,
      replies: [],
      resolved: false,
      tags: []
    };

    setState(prev => ({
      ...prev,
      discussions: {
        ...prev.discussions,
        threads: [newThread, ...prev.discussions.threads]
      },
      user: { ...prev.user, contributions: prev.user.contributions + 1 }
    }));

    setNewThreadTitle("");
    setNewThreadContent("");
    setShowNewThread(false);
  };

  const getTypeIcon = (type) => {
    switch(type) {
      case "question": return <HelpCircle size={18} />;
      case "discussion": return <MessageSquare size={18} />;
      case "aide": return <Heart size={18} />;
      default: return <Lightbulb size={18} />;
    }
  };

  const getTypeLabel = (type) => {
    switch(type) {
      case "question": return "Question";
      case "discussion": return "Discussion";
      case "aide": return "Demande d'aide";
      default: return "Sujet";
    }
  };

  return (
    <main className="page-content discussions-page" data-testid="discussions-page">
      <div className="discussions-header">
        <h1 className="page-title">Espace Discussions</h1>
        <p className="page-intro">Forum d'entraide, questions-réponses et messagerie de la communauté Ubuntoo</p>
      </div>

      {/* Tabs */}
      <div className="discussions-tabs">
        <button 
          className={`tab-btn ${activeTab === 'forum' ? 'active' : ''}`}
          onClick={() => setActiveTab('forum')}
        >
          <MessageSquare size={18} />
          Forum & Q/A
        </button>
        <button 
          className={`tab-btn ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => setActiveTab('chat')}
        >
          <Hash size={18} />
          Salons
          {discussions.chatRooms.reduce((acc, r) => acc + r.unread, 0) > 0 && (
            <span className="unread-badge">{discussions.chatRooms.reduce((acc, r) => acc + r.unread, 0)}</span>
          )}
        </button>
        <button 
          className={`tab-btn ${activeTab === 'messages' ? 'active' : ''}`}
          onClick={() => setActiveTab('messages')}
        >
          <Lock size={18} />
          Messages privés
          {discussions.privateMessages.reduce((acc, m) => acc + m.unread, 0) > 0 && (
            <span className="unread-badge">{discussions.privateMessages.reduce((acc, m) => acc + m.unread, 0)}</span>
          )}
        </button>
      </div>

      {/* Forum Tab */}
      {activeTab === 'forum' && (
        <div className="forum-container">
          {/* Toolbar */}
          <div className="forum-toolbar">
            <div className="filter-buttons">
              <button 
                className={`filter-btn ${filterType === 'all' ? 'active' : ''}`}
                onClick={() => setFilterType('all')}
              >
                Tous
              </button>
              <button 
                className={`filter-btn ${filterType === 'question' ? 'active' : ''}`}
                onClick={() => setFilterType('question')}
              >
                <HelpCircle size={14} /> Questions
              </button>
              <button 
                className={`filter-btn ${filterType === 'discussion' ? 'active' : ''}`}
                onClick={() => setFilterType('discussion')}
              >
                <MessageSquare size={14} /> Discussions
              </button>
              <button 
                className={`filter-btn ${filterType === 'aide' ? 'active' : ''}`}
                onClick={() => setFilterType('aide')}
              >
                <Heart size={14} /> Entraide
              </button>
            </div>
            <button className="btn-primary" onClick={() => setShowNewThread(true)}>
              + Nouveau sujet
            </button>
          </div>

          {/* New Thread Form */}
          {showNewThread && (
            <div className="new-thread-form">
              <h3>Créer un nouveau sujet</h3>
              <input
                type="text"
                placeholder="Titre de votre sujet..."
                value={newThreadTitle}
                onChange={e => setNewThreadTitle(e.target.value)}
                className="thread-title-input"
              />
              <textarea
                placeholder="Décrivez votre question ou sujet de discussion..."
                value={newThreadContent}
                onChange={e => setNewThreadContent(e.target.value)}
                className="thread-content-input"
                rows={4}
              />
              <div className="form-actions">
                <button className="btn-secondary" onClick={() => setShowNewThread(false)}>Annuler</button>
                <button className="btn-primary" onClick={createThread}>Publier</button>
              </div>
            </div>
          )}

          {/* Thread List or Detail */}
          {!selectedThread ? (
            <div className="threads-list">
              {filteredThreads.map(thread => (
                <div 
                  key={thread.id} 
                  className={`thread-card ${thread.resolved ? 'resolved' : ''}`}
                  onClick={() => setSelectedThread(thread)}
                >
                  <div className="thread-type-badge" data-type={thread.type}>
                    {getTypeIcon(thread.type)}
                    {getTypeLabel(thread.type)}
                  </div>
                  
                  <div className="thread-main">
                    <h3 className="thread-title">
                      {thread.resolved && <CheckCircle2 size={18} className="resolved-icon" />}
                      {thread.title}
                    </h3>
                    <p className="thread-excerpt">{thread.content.substring(0, 150)}...</p>
                    
                    <div className="thread-tags">
                      {thread.tags.map(tag => (
                        <span key={tag} className="tag">{tag}</span>
                      ))}
                    </div>
                  </div>

                  <div className="thread-meta">
                    <div className="thread-author">
                      <div className="author-avatar">{thread.author.avatar}</div>
                      <div className="author-info">
                        <span className="author-name">{thread.author.name}</span>
                        <span className="author-status">{thread.author.status}</span>
                      </div>
                    </div>
                    <div className="thread-stats">
                      <span><Clock size={14} /> {thread.createdAt}</span>
                      <span><MessageCircle size={14} /> {thread.replies.length}</span>
                      <span><ThumbsUp size={14} /> {thread.likes}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="thread-detail">
              <button className="back-btn" onClick={() => setSelectedThread(null)}>
                ← Retour aux discussions
              </button>

              <div className="thread-full">
                <div className="thread-header">
                  <div className="thread-type-badge" data-type={selectedThread.type}>
                    {getTypeIcon(selectedThread.type)}
                    {getTypeLabel(selectedThread.type)}
                  </div>
                  {selectedThread.resolved && (
                    <span className="resolved-badge">
                      <CheckCircle2 size={16} /> Résolu
                    </span>
                  )}
                </div>

                <h2>{selectedThread.title}</h2>
                
                <div className="thread-author-full">
                  <div className="author-avatar large">{selectedThread.author.avatar}</div>
                  <div className="author-info">
                    <span className="author-name">{selectedThread.author.name}</span>
                    <span className="author-status">{selectedThread.author.status}</span>
                    <span className="post-time">{selectedThread.createdAt}</span>
                  </div>
                </div>

                <div className="thread-content-full">
                  {selectedThread.content}
                </div>

                <div className="thread-actions">
                  <button className="action-btn" onClick={() => handleLikeThread(selectedThread.id)}>
                    <ThumbsUp size={18} /> {selectedThread.likes}
                  </button>
                  <span className="views"><Clock size={14} /> {selectedThread.views} vues</span>
                </div>

                <div className="thread-tags">
                  {selectedThread.tags.map(tag => (
                    <span key={tag} className="tag">{tag}</span>
                  ))}
                </div>
              </div>

              {/* Replies */}
              <div className="replies-section">
                <h3>{selectedThread.replies.length} Réponse{selectedThread.replies.length > 1 ? 's' : ''}</h3>
                
                {selectedThread.replies.map(reply => (
                  <div key={reply.id} className={`reply-card ${reply.isAnswer ? 'is-answer' : ''}`}>
                    {reply.isAnswer && (
                      <div className="answer-badge">
                        <CheckCircle2 size={14} /> Meilleure réponse
                      </div>
                    )}
                    <div className="reply-author">
                      <div className="author-avatar">{reply.author.avatar}</div>
                      <div className="author-info">
                        <span className="author-name">{reply.author.name}</span>
                        <span className="author-status">{reply.author.status}</span>
                      </div>
                      <span className="reply-time">{reply.createdAt}</span>
                    </div>
                    <div className="reply-content">
                      {reply.content}
                    </div>
                    <div className="reply-actions">
                      <button className="action-btn" onClick={() => handleLikeReply(selectedThread.id, reply.id)}>
                        <ThumbsUp size={16} /> {reply.likes}
                      </button>
                      <button className="action-btn">
                        <Reply size={16} /> Répondre
                      </button>
                    </div>
                  </div>
                ))}

                {/* New Reply Form */}
                <div className="new-reply-form">
                  <div className="reply-input-container">
                    <textarea
                      placeholder="Votre réponse..."
                      value={newMessage}
                      onChange={e => setNewMessage(e.target.value)}
                      rows={3}
                    />
                    <button className="btn-primary" onClick={() => addReply(selectedThread.id)}>
                      <Send size={18} /> Répondre
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Chat Rooms Tab */}
      {activeTab === 'chat' && (
        <div className="chat-container">
          <div className="chat-sidebar">
            <h3>Salons de discussion</h3>
            {discussions.chatRooms.map(room => (
              <div 
                key={room.id}
                className={`chat-room-item ${selectedChat === room.id ? 'active' : ''}`}
                onClick={() => setSelectedChat(room.id)}
              >
                <div className="room-icon">
                  <Hash size={18} />
                </div>
                <div className="room-info">
                  <span className="room-name">{room.name}</span>
                  <span className="room-preview">{room.lastMessage}</span>
                </div>
                <div className="room-meta">
                  <span className="room-members">{room.members}</span>
                  {room.unread > 0 && <span className="unread-count">{room.unread}</span>}
                </div>
              </div>
            ))}
          </div>
          
          <div className="chat-main">
            {selectedChat ? (
              <>
                <div className="chat-header">
                  <Hash size={20} />
                  <span>{discussions.chatRooms.find(r => r.id === selectedChat)?.name}</span>
                  <span className="member-count">{discussions.chatRooms.find(r => r.id === selectedChat)?.members} membres</span>
                </div>
                <div className="chat-messages">
                  <div className="chat-message other">
                    <div className="msg-avatar">SL</div>
                    <div className="msg-content">
                      <span className="msg-author">Sophie L.</span>
                      <p>Bonjour à tous ! Quelqu'un a des conseils pour un premier entretien en ESS ?</p>
                      <span className="msg-time">10:15</span>
                    </div>
                  </div>
                  <div className="chat-message other">
                    <div className="msg-avatar">JP</div>
                    <div className="msg-content">
                      <span className="msg-author">Jean-Pierre M.</span>
                      <p>Oui ! Mettez en avant vos valeurs et votre motivation. Le secteur ESS recherche des personnes engagées.</p>
                      <span className="msg-time">10:18</span>
                    </div>
                  </div>
                  <div className="chat-message self">
                    <div className="msg-content">
                      <p>Merci pour vos conseils ! 🙏</p>
                      <span className="msg-time">10:20</span>
                    </div>
                  </div>
                </div>
                <div className="chat-input">
                  <input 
                    type="text" 
                    placeholder="Écrivez votre message..."
                    value={chatMessage}
                    onChange={e => setChatMessage(e.target.value)}
                  />
                  <button className="send-btn">
                    <Send size={20} />
                  </button>
                </div>
              </>
            ) : (
              <div className="chat-placeholder">
                <MessageSquare size={48} />
                <p>Sélectionnez un salon pour commencer à discuter</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Private Messages Tab */}
      {activeTab === 'messages' && (
        <div className="chat-container">
          <div className="chat-sidebar">
            <h3>Messages privés</h3>
            {discussions.privateMessages.map(pm => (
              <div 
                key={pm.id}
                className={`chat-room-item ${selectedPM === pm.id ? 'active' : ''}`}
                onClick={() => setSelectedPM(pm.id)}
              >
                <div className="pm-avatar">{pm.with.avatar}</div>
                <div className="room-info">
                  <span className="room-name">{pm.with.name}</span>
                  <span className="room-preview">{pm.lastMessage}</span>
                </div>
                <div className="room-meta">
                  <span className="pm-time">{pm.time}</span>
                  {pm.unread > 0 && <span className="unread-count">{pm.unread}</span>}
                </div>
              </div>
            ))}
          </div>
          
          <div className="chat-main">
            {selectedPM ? (
              <>
                <div className="chat-header">
                  <div className="pm-avatar">{discussions.privateMessages.find(m => m.id === selectedPM)?.with.avatar}</div>
                  <span>{discussions.privateMessages.find(m => m.id === selectedPM)?.with.name}</span>
                  <span className="pm-status">{discussions.privateMessages.find(m => m.id === selectedPM)?.with.status}</span>
                </div>
                <div className="chat-messages">
                  <div className="chat-message other">
                    <div className="msg-avatar">{discussions.privateMessages.find(m => m.id === selectedPM)?.with.avatar}</div>
                    <div className="msg-content">
                      <p>Bonjour ! J'ai vu votre profil et je serais ravi de vous accompagner dans votre reconversion.</p>
                      <span className="msg-time">Hier 14:30</span>
                    </div>
                  </div>
                  <div className="chat-message self">
                    <div className="msg-content">
                      <p>Bonjour ! Merci beaucoup, c'est très gentil. Quelles sont vos disponibilités ?</p>
                      <span className="msg-time">Hier 15:45</span>
                    </div>
                  </div>
                  <div className="chat-message other">
                    <div className="msg-avatar">{discussions.privateMessages.find(m => m.id === selectedPM)?.with.avatar}</div>
                    <div className="msg-content">
                      <p>D'accord pour un appel mardi ?</p>
                      <span className="msg-time">10:32</span>
                    </div>
                  </div>
                </div>
                <div className="chat-input">
                  <input type="text" placeholder="Écrivez votre message..." />
                  <button className="send-btn">
                    <Send size={20} />
                  </button>
                </div>
              </>
            ) : (
              <div className="chat-placeholder">
                <Lock size={48} />
                <p>Sélectionnez une conversation</p>
              </div>
            )}
          </div>
        </div>
      )}
    </main>
  );
};

// Page Mentorat
const MentoringPage = ({ state, setState }) => {
  const [activeMentor, setActiveMentor] = useState(null);

  const startMentoring = (mentor) => {
    setActiveMentor(mentor);
  };

  return (
    <main className="page-content" data-testid="mentoring-page">
      <h1 className="page-title">Mentorat Pair-à-Pair</h1>
      
      <div className="mentoring-intro">
        <p>Le mentorat Ubuntoo connecte les membres expérimentés avec ceux qui débutent leur parcours. 
        Chacun apporte et reçoit dans un esprit de réciprocité.</p>
      </div>

      {!activeMentor ? (
        <>
          <h2>Mentors Disponibles</h2>
          <div className="mentors-grid">
            {state.mentors.map(mentor => (
              <div key={mentor.id} className="mentor-card" data-testid={`mentor-${mentor.id}`}>
                <div className="mentor-avatar">
                  <UserCheck size={32} />
                </div>
                <h3>{mentor.name}</h3>
                <div className="mentor-focus">{mentor.focus}</div>
                <div className="mentor-meta">
                  <span>Disponibilité: {mentor.availability}</span>
                  <span className="rating">★ {mentor.rating}</span>
                </div>
                <button className="btn-primary" onClick={() => startMentoring(mentor)}>
                  Demander un mentorat
                </button>
              </div>
            ))}
          </div>
        </>
      ) : (
        <div className="active-mentoring">
          <div className="mentoring-card">
            <div className="mentoring-header">
              <UserCheck size={40} />
              <div>
                <h2>Mentorat actif avec {activeMentor.name}</h2>
                <span>Focus: {activeMentor.focus}</span>
              </div>
            </div>
            
            <div className="mentoring-timeline">
              <h3>Programme 3 mois</h3>
              <div className="timeline-steps">
                <div className="step active">
                  <div className="step-number">1</div>
                  <span>Mois 1: Diagnostic & Objectifs</span>
                </div>
                <div className="step">
                  <div className="step-number">2</div>
                  <span>Mois 2: Accompagnement personnalisé</span>
                </div>
                <div className="step">
                  <div className="step-number">3</div>
                  <span>Mois 3: Autonomie & Feedback</span>
                </div>
              </div>
            </div>

            <button className="btn-secondary" onClick={() => setActiveMentor(null)}>
              Terminer le mentorat (simulation)
            </button>
          </div>
        </div>
      )}

      <div className="mentoring-levels">
        <h2>Niveaux de progression</h2>
        <div className="levels-grid">
          <div className="level-card">
            <span className="level-number">1</span>
            <h4>Membre</h4>
          </div>
          <div className="level-card">
            <span className="level-number">2</span>
            <h4>Pair-aidant</h4>
          </div>
          <div className="level-card highlight">
            <span className="level-number">3</span>
            <h4>Mentor certifié</h4>
          </div>
          <div className="level-card">
            <span className="level-number">4</span>
            <h4>Ambassadeur</h4>
          </div>
        </div>
      </div>
    </main>
  );
};

// Page Impact
const ImpactPage = ({ state }) => {
  const { impact } = state;
  const progress = Math.round((impact.currentMembers / impact.membersGoalYear3) * 100);

  return (
    <main className="page-content" data-testid="impact-page">
      <h1 className="page-title">Tableau de Bord Impact</h1>
      
      <div className="impact-grid">
        <div className="impact-card large">
          <h3>Objectif An 3 : 50 000 membres</h3>
          <div className="progress-container">
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${progress}%` }}></div>
            </div>
            <div className="progress-stats">
              <span>{impact.currentMembers.toLocaleString()} membres actuels</span>
              <span>{progress}%</span>
            </div>
          </div>
        </div>

        <div className="impact-card orange">
          <TrendingUp size={32} />
          <div className="impact-value">+{impact.successLift}%</div>
          <div className="impact-label">Réussite vs parcours isolés</div>
        </div>

        <div className="impact-card cyan">
          <Users size={32} />
          <div className="impact-value">-{impact.isolationDrop}%</div>
          <div className="impact-label">Sentiment d'isolement</div>
        </div>

        <div className="impact-card purple">
          <Heart size={32} />
          <div className="impact-value">{impact.satisfaction}%</div>
          <div className="impact-label">Satisfaction communauté</div>
        </div>
      </div>

      <div className="impact-details">
        <h2>Indicateurs complémentaires</h2>
        <div className="metrics-grid">
          <div className="metric-card">
            <span className="metric-label">Mentorats actifs</span>
            <span className="metric-value">342</span>
          </div>
          <div className="metric-card">
            <span className="metric-label">Taux d'engagement mensuel</span>
            <span className="metric-value">67%</span>
          </div>
          <div className="metric-card">
            <span className="metric-label">Insertion durable (6 mois)</span>
            <span className="metric-value">72%</span>
          </div>
          <div className="metric-card">
            <span className="metric-label">Événements territoriaux</span>
            <span className="metric-value">24/an</span>
          </div>
        </div>
      </div>

      <div className="impact-vision">
        <h2>Vision RE'ACTIF PRO + UBUNTOO</h2>
        <div className="vision-cards">
          <div className="vision-card">
            <h4>Court terme</h4>
            <p>Outil d'insertion</p>
          </div>
          <div className="vision-card">
            <h4>Moyen terme</h4>
            <p>Réseau contributif</p>
          </div>
          <div className="vision-card highlight">
            <h4>Long terme</h4>
            <p>Référentiel démocratique européen</p>
          </div>
        </div>
      </div>
    </main>
  );
};

function App() {
  const [state, setState] = useState(initialState);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loggedUser, setLoggedUser] = useState(null);

  const handleLogin = (userData) => {
    setIsLoggedIn(true);
    setLoggedUser(userData);
    setState(prev => ({
      ...prev,
      user: {
        ...prev.user,
        name: userData.name || prev.user.name
      }
    }));
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setLoggedUser(null);
  };

  return (
    <div className="App ubuntoo-ancien">
      <>
        <Routes>
          {/* RE'ACTIF PRO Routes */}
          <Route path="reactif-pro/*" element={<ReactifProApp />} />
          
          {/* Ubuntoo Routes */}
          <Route path="*" element={
            <>
              <Navigation 
                isLoggedIn={isLoggedIn}
                user={loggedUser}
                onLogout={handleLogout}
              />
              <LoginModal 
                isOpen={showLoginModal}
                onClose={() => setShowLoginModal(false)}
                onLogin={handleLogin}
              />
              <Routes>
                <Route path="/" element={<HomePage state={state} setState={setState} />} />
                <Route path="profile" element={<ProfilePage state={state} setState={setState} />} />
                <Route path="groups" element={<GroupsPage state={state} setState={setState} />} />
                <Route path="discussions" element={<DiscussionsPage state={state} setState={setState} />} />
                <Route path="mentoring" element={<MentoringPage state={state} setState={setState} />} />
                <Route path="impact" element={<ImpactPage state={state} />} />
              </Routes>
            </>
          } />
        </Routes>
      </>
    </div>
  );
}

// ========== RE'ACTIF PRO APPLICATION ==========

const ReactifProApp = () => {
  const [currentStep, setCurrentStep] = useState("home"); // home, questionnaire, results, identity-card
  const [answers, setAnswers] = useState({});
  const [profileData, setProfileData] = useState(null);
  const location = useLocation();

  return (
    <div className="reactif-pro-app">
      <ReactifProNav />
      <Routes>
        <Route path="/" element={<ReactifProHome onStart={() => setCurrentStep("questionnaire")} />} />
        <Route path="questionnaire" element={
          <ReactifProQuestionnaire 
            answers={answers} 
            setAnswers={setAnswers}
            onComplete={(data) => {
              setProfileData(data);
              setCurrentStep("results");
            }}
          />
        } />
        <Route path="resultats" element={<ReactifProResults profileData={profileData} />} />
        <Route path="carte-identite" element={<ReactifProIdentityCard profileData={profileData} />} />
        <Route path="metiers" element={<ReactifProMetiers profileData={profileData} />} />
      </Routes>
    </div>
  );
};

const ReactifProNav = () => {
  const location = useLocation();
  const navItems = [
    { path: "/reactif-pro", label: "Accueil", icon: Home },
    { path: "/reactif-pro/questionnaire", label: "Questionnaire", icon: HelpCircle },
    { path: "/reactif-pro/carte-identite", label: "Carte d'identité Pro", icon: User },
    { path: "/reactif-pro/metiers", label: "Métiers", icon: Compass },
  ];

  return (
    <header className="reactif-nav">
      <div className="reactif-brand">
        <span className="reactif-logo">RE'ACTIF</span>
        <span className="reactif-pro">PRO</span>
        <span className="brand-tag">Refonte</span>
      </div>
      <nav className="reactif-nav-links">
        {navItems.map(item => (
          <Link
            key={item.path}
            to={item.path}
            className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
          >
            <item.icon size={18} />
            <span>{item.label}</span>
          </Link>
        ))}
      </nav>
      <Link to="/ubuntoo-ancien" className="btn-ubuntoo-link">
        <img src={UBUNTOO_LOGO} alt="Ubuntoo" className="ubuntoo-mini-logo" />
        Espace Ubuntoo
      </Link>
    </header>
  );
};

const ReactifProHome = ({ onStart }) => {
  return (
    <main className="reactif-home">
      <section className="reactif-hero">
        <div className="reactif-hero-content">
          <h1>
            <span className="gradient-text">DE'CLIC PRO</span>
            <span className="subtitle">Découvrez votre potentiel professionnel</span>
          </h1>
          <p>
            Un parcours personnalisé pour identifier vos soft skills, 
            vos valeurs et les métiers qui vous correspondent.
          </p>
          <div className="hero-buttons">
            <Link to="/ubuntoo-ancien/reactif-pro/questionnaire" className="btn-primary-large">
              <Sparkles size={20} />
              Commencer le questionnaire
            </Link>
            <Link to="/ubuntoo-ancien/reactif-pro/carte-identite" className="btn-secondary-large">
              <User size={20} />
              Voir ma carte d'identité Pro
            </Link>
          </div>
        </div>
        <div className="reactif-hero-visual">
          <div className="hero-cards">
            <div className="floating-card card-1">
              <Heart size={24} />
              <span>Soft Skills</span>
            </div>
            <div className="floating-card card-2">
              <Compass size={24} />
              <span>Valeurs</span>
            </div>
            <div className="floating-card card-3">
              <TrendingUp size={24} />
              <span>Potentiel</span>
            </div>
            <div className="floating-card card-4">
              <Award size={24} />
              <span>Métiers</span>
            </div>
          </div>
        </div>
      </section>

      <section className="reactif-features">
        <h2>Votre parcours en 4 étapes</h2>
        <div className="features-timeline">
          <div className="timeline-item">
            <div className="timeline-number">1</div>
            <div className="timeline-content">
              <h3>Questionnaire</h3>
              <p>Répondez à des questions sur vos préférences, valeurs et comportements</p>
            </div>
          </div>
          <div className="timeline-item">
            <div className="timeline-number">2</div>
            <div className="timeline-content">
              <h3>Analyse</h3>
              <p>Notre algorithme analyse vos réponses pour identifier vos forces</p>
            </div>
          </div>
          <div className="timeline-item">
            <div className="timeline-number">3</div>
            <div className="timeline-content">
              <h3>Carte d'identité Pro</h3>
              <p>Découvrez votre profil complet : soft skills, valeurs, potentiel</p>
            </div>
          </div>
          <div className="timeline-item">
            <div className="timeline-number">4</div>
            <div className="timeline-content">
              <h3>Matching Métiers</h3>
              <p>Explorez les métiers compatibles avec votre profil</p>
            </div>
          </div>
        </div>
      </section>

      <section className="reactif-cta">
        <div className="cta-card-large">
          <h2>Prêt à découvrir votre potentiel ?</h2>
          <p>Le questionnaire prend environ 15 minutes. Vos réponses sont confidentielles.</p>
          <Link to="/ubuntoo-ancien/reactif-pro/questionnaire" className="btn-primary-large">
            Démarrer maintenant
          </Link>
        </div>
      </section>
    </main>
  );
};

const ReactifProQuestionnaire = ({ answers, setAnswers, onComplete }) => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [isComplete, setIsComplete] = useState(false);

  const questions = [
    {
      id: "q1",
      category: "Soft Skills",
      question: "Face à un problème complexe, vous préférez :",
      options: [
        { value: "a", label: "Analyser méthodiquement toutes les options", skill: "Analyse" },
        { value: "b", label: "Faire confiance à votre intuition", skill: "Intuition" },
        { value: "c", label: "Demander l'avis de plusieurs personnes", skill: "Collaboration" },
        { value: "d", label: "Tester rapidement différentes solutions", skill: "Adaptabilité" }
      ]
    },
    {
      id: "q2",
      category: "Valeurs",
      question: "Ce qui vous motive le plus dans un travail :",
      options: [
        { value: "a", label: "Aider les autres et avoir un impact positif", skill: "Solidarité" },
        { value: "b", label: "Apprendre et développer de nouvelles compétences", skill: "Croissance" },
        { value: "c", label: "Travailler en équipe et créer des liens", skill: "Collaboration" },
        { value: "d", label: "Avoir de l'autonomie et de la liberté", skill: "Indépendance" }
      ]
    },
    {
      id: "q3",
      category: "Environnement",
      question: "Votre environnement de travail idéal :",
      options: [
        { value: "a", label: "Calme et structuré", skill: "Organisation" },
        { value: "b", label: "Dynamique et en mouvement", skill: "Énergie" },
        { value: "c", label: "Collaboratif avec beaucoup d'échanges", skill: "Communication" },
        { value: "d", label: "Flexible avec du télétravail", skill: "Flexibilité" }
      ]
    },
    {
      id: "q4",
      category: "Communication",
      question: "En situation de conflit, vous avez tendance à :",
      options: [
        { value: "a", label: "Écouter toutes les parties avant de réagir", skill: "Empathie" },
        { value: "b", label: "Chercher un compromis rapidement", skill: "Négociation" },
        { value: "c", label: "Exprimer clairement votre point de vue", skill: "Assertivité" },
        { value: "d", label: "Prendre du recul avant de répondre", skill: "Réflexion" }
      ]
    },
    {
      id: "q5",
      category: "Leadership",
      question: "Dans un projet de groupe, vous êtes plutôt :",
      options: [
        { value: "a", label: "Celui qui organise et planifie", skill: "Organisation" },
        { value: "b", label: "Celui qui motive et encourage", skill: "Leadership" },
        { value: "c", label: "Celui qui propose des idées créatives", skill: "Créativité" },
        { value: "d", label: "Celui qui s'assure que tout le monde est inclus", skill: "Inclusion" }
      ]
    }
  ];

  const handleAnswer = (questionId, option) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: option
    }));
    
    if (currentQuestion < questions.length - 1) {
      setTimeout(() => setCurrentQuestion(currentQuestion + 1), 300);
    } else {
      setIsComplete(true);
    }
  };

  const progress = ((currentQuestion + 1) / questions.length) * 100;

  if (isComplete) {
    return (
      <main className="questionnaire-complete">
        <div className="complete-card">
          <div className="complete-icon">
            <CheckCircle2 size={64} />
          </div>
          <h2>Questionnaire terminé !</h2>
          <p>Nous avons analysé vos réponses et préparé votre profil.</p>
          <div className="complete-actions">
            <Link to="/ubuntoo-ancien/reactif-pro/carte-identite" className="btn-primary-large">
              <User size={20} />
              Voir ma carte d'identité Pro
            </Link>
            <Link to="/ubuntoo-ancien/reactif-pro/metiers" className="btn-secondary-large">
              <Compass size={20} />
              Explorer les métiers compatibles
            </Link>
          </div>
        </div>
      </main>
    );
  }

  const q = questions[currentQuestion];

  return (
    <main className="questionnaire-page">
      <div className="questionnaire-header">
        <div className="progress-info">
          <span>Question {currentQuestion + 1} sur {questions.length}</span>
          <span className="category-badge">{q.category}</span>
        </div>
        <div className="progress-bar-large">
          <div className="progress-fill-large" style={{ width: `${progress}%` }}></div>
        </div>
      </div>

      <div className="question-card">
        <h2>{q.question}</h2>
        <div className="options-grid">
          {q.options.map((option, index) => (
            <button
              key={option.value}
              className={`option-card ${answers[q.id]?.value === option.value ? 'selected' : ''}`}
              onClick={() => handleAnswer(q.id, option)}
            >
              <span className="option-letter">{String.fromCharCode(65 + index)}</span>
              <span className="option-text">{option.label}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="questionnaire-nav">
        {currentQuestion > 0 && (
          <button 
            className="btn-secondary"
            onClick={() => setCurrentQuestion(currentQuestion - 1)}
          >
            Question précédente
          </button>
        )}
      </div>
    </main>
  );
};

const ReactifProResults = ({ profileData }) => {
  return (
    <main className="results-page">
      <h1 className="page-title">Vos résultats</h1>
      <p>Analyse en cours...</p>
    </main>
  );
};

const ReactifProIdentityCard = ({ profileData }) => {
  const profile = {
    name: "Marie Dupont",
    territory: "Grand Est",
    softSkills: [
      { name: "Empathie", level: 85 },
      { name: "Adaptabilité", level: 78 },
      { name: "Communication", level: 82 },
      { name: "Organisation", level: 75 },
      { name: "Travail en équipe", level: 88 },
      { name: "Résolution de problèmes", level: 72 }
    ],
    values: ["Solidarité", "Entraide", "Développement personnel", "Innovation sociale"],
    personality: {
      dominant: "Collaboratif",
      secondary: "Analytique",
      workStyle: "Structuré et empathique"
    },
    potentialScore: 82,
    adaptationScore: 76,
    trajectory: "Reconversion - Secteur social et solidaire"
  };

  return (
    <main className="identity-card-page">
      <h1 className="page-title">Carte d'identité Professionnelle</h1>
      
      <div className="identity-card-container">
        <div className="identity-card-main">
          <div className="card-header-section">
            <div className="profile-avatar-large">
              <User size={48} />
            </div>
            <div className="profile-info-large">
              <h2>{profile.name}</h2>
              <span className="territory-badge">{profile.territory}</span>
              <span className="trajectory-badge">{profile.trajectory}</span>
            </div>
          </div>

          <div className="card-section">
            <h3><Heart size={20} /> Soft Skills</h3>
            <div className="skills-bars">
              {profile.softSkills.map(skill => (
                <div key={skill.name} className="skill-bar-item">
                  <div className="skill-bar-header">
                    <span>{skill.name}</span>
                    <span className="skill-percentage">{skill.level}%</span>
                  </div>
                  <div className="skill-bar-track">
                    <div 
                      className="skill-bar-fill" 
                      style={{ width: `${skill.level}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="card-section">
            <h3><Star size={20} /> Valeurs dominantes</h3>
            <div className="values-tags">
              {profile.values.map(value => (
                <span key={value} className="value-tag">{value}</span>
              ))}
            </div>
          </div>

          <div className="card-section">
            <h3><User size={20} /> Profil de personnalité</h3>
            <div className="personality-grid">
              <div className="personality-item">
                <span className="personality-label">Trait dominant</span>
                <span className="personality-value">{profile.personality.dominant}</span>
              </div>
              <div className="personality-item">
                <span className="personality-label">Trait secondaire</span>
                <span className="personality-value">{profile.personality.secondary}</span>
              </div>
              <div className="personality-item full-width">
                <span className="personality-label">Style de travail</span>
                <span className="personality-value">{profile.personality.workStyle}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="identity-card-sidebar">
          <div className="score-card">
            <h3>Score de potentiel</h3>
            <div className="score-circle">
              <svg viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="45" className="score-bg" />
                <circle 
                  cx="50" cy="50" r="45" 
                  className="score-fill"
                  strokeDasharray={`${profile.potentialScore * 2.83} 283`}
                />
              </svg>
              <span className="score-value">{profile.potentialScore}%</span>
            </div>
            <p>Potentiel global</p>
          </div>

          <div className="score-card">
            <h3>Adaptabilité</h3>
            <div className="score-circle adaptation">
              <svg viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="45" className="score-bg" />
                <circle 
                  cx="50" cy="50" r="45" 
                  className="score-fill"
                  strokeDasharray={`${profile.adaptationScore * 2.83} 283`}
                />
              </svg>
              <span className="score-value">{profile.adaptationScore}%</span>
            </div>
            <p>Capacité d'adaptation</p>
          </div>

          <div className="action-card">
            <h3>Actions</h3>
            <Link to="/ubuntoo-ancien/reactif-pro/metiers" className="btn-action">
              <Compass size={18} />
              Explorer les métiers
            </Link>
            <Link to="/ubuntoo-ancien" className="btn-action secondary">
              <img src={UBUNTOO_LOGO} alt="" className="btn-logo" />
              Rejoindre Ubuntoo
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
};

const ReactifProMetiers = ({ profileData }) => {
  const metiers = [
    { 
      id: 1, 
      title: "Conseiller en insertion professionnelle", 
      match: 92,
      sector: "Social",
      description: "Accompagner les personnes dans leur parcours vers l'emploi",
      skills: ["Empathie", "Communication", "Organisation"]
    },
    { 
      id: 2, 
      title: "Chargé de projet ESS", 
      match: 87,
      sector: "Économie sociale",
      description: "Piloter des projets à impact social et solidaire",
      skills: ["Organisation", "Leadership", "Innovation"]
    },
    { 
      id: 3, 
      title: "Médiateur social", 
      match: 85,
      sector: "Social",
      description: "Faciliter les relations et résoudre les conflits",
      skills: ["Empathie", "Communication", "Négociation"]
    },
    { 
      id: 4, 
      title: "Formateur pour adultes", 
      match: 82,
      sector: "Formation",
      description: "Transmettre des savoirs et accompagner l'apprentissage",
      skills: ["Communication", "Pédagogie", "Adaptabilité"]
    },
    { 
      id: 5, 
      title: "Coordinateur de projets associatifs", 
      match: 79,
      sector: "Associatif",
      description: "Organiser et coordonner les activités d'une association",
      skills: ["Organisation", "Travail en équipe", "Gestion"]
    }
  ];

  return (
    <main className="metiers-page">
      <h1 className="page-title">Métiers compatibles</h1>
      <p className="page-intro">
        Basé sur votre profil, voici les métiers qui correspondent le mieux à vos compétences et valeurs.
      </p>

      <div className="metiers-grid">
        {metiers.map(metier => (
          <div key={metier.id} className="metier-card">
            <div className="metier-header">
              <div className="match-badge" data-match={metier.match >= 90 ? 'high' : metier.match >= 80 ? 'medium' : 'low'}>
                {metier.match}% compatible
              </div>
              <span className="sector-tag">{metier.sector}</span>
            </div>
            <h3>{metier.title}</h3>
            <p>{metier.description}</p>
            <div className="metier-skills">
              {metier.skills.map(skill => (
                <span key={skill} className="skill-mini">{skill}</span>
              ))}
            </div>
            <button className="btn-explore">
              En savoir plus
              <ArrowRight size={16} />
            </button>
          </div>
        ))}
      </div>
    </main>
  );
};

export default App;
