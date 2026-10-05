import React, { useState, useEffect, useCallback } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { GraduationCap, HandHeart, Loader2, Save, UserPlus, X, Sparkles } from "lucide-react";
import { toast } from "sonner";
import { u2 } from "../api";

const ROLES = [
  { value: "mentee", label: "Je souhaite être accompagné(e)", desc: "Un mentor partage son expérience pour faire avancer votre projet", icon: Sparkles },
  { value: "mentor", label: "Je souhaite devenir mentor", desc: "Transmettez votre expérience et accompagnez un membre", icon: GraduationCap },
];

const MentoratRequestDialog = ({ match, open, onOpenChange, onSent }) => {
  const [message, setMessage] = useState("");
  const [sending, setSending] = useState(false);
  if (!match) return null;
  const asRole = match.propose_as === "mentor" ? "mentee" : "mentor";
  const send = async () => {
    setSending(true);
    try {
      await u2.post("/connections", { to_id: match.token_id, message, kind: "mentorat", as_role: asRole });
      toast.success(`Demande de mentorat envoyée à ${match.display_name}`);
      onSent?.();
      onOpenChange(false);
      setMessage("");
    } catch (e) { toast.error(e.response?.data?.detail || "Erreur"); }
    finally { setSending(false); }
  };
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md rounded-2xl" data-testid="mentorat-request-dialog">
        <DialogHeader>
          <DialogTitle className="u2-heading">{asRole === "mentee" ? `Demander ${match.display_name} comme mentor` : `Proposer votre accompagnement à ${match.display_name}`}</DialogTitle>
          <DialogDescription>La mise en relation reste soumise au consentement des deux personnes.</DialogDescription>
        </DialogHeader>
        <Textarea value={message} onChange={e => setMessage(e.target.value)} rows={3} maxLength={300}
          placeholder="Présentez votre objectif ou ce que vous pouvez apporter…" className="rounded-xl" data-testid="mentorat-message-input" />
        <div className="flex justify-end gap-2">
          <Button variant="outline" className="rounded-xl" onClick={() => onOpenChange(false)}>Annuler</Button>
          <Button className="rounded-xl u2-btn-primary" onClick={send} disabled={sending} data-testid="send-mentorat-request-btn">
            {sending ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <UserPlus className="w-4 h-4 mr-2" />}Envoyer
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default function MentoratTab() {
  const [profile, setProfile] = useState(null);
  const [topicInput, setTopicInput] = useState("");
  const [saving, setSaving] = useState(false);
  const [matches, setMatches] = useState([]);
  const [relations, setRelations] = useState({ mentors: [], mentores: [], relations: [] });
  const [loadingMatches, setLoadingMatches] = useState(false);
  const [requestMatch, setRequestMatch] = useState(null);
  const [terminateRel, setTerminateRel] = useState(null);
  const [bilan, setBilan] = useState("");
  const [feedbackRel, setFeedbackRel] = useState(null);
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState("");
  const [acting, setActing] = useState(false);

  const loadMatches = useCallback(async () => {
    setLoadingMatches(true);
    try {
      const [m, r] = await Promise.all([u2.get("/mentoring/matches"), u2.get("/mentoring/relations")]);
      setMatches(m.data.matches || []);
      setRelations(r.data);
    } catch { /* silent */ }
    finally { setLoadingMatches(false); }
  }, []);

  useEffect(() => {
    u2.get("/me").then(r => {
      setProfile(r.data);
      if (r.data.mentoring_role !== "none") loadMatches();
    }).catch(() => {});
  }, [loadMatches]);

  const toggleRole = (role) => {
    setProfile(p => {
      const cur = p.mentoring_role || "none";
      let next;
      if (cur === role) next = "none";
      else if (cur === "none") next = role;
      else if (cur === "both") next = role === "mentor" ? "mentee" : "mentor";
      else next = "both";
      return { ...p, mentoring_role: next };
    });
  };

  const addTopic = () => {
    const t = topicInput.trim();
    if (!t) return;
    setProfile(p => ({ ...p, mentoring_topics: [...new Set([...(p.mentoring_topics || []), t])] }));
    setTopicInput("");
  };

  const save = async () => {
    setSaving(true);
    try {
      await u2.put("/me", {
        mentoring_role: profile.mentoring_role || "none",
        mentoring_topics: profile.mentoring_topics || [],
        mentoring_goal: profile.mentoring_goal || "",
      });
      toast.success("Préférences de mentorat enregistrées");
      if (profile.mentoring_role !== "none") loadMatches();
      else { setMatches([]); }
    } catch { toast.error("Erreur"); }
    finally { setSaving(false); }
  };

  if (!profile) return <div className="flex justify-center py-10"><Loader2 className="w-7 h-7 animate-spin text-[#C85A32]" /></div>;

  const role = profile.mentoring_role || "none";
  const isActive = (r) => role === r || role === "both";

  return (
    <div className="space-y-4 mt-4" data-testid="mentorat-tab">
      {/* Relations de mentorat */}
      {relations.relations?.length > 0 && (
        <Card className="rounded-2xl border border-violet-200 shadow-none bg-violet-50/40">
          <CardContent className="p-4 space-y-2">
            <h3 className="text-sm font-semibold u2-heading flex items-center gap-1.5"><GraduationCap className="w-4 h-4 text-violet-600" />Mon mentorat</h3>
            <p className="text-[11px] text-stone-400">Demande → Acceptation → Objectif → Échanges → Actions → Bilan</p>
            {relations.relations.map(r => (
              <div key={r.conn_id} className="bg-white rounded-xl border border-[#E2DFD8] p-3 space-y-1.5" data-testid={`mentorat-relation-${r.conn_id}`}>
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-sm font-semibold">{r.other?.display_name}</span>
                  <Badge variant="outline" className="rounded-full text-[10px]">{r.my_role === "mentor" ? "Mon mentoré(e)" : "Mon mentor"}</Badge>
                  <Badge className={`rounded-full text-[10px] border hover:bg-inherit ${r.mentorat_status === "termine" ? "bg-stone-100 text-stone-500 border-stone-200" : "bg-emerald-50 text-emerald-700 border-emerald-200"}`}>
                    {r.mentorat_status === "termine" ? "Terminé" : "En cours"}
                  </Badge>
                </div>
                {r.objective && <p className="text-xs text-stone-500">Objectif : {r.objective}</p>}
                {r.bilan && <p className="text-xs text-stone-500 italic">Bilan : {r.bilan}</p>}
                <div className="flex gap-2 flex-wrap">
                  {r.mentorat_status !== "termine" && (
                    <Button size="sm" variant="outline" className="rounded-xl h-7 text-xs" onClick={() => { setTerminateRel(r); setBilan(""); }} data-testid={`terminate-mentorat-${r.conn_id}`}>
                      Clôturer avec un bilan
                    </Button>
                  )}
                  {r.my_role === "mentee" && r.mentorat_status === "termine" && !r.feedback_given && (
                    <Button size="sm" className="rounded-xl h-7 text-xs u2-btn-primary" onClick={() => { setFeedbackRel(r); setRating(0); setComment(""); }} data-testid={`feedback-mentorat-${r.conn_id}`}>
                      Donner un retour confidentiel
                    </Button>
                  )}
                  {r.my_role === "mentee" && r.feedback_given && <span className="text-[11px] text-emerald-600">Retour confidentiel transmis ✓</span>}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Choix du rôle */}
      <div className="grid gap-3 sm:grid-cols-2">
        {ROLES.map(r => {
          const Icon = r.icon;
          const active = isActive(r.value);
          return (
            <button key={r.value} onClick={() => toggleRole(r.value)} data-testid={`mentoring-role-${r.value}`}
              className={`rounded-2xl border p-4 text-left transition-colors ${active ? "bg-[#C85A32] text-white border-transparent shadow" : "bg-white border-[#E2DFD8] hover:border-orange-300"}`}>
              <Icon className={`w-5 h-5 mb-2 ${active ? "text-white" : "text-[#C85A32]"}`} />
              <div className="text-sm font-semibold u2-heading">{r.label}</div>
              <div className={`text-xs mt-1 leading-snug ${active ? "text-white/80" : "text-stone-400"}`}>{r.desc}</div>
            </button>
          );
        })}
      </div>

      {role !== "none" && (
        <Card className="rounded-2xl border border-[#E2DFD8] shadow-none bg-white">
          <CardContent className="p-4 space-y-3">
            {isActive("mentor") && (
              <p className="text-[11px] text-violet-700 bg-violet-50 border border-violet-100 rounded-lg px-3 py-2" data-testid="mentor-validation-hint">
                Le statut « Mentor UBUNTOO » est un rôle de confiance validé : acceptez la charte et candidatez depuis Profil → Mon parcours UBUNTOO.
              </p>
            )}
            <div>
              <label className="text-xs font-semibold text-stone-500 uppercase tracking-wide">Domaines de mentorat (métier, secteur, compétence…)</label>
              <div className="flex gap-2 mt-1.5">
                <Input value={topicInput} onChange={e => setTopicInput(e.target.value)} onKeyDown={e => e.key === "Enter" && addTopic()}
                  placeholder="Ex : restauration, management, reconversion…" className="rounded-xl text-sm" data-testid="mentoring-topic-input" />
                <Button variant="outline" className="rounded-xl shrink-0" onClick={addTopic} data-testid="add-topic-btn">Ajouter</Button>
              </div>
              {profile.mentoring_topics?.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mt-2">
                  {profile.mentoring_topics.map(t => (
                    <Badge key={t} variant="outline" className="rounded-full text-xs border-[#E2DFD8]">
                      {t}<button className="ml-1" onClick={() => setProfile(p => ({ ...p, mentoring_topics: p.mentoring_topics.filter(x => x !== t) }))}><X className="w-3 h-3" /></button>
                    </Badge>
                  ))}
                </div>
              )}
            </div>
            {isActive("mentee") && (
              <div>
                <label className="text-xs font-semibold text-stone-500 uppercase tracking-wide">Mon objectif d'accompagnement</label>
                <Textarea value={profile.mentoring_goal || ""} onChange={e => setProfile(p => ({ ...p, mentoring_goal: e.target.value }))}
                  rows={2} maxLength={300} placeholder="Ex : préparer ma reconversion vers…" className="rounded-xl text-sm mt-1.5" data-testid="mentoring-goal-input" />
              </div>
            )}
            <div className="flex justify-end">
              <Button size="sm" className="rounded-xl u2-btn-primary" onClick={save} disabled={saving} data-testid="save-mentoring-btn">
                {saving ? <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" /> : <Save className="w-3.5 h-3.5 mr-1.5" />}Enregistrer
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Suggestions */}
      {role !== "none" && (
        <div>
          <h3 className="text-sm font-semibold u2-heading mb-2">Suggestions de rapprochement</h3>
          <p className="text-xs text-stone-400 mb-3">Rapprochement selon métier, compétences, centres d'intérêt et domaines. La décision finale vous appartient toujours.</p>
          {loadingMatches ? <div className="flex justify-center py-6"><Loader2 className="w-6 h-6 animate-spin text-[#C85A32]" /></div> : (
            <div className="space-y-2">
              {matches.map(m => (
                <Card key={m.token_id} className="rounded-2xl border border-[#E2DFD8] shadow-none bg-white" data-testid={`mentoring-match-${m.token_id}`}>
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-full bg-[#E09F3E]/20 text-[#A84624] flex items-center justify-center text-sm font-bold shrink-0">{(m.display_name || "?")[0].toUpperCase()}</div>
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-sm font-semibold">{m.display_name}</span>
                          <Badge className={`rounded-full text-[10px] border hover:bg-inherit ${m.propose_as === "mentor" ? "bg-violet-50 text-violet-700 border-violet-200" : "bg-emerald-50 text-emerald-700 border-emerald-200"}`}>
                            {m.propose_as === "mentor" ? "Mentor potentiel" : "Cherche un mentor"}
                          </Badge>
                          <Badge variant="outline" className="rounded-full text-[10px] border-orange-200 text-orange-700">Affinité {m.match_score}%</Badge>
                        </div>
                        {m.headline && <div className="text-xs text-stone-400 truncate mt-0.5">{m.headline}</div>}
                        {m.match_reasons?.length > 0 && <div className="text-[11px] text-stone-500 mt-0.5">Points communs : {m.match_reasons.join(", ")}</div>}
                      </div>
                      {m.connection_status === "none" ? (
                        <Button size="sm" className="rounded-xl u2-btn-primary shrink-0" onClick={() => setRequestMatch(m)} data-testid={`request-mentoring-${m.token_id}`}>
                          <HandHeart className="w-3.5 h-3.5 sm:mr-1.5" /><span className="hidden sm:inline">{m.propose_as === "mentor" ? "Demander" : "Proposer"}</span>
                        </Button>
                      ) : <Badge variant="outline" className="rounded-full text-xs text-stone-500 shrink-0">{m.connection_status === "contact" ? "En relation" : "En attente"}</Badge>}
                    </div>
                  </CardContent>
                </Card>
              ))}
              {matches.length === 0 && <p className="text-sm text-stone-400 text-center py-5">Aucune suggestion pour le moment. Ajoutez des domaines et revenez bientôt.</p>}
            </div>
          )}
        </div>
      )}

      <MentoratRequestDialog match={requestMatch} open={!!requestMatch} onOpenChange={v => !v && setRequestMatch(null)} onSent={loadMatches} />

      {/* Dialog clôture mentorat */}
      <Dialog open={!!terminateRel} onOpenChange={v => !v && setTerminateRel(null)}>
        <DialogContent className="max-w-md rounded-2xl" data-testid="terminate-dialog">
          <DialogHeader>
            <DialogTitle className="u2-heading">Clôturer le mentorat</DialogTitle>
            <DialogDescription>Chaque mentorat a un début et une fin. Rédigez un court bilan des échanges et actions menées.</DialogDescription>
          </DialogHeader>
          <Textarea value={bilan} onChange={e => setBilan(e.target.value)} rows={3} maxLength={800}
            placeholder="Bilan : objectifs atteints, actions réalisées, suite envisagée…" className="rounded-xl text-sm" data-testid="bilan-input" />
          <div className="flex justify-end gap-2">
            <Button variant="outline" className="rounded-xl" onClick={() => setTerminateRel(null)}>Annuler</Button>
            <Button className="rounded-xl u2-btn-primary" disabled={acting} data-testid="submit-terminate-btn" onClick={async () => {
              setActing(true);
              try {
                await u2.post(`/mentoring/relations/${terminateRel.conn_id}/terminate`, { bilan });
                toast.success("Mentorat clôturé avec bilan");
                setTerminateRel(null); loadMatches();
              } catch (e) { toast.error(e.response?.data?.detail || "Erreur"); }
              finally { setActing(false); }
            }}>Clôturer</Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Dialog retour confidentiel */}
      <Dialog open={!!feedbackRel} onOpenChange={v => !v && setFeedbackRel(null)}>
        <DialogContent className="max-w-md rounded-2xl" data-testid="feedback-dialog">
          <DialogHeader>
            <DialogTitle className="u2-heading">Retour confidentiel sur l'accompagnement</DialogTitle>
            <DialogDescription>Votre retour reste confidentiel. Il contribue à la reconnaissance des mentors de qualité.</DialogDescription>
          </DialogHeader>
          <div className="flex justify-center gap-2 py-1" data-testid="rating-stars">
            {[1, 2, 3, 4, 5].map(n => (
              <button key={n} onClick={() => setRating(n)} data-testid={`rating-${n}`}
                className={`h-10 w-10 rounded-xl border text-lg font-bold transition-colors ${rating >= n ? "bg-[#E09F3E] text-white border-transparent" : "bg-white border-[#E2DFD8] text-stone-300"}`}>★</button>
            ))}
          </div>
          <Textarea value={comment} onChange={e => setComment(e.target.value)} rows={2} maxLength={500}
            placeholder="Commentaire (facultatif)" className="rounded-xl text-sm" data-testid="feedback-comment-input" />
          <div className="flex justify-end gap-2">
            <Button variant="outline" className="rounded-xl" onClick={() => setFeedbackRel(null)}>Annuler</Button>
            <Button className="rounded-xl u2-btn-primary" disabled={acting || rating === 0} data-testid="submit-feedback-btn" onClick={async () => {
              setActing(true);
              try {
                const res = await u2.post(`/mentoring/relations/${feedbackRel.conn_id}/feedback`, { rating, comment });
                toast.success(res.data.message);
                setFeedbackRel(null); loadMatches();
              } catch (e) { toast.error(e.response?.data?.detail || "Erreur"); }
              finally { setActing(false); }
            }}>Envoyer</Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
