import React, { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Switch } from "@/components/ui/switch";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import {
  Sprout, UserCheck, MessageCircle, Compass, HandHeart, BookOpen, Lightbulb, Link2, Gift, Heart, UsersRound, ShieldCheck,
  Lock, CheckCircle2, ArrowRight, Info, Award,
} from "lucide-react";
import { toast } from "sonner";
import { u2, BADGES_META } from "../api";

const ICONS = { Sprout, UserCheck, MessageCircle, Compass, HandHeart, BookOpen, Lightbulb, Link2, Gift, Heart, UsersRound, ShieldCheck };

export const BadgeChip = ({ badgeId, small }) => {
  const meta = BADGES_META[badgeId];
  if (!meta) return null;
  const Icon = ICONS[meta.icon] || Award;
  return (
    <Badge variant="outline" className={`rounded-full gap-1 ${meta.cls} ${small ? "text-[10px] px-1.5" : "text-[11px]"}`} data-testid={`badge-chip-${badgeId}`}>
      <Icon className="w-3 h-3" />{meta.label}
    </Badge>
  );
};

const CATEG_LABELS = {
  premiers: "Premiers badges — accessibles à tous",
  contribution: "Badges de contribution",
  verifie: "Badge vérifié",
};

export const BadgeFicheDialog = ({ badge, open, onOpenChange, onDisplayChange }) => {
  const [saving, setSaving] = useState(false);
  if (!badge) return null;
  const meta = BADGES_META[badge.id] || {};
  const Icon = ICONS[meta.icon] || Award;
  const pct = Math.round((badge.progress.current / badge.progress.target) * 100);
  const toggleDisplay = async (checked) => {
    setSaving(true);
    try {
      await u2.put("/badges/display", { badge_id: badge.id, displayed: checked });
      onDisplayChange?.(badge.id, checked);
      toast.success(checked ? "Badge affiché sur votre profil" : "Badge masqué de votre profil");
    } catch { toast.error("Erreur"); }
    finally { setSaving(false); }
  };
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md rounded-2xl max-h-[85vh] overflow-y-auto" data-testid="badge-fiche-dialog">
        <DialogHeader>
          <DialogTitle className="u2-heading flex items-center gap-2">
            <span className={`h-9 w-9 rounded-xl border flex items-center justify-center ${meta.cls}`}><Icon className="w-4.5 h-4.5 w-4 h-4" /></span>
            {badge.label}
          </DialogTitle>
          <DialogDescription>{badge.desc}</DialogDescription>
        </DialogHeader>
        <div className="space-y-3 text-sm">
          <div className="rounded-xl bg-stone-50 border border-stone-100 p-3">
            <div className="flex items-center justify-between text-xs mb-1.5">
              <span className="font-semibold text-stone-600">Votre progression</span>
              <span className="font-bold text-[#C85A32]" data-testid="badge-progress-text">{badge.progress.current}/{badge.progress.target}</span>
            </div>
            <Progress value={pct} className="h-2" />
            {badge.earned
              ? <p className="text-xs text-emerald-600 mt-1.5 flex items-center gap-1"><CheckCircle2 className="w-3.5 h-3.5" />Badge obtenu</p>
              : <p className="text-xs text-stone-500 mt-1.5">{badge.progress.target - badge.progress.current} action(s) reconnue(s) pour compléter ce badge.</p>}
          </div>
          <div><div className="text-[11px] font-semibold text-stone-400 uppercase tracking-wide mb-0.5">Pourquoi ce badge existe</div><p className="text-stone-600">{badge.pourquoi}</p></div>
          <div><div className="text-[11px] font-semibold text-stone-400 uppercase tracking-wide mb-0.5">Comment l'obtenir</div><p className="text-stone-600">{badge.comment}</p></div>
          <div>
            <div className="text-[11px] font-semibold text-stone-400 uppercase tracking-wide mb-0.5">Actions prises en compte</div>
            <ul className="space-y-0.5">{badge.actions.map((a, i) => <li key={i} className="text-stone-600 flex items-start gap-1.5"><ArrowRight className="w-3.5 h-3.5 mt-0.5 text-[#C85A32] shrink-0" />{a}</li>)}</ul>
          </div>
          <div><div className="text-[11px] font-semibold text-stone-400 uppercase tracking-wide mb-0.5">Ce qu'il permet de valoriser</div><p className="text-stone-600">{badge.valorise}</p></div>
          <div><div className="text-[11px] font-semibold text-stone-400 uppercase tracking-wide mb-0.5">Étape suivante possible</div><p className="text-stone-600">{badge.etape_suivante}</p></div>
          {badge.validation_humaine && (
            <p className="text-xs text-violet-700 bg-violet-50 border border-violet-100 rounded-lg px-3 py-2 flex items-start gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 mt-0.5 shrink-0" />Ce badge repose sur des éléments vérifiés — il n'est pas attribué par simple activité.
            </p>
          )}
          {badge.earned && (
            <div className="flex items-center justify-between rounded-xl border border-stone-100 p-3">
              <span className="text-xs text-stone-600">Afficher ce badge sur mon profil public</span>
              <Switch checked={badge.displayed} onCheckedChange={toggleDisplay} disabled={saving} data-testid="badge-display-switch" />
            </div>
          )}
          <p className="text-[11px] text-stone-400 italic">Un badge reconnaît ce que vous avez apporté aux autres — il ne constitue pas une certification de compétence professionnelle.</p>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export const BadgesGrid = ({ badges, onDisplayChange }) => {
  const [selected, setSelected] = useState(null);
  const categs = ["premiers", "contribution", "verifie"];
  return (
    <div className="space-y-4" data-testid="badges-grid">
      {categs.map(cat => {
        const items = badges.filter(b => b.categorie === cat);
        if (!items.length) return null;
        return (
          <div key={cat}>
            <div className="text-[11px] font-semibold text-stone-400 uppercase tracking-wide mb-2">{CATEG_LABELS[cat]}</div>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {items.map(b => {
                const meta = BADGES_META[b.id] || {};
                const Icon = ICONS[meta.icon] || Award;
                const pct = Math.round((b.progress.current / b.progress.target) * 100);
                return (
                  <button key={b.id} onClick={() => setSelected(b)} data-testid={`badge-card-${b.id}`}
                    className={`rounded-xl border p-3 text-left u2-lift hover:border-orange-300 ${b.earned ? "bg-white border-[#E2DFD8]" : "bg-stone-50/60 border-stone-100"}`}>
                    <div className="flex items-center justify-between mb-1.5">
                      <span className={`h-8 w-8 rounded-lg border flex items-center justify-center ${b.earned ? meta.cls : "bg-stone-100 text-stone-300 border-stone-200"}`}>
                        {b.earned ? <Icon className="w-4 h-4" /> : <Lock className="w-3.5 h-3.5" />}
                      </span>
                      {b.earned
                        ? <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                        : <span className="text-[10px] font-bold text-stone-400">{b.progress.current}/{b.progress.target}</span>}
                    </div>
                    <div className={`text-xs font-semibold leading-tight ${b.earned ? "text-stone-800" : "text-stone-500"}`}>{b.label}</div>
                    {!b.earned && <div className="mt-1.5 h-1 rounded-full bg-stone-200 overflow-hidden"><div className="h-full bg-[#E09F3E]" style={{ width: `${pct}%` }} /></div>}
                  </button>
                );
              })}
            </div>
          </div>
        );
      })}
      <BadgeFicheDialog badge={selected} open={!!selected} onOpenChange={v => !v && setSelected(null)} onDisplayChange={onDisplayChange} />
    </div>
  );
};

export const ComprendreBadgesDialog = ({ open, onOpenChange }) => (
  <Dialog open={open} onOpenChange={onOpenChange}>
    <DialogContent className="max-w-lg rounded-2xl max-h-[85vh] overflow-y-auto" data-testid="comprendre-badges-dialog">
      <DialogHeader>
        <DialogTitle className="u2-heading flex items-center gap-2"><Info className="w-5 h-5 text-[#C85A32]" />Comprendre les badges UBUNTOO</DialogTitle>
        <DialogDescription>Reconnaître l'engagement, l'entraide et la contribution</DialogDescription>
      </DialogHeader>
      <div className="space-y-3 text-sm text-stone-600">
        <div className="rounded-xl bg-orange-50 border border-orange-100 p-3 text-stone-700 font-medium">
          Tout le monde possède quelque chose qu'il peut transmettre aux autres. Une personne en recherche d'emploi peut être contributrice au même titre qu'un salarié, un recruteur ou un employeur.
        </div>
        <div>
          <div className="text-[11px] font-semibold text-stone-400 uppercase tracking-wide mb-1">Pourquoi des badges ?</div>
          <p>Ils reconnaissent et rendent visibles les contributions positives : partager une expérience, aider un membre, faire découvrir un métier, partager une opportunité, accueillir les nouveaux… <strong>Ils ne servent jamais à classer les personnes entre elles.</strong></p>
        </div>
        <div>
          <div className="text-[11px] font-semibold text-stone-400 uppercase tracking-wide mb-1">À quoi servent-ils ?</div>
          <ul className="space-y-1">
            <li><strong>Reconnaître</strong> une action réalisée dans UBUNTOO.</li>
            <li><strong>Encourager</strong> en montrant différentes manières de participer.</li>
            <li><strong>Valoriser</strong> une trace de vos engagements, que vous choisissez d'afficher ou non.</li>
            <li><strong>Progresser</strong> : Membre → Membre actif → Contributeur → Mentor / Animateur → Ambassadeur.</li>
          </ul>
        </div>
        <div>
          <div className="text-[11px] font-semibold text-stone-400 uppercase tracking-wide mb-1">Comment les obtenir ?</div>
          <ul className="space-y-1">
            <li><strong>Automatiquement</strong> : action objective (compléter son profil, premier échange, rejoindre des communautés).</li>
            <li><strong>Confirmé par un membre</strong> : après une interaction, un membre peut reconnaître l'aide reçue (« Cette personne vous a-t-elle été utile ? »). Il ne s'agit pas d'une note.</li>
            <li><strong>Validé par la communauté</strong> : plusieurs membres reconnaissent la qualité de vos contributions (bouton « Utile »).</li>
            <li><strong>Vérifié</strong> : les rôles de confiance (Mentor, Animateur, Ambassadeur) nécessitent une validation humaine.</li>
          </ul>
        </div>
        <div>
          <div className="text-[11px] font-semibold text-stone-400 uppercase tracking-wide mb-1">Devenir Contributeur — accessible à tous</div>
          <p>Le rôle Contributeur ne dépend ni du diplôme, ni du statut, ni de l'âge, ni du réseau. Il dépend des contributions réellement apportées. Quatre parcours y mènent : <strong>entraide</strong>, <strong>expérience</strong>, <strong>réseau</strong> ou <strong>communauté</strong> — deux membres peuvent devenir Contributeur sans avoir les mêmes badges.</p>
        </div>
        <div className="rounded-xl bg-stone-50 border border-stone-100 p-3">
          <p className="text-xs italic">« On ne reconnaît pas ce que la personne prétend être. On reconnaît ce qu'elle a effectivement apporté aux autres. »</p>
          <p className="text-xs mt-1.5 text-stone-500">Je découvre → Je participe → Je partage → J'aide → Je contribue → Je transmets → J'accompagne.</p>
        </div>
        <p className="text-[11px] text-stone-400">UBUNTOO n'affiche ni classement, ni score public, ni compétition. Un badge n'est pas une certification de compétence : il documente des contributions concrètes observées dans la communauté.</p>
      </div>
    </DialogContent>
  </Dialog>
);
