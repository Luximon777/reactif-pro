/**
 * OPC — Fetch helpers
 * Toutes les routes OPC sont préfixées par /api/opc/...
 */

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const BASE = `${BACKEND_URL}/api`;

async function request(path, options = {}, { retries = 2, delay = 600 } = {}) {
    let lastErr;
    for (let attempt = 0; attempt <= retries; attempt++) {
        try {
            const res = await fetch(`${BASE}${path}`, {
                headers: { "Content-Type": "application/json" },
                ...options,
            });
            if (!res.ok) {
                if (res.status === 404) {
                    const err = await res.json().catch(() => ({}));
                    throw new Error(err.detail || "Ressource introuvable");
                }
                if (res.status >= 500 || res.status === 502 || res.status === 503) {
                    throw new Error(`Erreur serveur ${res.status}`);
                }
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail || `Erreur ${res.status}`);
            }
            return res.json();
        } catch (e) {
            lastErr = e;
            if (attempt < retries && !String(e.message).includes("introuvable")) {
                await new Promise((r) => setTimeout(r, delay * (attempt + 1)));
                continue;
            }
            break;
        }
    }
    throw lastErr;
}

export const opcApi = {
    stats: () => request("/opc/ingestion/stats"),
    confiance: () => request("/opc/ia/kpis-confiance"),
    synthese: (territoire = "Grand Est") =>
        request(`/opc/ia/synthese?territoire=${encodeURIComponent(territoire)}`),
    vue: {
        particulier: (userId, territoire = "Grand Est") =>
            request(`/opc/vue/particulier/${encodeURIComponent(userId)}?territoire=${encodeURIComponent(territoire)}`),
        particulierParMetier: (metier, territoire = "Grand Est") =>
            request(`/opc/vue/particulier-par-metier?metier=${encodeURIComponent(metier)}&territoire=${encodeURIComponent(territoire)}`),
        rh: (entrepriseId, territoire = "Grand Est") =>
            request(`/opc/vue/rh/${encodeURIComponent(entrepriseId)}?territoire=${encodeURIComponent(territoire)}`),
        conseiller: (territoire = "Grand Est") =>
            request(`/opc/vue/conseiller?territoire=${encodeURIComponent(territoire)}`),
        institution: (territoire = "Grand Est") =>
            request(`/opc/vue/institution?territoire=${encodeURIComponent(territoire)}`),
    },
};

export const PUBLIC_TYPES = {
    PARTICULIER: "particulier",
    RH: "rh",
    CONSEILLER: "conseiller",
    INSTITUTION: "institution",
};
