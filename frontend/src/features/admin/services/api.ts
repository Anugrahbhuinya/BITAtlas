import axios from "axios";
import { useAdminStore } from "../hooks/adminStore";

const API_BASE_URL = "http://localhost:8000";

const adminApi = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Automatically inject JWT token into header
adminApi.interceptors.request.use(
  (config) => {
    const token = useAdminStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Catch 401 errors to trigger immediate logout
adminApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      useAdminStore.getState().setLogout();
    }
    return Promise.reject(error);
  }
);

export default adminApi;
