import apiClient from "./apiClient";
import { normalizePage } from "../utils/pagination";

const DATA_ENDPOINTS = {
  dashboard: "dashboard/",
  materiels: "stock/materiels/",
  consommables: "stock/consommables/",
  mouvements: "operations/mouvements/",
  consommations: "operations/consommations/",
  demandes: "demandes/",
  inventaires: "inventaires/",
  entretiens: "maintenance/entretiens/",
  reparations: "maintenance/reparations/",
};

async function fetchList(endpoint, perpage = 50) {
  const firstResponse = await apiClient.get(endpoint, { params: { page: 1, perpage } });
  const firstPage = normalizePage(firstResponse.data);
  const results = [...firstPage.results];

  if (firstPage.totalPages <= 1) return results;

  const remainingPages = Array.from({ length: firstPage.totalPages - 1 }, (_, index) => index + 2);
  const pageResponses = await Promise.all(
    remainingPages.map((page) => apiClient.get(endpoint, { params: { page, perpage } })),
  );

  pageResponses.forEach((response) => {
    results.push(...normalizePage(response.data).results);
  });

  return results;
}

export async function getDataStudySnapshot() {
  const entries = Object.entries(DATA_ENDPOINTS);
  const responses = await Promise.allSettled(
    entries.map(async ([key, endpoint]) => {
      if (key === "dashboard") {
        const { data } = await apiClient.get(endpoint);
        return [key, data];
      }
      return [key, await fetchList(endpoint)];
    }),
  );

  if (responses.every((response) => response.status === "rejected")) {
    throw responses[0].reason;
  }

  return responses.reduce((snapshot, response, index) => {
    const [key] = entries[index];
    if (response.status === "fulfilled") {
      const [, value] = response.value;
      snapshot[key] = value;
    } else {
      snapshot[key] = key === "dashboard" ? {} : [];
    }
    return snapshot;
  }, {});
}
