import React, { useState, useEffect, useRef, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, MessageSquare, ArrowLeft, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";
import { u2, timeAgo } from "../api";

export default function MessagesU({ onRead }) {
  const [convs, setConvs] = useState([]);
  const [active, setActive] = useState(null);
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(true);
  const bottomRef = useRef(null);
  const pollRef = useRef(null);
  const navigate = useNavigate();

  const loadConvs = useCallback(async () => {
    try {
      const res = await u2.get("/conversations");
      setConvs(res.data);
    } catch { /* silent */ }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { loadConvs(); }, [loadConvs]);

  const openConv = useCallback(async (conv) => {
    setActive(conv);
    try {
      const res = await u2.get(`/conversations/${conv.id}/messages`);
      setMessages(res.data);
      setConvs(prev => prev.map(c => c.id === conv.id ? { ...c, unread: 0 } : c));
      onRead?.();
    } catch { /* silent */ }
  }, [onRead]);

  useEffect(() => {
    clearInterval(pollRef.current);
    if (active) {
      pollRef.current = setInterval(async () => {
        try {
          const res = await u2.get(`/conversations/${active.id}/messages`);
          setMessages(res.data);
        } catch { /* silent */ }
      }, 5000);
    }
    return () => clearInterval(pollRef.current);
  }, [active]);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  const send = async () => {
    const t = text.trim();
    if (!t || !active) return;
    try {
      const res = await u2.post(`/conversations/${active.id}/messages`, { text: t });
      setMessages(prev => [...prev, res.data]);
      setText("");
      loadConvs();
    } catch (e) { toast.error(e.response?.data?.detail || "Erreur d'envoi"); }
  };

  const myId = convs.length && active ? null : null;

  if (loading) return <div className="flex justify-center py-16"><Loader2 className="w-8 h-8 animate-spin text-[#C85A32]" /></div>;

  // Vue chat (mobile : plein écran ; desktop : 2 colonnes)
  return (
    <div className="space-y-4" data-testid="ubuntoo-messages">
      {!active && (
        <div>
          <h1 className="text-2xl font-extrabold u2-heading tracking-tight">Messages</h1>
          <p className="text-sm text-stone-500 mt-1">Messagerie professionnelle, réservée à vos contacts acceptés.</p>
        </div>
      )}

      {!active ? (
        <div className="space-y-2">
          {convs.length === 0 && (
            <div className="text-center py-10">
              <MessageSquare className="w-9 h-9 text-stone-200 mx-auto mb-2" />
              <p className="text-sm text-stone-400 mb-3">Aucune conversation. Acceptez une mise en relation puis écrivez à vos contacts.</p>
              <Button size="sm" className="rounded-xl u2-btn-primary" onClick={() => navigate("/ubuntoo/reseau")} data-testid="go-reseau-btn">Voir mon réseau</Button>
            </div>
          )}
          {convs.map(c => (
            <button key={c.id} onClick={() => openConv(c)} data-testid={`conversation-${c.id}`}
              className="w-full flex items-center gap-3 rounded-2xl border border-[#E2DFD8] bg-white px-4 py-3.5 text-left hover:border-orange-300 transition-colors">
              <div className="h-10 w-10 rounded-full bg-[#E09F3E]/20 text-[#A84624] flex items-center justify-center text-sm font-bold shrink-0">{(c.other?.display_name || "?")[0].toUpperCase()}</div>
              <div className="min-w-0 flex-1">
                <div className="text-sm font-semibold">{c.other?.display_name}</div>
                <div className="text-xs text-stone-400 truncate">{c.last_message_text || "Conversation ouverte"}</div>
              </div>
              <div className="flex flex-col items-end gap-1 shrink-0">
                <span className="text-[11px] text-stone-400">{timeAgo(c.last_message_at)}</span>
                {c.unread > 0 && <span className="h-4.5 min-w-[18px] h-[18px] px-1 rounded-full bg-[#C85A32] text-white text-[10px] font-bold flex items-center justify-center">{c.unread}</span>}
              </div>
            </button>
          ))}
        </div>
      ) : (
        <div className="rounded-2xl border border-[#E2DFD8] bg-white overflow-hidden flex flex-col" style={{ height: "calc(100vh - 220px)", minHeight: 420 }} data-testid="chat-window">
          <div className="flex items-center gap-3 px-4 py-3 border-b border-stone-100 bg-white">
            <Button variant="ghost" size="icon" className="h-8 w-8 rounded-full" onClick={() => { setActive(null); loadConvs(); }} data-testid="back-to-conversations-btn">
              <ArrowLeft className="w-4 h-4" />
            </Button>
            <div className="h-8 w-8 rounded-full bg-[#E09F3E]/20 text-[#A84624] flex items-center justify-center text-xs font-bold">{(active.other?.display_name || "?")[0].toUpperCase()}</div>
            <span className="text-sm font-semibold">{active.other?.display_name}</span>
          </div>
          <div className="flex-1 overflow-y-auto px-4 py-3 space-y-2 bg-[#FAF8F5]">
            {messages.map(m => {
              const mine = m.sender_id !== active.other?.token_id;
              return (
                <div key={m.id} className={`flex ${mine ? "justify-end" : "justify-start"}`}>
                  <div className={`max-w-[75%] rounded-2xl px-3.5 py-2 text-sm leading-relaxed ${mine ? "bg-[#C85A32] text-white rounded-br-md" : "bg-white border border-[#E2DFD8] text-stone-800 rounded-bl-md"}`}>
                    <p className="whitespace-pre-wrap">{m.text}</p>
                    <p className={`text-[10px] mt-0.5 ${mine ? "text-white/60" : "text-stone-400"}`}>{timeAgo(m.created_at)}</p>
                  </div>
                </div>
              );
            })}
            {messages.length === 0 && <p className="text-xs text-stone-400 text-center py-6">Démarrez la conversation — restez professionnel et bienveillant.</p>}
            <div ref={bottomRef} />
          </div>
          <div className="flex gap-2 px-3 py-3 border-t border-stone-100 bg-white">
            <Input value={text} onChange={e => setText(e.target.value)} onKeyDown={e => e.key === "Enter" && send()}
              placeholder="Votre message…" className="rounded-xl" data-testid="message-input" />
            <Button size="icon" className="rounded-xl u2-btn-primary shrink-0" onClick={send} data-testid="send-message-btn"><Send className="w-4 h-4" /></Button>
          </div>
        </div>
      )}
    </div>
  );
}
