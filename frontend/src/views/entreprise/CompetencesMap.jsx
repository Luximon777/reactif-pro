import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Brain, Users, BarChart3, Loader2 } from "lucide-react";

const CompetencesMap = ({ token }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${API}/entreprise/competences-map?token=${token}`)
      .then(r => setData(r.data)).catch(() => {}).finally(() => setLoading(false));
  }, [token]);

  if (loading) return <div className="flex justify-center py-20"><Loader2 className="w-8 h-8 animate-spin text-emerald-600" /></div>;
  if (!data) return null;

  const maxCount = Math.max(...(data.hard_skills || []).map(s => s.count), 1);

  return (
    <div className="space-y-6" data-testid="competences-map">
      <div>
        <h1 className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>Competences & Cartographie</h1>
        <p className="text-sm text-slate-500">{data.total_collaborateurs} collaborateur{data.total_collaborateurs !== 1 ? "s" : ""} analyses</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Hard Skills */}
        <Card className="border border-slate-100" data-testid="hard-skills-card">
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2"><BarChart3 className="w-4 h-4 text-emerald-600" /> Hard Skills</CardTitle>
            <CardDescription>Competences techniques detectees</CardDescription>
          </CardHeader>
          <CardContent>
            {(data.hard_skills || []).length === 0 ? <p className="text-sm text-slate-400 text-center py-6">Aucune compétence</p> : (
              <div className="space-y-2">
                {data.hard_skills.slice(0, 15).map((s, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <span className="text-sm text-slate-700 w-40 truncate">{s.name}</span>
                    <div className="flex-1 h-5 bg-slate-100 rounded-full overflow-hidden">
                      <div className="h-full bg-emerald-500 rounded-full transition-all"
                        style={{ width: `${(s.count / maxCount) * 100}%` }} />
                    </div>
                    <span className="text-xs text-slate-500 w-6 text-right">{s.count}</span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Soft Skills */}
        <Card className="border border-slate-100" data-testid="soft-skills-card">
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2"><Brain className="w-4 h-4 text-indigo-600" /> Soft Skills D'CLIC PRO</CardTitle>
            <CardDescription>Competences transversales issues des tests</CardDescription>
          </CardHeader>
          <CardContent>
            {(data.soft_skills || []).length === 0 ? <p className="text-sm text-slate-400 text-center py-6">Aucune</p> : (
              <div className="flex flex-wrap gap-2">
                {data.soft_skills.map((s, i) => (
                  <Badge key={i} className="bg-indigo-50 text-indigo-700 border border-indigo-200 text-sm py-1.5 px-3">
                    {s.name} <span className="ml-1 opacity-60">x{s.count}</span>
                  </Badge>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* By Department */}
      {Object.keys(data.by_department || {}).length > 0 && (
        <Card className="border border-slate-100" data-testid="dept-skills">
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2"><Users className="w-4 h-4 text-emerald-600" /> Par département</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(data.by_department).map(([dept, skills]) => (
                <div key={dept} className="p-3 rounded-lg bg-slate-50 border border-slate-100">
                  <h4 className="text-sm font-semibold text-slate-800 mb-2">{dept}</h4>
                  <div className="flex flex-wrap gap-1">
                    {skills.slice(0, 6).map(([name, count], i) => (
                      <Badge key={i} variant="secondary" className="text-[10px]">{name} ({count})</Badge>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default CompetencesMap;
