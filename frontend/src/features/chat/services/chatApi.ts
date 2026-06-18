import axios from "axios";
import type { ChatRequest, ChatResponse, HistoryResponse } from "../types";

const API_BASE_URL = "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const sendMessage = async (message: string, sessionId?: string): Promise<ChatResponse> => {
  const payload: ChatRequest = {
    message,
    sessionId,
  };

  const response = await api.post<ChatResponse>("/chat", payload);

  return response.data;
};

export const fetchChatHistory = async (sessionId: string): Promise<HistoryResponse> => {
  const response = await api.get<HistoryResponse>(`/chat/history/${sessionId}`);
  return response.data;
};

export const clearChatHistory = async (sessionId: string): Promise<void> => {
  await api.delete(`/chat/history/${sessionId}`);
};

export default api;
