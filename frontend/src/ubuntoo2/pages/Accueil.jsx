import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Users, Compass, MessageSquare, HandHeart, ChevronRight, UserPlus, Loader2, GraduationCap, Award, Info, Sparkles, CheckCircle2 } from "lucide-react";
import { u2, timeAgo, CATEGORIES } from "../api";
import { BadgeChip, ComprendreBadgesDialog } from "./BadgesSection";
import { LoadFail } from "../LoadFail";

export default function Accueil() {
  const [data, setData] = useState(null);
  const [comprendreOpen, setComprendreOpen] = useState(false);
  const navigate = useNavigate();

  const load = () => {
    setData(null);
    u2.get("/dashboard").then(r => setData(r.data)).catch(() => setData("error"));
  };
  useEffect(load, []);

  if (data === "error") return <LoadFail onRetry={load} />;
  if (!data) return <div className="flex justify-center py-16"><Loader2 className="w-8 h-8 animate-spin text-[#C85A32]" /></div>;

  const stats = [
    { label: "Mon réseau", value: data.contacts_count, icon: Users, to: "/ubuntoo/reseau", testid: "stat-reseau" },
    { label: "Mes communautés", value: data.communities?.length || 0, icon: Compass, to: "/ubuntoo/communautes", testid: "stat-communautes" },
    { label: "Mes contributions", value: data.contributions_count, icon: HandHeart, to: "/ubuntoo/communautes", testid: "stat-contributions" },
  ];

  return (
    <div className="space-y-5 u2-animate" data-testid="ubuntoo-accueil">
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold u2-heading tracking-tight">Bonjour <span className="u2-rainbow-text">{data.display_name}</span> 👋🏾</h1>
        <p className="text-sm text-stone-500 mt-1">De qui ou de quoi avez-vous besoin pour avancer aujourd'hui ?</p>
      </div>

      {data.pending_requests > 0 && (
        <button onClick={() => navigate("/ubuntoo/reseau")} className="w-full text-left rounded-2xl border border-amber-200 bg-amber-50 p-4 flex items-center justify-between hover:bg-amber-100 transition-colors" data-testid="pending-requests-banner">
          <div className="flex items-center gap-3">
            <UserPlus className="w-5 h-5 text-amber-700" />
            <span className="text-sm font-medium text-amber-900">{data.pending_requests} demande{data.pending_requests > 1 ? "s" : ""} de mise en relation en attente</span>
          </div>
          <ChevronRight className="w-4 h-4 text-amber-600" />
        </button>
      )}

      {/* Point de départ : mon parcours de contribution */}
      {data.progression && (
        <div className="rounded-2xl u2-hero-rainbow p-5 text-white u2-lift" data-testid="contribution-path-card">
          <div className="flex items-start justify-between gap-3 flex-wrap">
            <div>
              <div className="flex items-center gap-2 text-[11px] uppercase tracking-wider text-white/70 font-semibold"><Sparkles className="w-3.5 h-3.5" />Mon parcours de contribution</div>
              <div className="text-xl font-extrabold u2-heading mt-1" data-testid="home-current-level">Vous êtes {data.progression.current_label}</div>
              <p className="text-sm text-white/85 mt-1">Tout le monde possède quelque chose à transmettre — chaque contribution compte.</p>
            </div>
            <div className="flex gap-1.5">
              {(data.progression.parcours || []).map(p => (
                <span key={p.id} title={p.label} className={`h-2.5 w-2.5 rounded-full ${p.complete ? "bg-emerald-300" : "bg-white/30"}`} />
              ))}
            </div>
          </div>
          {data.progression.next_steps?.length > 0 && (
            <div className="mt-3 space-y-1.5" data-testid="home-suggestions">
              {data.progression.next_steps.slice(0, 2).map((s, i) => (
                <div key={i} className="flex items-start gap-2 text-sm text-white/90">
                  <CheckCircle2 className="w-4 h-4 mt-0.5 shrink-0 text-amber-300" />{s}
                </div>
              ))}
            </div>
          )}
          <div className="mt-4 flex gap-2 flex-wrap">
            <Button size="sm" className="rounded-xl bg-white text-[#2c2250] hover:bg-orange-50 font-semibold" onClick={() => navigate("/ubuntoo/profil")} data-testid="home-badges-btn">
              <Award className="w-4 h-4 mr-1.5" />Mes badges & parcours
            </Button>
            <Button size="sm" variant="outline" className="rounded-xl border-white/40 bg-transparent text-white hover:bg-white/10 hover:text-white" onClick={() => setComprendreOpen(true)} data-testid="home-comprendre-btn">
              <Info className="w-4 h-4 mr-1.5" />Comprendre les badges
            </Button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-3 gap-3">
        {stats.map(s => {
          const Icon = s.icon;
          return (
            <button key={s.label} onClick={() => navigate(s.to)} data-testid={s.testid}
              className="rounded-2xl bg-white border border-[#E2DFD8] p-4 text-left u2-lift hover:border-orange-300">
              <Icon className="w-5 h-5 text-[#C85A32] mb-2" />
              <div className="text-2xl font-extrabold u2-heading">{s.value}</div>
              <div className="text-xs text-stone-500 leading-tight mt-0.5">{s.label}</div>
            </button>
          );
        })}
      </div>

      {/* Contacts récents */}
      <Card className="rounded-2xl border border-[#E2DFD8] shadow-none bg-white">
        <CardContent className="p-5">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-base font-semibold u2-heading">Contacts récents</h3>
            <Button variant="ghost" size="sm" className="text-xs text-[#C85A32]" onClick={() => navigate("/ubuntoo/reseau")} data-testid="see-all-contacts-btn">Voir tout</Button>
          </div>
          {data.recent_contacts?.length > 0 ? (
            <div className="space-y-2">
              {data.recent_contacts.map(c => (
                <div key={c.token_id} className="flex items-center gap-3 py-1.5">
                  <div className="h-9 w-9 rounded-full bg-[#E09F3E]/20 text-[#A84624] flex items-center justify-center text-sm font-bold shrink-0">{(c.display_name || "?")[0].toUpperCase()}</div>
                  <div className="min-w-0">
                    <div className="text-sm font-medium truncate">{c.display_name}</div>
                    {c.headline && <div className="text-xs text-stone-400 truncate">{c.headline}</div>}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-4">
              <p className="text-sm text-stone-400 mb-3">Votre réseau démarre ici. Toute mise en relation repose sur l'accord mutuel des deux membres.</p>
              <Button size="sm" className="rounded-xl u2-btn-primary" onClick={() => navigate("/ubuntoo/reseau")} data-testid="find-members-btn">
                <Users className="w-3.5 h-3.5 mr-1.5" />Trouver des membres
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Mes communautés */}
      <Card className="rounded-2xl border border-[#E2DFD8] shadow-none bg-white">
        <CardContent className="p-5">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-base font-semibold u2-heading">Mes communautés</h3>
            <Button variant="ghost" size="sm" className="text-xs text-[#C85A32]" onClick={() => navigate("/ubuntoo/communautes")} data-testid="explore-communities-btn">Explorer</Button>
          </div>
          {data.communities?.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {data.communities.map(c => (
                <button key={c.id} onClick={() => navigate(`/ubuntoo/communautes/${c.id}`)}
                  className="rounded-full border border-[#E2DFD8] bg-[#FAF8F5] px-3 py-1.5 text-xs font-medium text-stone-700 hover:border-orange-300 transition-colors" data-testid={`my-community-${c.id}`}>
                  {c.name} <span className="text-stone-400">· {CATEGORIES[c.category]}</span>
                </button>
              ))}
            </div>
          ) : (
            <p className="text-sm text-stone-400">Rejoignez une communauté métier, situation, territoire ou thématique pour échanger.</p>
          )}
        </CardContent>
      </Card>

      {/* Conversations récentes */}
      <Card className="rounded-2xl border border-[#E2DFD8] shadow-none bg-white">
        <CardContent className="p-5">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-base font-semibold u2-heading">Mes conversations</h3>
            <Button variant="ghost" size="sm" className="text-xs text-[#C85A32]" onClick={() => navigate("/ubuntoo/messages")} data-testid="see-messages-btn">Messagerie</Button>
          </div>
          {data.recent_conversations?.length > 0 ? (
            <div className="space-y-2">
              {data.recent_conversations.map(c => (
                <button key={c.id} onClick={() => navigate("/ubuntoo/messages")} className="w-full flex items-center gap-3 py-1.5 text-left">
                  <MessageSquare className="w-4 h-4 text-stone-400 shrink-0" />
                  <div className="min-w-0 flex-1">
                    <div className="text-sm font-medium truncate">{c.other_name}</div>
                    <div className="text-xs text-stone-400 truncate">{c.last_message_text || "Conversation ouverte"}</div>
                  </div>
                  <span className="text-[11px] text-stone-400 shrink-0">{timeAgo(c.last_message_at)}</span>
                </button>
              ))}
            </div>
          ) : (
            <p className="text-sm text-stone-400">Aucune conversation. La messagerie s'ouvre entre contacts acceptés.</p>
          )}
        </CardContent>
      </Card>

      {/* Mentorat */}
      <Card className="rounded-2xl border border-[#E2DFD8] shadow-none bg-white">
        <CardContent className="p-5">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-base font-semibold u2-heading flex items-center gap-1.5"><GraduationCap className="w-4 h-4 text-violet-600" />Mon mentor / mes mentorés</h3>
            <Button variant="ghost" size="sm" className="text-xs text-[#C85A32]" onClick={() => navigate("/ubuntoo/reseau?tab=mentorat")} data-testid="go-mentorat-btn">Mentorat</Button>
          </div>
          {(data.mentoring?.mentors?.length > 0 || data.mentoring?.mentores?.length > 0) ? (
            <div className="space-y-1 text-sm text-stone-700" data-testid="mentoring-summary">
              {data.mentoring.mentors.length > 0 && <p>Mon mentor : <span className="font-medium">{data.mentoring.mentors.join(", ")}</span></p>}
              {data.mentoring.mentores.length > 0 && <p>Mes mentoré(e)s : <span className="font-medium">{data.mentoring.mentores.join(", ")}</span></p>}
            </div>
          ) : (
            <p className="text-sm text-stone-400">
              {data.mentoring?.role === "none" ? "Indiquez si vous souhaitez être accompagné(e) ou devenir mentor." : "Aucune relation de mentorat pour le moment — consultez les suggestions."}
            </p>
          )}
        </CardContent>
      </Card>

      {/* Badges */}
      <Card className="rounded-2xl border border-[#E2DFD8] shadow-none bg-white">
        <CardContent className="p-5">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-base font-semibold u2-heading flex items-center gap-1.5"><Award className="w-4 h-4 text-[#E09F3E]" />Mes badges</h3>
            <Button variant="ghost" size="sm" className="text-xs text-[#C85A32]" onClick={() => navigate("/ubuntoo/profil")} data-testid="go-badges-btn">Voir tout</Button>
          </div>
          {data.badges?.length > 0 ? (
            <div className="flex flex-wrap gap-1.5" data-testid="my-badges">
              {data.badges.map(b => <BadgeChip key={b.id} badgeId={b.id} />)}
            </div>
          ) : (
            <p className="text-sm text-stone-400">Complétez votre profil et participez à une communauté pour obtenir votre premier badge.</p>
          )}
        </CardContent>
      </Card>

      <p className="text-xs text-stone-400 text-center px-4">Sur Ubuntoo, pas de course aux likes : valorisez les contributions réellement utiles.</p>
      <ComprendreBadgesDialog open={comprendreOpen} onOpenChange={setComprendreOpen} />
    </div>
  );
}
