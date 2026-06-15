import { cn } from "@/lib/utils";

const STATUTS = {
    en_croissance: { label: "En croissance", cls: "bg-emerald-50 text-emerald-700 ring-emerald-600/20" },
    en_transformation: { label: "En transformation", cls: "bg-violet-50 text-violet-700 ring-violet-600/20" },
    stable: { label: "Stable", cls: "bg-slate-100 text-slate-700 ring-slate-600/20" },
    en_declin: { label: "En déclin", cls: "bg-orange-50 text-orange-700 ring-orange-600/20" },
    emergent: { label: "Émergent", cls: "bg-blue-50 text-blue-700 ring-blue-600/20" },
};

export function StatutBadge({ statut, className }) {
    const s = STATUTS[statut] || { label: statut || "—", cls: "bg-slate-100 text-slate-700 ring-slate-600/20" };
    return (
        <span
            data-testid={`statut-badge-${statut}`}
            className={cn(
                "inline-flex items-center rounded-full px-2.5 py-0.5 text-[11px] font-medium ring-1 ring-inset whitespace-nowrap",
                s.cls,
                className
            )}
        >
            {s.label}
        </span>
    );
}

export function TensionPill({ value }) {
    if (value == null) return null;
    const high = value >= 60;
    const mid = value >= 30;
    const tone = high ? "text-orange-700 bg-orange-50 ring-orange-600/20"
        : mid ? "text-amber-700 bg-amber-50 ring-amber-600/20"
        : "text-emerald-700 bg-emerald-50 ring-emerald-600/20";
    return (
        <span className={cn("tabular inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-medium ring-1 ring-inset", tone)}>
            {value}%
        </span>
    );
}
