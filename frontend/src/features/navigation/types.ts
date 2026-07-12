// src/features/navigation/types.ts

export interface Entrance {
  name: string;
  latitude: number;
  longitude: number;
}

export interface Accessibility {
  wheelchair_accessible: boolean;
  has_elevator?: boolean;
  has_ramp?: boolean;
}

export interface Coordinates {
  latitude: number;
  longitude: number;
}

export interface NodeReference {
  id: string;
  type: string;
  name: string;
}

export interface Building {
  _id: string;
  building_code: string;
  building_name: string;
  description: string;
  category: string;
  latitude: number;
  longitude: number;
  address: string;
  image?: string | null;
  opening_hours: string;
  contact: string;
  departments: string[];
  entrances: Entrance[];
  floors: number[];
  accessibility: Accessibility;
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
  osm_id?: string;
  osm_type?: string;
  geometry?: [number, number][];
  entrance_geometry?: [number, number];
}

export interface Room {
  _id: string;
  room_number: string;
  room_name: string;
  building_id: string;
  floor: number;
  department?: string | null;
  room_type: string;
  capacity: number;
  latitude?: number | null;
  longitude?: number | null;
  description: string;
  facilities: string[];
  metadata: Record<string, any>;
}

export interface Landmark {
  _id: string;
  name: string;
  latitude: number;
  longitude: number;
  coordinates: Coordinates;
  description: string;
  category: string;
  image?: string | null;
  metadata: Record<string, any>;
  osm_id?: string;
  osm_type?: string;
  geometry?: [number, number][];
  entrance_geometry?: [number, number];
}

export interface Facility {
  _id: string;
  name: string;
  latitude: number;
  longitude: number;
  coordinates: Coordinates;
  category: string;
  timing: string;
  services: string[];
  accessibility: Accessibility;
  metadata: Record<string, any>;
  osm_id?: string;
  osm_type?: string;
  geometry?: [number, number][];
  entrance_geometry?: [number, number];
}

export interface Pathway {
  _id: string;
  start_node: NodeReference;
  end_node: NodeReference;
  path_type: string;
  distance: number;
  surface: string;
  accessible: boolean;
  lighting: string;
  notes: string;
  metadata: Record<string, any>;
}

export interface NavigationSearchResult {
  _id: string;
  type: "building" | "room" | "landmark" | "facility";
  name: string;
  description: string;
  latitude: number;
  longitude: number;
  category: string;
  snippet: string;
  metadata: Record<string, any>;
}

export interface NavigationFilters {
  search: string;
  category: string;
  accessibilityOnly: boolean;
}

export interface GraphNode {
  id: string;
  type: string;
  name: string;
  coordinates: {
    latitude: number;
    longitude: number;
  };
  metadata: Record<string, any>;
}

export interface GraphEdge {
  source: string;
  destination: string;
  relationship: string;
  distance?: number | null;
  accessibility: boolean;
  metadata: Record<string, any>;
}

export interface GraphNeighbor {
  node: GraphNode;
  edge: GraphEdge;
}

export interface GraphSummary {
  total_nodes: number;
  total_edges: number;
  node_type_counts: Record<string, number>;
  edge_relationship_counts: Record<string, number>;
  is_valid: boolean;
}

export interface GraphValidationError {
  type: string;
  message: string;
  severity: "ERROR" | "WARNING";
  details: Record<string, any>;
}

export interface GraphValidationReport {
  is_valid: boolean;
  errors: GraphValidationError[];
  total_errors: number;
  total_warnings: number;
}

export interface Route {
  start_node: GraphNode;
  destination_node: GraphNode;
  ordered_path: GraphEdge[];
  ordered_nodes: GraphNode[];
  total_distance: number;
  estimated_walking_time: number;
  total_nodes: number;
  navigation_instructions: string[];
  accessibility_information: boolean;
  alternative_routes: any[];
  metadata: Record<string, any>;
  geometry?: number[][];
}

export interface RouteETA {
  start_id: string;
  destination_id: string;
  distance_meters: number;
  estimated_seconds: number;
  accessible: boolean;
}

