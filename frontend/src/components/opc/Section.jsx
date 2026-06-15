import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

export function Section({ title, icon: Icon, action, className, children, testId }) {
    return (
        <Card
            data-testid={testId}
            className={cn(
                "border-slate-200/80 bg-white p-6",
                className
            )}
        >
            <div className="mb-4 flex items-center justify-between gap-3">
                <div className="flex items-center gap-2.5">
                    {Icon && <Icon className="h-4 w-4 text-slate-500" strokeWidth={1.75} />}
                    <h3 className="font-display text-base font-semibold tracking-tight text-ink">
                        {title}
                    </h3>
                </div>
                {action}
            </div>
            <div>{children}</div>
        </Card>
    );
}

export function EmptyHint({ children = "Aucune donnée disponible pour l'instant." }) {
    return (
        <p className="rounded-md border border-dashed border-slate-200 bg-slate-50/50 px-3 py-4 text-center text-xs text-slate-500">
            {children}
        </p>
    );
}

export function Chip({ children, tone = "neutral" }) {
    const tones = {
        neutral: "border-slate-200 bg-white text-slate-700 hover:bg-slate-50",
        emerald: "border-emerald-200 bg-emerald-50 text-emerald-700",
        amber: "border-amber-200 bg-amber-50 text-amber-800",
        orange: "border-orange-200 bg-orange-50 text-orange-700",
        violet: "border-violet-200 bg-violet-50 text-violet-700",
        blue: "border-blue-200 bg-blue-50 text-blue-700",
    };
    return (
        <span className={cn(
            "inline-flex items-center rounded-full border px-2.5 py-1 text-[11px] font-medium transition-colors",
            tones[tone] || tones.neutral
        )}>
            {children}
        </span>
    );
}
