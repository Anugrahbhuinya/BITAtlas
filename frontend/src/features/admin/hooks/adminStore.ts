import { create } from "zustand";

interface Toast {
  message: string;
  type: "success" | "error" | "info";
}

interface AdminState {
  token: string | null;
  username: string | null;
  isAuthenticated: boolean;
  sidebarCollapsed: boolean;
  toast: Toast | null;
  setLogin: (token: string, username: string) => void;
  setLogout: () => void;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  showToast: (message: string, type?: "success" | "error" | "info") => void;
  clearToast: () => void;
}

export const useAdminStore = create<AdminState>((set) => {
  // Read initial auth state from localStorage
  const savedToken = localStorage.getItem("bit_admin_token");
  const savedUsername = localStorage.getItem("bit_admin_username");

  return {
    token: savedToken,
    username: savedUsername,
    isAuthenticated: !!savedToken,
    sidebarCollapsed: false,
    toast: null,

    setLogin: (token: string, username: string) => {
      localStorage.setItem("bit_admin_token", token);
      localStorage.setItem("bit_admin_username", username);
      set({ token, username, isAuthenticated: true });
    },

    setLogout: () => {
      localStorage.removeItem("bit_admin_token");
      localStorage.removeItem("bit_admin_username");
      set({ token: null, username: null, isAuthenticated: false });
    },

    toggleSidebar: () =>
      set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),

    setSidebarCollapsed: (collapsed: boolean) =>
      set({ sidebarCollapsed: collapsed }),

    showToast: (message: string, type = "success") => {
      set({ toast: { message, type } });
      // Auto-clear toast after 4 seconds
      setTimeout(() => {
        set((state) => {
          if (state.toast?.message === message) {
            return { toast: null };
          }
          return {};
        });
      }, 4000);
    },

    clearToast: () => set({ toast: null }),
  };
});
