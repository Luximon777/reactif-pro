import { Routes, Route, Navigate, useNavigate } from "react-router-dom";
import { UbuntooSocialProvider, useAuth } from "./UbuntooSocialContext";
import { UbuntooNavbar } from "./Navbar";
import { Button } from "@/components/ui/button";
import Feed from "./Feed";
import Messages from "./Messages";
import Groups from "./Groups";
import GroupDetail from "./GroupDetail";
import DiscussionDetail from "./DiscussionDetail";
import Community from "./Community";
import Profile from "./Profile";
import Search from "./Search";

const Shell = () => {
  const { user, loading, error, retrySso } = useAuth();
  const navigate = useNavigate();

  if (loading) {
    return (
      <div className="min-h-screen bg-[#FDFBF7] flex items-center justify-center" data-testid="ubuntoo-loading">
        <div className="w-12 h-12 border-4 border-[#0F4C5C] border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-[#FDFBF7] flex flex-col items-center justify-center gap-4 px-6 text-center" data-testid="ubuntoo-auth-error">
        <img src="https://customer-assets.emergentagent.com/job_keen-meitner-5/artifacts/t3wjk59k_logo_ubuntoo_transparent.png" alt="Ubuntoo" className="h-12 w-auto" />
        <p className="text-sm text-slate-600 max-w-sm">
          {error === "no_session"
            ? "Connectez-vous à Ré'Actif Pro pour accéder à l'espace Ubuntoo."
            : "Impossible d'ouvrir votre session Ubuntoo pour le moment."}
        </p>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => navigate("/")} data-testid="ubuntoo-goto-login">Se connecter</Button>
          {error === "sso_failed" && <Button onClick={retrySso} data-testid="ubuntoo-retry-sso">Réessayer</Button>}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#FDFBF7]">
      <UbuntooNavbar />
      <Routes>
        <Route index element={<Feed />} />
        <Route path="groups" element={<Groups />} />
        <Route path="groups/:groupId" element={<GroupDetail />} />
        <Route path="discussions/:discussionId" element={<DiscussionDetail />} />
        <Route path="messages" element={<Messages />} />
        <Route path="community" element={<Community />} />
        <Route path="search" element={<Search />} />
        <Route path="profile" element={<Profile />} />
        <Route path="*" element={<Navigate to="/ubuntoo" replace />} />
      </Routes>
    </div>
  );
};

export default function UbuntooSocialApp() {
  return (
    <UbuntooSocialProvider>
      <Shell />
    </UbuntooSocialProvider>
  );
}
