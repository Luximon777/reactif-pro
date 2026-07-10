import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from './UbuntooSocialContext';
import { groupsApi } from './api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { toast } from 'sonner';
import { 
  Users, 
  Plus, 
  Briefcase, 
  GraduationCap, 
  Heart, 
  Handshake,
  Loader2,
  ArrowRight
} from 'lucide-react';

export default function Groups() {
  const { user, refreshUser } = useAuth();
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('all');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [creating, setCreating] = useState(false);
  const [newGroup, setNewGroup] = useState({
    name: '',
    description: '',
    category: 'entraide'
  });

  useEffect(() => {
    fetchGroups();
  }, [activeTab]);

  const fetchGroups = async () => {
    setLoading(true);
    try {
      const category = activeTab === 'all' ? null : activeTab;
      const response = await groupsApi.getAll(category);
      setGroups(response.data);
    } catch (error) {
      toast.error('Erreur lors du chargement des groupes');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateGroup = async (e) => {
    e.preventDefault();
    if (!newGroup.name.trim() || !newGroup.description.trim()) return;

    setCreating(true);
    try {
      await groupsApi.create(newGroup);
      setNewGroup({ name: '', description: '', category: 'entraide' });
      setDialogOpen(false);
      fetchGroups();
      refreshUser();
      toast.success('Groupe créé !');
    } catch (error) {
      toast.error('Erreur lors de la création');
    } finally {
      setCreating(false);
    }
  };

  const handleJoinGroup = async (groupId) => {
    try {
      const response = await groupsApi.join(groupId);
      fetchGroups();
      toast.success(response.data.joined ? 'Vous avez rejoint le groupe' : 'Vous avez quitté le groupe');
    } catch (error) {
      toast.error('Erreur');
    }
  };

  const categories = [
    { value: 'emploi', label: 'Emploi', icon: Briefcase, color: 'category-emploi' },
    { value: 'formation', label: 'Formation', icon: GraduationCap, color: 'category-formation' },
    { value: 'bien-etre', label: 'Bien-être', icon: Heart, color: 'category-bien-etre' },
    { value: 'entraide', label: 'Entraide', icon: Handshake, color: 'category-entraide' }
  ];

  const getCategoryInfo = (categoryValue) => {
    return categories.find(c => c.value === categoryValue) || categories[3];
  };

  return (
    <div className="min-h-screen bg-[#FDFBF7] pt-20">
      <div className="container-main py-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold text-[#1A1A1A]" style={{ fontFamily: 'Manrope, sans-serif' }}>
              Groupes thématiques
            </h1>
            <p className="text-[#5C5C5C] mt-1">
              Rejoignez des communautés qui partagent vos intérêts
            </p>
          </div>
          
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button className="btn-secondary" data-testid="create-group-button">
                <Plus size={18} className="mr-2" />
                Créer un groupe
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-md" aria-describedby="create-group-description">
              <DialogHeader>
                <DialogTitle className="text-xl font-bold" style={{ fontFamily: 'Manrope, sans-serif' }}>
                  Créer un nouveau groupe
                </DialogTitle>
                <p id="create-group-description" className="text-sm text-[#5C5C5C]">
                  Créez un espace de discussion pour la communauté
                </p>
              </DialogHeader>
              <form onSubmit={handleCreateGroup} className="space-y-4 mt-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Nom du groupe</Label>
                  <Input
                    id="name"
                    value={newGroup.name}
                    onChange={(e) => setNewGroup({ ...newGroup, name: e.target.value })}
                    placeholder="Ex: Reconversion dans le numérique"
                    className="ubuntoo-input"
                    data-testid="group-name-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="category">Catégorie</Label>
                  <Select
                    value={newGroup.category}
                    onValueChange={(value) => setNewGroup({ ...newGroup, category: value })}
                  >
                    <SelectTrigger className="ubuntoo-input" data-testid="group-category-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {categories.map((cat) => (
                        <SelectItem key={cat.value} value={cat.value}>
                          <div className="flex items-center gap-2">
                            <cat.icon size={16} />
                            {cat.label}
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    value={newGroup.description}
                    onChange={(e) => setNewGroup({ ...newGroup, description: e.target.value })}
                    placeholder="Décrivez l'objectif du groupe..."
                    className="ubuntoo-input min-h-[100px]"
                    data-testid="group-description-input"
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
                    data-testid="submit-group-button"
                  >
                    {creating ? <Loader2 className="animate-spin" size={18} /> : 'Créer'}
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {/* Filters */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-8">
          <TabsList className="bg-white border border-[#E5E0D8] p-1 rounded-xl flex-wrap h-auto">
            <TabsTrigger 
              value="all" 
              className="rounded-lg data-[state=active]:bg-[#0F4C5C] data-[state=active]:text-white"
            >
              Tous
            </TabsTrigger>
            {categories.map((cat) => (
              <TabsTrigger
                key={cat.value}
                value={cat.value}
                className="rounded-lg data-[state=active]:bg-[#0F4C5C] data-[state=active]:text-white"
              >
                <cat.icon size={16} className="mr-1.5" />
                {cat.label}
              </TabsTrigger>
            ))}
          </TabsList>
        </Tabs>

        {/* Groups Grid */}
        {loading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="animate-spin text-[#0F4C5C]" size={32} />
          </div>
        ) : groups.length === 0 ? (
          <div className="ubuntoo-card p-12 text-center max-w-md mx-auto">
            <Users size={48} className="mx-auto text-[#E5E0D8] mb-4" />
            <h3 className="text-lg font-semibold text-[#1A1A1A] mb-2">Aucun groupe</h3>
            <p className="text-[#5C5C5C] mb-4">
              Soyez le premier à créer un groupe dans cette catégorie !
            </p>
            <Button onClick={() => setDialogOpen(true)} className="btn-secondary">
              <Plus size={18} className="mr-2" />
              Créer un groupe
            </Button>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {groups.map((group, index) => {
              const catInfo = getCategoryInfo(group.category);
              return (
                <div
                  key={group.id}
                  className="ubuntoo-card p-6 card-hover animate-fade-in"
                  style={{ animationDelay: `${index * 0.05}s` }}
                  data-testid={`group-${group.id}`}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className={`p-3 rounded-xl ${catInfo.color}`}>
                      <catInfo.icon size={24} />
                    </div>
                    <span className={`text-xs px-3 py-1 rounded-full ${catInfo.color}`}>
                      {catInfo.label}
                    </span>
                  </div>
                  
                  <h3 className="text-lg font-semibold text-[#1A1A1A] mb-2" style={{ fontFamily: 'Manrope, sans-serif' }}>
                    {group.name}
                  </h3>
                  <p className="text-[#5C5C5C] text-sm mb-4 line-clamp-2">
                    {group.description}
                  </p>
                  
                  <div className="flex items-center justify-between pt-4 border-t border-[#E5E0D8]">
                    <div className="flex items-center gap-2 text-sm text-[#5C5C5C]">
                      <Users size={16} />
                      <span>{group.members_count} membre{group.members_count > 1 ? 's' : ''}</span>
                    </div>
                    <Link to={`/ubuntoo/groups/${group.id}`}>
                      <Button variant="ghost" size="sm" className="text-[#0F4C5C] hover:text-[#0F4C5C] hover:bg-[#E8F4F8]">
                        Voir
                        <ArrowRight size={16} className="ml-1" />
                      </Button>
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
