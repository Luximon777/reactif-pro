import React from "react";
import { Badge } from "@/components/ui/badge";
import { Sprout, Compass, HandHeart, GraduationCap, Award, ShieldCheck, Lock } from "lucide-react";
import { BADGES_META } from "../api";

const ICONS = { Sprout, Compass, HandHeart, GraduationCap, Award, ShieldCheck };

export const BadgeChip = ({ badgeId, small }) => {
  const meta = BADGES_META[badgeId];
  if (!meta) return null;
  const Icon = ICONS[meta.icon] || Award;
  return (
    <Badge className={`rounded-full border hover:bg-inherit ${meta.cls} ${small ? "text-[10px]" : "text-xs"}`} data-testid={`badge-chip-${badgeId}`}>
      <Icon className="w-3 h-3 mr-1" />{meta.label}
    </Badge>
  );
};

export const BadgesGrid = ({ badges }) => (
  <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5" data-testid="badges-grid">
    {badges.map(b => {
      const meta = BADGES_META[b.id] || {};
      const Icon = ICONS[meta.icon] || Award;
      return (
        <div key={b.id} data-testid={`badge-card-${b.id}`}
          className={`rounded-2xl border p-3.5 flex flex-col gap-1.5 ${b.earned ? "bg-white border-orange-200" : "bg-stone-50 border-[#E2DFD8] opacity-60"}`}>
          <div className={`h-9 w-9 rounded-xl flex items-center justify-center ${b.earned ? "bg-[#C85A32] text-white" : "bg-stone-200 text-stone-400"}`}>
            {b.earned ? <Icon className="w-4.5 h-4.5 w-4 h-4" /> : <Lock className="w-4 h-4" />}
          </div>
          <div className="text-xs font-semibold u2-heading leading-tight">{b.label}</div>
          <div className="text-[10px] text-stone-400 leading-tight">{b.desc}</div>
        </div>
      );
    })}
  </div>
);
