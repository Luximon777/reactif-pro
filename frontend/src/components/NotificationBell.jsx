import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { API } from "@/App";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Bell, CalendarDays, Check, CheckCheck, X, ChevronRight, Target, MapPin, Shield
} from "lucide-react";
import { useNavigate } from "react-router-dom";

const MATCH_COLORS = {
  fort: "bg-emerald-100 text-emerald-700 border-emerald-200",
  moyen: "bg-blue-100 text-blue-700 border-blue-200",
  faible: "bg-slate-100 text-slate-600 border-slate-200",
};

const NotificationBell = ({ token }) => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [open, setOpen] = useState(false);
  const [toastShown, setToastShown] = useState(false);
  const [filter, setFilter] = useState("all");
  const ref = useRef(null);
  const navigate = useNavigate();

  const loadNotifications = async () => {
    if (!token) return;
    try {
      const res = await axios.get(`${API}/notifications`, { params: { token, limit: 15 }, timeout: 10000 });
      setNotifications(res.data?.notifications || []);
      setUnreadCount(res.data?.unread_count || 0);
    } catch (_) {}
  };

  useEffect(() => {
    if (token) loadNotifications();
    const interval = setInterval(() => { if (token) loadNotifications(); }, 60000);
    return () => clearInterval(interval);
  }, [token]);

  // Show toast for new notifications on first load — adapt copy depending on type
  useEffect(() => {
    if (unreadCount > 0 && !toastShown && notifications.length > 0) {
      setToastShown(true);
      const accessReqUnread = notifications.filter(n => !n.read && n.type === "access_request");
      const ubuntooMsgUnread = notifications.filter(n => !n.read && n.type === "ubuntoo_message");
      const jobDatingUnread = notifications.filter(n => !n.read && (n.type === "job_dating_new" || !n.type));

      import("sonner").then(({ toast }) => {
        if (accessReqUnread.length > 0) {
          toast.info(
            `${accessReqUnread.length} demande${accessReqUnread.length > 1 ? "s" : ""} d'accès à votre profil en attente`,
            {
              action: { label: "Voir", onClick: () => navigate("/dashboard/confidentialite") },
              duration: 6000,
            }
          );
        }
        if (ubuntooMsgUnread.length > 0) {
          toast.info(
            `${ubuntooMsgUnread.length} nouveau${ubuntooMsgUnread.length > 1 ? "x" : ""} message${ubuntooMsgUnread.length > 1 ? "s" : ""} Ubuntoo`,
            {
              action: { label: "Lire", onClick: () => window.location.assign("/ubuntoo") },
              duration: 6000,
            }
          );
        }
        if (jobDatingUnread.length > 0) {
          toast.info(
            `${jobDatingUnread.length} nouveau${jobDatingUnread.length > 1 ? "x" : ""} Job Dating${jobDatingUnread.length > 1 ? "s" : ""} correspond${jobDatingUnread.length > 1 ? "ent" : ""} à votre profil !`,
            {
              action: { label: "Voir", onClick: () => navigate("/dashboard/job-dating") },
              duration: 6000,
            }
          );
        }
      });
    }
  }, [unreadCount, toastShown, notifications, navigate]);

  // Close on outside click
  useEffect(() => {
    const handleClick = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const handleMarkAllRead = async () => {
    try {
      await axios.post(`${API}/notifications/mark-all-read`, null, { params: { token } });
      setNotifications(prev => prev.map(n => ({ ...n, read: true })));
      setUnreadCount(0);
    } catch (_) {}
  };

  const handleClickNotif = async (notif) => {
    if (!notif.read) {
      try {
        await axios.post(`${API}/notifications/mark-read`, null, { params: { token, event_title: notif.event_title } });
        setNotifications(prev => prev.map(n => n.event_title === notif.event_title ? { ...n, read: true } : n));
        setUnreadCount(prev => Math.max(0, prev - 1));
      } catch (_) {}
    }
    setOpen(false);
    if (notif.type === "access_request") {
      navigate("/dashboard/confidentialite");
    } else if (notif.type === "ubuntoo_message") {
      window.location.assign("/ubuntoo");
    } else if (notif.type === "vsi_group_invitation"
            || notif.type === "vsi_group_added"
            || notif.type === "vsi_invitation_accepted"
            || notif.type === "vsi_invitation_declined"
            || notif.type === "vsi_event_created"
            || notif.type === "vsi_event_canceled"
            || notif.type === "vsi_event_reminder_h24"
            || notif.type === "vsi_event_reminder_h1"
            || notif.type === "vsi_cross_event_created"
            || notif.type === "vsi_cross_post"
            || notif.type === "vsi_group_message") {
      window.location.assign("/ubuntoo");
    } else if (notif.type === "mentorship_request"
            || notif.type === "mentorship_accepted"
            || notif.type === "mentorship_declined") {
      window.location.assign("/ubuntoo");
    } else {
      navigate("/dashboard/job-dating");
    }
  };

  const formatTime = (iso) => {
    if (!iso) return "";
    try {
      const d = new Date(iso);
      const now = new Date();
      const diff = Math.floor((now - d) / 60000);
      if (diff < 1) return "À l'instant";
      if (diff < 60) return `Il y a ${diff} min`;
      if (diff < 1440) return `Il y a ${Math.floor(diff / 60)}h`;
      return d.toLocaleDateString("fr-FR", { day: "numeric", month: "short" });
    } catch { return ""; }
  };

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen(!open)}
        className="relative p-2 rounded-lg hover:bg-slate-100 transition-colors"
        data-testid="notification-bell"
      >
        <Bell className={`w-5 h-5 ${unreadCount > 0 ? "text-[#1e3a5f]" : "text-slate-400"}`} />
        {unreadCount > 0 && (
          <span className="absolute -top-0.5 -right-0.5 w-5 h-5 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center animate-pulse" data-testid="notification-count">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-2 w-[360px] bg-white rounded-xl shadow-xl border border-slate-200 z-[100] overflow-hidden" data-testid="notification-dropdown">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100 bg-slate-50/50">
            <h4 className="text-sm font-bold text-slate-800 flex items-center gap-1.5">
              <Bell className="w-4 h-4 text-[#1e3a5f]" />
              Notifications
              {unreadCount > 0 && (
                <Badge className="bg-red-100 text-red-700 text-[10px] ml-1">{unreadCount}</Badge>
              )}
            </h4>
            {unreadCount > 0 && (
              <button
                onClick={handleMarkAllRead}
                className="text-[10px] text-[#1e3a5f] hover:underline font-medium flex items-center gap-0.5"
                data-testid="mark-all-read-btn"
              >
                <CheckCheck className="w-3 h-3" /> Tout marquer lu
              </button>
            )}
          </div>

          {/* Filter tabs */}
          {(() => {
            const counts = {
              all: notifications.length,
              messages: notifications.filter(n => n.type === "ubuntoo_message").length,
              jobdating: notifications.filter(n => n.type === "job_dating_new" || !n.type).length,
              access: notifications.filter(n => n.type === "access_request").length,
            };
            const filterPredicate = {
              all: () => true,
              messages: (n) => n.type === "ubuntoo_message",
              jobdating: (n) => n.type === "job_dating_new" || !n.type,
              access: (n) => n.type === "access_request",
            };
            const filtered = notifications.filter(filterPredicate[filter] || filterPredicate.all);
            const tabs = [
              { id: "all", label: "Tous", count: counts.all },
              { id: "messages", label: "Messages", count: counts.messages },
              { id: "jobdating", label: "Job Dating", count: counts.jobdating },
              { id: "access", label: "Accès", count: counts.access },
            ];
            return (
              <>
                <div className="flex items-center gap-0.5 px-2 py-1.5 border-b border-slate-100 bg-white overflow-x-auto" data-testid="notif-filter-tabs">
                  {tabs.map(t => (
                    <button
                      key={t.id}
                      data-testid={`notif-filter-${t.id}`}
                      onClick={() => setFilter(t.id)}
                      className={`px-2 py-1 rounded-md text-[10px] font-medium whitespace-nowrap transition-colors ${
                        filter === t.id ? "bg-[#1e3a5f] text-white" : "text-slate-500 hover:bg-slate-100"
                      }`}
                    >
                      {t.label} {t.count > 0 && <span className={`ml-0.5 ${filter === t.id ? "opacity-90" : "text-slate-400"}`}>({t.count})</span>}
                    </button>
                  ))}
                </div>

                {/* Notifications list */}
                <div className="max-h-[340px] overflow-y-auto">
                  {filtered.length === 0 ? (
                    <div className="py-10 text-center">
                      <Bell className="w-8 h-8 text-slate-200 mx-auto mb-2" />
                      <p className="text-xs text-slate-400 mb-2">{filter === "all" ? "Aucune notification" : "Aucune notification dans cette catégorie"}</p>
                      <button
                        onClick={() => { setOpen(false); navigate("/dashboard/notifications"); }}
                        className="text-[11px] text-[#1e3a5f] hover:underline font-medium"
                        data-testid="empty-history-link"
                      >
                        Voir l'historique complet →
                      </button>
                    </div>
                  ) : (
                    filtered.map((notif, i) => {
                const isAccessReq = notif.type === "access_request";
                const isUbuntooMsg = notif.type === "ubuntoo_message";
                return (
                <button
                  key={i}
                  onClick={() => handleClickNotif(notif)}
                  className={`w-full text-left px-4 py-3 border-b border-slate-50 hover:bg-slate-50/80 transition-colors flex gap-3 ${
                    !notif.read ? "bg-blue-50/30" : ""
                  }`}
                  data-testid={`notification-item-${i}`}
                >
                  <div className={`shrink-0 w-8 h-8 rounded-lg flex items-center justify-center mt-0.5 ${
                    isAccessReq ? "bg-amber-100" :
                    isUbuntooMsg ? "bg-violet-100" :
                    notif.match_level === "fort" ? "bg-emerald-100" : notif.match_level === "moyen" ? "bg-blue-100" : "bg-slate-100"
                  }`}>
                    {isAccessReq ? (
                      <Shield className="w-4 h-4 text-amber-600" />
                    ) : isUbuntooMsg ? (
                      <Target className="w-4 h-4 text-violet-600" />
                    ) : (
                      <CalendarDays className={`w-4 h-4 ${
                        notif.match_level === "fort" ? "text-emerald-600" : notif.match_level === "moyen" ? "text-blue-600" : "text-slate-500"
                      }`} />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className={`text-xs leading-relaxed ${!notif.read ? "font-semibold text-slate-900" : "text-slate-600"}`}>
                      {notif.title}
                    </p>
                    <p className="text-[10px] text-slate-500 mt-0.5 line-clamp-1">{notif.message}</p>
                    <div className="flex items-center gap-2 mt-1">
                      {isAccessReq ? (
                        <Badge className="text-[9px] px-1.5 py-0 bg-amber-100 text-amber-700 border-amber-200">
                          <Shield className="w-2.5 h-2.5 mr-0.5" />
                          Accès profil
                        </Badge>
                      ) : isUbuntooMsg ? (
                        <Badge className="text-[9px] px-1.5 py-0 bg-violet-100 text-violet-700 border-violet-200">
                          Message Ubuntoo
                        </Badge>
                      ) : (
                        <Badge className={`text-[9px] px-1.5 py-0 ${MATCH_COLORS[notif.match_level] || MATCH_COLORS.faible}`}>
                          <Target className="w-2.5 h-2.5 mr-0.5" />
                          {notif.match_score}%
                        </Badge>
                      )}
                      <span className="text-[10px] text-slate-400">{formatTime(notif.created_at)}</span>
                    </div>
                  </div>
                  {!notif.read && (
                    <div className="shrink-0 w-2 h-2 rounded-full bg-[#1e3a5f] mt-2" />
                  )}
                </button>
                );
              })
            )}
          </div>

          {/* Footer adaptatif au filtre actif */}
          {filtered.length > 0 && (() => {
            const hasAccessReq = filtered.some(n => n.type === "access_request");
            const hasUbuntoo = filtered.some(n => n.type === "ubuntoo_message");
            let target = "/dashboard/job-dating";
            let label = "Voir tous les Job Dating";
            let isExternal = false;
            if (filter === "messages" || (filter === "all" && hasUbuntoo)) { target = "/ubuntoo"; label = "Ouvrir Ubuntoo"; isExternal = true; }
            else if (filter === "access" || (filter === "all" && hasAccessReq && !hasUbuntoo)) { target = "/dashboard/confidentialite"; label = "Gérer les accès partenaires"; }
            return (
              <div className="px-4 py-2.5 border-t border-slate-100 bg-slate-50/50 flex items-center justify-between gap-2">
                <button
                  onClick={() => { setOpen(false); if (isExternal) { window.location.assign(target); } else { navigate(target); } }}
                  className="text-xs text-[#1e3a5f] font-medium hover:underline flex items-center gap-1"
                  data-testid="view-all-jobdating-btn"
                >
                  {label} <ChevronRight className="w-3 h-3" />
                </button>
                <button
                  onClick={() => { setOpen(false); navigate("/dashboard/notifications"); }}
                  className="text-[10px] text-slate-500 hover:underline"
                  data-testid="open-notif-history-btn"
                >
                  Historique
                </button>
              </div>
            );
          })()}
              </>
            );
          })()}
        </div>
      )}
    </div>
  );
};

export default NotificationBell;
