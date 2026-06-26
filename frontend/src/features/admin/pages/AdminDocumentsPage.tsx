import { useState, useEffect, useRef } from "react";
import adminApi from "../services/api";
import { TableToolbar } from "../components/TableToolbar";
import { TableSkeleton } from "../components/LoadingSkeleton";
import { EmptyState } from "../components/EmptyState";
import { ConfirmationDialog } from "../components/ConfirmationDialog";
import { useAdminStore } from "../hooks/adminStore";
import { FileText, Trash2, Eye, Upload, RefreshCw } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const STEPS = [
  { name: "Uploading", pct: 10, label: "Uploading file..." },
  { name: "Extracting", pct: 30, label: "Extracting text from PDF..." },
  { name: "Chunking", pct: 50, label: "Splitting text into chunks..." },
  { name: "Embedding", pct: 70, label: "Generating text embeddings..." },
  { name: "Updating Chroma", pct: 85, label: "Inserting chunks into ChromaDB..." },
  { name: "Saving Metadata", pct: 95, label: "Saving document metadata..." },
  { name: "Completed", pct: 100, label: "Document indexed successfully!" },
];

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

  // Upload/Reindexing state
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [uploadingFile, setUploadingFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState("");
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [duplicateFound, setDuplicateFound] = useState(false);
  const [duplicateDocId, setDuplicateDocId] = useState<string | null>(null);

  // File input ref
  const fileInputRef = useRef<HTMLInputElement>(null);

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
      showToast("Failed to load documents list", "error");
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
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.type !== "application/pdf" && !file.name.endsWith(".pdf")) {
        showToast("Only PDF files are supported.", "error");
        return;
      }
      startUpload(file);
    }
    // Reset file input value so same file can be uploaded again
    if (e.target) {
      e.target.value = "";
    }
  };

  const startUpload = async (fileToUpload: File, isOverwrite: boolean = false) => {
    setUploadModalOpen(true);
    setUploadingFile(fileToUpload);
    setUploadProgress(10);
    setUploadStatus("Uploading");
    setUploadError(null);
    setDuplicateFound(false);
    setDuplicateDocId(null);

    const formData = new FormData();
    formData.append("file", fileToUpload);

    try {
      const token = useAdminStore.getState().token;
      const url = `http://localhost:8000/api/admin/documents/upload${isOverwrite ? "?overwrite=true" : ""}`;

      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Server error occurred during upload.");
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      if (!reader) {
        throw new Error("Failed to read progress stream.");
      }

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const data = JSON.parse(line);

            if (data.status === "Failed") {
              throw new Error(data.detail || "Indexing failed.");
            } else if (data.status === "Duplicate") {
              setDuplicateFound(true);
              setDuplicateDocId(data.doc_id);
              setUploadStatus("Duplicate");
              setUploadError(data.detail);
              return;
            } else {
              setUploadStatus(data.status);
              if (data.progress) {
                setUploadProgress(data.progress);
              }
            }
          } catch (e: any) {
            throw new Error(e.message || "Failed to process progress details.");
          }
        }
      }

      // Finished successfully
      showToast(`Successfully indexed "${fileToUpload.name}"`, "success");
      fetchDocs();
    } catch (err: any) {
      console.error("Upload error:", err);
      setUploadError(err.message || "An unexpected error occurred.");
      setUploadStatus("Failed");
      showToast(err.message || "Upload failed", "error");
    }
  };

  const startReindex = async (docId: string, filename: string) => {
    setUploadModalOpen(true);
    setUploadingFile({ name: filename } as any);
    setUploadProgress(20);
    setUploadStatus("Extracting");
    setUploadError(null);
    setDuplicateFound(false);

    try {
      const token = useAdminStore.getState().token;
      const url = `http://localhost:8000/api/admin/documents/${docId}/reindex`;

      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Server error occurred during reindexing.");
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      if (!reader) {
        throw new Error("Failed to read progress stream.");
      }

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const data = JSON.parse(line);

            if (data.status === "Failed") {
              throw new Error(data.detail || "Reindexing failed.");
            } else {
              setUploadStatus(data.status);
              if (data.progress) {
                setUploadProgress(data.progress);
              }
            }
          } catch (e: any) {
            throw new Error(e.message || "Failed to process progress details.");
          }
        }
      }

      // Finished successfully
      showToast(`Successfully reindexed "${filename}"`, "success");
      fetchDocs();
    } catch (err: any) {
      console.error("Reindex error:", err);
      setUploadError(err.message || "An unexpected error occurred during reindexing.");
      setUploadStatus("Failed");
      showToast(err.message || "Reindexing failed", "error");
    }
  };

  const openDeleteDialog = (doc: any) => {
    setDocToDelete(doc);
    setDeleteDialogOpen(true);
  };

  const confirmDeleteDoc = async () => {
    if (docToDelete) {
      try {
        await adminApi.delete(`/api/admin/documents/${docToDelete.id}`);
        setDocuments(documents.filter((d) => d.id !== docToDelete.id));
        showToast(`Document "${docToDelete.filename}" removed from knowledge base`, "success");
      } catch (err: any) {
        console.error("Failed to delete document:", err);
        showToast(err.response?.data?.detail || "Failed to delete document", "error");
      } finally {
        setDocToDelete(null);
        setDeleteDialogOpen(false);
      }
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
      {/* Hidden input for PDF uploads */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept=".pdf"
        className="hidden"
      />

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
                  {pagedDocs.map((doc, i) => {
                    const isDynamic = doc.id.startsWith("doc_") && doc.id.length > 10;
                    return (
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
                              onClick={() => showToast(`Opening details for ${doc.filename}`, "info")}
                              className="p-2 hover:bg-slate-800 rounded-xl text-slate-400 hover:text-slate-200 transition-colors cursor-pointer"
                              title="View Info"
                            >
                              <Eye className="w-4 h-4" />
                            </button>
                            {isDynamic && (
                              <button
                                onClick={() => startReindex(doc.id, doc.filename)}
                                className="p-2 hover:bg-slate-800 rounded-xl text-slate-400 hover:text-blue-400 transition-colors cursor-pointer"
                                title="Reindex Document"
                              >
                                <RefreshCw className="w-4 h-4" />
                              </button>
                            )}
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
                    );
                  })}
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

      {/* Upload/Reindex Progress Modal */}
      {uploadModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="glass-panel w-full max-w-md p-6 rounded-2xl border border-slate-800/80 shadow-2xl space-y-6">
            <div className="space-y-1">
              <h3 className="text-lg font-bold text-slate-100">
                {uploadStatus === "Failed" 
                  ? "Indexing Failed" 
                  : uploadStatus === "Completed"
                  ? "Indexing Completed"
                  : uploadStatus === "Duplicate"
                  ? "Duplicate Detected"
                  : "Indexing Knowledge..."}
              </h3>
              <p className="text-xs text-slate-400 truncate">
                File: {uploadingFile?.name}
              </p>
            </div>

            {/* Progress Bar & Percentage */}
            {uploadStatus !== "Duplicate" && (
              <div className="space-y-2">
                <div className="flex justify-between items-center text-xs font-mono">
                  <span className="text-slate-400">
                    {STEPS.find(s => s.name === uploadStatus)?.label || "Processing..."}
                  </span>
                  <span className={uploadStatus === "Failed" ? "text-rose-400" : "text-blue-400"}>
                    {uploadStatus === "Failed" ? "ERROR" : `${uploadProgress}%`}
                  </span>
                </div>
                <div className="w-full h-2 bg-slate-950 rounded-full overflow-hidden border border-slate-800/60">
                  <motion.div 
                    className={`h-full rounded-full ${
                      uploadStatus === "Failed" ? "bg-rose-500" : "bg-gradient-to-r from-blue-500 to-indigo-500"
                    }`}
                    initial={{ width: 0 }}
                    animate={{ width: `${uploadProgress}%` }}
                    transition={{ duration: 0.3 }}
                  />
                </div>
              </div>
            )}

            {/* Duplicate File Option */}
            {uploadStatus === "Duplicate" && (
              <div className="space-y-4">
                <p className="text-sm text-slate-300 bg-amber-950/20 border border-amber-900/40 p-3.5 rounded-xl text-left">
                  {uploadError || "A document with identical content already exists in the knowledge base."}
                </p>
                <div className="flex gap-3 justify-end">
                  <button
                    onClick={() => setUploadModalOpen(false)}
                    className="px-4 py-2 rounded-xl text-xs font-semibold border border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-900 transition-all cursor-pointer"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => uploadingFile && startUpload(uploadingFile, true)}
                    className="px-4 py-2 rounded-xl text-xs font-semibold bg-amber-600 hover:bg-amber-500 text-white transition-all cursor-pointer shadow-lg hover:shadow-amber-500/20"
                  >
                    Overwrite Existing
                  </button>
                </div>
              </div>
            )}

            {/* Error Message */}
            {uploadStatus === "Failed" && uploadError && (
              <div className="space-y-4">
                <p className="text-sm text-rose-400 bg-rose-950/20 border border-rose-900/40 p-3.5 rounded-xl text-left">
                  {uploadError}
                </p>
                <div className="flex justify-end">
                  <button
                    onClick={() => setUploadModalOpen(false)}
                    className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 transition-all cursor-pointer"
                  >
                    Close
                  </button>
                </div>
              </div>
            )}

            {/* Steps Checklist (Visual Progress) */}
            {uploadStatus !== "Duplicate" && uploadStatus !== "Failed" && (
              <div className="border-t border-slate-800/60 pt-4 space-y-2">
                {STEPS.map((step, index) => {
                  const stepIndex = STEPS.findIndex(s => s.name === step.name);
                  const currentIndex = STEPS.findIndex(s => s.name === uploadStatus);
                  const isDone = currentIndex > stepIndex || uploadStatus === "Completed";
                  const isActive = uploadStatus === step.name;
                  
                  return (
                    <div 
                      key={step.name} 
                      className={`flex items-center gap-3 text-xs transition-colors duration-200 ${
                        isDone ? "text-emerald-400 font-medium" : isActive ? "text-blue-400 font-bold" : "text-slate-500"
                      }`}
                    >
                      <div className={`w-4 h-4 rounded-full flex items-center justify-center border text-[9px] ${
                        isDone 
                          ? "bg-emerald-950/40 border-emerald-500 text-emerald-400" 
                          : isActive 
                          ? "bg-blue-950/40 border-blue-500 text-blue-400 animate-pulse" 
                          : "border-slate-800 text-slate-500"
                      }`}>
                        {isDone ? "✓" : index + 1}
                      </div>
                      <span>{step.name}</span>
                    </div>
                  );
                })}
              </div>
            )}

            {/* Success Close Button */}
            {uploadStatus === "Completed" && (
              <div className="flex justify-end pt-2">
                <button
                  onClick={() => setUploadModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white transition-all cursor-pointer shadow-lg hover:shadow-emerald-500/20"
                >
                  Done
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
