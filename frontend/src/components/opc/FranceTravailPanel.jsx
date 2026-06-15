import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CheckCircle2, AlertCircle, RefreshCw, ExternalLink, Database } from "lucide-react";
import { OPC } from "@/constants/testIds";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export function FranceTravailPanel() {
    const [status, setStatus] = useState(null);
    const [loading, setLoading] = useState(true);
    const [syncing, setSyncing] = useState(null);
    const [message, setMessage] = useState(null);

    const fetchStatus = async () => {
        setLoading(true);
        try {
            const r = await fetch(`${BACKEND_URL}/api/opc/admin/france-travail/status`);
            const d = await r.json();
            setStatus(d);
        } catch {
            setStatus({ configured: false });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        let cancelled = false;
        const load = async () => {
            try {
                const r = await fetch(`${BACKEND_URL}/api/opc/admin/france-travail/status`);
                const d = await r.json();
                if (!cancelled) setStatus(d);
            } catch {
                if (!cancelled) setStatus({ configured: false });
            } finally {
                if (!cancelled) setLoading(false);
            }
        };
        load();
        return () => { cancelled = true; };
    }, []);

    const lancerSync = async (kind) => {
        setSyncing(kind);
        setMessage(null);
        const url = kind === "rome"
            ? `${BACKEND_URL}/api/opc/admin/france-travail/sync-rome`
            : `${BACKEND_URL}/api/opc/admin/france-travail/sync?max_par_dept=150`;
        try {
            const r = await fetch(url, { method: "POST" });
            const d = await r.json();
            setMessage(d.message || "Lancé");
        } catch {
            setMessage("Erreur lors du lancement");
        } finally {
            setTimeout(() => setSyncing(null), 1200);
        }
    };

    if (loading) return null;
    if (!status?.configured) return null;

    const offresOK = status.ready_offres;
    const romeOK = status.ready_rome;

    return (
        <Card className="border-slate-200/80 p-5" data-testid={OPC.ftPanel}>
            <div className="mb-4 flex items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                    <Database className="h-4 w-4 text-navy" />
                    <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-500">
                        Connecteur France Travail
                    </p>
                </div>
                <Button variant="ghost" size="sm" onClick={fetchStatus} className="h-7 text-[11px]">
                    <RefreshCw className="h-3 w-3 mr-1" /> rafraîchir
                </Button>
            </div>

            <ul className="space-y-2.5">
                <li className="flex items-center justify-between gap-3 rounded-md border border-slate-200 bg-slate-50/40 px-3 py-2">
                    <div className="flex items-center gap-2">
                        {romeOK
                            ? <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                            : <AlertCircle className="h-4 w-4 text-amber-600" />}
                        <span className="text-sm font-medium">ROME 4.0</span>
                        <span className="text-[11px] text-slate-500">référentiel métiers officiel</span>
                    </div>
                    {romeOK && (
                        <Button
                            size="sm"
                            variant="outline"
                            onClick={() => lancerSync("rome")}
                            disabled={syncing === "rome"}
                            className="h-7 text-[11px]"
                            data-testid={OPC.ftSyncRomeBtn}
                        >
                            {syncing === "rome" ? "Sync…" : "Importer"}
                        </Button>
                    )}
                </li>

                <li className="flex items-center justify-between gap-3 rounded-md border border-slate-200 bg-slate-50/40 px-3 py-2">
                    <div className="flex items-center gap-2">
                        {offresOK
                            ? <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                            : <AlertCircle className="h-4 w-4 text-amber-600" />}
                        <span className="text-sm font-medium">Offres d&apos;emploi v2</span>
                        <span className="text-[11px] text-slate-500">offres Grand Est (10 départements)</span>
                    </div>
                    {offresOK ? (
                        <Button
                            size="sm"
                            variant="outline"
                            onClick={() => lancerSync("offres")}
                            disabled={syncing === "offres"}
                            className="h-7 text-[11px]"
                            data-testid={OPC.ftSyncOffresBtn}
                        >
                            {syncing === "offres" ? "Sync…" : "Importer"}
                        </Button>
                    ) : (
                        <a
                            href="https://francetravail.io/produits-partages/catalogue/offres-emploi/informations"
                            target="_blank"
                            rel="noreferrer"
                            className="inline-flex items-center gap-1 text-[11px] text-amber-700 hover:underline"
                        >
                            À souscrire <ExternalLink className="h-3 w-3" />
                        </a>
                    )}
                </li>
            </ul>

            {!offresOK && (
                <div className="mt-4 rounded-md border border-amber-200 bg-amber-50/60 px-3 py-2 text-xs leading-relaxed text-amber-900">
                    <strong>Pour activer la synchro des offres :</strong> rends-toi sur ton application
                    francetravail.io › <strong>API du catalogue</strong> › clique <strong>Souscrire</strong> à « Offres d&apos;emploi v2 ».
                    Validation par France Travail sous 24–72 h.
                </div>
            )}

            {message && (
                <p className="mt-3 text-xs text-emerald-700" data-testid={OPC.ftSyncMessage}>{message}</p>
            )}
        </Card>
    );
}
