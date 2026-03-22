import { useState, useEffect, useCallback } from "react";
import { useAuth, API } from "@/App";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "sonner";
import axios from "axios";
import {
  Building2, Handshake, Mail, Lock, Eye, EyeOff, ArrowRight,
  CheckCircle2, AlertTriangle, Search, Loader2, FileCheck, User
} from "lucide-react";

const ProRegisterModal = ({ open, onOpenChange, roleType, onSuccess }) => {
  const isEntreprise = roleType === "entreprise";
  const title = isEntreprise ? "Espace Employeurs" : "Espace Partenaires";
  const Icon = isEntreprise ? Building2 : Handshake;
  const [tab, setTab] = useState("register");

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[520px] p-0 overflow-hidden max-h-[90vh] overflow-y-auto" data-testid={`pro-register-modal-${roleType}`}>
        <div className="bg-[#1e3a5f] px-6 pt-6 pb-5">
          <DialogHeader>
            <DialogTitle className="text-white text-xl flex items-center gap-2" style={{ fontFamily: 'Outfit, sans-serif' }}>
              <Icon className="w-5 h-5" /> {title}
            </DialogTitle>
          </DialogHeader>
          <p className="text-blue-200 text-sm mt-1">
            {isEntreprise ? "Inscription rapide en 2 minutes" : "Inscription simple et rapide"}
          </p>
          <div className="flex gap-2 mt-4">
            <button
              onClick={() => setTab("register")}
              className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-all ${
                tab === "register" ? "bg-white text-[#1e3a5f]" : "bg-white/15 text-blue-100 hover:bg-white/25"
              }`}
              data-testid={`pro-tab-register-${roleType}`}
            >
              Créer un compte
            </button>
            <button
              onClick={() => setTab("login")}
              className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-all ${
                tab === "login" ? "bg-white text-[#1e3a5f]" : "bg-white/15 text-blue-100 hover:bg-white/25"
              }`}
              data-testid={`pro-tab-login-${roleType}`}
            >
              Se connecter
            </button>
          </div>
        </div>
        <div className="p-6">
          {tab === "register" ? (
            isEntreprise
              ? <EntrepriseForm onSuccess={onSuccess} />
              : <PartenaireForm onSuccess={onSuccess} />
          ) : (
            <ProLoginForm onSuccess={onSuccess} roleType={roleType} />
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};

const ProLoginForm = ({ onSuccess, roleType }) => {
  const { loginPro } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPwd, setShowPwd] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email.trim() || !password) return;
    setLoading(true);
    const result = await loginPro(email, password);
    if (result.success) {
      toast.success("Connexion réussie !");
      onSuccess?.();
    } else {
      toast.error(result.error);
    }
    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label>Email professionnel</Label>
        <div className="relative">
          <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <Input placeholder="votre@email-pro.fr" value={email} onChange={(e) => setEmail(e.target.value)}
            className="pl-10" data-testid={`pro-login-email-${roleType}`} autoComplete="email" />
        </div>
      </div>
      <div className="space-y-2">
        <Label>Mot de passe</Label>
        <div className="relative">
          <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <Input type={showPwd ? "text" : "password"} placeholder="Votre mot de passe" value={password}
            onChange={(e) => setPassword(e.target.value)} className="pl-10 pr-10"
            data-testid={`pro-login-password-${roleType}`} autoComplete="current-password" />
          <button type="button" onClick={() => setShowPwd(!showPwd)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
            {showPwd ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        </div>
      </div>
      <Button type="submit" className="w-full bg-[#1e3a5f] hover:bg-[#152a45]" disabled={loading || !email || !password}
        data-testid={`pro-login-submit-${roleType}`}>
        {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <>Se connecter <ArrowRight className="w-4 h-4 ml-2" /></>}
      </Button>
    </form>
  );
};

