export interface ChatMessage {
  sender: "user" | "bot";
  text: string;
}

export interface ChatRequest {
  message: string;
  sessionId?: string;
}

export interface ChatResponse {
  type: string;
  answer: string;
  score?: number;
  event?: string;
  start_date?: string;
  end_date?: string;
}

export interface HistoryMessage {
  role: "user" | "assistant";
  content: string;
}

export interface HistoryResponse {
  sessionId: string;
  messages: HistoryMessage[];
}
