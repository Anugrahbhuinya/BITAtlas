import React from "react";

interface DepartmentChipsProps {
  departments: string[];
  selectedDept: string;
  onSelect: (dept: string) => void;
}

export const DepartmentChips: React.FC<DepartmentChipsProps> = ({
  departments,
  selectedDept,
  onSelect
}) => {
  return (
    <div className="w-full overflow-x-auto no-scrollbar py-2 flex gap-2 select-none border-t border-outline-variant/10">
      <button
        onClick={() => onSelect("all")}
        className={`px-3 py-1 text-[9px] font-extrabold uppercase tracking-wider rounded-full border transition-all cursor-pointer whitespace-nowrap ${
          selectedDept === "all"
            ? "bg-primary text-background border-primary"
            : "bg-surface-container border-outline-variant/50 text-primary hover:border-primary/50"
        }`}
      >
        All Departments
      </button>
      {departments.map((dept) => {
        const isSelected = selectedDept === dept;
        return (
          <button
            key={dept}
            onClick={() => onSelect(dept)}
            className={`px-3 py-1 text-[9px] font-extrabold uppercase tracking-wider rounded-full border transition-all cursor-pointer whitespace-nowrap ${
              isSelected
                ? "bg-primary text-background border-primary"
                : "bg-surface-container border-outline-variant/50 text-primary hover:border-primary/50"
            }`}
          >
            {dept}
          </button>
        );
      })}
    </div>
  );
};
export default DepartmentChips;
