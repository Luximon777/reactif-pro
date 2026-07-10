import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from './UbuntooSocialContext';
import { groupsApi, discussionsApi } from './api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { toast } from 'sonner';
import { 
  ArrowLeft, 
  Users, 
  MessageSquare, 
  Plus, 
  Loader2,
  Calendar,
  Briefcase,
  GraduationCap,
  Heart,
  Handshake
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { fr } from 'date-fns/locale';

export default function GroupDetail() {
  const { groupId } = useParams();
  const { user, refreshUser } = useAuth();
  const [group, setGroup] = useState(null);
  const [discussions, setDiscussions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [creating, setCreating] = useState(false);
  const [joining, setJoining] = useState(false);
  const [newDiscussion, setNewDiscussion] = useState({ title: '', content: '' });

  useEffect(() => {
    fetchGroup();
    fetchDiscussions();
  }, [groupId]);

  const fetchGroup = async () => {
    try {
      const response = await groupsApi.getById(groupId);
      setGroup(response.data);
    } catch (error) {
      toast.error('Groupe non trouvé');
    } finally {
      setLoading(false);
    }
  };

  const fetchDiscussions = async () => {
    try {
      const response = await groupsApi.getDiscussions(groupId);
      setDiscussions(response.data);
    } catch (error) {
      console.error('Failed to fetch discussions');
    }
  };

  const handleJoinGroup = async () => {
    setJoining(true);
    try {
      const response = await groupsApi.join(groupId);
      fetchGroup();
      toast.success(response.data.joined ? 'Vous avez rejoint le groupe' : 'Vous avez quitté le groupe');
    } catch (error) {
      toast.error('Erreur');
    } finally {
      setJoining(false);
    }
  };

  const handleCreateDiscussion = async (e) => {
    e.preventDefault();
    if (!newDiscussion.title.trim() || !newDiscussion.content.trim()) return;

    setCreating(true);
    try {
      await discussionsApi.create({
        ...newDiscussion,
        group_id: groupId
      });
      setNewDiscussion({ title: '', content: '' });
      setDialogOpen(false);
      fetchDiscussions();
      refreshUser();
      toast.success('Discussion créée !');
    } catch (error) {
      toast.error('Erreur lors de la création');
    } finally {
      setCreating(false);
    }
  };

  const getCategoryIcon = (category) => {
    const icons = {
      emploi: Briefcase,
      formation: GraduationCap,
      'bien-etre': Heart,
      entraide: Handshake
    };
    return icons[category] || Handshake;
  };

  const getCategoryColor = (category) => {
    const colors = {
      emploi: 'bg-[#EAF8F6] text-[#2A9D8F]',
      formation: 'bg-[#FEF0E3] text-[#E36414]',
      'bien-etre': 'bg-[#E8F4F8] text-[#0F4C5C]',
      entraide: 'bg-[#FFF8E8] text-[#FB8B24]'
    };
    return colors[category] || colors.entraide;
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

  if (!group) {
    return (
      <div className="min-h-screen bg-[#FDFBF7] pt-20">
        <div className="container-main py-8 text-center">
          <h2 className="text-2xl font-bold text-[#1A1A1A]">Groupe non trouvé</h2>
          <Link to="/ubuntoo/groups" className="text-[#0F4C5C] mt-4 inline-block">
            Retour aux groupes
          </Link>
        </div>
      </div>
    );
  }

  const CategoryIcon = getCategoryIcon(group.category);

  return (
    <div className="min-h-screen bg-[#FDFBF7] pt-20">
      <div className="container-main py-8">
        {/* Back link */}
        <Link 
          to="/ubuntoo/groups" 
          className="inline-flex items-center gap-2 text-[#5C5C5C] hover:text-[#0F4C5C] mb-6 transition-colors"
        >
          <ArrowLeft size={20} />
          Retour aux groupes
        </Link>

        {/* Group Header */}
        <div className="ubuntoo-card p-8 mb-8 animate-fade-in">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            <div className="flex items-start gap-4">
              <div className={`p-4 rounded-2xl ${getCategoryColor(group.category)}`}>
                <CategoryIcon size={32} />
              </div>
              <div>
                <span className={`text-xs px-3 py-1 rounded-full ${getCategoryColor(group.category)} mb-2 inline-block`}>
                  {group.category === 'bien-etre' ? 'Bien-être' : group.category.charAt(0).toUpperCase() + group.category.slice(1)}
                </span>
                <h1 className="text-2xl lg:text-3xl font-bold text-[#1A1A1A]" style={{ fontFamily: 'Manrope, sans-serif' }}>
                  {group.name}
                </h1>
                <p className="text-[#5C5C5C] mt-2">{group.description}</p>
                <div className="flex items-center gap-4 mt-4 text-sm text-[#5C5C5C]">
                  <span className="flex items-center gap-1">
                    <Users size={16} />
                    {group.members_count} membre{group.members_count > 1 ? 's' : ''}
                  </span>
                  <span className="flex items-center gap-1">
                    <Calendar size={16} />
                    Créé {formatDistanceToNow(new Date(group.created_at), { addSuffix: true, locale: fr })}
                  </span>
                </div>
              </div>
            </div>
            
            <Button 
              onClick={handleJoinGroup}
              disabled={joining}
              className="btn-primary"
              data-testid="join-group-button"
            >
              {joining ? <Loader2 className="animate-spin" size={18} /> : 'Rejoindre / Quitter'}
            </Button>
          </div>
        </div>

        {/* Discussions Section */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-[#1A1A1A]" style={{ fontFamily: 'Manrope, sans-serif' }}>
            Discussions ({discussions.length})
          </h2>
          
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button className="btn-secondary" data-testid="create-discussion-button">
                <Plus size={18} className="mr-2" />
                Nouvelle discussion
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-lg" aria-describedby="create-discussion-description">
              <DialogHeader>
                <DialogTitle className="text-xl font-bold" style={{ fontFamily: 'Manrope, sans-serif' }}>
                  Créer une discussion
                </DialogTitle>
                <p id="create-discussion-description" className="text-sm text-[#5C5C5C]">
                  Lancez un nouveau sujet de discussion
                </p>
              </DialogHeader>
              <form onSubmit={handleCreateDiscussion} className="space-y-4 mt-4">
                <div className="space-y-2">
                  <Label htmlFor="title">Titre</Label>
                  <Input
                    id="title"
                    value={newDiscussion.title}
                    onChange={(e) => setNewDiscussion({ ...newDiscussion, title: e.target.value })}
                    placeholder="De quoi souhaitez-vous discuter ?"
                    className="ubuntoo-input"
                    data-testid="discussion-title-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="content">Contenu</Label>
                  <Textarea
                    id="content"
                    value={newDiscussion.content}
                    onChange={(e) => setNewDiscussion({ ...newDiscussion, content: e.target.value })}
                    placeholder="Détaillez votre sujet..."
                    className="ubuntoo-input min-h-[150px]"
                    data-testid="discussion-content-input"
                  />
                </div>
                <div className="flex gap-3 pt-2">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setDialogOpen(false)}
                    className="flex-1"
                  >
                    Annuler
                  </Button>
                  <Button 
                    type="submit" 
                    className="flex-1 btn-primary"
                    disabled={creating}
                    data-testid="submit-discussion-button"
                  >
                    {creating ? <Loader2 className="animate-spin" size={18} /> : 'Publier'}
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {/* Discussions List */}
        {discussions.length === 0 ? (
          <div className="ubuntoo-card p-12 text-center">
            <MessageSquare size={48} className="mx-auto text-[#E5E0D8] mb-4" />
            <h3 className="text-lg font-semibold text-[#1A1A1A] mb-2">Aucune discussion</h3>
            <p className="text-[#5C5C5C]">Soyez le premier à lancer une discussion !</p>
          </div>
        ) : (
          <div className="space-y-4">
            {discussions.map((discussion, index) => (
              <Link
                key={discussion.id}
                to={`/ubuntoo/discussions/${discussion.id}`}
                className="ubuntoo-card p-6 block card-hover animate-fade-in"
                style={{ animationDelay: `${index * 0.05}s` }}
                data-testid={`discussion-${discussion.id}`}
              >
                <div className="flex items-start gap-4">
                  <Avatar className="h-12 w-12">
                    <AvatarFallback className="bg-[#0F4C5C] text-white">
                      {discussion.author_name?.charAt(0).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-[#1A1A1A] mb-1" style={{ fontFamily: 'Manrope, sans-serif' }}>
                      {discussion.title}
                    </h3>
                    <p className="text-sm text-[#5C5C5C] line-clamp-2 mb-3">
                      {discussion.content}
                    </p>
                    <div className="flex items-center gap-4 text-sm text-[#5C5C5C]">
                      <span className="flex items-center gap-1">
                        <span className="font-medium">{discussion.author_name}</span>
                        <span className={`text-xs px-2 py-0.5 rounded-full ${getRoleColor(discussion.author_role)}`}>
                          {getRoleLabel(discussion.author_role)}
                        </span>
                      </span>
                      <span>•</span>
                      <span className="flex items-center gap-1">
                        <MessageSquare size={14} />
                        {discussion.replies_count} réponse{discussion.replies_count > 1 ? 's' : ''}
                      </span>
                      <span>•</span>
                      <span>
                        {formatDistanceToNow(new Date(discussion.created_at), { addSuffix: true, locale: fr })}
                      </span>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
