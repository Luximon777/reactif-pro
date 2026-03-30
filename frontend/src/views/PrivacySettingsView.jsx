import { useState, useEffect } from "react";
import axios from "axios";
import { API, useAuth } from "@/App";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import {
  Dialog, DialogContent, DialogDescription, DialogFooter,
  DialogHeader, DialogTitle, DialogTrigger
} from "@/components/ui/dialog";
import {
  Shield, User, Eye, EyeOff, Lock, Download, Trash2,
  CheckCircle2, AlertTriangle, Info, ArrowUpCircle, Mail
} from "lucide-react";
import { toast } from "sonner";

const PrivacySettingsView = ({ token }) => {
  const { authMode, pseudo, logout, upgradeAccount } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [upgradeOpen, setUpgradeOpen] = useState(false);
  const [changePwdOpen, setChangePwdOpen] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [deleting, setDeleting] = useState(false);

  // Privacy form
  const [visibilityLevel, setVisibilityLevel] = useState("private");
  const [displayName, setDisplayName] = useState("");
  const [bio, setBio] = useState("");
  const [consentMarketing, setConsentMarketing] = useState(false);
  const [realFirstName, setRealFirstName] = useState("");
  const [realLastName, setRealLastName] = useState("");

  useEffect(() => { loadProfile(); }, [token]);

  const loadProfile = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/profile?token=${token}`);
      setProfile(res.data);
      setVisibilityLevel(res.data.visibility_level || "private");
      setDisplayName(res.data.display_name || "");
      setBio(res.data.bio || "");
      setConsentMarketing(res.data.consent_marketing || false);
      setRealFirstName(res.data.real_first_name || "");
      setRealLastName(res.data.real_last_name || "");
    } catch (err) {
      toast.error("Erreur chargement du profil");
    }
    setLoading(false);
  };

  const savePrivacy = async () => {
    if (visibilityLevel === "limited" && (!realFirstName.trim() || !realLastName.trim())) {
      toast.error("Nom et prénom requis pour le mode Limité");
      return;
    }
    setSaving(true);
    try {
      const params = new URLSearchParams({ token });
      if (visibilityLevel) params.append("visibility_level", visibilityLevel);
      if (displayName !== undefined) params.append("display_name", displayName);
      if (bio !== undefined) params.append("bio", bio);
      params.append("consent_marketing", consentMarketing);
      if (realFirstName !== undefined) params.append("real_first_name", realFirstName);
      if (realLastName !== undefined) params.append("real_last_name", realLastName);
      await axios.put(`${API}/profile/privacy?${params.toString()}`);
      toast.success("Paramètres de confidentialité mis à jour");
      loadProfile();
    } catch (err) {
      toast.error("Erreur lors de la sauvegarde");
    }
    setSaving(false);
  };

  const handleExport = async () => {
    setExporting(true);
    try {
      const res = await axios.get(`${API}/auth/export-data?token=${token}`);
      const blob = new Blob([JSON.stringify(res.data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `reactif-pro-export-${new Date().toISOString().split("T")[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);
      toast.success("Données exportées avec succès");
    } catch (err) {
      toast.error("Erreur lors de l'export");
    }
    setExporting(false);
  };

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await axios.delete(`${API}/auth/account?token=${token}`);
      toast.success("Compte et données supprimés");
      logout();
    } catch (err) {
      toast.error("Erreur lors de la suppression");
    }
    setDeleting(false);
    setDeleteConfirmOpen(false);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
      </div>
    );
  }

  const visibilityOptions = [
    { value: "private", label: "Privé", desc: "Seul vous pouvez voir vos informations. Votre anonymat est préservé.", icon: Lock },
    { value: "limited", label: "Limité", desc: "Accessible aux partenaires de parcours autorisés. Votre nom et prénom seront communiqués.", icon: Eye },
    { value: "public", label: "Public", desc: "Votre profil pseudonyme est visible par tous", icon: EyeOff },
  ];

  return (
    <div className="space-y-8 animate-fade-in max-w-3xl" data-testid="privacy-settings">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>
          Paramètres de Confidentialité
        </h1>
        <p className="text-slate-600 mt-1">Gérez votre identité, vos données et votre niveau de visibilité</p>
      </div>

      {/* Account Status */}
      <Card className="border-l-4 border-l-[#1e3a5f]" data-testid="account-status-card">
        <CardContent className="p-6">
          <div className="flex items-start justify-between gap-4 flex-wrap">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center flex-shrink-0">
                <Shield className="w-6 h-6 text-[#1e3a5f]" />
              </div>
              <div>
                <h3 className="font-semibold text-slate-900">Statut du compte</h3>
                <div className="flex items-center gap-2 mt-1 flex-wrap">
                  <Badge className={authMode === "pseudo" ? "bg-green-100 text-green-700 border-green-200" : "bg-amber-100 text-amber-700 border-amber-200"}>
                    {authMode === "pseudo" ? "Compte pseudonyme" : "Compte anonyme"}
                  </Badge>
                  <Badge className="bg-slate-100 text-slate-600 border-slate-200">
                    Niveau : {profile?.identity_level === "none" ? "Non vérifié" : profile?.identity_level === "verified" ? "Vérifié" : "Vérifié+"}
                  </Badge>
                </div>
                {pseudo && <p className="text-sm text-slate-500 mt-1">Pseudo : <span className="font-medium text-slate-700">{pseudo}</span></p>}
              </div>
            </div>
            {authMode === "anonymous" && (
              <Button
                variant="outline"
                className="border-[#1e3a5f] text-[#1e3a5f] hover:bg-blue-50"
                onClick={() => setUpgradeOpen(true)}
                data-testid="upgrade-account-btn"
              >
                <ArrowUpCircle className="w-4 h-4 mr-2" />
                Passer en pseudonyme
              </Button>
            )}
          </div>

          {/* Info about FranceConnect */}
          <div className="mt-4 p-3 bg-slate-50 rounded-lg border border-slate-100">
            <div className="flex items-start gap-2">
              <Info className="w-4 h-4 text-slate-400 mt-0.5 flex-shrink-0" />
              <p className="text-xs text-slate-500">
                <strong>Certification d'identité (bientôt disponible)</strong> : Vous pourrez certifier votre identité via FranceConnect / L'Identité Numérique La Poste pour accéder à des fonctionnalités avancées. Votre pseudonyme restera votre identité publique.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Visibility Level */}
      <Card data-testid="visibility-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Eye className="w-5 h-5 text-[#1e3a5f]" />
            Niveau de visibilité
          </CardTitle>
          <CardDescription>Choisissez qui peut voir votre profil</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {visibilityOptions.map((opt) => {
            const Icon = opt.icon;
            const isSelected = visibilityLevel === opt.value;
            return (
              <button
                key={opt.value}
                onClick={() => setVisibilityLevel(opt.value)}
                className={`w-full flex items-start gap-3 p-4 rounded-lg border-2 transition-all text-left ${
                  isSelected ? "border-[#1e3a5f] bg-blue-50/50" : "border-slate-100 hover:border-slate-200"
                }`}
                data-testid={`visibility-${opt.value}`}
              >
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                  isSelected ? "bg-[#1e3a5f] text-white" : "bg-slate-100 text-slate-400"
                }`}>
                  <Icon className="w-4 h-4" />
                </div>
                <div>
                  <p className={`font-medium ${isSelected ? "text-[#1e3a5f]" : "text-slate-700"}`}>{opt.label}</p>
                  <p className="text-xs text-slate-500">{opt.desc}</p>
                </div>
                {isSelected && <CheckCircle2 className="w-5 h-5 text-[#1e3a5f] ml-auto flex-shrink-0 mt-1" />}
              </button>
            );
          })}

          {visibilityLevel === "limited" && (
            <div className="space-y-4 mt-4 p-4 bg-amber-50/50 rounded-lg border border-amber-200">
              <div className="flex items-start gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-sm font-medium text-amber-800">Levée de l'anonymat</p>
                  <p className="text-xs text-amber-700 mt-1">
                    En choisissant le mode "Limité", vous acceptez que votre nom et prénom soient communiqués aux partenaires de parcours (Mission Locale, France Travail, APEC, etc.) qui effectuent une demande d'accès à votre profil. Vos données restent protégées et le partage est révocable à tout moment.
                  </p>
                </div>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="space-y-2">
                  <Label htmlFor="real-first-name">Prénom *</Label>
                  <Input
                    id="real-first-name"
                    placeholder="Votre prénom"
                    value={realFirstName}
                    onChange={(e) => setRealFirstName(e.target.value)}
                    data-testid="real-first-name-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="real-last-name">Nom *</Label>
                  <Input
                    id="real-last-name"
                    placeholder="Votre nom de famille"
                    value={realLastName}
                    onChange={(e) => setRealLastName(e.target.value)}
                    data-testid="real-last-name-input"
                  />
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Display Name & Bio */}
      <Card data-testid="display-info-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <User className="w-5 h-5 text-[#1e3a5f]" />
            Profil public
          </CardTitle>
          <CardDescription>Informations visibles selon votre niveau de visibilité</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="display-name">Nom d'affichage</Label>
            <Input
              id="display-name"
              placeholder="Laissez vide pour utiliser votre pseudo"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              data-testid="display-name-input"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="bio">Bio (courte description)</Label>
            <Textarea
              id="bio"
              placeholder="Décrivez-vous en quelques mots (facultatif)"
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              rows={3}
              data-testid="bio-input"
            />
          </div>
        </CardContent>
      </Card>

      {/* Consents */}
      <Card data-testid="consents-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <CheckCircle2 className="w-5 h-5 text-[#1e3a5f]" />
            Consentements
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg border border-green-100">
            <div>
              <p className="text-sm font-medium text-green-800">Conditions générales d'utilisation</p>
              <p className="text-xs text-green-600">Acceptées lors de l'inscription</p>
            </div>
            <Badge className="bg-green-100 text-green-700">Accepté</Badge>
          </div>
          <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg border border-green-100">
            <div>
              <p className="text-sm font-medium text-green-800">Politique de confidentialité</p>
              <p className="text-xs text-green-600">Acceptée lors de l'inscription</p>
            </div>
            <Badge className="bg-green-100 text-green-700">Accepté</Badge>
          </div>
          <div className="flex items-center justify-between p-3 rounded-lg border border-slate-100">
            <div>
              <p className="text-sm font-medium text-slate-700">Communications marketing</p>
              <p className="text-xs text-slate-500">Recevoir des informations et actualités</p>
            </div>
            <Switch
              checked={consentMarketing}
              onCheckedChange={setConsentMarketing}
              data-testid="consent-marketing-switch"
            />
          </div>
        </CardContent>
      </Card>

      {/* Access Requests History */}
      <AccessHistoryCard token={token} />

      {/* Save Button */}
      <div className="flex justify-end">
        <Button
          onClick={savePrivacy}
          disabled={saving}
          className="bg-[#1e3a5f] hover:bg-[#152a45] text-white px-8"
          data-testid="save-privacy-btn"
        >
          {saving ? "Enregistrement..." : "Enregistrer les modifications"}
        </Button>
      </div>

      {/* Security Section */}
      {authMode === "pseudo" && (
        <Card data-testid="security-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Lock className="w-5 h-5 text-[#1e3a5f]" />
              Sécurité
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Button
              variant="outline"
              onClick={() => setChangePwdOpen(true)}
              data-testid="change-password-btn"
            >
              <Lock className="w-4 h-4 mr-2" />
              Changer le mot de passe
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Data Management */}
      <Card className="border-amber-200" data-testid="data-management-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg text-amber-700">
            <AlertTriangle className="w-5 h-5" />
            Gestion des données
          </CardTitle>
          <CardDescription>Exportez ou supprimez vos données personnelles</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <Button
              variant="outline"
              onClick={handleExport}
              disabled={exporting}
              data-testid="export-data-btn"
            >
              <Download className="w-4 h-4 mr-2" />
              {exporting ? "Export en cours..." : "Exporter mes données"}
            </Button>
            <Button
              variant="outline"
              className="border-red-200 text-red-600 hover:bg-red-50 hover:text-red-700"
              onClick={() => setDeleteConfirmOpen(true)}
              data-testid="delete-account-btn"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Supprimer mon compte
            </Button>
          </div>
          <p className="text-xs text-slate-400">
            La suppression du compte efface définitivement toutes vos données : profil, passeport, coffre-fort et analyses CV.
          </p>
        </CardContent>
      </Card>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteConfirmOpen} onOpenChange={setDeleteConfirmOpen}>
        <DialogContent data-testid="delete-confirm-dialog">
          <DialogHeader>
            <DialogTitle className="text-red-600 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5" /> Supprimer le compte
            </DialogTitle>
            <DialogDescription>
              Cette action est irréversible. Toutes vos données seront définitivement supprimées.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="gap-2">
            <Button variant="outline" onClick={() => setDeleteConfirmOpen(false)} data-testid="delete-cancel-btn">
              Annuler
            </Button>
            <Button
              variant="destructive"
              onClick={handleDelete}
              disabled={deleting}
              data-testid="delete-confirm-btn"
            >
              {deleting ? "Suppression..." : "Confirmer la suppression"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Upgrade Dialog */}
      <UpgradeDialog open={upgradeOpen} onOpenChange={setUpgradeOpen} token={token} upgradeAccount={upgradeAccount} onSuccess={loadProfile} />

      {/* Change Password Dialog */}
      <ChangePasswordDialog open={changePwdOpen} onOpenChange={setChangePwdOpen} token={token} />
    </div>
  );
};

const UpgradeDialog = ({ open, onOpenChange, token, upgradeAccount, onSuccess }) => {
  const [pseudo, setPseudo] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);

  const handleUpgrade = async () => {
    if (pseudo.trim().length < 3 || password.length < 6) {
      toast.error("Pseudo (min 3 car.) et mot de passe (min 6 car.) requis");
      return;
    }
    setLoading(true);
    const result = await upgradeAccount(pseudo, password, email || null);
    if (result.success) {
      toast.success("Compte mis à niveau vers pseudonyme !");
      onOpenChange(false);
      onSuccess?.();
    } else {
      toast.error(result.error);
    }
    setLoading(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent data-testid="upgrade-dialog">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <ArrowUpCircle className="w-5 h-5 text-[#1e3a5f]" />
            Passer en compte pseudonyme
          </DialogTitle>
          <DialogDescription>
            Sécurisez votre compte avec un pseudo et un mot de passe. Vous conservez toutes vos données existantes.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-2">
          <div className="space-y-2">
            <Label>Pseudonyme</Label>
            <Input placeholder="Min. 3 caractères" value={pseudo} onChange={(e) => setPseudo(e.target.value)} data-testid="upgrade-pseudo-input" />
          </div>
          <div className="space-y-2">
            <Label>Mot de passe</Label>
            <Input type="password" placeholder="Min. 6 caractères" value={password} onChange={(e) => setPassword(e.target.value)} data-testid="upgrade-password-input" />
          </div>
          <div className="space-y-2">
            <Label className="flex items-center gap-2">
              Email de récupération <Badge variant="secondary" className="text-xs">Facultatif</Badge>
            </Label>
            <Input type="email" placeholder="Pour récupérer votre compte" value={email} onChange={(e) => setEmail(e.target.value)} data-testid="upgrade-email-input" />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>Annuler</Button>
          <Button onClick={handleUpgrade} disabled={loading} className="bg-[#1e3a5f] text-white" data-testid="upgrade-submit-btn">
            {loading ? "Mise à niveau..." : "Confirmer"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

const ChangePasswordDialog = ({ open, onOpenChange, token }) => {
  const [current, setCurrent] = useState("");
  const [newPwd, setNewPwd] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = async () => {
    if (newPwd.length < 6) {
      toast.error("Le nouveau mot de passe doit contenir au moins 6 caractères");
      return;
    }
    setLoading(true);
    try {
      await axios.post(`${API}/auth/change-password?token=${token}`, {
        current_password: current,
        new_password: newPwd
      });
      toast.success("Mot de passe modifié");
      onOpenChange(false);
      setCurrent("");
      setNewPwd("");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Erreur");
    }
    setLoading(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent data-testid="change-password-dialog">
        <DialogHeader>
          <DialogTitle>Changer le mot de passe</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 py-2">
          <div className="space-y-2">
            <Label>Mot de passe actuel</Label>
            <Input type="password" value={current} onChange={(e) => setCurrent(e.target.value)} data-testid="current-password-input" />
          </div>
          <div className="space-y-2">
            <Label>Nouveau mot de passe</Label>
            <Input type="password" placeholder="Min. 6 caractères" value={newPwd} onChange={(e) => setNewPwd(e.target.value)} data-testid="new-password-input" />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>Annuler</Button>
          <Button onClick={handleChange} disabled={loading} className="bg-[#1e3a5f] text-white" data-testid="change-password-submit-btn">
            {loading ? "Modification..." : "Confirmer"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

// ===== HISTORIQUE DES ACCES PARTENAIRES =====
const AccessHistoryCard = ({ token }) => {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [responding, setResponding] = useState(null);

  useEffect(() => { loadRequests(); }, []);

  const loadRequests = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/notifications/access-requests?token=${token}`);
      setRequests(res.data);
    } catch {}
    setLoading(false);
  };

  const respond = async (requestId, action) => {
    setResponding(requestId);
    try {
      await axios.post(`${API}/notifications/access-requests/${requestId}/respond?token=${token}`, { action }, { headers: { "Content-Type": "application/json" } });
      toast.success(action === "accept" ? "Accès autorisé" : "Demande refusée");
      loadRequests();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Erreur");
    }
    setResponding(null);
  };

  if (loading) return null;
  if (requests.length === 0) return null;

  const pending = requests.filter(r => r.status === "en_attente");
  const past = requests.filter(r => r.status !== "en_attente");

  return (
    <Card data-testid="access-history-card">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-lg">
          <Eye className="w-5 h-5 text-[#1e3a5f]" />
          Historique des accès partenaires
          {pending.length > 0 && <Badge className="bg-amber-100 text-amber-700 text-xs ml-1">{pending.length} en attente</Badge>}
        </CardTitle>
        <CardDescription>Demandes d'accès à votre profil par les partenaires de parcours</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {pending.map(req => (
          <div key={req.id} className="flex items-center justify-between p-3 rounded-lg border border-amber-200 bg-amber-50/50" data-testid={`privacy-req-${req.id}`}>
            <div>
              <p className="text-sm font-semibold text-slate-800">{req.partner_name}</p>
              <p className="text-xs text-slate-500">Demandé le {new Date(req.created_at).toLocaleDateString('fr-FR')}</p>
              <p className="text-xs text-amber-600 mt-1">En acceptant, votre nom et prénom seront communiqués.</p>
            </div>
            <div className="flex gap-2 flex-shrink-0">
              <Button size="sm" className="bg-green-600 hover:bg-green-700 h-7 text-xs" onClick={() => respond(req.id, "accept")}
                disabled={responding === req.id} data-testid={`privacy-accept-${req.id}`}>
                <CheckCircle2 className="w-3 h-3 mr-1" /> Accepter
              </Button>
              <Button size="sm" variant="outline" className="text-red-500 hover:bg-red-50 h-7 text-xs border-red-200" onClick={() => respond(req.id, "reject")}
                disabled={responding === req.id} data-testid={`privacy-reject-${req.id}`}>
                Refuser
              </Button>
            </div>
          </div>
        ))}
        {past.length > 0 && (
          <div className={pending.length > 0 ? "pt-2 border-t border-slate-100" : ""}>
            {pending.length > 0 && <p className="text-xs font-medium text-slate-500 mb-2">Historique</p>}
            <div className="space-y-1">
              {past.map(req => (
                <div key={req.id} className="flex items-center justify-between py-2 px-3 rounded-lg bg-slate-50" data-testid={`privacy-history-${req.id}`}>
                  <div>
                    <p className="text-sm text-slate-700">{req.partner_name}</p>
                    <p className="text-xs text-slate-400">{new Date(req.responded_at || req.created_at).toLocaleDateString('fr-FR')}</p>
                  </div>
                  <Badge className={req.status === "accepte" ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}>
                    {req.status === "accepte" ? "Accepté" : "Refusé"}
                  </Badge>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default PrivacySettingsView;
