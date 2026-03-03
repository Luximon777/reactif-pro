import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowLeft, ArrowRight, CheckCircle, ChevronRight } from "lucide-react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const questions = [
  {
    id: 1,
    category: "soft_skills",
    question: "Face à un problème complexe, quelle est votre première réaction ?",
    options: [
      { value: "analytical", label: "Je décompose le problème en parties plus petites", trait: "Esprit analytique" },
      { value: "creative", label: "Je cherche des solutions innovantes et originales", trait: "Créativité" },
      { value: "collaborative", label: "Je consulte mes collègues pour avoir différents avis", trait: "Collaboration" },
      { value: "decisive", label: "Je prends rapidement une décision et j'agis", trait: "Prise de décision" }
    ]
  },
  {
    id: 2,
    category: "soft_skills",
    question: "Comment préférez-vous communiquer dans un contexte professionnel ?",
    options: [
      { value: "written", label: "Par écrit, pour être précis et garder une trace", trait: "Communication écrite" },
      { value: "verbal", label: "À l'oral, pour des échanges plus dynamiques", trait: "Communication orale" },
      { value: "visual", label: "Avec des supports visuels et des présentations", trait: "Communication visuelle" },
      { value: "listening", label: "J'écoute d'abord avant de m'exprimer", trait: "Écoute active" }
    ]
  },
  {
    id: 3,
    category: "values",
    question: "Qu'est-ce qui vous motive le plus au travail ?",
    options: [
      { value: "impact", label: "Avoir un impact positif sur la société", trait: "Impact social" },
      { value: "growth", label: "Apprendre et progresser continuellement", trait: "Développement personnel" },
      { value: "autonomy", label: "Être autonome et gérer mes propres projets", trait: "Autonomie" },
      { value: "recognition", label: "Être reconnu pour mon travail et mes compétences", trait: "Reconnaissance" }
    ]
  },
  {
    id: 4,
    category: "values",
    question: "Quel environnement de travail vous correspond le mieux ?",
    options: [
      { value: "structured", label: "Un cadre structuré avec des processus clairs", trait: "Structure" },
      { value: "flexible", label: "Un environnement flexible et adaptable", trait: "Flexibilité" },
      { value: "innovative", label: "Une culture d'innovation et d'expérimentation", trait: "Innovation" },
      { value: "collaborative", label: "Une équipe soudée avec une forte entraide", trait: "Esprit d'équipe" }
    ]
  },
  {
    id: 5,
    category: "potential",
    question: "Comment gérez-vous la pression et les deadlines serrées ?",
    options: [
      { value: "calm", label: "Je reste calme et méthodique", trait: "Gestion du stress" },
      { value: "energized", label: "La pression me stimule et me rend plus productif", trait: "Résilience" },
      { value: "organized", label: "Je m'organise et priorise les tâches", trait: "Organisation" },
      { value: "delegating", label: "Je délègue et mobilise mon équipe", trait: "Leadership" }
    ]
  },
  {
    id: 6,
    category: "potential",
    question: "Face au changement, comment réagissez-vous ?",
    options: [
      { value: "embracing", label: "J'accueille le changement comme une opportunité", trait: "Adaptabilité" },
      { value: "cautious", label: "Je prends le temps d'analyser avant de m'adapter", trait: "Prudence" },
      { value: "proactive", label: "J'initie souvent le changement moi-même", trait: "Proactivité" },
      { value: "supportive", label: "J'aide les autres à s'adapter au changement", trait: "Empathie" }
    ]
  },
  {
    id: 7,
    category: "career",
    question: "Quel type de tâches vous épanouit le plus ?",
    options: [
      { value: "strategic", label: "Définir des stratégies et planifier à long terme", trait: "Vision stratégique" },
      { value: "operational", label: "Exécuter et concrétiser des projets", trait: "Sens opérationnel" },
      { value: "relational", label: "Développer des relations et négocier", trait: "Relationnel" },
      { value: "technical", label: "Résoudre des problèmes techniques complexes", trait: "Expertise technique" }
    ]
  },
  {
    id: 8,
    category: "career",
    question: "Comment envisagez-vous votre évolution professionnelle ?",
    options: [
      { value: "management", label: "Évoluer vers des responsabilités managériales", trait: "Leadership" },
      { value: "expertise", label: "Devenir expert reconnu dans mon domaine", trait: "Expertise" },
      { value: "entrepreneurship", label: "Créer ma propre activité ou entreprise", trait: "Entrepreneuriat" },
      { value: "versatility", label: "Diversifier mes compétences et expériences", trait: "Polyvalence" }
    ]
  }
];

