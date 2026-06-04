import axios from "axios";
const API_URL = import.meta.env.VITE_API_URL;


export const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
});

export function attachAuthToken(token) {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common.Authorization;
  }
}

export async function predictCad(payload) {
  const { data } = await api.post("/api/predict", payload);
  return data;
}

export async function getAnalytics() {
  const { data } = await api.get("/api/analytics");
  return data;
}

export async function getHistory(params = {}) {
  const { data } = await api.get("/api/history", { params });
  return data;
}

export async function downloadReport(payload) {
  const { data } = await api.post("/api/reports/pdf", payload, { responseType: "blob" });
  return data;
}
