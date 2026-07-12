// src/features/navigation/components/RoomCard.tsx

import React from "react";
import { Users, Info, Cpu, CheckSquare } from "lucide-react";
import type { Room } from "../types";

interface RoomCardProps {
  room: Room;
  buildingName?: string;
  onSelect?: (room: Room) => void;
}

export const RoomCard: React.FC<RoomCardProps> = ({ room, buildingName, onSelect }) => {
  const { room_number, room_name, floor, room_type, capacity, facilities, description } = room;

  return (
    <div
      className="group relative overflow-hidden rounded-xl border border-outline-variant/50 bg-surface/30 p-4 transition-all duration-300 hover:border-primary/40 hover:bg-surface/50 hover:shadow-md cursor-pointer"
      onClick={() => onSelect?.(room)}
    >
      <div className="flex justify-between items-start mb-2">
        <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-secondary/15 text-secondary">
          {room_type}
        </span>
        <span className="text-[11px] font-semibold text-on-surface/55">
          Floor {floor}
        </span>
      </div>

      <div className="flex items-baseline gap-1.5 mb-1">
        <h4 className="text-sm font-bold text-on-surface font-mono group-hover:text-primary transition-colors">
          {room_number}
        </h4>
        <span className="text-xs text-on-surface/75 truncate">{room_name}</span>
      </div>

      {buildingName && (
        <p className="text-[10px] text-on-surface/50 font-medium mb-2 uppercase tracking-wide">
          📍 {buildingName}
        </p>
      )}

      <p className="text-xs text-on-surface/60 line-clamp-2 mb-3 leading-relaxed">
        {description || "No description available for this room."}
      </p>

      <div className="flex items-center justify-between border-t border-outline-variant/30 pt-3 text-[11px] text-on-surface/55">
        <div className="flex items-center gap-1">
          <Users className="w-3.5 h-3.5 text-secondary/75" />
          <span>Cap: {capacity}</span>
        </div>
        
        {facilities.length > 0 && (
          <div className="flex gap-1.5 max-w-[120px] overflow-hidden truncate">
            {facilities.slice(0, 2).map((fac, idx) => (
              <span
                key={idx}
                className="text-[9px] px-1 py-0.2 rounded bg-surface-variant text-on-surface/80"
                title={fac}
              >
                {fac}
              </span>
            ))}
            {facilities.length > 2 && (
              <span className="text-[9px] text-on-surface/40 font-bold">
                +{facilities.length - 2}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
