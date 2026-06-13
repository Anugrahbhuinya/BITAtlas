import axios from "axios";
import type { ChatRequest, ChatResponse } from "../types";

const API_BASE_URL = "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const sendMessage = async (message: string): Promise<ChatResponse> => {
  const payload: ChatRequest = {
    message,
  };

  const response = await api.post<ChatResponse>("/chat", payload);

  return response.data;
};

export default api;
