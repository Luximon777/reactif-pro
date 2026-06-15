import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { FileDown, FileText, Shield, Lock, Download, Loader2, CheckCircle2, Users } from "lucide-react";
import { toast } from "sonner";

const ExportConformite = ({ token }) => {
  const [collabs, setCollabs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(null);
  const [exportResult, setExportResult] = useState(null);

  useEffect(() => {
    axios.get(`${API}/entreprise/collaborateurs?token=${token}`)
      .then(r => setCollabs(r.data)).catch(() => {}).finally(() => setLoading(false));
  }, [token]);

  const doExport = async (collabId, type) => {
    setExporting(collabId);
    try {
      const r = await axios.post(`${API}/entreprise/collaborateurs/${collabId}/export?token=${token}&export_type=${type}`);
      setExportResult(r.data);
      toast.success("Dossier généré");
    } catch (err) { toast.error(err.response?.data?.detail || "Erreur"); }
    setExporting(null);
  };

  if (loading) return <div className="flex justify-center py-20"><Loader2 className="w-8 h-8 animate-spin text-emerald-600" /></div>;

  return (
    <div className="space-y-6" data-testid="export-view">
      <div>
        <h1 className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>Export & Conformite</h1>
        <p className="text-sm text-slate-500">Generation de dossiers et gestion du consentement</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="border border-emerald-200 bg-emerald-50/30">
          <CardContent className="p-4 flex items-start gap-3">
            <FileDown className="w-5 h-5 text-emerald-600 mt-0.5" />
            <div><p className="text-sm font-medium">Export 1-clic</p><p className="text-xs text-slate-500">Generez un profil professionnel complet, un dossier de reclassement ou un export France Travail en un seul clic.</p></div>
          </CardContent>
        </Card>
        <Card className="border border-blue-200 bg-blue-50/30">
          <CardContent className="p-4 flex items-start gap-3">
            <Shield className="w-5 h-5 text-blue-600 mt-0.5" />
            <div><p className="text-sm font-medium">RGPD & Consentement</p><p className="text-xs text-slate-500">Les exports respectent le niveau de consentement de chaque collaborateur. Données chiffrées et tracées.</p></div>
          </CardContent>
        </Card>
      </div>

      {/* Collaborators list for export */}
      <Card className="border border-slate-100" data-testid="export-collab-list">
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2"><Users className="w-4 h-4 text-emerald-600" /> Collaborateurs exportables</CardTitle>
          <CardDescription>{collabs.length} collaborateur{collabs.length !== 1 ? "s" : ""}</CardDescription>
        </CardHeader>
        <CardContent>
          {collabs.length === 0 ? <p className="text-sm text-slate-400 text-center py-6">Aucun collaborateur</p> : (
            <div className="space-y-2">
              {collabs.map(c => (
                <div key={c.id} className="flex items-center justify-between p-3 rounded-lg border border-slate-100 hover:bg-slate-50" data-testid={`export-row-${c.id}`}>
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-700 font-bold text-xs">
                      {c.name.split(" ").map(n => n[0]).join("").slice(0, 2)}
                    </div>
                    <div>
                      <p className="text-sm font-medium">{c.name}</p>
                      <div className="flex items-center gap-1.5 text-xs text-slate-500">
                        <span>{c.poste}</span>
                        <Badge variant="secondary" className="text-[10px] py-0">
                          <Lock className="w-2.5 h-2.5 mr-0.5" />{c.consent_level || "aucun"}
                        </Badge>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button size="sm" variant="outline" className="h-8 text-xs" onClick={() => doExport(c.id, "profil_complet")}
                      disabled={exporting === c.id} data-testid={`export-profil-${c.id}`}>
                      {exporting === c.id ? <Loader2 className="w-3 h-3 animate-spin" /> : <FileText className="w-3 h-3 mr-1" />}Profil
                    </Button>
                    {c.parcours_type === "pse_reclassement" && (
                      <Button size="sm" variant="outline" className="h-8 text-xs text-red-600" onClick={() => doExport(c.id, "dossier_reclassement")}
                        disabled={exporting === c.id} data-testid={`export-reclassement-${c.id}`}>
                        <Shield className="w-3 h-3 mr-1" />Reclassement
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Export Result */}
      {exportResult && (
        <Card className="border border-emerald-200 bg-emerald-50/30" data-testid="export-result">
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2"><CheckCircle2 className="w-5 h-5 text-emerald-600" /> Dossier généré</CardTitle>
            <CardDescription>Type: {exportResult.export_type} — {new Date(exportResult.generated_at).toLocaleDateString('fr-FR')}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 text-sm">
              {exportResult.sections?.identite && (
                <div className="p-3 bg-white rounded-lg border border-slate-100">
                  <p className="font-semibold text-slate-800 mb-1">Identite</p>
                  <p>Nom : {exportResult.sections.identite.nom} | Poste : {exportResult.sections.identite.poste}</p>
                </div>
              )}
              {exportResult.sections?.competences && (
                <div className="p-3 bg-white rounded-lg border border-slate-100">
                  <p className="font-semibold text-slate-800 mb-1">Competences ({(exportResult.sections.competences.hard_skills||[]).length} hard + {(exportResult.sections.competences.soft_skills||[]).length} soft)</p>
                  <div className="flex flex-wrap gap-1 mt-1">{(exportResult.sections.competences.hard_skills||[]).slice(0,8).map((s,i) => <Badge key={i} variant="secondary" className="text-xs">{s}</Badge>)}</div>
                </div>
              )}
              {exportResult.sections?.passeport && (
                <div className="p-3 bg-white rounded-lg border border-slate-100">
                  <p className="font-semibold text-slate-800 mb-1">Passeport de competences</p>
                  {exportResult.sections.passeport.career_project && <p className="text-slate-600">{exportResult.sections.passeport.career_project}</p>}
                </div>
              )}
              {exportResult.sections?.dclic_pro && Object.keys(exportResult.sections.dclic_pro).length > 0 && (
                <div className="p-3 bg-white rounded-lg border border-slate-100">
                  <p className="font-semibold text-slate-800 mb-1">D'CLIC PRO</p>
                  <div className="flex flex-wrap gap-2">{Object.entries(exportResult.sections.dclic_pro).filter(([,v]) => typeof v === "number").map(([k,v]) => <Badge key={k} className="bg-indigo-50 text-indigo-700">{k}: {v}</Badge>)}</div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default ExportConformite;
