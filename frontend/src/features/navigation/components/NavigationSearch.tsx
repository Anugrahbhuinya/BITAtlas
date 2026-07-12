// src/features/navigation/components/NavigationSearch.tsx

import React, { useState, useEffect, useRef } from "react";
import { Search, X, MapPin, Landmark, Coffee, HelpCircle, Loader2, History } from "lucide-react";
import { useNavigationSearch } from "../hooks/useNavigation";
import type { NavigationSearchResult } from "../types";

interface NavigationSearchProps {
  onResultSelect: (result: NavigationSearchResult) => void;
  onClear?: () => void;
}

export const NavigationSearch: React.FC<NavigationSearchProps> = ({ onResultSelect, onClear }) => {
  const { query, setQuery, results, loading } = useNavigationSearch();
  const [isOpen, setIsOpen] = useState(false);
  const [focusedIndex, setFocusedIndex] = useState(-1);
  const containerRef = useRef<HTMLDivElement>(null);

  // Load recents from localStorage
  const [recents, setRecents] = useState<NavigationSearchResult[]>(() => {
    const saved = localStorage.getItem("map_recent_searches");
    return saved ? JSON.parse(saved) : [];
  });

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Reset focused index when query or results change
  useEffect(() => {
    setFocusedIndex(-1);
  }, [query, results]);

  const handleSelect = (result: NavigationSearchResult) => {
    onResultSelect(result);
    setQuery(result.name);
    setIsOpen(false);

    // Save to recents history
    const updated = [result, ...recents.filter((r) => r._id !== result._id)].slice(0, 5);
    setRecents(updated);
    localStorage.setItem("map_recent_searches", JSON.stringify(updated));
  };

  const handleClear = () => {
    setQuery("");
    setIsOpen(false);
    setFocusedIndex(-1);
    onClear?.();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    const listToUse = query.trim().length >= 2 ? results : recents;
    if (!listToUse || listToUse.length === 0) return;

    if (e.key === "ArrowDown") {
      e.preventDefault();
      setFocusedIndex((prev) => (prev < listToUse.length - 1 ? prev + 1 : 0));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setFocusedIndex((prev) => (prev > 0 ? prev - 1 : listToUse.length - 1));
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (focusedIndex >= 0 && focusedIndex < listToUse.length) {
        handleSelect(listToUse[focusedIndex]);
      } else if (listToUse.length > 0) {
        handleSelect(listToUse[0]);
      }
    } else if (e.key === "Escape") {
      setIsOpen(false);
    }
  };

  const getIcon = (type: string) => {
    switch (type) {
      case "building":
        return <MapPin className="w-4 h-4 text-primary shrink-0" />;
      case "room":
        return <HelpCircle className="w-4 h-4 text-secondary shrink-0" />;
      case "landmark":
        return <Landmark className="w-4 h-4 text-amber-500 shrink-0" />;
      case "facility":
        return <Coffee className="w-4 h-4 text-emerald-500 shrink-0" />;
      default:
        return <MapPin className="w-4 h-4 text-on-surface/50 shrink-0" />;
    }
  };

  const getTypeBadgeColor = (type: string) => {
    switch (type) {
      case "building":
        return "bg-blue-500/10 text-blue-400 border border-blue-500/20";
      case "room":
        return "bg-purple-500/10 text-purple-400 border border-purple-500/20";
      case "landmark":
        return "bg-amber-500/10 text-amber-400 border border-amber-500/20";
      case "facility":
        return "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20";
      default:
        return "bg-on-surface/5 text-on-surface/50 border border-outline-variant/30";
    }
  };

  return (
    <div ref={containerRef} className="relative w-full z-[1000]">
      <div className="relative flex items-center w-full bg-surface/85 border border-outline-variant/65 rounded-2xl px-4 py-2.5 shadow-2xl backdrop-blur-md focus-within:border-primary/60 focus-within:bg-surface transition duration-200">
        <Search className="w-4 h-4 text-on-surface/40 mr-2.5 shrink-0" />
        <input
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
          onKeyDown={handleKeyDown}
          placeholder="Search classrooms, buildings, canteens, ATMs..."
          className="flex-1 bg-transparent text-sm text-on-surface placeholder-on-surface/40 focus:outline-none min-w-0"
        />
        {loading && <Loader2 className="w-4 h-4 animate-spin text-primary mr-2 shrink-0" />}
        {query && (
          <button onClick={handleClear} className="p-0.5 rounded-full hover:bg-surface-variant text-on-surface/60 shrink-0">
            <X className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      {/* Dropdown Options */}
      {isOpen && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-surface/95 border border-outline-variant/65 rounded-2xl shadow-2xl backdrop-blur-xl overflow-hidden max-h-72 overflow-y-auto z-[2000] custom-scrollbar text-left">
          {/* Query Results */}
          {query.trim().length >= 2 ? (
            results.length > 0 ? (
              <div className="py-1">
                {results.map((result, idx) => (
                  <div
                    key={result._id}
                    onClick={() => handleSelect(result)}
                    className={`flex items-center gap-3 px-4 py-2.5 cursor-pointer border-b border-outline-variant/20 last:border-0 transition duration-150 ${
                      focusedIndex === idx ? "bg-primary/10 border-primary" : "hover:bg-primary/5"
                    }`}
                  >
                    <div className="p-1.5 rounded-xl bg-surface-variant/40 shrink-0">
                      {getIcon(result.type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex justify-between items-center gap-2">
                        <p className="text-xs font-black text-on-surface truncate">{result.name}</p>
                        <span className={`text-[8px] font-black uppercase px-1.5 py-0.5 rounded shrink-0 ${getTypeBadgeColor(result.type)}`}>
                          {result.type}
                        </span>
                      </div>
                      <p className="text-[10px] text-on-surface/50 truncate mt-0.5">{result.snippet}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-4 text-center text-xs text-on-surface/50 font-semibold">
                {loading ? "Searching..." : "No matches found."}
              </div>
            )
          ) : (
            /* Recent Searches Suggestions list when query is empty */
            recents.length > 0 && (
              <div className="py-1">
                <div className="px-4 py-1.5 border-b border-outline-variant/20">
                  <p className="text-[9px] uppercase font-bold text-on-surface/40 tracking-wider flex items-center gap-1.5">
                    <History className="w-3 h-3" />
                    Recent Searches
                  </p>
                </div>
                {recents.map((item, idx) => (
                  <div
                    key={item._id}
                    onClick={() => handleSelect(item)}
                    className={`flex items-center gap-3 px-4 py-2 cursor-pointer border-b border-outline-variant/20 last:border-0 transition duration-150 ${
                      focusedIndex === idx ? "bg-primary/10 border-primary" : "hover:bg-primary/5"
                    }`}
                  >
                    <History className="w-3.5 h-3.5 text-on-surface/30 shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="flex justify-between items-center gap-2">
                        <p className="text-xs font-bold text-on-surface/85 truncate">{item.name}</p>
                        <span className={`text-[8px] font-extrabold uppercase px-1.5 py-0.2 rounded shrink-0 ${getTypeBadgeColor(item.type)}`}>
                          {item.type}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )
          )}
        </div>
      )}
    </div>
  );
};
export default NavigationSearch;
