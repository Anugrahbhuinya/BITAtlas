import { useEffect, useRef } from "react";
import { Trash2 } from "lucide-react";

import MessageBubble from "./MessageBubble";
import ChatInput from "./ChatInput";

import { useChat } from "../hooks/useChat";

function ChatWindow() {
  const {
    messages,
    loading,
    sendChatMessage,
    clearHistory,
    speak,
    stopSpeaking,
    speakingText,
  } = useChat();

  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages]);

  return (
    <div className="h-screen bg-slate-900 flex flex-col">
      {/* Header */}

      <div className="border-b border-slate-700 p-4">
        <div className="max-w-5xl mx-auto flex items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-white">
              BIT Mesra AI Assistant
            </h1>

            <p className="text-slate-400 mt-1">
              Ask anything about academics, hostels, clubs, notices, locations and
              more.
            </p>
          </div>
          
          <button
            onClick={clearHistory}
            className="flex items-center gap-2 px-3 py-2 bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500/20 hover:text-red-300 rounded-xl transition duration-200 text-sm font-medium"
            title="Clear chat history"
          >
            <Trash2 size={16} />
            <span>Clear Chat</span>
          </button>
        </div>
      </div>

      {/* Messages */}

      <div className="flex-1 overflow-y-auto">
        <div className="max-w-5xl mx-auto p-6">
          {messages.map((message, index) => (
            <MessageBubble
              key={index}
              message={message}
              onSpeak={speak}
              onStopSpeaking={stopSpeaking}
              isSpeaking={speakingText === message.text}
            />
          ))}

          {loading && (
            <div className="flex justify-start mb-4">
              <div className="bg-slate-800 text-white px-4 py-3 rounded-2xl">
                Thinking...
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      </div>

      {/* Input */}

      <div className="border-t border-slate-700 bg-slate-900 p-4">
        <div className="max-w-5xl mx-auto">
          <ChatInput onSend={sendChatMessage} onStopSpeaking={stopSpeaking} />
        </div>
      </div>
    </div>
  );
}

export default ChatWindow;
