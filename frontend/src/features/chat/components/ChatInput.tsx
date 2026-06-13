import { useState } from "react";
import { Send } from "lucide-react";

interface ChatInputProps {
  onSend: (message: string) => Promise<void>;
}

function ChatInput({ onSend }: ChatInputProps) {
  const [input, setInput] = useState("");

  const handleSend = async () => {
    const message = input.trim();

    if (!message) return;

    setInput("");

    await onSend(message);
  };

  const handleKeyDown = async (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();

      await handleSend();
    }
  };

  return (
    <div className="flex gap-3">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask anything about BIT Mesra..."
        className="
          flex-1
          bg-slate-800
          text-white
          border
          border-slate-700
          rounded-xl
          px-4
          py-3
          focus:outline-none
          focus:ring-2
          focus:ring-blue-500
        "
      />

      <button
        onClick={handleSend}
        className="
          bg-blue-600
          hover:bg-blue-700
          transition
          text-white
          px-5
          rounded-xl
          flex
          items-center
          justify-center
        "
      >
        <Send size={20} />
      </button>
    </div>
  );
}

export default ChatInput;
