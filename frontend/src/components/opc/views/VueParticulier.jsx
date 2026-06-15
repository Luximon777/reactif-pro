import { KpiCard } from "../KpiCard";
import { Section, EmptyHint, Chip } from "../Section";
import { StatutBadge, TensionPill } from "../StatutBadge";
import { FicheMetier } from "../FicheMetier";
import { Briefcase, GraduationCap, Compass, TrendingUp, ListChecks, Activity, Sparkles } from "lucide-react";
import { OPC } from "@/constants/testIds";

export function VueParticulier({ data }) {
    const { profil, ecart_competences_prioritaires, offres_compatibles,
        formations_accessibles, trajectoires_conseillees, suivi_parcours, referentiel_metier } = data;

    return (
        <div className="space-y-6 animate-fade-in-up" data-testid={OPC.viewParticulier}>
            {data?.anonyme && (
                <div className="rounded-lg border border-blue-200 bg-blue-50/60 px-4 py-3 text-sm text-blue-900">
                    <strong>Mode exploration anonyme</strong> — aucun profil utilisateur ne correspond exactement à ce métier dans la base. Les recommandations ci-dessous sont construites depuis le référentiel vivant et le marché de l&apos;emploi. Crée un profil pour personnaliser l&apos;analyse.
                </div>
            )}
            {/* Header profil */}
            <div className="rounded-xl border border-slate-200 bg-white p-6">
                <div className="flex flex-wrap items-start justify-between gap-4">
                    <div>
                        <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-500">Métier visé</p>
                        <h2 className="font-display text-2xl font-bold tracking-tight text-navy mt-1">
                            {profil?.metier_vise || "—"}
                        </h2>
                        <p className="mt-1 text-sm text-slate-600">
                            {profil?.metier_exerce ? `Actuellement : ${profil.metier_exerce}` : "Aucun métier exercé renseigné"}
                            {profil?.annees_experience != null && ` · ${profil.annees_experience} ans d'expérience`}
                        </p>
                    </div>
                    {referentiel_metier && (
                        <div className="flex items-center gap-2">
                            <StatutBadge statut={referentiel_metier.statut} />
                            <TensionPill value={referentiel_metier.taux_tension_territorial} />
                        </div>
                    )}
                </div>
                {profil?.projet_reconversion && (
                    <p className="mt-4 border-t border-slate-100 pt-4 text-sm italic text-slate-600">
                        « {profil.projet_reconversion} »
                    </p>
                )}
            </div>

            {/* KPIs perso */}
            <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
                <KpiCard label="Compétences techniques" value={profil?.competences_techniques?.length || 0} icon={ListChecks} accent="text-brand-blue" />
                <KpiCard label="Offres compatibles" value={offres_compatibles?.length || 0} icon={Briefcase} accent="text-brand-green" />
                <KpiCard label="Formations accessibles" value={formations_accessibles?.length || 0} icon={GraduationCap} accent="text-brand-amber" />
                <KpiCard label="Trajectoires possibles" value={trajectoires_conseillees?.length || 0} icon={Compass} accent="text-brand-purple" />
            </div>

            {/* Écart compétences */}
            <Section title="Compétences à développer en priorité" icon={TrendingUp}>
                {ecart_competences_prioritaires?.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                        {ecart_competences_prioritaires.map((c, i) => (
                            <Chip key={i} tone="amber">{c}</Chip>
                        ))}
                    </div>
                ) : <EmptyHint>Aucun écart détecté avec le marché.</EmptyHint>}
            </Section>

            {/* Fiche métier détaillée (mission + capacités + savoirs-être) */}
            {profil?.metier_vise && <FicheMetier metierLabel={profil.metier_vise} />}

            {/* Trajectoires conseillées */}
            <Section title="Trajectoires professionnelles conseillées" icon={Compass}>
                {trajectoires_conseillees?.length > 0 ? (
                    <ul className="divide-y divide-slate-100">
                        {trajectoires_conseillees.map((t, i) => (
                            <li key={i} className="flex flex-wrap items-center justify-between gap-3 py-3">
                                <div className="min-w-0">
                                    <p className="text-sm font-medium text-ink">{t.intitule}</p>
                                    <p className="font-mono text-[11px] text-slate-500">{t.code_rome} · horizon {t.horizon}</p>
                                </div>
                                <div className="flex items-center gap-2">
                                    <StatutBadge statut={t.statut} />
                                    <TensionPill value={t.taux_tension} />
                                </div>
                            </li>
                        ))}
                    </ul>
                ) : <EmptyHint />}
            </Section>

            {/* Offres */}
            <Section title="Offres d'emploi compatibles" icon={Briefcase}>
                {offres_compatibles?.length > 0 ? (
                    <ul className="divide-y divide-slate-100">
                        {offres_compatibles.slice(0, 6).map((o, i) => (
                            <li key={i} className="py-3">
                                <div className="flex flex-wrap items-baseline justify-between gap-2">
                                    <p className="text-sm font-medium text-ink">{o.intitule_poste}</p>
                                    {o.salaire_min && (
                                        <p className="tabular text-xs text-slate-500">{o.salaire_min.toLocaleString("fr-FR")} – {o.salaire_max?.toLocaleString("fr-FR")} €</p>
                                    )}
                                </div>
                                <p className="text-xs text-slate-500 mt-0.5">
                                    {o.localisation} · {o.type_contrat?.toUpperCase()} · {o.secteur}
                                </p>
                                {o.mots_cles_emergents?.length > 0 && (
                                    <div className="mt-2 flex flex-wrap gap-1.5">
                                        {o.mots_cles_emergents.slice(0, 4).map((m, j) => (
                                            <Chip key={j} tone="violet">{m}</Chip>
                                        ))}
                                    </div>
                                )}
                            </li>
                        ))}
                    </ul>
                ) : <EmptyHint />}
            </Section>

            {/* Formations */}
            <Section title="Formations accessibles" icon={GraduationCap}>
                {formations_accessibles?.length > 0 ? (
                    <ul className="divide-y divide-slate-100">
                        {formations_accessibles.map((f, i) => (
                            <li key={i} className="py-3">
                                <div className="flex flex-wrap items-baseline justify-between gap-2">
                                    <p className="text-sm font-medium text-ink">{f.intitule}</p>
                                    {f.taux_insertion != null && (
                                        <p className="tabular text-xs text-emerald-700">{f.taux_insertion}% insertion</p>
                                    )}
                                </div>
                                <p className="text-xs text-slate-500">{f.organisme} · {f.duree_heures}h · {f.localisation}</p>
                                {f.financements_possibles?.length > 0 && (
                                    <div className="mt-2 flex flex-wrap gap-1.5">
                                        {f.financements_possibles.map((fp, j) => <Chip key={j} tone="emerald">{fp}</Chip>)}
                                    </div>
                                )}
                            </li>
                        ))}
                    </ul>
                ) : <EmptyHint />}
            </Section>

            {/* Suivi parcours */}
            {suivi_parcours && (
                <Section title="Suivi de parcours" icon={Activity}>
                    <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
                        <KpiCard label="Candidatures" value={suivi_parcours.candidatures_envoyees} accent="text-brand-blue" />
                        <KpiCard label="Entretiens" value={suivi_parcours.entretiens_obtenus} accent="text-brand-green" />
                        <KpiCard label="Emploi retrouvé" value={suivi_parcours.emploi_retrouve ? "Oui" : "En cours"} accent={suivi_parcours.emploi_retrouve ? "text-brand-green" : "text-brand-amber"} icon={Sparkles} />
                        <KpiCard label="Maintien 12 mois" value={suivi_parcours.maintien_12mois === true ? "Oui" : suivi_parcours.maintien_12mois === false ? "Non" : "—"} accent="text-brand-purple" />
                    </div>
                </Section>
            )}
        </div>
    );
}
