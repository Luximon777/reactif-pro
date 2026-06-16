import { useEffect, useState, createContext, useContext } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";
import { Toaster } from "@/components/ui/sonner";
import { toast } from "sonner";
import Landing from "@/pages/Landing";
import Dashboard from "@/pages/Dashboard";
import SharedPassportPage from "@/pages/SharedPassportPage";
import SharedTrajectoryPage from "@/pages/SharedTrajectoryPage";
import DclicTestPage from "@/pages/DclicTestPage";
import UbuntooPage from "@/pages/UbuntooPage";
import OpcPublicPage from "@/pages/OpcPublicPage";
import OpcDediePage from "@/pages/OpcDediePage";
import AdminGate from "@/components/AdminGate";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "";
export const API = `${BACKEND_URL}/api`;

// Auth Context
export const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
};

const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(localStorage.getItem("reactif_token"));
  const [role, setRole] = useState(localStorage.getItem("reactif_role") || "particulier");
  const [profileId, setProfileId] = useState(localStorage.getItem("reactif_profile_id"));
  const [authMode, setAuthMode] = useState(localStorage.getItem("reactif_auth_mode") || "anonymous");
  const [pseudo, setPseudo] = useState(localStorage.getItem("reactif_pseudo") || null);
  const [identityLevel, setIdentityLevel] = useState(localStorage.getItem("reactif_identity_level") || "none");
  const [isLoading, setIsLoading] = useState(true);
  const [adminStatus, setAdminStatus] = useState(localStorage.getItem("reactif_admin_status") || null);
  const [isReadOnly, setIsReadOnly] = useState(localStorage.getItem("reactif_read_only") === "true");

  useEffect(() => {
    const verifyToken = async () => {
      if (token) {
        try {
          const response = await axios.get(`${API}/auth/verify?token=${token}`);
          if (response.data.valid) {
            setRole(response.data.role);
            setProfileId(response.data.profile_id);
            setAuthMode(response.data.auth_mode || "anonymous");
            setPseudo(response.data.pseudo || null);
            setIdentityLevel(response.data.identity_level || "none");
            localStorage.setItem("reactif_auth_mode", response.data.auth_mode || "anonymous");
            if (response.data.pseudo) localStorage.setItem("reactif_pseudo", response.data.pseudo);
            if (response.data.identity_level) localStorage.setItem("reactif_identity_level", response.data.identity_level);
          } else {
            logout();
          }
        } catch {
          logout();
        }
      }
      setIsLoading(false);
    };
    verifyToken();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Anonymous login (existing behavior)
  const login = async (selectedRole = "particulier") => {
    try {
      const response = await axios.post(`${API}/auth/anonymous`, { role: selectedRole });
      const { token: newToken, role: newRole, profile_id, auth_mode: am } = response.data;
      setAuthState(newToken, newRole, profile_id, am || "anonymous", null, "none");
      return true;
    } catch (error) {
      console.error("Login error:", error);
      return false;
    }
  };

  // Pseudonymous registration
  const register = async (pseudoName, password, selectedRole = "particulier", emailRecovery = null, consentMarketing = false, identifiantFT = null) => {
    try {
      const response = await axios.post(`${API}/auth/register`, {
        pseudo: pseudoName,
        password,
        role: selectedRole,
        email_recovery: emailRecovery || null,
        identifiant_france_travail: identifiantFT || null,
        consent_cgu: true,
        consent_privacy: true,
        consent_marketing: consentMarketing
      });
      const { token: newToken, role: newRole, profile_id, pseudo: p, auth_mode: am } = response.data;
      setAuthState(newToken, newRole, profile_id, am || "pseudo", p, "none");
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || "Erreur lors de l'inscription" };
    }
  };

  // Pseudonymous login
  const loginPseudo = async (pseudoName, password, targetRole) => {
    try {
      const response = await axios.post(`${API}/auth/login`, {
        pseudo: pseudoName,
        password
      });
      const { token: newToken, role: newRole, profile_id, pseudo: p, auth_mode: am } = response.data;
      
      // If targetRole is specified and different from current role, switch role
      let finalRole = newRole;
      if (targetRole && targetRole !== newRole) {
        try {
          await axios.post(`${API}/auth/switch-role?token=${newToken}&new_role=${targetRole}`);
          finalRole = targetRole;
        } catch {
          // Switch failed, use original role
        }
      }
      
      setAuthState(newToken, finalRole, profile_id, am || "pseudo", p, "none");
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || "Pseudo ou mot de passe incorrect" };
    }
  };

  // Upgrade anonymous to pseudo
  const upgradeAccount = async (pseudoName, password, emailRecovery = null) => {
    try {
      await axios.post(`${API}/auth/upgrade?token=${token}`, {
        pseudo: pseudoName,
        password,
        email_recovery: emailRecovery || null,
        consent_cgu: true,
        consent_privacy: true
      });
      setAuthMode("pseudo");
      setPseudo(pseudoName);
      localStorage.setItem("reactif_auth_mode", "pseudo");
      localStorage.setItem("reactif_pseudo", pseudoName);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || "Erreur lors de la mise à niveau" };
    }
  };

  // Entreprise registration
  const registerEntreprise = async (data) => {
    try {
      const response = await axios.post(`${API}/auth/register-entreprise`, data);
      const { token: t, role: r, profile_id, auth_mode: am } = response.data;
      setAuthState(t, r, profile_id, am || "pseudo", data.email, "none");
      return { success: true, emailWarning: response.data.email_warning };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || "Erreur lors de l'inscription" };
    }
  };

  // Partenaire registration
  const registerPartenaire = async (data) => {
    try {
      const response = await axios.post(`${API}/auth/register-partenaire`, data);
      const { token: t, role: r, profile_id, auth_mode: am } = response.data;
      setAuthState(t, r, profile_id, am || "pseudo", data.email, "none");
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || "Erreur lors de l'inscription" };
    }
  };

  // Login for entreprise/partenaire (by email)
  const loginPro = async (email, password) => {
    try {
      const response = await axios.post(`${API}/auth/login-pro`, {
        pseudo: email,
        password
      });
      const { token: t, role: r, profile_id, pseudo: p, auth_mode: am, company_name } = response.data;
      const displayName = company_name || p;
      setAuthState(t, r, profile_id, am || "pseudo", displayName, "none");
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || "Email ou mot de passe incorrect" };
    }
  };

  const setAuthState = (newToken, newRole, profileId, am, p, il) => {
    setToken(newToken);
    setRole(newRole);
    setProfileId(profileId);
    setAuthMode(am);
    setPseudo(p);
    setIdentityLevel(il);
    localStorage.setItem("reactif_token", newToken);
    localStorage.setItem("reactif_role", newRole);
    localStorage.setItem("reactif_profile_id", profileId);
    localStorage.setItem("reactif_auth_mode", am);
    if (p) localStorage.setItem("reactif_pseudo", p);
    if (il) localStorage.setItem("reactif_identity_level", il);
  };

  const switchRole = async (newRole) => {
    try {
      await axios.post(`${API}/auth/switch-role?token=${token}&new_role=${newRole}`);
      setRole(newRole);
      localStorage.setItem("reactif_role", newRole);
      return true;
    } catch (error) {
      console.error("Switch role error:", error);
      return false;
    }
  };

  const loginFromGate = (data) => {
    setToken(data.token);
    setRole(data.role);
    setProfileId(data.profileId);
    setAuthMode(data.authMode || "pseudo");
    setPseudo(data.pseudo || null);
    setAdminStatus(data.adminStatus);
    setIsReadOnly(data.isReadOnly || false);
    localStorage.setItem("reactif_token", data.token);
    localStorage.setItem("reactif_role", data.role);
    localStorage.setItem("reactif_profile_id", data.profileId);
    localStorage.setItem("reactif_auth_mode", data.authMode || "pseudo");
    if (data.pseudo) localStorage.setItem("reactif_pseudo", data.pseudo);
    localStorage.setItem("reactif_admin_status", data.adminStatus);
    localStorage.setItem("reactif_read_only", String(data.isReadOnly || false));
  };

  const logout = () => {
    setToken(null);
    setRole("particulier");
    setProfileId(null);
    setAuthMode("anonymous");
    setPseudo(null);
    setIdentityLevel("none");
    setAdminStatus(null);
    setIsReadOnly(false);
    localStorage.removeItem("reactif_token");
    localStorage.removeItem("reactif_role");
    localStorage.removeItem("reactif_profile_id");
    localStorage.removeItem("reactif_auth_mode");
    localStorage.removeItem("reactif_pseudo");
    localStorage.removeItem("reactif_identity_level");
    localStorage.removeItem("reactif_admin_status");
    localStorage.removeItem("reactif_read_only");
  };

  return (
    <AuthContext.Provider value={{
      token, role, profileId, authMode, pseudo, identityLevel,
      isLoading, login, loginPseudo, loginPro, register,
      registerEntreprise, registerPartenaire, upgradeAccount,
      switchRole, logout, loginFromGate,
      adminStatus, isReadOnly,
      isAuthenticated: !!token
    }}>
      {children}
    </AuthContext.Provider>
  );
};

