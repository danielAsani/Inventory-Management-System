import apiClient from "./apiClient";

function hasFileValue(payload) {
  return typeof File !== "undefined" && Object.values(payload || {}).some((value) => value instanceof File);
}

function toRequestPayload(payload) {
  if (!hasFileValue(payload)) return payload;

  const formData = new FormData();
  Object.entries(payload).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      formData.append(key, value);
    }
  });
  return formData;
}

export function createResourceApi(endpoint) {
  return {
    async list(params = {}) {
      const { data } = await apiClient.get(endpoint, { params });
      return data;
    },
    async retrieve(id) {
      const { data } = await apiClient.get(`${endpoint}${id}/`);
      return data;
    },
    async create(payload) {
      const requestPayload = toRequestPayload(payload);
      const { data } = await apiClient.post(endpoint, requestPayload, hasFileValue(payload) ? {
        headers: { "Content-Type": "multipart/form-data" },
      } : undefined);
      return data;
    },
    async update(id, payload) {
      const requestPayload = toRequestPayload(payload);
      const { data } = await apiClient.patch(`${endpoint}${id}/`, requestPayload, hasFileValue(payload) ? {
        headers: { "Content-Type": "multipart/form-data" },
      } : undefined);
      return data;
    },
    async action(id, actionName, payload = {}) {
      const { data } = await apiClient.post(`${endpoint}${id}/${actionName}/`, payload);
      return data;
    },
    async remove(id, params = {}) {
      await apiClient.delete(`${endpoint}${id}/`, { params });
    },
  };
}
