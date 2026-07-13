import { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Trash2, AlertCircle, Bot, X } from "lucide-react";
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
  const navigate = useNavigate();
  const bottomRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const prefilledSent = useRef(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(() => {
    return location.state?.error || null;
  });

  // Catch errors passed via redirect state (e.g. from missing navigation data)
  useEffect(() => {
    if (location.state?.error) {
      // Clear location state history so it doesn't reappear on navigation back/forth
      navigate(location.pathname, { replace: true, state: {} });
    }
  }, [location.state, location.pathname, navigate]);

  useEffect(() => {
    const container = scrollContainerRef.current;
    if (!container) return;

    const isAtBottom = container.scrollHeight - container.scrollTop - container.clientHeight <= 150;
    const lastMessage = messages[messages.length - 1];
    const isUserMessage = lastMessage?.sender === "user";

    if (isAtBottom || isUserMessage || messages.length <= 2) {
      bottomRef.current?.scrollIntoView({
        behavior: "smooth",
      });
    }
  }, [messages, loading]);

  // Handle auto-seeding of dashboard quick prompts
  useEffect(() => {
    const statePrompt = location.state?.prefilledPrompt;
    if (statePrompt && !prefilledSent.current) {
      prefilledSent.current = true;
      sendChatMessage(statePrompt);
      // Clear history state to prevent duplicate prompt execution on refresh (F5)
      navigate(location.pathname, { replace: true, state: {} });
    }
  }, [location.state, location.pathname, navigate, sendChatMessage]);

  const handleSuggestionClick = (prompt: string) => {
    sendChatMessage(prompt);
  };

  const hasUserMessages = messages.some(m => m.sender === "user");

  return (
    <div className="h-full flex flex-col bg-background min-h-0 relative select-text">
      {/* Dynamic Main Chat Scroll Area */}
      <div ref={scrollContainerRef} className="flex-1 overflow-y-auto custom-scrollbar px-4 py-6">
        <div className="max-w-[850px] mx-auto w-full pb-6">
          {errorMessage && (
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 text-red-500 rounded-2xl flex items-center justify-between animate-in fade-in duration-200 select-none">
              <div className="flex items-center gap-2">
                <AlertCircle size={16} />
                <span className="text-xs font-bold leading-relaxed">{errorMessage}</span>
              </div>
              <button
                onClick={() => setErrorMessage(null)}
                className="p-1 text-red-500 hover:text-red-700 hover:bg-red-500/10 rounded-lg transition-colors cursor-pointer"
              >
                <X size={14} />
              </button>
            </div>
          )}

          {!hasUserMessages ? (
            /* Centered Welcome Hero State - Gemini/ChatGPT-inspired */
            <div className="flex flex-col items-center justify-center min-h-[60vh] text-center px-4 py-8 animate-in fade-in duration-500 select-none">
              <div className="w-12 h-12 rounded-xl bg-primary flex items-center justify-center text-background mb-6 shadow-lg">
                <Bot size={26} className="text-background" />
              </div>
              <h2 className="text-3xl md:text-4xl font-extrabold text-primary mb-3 tracking-tight">
                How can I help you today?
              </h2>
              <p className="text-xs md:text-sm text-on-surface-variant max-w-md mx-auto mb-8 leading-relaxed opacity-85">
                Ask anything about academics, notices, timetables, departments, campus buildings, food spots, or general information.
              </p>
              
              {/* Suggested Prompts Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-left max-w-xl w-full mx-auto">
                {[
                  {
                    title: "Show my timetable",
                    desc: "View daily class routine",
                  },
                  {
                    title: "Where should I go now?",
                    desc: "AI navigation & departure advisor",
                  },
                  {
                    title: "What notices are relevant to me?",
                    desc: "Latest updates from Deans & Depts",
                  },
                  {
                    title: "What's nearby right now?",
                    desc: "Cafeterias, ATMs, study spots",
                  },
                ].map((item) => (
                  <button
                    key={item.title}
                    onClick={() => handleSuggestionClick(item.title)}
                    className="p-4 bg-surface-container-low border border-outline-variant rounded-xl hover:bg-surface-container hover:border-primary transition-all duration-150 group text-left cursor-pointer shadow-xs"
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
                <div className="flex gap-3 max-w-[85%] md:max-w-[850px] w-full flex-row animate-in fade-in duration-200">
                  <div className="w-7 h-7 rounded-lg bg-surface-container border border-outline-variant flex items-center justify-center shrink-0 self-start mt-1 shadow-sm">
                    <Bot size={14} className="text-primary" />
                  </div>
                  <div className="flex-1 min-w-0 flex flex-col items-start">
                    <div className="bg-surface-container border border-outline-variant px-4 py-2.5 rounded-2xl rounded-tl-sm text-on-surface-variant font-medium">
                      <div className="flex items-center gap-1.5 py-1 px-1">
                        <span className="w-1.5 h-1.5 bg-primary/75 rounded-full animate-bounce [animation-duration:1s]" style={{ animationDelay: "0ms" }}></span>
                        <span className="w-1.5 h-1.5 bg-primary/75 rounded-full animate-bounce [animation-duration:1s]" style={{ animationDelay: "150ms" }}></span>
                        <span className="w-1.5 h-1.5 bg-primary/75 rounded-full animate-bounce [animation-duration:1s]" style={{ animationDelay: "300ms" }}></span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={bottomRef} />
            </div>
          )}
        </div>
      </div>

      {/* Sticky/Static Composer at the bottom in the normal document flow */}
      <div className="w-full border-t border-outline-variant/30 bg-background/95 backdrop-blur px-6 py-4 shrink-0 z-30">
        <div className="max-w-[850px] mx-auto w-full">
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
