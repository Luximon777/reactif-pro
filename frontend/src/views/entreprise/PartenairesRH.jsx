import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Handshake, Plus, Trash2, Building2, GraduationCap, Users, UserCheck, Loader2 } from "lucide-react";
import { toast } from "sonner";

const TYPE_INFO = {
  france_travail: { label: "France Travail", color: "bg-blue-100 text-blue-700", icon: Building2 },
  formation: { label: "Organisme formation", color: "bg-emerald-100 text-emerald-700", icon: GraduationCap },
  consultant: { label: "Consultant", color: "bg-purple-100 text-purple-700", icon: UserCheck },
  organisme: { label: "Organisme", color: "bg-amber-100 text-amber-700", icon: Users },
};

const PartenairesRH = ({ token }) => {
  const [partners, setPartners] = useState([]);
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);

  const load = () => {
    setLoading(true);
    axios.get(`${API}/entreprise/partenaires?token=${token}`)
      .then(r => setPartners(r.data)).catch(() => {}).finally(() => setLoading(false));
  };
  useEffect(load, [token]);

  const handleDelete = async (id) => {
    try { await axios.delete(`${API}/entreprise/partenaires/${id}?token=${token}`); toast.success("Supprimé"); load(); } catch { toast.error("Erreur"); }
  };

  if (loading) return <div className="flex justify-center py-20"><Loader2 className="w-8 h-8 animate-spin text-emerald-600" /></div>;

  return (
    <div className="space-y-6" data-testid="partenaires-view">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>Partenaires de parcours</h1>
          <p className="text-sm text-slate-500">Ecosysteme d'accompagnement coordonne</p>
        </div>
        <Button onClick={() => setCreateOpen(true)} className="bg-emerald-600 hover:bg-emerald-700" data-testid="add-partner-btn">
          <Plus className="w-4 h-4 mr-1.5" />Ajouter un partenaire
        </Button>
      </div>

      <Card className="border border-emerald-200 bg-emerald-50/30">
        <CardContent className="p-4 flex items-start gap-3">
          <Handshake className="w-5 h-5 text-emerald-600 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-slate-800">Coordination des parcours</p>
            <p className="text-xs text-slate-500">Connectez-vous avec France Travail, organismes de formation et consultants pour un suivi coordonne des trajectoires.</p>
          </div>
        </CardContent>
      </Card>

      {partners.length === 0 ? (
        <Card className="border-dashed border-2"><CardContent className="py-16 text-center">
          <Handshake className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-500">Aucun partenaire ajoute</p>
        </CardContent></Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" data-testid="partners-list">
          {partners.map(p => {
            const info = TYPE_INFO[p.type] || TYPE_INFO.organisme;
            const Icon = info.icon;
            return (
              <Card key={p.id} className="border border-slate-100 hover:border-emerald-200 transition-all" data-testid={`partner-${p.id}`}>
                <CardContent className="p-4">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-lg ${info.color} flex items-center justify-center`}><Icon className="w-5 h-5" /></div>
                      <div><h3 className="font-semibold text-slate-900 text-sm">{p.name}</h3><Badge className={`${info.color} text-[10px]`}>{info.label}</Badge></div>
                    </div>
                    <Button variant="ghost" size="icon" className="text-red-400 hover:text-red-600 h-8 w-8" onClick={() => handleDelete(p.id)}><Trash2 className="w-4 h-4" /></Button>
                  </div>
                  {p.contact && <p className="text-xs text-slate-500 mt-2">{p.contact}</p>}
                  {p.notes && <p className="text-xs text-slate-400 mt-1">{p.notes}</p>}
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      <CreatePartnerDialog open={createOpen} onOpenChange={setCreateOpen} token={token} onCreated={load} />
    </div>
  );
};

const CreatePartnerDialog = ({ open, onOpenChange, token, onCreated }) => {
  const [name, setName] = useState(""); const [type, setType] = useState("organisme"); const [contact, setContact] = useState(""); const [notes, setNotes] = useState("");
  const [creating, setCreating] = useState(false);
  const handle = async () => {
    if (!name.trim()) { toast.error("Nom obligatoire"); return; }
    setCreating(true);
    try {
      await axios.post(`${API}/entreprise/partenaires?token=${token}`, { name: name.trim(), type, contact: contact.trim(), notes: notes.trim() });
      toast.success("Partenaire ajoute"); setName(""); setContact(""); setNotes(""); onOpenChange(false); onCreated();
    } catch (err) { toast.error(err.response?.data?.detail || "Erreur"); }
    setCreating(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]" data-testid="create-partner-dialog">
        <DialogHeader><DialogTitle>Ajouter un partenaire</DialogTitle></DialogHeader>
        <div className="space-y-3 mt-2">
          <div><label className="text-sm font-medium">Nom *</label><Input placeholder="Nom de l'organisme" value={name} onChange={e => setName(e.target.value)} data-testid="partner-name" /></div>
          <div><label className="text-sm font-medium">Type</label>
            <Select value={type} onValueChange={setType}><SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>{Object.entries(TYPE_INFO).map(([k, v]) => <SelectItem key={k} value={k}>{v.label}</SelectItem>)}</SelectContent></Select></div>
          <div><label className="text-sm font-medium">Contact</label><Input placeholder="Email ou telephone" value={contact} onChange={e => setContact(e.target.value)} /></div>
          <div><label className="text-sm font-medium">Notes</label><Input placeholder="Notes..." value={notes} onChange={e => setNotes(e.target.value)} /></div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>Annuler</Button>
          <Button onClick={handle} disabled={creating} className="bg-emerald-600 hover:bg-emerald-700" data-testid="submit-partner">
            {creating ? <Loader2 className="w-4 h-4 mr-1 animate-spin" /> : <Plus className="w-4 h-4 mr-1" />}Ajouter
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default PartenairesRH;
