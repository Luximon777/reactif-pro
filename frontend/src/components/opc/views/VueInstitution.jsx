import { KpiCard } from "../KpiCard";
import { Section, EmptyHint, Chip } from "../Section";
import { StatutBadge } from "../StatutBadge";
import { Users, Briefcase, GraduationCap, Activity, Map, Sparkles, BarChart3, AlertOctagon, Database } from "lucide-react";
import { OPC } from "@/constants/testIds";

export function VueInstitution({ data }) {
    const { kpis_macro, cartographie_tensions_par_statut, competences_emergentes_territoriales,
        signaux_marche_mots_cles, adequation_offre_demande_par_secteur,
        besoins_formation_non_couverts, sources_institutionnelles_integrees } = data;

    return (
        <div className="space-y-6 animate-fade-in-up" data-testid={OPC.viewInstitution}>
            {/* KPIs macro */}
            <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
                <KpiCard label="Profils plateforme" value={kpis_macro?.total_profils_plateforme} icon={Users} accent="text-brand-blue" />
                <KpiCard label="Offres analysées" value={kpis_macro?.total_offres_analysees} icon={Briefcase} accent="text-brand-green" />
                <KpiCard label="Référentiels vivants" value={kpis_macro?.total_referentiels_vivants} icon={GraduationCap} accent="text-brand-purple" />
                <KpiCard label="Emplois retrouvés" value={kpis_macro?.emplois_retrouves_total} icon={Activity} accent="text-brand-amber" />
            </div>

            {/* Cartographie tensions */}
            <Section title="Cartographie des métiers par statut" icon={Map}>
                {cartographie_tensions_par_statut?.length > 0 ? (
                    <ul className="space-y-2">
                        {cartographie_tensions_par_statut.map((t, i) => (
                            <li key={i} className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-slate-200 bg-slate-50/40 p-3">
                                <div className="flex items-center gap-3">
                                    <StatutBadge statut={t.statut} />
                                    <span className="tabular text-sm font-medium text-ink">{t.nombre_metiers} métier(s)</span>
                                </div>
                                <p className="flex-1 text-xs text-slate-500 sm:text-right">{t.exemples?.slice(0, 3).join(" · ")}</p>
                            </li>
                        ))}
                    </ul>
                ) : <EmptyHint />}
            </Section>

            {/* Compétences émergentes territoriales */}
            <Section title="Compétences émergentes territoriales" icon={Sparkles}>
                {competences_emergentes_territoriales?.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                        {competences_emergentes_territoriales.slice(0, 18).map((c, i) => (
                            <Chip key={i} tone="violet">
                                {c.competence} <span className="ml-1 tabular text-violet-500">·{c.nb_metiers_concernes}</span>
                            </Chip>
                        ))}
                    </div>
                ) : <EmptyHint />}
            </Section>

            {/* Signaux marché */}
            <Section title="Signaux faibles dans les offres (mots-clés émergents)" icon={BarChart3}>
                {signaux_marche_mots_cles?.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                        {signaux_marche_mots_cles.slice(0, 20).map((m, i) => (
                            <Chip key={i} tone="blue">
                                {m.mot_cle} <span className="ml-1 tabular text-blue-500">·{m.frequence}</span>
                            </Chip>
                        ))}
                    </div>
                ) : <EmptyHint />}
            </Section>

            {/* Adéquation offre/demande */}
            <Section title="Adéquation offre / demande par secteur" icon={BarChart3}>
                {adequation_offre_demande_par_secteur?.length > 0 ? (
                    <div className="overflow-hidden rounded-lg border border-slate-200">
                        <table className="min-w-full divide-y divide-slate-200 text-sm">
                            <thead className="bg-slate-50">
                                <tr>
                                    <th className="px-4 py-2.5 text-left text-[10px] font-bold uppercase tracking-[0.12em] text-slate-500">Secteur</th>
                                    <th className="px-4 py-2.5 text-right text-[10px] font-bold uppercase tracking-[0.12em] text-slate-500">Offres</th>
                                    <th className="px-4 py-2.5 text-right text-[10px] font-bold uppercase tracking-[0.12em] text-slate-500">Profils</th>
                                    <th className="px-4 py-2.5 text-right text-[10px] font-bold uppercase tracking-[0.12em] text-slate-500">Ratio</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100">
                                {adequation_offre_demande_par_secteur.map((s, i) => (
                                    <tr key={i}>
                                        <td className="px-4 py-2.5 text-slate-700 capitalize">{s.secteur || "—"}</td>
                                        <td className="px-4 py-2.5 text-right tabular text-slate-700">{s.nb_offres}</td>
                                        <td className="px-4 py-2.5 text-right tabular text-slate-700">{s.nb_profils_disponibles}</td>
                                        <td className="px-4 py-2.5 text-right tabular font-medium text-navy">
                                            {s.ratio_offres_profils != null ? `${s.ratio_offres_profils}x` : "—"}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : <EmptyHint />}
            </Section>

            {/* Besoins formation non couverts */}
            <Section title="Besoins de formation non couverts" icon={AlertOctagon}>
                {besoins_formation_non_couverts?.length > 0 ? (
                    <ul className="divide-y divide-slate-100">
                        {besoins_formation_non_couverts.slice(0, 10).map((b, i) => (
                            <li key={i} className="flex items-baseline justify-between gap-3 py-2.5">
                                <span className="text-sm text-ink">{b.competence}</span>
                                <div className="flex items-center gap-3">
                                    <span className="tabular text-xs text-slate-500">demande : {b.demande_marche}</span>
                                    <Chip tone="orange">Pas de formation</Chip>
                                </div>
                            </li>
                        ))}
                    </ul>
                ) : <EmptyHint>Toutes les compétences demandées sont couvertes par une formation.</EmptyHint>}
            </Section>

            {/* Sources institutionnelles */}
            {sources_institutionnelles_integrees?.length > 0 && (
                <Section title="Sources institutionnelles intégrées" icon={Database}>
                    <ul className="divide-y divide-slate-100">
                        {sources_institutionnelles_integrees.map((s, i) => (
                            <li key={i} className="flex items-baseline justify-between py-2">
                                <span className="text-sm text-ink font-mono">{s.source}</span>
                                <span className="tabular text-xs text-slate-500">{s.documents} document(s)</span>
                            </li>
                        ))}
                    </ul>
                </Section>
            )}
        </div>
    );
}
