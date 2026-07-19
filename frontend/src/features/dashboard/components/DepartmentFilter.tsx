import React from "react";

interface DepartmentFilterProps {
  value: string;
  onChange: (value: string) => void;
  departments: string[];
}

export const DepartmentFilter: React.FC<DepartmentFilterProps> = ({
  value,
  onChange,
  departments
}) => {
  return (
    <div className="relative min-w-[180px]">
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        aria-label="Filter by department"
        className="w-full px-4 py-2 bg-surface-container border border-outline-variant/60 hover:border-outline focus:border-primary rounded-xl text-xs text-on-surface focus:outline-none transition-colors cursor-pointer appearance-none"
      >
        <option value="all">All Departments</option>
        {departments.map((dept) => (
          <option key={dept} value={dept}>
            {dept}
          </option>
        ))}
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
