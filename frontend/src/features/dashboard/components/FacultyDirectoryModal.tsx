import React, { useState, useEffect, useRef, useMemo, Suspense } from "react";
import { X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { SearchInput } from "./SearchInput";
import { DepartmentFilter } from "./DepartmentFilter";
import { SortDropdown } from "./SortDropdown";
import type { SortOption } from "./SortDropdown";
import { DepartmentChips } from "./DepartmentChips";
import { FacultyCard } from "./FacultyCard";
import type { FacultyMember } from "./FacultyCard";
import { LoadingSkeleton } from "./LoadingSkeleton";
import { EmptyState } from "./EmptyState";
import { ErrorState } from "./ErrorState";
import { Pagination } from "./Pagination";
import { API_BASE_URL } from "../../../config";

// Lazy-load the profile drawer to optimize initial load times
const FacultyProfileDrawer = React.lazy(() =>
  import("./FacultyProfileDrawer").then((module) => ({
    default: module.FacultyProfileDrawer,
  }))
);

interface FacultyDirectoryModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const ITEMS_PER_PAGE = 10;

export const FacultyDirectoryModal: React.FC<FacultyDirectoryModalProps> = ({
  isOpen,
  onClose,
}) => {
  const [faculty, setFaculty] = useState<FacultyMember[]>([]);
  const [departments, setDepartments] = useState<string[]>([]);

  const [searchVal, setSearchVal] = useState("");
  const [debouncedSearchVal, setDebouncedSearchVal] = useState("");
  const [selectedDept, setSelectedDept] = useState("all");
  const [sortOption, setSortOption] = useState<SortOption>("name-asc");
  const [currentPage, setCurrentPage] = useState(1);

  const [selectedFaculty, setSelectedFaculty] = useState<FacultyMember | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  const modalRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  // 1. Search Debounce (300ms)
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchVal(searchVal);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchVal]);

  // Reset page to 1 whenever filters or search terms change
  useEffect(() => {
    setCurrentPage(1);
  }, [debouncedSearchVal, selectedDept]);

  // 2. Fetch Departments on modal mount
  useEffect(() => {
    if (!isOpen) return;
    const fetchDepts = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/api/faculty/departments`);
        if (!res.ok) throw new Error();
        const json = await res.json();
        setDepartments(json.data || []);
      } catch (err) {
        console.error("Failed to load departments", err);
      }
    };
    fetchDepts();
  }, [isOpen]);

  // 3. Fetch Faculty members dynamically from API
  const fetchFaculty = async () => {
    setLoading(true);
    setError(false);
    try {
      let url = `${API_BASE_URL}/api/faculty`;
      const query = debouncedSearchVal.trim();

      if (query) {
        url = `${API_BASE_URL}/api/faculty/search?q=${encodeURIComponent(query)}`;
      } else if (selectedDept !== "all") {
        url = `${API_BASE_URL}/api/faculty/department/${encodeURIComponent(selectedDept)}`;
      }

      const res = await fetch(url);
      if (!res.ok) throw new Error();
      const json = await res.json();

      let list = json.data || [];
      // Combine search and department filter on client side if both active
      if (query && selectedDept !== "all") {
        list = list.filter((m: FacultyMember) => m.department === selectedDept);
      }
      setFaculty(list);
    } catch (err) {
      console.error(err);
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchFaculty();
    }
  }, [isOpen, debouncedSearchVal, selectedDept]);

  // 4. Client-side sorting of faculty members
  const sortedFaculty = useMemo(() => {
    const list = [...faculty];
    if (sortOption === "name-asc") {
      list.sort((a, b) => a.name.localeCompare(b.name));
    } else if (sortOption === "name-desc") {
      list.sort((a, b) => b.name.localeCompare(a.name));
    } else if (sortOption === "department") {
      list.sort((a, b) => a.department.localeCompare(b.department));
    } else if (sortOption === "designation") {
      const getRank = (designation: string | null) => {
        if (!designation) return 99;
        const d = designation.toLowerCase();
        if (d.includes("professor") && d.includes("assistant")) return 3;
        if (d.includes("professor") && d.includes("associate")) return 2;
        if (d.includes("professor")) return 1;
        return 4;
      };
      list.sort((a, b) => getRank(a.designation) - getRank(b.designation));
    }
    return list;
  }, [faculty, sortOption]);

  // 5. Client-side slicing for pagination
  const totalPages = Math.ceil(sortedFaculty.length / ITEMS_PER_PAGE);
  const paginatedFaculty = useMemo(() => {
    const start = (currentPage - 1) * ITEMS_PER_PAGE;
    return sortedFaculty.slice(start, start + ITEMS_PER_PAGE);
  }, [sortedFaculty, currentPage]);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    // Smooth scroll the content area back to the top on page transition
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  const handleClearFilters = () => {
    setSearchVal("");
    setSelectedDept("all");
    setCurrentPage(1);
    // Restore focus to search input
    if (modalRef.current) {
      const input = modalRef.current.querySelector("input");
      if (input) input.focus();
    }
  };

  // Keyboard accessibility Esc handler
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        if (isDrawerOpen) {
          setIsDrawerOpen(false);
        } else {
          onClose();
        }
      }
    };
    if (isOpen) {
      window.addEventListener("keydown", handleKeyDown);
      return () => window.removeEventListener("keydown", handleKeyDown);
    }
  }, [isOpen, isDrawerOpen, onClose]);

  const handleCardClick = (member: FacultyMember) => {
    setSelectedFaculty(member);
    setIsDrawerOpen(true);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop overlay */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
        className="fixed inset-0 bg-background/80 backdrop-blur-sm"
      />

      {/* Modal Container */}
      <motion.div
        ref={modalRef}
        initial={{ opacity: 0, scale: 0.95, y: 10 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 10 }}
        transition={{ type: "spring", duration: 0.3 }}
        role="dialog"
        aria-modal="true"
        aria-label="Faculty Directory Modal"
        className="relative w-full max-w-4xl max-h-[85vh] bg-surface-container-low border border-outline-variant/40 rounded-2xl shadow-2xl flex flex-col overflow-hidden z-10 text-on-surface font-sans"
      >
        {/* Sticky Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-outline-variant/20 select-none shrink-0 bg-surface-container-low z-20">
          <div>
            <div className="flex items-center gap-3">
              <h3 className="text-sm font-extrabold text-primary uppercase tracking-wider">
                Faculty Directory
              </h3>
              <span className="bg-primary/10 border border-primary/20 text-primary text-[8px] font-bold px-2 py-0.5 rounded-full">
                {faculty.length} Matches
              </span>
            </div>
            <p className="text-[10px] text-on-surface-variant mt-1 leading-none font-medium">
              Explore contact information, office hours, and research interests of BIT Mesra faculty.
            </p>
          </div>
          <button
            onClick={onClose}
            aria-label="Close directory modal"
            className="p-1.5 text-on-surface-variant hover:text-primary bg-surface-container hover:bg-surface-variant rounded-lg transition-colors cursor-pointer"
          >
            <X size={16} />
          </button>
        </div>

        {/* Sticky Toolbar (Search, Filter, Sort and Chips) */}
        <div className="sticky top-0 bg-surface-container-low/95 backdrop-blur-xs z-20 px-6 py-4 border-b border-outline-variant/10 space-y-3 shrink-0">
          <div className="flex flex-wrap gap-4 items-center justify-between">
            <div className="flex-1 flex gap-4 min-w-0">
              <SearchInput value={searchVal} onChange={setSearchVal} />
              <DepartmentFilter
                value={selectedDept}
                onChange={setSelectedDept}
                departments={departments}
              />
            </div>
            <SortDropdown value={sortOption} onChange={setSortOption} />
          </div>
          <DepartmentChips
            departments={departments}
            selectedDept={selectedDept}
            onSelect={setSelectedDept}
          />
        </div>

        {/* Content Body (Scrollable) */}
        <div
          ref={scrollContainerRef}
          className="flex-1 overflow-y-auto custom-scrollbar p-6 min-h-[300px] scroll-smooth"
        >
          {loading ? (
            <LoadingSkeleton />
          ) : error ? (
            <ErrorState onRetry={fetchFaculty} />
          ) : paginatedFaculty.length === 0 ? (
            <EmptyState onClearFilters={handleClearFilters} />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {paginatedFaculty.map((member) => (
                <FacultyCard
                  key={member.id}
                  member={member}
                  onClick={() => handleCardClick(member)}
                />
              ))}
            </div>
          )}

          {/* Pagination Controls */}
          {!loading && !error && faculty.length > 0 && (
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={handlePageChange}
            />
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-6 py-3 border-t border-outline-variant/10 bg-surface-container/10 text-[9px] font-bold text-on-surface-variant/60 uppercase tracking-wider select-none shrink-0">
          <span>Displaying {paginatedFaculty.length} of {faculty.length} entries</span>
          <span>Birla Institute of Technology, Mesra</span>
        </div>
      </motion.div>

      {/* Profile Drawer Panel */}
      <AnimatePresence>
        {isDrawerOpen && (
          <Suspense fallback={null}>
            <FacultyProfileDrawer
              isOpen={isDrawerOpen}
              onClose={() => setIsDrawerOpen(false)}
              member={selectedFaculty}
            />
          </Suspense>
        )}
      </AnimatePresence>
    </div>
  );
};
