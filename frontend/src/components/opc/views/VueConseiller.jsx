import { KpiCard } from "../KpiCard";
import { Section, EmptyHint, Chip } from "../Section";
import { StatutBadge, TensionPill } from "../StatutBadge";
import { Users, Briefcase, Award, GraduationCap, Flame, Activity, LifeBuoy, BarChart3 } from "lucide-react";
import { OPC } from "@/constants/testIds";

export function VueConseiller({ data }) {
    const { kpis_territoire, competences_les_plus_demandees, metiers_en_tension,
        observations_terrain_recentes, profils_en_difficulte, efficacite_accompagnements } = data;

    return (
        <div className="space-y-6 animate-fade-in-up" data-testid={OPC.viewConseiller}>
            {/* KPIs */}
            <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
                <KpiCard label="Profils actifs" value={kpis_territoire?.profils_actifs} icon={Users} accent="text-brand-blue" />
                <KpiCard label="Offres actives" value={kpis_territoire?.offres_actives} icon={Briefcase} accent="text-brand-green" />
                <KpiCard label="Retour à l'emploi" value={`${kpis_territoire?.taux_retour_emploi_pct || 0}%`} icon={Award} accent="text-navy" />
                <KpiCard label="Formations dispo." value={kpis_territoire?.formations_disponibles} icon={GraduationCap} accent="text-brand-purple" />
            </div>

            {/* Efficacité accompagnement */}
            {efficacite_accompagnements?.total_parcours_suivis > 0 && (
                <Section title="Efficacité des accompagnements" icon={BarChart3}>
                    <div className="grid grid-cols-3 gap-4">
                        <KpiCard label="Maintien 3 mois" value={`${efficacite_accompagnements.maintien_3mois_pct}%`} accent="text-brand-blue" />
                        <KpiCard label="Maintien 6 mois" value={`${efficacite_accompagnements.maintien_6mois_pct}%`} accent="text-brand-green" />
                        <KpiCard label="Maintien 12 mois" value={`${efficacite_accompagnements.maintien_12mois_pct}%`} accent="text-brand-purple" />
                    </div>
                    <p className="mt-3 text-xs text-slate-500">
                        Sur {efficacite_accompagnements.total_parcours_suivis} parcours suivis.
                    </p>
                </Section>
            )}

            {/* Métiers en tension */}
            <Section title="Métiers en tension sur le territoire" icon={Flame}>
                {metiers_en_tension?.length > 0 ? (
                    <ul className="divide-y divide-slate-100">
                        {metiers_en_tension.map((m, i) => (
                            <li key={i} className="flex flex-wrap items-center justify-between gap-3 py-3">
                                <div className="min-w-0">
                                    <p className="text-sm font-medium text-ink truncate">{m.intitule}</p>
                                    <p className="font-mono text-[11px] text-slate-500">{m.code_rome}</p>
                                </div>
                                <div className="flex items-center gap-2">
                                    <StatutBadge statut={m.statut} />
                                    <TensionPill value={m.taux_tension} />
                                </div>
                                {m.competences_emergentes?.length > 0 && (
                                    <div className="flex w-full flex-wrap gap-1.5">
                                        {m.competences_emergentes.map((c, j) => (
                                            <Chip key={j} tone="violet">{c}</Chip>
                                        ))}
                                    </div>
                                )}
                            </li>
                        ))}
                    </ul>
                ) : <EmptyHint />}
            </Section>

            {/* Compétences les plus demandées */}
            <Section title="Compétences les plus demandées" icon={BarChart3}>
                {competences_les_plus_demandees?.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                        {competences_les_plus_demandees.slice(0, 18).map((c, i) => (
                            <Chip key={i} tone="blue">
                                {c.competence} <span className="ml-1 tabular text-slate-500">·{c.occurrences}</span>
                            </Chip>
                        ))}
                    </div>
                ) : <EmptyHint />}
            </Section>

            {/* Observations terrain */}
            <Section title="Observations terrain récentes" icon={Activity}>
                {observations_terrain_recentes?.length > 0 ? (
                    <ul className="space-y-2.5">
                        {observations_terrain_recentes.slice(0, 6).map((t, i) => (
                            <li key={i} className={`rounded-lg border p-3 ${
                                t.sentiment === "positif" ? "border-emerald-200 bg-emerald-50/40"
                                : t.sentiment === "negatif" ? "border-orange-200 bg-orange-50/40"
                                : "border-slate-200 bg-slate-50/40"
                            }`}>
                                <p className="text-xs text-slate-500">
                                    <span className="font-medium uppercase tracking-wide">{t.type_source?.replace(/_/g, " ")}</span>
                                    {t.metier && ` · ${t.metier}`}
                                </p>
                                <p className="mt-1 text-sm text-slate-700">« {t.observation} »</p>
                                {t.competences?.length > 0 && (
                                    <div className="mt-2 flex flex-wrap gap-1.5">
                                        {t.competences.slice(0, 5).map((c, j) => <Chip key={j}>{c}</Chip>)}
                                    </div>
                                )}
                            </li>
                        ))}
                    </ul>
                ) : <EmptyHint />}
            </Section>

            {/* Profils en difficulté */}
            <Section title="Profils nécessitant un appui renforcé" icon={LifeBuoy}>
                {profils_en_difficulte?.length > 0 ? (
                    <ul className="divide-y divide-slate-100">
                        {profils_en_difficulte.slice(0, 10).map((p, i) => (
                            <li key={i} className="py-3">
                                <div className="flex items-baseline justify-between gap-2">
                                    <p className="text-sm font-medium text-ink">{p.metier_vise || "—"}</p>
                                    <p className="font-mono text-[11px] text-slate-400">{p.user_id}</p>
                                </div>
                                {p.freins?.length > 0 && (
                                    <div className="mt-1.5 flex flex-wrap gap-1.5">
                                        {p.freins.map((f, j) => <Chip key={j} tone="orange">{f}</Chip>)}
                                    </div>
                                )}
                            </li>
                        ))}
                    </ul>
                ) : <EmptyHint>Aucun profil signalé en difficulté.</EmptyHint>}
            </Section>
        </div>
    );
}
