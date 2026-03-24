import { useEffect, useState, createContext, useContext } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";
import { Toaster } from "@/components/ui/sonner";
import Landing from "@/pages/Landing";
import Dashboard from "@/pages/Dashboard";
import SharedPassportPage from "@/pages/SharedPassportPage";
import DclicTestPage from "@/pages/DclicTestPage";

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
  const register = async (pseudoName, password, selectedRole = "particulier", emailRecovery = null, consentMarketing = false) => {
    try {
      const response = await axios.post(`${API}/auth/register`, {
        pseudo: pseudoName,
        password,
        role: selectedRole,
        email_recovery: emailRecovery || null,
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
  const loginPseudo = async (pseudoName, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, {
        pseudo: pseudoName,
        password
      });
      const { token: newToken, role: newRole, profile_id, pseudo: p, auth_mode: am } = response.data;
      setAuthState(newToken, newRole, profile_id, am || "pseudo", p, "none");
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
      const { token: t, role: r, profile_id, pseudo: p, auth_mode: am } = response.data;
      setAuthState(t, r, profile_id, am || "pseudo", p, "none");
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

  const logout = () => {
    setToken(null);
    setRole("particulier");
    setProfileId(null);
    setAuthMode("anonymous");
    setPseudo(null);
    setIdentityLevel("none");
    localStorage.removeItem("reactif_token");
    localStorage.removeItem("reactif_role");
    localStorage.removeItem("reactif_profile_id");
    localStorage.removeItem("reactif_auth_mode");
    localStorage.removeItem("reactif_pseudo");
    localStorage.removeItem("reactif_identity_level");
  };

  return (
    <AuthContext.Provider value={{
      token, role, profileId, authMode, pseudo, identityLevel,
      isLoading, login, loginPseudo, loginPro, register,
      registerEntreprise, registerPartenaire, upgradeAccount,
      switchRole, logout, isAuthenticated: !!token
    }}>
      {children}
    </AuthContext.Provider>
  );
};

function App() {
  return (
    <AuthProvider>
      <div className="min-h-screen bg-white">
        <Toaster position="top-right" richColors />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/passport/shared/:shareId" element={<SharedPassportPage />} />
            <Route path="/test-dclic" element={<DclicTestPage />} />
            <Route path="/dashboard/*" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </div>
    </AuthProvider>
  );
}

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
