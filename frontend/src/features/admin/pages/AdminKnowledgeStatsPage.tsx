import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import adminApi from "../services/api";
import { useAdminStore } from "../hooks/adminStore";
import { DashboardCard } from "../components/DashboardCard";
import { CardSkeleton, TableSkeleton } from "../components/LoadingSkeleton";
import { 
  Database, 
  FileText, 
  Globe, 
  Layers, 
  Activity, 
  Server, 
  Clock, 
  AlertTriangle,
  FolderOpen,
  PieChart
} from "lucide-react";

export const AdminKnowledgeStatsPage = () => {
  const navigate = useNavigate();
  const { showToast } = useAdminStore();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<any>(null);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const response = await adminApi.get("/api/admin/knowledge/stats");
      setStats(response.data);
    } catch (e: any) {
      showToast(e.response?.data?.detail || "Failed to load KMS stats", "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  // Format bytes helper
  const formatBytes = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-xl font-bold text-slate-100">KMS Analytics</h2>
          <p className="text-xs text-slate-400 mt-1">Aggregating statistics...</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <CardSkeleton />
          <CardSkeleton />
          <CardSkeleton />
          <CardSkeleton />
        </div>
        <TableSkeleton />
      </div>
    );
  }

  const statCards = [
    { title: "Total KMS Items", value: stats?.total_items, subtitle: "All formats & drafts", icon: Database, color: "text-blue-400" },
    { title: "Published Chunks", value: stats?.published, subtitle: "Offline vs Indexed: Published", icon: Layers, color: "text-emerald-400" },
    { title: "Draft Documents", value: stats?.drafts, subtitle: "Offline drafts in progress", icon: FileText, color: "text-slate-400" },
    { title: "Archived/Expired", value: (stats?.archived || 0) + (stats?.expired || 0), subtitle: "Remnants of historical circulars", icon: Clock, color: "text-amber-400" }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-slate-100 tracking-tight">KMS Analytics & Telemetry</h2>
        <p className="text-xs text-slate-400 mt-1">
          Detailed metrics showing document format distribution, category density, and ChromaDB vector usage.
        </p>
      </div>

      {/* Grid of stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((card, i) => {
          const Icon = card.icon;
          return (
            <div key={i} className="glass-panel p-5 rounded-2xl border border-slate-800/40 space-y-4 hover:border-slate-800 transition-all select-none">
              <div className="flex items-center justify-between">
                <span className="text-[10px] uppercase font-bold text-slate-400 font-mono tracking-wider">{card.title}</span>
                <div className={`p-2 bg-slate-900 border border-slate-800 rounded-xl ${card.color}`}>
                  <Icon className="w-4 h-4" />
                </div>
              </div>
              <div className="space-y-1">
                <span className="text-2xl font-black text-slate-100 font-mono tracking-tight block">{card.value}</span>
                <span className="text-[10px] text-slate-500 block">{card.subtitle}</span>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Source types breakdown */}
        <div className="lg:col-span-1">
          <DashboardCard title="Format Distribution" subtitle="Distribution across files & manual note inputs">
            <div className="space-y-3 pt-2 select-none">
              {[
                { label: "PDF Documents", count: stats?.pdfs_count, color: "bg-red-500" },
                { label: "Website Links", count: stats?.websites_count, color: "bg-blue-500" },
                { label: "DOCX Files", count: stats?.docx_count, color: "bg-indigo-500" },
                { label: "Markdown (.md) files", count: stats?.markdown_count, color: "bg-teal-500" },
                { label: "Plain Text (.txt) files", count: stats?.txt_count, color: "bg-yellow-500" },
                { label: "Manual Editor Notes", count: stats?.manual_count, color: "bg-emerald-500" }
              ].map((src, i) => (
                <div key={i} className="flex items-center justify-between p-2.5 bg-slate-900/60 border border-slate-900 rounded-xl">
                  <div className="flex items-center gap-2.5">
                    <div className={`w-2 h-2 rounded-full ${src.color}`} />
                    <span className="text-xs text-slate-300 font-medium">{src.label}</span>
                  </div>
                  <span className="text-xs font-bold text-slate-200 font-mono">{src.count}</span>
                </div>
              ))}
            </div>
          </DashboardCard>
        </div>

        {/* Vector DB status */}
        <div className="lg:col-span-2">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <DashboardCard title="Vector Databases status" subtitle="ChromaDB physical metrics">
              <div className="space-y-4 pt-2 select-none">
                <div className="p-3 bg-slate-900/60 border border-slate-900 rounded-xl flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Server className="w-4 h-4 text-indigo-400" />
                    <div>
                      <span className="text-[10px] text-slate-500 uppercase block font-mono">Total Vectors</span>
                      <span className="text-xs font-semibold text-slate-300 mt-0.5 block font-mono">{stats?.vector_count}</span>
                    </div>
                  </div>
                </div>

                <div className="p-3 bg-slate-900/60 border border-slate-900 rounded-xl flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <PieChart className="w-4 h-4 text-emerald-400" />
                    <div>
                      <span className="text-[10px] text-slate-500 uppercase block font-mono">Raw size on disk</span>
                      <span className="text-xs font-semibold text-slate-300 mt-0.5 block font-mono">{formatBytes(stats?.storage_used_bytes || 0)}</span>
                    </div>
                  </div>
                </div>
              </div>
            </DashboardCard>

            <DashboardCard title="Category Index Density" subtitle="Document counts per KMS category">
              <div className="max-h-[170px] overflow-y-auto space-y-2 pr-1 custom-scrollbar pt-2 select-none text-xs">
                {Object.entries(stats?.category_counts || {})
                  .sort((a: any, b: any) => b[1] - a[1])
                  .map(([cat, count]: any) => (
                    <div key={cat} className="flex justify-between items-center py-1.5 border-b border-slate-900/60">
                      <span className="text-slate-300">{cat}</span>
                      <span className="font-mono font-bold text-slate-400">{count}</span>
                    </div>
                  ))}
              </div>
            </DashboardCard>
          </div>

          {/* Recent changes list */}
          <div className="mt-6">
            <DashboardCard title="Recent KMS Activity" subtitle="Last 10 updates and drafts">
              {stats?.recent_updates?.length === 0 ? (
                <div className="py-6 text-center text-xs text-slate-500">No recent updates detected.</div>
              ) : (
                <div className="overflow-x-auto pt-2 select-none">
                  <table className="w-full text-left border-collapse">
                    <thead>
                      <tr className="border-b border-slate-900 text-[10px] text-slate-500 uppercase font-mono tracking-wider">
                        <th className="py-2 px-3">Title</th>
                        <th className="py-2 px-3">Status</th>
                        <th className="py-2 px-3">Format</th>
                        <th className="py-2 px-3">Modified</th>
                        <th className="py-2 px-3">Author</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-900/60 text-xs">
                      {stats?.recent_updates?.map((item: any) => (
                        <tr key={item.id} className="hover:bg-slate-950/20 text-slate-300">
                          <td 
                            className="py-2 px-3 font-semibold text-slate-200 truncate max-w-[200px] cursor-pointer hover:underline"
                            onClick={() => navigate(`/admin/knowledge/editor/${item.id}`)}
                          >
                            {item.title}
                          </td>
                          <td className="py-2 px-3">
                            <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded border ${
                              item.status === "published" ? "bg-emerald-950/20 border-emerald-500/20 text-emerald-400" :
                              "bg-slate-900 border-slate-800 text-slate-400"
                            }`}>
                              {item.status.toUpperCase()}
                            </span>
                          </td>
                          <td className="py-2 px-3 uppercase font-mono text-[9px] text-slate-400">{item.source_type}</td>
                          <td className="py-2 px-3 text-slate-500 font-mono text-[10px]">
                            {new Date(item.updated_at).toLocaleString()}
                          </td>
                          <td className="py-2 px-3 text-slate-400">{item.author}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </DashboardCard>
          </div>
        </div>
      </div>
    </div>
  );
};
