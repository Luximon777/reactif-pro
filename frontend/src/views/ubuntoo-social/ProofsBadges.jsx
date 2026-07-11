import { FileCheck2, CheckCircle2, Lock, Layers, Loader2 } from 'lucide-react';

export default function ProofsBadges({ data }) {
  if (!data) {
    return (
      <div className="ubuntoo-card p-6 mb-8 flex justify-center">
        <Loader2 className="animate-spin text-[#0F4C5C]" size={24} />
      </div>
    );
  }
  if (!data.proof_track) return null;

  const { proof_track, families } = data;
  const { count, tiers, next_tier, origins, diversity_earned, verified_earned } = proof_track;
  const maxTier = tiers[tiers.length - 1].threshold;
  const pct = Math.min(100, Math.round((count / (next_tier ? next_tier.threshold : maxTier)) * 100));

  return (
    <>
      {/* Piste 1 — Documenter ses compétences */}
      <div className="ubuntoo-card p-6 md:p-8 mb-8 animate-fade-in" data-testid="proof-track">
        <div className="flex items-center gap-3 mb-1">
          <div className="p-3 rounded-xl bg-[#E8F4F8]">
            <FileCheck2 size={22} className="text-[#0F4C5C]" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-[#1A1A1A]" style={{ fontFamily: 'Manrope, sans-serif' }}>
              Piste Preuves — Documenter mes compétences
            </h2>
            <p className="text-sm text-[#5C5C5C]">
              {count} preuve{count > 1 ? 's' : ''} validée{count > 1 ? 's' : ''} dans votre portefeuille RE'ACTIF PRO
              {next_tier && <> — prochain palier : <strong>{next_tier.name}</strong> ({count}/{next_tier.threshold})</>}
            </p>
          </div>
        </div>

        {/* Paliers */}
        <div className="mt-5 mb-6">
          <div className="h-2.5 rounded-full bg-[#F5F2EB] overflow-hidden mb-3">
            <div className="h-full rounded-full bg-gradient-to-r from-[#2A9D8F] to-[#0F4C5C] transition-all duration-700" style={{ width: `${pct}%` }} />
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
            {tiers.map((t) => (
              <div
                key={t.id}
                className={`rounded-xl p-3 text-center border-2 transition-all ${
                  t.earned ? 'bg-white border-[#2A9D8F] shadow-sm' : 'bg-[#F5F2EB] border-transparent opacity-60'
                }`}
                data-testid={`proof-tier-${t.threshold}`}
              >
                <span className="text-2xl block mb-1">{t.earned ? t.icon : <Lock size={18} className="mx-auto text-[#B0AA9E]" />}</span>
                <p className="text-xs font-semibold text-[#1A1A1A] leading-tight">{t.name}</p>
                <p className="text-[10px] text-[#5C5C5C]">{t.threshold} preuve{t.threshold > 1 ? 's' : ''}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Bonus diversité + vérification */}
        <div className="grid sm:grid-cols-2 gap-3 mb-5">
          <div className={`rounded-xl p-4 border-2 ${diversity_earned ? 'border-[#2A9D8F] bg-[#EAF8F6]' : 'border-[#E5E0D8] bg-[#F5F2EB]'}`} data-testid="badge-diversity">
            <div className="flex items-center gap-2">
              <span className="text-xl">🎯</span>
              <p className="font-semibold text-sm text-[#1A1A1A]">Compétences démontrées</p>
              {diversity_earned && <CheckCircle2 size={16} className="text-[#2A9D8F] ml-auto" />}
            </div>
            <p className="text-xs text-[#5C5C5C] mt-1">Preuves issues de plusieurs origines différentes</p>
          </div>
          <div className={`rounded-xl p-4 border-2 ${verified_earned ? 'border-[#2A9D8F] bg-[#EAF8F6]' : 'border-[#E5E0D8] bg-[#F5F2EB]'}`} data-testid="badge-verified">
            <div className="flex items-center gap-2">
              <span className="text-xl">✅</span>
              <p className="font-semibold text-sm text-[#1A1A1A]">Compétence vérifiée</p>
              {verified_earned && <CheckCircle2 size={16} className="text-[#2A9D8F] ml-auto" />}
            </div>
            <p className="text-xs text-[#5C5C5C] mt-1">Preuve confirmée par un tiers qualifié (employeur, formateur, certificateur)</p>
          </div>
        </div>

        {/* Origines des preuves */}
        <p className="text-xs font-bold uppercase tracking-wider text-[#5C5C5C] mb-2">Origines de mes preuves</p>
        <div className="flex flex-wrap gap-2">
          {origins.map((o) => (
            <span
              key={o.id}
              className={`px-3 py-1.5 rounded-full text-xs font-medium ${
                o.count > 0 ? 'bg-[#0F4C5C] text-white' : 'bg-[#F5F2EB] text-[#B0AA9E]'
              }`}
              data-testid={`origin-${o.id}`}
            >
              {o.label}{o.count > 0 ? ` · ${o.count}` : ''}
            </span>
          ))}
        </div>
        <p className="text-[11px] italic text-[#5C5C5C] mt-3">
          Chaque preuve déposée dans votre portefeuille RE'ACTIF PRO (méthode S.A.R.E., coffre-fort, certifications) alimente automatiquement cette piste.
        </p>
      </div>

      {/* Les 5 familles de badges */}
      <div className="ubuntoo-card p-6 md:p-8 mb-8 animate-fade-in" data-testid="badge-families">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-3 rounded-xl bg-[#FEF0E3]">
            <Layers size={22} className="text-[#E36414]" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-[#1A1A1A]" style={{ fontFamily: 'Manrope, sans-serif' }}>
              Les 5 familles de badges
            </h2>
            <p className="text-sm text-[#5C5C5C]">Tous vos badges se rattachent à cinq familles transversales</p>
          </div>
        </div>
        <div className="space-y-5">
          {families.map((f) => {
            const earned = f.badges.filter((b) => b.earned).length;
            return (
              <div key={f.id} data-testid={`family-${f.id}`}>
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-lg">{f.icon}</span>
                  <h3 className="font-semibold text-[#1A1A1A]">{f.name}</h3>
                  <span className="text-xs text-[#5C5C5C]">— {f.desc}</span>
                  <span className="ml-auto text-xs font-bold text-[#0F4C5C]">{earned}/{f.badges.length}</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {f.badges.map((b) => (
                    <div
                      key={b.id}
                      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                        b.earned ? 'bg-[#0F4C5C] text-white shadow-sm' : 'bg-[#F5F2EB] text-[#B0AA9E]'
                      }`}
                      title={b.description}
                      data-testid={`family-badge-${b.id}`}
                    >
                      <span>{b.icon}</span> {b.name}
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </>
  );
}
