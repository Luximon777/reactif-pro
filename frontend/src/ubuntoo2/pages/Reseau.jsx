import React, { useState, useEffect, useCallback } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Search, UserPlus, Check, X, Eye, Loader2, Users, MessageSquare, HandHeart } from "lucide-react";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";
import { u2, timeAgo, RECOGNITION_TYPES } from "../api";
import MentoratTab from "./MentoratTab";
import { BadgeChip } from "./BadgesSection";

const Avatar = ({ name }) => (
  <div className="h-10 w-10 rounded-full bg-[#E09F3E]/20 text-[#A84624] flex items-center justify-center text-sm font-bold shrink-0">
    {(name || "?")[0].toUpperCase()}
  </div>
);

const MemberProfileDialog = ({ member, open, onOpenChange }) => {
  const [full, setFull] = useState(null);
  useEffect(() => {
    if (open && member) u2.get(`/members/${member.token_id}`).then(r => setFull(r.data)).catch(() => setFull(member));
  }, [open, member]);
  const m = full || member;
  if (!m) return null;
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md rounded-2xl" data-testid="member-profile-dialog">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-3 u2-heading"><Avatar name={m.display_name} />{m.display_name}</DialogTitle>
          {m.headline && <DialogDescription>{m.headline}</DialogDescription>}
        </DialogHeader>
        <div className="space-y-3 text-sm">
          {(m.badges?.length > 0 || m.mentoring_role === "mentor" || m.mentoring_role === "both") && (
            <div className="flex flex-wrap gap-1.5">
              {(m.badges || []).map(b => <BadgeChip key={b} badgeId={b} small />)}
            </div>
          )}
          {m.projet && <div><div className="text-xs font-semibold text-stone-400 uppercase tracking-wide mb-1">Projet professionnel</div><p className="text-stone-700">{m.projet}</p></div>}
          {m.experiences?.length > 0 && <div><div className="text-xs font-semibold text-stone-400 uppercase tracking-wide mb-1">Expériences</div>{m.experiences.map((e, i) => <p key={i} className="text-stone-700">{e.title}{e.organization ? ` — ${e.organization}` : ""}</p>)}</div>}
          {m.competences?.length > 0 && <div><div className="text-xs font-semibold text-stone-400 uppercase tracking-wide mb-1.5">Compétences</div><div className="flex flex-wrap gap-1.5">{m.competences.map((c, i) => <Badge key={i} variant="outline" className="rounded-full text-xs border-[#E2DFD8]">{c}</Badge>)}</div></div>}
          {m.soft_skills?.length > 0 && <div><div className="text-xs font-semibold text-stone-400 uppercase tracking-wide mb-1.5">Soft skills</div><div className="flex flex-wrap gap-1.5">{m.soft_skills.map((c, i) => <Badge key={i} variant="outline" className="rounded-full text-xs border-emerald-200 text-emerald-700">{c}</Badge>)}</div></div>}
          {m.help_offers?.length > 0 && <div><div className="text-xs font-semibold text-stone-400 uppercase tracking-wide mb-1.5 flex items-center gap-1"><HandHeart className="w-3.5 h-3.5" />Disponible pour aider</div><div className="flex flex-wrap gap-1.5">{m.help_offers.map((c, i) => <Badge key={i} className="rounded-full text-xs bg-orange-100 text-orange-800 border border-orange-300 hover:bg-orange-100">{c}</Badge>)}</div></div>}
          {!m.projet && !m.competences?.length && <p className="text-stone-400 text-sm">Ce membre limite la visibilité de son profil. Les informations « Réseau UBUNTOO » seront visibles après mise en relation acceptée.</p>}
          {m.is_contact && (
            <div className="rounded-xl border border-orange-100 bg-orange-50/50 p-3" data-testid="recognition-box">
              <div className="text-xs font-semibold text-stone-700 mb-0.5">Cette personne vous a-t-elle été utile ?</div>
              <p className="text-[11px] text-stone-500 mb-2">Reconnaissez sa contribution — ce n'est pas une note, c'est un merci qui compte pour ses badges.</p>
              <div className="flex flex-wrap gap-1.5">
                {Object.entries(RECOGNITION_TYPES).map(([k, label]) => (
                  <button key={k} data-testid={`recognize-${k}`}
                    onClick={async () => {
                      try {
                        const res = await u2.post("/recognitions", { to_id: m.token_id, type: k });
                        toast.success(res.data.message);
                      } catch (e) { toast.error(e.response?.data?.detail || "Erreur"); }
                    }}
                    className="rounded-full border border-orange-200 bg-white px-2.5 py-1 text-[11px] text-stone-700 hover:bg-orange-100 transition-colors">
                    {label}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};

const ConnectDialog = ({ member, open, onOpenChange, onSent }) => {
  const [message, setMessage] = useState("");
  const [sending, setSending] = useState(false);
  const send = async () => {
    setSending(true);
    try {
      await u2.post("/connections", { to_id: member.token_id, message });
      toast.success(`Demande envoyée à ${member.display_name}`);
      onSent?.();
      onOpenChange(false);
      setMessage("");
    } catch (e) {
      toast.error(e.response?.data?.detail || "Erreur");
    } finally { setSending(false); }
  };
  if (!member) return null;
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md rounded-2xl" data-testid="connect-dialog">
        <DialogHeader>
          <DialogTitle className="u2-heading">Demander une mise en relation</DialogTitle>
          <DialogDescription>Toute mise en relation repose sur l'accord mutuel des deux membres. {member.display_name} pourra accepter, refuser ou consulter votre profil.</DialogDescription>
        </DialogHeader>
        <Textarea value={message} onChange={e => setMessage(e.target.value)} rows={3} maxLength={300}
          placeholder={`Ex : Bonjour, je souhaite échanger avec vous au sujet de votre métier…`}
          className="rounded-xl" data-testid="connect-message-input" />
        <div className="flex justify-end gap-2">
          <Button variant="outline" className="rounded-xl" onClick={() => onOpenChange(false)}>Annuler</Button>
          <Button className="rounded-xl u2-btn-primary" onClick={send} disabled={sending} data-testid="send-connection-btn">
            {sending ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <UserPlus className="w-4 h-4 mr-2" />}Envoyer la demande
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default function Reseau() {
  const [tab, setTab] = useState(() => new URLSearchParams(window.location.search).get("tab") || "contacts");
  const [contacts, setContacts] = useState([]);
  const [received, setReceived] = useState([]);
  const [sent, setSent] = useState([]);
  const [members, setMembers] = useState([]);
  const [q, setQ] = useState("");
  const [searching, setSearching] = useState(false);
  const [viewMember, setViewMember] = useState(null);
  const [connectMember, setConnectMember] = useState(null);
  const navigate = useNavigate();

  const loadAll = useCallback(async () => {
    try {
      const [c, r, s] = await Promise.all([u2.get("/contacts"), u2.get("/connections", { box: "received" }), u2.get("/connections", { box: "sent" })]);
      setContacts(c.data); setReceived(r.data); setSent(s.data);
    } catch { /* silent */ }
  }, []);

  useEffect(() => { loadAll(); }, [loadAll]);

  const search = async () => {
    setSearching(true);
    try {
      const res = await u2.get("/members", { q });
      setMembers(res.data);
    } catch { toast.error("Erreur de recherche"); }
    finally { setSearching(false); }
  };

  useEffect(() => { if (tab === "recherche" && members.length === 0) search(); }, [tab]); // eslint-disable-line

  const respond = async (connId, action) => {
    try {
      await u2.post(`/connections/${connId}/respond`, { action });
      toast.success(action === "accept" ? "Mise en relation acceptée" : "Demande refusée");
      loadAll();
    } catch { toast.error("Erreur"); }
  };

  const openChat = async (contact) => {
    try {
      await u2.post("/conversations", { contact_id: contact.token_id });
      navigate("/ubuntoo/messages");
    } catch (e) { toast.error(e.response?.data?.detail || "Erreur"); }
  };

  return (
    <div className="space-y-4" data-testid="ubuntoo-reseau">
      <div>
        <h1 className="text-2xl font-extrabold u2-heading tracking-tight">Mon réseau</h1>
        <p className="text-sm text-stone-500 mt-1">Toute mise en relation repose sur l'accord mutuel des deux membres.</p>
      </div>

      <Tabs value={tab} onValueChange={setTab}>
        <TabsList className="rounded-xl bg-stone-100 w-full grid grid-cols-4">
          <TabsTrigger value="contacts" className="rounded-lg text-xs sm:text-sm" data-testid="tab-contacts">Contacts ({contacts.length})</TabsTrigger>
          <TabsTrigger value="demandes" className="rounded-lg text-xs sm:text-sm" data-testid="tab-demandes">
            Demandes {received.length > 0 && <span className="ml-1 h-4 min-w-4 px-1 rounded-full bg-[#C85A32] text-white text-[10px] font-bold inline-flex items-center justify-center">{received.length}</span>}
          </TabsTrigger>
          <TabsTrigger value="recherche" className="rounded-lg text-xs sm:text-sm" data-testid="tab-recherche">Rechercher</TabsTrigger>
          <TabsTrigger value="mentorat" className="rounded-lg text-xs sm:text-sm" data-testid="tab-mentorat">Mentorat</TabsTrigger>
        </TabsList>

        <TabsContent value="contacts" className="space-y-2 mt-4">
          {contacts.length === 0 && <p className="text-sm text-stone-400 text-center py-8">Aucun contact pour le moment. Recherchez des membres et envoyez une demande de mise en relation.</p>}
          {contacts.map(c => (
            <Card key={c.token_id} className="rounded-2xl border border-[#E2DFD8] shadow-none bg-white" data-testid={`contact-card-${c.token_id}`}>
              <CardContent className="p-4 flex items-center gap-3">
                <Avatar name={c.display_name} />
                <div className="min-w-0 flex-1">
                  <div className="text-sm font-semibold">{c.display_name}</div>
                  {c.headline && <div className="text-xs text-stone-400 truncate">{c.headline}</div>}
                </div>
                <Button variant="outline" size="sm" className="rounded-xl" onClick={() => setViewMember(c)} data-testid={`view-contact-${c.token_id}`}><Eye className="w-3.5 h-3.5" /></Button>
                <Button size="sm" className="rounded-xl u2-btn-primary" onClick={() => openChat(c)} data-testid={`chat-contact-${c.token_id}`}><MessageSquare className="w-3.5 h-3.5 mr-1.5" />Écrire</Button>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="demandes" className="space-y-4 mt-4">
          <div>
            <h3 className="text-sm font-semibold u2-heading mb-2">Demandes reçues</h3>
            {received.length === 0 && <p className="text-sm text-stone-400">Aucune demande en attente.</p>}
            {received.map(r => (
              <Card key={r.id} className="rounded-2xl border border-amber-200 shadow-none bg-white mb-2" data-testid={`request-card-${r.id}`}>
                <CardContent className="p-4 space-y-3">
                  <div className="flex items-center gap-3">
                    <Avatar name={r.member?.display_name} />
                    <div className="min-w-0 flex-1">
                      <p className="text-sm"><span className="font-semibold">{r.member?.display_name}</span> souhaite entrer en contact avec vous{r.message ? "" : "."}</p>
                      {r.message && <p className="text-sm text-stone-600 italic mt-0.5">« {r.message} »</p>}
                      <p className="text-[11px] text-stone-400 mt-0.5">{timeAgo(r.created_at)}</p>
                    </div>
                  </div>
                  <div className="flex gap-2 flex-wrap">
                    <Button size="sm" className="rounded-xl bg-[#2E7D5B] hover:bg-[#246349] text-white" onClick={() => respond(r.id, "accept")} data-testid={`accept-request-${r.id}`}><Check className="w-3.5 h-3.5 mr-1.5" />Accepter</Button>
                    <Button size="sm" variant="outline" className="rounded-xl text-rose-700 border-rose-200 hover:bg-rose-50" onClick={() => respond(r.id, "decline")} data-testid={`decline-request-${r.id}`}><X className="w-3.5 h-3.5 mr-1.5" />Refuser</Button>
                    <Button size="sm" variant="ghost" className="rounded-xl" onClick={() => setViewMember(r.member)} data-testid={`view-requester-${r.id}`}><Eye className="w-3.5 h-3.5 mr-1.5" />Voir le profil</Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
          {sent.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold u2-heading mb-2">Demandes envoyées</h3>
              {sent.map(s => (
                <div key={s.id} className="flex items-center gap-3 rounded-xl border border-[#E2DFD8] bg-white px-4 py-3 mb-2 text-sm">
                  <Avatar name={s.member?.display_name} />
                  <span className="flex-1">{s.member?.display_name}</span>
                  <Badge variant="outline" className="rounded-full text-xs text-stone-500">En attente</Badge>
                </div>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="recherche" className="space-y-3 mt-4">
          <div className="flex gap-2">
            <Input value={q} onChange={e => setQ(e.target.value)} onKeyDown={e => e.key === "Enter" && search()}
              placeholder="Nom, métier, compétence…" className="rounded-xl bg-white" data-testid="member-search-input" />
            <Button className="rounded-xl u2-btn-primary shrink-0" onClick={search} disabled={searching} data-testid="member-search-btn">
              {searching ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
            </Button>
          </div>
          {members.map(m => (
            <Card key={m.token_id} className="rounded-2xl border border-[#E2DFD8] shadow-none bg-white" data-testid={`member-card-${m.token_id}`}>
              <CardContent className="p-4 flex items-center gap-3">
                <Avatar name={m.display_name} />
                <div className="min-w-0 flex-1">
                  <div className="text-sm font-semibold">{m.display_name}</div>
                  {m.headline && <div className="text-xs text-stone-400 truncate">{m.headline}</div>}
                </div>
                <Button variant="ghost" size="sm" className="rounded-xl shrink-0" onClick={() => setViewMember(m)} data-testid={`view-member-${m.token_id}`}><Eye className="w-3.5 h-3.5" /></Button>
                {m.connection_status === "none" && (
                  <Button size="sm" className="rounded-xl u2-btn-primary shrink-0" onClick={() => setConnectMember(m)} data-testid={`connect-member-${m.token_id}`}>
                    <UserPlus className="w-3.5 h-3.5 sm:mr-1.5" /><span className="hidden sm:inline">Mise en relation</span>
                  </Button>
                )}
                {m.connection_status === "pending_sent" && <Badge variant="outline" className="rounded-full text-xs text-stone-500 shrink-0">Demande envoyée</Badge>}
                {m.connection_status === "pending_received" && <Badge className="rounded-full text-xs bg-amber-100 text-amber-800 border border-amber-300 hover:bg-amber-100 shrink-0">Vous a sollicité</Badge>}
                {m.connection_status === "contact" && <Badge className="rounded-full text-xs bg-emerald-50 text-emerald-700 border border-emerald-200 hover:bg-emerald-50 shrink-0"><Users className="w-3 h-3 mr-1" />Contact</Badge>}
              </CardContent>
            </Card>
          ))}
          {!searching && members.length === 0 && <p className="text-sm text-stone-400 text-center py-6">Aucun membre trouvé.</p>}
        </TabsContent>

        <TabsContent value="mentorat">
          <MentoratTab />
        </TabsContent>
      </Tabs>

      <MemberProfileDialog member={viewMember} open={!!viewMember} onOpenChange={v => !v && setViewMember(null)} />
      <ConnectDialog member={connectMember} open={!!connectMember} onOpenChange={v => !v && setConnectMember(null)} onSent={() => { loadAll(); search(); }} />
    </div>
  );
}
