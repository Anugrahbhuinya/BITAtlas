import { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import adminApi from "../services/api";
import { useAdminStore } from "../hooks/adminStore";
import { DashboardCard } from "../components/DashboardCard";
import { TableSkeleton } from "../components/LoadingSkeleton";
import { 
  Search, 
  Filter, 
  Edit2, 
  Trash2, 
  Layers, 
  Eye, 
  RefreshCw, 
  Plus, 
  Check, 
  Archive, 
  CheckCircle,
  AlertTriangle,
  FolderOpen
} from "lucide-react";

export const AdminKnowledgeSearchPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { showToast } = useAdminStore();
  
  const [loading, setLoading] = useState(false);
  const [items, setItems] = useState<any[]>([]);
  
  // Search query & filters
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("");
  const [category, setCategory] = useState("");
  const [sourceType, setSourceType] = useState("");
  const [priority, setPriority] = useState("");
  const [department, setDepartment] = useState("");
  const [tag, setTag] = useState("");
  
  // Bulk selection
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [bulkActionLoading, setBulkActionLoading] = useState(false);
  
  // Preview modal
  const [previewItem, setPreviewItem] = useState<any | null>(null);

  const categories = [
    "Academic", "Notice", "Event", "Department", "Hostel", "Placement", 
    "Club", "Faculty", "Library", "Transport", "Policy", "Admission", 
    "Scholarship", "FAQ", "Research", "Other"
  ];

  const sourceTypes = ["manual", "txt", "markdown", "docx", "pdf", "website"];

  // Read URL query params if any
  useEffect(() => {
    const catParam = searchParams.get("category");
    const tagParam = searchParams.get("tag");
    const statusParam = searchParams.get("status");
    if (catParam) setCategory(catParam);
    if (tagParam) setTag(tagParam);
    if (statusParam) setStatus(statusParam);
  }, [searchParams]);

  const fetchItems = async () => {
    setLoading(true);
    try {
      const response = await adminApi.get("/api/admin/knowledge/search", {
        params: {
          q: query || undefined,
          status: status || undefined,
          category: category || undefined,
          source_type: sourceType || undefined,
          priority: priority || undefined,
          department: department || undefined,
          tag: tag || undefined
        }
      });
      setItems(response.data);
      setSelectedIds([]);
    } catch (e: any) {
      showToast(e.response?.data?.detail || "Failed to load KMS search results", "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItems();
  }, [status, category, sourceType, priority, department, tag]);

  const handleSearchSubmit = (e: any) => {
    e.preventDefault();
    fetchItems();
  };

  const handleSelectAll = (e: any) => {
    if (e.target.checked) {
      setSelectedIds(items.map(i => i._id));
    } else {
      setSelectedIds([]);
    }
  };

  const handleSelectOne = (id: string, checked: boolean) => {
    if (checked) {
      setSelectedIds([...selectedIds, id]);
    } else {
      setSelectedIds(selectedIds.filter(x => x !== id));
    }
  };

  const handleBulkAction = async (action: "publish" | "archive" | "delete" | "reindex") => {
    if (selectedIds.length === 0) return;
    if (action === "delete" && !window.confirm(`Are you sure you want to delete ${selectedIds.length} selected items?`)) {
      return;
    }
    
    setBulkActionLoading(true);
    try {
      await adminApi.post(`/api/admin/knowledge/bulk/${action}`, { ids: selectedIds });
      showToast(`Bulk ${action} operation completed successfully.`, "success");
      fetchItems();
    } catch (e: any) {
      showToast(e.response?.data?.detail || "Bulk action failed", "error");
    } finally {
      setBulkActionLoading(false);
    }
  };

  const handleSingleDelete = async (id: string) => {
    if (window.confirm("Are you sure you want to delete this item?")) {
      try {
        await adminApi.delete(`/api/admin/knowledge/${id}`);
        showToast("Item deleted successfully", "success");
        fetchItems();
      } catch (e: any) {
        showToast(e.response?.data?.detail || "Failed to delete item", "error");
      }
    }
  };

  const handleSingleReindex = async (id: string) => {
    try {
      await adminApi.post(`/api/admin/knowledge/bulk/reindex`, { ids: [id] });
      showToast("Item reindexed successfully", "success");
      fetchItems();
    } catch (e: any) {
      showToast(e.response?.data?.detail || "Failed to reindex item", "error");
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-slate-100 tracking-tight">KMS Search & Directory</h2>
          <p className="text-xs text-slate-400 mt-1">
            Search, filter, and execute bulk actions on manual articles, TXT, MD, and DOCX records.
          </p>
        </div>
        <button
          onClick={() => navigate("/admin/knowledge/editor")}
          className="px-4 py-2 bg-primary text-background font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg hover:opacity-95 transition-opacity cursor-pointer animate-fade-in"
        >
          <Plus className="w-4 h-4" />
          <span>New Article</span>
        </button>
      </div>

      {/* Search & filters panel */}
      <form onSubmit={handleSearchSubmit} className="grid grid-cols-1 md:grid-cols-4 lg:grid-cols-6 gap-4">
        {/* Text query input */}
        <div className="md:col-span-2 lg:col-span-3 relative">
          <Search className="absolute left-3 top-3 w-4 h-4 text-slate-500" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search keywords in title or content..."
            className="w-full bg-slate-900/60 border border-slate-900 rounded-xl pl-10 pr-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-primary"
          />
        </div>

        {/* Category filter */}
        <div>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="w-full bg-slate-900/60 border border-slate-900 rounded-xl px-3 py-2.5 text-xs text-slate-400 focus:outline-none focus:border-primary"
          >
            <option value="">All Categories</option>
            {categories.map(c => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>

        {/* Source Type filter */}
        <div>
          <select
            value={sourceType}
            onChange={(e) => setSourceType(e.target.value)}
            className="w-full bg-slate-900/60 border border-slate-900 rounded-xl px-3 py-2.5 text-xs text-slate-400 focus:outline-none focus:border-primary"
          >
            <option value="">All Sources</option>
            {sourceTypes.map(s => (
              <option key={s} value={s}>{s.toUpperCase()}</option>
            ))}
          </select>
        </div>

        {/* Status filter */}
        <div>
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="w-full bg-slate-900/60 border border-slate-900 rounded-xl px-3 py-2.5 text-xs text-slate-400 focus:outline-none focus:border-primary"
          >
            <option value="">All Statuses</option>
            <option value="published">Published</option>
            <option value="draft">Draft</option>
            <option value="archived">Archived</option>
            <option value="expired">Expired</option>
          </select>
        </div>
      </form>

      {/* Bulk action actionbar (shown when items selected) */}
      {selectedIds.length > 0 && (
        <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl flex items-center justify-between animate-slide-up">
          <div className="text-xs text-slate-300">
            <strong>{selectedIds.length}</strong> items selected
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => handleBulkAction("publish")}
              disabled={bulkActionLoading}
              className="px-3 py-1 bg-primary/20 text-primary border border-primary/20 text-[10px] font-bold rounded-lg flex items-center gap-1.5 hover:bg-primary/30 transition-all cursor-pointer"
            >
              <CheckCircle className="w-3 h-3" />
              <span>Publish</span>
            </button>
            <button
              onClick={() => handleBulkAction("archive")}
              disabled={bulkActionLoading}
              className="px-3 py-1 bg-amber-500/10 text-amber-300 border border-amber-500/20 text-[10px] font-bold rounded-lg flex items-center gap-1.5 hover:bg-amber-500/20 transition-all cursor-pointer"
            >
              <Archive className="w-3 h-3" />
              <span>Archive</span>
            </button>
            <button
              onClick={() => handleBulkAction("reindex")}
              disabled={bulkActionLoading}
              className="px-3 py-1 bg-blue-500/10 text-blue-300 border border-blue-500/20 text-[10px] font-bold rounded-lg flex items-center gap-1.5 hover:bg-blue-500/20 transition-all cursor-pointer"
            >
              <RefreshCw className="w-3 h-3" />
              <span>Reindex</span>
            </button>
            <button
              onClick={() => handleBulkAction("delete")}
              disabled={bulkActionLoading}
              className="px-3 py-1 bg-red-500/10 text-red-300 border border-red-500/20 text-[10px] font-bold rounded-lg flex items-center gap-1.5 hover:bg-red-500/20 transition-all cursor-pointer"
            >
              <Trash2 className="w-3 h-3" />
              <span>Delete</span>
            </button>
          </div>
        </div>
      )}

      {/* Main Results table */}
      <DashboardCard title="Search Results" subtitle={`${items.length} records found`}>
        {loading ? (
          <TableSkeleton />
        ) : items.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 gap-3 text-slate-500">
            <FolderOpen className="w-10 h-10 text-slate-700 animate-pulse" />
            <span className="text-xs">No records matching search query.</span>
          </div>
        ) : (
          <div className="overflow-x-auto select-none pt-2">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-900 text-[10px] text-slate-500 uppercase font-mono tracking-wider">
                  <th className="py-3 px-4 w-10">
                    <input
                      type="checkbox"
                      onChange={handleSelectAll}
                      checked={selectedIds.length === items.length && items.length > 0}
                      className="rounded border-slate-800 cursor-pointer"
                    />
                  </th>
                  <th className="py-3 px-4">Title</th>
                  <th className="py-3 px-4">Category</th>
                  <th className="py-3 px-4">Source</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Priority</th>
                  <th className="py-3 px-4">Author</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-900/60">
                {items.map((item) => (
                  <tr key={item._id} className="hover:bg-slate-950/20 text-xs text-slate-300 transition-colors">
                    <td className="py-3 px-4">
                      <input
                        type="checkbox"
                        checked={selectedIds.includes(item._id)}
                        onChange={(e) => handleSelectOne(item._id, e.target.checked)}
                        className="rounded border-slate-800 cursor-pointer"
                      />
                    </td>
                    <td className="py-3 px-4 font-semibold text-slate-200 max-w-xs truncate">{item.title}</td>
                    <td className="py-3 px-4">
                      <span className="text-[10px] font-bold bg-slate-900 px-2 py-0.5 rounded border border-slate-800/80">
                        {item.category}
                      </span>
                    </td>
                    <td className="py-3 px-4 uppercase font-mono text-[10px] text-slate-400">{item.source_type}</td>
                    <td className="py-3 px-4">
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                        item.status === "published" ? "bg-emerald-950/20 border-emerald-500/20 text-emerald-400" :
                        item.status === "draft" ? "bg-slate-900 border-slate-800 text-slate-400" :
                        item.status === "archived" ? "bg-amber-950/20 border-amber-500/20 text-amber-400" :
                        "bg-red-950/20 border-red-500/20 text-red-400"
                      }`}>
                        {item.status.toUpperCase()}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-center font-mono">{item.priority}</td>
                    <td className="py-3 px-4 text-slate-400">{item.author}</td>
                    <td className="py-3 px-4 text-right space-x-1">
                      <button
                        onClick={() => setPreviewItem(item)}
                        className="p-1.5 hover:bg-slate-900 text-slate-500 hover:text-slate-300 rounded cursor-pointer"
                        title="Preview"
                      >
                        <Eye className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => navigate(`/admin/knowledge/editor/${item._id}`)}
                        className="p-1.5 hover:bg-slate-900 text-slate-500 hover:text-slate-300 rounded cursor-pointer"
                        title="Edit"
                      >
                        <Edit2 className="w-3.5 h-3.5" />
                      </button>
                      {item.status === "published" && (
                        <button
                          onClick={() => handleSingleReindex(item._id)}
                          className="p-1.5 hover:bg-slate-900 text-slate-500 hover:text-slate-300 rounded cursor-pointer"
                          title="Reindex vectors"
                        >
                          <RefreshCw className="w-3.5 h-3.5" />
                        </button>
                      )}
                      <button
                        onClick={() => handleSingleDelete(item._id)}
                        className="p-1.5 hover:bg-slate-900 text-slate-500 hover:text-red-400 rounded cursor-pointer"
                        title="Delete"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </DashboardCard>

      {/* Preview Modal */}
      {previewItem && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-950 border border-slate-800 rounded-2xl w-full max-w-2xl overflow-hidden shadow-2xl flex flex-col max-h-[85vh]">
            <div className="p-5 border-b border-slate-900 flex justify-between items-center">
              <div>
                <h3 className="font-bold text-slate-100 text-base">{previewItem.title}</h3>
                <span className="text-[10px] text-slate-500 block uppercase font-mono mt-1">
                  ID: {previewItem._id} | Version: v{previewItem.version}
                </span>
              </div>
              <button
                onClick={() => setPreviewItem(null)}
                className="text-slate-400 hover:text-slate-200 text-sm font-semibold p-1.5 hover:bg-slate-900 rounded-lg"
              >
                ✕
              </button>
            </div>
            
            {/* Modal Body */}
            <div className="p-6 overflow-y-auto flex-1 space-y-4">
              {/* Badges */}
              <div className="flex gap-2">
                <span className="text-[9px] font-bold px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-300">
                  {previewItem.category}
                </span>
                <span className="text-[9px] font-bold px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-300">
                  {previewItem.source_type.toUpperCase()}
                </span>
                <span className={`text-[9px] font-bold px-2 py-0.5 rounded border ${
                  previewItem.status === "published" ? "bg-emerald-950/20 border-emerald-500/20 text-emerald-400" :
                  previewItem.status === "draft" ? "bg-slate-900 border-slate-800 text-slate-400" :
                  "bg-amber-950/20 border-amber-500/20 text-amber-400"
                }`}>
                  {previewItem.status.toUpperCase()}
                </span>
              </div>
              
              {/* Content text */}
              <div className="bg-slate-950/60 p-4 border border-slate-900/60 rounded-xl max-h-[400px] overflow-y-auto text-xs text-slate-300 font-mono leading-relaxed whitespace-pre-wrap">
                {previewItem.content}
              </div>
            </div>
            
            {/* Modal Footer */}
            <div className="p-4 border-t border-slate-900 bg-slate-950/60 flex justify-end gap-2">
              <button
                onClick={() => { navigate(`/admin/knowledge/editor/${previewItem._id}`); setPreviewItem(null); }}
                className="px-4 py-1.5 bg-primary text-background font-bold text-xs rounded-xl flex items-center gap-1.5 shadow"
              >
                <Edit2 className="w-3.5 h-3.5" />
                <span>Edit Document</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
