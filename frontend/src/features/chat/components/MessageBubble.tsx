import type { ChatMessage } from "../types";

interface Props {
  message: ChatMessage;
}

function MessageBubble({ message }: Props) {
  const isUser = message.sender === "user";

  return (
    <div className={`flex mb-4 ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`
          px-4 py-3
          rounded-2xl
          max-w-[70%]
          break-words
          ${isUser ? "bg-blue-600 text-white" : "bg-slate-800 text-white"}
        `}
      >
        {message.text}
      </div>
    </div>
  );
}

export default MessageBubble;
