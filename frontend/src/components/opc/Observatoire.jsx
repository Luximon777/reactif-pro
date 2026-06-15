import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
    RotateCw, Users, Building2, Handshake, Globe2, Sparkles, ShieldCheck, MapPin,
    Briefcase, GraduationCap, Activity, LogIn, LogOut
} from "lucide-react";
import { useOPCView, useOPCStats, useOPCConfiance, useOPCSynthese, PUBLIC_TYPES } from "@/hooks/useOPC";
import { OPC } from "@/constants/testIds";
import { KpiCard } from "./KpiCard";
import { RechercheMetier } from "./RechercheMetier";
import { FranceTravailPanel } from "./FranceTravailPanel";
import { VueParticulier } from "./views/VueParticulier";
import { VueRH } from "./views/VueRH";
import { VueConseiller } from "./views/VueConseiller";
import { VueInstitution } from "./views/VueInstitution";

const TERRITOIRES = ["Grand Est", "Île-de-France", "Auvergne-Rhône-Alpes", "Hauts-de-France"];

const TABS = [
    { key: PUBLIC_TYPES.PARTICULIER, label: "Particulier", icon: Users, testId: OPC.tabParticulier },
    { key: PUBLIC_TYPES.RH, label: "Employeurs RH", icon: Building2, testId: OPC.tabRh },
    { key: PUBLIC_TYPES.CONSEILLER, label: "Conseillers", icon: Handshake, testId: OPC.tabConseiller },
    { key: PUBLIC_TYPES.INSTITUTION, label: "Institutions", icon: Globe2, testId: OPC.tabInstitution },
];

const CONFIANCE_LABELS = [
    { key: "fiabilite_prouvee_pct", label: "Fiabilité prouvée" },
    { key: "completude_profils_pct", label: "Complétude profils" },
    { key: "coherence_parcours_pct", label: "Cohérence parcours" },
    { key: "fraicheur_donnees_pct", label: "Fraîcheur données" },
];

const VUE_MAP = { particulier: PUBLIC_TYPES.PARTICULIER, rh: PUBLIC_TYPES.RH, conseiller: PUBLIC_TYPES.CONSEILLER, institution: PUBLIC_TYPES.INSTITUTION };

