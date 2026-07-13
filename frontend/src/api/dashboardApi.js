import apiClient from "./apiClient";

export async function getDashboardStats() {
  const { data } = await apiClient.get("dashboard/");
  return data;
}
