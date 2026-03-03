import { useState, useEffect, useRef } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import html2canvas from "html2canvas";
import { jsPDF } from "jspdf";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { 
  RadarChart, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis, 
  Radar, 
  ResponsiveContainer,
  Tooltip
} from "recharts";
import { 
  ChevronRight, 
  ChevronLeft, 
  ChevronDown,
  ChevronUp,
  Search, 
  Compass, 
  Target, 
  Brain, 
  Heart, 
  Shield, 
  Zap,
  Award,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  Lightbulb,
  Users,
  Briefcase,
  ArrowRight,
  Calendar,
  Clock,
  Sparkles,
  Layers,
  Star,
  Gem,
  Crown,
  Download,
  Share2,
  BookOpen,
  Flame,
  Eye,
  Hand,
  QrCode,
  ExternalLink,
  Loader2,
  Info,
  User,
  Map,
  Globe,
  Network,
  Settings,
  Cpu,
  Building,
  AlertCircle
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// ============================================================================
// DECLIC PRO LOGO SVG
// ============================================================================
const DeclicProLogo = ({ size = 120, animated = true }) => (
  <svg width={size} height={size} viewBox="0 0 120 120">
    {/* Cercle de pulsation */}
    {animated && (
      <circle 
        className="pulse-ring" 
        cx="60" cy="60" r="50" 
        fill="none" 
        stroke="#F97316" 
        strokeWidth="2" 
        opacity="0.3"
      />
    )}
    
    {/* Cercle de fond */}
    <circle cx="60" cy="60" r="50" fill="none" stroke="#FFE4D6" strokeWidth="2"/>
    
    {/* Point de connexion central (le déclic) */}
    <circle cx="60" cy="60" r="15" fill="#F97316" className={animated ? "glow-effect" : ""}/>
    
    {/* Éclairs/étincelles du déclic */}
    <g className={animated ? "spark" : ""}>
      <path d="M 60 35 L 62 50 L 70 48 L 60 60" fill="#FBBF24" opacity="0.9"/>
      <path d="M 85 60 L 70 62 L 72 70 L 60 60" fill="#FBBF24" opacity="0.9"/>
      <path d="M 60 85 L 58 70 L 50 72 L 60 60" fill="#FBBF24" opacity="0.9"/>
      <path d="M 35 60 L 50 58 L 48 50 L 60 60" fill="#FBBF24" opacity="0.9"/>
    </g>
    
    {/* Nœuds périphériques (connexions activées) */}
    <circle cx="60" cy="20" r="5" fill="#F97316"/>
    <circle cx="90" cy="40" r="5" fill="#F97316"/>
    <circle cx="90" cy="80" r="5" fill="#F97316"/>
    <circle cx="60" cy="100" r="5" fill="#F97316"/>
    <circle cx="30" cy="80" r="5" fill="#F97316"/>
    <circle cx="30" cy="40" r="5" fill="#F97316"/>
    
    {/* Lignes de connexion activées */}
    <line x1="60" y1="20" x2="60" y2="45" stroke="#F97316" strokeWidth="2" strokeLinecap="round"/>
    <line x1="90" y1="40" x2="75" y2="60" stroke="#F97316" strokeWidth="2" strokeLinecap="round"/>
    <line x1="90" y1="80" x2="75" y2="60" stroke="#F97316" strokeWidth="2" strokeLinecap="round"/>
    <line x1="60" y1="100" x2="60" y2="75" stroke="#F97316" strokeWidth="2" strokeLinecap="round"/>
    <line x1="30" y1="80" x2="45" y2="60" stroke="#F97316" strokeWidth="2" strokeLinecap="round"/>
    <line x1="30" y1="40" x2="45" y2="60" stroke="#F97316" strokeWidth="2" strokeLinecap="round"/>
  </svg>
);

// ============================================================================
// RE'ACTIF PRO LOGO SVG - Purple/Blue Theme (Official Brand Colors)
// ============================================================================
const ReactifProLogo = ({ size = 80, animated = false }) => (
  <svg width={size} height={size} viewBox="0 0 100 100" className="reactif-logo-svg">
    {/* Outer circle with dashes (traits d'union) - animated rotation */}
    <circle 
      cx="50" cy="50" r="45" 
      fill="none" 
      stroke="#c7d2fe" 
      strokeWidth="2" 
      strokeDasharray="12 6"
      strokeLinecap="round"
      className={animated ? "reactif-rotating-circle" : ""}
    />
    
    {/* Hexagonal nodes - connected points (purple) */}
    <circle cx="50" cy="12" r="5" fill="#6366f1"/>
    <circle cx="82" cy="30" r="5" fill="#6366f1"/>
    <circle cx="82" cy="70" r="5" fill="#6366f1"/>
    <circle cx="50" cy="88" r="5" fill="#6366f1"/>
    <circle cx="18" cy="70" r="5" fill="#6366f1"/>
    <circle cx="18" cy="30" r="5" fill="#6366f1"/>
    
    {/* Connection lines with dashes (traits d'union) */}
    <g className={animated ? "reactif-rotating-lines" : ""}>
      <line x1="50" y1="12" x2="82" y2="30" stroke="#a5b4fc" strokeWidth="2" strokeDasharray="8 4" strokeLinecap="round"/>
      <line x1="82" y1="30" x2="82" y2="70" stroke="#a5b4fc" strokeWidth="2" strokeDasharray="8 4" strokeLinecap="round"/>
      <line x1="82" y1="70" x2="50" y2="88" stroke="#a5b4fc" strokeWidth="2" strokeDasharray="8 4" strokeLinecap="round"/>
      <line x1="50" y1="88" x2="18" y2="70" stroke="#a5b4fc" strokeWidth="2" strokeDasharray="8 4" strokeLinecap="round"/>
      <line x1="18" y1="70" x2="18" y2="30" stroke="#a5b4fc" strokeWidth="2" strokeDasharray="8 4" strokeLinecap="round"/>
      <line x1="18" y1="30" x2="50" y2="12" stroke="#a5b4fc" strokeWidth="2" strokeDasharray="8 4" strokeLinecap="round"/>
    </g>
    
    {/* Inner connections to center (medium purple) */}
    <line x1="50" y1="12" x2="50" y2="35" stroke="#818cf8" strokeWidth="1.5"/>
    <line x1="82" y1="30" x2="62" y2="42" stroke="#818cf8" strokeWidth="1.5"/>
    <line x1="82" y1="70" x2="62" y2="58" stroke="#818cf8" strokeWidth="1.5"/>
    <line x1="50" y1="88" x2="50" y2="65" stroke="#818cf8" strokeWidth="1.5"/>
    <line x1="18" y1="70" x2="38" y2="58" stroke="#818cf8" strokeWidth="1.5"/>
    <line x1="18" y1="30" x2="38" y2="42" stroke="#818cf8" strokeWidth="1.5"/>
    
    {/* Central element - glow background (pale lavender) */}
    <circle cx="50" cy="50" r="18" fill="#e0e7ff"/>
    
    {/* Central circle (indigo) */}
    <circle cx="50" cy="50" r="13" fill="#4f46e5"/>
    
    {/* R letter in the center */}
    <text x="50" y="56" textAnchor="middle" fill="white" fontSize="16" fontWeight="bold" fontFamily="Arial, sans-serif">R</text>
  </svg>
);

// ============================================================================
// LANDING PAGE - DE'CLIC PRO Design
// ============================================================================
const LandingPage = ({ onSelectPath }) => {
  return (
    <div className="landing-page declic-theme">
      <div className="landing-hero">
        {/* Header row with both logos */}
        <div className="landing-logos-row">
          <div className="declic-logo-container">
            <DeclicProLogo size={140} animated={true} />
            <div className="declic-brand">
              <h1 className="declic-title">
                DE'<span className="declic-highlight">CLIC</span> PRO
              </h1>
              <p className="declic-tagline">L'APPLY RE'ACTIF PRO</p>
            </div>
          </div>
          
          <div className="landing-reactif-logo" data-testid="landing-reactif-logo">
            <img src="/reactif-pro-logo.png" alt="RE'ACTIF PRO" className="reactif-logo-img-landing" />
          </div>
        </div>
        
        {/* PHASE 1 */}
        <div className="landing-phase-section">
          <div className="phase-badge phase-1-badge">
            <span className="phase-number">PHASE 1</span>
          </div>
        </div>
      </div>

      <div className="path-selection">
        <Card 
          className="path-card path-job declic-card" 
          onClick={() => onSelectPath('job')}
          data-testid="path-job-card"
        >
          <CardHeader>
            <div className="path-icon declic-icon">
              <Target size={48} />
            </div>
            <CardTitle>Je cherche mon job</CardTitle>
            <CardDescription className="path-highlight">
              <strong className="path-highlight-title">Avant de postuler !</strong> Vérifies si tes compétences sont à jour et valorises toi !
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button className="path-button declic-button" data-testid="start-job-path-btn">
              Commencer <ChevronRight size={20} />
            </Button>
          </CardContent>
        </Card>

        <Card 
          className="path-card path-explore declic-card" 
          onClick={() => onSelectPath('explore')}
          data-testid="path-explore-card"
        >
          <CardHeader>
            <div className="path-icon declic-icon-secondary">
              <Compass size={48} />
            </div>
            <CardTitle>Je cherche encore...</CardTitle>
            <CardDescription className="path-highlight">
              <strong className="path-highlight-title">Pas encore d'idée précise ?</strong> Peu d'expérience ou nouvelle orientation pro. découvre tes soft skills et des métiers qui pourraient te correspondre.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button className="path-button declic-button-secondary" variant="secondary" data-testid="start-explore-path-btn">
              Explorer <ChevronRight size={20} />
            </Button>
          </CardContent>
        </Card>
      </div>

      <p className="phase-description-below-cards">
        Je débute par un questionnaire <strong style={{color: '#f97316'}}>TOTALEMENT ANONYME</strong> et <strong style={{color: '#f97316'}}>GRATUIT</strong> en moins de 5 mn.
      </p>

      {/* PHASE 2 */}
      <div className="landing-phase-section phase-2-section">
        <div className="phase-badge phase-2-badge">
          <span className="phase-number">PHASE 2</span>
        </div>
        <p className="phase-description">
          J'ai accès à des services professionnels pour garantir mon employabilité <strong>tout au long de ma vie !</strong>
        </p>
      </div>

      {/* Services RE'ACTIF PRO */}
      <div className="reactif-services-pro">
        {/* NIVEAU 1 */}
        <div className="service-level-pro">
          <div className="level-header level-1-header">
            <div className="level-icon"><Layers size={24} /></div>
            <div className="level-info">
              <span className="level-tag">NIVEAU 1</span>
              <h3>FONDATION</h3>
              <p>Vision & Cadre Structurant</p>
            </div>
          </div>
          
          {/* Job Matching Intelligent - Service Principal */}
          <div className="service-highlight-pro">
            <div className="highlight-header">
              <div className="highlight-icon"><Target size={28} /></div>
              <div className="highlight-title">
                <h4>Job Matching Intelligent & Évolutif</h4>
                <p className="highlight-tagline">Au-delà des compétences déclarées, vers le potentiel réel</p>
              </div>
            </div>
            
            <div className="highlight-grid">
              {/* Profil Dynamique */}
              <div className="highlight-card">
                <div className="highlight-card-header">
                  <User size={20} />
                  <h5>Profil Utilisateur Dynamique</h5>
                </div>
                <p className="highlight-card-intro">Le dispositif repose sur un profil enrichi intégrant :</p>
                <ul className="highlight-list">
                  <li><Briefcase size={14} className="list-icon-svg" /> Compétences techniques</li>
                  <li><Users size={14} className="list-icon-svg" /> Soft skills</li>
                  <li><Heart size={14} className="list-icon-svg" /> Valeurs et motivations</li>
                  <li><TrendingUp size={14} className="list-icon-svg" /> Potentiel d'adaptation</li>
                  <li><ArrowRight size={14} className="list-icon-svg" /> Trajectoire professionnelle</li>
                  <li><Target size={14} className="list-icon-svg" /> Secteur de "gravité professionnelle"</li>
                </ul>
                <p className="highlight-outcome">
                  <Target size={14} /> <strong>Objectif&nbsp;:</strong> proposer des offres cohérentes avec le potentiel réel, pas uniquement le dernier poste occupé.
                </p>
              </div>

              {/* Logique Écosystème */}
              <div className="highlight-card">
                <div className="highlight-card-header">
                  <Network size={20} />
                  <h5>Logique d'Écosystème</h5>
                </div>
                <p className="highlight-card-intro">Le matching positionne la personne dans :</p>
                <ul className="highlight-list">
                  <li><Globe size={14} className="list-icon-svg" /> Un écosystème métiers</li>
                  <li><Building size={14} className="list-icon-svg" /> Des secteurs compatibles</li>
                  <li><Map size={14} className="list-icon-svg" /> Des trajectoires possibles</li>
                  <li><Sparkles size={14} className="list-icon-svg" /> Des métiers émergents ou hybrides</li>
                </ul>
                <p className="highlight-outcome">
                  <TrendingUp size={14} /> Ce n'est pas une correspondance statique, mais une <strong>projection évolutive</strong>.
                </p>
              </div>

              {/* Observatoire Intégré - Accent */}
              <div className="highlight-card highlight-card-accent-blue">
                <div className="highlight-card-header">
                  <Eye size={20} />
                  <h5>Observatoire des Compétences Prédictif</h5>
                </div>
                <p className="highlight-card-intro">Le job matching est connecté à :</p>
                <ul className="highlight-list-check">
                  <li><CheckCircle2 size={14} /> Observatoire dynamique des compétences</li>
                  <li><CheckCircle2 size={14} /> Analyse des usages réels sur le terrain</li>
                  <li><CheckCircle2 size={14} /> Identification des compétences hybrides</li>
                  <li><CheckCircle2 size={14} /> Anticipation des besoins futurs</li>
                </ul>
                <p className="highlight-conclusion-blue">
                  <Users size={14} /> Les usagers deviennent <strong>contributeurs</strong> à la lecture des transformations du travail.
                </p>
              </div>

              {/* Différenciation Stratégique */}
              <div className="highlight-card highlight-card-accent">
                <div className="highlight-card-header">
                  <Award size={20} />
                  <h5>Différenciation RE'ACTIF PRO</h5>
                </div>
                <p className="highlight-card-intro">Notre vision stratégique :</p>
                <ul className="highlight-list-check">
                  <li><CheckCircle2 size={14} /> Sortir du matching déclaratif</li>
                  <li><CheckCircle2 size={14} /> Intégrer la dimension axiologique (sens, valeurs)</li>
                  <li><CheckCircle2 size={14} /> Identifier les écarts avec micro-actions correctives</li>
                  <li><CheckCircle2 size={14} /> Valoriser le potentiel plutôt que le passé</li>
                </ul>
                <p className="highlight-conclusion">
                  <Zap size={14} /> <span>Le job matching devient un <strong>outil d'orientation active</strong> et non plus seulement de placement.</span>
                </p>
              </div>
            </div>
          </div>

          {/* Services Complémentaires */}
          <div className="service-grid-pro service-grid-complementary">
            <div className="service-item-pro">
              <div className="service-header-pro">
                <div className="service-icon-pro"><Compass size={20} /></div>
                <h4>Parcours d'accompagnement hybride</h4>
              </div>
              <div className="service-content-pro">
                <span className="content-label">Socle opérationnel :</span>
                <ul className="service-list-check">
                  <li><CheckCircle2 size={14} className="check-icon" /> Accompagnement humain renforcé par la technologie</li>
                  <li><CheckCircle2 size={14} className="check-icon" /> Diagnostic global : compétences, personnalité, aspirations</li>
                  <li><CheckCircle2 size={14} className="check-icon" /> Analyse des freins et leviers</li>
                  <li><CheckCircle2 size={14} className="check-icon" /> Construction d'un plan d'action individualisé</li>
                  <li><CheckCircle2 size={14} className="check-icon" /> Positionnement professionnel aligné avec le sens et la transférabilité</li>
                </ul>
              </div>
            </div>

            <div className="service-item-pro">
              <div className="service-header-pro">
                <div className="service-icon-pro"><Shield size={20} /></div>
                <h4>Gouvernance & Éthique IA</h4>
              </div>
              <div className="service-content-pro">
                <ul className="service-list-check">
                  <li><CheckCircle2 size={14} className="check-icon" /> Charte éthique IA dédiée à l'accompagnement</li>
                  <li><CheckCircle2 size={14} className="check-icon" /> IA explicable et non discriminante</li>
                  <li><CheckCircle2 size={14} className="check-icon" /> Transparence des algorithmes décisionnels</li>
                  <li><CheckCircle2 size={14} className="check-icon" /> Protection des données</li>
                  <li><CheckCircle2 size={14} className="check-icon" /> Comité éthique et mission</li>
                </ul>
              </div>
              <p className="service-note-pro">
                <AlertCircle size={14} /> L'IA reste un outil d'aide à la décision, jamais un substitut au conseiller.
              </p>
            </div>
          </div>
        </div>

        {/* NIVEAU 2 */}
        <div className="service-level-pro">
          <div className="level-header level-2-header">
            <div className="level-icon"><Settings size={24} /></div>
            <div className="level-info">
              <span className="level-tag">NIVEAU 2</span>
              <h3>DISPOSITIFS OPÉRATIONNELS</h3>
              <p>Outils & Méthodes</p>
            </div>
          </div>
          
          <div className="service-grid-pro service-grid-3">
            <div className="service-item-pro">
              <div className="service-header-pro">
                <div className="service-icon-pro"><User size={20} /></div>
                <h4>Dispositif VSI (Valoriser Son Identité)</h4>
              </div>
              <div className="service-content-pro">
                <ul className="service-list-check">
                  <li><CheckCircle2 size={14} className="check-icon" /> Diagnostic des compétences visibles et invisibles</li>
                  <li><CheckCircle2 size={14} className="check-icon" /> Travail sur posture et identité professionnelle</li>
                  <li><CheckCircle2 size={14} className="check-icon" /> Développement de la confiance</li>
                  <li><CheckCircle2 size={14} className="check-icon" /> Objectifs personnalisés</li>
                  <li><CheckCircle2 size={14} className="check-icon" /> Consolidation du projet</li>
                </ul>
              </div>
            </div>

            <div className="service-item-pro">
              <div className="service-header-pro">
                <div className="service-icon-pro"><Users size={20} /></div>
                <h4>Ateliers & Programmes collectifs</h4>
              </div>
              <div className="service-content-pro">
                <ul className="service-list-check">
                  <li><CheckCircle2 size={14} className="check-icon" /> Développement des soft skills</li>
                  <li><CheckCircle2 size={14} className="check-icon" /> Simulation d'entretiens</li>
                  <li><CheckCircle2 size={14} className="check-icon" /> Narration professionnelle</li>
                  <li><CheckCircle2 size={14} className="check-icon" /> Travail sur les biais et discriminations</li>
                  <li><CheckCircle2 size={14} className="check-icon" /> Appropriation des outils numériques</li>
                </ul>
              </div>
              <p className="service-note-pro">
                Renforce la cohérence entre compétences, valeurs et environnement professionnel.
              </p>
            </div>

            <div className="service-item-pro">
              <div className="service-header-pro">
                <div className="service-icon-pro"><Map size={20} /></div>
                <h4>Cartographie Interactive</h4>
              </div>
              <div className="service-content-pro">
                <ul className="service-list-check">
                  <li><CheckCircle2 size={14} className="check-icon" /> Visualisation profil ↔ métiers</li>
                  <li><CheckCircle2 size={14} className="check-icon" /> Identification de passerelles</li>
                  <li><CheckCircle2 size={14} className="check-icon" /> Lecture des compétences transférables</li>
                  <li><CheckCircle2 size={14} className="check-icon" /> Projection sectorielle</li>
                  <li><CheckCircle2 size={14} className="check-icon" /> Support d'aide à la décision</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* NIVEAU 3 */}
        <div className="service-level-pro">
          <div className="level-header level-3-header">
            <div className="level-icon"><Globe size={24} /></div>
            <div className="level-info">
              <span className="level-tag">NIVEAU 3</span>
              <h3>IMPACT & ÉCOSYSTÈME</h3>
              <p>Dimension Collective</p>
            </div>
          </div>
          
          <div className="service-grid-pro">
            <div className="service-item-pro service-item-wide">
              <div className="service-header-pro">
                <div className="service-icon-pro"><Network size={20} /></div>
                <h4>Dimension communautaire & Intelligence collective</h4>
              </div>
              <div className="service-content-pro service-content-columns">
                <ul className="service-list-check">
                  <li><CheckCircle2 size={14} className="check-icon" /> Mise en réseau bénéficiaires – entreprises – partenaires</li>
                  <li><CheckCircle2 size={14} className="check-icon" /> Communautés sectorielles</li>
                  <li><CheckCircle2 size={14} className="check-icon" /> Dynamique contributive</li>
                  <li><CheckCircle2 size={14} className="check-icon" /> Valorisation des parcours atypiques</li>
                  <li><CheckCircle2 size={14} className="check-icon" /> Intelligence collective au service des trajectoires</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

      </div>

      <div className="landing-features declic-features hidden">
        <div className="feature">
          <Brain className="feature-icon declic-feature-icon" />
          <h3>Profil Personnalité</h3>
          <p>Analyse de vos motivations profondes et de votre style de fonctionnement</p>
        </div>
        <div className="feature">
          <Award className="feature-icon" />
          <h3>Compétences</h3>
          <p>Identification de vos forces et compétences transversales</p>
        </div>
        <div className="feature">
          <TrendingUp className="feature-icon" />
          <h3>Matching Intelligent</h3>
          <p>Score de compatibilité personnalisé pour chaque métier</p>
        </div>
      </div>

      <footer className="landing-footer" data-testid="landing-footer">
        <p>
          Un projet porté par{' '}
          <a 
            href="https://www.alt-act.eu" 
            target="_blank" 
            rel="noopener noreferrer"
            className="altact-link"
            data-testid="altact-link"
          >
            ALT&ACT
          </a>
        </p>
        <p className="footer-compliance">Conforme au règlement européen sur l'intelligence artificielle (AI Act)</p>
      </footer>
    </div>
  );
};

// ============================================================================
// QUESTIONNAIRE COMPONENT (with Birth Date)
// ============================================================================
// ============================================================================
// DECLIC PRO LOGO COMPACT (pour header)
// ============================================================================
const DeclicProLogoCompact = ({ size = 40 }) => (
  <div className="declic-logo-compact">
    <svg width={size} height={size} viewBox="0 0 120 120">
      <circle cx="60" cy="60" r="50" fill="none" stroke="#FFE4D6" strokeWidth="2"/>
      <circle cx="60" cy="60" r="15" fill="#F97316"/>
      <g>
        <path d="M 60 35 L 62 50 L 70 48 L 60 60" fill="#FBBF24" opacity="0.9"/>
        <path d="M 85 60 L 70 62 L 72 70 L 60 60" fill="#FBBF24" opacity="0.9"/>
        <path d="M 60 85 L 58 70 L 50 72 L 60 60" fill="#FBBF24" opacity="0.9"/>
        <path d="M 35 60 L 50 58 L 48 50 L 60 60" fill="#FBBF24" opacity="0.9"/>
      </g>
      <circle cx="60" cy="20" r="4" fill="#F97316"/>
      <circle cx="90" cy="40" r="4" fill="#F97316"/>
      <circle cx="90" cy="80" r="4" fill="#F97316"/>
      <circle cx="60" cy="100" r="4" fill="#F97316"/>
      <circle cx="30" cy="80" r="4" fill="#F97316"/>
      <circle cx="30" cy="40" r="4" fill="#F97316"/>
    </svg>
    <span className="declic-logo-text">DE'<span className="declic-highlight">CLIC</span> <span className="declic-pro">PRO</span></span>
  </div>
);

const Questionnaire = ({ questions, onComplete, onBack }) => {
  const [currentIndex, setCurrentIndex] = useState(-1); // Start at -1 for birth date step
  const [answers, setAnswers] = useState({});
  const [birthDate, setBirthDate] = useState("");
  const [rankingSelections, setRankingSelections] = useState({}); // For ranking questions
  
  const isAskingBirthDate = currentIndex === -1;
  const currentQuestion = isAskingBirthDate ? null : questions[currentIndex];
  const totalSteps = questions.length + 1; // +1 for birth date
  const progress = ((currentIndex + 2) / totalSteps) * 100;
  const isLastQuestion = currentIndex === questions.length - 1;
  
  // For ranking questions, check if 4 items are selected
  const isRankingQuestion = currentQuestion?.type === 'ranking';
  const currentRanking = rankingSelections[currentQuestion?.id] || [];
  const rankingComplete = isRankingQuestion && currentRanking.length === 4;
  
  const canProceed = isAskingBirthDate 
    ? birthDate.length >= 8 
    : isRankingQuestion 
      ? rankingComplete 
      : answers[currentQuestion?.id];

  const handleAnswer = (value) => {
    setAnswers(prev => ({
      ...prev,
      [currentQuestion.id]: value
    }));
  };

  // Handle ranking selection
  const handleRankingSelect = (choice) => {
    const questionId = currentQuestion.id;
    const currentSelections = rankingSelections[questionId] || [];
    
    // Check if already selected
    const existingIndex = currentSelections.findIndex(s => s.value === choice.value);
    
    if (existingIndex !== -1) {
      // Remove from selection
      const newSelections = currentSelections.filter(s => s.value !== choice.value);
      setRankingSelections(prev => ({
        ...prev,
        [questionId]: newSelections
      }));
    } else if (currentSelections.length < 4) {
      // Add to selection with rank
      const newSelections = [...currentSelections, { ...choice, rank: currentSelections.length + 1 }];
      setRankingSelections(prev => ({
        ...prev,
        [questionId]: newSelections
      }));
      
      // If 4 selections made, save to answers
      if (newSelections.length === 4) {
        const rankedValue = newSelections.map(s => s.value).join(',');
        setAnswers(prev => ({
          ...prev,
          [questionId]: rankedValue
        }));
      }
    }
  };

  // Get rank for a choice (1-4 or null)
  const getRankForChoice = (choiceValue) => {
    const questionId = currentQuestion?.id;
    const selections = rankingSelections[questionId] || [];
    const found = selections.find(s => s.value === choiceValue);
    return found ? found.rank : null;
  };

  const handleNext = () => {
    if (isAskingBirthDate) {
      setCurrentIndex(0);
    } else if (isLastQuestion && canProceed) {
      onComplete(answers, birthDate);
    } else if (canProceed) {
      setCurrentIndex(prev => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (isAskingBirthDate) {
      onBack();
    } else if (currentIndex > 0) {
      setCurrentIndex(prev => prev - 1);
    } else {
      setCurrentIndex(-1);
    }
  };

  // Birth date step
  if (isAskingBirthDate) {
    return (
      <div className="questionnaire-container declic-questionnaire">
        <div className="questionnaire-header">
          <Button variant="ghost" onClick={handlePrevious} data-testid="questionnaire-back-btn" className="declic-back-btn">
            <ChevronLeft size={20} /> Retour
          </Button>
          <DeclicProLogoCompact size={36} />
          <div className="progress-info">
            <span>Étape 1 / {totalSteps}</span>
          </div>
        </div>

        <Progress value={progress} className="questionnaire-progress declic-progress" />

        <Card className="question-card birth-date-card declic-card">
          <CardHeader>
            <div className="birth-date-icon declic-icon">
              <Calendar size={48} />
            </div>
            <CardTitle className="question-text" data-testid="birth-date-question">
              Quelle est votre date de naissance ?
            </CardTitle>
            <CardDescription>
              Cette information nous permet de personnaliser davantage votre analyse et vos recommandations d'actions
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="birth-date-input-container">
              <Input
                type="date"
                value={birthDate}
                onChange={(e) => setBirthDate(e.target.value)}
                className="birth-date-input"
                data-testid="birth-date-input"
                max={new Date().toISOString().split('T')[0]}
              />
            </div>
          </CardContent>
        </Card>

        <div className="questionnaire-actions">
          <Button 
            onClick={handleNext} 
            disabled={!canProceed}
            className="next-button"
            data-testid="questionnaire-next-btn"
          >
            Commencer le questionnaire
            <ChevronRight size={20} />
          </Button>
        </div>
      </div>
    );
  }

  if (!currentQuestion) return null;

  // Déterminer le type de question (visual, visual_quad, text_choice, ranking ou legacy)
  const questionType = currentQuestion.type || 'legacy';
  const isVisual = questionType === 'visual' || questionType === 'visual_quad';
  const isTextChoice = questionType === 'text_choice';
  const isRanking = questionType === 'ranking';
  const choices = currentQuestion.choices || currentQuestion.options || [];
  const hasImages = choices.length > 0 && choices[0].image;

  return (
    <div className="questionnaire-container declic-questionnaire">
      <div className="questionnaire-header">
        <Button variant="ghost" onClick={handlePrevious} data-testid="questionnaire-back-btn" className="declic-back-btn">
          <ChevronLeft size={20} /> Retour
        </Button>
        <DeclicProLogoCompact size={36} />
        <div className="progress-info">
          <span>Question {currentIndex + 1} / {questions.length}</span>
        </div>
      </div>

      <Progress value={progress} className="questionnaire-progress declic-progress" />

      <Card className="question-card declic-card">
        <CardHeader>
          <CardTitle className="question-text visual-question-text" data-testid="question-text">
            {currentQuestion.question || currentQuestion.text}
          </CardTitle>
          {currentQuestion.instruction && (
            <CardDescription className="ranking-instruction">
              {currentQuestion.instruction}
            </CardDescription>
          )}
        </CardHeader>
        <CardContent>
          {/* RANKING FORMAT - Choix avec priorisation 1-4 */}
          {isRanking && (
            <div className={`ranking-choices ${hasImages ? 'ranking-with-images' : 'ranking-text-only'}`}>
              <div className="ranking-progress-indicator">
                <span className={currentRanking.length >= 1 ? 'filled' : ''}>1</span>
                <span className={currentRanking.length >= 2 ? 'filled' : ''}>2</span>
                <span className={currentRanking.length >= 3 ? 'filled' : ''}>3</span>
                <span className={currentRanking.length >= 4 ? 'filled' : ''}>4</span>
              </div>
              <p className="ranking-help-text">
                {currentRanking.length < 4 
                  ? `Sélectionnez votre choix n°${currentRanking.length + 1} (${4 - currentRanking.length} restant${4 - currentRanking.length > 1 ? 's' : ''})` 
                  : '✓ Classement complet ! Cliquez sur un choix pour le retirer.'}
              </p>
              <div className={`ranking-grid ${hasImages ? 'ranking-grid-images' : 'ranking-grid-text'}`}>
                {choices.map((choice) => {
                  const rank = getRankForChoice(choice.value);
                  const isSelected = rank !== null;
                  return (
                    <button
                      key={choice.id}
                      className={`ranking-choice-card ${isSelected ? 'selected' : ''} ${!isSelected && currentRanking.length >= 4 ? 'disabled' : ''}`}
                      onClick={() => handleRankingSelect(choice)}
                      data-testid={`ranking-choice-${choice.id}`}
                      disabled={!isSelected && currentRanking.length >= 4}
                    >
                      {isSelected && (
                        <div className="ranking-badge">
                          <span>{rank}</span>
                        </div>
                      )}
                      {hasImages && (
                        <div className="ranking-choice-image">
                          <img 
                            src={choice.image} 
                            alt={choice.alt || choice.label}
                            loading="lazy"
                          />
                        </div>
                      )}
                      <div className="ranking-choice-label">
                        {choice.label}
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* VISUAL FORMAT - Images avec choix binaires ou quadruples */}
          {isVisual && (
            <div className={`visual-choices ${questionType === 'visual_quad' ? 'quad-grid' : 'binary-grid'}`}>
              {choices.map((choice) => (
                <button
                  key={choice.id}
                  className={`visual-choice-card ${answers[currentQuestion.id] === choice.value ? 'selected' : ''}`}
                  onClick={() => handleAnswer(choice.value)}
                  data-testid={`visual-choice-${choice.id}`}
                >
                  <div className="visual-choice-image">
                    <img 
                      src={choice.image} 
                      alt={choice.alt || choice.label}
                      loading="lazy"
                    />
                  </div>
                  <div className="visual-choice-label">
                    {choice.label}
                  </div>
                  {answers[currentQuestion.id] === choice.value && (
                    <div className="visual-choice-check">
                      <CheckCircle2 size={24} />
                    </div>
                  )}
                </button>
              ))}
            </div>
          )}

          {/* TEXT CHOICE FORMAT - Choix texte multiples (Ennéagramme) */}
          {isTextChoice && (
            <div className="text-choices-grid">
              {choices.map((choice) => (
                <button
                  key={choice.id}
                  className={`text-choice-card ${answers[currentQuestion.id] === choice.value ? 'selected' : ''}`}
                  onClick={() => handleAnswer(choice.value)}
                  data-testid={`text-choice-${choice.id}`}
                >
                  <span className="text-choice-label">{choice.label}</span>
                  {answers[currentQuestion.id] === choice.value && (
                    <CheckCircle2 size={18} className="text-choice-check" />
                  )}
                </button>
              ))}
            </div>
          )}

          {/* LEGACY FORMAT - Radio buttons */}
          {!isVisual && !isTextChoice && !isRanking && (
            <RadioGroup
              value={answers[currentQuestion.id] || ""}
              onValueChange={handleAnswer}
              className="options-list"
            >
              {choices.map((option) => (
                <div 
                  key={option.id} 
                  className={`option-item declic-option ${answers[currentQuestion.id] === option.value ? 'selected' : ''}`}
                >
                  <RadioGroupItem value={option.value} id={option.id} data-testid={`option-${option.id}`} />
                  <Label htmlFor={option.id} className="option-label">
                    {option.text || option.label}
                  </Label>
                </div>
              ))}
            </RadioGroup>
          )}
        </CardContent>
      </Card>

      <div className="questionnaire-actions">
        <Button 
          onClick={handleNext} 
          disabled={!canProceed}
          className="next-button declic-button"
          data-testid="questionnaire-next-btn"
        >
          {isLastQuestion ? "Voir mes résultats" : "Suivant"}
          <ChevronRight size={20} />
        </Button>
      </div>
    </div>
  );
};

// ============================================================================
// MICRO-ACTIONS COMPONENT (Life Path based) - Simplified without timebox
// ============================================================================
const MicroActions = ({ lifePath }) => {
  if (!lifePath || !lifePath.micro_actions) return null;

  return (
    <Card className="micro-actions-card">
      <CardHeader>
        <CardTitle className="micro-actions-title">
          <TrendingUp size={24} /> Axes de Développement
        </CardTitle>
        <CardDescription>
          Développez vos soft skills avec ces pistes concrètes
        </CardDescription>
      </CardHeader>
      <CardContent>
        {/* Strengths & Watchouts */}
        <div className="life-path-insights">
          <div className="insight-row">
            <div className="insight-block strengths">
              <h5><CheckCircle2 size={16} /> Vos forces naturelles</h5>
              <div className="insight-badges">
                {lifePath.strengths?.slice(0, 4).map((strength, idx) => (
                  <Badge key={idx} variant="outline" className="strength-badge">{strength}</Badge>
                ))}
              </div>
            </div>
            <div className="insight-block watchouts">
              <h5><AlertTriangle size={16} /> Points de vigilance</h5>
              <div className="insight-badges">
                {lifePath.watchouts?.slice(0, 3).map((watchout, idx) => (
                  <Badge key={idx} variant="secondary" className="watchout-badge">{watchout}</Badge>
                ))}
              </div>
            </div>
          </div>
        </div>

        <Separator className="micro-actions-separator" />

        {/* Soft Skills Development Axes */}
        <div className="micro-actions-list">
          <h5><Lightbulb size={18} /> Pistes pour progresser</h5>
          {lifePath.micro_actions.map((action, idx) => (
            <div key={idx} className="micro-action-item">
              <Badge className="focus-badge">{action.focus}</Badge>
              <p className="micro-action-text">{action.action}</p>
            </div>
          ))}
        </div>

        {/* Work Preferences */}
        {lifePath.work_preferences && (
          <div className="work-preferences">
            <h5><Briefcase size={16} /> Environnements favorables</h5>
            <div className="preferences-list">
              {lifePath.work_preferences.map((pref, idx) => (
                <span key={idx} className="preference-item">
                  <ArrowRight size={14} /> {pref}
                </span>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// ============================================================================
// CROSS ANALYSIS - Synergies & Equilibres
// ============================================================================
const CrossAnalysisDisplay = ({ crossAnalysis, lifePath }) => {
  if (!crossAnalysis || !crossAnalysis.has_cross_analysis) return null;

  const { synergy_disc, synergy_ennea, tension, integration_insight } = crossAnalysis;

  return (
    <Card className="cross-analysis-card" data-testid="cross-analysis-section">
      <CardHeader>
        <CardTitle className="cross-analysis-title">
          <Layers size={24} /> Votre Profil Croisé
        </CardTitle>
        <CardDescription>
          Votre profil unique révèle des synergies puissantes entre vos différentes dimensions
        </CardDescription>
      </CardHeader>
      <CardContent>
        {/* Synergies Section */}
        <div className="cross-section synergies-section">
          <div className="cross-section-header">
            <Sparkles size={20} className="synergy-icon" />
            <h4>Vos Synergies</h4>
          </div>
          
          <div className="synergy-cards">
            {synergy_disc && (
              <div className="synergy-card">
                <div className="synergy-badge">
                  <Zap size={16} /> Style & Dynamique
                </div>
                <p className="synergy-text">{synergy_disc}</p>
              </div>
            )}
            
            {synergy_ennea && (
              <div className="synergy-card">
                <div className="synergy-badge">
                  <Heart size={16} /> Moteur & Identité
                </div>
                <p className="synergy-text">{synergy_ennea}</p>
              </div>
            )}
          </div>
        </div>

        {/* Integration Insight */}
        {integration_insight && (
          <div className="integration-insight">
            <div className="insight-glow">
              <Star size={20} />
            </div>
            <p className="insight-text">{integration_insight}</p>
          </div>
        )}

        {/* Tension Section (Growth Opportunity) */}
        {tension && (
          <div className="cross-section tension-section">
            <div className="cross-section-header">
              <TrendingUp size={20} className="growth-icon" />
              <h4>Équilibre à cultiver</h4>
            </div>
            <div className="tension-card">
              <p className="tension-text">{tension}</p>
            </div>
          </div>
        )}

        {/* Thematic Label - without technical terms */}
        {lifePath && lifePath.label && (
          <div className="life-path-context">
            <div className="context-label">
              <Compass size={14} />
              <span>Votre thématique : <strong>{lifePath.label}</strong></span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};



// ============================================================================
// JOB SEARCH INPUT
// ============================================================================
const JobSearchInput = ({ onSearch, onBack }) => {
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (query.trim()) {
      setIsLoading(true);
      await onSearch(query.trim());
      setIsLoading(false);
    }
  };

  return (
    <div className="job-search-container">
      <Button variant="ghost" onClick={onBack} className="back-btn" data-testid="job-search-back-btn">
        <ChevronLeft size={20} /> Retour
      </Button>
      
      <Card className="job-search-card">
        <CardHeader>
          <div className="search-icon">
            <Search size={48} />
          </div>
          <CardTitle>Quel métier vous intéresse ?</CardTitle>
          <CardDescription>
            Entrez le nom du métier que vous visez pour découvrir votre compatibilité
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="search-form">
            <Input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ex: Développeur web, Infirmier, Commercial..."
              className="search-input"
              data-testid="job-search-input"
            />
            <Button 
              type="submit" 
              disabled={!query.trim() || isLoading}
              className="search-button"
              data-testid="job-search-submit-btn"
            >
              {isLoading ? "Analyse en cours..." : "Analyser la compatibilité"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

// ============================================================================
// SKILLS ARCHEOLOGY - Structure Tripartite CK1 : Cognition / Conation / Affection
// ============================================================================
const SkillsArcheology = ({ vertus, competences }) => {
  if (!vertus) return null;

  // Structure tripartite basée sur le tableau CK1 - Archéologie des Compétences
  // Cognition = Ce qu'on pense/sait | Conation = Ce qu'on fait/veut | Affection = Ce qu'on ressent
  
  const tripartiteStructure = [
    {
      id: 'cognition',
      label: 'Cognition',
      subtitle: 'Ce que je pense & sais',
      description: 'Forces cognitives qui favorisent l\'acquisition et l\'usage de la connaissance',
      icon: Brain,
      color: '#4338ca',
      gradient: 'linear-gradient(135deg, #4338ca 0%, #6366f1 100%)',
      items: vertus.cognition?.slice(0, 6) || ['Connaissance', 'Curiosité', 'Pensée critique', 'Lucidité']
    },
    {
      id: 'conation',
      label: 'Conation',
      subtitle: 'Ce que je fais & veux',
      description: 'Forces émotionnelles impliquant l\'exercice de la volonté pour atteindre ses buts',
      icon: Flame,
      color: '#dc2626',
      gradient: 'linear-gradient(135deg, #dc2626 0%, #f97316 100%)',
      items: vertus.conation?.slice(0, 6) || ['Détermination', 'Persévérance', 'Volonté', 'Initiative']
    },
    {
      id: 'affection',
      label: 'Affection',
      subtitle: 'Ce que je ressens & partage',
      description: 'Forces interpersonnelles pour tendre vers les autres et leur venir en aide',
      icon: Heart,
      color: '#ec4899',
      gradient: 'linear-gradient(135deg, #ec4899 0%, #f472b6 100%)',
      items: vertus.affection?.slice(0, 6) || ['Empathie', 'Bienveillance', 'Compassion', 'Solidarité']
    }
  ];

  // Sections complémentaires (Valeurs, Forces, Savoirs-être)
  const complementarySections = [
    {
      id: 'valeurs',
      label: 'Valeurs Universelles',
      subtitle: 'Schwartz',
      icon: Gem,
      color: '#0891b2',
      gradient: 'linear-gradient(135deg, #0891b2 0%, #06b6d4 100%)',
      items: vertus.valeurs_schwartz?.slice(0, 4) || []
    },
    {
      id: 'forces',
      label: 'Forces de Caractère',
      subtitle: 'Seligman & Peterson',
      icon: Award,
      color: '#f59e0b',
      gradient: 'linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)',
      items: vertus.forces?.slice(0, 5) || []
    },
    {
      id: 'savoirs',
      label: 'Savoirs-être Pro',
      subtitle: 'France Travail',
      icon: BookOpen,
      color: '#059669',
      gradient: 'linear-gradient(135deg, #059669 0%, #10b981 100%)',
      items: vertus.savoirs_etre?.slice(0, 4) || []
    }
  ];

  return (
    <Card className="archeology-card" data-testid="skills-archeology">
      <CardHeader>
        <CardTitle className="archeology-title">
          <Layers size={24} /> Votre Identité & Compétences
        </CardTitle>
        <CardDescription className="archeology-description">
          <span className="tooltip-wrapper">
            <span className="tooltip-trigger">
              Generic Skills Component Approach
              <Info size={14} className="info-icon" />
            </span>
            <span className="tooltip-content">
              <strong>Generic Skills Component Approach</strong>
              <br /><br />
              La Generic Skills Component Approach (approche par composantes des compétences génériques) est un cadre d'analyse qui consiste à décomposer les compétences transversales en éléments observables, mesurables et transférables.
              <br /><br />
              Plutôt que de considérer une compétence comme un bloc global (ex. : "esprit d'équipe" ou "communication"), cette approche identifie ses composantes spécifiques : connaissances mobilisées, habiletés comportementales, attitudes, capacités cognitives, régulation émotionnelle, etc.
              <br /><br />
              Elle est particulièrement utile en orientation, en formation et en insertion professionnelle, car elle permet :
              <br />• de rendre visibles des compétences acquises dans des contextes variés (emploi, bénévolat, vie personnelle)
              <br />• d'objectiver les écarts entre un profil et un métier visé
              <br />• de construire des plans de développement ciblés et progressifs
              <br /><br />
              <em>En résumé, cette approche transforme les "soft skills" en leviers concrets d'employabilité, en les rendant analytiques, structurées et actionnables.</em>
              <br /><br />
              <span className="tooltip-authors">Chercheurs et auteurs : Jeremy Lamri et Todd Lubart, chercheurs au LaPEA (Université Paris Cité & Université Gustave Eiffel)</span>
            </span>
          </span>
          {' × '}
          <span className="tooltip-wrapper">
            <span className="tooltip-trigger">
              Archéologie des Compétences
              <Info size={14} className="info-icon" />
            </span>
            <span className="tooltip-content">
              <strong>Archéologie des Compétences</strong>
              <br /><br />
              L'approche d'archéologie des compétences appliquée à l'orientation et à l'insertion professionnelle vise à analyser un parcours comme un ensemble cohérent d'expériences révélant des compétences visibles, transférables et identitaires. Elle ne se limite pas à l'inventaire des savoir-faire, mais cherche à mettre au jour les constantes comportementales, les motivations profondes et les valeurs structurantes qui orientent durablement les choix professionnels.
              <br /><br />
              Cette démarche s'inscrit notamment dans une articulation entre axiologie (clarification des valeurs opérantes), phénoménologie (prise en compte de l'expérience vécue et du sens donné par la personne) et constructivisme (co-construction progressive du projet à partir des représentations et apprentissages).
              <br /><br />
              <em>Elle permet ainsi de passer d'une logique de placement à une logique d'alignement, favorisant des parcours plus cohérents, soutenables et porteurs de sens.</em>
              <br /><br />
              <span className="tooltip-authors">Chitrasen LUXIMON, Fondateur Alt&Act. Expert en transitions professionnelles.</span>
            </span>
          </span>
        </CardDescription>
      </CardHeader>
      <CardContent>
        {/* Structure Tripartite Principale */}
        <div className="tripartite-grid">
          {tripartiteStructure.map((section) => {
            const Icon = section.icon;
            return (
              <div 
                key={section.id} 
                className={`tripartite-section tripartite-${section.id}`}
                data-testid={`section-${section.id}`}
              >
                <div className="tripartite-header" style={{ background: section.gradient }}>
                  <Icon size={28} className="tripartite-icon" />
                  <div className="tripartite-title-block">
                    <h3>{section.label}</h3>
                    <span className="tripartite-subtitle">{section.subtitle}</span>
                  </div>
                </div>
                <p className="tripartite-description">{section.description}</p>
                <div className="tripartite-items">
                  {section.items.map((item, idx) => (
                    <Badge 
                      key={idx} 
                      className="tripartite-badge"
                      style={{ 
                        borderColor: section.color, 
                        color: section.color,
                        backgroundColor: `${section.color}10`
                      }}
                    >
                      {item}
                    </Badge>
                  ))}
                </div>
              </div>
            );
          })}
        </div>

        <Separator className="archeology-separator" />

        {/* Sections Complémentaires - Design amélioré */}
        <div className="complementary-grid">
          {complementarySections.map((section) => {
            const Icon = section.icon;
            return (
              <div 
                key={section.id} 
                className="complementary-section-v2"
              >
                <div className="complementary-header-v2" style={{ background: section.gradient }}>
                  <Icon size={22} className="complementary-icon" />
                  <div className="complementary-title-block">
                    <h4>{section.label}</h4>
                    <span className="complementary-subtitle">{section.subtitle}</span>
                  </div>
                </div>
                <div className="complementary-items-v2">
                  {section.items.map((item, idx) => (
                    <Badge 
                      key={idx} 
                      className="complementary-badge-v2"
                      style={{ 
                        borderColor: section.color, 
                        color: section.color,
                        backgroundColor: `${section.color}10`
                      }}
                    >
                      {item}
                    </Badge>
                  ))}
                </div>
              </div>
            );
          })}
        </div>

        {/* Bandeau Vertu Dominante */}
        <div className="vertu-banner" data-testid="vertu-banner">
          <Crown size={20} className="vertu-banner-icon" />
          <span className="vertu-banner-label">Vertu dominante :</span>
          <span className="vertu-banner-value">{vertus.name}</span>
        </div>
      </CardContent>
    </Card>
  );
};

// ============================================================================
// TRIPARTITE RADAR - Visualisation Interactive Cognition/Conation/Affection + DISC + Archéologie
// ============================================================================
const TripartiteRadar = ({ vertus, lifePath, profileSummary }) => {
  if (!vertus) return null;

  // Calculer les scores basés sur le TYPE de vertu (chaque vertu a une dominance différente)
  const getVertuScores = (vertuName) => {
    const vertuType = vertuName?.toLowerCase() || '';
    
    if (vertuType.includes('sagesse')) {
      return { cognition: 95, conation: 65, affection: 70 };
    } else if (vertuType.includes('courage')) {
      return { cognition: 70, conation: 95, affection: 60 };
    } else if (vertuType.includes('humanit')) {
      return { cognition: 60, conation: 70, affection: 95 };
    } else if (vertuType.includes('justice')) {
      return { cognition: 85, conation: 85, affection: 65 };
    } else if (vertuType.includes('tempér') || vertuType.includes('temper')) {
      return { cognition: 70, conation: 85, affection: 80 };
    } else if (vertuType.includes('transcend')) {
      return { cognition: 80, conation: 65, affection: 90 };
    }
    return { cognition: 75, conation: 75, affection: 75 };
  };

  const scores = getVertuScores(vertus.name);

  // Récupérer les scores DISC du profil
  const discScores = profileSummary?.disc_scores || { D: 1, I: 1, S: 1, C: 1 };
  const maxDisc = Math.max(...Object.values(discScores), 1);
  
  // Normaliser les scores DISC sur 100
  const normalizedDisc = {
    D: Math.round((discScores.D / maxDisc) * 100),
    I: Math.round((discScores.I / maxDisc) * 100),
    S: Math.round((discScores.S / maxDisc) * 100),
    C: Math.round((discScores.C / maxDisc) * 100)
  };

  // Données pour le radar tripartite
  const tripartiteData = [
    { dimension: 'Cognition', score: scores.cognition, fullMark: 100 },
    { dimension: 'Conation', score: scores.conation, fullMark: 100 },
    { dimension: 'Affection', score: scores.affection, fullMark: 100 }
  ];

  // Données pour le radar DISC
  const discData = [
    { dimension: 'D', fullName: 'Dominance', score: normalizedDisc.D, fullMark: 100, description: 'Action & Résultats' },
    { dimension: 'I', fullName: 'Influence', score: normalizedDisc.I, fullMark: 100, description: 'Relations & Communication' },
    { dimension: 'S', fullName: 'Stabilité', score: normalizedDisc.S, fullMark: 100, description: 'Coopération & Fiabilité' },
    { dimension: 'C', fullName: 'Conformité', score: normalizedDisc.C, fullMark: 100, description: 'Précision & Analyse' }
  ];

  // Données pour le radar Archéologie des Compétences
  const archeologyData = [
    { 
      dimension: 'Forces', 
      fullName: 'Forces de Caractère', 
      score: Math.min((vertus.forces?.length || 0) * 20, 100),
      fullMark: 100,
      description: 'Seligman & Peterson'
    },
    { 
      dimension: 'Valeurs', 
      fullName: 'Valeurs Universelles', 
      score: Math.min((vertus.valeurs_schwartz?.length || 0) * 25, 100),
      fullMark: 100,
      description: 'Schwartz'
    },
    { 
      dimension: 'Savoirs', 
      fullName: 'Savoirs-être Pro', 
      score: Math.min((vertus.savoirs_etre?.length || 0) * 30, 100),
      fullMark: 100,
      description: 'France Travail'
    },
    { 
      dimension: 'CPS', 
      fullName: 'Compétences Psycho-Sociales', 
      score: Math.min((vertus.competences_oms?.length || 0) * 30, 100),
      fullMark: 100,
      description: 'Life Skills'
    },
    { 
      dimension: 'Qualités', 
      fullName: 'Qualités Humaines', 
      score: Math.min((vertus.qualites_humaines?.length || 0) * 15, 100),
      fullMark: 100,
      description: 'Soft Skills'
    }
  ];

  // Tooltip personnalisé
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="radar-tooltip">
          <p className="radar-tooltip-title">{data.fullName || data.dimension}</p>
          {data.description && <p className="radar-tooltip-desc">{data.description}</p>}
          <p className="radar-tooltip-score">{data.score}%</p>
        </div>
      );
    }
    return null;
  };

  return (
    <Card className="radar-card" data-testid="tripartite-radar">
      <CardHeader>
        <CardTitle className="radar-title">
          <Target size={24} /> Profil Comportemental
        </CardTitle>
        <CardDescription>
          Tripartite × DISC × Archéologie des Compétences
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="radar-triple-container">
          {/* Radar Tripartite */}
          <div className="radar-section">
            <h4 className="radar-section-title">
              <Brain size={18} /> Tripartite
            </h4>
            <ResponsiveContainer width="100%" height={240}>
              <RadarChart cx="50%" cy="50%" outerRadius="70%" data={tripartiteData}>
                <PolarGrid stroke="#cbd5e1" strokeWidth={1} />
                <PolarAngleAxis 
                  dataKey="dimension" 
                  tick={{ fill: '#1e293b', fontSize: 11, fontWeight: 600 }}
                  tickLine={false}
                />
                <PolarRadiusAxis angle={90} domain={[0, 100]} tick={false} axisLine={false} />
                <Radar
                  name="Tripartite"
                  dataKey="score"
                  stroke="#6366f1"
                  fill="url(#tripartiteGradient)"
                  fillOpacity={0.6}
                  strokeWidth={2}
                />
                <Tooltip content={<CustomTooltip />} />
                <defs>
                  <linearGradient id="tripartiteGradient" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stopColor="#4338ca" stopOpacity={0.8}/>
                    <stop offset="50%" stopColor="#dc2626" stopOpacity={0.6}/>
                    <stop offset="100%" stopColor="#ec4899" stopOpacity={0.8}/>
                  </linearGradient>
                </defs>
              </RadarChart>
            </ResponsiveContainer>
          </div>

          {/* Radar DISC */}
          <div className="radar-section">
            <h4 className="radar-section-title">
              <Users size={18} /> DISC
            </h4>
            <ResponsiveContainer width="100%" height={240}>
              <RadarChart cx="50%" cy="50%" outerRadius="70%" data={discData}>
                <PolarGrid stroke="#cbd5e1" strokeWidth={1} />
                <PolarAngleAxis 
                  dataKey="dimension" 
                  tick={{ fill: '#1e293b', fontSize: 12, fontWeight: 700 }}
                  tickLine={false}
                />
                <PolarRadiusAxis angle={90} domain={[0, 100]} tick={false} axisLine={false} />
                <Radar
                  name="DISC"
                  dataKey="score"
                  stroke="#059669"
                  fill="url(#discGradient)"
                  fillOpacity={0.6}
                  strokeWidth={2}
                />
                <Tooltip content={<CustomTooltip />} />
                <defs>
                  <linearGradient id="discGradient" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stopColor="#dc2626" stopOpacity={0.8}/>
                    <stop offset="33%" stopColor="#f59e0b" stopOpacity={0.7}/>
                    <stop offset="66%" stopColor="#059669" stopOpacity={0.7}/>
                    <stop offset="100%" stopColor="#0891b2" stopOpacity={0.8}/>
                  </linearGradient>
                </defs>
              </RadarChart>
            </ResponsiveContainer>
          </div>

          {/* Radar Archéologie */}
          <div className="radar-section">
            <h4 className="radar-section-title">
              <Layers size={18} /> Archéologie
            </h4>
            <ResponsiveContainer width="100%" height={240}>
              <RadarChart cx="50%" cy="50%" outerRadius="65%" data={archeologyData}>
                <PolarGrid stroke="#cbd5e1" strokeWidth={1} />
                <PolarAngleAxis 
                  dataKey="dimension" 
                  tick={{ fill: '#1e293b', fontSize: 10, fontWeight: 600 }}
                  tickLine={false}
                />
                <PolarRadiusAxis angle={90} domain={[0, 100]} tick={false} axisLine={false} />
                <Radar
                  name="Archéologie"
                  dataKey="score"
                  stroke="#7c3aed"
                  fill="url(#archeologyGradient)"
                  fillOpacity={0.6}
                  strokeWidth={2}
                />
                <Tooltip content={<CustomTooltip />} />
                <defs>
                  <linearGradient id="archeologyGradient" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stopColor="#7c3aed" stopOpacity={0.8}/>
                    <stop offset="50%" stopColor="#0891b2" stopOpacity={0.7}/>
                    <stop offset="100%" stopColor="#059669" stopOpacity={0.8}/>
                  </linearGradient>
                </defs>
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Légendes */}
        <div className="radar-legends">
          <div className="disc-legend">
            <div className="disc-legend-item" style={{ borderColor: '#dc2626' }}>
              <span className="disc-letter" style={{ color: '#dc2626' }}>D</span>
              <span>Dominance</span>
            </div>
            <div className="disc-legend-item" style={{ borderColor: '#f59e0b' }}>
              <span className="disc-letter" style={{ color: '#f59e0b' }}>I</span>
              <span>Influence</span>
            </div>
            <div className="disc-legend-item" style={{ borderColor: '#059669' }}>
              <span className="disc-letter" style={{ color: '#059669' }}>S</span>
              <span>Stabilité</span>
            </div>
            <div className="disc-legend-item" style={{ borderColor: '#0891b2' }}>
              <span className="disc-letter" style={{ color: '#0891b2' }}>C</span>
              <span>Conformité</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// ============================================================================
// BOUSSOLE DE FONCTIONNEMENT - Préférences Cognitives
// ============================================================================
const FunctioningCompass = ({ compass }) => {
  if (!compass || !compass.axes) return null;

  const getAxisColor = (axisName) => {
    const colors = {
      "Source d'énergie": "#f59e0b",
      "Traitement de l'information": "#6366f1",
      "Mode de décision": "#10b981",
      "Rapport à l'organisation": "#ec4899"
    };
    return colors[axisName] || "#6366f1";
  };

  return (
    <Card className="compass-card" data-testid="functioning-compass">
      <CardHeader>
        <CardTitle className="compass-title">
          <Compass size={24} /> Boussole de Fonctionnement
        </CardTitle>
        <CardDescription>
          Vos préférences cognitives naturelles (4 axes)
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="compass-summary">
          <p>{compass.summary}</p>
        </div>
        
        <div className="compass-axes">
          {compass.axes.map((axis, idx) => (
            <div key={idx} className="compass-axis">
              <div className="axis-header">
                <span className="axis-name" style={{ color: getAxisColor(axis.name) }}>
                  {axis.name}
                </span>
                <span className="axis-dominant">{axis.dominant === axis.pole_a.code ? axis.pole_a.label : axis.pole_b.label}</span>
              </div>
              
              <div className="axis-poles">
                <div className={`pole pole-a ${axis.dominant === axis.pole_a.code ? 'active' : ''}`}>
                  <span className="pole-label">{axis.pole_a.label}</span>
                  <span className="pole-code">{axis.pole_a.code}</span>
                </div>
                
                <div className="axis-bar">
                  <div 
                    className="axis-indicator" 
                    style={{ 
                      left: axis.dominant === axis.pole_a.code ? '25%' : '75%',
                      backgroundColor: getAxisColor(axis.name)
                    }}
                  />
                </div>
                
                <div className={`pole pole-b ${axis.dominant === axis.pole_b.code ? 'active' : ''}`}>
                  <span className="pole-label">{axis.pole_b.label}</span>
                  <span className="pole-code">{axis.pole_b.code}</span>
                </div>
              </div>
              
              <p className="axis-insight">{axis.insight}</p>
            </div>
          ))}
        </div>
        
        <div className="compass-profile-badge">
          <span className="profile-label">Profil global :</span>
          <span className="profile-code">{compass.global_profile}</span>
        </div>
      </CardContent>
    </Card>
  );
};

// ============================================================================
// ANALYSE INTÉGRÉE - 3 Niveaux de Lecture
// ============================================================================
const IntegratedAnalysis = ({ analysis }) => {
  if (!analysis) return null;

  const { niveau_1_preuves, niveau_2_fonctionnement, niveau_3_regulation, synthese } = analysis;

  return (
    <Card className="integrated-analysis-card" data-testid="integrated-analysis">
      <CardHeader>
        <CardTitle className="integrated-title">
          <Layers size={24} /> Analyse Intégrée
        </CardTitle>
        <CardDescription>
          3 niveaux de lecture : Preuves → Fonctionnement → Régulation
        </CardDescription>
      </CardHeader>
      <CardContent>
        {/* Niveau 1: Preuves */}
        <div className="analysis-level level-1">
          <div className="level-header">
            <span className="level-number">1</span>
            <div className="level-title-block">
              <h4>{niveau_1_preuves?.titre}</h4>
              <p className="level-description">{niveau_1_preuves?.description}</p>
            </div>
          </div>
          <div className="level-content">
            <div className="level-grid">
              <div className="level-item">
                <span className="item-label">Compétences prouvées</span>
                <div className="item-tags">
                  {niveau_1_preuves?.elements?.competences_prouvees?.map((c, i) => (
                    <span key={i} className="tag tag-competence">{c}</span>
                  ))}
                </div>
              </div>
              <div className="level-item">
                <span className="item-label">Forces clés</span>
                <div className="item-tags">
                  {niveau_1_preuves?.elements?.forces_cles?.map((f, i) => (
                    <span key={i} className="tag tag-force">{f}</span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Niveau 2: Fonctionnement */}
        <div className="analysis-level level-2">
          <div className="level-header">
            <span className="level-number">2</span>
            <div className="level-title-block">
              <h4>{niveau_2_fonctionnement?.titre}</h4>
              <p className="level-description">{niveau_2_fonctionnement?.description}</p>
            </div>
          </div>
          <div className="level-content">
            <div className="style-card">
              <div className="style-header">{niveau_2_fonctionnement?.elements?.style_disc?.style}</div>
              <p className="style-contribution">{niveau_2_fonctionnement?.elements?.style_disc?.contribution}</p>
              <div className="style-env">
                <span className="env-label">Environnement favorable :</span>
                <div className="env-tags">
                  {niveau_2_fonctionnement?.elements?.environnement_favorable?.map((e, i) => (
                    <span key={i} className="tag tag-env">{e}</span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Niveau 3: Régulation */}
        <div className="analysis-level level-3">
          <div className="level-header">
            <span className="level-number">3</span>
            <div className="level-title-block">
              <h4>{niveau_3_regulation?.titre}</h4>
              <p className="level-description">{niveau_3_regulation?.description}</p>
            </div>
          </div>
          <div className="level-content">
            <div className="regulation-grid">
              <div className="regulation-item">
                <span className="reg-label">🎯 Moteur interne</span>
                <p>{niveau_3_regulation?.elements?.moteur_ennea?.moteur}</p>
              </div>
              <div className="regulation-item">
                <span className="reg-label">🚀 Leviers de croissance</span>
                <ul>
                  {niveau_3_regulation?.elements?.leviers_croissance?.slice(0, 2).map((l, i) => (
                    <li key={i}>{l}</li>
                  ))}
                </ul>
              </div>
              <div className="regulation-item">
                <span className="reg-label">⚠️ Signaux de stress</span>
                <ul>
                  {niveau_3_regulation?.elements?.signaux_stress?.slice(0, 2).map((s, i) => (
                    <li key={i}>{s}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Synthèse */}
        <div className="analysis-synthesis">
          <p>{synthese}</p>
        </div>
      </CardContent>
    </Card>
  );
};

// ============================================================================
// PROFESSIONAL ID CARD - Carte d'Identité Professionnelle (4 piliers)
// ============================================================================
const ProfessionalIdCard = ({ vertus, competences, narrative, lifePath, jobInfo }) => {
  const cardRef = useRef(null);
  const [isDownloading, setIsDownloading] = useState(false);
  
  if (!vertus) return null;

  // Extract hard skills critiques from job if available
  const hardSkillsCritiques = jobInfo?.hard_skills_essentiels
    ?.filter(s => s.importance === 'critique')
    ?.map(s => s.nom)
    ?.slice(0, 3) || [];

  // Extract data for each pillar
  const identitePersonnelle = {
    qualites: vertus.qualites_humaines?.slice(0, 3) || [],
    valeurs: vertus.valeurs_schwartz?.slice(0, 3) || [],
    vertus: vertus.forces?.slice(0, 2) || [],
    unique: vertus.name || ''
  };

  const identiteProfessionnelle = {
    competences: competences?.slice(0, 3) || [],
    savoirEtre: vertus.savoirs_etre?.slice(0, 3) || [],
    savoirFaire: vertus.competences_oms?.slice(0, 2) || [],
    hardSkills: hardSkillsCritiques
  };

  const identiteSociale = {
    roles: ['Contributeur', 'Collaborateur'],
    impact: lifePath?.work_preferences?.slice(0, 2) || []
  };

  const identiteProfonde = {
    sens: lifePath?.label || '',
    mission: lifePath?.strengths?.slice(0, 2) || [],
    vision: vertus.valeurs_schwartz?.[0] || ''
  };

  const handleDownloadPdf = async () => {
    if (!cardRef.current || isDownloading) return;
    
    setIsDownloading(true);
    try {
      const cardElement = cardRef.current;
      
      // Generate canvas from the card element
      const canvas = await html2canvas(cardElement, {
        scale: 2,
        useCORS: true,
        backgroundColor: '#ffffff',
        logging: false
      });
      
      // Add "COPY INUTILISABLE" watermark diagonally
      const ctx = canvas.getContext('2d');
      ctx.save();
      
      // Configure watermark text style - RED and BOLD
      ctx.globalAlpha = 0.35;
      ctx.fillStyle = '#ef4444';
      ctx.font = 'bold 100px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      
      // Rotate and position text diagonally across the card
      ctx.translate(canvas.width / 2, canvas.height / 2);
      ctx.rotate(-35 * Math.PI / 180);
      
      // Draw the watermark text - single line, all caps
      ctx.fillText('COPY INUTILISABLE', 0, 0);
      
      ctx.restore();
      
      // Create PDF
      const imgWidth = 210; // A4 width in mm
      const imgHeight = (canvas.height * imgWidth) / canvas.width;
      
      const pdf = new jsPDF('p', 'mm', 'a4');
      const imgData = canvas.toDataURL('image/png');
      
      // Center the card on the page
      const xOffset = 0;
      const yOffset = 20;
      
      pdf.addImage(imgData, 'PNG', xOffset, yOffset, imgWidth, imgHeight);
      
      // Download the PDF
      pdf.save('carte-identite-professionnelle.pdf');
    } catch (error) {
      console.error('Error generating PDF:', error);
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <Card className="pro-id-card-v2">
      <CardHeader>
        <div className="pro-id-header-row">
          <CardTitle className="pro-id-title-v2">
            <QrCode size={20} /> Carte d'Identité Professionnelle
          </CardTitle>
          <div className="cv-interactif-badge">
            BIENTÔT CV INTERACTIF ET DYNAMIQUE POUR POSTULER
          </div>
        </div>
        <CardDescription>Synthèse de votre profil - 4 dimensions</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="id-card-v2" ref={cardRef}>
          {/* Watermark - Filigrane central */}
          <div className="id-card-watermark">
            <span className="watermark-text">COPY INUTILISABLE</span>
          </div>
          
          {/* Header */}
          <div className="id-card-v2-header">
            <div className="id-logo">
              <span className="logo-name">John DO</span>
            </div>
            <div className="id-badge-reactif-logo">
              <img src="/reactif-pro-logo.png" alt="RE'ACTIF PRO" className="reactif-logo-img-small" />
            </div>
          </div>

          {/* 4 Pillars Grid */}
          <div className="id-pillars-grid">
            {/* Identité Personnelle */}
            <div className="id-pillar pillar-personnel">
              <div className="pillar-header">
                <Users size={16} />
                <h4>Identité Personnelle</h4>
              </div>
              <div className="pillar-content">
                <div className="pillar-field">
                  <span className="field-label">Qualités humaines</span>
                  <div className="field-tags">
                    {identitePersonnelle.qualites.map((q, i) => (
                      <span key={i} className="tag">{q}</span>
                    ))}
                  </div>
                </div>
                <div className="pillar-field">
                  <span className="field-label">Valeurs</span>
                  <div className="field-tags">
                    {identitePersonnelle.valeurs.map((v, i) => (
                      <span key={i} className="tag">{v}</span>
                    ))}
                  </div>
                </div>
                <div className="pillar-field">
                  <span className="field-label">Ce qui me rend unique</span>
                  <span className="field-value highlight">{identitePersonnelle.unique}</span>
                </div>
              </div>
            </div>

            {/* Identité Professionnelle */}
            <div className="id-pillar pillar-professionnel">
              <div className="pillar-header">
                <Briefcase size={16} />
                <h4>Identité Professionnelle</h4>
              </div>
              <div className="pillar-content">
                <div className="pillar-field">
                  <span className="field-label">Savoir-être</span>
                  <div className="field-tags">
                    {identiteProfessionnelle.savoirEtre.map((s, i) => (
                      <span key={i} className="tag">{s}</span>
                    ))}
                  </div>
                </div>
                {identiteProfessionnelle.hardSkills.length > 0 && (
                  <div className="pillar-field">
                    <span className="field-label">Hard Skills essentiels</span>
                    <div className="field-tags">
                      {identiteProfessionnelle.hardSkills.map((h, i) => (
                        <span key={i} className="tag">{h}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Identité Sociale */}
            <div className="id-pillar pillar-social">
              <div className="pillar-header">
                <Heart size={16} />
                <h4>Identité Sociale</h4>
              </div>
              <div className="pillar-content">
                <div className="pillar-field">
                  <span className="field-label">Mes rôles</span>
                  <div className="field-tags">
                    {identiteSociale.roles.map((r, i) => (
                      <span key={i} className="tag">{r}</span>
                    ))}
                  </div>
                </div>
                <div className="pillar-field">
                  <span className="field-label">Impact social</span>
                  <div className="field-tags">
                    {identiteSociale.impact.map((i, idx) => (
                      <span key={idx} className="tag">{i}</span>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Identité Profonde */}
            <div className="id-pillar pillar-profond">
              <div className="pillar-header">
                <Compass size={16} />
                <h4>Identité Profonde</h4>
              </div>
              <div className="pillar-content">
                <div className="pillar-field">
                  <span className="field-label">Ce qui donne du sens</span>
                  <span className="field-value highlight">{identiteProfonde.sens}</span>
                </div>
                <div className="pillar-field">
                  <span className="field-label">Ma mission</span>
                  <div className="field-tags">
                    {identiteProfonde.mission.map((m, i) => (
                      <span key={i} className="tag">{m}</span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="id-card-v2-footer">
            <div className="id-qr-section">
              <div className="id-qr">
                <QrCode size={36} />
              </div>
              <div className="id-metier-actuel">
                <span className="metier-label">{jobInfo?.job_label ? 'MÉTIER VISÉ' : 'PROFIL'}</span>
                <span className="metier-value">{jobInfo?.job_label || 'En exploration'}</span>
              </div>
            </div>
            <div className="id-meta">
              <span className="id-verified">Profil vérifié</span>
              <div className="id-meta-bottom">
                <span className="id-number">ID RCT.P/ 574159B</span>
                <span className="id-date">{new Date().toLocaleDateString('fr-FR')}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="id-card-actions-v2">
          <Button 
            variant="outline" 
            className="id-action-btn-v2" 
            onClick={handleDownloadPdf}
            disabled={isDownloading}
            data-testid="download-pdf-btn"
          >
            {isDownloading ? (
              <>
                <Loader2 size={16} className="animate-spin" /> Génération...
              </>
            ) : (
              <>
                <Download size={16} /> Télécharger PDF
              </>
            )}
          </Button>
          <Button variant="outline" className="id-action-btn-v2" disabled>
            <Share2 size={16} /> Partager
            <Badge variant="secondary" className="coming-soon">Bientôt</Badge>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

// ============================================================================
// CTA RE'ACTIF PRO - Invitation to continue
// ============================================================================
const ReactifProCTA = () => {
  // Generate unique alphanumeric code with date
  const generateProfileCode = () => {
    const now = new Date();
    const dateStr = now.getFullYear().toString() +
      String(now.getMonth() + 1).padStart(2, '0') +
      String(now.getDate()).padStart(2, '0');
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let randomPart = '';
    for (let i = 0; i < 5; i++) {
      randomPart += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return `DECLIC-${dateStr}-${randomPart}`;
  };

  const [profileCode] = useState(() => generateProfileCode());

  return (
    <Card className="reactif-cta-card" data-testid="reactif-pro-cta">
      <CardContent className="cta-card-content">
        <div className="cta-layout">
          {/* Left side - Logo and branding */}
          <div className="cta-brand-section">
            <img src="/reactif-pro-logo.png" alt="RE'ACTIF PRO" className="reactif-logo-img-cta" />
          </div>
          
          {/* Right side - Content and CTA */}
          <div className="cta-info-section">
            <h3 className="cta-title">
              RÉCUPÈRE ton rapport<br />
              <span style={{color: '#fbbf24'}}>profil personnalité & compétences</span><br />
              sur RE'ACTIF PRO
            </h3>
            <p className="cta-description">
              Poursuis ton parcours pro tout en gagnant en <strong>CONFIANCE</strong> et en <strong>ESTIME DE SOI</strong> !
            </p>
            <div className="cta-code-section">
              <span className="cta-code-label">Code à utiliser :</span>
              <span className="cta-code-value">{profileCode}</span>
            </div>
            <Button className="cta-button-new" disabled data-testid="discover-reactif-btn">
              <span>Découvrir RE'ACTIF PRO</span>
              <ExternalLink size={16} />
              <Badge className="cta-badge-soon">Bientôt</Badge>
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// ============================================================================
// PROFILE SUMMARY - Concise version at the end
// ============================================================================
const ProfileSummary = ({ narrative, competences }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  if (!narrative) return null;

  return (
    <Card className="profile-summary-card">
      <CardHeader>
        <div className="summary-header-row">
          <CardTitle className="summary-title">
            <Brain size={20} /> Synthèse Professionnelle
          </CardTitle>
          <Button 
            variant="ghost" 
            size="sm"
            onClick={() => setIsExpanded(!isExpanded)}
            className="expand-summary-btn"
          >
            {isExpanded ? 'Réduire' : 'Voir détails'}
            {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {/* Always visible: Key points */}
        <div className="summary-highlights">
          <p className="summary-main">
            {narrative.synthese_personnalite?.split('.').slice(0, 2).join('.') + '.'}
          </p>
          {competences?.length > 0 && (
            <div className="summary-competences">
              {competences.slice(0, 4).map((comp, idx) => (
                <Badge key={idx} className="competence-badge-mini">
                  {comp}
                </Badge>
              ))}
            </div>
          )}
        </div>

        {/* Expanded details */}
        {isExpanded && (
          <div className="summary-details">
            <Separator className="summary-separator" />
            
            {narrative.forces_et_talents && (
              <div className="summary-section">
                <h5><Award size={16} /> Forces</h5>
                <p>{narrative.forces_et_talents}</p>
              </div>
            )}
            
            {narrative.environnement_ideal && (
              <div className="summary-section">
                <h5><Briefcase size={16} /> Environnement idéal</h5>
                <p>{narrative.environnement_ideal}</p>
              </div>
            )}
            
            {narrative.axes_de_developpement && (
              <div className="summary-section">
                <h5><TrendingUp size={16} /> Axes de développement</h5>
                <p>{narrative.axes_de_developpement}</p>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// ============================================================================
// JOB NARRATIVE COMPONENT (with ROME, Soft Skills & Hard Skills)
// ============================================================================
const JobNarrative = ({ narrative, job }) => {
  const [expandedSections, setExpandedSections] = useState({});

  if (!narrative) return null;

  const toggleSection = (sectionId) => {
    setExpandedSections(prev => ({
      ...prev,
      [sectionId]: !prev[sectionId]
    }));
  };

  // Informations complémentaires pour "En savoir plus"
  const getMoreInfo = (sectionId) => {
    const moreInfoContent = {
      fiche_metier: {
        title: "À propos du référentiel ROME",
        content: "Le ROME (Répertoire Opérationnel des Métiers et des Emplois) est le référentiel officiel de France Travail. Il recense plus de 530 fiches métiers et permet d'identifier les compétences, formations et évolutions possibles pour chaque profession."
      },
      hard_skills: {
        title: "Comprendre les compétences techniques",
        content: "Les hard skills sont des compétences mesurables et spécifiques acquises par la formation ou l'expérience. Les compétences marquées ★ sont critiques pour ce métier, celles marquées ○ sont importantes mais peuvent être développées."
      },
      soft_skills: {
        title: "L'importance des soft skills",
        content: "Les soft skills (compétences comportementales) représentent 85% des facteurs de réussite professionnelle selon Harvard. Elles sont transférables entre métiers et peuvent se développer tout au long de la vie."
      },
      analyse: {
        title: "Comment est calculée la compatibilité ?",
        content: "Le score de compatibilité est calculé en croisant votre profil (personnalité, valeurs, compétences) avec les exigences du métier. Un score supérieur à 70% indique une bonne adéquation naturelle."
      },
      atouts: {
        title: "Valoriser vos atouts",
        content: "Ces atouts sont vos forces naturelles qui correspondent aux attentes du métier. Mettez-les en avant dans votre CV et vos entretiens pour maximiser vos chances."
      },
      progression: {
        title: "Développer ses soft skills",
        content: "Les soft skills se développent par la pratique, la formation et la prise de conscience. Des exercices quotidiens, du feedback régulier et de l'introspection sont les clés de la progression."
      }
    };
    return moreInfoContent[sectionId] || null;
  };

  const SectionWithMore = ({ sectionId, title, icon, children, className }) => {
    const moreInfo = getMoreInfo(sectionId);
    const isExpanded = expandedSections[sectionId];

    return (
      <div className={`job-narrative-section ${className || ''}`}>
        <div className="section-header-with-more">
          <h4>{icon} {title}</h4>
          {moreInfo && (
            <button 
              className="en-savoir-plus-btn"
              onClick={() => toggleSection(sectionId)}
              data-testid={`more-info-${sectionId}`}
            >
              <Info size={14} />
              {isExpanded ? 'Réduire' : 'En savoir plus'}
            </button>
          )}
        </div>
        
        {isExpanded && moreInfo && (
          <div className="more-info-content">
            <strong>{moreInfo.title}</strong>
            <p>{moreInfo.content}</p>
          </div>
        )}
        
        {children}
      </div>
    );
  };

  return (
    <div className="job-narrative">
      {/* Fiche Métier ROME */}
      {narrative.fiche_metier && (
        <SectionWithMore 
          sectionId="fiche_metier" 
          title="Fiche Métier" 
          icon={<Briefcase size={18} />}
          className="fiche-metier-section"
        >
          <div className="rome-header">
            {job?.code_rome && (
              <Badge variant="outline" className="rome-badge">Code ROME: {job.code_rome}</Badge>
            )}
            {job?.source === "france_travail" && (
              <Badge variant="secondary" className="source-badge france-travail-badge">
                Données France Travail
              </Badge>
            )}
          </div>
          <p>{narrative.fiche_metier}</p>
          {job?.acces_emploi && (
            <p className="acces-emploi"><strong>Accès à l'emploi :</strong> {job.acces_emploi}</p>
          )}
        </SectionWithMore>
      )}

      {/* Hard Skills Requis */}
      {job?.hard_skills_essentiels && job.hard_skills_essentiels.length > 0 && (
        <SectionWithMore 
          sectionId="hard_skills" 
          title="Compétences Techniques (Hard Skills)" 
          icon={<Zap size={18} />}
          className="hard-skills-section"
        >
          <div className="hard-skills-badges">
            {job.hard_skills_essentiels.map((skill, idx) => (
              <Badge 
                key={idx} 
                className={`hard-skill-badge ${skill.importance === 'critique' ? 'critique' : 'important'}`}
                title={skill.description}
              >
                {skill.importance === 'critique' ? '★' : '○'} {skill.nom}
              </Badge>
            ))}
          </div>
        </SectionWithMore>
      )}

      {/* Soft Skills Requis */}
      {narrative.soft_skills_requis && (
        <SectionWithMore 
          sectionId="soft_skills" 
          title="Soft Skills Essentiels" 
          icon={<Heart size={18} />}
          className="soft-skills-section"
        >
          <p>{narrative.soft_skills_requis}</p>
          {job?.soft_skills_essentiels && (
            <div className="soft-skills-badges">
              {job.soft_skills_essentiels.map((skill, idx) => (
                <Badge 
                  key={idx} 
                  className={`soft-skill-badge ${skill.importance === 'critique' ? 'critique' : 'important'}`}
                  title={skill.description}
                >
                  {skill.importance === 'critique' ? '★' : '○'} {skill.nom}
                </Badge>
              ))}
            </div>
          )}
        </SectionWithMore>
      )}

      {/* Analyse Compatibilité */}
      {narrative.analyse_compatibilite && (
        <SectionWithMore 
          sectionId="analyse" 
          title="Analyse de compatibilité" 
          icon={<Target size={18} />}
          className="analyse-section"
        >
          <p>{narrative.analyse_compatibilite}</p>
        </SectionWithMore>
      )}

      {/* Vos Atouts */}
      {(narrative.vos_atouts || narrative.atouts_pour_ce_metier) && (
        <SectionWithMore 
          sectionId="atouts" 
          title="Vos atouts pour ce métier" 
          icon={<CheckCircle2 size={18} />}
          className="atouts-section"
        >
          <p>{narrative.vos_atouts || narrative.atouts_pour_ce_metier}</p>
        </SectionWithMore>
      )}

      {/* Axes de Progression */}
      {(narrative.axes_progression || narrative.recommandations) && (
        <SectionWithMore 
          sectionId="progression" 
          title="Soft skills à développer" 
          icon={<TrendingUp size={18} />}
          className="progression-section"
        >
          <p>{narrative.axes_progression || narrative.recommandations}</p>
        </SectionWithMore>
      )}
    </div>
  );
};

// ============================================================================
// ZONES DE VIGILANCE - CADRAN D'OFMAN
// ============================================================================
const ZonesVigilance = ({ zones }) => {
  if (!zones || zones.length === 0) return null;

  return (
    <Card className="zones-vigilance-card">
      <CardHeader>
        <CardTitle className="zones-title">
          <AlertTriangle size={24} /> 
          <span className="tooltip-wrapper">
            <span className="tooltip-trigger">
              Cadran d'Ofman - Zones de Vigilance
              <Info size={16} className="info-icon" />
            </span>
            <span className="tooltip-content tooltip-large">
              Qu'est-ce que le Quadrant d'Ofman ?
              <br /><br />
              Conçu par le Néerlandais Daniel Ofman dans les années 1990, c'est un modèle simple et puissant d'auto-analyse. Il permet de mieux comprendre ses propres comportements, ses forces, et surtout, pourquoi nos qualités peuvent parfois devenir des défauts ou créer des tensions avec les autres.
              <br /><br />
              Le quadrant met en relation quatre éléments clés de notre personnalité :
              <br /><br />
              La Qualité fondamentale (Notre force) : C'est ce qui nous définit, notre point fort inné (ex : la détermination, la patience, l'ordre). C'est notre atout naturel.
              <br /><br />
              Le Piège (L'excès de la qualité) : Une qualité poussée à l'extrême devient un défaut. La détermination se transforme alors en entêtement ou en rigidité. C'est souvent ce qui provoque des conflits.
              <br /><br />
              Le Challenge (L'effort à fournir) : Pour sortir du piège, il faut cultiver la qualité opposée à ce piège. Si le piège est l'entêtement, le challenge sera la souplesse ou l'ouverture d'esprit. C'est l'axe de progrès.
              <br /><br />
              L'Allergie (Ce qui nous irrite chez l'autre) : C'est l'excès de notre propre challenge. Si nous devons apprendre la souplesse (notre challenge), nous serons très irrités par quelqu'un de trop "passif" ou "inconsistant". L'allergie agit comme un révélateur : ce qui nous énerve chez l'autre pointe directement sur ce que nous devons travailler chez nous.
              <br /><br />
              En résumé : Le quadrant montre que chaque force a une faiblesse symétrique. Il ne s'agit pas de supprimer nos qualités, mais d'apprendre à les équilibrer en travaillant sur notre challenge, afin d'être moins "allergique" aux autres et de mieux vivre ensemble.
              <br /><br />
              <span className="tooltip-authors">Daniel Ofman, consultant néerlandais en développement personnel et organisationnel.</span>
            </span>
          </span>
        </CardTitle>
        <CardDescription>
          Analyse personnalisée basée sur vos profils issus d'outils d'orientation professionnelle et de personnalité
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="zones-grid">
          {zones.map((zone, idx) => (
            <div key={idx} className="zone-card">
              <div className="zone-ofman-grid">
                {/* Qualité Fondamentale (Notre force) */}
                <div className="zone-item zone-qualite-box">
                  <span className="zone-label">💎 Qualité Fondamentale</span>
                  <span className="zone-value zone-qualite-value">{zone.qualite}</span>
                  <span className="zone-sublabel">Votre force naturelle</span>
                </div>
                
                {/* Piège (L'excès de la qualité) */}
                <div className="zone-item zone-piege">
                  <span className="zone-label">⚠️ Piège</span>
                  <span className="zone-value">{zone.piege}</span>
                  <span className="zone-sublabel">L'excès de votre qualité</span>
                </div>
                
                {/* Challenge (L'effort à fournir) */}
                <div className="zone-item zone-defi">
                  <span className="zone-label">🎯 Challenge</span>
                  <span className="zone-value">{zone.defi}</span>
                  <span className="zone-sublabel">L'axe de progrès</span>
                </div>
                
                {/* Allergie (Ce qui nous irrite) */}
                <div className="zone-item zone-allergie">
                  <span className="zone-label">🚫 Allergie</span>
                  <span className="zone-value">{zone.allergie}</span>
                  <span className="zone-sublabel">Ce qui vous irrite chez l'autre</span>
                </div>
              </div>
              
              <div className="zone-recommandation">
                <span className="zone-label">💡 Conseil personnalisé</span>
                <p>{zone.recommandation}</p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

// ============================================================================
// NAVIGATION SIDEBAR - Menu de navigation des sections
// ============================================================================
const NavigationSidebar = ({ isExplore = false }) => {
  const [activeSection, setActiveSection] = useState('archeologie');
  
  const jobSections = [
    { id: 'archeologie', icon: '🔍', title: 'Archéologie des Compétences', subtitle: 'Vos talents naturels' },
    { id: 'tripartite', icon: '📊', title: 'Radar Tripartite', subtitle: 'Vision globale' },
    { id: 'boussole', icon: '🧭', title: 'Boussole de Fonctionnement', subtitle: 'Vos axes cognitifs' },
    { id: 'analyse', icon: '🔬', title: 'Analyse Intégrée', subtitle: '3 niveaux de lecture' },
    { id: 'actions', icon: '🎯', title: 'Pistes d\'Action', subtitle: 'Leviers de progression' },
    { id: 'croisee', icon: '⚡', title: 'Analyse Croisée', subtitle: 'Synergies & tensions' },
    { id: 'ofman', icon: '⚠️', title: 'Cadran d\'Ofman', subtitle: 'Zones de vigilance' },
    { id: 'metier', icon: '💼', title: 'Résultat Métier', subtitle: 'Compatibilité job' },
    { id: 'carte', icon: '🪪', title: 'Carte d\'Identité Pro', subtitle: 'Synthèse du profil' },
  ];

  const exploreSections = [
    { id: 'archeologie', icon: '🔍', title: 'Archéologie des Compétences', subtitle: 'Vos talents naturels' },
    { id: 'tripartite', icon: '📊', title: 'Radar Tripartite', subtitle: 'Vision globale' },
    { id: 'boussole', icon: '🧭', title: 'Boussole de Fonctionnement', subtitle: 'Vos axes cognitifs' },
    { id: 'analyse', icon: '🔬', title: 'Analyse Intégrée', subtitle: '3 niveaux de lecture' },
    { id: 'actions', icon: '🎯', title: 'Pistes d\'Action', subtitle: 'Leviers de progression' },
    { id: 'croisee', icon: '⚡', title: 'Analyse Croisée', subtitle: 'Synergies & tensions' },
    { id: 'ofman', icon: '⚠️', title: 'Cadran d\'Ofman', subtitle: 'Zones de vigilance' },
    { id: 'filieres', icon: '🧩', title: 'Filières Recommandées', subtitle: 'Vos orientations' },
    { id: 'topjobs', icon: '🏆', title: 'Top 10 Métiers', subtitle: 'Meilleures compatibilités' },
    { id: 'carte', icon: '🪪', title: 'Carte d\'Identité Pro', subtitle: 'Synthèse du profil' },
  ];

  const sections = isExplore ? exploreSections : jobSections;

  const scrollToSection = (sectionId) => {
    setActiveSection(sectionId);
    const element = document.getElementById(`section-${sectionId}`);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <div className="navigation-sidebar" data-testid="navigation-sidebar">
      <div className="nav-sidebar-header">
        <BookOpen size={18} />
        <span>Navigation</span>
      </div>
      <div className="nav-sidebar-items">
        {sections.map((section, index) => (
          <button
            key={section.id}
            className={`nav-sidebar-item ${activeSection === section.id ? 'active' : ''}`}
            onClick={() => scrollToSection(section.id)}
          >
            <span className="nav-item-icon">{section.icon}</span>
            <div className="nav-item-text">
              <span className="nav-item-title">{index + 1}. {section.title}</span>
              <span className="nav-item-subtitle">{section.subtitle}</span>
            </div>
            <ChevronRight size={16} className="nav-item-arrow" />
          </button>
        ))}
      </div>
    </div>
  );
};

// ============================================================================
// RESULTS MEMO - Récapitulatif sur le côté gauche
// ============================================================================
const ResultsMemo = ({ result, jobInfo, bestMatch }) => {
  const { profile_summary, profile_narrative, vertus_data, life_path, cross_analysis } = result || {};

  return (
    <div className="results-memo" data-testid="results-memo">
      <div className="memo-sticky">
        <h3 className="memo-title">
          <BookOpen size={18} /> Votre Profil
        </h3>

        {/* Métier visé */}
        {bestMatch && (
          <div className="memo-section memo-job">
            <div className="memo-job-header">
              <Briefcase size={16} />
              <span className="memo-job-title">{bestMatch.job_label}</span>
            </div>
            <div className={`memo-score ${bestMatch.score >= 70 ? 'high' : bestMatch.score >= 50 ? 'medium' : 'low'}`}>
              {bestMatch.score}% compatible
            </div>
          </div>
        )}

        {/* Compétences clés */}
        {profile_summary?.competences_fortes && (
          <div className="memo-section">
            <h4><Zap size={14} /> Compétences clés</h4>
            <div className="memo-tags">
              {profile_summary.competences_fortes.slice(0, 4).map((comp, idx) => (
                <span key={idx} className="memo-tag">{comp}</span>
              ))}
            </div>
          </div>
        )}

        {/* Forces naturelles */}
        {life_path?.strengths && (
          <div className="memo-section">
            <h4><CheckCircle2 size={14} /> Forces</h4>
            <div className="memo-tags">
              {life_path.strengths.slice(0, 3).map((s, idx) => (
                <span key={idx} className="memo-tag strength">{s}</span>
              ))}
            </div>
          </div>
        )}

        {/* Points de vigilance */}
        {life_path?.watchouts && (
          <div className="memo-section">
            <h4><AlertTriangle size={14} /> Vigilances</h4>
            <div className="memo-tags">
              {life_path.watchouts.slice(0, 2).map((w, idx) => (
                <span key={idx} className="memo-tag warning">{w}</span>
              ))}
            </div>
          </div>
        )}

        {/* Valeurs/Vertus */}
        {vertus_data && (
          <div className="memo-section">
            <h4><Heart size={14} /> Valeurs</h4>
            <div className="memo-tags">
              {vertus_data.qualites_humaines?.slice(0, 3).map((q, idx) => (
                <span key={idx} className="memo-tag value">{q}</span>
              ))}
            </div>
          </div>
        )}

        {/* Thématique */}
        {life_path?.label && (
          <div className="memo-section memo-theme">
            <h4><Compass size={14} /> Thématique</h4>
            <span className="memo-theme-label">{life_path.label}</span>
          </div>
        )}

        {/* Environnements favorables */}
        {life_path?.work_preferences && (
          <div className="memo-section">
            <h4><Target size={14} /> Environnements</h4>
            <ul className="memo-list">
              {life_path.work_preferences.slice(0, 3).map((pref, idx) => (
                <li key={idx}>{pref}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Synergies */}
        {cross_analysis?.has_cross_analysis && (
          <div className="memo-section memo-synergy">
            <h4><Sparkles size={14} /> Synergie clé</h4>
            <p className="memo-synergy-text">
              {cross_analysis.synergy_disc?.substring(0, 80)}...
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

// ============================================================================
// JOB MATCH RESULT
// ============================================================================
const JobMatchResult = ({ result, onBack, onNewSearch }) => {
  if (!result) return null;

  const { profile_summary, profile_narrative, vertus_data, zones_vigilance, life_path, cross_analysis, functioning_compass, integrated_analysis, best_match, job_info, job_narrative, other_matches, suggested_jobs } = result;

  const getScoreColor = (score) => {
    if (score >= 80) return 'score-excellent';
    if (score >= 60) return 'score-good';
    if (score >= 40) return 'score-moderate';
    return 'score-low';
  };

  return (
    <div className="results-container declic-results">
      <div className="results-header">
        <Button variant="ghost" onClick={onBack} data-testid="results-back-btn" className="declic-back-btn">
          <ChevronLeft size={20} /> Retour à l'accueil
        </Button>
        <DeclicProLogoCompact size={40} />
        <div className="header-right-section">
          <Button variant="outline" onClick={onNewSearch} data-testid="new-search-btn" className="declic-button-secondary">
            <Search size={18} /> Nouvelle recherche
          </Button>
          <div className="reactif-logo-header" data-testid="reactif-logo-header">
            <img src="/reactif-pro-logo.png" alt="RE'ACTIF PRO" className="reactif-logo-img-header" />
          </div>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="results-disclaimer">
        <Info size={16} />
        <p>Cette analyse exploratoire vous offre un premier éclairage sur votre profil. Pour une évaluation approfondie et certifiée, un accompagnement personnalisé est disponible via la plateforme <strong>RE'ACTIF PRO</strong>.</p>
      </div>

      {/* Layout avec navigation */}
      <div className="results-with-nav">
        {/* Sidebar Navigation */}
        <NavigationSidebar />
        
        {/* Contenu principal */}
        <div className="results-main-content">
      {/* Layout principal */}
      <div className="results-layout-full">
        {/* Contenu principal */}
        <div className="results-main">
          {/* 1. Archéologie des Compétences (items du tableau) */}
          <div id="section-archeologie">
            <SkillsArcheology vertus={vertus_data} />
          </div>

          {/* 2. Graphique Radar Tripartite */}
          <div id="section-tripartite">
            <TripartiteRadar vertus={vertus_data} lifePath={life_path} profileSummary={profile_summary} />
          </div>

          {/* 2.bis Boussole de Fonctionnement */}
          <div id="section-boussole">
            <FunctioningCompass compass={functioning_compass} />
          </div>

          {/* 2.ter Analyse Intégrée - 3 Niveaux */}
          <div id="section-analyse">
            <IntegratedAnalysis analysis={integrated_analysis} />
          </div>

          {/* 3. Pistes d'Action */}
          <div id="section-actions">
            <MicroActions lifePath={life_path} />
          </div>

          {/* 4. Analyse Croisée - Synergies & Tensions */}
          <div id="section-croisee">
            <CrossAnalysisDisplay crossAnalysis={cross_analysis} lifePath={life_path} />
          </div>

          {/* 5. Zones de Vigilance - Cadran d'Ofman */}
          <div id="section-ofman">
            <ZonesVigilance zones={zones_vigilance} />
          </div>

          <Separator className="results-separator" />

      {/* 6. Résultat Métier */}
      <div id="section-metier">
      {best_match && (
        <Card className="match-card best-match-card declic-match-card">
          <CardHeader>
            <div className="match-header">
              <div className="match-info">
                <CardTitle className="match-title">
                  <Briefcase size={24} /> {best_match.job_label}
                </CardTitle>
                <CardDescription>
                  {best_match.filiere} • {best_match.secteur}
                </CardDescription>
              </div>
              <div className={`score-circle ${getScoreColor(best_match.score)}`} data-testid="match-score">
                <span className="score-value">{best_match.score}%</span>
                <span className="score-label">{best_match.category}</span>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <JobNarrative narrative={job_narrative} job={job_info} />
          </CardContent>
        </Card>
      )}

      {/* Note: Section "other_matches" supprimée car elle affichait des métiers 
          de la base locale qui n'étaient pas similaires au métier recherché.
          Seule la section "suggested_jobs" est pertinente (métiers adaptés au profil si score < 70%) */}

      {/* Métiers suggérés si score < 70% */}
      {suggested_jobs && suggested_jobs.length > 0 && (
        <Card className="suggested-jobs-card" data-testid="suggested-jobs-section">
          <CardHeader>
            <CardTitle className="suggested-jobs-title">
              <Lightbulb size={24} /> Métiers plus adaptés à votre profil
            </CardTitle>
            <CardDescription>
              Votre score de compatibilité avec le métier recherché est inférieur à 70%. 
              Voici des métiers qui correspondent mieux à votre profil.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="suggested-jobs-grid">
              {suggested_jobs.map((job, idx) => (
                <div key={idx} className="suggested-job-item">
                  <div className="suggested-job-header">
                    <div className="suggested-job-info">
                      <h4>{job.job_label}</h4>
                      <span className="suggested-job-sector">{job.secteur}</span>
                    </div>
                    <Badge className={`suggested-job-score ${getScoreColor(job.score)}`}>
                      {job.score}%
                    </Badge>
                  </div>
                  {job.reasons && job.reasons.length > 0 && (
                    <p className="suggested-job-reason">{job.reasons[0]}</p>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
      </div>
        </div>
      </div>

      {/* 5. Carte d'Identité Professionnelle - Pleine largeur */}
      <div id="section-carte">
        <ProfessionalIdCard 
          vertus={vertus_data} 
          competences={profile_summary?.competences_fortes}
          narrative={profile_narrative}
          lifePath={life_path}
          jobInfo={job_info}
        />
      </div>

      {/* 6. Synthèse Professionnelle (à la fin, concise) */}
      <ProfileSummary narrative={profile_narrative} competences={profile_summary?.competences_fortes} />

      {/* 7. CTA RE'ACTIF PRO */}
      <ReactifProCTA />
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// EXPLORE RESULT
// ============================================================================
const ExploreResult = ({ result, onBack }) => {
  if (!result) return null;

  const { profile_summary, profile_narrative, vertus_data, zones_vigilance, life_path, cross_analysis, functioning_compass, integrated_analysis, exploration_paths, top_jobs } = result;

  const getScoreColor = (score) => {
    if (score >= 80) return 'score-excellent';
    if (score >= 60) return 'score-good';
    if (score >= 40) return 'score-moderate';
    return 'score-low';
  };

  return (
    <div className="results-container explore-results declic-results">
      <div className="results-header">
        <Button variant="ghost" onClick={onBack} data-testid="explore-results-back-btn" className="declic-back-btn">
          <ChevronLeft size={20} /> Retour à l'accueil
        </Button>
        <DeclicProLogoCompact size={40} />
        <div className="header-right-section">
          <div className="reactif-logo-header" data-testid="reactif-logo-header-explore">
            <img src="/reactif-pro-logo.png" alt="RE'ACTIF PRO" className="reactif-logo-img-header" />
          </div>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="results-disclaimer">
        <Info size={16} />
        <p>Cette analyse exploratoire vous offre un premier éclairage sur votre profil. Pour une évaluation approfondie et certifiée, un accompagnement personnalisé est disponible via la plateforme <strong>RE'ACTIF PRO</strong>.</p>
      </div>

      {/* Layout avec navigation */}
      <div className="results-with-nav">
        {/* Sidebar Navigation */}
        <NavigationSidebar isExplore={true} />
        
        {/* Contenu principal */}
        <div className="results-main-content">
      {/* Layout principal */}
      <div className="results-layout-full">
        {/* Contenu principal */}
        <div className="results-main">
          {/* 1. Archéologie des Compétences (items du tableau) */}
          <div id="section-archeologie">
            <SkillsArcheology vertus={vertus_data} />
          </div>

          {/* 2. Graphique Radar Tripartite */}
          <div id="section-tripartite">
            <TripartiteRadar vertus={vertus_data} lifePath={life_path} profileSummary={profile_summary} />
          </div>

          {/* 2.bis Boussole de Fonctionnement */}
          <div id="section-boussole">
            <FunctioningCompass compass={functioning_compass} />
          </div>

          {/* 2.ter Analyse Intégrée - 3 Niveaux */}
          <div id="section-analyse">
            <IntegratedAnalysis analysis={integrated_analysis} />
          </div>

          {/* 3. Pistes d'Action */}
          <div id="section-actions">
            <MicroActions lifePath={life_path} />
          </div>

          {/* 4. Analyse Croisée - Synergies & Tensions */}
          <div id="section-croisee">
            <CrossAnalysisDisplay crossAnalysis={cross_analysis} lifePath={life_path} />
          </div>

          {/* 5. Zones de Vigilance - Cadran d'Ofman */}
          <div id="section-ofman">
            <ZonesVigilance zones={zones_vigilance} />
          </div>

          <Separator className="results-separator" />

          {/* 6. Filières recommandées */}
          <div id="section-filieres">
          <h2 className="section-title declic-section-title">
            <Compass size={28} /> Filières recommandées
          </h2>

          <div className="paths-grid">
            {exploration_paths?.map((path, idx) => (
              <Card key={idx} className="path-result-card">
                <CardHeader>
                  <div className="path-result-header">
                    <CardTitle>{path.filiere}</CardTitle>
                    <Badge className={getScoreColor(path.avg_compatibility)}>
                      {path.avg_compatibility}% compatibilité
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="path-secteurs">
                    <h5>Secteurs :</h5>
                    <div className="secteurs-badges">
                      {path.secteurs?.map((s, i) => (
                        <Badge key={i} variant="outline">{s}</Badge>
                      ))}
                    </div>
                  </div>
                  <div className="path-jobs">
                    <h5>Métiers indicatifs :</h5>
                    <ul>
                      {path.indicative_jobs?.map((job, i) => (
                    <li key={i}><ArrowRight size={14} /> {job}</li>
                  ))}
                </ul>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Separator className="results-separator" />

      {/* 5. Top 10 métiers */}
      </div>
      <div id="section-topjobs">
      <h2 className="section-title">
        <TrendingUp size={28} /> Top 10 métiers pour vous
      </h2>

      <div className="top-jobs-list">
        {top_jobs?.map((job, idx) => (
          <Card key={idx} className="top-job-card">
            <CardContent className="top-job-content">
              <div className="top-job-rank">#{idx + 1}</div>
              <div className="top-job-info">
                <h4>{job.job_label}</h4>
                <p>{job.filiere} • {job.secteur}</p>
              </div>
              <div className={`top-job-score ${getScoreColor(job.score)}`}>
                <span className="score-num">{job.score}%</span>
                <span className="score-cat">{job.category}</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
      </div>
        </div>
      </div>

      {/* 6. Carte d'Identité Professionnelle - Pleine largeur */}
      <div id="section-carte">
        <ProfessionalIdCard 
          vertus={vertus_data} 
          competences={profile_summary?.competences_fortes}
          narrative={profile_narrative}
          lifePath={life_path}
        />
      </div>

      {/* 7. Synthèse Professionnelle (à la fin, concise) */}
      <ProfileSummary narrative={profile_narrative} competences={profile_summary?.competences_fortes} />

      {/* 8. CTA RE'ACTIF PRO */}
      <ReactifProCTA />
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// MAIN APP
// ============================================================================
const Home = () => {
  const [step, setStep] = useState('landing'); // landing, questionnaire, job-search, job-result, explore-result
  const [pathType, setPathType] = useState(null); // 'job' or 'explore'
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [birthDate, setBirthDate] = useState("");
  const [jobResult, setJobResult] = useState(null);
  const [exploreResult, setExploreResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadQuestionnaire();
  }, []);

  const loadQuestionnaire = async () => {
    try {
      // Charger le questionnaire visuel (images) pour une meilleure accessibilité
      const response = await axios.get(`${API}/questionnaire/visual`);
      setQuestions(response.data.questions);
    } catch (e) {
      console.error("Error loading questionnaire:", e);
      // Fallback to legacy questionnaire if visual not available
      try {
        const fallback = await axios.get(`${API}/questionnaire`);
        setQuestions(fallback.data.questions);
      } catch (e2) {
        console.error("Error loading fallback questionnaire:", e2);
      }
    }
  };

  const handleSelectPath = (path) => {
    setPathType(path);
    setStep('questionnaire');
  };

  const handleQuestionnaireComplete = async (completedAnswers, completedBirthDate) => {
    setAnswers(completedAnswers);
    setBirthDate(completedBirthDate);
    
    if (pathType === 'job') {
      setStep('job-search');
    } else {
      // Explore path - get results directly
      setIsLoading(true);
      try {
        const response = await axios.post(`${API}/explore`, {
          answers: completedAnswers,
          birth_date: completedBirthDate
        });
        setExploreResult(response.data);
        setStep('explore-result');
      } catch (e) {
        console.error("Error getting explore results:", e);
      }
      setIsLoading(false);
    }
  };

  const handleJobSearch = async (query) => {
    setIsLoading(true);
    try {
      const response = await axios.post(`${API}/job-match`, {
        answers: answers,
        job_query: query,
        birth_date: birthDate
      });
      setJobResult(response.data);
      setStep('job-result');
    } catch (e) {
      console.error("Error getting job match:", e);
    }
    setIsLoading(false);
  };

  const handleBack = () => {
    setStep('landing');
    setPathType(null);
    setAnswers({});
    setBirthDate("");
    setJobResult(null);
    setExploreResult(null);
  };

  const handleNewSearch = () => {
    setStep('job-search');
  };

  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner" />
        <p className="loading-title">Analyse de votre profil en cours...</p>
        <p className="loading-subtitle">Notre IA analyse vos réponses et génère votre rapport personnalisé.</p>
        <p className="loading-time">Cette opération peut prendre jusqu'à 1 minute.</p>
      </div>
    );
  }

  return (
    <div className="app-container">
      {step === 'landing' && (
        <LandingPage onSelectPath={handleSelectPath} />
      )}

      {step === 'questionnaire' && (
        <Questionnaire 
          questions={questions}
          onComplete={handleQuestionnaireComplete}
          onBack={handleBack}
        />
      )}

      {step === 'job-search' && (
        <JobSearchInput 
          onSearch={handleJobSearch}
          onBack={() => setStep('questionnaire')}
        />
      )}

      {step === 'job-result' && (
        <JobMatchResult 
          result={jobResult}
          onBack={handleBack}
          onNewSearch={handleNewSearch}
        />
      )}

      {step === 'explore-result' && (
        <ExploreResult 
          result={exploreResult}
          onBack={handleBack}
        />
      )}
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="*" element={<Home />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
