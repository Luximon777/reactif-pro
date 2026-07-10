import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { social } from "./api";

const UbuntooSocialContext = createContext(null);

export const UbuntooSocialProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem("ubuntoo_jwt"));
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const sso = useCallback(async () => {
    const reactifToken = localStorage.getItem("reactif_token");
    if (!reactifToken) {
      setError("no_session");
      setLoading(false);
      return;
    }
    try {
      const res = await social.post("/auth/sso", { token: reactifToken });
      localStorage.setItem("ubuntoo_jwt", res.data.token);
      setToken(res.data.token);
      setUser(res.data.user);
      setError(null);
    } catch {
      setError("sso_failed");
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    const init = async () => {
      const jwt = localStorage.getItem("ubuntoo_jwt");
      if (jwt) {
        try {
          const res = await social.get("/auth/me");
          setUser(res.data);
          setToken(jwt);
          setLoading(false);
          return;
        } catch {
          localStorage.removeItem("ubuntoo_jwt");
        }
      }
      await sso();
    };
    init();
  }, [sso]);

  const refreshUser = async () => {
    try {
      const res = await social.get("/auth/me");
      setUser(res.data);
    } catch { /* ignore */ }
  };

  return (
    <UbuntooSocialContext.Provider value={{ user, token, loading, error, refreshUser, retrySso: sso }}>
      {children}
    </UbuntooSocialContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(UbuntooSocialContext);
  if (!context) {
    throw new Error("useAuth must be used within UbuntooSocialProvider");
  }
  return context;
};
