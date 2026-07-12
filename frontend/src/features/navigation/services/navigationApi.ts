// src/features/navigation/services/navigationApi.ts

import studentApi from "../../auth/services/api";
import adminApi from "../../admin/services/api";
import type {
  Building,
  Room,
  Facility,
  Landmark,
  Pathway,
  NavigationSearchResult,
  GraphNode,
  GraphEdge,
  GraphNeighbor,
  GraphSummary,
  GraphValidationReport,
  Route,
  RouteETA
} from "../types";

export const navigationApi = {
  // --- BUILDINGS API ---
  fetchBuildings: async (params?: { search?: string; category?: string; skip?: number; limit?: number }) => {
    const response = await studentApi.get<{ buildings: Building[]; total: number }>("/api/navigation/buildings", { params });
    return response.data;
  },

  fetchBuilding: async (id: string) => {
    const response = await studentApi.get<Building>(`/api/navigation/buildings/${id}`);
    return response.data;
  },

  fetchBuildingByCode: async (code: string) => {
    const response = await studentApi.get<Building>(`/api/navigation/buildings/code/${code}`);
    return response.data;
  },

  createBuilding: async (payload: Omit<Building, "_id" | "created_at" | "updated_at">) => {
    const response = await adminApi.post<Building>("/api/navigation/buildings", payload);
    return response.data;
  },

  updateBuilding: async (id: string, payload: Partial<Omit<Building, "_id" | "created_at" | "updated_at">>) => {
    const response = await adminApi.put<Building>(`/api/navigation/buildings/${id}`, payload);
    return response.data;
  },

  deleteBuilding: async (id: string) => {
    const response = await adminApi.delete<void>(`/api/navigation/buildings/${id}`);
    return response.data;
  },

  // --- ROOMS API ---
  fetchRooms: async (params?: { search?: string; building_id?: string; floor?: number; room_type?: string; skip?: number; limit?: number }) => {
    const response = await studentApi.get<{ rooms: Room[]; total: number }>("/api/navigation/rooms", { params });
    return response.data;
  },

  fetchRoom: async (id: string) => {
    const response = await studentApi.get<Room>(`/api/navigation/rooms/${id}`);
    return response.data;
  },

  createRoom: async (payload: Omit<Room, "_id">) => {
    const response = await adminApi.post<Room>("/api/navigation/rooms", payload);
    return response.data;
  },

  updateRoom: async (id: string, payload: Partial<Omit<Room, "_id">>) => {
    const response = await adminApi.put<Room>(`/api/navigation/rooms/${id}`, payload);
    return response.data;
  },

  deleteRoom: async (id: string) => {
    const response = await adminApi.delete<void>(`/api/navigation/rooms/${id}`);
    return response.data;
  },

  // --- FACILITIES API ---
  fetchFacilities: async (params?: { search?: string; category?: string; skip?: number; limit?: number }) => {
    const response = await studentApi.get<{ facilities: Facility[]; total: number }>("/api/navigation/facilities", { params });
    return response.data;
  },

  fetchFacility: async (id: string) => {
    const response = await studentApi.get<Facility>(`/api/navigation/facilities/${id}`);
    return response.data;
  },

  createFacility: async (payload: Omit<Facility, "_id">) => {
    const response = await adminApi.post<Facility>("/api/navigation/facilities", payload);
    return response.data;
  },

  updateFacility: async (id: string, payload: Partial<Omit<Facility, "_id">>) => {
    const response = await adminApi.put<Facility>(`/api/navigation/facilities/${id}`, payload);
    return response.data;
  },

  deleteFacility: async (id: string) => {
    const response = await adminApi.delete<void>(`/api/navigation/facilities/${id}`);
    return response.data;
  },

  // --- LANDMARKS API ---
  fetchLandmarks: async (params?: { search?: string; category?: string; skip?: number; limit?: number }) => {
    const response = await studentApi.get<{ landmarks: Landmark[]; total: number }>("/api/navigation/landmarks", { params });
    return response.data;
  },

  fetchLandmark: async (id: string) => {
    const response = await studentApi.get<Landmark>(`/api/navigation/landmarks/${id}`);
    return response.data;
  },

  createLandmark: async (payload: Omit<Landmark, "_id">) => {
    const response = await adminApi.post<Landmark>("/api/navigation/landmarks", payload);
    return response.data;
  },

  updateLandmark: async (id: string, payload: Partial<Omit<Landmark, "_id">>) => {
    const response = await adminApi.put<Landmark>(`/api/navigation/landmarks/${id}`, payload);
    return response.data;
  },

  deleteLandmark: async (id: string) => {
    const response = await adminApi.delete<void>(`/api/navigation/landmarks/${id}`);
    return response.data;
  },

  // --- PATHWAYS API ---
  fetchPathways: async (params?: { path_type?: string; accessible?: boolean; skip?: number; limit?: number }) => {
    const response = await studentApi.get<{ pathways: Pathway[]; total: number }>("/api/navigation/pathways", { params });
    return response.data;
  },

  fetchPathway: async (id: string) => {
    const response = await studentApi.get<Pathway>(`/api/navigation/pathways/${id}`);
    return response.data;
  },

  createPathway: async (payload: Omit<Pathway, "_id">) => {
    const response = await adminApi.post<Pathway>("/api/navigation/pathways", payload);
    return response.data;
  },

  updatePathway: async (id: string, payload: Partial<Omit<Pathway, "_id">>) => {
    const response = await adminApi.put<Pathway>(`/api/navigation/pathways/${id}`, payload);
    return response.data;
  },

  deletePathway: async (id: string) => {
    const response = await adminApi.delete<void>(`/api/navigation/pathways/${id}`);
    return response.data;
  },

  // --- UNIFIED SEARCH API ---
  searchNavigation: async (query: string, limit?: number) => {
    const response = await studentApi.get<NavigationSearchResult[]>("/api/navigation/search", {
      params: { q: query, limit }
    });
    return response.data;
  },

  // --- GRAPH ENGINE API ---
  fetchGraphSummary: async () => {
    const response = await studentApi.get<GraphSummary>("/api/navigation/graph");
    return response.data;
  },

  fetchGraphNodes: async (type?: string) => {
    const response = await studentApi.get<GraphNode[]>("/api/navigation/graph/nodes", {
      params: { type }
    });
    return response.data;
  },

  fetchGraphEdges: async () => {
    const response = await studentApi.get<GraphEdge[]>("/api/navigation/graph/edges");
    return response.data;
  },

  fetchGraphNode: async (id: string) => {
    const response = await studentApi.get<GraphNode>(`/api/navigation/graph/node/${id}`);
    return response.data;
  },

  fetchGraphNeighbors: async (id: string) => {
    const response = await studentApi.get<GraphNeighbor[]>(`/api/navigation/graph/neighbors/${id}`);
    return response.data;
  },

  fetchGraphBuildingRooms: async (id: string) => {
    const response = await studentApi.get<GraphNode[]>(`/api/navigation/graph/building/${id}/rooms`);
    return response.data;
  },

  fetchGraphBuildingFacilities: async (id: string, radius?: number) => {
    const response = await studentApi.get<GraphNode[]>(`/api/navigation/graph/building/${id}/facilities`, {
      params: { radius }
    });
    return response.data;
  },

  fetchGraphValidation: async () => {
    const response = await studentApi.get<GraphValidationReport>("/api/navigation/graph/validate");
    return response.data;
  },

  rebuildGraph: async () => {
    const response = await adminApi.post<GraphSummary>("/api/navigation/graph/rebuild");
    return response.data;
  },

  calculateRoute: async (start: string, destination: string, routeType: "shortest" | "fastest" | "accessible" = "shortest") => {
    const response = await studentApi.get<Route>("/api/navigation/route", {
      params: { start, destination, routeType }
    });
    return response.data;
  },

  fetchRouteEta: async (start: string, destination: string) => {
    const response = await studentApi.get<RouteETA>("/api/navigation/route/eta", {
      params: { start, destination }
    });
    return response.data;
  },

  fetchRouteInstructions: async (start: string, destination: string) => {
    const response = await studentApi.get<string[]>("/api/navigation/route/instructions", {
      params: { start, destination }
    });
    return response.data;
  },

  fetchReachableNodes: async (start: string) => {
    const response = await studentApi.get<{ start_id: string; reachable_node_ids: string[]; total_reachable: number }>(
      "/api/navigation/route/reachable",
      { params: { start } }
    );
    return response.data;
  },

  fetchNearbyNodes: async (latitude: number, longitude: number, radius?: number) => {
    const response = await studentApi.get<{ center_latitude: number; center_longitude: number; radius_meters: number; nearby_nodes: GraphNode[] }>(
      "/api/navigation/route/nearby",
      { params: { latitude, longitude, radius } }
    );
    return response.data;
  }
};

export default navigationApi;
