import React, { useState, useEffect, useCallback } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Route, Check, Lock, GraduationCap, Megaphone, Crown, Loader2, HandHeart, ShieldCheck, ArrowRight } from "lucide-react";
import { toast } from "sonner";
import { u2 } from "../api";

const Step = ({ reached, label, sub, pending }) => (
  <div className={`flex items-center gap-2.5 rounded-xl border px-3 py-2 ${reached ? "bg-white border-emerald-200" : pending ? "bg-amber-50 border-amber-200" : "bg-stone-50 border-[#E2DFD8] opacity-70"}`}>
    <div className={`h-6 w-6 rounded-full flex items-center justify-center shrink-0 ${reached ? "bg-[#2E7D5B] text-white" : pending ? "bg-amber-400 text-white" : "bg-stone-200 text-stone-400"}`}>
      {reached ? <Check className="w-3.5 h-3.5" /> : pending ? <Loader2 className="w-3 h-3 animate-spin" /> : <Lock className="w-3 h-3" />}
    </div>
    <div className="min-w-0">
      <div className="text-xs font-semibold leading-tight">{label}</div>
      {sub && <div className="text-[10px] text-stone-400 leading-tight">{sub}</div>}
    </div>
  </div>
);

export default function ParcoursUbuntoo() {
  const [prog, setProg] = useState(null);
  const [charteOpen, setCharteOpen] = useState(false);
  const [charteAccepted, setCharteAccepted] = useState(false);
  const [motivation, setMotivation] = useState("");
  const [ambOpen, setAmbOpen] = useState(false);
  const [sending, setSending] = useState(false);
  const [candidatures, setCandidatures] = useState(null);

  const load = useCallback(() => {
    u2.get("/progression").then(r => setProg(r.data)).catch(() => {});
    u2.get("/admin/candidatures").then(r => setCandidatures(r.data)).catch(() => setCandidatures(null));
  }, []);
  useEffect(() => { load(); }, [load]);

  const applyMentor = async () => {
    setSending(true);
    try {
      const res = await u2.post("/progression/mentor-candidature", { accept_charte: charteAccepted, motivation });
      toast.success(res.data.message);
      setCharteOpen(false); setMotivation("");
      load();
    } catch (e) { toast.error(e.response?.data?.detail || "Erreur"); }
    finally { setSending(false); }
  };

  const applyAmbassadeur = async () => {
    setSending(true);
    try {
      const res = await u2.post("/progression/ambassadeur-candidature", { motivation });
      toast.success(res.data.message);
      setAmbOpen(false); setMotivation("");
      load();
    } catch (e) { toast.error(e.response?.data?.detail || "Erreur"); }
    finally { setSending(false); }
  };

  const decide = async (candId, action) => {
    try {
      await u2.post(`/admin/candidatures/${candId}/decide`, { action });
      toast.success(action === "approve" ? "Candidature validée" : "Candidature refusée");
      load();
    } catch { toast.error("Erreur"); }
  };

  if (!prog) return null;
  const L = prog.levels;
  const contrib = prog.contributions;

  return (
    <Card className="rounded-2xl border border-[#E2DFD8] shadow-none bg-white" data-testid="parcours-ubuntoo">
      <CardContent className="p-5 space-y-4">
        <div className="flex items-center justify-between gap-2 flex-wrap">
          <h3 className="text-base font-semibold u2-heading flex items-center gap-1.5"><Route className="w-4 h-4 text-[#C85A32]" />Mon parcours UBUNTOO</h3>
          <Badge className="rounded-full bg-[#C85A32] text-white hover:bg-[#C85A32]" data-testid="current-level-badge">{prog.current_label}</Badge>
        </div>
        <p className="text-xs text-stone-400">Mentor et Ambassadeur sont des rôles de confiance : ils traduisent une progression réelle dans la communauté, pas une accumulation de points.</p>

        {/* Tronc commun */}
        <div className="grid grid-cols-3 gap-2">
          <Step reached={L.membre} label="Membre" sub="Profil et communautés" />
          <Step reached={L.membre_actif} label="Membre actif" sub="Échanges et participation" />
          <Step reached={L.contributeur} label="Contributeur" sub="Contributions utiles" />
        </div>

        {/* Deux branches */}
        <div className="grid gap-3 sm:grid-cols-2">
          <div className="rounded-xl border border-violet-100 bg-violet-50/30 p-3 space-y-2">
            <div className="text-[11px] font-semibold text-violet-700 uppercase tracking-wide flex items-center gap-1"><GraduationCap className="w-3.5 h-3.5" />Branche Mentorat</div>
            <Step reached={L.mentor_candidat && prog.mentor_status !== "candidat"} pending={prog.mentor_status === "candidat"} label="Mentor candidat" sub="Charte acceptée, candidature examinée" />
            <Step reached={L.mentor} label="Mentor UBUNTOO" sub="Statut validé — accompagne des membres" />
            <Step reached={L.mentor_confirme} label="Mentor confirmé" sub="Mentorats terminés + retours positifs" />
            {prog.can_apply_mentor && (
              <Button size="sm" className="w-full rounded-xl u2-btn-primary" onClick={() => setCharteOpen(true)} data-testid="apply-mentor-btn">
                <GraduationCap className="w-3.5 h-3.5 mr-1.5" />Devenir Mentor candidat
              </Button>
            )}
          </div>
          <div className="rounded-xl border border-blue-100 bg-blue-50/30 p-3 space-y-2">
            <div className="text-[11px] font-semibold text-blue-700 uppercase tracking-wide flex items-center gap-1"><Megaphone className="w-3.5 h-3.5" />Branche Animation</div>
            <Step reached={L.animateur} label="Animateur" sub="Crée ou fait vivre des communautés" />
            <p className="text-[11px] text-stone-400 leading-snug px-1">Accueillir les nouveaux, animer une communauté, faciliter les mises en relation — sans obligation de devenir mentor.</p>
          </div>
        </div>

        {/* Ambassadeur */}
        <div className="rounded-xl border border-amber-200 bg-amber-50/50 p-3 space-y-2">
          <Step reached={L.ambassadeur} pending={prog.ambassadeur_status === "candidat"} label="Ambassadeur UBUNTOO"
            sub={L.ambassadeur ? `Mandat jusqu'au ${(prog.ambassadeur_mandat_end || "").substring(0, 10)}` : "Niveau de confiance communautaire le plus élevé — validation humaine"} />
          {prog.can_apply_ambassadeur && (
            <Button size="sm" className="w-full rounded-xl bg-amber-500 hover:bg-amber-600 text-white" onClick={() => setAmbOpen(true)} data-testid="apply-ambassadeur-btn">
              <Crown className="w-3.5 h-3.5 mr-1.5" />Candidater comme Ambassadeur
            </Button>
          )}
        </div>

        {/* Contributions concrètes */}
        <div>
          <div className="text-xs font-semibold text-stone-500 uppercase tracking-wide mb-1.5">Mes contributions concrètes</div>
          <div className="flex flex-wrap gap-1.5" data-testid="contributions-summary">
            <Badge variant="outline" className="rounded-full text-[11px]">{contrib.publications} publication{contrib.publications > 1 ? "s" : ""}</Badge>
            <Badge variant="outline" className="rounded-full text-[11px]">{contrib.reponses} réponse{contrib.reponses > 1 ? "s" : ""}</Badge>
            <Badge variant="outline" className="rounded-full text-[11px]"><HandHeart className="w-3 h-3 mr-1" />{contrib.utiles_recus} « Utile » reçus</Badge>
            <Badge variant="outline" className="rounded-full text-[11px]">{contrib.communautes} communauté{contrib.communautes > 1 ? "s" : ""}{contrib.communautes_creees > 0 ? ` (${contrib.communautes_creees} créée${contrib.communautes_creees > 1 ? "s" : ""})` : ""}</Badge>
            <Badge variant="outline" className="rounded-full text-[11px]">{contrib.mentorats_termines} mentorat{contrib.mentorats_termines > 1 ? "s" : ""} terminé{contrib.mentorats_termines > 1 ? "s" : ""}{contrib.note_moyenne_mentorat ? ` · ${contrib.note_moyenne_mentorat}/5` : ""}</Badge>
          </div>
        </div>

        {/* Prochaines possibilités */}
        {prog.next_steps?.length > 0 && (
          <div>
            <div className="text-xs font-semibold text-stone-500 uppercase tracking-wide mb-1.5">Prochaines possibilités</div>
            <ul className="space-y-1">
              {prog.next_steps.map((s, i) => <li key={i} className="text-xs text-stone-600 flex items-start gap-1.5"><ArrowRight className="w-3 h-3 mt-0.5 text-[#C85A32] shrink-0" />{s}</li>)}
            </ul>
          </div>
        )}

        {/* Panneau admin : candidatures en attente */}
        {candidatures && candidatures.length > 0 && (
          <div className="rounded-xl border border-rose-200 bg-rose-50/40 p-3 space-y-2" data-testid="admin-candidatures-panel">
            <div className="text-xs font-semibold text-rose-700 uppercase tracking-wide">Candidatures à valider (équipe UBUNTOO)</div>
            {candidatures.map(c => (
              <div key={c.id} className="flex items-center gap-2 bg-white rounded-xl border border-[#E2DFD8] px-3 py-2" data-testid={`candidature-${c.id}`}>
                <div className="min-w-0 flex-1">
                  <span className="text-sm font-medium">{c.display_name}</span>
                  <Badge variant="outline" className="rounded-full text-[10px] ml-2">{c.type === "mentor" ? "Mentor" : "Ambassadeur"}</Badge>
                  {c.motivation && <p className="text-[11px] text-stone-400 truncate">{c.motivation}</p>}
                </div>
                <Button size="sm" className="rounded-xl bg-[#2E7D5B] hover:bg-[#246349] text-white h-7 text-xs" onClick={() => decide(c.id, "approve")} data-testid={`approve-${c.id}`}>Valider</Button>
                <Button size="sm" variant="outline" className="rounded-xl h-7 text-xs text-rose-700 border-rose-200" onClick={() => decide(c.id, "reject")} data-testid={`reject-${c.id}`}>Refuser</Button>
              </div>
            ))}
          </div>
        )}
      </CardContent>

      {/* Dialog charte mentor */}
      <Dialog open={charteOpen} onOpenChange={setCharteOpen}>
        <DialogContent className="max-w-lg rounded-2xl" data-testid="charte-mentor-dialog">
          <DialogHeader>
            <DialogTitle className="u2-heading flex items-center gap-2"><ShieldCheck className="w-5 h-5 text-violet-600" />Charte du mentor UBUNTOO</DialogTitle>
            <DialogDescription>Le mentorat est un rôle de confiance. Prenez connaissance de la charte avant de candidater.</DialogDescription>
          </DialogHeader>
          <ul className="space-y-2">
            {(prog.charte || []).map((c, i) => <li key={i} className="text-sm text-stone-700 flex items-start gap-2"><Check className="w-4 h-4 mt-0.5 text-[#2E7D5B] shrink-0" />{c}</li>)}
          </ul>
          <Textarea value={motivation} onChange={e => setMotivation(e.target.value)} rows={2} maxLength={500}
            placeholder="Votre expérience ou expertise mobilisable (facultatif)" className="rounded-xl text-sm" data-testid="mentor-motivation-input" />
          <label className="flex items-start gap-2 text-sm text-stone-700 cursor-pointer">
            <Checkbox checked={charteAccepted} onCheckedChange={setCharteAccepted} data-testid="accept-charte-checkbox" className="mt-0.5" />
            J'accepte la charte du mentor UBUNTOO
          </label>
          <div className="flex justify-end gap-2">
            <Button variant="outline" className="rounded-xl" onClick={() => setCharteOpen(false)}>Annuler</Button>
            <Button className="rounded-xl u2-btn-primary" onClick={applyMentor} disabled={!charteAccepted || sending} data-testid="submit-mentor-candidature-btn">
              {sending ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <GraduationCap className="w-4 h-4 mr-2" />}Candidater
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Dialog candidature ambassadeur */}
      <Dialog open={ambOpen} onOpenChange={setAmbOpen}>
        <DialogContent className="max-w-md rounded-2xl" data-testid="ambassadeur-dialog">
          <DialogHeader>
            <DialogTitle className="u2-heading flex items-center gap-2"><Crown className="w-5 h-5 text-amber-500" />Candidature Ambassadeur</DialogTitle>
            <DialogDescription>Candidature → vérification des critères → échange → validation → mandat de 12 mois. L'Ambassadeur accueille, anime, facilite et fait remonter les besoins.</DialogDescription>
          </DialogHeader>
          <Textarea value={motivation} onChange={e => setMotivation(e.target.value)} rows={3} maxLength={500}
            placeholder="Ce que vous souhaitez apporter à la communauté…" className="rounded-xl text-sm" data-testid="ambassadeur-motivation-input" />
          <div className="flex justify-end gap-2">
            <Button variant="outline" className="rounded-xl" onClick={() => setAmbOpen(false)}>Annuler</Button>
            <Button className="rounded-xl bg-amber-500 hover:bg-amber-600 text-white" onClick={applyAmbassadeur} disabled={sending} data-testid="submit-ambassadeur-btn">Envoyer ma candidature</Button>
          </div>
        </DialogContent>
      </Dialog>
    </Card>
  );
}
