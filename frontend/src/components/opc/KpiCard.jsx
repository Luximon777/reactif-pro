import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

export function KpiCard({ value, label, icon: Icon, accent = "text-navy", testId }) {
    return (
        <Card
            data-testid={testId}
            className="group relative overflow-hidden border-slate-200/80 bg-white p-5 transition-shadow hover:shadow-md"
        >
            <div className="flex items-start justify-between gap-3">
                <div className="space-y-1">
                    <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-500">
                        {label}
                    </p>
                    <p className={cn("font-display text-3xl font-bold tracking-tight tabular leading-none", accent)}>
                        {value ?? "—"}
                    </p>
                </div>
                {Icon && (
                    <div className="rounded-md bg-slate-50 p-2 text-slate-500 transition-colors group-hover:bg-navy/5 group-hover:text-navy">
                        <Icon className="h-4 w-4" strokeWidth={1.75} />
                    </div>
                )}
            </div>
        </Card>
    );
}
