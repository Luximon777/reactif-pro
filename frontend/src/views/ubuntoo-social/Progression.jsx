import { useState, useEffect } from 'react';
import { progressionApi } from './api';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent } from '@/components/ui/dialog';
import { toast } from 'sonner';
import {
  Compass, Sprout, Megaphone, Award, GraduationCap, Crown, Gem,
  CheckCircle2, Circle, Lock, Sparkles, TrendingUp, ScrollText, Loader2,
  HandHeart, BookOpen, CalendarCheck, HeartHandshake
} from 'lucide-react';

const LEVEL_ICONS = {
  compass: Compass, sprout: Sprout, megaphone: Megaphone, award: Award,
  'graduation-cap': GraduationCap, crown: Crown, gem: Gem,
};

const LEVEL_COLORS = {
  explorateur: '#2A9D8F', contributeur: '#0F4C5C', ambassadeur: '#E36414',
  expert: '#9A031E', mentor: '#5F0F40', leader: '#B8860B', pionnier: '#7B2CBF',
};

const DIMENSIONS = [
  { key: 'contribution', label: 'Contribution', icon: HandHeart, color: '#E36414', desc: 'Publications, ressources, aide apportée' },
  { key: 'expertise', label: 'Expertise', icon: BookOpen, color: '#0F4C5C', desc: "Compétences reconnues et certifications RE'ACTIF PRO" },
  { key: 'engagement', label: 'Engagement', icon: CalendarCheck, color: '#2A9D8F', desc: 'Ancienneté, régularité, participation' },
  { key: 'impact', label: 'Impact humain', icon: HeartHandshake, color: '#9A031E', desc: 'Mentorat, recommandations, réussites accompagnées' },
];

