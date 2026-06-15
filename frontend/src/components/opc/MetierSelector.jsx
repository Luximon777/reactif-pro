import { useEffect, useState } from "react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Briefcase } from "lucide-react";
import { OPC } from "@/constants/testIds";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export function MetierSelector({ value, onChange, territoire = "Grand Est" }) {
    const [metiers, setMetiers] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        let cancelled = false;
        const load = async () => {
            setLoading(true);
            try {
                const r = await fetch(`${BACKEND_URL}/api/opc/vue/metiers-vises?territoire=${encodeURIComponent(territoire)}`);
                const d = await r.json();
                if (!cancelled) setMetiers(d.metiers || []);
            } catch {
                if (!cancelled) setMetiers([]);
            } finally {
                if (!cancelled) setLoading(false);
            }
        };
        load();
        return () => { cancelled = true; };
    }, [territoire]);

    return (
        <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500">Métier visé</span>
            <Select value={value} onValueChange={onChange} disabled={loading}>
                <SelectTrigger
                    className="h-9 w-[320px] text-xs"
                    data-testid={OPC.metierSelect}
                >
                    <Briefcase className="h-3.5 w-3.5 mr-1.5 text-slate-500" />
                    <SelectValue placeholder={loading ? "Chargement…" : "Sélectionner un métier"} />
                </SelectTrigger>
                <SelectContent>
                    {metiers.map((m) => (
                        <SelectItem
                            key={`${m.label}-${m.code_rome}`}
                            value={m.label}
                            className="text-xs"
                        >
                            <div className="flex flex-col">
                                <span className="font-medium">{m.label}</span>
                                <span className="font-mono text-[10px] text-slate-500">
                                    {m.code_rome}
                                    {m.user_id && " · profil démo disponible"}
                                </span>
                            </div>
                        </SelectItem>
                    ))}
                </SelectContent>
            </Select>
        </div>
    );
}