export const QuestionnairePage = () => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [isComplete, setIsComplete] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  const progress = ((currentQuestion + 1) / questions.length) * 100;
  const question = questions[currentQuestion];

  const handleAnswer = (value) => {
    const selectedOption = question.options.find(opt => opt.value === value);
    setAnswers(prev => ({
      ...prev,
      [question.id]: {
        value,
        trait: selectedOption.trait,
        category: question.category
      }
    }));
  };

  const handleNext = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(prev => prev + 1);
    } else {
      handleSubmit();
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(prev => prev - 1);
    }
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      // Prepare profile data from answers
      const softSkills = [];
      const values = [];
      const potentials = [];

      Object.values(answers).forEach(answer => {
        if (answer.category === 'soft_skills') {
          softSkills.push(answer.trait);
        } else if (answer.category === 'values') {
          values.push(answer.trait);
        } else if (answer.category === 'potential' || answer.category === 'career') {
          potentials.push(answer.trait);
        }
      });

      const profileData = {
        soft_skills: softSkills,
        values: values,
        potentials: potentials,
        answers: answers,
        timestamp: new Date().toISOString()
      };

      // Save to backend
      const response = await axios.post(`${API}/profile`, profileData);
      
      // Store profile ID in localStorage
      localStorage.setItem('profileId', response.data.id);
      localStorage.setItem('profile', JSON.stringify(response.data));
      
      setIsComplete(true);
    } catch (error) {
      console.error('Error submitting profile:', error);
      // Still mark as complete even if API fails - we have local data
      const localProfile = {
        id: `local_${Date.now()}`,
        soft_skills: Object.values(answers).filter(a => a.category === 'soft_skills').map(a => a.trait),
        values: Object.values(answers).filter(a => a.category === 'values').map(a => a.trait),
        potentials: Object.values(answers).filter(a => a.category === 'potential' || a.category === 'career').map(a => a.trait),
        answers: answers
      };
      localStorage.setItem('profile', JSON.stringify(localProfile));
      setIsComplete(true);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isComplete) {
    return (
      <div className="min-h-screen hero-bg flex items-center justify-center px-6" data-testid="questionnaire-complete">
        <div className="text-center space-y-8 max-w-lg animate-scale-in">
          <div className="w-24 h-24 mx-auto rounded-full bg-gradient-to-br from-green-400 to-emerald-500 flex items-center justify-center">
            <CheckCircle className="w-12 h-12 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-white">Questionnaire terminé !</h1>
          <p className="text-white/60 text-lg">
            Votre profil professionnel a été généré avec succès. Découvrez maintenant votre carte d'identité Pro.
          </p>
          <Link
            to="/carte-identite"
            className="btn-primary px-8 py-4 rounded-full font-semibold text-white inline-flex items-center justify-center gap-2"
            data-testid="view-results-btn"
          >
            Voir mes résultats
            <ChevronRight className="w-5 h-5" />
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen hero-bg" data-testid="questionnaire-page">
      {/* Header */}
      <header className="px-6 py-6 flex items-center justify-between max-w-4xl mx-auto">
        <Link to="/" className="flex items-center gap-2 text-white/60 hover:text-white transition-colors" data-testid="back-home-link">
          <ArrowLeft className="w-5 h-5" />
          <span>Retour</span>
        </Link>
        <span className="text-white/60 text-sm">
          Question {currentQuestion + 1} sur {questions.length}
        </span>
      </header>

      {/* Progress Bar */}
      <div className="max-w-4xl mx-auto px-6 mb-12">
        <div className="h-2 bg-white/10 rounded-full overflow-hidden">
          <div 
            className="progress-bar h-full rounded-full transition-all duration-500"
            style={{ width: `${progress}%` }}
            data-testid="progress-bar"
          />
        </div>
      </div>

      {/* Question Card */}
      <main className="max-w-3xl mx-auto px-6 pb-20">
        <div className="question-card animate-fade-in-up" data-testid={`question-${question.id}`}>
          <div className="mb-8">
            <span className="text-sm text-purple-400 font-medium uppercase tracking-wider">
              {question.category === 'soft_skills' && 'Compétences'}
              {question.category === 'values' && 'Valeurs'}
              {question.category === 'potential' && 'Potentiel'}
              {question.category === 'career' && 'Carrière'}
            </span>
            <h2 className="text-2xl md:text-3xl font-bold text-white mt-2">
              {question.question}
            </h2>
          </div>

          <div className="space-y-4">
            {question.options.map((option, index) => (
              <button
                key={option.value}
                onClick={() => handleAnswer(option.value)}
                className={`answer-option w-full text-left ${
                  answers[question.id]?.value === option.value ? 'selected' : ''
                }`}
                data-testid={`option-${option.value}`}
              >
                <div className="flex items-center gap-4">
                  <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all ${
                    answers[question.id]?.value === option.value 
                      ? 'border-purple-500 bg-purple-500' 
                      : 'border-white/30'
                  }`}>
                    {answers[question.id]?.value === option.value && (
                      <div className="w-2 h-2 bg-white rounded-full" />
                    )}
                  </div>
                  <span className="text-white/90">{option.label}</span>
                </div>
              </button>
            ))}
          </div>

          {/* Navigation */}
          <div className="flex justify-between mt-10 pt-6 border-t border-white/10">
            <button
              onClick={handlePrevious}
              disabled={currentQuestion === 0}
              className="px-6 py-3 rounded-full font-medium text-white/60 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
              data-testid="prev-question-btn"
            >
              <ArrowLeft className="w-4 h-4" />
              Précédent
            </button>
            <button
              onClick={handleNext}
              disabled={!answers[question.id] || isSubmitting}
              className="btn-primary px-8 py-3 rounded-full font-semibold text-white flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              data-testid="next-question-btn"
            >
              {isSubmitting ? (
                'Analyse en cours...'
              ) : currentQuestion === questions.length - 1 ? (
                <>
                  Terminer
                  <CheckCircle className="w-4 h-4" />
                </>
              ) : (
                <>
                  Suivant
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </div>
      </main>
    </div>
  );
};
