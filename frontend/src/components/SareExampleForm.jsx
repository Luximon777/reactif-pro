import React, { useState } from "react";
import axios from "axios";
import { API } from "@/App";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Award, Check, Loader2, X } from "lucide-react";
import { toast } from "sonner";

export const SareExampleForm = ({ exp, token, competences, onSaved, onClose }) => {
  const [skill, setSkill] = useState("");
  const [skillType, setSkillType] = useState("soft");
  const [situation, setSituation] = useState("");
  const [action, setAction] = useState("");
  const [resultat, setResultat] = useState("");
  const [enseignement, setEnseignement] = useState("");
  const [saving, setSaving] = useState(false);

  const hardSkills = [...new Set((competences || []).filter(c => c.nature === "savoir_faire").map(c => c.name))];
  const softSkills = [...new Set((competences || []).filter(c => c.nature === "savoir_etre").map(c => c.name))];
  const expSkills = (exp.skills_used || []).filter(s => !hardSkills.includes(s) && !softSkills.includes(s));

  const handleSave = async () => {
    if (!skill || !situation.trim() || !action.trim()) {
      toast.error("Choisissez une compétence et décrivez au moins la Situation et l'Action");
      return;
    }
    setSaving(true);
    try {
      const parts = [
        `Compétence illustrée (${skillType === "hard" ? "savoir-faire" : "savoir-être"}) : ${skill}`,
        `Situation : ${situation.trim()}`,
        `Action : ${action.trim()}`,
      ];
      if (resultat.trim()) parts.push(`Résultat : ${resultat.trim()}`);
      if (enseignement.trim()) parts.push(`Enseignement : ${enseignement.trim()}`);
      await axios.post(`${API}/passport/illustrations?token=${token}`, {
        experience_id: exp.id,
        soft_skill: skill,
        skill_type: skillType,
        sare_situation: situation.trim(),
        sare_action: action.trim(),
        sare_resultat: resultat.trim(),
        sare_enseignement: enseignement.trim(),
        opc_consent: true,
      });
      await axios.post(`${API}/passport/experience-proof?token=${token}`, {
        experience_id: exp.id,
        proof: parts.join("\n"),
      });
      toast.success("Exemple S.A.R.E enregistré — merci pour votre contribution à l'OPC !");
      if (onSaved) onSaved();
    } catch {
      toast.error("Erreur lors de l'enregistrement");
    }
    setSaving(false);
  };

  const taCls = "w-full text-xs border border-slate-200 rounded-lg p-2 min-h-[48px] resize-y focus:outline-none focus:ring-2 focus:ring-amber-200 focus:border-amber-300 bg-white";

  return (
    <div className="mt-2.5 bg-amber-50/60 rounded-xl border border-amber-200 p-3 space-y-2.5" data-testid={`sare-form-${exp.id}`}>
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-amber-100 flex items-center justify-center shrink-0">
            <Award className="w-4 h-4 text-amber-700" />
          </div>
          <div>
            <p className="text-xs font-bold text-amber-900">Méthode S.A.R.E — Illustrez cette expérience</p>
            <p className="text-[10px] text-amber-700">Situation, Action, Résultat, Enseignement : racontez un fait concret qui prouve une compétence.</p>
          </div>
        </div>
        <Button variant="ghost" size="sm" className="h-6 w-6 p-0 text-slate-400 hover:text-slate-600" onClick={onClose} data-testid={`sare-close-${exp.id}`}>
          <X className="w-3.5 h-3.5" />
        </Button>
      </div>

      <div className="grid grid-cols-4 gap-1.5">
        {[["S", "Situation"], ["A", "Action"], ["R", "Résultat"], ["E", "Enseignement"]].map(([l, t]) => (
          <div key={l} className="bg-white/70 rounded-lg px-2 py-1.5 text-center border border-amber-100">
            <p className="text-sm font-black text-amber-800">{l}</p>
            <p className="text-[9px] text-amber-600 leading-tight">{t}</p>
          </div>
        ))}
      </div>

      <div>
        <label className="text-[11px] font-bold text-slate-700 mb-0.5 block">1. Quelle compétence cet exemple illustre-t-il ?</label>
        <Select value={skill} onValueChange={(val) => {
          setSkill(val);
          setSkillType(hardSkills.includes(val) ? "hard" : "soft");
        }}>
          <SelectTrigger className="h-8 text-xs bg-white" data-testid={`sare-skill-select-${exp.id}`}>
            <SelectValue placeholder="Choisir un savoir-faire ou un savoir-être..." />
          </SelectTrigger>
          <SelectContent>
            {softSkills.length > 0 && (
              <>
                <div className="px-2 py-1.5 text-[10px] font-bold text-rose-600 uppercase tracking-wide">Savoir-être</div>
                {softSkills.map((s, i) => <SelectItem key={`se-${i}`} value={s} className="text-xs">{s}</SelectItem>)}
              </>
            )}
            {hardSkills.length > 0 && (
              <>
                <div className="px-2 py-1.5 text-[10px] font-bold text-sky-600 uppercase tracking-wide border-t mt-1 pt-1.5">Savoir-faire</div>
                {hardSkills.map((s, i) => <SelectItem key={`sf-${i}`} value={s} className="text-xs">{s}</SelectItem>)}
              </>
            )}
            {expSkills.length > 0 && (
              <>
                <div className="px-2 py-1.5 text-[10px] font-bold text-slate-500 uppercase tracking-wide border-t mt-1 pt-1.5">Compétences de cette expérience</div>
                {expSkills.map((s, i) => <SelectItem key={`ex-${i}`} value={s} className="text-xs">{s}</SelectItem>)}
              </>
            )}
          </SelectContent>
        </Select>
        {skill && (
          <Badge className={`mt-1 text-[9px] ${skillType === "hard" ? "bg-sky-100 text-sky-700" : "bg-rose-100 text-rose-700"}`}>
            {skillType === "hard" ? "Savoir-faire" : "Savoir-être"}
          </Badge>
        )}
      </div>

      <div>
        <label className="flex items-center gap-1.5 text-[11px] font-bold text-amber-800 mb-0.5">
          <span className="inline-flex items-center justify-center w-4 h-4 rounded bg-amber-100 text-[10px] font-black">S</span>
          Situation — Le contexte
        </label>
        <textarea value={situation} onChange={e => setSituation(e.target.value)}
          placeholder={`Chez ${exp.organization || "cet employeur"}, j'ai été confronté(e) à... (Où ? Quand ? Quel contexte ?)`}
          className={taCls} data-testid={`sare-situation-${exp.id}`} />
      </div>
      <div>
        <label className="flex items-center gap-1.5 text-[11px] font-bold text-amber-800 mb-0.5">
          <span className="inline-flex items-center justify-center w-4 h-4 rounded bg-amber-100 text-[10px] font-black">A</span>
          Action — Ce que vous avez fait
        </label>
        <textarea value={action} onChange={e => setAction(e.target.value)}
          placeholder="J'ai décidé de... / J'ai mis en place... / J'ai proposé..."
          className={taCls} data-testid={`sare-action-${exp.id}`} />
      </div>
      <div>
        <label className="flex items-center gap-1.5 text-[11px] font-bold text-amber-800 mb-0.5">
          <span className="inline-flex items-center justify-center w-4 h-4 rounded bg-amber-100 text-[10px] font-black">R</span>
          Résultat — L'impact obtenu
        </label>
        <textarea value={resultat} onChange={e => setResultat(e.target.value)}
          placeholder="Cela a permis de... / Le résultat mesurable a été..."
          className={taCls} data-testid={`sare-resultat-${exp.id}`} />
      </div>
      <div>
        <label className="flex items-center gap-1.5 text-[11px] font-bold text-amber-800 mb-0.5">
          <span className="inline-flex items-center justify-center w-4 h-4 rounded bg-amber-100 text-[10px] font-black">E</span>
          Enseignement — Ce que ça dit de vous
        </label>
        <textarea value={enseignement} onChange={e => setEnseignement(e.target.value)}
          placeholder="Cela montre que je suis capable de... / Cette situation démontre ma..."
          className={taCls} data-testid={`sare-enseignement-${exp.id}`} />
      </div>

      <div className="bg-white border border-dashed border-amber-200 rounded-lg p-2">
        <p className="text-[10px] text-amber-700 leading-relaxed">
          <span className="font-bold">Exemple :</span> "Lors d'un pic d'activité, nous avions un retard important. J'ai priorisé les tâches et redistribué les missions. Nous avons rattrapé le retard en 3 jours sans erreur. Cela montre ma capacité à gérer le stress et rester efficace sous pression."
        </p>
      </div>

      <Button size="sm" className="h-8 text-xs bg-emerald-600 hover:bg-emerald-700 w-full" onClick={handleSave}
        disabled={saving || !skill || !situation.trim() || !action.trim()} data-testid={`sare-save-${exp.id}`}>
        {saving ? <Loader2 className="w-3 h-3 animate-spin mr-1" /> : <Check className="w-3 h-3 mr-1" />}
        Enregistrer l'exemple S.A.R.E
      </Button>
    </div>
  );
};

export default SareExampleForm;
