import React from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalPages,
  onPageChange
}) => {
  if (totalPages <= 1) return null;

  return (
    <nav
      aria-label="Pagination Navigation"
      className="flex justify-between items-center mt-6 pt-4 border-t border-outline-variant/10 select-none text-on-surface font-sans"
    >
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        aria-label="Go to previous page"
        className="flex items-center gap-1 px-3 py-1.5 border border-outline-variant/60 disabled:opacity-40 enabled:hover:border-primary text-[10px] font-extrabold uppercase tracking-wider rounded-lg transition-colors cursor-pointer disabled:cursor-not-allowed active:enabled:scale-[0.98]"
      >
        <ChevronLeft size={12} />
        <span>Prev</span>
      </button>

      <span className="text-[10px] font-extrabold uppercase tracking-wider text-on-surface-variant">
        Page {currentPage} of {totalPages}
      </span>

      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        aria-label="Go to next page"
        className="flex items-center gap-1 px-3 py-1.5 border border-outline-variant/60 disabled:opacity-40 enabled:hover:border-primary text-[10px] font-extrabold uppercase tracking-wider rounded-lg transition-colors cursor-pointer disabled:cursor-not-allowed active:enabled:scale-[0.98]"
      >
        <span>Next</span>
        <ChevronRight size={12} />
      </button>
    </nav>
  );
};
export default Pagination;
