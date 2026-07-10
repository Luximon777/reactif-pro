import { useState } from 'react';
import { Link } from 'react-router-dom';
import { searchApi } from './api';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { toast } from 'sonner';
import { Search as SearchIcon, Loader2, Users, MessageCircle, MapPin, Briefcase } from 'lucide-react';

export default function Search() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [results, setResults] = useState({ users: [], posts: [], groups: [] });

  const handleSearch = async (e) => {
    e?.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    try {
      const res = await searchApi.search(query.trim());
      setResults(res.data);
      setSearched(true);
    } catch (error) {
      toast.error('Erreur lors de la recherche');
    } finally {
      setLoading(false);
    }
  };

  const total = results.users.length + results.posts.length + results.groups.length;

  return (
    <div className="min-h-screen bg-[#FDFBF7] pt-20">
      <div className="container-main py-8">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-3xl font-bold text-[#1A1A1A] mb-2" style={{ fontFamily: 'Manrope, sans-serif' }}>
            Rechercher
          </h1>
          <p className="text-[#5C5C5C] mb-6">Trouvez des membres, des publications et des groupes.</p>

          <form onSubmit={handleSearch} className="flex gap-2 mb-8">
            <div className="relative flex-1">
              <SearchIcon size={20} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#5C5C5C] pointer-events-none" />
              <Input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Métier, compétence, ville, nom, secteur..."
                className="ubuntoo-input pl-12"
                data-testid="search-input"
              />
            </div>
            <Button type="submit" className="btn-primary" disabled={loading} data-testid="search-submit">
              {loading ? <Loader2 className="animate-spin" size={18} /> : 'Rechercher'}
            </Button>
          </form>

          {loading ? (
            <div className="flex justify-center py-12">
              <Loader2 className="animate-spin text-[#0F4C5C]" size={32} />
            </div>
          ) : searched && total === 0 ? (
            <div className="ubuntoo-card p-12 text-center" data-testid="no-results">
              <SearchIcon size={48} className="mx-auto text-[#E5E0D8] mb-4" />
              <p className="text-[#5C5C5C]">Aucun résultat pour « {query} »</p>
            </div>
          ) : searched ? (
            <div className="space-y-8">
              {/* Members */}
              {results.users.length > 0 && (
                <section data-testid="results-users">
                  <div className="flex items-center gap-2 mb-3 text-[#0F4C5C] font-semibold">
                    <Users size={18} /> Membres ({results.users.length})
                  </div>
                  <div className="space-y-3">
                    {results.users.map((u) => (
                      <div key={u.id} className="ubuntoo-card p-4 flex items-center gap-4" data-testid={`result-user-${u.id}`}>
                        <Avatar className="h-11 w-11 border-2 border-[#E36414]">
                          <AvatarFallback className="bg-[#0F4C5C] text-white font-semibold">
                            {u.full_name?.charAt(0).toUpperCase()}
                          </AvatarFallback>
                        </Avatar>
                        <div className="flex-1">
                          <p className="font-semibold text-[#1A1A1A]">{u.full_name}</p>
                          <div className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-[#5C5C5C]">
                            {u.sector && <span className="flex items-center gap-1"><Briefcase size={14} /> {u.sector}</span>}
                            {u.location && <span className="flex items-center gap-1"><MapPin size={14} /> {u.location}</span>}
                          </div>
                          {u.bio && <p className="text-sm text-[#5C5C5C] mt-1 italic line-clamp-1">"{u.bio}"</p>}
                        </div>
                      </div>
                    ))}
                  </div>
                </section>
              )}

              {/* Groups */}
              {results.groups.length > 0 && (
                <section data-testid="results-groups">
                  <div className="flex items-center gap-2 mb-3 text-[#0F4C5C] font-semibold">
                    <Users size={18} /> Groupes ({results.groups.length})
                  </div>
                  <div className="space-y-3">
                    {results.groups.map((g) => (
                      <Link key={g.id} to={`/ubuntoo/groups/${g.id}`} className="block" data-testid={`result-group-${g.id}`}>
                        <div className="ubuntoo-card p-4 hover:border-[#0F4C5C] transition-colors">
                          <div className="flex items-center justify-between">
                            <p className="font-semibold text-[#1A1A1A]">{g.name}</p>
                            <span className="text-xs text-[#5C5C5C]">{g.members_count} membre{g.members_count > 1 ? 's' : ''}</span>
                          </div>
                          <p className="text-sm text-[#5C5C5C] mt-1 line-clamp-2">{g.description}</p>
                        </div>
                      </Link>
                    ))}
                  </div>
                </section>
              )}

              {/* Posts */}
              {results.posts.length > 0 && (
                <section data-testid="results-posts">
                  <div className="flex items-center gap-2 mb-3 text-[#0F4C5C] font-semibold">
                    <MessageCircle size={18} /> Publications ({results.posts.length})
                  </div>
                  <div className="space-y-3">
                    {results.posts.map((p) => (
                      <div key={p.id} className="ubuntoo-card p-4" data-testid={`result-post-${p.id}`}>
                        <p className="text-sm font-medium text-[#0F4C5C] mb-1">{p.author_name}</p>
                        <p className="text-[#1A1A1A] line-clamp-3">{p.content}</p>
                      </div>
                    ))}
                  </div>
                </section>
              )}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
