import { SearchBar } from "./SearchBar";
import { Filter, SortAsc, RotateCcw } from "lucide-react";

interface TableToolbarProps {
  searchValue: string;
  onSearchChange: (value: string) => void;
  statusFilter: string;
  onStatusFilterChange: (value: string) => void;
  typeFilter: string;
  onTypeFilterChange: (value: string) => void;
  sortBy: string;
  onSortByChange: (value: string) => void;
  onReset: () => void;
}

export const TableToolbar = ({
  searchValue,
  onSearchChange,
  statusFilter,
  onStatusFilterChange,
  typeFilter,
  onTypeFilterChange,
  sortBy,
  onSortByChange,
  onReset,
}: TableToolbarProps) => {
  return (
    <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 p-4 bg-slate-900/40 rounded-2xl border border-slate-800/40">
      {/* Search box */}
      <div className="w-full lg:w-72">
        <SearchBar
          value={searchValue}
          onChange={onSearchChange}
          placeholder="Search file name..."
        />
      </div>

      {/* Action items */}
      <div className="flex flex-wrap items-center gap-3">
        {/* Status Filter */}
        <div className="flex items-center gap-2">
          <Filter className="w-3.5 h-3.5 text-slate-400" />
          <select
            value={statusFilter}
            onChange={(e) => onStatusFilterChange(e.target.value)}
            className="text-xs bg-slate-900 border border-slate-800 text-slate-300 rounded-xl px-3 py-2 focus:outline-none focus:border-blue-500/60 cursor-pointer"
          >
            <option value="all">All Statuses</option>
            <option value="indexed">Indexed</option>
            <option value="pending">Pending</option>
            <option value="failed">Failed</option>
          </select>
        </div>

        {/* Type Filter */}
        <select
          value={typeFilter}
          onChange={(e) => onTypeFilterChange(e.target.value)}
          className="text-xs bg-slate-900 border border-slate-800 text-slate-300 rounded-xl px-3 py-2 focus:outline-none focus:border-blue-500/60 cursor-pointer"
        >
          <option value="all">All Types</option>
          <option value="pdf">PDF Docs</option>
          <option value="json">JSON Datasets</option>
          <option value="txt">TXT Files</option>
        </select>

        {/* Sort selector */}
        <div className="flex items-center gap-2">
          <SortAsc className="w-3.5 h-3.5 text-slate-400" />
          <select
            value={sortBy}
            onChange={(e) => onSortByChange(e.target.value)}
            className="text-xs bg-slate-900 border border-slate-800 text-slate-300 rounded-xl px-3 py-2 focus:outline-none focus:border-blue-500/60 cursor-pointer"
          >
            <option value="created_desc">Newest Created</option>
            <option value="created_asc">Oldest Created</option>
            <option value="name_asc">Name (A-Z)</option>
            <option value="size_desc">Size (Large first)</option>
          </select>
        </div>

        {/* Reset filter button */}
        {(searchValue || statusFilter !== "all" || typeFilter !== "all" || sortBy !== "created_desc") && (
          <button
            onClick={onReset}
            className="flex items-center gap-1.5 px-3 py-2 text-xs font-semibold bg-slate-800 text-slate-300 border border-slate-700/30 rounded-xl hover:bg-slate-700/60 hover:text-white transition-colors cursor-pointer"
          >
            <RotateCcw className="w-3 h-3" />
            <span>Reset</span>
          </button>
        )}
      </div>
    </div>
  );
};
