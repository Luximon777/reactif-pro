import { useEffect, useState } from "react";
import { Section, Chip } from "./Section";
import { Briefcase, Wrench, Heart, Target, Sparkles, Globe, Users, CheckCircle2, Award } from "lucide-react";
import { OPC } from "@/constants/testIds";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export function FicheMetier({ metierLabel }) {
    const [fiche, setFiche] = useState(null);
    const [opcData, setOpcData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [notFound, setNotFound] = useState(false);

    useEffect(() => {
        let cancelled = false;
        const load = async () => {
            if (!metierLabel) {
                if (!cancelled) { setFiche(null); setOpcData(null); }
                return;
            }
            if (!cancelled) setLoading(true);
            try {
                const [ficheRes, opcRes] = await Promise.all([
                    fetch(`${BACKEND_URL}/api/opc/vue/metier-details?label=${encodeURIComponent(metierLabel)}`),
                    fetch(`${BACKEND_URL}/api/opc/fiche-metier/${encodeURIComponent(metierLabel)}`).catch(() => null),
                ]);
                if (cancelled) return;
                if (ficheRes.status === 404) {
                    setNotFound(true);
                    setFiche(null);
                } else {
                    const d = await ficheRes.json();
                    if (!cancelled) {
                        setFiche(d);
                        setNotFound(false);
                    }
                }
                if (opcRes && opcRes.ok) {
                    const opcJson = await opcRes.json();
                    if (!cancelled && opcJson.found) setOpcData(opcJson);
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

            {/* Compétences prouvées par les contributeurs OPC */}
            {opcData && Object.keys(opcData.competences || {}).length > 0 && (
                <div className="rounded-xl border-2 border-cyan-200 bg-gradient-to-br from-cyan-50/60 to-white p-5 space-y-4" data-testid="opc-contributions-section">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <Globe className="h-4 w-4 text-cyan-600" />
                            <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-cyan-800">
                                Compétences prouvées par les contributeurs OPC
                            </p>
                        </div>
                        <div className="flex items-center gap-1.5 text-[10px] text-cyan-700 bg-cyan-100 rounded-full px-2.5 py-1 font-semibold">
                            <Users className="h-3 w-3" />
                            {opcData.total_contributors} contributeur{opcData.total_contributors > 1 ? "s" : ""}
                        </div>
                    </div>
                    <p className="text-xs text-slate-600 leading-relaxed">
                        Ces compétences ont été illustrées par des professionnels avec la méthode <strong>S.A.R.E</strong> (Situation, Action, Résultat, Enseignement) et certifiées par un contrat de travail.
                    </p>
                    <div className="space-y-3">
                        {Object.entries(opcData.competences).map(([skill, info]) => (
                            <div key={skill} className="rounded-lg border border-cyan-100 bg-white p-4 space-y-2">
                                <div className="flex items-center gap-2">
                                    <Award className="h-4 w-4 text-amber-500" />
                                    <span className="text-sm font-bold text-slate-800">{skill}</span>
                                    <span className="text-[10px] bg-emerald-100 text-emerald-700 rounded-full px-2 py-0.5 font-semibold">
                                        {info.contributors_count} preuve{info.contributors_count > 1 ? "s" : ""} certifiée{info.contributors_count > 1 ? "s" : ""}
                                    </span>
                                </div>
                                {info.examples.slice(0, 3).map((ex, i) => (
                                    <div key={i} className="bg-slate-50 rounded-lg p-3 space-y-1.5 border border-slate-100">
                                        <p className="text-[10px] text-slate-400 font-medium">{ex.organization}</p>
                                        {ex.sare_situation && (
                                            <div className="flex gap-2">
                                                <span className="inline-flex items-center justify-center w-5 h-5 rounded bg-amber-100 text-[9px] font-black text-amber-800 shrink-0">S</span>
                                                <p className="text-xs text-slate-700 leading-relaxed">{ex.sare_situation}</p>
                                            </div>
                                        )}
                                        {ex.sare_action && (
                                            <div className="flex gap-2">
                                                <span className="inline-flex items-center justify-center w-5 h-5 rounded bg-amber-100 text-[9px] font-black text-amber-800 shrink-0">A</span>
                                                <p className="text-xs text-slate-700 leading-relaxed">{ex.sare_action}</p>
                                            </div>
                                        )}
                                        {ex.sare_resultat && (
                                            <div className="flex gap-2">
                                                <span className="inline-flex items-center justify-center w-5 h-5 rounded bg-amber-100 text-[9px] font-black text-amber-800 shrink-0">R</span>
                                                <p className="text-xs text-slate-700 leading-relaxed">{ex.sare_resultat}</p>
                                            </div>
                                        )}
                                        {ex.sare_enseignement && (
                                            <div className="flex gap-2">
                                                <span className="inline-flex items-center justify-center w-5 h-5 rounded bg-amber-100 text-[9px] font-black text-amber-800 shrink-0">E</span>
                                                <p className="text-xs text-slate-700 leading-relaxed">{ex.sare_enseignement}</p>
                                            </div>
                                        )}
                                        <div className="flex items-center gap-1 pt-1">
                                            <CheckCircle2 className="h-3 w-3 text-emerald-500" />
                                            <span className="text-[10px] text-emerald-600 font-medium">Certifié par contrat de travail</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ))}
                    </div>
                    {(opcData.organizations || []).length > 0 && (
                        <div className="flex flex-wrap gap-1.5 pt-1">
                            <span className="text-[10px] text-slate-500 font-medium">Organisations :</span>
                            {opcData.organizations.map((org, i) => (
                                <span key={i} className="text-[10px] bg-slate-100 text-slate-600 rounded-full px-2 py-0.5">{org}</span>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
