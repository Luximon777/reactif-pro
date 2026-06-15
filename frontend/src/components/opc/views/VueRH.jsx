import { KpiCard } from "../KpiCard";
import { Section, EmptyHint, Chip } from "../Section";
import { StatutBadge, TensionPill } from "../StatutBadge";
import { Building2, Users, Target, GraduationCap, AlertTriangle, MessageSquare, BadgeCheck } from "lucide-react";
import { OPC } from "@/constants/testIds";

export function VueRH({ data }) {
    const { entreprise, matching, referentiels_metiers_tension, formations_gepp_disponibles, retours_recruteurs_secteur } = data;

    return (
        <div className="space-y-6 animate-fade-in-up" data-testid={OPC.viewRh}>
            {/* Header entreprise */}
            <div className="rounded-xl border border-slate-200 bg-white p-6">
                <div className="flex flex-wrap items-start justify-between gap-4">
                    <div>
                        <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-500">Secteur</p>
                        <h2 className="font-display text-2xl font-bold tracking-tight text-navy mt-1 capitalize">
                            {entreprise?.secteur || "—"}
                        </h2>
                        <p className="mt-1 text-sm text-slate-600">
                            {entreprise?.taille && `Taille : ${entreprise.taille}`}
                            {entreprise?.metiers_en_tension?.length > 0 &&
                                ` · ${entreprise.metiers_en_tension.length} métier(s) en tension`}
                        </p>
                    </div>
                    <Building2 className="h-8 w-8 text-navy/40" strokeWidth={1.5} />
                </div>
                {entreprise?.besoins_gepp && (
                    <p className="mt-4 border-t border-slate-100 pt-4 text-sm italic text-slate-600">
                        « {entreprise.besoins_gepp} »
                    </p>
                )}
            </div>

            {/* KPIs */}
            <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
                <KpiCard label="Profils compatibles" value={matching?.profils_compatibles || 0} icon={Users} accent="text-brand-green" />
                <KpiCard label="Taux matching" value={`${matching?.taux_matching_pct || 0}%`} icon={Target} accent="text-navy" />
                <KpiCard label="Formations GEPP" value={formations_gepp_disponibles?.length || 0} icon={GraduationCap} accent="text-brand-purple" />
                <KpiCard label="Retours recruteurs" value={retours_recruteurs_secteur?.length || 0} icon={MessageSquare} accent="text-brand-amber" />
            </div>

            {/* Compétences manquantes & besoins recrutement */}
            <div className="grid gap-6 md:grid-cols-2">
                <Section title="Compétences manquantes identifiées" icon={AlertTriangle}>
                    {entreprise?.competences_manquantes?.length > 0 ? (
                        <div className="flex flex-wrap gap-2">
                            {entreprise.competences_manquantes.map((c, i) => (
                                <Chip key={i} tone="orange">{c}</Chip>
                            ))}
                        </div>
                    ) : <EmptyHint />}
                </Section>

                <Section title="Besoins de recrutement" icon={Target}>
                    {entreprise?.besoins_recrutement?.length > 0 ? (
                        <ul className="divide-y divide-slate-100">
                            {entreprise.besoins_recrutement.map((b, i) => (
                                <li key={i} className="flex items-baseline justify-between py-2">
                                    <span className="text-sm text-ink">{b.metier}</span>
                                    <span className="tabular text-xs text-slate-500">
                                        {b.nb_postes} poste(s) · {b.horizon_mois} mois
                                    </span>
                                </li>
                            ))}
                        </ul>
                    ) : <EmptyHint />}
                </Section>
            </div>

            {/* Référentiels métiers tension */}
            <Section title="Métiers en tension dans votre secteur" icon={AlertTriangle}>
                {referentiels_metiers_tension?.length > 0 ? (
                    <ul className="space-y-3">
                        {referentiels_metiers_tension.map((r, i) => (
                            <li key={i} className="rounded-lg border border-slate-200 bg-slate-50/40 p-3">
                                <div className="flex flex-wrap items-center justify-between gap-2">
                                    <span className="text-sm font-medium text-ink">{r.intitule_metier}</span>
                                    <div className="flex items-center gap-2">
                                        <StatutBadge statut={r.statut} />
                                        <TensionPill value={r.taux_tension_territorial} />
                                    </div>
                                </div>
                                {r.competences_emergentes?.length > 0 && (
                                    <div className="mt-2 flex flex-wrap gap-1.5">
                                        {r.competences_emergentes.slice(0, 5).map((c, j) => (
                                            <Chip key={j} tone="violet">{c}</Chip>
                                        ))}
                                    </div>
                                )}
                            </li>
                        ))}
                    </ul>
                ) : <EmptyHint />}
            </Section>

            {/* Profils disponibles */}
            <Section title="Profils disponibles vérifiés" icon={Users}>
                {matching?.profils?.length > 0 ? (
                    <ul className="divide-y divide-slate-100">
                        {matching.profils.slice(0, 8).map((p, i) => (
                            <li key={i} className="py-3">
                                <div className="flex items-baseline justify-between gap-2">
                                    <span className="text-sm font-medium text-ink">
                                        {p.metier_vise}
                                        {p.annees_experience != null && (
                                            <span className="text-xs text-slate-500 font-normal"> · {p.annees_experience} ans exp.</span>
                                        )}
                                    </span>
                                    <span className="font-mono text-[11px] text-slate-400">{p.user_id}</span>
                                </div>
                                {p.soft_skills_prouves?.length > 0 && (
                                    <div className="mt-1.5 flex flex-wrap gap-1.5">
                                        {p.soft_skills_prouves.slice(0, 4).map((s, j) => (
                                            <Chip key={j} tone="emerald"><BadgeCheck className="h-3 w-3 mr-1" />{s}</Chip>
                                        ))}
                                    </div>
                                )}
                            </li>
                        ))}
                    </ul>
                ) : <EmptyHint>Aucun profil compatible pour le moment.</EmptyHint>}
            </Section>

            {/* Formations GEPP */}
            {formations_gepp_disponibles?.length > 0 && (
                <Section title="Formations GEPP disponibles" icon={GraduationCap}>
                    <ul className="divide-y divide-slate-100">
                        {formations_gepp_disponibles.map((f, i) => (
                            <li key={i} className="py-3">
                                <div className="flex flex-wrap items-baseline justify-between gap-2">
                                    <p className="text-sm font-medium text-ink">{f.intitule}</p>
                                    <p className="tabular text-xs text-slate-500">{f.duree_heures}h · {f.organisme}</p>
                                </div>
                                {f.blocs_competences?.length > 0 && (
                                    <div className="mt-1.5 flex flex-wrap gap-1.5">
                                        {f.blocs_competences.slice(0, 6).map((b, j) => (
                                            <Chip key={j}>{b}</Chip>
                                        ))}
                                    </div>
                                )}
                            </li>
                        ))}
                    </ul>
                </Section>
            )}

            {/* Retours recruteurs */}
            {retours_recruteurs_secteur?.length > 0 && (
                <Section title="Retours recruteurs du secteur" icon={MessageSquare}>
                    <div className="space-y-2">
                        {retours_recruteurs_secteur.map((r, i) => (
                            <blockquote
                                key={i}
                                className={`border-l-2 px-3 py-2 text-sm italic text-slate-700 ${
                                    r.sentiment === "positif" ? "border-emerald-400 bg-emerald-50/50"
                                    : r.sentiment === "negatif" ? "border-orange-400 bg-orange-50/50"
                                    : "border-slate-300 bg-slate-50/50"
                                }`}
                            >
                                « {r.observation} »
                            </blockquote>
                        ))}
                    </div>
                </Section>
            )}
        </div>
    );
}
