import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from './UbuntooSocialContext';
import { usersApi } from './api';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Input } from '@/components/ui/input';
import { toast } from 'sonner';
import { 
  Users, 
  Search, 
  Award,
  Loader2,
  MessageSquare
} from 'lucide-react';

export default function Community() {
  const { user } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await usersApi.getAll();
      setUsers(response.data);
    } catch (error) {
      toast.error('Erreur lors du chargement');
    } finally {
      setLoading(false);
    }
  };

  const getRoleLabel = (role) => {
    return 'Membre';
  };

  const getRoleColor = (role) => {
    return 'bg-[#0F4C5C] text-white';
  };

  const filteredUsers = users
    .filter(u => {
      const matchesSearch = u.full_name.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesSearch;
    })
    .sort((a, b) => {
      // Trier par nombre de badges
      const badgesA = a.badges?.length || 0;
      const badgesB = b.badges?.length || 0;
      return badgesB - badgesA;
    });

  const stats = {
    total: users.length,
    withBadges: users.filter(u => (u.badges?.length || 0) > 1).length
  };

  return (
    <div className="min-h-screen bg-[#FDFBF7] pt-20">
      <div className="container-main py-8">
        {/* Header */}
        <div className="mb-8 animate-fade-in">
          <h1 className="text-3xl font-bold text-[#1A1A1A] mb-2" style={{ fontFamily: 'Manrope, sans-serif' }}>
            Notre communauté
          </h1>
          <p className="text-[#5C5C5C]">
            Découvrez les membres de la communauté UBUNTOO
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-4 mb-8">
          <div className="ubuntoo-card p-4 animate-fade-in stagger-1">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-[#F5F2EB]">
                <Users size={20} className="text-[#0F4C5C]" />
              </div>
              <div>
                <p className="text-2xl font-bold text-[#1A1A1A]">{stats.total}</p>
                <p className="text-sm text-[#5C5C5C]">Membres</p>
              </div>
            </div>
          </div>
          <div className="ubuntoo-card p-4 animate-fade-in stagger-2">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-[#FEF0E3]">
                <Award size={20} className="text-[#E36414]" />
              </div>
              <div>
                <p className="text-2xl font-bold text-[#1A1A1A]">{stats.withBadges}</p>
                <p className="text-sm text-[#5C5C5C]">Actifs</p>
              </div>
            </div>
          </div>
        </div>

        {/* Search */}
        <div className="mb-8">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-[#5C5C5C]" size={18} />
            <Input
              placeholder="Rechercher un membre..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 ubuntoo-input"
              data-testid="search-members"
            />
          </div>
        </div>

        {/* Members Grid */}
        {loading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="animate-spin text-[#0F4C5C]" size={32} />
          </div>
        ) : filteredUsers.length === 0 ? (
          <div className="ubuntoo-card p-12 text-center">
            <Users size={48} className="mx-auto text-[#E5E0D8] mb-4" />
            <h3 className="text-lg font-semibold text-[#1A1A1A] mb-2">Aucun membre trouvé</h3>
            <p className="text-[#5C5C5C]">Essayez une autre recherche</p>
          </div>
        ) : (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {filteredUsers.map((member, index) => (
              <div
                key={member.id}
                className={`ubuntoo-card p-6 card-hover animate-fade-in ${member.id === user?.id ? 'ring-2 ring-[#E36414]' : ''}`}
                style={{ animationDelay: `${index * 0.03}s` }}
                data-testid={`member-${member.id}`}
              >
                <div className="text-center">
                  <Avatar className="h-16 w-16 mx-auto mb-4 border-2 border-[#E5E0D8]">
                    <AvatarFallback className="bg-[#0F4C5C] text-white text-xl">
                      {member.full_name?.charAt(0).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  
                  <h3 className="font-semibold text-[#1A1A1A] mb-1">
                    {member.full_name}
                    {member.id === user?.id && <span className="text-[#E36414] ml-1">(vous)</span>}
                  </h3>
                  
                  <span className="inline-block text-xs px-3 py-1 rounded-full bg-[#0F4C5C] text-white mb-3">
                    Membre
                  </span>
                  
                  {member.bio && (
                    <p className="text-sm text-[#5C5C5C] line-clamp-2 mb-3">{member.bio}</p>
                  )}
                  
                  <div className="flex items-center justify-center gap-2 pt-3 border-t border-[#E5E0D8]">
                    <div className="text-center">
                      <p className="font-bold text-[#E36414]">{member.badges?.length || 0}</p>
                      <p className="text-xs text-[#5C5C5C]">expériences</p>
                    </div>
                  </div>

                  {member.id !== user?.id && (
                    <Link 
                      to="/ubuntoo/messages"
                      className="mt-4 flex items-center justify-center gap-2 text-sm text-[#0F4C5C] hover:text-[#E36414] transition-colors"
                    >
                      <MessageSquare size={16} />
                      Envoyer un message
                    </Link>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
