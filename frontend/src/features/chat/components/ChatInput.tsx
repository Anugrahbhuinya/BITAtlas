import { useState, useRef, useEffect } from "react";
import { Send, Mic, Square } from "lucide-react";
import { useSpeechRecognition } from "../hooks/useSpeechRecognition";

interface ChatInputProps {
  onSend: (message: string, isVoice?: boolean) => Promise<void>;
  onStopSpeaking: () => void;
}

export const ChatInput = ({ onSend, onStopSpeaking }: ChatInputProps) => {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const { isSupported, isListening, startListening, stopListening } =
    useSpeechRecognition();

  // Auto-resize textarea height as content changes
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [input]);

  const handleSend = async () => {
    const message = input.trim();
    if (!message) return;

    setInput("");
    onStopSpeaking();
    await onSend(message, false);
  };

  const handleKeyDown = async (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      await handleSend();
    }
  };

  const handleVoiceInput = () => {
    onStopSpeaking();
    startListening(async (text: string) => {
      if (text.trim()) {
        setInput(text);
        await onSend(text, true);
        setInput("");
      }
    });
  };

  return (
    <div className="w-full flex flex-col gap-1.5 bg-[#18181b]/95 backdrop-blur-md border border-outline-variant rounded-xl p-1.5 relative shadow-2xl transition-all focus-within:border-primary/80 focus-within:ring-1 focus-within:ring-primary/20">
      {/* Listening Status Indicator */}
      {isListening && (
        <div className="px-3 pt-1 text-red-400 text-[10px] font-bold animate-pulse flex items-center gap-1.5 select-none">
          <span className="w-1.5 h-1.5 bg-red-500 rounded-full"></span>
          🎤 LISTENING...
        </div>
      )}

      {/* Growing Prompt Textarea */}
      <textarea
        ref={textareaRef}
        rows={1}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask BIT AI anything..."
        aria-label="Query input box"
        className="w-full bg-transparent border-none focus:outline-none focus:ring-0 text-on-surface text-xs md:text-sm py-1.5 px-3 resize-none min-h-[32px] max-h-[120px] placeholder:text-on-surface-variant/40"
      />

      {/* Bottom Controls Bar */}
      <div className="flex items-center justify-between border-t border-outline-variant/20 px-2 pt-1.5 pb-0.5 shrink-0">
        <div className="flex items-center gap-1">
          {isSupported && (
            <button
              type="button"
              onClick={isListening ? stopListening : handleVoiceInput}
              aria-label={isListening ? "Stop listening to voice input" : "Start voice input"}
              className={`
                p-1.5
                rounded-lg
                flex
                items-center
                justify-center
                transition-colors
                cursor-pointer
                ${
                  isListening
                    ? "bg-red-500/10 text-red-400 border border-red-500/20"
                    : "text-on-surface-variant hover:bg-surface-container-high hover:text-primary"
                }
              `}
              title={isListening ? "Stop Listening" : "Start Voice Input"}
            >
              {isListening ? <Square size={14} /> : <Mic size={14} />}
            </button>
          )}
        </div>

        <div className="flex items-center gap-3 select-none">
          <span className="text-[10px] text-on-surface-variant/50 hidden sm:block font-medium">
            Press ⏎ to send
          </span>
          <button
            onClick={handleSend}
            disabled={!input.trim()}
            aria-label="Send query"
            className={`
              w-8 h-8
              rounded-xl
              flex
              items-center
              justify-center
              transition-all
              active:scale-95
              cursor-pointer
              ${input.trim()
                ? "bg-primary text-background hover:bg-primary/90 shadow-md"
                : "bg-surface-container border border-outline-variant text-on-surface-variant/30 cursor-not-allowed opacity-50"
              }
            `}
            title="Send Message"
          >
            <Send size={12} className={input.trim() ? "text-background" : "text-on-surface-variant/30"} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInput;
