import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import adminApi from "../services/api";
import { useAdminStore } from "../hooks/adminStore";
import { DashboardCard } from "../components/DashboardCard";
import { TableSkeleton } from "../components/LoadingSkeleton";
import { 
  FileText, 
  Edit2, 
  Trash2, 
  CheckCircle, 
  FolderOpen,
  Loader2,
  Layers
} from "lucide-react";

export const AdminDraftsPage = () => {
  const navigate = useNavigate();
  const { showToast } = useAdminStore();
  const [loading, setLoading] = useState(false);
  const [items, setItems] = useState<any[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [actionLoading, setActionLoading] = useState(false);

  const fetchDrafts = async () => {
    setLoading(true);
    try {
      const response = await adminApi.get("/api/admin/knowledge", {
        params: { status: "draft" }
      });
      setItems(response.data.items || []);
      setSelectedIds([]);
    } catch (e: any) {
      showToast(e.response?.data?.detail || "Failed to load drafts", "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDrafts();
  }, []);

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

  const handleBulkPublish = async () => {
    if (selectedIds.length === 0) return;
    setActionLoading(true);
    try {
      await adminApi.post("/api/admin/knowledge/bulk/publish", { ids: selectedIds });
      showToast(`Successfully published ${selectedIds.length} draft documents.`, "success");
      fetchDrafts();
    } catch (e: any) {
      showToast(e.response?.data?.detail || "Bulk publish failed", "error");
    } finally {
      setActionLoading(false);
    }
  };

  const handleSingleDelete = async (id: string) => {
    if (window.confirm("Are you sure you want to delete this draft?")) {
      try {
        await adminApi.delete(`/api/admin/knowledge/${id}`);
        showToast("Draft deleted successfully", "success");
        fetchDrafts();
      } catch (e: any) {
        showToast(e.response?.data?.detail || "Failed to delete draft", "error");
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-slate-100 tracking-tight">KMS Offline Drafts</h2>
          <p className="text-xs text-slate-400 mt-1">
            Review and publish offline draft articles before they are indexed for student chat retrieval.
          </p>
        </div>
      </div>

      {/* Actionbar */}
      {selectedIds.length > 0 && (
        <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl flex items-center justify-between animate-slide-up">
          <div className="text-xs text-slate-300">
            <strong>{selectedIds.length}</strong> drafts selected
          </div>
          <button
            onClick={handleBulkPublish}
            disabled={actionLoading}
            className="px-4 py-1.5 bg-primary text-background font-bold text-xs rounded-xl flex items-center gap-1.5 hover:opacity-90 shadow transition-colors cursor-pointer"
          >
            {actionLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <CheckCircle className="w-3.5 h-3.5" />}
            <span>Bulk Publish Chunks</span>
          </button>
        </div>
      )}

      {/* Results table */}
      <DashboardCard title="Draft Items" subtitle={`${items.length} drafts pending review`}>
        {loading ? (
          <TableSkeleton />
        ) : items.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 gap-3 text-slate-500">
            <FolderOpen className="w-10 h-10 text-slate-700 animate-pulse" />
            <span className="text-xs">No pending drafts found.</span>
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
                  <th className="py-3 px-4">Format</th>
                  <th className="py-3 px-4">Last Updated</th>
                  <th className="py-3 px-4">Author</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-900/60 text-xs">
                {items.map((item) => (
                  <tr key={item._id} className="hover:bg-slate-950/20 text-slate-300">
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
                      <span className="text-[10px] font-bold bg-slate-900 px-2 py-0.5 rounded border border-slate-800/80 text-slate-300">
                        {item.category}
                      </span>
                    </td>
                    <td className="py-3 px-4 uppercase font-mono text-[10px] text-slate-400">{item.source_type}</td>
                    <td className="py-3 px-4 text-slate-500 font-mono text-[10px]">
                      {new Date(item.updated_at).toLocaleString()}
                    </td>
                    <td className="py-3 px-4 text-slate-400">{item.author}</td>
                    <td className="py-3 px-4 text-right space-x-1">
                      <button
                        onClick={() => navigate(`/admin/knowledge/editor/${item._id}`)}
                        className="p-1.5 hover:bg-slate-900 text-slate-500 hover:text-slate-300 rounded cursor-pointer"
                        title="Edit Draft"
                      >
                        <Edit2 className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => handleSingleDelete(item._id)}
                        className="p-1.5 hover:bg-slate-900 text-slate-500 hover:text-red-400 rounded cursor-pointer"
                        title="Delete Draft"
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
    </div>
  );
};