function AppContent() {
  const { adminStatus, loginFromGate, isAuthenticated, isReadOnly } = useAuth();

  // Global axios interceptor to block write requests in read-only mode
  useEffect(() => {
    if (!isReadOnly) return;
    const id = axios.interceptors.request.use((config) => {
      const method = config.method?.toLowerCase();
      if (['post', 'put', 'delete', 'patch'].includes(method)) {
        const url = config.url || "";
        // Allow auth/seed/verify endpoints
        if (url.includes('/auth/') || url.includes('/seed') || url.includes('/verify')) {
          return config;
        }
        toast.info("Mode lecture seule — action non disponible pour les invités");
        return Promise.reject(new axios.Cancel("Read-only mode"));
      }
      return config;
    });
    return () => axios.interceptors.request.eject(id);
  }, [isReadOnly]);

  if (!adminStatus) {
    // Allow public routes without admin gate
    const currentPath = window.location.pathname;
    if (currentPath === "/observatoire") {
      return (
        <>
          <Toaster position="top-right" richColors />
          <BrowserRouter>
            <Routes>
              <Route path="/observatoire" element={<OpcPublicPage />} />
              <Route path="*" element={<AdminGate onAuthenticated={loginFromGate} />} />
            </Routes>
          </BrowserRouter>
        </>
      );
    }
    return (
      <>
        <Toaster position="top-right" richColors />
        <AdminGate onAuthenticated={loginFromGate} />
      </>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <Toaster position="top-right" richColors />
      {isReadOnly && <ReadOnlyBanner />}
      <BrowserRouter>
        <Routes>
          <Route path="/" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Landing />} />
          <Route path="/passport/shared/:shareId" element={<SharedPassportPage />} />
          <Route path="/trajectoire/:shareId" element={<SharedTrajectoryPage />} />
          <Route path="/test-dclic" element={<DclicTestPage />} />
          <Route path="/ubuntoo" element={<UbuntooPage />} />
          <Route path="/observatoire" element={<OpcPublicPage />} />
          <Route path="/opc" element={<ProtectedRoute><OpcDedieWrapper /></ProtectedRoute>} />
          <Route path="/dashboard/*" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

const ReadOnlyBanner = () => (
  <div className="bg-amber-500 text-white text-center py-1.5 px-4 text-sm font-medium fixed bottom-0 left-0 right-0 z-[9999] flex items-center justify-center gap-2" data-testid="read-only-banner">
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>
    Mode Lecture Seule — Vous naviguez en tant qu'Invité
  </div>
);

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

const OpcDedieWrapper = () => {
  const { token } = useAuth();
  const navigate = window.location;
  return <OpcDediePage token={token} onBack={() => { navigate.href = "/dashboard"; }} />;
};

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }
  
  return children;
};

export default App;
