import axios from "axios";
import { API_BASE_URL } from "../../config";
import { useAdminStore } from "../../features/admin/hooks/adminStore";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export function clearStudentSession() {
  localStorage.removeItem("bit_student_access_token");
  localStorage.removeItem("bit_student_refresh_token");
  sessionStorage.removeItem("bit_student_access_token");
  sessionStorage.removeItem("bit_student_refresh_token");
  window.dispatchEvent(new Event("student-logout"));
}

// Request Interceptor: Attach JWT Token based on request context (Admin vs. Student)
apiClient.interceptors.request.use(
  (config) => {
    // 1. If it's an admin route, inject the admin store token
    if (config.url?.includes("/api/admin")) {
      const adminToken = useAdminStore.getState().token;
      if (adminToken && config.headers) {
        config.headers.Authorization = `Bearer ${adminToken}`;
      }
      return config;
    }

    // 2. Otherwise, inject student token
    const studentToken =
      localStorage.getItem("bit_student_access_token") ||
      sessionStorage.getItem("bit_student_access_token");
    if (studentToken && config.headers) {
      config.headers.Authorization = `Bearer ${studentToken}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response Interceptor: Manage token refresh and session invalidation
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Detect 401 Unauthorized errors
    if (
      error.response &&
      error.response.status === 401 &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true;

      // Handle Admin Session Invalidation
      if (originalRequest.url?.includes("/api/admin")) {
        useAdminStore.getState().setLogout();
        return Promise.reject(error);
      }

      // Handle Student Token Rotation Flow
      if (
        !originalRequest.url.includes("/api/auth/login") &&
        !originalRequest.url.includes("/api/auth/refresh")
      ) {
        const refreshToken =
          localStorage.getItem("bit_student_refresh_token") ||
          sessionStorage.getItem("bit_student_refresh_token");

        if (!refreshToken) {
          clearStudentSession();
          return Promise.reject(error);
        }

        try {
          const response = await axios.post(`${API_BASE_URL}/api/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token, refresh_token } = response.data;
          const isLocalStorage =
            localStorage.getItem("bit_student_refresh_token") !== null;
          const storage = isLocalStorage ? localStorage : sessionStorage;

          storage.setItem("bit_student_access_token", access_token);
          storage.setItem("bit_student_refresh_token", refresh_token);

          // Update header and retry original request
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
          }
          return apiClient(originalRequest);
        } catch (refreshError) {
          clearStudentSession();
          return Promise.reject(refreshError);
        }
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
