import React, { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { LoadFail } from "../LoadFail";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ArrowLeft, Users, Send, Flag, MessageCircle, HandHeart, Loader2, Check } from "lucide-react";
import { toast } from "sonner";
import { u2, POST_TYPES, REPORT_REASONS, CATEGORIES, timeAgo } from "../api";

const ReportDialog = ({ target, open, onOpenChange }) => {
  const [reason, setReason] = useState("");
  const [sending, setSending] = useState(false);
  const send = async () => {
    if (!reason) { toast.error("Choisissez un motif"); return; }
    setSending(true);
    try {
      const res = await u2.post("/reports", { target_type: target.type, target_id: target.id, reason });
      toast.success(res.data.message);
      onOpenChange(false);
      setReason("");
    } catch { toast.error("Erreur"); }
    finally { setSending(false); }
  };
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md rounded-2xl" data-testid="report-dialog">
        <DialogHeader>
          <DialogTitle className="u2-heading flex items-center gap-2"><Flag className="w-4 h-4 text-rose-600" />Signaler ce contenu</DialogTitle>
          <DialogDescription>Votre signalement sera traité par la modération.</DialogDescription>
        </DialogHeader>
        <Select value={reason} onValueChange={setReason}>
          <SelectTrigger className="rounded-xl" data-testid="report-reason-select"><SelectValue placeholder="Motif du signalement" /></SelectTrigger>
          <SelectContent>{REPORT_REASONS.map(r => <SelectItem key={r} value={r}>{r}</SelectItem>)}</SelectContent>
        </Select>
        <div className="flex justify-end gap-2">
          <Button variant="outline" className="rounded-xl" onClick={() => onOpenChange(false)}>Annuler</Button>
          <Button className="rounded-xl bg-rose-600 hover:bg-rose-700 text-white" onClick={send} disabled={sending} data-testid="submit-report-btn">Signaler</Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

const PostCard = ({ post, onReport }) => {
  const [showReplies, setShowReplies] = useState(false);
  const [replies, setReplies] = useState([]);
  const [replyText, setReplyText] = useState("");
  const [utile, setUtile] = useState(post.utile_by_me);
  const [utileCount, setUtileCount] = useState(post.utile_count);
  const [repliesCount, setRepliesCount] = useState(post.replies_count || 0);
  const typeCfg = POST_TYPES[post.type] || POST_TYPES.information;

  const loadReplies = async () => {
    if (!showReplies) {
      try { const res = await u2.get(`/posts/${post.id}/replies`); setReplies(res.data); } catch { /* silent */ }
    }
    setShowReplies(!showReplies);
  };

  const toggleUtile = async () => {
    try {
      const res = await u2.post(`/posts/${post.id}/utile`);
      setUtile(res.data.utile); setUtileCount(res.data.utile_count);
    } catch { /* silent */ }
  };

  const reply = async () => {
    const t = replyText.trim();
    if (t.length < 2) return;
    try {
      const res = await u2.post(`/posts/${post.id}/replies`, { content: t });
      setReplies(prev => [...prev, res.data]);
      setRepliesCount(c => c + 1);
      setReplyText("");
    } catch (e) { toast.error(e.response?.data?.detail || "Erreur"); }
  };

  return (
    <Card className="rounded-2xl border border-[#E2DFD8] shadow-none bg-white" data-testid={`post-card-${post.id}`}>
      <CardContent className="p-4 space-y-3">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="h-9 w-9 rounded-full bg-[#E09F3E]/20 text-[#A84624] flex items-center justify-center text-sm font-bold shrink-0">{(post.author_name || "?")[0].toUpperCase()}</div>
            <div className="min-w-0">
              <div className="text-sm font-semibold truncate">{post.author_name}</div>
              <div className="text-[11px] text-stone-400">{timeAgo(post.created_at)}</div>
            </div>
          </div>
          <div className="flex items-center gap-1.5 shrink-0">
            <Badge className={`rounded-full border text-[10px] uppercase tracking-wide hover:bg-inherit ${typeCfg.cls}`}>{typeCfg.label}</Badge>
            <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => onReport({ type: "post", id: post.id })} data-testid={`report-post-${post.id}`}>
              <Flag className="w-3.5 h-3.5 text-stone-300" />
            </Button>
          </div>
        </div>
        {post.title && <h4 className="text-sm font-semibold u2-heading">{post.title}</h4>}
        <p className="text-sm text-stone-700 leading-relaxed whitespace-pre-wrap">{post.content}</p>
        <div className="flex items-center gap-2">
          <button onClick={toggleUtile} data-testid={`useful-button-${post.id}`}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${utile ? "bg-orange-100 text-orange-800 border-orange-300 font-semibold" : "border-stone-200 text-stone-600 hover:bg-orange-50 hover:border-orange-300"}`}>
            <HandHeart className="w-3.5 h-3.5" />Utile{utileCount > 0 ? ` · ${utileCount}` : ""}
          </button>
          <button onClick={loadReplies} data-testid={`toggle-replies-${post.id}`}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border border-stone-200 text-stone-600 hover:bg-stone-50 transition-colors">
            <MessageCircle className="w-3.5 h-3.5" />{repliesCount} réponse{repliesCount > 1 ? "s" : ""}
          </button>
        </div>
        {showReplies && (
          <div className="space-y-2.5 pt-1 border-t border-stone-100">
            {replies.map(r => (
              <div key={r.id} className="flex gap-2.5 pt-2">
                <div className="h-7 w-7 rounded-full bg-stone-100 text-stone-500 flex items-center justify-center text-xs font-bold shrink-0">{(r.author_name || "?")[0].toUpperCase()}</div>
                <div className="min-w-0 flex-1 bg-[#FAF8F5] rounded-xl px-3 py-2">
                  <div className="flex items-center gap-2"><span className="text-xs font-semibold">{r.author_name}</span><span className="text-[10px] text-stone-400">{timeAgo(r.created_at)}</span></div>
                  <p className="text-sm text-stone-700 mt-0.5">{r.content}</p>
                </div>
              </div>
            ))}
            <div className="flex gap-2 pt-1">
              <Input value={replyText} onChange={e => setReplyText(e.target.value)} onKeyDown={e => e.key === "Enter" && reply()}
                placeholder="Apporter une réponse utile…" className="rounded-xl text-sm" data-testid={`reply-input-${post.id}`} />
              <Button size="icon" className="rounded-xl u2-btn-primary shrink-0" onClick={reply} data-testid={`send-reply-${post.id}`}><Send className="w-4 h-4" /></Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default function CommunauteDetail() {
  const { commId } = useParams();
  const navigate = useNavigate();
  const [comm, setComm] = useState(null);
  const [posts, setPosts] = useState([]);
  const [filter, setFilter] = useState("");
  const [publishOpen, setPublishOpen] = useState(false);
  const [form, setForm] = useState({ type: "question", title: "", content: "" });
  const [publishing, setPublishing] = useState(false);
  const [reportTarget, setReportTarget] = useState(null);

  const load = useCallback(async () => {
    try {
      const [c, p] = await Promise.all([
        u2.get(`/communities/${commId}`),
        u2.get(`/communities/${commId}/posts`, filter ? { post_type: filter } : {}),
      ]);
      setComm(c.data); setPosts(p.data);
    } catch { setComm(prev => prev || "error"); }
  }, [commId, filter]);

  useEffect(() => { load(); }, [load]);

  const toggleJoin = async () => {
    try {
      await u2.post(`/communities/${commId}/${comm.joined ? "leave" : "join"}`);
      setComm(p => ({ ...p, joined: !p.joined, members_count: p.members_count + (p.joined ? -1 : 1) }));
    } catch { toast.error("Erreur"); }
  };

  const publish = async () => {
    setPublishing(true);
    try {
      await u2.post(`/communities/${commId}/posts`, form);
      toast.success("Publication partagée avec la communauté");
      setPublishOpen(false);
      setForm({ type: "question", title: "", content: "" });
      load();
    } catch (e) { toast.error(e.response?.data?.detail || "Erreur"); }
    finally { setPublishing(false); }
  };

  if (comm === "error") return <LoadFail onRetry={load} />;
  if (!comm) return <div className="flex justify-center py-16"><Loader2 className="w-8 h-8 animate-spin text-[#C85A32]" /></div>;

  return (
    <div className="space-y-4" data-testid="ubuntoo-communaute-detail">
      <button onClick={() => navigate("/ubuntoo/communautes")} className="inline-flex items-center gap-1.5 text-sm text-stone-500 hover:text-stone-700" data-testid="back-to-communities-btn">
        <ArrowLeft className="w-4 h-4" />Communautés
      </button>

      <Card className="rounded-2xl border border-[#E2DFD8] shadow-none bg-white">
        <CardContent className="p-5">
          <div className="flex items-start justify-between gap-3 flex-wrap">
            <div>
              <Badge variant="outline" className="rounded-full text-[10px] uppercase tracking-wide border-[#E2DFD8] text-stone-500 mb-1.5">{CATEGORIES[comm.category]}</Badge>
              <h1 className="text-xl font-extrabold u2-heading tracking-tight">{comm.name}</h1>
              <p className="text-sm text-stone-500 mt-1">{comm.description}</p>
              <p className="text-xs text-stone-400 mt-2 flex items-center gap-1"><Users className="w-3.5 h-3.5" />{comm.members_count} membre{comm.members_count > 1 ? "s" : ""}</p>
            </div>
            <div className="flex gap-2">
              <Button size="sm" variant={comm.joined ? "outline" : "default"} className={`rounded-xl ${comm.joined ? "text-stone-500" : "u2-btn-primary"}`} onClick={toggleJoin} data-testid="toggle-join-btn">
                {comm.joined ? "Quitter" : <><Check className="w-3.5 h-3.5 mr-1.5" />Rejoindre</>}
              </Button>
              {comm.joined && <Button size="sm" className="rounded-xl u2-btn-primary" onClick={() => setPublishOpen(true)} data-testid="open-publish-btn"><Send className="w-3.5 h-3.5 mr-1.5" />Publier</Button>}
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="flex gap-2 overflow-x-auto pb-1 -mx-1 px-1">
        <button onClick={() => setFilter("")} className={`rounded-full px-3 py-1.5 text-xs font-medium whitespace-nowrap border transition-colors ${!filter ? "bg-stone-800 text-white border-transparent" : "bg-white text-stone-600 border-[#E2DFD8]"}`} data-testid="filter-type-all">Tout</button>
        {Object.entries(POST_TYPES).map(([k, cfg]) => (
          <button key={k} onClick={() => setFilter(filter === k ? "" : k)} data-testid={`filter-type-${k}`}
            className={`rounded-full px-3 py-1.5 text-xs font-medium whitespace-nowrap border transition-colors ${filter === k ? cfg.cls + " font-semibold" : "bg-white text-stone-600 border-[#E2DFD8]"}`}>
            {cfg.label}
          </button>
        ))}
      </div>

      <div className="space-y-3">
        {posts.map(p => <PostCard key={p.id} post={p} onReport={setReportTarget} />)}
        {posts.length === 0 && (
          <div className="text-center py-10">
            <MessageCircle className="w-9 h-9 text-stone-200 mx-auto mb-2" />
            <p className="text-sm text-stone-400">Aucune publication pour le moment.{comm.joined ? " Lancez la première discussion !" : " Rejoignez la communauté pour publier."}</p>
          </div>
        )}
      </div>

      <Dialog open={publishOpen} onOpenChange={setPublishOpen}>
        <DialogContent className="max-w-lg rounded-2xl" data-testid="publish-dialog">
          <DialogHeader>
            <DialogTitle className="u2-heading">Publier dans {comm.name}</DialogTitle>
            <DialogDescription>Privilégiez les contributions utiles : question, expérience, information, ressource, opportunité ou demande d'aide.</DialogDescription>
          </DialogHeader>
          <div className="space-y-3">
            <div className="flex flex-wrap gap-1.5">
              {Object.entries(POST_TYPES).map(([k, cfg]) => (
                <button key={k} onClick={() => setForm(p => ({ ...p, type: k }))} data-testid={`post-type-${k}`}
                  className={`rounded-full px-3 py-1.5 text-xs font-medium border transition-colors ${form.type === k ? cfg.cls + " font-semibold" : "bg-white text-stone-500 border-[#E2DFD8]"}`}>
                  {cfg.label}
                </button>
              ))}
            </div>
            <Input value={form.title} onChange={e => setForm(p => ({ ...p, title: e.target.value }))} maxLength={150} placeholder="Titre (facultatif)" className="rounded-xl" data-testid="post-title-input" />
            <Textarea value={form.content} onChange={e => setForm(p => ({ ...p, content: e.target.value }))} rows={4} maxLength={4000} placeholder="Votre message…" className="rounded-xl" data-testid="post-content-input" />
            <div className="flex justify-end gap-2">
              <Button variant="outline" className="rounded-xl" onClick={() => setPublishOpen(false)}>Annuler</Button>
              <Button className="rounded-xl u2-btn-primary" onClick={publish} disabled={publishing} data-testid="submit-post-btn">
                {publishing ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Send className="w-4 h-4 mr-2" />}Publier
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <ReportDialog target={reportTarget || {}} open={!!reportTarget} onOpenChange={v => !v && setReportTarget(null)} />
    </div>
  );
}
