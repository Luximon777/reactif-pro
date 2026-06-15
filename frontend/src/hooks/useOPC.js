import { useState, useEffect, useCallback } from "react";
import { opcApi, PUBLIC_TYPES } from "@/lib/opcApi";

export { PUBLIC_TYPES };

export function useOPCView({ publicType, userId, metier, entrepriseId, territoire }) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchVue = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            let r;
            switch (publicType) {
                case PUBLIC_TYPES.PARTICULIER:
                    if (metier) {
                        r = await opcApi.vue.particulierParMetier(metier, territoire);
                    } else if (userId) {
                        r = await opcApi.vue.particulier(userId, territoire);
                    } else {
                        throw new Error("Sélectionnez un métier visé");
                    }
                    break;
                case PUBLIC_TYPES.RH:
                    if (!entrepriseId) throw new Error("entrepriseId requis pour la vue RH");
                    r = await opcApi.vue.rh(entrepriseId, territoire);
                    break;
                case PUBLIC_TYPES.CONSEILLER:
                    r = await opcApi.vue.conseiller(territoire);
                    break;
                case PUBLIC_TYPES.INSTITUTION:
                    r = await opcApi.vue.institution(territoire);
                    break;
                default:
                    throw new Error(`publicType inconnu : ${publicType}`);
            }
            setData(r);
        } catch (e) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    }, [publicType, userId, metier, entrepriseId, territoire]);

    useEffect(() => {
        fetchVue();
    }, [fetchVue]);

    return { data, loading, error, refresh: fetchVue };
}

export function useOPCStats() {
    const [stats, setStats] = useState(null);
    const [refreshKey, setRefreshKey] = useState(0);
    useEffect(() => {
        opcApi.stats().then(setStats).catch(() => {});
    }, [refreshKey]);
    return { stats, refresh: () => setRefreshKey((k) => k + 1) };
}

export function useOPCConfiance() {
    const [confiance, setConfiance] = useState(null);
    useEffect(() => {
        opcApi.confiance().then(setConfiance).catch(() => {});
    }, []);
    return { confiance };
}

export function useOPCSynthese(territoire = "Grand Est", filiere = null, metier = null) {
    const [synthese, setSynthese] = useState(null);
    const [loading, setLoading] = useState(true);
    useEffect(() => {
        let cancelled = false;
        const load = async () => {
            if (!cancelled) setLoading(true);
            const params = new URLSearchParams({ territoire });
            if (filiere) params.set("filiere", filiere);
            if (metier) params.set("metier", metier);
            try {
                const r = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/opc/ia/synthese?${params}`);
                const d = await r.json();
                if (!cancelled) setSynthese(d.synthese);
            } catch {
                if (!cancelled) setSynthese(null);
            } finally {
                if (!cancelled) setLoading(false);
            }
        };
        load();
        return () => { cancelled = true; };
    }, [territoire, filiere, metier]);
    return { synthese, loading };
}
