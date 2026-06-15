import { useEffect, useState } from "react";
import { Section, Chip } from "./Section";
import { Briefcase, Wrench, Heart, Target, Sparkles } from "lucide-react";
import { OPC } from "@/constants/testIds";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export function FicheMetier({ metierLabel }) {
    const [fiche, setFiche] = useState(null);
    const [loading, setLoading] = useState(false);
    const [notFound, setNotFound] = useState(false);

    useEffect(() => {
        let cancelled = false;
        const load = async () => {
            if (!metierLabel) {
                if (!cancelled) setFiche(null);
                return;
            }
            if (!cancelled) setLoading(true);
            try {
                const r = await fetch(
                    `${BACKEND_URL}/api/opc/vue/metier-details?label=${encodeURIComponent(metierLabel)}`
                );
                if (cancelled) return;
                if (r.status === 404) {
                    setNotFound(true);
                    setFiche(null);
                } else {
                    const d = await r.json();
                    if (!cancelled) {
                        setFiche(d);
                        setNotFound(false);
                    }
                }
            } catch {
                if (!cancelled) setFiche(null);
            } finally {
                if (!cancelled) setLoading(false);
            }
        };
        load();
        return () => { cancelled = true; };
    }, [metierLabel]);

    if (!metierLabel) return null;
    if (loading) {
        return (
            <div className="rounded-xl border border-slate-200 bg-white p-5 animate-pulse">
                <div className="h-3 w-1/3 rounded bg-slate-100 mb-3" />
                <div className="h-3 w-full rounded bg-slate-100 mb-2" />
                <div className="h-3 w-5/6 rounded bg-slate-100" />
            </div>
        );
    }
    if (notFound) {
        return (
            <div className="rounded-lg border border-amber-200 bg-amber-50/60 px-4 py-3 text-sm text-amber-900">
                Aucune fiche métier détaillée disponible pour <strong>{metierLabel}</strong>.
                Capacités génériques fournies par défaut.
            </div>
        );
    }
    if (!fiche) return null;

    return (
        <div className="space-y-4" data-testid={OPC.ficheMetier}>
            {/* En-tête mission */}
            <div className="rounded-xl border border-navy/10 bg-gradient-to-br from-slate-50 to-white p-5">
                <div className="flex flex-wrap items-baseline gap-2 mb-2">
                    <Briefcase className="h-4 w-4 text-navy" />
                    <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-navy">
                        Fiche métier · {fiche.filiere.code}
                    </p>
                    <p className="text-[11px] text-slate-500">
                        {fiche.filiere.label} · {fiche.secteur.label}
                    </p>
                </div>
                <h3 className="font-display text-lg font-bold tracking-tight text-ink">
                    {fiche.label}
                </h3>
                {fiche.mission && (
                    <p className="mt-2 text-sm leading-relaxed text-slate-700">
                        {fiche.mission}
                    </p>
                )}
            </div>

            <div className="grid gap-4 md:grid-cols-2">
                {/* Capacités techniques */}
                <Section title="Capacités techniques" icon={Wrench}>
                    <ul className="space-y-2">
                        {fiche.capacites_techniques.map((c, i) => (
                            <li key={i} className="flex gap-2 text-sm leading-relaxed text-slate-700">
                                <span className="mt-2 inline-block h-1 w-1 flex-shrink-0 rounded-full bg-brand-blue" />
                                <span>{c}</span>
                            </li>
                        ))}
                    </ul>
                </Section>

                {/* Capacités professionnelles */}
                <Section title="Capacités professionnelles" icon={Target}>
                    <ul className="space-y-2">
                        {fiche.capacites_professionnelles.map((c, i) => (
                            <li key={i} className="flex gap-2 text-sm leading-relaxed text-slate-700">
                                <span className="mt-2 inline-block h-1 w-1 flex-shrink-0 rounded-full bg-brand-green" />
                                <span>{c}</span>
                            </li>
                        ))}
                    </ul>
                </Section>
            </div>

            {/* Savoirs-être */}
            <Section title="Savoirs-être professionnels" icon={Heart}>
                <div className="mb-3 flex flex-wrap gap-2">
                    {fiche.savoirs_etre.map((s, i) => (
                        <Chip key={i} tone="violet">{s}</Chip>
                    ))}
                </div>
                {Object.keys(fiche.qualites_humaines || {}).length > 0 && (
                    <div className="mt-3 border-t border-slate-100 pt-3">
                        <div className="flex items-center gap-1.5 mb-2">
                            <Sparkles className="h-3.5 w-3.5 text-violet-500" />
                            <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-500">
                                Qualités humaines associées
                            </p>
                        </div>
                        <ul className="space-y-2">
                            {Object.entries(fiche.qualites_humaines).map(([se, desc], i) => (
                                <li key={i} className="text-xs leading-relaxed text-slate-600">
                                    <strong className="text-ink">{se}</strong> — {desc}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </Section>
        </div>
    );
}
