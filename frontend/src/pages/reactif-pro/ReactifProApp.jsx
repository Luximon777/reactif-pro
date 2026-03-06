import React, { useState, useEffect } from 'react';
import { 
  User, Building2, Users, ArrowRight, Shield, Key, 
  LayoutDashboard, FileText, Target, Settings, LogOut,
  ChevronLeft, Eye, EyeOff, Check, AlertCircle, Loader2
} from 'lucide-react';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import './ReactifPro.css';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// ============================================================================
// LANDING PAGE RE'ACTIF PRO
// ============================================================================
const ReactifProLanding = ({ onSelectAccess }) => {
  return (
    <div className="reactif-landing">
      <div className="reactif-landing-header">
        <img src="/reactif-pro-logo-full.png" alt="RE'ACTIF PRO" className="reactif-logo" />
        <h1>RE'ACTIF PRO</h1>
        <p className="reactif-tagline">
          Plateforme d'accompagnement professionnel personnalisé
        </p>
      </div>

      <div className="reactif-access-cards">
        {/* Mon Espace Pro */}
        <Card 
          className="reactif-access-card access-pro"
          onClick={() => onSelectAccess('pro')}
          data-testid="access-pro"
        >
          <CardHeader>
            <div className="access-icon-wrapper pro">
              <User size={32} />
            </div>
            <CardTitle>Mon Espace Pro</CardTitle>
            <CardDescription>
              Espace personnel confidentiel sous pseudonyme
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="access-features">
              <li><Check size={14} /> Compte pseudonyme (pas d'identité civile)</li>
              <li><Check size={14} /> Récupère tes résultats DE'CLIC PRO</li>
              <li><Check size={14} /> Tableau de bord personnalisé</li>
              <li><Check size={14} /> Suivi de ton parcours professionnel</li>
            </ul>
            <Button className="access-btn pro-btn">
              Accéder <ArrowRight size={16} />
            </Button>
          </CardContent>
        </Card>

        {/* Entreprise RH */}
        <Card 
          className="reactif-access-card access-rh"
          onClick={() => onSelectAccess('rh')}
          data-testid="access-rh"
        >
          <CardHeader>
            <div className="access-icon-wrapper rh">
              <Building2 size={32} />
            </div>
            <CardTitle>Entreprise RH</CardTitle>
            <CardDescription>
              Espace dédié aux professionnels RH
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="access-features">
              <li><Check size={14} /> Gestion des offres d'emploi</li>
              <li><Check size={14} /> Matching candidats anonymisés</li>
              <li><Check size={14} /> Dashboard analytics RH</li>
              <li><Check size={14} /> Outils de recrutement responsable</li>
            </ul>
            <Button className="access-btn rh-btn" disabled>
              Bientôt disponible
            </Button>
          </CardContent>
        </Card>

        {/* Partenaires Sociaux */}
        <Card 
          className="reactif-access-card access-partners"
          onClick={() => onSelectAccess('partners')}
          data-testid="access-partners"
        >
          <CardHeader>
            <div className="access-icon-wrapper partners">
              <Users size={32} />
            </div>
            <CardTitle>Partenaires Sociaux</CardTitle>
            <CardDescription>
              Espace de consultation et collaboration
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="access-features">
              <li><Check size={14} /> Statistiques d'usage anonymisées</li>
              <li><Check size={14} /> Rapports tendances emploi</li>
              <li><Check size={14} /> Espace de collaboration</li>
              <li><Check size={14} /> Documentation partagée</li>
            </ul>
            <Button className="access-btn partners-btn" disabled>
              Bientôt disponible
            </Button>
          </CardContent>
        </Card>
      </div>

      <div className="reactif-landing-footer">
        <div className="privacy-badge">
          <Shield size={16} />
          <span>Vos données sont protégées - Compte pseudonyme sans identité civile obligatoire</span>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// AUTHENTIFICATION - CONNEXION / INSCRIPTION
// ============================================================================
const AuthPage = ({ onBack, onAuthSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Champs du formulaire
  const [pseudo, setPseudo] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [emailRecovery, setEmailRecovery] = useState('');
  const [accessCode, setAccessCode] = useState('');
  const [consentCgu, setConsentCgu] = useState(false);
  const [consentPrivacy, setConsentPrivacy] = useState(false);
  const [consentMarketing, setConsentMarketing] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/reactif/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pseudo, password })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Erreur de connexion');
      }

      // Stocker le token et les infos utilisateur
      localStorage.setItem('reactif_token', data.token);
      localStorage.setItem('reactif_user', JSON.stringify(data.user));
      onAuthSuccess(data.user);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');

    // Validations
    if (password !== confirmPassword) {
      setError('Les mots de passe ne correspondent pas');
      return;
    }
    if (password.length < 8) {
      setError('Le mot de passe doit contenir au moins 8 caractères');
      return;
    }
    if (!consentCgu || !consentPrivacy) {
      setError('Vous devez accepter les CGU et la politique de confidentialité');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/reactif/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          pseudo,
          password,
          email_recovery: emailRecovery || null,
          access_code: accessCode || null,
          consent_cgu: consentCgu,
          consent_privacy: consentPrivacy,
          consent_marketing: consentMarketing
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Erreur lors de l\'inscription');
      }

      // Stocker le token et les infos utilisateur
      localStorage.setItem('reactif_token', data.token);
      localStorage.setItem('reactif_user', JSON.stringify(data.user));
      onAuthSuccess(data.user);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="reactif-auth-page">
      <Button variant="ghost" onClick={onBack} className="auth-back-btn">
        <ChevronLeft size={20} /> Retour
      </Button>

      <div className="auth-container">
        <div className="auth-header">
          <User size={40} className="auth-icon" />
          <h2>{isLogin ? 'Connexion' : 'Créer un compte'}</h2>
          <p className="auth-subtitle">
            {isLogin 
              ? 'Connecte-toi avec ton pseudonyme' 
              : 'Crée ton espace personnel confidentiel'}
          </p>
        </div>

        {!isLogin && (
          <div className="auth-reassurance">
            <Shield size={16} />
            <p>
              Tu peux utiliser ce service sous pseudonyme.<br/>
              Ton identité civile n'est pas requise pour créer un compte.<br/>
              Seules les données strictement nécessaires sont collectées.
            </p>
          </div>
        )}

        {error && (
          <div className="auth-error">
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={isLogin ? handleLogin : handleRegister} className="auth-form">
          {/* Pseudonyme */}
          <div className="form-group">
            <label htmlFor="pseudo">Pseudonyme *</label>
            <Input
              id="pseudo"
              type="text"
              value={pseudo}
              onChange={(e) => setPseudo(e.target.value)}
              placeholder="Ton pseudonyme"
              required
              minLength={3}
              maxLength={50}
              data-testid="input-pseudo"
            />
          </div>

          {/* Mot de passe */}
          <div className="form-group">
            <label htmlFor="password">Mot de passe *</label>
            <div className="password-input-wrapper">
              <Input
                id="password"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Ton mot de passe"
                required
                minLength={8}
                data-testid="input-password"
              />
              <button 
                type="button" 
                className="password-toggle"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          {/* Champs supplémentaires pour l'inscription */}
          {!isLogin && (
            <>
              {/* Confirmation mot de passe */}
              <div className="form-group">
                <label htmlFor="confirmPassword">Confirmer le mot de passe *</label>
                <Input
                  id="confirmPassword"
                  type={showPassword ? 'text' : 'password'}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Confirme ton mot de passe"
                  required
                  minLength={8}
                  data-testid="input-confirm-password"
                />
              </div>

              {/* Email de récupération (facultatif) */}
              <div className="form-group optional">
                <label htmlFor="emailRecovery">
                  Email de récupération <span className="optional-badge">Facultatif</span>
                </label>
                <Input
                  id="emailRecovery"
                  type="email"
                  value={emailRecovery}
                  onChange={(e) => setEmailRecovery(e.target.value)}
                  placeholder="Pour récupérer ton accès si besoin"
                  data-testid="input-email"
                />
              </div>

              {/* Code d'accès DE'CLIC PRO (facultatif) */}
              <div className="form-group optional">
                <label htmlFor="accessCode">
                  Code d'accès DE'CLIC PRO <span className="optional-badge">Facultatif</span>
                </label>
                <Input
                  id="accessCode"
                  type="text"
                  value={accessCode}
                  onChange={(e) => setAccessCode(e.target.value.toUpperCase())}
                  placeholder="XXXX-XXXX"
                  maxLength={9}
                  data-testid="input-access-code"
                />
                <p className="form-hint">
                  <Key size={12} /> Si tu as passé le test DE'CLIC PRO, entre ton code pour récupérer tes résultats
                </p>
              </div>

              {/* Consentements */}
              <div className="consent-section">
                <label className="consent-checkbox">
                  <input
                    type="checkbox"
                    checked={consentCgu}
                    onChange={(e) => setConsentCgu(e.target.checked)}
                    required
                    data-testid="consent-cgu"
                  />
                  <span>J'accepte les <a href="/cgu" target="_blank">Conditions Générales d'Utilisation</a> *</span>
                </label>

                <label className="consent-checkbox">
                  <input
                    type="checkbox"
                    checked={consentPrivacy}
                    onChange={(e) => setConsentPrivacy(e.target.checked)}
                    required
                    data-testid="consent-privacy"
                  />
                  <span>J'ai lu et j'accepte la <a href="/privacy" target="_blank">Politique de Confidentialité</a> *</span>
                </label>

                <label className="consent-checkbox optional">
                  <input
                    type="checkbox"
                    checked={consentMarketing}
                    onChange={(e) => setConsentMarketing(e.target.checked)}
                    data-testid="consent-marketing"
                  />
                  <span>J'accepte de recevoir des informations sur les services RE'ACTIF PRO</span>
                </label>
              </div>
            </>
          )}

          <Button 
            type="submit" 
            className="auth-submit-btn"
            disabled={loading}
            data-testid="auth-submit"
          >
            {loading ? (
              <><Loader2 size={18} className="animate-spin" /> Chargement...</>
            ) : (
              isLogin ? 'Se connecter' : 'Créer mon compte'
            )}
          </Button>
        </form>

        <div className="auth-switch">
          {isLogin ? (
            <p>Pas encore de compte ? <button onClick={() => setIsLogin(false)}>Créer un compte</button></p>
          ) : (
            <p>Déjà un compte ? <button onClick={() => setIsLogin(true)}>Se connecter</button></p>
          )}
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// DASHBOARD - ESPACE PERSONNEL
// ============================================================================
const Dashboard = ({ user, onLogout }) => {
  const [activeSection, setActiveSection] = useState('overview');

  const handleLogout = () => {
    localStorage.removeItem('reactif_token');
    localStorage.removeItem('reactif_user');
    onLogout();
  };

  return (
    <div className="reactif-dashboard">
      {/* Sidebar */}
      <aside className="dashboard-sidebar">
        <div className="sidebar-header">
          <img src="/reactif-pro-logo-full.png" alt="RE'ACTIF PRO" className="sidebar-logo" />
          <div className="user-info">
            <User size={20} />
            <span className="user-pseudo">{user?.pseudo || 'Utilisateur'}</span>
          </div>
        </div>

        <nav className="sidebar-nav">
          <button 
            className={`nav-item ${activeSection === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveSection('overview')}
          >
            <LayoutDashboard size={18} /> Tableau de bord
          </button>
          <button 
            className={`nav-item ${activeSection === 'parcours' ? 'active' : ''}`}
            onClick={() => setActiveSection('parcours')}
          >
            <FileText size={18} /> Mes parcours
          </button>
          <button 
            className={`nav-item ${activeSection === 'results' ? 'active' : ''}`}
            onClick={() => setActiveSection('results')}
          >
            <Target size={18} /> Mes résultats
          </button>
          <button 
            className={`nav-item ${activeSection === 'settings' ? 'active' : ''}`}
            onClick={() => setActiveSection('settings')}
          >
            <Settings size={18} /> Paramètres
          </button>
        </nav>

        <div className="sidebar-footer">
          <button className="logout-btn" onClick={handleLogout}>
            <LogOut size={18} /> Déconnexion
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="dashboard-main">
        {activeSection === 'overview' && (
          <DashboardOverview user={user} />
        )}
        {activeSection === 'parcours' && (
          <DashboardParcours user={user} />
        )}
        {activeSection === 'results' && (
          <DashboardResults user={user} />
        )}
        {activeSection === 'settings' && (
          <DashboardSettings user={user} onLogout={handleLogout} />
        )}
      </main>
    </div>
  );
};

// ============================================================================
// DASHBOARD SECTIONS
// ============================================================================
const DashboardOverview = ({ user }) => {
  return (
    <div className="dashboard-section overview">
      <h1>Bienvenue, {user?.pseudo} !</h1>
      <p className="section-subtitle">Voici un aperçu de ton espace professionnel</p>

      <div className="overview-cards">
        <Card className="overview-card">
          <CardHeader>
            <CardTitle>Profil complété</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="progress-circle">
              <span className="progress-value">{user?.profile_completion || 0}%</span>
            </div>
          </CardContent>
        </Card>

        <Card className="overview-card">
          <CardHeader>
            <CardTitle>Tests réalisés</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="stat-value">{user?.tests_completed || 0}</div>
          </CardContent>
        </Card>

        <Card className="overview-card">
          <CardHeader>
            <CardTitle>Projets en cours</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="stat-value">{user?.active_projects || 0}</div>
          </CardContent>
        </Card>
      </div>

      <div className="quick-actions">
        <h2>Actions rapides</h2>
        <div className="actions-grid">
          <Button className="action-btn">
            Passer le test DE'CLIC PRO
          </Button>
          <Button className="action-btn" variant="outline">
            Créer un projet professionnel
          </Button>
          <Button className="action-btn" variant="outline">
            Importer un résultat
          </Button>
        </div>
      </div>
    </div>
  );
};

const DashboardParcours = ({ user }) => {
  return (
    <div className="dashboard-section parcours">
      <h1>Mes parcours</h1>
      <p className="section-subtitle">Suivi de tes questionnaires et parcours</p>
      
      <div className="empty-state">
        <FileText size={48} />
        <p>Aucun parcours pour le moment</p>
        <Button>Commencer un nouveau parcours</Button>
      </div>
    </div>
  );
};

const DashboardResults = ({ user }) => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchResults();
  }, []);

  const fetchResults = async () => {
    try {
      const token = localStorage.getItem('reactif_token');
      const response = await fetch(`${API_URL}/api/reactif/user/results`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setResults(data.results || []);
      }
    } catch (err) {
      console.error('Erreur chargement résultats:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="dashboard-section results loading">
        <Loader2 size={32} className="animate-spin" />
        <p>Chargement des résultats...</p>
      </div>
    );
  }

  return (
    <div className="dashboard-section results">
      <h1>Mes résultats</h1>
      <p className="section-subtitle">Résultats de tes tests et analyses</p>
      
      {results.length === 0 ? (
        <div className="empty-state">
          <Target size={48} />
          <p>Aucun résultat pour le moment</p>
          <p className="hint">Passe le test DE'CLIC PRO ou importe tes résultats avec un code d'accès</p>
          <Button>Passer le test DE'CLIC PRO</Button>
        </div>
      ) : (
        <div className="results-list">
          {results.map((result, idx) => (
            <Card key={idx} className="result-card">
              <CardHeader>
                <CardTitle>{result.title || 'Résultat DE\'CLIC PRO'}</CardTitle>
                <CardDescription>{new Date(result.created_at).toLocaleDateString('fr-FR')}</CardDescription>
              </CardHeader>
              <CardContent>
                <p>MBTI: {result.result_data?.profile_summary?.mbti}</p>
                <Button variant="outline" size="sm">Voir le détail</Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

const DashboardSettings = ({ user, onLogout }) => {
  return (
    <div className="dashboard-section settings">
      <h1>Paramètres</h1>
      <p className="section-subtitle">Gère ton compte et tes préférences</p>

      <div className="settings-cards">
        <Card className="settings-card">
          <CardHeader>
            <CardTitle>Informations du compte</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="info-row">
              <span className="label">Pseudonyme</span>
              <span className="value">{user?.pseudo}</span>
            </div>
            <div className="info-row">
              <span className="label">Email de récupération</span>
              <span className="value">{user?.email_recovery || 'Non renseigné'}</span>
            </div>
            <div className="info-row">
              <span className="label">Membre depuis</span>
              <span className="value">{user?.created_at ? new Date(user.created_at).toLocaleDateString('fr-FR') : 'N/A'}</span>
            </div>
          </CardContent>
        </Card>

        <Card className="settings-card">
          <CardHeader>
            <CardTitle>Confidentialité</CardTitle>
          </CardHeader>
          <CardContent>
            <Button variant="outline">Télécharger mes données</Button>
            <Button variant="outline" className="danger">Supprimer mon compte</Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// ============================================================================
// APP PRINCIPALE RE'ACTIF PRO
// ============================================================================
const ReactifProApp = () => {
  const [currentView, setCurrentView] = useState('landing'); // landing, auth, dashboard
  const [selectedAccess, setSelectedAccess] = useState(null);
  const [user, setUser] = useState(null);

  // Vérifier si l'utilisateur est déjà connecté
  useEffect(() => {
    const token = localStorage.getItem('reactif_token');
    const savedUser = localStorage.getItem('reactif_user');
    
    if (token && savedUser) {
      try {
        setUser(JSON.parse(savedUser));
        setCurrentView('dashboard');
      } catch (e) {
        localStorage.removeItem('reactif_token');
        localStorage.removeItem('reactif_user');
      }
    }
  }, []);

  const handleSelectAccess = (access) => {
    setSelectedAccess(access);
    if (access === 'pro') {
      setCurrentView('auth');
    }
    // Les autres accès sont désactivés pour l'instant
  };

  const handleAuthSuccess = (userData) => {
    setUser(userData);
    setCurrentView('dashboard');
  };

  const handleLogout = () => {
    setUser(null);
    setCurrentView('landing');
  };

  const handleBackToLanding = () => {
    setCurrentView('landing');
    setSelectedAccess(null);
  };

  return (
    <div className="reactif-pro-app">
      {currentView === 'landing' && (
        <ReactifProLanding onSelectAccess={handleSelectAccess} />
      )}
      {currentView === 'auth' && (
        <AuthPage 
          onBack={handleBackToLanding} 
          onAuthSuccess={handleAuthSuccess}
        />
      )}
      {currentView === 'dashboard' && (
        <Dashboard 
          user={user} 
          onLogout={handleLogout}
        />
      )}
    </div>
  );
};

export default ReactifProApp;
