import apiClient from "./apiClient";

export async function login(credentials) {
  const { data } = await apiClient.post("auth/login/", credentials);
  return data;
}

export async function fetchCurrentUser() {
  const { data } = await apiClient.get("auth/me/");
  return data;
}

export async function logout() {
  if (!localStorage.getItem("access_token")) return;

  try {
    await apiClient.post("auth/logout/");
  } catch {
  }
}
