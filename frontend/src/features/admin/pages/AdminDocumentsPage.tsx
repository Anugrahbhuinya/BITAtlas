import { useState, useEffect } from "react";
import adminApi from "../services/api";
import { TableToolbar } from "../components/TableToolbar";
import { TableSkeleton } from "../components/LoadingSkeleton";
import { EmptyState } from "../components/EmptyState";
import { ConfirmationDialog } from "../components/ConfirmationDialog";
import { useAdminStore } from "../hooks/adminStore";
import { FileText, Trash2, Eye, Upload } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export const AdminDocumentsPage = () => {
  const { showToast } = useAdminStore();
  const [documents, setDocuments] = useState<any[]>([]);
  const [filteredDocs, setFilteredDocs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Filter and Sorting states
  const [searchValue, setSearchValue] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [typeFilter, setTypeFilter] = useState("all");
  const [sortBy, setSortBy] = useState("created_desc");

  // Deletion state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [docToDelete, setDocToDelete] = useState<any>(null);

  // Pagination states
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5;

  const fetchDocs = async () => {
    setLoading(true);
    try {
      const response = await adminApi.get("/api/admin/documents");
      setDocuments(response.data.documents || []);
    } catch (e) {
      console.error("Failed to load documents", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  // Filter & sort logic
  useEffect(() => {
    let result = [...documents];

    // 1. Text Search Filter
    if (searchValue.trim()) {
      const q = searchValue.toLowerCase();
      result = result.filter((doc) => doc.filename.toLowerCase().includes(q));
    }

    // 2. Status Filter
    if (statusFilter !== "all") {
      result = result.filter((doc) => doc.status.toLowerCase() === statusFilter);
    }

    // 3. Type Filter
    if (typeFilter !== "all") {
      result = result.filter((doc) => doc.type.toLowerCase() === typeFilter);
    }

    // 4. Sorting
    result.sort((a, b) => {
      if (sortBy === "created_desc") {
        return new Date(b.created).getTime() - new Date(a.created).getTime();
      }
      if (sortBy === "created_asc") {
        return new Date(a.created).getTime() - new Date(b.created).getTime();
      }
      if (sortBy === "name_asc") {
        return a.filename.localeCompare(b.filename);
      }
      if (sortBy === "size_desc") {
        return b.size_bytes - a.size_bytes;
      }
      return 0;
    });

    setFilteredDocs(result);
    setCurrentPage(1); // Reset page on filter
  }, [documents, searchValue, statusFilter, typeFilter, sortBy]);

  const handleResetFilters = () => {
    setSearchValue("");
    setStatusFilter("all");
    setTypeFilter("all");
    setSortBy("created_desc");
    showToast("Filters reset successfully", "info");
  };

  const handleUploadClick = () => {
    showToast("PDF ingestion and vector parsing are scheduled for Phase 5B.", "info");
  };

  const openDeleteDialog = (doc: any) => {
    setDocToDelete(doc);
    setDeleteDialogOpen(true);
  };

  const confirmDeleteDoc = () => {
    if (docToDelete) {
      // Perform local mock deletion
      setDocuments(documents.filter((d) => d.id !== docToDelete.id));
      showToast(`Document "${docToDelete.filename}" removed from knowledge base`, "success");
      setDocToDelete(null);
    }
  };

  // Pagination calculation
  const totalPages = Math.ceil(filteredDocs.length / itemsPerPage);
  const pagedDocs = filteredDocs.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const formatSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-100 tracking-tight flex items-center gap-2">
            <span>Knowledge Documents</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Audit and filter file segments ingested into ChromaDB.
          </p>
        </div>

        <button
          onClick={handleUploadClick}
          className="px-4 py-2.5 text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white rounded-xl shadow-lg hover:shadow-blue-500/20 active:scale-[0.98] transition-all flex items-center gap-2 cursor-pointer select-none"
        >
          <Upload className="w-4 h-4" />
          <span>Upload Document</span>
        </button>
      </div>

      {/* Toolbar controls */}
      <TableToolbar
        searchValue={searchValue}
        onSearchChange={setSearchValue}
        statusFilter={statusFilter}
        onStatusFilterChange={setStatusFilter}
        typeFilter={typeFilter}
        onTypeFilterChange={setTypeFilter}
        sortBy={sortBy}
        onSortByChange={setSortBy}
        onReset={handleResetFilters}
      />

      {/* Table Section */}
      <div className="glass-panel rounded-2xl border border-slate-800/40 overflow-hidden">
        {loading ? (
          <div className="p-6">
            <TableSkeleton rows={4} cols={5} />
          </div>
        ) : filteredDocs.length === 0 ? (
          <div className="p-6">
            <EmptyState
              title="No documents matching search"
              description="Adjust filters or search parameters to view items"
              onAction={handleResetFilters}
              actionLabel="Clear Filters"
            />
          </div>
        ) : (
          <div className="overflow-x-auto custom-scrollbar">
            <table className="w-full text-left border-collapse select-none">
              <thead>
                <tr className="border-b border-slate-800/60 bg-slate-900/30 text-xs text-slate-400 uppercase tracking-wider font-semibold">
                  <th className="py-4 px-6">Filename</th>
                  <th className="py-4 px-6">Type</th>
                  <th className="py-4 px-6">Size</th>
                  <th className="py-4 px-6">Indexing Status</th>
                  <th className="py-4 px-6">Created Date</th>
                  <th className="py-4 px-6 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/30 text-sm text-slate-300">
                <AnimatePresence>
                  {pagedDocs.map((doc, i) => (
                    <motion.tr
                      key={doc.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 0.2, delay: i * 0.05 }}
                      className="hover:bg-slate-900/20 transition-colors"
                    >
                      <td className="py-4 px-6 font-semibold text-slate-200">
                        <div className="flex items-center gap-2.5 truncate max-w-xs">
                          <FileText className="w-4 h-4 text-slate-500 shrink-0" />
                          <span title={doc.filename}>{doc.filename}</span>
                        </div>
                      </td>
                      <td className="py-4 px-6">
                        <span className="font-mono text-xs text-slate-400 uppercase bg-slate-900 border border-slate-800 px-2 py-0.5 rounded">
                          {doc.type}
                        </span>
                      </td>
                      <td className="py-4 px-6 font-mono text-xs text-slate-400">
                        {formatSize(doc.size_bytes)}
                      </td>
                      <td className="py-4 px-6">
                        <div className="flex items-center gap-2">
                          <span className={`w-1.5 h-1.5 rounded-full ${
                            doc.status.toLowerCase() === "indexed"
                              ? "bg-emerald-400"
                              : doc.status.toLowerCase() === "pending"
                              ? "bg-amber-400"
                              : "bg-rose-400"
                          }`} />
                          <span className={`text-xs font-semibold ${
                            doc.status.toLowerCase() === "indexed"
                              ? "text-emerald-400"
                              : doc.status.toLowerCase() === "pending"
                              ? "text-amber-400"
                              : "text-rose-400"
                          }`}>
                            {doc.status}
                          </span>
                        </div>
                      </td>
                      <td className="py-4 px-6 text-xs text-slate-400">
                        {new Date(doc.created).toLocaleDateString(undefined, {
                          year: "numeric",
                          month: "short",
                          day: "numeric",
                        })}
                      </td>
                      <td className="py-4 px-6 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => showToast(`Opening preview for ${doc.filename}`, "info")}
                            className="p-2 hover:bg-slate-800 rounded-xl text-slate-400 hover:text-slate-200 transition-colors cursor-pointer"
                            title="View Info"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => openDeleteDialog(doc)}
                            className="p-2 hover:bg-rose-950/30 rounded-xl text-slate-400 hover:text-rose-400 transition-colors cursor-pointer"
                            title="Delete"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </motion.tr>
                  ))}
                </AnimatePresence>
              </tbody>
            </table>
          </div>
        )}

        {/* Table footer Pagination controls */}
        {!loading && filteredDocs.length > 0 && (
          <div className="flex items-center justify-between p-4 border-t border-slate-800/60 bg-slate-900/10 text-xs select-none">
            <span className="text-slate-400">
              Showing{" "}
              <span className="font-semibold text-slate-200">
                {(currentPage - 1) * itemsPerPage + 1}
              </span>{" "}
              to{" "}
              <span className="font-semibold text-slate-200">
                {Math.min(currentPage * itemsPerPage, filteredDocs.length)}
              </span>{" "}
              of{" "}
              <span className="font-semibold text-slate-200">
                {filteredDocs.length}
              </span>{" "}
              entries
            </span>

            {totalPages > 1 && (
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setCurrentPage(currentPage - 1)}
                  disabled={currentPage === 1}
                  className="px-3 py-1.5 rounded-lg border border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-900 disabled:opacity-50 disabled:pointer-events-none transition-all cursor-pointer"
                >
                  Previous
                </button>
                {Array.from({ length: totalPages }).map((_, i) => (
                  <button
                    key={i}
                    onClick={() => setCurrentPage(i + 1)}
                    className={`w-7 h-7 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                      currentPage === i + 1
                        ? "bg-blue-600 text-white shadow-lg"
                        : "border border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-900"
                    }`}
                  >
                    {i + 1}
                  </button>
                ))}
                <button
                  onClick={() => setCurrentPage(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  className="px-3 py-1.5 rounded-lg border border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-900 disabled:opacity-50 disabled:pointer-events-none transition-all cursor-pointer"
                >
                  Next
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Confirmation Dialog component */}
      <ConfirmationDialog
        isOpen={deleteDialogOpen}
        title="Remove Document"
        message={`Are you sure you want to delete "${docToDelete?.filename}"? This action will drop its indexed text chunks from the vector database.`}
        confirmLabel="Remove File"
        onConfirm={confirmDeleteDoc}
        onCancel={() => setDeleteDialogOpen(false)}
      />
    </div>
  );
};
