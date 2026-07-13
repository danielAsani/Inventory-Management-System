import axios from "axios";
import { clearTokens, getAccessToken, getRefreshToken, setTokens } from "./tokenStorage";

const baseURL = import.meta.env.VITE_API_BASE_URL || "/api";

const apiClient = axios.create({
  baseURL: baseURL.endsWith("/") ? baseURL : `${baseURL}/`,
  headers: { "Content-Type": "application/json" },
});

let refreshPromise = null;

function isTokenError(detail) {
  if (typeof detail !== "string") return false;
  const normalized = detail.toLowerCase();
  return normalized.includes("token invalide") || normalized.includes("token manquant") || normalized.includes("expire");
}

function expireSession() {
  clearTokens();
  window.dispatchEvent(new Event("auth:expired"));
}

apiClient.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const status = error.response?.status;
    const detail = error.response?.data?.detail;
    const hasTokenError = isTokenError(detail);

    if (hasTokenError && originalRequest?.url?.includes("auth/refresh/")) {
      expireSession();
      return Promise.reject(error);
    }

    if ((!hasTokenError && status !== 401) || originalRequest?._retry || originalRequest?.url?.includes("auth/refresh/")) {
      return Promise.reject(error);
    }

    const refresh = getRefreshToken();
    if (!refresh) {
      expireSession();
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    try {
      refreshPromise ??= apiClient.post("auth/refresh/", { refresh });
      const response = await refreshPromise;
      setTokens({ access: response.data.access });
      originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
      return apiClient(originalRequest);
    } catch (refreshError) {
      expireSession();
      return Promise.reject(refreshError);
    } finally {
      refreshPromise = null;
    }
  },
);

export default apiClient;