export default function Progression() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [accepting, setAccepting] = useState(false);
  const [celebrate, setCelebrate] = useState(false);
  const [expandedLevel, setExpandedLevel] = useState(null);

  const load = async () => {
    try {
      const res = await progressionApi.get();
      setData(res.data);
      if (res.data.level_up) setCelebrate(true);
    } catch {
      /* ignore */
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const acceptCharter = async () => {
    setAccepting(true);
    try {
      await progressionApi.acceptCharter();
      toast.success('Charte éthique acceptée. Bienvenue dans la communauté !');
      await load();
    } catch {
      toast.error("Erreur lors de l'acceptation de la charte");
    } finally {
      setAccepting(false);
    }
  };

  if (loading) {
    return (
      <div className="ubuntoo-card p-6 mb-8 flex justify-center">
        <Loader2 className="animate-spin text-[#0F4C5C]" size={24} />
      </div>
    );
  }
  if (!data) return null;

  const { current_level, next_level, levels, dimensions, stats } = data;
  const CurrentIcon = current_level ? LEVEL_ICONS[current_level.icon] : Compass;
  const currentColor = current_level ? LEVEL_COLORS[current_level.id] : '#94A3B8';
  const charterNeeded = !stats.charter_accepted;

  return (
    <div className="ubuntoo-card p-6 md:p-8 mb-8 animate-fade-in" data-testid="ubuntoo-progression">
      {/* Header : niveau actuel */}
      <div className="flex flex-col sm:flex-row items-center gap-5 mb-8">
        <div
          className="w-20 h-20 rounded-2xl flex items-center justify-center shrink-0 shadow-lg"
          style={{ backgroundColor: currentColor }}
          data-testid="current-level-badge"
        >
          <CurrentIcon size={40} className="text-white" />
        </div>
        <div className="flex-1 text-center sm:text-left">
          <p className="text-xs uppercase tracking-widest text-[#5C5C5C] font-semibold">Mon parcours Ubuntoo</p>
          <h2 className="text-2xl font-bold text-[#1A1A1A]" style={{ fontFamily: 'Manrope, sans-serif' }}>
            {current_level ? current_level.name : 'En route vers Explorateur'}
          </h2>
          <p className="text-sm text-[#5C5C5C]">{current_level ? current_level.tagline : 'Complétez votre profil et acceptez la charte pour débuter votre parcours.'}</p>
        </div>
        {next_level && (
          <div className="text-center sm:text-right shrink-0">
            <p className="text-[10px] uppercase tracking-wider text-[#5C5C5C]">Prochain niveau</p>
            <p className="text-sm font-bold" style={{ color: LEVEL_COLORS[next_level.id] }}>{next_level.name}</p>
            <p className="text-xs text-[#5C5C5C]">
              {next_level.criteria.filter((c) => c.met).length}/{next_level.criteria.length} critères
            </p>
          </div>
        )}
      </div>

      {/* Chemin de progression */}
      <div className="flex items-center justify-between mb-8 overflow-x-auto pb-2" data-testid="progression-path">
        {levels.map((lvl, i) => {
          const Icon = LEVEL_ICONS[lvl.icon];
          const color = LEVEL_COLORS[lvl.id];
          const state = lvl.achieved ? 'achieved' : (next_level && lvl.id === next_level.id ? 'next' : 'locked');
          return (
            <div key={lvl.id} className="flex items-center flex-1 min-w-[70px]">
              <button
                onClick={() => setExpandedLevel(expandedLevel === lvl.id ? null : lvl.id)}
                className="flex flex-col items-center gap-1.5 group mx-auto"
                data-testid={`level-node-${lvl.id}`}
              >
                <div
                  className={`w-11 h-11 rounded-full flex items-center justify-center border-2 transition-all group-hover:scale-110 ${
                    state === 'achieved' ? 'shadow-md' : ''
                  }`}
                  style={{
                    backgroundColor: state === 'achieved' ? color : state === 'next' ? '#fff' : '#F5F2EB',
                    borderColor: state === 'locked' ? '#E5E0D8' : color,
                  }}
                >
                  {state === 'locked'
                    ? <Lock size={16} className="text-[#B0AA9E]" />
                    : <Icon size={20} style={{ color: state === 'achieved' ? '#fff' : color }} />}
                </div>
                <span className={`text-[10px] font-medium text-center leading-tight ${state === 'locked' ? 'text-[#B0AA9E]' : 'text-[#1A1A1A]'}`}>
                  {lvl.name.replace(' Communautaire', '').replace(' Ubuntoo', '')}
                </span>
              </button>
              {i < levels.length - 1 && (
                <div className="h-0.5 flex-1 mx-1 rounded-full mb-4" style={{ backgroundColor: lvl.achieved ? color : '#E5E0D8' }} />
              )}
            </div>
          );
        })}
      </div>

      {/* Détail d'un niveau cliqué */}
      {expandedLevel && (() => {
        const lvl = levels.find((l) => l.id === expandedLevel);
        const color = LEVEL_COLORS[lvl.id];
        return (
          <div className="rounded-2xl border-2 p-5 mb-8 animate-fade-in" style={{ borderColor: `${color}40`, backgroundColor: `${color}08` }} data-testid="level-detail">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-bold text-[#1A1A1A]" style={{ fontFamily: 'Manrope, sans-serif' }}>
                {lvl.name} — <span className="font-normal text-sm text-[#5C5C5C]">{lvl.tagline}</span>
              </h3>
              {lvl.achieved && <span className="text-xs font-medium px-3 py-1 rounded-full text-white" style={{ backgroundColor: color }}>✓ Acquis</span>}
            </div>
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-[#5C5C5C] mb-2">Critères</p>
                <ul className="space-y-1.5">
                  {lvl.criteria.map((c, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm">
                      {c.met
                        ? <CheckCircle2 size={16} className="text-[#2A9D8F] mt-0.5 shrink-0" />
                        : <Circle size={16} className="text-[#B0AA9E] mt-0.5 shrink-0" />}
                      <span className={c.met ? 'text-[#1A1A1A]' : 'text-[#5C5C5C]'}>
                        {c.label}
                        {c.detail && <span className="ml-1 text-xs text-[#5C5C5C]">({c.detail})</span>}
                      </span>
                    </li>
                  ))}
                </ul>
                {lvl.id === 'pionnier' && (
                  <p className="text-xs italic text-[#5C5C5C] mt-2">Attribué par un comité (ALT&ACT + communauté), indépendamment des points.</p>
                )}
              </div>
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-[#5C5C5C] mb-2">Débloque</p>
                <ul className="space-y-1.5">
                  {lvl.unlocks.map((u, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-[#1A1A1A]">
                      <Sparkles size={14} className="mt-0.5 shrink-0" style={{ color }} />
                      {u}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        );
      })()}

      {/* Charte éthique */}
      {charterNeeded && (
        <div className="flex flex-col sm:flex-row items-center gap-3 rounded-2xl bg-[#FEF0E3] border border-[#E36414]/30 p-4 mb-8" data-testid="charter-banner">
          <ScrollText size={22} className="text-[#E36414] shrink-0" />
          <p className="text-sm text-[#1A1A1A] flex-1 text-center sm:text-left">
            <strong>Charte éthique Ubuntoo</strong> — Je m'engage à respecter les valeurs de solidarité, d'inclusion, de bienveillance et de coopération de la communauté.
          </p>
          <Button onClick={acceptCharter} disabled={accepting} className="btn-primary shrink-0" data-testid="accept-charter-btn">
            {accepting ? <Loader2 className="animate-spin mr-2" size={14} /> : null}
            J'accepte la charte
          </Button>
        </div>
      )}

      {/* 4 dimensions */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp size={18} className="text-[#0F4C5C]" />
          <h3 className="font-bold text-[#1A1A1A]" style={{ fontFamily: 'Manrope, sans-serif' }}>Mes 4 dimensions</h3>
        </div>
        <div className="grid sm:grid-cols-2 gap-4">
          {DIMENSIONS.map((d) => {
            const Icon = d.icon;
            const val = dimensions[d.key] || 0;
            return (
              <div key={d.key} className="rounded-xl bg-[#F5F2EB] p-4" data-testid={`dimension-${d.key}`}>
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center gap-2">
                    <Icon size={16} style={{ color: d.color }} />
                    <span className="text-sm font-semibold text-[#1A1A1A]">{d.label}</span>
                  </div>
                  <span className="text-sm font-bold" style={{ color: d.color }}>{val}</span>
                </div>
                <div className="h-2 rounded-full bg-white overflow-hidden">
                  <div className="h-full rounded-full transition-all duration-700" style={{ width: `${val}%`, backgroundColor: d.color }} />
                </div>
                <p className="text-[11px] text-[#5C5C5C] mt-1.5">{d.desc}</p>
              </div>
            );
          })}
        </div>
        <p className="text-[11px] italic text-[#5C5C5C] mt-3">
          Un membre très actif mais peu utile ne progresse pas plus vite qu'un membre moins présent mais ayant un fort impact.
        </p>
      </div>

      {/* Célébration de passage de niveau */}
      <Dialog open={celebrate} onOpenChange={setCelebrate}>
        <DialogContent className="max-w-sm text-center" data-testid="level-up-dialog">
          {current_level && (
            <div className="py-4">
              <div
                className="w-24 h-24 mx-auto rounded-3xl flex items-center justify-center shadow-xl animate-bounce"
                style={{ backgroundColor: currentColor }}
              >
                <CurrentIcon size={48} className="text-white" />
              </div>
              <h3 className="text-2xl font-bold mt-5 text-[#1A1A1A]" style={{ fontFamily: 'Manrope, sans-serif' }}>
                Félicitations ! 🎉
              </h3>
              <p className="text-[#5C5C5C] mt-2">
                Vous êtes désormais <strong style={{ color: currentColor }}>{current_level.name}</strong> de la communauté Ubuntoo.
              </p>
              <div className="text-left mt-4 bg-[#F5F2EB] rounded-xl p-4">
                <p className="text-xs font-bold uppercase tracking-wider text-[#5C5C5C] mb-2">Vous débloquez</p>
                <ul className="space-y-1">
                  {current_level.unlocks.map((u, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-[#1A1A1A]">
                      <Sparkles size={14} className="mt-0.5 shrink-0" style={{ color: currentColor }} /> {u}
                    </li>
                  ))}
                </ul>
              </div>
              <Button onClick={() => setCelebrate(false)} className="btn-primary mt-5 w-full" data-testid="close-celebration-btn">
                Continuer mon parcours
              </Button>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
