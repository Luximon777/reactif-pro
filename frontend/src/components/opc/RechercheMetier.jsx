import { useEffect, useState } from "react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Layers, Building2, Briefcase, Link2, Search } from "lucide-react";
import { Chip } from "./Section";
import { StatutBadge, TensionPill } from "./StatutBadge";
import { OPC } from "@/constants/testIds";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

function findMetierInTree(tree, metierLabel) {
    if (!metierLabel || !tree?.filieres) return null;
    for (const f of tree.filieres) {
        for (const s of f.secteurs) {
            const m = s.metiers.find((x) => x.label === metierLabel);
            if (m) return { filiere: f, secteur: s, metier: m };
        }
    }
    return null;
}

export function RechercheMetier({ metier, onMetierChange, onFiliereChange, territoire = "Grand Est" }) {
    const [tree, setTree] = useState({ filieres: [], total_metiers: 0 });
    const [loading, setLoading] = useState(true);
    const [filiereKey, setFiliereKey] = useState("");
    const [secteurKey, setSecteurKey] = useState("");
    const [lies, setLies] = useState(null);
    const [searchQuery, setSearchQuery] = useState("");
    const [searchResults, setSearchResults] = useState([]);
    const [searchOpen, setSearchOpen] = useState(false);

    // Charger l'arborescence
    useEffect(() => {
        let cancelled = false;
        const load = async () => {
            setLoading(true);
            try {
                const r = await fetch(
                    `${BACKEND_URL}/api/opc/vue/filieres?territoire=${encodeURIComponent(territoire)}`
                );
                const d = await r.json();
                if (cancelled) return;
                setTree(d);
                // Resync filière/secteur depuis le métier courant
                const hit = findMetierInTree(d, metier);
                if (hit) {
                    setFiliereKey(hit.filiere.key);
                    setSecteurKey(hit.secteur.key);
                }
            } catch {
                if (!cancelled) setTree({ filieres: [], total_metiers: 0 });
            } finally {
                if (!cancelled) setLoading(false);
            }
        };
        load();
        return () => { cancelled = true; };
    }, [territoire]);

    // Charger les métiers liés au métier courant
    useEffect(() => {
        let cancelled = false;
        const hit = findMetierInTree(tree, metier);
        const rome = hit?.metier.code_rome;
        const load = async () => {
            if (!rome) { if (!cancelled) setLies(null); return; }
            try {
                const r = await fetch(
                    `${BACKEND_URL}/api/opc/vue/metiers-lies/${encodeURIComponent(rome)}?territoire=${encodeURIComponent(territoire)}`
                );
                const d = await r.json();
                if (!cancelled) setLies(d);
            } catch {
                if (!cancelled) setLies(null);
            }
        };
        load();
        return () => { cancelled = true; };
    }, [metier, tree, territoire]);

    const filiereActive = tree.filieres.find((f) => f.key === filiereKey) || null;
    const secteurs = filiereActive?.secteurs || [];
    const secteurActif = secteurs.find((s) => s.key === secteurKey) || null;
    const metiersDisponibles = secteurActif?.metiers || [];

    // Recherche full-text avec debounce
    useEffect(() => {
        let cancelled = false;
        const load = async () => {
            if (!searchQuery || searchQuery.length < 2) {
                if (!cancelled) { setSearchResults([]); setSearchOpen(false); }
                return;
            }
            try {
                const r = await fetch(
                    `${BACKEND_URL}/api/opc/vue/recherche-metier?q=${encodeURIComponent(searchQuery)}&limit=10`
                );
                const d = await r.json();
                if (!cancelled) {
                    setSearchResults(d.results || []);
                    setSearchOpen(true);
                }
            } catch {
                if (!cancelled) setSearchResults([]);
            }
        };
        const t = setTimeout(load, 250);
        return () => { cancelled = true; clearTimeout(t); };
    }, [searchQuery]);

    const handleFiliere = (k) => {
        setFiliereKey(k);
        setSecteurKey("");
        onMetierChange("");
        onFiliereChange?.(k || null);
    };
    const handleSecteur = (k) => {
        setSecteurKey(k);
        onMetierChange("");
    };
    const handleMetier = (label) => {
        const hit = findMetierInTree(tree, label);
        if (hit) {
            setFiliereKey(hit.filiere.key);
            setSecteurKey(hit.secteur.key);
            onFiliereChange?.(hit.filiere.key);
        }
        onMetierChange(label);
    };

    return (
        <div className="space-y-4" data-testid={OPC.rechercheMetier}>
            {/* Recherche full-text */}
            <div className="relative">
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                    <Input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        onFocus={() => searchResults.length > 0 && setSearchOpen(true)}
                        onBlur={() => setTimeout(() => setSearchOpen(false), 200)}
                        placeholder="Rechercher un métier…"
                        className="pl-9 h-10 text-sm"
                        data-testid={OPC.searchMetierInput}
                    />
                </div>
                {searchOpen && searchResults.length > 0 && (
                    <div
                        className="absolute z-20 mt-1 w-full max-h-80 overflow-y-auto rounded-lg border border-slate-200 bg-white shadow-lg"
                        data-testid={OPC.searchMetierResults}
                    >
                        {searchResults.map((r, i) => (
                            <button
                                key={i}
                                onMouseDown={(e) => {
                                    e.preventDefault();
                                    handleMetier(r.label);
                                    setSearchQuery("");
                                    setSearchOpen(false);
                                }}
                                className="flex w-full flex-col items-start gap-0.5 border-b border-slate-100 px-3 py-2 text-left transition-colors last:border-0 hover:bg-slate-50"
                            >
                                <div className="flex w-full items-baseline justify-between gap-2">
                                    <span className="text-sm font-medium text-ink">{r.label}</span>
                                    {r.code_rome && (
                                        <span className="font-mono text-[10px] text-slate-400">{r.code_rome}</span>
                                    )}
                                </div>
                                <span className="text-[11px] text-slate-500">
                                    {r.filiere.code} · {r.filiere.label} › {r.secteur.label}
                                </span>
                                {r.mission && (
                                    <span className="line-clamp-1 text-[11px] italic text-slate-400">
                                        {r.mission}
                                    </span>
                                )}
                            </button>
                        ))}
                    </div>
                )}
            </div>

            <div className="grid gap-3 sm:grid-cols-3">
                {/* Filière */}
                <div>
                    <label className="mb-1.5 block text-[10px] font-bold uppercase tracking-[0.18em] text-slate-500">
                        Filière professionnelle
                    </label>
                    <Select value={filiereKey} onValueChange={handleFiliere} disabled={loading}>
                        <SelectTrigger className="h-9 text-xs" data-testid={OPC.filiereSelect}>
                            <Layers className="h-3.5 w-3.5 mr-1.5 text-slate-500" />
                            <SelectValue placeholder={loading ? "Chargement…" : "Sélectionner une filière"} />
                        </SelectTrigger>
                        <SelectContent>
                            {tree.filieres.map((f) => (
                                <SelectItem key={f.key} value={f.key} className="text-xs">
                                    {f.label}
                                    <span className="ml-2 text-[10px] text-slate-400 tabular">· {f.nb_metiers}</span>
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>

                {/* Secteur */}
                <div>
                    <label className="mb-1.5 block text-[10px] font-bold uppercase tracking-[0.18em] text-slate-500">
                        Secteur d&apos;activité
                    </label>
                    <Select value={secteurKey} onValueChange={handleSecteur} disabled={!filiereActive}>
                        <SelectTrigger className="h-9 text-xs" data-testid={OPC.secteurSelect}>
                            <Building2 className="h-3.5 w-3.5 mr-1.5 text-slate-500" />
                            <SelectValue placeholder={filiereActive ? "Sélectionner un secteur" : "—"} />
                        </SelectTrigger>
                        <SelectContent>
                            {secteurs.map((s) => (
                                <SelectItem key={s.key} value={s.key} className="text-xs capitalize">
                                    {s.label}
                                    <span className="ml-2 text-[10px] text-slate-400 tabular">· {s.metiers.length}</span>
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>

                {/* Métier */}
                <div>
                    <label className="mb-1.5 block text-[10px] font-bold uppercase tracking-[0.18em] text-slate-500">
                        Métier
                    </label>
                    <Select value={metier || ""} onValueChange={handleMetier} disabled={!secteurActif}>
                        <SelectTrigger className="h-9 text-xs" data-testid={OPC.metierSelect}>
                            <Briefcase className="h-3.5 w-3.5 mr-1.5 text-slate-500" />
                            <SelectValue placeholder={secteurActif ? "Choisir un métier" : "—"} />
                        </SelectTrigger>
                        <SelectContent>
                            {metiersDisponibles.map((m) => (
                                <SelectItem key={`${m.label}-${m.code_rome}`} value={m.label} className="text-xs">
                                    <div className="flex flex-col">
                                        <span className="font-medium">{m.label}</span>
                                        <span className="font-mono text-[10px] text-slate-500">
                                            {m.code_rome}
                                            {m.user_id && " · profil démo"}
                                        </span>
                                    </div>
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>
            </div>

            {/* Métiers en lien */}
            {lies && (lies.trajectoires_compatibles?.length > 0 || lies.metiers_meme_secteur?.length > 0) && (
                <div className="rounded-lg border border-slate-200 bg-slate-50/50 p-3">
                    <div className="mb-2 flex items-center gap-2">
                        <Link2 className="h-3.5 w-3.5 text-slate-500" />
                        <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-500">
                            Métiers en lien
                        </p>
                    </div>
                    <div className="flex flex-wrap gap-2" data-testid={OPC.metiersLies}>
                        {lies.trajectoires_compatibles?.map((t, i) => (
                            <button
                                key={`traj-${i}`}
                                onClick={() => handleMetier(t.intitule)}
                                className="group flex items-center gap-1.5 rounded-full border border-violet-200 bg-violet-50 px-2.5 py-1 text-[11px] font-medium text-violet-700 transition-colors hover:bg-violet-100"
                            >
                                <span>{t.intitule}</span>
                                {t.statut && <StatutBadge statut={t.statut} className="text-[10px]" />}
                                {t.taux_tension != null && <TensionPill value={t.taux_tension} />}
                            </button>
                        ))}
                        {lies.metiers_meme_secteur?.map((m, i) => (
                            <button
                                key={`sect-${i}`}
                                onClick={() => handleMetier(m.intitule)}
                                className="group flex items-center gap-1.5 rounded-full border border-blue-200 bg-blue-50 px-2.5 py-1 text-[11px] font-medium text-blue-700 transition-colors hover:bg-blue-100"
                            >
                                <span>{m.intitule}</span>
                                <span className="font-mono text-[10px] text-blue-500">{m.code_rome}</span>
                                <Chip tone="blue">{m.nb_offres} offre(s)</Chip>
                            </button>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
