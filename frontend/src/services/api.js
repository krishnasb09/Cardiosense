import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "https://your-fastapi-backend.onrender.com/predict";

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
  const { data } = await api.post("/predict", payload);
  return data;
}

export async function getAnalytics() {
  const { data } = await api.get("/analytics");
  return data;
}

export async function getHistory(params = {}) {
  const { data } = await api.get("/history", { params });
  return data;
}

export async function downloadReport(payload) {
  const { data } = await api.post("/reports/pdf", payload, { responseType: "blob" });
  return data;
}
