import { useState, useEffect } from 'react';
import { useAuth } from './UbuntooSocialContext';
import { badgesApi, usersApi, progressionApi } from './api';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';
import {
  Award,
  Calendar,
  Loader2,
  Heart,
  Users,
  Home,
  MapPin,
  Briefcase,
  Target,
  Clock,
  Languages,
  Pencil,
  Save,
  X
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { fr } from 'date-fns/locale';
import Progression from './Progression';
import ProofsBadges from './ProofsBadges';

const toList = (str) => str.split(',').map((s) => s.trim()).filter(Boolean);

export default function Profile() {
  const { user, refreshUser } = useAuth();
  const [badges, setBadges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState(null);
  const [progression, setProgression] = useState(null);

  const loadProgression = async () => {
    try {
      const res = await progressionApi.get();
      setProgression(res.data);
    } catch { /* ignore */ }
  };

  useEffect(() => {
    fetchBadges();
    loadProgression();
  }, []);

  const fetchBadges = async () => {
    try {
      const response = await badgesApi.getAll();
      setBadges(response.data);
    } catch (error) {
      console.error('Failed to fetch badges');
    } finally {
      setLoading(false);
    }
  };

  const startEdit = () => {
    setForm({
      full_name: user?.full_name || '',
      bio: user?.bio || '',
      location: user?.location || '',
      sector: user?.sector || '',
      jobs_sought: (user?.jobs_sought || []).join(', '),
      skills: (user?.skills || []).join(', '),
      availability: user?.availability || '',
      languages: (user?.languages || []).join(', '),
    });
    setEditing(true);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await usersApi.updateProfile({
        full_name: form.full_name,
        bio: form.bio,
        location: form.location,
        sector: form.sector,
        jobs_sought: toList(form.jobs_sought),
        skills: toList(form.skills),
        availability: form.availability,
        languages: toList(form.languages),
      });
      await refreshUser();
      await loadProgression();
      setEditing(false);
      toast.success('Profil mis à jour !');
    } catch (error) {
      toast.error('Erreur lors de la mise à jour');
    } finally {
      setSaving(false);
    }
  };

  const earnedBadgesCount = user?.badges?.length || 0;
  const totalBadges = badges.length;

  const Chips = ({ items }) => (
    <div className="flex flex-wrap gap-2">
      {items.map((it, i) => (
        <span key={i} className="px-3 py-1 rounded-full bg-[#F5F2EB] text-[#0F4C5C] text-sm font-medium">
          {it}
        </span>
      ))}
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-[#FDFBF7] pt-20 flex items-center justify-center">
        <Loader2 className="animate-spin text-[#0F4C5C]" size={32} />
      </div>
    );
  }

  const infoRows = [
    { icon: MapPin, label: 'Localisation', value: user?.location },
    { icon: Briefcase, label: 'Secteur professionnel', value: user?.sector },
    { icon: Clock, label: 'Disponibilités', value: user?.availability },
  ].filter((r) => r.value);

  return (
    <div className="min-h-screen bg-[#FDFBF7] pt-20">
      <div className="container-main py-8">
        <div className="max-w-4xl mx-auto">
          {/* Profile Header */}
          <div className="ubuntoo-card p-8 mb-8 animate-fade-in">
            <div className="flex flex-col md:flex-row items-center md:items-start gap-6">
              <Avatar className="h-28 w-28 border-4 border-[#E36414]">
                <AvatarFallback className="bg-[#0F4C5C] text-white text-4xl">
                  {user?.full_name?.charAt(0).toUpperCase()}
                </AvatarFallback>
              </Avatar>

              <div className="flex-1 text-center md:text-left w-full">
                <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-3">
                  <div>
                    <h1 className="text-3xl font-bold text-[#1A1A1A] mb-2" style={{ fontFamily: 'Manrope, sans-serif' }}>
                      {user?.full_name}
                    </h1>
                    <p className="text-[#5C5C5C] mb-2">{user?.email}</p>
                  </div>
                  {!editing && (
                    <Button onClick={startEdit} className="btn-secondary shrink-0" data-testid="edit-profile-button">
                      <Pencil size={16} className="mr-2" /> Modifier mon profil
                    </Button>
                  )}
                </div>

                {!editing && user?.bio && <p className="text-[#5C5C5C] mb-4 max-w-xl italic">"{user?.bio}"</p>}

                {!editing && (
                  <>
                    {infoRows.length > 0 && (
                      <div className="grid sm:grid-cols-2 gap-2 mb-4 mt-3">
                        {infoRows.map((r, i) => (
                          <div key={i} className="flex items-center gap-2 text-sm text-[#5C5C5C]">
                            <r.icon size={16} className="text-[#0F4C5C]" />
                            <span className="font-medium text-[#1A1A1A]">{r.label} :</span> {r.value}
                          </div>
                        ))}
                      </div>
                    )}
                    {user?.jobs_sought?.length > 0 && (
                      <div className="mb-3">
                        <div className="flex items-center gap-2 text-sm font-medium text-[#1A1A1A] mb-1">
                          <Target size={16} className="text-[#0F4C5C]" /> Métiers recherchés
                        </div>
                        <Chips items={user.jobs_sought} />
                      </div>
                    )}
                    {user?.skills?.length > 0 && (
                      <div className="mb-3">
                        <div className="flex items-center gap-2 text-sm font-medium text-[#1A1A1A] mb-1">
                          <Award size={16} className="text-[#0F4C5C]" /> Compétences
                        </div>
                        <Chips items={user.skills} />
                      </div>
                    )}
                    {user?.languages?.length > 0 && (
                      <div className="mb-3">
                        <div className="flex items-center gap-2 text-sm font-medium text-[#1A1A1A] mb-1">
                          <Languages size={16} className="text-[#0F4C5C]" /> Langues parlées
                        </div>
                        <Chips items={user.languages} />
                      </div>
                    )}
                    <div className="flex items-center justify-center md:justify-start gap-2 text-sm text-[#5C5C5C] mt-2">
                      <Calendar size={16} />
                      Membre depuis {formatDistanceToNow(new Date(user?.created_at), { locale: fr })}
                    </div>
                  </>
                )}
              </div>
            </div>

            {/* Edit form */}
            {editing && form && (
              <div className="mt-6 pt-6 border-t border-[#E5E0D8] space-y-4 animate-fade-in" data-testid="edit-profile-form">
                <div className="grid sm:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Nom / Pseudonyme</Label>
                    <Input value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} className="ubuntoo-input" data-testid="edit-full-name" />
                  </div>
                  <div className="space-y-2">
                    <Label>Localisation (ville / région)</Label>
                    <Input value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} className="ubuntoo-input" data-testid="edit-location" />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Présentation (bio)</Label>
                  <Textarea value={form.bio} onChange={(e) => setForm({ ...form, bio: e.target.value })} className="ubuntoo-input min-h-[80px] resize-none" data-testid="edit-bio" />
                </div>
                <div className="grid sm:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Secteur professionnel</Label>
                    <Input value={form.sector} onChange={(e) => setForm({ ...form, sector: e.target.value })} className="ubuntoo-input" data-testid="edit-sector" />
                  </div>
                  <div className="space-y-2">
                    <Label>Disponibilités</Label>
                    <Input value={form.availability} onChange={(e) => setForm({ ...form, availability: e.target.value })} className="ubuntoo-input" placeholder="ex. Soirs et week-ends" data-testid="edit-availability" />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Métiers recherchés <span className="text-[#5C5C5C] font-normal">(séparés par des virgules)</span></Label>
                  <Input value={form.jobs_sought} onChange={(e) => setForm({ ...form, jobs_sought: e.target.value })} className="ubuntoo-input" data-testid="edit-jobs" />
                </div>
                <div className="space-y-2">
                  <Label>Compétences <span className="text-[#5C5C5C] font-normal">(séparées par des virgules)</span></Label>
                  <Input value={form.skills} onChange={(e) => setForm({ ...form, skills: e.target.value })} className="ubuntoo-input" data-testid="edit-skills" />
                </div>
                <div className="space-y-2">
                  <Label>Langues parlées <span className="text-[#5C5C5C] font-normal">(séparées par des virgules)</span></Label>
                  <Input value={form.languages} onChange={(e) => setForm({ ...form, languages: e.target.value })} className="ubuntoo-input" data-testid="edit-languages" />
                </div>
                <div className="flex gap-3 justify-end">
                  <Button variant="ghost" onClick={() => setEditing(false)} disabled={saving} data-testid="cancel-edit-button">
                    <X size={16} className="mr-2" /> Annuler
                  </Button>
                  <Button onClick={handleSave} disabled={saving} className="btn-primary" data-testid="save-profile-button">
                    {saving ? <Loader2 className="animate-spin mr-2" size={16} /> : <Save size={16} className="mr-2" />}
                    Enregistrer
                  </Button>
                </div>
              </div>
            )}
          </div>

          {/* Parcours d'évolution Ubuntoo */}
          <Progression data={progression} reload={loadProgression} />

          {/* Piste Preuves + 5 familles de badges */}
          <ProofsBadges data={progression} />

          {/* Expériences vécues - Résumé */}
          <div className="ubuntoo-card p-6 mb-8 animate-fade-in stagger-1">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-3 rounded-xl bg-[#FEF0E3]">
                <Award size={24} className="text-[#E36414]" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-[#1A1A1A]" style={{ fontFamily: 'Manrope, sans-serif' }}>
                  Mes expériences
                </h2>
                <p className="text-sm text-[#5C5C5C]">
                  {earnedBadgesCount} expérience{earnedBadgesCount > 1 ? 's' : ''} vécue{earnedBadgesCount > 1 ? 's' : ''} sur {totalBadges}
                </p>
              </div>
            </div>
            <div className="flex flex-wrap gap-3">
              {badges
                .filter((badge) => user?.badges?.includes(badge.id))
                .map((badge) => (
                  <div key={badge.id} className="flex items-center gap-2 px-4 py-2 rounded-full bg-[#0F4C5C] text-white">
                    <span className="text-lg">{badge.icon}</span>
                    <span className="font-medium text-sm">{badge.name}</span>
                  </div>
                ))}
            </div>
          </div>

          {/* Badges par catégorie — remplacé par les 5 familles de badges (ProofsBadges) */}

          <div className="ubuntoo-card p-8 text-center bg-gradient-to-br from-[#0F4C5C] to-[#0A3844] text-white animate-fade-in">
            <p className="text-xl font-medium mb-2" style={{ fontFamily: 'Manrope, sans-serif' }}>
              "Je suis parce que nous sommes"
            </p>
            <p className="text-white/70 text-sm">
              Chaque expérience compte. Continuez à partager et à grandir avec la communauté.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
