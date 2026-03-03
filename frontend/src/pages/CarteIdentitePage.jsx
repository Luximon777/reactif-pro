import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { ArrowLeft, Sparkles, Heart, TrendingUp, Briefcase, Star, Download, Share2 } from "lucide-react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Default profile data for demonstration
const defaultProfile = {
  soft_skills: ["Esprit analytique", "Communication orale", "Organisation", "Adaptabilité"],
  values: ["Impact social", "Flexibilité", "Développement personnel", "Esprit d'équipe"],
  potentials: ["Gestion du stress", "Proactivité", "Vision stratégique", "Expertise"],
  compatibility_jobs: [
    { title: "Chef de projet", compatibility: 92, sector: "Management" },
    { title: "Consultant", compatibility: 88, sector: "Conseil" },
    { title: "Product Manager", compatibility: 85, sector: "Tech" },
    { title: "Responsable RH", compatibility: 82, sector: "Ressources Humaines" },
    { title: "Entrepreneur", compatibility: 78, sector: "Entrepreneuriat" }
  ]
};

export const CarteIdentitePage = () => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [jobs, setJobs] = useState([]);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      // First try to get from localStorage
      const storedProfile = localStorage.getItem('profile');
      
      if (storedProfile) {
        const parsedProfile = JSON.parse(storedProfile);
        setProfile(parsedProfile);
        
        // Fetch matching jobs
        try {
          const jobsResponse = await axios.post(`${API}/matching-jobs`, {
            soft_skills: parsedProfile.soft_skills,
            values: parsedProfile.values,
            potentials: parsedProfile.potentials
          });
          setJobs(jobsResponse.data.jobs || defaultProfile.compatibility_jobs);
        } catch {
          setJobs(defaultProfile.compatibility_jobs);
        }
      } else {
        // Use default profile for demonstration
        setProfile(defaultProfile);
        setJobs(defaultProfile.compatibility_jobs);
      }
    } catch (error) {
      console.error('Error loading profile:', error);
      setProfile(defaultProfile);
      setJobs(defaultProfile.compatibility_jobs);
    } finally {
      setLoading(false);
    }
  };

  const getCompatibilityColor = (score) => {
    if (score >= 85) return 'compatibility-high';
    return 'compatibility-medium';
  };

  const getPotentialScore = (index) => {
    const scores = [95, 88, 82, 75];
    return scores[index] || 70;
  };

  if (loading) {
    return (
      <div className="min-h-screen hero-bg flex items-center justify-center" data-testid="loading-state">
        <div className="animate-pulse text-white/60">Chargement de votre profil...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen hero-bg pb-20" data-testid="carte-identite-page">
      {/* Header */}
      <header className="px-6 py-6 flex items-center justify-between max-w-6xl mx-auto">
        <Link to="/" className="flex items-center gap-2 text-white/60 hover:text-white transition-colors" data-testid="back-home-link">
          <ArrowLeft className="w-5 h-5" />
          <span>Retour</span>
        </Link>
        <div className="flex gap-3">
          <button className="p-2 rounded-full glass hover:bg-white/10 transition-colors" data-testid="share-btn">
            <Share2 className="w-5 h-5 text-white/60" />
          </button>
          <button className="p-2 rounded-full glass hover:bg-white/10 transition-colors" data-testid="download-btn">
            <Download className="w-5 h-5 text-white/60" />
          </button>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6">
        {/* Title */}
        <div className="text-center mb-12 animate-fade-in-up">
          <h1 className="text-4xl md:text-5xl font-bold">
            <span className="gradient-text">Carte d'identité Pro</span>
          </h1>
          <p className="text-white/60 mt-4">Votre profil professionnel personnalisé</p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Left Column - Skills & Values */}
          <div className="space-y-8">
            {/* Soft Skills */}
            <section className="identity-card p-8 animate-fade-in-up" data-testid="soft-skills-section">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-3 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-400">
                  <Sparkles className="w-6 h-6 text-white" />
                </div>
                <h2 className="text-2xl font-bold text-white">Soft Skills</h2>
              </div>
              <div className="flex flex-wrap gap-3">
                {profile.soft_skills.map((skill, index) => (
                  <span key={index} className="skill-badge" data-testid={`skill-${index}`}>
                    <Star className="w-4 h-4 text-purple-400" />
                    {skill}
                  </span>
                ))}
              </div>
            </section>

            {/* Values */}
            <section className="identity-card p-8 animate-fade-in-up" style={{ animationDelay: '0.1s' }} data-testid="values-section">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-3 rounded-xl bg-gradient-to-br from-pink-500 to-rose-400">
                  <Heart className="w-6 h-6 text-white" />
                </div>
                <h2 className="text-2xl font-bold text-white">Valeurs</h2>
              </div>
              <div className="flex flex-wrap gap-3">
                {profile.values.map((value, index) => (
                  <span key={index} className="value-tag" data-testid={`value-${index}`}>
                    {value}
                  </span>
                ))}
              </div>
            </section>

            {/* Potential */}
            <section className="identity-card p-8 animate-fade-in-up" style={{ animationDelay: '0.2s' }} data-testid="potential-section">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-3 rounded-xl bg-gradient-to-br from-purple-500 to-violet-400">
                  <TrendingUp className="w-6 h-6 text-white" />
                </div>
                <h2 className="text-2xl font-bold text-white">Potentiel</h2>
              </div>
              <div className="space-y-4">
                {profile.potentials.map((potential, index) => (
                  <div key={index} data-testid={`potential-${index}`}>
                    <div className="flex justify-between mb-2">
                      <span className="text-white/80">{potential}</span>
                      <span className="text-purple-400 font-semibold">{getPotentialScore(index)}%</span>
                    </div>
                    <div className="potential-meter">
                      <div 
                        className="potential-fill" 
                        style={{ width: `${getPotentialScore(index)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </section>
          </div>

          {/* Right Column - Job Matching */}
          <div className="space-y-8">
            <section className="identity-card p-8 animate-fade-in-up" style={{ animationDelay: '0.3s' }} data-testid="jobs-section">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-3 rounded-xl bg-gradient-to-br from-amber-500 to-orange-400">
                  <Briefcase className="w-6 h-6 text-white" />
                </div>
                <h2 className="text-2xl font-bold text-white">Métiers compatibles</h2>
              </div>
              
              <div className="space-y-4">
                {jobs.map((job, index) => (
                  <div key={index} className="job-card" data-testid={`job-${index}`}>
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h3 className="text-lg font-semibold text-white">{job.title}</h3>
                        <span className="text-white/50 text-sm">{job.sector}</span>
                      </div>
                      <span className={`compatibility-badge ${getCompatibilityColor(job.compatibility)}`}>
                        {job.compatibility}% match
                      </span>
                    </div>
                    <div className="potential-meter">
                      <div 
                        className="potential-fill" 
                        style={{ width: `${job.compatibility}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {/* CTA */}
            <div className="identity-card p-8 text-center animate-fade-in-up" style={{ animationDelay: '0.4s' }} data-testid="cta-card">
              <h3 className="text-xl font-bold text-white mb-3">Vous n'avez pas encore répondu au questionnaire ?</h3>
              <p className="text-white/60 mb-6">Découvrez votre véritable profil professionnel</p>
              <Link 
                to="/questionnaire"
                className="btn-primary px-8 py-3 rounded-full font-semibold text-white inline-block"
                data-testid="start-questionnaire-link"
              >
                Faire le questionnaire
              </Link>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};