const SiretField = ({ siret, setSiret, siretResult, setSiretResult, setCompanyFromSiret }) => {
  const [checking, setChecking] = useState(false);

  const verifySiret = useCallback(async () => {
    const clean = siret.replace(/\s/g, "");
    if (clean.length < 9) return;
    setChecking(true);
    try {
      const res = await axios.get(`${API}/siret/verify?siret=${clean}`);
      setSiretResult(res.data);
      if (res.data.valid && res.data.company_name) {
        setCompanyFromSiret(res.data.company_name);
      }
    } catch {
      setSiretResult({ valid: false, error: "Erreur de vérification" });
    }
    setChecking(false);
  }, [siret, setSiretResult, setCompanyFromSiret]);

  return (
    <div className="space-y-2">
      <Label>SIRET / SIREN <span className="text-red-500">*</span></Label>
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
        <Input placeholder="Ex: 12345678901234" value={siret}
          onChange={(e) => { setSiret(e.target.value); setSiretResult(null); }}
          className="pl-10 pr-24" data-testid="siret-input" />
        <Button type="button" size="sm" variant="outline" onClick={verifySiret}
          disabled={checking || siret.replace(/\s/g, "").length < 9}
          className="absolute right-1 top-1/2 -translate-y-1/2 h-8 text-xs"
          data-testid="siret-verify-btn">
          {checking ? <Loader2 className="w-3 h-3 animate-spin" /> : "Vérifier"}
        </Button>
      </div>
      {siretResult && (
        <div className={`p-2 rounded-lg text-xs ${siretResult.valid ? "bg-green-50 text-green-700 border border-green-200" : "bg-red-50 text-red-600 border border-red-200"}`}
          data-testid="siret-result">
          {siretResult.valid ? (
            <div className="flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3 flex-shrink-0" />
              <span><strong>{siretResult.company_name}</strong> — {siretResult.adresse || "Adresse non disponible"}</span>
            </div>
          ) : (
            <div className="flex items-center gap-1">
              <AlertTriangle className="w-3 h-3 flex-shrink-0" />
              <span>{siretResult.error || "Numéro non trouvé"}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const CharteEthiqueSection = ({ signed, setSigned }) => {
  const [expanded, setExpanded] = useState(false);
  const principles = [
    "Voir le potentiel avant le manque",
    "Faire de l'identité professionnelle un facteur de stabilité sociale",
    "Assumer une innovation responsable",
    "Agir sur les causes plutôt que sur les symptômes",
    "Porter une responsabilité sociétale mesurable",
    "Garantir une éthique irréprochable de la donnée",
    "Cultiver une indépendance qui protège l'intérêt des publics",
    "Installer une gouvernance qui anticipe",
    "Construire des coopérations qui élèvent les pratiques",
    "Préparer le futur du travail avec lucidité"
  ];

  return (
    <div className="border-2 border-blue-100 rounded-lg overflow-hidden" data-testid="charte-section">
      <button type="button" onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between p-3 bg-blue-50 hover:bg-blue-100 transition-colors text-left">
        <div className="flex items-center gap-2">
          <FileCheck className="w-4 h-4 text-[#1e3a5f]" />
          <span className="text-sm font-semibold text-[#1e3a5f]">Charte Éthique ALT&ACT</span>
        </div>
        <span className="text-xs text-slate-500">{expanded ? "Réduire" : "Lire les 10 principes"}</span>
      </button>
      {expanded && (
        <div className="p-4 space-y-2 max-h-48 overflow-y-auto">
          {principles.map((p, i) => (
            <div key={i} className="flex items-start gap-2 text-xs text-slate-600">
              <Badge variant="outline" className="flex-shrink-0 text-[10px] px-1.5">{i + 1}</Badge>
              {p}
            </div>
          ))}
          <a href="https://www.alt-act.eu/#/charte-ethique" target="_blank" rel="noopener noreferrer"
            className="text-xs text-[#1e3a5f] underline block mt-2">Lire la charte complète</a>
        </div>
      )}
      <div className="p-3 border-t border-blue-100">
        <div className="flex items-start gap-2">
          <Checkbox id="charte-sign" checked={signed} onCheckedChange={setSigned} data-testid="charte-sign-checkbox" />
          <label htmlFor="charte-sign" className="text-sm text-slate-700 cursor-pointer leading-tight">
            Je m'engage à respecter la <strong>Charte Éthique ALT&ACT</strong> et ses 10 principes <span className="text-red-500">*</span>
          </label>
        </div>
      </div>
    </div>
  );
};

const EmailWarning = ({ email }) => {
  const free = ["gmail.com", "yahoo.com", "yahoo.fr", "hotmail.com", "hotmail.fr", "outlook.com", "live.com", "orange.fr", "free.fr", "sfr.fr"];
  const domain = email.split("@")[1]?.toLowerCase() || "";
  if (!domain || !free.includes(domain)) return null;
  return (
    <div className="flex items-start gap-2 p-2 bg-amber-50 rounded-lg border border-amber-200 text-xs text-amber-700" data-testid="email-warning">
      <AlertTriangle className="w-3 h-3 flex-shrink-0 mt-0.5" />
      <span>Nous recommandons un <strong>email professionnel</strong> pour plus de crédibilité auprès des utilisateurs.</span>
    </div>
  );
};

const EntrepriseForm = ({ onSuccess }) => {
  const { registerEntreprise } = useAuth();
  const [companyName, setCompanyName] = useState("");
  const [siret, setSiret] = useState("");
  const [siretResult, setSiretResult] = useState(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPwd, setShowPwd] = useState(false);
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [func, setFunc] = useState("");
  const [charteSigned, setCharteSigned] = useState(false);
  const [consentCgu, setConsentCgu] = useState(false);
  const [consentPrivacy, setConsentPrivacy] = useState(false);
  const [loading, setLoading] = useState(false);

  const isValid = companyName.trim() && siret.replace(/\s/g, "").length >= 9 && email.includes("@")
    && password.length >= 6 && firstName.trim() && lastName.trim() && func
    && charteSigned && consentCgu && consentPrivacy;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!isValid) return;
    setLoading(true);
    const result = await registerEntreprise({
      company_name: companyName, siret: siret.replace(/\s/g, ""), email,
      password, referent_first_name: firstName, referent_last_name: lastName,
      referent_function: func, charte_ethique_signed: true,
      consent_cgu: true, consent_privacy: true
    });
    if (result.success) {
      if (result.emailWarning) toast.info(result.emailWarning);
      toast.success("Compte entreprise créé !");
      onSuccess?.();
    } else {
      toast.error(result.error);
    }
    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label>Nom de l'entreprise <span className="text-red-500">*</span></Label>
        <Input placeholder="Ex: ACME SAS" value={companyName} onChange={(e) => setCompanyName(e.target.value)}
          data-testid="ent-company-name" />
      </div>

      <SiretField siret={siret} setSiret={setSiret} siretResult={siretResult} setSiretResult={setSiretResult}
        setCompanyFromSiret={(name) => { if (!companyName) setCompanyName(name); }} />

      <div className="space-y-2">
        <Label>Email professionnel <span className="text-red-500">*</span></Label>
        <div className="relative">
          <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <Input type="email" placeholder="referent@entreprise.fr" value={email}
            onChange={(e) => setEmail(e.target.value)} className="pl-10" data-testid="ent-email" autoComplete="email" />
        </div>
        <EmailWarning email={email} />
      </div>

      <div className="space-y-2">
        <Label>Mot de passe <span className="text-red-500">*</span></Label>
        <div className="relative">
          <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <Input type={showPwd ? "text" : "password"} placeholder="Minimum 6 caractères" value={password}
            onChange={(e) => setPassword(e.target.value)} className="pl-10 pr-10" data-testid="ent-password" autoComplete="new-password" />
          <button type="button" onClick={() => setShowPwd(!showPwd)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
            {showPwd ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-2">
          <Label>Prénom du référent <span className="text-red-500">*</span></Label>
          <Input placeholder="Prénom" value={firstName} onChange={(e) => setFirstName(e.target.value)}
            data-testid="ent-first-name" />
        </div>
        <div className="space-y-2">
          <Label>Nom du référent <span className="text-red-500">*</span></Label>
          <Input placeholder="Nom" value={lastName} onChange={(e) => setLastName(e.target.value)}
            data-testid="ent-last-name" />
        </div>
      </div>

      <div className="space-y-2">
        <Label>Fonction <span className="text-red-500">*</span></Label>
        <Select value={func} onValueChange={setFunc}>
          <SelectTrigger data-testid="ent-function">
            <SelectValue placeholder="Sélectionnez votre fonction" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="rh">Responsable RH</SelectItem>
            <SelectItem value="dirigeant">Dirigeant</SelectItem>
            <SelectItem value="recruteur">Recruteur</SelectItem>
            <SelectItem value="manager">Manager</SelectItem>
            <SelectItem value="autre">Autre</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <CharteEthiqueSection signed={charteSigned} setSigned={setCharteSigned} />

      <div className="space-y-3">
        <div className="flex items-start gap-2">
          <Checkbox id="ent-cgu" checked={consentCgu} onCheckedChange={setConsentCgu} data-testid="ent-consent-cgu" />
          <label htmlFor="ent-cgu" className="text-sm text-slate-600 cursor-pointer leading-tight">
            J'accepte les <span className="text-[#1e3a5f] font-medium underline">CGU</span> <span className="text-red-500">*</span>
          </label>
        </div>
        <div className="flex items-start gap-2">
          <Checkbox id="ent-privacy" checked={consentPrivacy} onCheckedChange={setConsentPrivacy} data-testid="ent-consent-privacy" />
          <label htmlFor="ent-privacy" className="text-sm text-slate-600 cursor-pointer leading-tight">
            J'accepte la <span className="text-[#1e3a5f] font-medium underline">politique de confidentialité</span> <span className="text-red-500">*</span>
          </label>
        </div>
      </div>

      <Button type="submit" className="w-full bg-[#1e3a5f] hover:bg-[#152a45]" disabled={loading || !isValid}
        data-testid="ent-register-submit">
        {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <>Créer mon compte employeur <ArrowRight className="w-4 h-4 ml-2" /></>}
      </Button>
    </form>
  );
};

const PartenaireForm = ({ onSuccess }) => {
  const { registerPartenaire } = useAuth();
  const [structureName, setStructureName] = useState("");
  const [structureType, setStructureType] = useState("");
  const [siret, setSiret] = useState("");
  const [siretResult, setSiretResult] = useState(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPwd, setShowPwd] = useState(false);
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [func, setFunc] = useState("");
  const [charteSigned, setCharteSigned] = useState(false);
  const [consentCgu, setConsentCgu] = useState(false);
  const [consentPrivacy, setConsentPrivacy] = useState(false);
  const [loading, setLoading] = useState(false);

  const isValid = structureName.trim() && structureType && siret.replace(/\s/g, "").length >= 9
    && email.includes("@") && password.length >= 6 && firstName.trim() && lastName.trim() && func
    && charteSigned && consentCgu && consentPrivacy;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!isValid) return;
    setLoading(true);
    const result = await registerPartenaire({
      structure_name: structureName, structure_type: structureType,
      siret: siret.replace(/\s/g, ""), email, password,
      referent_first_name: firstName, referent_last_name: lastName,
      referent_function: func, charte_ethique_signed: true,
      consent_cgu: true, consent_privacy: true
    });
    if (result.success) {
      toast.success("Compte partenaire créé !");
      onSuccess?.();
    } else {
      toast.error(result.error);
    }
    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label>Nom de la structure <span className="text-red-500">*</span></Label>
        <Input placeholder="Ex: Mission Locale de Strasbourg" value={structureName}
          onChange={(e) => setStructureName(e.target.value)} data-testid="part-structure-name" />
      </div>

      <div className="space-y-2">
        <Label>Type de structure <span className="text-red-500">*</span></Label>
        <Select value={structureType} onValueChange={setStructureType}>
          <SelectTrigger data-testid="part-structure-type">
            <SelectValue placeholder="Sélectionnez le type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="organisme_formation">Organisme de formation</SelectItem>
            <SelectItem value="association">Association</SelectItem>
            <SelectItem value="institution_publique">Institution publique</SelectItem>
            <SelectItem value="acteur_insertion">Acteur de l'insertion (mission locale, etc.)</SelectItem>
            <SelectItem value="autre">Autre</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <SiretField siret={siret} setSiret={setSiret} siretResult={siretResult} setSiretResult={setSiretResult}
        setCompanyFromSiret={(name) => { if (!structureName) setStructureName(name); }} />

      <div className="space-y-2">
        <Label>Email professionnel <span className="text-red-500">*</span></Label>
        <div className="relative">
          <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <Input type="email" placeholder="referent@structure.fr" value={email}
            onChange={(e) => setEmail(e.target.value)} className="pl-10" data-testid="part-email" autoComplete="email" />
        </div>
      </div>

      <div className="space-y-2">
        <Label>Mot de passe <span className="text-red-500">*</span></Label>
        <div className="relative">
          <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <Input type={showPwd ? "text" : "password"} placeholder="Minimum 6 caractères" value={password}
            onChange={(e) => setPassword(e.target.value)} className="pl-10 pr-10" data-testid="part-password" autoComplete="new-password" />
          <button type="button" onClick={() => setShowPwd(!showPwd)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
            {showPwd ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-2">
          <Label>Prénom du référent <span className="text-red-500">*</span></Label>
          <Input placeholder="Prénom" value={firstName} onChange={(e) => setFirstName(e.target.value)}
            data-testid="part-first-name" />
        </div>
        <div className="space-y-2">
          <Label>Nom du référent <span className="text-red-500">*</span></Label>
          <Input placeholder="Nom" value={lastName} onChange={(e) => setLastName(e.target.value)}
            data-testid="part-last-name" />
        </div>
      </div>

      <div className="space-y-2">
        <Label>Fonction <span className="text-red-500">*</span></Label>
        <Select value={func} onValueChange={setFunc}>
          <SelectTrigger data-testid="part-function">
            <SelectValue placeholder="Sélectionnez votre fonction" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="conseiller">Conseiller emploi / insertion</SelectItem>
            <SelectItem value="formateur">Formateur</SelectItem>
            <SelectItem value="directeur">Directeur / Responsable</SelectItem>
            <SelectItem value="charge_mission">Chargé de mission</SelectItem>
            <SelectItem value="autre">Autre</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <CharteEthiqueSection signed={charteSigned} setSigned={setCharteSigned} />

      <div className="space-y-3">
        <div className="flex items-start gap-2">
          <Checkbox id="part-cgu" checked={consentCgu} onCheckedChange={setConsentCgu} data-testid="part-consent-cgu" />
          <label htmlFor="part-cgu" className="text-sm text-slate-600 cursor-pointer leading-tight">
            J'accepte les <span className="text-[#1e3a5f] font-medium underline">CGU</span> <span className="text-red-500">*</span>
          </label>
        </div>
        <div className="flex items-start gap-2">
          <Checkbox id="part-privacy" checked={consentPrivacy} onCheckedChange={setConsentPrivacy} data-testid="part-consent-privacy" />
          <label htmlFor="part-privacy" className="text-sm text-slate-600 cursor-pointer leading-tight">
            J'accepte la <span className="text-[#1e3a5f] font-medium underline">politique de confidentialité</span> <span className="text-red-500">*</span>
          </label>
        </div>
      </div>

      <Button type="submit" className="w-full bg-[#1e3a5f] hover:bg-[#152a45]" disabled={loading || !isValid}
        data-testid="part-register-submit">
        {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <>Créer mon compte partenaire <ArrowRight className="w-4 h-4 ml-2" /></>}
      </Button>
    </form>
  );
};

export default ProRegisterModal;
