import React, { useState, useEffect, useCallback } from "react";
import { Routes, Route, NavLink, useNavigate } from "react-router-dom";
import { Home, Users, Compass, MessageSquare, User, Bell, ArrowLeft, HeartHandshake } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { u2, timeAgo } from "./api";
import Accueil from "./pages/Accueil";
import Reseau from "./pages/Reseau";
import Communautes from "./pages/Communautes";
import CommunauteDetail from "./pages/CommunauteDetail";
import MessagesU from "./pages/MessagesU";
import ProfilU from "./pages/ProfilU";
import "./ubuntoo2.css";

const TABS = [
  { to: "/ubuntoo", end: true, label: "Accueil", icon: Home, testid: "nav-tab-accueil" },
  { to: "/ubuntoo/reseau", label: "Réseau", icon: Users, testid: "nav-tab-reseau" },
  { to: "/ubuntoo/communautes", label: "Communautés", icon: Compass, testid: "nav-tab-communautes" },
  { to: "/ubuntoo/messages", label: "Messages", icon: MessageSquare, testid: "nav-tab-messages" },
  { to: "/ubuntoo/profil", label: "Profil", icon: User, testid: "nav-tab-profil" },
];

const NotificationsBell = ({ unread, onOpened }) => {
  const [notifs, setNotifs] = useState([]);
  const load = async () => {
    try {
      const res = await u2.get("/notifications");
      setNotifs(res.data);
      await u2.post("/notifications/mark-read");
      onOpened?.();
    } catch { /* silent */ }
  };
  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="icon" className="relative rounded-full" onClick={load} data-testid="notifications-bell">
          <Bell className="w-5 h-5 text-stone-600" />
          {unread > 0 && <span className="absolute -top-0.5 -right-0.5 h-4 min-w-4 px-1 rounded-full bg-[#C85A32] text-white text-[10px] font-bold flex items-center justify-center">{unread}</span>}
        </Button>
      </PopoverTrigger>
      <PopoverContent align="end" className="w-80 p-0 rounded-xl" data-testid="notifications-panel">
        <div className="px-4 py-3 border-b border-stone-100 text-sm font-semibold u2-heading">Notifications</div>
        <div className="max-h-80 overflow-y-auto">
          {notifs.length === 0 && <p className="text-sm text-stone-400 text-center py-6">Aucune notification</p>}
          {notifs.map(n => (
            <div key={n.id} className={`px-4 py-3 border-b border-stone-50 text-sm ${n.read ? "text-stone-500" : "text-stone-800 bg-orange-50/50"}`}>
              <p className="leading-snug">{n.text}</p>
              <p className="text-[11px] text-stone-400 mt-1">{timeAgo(n.created_at)}</p>
            </div>
          ))}
        </div>
      </PopoverContent>
    </Popover>
  );
};

export default function UbuntooV2App() {
  const navigate = useNavigate();
  const [unread, setUnread] = useState(0);
  const [unreadMsgs, setUnreadMsgs] = useState(0);

  const refreshCounts = useCallback(async () => {
    try {
      const res = await u2.get("/dashboard");
      setUnread(res.data.unread_notifications || 0);
      setUnreadMsgs(res.data.unread_messages || 0);
    } catch { /* silent */ }
  }, []);

  useEffect(() => {
    refreshCounts();
    const iv = setInterval(refreshCounts, 30000);
    return () => clearInterval(iv);
  }, [refreshCounts]);

  return (
    <div className="u2-root">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-[#E2DFD8]">
        <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between gap-3">
          <div className="flex items-center gap-2 min-w-0">
            <Button variant="ghost" size="icon" className="rounded-full shrink-0" onClick={() => navigate("/dashboard")} data-testid="back-to-reactif-btn" title="Retour à Ré'Actif Pro">
              <ArrowLeft className="w-4 h-4 text-stone-500" />
            </Button>
            <div className="flex items-center gap-2 min-w-0">
              <div className="h-8 w-8 rounded-xl bg-[#C85A32] flex items-center justify-center shrink-0">
                <HeartHandshake className="w-4.5 h-4.5 text-white w-4 h-4" />
              </div>
              <div className="min-w-0">
                <div className="text-base font-extrabold u2-heading tracking-tight leading-none">UBUNTOO</div>
                <div className="text-[10px] text-stone-400 truncate hidden sm:block">« Je suis parce que nous sommes »</div>
              </div>
            </div>
          </div>
          {/* Desktop nav */}
          <nav className="hidden sm:flex items-center gap-1">
            {TABS.map(t => (
              <NavLink key={t.to} to={t.to} end={t.end} data-testid={`${t.testid}-desktop`}
                className={({ isActive }) => `relative px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${isActive ? "bg-[#C85A32] text-white" : "text-stone-600 hover:bg-stone-100"}`}>
                {t.label}
                {t.label === "Messages" && unreadMsgs > 0 && <span className="absolute -top-1 -right-1 h-4 min-w-4 px-1 rounded-full bg-[#E09F3E] text-white text-[10px] font-bold flex items-center justify-center">{unreadMsgs}</span>}
              </NavLink>
            ))}
          </nav>
          <NotificationsBell unread={unread} onOpened={() => setUnread(0)} />
        </div>
      </header>

      {/* Content */}
      <main className="max-w-5xl mx-auto px-4 py-5 pb-24 sm:pb-10">
        <Routes>
          <Route index element={<Accueil />} />
          <Route path="reseau" element={<Reseau />} />
          <Route path="communautes" element={<Communautes />} />
          <Route path="communautes/:commId" element={<CommunauteDetail />} />
          <Route path="messages" element={<MessagesU onRead={refreshCounts} />} />
          <Route path="profil" element={<ProfilU />} />
        </Routes>
      </main>

      {/* Bottom nav mobile */}
      <nav className="fixed bottom-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-md border-t border-[#E2DFD8] px-2 py-1.5 shadow-lg sm:hidden flex justify-around items-center h-16" data-testid="bottom-nav">
        {TABS.map(t => {
          const Icon = t.icon;
          return (
            <NavLink key={t.to} to={t.to} end={t.end} data-testid={t.testid}
              className={({ isActive }) => `relative flex flex-col items-center gap-0.5 px-3 py-1.5 rounded-xl min-w-[56px] ${isActive ? "text-[#C85A32]" : "text-stone-500"}`}>
              <Icon className="w-5 h-5" />
              <span className="text-[10px] font-medium">{t.label}</span>
              {t.label === "Messages" && unreadMsgs > 0 && <span className="absolute top-0 right-1 h-4 min-w-4 px-1 rounded-full bg-[#C85A32] text-white text-[10px] font-bold flex items-center justify-center">{unreadMsgs}</span>}
            </NavLink>
          );
        })}
      </nav>
    </div>
  );
}
