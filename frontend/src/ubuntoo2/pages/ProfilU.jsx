import React, { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Lock, Users, Globe, RefreshCw, Save, Loader2, HandHeart, Award, Info, CheckCircle2 } from "lucide-react";
import { toast } from "sonner";
import { u2, HELP_OFFERS, PRIVACY_LEVELS } from "../api";
import { BadgesGrid, ComprendreBadgesDialog } from "./BadgesSection";
import ParcoursUbuntoo from "./ParcoursUbuntoo";
import { LoadFail } from "../LoadFail";

const PRIVACY_ICONS = { prive: Lock, reseau: Users, public: Globe };
const FIELD_LABELS = {
  projet: "Projet professionnel",
  experiences: "Expériences",
  competences: "Compétences techniques",
  soft_skills: "Soft skills",
  interests: "Centres d'intérêt",
  help_offers: "Disponibilité pour aider",
};

const PrivacySelect = ({ value, onChange, field }) => (
  <Select value={value} onValueChange={onChange}>
    <SelectTrigger className="rounded-xl h-8 w-[170px] text-xs" data-testid={`privacy-select-${field}`}>
      <SelectValue />
    </SelectTrigger>
    <SelectContent>
      {PRIVACY_LEVELS.map(l => {
        const Icon = PRIVACY_ICONS[l.value];
        return (
          <SelectItem key={l.value} value={l.value} data-testid={`privacy-option-${field}-${l.value}`}>
            <span className="flex items-center gap-1.5 text-xs"><Icon className="w-3 h-3" />{l.label}</span>
          </SelectItem>
        );
      })}
    </SelectContent>
  </Select>
);

