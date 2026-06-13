import { useState } from "react";

import { sendMessage } from "../services/chatApi";
import type { ChatMessage } from "../types";

export const useChat = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      sender: "bot",
      text: "Hello 👋 I am the BIT Mesra AI Assistant.",
    },
  ]);

  const [loading, setLoading] = useState(false);

  const sendChatMessage = async (text: string) => {
    if (!text.trim()) return;

    const userMessage: ChatMessage = {
      sender: "user",
      text,
    };

    setMessages((prev) => [...prev, userMessage]);

    try {
      setLoading(true);

      const response = await sendMessage(text);

      const botMessage: ChatMessage = {
        sender: "bot",
        text: response.answer,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: "Something went wrong.",
        },
      ]);

      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return {
    messages,
    loading,
    sendChatMessage,
  };
};
