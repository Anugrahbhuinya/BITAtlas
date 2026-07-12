export interface NavigationContext {
  source?: string;
  destination: string;
  walking_distance?: number;
  estimated_time?: number;
  directions: string[];
  landmarks: string[];
  nearby_facilities: string[];
  graph_path: string[];
  confidence: number;
  accessibility_mode: boolean;
  building_metadata: {
    building_code?: string;
    category?: string;
    description?: string;
    address?: string;
    ambiguities?: string[];
  };
  validation_status: string;
}

export interface ChatMessage {
  sender: "user" | "bot";
  text: string;
  navigation_context?: NavigationContext;
  messageType?: "text" | "navigation";
  metadata?: {
    cardType: "place" | "route";
    title: string;
    building?: any;
    landmarks?: string[];
    facilities?: string[];
    actions?: string[];
    navigation_context?: NavigationContext;
  };
  diagnostics?: any;
}

export interface ChatRequest {
  message: string;
  sessionId?: string;
  currentLocationNodeId?: string;
  currentDestinationNodeId?: string;
  accessibilityMode?: boolean;
}

export interface ChatResponse {
  type: string;
  answer: string;
  navigation_context?: NavigationContext;
  score?: number;
  event?: string;
  start_date?: string;
  end_date?: string;
  messageType?: "text" | "navigation";
  metadata?: any;
  diagnostics?: any;
}

export interface HistoryMessage {
  role: "user" | "assistant";
  content: string;
  messageType?: "text" | "navigation";
  metadata?: any;
}

export interface HistoryResponse {
  sessionId: string;
  messages: HistoryMessage[];
}
