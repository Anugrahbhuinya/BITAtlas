import { useState, useEffect } from "react";
import {
  sendMessage,
  fetchChatHistory,
  clearChatHistory,
} from "../services/chatApi";
import type { ChatMessage } from "../types";
import { useTextToSpeech } from "./useTextToSpeech";
import { getSessionId } from "../utils/session";

export const useChat = () => {
  const { speak, stopSpeaking, speakingText } = useTextToSpeech();
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      sender: "bot",
      text: "Hey I am the BIT Mesra agent",
    },
  ]);
  const [loading, setLoading] = useState(false);
  const sessionId = getSessionId();

  // Load chat history on mount
  useEffect(() => {
    const loadHistory = async () => {
      try {
        setLoading(true);

        const history = await fetchChatHistory(sessionId);

        if (history && history.messages && history.messages.length > 0) {
          const formatted = history.messages.map((msg) => ({
            sender:
              msg.role === "assistant" ? ("bot" as const) : ("user" as const),
            text: msg.content,
          }));

          setMessages([
            {
              sender: "bot",
              text: "Hey I am the BIT Mesra agent",
            },
            ...formatted,
          ]);
        } else {
          setMessages([
            {
              sender: "bot",
              text: "Hey I am the BIT Mesra agent",
            },
          ]);
        }
      } catch (error) {
        console.error("Failed to load chat history:", error);

        setMessages([
          {
            sender: "bot",
            text: "Hey I am the BIT Mesra agent",
          },
        ]);
      } finally {
        setLoading(false);
      }
    };

    loadHistory();
  }, [sessionId]);

  const sendChatMessage = async (text: string, isVoice = false) => {
    if (!text.trim()) return;

    const userMessage: ChatMessage = {
      sender: "user",
      text,
    };

    setMessages((prev) => [...prev, userMessage]);

    try {
      setLoading(true);

      const response = await sendMessage(text, sessionId);

      const botMessage: ChatMessage = {
        sender: "bot",
        text: response.answer,
      };

      setMessages((prev) => [...prev, botMessage]);
      if (isVoice) {
        speak(response.answer);
      }
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

  const clearHistory = async () => {
    try {
      setLoading(true);
      await clearChatHistory(sessionId);
      setMessages([
        {
          sender: "bot",
          text: "Hey I am the BIT Mesra agent",
        },
      ]);
    } catch (error) {
      console.error("Failed to clear chat history:", error);
    } finally {
      setLoading(false);
    }
  };

  return {
    messages,
    loading,
    sendChatMessage,
    clearHistory,
    speak,
    stopSpeaking,
    speakingText,
  };
};
