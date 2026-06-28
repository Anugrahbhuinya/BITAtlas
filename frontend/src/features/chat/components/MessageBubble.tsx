import { Volume2, VolumeX, MapPinned, Bot } from "lucide-react";
import { useNavigate } from "react-router-dom";
import type { ChatMessage } from "../types";
import { useMapStore } from "../../map/store/useMapStore";

interface Props {
  message: ChatMessage;
  onSpeak: (text: string) => void;
  onStopSpeaking: () => void;
  isSpeaking: boolean;
}

const locationMapping: Record<string, string> = {
  "cat hall": "CAT Hall",
  "central lecture hall": "CAT Hall",
  "central library": "Library",
  library: "Library",
  "administrative building": "Main Building",
  "main building": "Main Building",
  "administrative block": "Main Building",
  "institute administration offices": "Main Building",
};

export const MessageBubble = ({
  message,
  onSpeak,
  onStopSpeaking,
  isSpeaking,
}: Props) => {
  const isUser = message.sender === "user";
  const navigate = useNavigate();
  const setSelectedLocation = useMapStore((state) => state.setSelectedLocation);

  const detectedKey = Object.keys(locationMapping).find((key) =>
    message.text.toLowerCase().includes(key)
  );

  const detectedLocation = detectedKey
    ? locationMapping[detectedKey]
    : undefined;

  const handleOpenMap = () => {
    if (!detectedLocation) return;
    setSelectedLocation(detectedLocation);
    navigate("/map");
  };

  return (
    <div className={`flex flex-col mb-4 ${isUser ? "items-end" : "items-start"}`}>
      {/* Bot Message Header */}
      {!isUser && (
        <div className="flex items-center gap-2 mb-1.5 px-1 select-none">
          <div className="w-5 h-5 rounded bg-surface-container border border-outline-variant flex items-center justify-center">
            <Bot size={11} className="text-primary" />
          </div>
          <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider">
            BIT AI Assistant
          </span>
        </div>
      )}

      {/* Bubble Container */}
      <div className={`flex items-center gap-3 w-full ${isUser ? "justify-end" : "justify-start"}`}>
        <div
          className={`
            px-5 py-3
            rounded-2xl
            max-w-[85%]
            break-words
            text-xs
            leading-relaxed
            ${isUser 
              ? "bg-transparent border border-outline-variant text-primary font-semibold" 
              : "bg-surface-container border border-outline-variant text-on-surface"
            }
          `}
        >
          <div>{message.text}</div>

          {/* Map Redirect Trigger */}
          {!isUser && detectedLocation && (
            <button
              onClick={handleOpenMap}
              className="mt-3 flex items-center gap-1.5 bg-surface-container-high border border-outline-variant hover:border-primary px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider text-primary transition-all active:scale-[0.98] cursor-pointer"
            >
              <MapPinned size={12} />
              <span>Open on Map</span>
            </button>
          )}
        </div>

        {/* Speak Toggle Button */}
        {!isUser && (
          <button
            onClick={isSpeaking ? onStopSpeaking : () => onSpeak(message.text)}
            className={`
              p-2
              rounded-lg
              border
              transition-all
              duration-150
              cursor-pointer
              ${
                isSpeaking
                  ? "bg-red-500/10 border-red-500/20 text-red-400 hover:bg-red-500/20 scale-105"
                  : "bg-surface-container border-outline-variant text-on-surface-variant hover:text-primary hover:border-primary"
              }
            `}
            title={isSpeaking ? "Stop listening" : "Listen to answer"}
          >
            {isSpeaking ? <VolumeX size={13} /> : <Volume2 size={13} />}
          </button>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;
