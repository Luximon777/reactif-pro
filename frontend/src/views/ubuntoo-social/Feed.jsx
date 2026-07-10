import { useState, useEffect } from 'react';
import { useAuth } from './UbuntooSocialContext';
import { postsApi, reportApi } from './api';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { toast } from 'sonner';
import {
  MessageCircle,
  Send,
  HelpCircle,
  BookOpen,
  Sparkles,
  Star,
  HeartHandshake,
  LifeBuoy,
  Calendar,
  PartyPopper,
  Lightbulb,
  Flame,
  Flag,
  Loader2
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { fr } from 'date-fns/locale';

const POST_TYPES = [
  { value: 'temoignage', label: 'Témoignage', icon: MessageCircle },
  { value: 'reussite', label: 'Réussite', icon: Star },
  { value: 'question', label: 'Question', icon: HelpCircle },
  { value: 'offre_aide', label: "Offre d'aide", icon: HeartHandshake },
  { value: 'demande_aide', label: "Demande d'aide", icon: LifeBuoy },
  { value: 'retour_experience', label: "Retour d'expérience", icon: Sparkles },
  { value: 'ressource', label: 'Ressource utile', icon: BookOpen },
  { value: 'evenement', label: 'Événement', icon: Calendar },
];

// Rétro-compatibilité avec anciens types
const LEGACY_TYPES = {
  general: { label: 'Général', icon: MessageCircle },
  resource: { label: 'Ressource utile', icon: BookOpen },
  experience: { label: "Retour d'expérience", icon: Sparkles },
};

const REACTIONS = [
  { key: 'merci', label: 'Merci', icon: HeartHandshake },
  { key: 'bravo', label: 'Bravo', icon: PartyPopper },
  { key: 'interessant', label: 'Intéressant', icon: Lightbulb },
  { key: 'courage', label: 'Courage', icon: Flame },
  { key: 'inspirant', label: 'Inspirant', icon: Sparkles },
];

const getTypeMeta = (type) =>
  POST_TYPES.find((t) => t.value === type) || LEGACY_TYPES[type] || LEGACY_TYPES.general;

export default function Feed() {
  const { user, refreshUser } = useAuth();
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [posting, setPosting] = useState(false);
  const [activeTab, setActiveTab] = useState('all');
  const [newPost, setNewPost] = useState({ content: '', post_type: 'temoignage' });
  const [expandedComments, setExpandedComments] = useState({});
  const [comments, setComments] = useState({});
  const [newComments, setNewComments] = useState({});

  useEffect(() => {
    fetchPosts();
  }, [activeTab]);

  const fetchPosts = async () => {
    try {
      const postType = activeTab === 'all' ? null : activeTab;
      const response = await postsApi.getAll(postType);
      setPosts(response.data);
    } catch (error) {
      toast.error('Erreur lors du chargement des publications');
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePost = async (e) => {
    e.preventDefault();
    if (!newPost.content.trim()) return;
    setPosting(true);
    try {
      await postsApi.create(newPost);
      setNewPost({ content: '', post_type: 'temoignage' });
      fetchPosts();
      refreshUser();
      toast.success('Publication créée !');
    } catch (error) {
      toast.error('Erreur lors de la création');
    } finally {
      setPosting(false);
    }
  };

  const getUserReaction = (post) => {
    const reactions = post.reactions || {};
    return REACTIONS.find((r) => (reactions[r.key] || []).includes(user?.id))?.key || null;
  };

  const handleReact = async (postId, type) => {
    try {
      const res = await postsApi.react(postId, type);
      const newReaction = res.data.reaction;
      setPosts((prev) =>
        prev.map((p) => {
          if (p.id !== postId) return p;
          const reactions = { ...(p.reactions || {}) };
          Object.keys(reactions).forEach((k) => {
            reactions[k] = (reactions[k] || []).filter((id) => id !== user.id);
          });
          if (newReaction) {
            reactions[newReaction] = [...(reactions[newReaction] || []), user.id];
          }
          return { ...p, reactions };
        })
      );
    } catch (error) {
      toast.error('Erreur');
    }
  };

  const handleReport = async (postId) => {
    const reason = window.prompt('Pourquoi signalez-vous cette publication ?');
    if (reason === null) return;
    try {
      await reportApi.create('post', postId, reason || 'Contenu inapproprié');
      toast.success('Signalement transmis à la modération');
    } catch (error) {
      toast.error('Erreur lors du signalement');
    }
  };

  const toggleComments = async (postId) => {
    if (expandedComments[postId]) {
      setExpandedComments({ ...expandedComments, [postId]: false });
      return;
    }
    try {
      const response = await postsApi.getComments(postId);
      setComments({ ...comments, [postId]: response.data });
      setExpandedComments({ ...expandedComments, [postId]: true });
    } catch (error) {
      toast.error('Erreur lors du chargement des commentaires');
    }
  };

  const handleAddComment = async (postId) => {
    const content = newComments[postId];
    if (!content?.trim()) return;
    try {
      await postsApi.addComment(postId, content);
      setNewComments({ ...newComments, [postId]: '' });
      const response = await postsApi.getComments(postId);
      setComments({ ...comments, [postId]: response.data });
      setPosts(posts.map((p) => (p.id === postId ? { ...p, comments_count: p.comments_count + 1 } : p)));
      refreshUser();
      toast.success('Merci pour votre commentaire !');
    } catch (error) {
      toast.error('Erreur');
    }
  };

  const filterChips = [{ value: 'all', label: 'Tout' }, ...POST_TYPES.map((t) => ({ value: t.value, label: t.label }))];

  return (
    <div className="min-h-screen bg-[#FDFBF7] pt-20">
      <div className="container-main py-8">
        <div className="max-w-2xl mx-auto">
          {/* Create Post */}
          <div className="ubuntoo-card p-6 mb-6 animate-fade-in" data-testid="create-post-card">
            <div className="flex gap-4">
              <Avatar className="h-12 w-12 border-2 border-[#E36414]">
                <AvatarFallback className="bg-[#0F4C5C] text-white font-semibold">
                  {user?.full_name?.charAt(0).toUpperCase()}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1">
                <form onSubmit={handleCreatePost}>
                  <Textarea
                    placeholder="Partagez avec la communauté..."
                    value={newPost.content}
                    onChange={(e) => setNewPost({ ...newPost, content: e.target.value })}
                    className="ubuntoo-input min-h-[100px] resize-none mb-4"
                    data-testid="post-content-input"
                  />
                  <div className="flex flex-wrap gap-2 mb-4">
                    {POST_TYPES.map((type) => (
                      <button
                        key={type.value}
                        type="button"
                        onClick={() => setNewPost({ ...newPost, post_type: type.value })}
                        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                          newPost.post_type === type.value
                            ? 'bg-[#0F4C5C] text-white'
                            : 'bg-[#F5F2EB] text-[#5C5C5C] hover:bg-[#E5E0D8]'
                        }`}
                        data-testid={`post-type-${type.value}`}
                      >
                        <type.icon size={14} />
                        {type.label}
                      </button>
                    ))}
                  </div>
                  <div className="flex justify-end">
                    <Button
                      type="submit"
                      disabled={posting || !newPost.content.trim()}
                      className="btn-secondary"
                      data-testid="submit-post-button"
                    >
                      {posting ? <Loader2 className="animate-spin" size={18} /> : <Send size={18} />}
                      <span className="ml-2">Publier</span>
                    </Button>
                  </div>
                </form>
              </div>
            </div>
          </div>

          {/* Filters */}
          <div className="flex gap-2 mb-6 overflow-x-auto pb-2" data-testid="feed-filters">
            {filterChips.map((chip) => (
              <button
                key={chip.value}
                onClick={() => setActiveTab(chip.value)}
                className={`whitespace-nowrap px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                  activeTab === chip.value
                    ? 'bg-[#0F4C5C] text-white'
                    : 'bg-white border border-[#E5E0D8] text-[#5C5C5C] hover:bg-[#F5F2EB]'
                }`}
                data-testid={`filter-${chip.value}`}
              >
                {chip.label}
              </button>
            ))}
          </div>

          {/* Posts */}
          {loading ? (
            <div className="flex justify-center py-12">
              <Loader2 className="animate-spin text-[#0F4C5C]" size={32} />
            </div>
          ) : posts.length === 0 ? (
            <div className="ubuntoo-card p-12 text-center">
              <MessageCircle size={48} className="mx-auto text-[#E5E0D8] mb-4" />
              <h3 className="text-lg font-semibold text-[#1A1A1A] mb-2">Aucune publication</h3>
              <p className="text-[#5C5C5C]">Soyez le premier à partager avec la communauté !</p>
            </div>
          ) : (
            <div className="space-y-4">
              {posts.map((post, index) => {
                const meta = getTypeMeta(post.post_type);
                const MetaIcon = meta.icon;
                const userReaction = getUserReaction(post);
                return (
                  <div
                    key={post.id}
                    className="ubuntoo-card p-6 animate-fade-in"
                    style={{ animationDelay: `${index * 0.05}s` }}
                    data-testid={`post-${post.id}`}
                  >
                    {/* Post Header */}
                    <div className="flex items-start gap-4 mb-4">
                      <Avatar className="h-12 w-12 border-2 border-[#E5E0D8]">
                        <AvatarFallback className="bg-[#0F4C5C] text-white font-semibold">
                          {post.author_name?.charAt(0).toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="font-semibold text-[#1A1A1A]">{post.author_name}</span>
                          <span className="text-xs px-2 py-0.5 rounded-full bg-[#0F4C5C] text-white">Membre</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm text-[#5C5C5C]">
                          <span className="flex items-center gap-1">
                            <MetaIcon size={16} />
                            {meta.label}
                          </span>
                          <span>•</span>
                          <span>{formatDistanceToNow(new Date(post.created_at), { addSuffix: true, locale: fr })}</span>
                        </div>
                      </div>
                      <button
                        onClick={() => handleReport(post.id)}
                        className="text-[#B0B0B0] hover:text-[#E36414] transition-colors p-1"
                        title="Signaler"
                        data-testid={`report-button-${post.id}`}
                      >
                        <Flag size={16} />
                      </button>
                    </div>

                    {/* Post Content */}
                    <p className="text-[#1A1A1A] whitespace-pre-wrap mb-4">{post.content}</p>

                    {/* Reactions */}
                    <div className="flex flex-wrap items-center gap-2 pt-4 border-t border-[#E5E0D8]">
                      {REACTIONS.map((r) => {
                        const count = (post.reactions?.[r.key] || []).length;
                        const active = userReaction === r.key;
                        const RIcon = r.icon;
                        return (
                          <button
                            key={r.key}
                            onClick={() => handleReact(post.id, r.key)}
                            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                              active
                                ? 'bg-[#E36414] text-white'
                                : 'bg-[#F5F2EB] text-[#5C5C5C] hover:bg-[#E5E0D8]'
                            }`}
                            data-testid={`react-${r.key}-${post.id}`}
                          >
                            <RIcon size={14} />
                            <span>{r.label}</span>
                            {count > 0 && <span className="font-semibold">{count}</span>}
                          </button>
                        );
                      })}
                      <button
                        onClick={() => toggleComments(post.id)}
                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium text-[#5C5C5C] hover:text-[#0F4C5C] hover:bg-[#F5F2EB] transition-colors ml-auto"
                        data-testid={`comments-button-${post.id}`}
                      >
                        <MessageCircle size={16} />
                        <span>{post.comments_count}</span>
                      </button>
                    </div>

                    {/* Comments Section */}
                    {expandedComments[post.id] && (
                      <div className="mt-4 pt-4 border-t border-[#E5E0D8] animate-fade-in">
                        <div className="flex gap-3 mb-4">
                          <Avatar className="h-8 w-8">
                            <AvatarFallback className="bg-[#0F4C5C] text-white text-sm">
                              {user?.full_name?.charAt(0).toUpperCase()}
                            </AvatarFallback>
                          </Avatar>
                          <div className="flex-1 flex gap-2">
                            <input
                              type="text"
                              placeholder="Ajouter un commentaire..."
                              value={newComments[post.id] || ''}
                              onChange={(e) => setNewComments({ ...newComments, [post.id]: e.target.value })}
                              onKeyDown={(e) => e.key === 'Enter' && handleAddComment(post.id)}
                              className="ubuntoo-input flex-1 py-2"
                              data-testid={`comment-input-${post.id}`}
                            />
                            <Button
                              onClick={() => handleAddComment(post.id)}
                              size="sm"
                              className="bg-[#0F4C5C] hover:bg-[#0A3844]"
                              data-testid={`submit-comment-${post.id}`}
                            >
                              <Send size={16} />
                            </Button>
                          </div>
                        </div>
                        <div className="space-y-3">
                          {comments[post.id]?.map((comment) => (
                            <div key={comment.id} className="flex gap-3 p-3 bg-[#F5F2EB] rounded-xl">
                              <Avatar className="h-8 w-8">
                                <AvatarFallback className="bg-[#E36414] text-white text-sm">
                                  {comment.author_name?.charAt(0).toUpperCase()}
                                </AvatarFallback>
                              </Avatar>
                              <div>
                                <div className="flex items-center gap-2">
                                  <span className="font-medium text-sm text-[#1A1A1A]">{comment.author_name}</span>
                                  <span className="text-xs px-1.5 py-0.5 rounded-full bg-[#0F4C5C] text-white">Membre</span>
                                </div>
                                <p className="text-sm text-[#5C5C5C] mt-1">{comment.content}</p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
