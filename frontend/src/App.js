import { useEffect, useState, createContext, useContext } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";
import { Toaster } from "@/components/ui/sonner";
import Landing from "@/pages/Landing";
import Dashboard from "@/pages/Dashboard";

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
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const verifyToken = async () => {
      if (token) {
        try {
          const response = await axios.get(`${API}/auth/verify?token=${token}`);
          if (response.data.valid) {
            setRole(response.data.role);
            setProfileId(response.data.profile_id);
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

  const login = async (selectedRole = "particulier") => {
    try {
      const response = await axios.post(`${API}/auth/anonymous`, { role: selectedRole });
      const { token: newToken, role: newRole, profile_id } = response.data;
      
      setToken(newToken);
      setRole(newRole);
      setProfileId(profile_id);
      
      localStorage.setItem("reactif_token", newToken);
      localStorage.setItem("reactif_role", newRole);
      localStorage.setItem("reactif_profile_id", profile_id);
      
      return true;
    } catch (error) {
      console.error("Login error:", error);
      return false;
    }
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
    localStorage.removeItem("reactif_token");
    localStorage.removeItem("reactif_role");
    localStorage.removeItem("reactif_profile_id");
  };

  return (
    <AuthContext.Provider value={{ token, role, profileId, isLoading, login, switchRole, logout, isAuthenticated: !!token }}>
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