export default function Observatoire({
    userId: initialUserId = "user_demo_001",
    entrepriseId: initialEntrepriseId = "ent_demo_001",
    territoire: initialTerritoire = "Grand Est",
    defaultPublicType = PUBLIC_TYPES.CONSEILLER,
    defaultMetier = "Développeur Full-Stack Python/React",
}) {
    const [searchParams] = useSearchParams();
    const vueParam = searchParams.get("vue");
    const initialTab = (vueParam && VUE_MAP[vueParam]) || defaultPublicType;

    const [publicType, setPublicType] = useState(initialTab);
    const [territoire, setTerritoire] = useState(initialTerritoire);

    useEffect(() => {
        if (vueParam && VUE_MAP[vueParam]) {
            setPublicType(VUE_MAP[vueParam]);
        }
    }, [vueParam]);
    const [userId, setUserId] = useState(initialUserId);
    const [metier, setMetier] = useState(defaultMetier);
    const [filiereFocus, setFiliereFocus] = useState(null);
    const [entrepriseId, setEntrepriseId] = useState(initialEntrepriseId);
    const [isLoggedIn, setIsLoggedIn] = useState(false);

    const { data, loading, error, refresh } = useOPCView({ publicType, userId, metier, entrepriseId, territoire });
    const { stats, refresh: refreshStats } = useOPCStats();
    const { confiance } = useOPCConfiance();
    const { synthese, loading: syntheseLoading } = useOPCSynthese(
        territoire,
        publicType === PUBLIC_TYPES.PARTICULIER ? filiereFocus : null,
        publicType === PUBLIC_TYPES.PARTICULIER ? metier : null
    );

    const handleRefresh = () => { refresh(); refreshStats(); };

    return (
        <div className="min-h-screen bg-background">
            {/* Sticky header */}
            <header className="sticky top-0 z-30 border-b border-slate-200/80 bg-white/85 backdrop-blur-md">
                <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3 px-6 py-4 md:px-8 lg:px-12">
                    <a
                        href="https://reactif.pro"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="group flex items-center gap-3 transition-opacity hover:opacity-80"
                        data-testid="brand-logo-link"
                        aria-label="Aller sur reactif.pro"
                    >
                        <img
                            src="/logo-reactif-pro.png?v=3"
                            alt="RE'ACTIF PRO"
                            className="h-14 w-auto sm:h-16"
                            data-testid="brand-logo-img"
                        />
                        <span className="hidden sm:block h-8 w-px bg-slate-200" aria-hidden="true" />
                        <p className="hidden sm:block text-[11px] uppercase tracking-[0.18em] text-slate-500">
                            Observatoire Prédictif des Compétences
                        </p>
                    </a>
                    <div className="flex items-center gap-2">
                        <Select value={territoire} onValueChange={setTerritoire}>
                            <SelectTrigger className="w-[200px] h-9 text-xs" data-testid={OPC.territorySelect}>
                                <MapPin className="h-3.5 w-3.5 mr-1.5 text-slate-500" />
                                <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                                {TERRITOIRES.map((t) => (
                                    <SelectItem key={t} value={t} className="text-xs">{t}</SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={handleRefresh}
                            disabled={loading}
                            data-testid={OPC.refreshBtn}
                            className="gap-1.5 text-xs"
                        >
                            <RotateCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
                            Actualiser
                        </Button>
                        {isLoggedIn ? (
                            <Button
                                size="sm"
                                onClick={() => setIsLoggedIn(false)}
                                data-testid="logout-btn"
                                className="gap-1.5 text-xs bg-navy text-white hover:bg-navy/90"
                            >
                                <LogOut className="h-3.5 w-3.5" />
                                Déconnexion
                            </Button>
                        ) : (
                            <Button
                                size="sm"
                                onClick={() => setIsLoggedIn(true)}
                                data-testid="login-btn"
                                className="gap-1.5 text-xs bg-navy text-white hover:bg-navy/90"
                            >
                                <LogIn className="h-3.5 w-3.5" />
                                Connexion
                            </Button>
                        )}
                    </div>
                </div>
            </header>

            {/* Main */}
            <main className="mx-auto max-w-7xl px-6 py-10 md:px-8 lg:px-12 space-y-8">
                {/* Hero / Synthèse */}
                <section>
                    <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-brand-blue">
                        Infrastructure d&apos;intelligence territoriale
                    </p>
                    <h1 className="font-display mt-2 text-3xl font-bold tracking-tight text-navy sm:text-4xl lg:text-5xl">
                        Anticiper les compétences,<br className="hidden sm:block" /> piloter l&apos;emploi en {territoire}.
                    </h1>
                    <p className="mt-3 max-w-2xl text-sm leading-relaxed text-slate-600">
                        Plateforme apprenante d&apos;ALT&amp;ACT — agrège 8 flux territoriaux (profils, entreprises, offres, formations, institutionnel, terrain, parcours, référentiels vivants) pour produire 4 vues décisionnelles.
                    </p>
                </section>

                {/* KPI globaux */}
                {stats && (
                    <section className="grid grid-cols-2 gap-4 md:grid-cols-4">
                        <KpiCard testId={OPC.statsKpiProfils} label="Profils actifs" value={stats.profils_utilisateurs} icon={Users} accent="text-brand-blue" />
                        <KpiCard testId={OPC.statsKpiOffres} label="Offres analysées" value={stats.offres_emploi} icon={Briefcase} accent="text-brand-green" />
                        <KpiCard testId={OPC.statsKpiReferentiels} label="Référentiels vivants" value={stats.referentiels_vivants} icon={GraduationCap} accent="text-brand-purple" />
                        <KpiCard testId={OPC.statsKpiTerrain} label="Observations terrain" value={stats.observations_terrain} icon={Activity} accent="text-brand-orange" />
                    </section>
                )}

                {/* Synthèse IA */}
                <section>
                    <Card data-testid={OPC.syntheseBlock} className="border-navy/15 bg-navy text-white p-6">
                        <div className="flex items-center gap-2 mb-3">
                            <Sparkles className="h-4 w-4 text-blue-200" />
                            <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-blue-200">
                                Synthèse prédictive
                            </p>
                        </div>
                        {syntheseLoading ? (
                            <div className="space-y-2 animate-pulse">
                                <div className="h-3 w-full rounded bg-white/15" />
                                <div className="h-3 w-11/12 rounded bg-white/15" />
                                <div className="h-3 w-10/12 rounded bg-white/15" />
                            </div>
                        ) : (
                            <p className="font-display text-[15px] leading-relaxed text-white/90 whitespace-pre-line">
                                {(synthese || "Synthèse non disponible pour ce territoire.").replace(/\*\*/g, "")}
                            </p>
                        )}
                    </Card>
                </section>

                {/* Sélecteurs contextuels Particulier / RH */}
                {(publicType === PUBLIC_TYPES.PARTICULIER || publicType === PUBLIC_TYPES.RH) && (
                    <section className="rounded-xl border border-slate-200 bg-white p-5">
                        {publicType === PUBLIC_TYPES.PARTICULIER && (
                            <RechercheMetier
                                metier={metier}
                                onMetierChange={setMetier}
                                onFiliereChange={setFiliereFocus}
                                territoire={territoire}
                            />
                        )}
                        {publicType === PUBLIC_TYPES.RH && (
                            <div className="flex flex-wrap items-center gap-3">
                                <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-500">
                                    Cible
                                </p>
                                <div className="flex items-center gap-2">
                                    <span className="text-xs text-slate-500">entreprise_id</span>
                                    <Input
                                        value={entrepriseId}
                                        onChange={(e) => setEntrepriseId(e.target.value)}
                                        placeholder="ent_demo_001"
                                        className="h-8 w-[220px] font-mono text-xs"
                                        data-testid={OPC.entrepriseIdInput}
                                    />
                                </div>
                            </div>
                        )}
                    </section>
                )}

                {/* Tabs */}
                <section>
                    <Tabs value={publicType} onValueChange={setPublicType}>
                        <TabsList className="grid w-full grid-cols-2 sm:grid-cols-4 h-auto bg-slate-100/70 p-1">
                            {TABS.map(({ key, label, icon: Icon, testId }) => (
                                <TabsTrigger
                                    key={key}
                                    value={key}
                                    data-testid={testId}
                                    className="gap-1.5 py-2 text-xs sm:text-sm data-[state=active]:bg-white data-[state=active]:text-navy data-[state=active]:shadow-sm"
                                >
                                    <Icon className="h-3.5 w-3.5" strokeWidth={1.75} />
                                    <span>{label}</span>
                                </TabsTrigger>
                            ))}
                        </TabsList>

                        <div className="mt-6">
                            {loading && (
                                <div data-testid={OPC.loadingState} className="flex items-center justify-center py-16">
                                    <RotateCw className="h-5 w-5 animate-spin text-navy" />
                                    <span className="ml-3 text-sm text-slate-500">Chargement de la vue…</span>
                                </div>
                            )}
                            {error && !loading && (
                                <Card data-testid={OPC.errorState} className="border-orange-200 bg-orange-50 p-4">
                                    <p className="text-sm text-orange-800">{error}</p>
                                </Card>
                            )}
                            {!loading && !error && data && (
                                <>
                                    <TabsContent value={PUBLIC_TYPES.PARTICULIER}><VueParticulier data={data} /></TabsContent>
                                    <TabsContent value={PUBLIC_TYPES.RH}><VueRH data={data} /></TabsContent>
                                    <TabsContent value={PUBLIC_TYPES.CONSEILLER}><VueConseiller data={data} /></TabsContent>
                                    <TabsContent value={PUBLIC_TYPES.INSTITUTION}><VueInstitution data={data} /></TabsContent>
                                </>
                            )}
                        </div>
                    </Tabs>
                </section>

                <footer className="pt-6 text-center text-[11px] text-slate-400">
                    Module OPC RE&apos;ACTIF PRO — ALT&amp;ACT © 2026
                </footer>
            </main>
        </div>
    );
}
