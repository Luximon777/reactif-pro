import { Badge } from "@/components/ui/badge";

const CvPreview = ({ data }) => {
  let cv;
  try {
    cv = typeof data === "string" ? JSON.parse(data) : data;
  } catch {
    return <pre className="text-xs text-slate-700 whitespace-pre-wrap font-sans leading-relaxed">{data}</pre>;
  }
  return (
    <div className="bg-white border rounded-lg p-6 space-y-4 text-slate-800 max-h-[600px] overflow-y-auto" style={{ fontFamily: "Calibri, sans-serif" }}>
      <div className="text-center border-b pb-4">
        <h1 className="text-2xl font-bold tracking-wide" style={{ color: "#1e3a5f" }}>{cv.nom || "Candidat"}</h1>
        {cv.titre && <p className="text-sm text-slate-500 mt-1">{cv.titre}</p>}
        {cv.contact && (
          <p className="text-xs text-slate-400 mt-2">
            {[cv.contact.email, cv.contact.telephone, cv.contact.adresse].filter(Boolean).join(" | ")}
          </p>
        )}
      </div>
      {cv.profil && (
        <div>
          <h2 className="text-xs font-bold uppercase tracking-wider mb-1" style={{ color: "#1e3a5f" }}>Profil professionnel</h2>
          <p className="text-sm leading-relaxed">{cv.profil}</p>
        </div>
      )}
      {cv.competences_cles?.length > 0 && (
        <div>
          <h2 className="text-xs font-bold uppercase tracking-wider mb-1" style={{ color: "#1e3a5f" }}>Compétences clés</h2>
          <div className="flex flex-wrap gap-1.5">
            {cv.competences_cles.map((c, i) => (
              <span key={i} className="text-xs px-2 py-0.5 rounded-full" style={{ background: "#f1f5f9", color: "#334155" }}>{c}</span>
            ))}
          </div>
        </div>
      )}
      {cv.savoir_faire?.length > 0 && (
        <div>
          <h2 className="text-xs font-bold uppercase tracking-wider mb-1" style={{ color: "#1e3a5f" }}>Savoir-faire</h2>
          <div className="grid grid-cols-2 gap-x-4 gap-y-1">
            {cv.savoir_faire.map((sf, i) => (
              <div key={i} className="flex items-center justify-between text-xs">
                <span className="font-medium text-slate-700">{sf.name}</span>
                <span className="text-slate-400 text-[10px]">{sf.level && sf.level.charAt(0).toUpperCase() + sf.level.slice(1)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
      {cv.savoir_etre?.length > 0 && (
        <div>
          <h2 className="text-xs font-bold uppercase tracking-wider mb-1" style={{ color: "#1e3a5f" }}>Savoir-être professionnels</h2>
          <div className="flex flex-wrap gap-1.5">
            {cv.savoir_etre.map((se, i) => (
              <span key={i} className="text-xs px-2 py-0.5 rounded-full bg-rose-50 text-rose-700 border border-rose-200">{se.name}</span>
            ))}
          </div>
        </div>
      )}
      {cv.experiences?.length > 0 && (
        <div>
          <h2 className="text-xs font-bold uppercase tracking-wider mb-2" style={{ color: "#1e3a5f" }}>Expériences professionnelles</h2>
          {cv.experiences.map((exp, i) => (
            <div key={i} className="mb-3">
              <p className="text-sm font-semibold text-slate-900">{exp.poste}</p>
              <p className="text-xs text-slate-500">{exp.entreprise} — {exp.periode}</p>
              <ul className="mt-1 space-y-0.5">
                {exp.missions?.map((m, j) => (
                  <li key={j} className="text-xs text-slate-600 pl-3 relative before:content-['•'] before:absolute before:left-0 before:text-slate-400">{m}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
      {cv.formations?.length > 0 && (
        <div>
          <h2 className="text-xs font-bold uppercase tracking-wider mb-1" style={{ color: "#1e3a5f" }}>Formation</h2>
          {cv.formations.map((f, i) => (
            <div key={i} className="mb-1">
              <p className="text-sm font-semibold">{f.diplome}</p>
              <p className="text-xs text-slate-500">{[f.etablissement, f.annee].filter(Boolean).join(" — ")}</p>
            </div>
          ))}
        </div>
      )}
      {cv.competences_techniques && Object.keys(cv.competences_techniques).length > 0 && (
        <div>
          <h2 className="text-xs font-bold uppercase tracking-wider mb-1" style={{ color: "#1e3a5f" }}>Compétences techniques</h2>
          {Object.entries(cv.competences_techniques).map(([domain, skills]) => (
            <p key={domain} className="text-xs"><span className="font-semibold">{domain} :</span> {Array.isArray(skills) ? skills.join(", ") : skills}</p>
          ))}
        </div>
      )}
      {cv.langues?.length > 0 && (
        <div>
          <h2 className="text-xs font-bold uppercase tracking-wider mb-1" style={{ color: "#1e3a5f" }}>Langues</h2>
          <p className="text-xs">{cv.langues.map(l => `${l.langue} — ${l.niveau}`).join(" | ")}</p>
        </div>
      )}
    </div>
  );
};

export default CvPreview;
