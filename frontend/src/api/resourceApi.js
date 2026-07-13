import apiClient from "./apiClient";

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
      const { data } = await apiClient.post(endpoint, payload);
      return data;
    },
    async update(id, payload) {
      const { data } = await apiClient.patch(`${endpoint}${id}/`, payload);
      return data;
    },
    async action(id, actionName, payload = {}) {
      const { data } = await apiClient.post(`${endpoint}${id}/${actionName}/`, payload);
      return data;
    },
    async remove(id) {
      await apiClient.delete(`${endpoint}${id}/`);
    },
  };
}
