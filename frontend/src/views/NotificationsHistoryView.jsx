import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { API } from "@/App";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Bell, Search, Archive, ArchiveRestore, Shield, CalendarDays, Target,
  ChevronLeft, ChevronRight, Inbox, X, ExternalLink
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { formatDistanceToNow } from "date-fns";
import { fr } from "date-fns/locale";

const TYPE_META = {
  ubuntoo_message: { label: "Message Ubuntoo", color: "bg-violet-100 text-violet-700 border-violet-200", Icon: Target, target: "/ubuntoo" },
  access_request: { label: "Demande d'accès", color: "bg-amber-100 text-amber-700 border-amber-200", Icon: Shield, target: "/dashboard/confidentialite" },
  job_dating_new: { label: "Job Dating", color: "bg-emerald-100 text-emerald-700 border-emerald-200", Icon: CalendarDays, target: "/dashboard/job-dating" },
  default: { label: "Notification", color: "bg-slate-100 text-slate-600 border-slate-200", Icon: Bell, target: null },
};

const formatTime = (iso) => {
  try { return formatDistanceToNow(new Date(iso), { addSuffix: true, locale: fr }); } catch (_) { return ""; }
};

const NotificationsHistoryView = ({ token }) => {
  const navigate = useNavigate();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [typeFilter, setTypeFilter] = useState("all");
  const [status, setStatus] = useState("active");
  const [read, setRead] = useState("all");
  const [search, setSearch] = useState("");
  const [searchDebounced, setSearchDebounced] = useState("");

  // Debounce search
  useEffect(() => {
    const t = setTimeout(() => setSearchDebounced(search), 350);
    return () => clearTimeout(t);
  }, [search]);

  const load = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const params = { token, page, page_size: 20, status };
      if (typeFilter !== "all") params.type_filter = typeFilter;
      if (read !== "all") params.read = read;
      if (searchDebounced.trim()) params.search = searchDebounced.trim();
      const res = await axios.get(`${API}/notifications/history`, { params });
      setItems(res.data?.items || []);
      setPages(res.data?.pages || 1);
      setTotal(res.data?.total || 0);
    } catch (_) {} finally { setLoading(false); }
  }, [token, page, status, typeFilter, read, searchDebounced]);

  useEffect(() => { load(); }, [load]);
  useEffect(() => { setPage(1); }, [status, typeFilter, read, searchDebounced]);

  const handleClick = async (notif) => {
    if (!notif.read) {
      try {
        await axios.post(`${API}/notifications/mark-read`, null, { params: { token, event_title: notif.event_title } });
      } catch (_) {}
    }
    const meta = TYPE_META[notif.type] || TYPE_META.default;
    if (meta.target) {
      if (meta.target.startsWith("/ubuntoo")) window.location.assign(meta.target);
      else navigate(meta.target);
    } else {
      load();
    }
  };

  const archive = async (id) => {
    try {
      await axios.post(`${API}/notifications/${id}/archive`, null, { params: { token } });
      load();
    } catch (_) {}
  };
  const unarchive = async (id) => {
    try {
      await axios.post(`${API}/notifications/${id}/unarchive`, null, { params: { token } });
      load();
    } catch (_) {}
  };

  const typeTabs = [
    { id: "all", label: "Tous types" },
    { id: "ubuntoo_message", label: "Messages" },
    { id: "job_dating", label: "Job Dating" },
    { id: "access_request", label: "Accès" },
  ];

  return (
    <div className="space-y-6 animate-fade-in" data-testid="notifications-history-view">
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <Bell className="w-6 h-6 text-[#1e3a5f]" />
            Historique des notifications
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Toutes vos notifications, archivées comprises. {total} résultat{total > 1 ? "s" : ""}.
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={() => navigate(-1)} data-testid="notif-history-back">
          <ChevronLeft className="w-4 h-4 mr-1" /> Retour
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4 space-y-3">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <Input
              data-testid="notif-history-search"
              placeholder="Rechercher dans titre ou message…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 pr-9"
            />
            {search && (
              <button
                onClick={() => setSearch("")}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-700"
                aria-label="Effacer"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          <div className="flex flex-wrap gap-4 items-center">
            {/* Type tabs */}
            <div className="flex gap-1" data-testid="notif-history-type-tabs">
              {typeTabs.map(t => (
                <button
                  key={t.id}
                  data-testid={`notif-history-type-${t.id}`}
                  onClick={() => setTypeFilter(t.id)}
                  className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                    typeFilter === t.id ? "bg-[#1e3a5f] text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </div>

            {/* Read filter */}
            <select
              data-testid="notif-history-read-filter"
              value={read}
              onChange={(e) => setRead(e.target.value)}
              className="text-xs border border-slate-200 rounded-md px-2 py-1.5 bg-white"
            >
              <option value="all">Toutes</option>
              <option value="unread">Non lues</option>
              <option value="read">Lues</option>
            </select>

            {/* Status filter */}
            <div className="ml-auto flex gap-1" data-testid="notif-history-status-tabs">
              {[
                { id: "active", label: "Boîte" },
                { id: "archived", label: "Archives" },
                { id: "all", label: "Tout" },
              ].map(s => (
                <button
                  key={s.id}
                  data-testid={`notif-history-status-${s.id}`}
                  onClick={() => setStatus(s.id)}
                  className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                    status === s.id ? "bg-emerald-600 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                  }`}
                >
                  {s.label}
                </button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* List */}
      <Card>
        <CardContent className="p-0">
          {loading ? (
            <div className="py-12 text-center text-slate-400 text-sm">Chargement…</div>
          ) : items.length === 0 ? (
            <div className="py-16 text-center" data-testid="notif-history-empty">
              <Inbox className="w-10 h-10 text-slate-200 mx-auto mb-3" />
              <p className="text-sm text-slate-400">
                {status === "archived" ? "Aucune notification archivée." : "Aucune notification trouvée."}
              </p>
            </div>
          ) : (
            <ul>
              {items.map((notif, i) => {
                const meta = TYPE_META[notif.type] || TYPE_META.default;
                const Icon = meta.Icon;
                return (
                  <li key={notif.id || i} className={`border-b border-slate-50 last:border-0 ${!notif.read ? "bg-blue-50/30" : ""}`}>
                    <div className="flex items-start gap-3 px-4 py-3" data-testid={`notif-history-item-${i}`}>
                      <div className={`shrink-0 w-9 h-9 rounded-lg flex items-center justify-center ${meta.color.split(" ")[0]}`}>
                        <Icon className={`w-4 h-4 ${meta.color.split(" ")[1]}`} />
                      </div>
                      <button
                        className="flex-1 text-left min-w-0"
                        onClick={() => handleClick(notif)}
                      >
                        <div className="flex items-center gap-2 flex-wrap">
                          <p className={`text-sm ${!notif.read ? "font-semibold text-slate-900" : "text-slate-700"}`}>
                            {notif.title}
                          </p>
                          <Badge className={`text-[10px] ${meta.color}`}>{meta.label}</Badge>
                          {notif.archived && <Badge className="text-[10px] bg-slate-100 text-slate-500 border-slate-200">Archivée</Badge>}
                          {!notif.read && <span className="w-2 h-2 rounded-full bg-[#1e3a5f]" />}
                        </div>
                        <p className="text-xs text-slate-500 mt-0.5 line-clamp-2">{notif.message}</p>
                        <p className="text-[11px] text-slate-400 mt-1">{formatTime(notif.created_at)}</p>
                      </button>
                      <div className="flex flex-col gap-1">
                        {meta.target && (
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handleClick(notif)}
                            data-testid={`notif-history-open-${i}`}
                            title="Ouvrir"
                          >
                            <ExternalLink className="w-4 h-4" />
                          </Button>
                        )}
                        {notif.archived ? (
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => unarchive(notif.id)}
                            data-testid={`notif-history-unarchive-${i}`}
                            title="Désarchiver"
                          >
                            <ArchiveRestore className="w-4 h-4" />
                          </Button>
                        ) : (
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => archive(notif.id)}
                            data-testid={`notif-history-archive-${i}`}
                            title="Archiver"
                          >
                            <Archive className="w-4 h-4" />
                          </Button>
                        )}
                      </div>
                    </div>
                  </li>
                );
              })}
            </ul>
          )}
        </CardContent>
      </Card>

      {/* Pagination */}
      {pages > 1 && (
        <div className="flex justify-center items-center gap-2" data-testid="notif-history-pagination">
          <Button
            size="sm"
            variant="outline"
            disabled={page <= 1}
            onClick={() => setPage(p => Math.max(1, p - 1))}
            data-testid="notif-history-prev-page"
          >
            <ChevronLeft className="w-4 h-4" /> Précédent
          </Button>
          <span className="text-xs text-slate-500">Page {page} / {pages}</span>
          <Button
            size="sm"
            variant="outline"
            disabled={page >= pages}
            onClick={() => setPage(p => Math.min(pages, p + 1))}
            data-testid="notif-history-next-page"
          >
            Suivant <ChevronRight className="w-4 h-4" />
          </Button>
        </div>
      )}
    </div>
  );
};

export default NotificationsHistoryView;
