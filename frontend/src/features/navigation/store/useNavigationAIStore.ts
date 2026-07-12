import { create } from "zustand";

interface NavigationAIStore {
  currentLocationNodeId: string | null;
  currentDestinationNodeId: string | null;
  accessibilityMode: boolean;

  setCurrentLocation: (nodeId: string | null) => void;
  setCurrentDestination: (nodeId: string | null) => void;
  setAccessibilityMode: (enabled: boolean) => void;
}

export const useNavigationAIStore = create<NavigationAIStore>((set) => ({
  currentLocationNodeId: null,
  currentDestinationNodeId: null,
  accessibilityMode: false,

  setCurrentLocation: (nodeId) =>
    set({ currentLocationNodeId: nodeId }),
  setCurrentDestination: (nodeId) =>
    set({ currentDestinationNodeId: nodeId }),
  setAccessibilityMode: (enabled) =>
    set({ accessibilityMode: enabled }),
}));
