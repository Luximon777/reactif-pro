import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from './UbuntooSocialContext';
import { discussionsApi } from './api';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { toast } from 'sonner';
import { ArrowLeft, MessageSquare, Send, Loader2 } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { fr } from 'date-fns/locale';

export default function DiscussionDetail() {
  const { discussionId } = useParams();
  const { user, refreshUser } = useAuth();
  const [discussion, setDiscussion] = useState(null);
  const [replies, setReplies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newReply, setNewReply] = useState('');
  const [sending, setSending] = useState(false);

  useEffect(() => {
    fetchDiscussion();
    fetchReplies();
  }, [discussionId]);

  const fetchDiscussion = async () => {
    try {
      const response = await discussionsApi.getById(discussionId);
      setDiscussion(response.data);
    } catch (error) {
      toast.error('Discussion non trouvée');
    } finally {
      setLoading(false);
    }
  };

  const fetchReplies = async () => {
    try {
      const response = await discussionsApi.getReplies(discussionId);
      setReplies(response.data);
    } catch (error) {
      console.error('Failed to fetch replies');
    }
  };

  const handleAddReply = async (e) => {
    e.preventDefault();
    if (!newReply.trim()) return;

    setSending(true);
    try {
      await discussionsApi.addReply(discussionId, newReply);
      setNewReply('');
      fetchReplies();
      fetchDiscussion();
      refreshUser();
      toast.success('Réponse ajoutée !');
    } catch (error) {
      toast.error('Erreur lors de l\'envoi');
    } finally {
      setSending(false);
    }
  };

  const getRoleColor = (role) => {
    return 'bg-[#0F4C5C] text-white';
  };

  const getRoleLabel = (role) => {
    return 'Membre';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#FDFBF7] pt-20 flex items-center justify-center">
        <Loader2 className="animate-spin text-[#0F4C5C]" size={32} />
      </div>
    );
  }

  if (!discussion) {
    return (
      <div className="min-h-screen bg-[#FDFBF7] pt-20">
        <div className="container-main py-8 text-center">
          <h2 className="text-2xl font-bold text-[#1A1A1A]">Discussion non trouvée</h2>
          <Link to="/ubuntoo/groups" className="text-[#0F4C5C] mt-4 inline-block">
            Retour aux groupes
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#FDFBF7] pt-20">
      <div className="container-main py-8">
        <div className="max-w-3xl mx-auto">
          {/* Back link */}
          <Link 
            to={`/ubuntoo/groups/${discussion.group_id}`}
            className="inline-flex items-center gap-2 text-[#5C5C5C] hover:text-[#0F4C5C] mb-6 transition-colors"
          >
            <ArrowLeft size={20} />
            Retour au groupe
          </Link>

          {/* Discussion */}
          <div className="ubuntoo-card p-8 mb-8 animate-fade-in">
            <div className="flex items-start gap-4 mb-6">
              <Avatar className="h-14 w-14 border-2 border-[#E36414]">
                <AvatarFallback className="bg-[#0F4C5C] text-white text-lg">
                  {discussion.author_name?.charAt(0).toUpperCase()}
                </AvatarFallback>
              </Avatar>
              <div>
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="font-semibold text-[#1A1A1A]">{discussion.author_name}</span>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${getRoleColor(discussion.author_role)}`}>
                    {getRoleLabel(discussion.author_role)}
                  </span>
                </div>
                <p className="text-sm text-[#5C5C5C]">
                  {formatDistanceToNow(new Date(discussion.created_at), { addSuffix: true, locale: fr })}
                </p>
              </div>
            </div>

            <h1 className="text-2xl font-bold text-[#1A1A1A] mb-4" style={{ fontFamily: 'Manrope, sans-serif' }}>
              {discussion.title}
            </h1>
            <p className="text-[#5C5C5C] whitespace-pre-wrap">
              {discussion.content}
            </p>

            <div className="mt-6 pt-6 border-t border-[#E5E0D8]">
              <span className="flex items-center gap-2 text-sm text-[#5C5C5C]">
                <MessageSquare size={16} />
                {discussion.replies_count} réponse{discussion.replies_count > 1 ? 's' : ''}
              </span>
            </div>
          </div>

          {/* Reply Form */}
          <div className="ubuntoo-card p-6 mb-8 animate-fade-in stagger-1">
            <h3 className="font-semibold text-[#1A1A1A] mb-4">Ajouter une réponse</h3>
            <form onSubmit={handleAddReply}>
              <Textarea
                placeholder="Partagez votre avis ou expérience..."
                value={newReply}
                onChange={(e) => setNewReply(e.target.value)}
                className="ubuntoo-input min-h-[100px] mb-4"
                data-testid="reply-input"
              />
              <Button 
                type="submit" 
                disabled={sending || !newReply.trim()}
                className="btn-primary"
                data-testid="submit-reply-button"
              >
                {sending ? <Loader2 className="animate-spin" size={18} /> : <Send size={18} />}
                <span className="ml-2">Répondre</span>
              </Button>
            </form>
          </div>

          {/* Replies */}
          <div className="space-y-4">
            <h3 className="font-semibold text-[#1A1A1A]">
              Réponses ({replies.length})
            </h3>
            
            {replies.length === 0 ? (
              <div className="ubuntoo-card p-8 text-center">
                <MessageSquare size={40} className="mx-auto text-[#E5E0D8] mb-3" />
                <p className="text-[#5C5C5C]">Soyez le premier à répondre !</p>
              </div>
            ) : (
              replies.map((reply, index) => (
                <div 
                  key={reply.id}
                  className="ubuntoo-card p-6 animate-fade-in"
                  style={{ animationDelay: `${index * 0.05}s` }}
                  data-testid={`reply-${reply.id}`}
                >
                  <div className="flex items-start gap-4">
                    <Avatar className="h-10 w-10">
                      <AvatarFallback className="bg-[#E36414] text-white">
                        {reply.author_name?.charAt(0).toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 flex-wrap mb-2">
                        <span className="font-semibold text-[#1A1A1A]">{reply.author_name}</span>
                        <span className={`text-xs px-2 py-0.5 rounded-full ${getRoleColor(reply.author_role)}`}>
                          {getRoleLabel(reply.author_role)}
                        </span>
                        <span className="text-sm text-[#5C5C5C]">
                          • {formatDistanceToNow(new Date(reply.created_at), { addSuffix: true, locale: fr })}
                        </span>
                      </div>
                      <p className="text-[#5C5C5C] whitespace-pre-wrap">{reply.content}</p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
