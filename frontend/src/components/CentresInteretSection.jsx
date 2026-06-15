import React, { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Heart, Plus, Trash2, Loader2, Sparkles, X } from "lucide-react";
import { toast } from "sonner";

const CentresInteretSection = ({ token }) => {
  const [centres, setCentres] = useState([]);
  const [analyses, setAnalyses] = useState([]);
  const [compTransversales, setCompTransversales] = useState([]);
  const [valeurs, setValeurs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editing, setEditing] = useState(false);
  const [inputs, setInputs] = useState([{ theme: "", description: "" }]);

  useEffect(() => {
    if (!token) return;
    axios.get(`${API}/cv/centres-interet?token=${token}`).then(r => {
      const data = r.data;
      if (data.centres && data.centres.length > 0) {
        setCentres(data.centres);
        setAnalyses(data.analyses || []);
        setCompTransversales(data.competences_transversales || []);
        setValeurs(data.valeurs_dominantes || []);
      }
    }).catch(() => {});
  }, [token]);

  const handleSave = async () => {
    const valid = inputs.filter(i => i.theme.trim());
    if (valid.length === 0) { toast.error("Ajoutez au moins un centre d'intérêt"); return; }
    setSaving(true);
    try {
      const res = await axios.post(`${API}/cv/centres-interet?token=${token}`, { centres: valid });
      setAnalyses(res.data.analyses || []);
      setCompTransversales(res.data.competences_transversales || []);
      setValeurs(res.data.valeurs_dominantes || []);
      setCentres(valid);
      setEditing(false);
      toast.success("Centres d'intérêt enregistrés et analysés par l'IA");
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Erreur lors de l'enregistrement");
    } finally { setSaving(false); }
  };

  const addInput = () => setInputs(p => [...p, { theme: "", description: "" }]);
  const removeInput = (idx) => setInputs(p => p.filter((_, i) => i !== idx));
  const updateInput = (idx, field, val) => setInputs(p => p.map((item, i) => i === idx ? { ...item, [field]: val } : item));

  const startEdit = () => {
    setInputs(centres.length > 0
      ? centres.map(c => ({ theme: c.theme || c.label || "", description: c.description || c.detail || "" }))
      : [{ theme: "", description: "" }]);
    setEditing(true);
  };

  return (
    <Card className="rounded-2xl border-0 shadow-sm" data-testid="centres-interet-section">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2 text-lg"><Heart className="w-5 h-5 text-rose-500" />{"Centres d'intérêt"}</CardTitle>
            <CardDescription className="text-sm">{"Vos passions révèlent des compétences transversales valorisables"}</CardDescription>
          </div>
          {!editing && (
            <Button variant="outline" size="sm" className="rounded-xl" onClick={startEdit} data-testid="edit-centres-btn">
              <Plus className="w-3.5 h-3.5 mr-1" />{centres.length > 0 ? "Modifier" : "Ajouter"}
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {editing ? (
          <div className="space-y-3">
            {inputs.map((input, idx) => (
              <div key={idx} className="flex gap-2 items-start">
                <div className="flex-1 space-y-1">
                  <Input
                    placeholder="Ex: Course à pied, Bénévolat, Photographie..."
                    value={input.theme}
                    onChange={e => updateInput(idx, "theme", e.target.value)}
                    className="text-sm"
                    data-testid={`centre-theme-${idx}`}
                  />
                  <Input
                    placeholder="Décrivez votre pratique (fréquence, contexte, engagements...)"
                    value={input.description}
                    onChange={e => updateInput(idx, "description", e.target.value)}
                    className="text-sm text-slate-500"
                    data-testid={`centre-desc-${idx}`}
                  />
                </div>
                {inputs.length > 1 && (
                  <Button variant="ghost" size="sm" onClick={() => removeInput(idx)} className="text-slate-400 hover:text-red-500 mt-1">
                    <Trash2 className="w-4 h-4" />
                  </Button>
                )}
              </div>
            ))}
            <div className="flex gap-2">
              <Button variant="outline" size="sm" className="rounded-xl" onClick={addInput} data-testid="add-centre-input">
                <Plus className="w-3.5 h-3.5 mr-1" />{"Ajouter un centre"}
              </Button>
            </div>
            <div className="flex gap-2 pt-2 border-t">
              <Button size="sm" className="rounded-xl bg-[#1e3a5f] hover:bg-[#152a45]" onClick={handleSave} disabled={saving} data-testid="save-centres-btn">
                {saving ? <Loader2 className="w-4 h-4 mr-1 animate-spin" /> : <Sparkles className="w-4 h-4 mr-1" />}
                {saving ? "Analyse IA en cours..." : "Enregistrer et analyser"}
              </Button>
              <Button variant="outline" size="sm" className="rounded-xl" onClick={() => setEditing(false)}>Annuler</Button>
            </div>
          </div>
        ) : centres.length > 0 ? (
          <div className="space-y-3">
            {/* Display saved centres with analyses */}
            {analyses.length > 0 ? analyses.map((a, i) => (
              <div key={i} className="bg-slate-50 rounded-xl p-3">
                <div className="flex items-center gap-2 mb-1">
                  <Heart className="w-3.5 h-3.5 text-rose-400" />
                  <span className="text-sm font-medium text-slate-800">{a.label}</span>
                  {a.credibility && <Badge variant="outline" className={`text-[9px] ${a.credibility === "forte" ? "border-emerald-200 text-emerald-600" : "border-amber-200 text-amber-600"}`}>{a.credibility === "forte" ? "Crédibilité forte" : "Crédibilité moyenne"}</Badge>}
                </div>
                {a.cv_reformulation && <p className="text-xs text-slate-600 ml-5 italic">{a.cv_reformulation}</p>}
                {a.qualites?.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-1.5 ml-5">
                    {a.qualites.map((q, j) => <Badge key={j} variant="secondary" className="text-[9px]">{q}</Badge>)}
                  </div>
                )}
              </div>
            )) : centres.map((c, i) => (
              <div key={i} className="bg-slate-50 rounded-xl p-3 flex items-center gap-2">
                <Heart className="w-3.5 h-3.5 text-rose-400" />
                <span className="text-sm text-slate-700">{c.theme || c.label}</span>
                {c.description && <span className="text-xs text-slate-400">{"\u2014 " + (c.description || c.detail)}</span>}
              </div>
            ))}

            {/* Compétences transversales */}
            {compTransversales.length > 0 && (
              <div className="pt-2 border-t mt-3">
                <p className="text-[10px] font-semibold text-slate-500 mb-1.5">{"Compétences transversales révélées"}</p>
                <div className="flex flex-wrap gap-1">
                  {compTransversales.map((c, i) => <Badge key={i} className="bg-rose-50 text-rose-700 border-rose-200 text-[10px]">{c}</Badge>)}
                </div>
              </div>
            )}
            {valeurs.length > 0 && (
              <div>
                <p className="text-[10px] font-semibold text-slate-500 mb-1.5">{"Valeurs dominantes"}</p>
                <div className="flex flex-wrap gap-1">
                  {valeurs.map((v, i) => <Badge key={i} className="bg-indigo-50 text-indigo-700 border-indigo-200 text-[10px]">{v}</Badge>)}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-4">
            <Heart className="w-8 h-8 text-slate-200 mx-auto mb-2" />
            <p className="text-sm text-slate-500">{"Aucun centre d'intérêt renseigné"}</p>
            <p className="text-xs text-slate-400 mt-1">{"Ajoutez vos passions pour enrichir votre profil et valoriser vos compétences transversales"}</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default CentresInteretSection;
