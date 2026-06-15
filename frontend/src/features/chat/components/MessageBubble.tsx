import { Volume2, VolumeX, MapPinned } from "lucide-react";

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

function MessageBubble({
  message,
  onSpeak,
  onStopSpeaking,
  isSpeaking,
}: Props) {
  const isUser = message.sender === "user";

  const navigate = useNavigate();

  const setSelectedLocation = useMapStore((state) => state.setSelectedLocation);

  const detectedKey = Object.keys(locationMapping).find((key) =>
    message.text.toLowerCase().includes(key),
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
    <div
      className={`flex items-end mb-4 gap-2 ${
        isUser ? "justify-end" : "justify-start"
      }`}
    >
      <div
        className={`
          px-4 py-3
          rounded-2xl
          max-w-[70%]
          break-words
          ${isUser ? "bg-blue-600 text-white" : "bg-slate-800 text-white"}
        `}
      >
        <div>{message.text}</div>

        {!isUser && detectedLocation && (
          <button
            onClick={handleOpenMap}
            className="
              mt-3
              flex
              items-center
              gap-2
              bg-blue-600
              hover:bg-blue-700
              px-3
              py-2
              rounded-lg
              text-sm
              transition
            "
          >
            <MapPinned size={16} />
            Open on Map
          </button>
        )}
      </div>

      {!isUser && (
        <button
          onClick={isSpeaking ? onStopSpeaking : () => onSpeak(message.text)}
          className={`
            p-2
            rounded-full
            transition-all
            duration-200
            ${
              isSpeaking
                ? "bg-red-500/20 text-red-400 hover:bg-red-500/30 scale-110 animate-pulse"
                : "text-slate-400 hover:bg-slate-800 hover:text-white hover:scale-105"
            }
          `}
          title={isSpeaking ? "Stop listening" : "Listen to answer"}
        >
          {isSpeaking ? <VolumeX size={16} /> : <Volume2 size={16} />}
        </button>
      )}
    </div>
  );
}

export default MessageBubble;
