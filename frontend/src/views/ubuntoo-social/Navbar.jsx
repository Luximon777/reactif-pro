import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "./UbuntooSocialContext";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Home, Users, MessageCircle, Globe, Search as SearchIcon, ArrowLeft } from "lucide-react";

const NAV = [
  { to: "/ubuntoo", label: "Fil", icon: Home, exact: true },
  { to: "/ubuntoo/groups", label: "Groupes", icon: Users },
  { to: "/ubuntoo/messages", label: "Messages", icon: MessageCircle },
  { to: "/ubuntoo/community", label: "Communauté", icon: Globe },
  { to: "/ubuntoo/search", label: "Recherche", icon: SearchIcon },
];

export const UbuntooNavbar = () => {
  const { user } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <nav className="sticky top-0 z-40 bg-white border-b border-slate-200 shadow-sm" data-testid="ubuntoo-navbar">
      <div className="max-w-5xl mx-auto px-4 flex items-center justify-between h-14">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate("/dashboard")}
            className="flex items-center gap-1 text-xs text-slate-500 hover:text-[#0F4C5C] transition-colors"
            data-testid="ubuntoo-back-btn"
            title="Retour à Ré'Actif Pro"
          >
            <ArrowLeft className="w-4 h-4" />
            <span className="hidden sm:inline">Ré'Actif Pro</span>
          </button>
          <Link to="/ubuntoo" className="flex items-center gap-2" data-testid="ubuntoo-logo">
            <img
              src="https://customer-assets.emergentagent.com/job_keen-meitner-5/artifacts/t3wjk59k_logo_ubuntoo_transparent.png"
              alt="Ubuntoo"
              className="h-7 w-auto"
            />
            <div className="hidden md:block">
              <p className="text-sm font-bold text-[#0F4C5C] leading-none">UBUNTOO</p>
              <p className="text-[9px] text-slate-400 leading-none mt-0.5">Je suis parce que nous sommes</p>
            </div>
          </Link>
        </div>

        <div className="flex items-center gap-0.5 sm:gap-1">
          {NAV.map((item) => {
            const active = item.exact ? location.pathname === item.to : location.pathname.startsWith(item.to);
            const Icon = item.icon;
            return (
              <Link
                key={item.to}
                to={item.to}
                className={`flex items-center gap-1.5 px-2 sm:px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                  active ? "bg-[#0F4C5C] text-white" : "text-slate-600 hover:bg-slate-100"
                }`}
                data-testid={`ubuntoo-nav-${item.label.toLowerCase()}`}
              >
                <Icon className="w-4 h-4" />
                <span className="hidden lg:inline">{item.label}</span>
              </Link>
            );
          })}
          <Link to="/ubuntoo/profile" className="ml-1" data-testid="ubuntoo-nav-profil">
            <Avatar className="w-8 h-8 border-2 border-[#0F4C5C]/20 hover:border-[#0F4C5C] transition-colors">
              <AvatarFallback className="bg-[#0F4C5C] text-white text-xs">
                {user?.full_name?.charAt(0)?.toUpperCase() || "U"}
              </AvatarFallback>
            </Avatar>
          </Link>
        </div>
      </div>
    </nav>
  );
};
