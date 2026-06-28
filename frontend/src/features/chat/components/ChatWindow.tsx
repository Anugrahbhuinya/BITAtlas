import { useEffect, useRef, useState } from "react";
import { useLocation } from "react-router-dom";
import { Trash2, AlertCircle, ArrowRight, Bot } from "lucide-react";
import MessageBubble from "./MessageBubble";
import ChatInput from "./ChatInput";
import { useChat } from "../hooks/useChat";

export const ChatWindow = () => {
  const {
    messages,
    loading,
    sendChatMessage,
    clearHistory,
    speak,
    stopSpeaking,
    speakingText,
  } = useChat();

  const location = useLocation();
  const bottomRef = useRef<HTMLDivElement>(null);
  const prefilledSent = useRef(false);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages]);

  // Handle auto-seeding of dashboard quick prompts
  useEffect(() => {
    const statePrompt = location.state?.prefilledPrompt;
    if (statePrompt && !prefilledSent.current) {
      prefilledSent.current = true;
      sendChatMessage(statePrompt);
    }
  }, [location.state, sendChatMessage]);

  const handleSuggestionClick = (prompt: string) => {
    sendChatMessage(prompt);
  };

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col bg-background min-h-0 relative select-text">
      {/* Dynamic Main Chat Scroll Area */}
      <div className="flex-1 overflow-y-auto custom-scrollbar px-4 py-6 pb-32">
        <div className="max-w-[800px] mx-auto w-full">
          {messages.length === 0 ? (
            /* Welcome / Empty State */
            <div className="text-center py-12 animate-in fade-in duration-300">
              <h2 className="text-3xl md:text-5xl font-extrabold text-primary mb-4 tracking-tight">
                BIT Mesra AI Assistant
              </h2>
              <p className="text-sm md:text-base text-on-surface-variant max-w-xl mx-auto mb-10 leading-relaxed">
                Ask anything about academics, notices, departments, clubs, campus navigation, or university information.
              </p>
              
              {/* Suggested Prompts Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left max-w-2xl mx-auto">
                {[
                  {
                    title: "When are my exams?",
                    desc: "Check semester calendar & schedules",
                  },
                  {
                    title: "Show my timetable",
                    desc: "View daily class routine",
                  },
                  {
                    title: "What notices are relevant to me?",
                    desc: "Latest updates from Deans & Depts",
                  },
                  {
                    title: "Where is the CS Department?",
                    desc: "Navigation & landmark directions",
                  },
                ].map((item) => (
                  <button
                    key={item.title}
                    onClick={() => handleSuggestionClick(item.title)}
                    className="p-4 bg-surface-container-low border border-outline-variant rounded-2xl hover:bg-surface-container hover:border-primary transition-all duration-150 group text-left cursor-pointer"
                  >
                    <p className="text-xs font-bold text-on-surface group-hover:text-primary uppercase tracking-wider">
                      {item.title}
                    </p>
                    <p className="text-[11px] text-on-surface-variant mt-1">
                      {item.desc}
                    </p>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            /* Active Message List */
            <div className="space-y-6">
              {/* Clear History Trigger */}
              <div className="flex justify-end mb-4">
                <button
                  onClick={clearHistory}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-surface-container border border-outline-variant hover:border-red-400 text-on-surface-variant hover:text-red-400 rounded-lg transition-colors text-xs font-bold uppercase tracking-wider cursor-pointer"
                >
                  <Trash2 size={12} />
                  <span>Clear Chat</span>
                </button>
              </div>

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
                <div className="flex flex-col items-start gap-2">
                  <div className="flex items-center gap-2 mb-1">
                    <div className="w-5 h-5 rounded bg-surface-container flex items-center justify-center border border-outline-variant">
                      <Bot size={12} className="text-primary" />
                    </div>
                    <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider">
                      BIT AI Assistant
                    </span>
                  </div>
                  <div className="bg-surface-container border border-outline-variant px-5 py-3 rounded-2xl max-w-[85%] text-xs text-on-surface-variant animate-pulse font-medium">
                    Thinking...
                  </div>
                </div>
              )}

              <div ref={bottomRef} />
            </div>
          )}
        </div>
      </div>

      {/* Floating Prompt Bar Container */}
      <div className="absolute bottom-0 left-0 right-0 p-6 pointer-events-none z-30">
        <div className="max-w-[800px] mx-auto w-full pointer-events-auto">
          <ChatInput 
            onSend={sendChatMessage} 
            onStopSpeaking={stopSpeaking} 
          />
          <p className="text-[10px] text-center text-on-surface-variant/40 mt-3 font-mono-code uppercase tracking-wider">
            BIT Mesra AI can make mistakes. Verify important academic notices via official portals.
          </p>
        </div>
      </div>
    </div>
  );
};

export default ChatWindow;
