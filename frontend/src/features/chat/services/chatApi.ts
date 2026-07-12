import apiClient from "../../../shared/api/client";
import type { ChatRequest, ChatResponse, HistoryResponse } from "../types";

export interface NavContext {
  currentLocationNodeId?: string;
  currentDestinationNodeId?: string;
  accessibilityMode?: boolean;
}

export const sendMessage = async (
  message: string,
  sessionId?: string,
  navContext?: NavContext
): Promise<ChatResponse> => {
  const payload: ChatRequest = {
    message,
    sessionId,
    ...navContext,
  };

  // Attach student auth token if available for personalized context
  const token = localStorage.getItem("bit_student_access_token") || localStorage.getItem("student_access_token");
  const headers: Record<string, string> = {};
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await apiClient.post<ChatResponse>("/chat", payload, { headers });
  return response.data;
};

export const fetchChatHistory = async (sessionId: string): Promise<HistoryResponse> => {
  const response = await apiClient.get<HistoryResponse>(`/chat/history/${sessionId}`);
  return response.data;
};

export const clearChatHistory = async (sessionId: string): Promise<void> => {
  await apiClient.delete(`/chat/history/${sessionId}`);
};

export default apiClient;
