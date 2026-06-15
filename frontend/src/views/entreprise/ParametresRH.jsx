import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Settings, Building2, Shield, Lock, Info } from "lucide-react";

const ParametresRH = ({ token, profile }) => {
  return (
    <div className="space-y-6" data-testid="parametres-view">
      <div>
        <h1 className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>Paramètres</h1>
        <p className="text-sm text-slate-500">Configuration de l'espace RH</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card className="border border-slate-100">
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2"><Building2 className="w-4 h-4 text-emerald-600" /> Entreprise</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div className="flex justify-between"><span className="text-slate-500">Nom</span><span className="font-medium">{profile?.company_name || "—"}</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Email</span><span className="font-medium">{profile?.email || "—"}</span></div>
            <div className="flex justify-between"><span className="text-slate-500">SIRET</span><span className="font-medium">{profile?.siret || "—"}</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Referent</span><span className="font-medium">{profile?.referent_first_name} {profile?.referent_last_name}</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Fonction</span><span className="font-medium">{profile?.referent_function || "—"}</span></div>
          </CardContent>
        </Card>

        <Card className="border border-slate-100">
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2"><Shield className="w-4 h-4 text-blue-600" /> Conformite RGPD</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="p-3 bg-blue-50 rounded-lg border border-blue-100">
              <p className="text-sm font-medium text-blue-800 flex items-center gap-1.5"><Lock className="w-4 h-4" /> Données chiffrées</p>
              <p className="text-xs text-blue-600 mt-1">Toutes les données sont chiffrées en transit et au repos.</p>
            </div>
            <div className="p-3 bg-emerald-50 rounded-lg border border-emerald-100">
              <p className="text-sm font-medium text-emerald-800 flex items-center gap-1.5"><Info className="w-4 h-4" /> Consentement utilisateur</p>
              <p className="text-xs text-emerald-600 mt-1">Chaque collaborateur contrôle le niveau de partage de ses données (aucun, partiel, complet).</p>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
              <p className="text-sm font-medium text-slate-800">Tracabilite</p>
              <p className="text-xs text-slate-500 mt-1">Chaque acces et export est trace dans l'historique du collaborateur.</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="border border-slate-100">
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2"><Settings className="w-4 h-4 text-slate-600" /> Synchronisation</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
            <div><p className="font-medium">Espace personnel → RH</p><p className="text-xs text-slate-500">Competences, soft skills, CV, projet pro</p></div>
            <Badge className="bg-emerald-100 text-emerald-700">Actif</Badge>
          </div>
          <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
            <div><p className="font-medium">Partenaires → RH</p><p className="text-xs text-slate-500">Suivi accompagnement, formations, evaluations</p></div>
            <Badge className="bg-emerald-100 text-emerald-700">Actif</Badge>
          </div>
          <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
            <div><p className="font-medium">D'CLIC PRO → RH</p><p className="text-xs text-slate-500">Resultats RIASEC, DISC, soft skills</p></div>
            <Badge className="bg-emerald-100 text-emerald-700">Actif</Badge>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ParametresRH;
