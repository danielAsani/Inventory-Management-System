import { useCallback, useEffect, useMemo, useState } from "react";
import { fetchCurrentUser, login as loginRequest, logout as logoutRequest } from "../api/authApi";
import { clearTokens, getAccessToken, setTokens } from "../api/tokenStorage";
import { getApiErrorMessage } from "../utils/apiErrors";
import { AuthContext } from "./authContextObject";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isBootstrapping, setIsBootstrapping] = useState(true);
  const [authError, setAuthError] = useState("");

  const loadUser = useCallback(async () => {
    if (!getAccessToken()) {
      setUser(null);
      setIsBootstrapping(false);
      return null;
    }

    try {
      const currentUser = await fetchCurrentUser();
      setUser(currentUser);
      return currentUser;
    } catch (error) {
      clearTokens();
      setUser(null);
      setAuthError(getApiErrorMessage(error));
      return null;
    } finally {
      setIsBootstrapping(false);
    }
  }, []);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  useEffect(() => {
    const expire = () => {
      setUser(null);
      setAuthError("Votre session a expire. Veuillez vous reconnecter.");
    };

    window.addEventListener("auth:expired", expire);
    return () => window.removeEventListener("auth:expired", expire);
  }, []);

  const login = useCallback(async (credentials) => {
    const response = await loginRequest(credentials);
    setTokens({ access: response.access, refresh: response.refresh });
    setUser(response.user);
    setAuthError("");
    return response.user;
  }, []);

  const logout = useCallback(async () => {
    await logoutRequest();
    clearTokens();
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ user, isAuthenticated: Boolean(user), isBootstrapping, authError, login, logout, reloadUser: loadUser }),
    [authError, isBootstrapping, loadUser, login, logout, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
