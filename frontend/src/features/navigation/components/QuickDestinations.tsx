// src/features/navigation/components/QuickDestinations.tsx

import React from "react";
import { BookOpen, Users, Compass, Laptop, Landmark, Coffee, Activity } from "lucide-react";

interface QuickDestinationItem {
  id: string;
  name: string;
  icon: React.ReactNode;
  color: string;
}

interface QuickDestinationsProps {
  onSelect: (id: string, name: string) => void;
  disabled?: boolean;
}

export const QuickDestinations: React.FC<QuickDestinationsProps> = ({ onSelect, disabled = false }) => {
  const items: QuickDestinationItem[] = [
    { id: "b_lib", name: "Central Library", icon: <BookOpen className="w-3.5 h-3.5" />, color: "text-blue-400 bg-blue-500/10 border-blue-500/20" },
    { id: "b_sac", name: "SAC (Student Activity Centre)", icon: <Users className="w-3.5 h-3.5" />, color: "text-purple-400 bg-purple-500/10 border-purple-500/20" },
    { id: "f_gate", name: "Main Gate", icon: <Compass className="w-3.5 h-3.5" />, color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20" },
    { id: "b_cse", name: "CSE Department", icon: <Laptop className="w-3.5 h-3.5" />, color: "text-cyan-400 bg-cyan-500/10 border-cyan-500/20" },
    { id: "f_atm", name: "SBI ATM", icon: <Landmark className="w-3.5 h-3.5" />, color: "text-amber-400 bg-amber-500/10 border-amber-500/20" },
    { id: "f_medical", name: "Medical Centre", icon: <Activity className="w-3.5 h-3.5" />, color: "text-rose-400 bg-rose-500/10 border-rose-500/20" },
    { id: "f_cafe", name: "Food Court", icon: <Coffee className="w-3.5 h-3.5" />, color: "text-orange-400 bg-orange-500/10 border-orange-500/20" }
  ];

  return (
    <div className="space-y-2 text-left">
      <p className="text-[9px] uppercase font-bold text-on-surface/40 tracking-wider">Quick Launch Destinations</p>
      <div className="flex flex-wrap gap-1.5">
        {items.map((item) => (
          <button
            key={item.id}
            onClick={() => onSelect(item.id, item.name)}
            disabled={disabled}
            className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl border text-[11px] font-bold hover:scale-105 transition-all duration-150 ${item.color} disabled:opacity-40 disabled:hover:scale-100`}
          >
            {item.icon}
            {item.name.split(" ")[0]}
          </button>
        ))}
      </div>
    </div>
  );
};
export default QuickDestinations;
