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
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
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
    <div className="w-full flex flex-col gap-2 bg-[#18181b]/95 backdrop-blur-md border border-outline-variant rounded-2xl p-2 relative shadow-2xl transition-all focus-within:border-primary">
      {/* Listening Status Indicator */}
      {isListening && (
        <div className="px-4 pt-2 text-red-400 text-xs font-bold animate-pulse flex items-center gap-1.5 select-none">
          <span className="w-2 h-2 bg-red-500 rounded-full"></span>
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
        className="w-full bg-transparent border-none focus:outline-none focus:ring-0 text-on-surface text-xs md:text-sm py-2.5 px-4 resize-none min-h-[40px] max-h-[180px] placeholder:text-on-surface-variant/40"
      />

      {/* Bottom Controls Bar */}
      <div className="flex items-center justify-between border-t border-outline-variant/30 px-2 pt-2 pb-1 shrink-0">
        <div className="flex items-center gap-1">
          {isSupported && (
            <button
              type="button"
              onClick={isListening ? stopListening : handleVoiceInput}
              className={`
                p-2
                rounded-xl
                flex
                items-center
                justify-center
                transition-colors
                cursor-pointer
                ${
                  isListening
                    ? "bg-red-500/10 text-red-400 border border-red-500/20"
                    : "text-on-surface-variant hover:bg-surface-variant rounded-xl"
                }
              `}
              title={isListening ? "Stop Listening" : "Start Voice Input"}
            >
              {isListening ? <Square size={16} /> : <Mic size={16} />}
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
            className={`
              w-9 h-9
              rounded-xl
              flex
              items-center
              justify-center
              transition-all
              active:scale-95
              cursor-pointer
              ${input.trim()
                ? "bg-primary text-background hover:bg-primary/95"
                : "bg-surface-container border border-outline-variant text-on-surface-variant/30 cursor-not-allowed"
              }
            `}
            title="Send Message"
          >
            <Send size={14} className={input.trim() ? "text-background" : "text-on-surface-variant/30"} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInput;
