import axios from "axios";

const baseURL = process.env.REACT_APP_API_BASE || "/api";
export const api = axios.create({ baseURL });

api.interceptors.request.use((cfg) => {
  const t = localStorage.getItem("token");
  if (t) cfg.headers.Authorization = `Bearer ${t}`;
  return cfg;
});

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response && err.response.status === 401) {
      localStorage.removeItem("token");
    }
    return Promise.reject(err);
  }
);