export default function ProfilU() {
  const [profile, setProfile] = useState(null);
  const [badgesData, setBadgesData] = useState(null);
  const [comprendreOpen, setComprendreOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [syncing, setSyncing] = useState(false);

  const loadProfile = () => {
    setProfile(null);
    u2.get("/me").then(r => setProfile(r.data)).catch(() => setProfile("error"));
    u2.get("/badges").then(r => setBadgesData(r.data)).catch(() => {});
  };
  useEffect(loadProfile, []);

  const save = async () => {
    setSaving(true);
    try {
      const res = await u2.put("/me", {
        display_name: profile.display_name, headline: profile.headline, projet: profile.projet,
        help_offers: profile.help_offers || [], privacy: profile.privacy || {},
      });
      setProfile(res.data);
      toast.success("Profil enregistré");
    } catch { toast.error("Erreur d'enregistrement"); }
    finally { setSaving(false); }
  };

  const resync = async () => {
    setSyncing(true);
    try {
      const res = await u2.post("/me/sync");
      setProfile(res.data);
      toast.success("Profil resynchronisé depuis Ré'Actif Pro");
    } catch { toast.error("Erreur de synchronisation"); }
    finally { setSyncing(false); }
  };

  const toggleHelp = (offer) => {
    setProfile(p => ({
      ...p,
      help_offers: p.help_offers?.includes(offer) ? p.help_offers.filter(o => o !== offer) : [...(p.help_offers || []), offer],
    }));
  };

  const setPrivacy = (field, value) => setProfile(p => ({ ...p, privacy: { ...p.privacy, [field]: value } }));

  if (profile === "error") return <LoadFail onRetry={loadProfile} />;
  if (!profile) return <div className="flex justify-center py-16"><Loader2 className="w-8 h-8 animate-spin text-[#C85A32]" /></div>;

  return (
    <div className="space-y-4" data-testid="ubuntoo-profil">
      <div className="flex items-start justify-between gap-3 flex-wrap">
        <div>
          <h1 className="text-2xl font-extrabold u2-heading tracking-tight">Mon profil UBUNTOO</h1>
          <p className="text-sm text-stone-500 mt-1">Construit à partir de votre profil Ré'Actif Pro. Vous restez maître de ce que vous rendez visible.</p>
        </div>
        <Button variant="outline" size="sm" className="rounded-xl" onClick={resync} disabled={syncing} data-testid="resync-profile-btn">
          {syncing ? <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" /> : <RefreshCw className="w-3.5 h-3.5 mr-1.5" />}Resynchroniser
        </Button>
      </div>

      <Card className="rounded-2xl border border-[#E2DFD8] shadow-none bg-white">
        <CardContent className="p-5 space-y-4">
          <div className="flex items-center gap-4">
            <div className="h-14 w-14 rounded-full bg-[#C85A32] text-white flex items-center justify-center text-xl font-bold shrink-0">{(profile.display_name || "?")[0].toUpperCase()}</div>
            <div className="flex-1 space-y-2">
              <Input value={profile.display_name || ""} onChange={e => setProfile(p => ({ ...p, display_name: e.target.value }))} placeholder="Identité d'usage" className="rounded-xl font-semibold" data-testid="display-name-input" />
              <Input value={profile.headline || ""} onChange={e => setProfile(p => ({ ...p, headline: e.target.value }))} maxLength={160} placeholder="Métier recherché, secteur ou objectif (titre affiché)" className="rounded-xl text-sm" data-testid="headline-input" />
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs font-semibold text-stone-500 uppercase tracking-wide">{FIELD_LABELS.projet}</label>
              <PrivacySelect value={profile.privacy?.projet || "reseau"} onChange={v => setPrivacy("projet", v)} field="projet" />
            </div>
            <Textarea value={profile.projet || ""} onChange={e => setProfile(p => ({ ...p, projet: e.target.value }))} rows={3} maxLength={600} className="rounded-xl text-sm" data-testid="projet-input" />
          </div>

          {[["experiences", profile.experiences?.map(e => `${e.title}${e.organization ? ` — ${e.organization}` : ""}`)],
            ["competences", profile.competences],
            ["soft_skills", profile.soft_skills],
            ["interests", profile.interests]].map(([field, items]) => (
            <div key={field}>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-semibold text-stone-500 uppercase tracking-wide">{FIELD_LABELS[field]}</label>
                <PrivacySelect value={profile.privacy?.[field === "experiences" ? "experiences" : field] || "reseau"} onChange={v => setPrivacy(field === "experiences" ? "experiences" : field, v)} field={field} />
              </div>
              {items?.length > 0 ? (
                <div className="flex flex-wrap gap-1.5">
                  {items.map((it, i) => <Badge key={i} variant="outline" className="rounded-full text-xs border-[#E2DFD8] text-stone-600">{it}</Badge>)}
                </div>
              ) : <p className="text-xs text-stone-400">Aucune donnée — complétez votre passeport Ré'Actif Pro puis resynchronisez.</p>}
            </div>
          ))}

          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs font-semibold text-stone-500 uppercase tracking-wide flex items-center gap-1"><HandHeart className="w-3.5 h-3.5" />{FIELD_LABELS.help_offers}</label>
              <PrivacySelect value={profile.privacy?.help_offers || "reseau"} onChange={v => setPrivacy("help_offers", v)} field="help_offers" />
            </div>
            <div className="flex flex-wrap gap-1.5">
              {HELP_OFFERS.map(o => (
                <button key={o} onClick={() => toggleHelp(o)} data-testid={`help-offer-${o.replace(/[^a-z]/gi, "-").toLowerCase()}`}
                  className={`rounded-full px-3 py-1.5 text-xs font-medium border transition-colors ${profile.help_offers?.includes(o) ? "bg-orange-100 text-orange-800 border-orange-300 font-semibold" : "bg-white text-stone-500 border-[#E2DFD8] hover:border-orange-300"}`}>
                  {o}
                </button>
              ))}
            </div>
          </div>

          <div className="rounded-xl bg-[#FAF8F5] border border-[#E2DFD8] p-3 text-xs text-stone-500 space-y-1">
            <p className="font-semibold text-stone-600">Niveaux de confidentialité</p>
            {PRIVACY_LEVELS.map(l => {
              const Icon = PRIVACY_ICONS[l.value];
              return <p key={l.value} className="flex items-center gap-1.5"><Icon className="w-3 h-3" /><span className="font-medium">{l.label}</span> — {l.desc}</p>;
            })}
          </div>

          <div className="flex justify-end">
            <Button className="rounded-xl u2-btn-primary" onClick={save} disabled={saving} data-testid="save-profile-btn">
              {saving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}Enregistrer
            </Button>
          </div>
        </CardContent>
      </Card>

      <ParcoursUbuntoo />

      {badgesData && (
        <Card className="rounded-2xl border border-[#E2DFD8] shadow-none bg-white">
          <CardContent className="p-5 space-y-4">
            <div className="flex items-center justify-between gap-2 flex-wrap">
              <h3 className="text-base font-semibold u2-heading flex items-center gap-1.5"><Award className="w-4 h-4 text-[#E09F3E]" />Mes badges & mon parcours de contribution</h3>
              <Button variant="outline" size="sm" className="rounded-xl text-xs" onClick={() => setComprendreOpen(true)} data-testid="comprendre-badges-btn">
                <Info className="w-3.5 h-3.5 mr-1.5" />Comprendre les badges
              </Button>
            </div>

            {/* Mon parcours de contribution — 4 chemins vers Contributeur */}
            <div className="rounded-xl border border-orange-100 bg-orange-50/40 p-3" data-testid="contribution-paths">
              <div className="text-xs font-semibold text-stone-700 mb-0.5">Devenir Contributeur — plusieurs chemins possibles</div>
              <p className="text-[11px] text-stone-500 mb-2.5">Le rôle Contributeur est accessible à tous : il dépend des contributions réellement apportées, pas du diplôme ni du statut. Complétez l'un de ces parcours :</p>
              <div className="grid sm:grid-cols-2 gap-2">
                {badgesData.parcours.map(p => (
                  <div key={p.id} className={`rounded-lg border p-2.5 ${p.complete ? "bg-emerald-50 border-emerald-200" : "bg-white border-stone-100"}`} data-testid={`parcours-${p.id}`}>
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-stone-700">{p.label}</span>
                      {p.complete && <CheckCircle2 className="w-4 h-4 text-emerald-500" />}
                    </div>
                    <p className="text-[10px] text-stone-400 mb-1.5">{p.desc}</p>
                    <div className="flex flex-wrap gap-1">
                      {p.badges.map(s => (
                        <span key={s.id} className={`text-[10px] rounded-full px-2 py-0.5 border ${s.earned ? "bg-emerald-100 text-emerald-700 border-emerald-200" : "bg-stone-50 text-stone-400 border-stone-200"}`}>
                          {s.earned ? "✓ " : `${s.progress.current}/${s.progress.target} `}{s.label}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <BadgesGrid badges={badgesData.badges}
              onDisplayChange={(id, displayed) => setBadgesData(d => ({ ...d, badges: d.badges.map(b => b.id === id ? { ...b, displayed } : b) }))} />
            <p className="text-[11px] text-stone-400">Les badges reconnaissent ce que vous apportez aux autres — pas une compétition. Cliquez sur un badge pour voir sa fiche complète et choisir de l'afficher sur votre profil.</p>
          </CardContent>
        </Card>
      )}
      <ComprendreBadgesDialog open={comprendreOpen} onOpenChange={setComprendreOpen} />
    </div>
  );
}
