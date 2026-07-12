// src/features/navigation/components/SearchFilters.tsx

import React from "react";
import { Filter, Accessibility } from "lucide-react";

interface SearchFiltersProps {
  category: string;
  setCategory: (category: string) => void;
  accessibilityOnly: boolean;
  setAccessibilityOnly: (only: boolean) => void;
  categories: string[];
}

export const SearchFilters: React.FC<SearchFiltersProps> = ({
  category,
  setCategory,
  accessibilityOnly,
  setAccessibilityOnly,
  categories
}) => {
  return (
    <div className="flex flex-wrap items-center gap-3 bg-surface/50 border border-outline-variant/60 rounded-xl p-3 shadow-md backdrop-blur-md">
      <div className="flex items-center gap-2 text-xs font-bold text-on-surface/75">
        <Filter className="w-3.5 h-3.5 text-primary" />
        Filter By:
      </div>

      <div className="flex flex-wrap gap-1.5">
        <button
          onClick={() => setCategory("")}
          className={`px-3 py-1 rounded-lg text-xs font-bold transition-all duration-200 ${
            category === ""
              ? "bg-primary text-background shadow-sm"
              : "bg-surface-variant/40 hover:bg-surface-variant/70 text-on-surface/80 border border-outline-variant/30"
          }`}
        >
          All Categories
        </button>
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setCategory(cat)}
            className={`px-3 py-1 rounded-lg text-xs font-bold transition-all duration-200 ${
              category === cat
                ? "bg-primary text-background shadow-sm"
                : "bg-surface-variant/40 hover:bg-surface-variant/70 text-on-surface/80 border border-outline-variant/30"
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      <div className="h-4 w-px bg-outline-variant/50 hidden md:block" />

      <button
        onClick={() => setAccessibilityOnly(!accessibilityOnly)}
        className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-bold border transition-all duration-200 ${
          accessibilityOnly
            ? "bg-primary/10 border-primary text-primary shadow-sm"
            : "border-outline-variant/40 hover:bg-surface-variant/50 text-on-surface/70"
        }`}
        title="Show Wheelchair Accessible Only"
      >
        <Accessibility className="w-3.5 h-3.5" />
        <span>Accessible Only</span>
      </button>
    </div>
  );
};
export default SearchFilters;
