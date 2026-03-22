import { useState } from "react";
import { useAuth } from "@/App";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { Shield, User, Lock, Mail, Eye, EyeOff, ArrowRight, CheckCircle2, Info } from "lucide-react";

const AuthModal = ({ open, onOpenChange, defaultRole = "particulier", onSuccess }) => {
  const [tab, setTab] = useState("login"); // login, register
  const { loginPseudo, register } = useAuth();

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[460px] p-0 overflow-hidden" data-testid="auth-modal">
        {/* Header */}
        <div className="bg-[#1e3a5f] px-6 pt-6 pb-5">
          <DialogHeader>
            <DialogTitle className="text-white text-xl" style={{ fontFamily: 'Outfit, sans-serif' }}>
              {tab === "login" ? "Connexion" : "Créer un compte"}
            </DialogTitle>
          </DialogHeader>
          <p className="text-blue-200 text-sm mt-1">
            Espace personnel confidentiel sous pseudonyme
          </p>
          {/* Tab Switcher */}
          <div className="flex gap-2 mt-4">
            <button
              onClick={() => setTab("login")}
              className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-all ${
                tab === "login"
                  ? "bg-white text-[#1e3a5f]"
                  : "bg-white/15 text-blue-100 hover:bg-white/25"
              }`}
              data-testid="auth-tab-login"
            >
              Se connecter
            </button>
            <button
              onClick={() => setTab("register")}
              className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-all ${
                tab === "register"
                  ? "bg-white text-[#1e3a5f]"
                  : "bg-white/15 text-blue-100 hover:bg-white/25"
              }`}
              data-testid="auth-tab-register"
            >
              Créer un compte
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          {tab === "login" ? (
            <LoginForm onSuccess={onSuccess} loginPseudo={loginPseudo} />
          ) : (
            <RegisterForm onSuccess={onSuccess} register={register} defaultRole={defaultRole} />
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};

const LoginForm = ({ onSuccess, loginPseudo }) => {
  const [pseudo, setPseudo] = useState("");
  const [password, setPassword] = useState("");
  const [showPwd, setShowPwd] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!pseudo.trim() || !password) return;
    setLoading(true);
    const result = await loginPseudo(pseudo, password);
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
        <Label htmlFor="login-pseudo" className="text-slate-700 font-medium">Pseudonyme</Label>
        <div className="relative">
          <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <Input
            id="login-pseudo"
            placeholder="Votre pseudonyme"
            value={pseudo}
            onChange={(e) => setPseudo(e.target.value)}
            className="pl-10"
            data-testid="login-pseudo-input"
            autoComplete="username"
          />
        </div>
      </div>
      <div className="space-y-2">
        <Label htmlFor="login-password" className="text-slate-700 font-medium">Mot de passe</Label>
        <div className="relative">
          <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <Input
            id="login-password"
            type={showPwd ? "text" : "password"}
            placeholder="Votre mot de passe"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="pl-10 pr-10"
            data-testid="login-password-input"
            autoComplete="current-password"
          />
          <button
            type="button"
            onClick={() => setShowPwd(!showPwd)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
          >
            {showPwd ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        </div>
      </div>
      <Button
        type="submit"
        className="w-full bg-[#1e3a5f] hover:bg-[#152a45] text-white"
        disabled={loading || !pseudo.trim() || !password}
        data-testid="login-submit-btn"
      >
        {loading ? (
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
        ) : (
          <>Se connecter <ArrowRight className="w-4 h-4 ml-2" /></>
        )}
      </Button>
    </form>
  );
};

const RegisterForm = ({ onSuccess, register, defaultRole }) => {
  const [pseudo, setPseudo] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPwd, setConfirmPwd] = useState("");
  const [email, setEmail] = useState("");
  const [showPwd, setShowPwd] = useState(false);
  const [consentCgu, setConsentCgu] = useState(false);
  const [consentPrivacy, setConsentPrivacy] = useState(false);
  const [loading, setLoading] = useState(false);

  const isValid = pseudo.trim().length >= 3 && password.length >= 6 && password === confirmPwd && consentCgu && consentPrivacy;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!isValid) return;
    setLoading(true);
    const result = await register(pseudo, password, defaultRole, email || null, false);
    if (result.success) {
      toast.success("Compte créé avec succès !");
      onSuccess?.();
    } else {
      toast.error(result.error);
    }
    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Privacy reassurance */}
      <div className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg border border-blue-100">
        <Shield className="w-5 h-5 text-[#1e3a5f] mt-0.5 flex-shrink-0" />
        <div>
          <p className="text-sm text-[#1e3a5f] font-medium">Inscription sous pseudonyme</p>
          <p className="text-xs text-slate-500 mt-0.5">
            Aucune identité civile n'est requise. Seules les données strictement nécessaires sont collectées.
          </p>
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="reg-pseudo" className="text-slate-700 font-medium">
          Pseudonyme <span className="text-red-500">*</span>
        </Label>
        <div className="relative">
          <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <Input
            id="reg-pseudo"
            placeholder="Choisissez un pseudonyme (min. 3 caractères)"
            value={pseudo}
            onChange={(e) => setPseudo(e.target.value)}
            className="pl-10"
            data-testid="register-pseudo-input"
            autoComplete="username"
          />
        </div>
        {pseudo.length > 0 && pseudo.length < 3 && (
          <p className="text-xs text-red-500">Minimum 3 caractères</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="reg-password" className="text-slate-700 font-medium">
          Mot de passe <span className="text-red-500">*</span>
        </Label>
        <div className="relative">
          <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <Input
            id="reg-password"
            type={showPwd ? "text" : "password"}
            placeholder="Minimum 6 caractères"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="pl-10 pr-10"
            data-testid="register-password-input"
            autoComplete="new-password"
          />
          <button
            type="button"
            onClick={() => setShowPwd(!showPwd)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
          >
            {showPwd ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="reg-confirm" className="text-slate-700 font-medium">
          Confirmer le mot de passe <span className="text-red-500">*</span>
        </Label>
        <div className="relative">
          <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <Input
            id="reg-confirm"
            type={showPwd ? "text" : "password"}
            placeholder="Confirmez votre mot de passe"
            value={confirmPwd}
            onChange={(e) => setConfirmPwd(e.target.value)}
            className="pl-10"
            data-testid="register-confirm-input"
            autoComplete="new-password"
          />
        </div>
        {confirmPwd && password !== confirmPwd && (
          <p className="text-xs text-red-500">Les mots de passe ne correspondent pas</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="reg-email" className="text-slate-700 font-medium flex items-center gap-2">
          Email de récupération
          <Badge variant="secondary" className="text-xs font-normal">Facultatif</Badge>
        </Label>
        <div className="relative">
          <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <Input
            id="reg-email"
            type="email"
            placeholder="Uniquement pour récupérer votre compte"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="pl-10"
            data-testid="register-email-input"
            autoComplete="email"
          />
        </div>
        <p className="text-xs text-slate-400 flex items-center gap-1">
          <Info className="w-3 h-3" /> Ne sera utilisé que pour la récupération de mot de passe
        </p>
      </div>

      {/* Consents */}
      <div className="space-y-3 pt-2">
        <div className="flex items-start gap-2">
          <Checkbox
            id="consent-cgu"
            checked={consentCgu}
            onCheckedChange={setConsentCgu}
            data-testid="register-consent-cgu"
          />
          <label htmlFor="consent-cgu" className="text-sm text-slate-600 cursor-pointer leading-tight">
            J'accepte les <span className="text-[#1e3a5f] font-medium underline">conditions générales d'utilisation</span> <span className="text-red-500">*</span>
          </label>
        </div>
        <div className="flex items-start gap-2">
          <Checkbox
            id="consent-privacy"
            checked={consentPrivacy}
            onCheckedChange={setConsentPrivacy}
            data-testid="register-consent-privacy"
          />
          <label htmlFor="consent-privacy" className="text-sm text-slate-600 cursor-pointer leading-tight">
            J'ai lu et j'accepte la <span className="text-[#1e3a5f] font-medium underline">politique de confidentialité</span> <span className="text-red-500">*</span>
          </label>
        </div>
      </div>

      <Button
        type="submit"
        className="w-full bg-[#1e3a5f] hover:bg-[#152a45] text-white mt-2"
        disabled={loading || !isValid}
        data-testid="register-submit-btn"
      >
        {loading ? (
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
        ) : (
          <>Créer mon compte confidentiel <CheckCircle2 className="w-4 h-4 ml-2" /></>
        )}
      </Button>
    </form>
  );
};

export default AuthModal;
