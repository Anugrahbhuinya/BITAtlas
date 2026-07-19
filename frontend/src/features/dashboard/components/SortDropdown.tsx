import React from "react";
import { ArrowUpDown } from "lucide-react";

export type SortOption = "name-asc" | "name-desc" | "department" | "designation";

interface SortDropdownProps {
  value: SortOption;
  onChange: (value: SortOption) => void;
}

export const SortDropdown: React.FC<SortDropdownProps> = ({ value, onChange }) => {
  return (
    <div className="relative min-w-[150px]">
      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-on-surface-variant/60">
        <ArrowUpDown size={14} />
      </div>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as SortOption)}
        aria-label="Sort faculty list"
        className="w-full pl-9 pr-8 py-2 bg-surface-container border border-outline-variant/60 hover:border-outline focus:border-primary rounded-xl text-xs text-on-surface focus:outline-none cursor-pointer appearance-none"
      >
        <option value="name-asc">Name A-Z</option>
        <option value="name-desc">Name Z-A</option>
        <option value="department">Department</option>
        <option value="designation">Designation</option>
      </select>
      <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none text-on-surface-variant/60">
        <svg
          className="w-4 h-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </div>
    </div>
  );
};
