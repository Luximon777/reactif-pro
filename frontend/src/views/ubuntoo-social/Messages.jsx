import { useState, useEffect, useRef, useCallback } from 'react';
import { useAuth } from './UbuntooSocialContext';
import { messagesApi, usersApi } from './api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { ScrollArea } from '@/components/ui/scroll-area';
import { toast } from 'sonner';
import { Send, Search, MessageSquare, Loader2, UserPlus, ArrowLeft, Check, CheckCheck } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { fr } from 'date-fns/locale';

export default function Messages() {
  const { user, token } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [showUserList, setShowUserList] = useState(false);
  const [online, setOnline] = useState(new Set());
  const [peerTyping, setPeerTyping] = useState(false);

  const messagesEndRef = useRef(null);
  const wsRef = useRef(null);
  const selectedUserRef = useRef(null);
  const typingTimeoutRef = useRef(null);
  const peerTypingTimeoutRef = useRef(null);
  const typingSentRef = useRef(false);

  const peerId = (u) => u?.user_id || u?.id;
  selectedUserRef.current = selectedUser;

  useEffect(() => {
    fetchConversations();
    fetchUsers();
  }, []);

  // WebSocket connection
  useEffect(() => {
    if (!token) return;
    const wsUrl = `${process.env.REACT_APP_BACKEND_URL.replace(/^http/, 'ws')}/api/social/ws?token=${token}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const sel = selectedUserRef.current;
      const selId = sel ? peerId(sel) : null;

      if (data.type === 'presence_snapshot') {
        setOnline(new Set(data.online));
      } else if (data.type === 'presence') {
        setOnline((prev) => {
          const next = new Set(prev);
          if (data.online) next.add(data.user_id);
          else next.delete(data.user_id);
          return next;
        });
      } else if (data.type === 'message') {
        const m = data.message;
        const involvesPeer = selId && (m.sender_id === selId || m.receiver_id === selId);
        if (involvesPeer) {
          setMessages((prev) => (prev.some((x) => x.id === m.id) ? prev : [...prev, m]));
          // If it's an incoming message in the open conversation, mark read
          if (m.sender_id === selId && wsRef.current?.readyState === 1) {
            wsRef.current.send(JSON.stringify({ type: 'read', sender_id: selId }));
          }
        }
        fetchConversations();
      } else if (data.type === 'typing') {
        if (selId && data.from === selId) {
          setPeerTyping(data.is_typing);
          clearTimeout(peerTypingTimeoutRef.current);
          if (data.is_typing) {
            peerTypingTimeoutRef.current = setTimeout(() => setPeerTyping(false), 4000);
          }
        }
      } else if (data.type === 'read') {
        if (selId && data.by === selId) {
          setMessages((prev) => prev.map((m) => (m.sender_id === user.id ? { ...m, status: 'read', read: true } : m)));
        }
      }
    };

    ws.onopen = () => { wsRef.current = ws; };
    ws.onclose = () => { if (wsRef.current === ws) wsRef.current = null; };

    return () => {
      ws.close();
    };
  }, [token, user?.id]);

  useEffect(() => {
    if (selectedUser) {
      setPeerTyping(false);
      fetchMessages(peerId(selectedUser));
    }
  }, [selectedUser]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, peerTyping]);

  const fetchConversations = async () => {
    try {
      const response = await messagesApi.getConversations();
      setConversations(response.data);
    } catch (error) {
      console.error('Failed to fetch conversations');
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await usersApi.getAll();
      setUsers(response.data.filter((u) => u.id !== user.id));
    } catch (error) {
      console.error('Failed to fetch users');
    }
  };

  const fetchMessages = async (userId) => {
    try {
      const response = await messagesApi.getMessages(userId);
      setMessages(response.data);
    } catch (error) {
      toast.error('Erreur lors du chargement des messages');
    }
  };

  const sendTyping = useCallback((isTyping) => {
    const sel = selectedUserRef.current;
    if (!sel || wsRef.current?.readyState !== 1) return;
    wsRef.current.send(JSON.stringify({ type: 'typing', receiver_id: peerId(sel), is_typing: isTyping }));
  }, []);

  const handleInputChange = (e) => {
    setNewMessage(e.target.value);
    if (!typingSentRef.current) {
      sendTyping(true);
      typingSentRef.current = true;
    }
    clearTimeout(typingTimeoutRef.current);
    typingTimeoutRef.current = setTimeout(() => {
      sendTyping(false);
      typingSentRef.current = false;
    }, 2000);
  };

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !selectedUser) return;
    const receiverId = peerId(selectedUser);
    const content = newMessage;
    setNewMessage('');
    clearTimeout(typingTimeoutRef.current);
    sendTyping(false);
    typingSentRef.current = false;

    if (wsRef.current?.readyState === 1) {
      wsRef.current.send(JSON.stringify({ type: 'message', receiver_id: receiverId, content }));
    } else {
      // Fallback REST
      messagesApi.send(receiverId, content).then(() => {
        fetchMessages(receiverId);
        fetchConversations();
      }).catch(() => toast.error("Erreur lors de l'envoi"));
    }
  };

  const startNewConversation = (targetUser) => {
    setSelectedUser({
      user_id: targetUser.id,
      user_name: targetUser.full_name,
      user_role: targetUser.role,
      user_avatar: targetUser.avatar_url,
    });
    setShowUserList(false);
    setMessages([]);
  };

  const filteredUsers = users.filter((u) => u.full_name.toLowerCase().includes(searchQuery.toLowerCase()));

  const statusIcon = (msg) => {
    if (msg.status === 'read') return <CheckCheck size={14} className="text-[#7ED0C4]" />;
    if (msg.status === 'delivered') return <CheckCheck size={14} className="text-white/60" />;
    return <Check size={14} className="text-white/60" />;
  };

  const isPeerOnline = selectedUser && online.has(peerId(selectedUser));

  return (
    <div className="min-h-screen bg-[#FDFBF7] pt-16">
      <div className="h-[calc(100vh-64px)] flex">
        {/* Sidebar */}
        <div className={`w-full md:w-80 lg:w-96 bg-white border-r border-[#E5E0D8] flex flex-col ${selectedUser ? 'hidden md:flex' : 'flex'}`}>
          <div className="p-4 border-b border-[#E5E0D8]">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-[#1A1A1A]" style={{ fontFamily: 'Manrope, sans-serif' }}>Messages</h2>
              <Button size="sm" variant="outline" onClick={() => setShowUserList(!showUserList)} className="border-[#0F4C5C] text-[#0F4C5C]" data-testid="new-conversation-button">
                <UserPlus size={18} />
              </Button>
            </div>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-[#5C5C5C] pointer-events-none" size={18} />
              <Input placeholder="Rechercher..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} className="pl-10 ubuntoo-input" data-testid="search-conversations" />
            </div>
          </div>

          <ScrollArea className="flex-1">
            {showUserList ? (
              <div className="p-2">
                <p className="px-3 py-2 text-sm text-[#5C5C5C] font-medium">Nouvelle conversation</p>
                {filteredUsers.map((targetUser) => (
                  <button key={targetUser.id} onClick={() => startNewConversation(targetUser)} className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-[#F5F2EB] transition-colors text-left" data-testid={`user-${targetUser.id}`}>
                    <div className="relative">
                      <Avatar className="h-12 w-12">
                        <AvatarFallback className="bg-[#0F4C5C] text-white">{targetUser.full_name?.charAt(0).toUpperCase()}</AvatarFallback>
                      </Avatar>
                      {online.has(targetUser.id) && <span className="absolute bottom-0 right-0 w-3 h-3 bg-[#2A9D8F] border-2 border-white rounded-full" />}
                    </div>
                    <div>
                      <p className="font-medium text-[#1A1A1A]">{targetUser.full_name}</p>
                      <span className="text-xs px-2 py-0.5 rounded-full bg-[#0F4C5C] text-white">Membre</span>
                    </div>
                  </button>
                ))}
              </div>
            ) : loading ? (
              <div className="flex justify-center py-12"><Loader2 className="animate-spin text-[#0F4C5C]" size={24} /></div>
            ) : conversations.length === 0 ? (
              <div className="p-8 text-center">
                <MessageSquare size={40} className="mx-auto text-[#E5E0D8] mb-3" />
                <p className="text-[#5C5C5C]">Aucune conversation</p>
                <p className="text-sm text-[#5C5C5C]/60">Commencez à échanger avec la communauté</p>
              </div>
            ) : (
              <div className="p-2">
                {conversations.map((conv) => (
                  <button key={conv.user_id} onClick={() => setSelectedUser(conv)} className={`w-full flex items-center gap-3 p-3 rounded-xl transition-colors text-left ${selectedUser && peerId(selectedUser) === conv.user_id ? 'bg-[#0F4C5C] text-white' : 'hover:bg-[#F5F2EB]'}`} data-testid={`conversation-${conv.user_id}`}>
                    <div className="relative">
                      <Avatar className="h-12 w-12">
                        <AvatarFallback className={selectedUser && peerId(selectedUser) === conv.user_id ? 'bg-white text-[#0F4C5C]' : 'bg-[#0F4C5C] text-white'}>{conv.user_name?.charAt(0).toUpperCase()}</AvatarFallback>
                      </Avatar>
                      {(conv.online || online.has(conv.user_id)) && <span className="absolute bottom-0 right-0 w-3 h-3 bg-[#2A9D8F] border-2 border-white rounded-full" data-testid={`online-${conv.user_id}`} />}
                      {conv.unread_count > 0 && <span className="absolute -top-1 -right-1 w-5 h-5 bg-[#E36414] text-white text-xs rounded-full flex items-center justify-center">{conv.unread_count}</span>}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className={`font-medium truncate ${selectedUser && peerId(selectedUser) === conv.user_id ? 'text-white' : 'text-[#1A1A1A]'}`}>{conv.user_name}</p>
                        <span className={`text-xs ${selectedUser && peerId(selectedUser) === conv.user_id ? 'text-white/60' : 'text-[#5C5C5C]'}`}>{formatDistanceToNow(new Date(conv.last_message_time), { locale: fr })}</span>
                      </div>
                      <p className={`text-sm truncate ${selectedUser && peerId(selectedUser) === conv.user_id ? 'text-white/80' : 'text-[#5C5C5C]'}`}>{conv.last_message}</p>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </ScrollArea>
        </div>

        {/* Chat Area */}
        <div className={`flex-1 flex flex-col ${!selectedUser ? 'hidden md:flex' : 'flex'}`}>
          {selectedUser ? (
            <>
              <div className="h-16 px-4 border-b border-[#E5E0D8] flex items-center gap-4 bg-white">
                <button onClick={() => setSelectedUser(null)} className="md:hidden p-2 -ml-2"><ArrowLeft size={20} /></button>
                <div className="relative">
                  <Avatar className="h-10 w-10"><AvatarFallback className="bg-[#0F4C5C] text-white">{selectedUser.user_name?.charAt(0).toUpperCase()}</AvatarFallback></Avatar>
                  {isPeerOnline && <span className="absolute bottom-0 right-0 w-3 h-3 bg-[#2A9D8F] border-2 border-white rounded-full" />}
                </div>
                <div>
                  <p className="font-semibold text-[#1A1A1A]">{selectedUser.user_name}</p>
                  <span className="text-xs text-[#2A9D8F]" data-testid="peer-status">
                    {peerTyping ? 'en train d\u2019écrire…' : isPeerOnline ? 'en ligne' : 'hors ligne'}
                  </span>
                </div>
              </div>

              <ScrollArea className="flex-1 p-4 bg-[#F5F2EB]">
                <div className="space-y-3 max-w-2xl mx-auto" data-testid="messages-list">
                  {messages.map((msg) => {
                    const isSent = msg.sender_id === user.id;
                    return (
                      <div key={msg.id} className={`flex ${isSent ? 'justify-end' : 'justify-start'}`} data-testid={`message-${msg.id}`}>
                        <div className={`max-w-[70%] px-4 py-3 ${isSent ? 'message-sent' : 'message-received'}`}>
                          <p>{msg.content}</p>
                          <div className={`flex items-center gap-1 mt-1 ${isSent ? 'justify-end text-white/60' : 'text-[#5C5C5C]'}`}>
                            <span className="text-xs">{formatDistanceToNow(new Date(msg.created_at), { addSuffix: true, locale: fr })}</span>
                            {isSent && <span data-testid={`status-${msg.id}`}>{statusIcon(msg)}</span>}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                  {peerTyping && (
                    <div className="flex justify-start" data-testid="typing-indicator">
                      <div className="message-received px-4 py-3 text-[#5C5C5C] italic text-sm">en train d'écrire…</div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>
              </ScrollArea>

              <form onSubmit={handleSendMessage} className="p-4 bg-white border-t border-[#E5E0D8] relative z-50">
                <div className="flex gap-3 max-w-2xl mx-auto pr-16 md:pr-0">
                  <Input placeholder="Écrire un message..." value={newMessage} onChange={handleInputChange} className="ubuntoo-input flex-1" data-testid="message-input" />
                  <Button type="submit" disabled={!newMessage.trim()} className="btn-primary px-6" data-testid="send-message-button"><Send size={18} /></Button>
                </div>
              </form>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center bg-[#F5F2EB]">
              <div className="text-center">
                <MessageSquare size={64} className="mx-auto text-[#E5E0D8] mb-4" />
                <h3 className="text-xl font-semibold text-[#1A1A1A] mb-2">Vos messages</h3>
                <p className="text-[#5C5C5C]">Sélectionnez une conversation ou démarrez-en une nouvelle</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
