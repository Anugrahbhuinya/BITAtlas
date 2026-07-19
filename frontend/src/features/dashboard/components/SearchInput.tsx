import React from "react";
import { Search } from "lucide-react";

interface SearchInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

export const SearchInput: React.FC<SearchInputProps> = ({
  value,
  onChange,
  placeholder = "Search by name, email, department or interest..."
}) => {
  return (
    <div className="relative flex-1 min-w-[200px]">
      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-on-surface-variant/60">
        <Search size={16} />
      </div>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        aria-label="Search faculty members"
        className="w-full pl-9 pr-4 py-2 bg-surface-container border border-outline-variant/60 hover:border-outline focus:border-primary rounded-xl text-xs text-on-surface focus:outline-none transition-colors"
      />
    </div>
  );
};
