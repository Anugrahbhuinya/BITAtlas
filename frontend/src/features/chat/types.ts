export interface ChatMessage {
  sender: "user" | "bot";
  text: string;
}

export interface ChatRequest {
  message: string;
}

export interface ChatResponse {
  type: string;
  answer: string;
  score?: number;
  event?: string;
  start_date?: string;
  end_date?: string;
}
