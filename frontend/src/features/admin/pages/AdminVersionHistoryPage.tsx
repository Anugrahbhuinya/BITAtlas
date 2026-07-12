import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import adminApi from "../services/api";
import { useAdminStore } from "../hooks/adminStore";
import { DashboardCard } from "../components/DashboardCard";
import { CardSkeleton, TableSkeleton } from "../components/LoadingSkeleton";
import { 
  History, 
  ChevronLeft, 
  RotateCcw, 
  Eye, 
  User, 
  Calendar,
  Layers,
  Clock
} from "lucide-react";

export const AdminVersionHistoryPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { showToast } = useAdminStore();
  
  const [loading, setLoading] = useState(true);
  const [versions, setVersions] = useState<any[]>([]);
  const [activeVersion, setActiveVersion] = useState<any | null>(null);
  const [restoring, setRestoring] = useState(false);

  const fetchVersions = async () => {
    setLoading(true);
    try {
      const response = await adminApi.get(`/api/admin/knowledge/${id}/versions`);
      setVersions(response.data);
      if (response.data.length > 0) {
        setActiveVersion(response.data[0]); // Select latest by default
      }
    } catch (e: any) {
      showToast(e.response?.data?.detail || "Failed to load version snapshots", "error");
      navigate(`/admin/knowledge/editor/${id}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (id) {
      fetchVersions();
    }
  }, [id]);

  const handleRestore = async (versionNum: number) => {
    if (window.confirm(`Are you sure you want to restore Version ${versionNum}? This will create a new version snapshot of the current state and restore this historical text content.`)) {
      setRestoring(true);
      try {
        await adminApi.post(`/api/admin/knowledge/${id}/versions/${versionNum}/restore`);
        showToast(`Successfully restored Version ${versionNum}.`, "success");
        navigate(`/admin/knowledge/editor/${id}`);
      } catch (e: any) {
        showToast(e.response?.data?.detail || "Failed to restore version", "error");
      } finally {
        setRestoring(false);
      }
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate(-1)} className="p-2 hover:bg-slate-900 border border-slate-800 text-slate-400 rounded-xl"><ChevronLeft className="w-4 h-4" /></button>
          <h2 className="text-xl font-bold text-slate-100">Version History</h2>
        </div>
        <TableSkeleton />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button 
          onClick={() => navigate(`/admin/knowledge/editor/${id}`)}
          className="p-2 hover:bg-surface-container rounded-xl border border-outline-variant text-slate-400 hover:text-slate-200 transition-colors"
        >
          <ChevronLeft className="w-4 h-4" />
        </button>
        <div>
          <h2 className="text-xl font-bold text-slate-100 tracking-tight">KMS Version Ledger</h2>
          <p className="text-xs text-slate-400 mt-1">
            Compare and restore historical snapshots of the document text.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left side: Version list */}
        <div className="lg:col-span-1">
          <DashboardCard title="Snapshot Ledger" subtitle={`${versions.length} versions stored`}>
            <div className="space-y-2 pt-2 max-h-[500px] overflow-y-auto pr-1 custom-scrollbar select-none text-xs">
              {versions.map((ver) => (
                <div 
                  key={ver._id}
                  onClick={() => setActiveVersion(ver)}
                  className={`p-3 border rounded-xl flex items-center justify-between cursor-pointer transition-colors ${
                    activeVersion?._id === ver._id 
                      ? "bg-primary/10 border-primary text-primary" 
                      : "bg-slate-900/60 border-slate-900 hover:border-slate-800 text-slate-300"
                  }`}
                >
                  <div className="space-y-1">
                    <span className="font-bold block">Version {ver.version}</span>
                    <span className="text-[10px] text-slate-500 block">
                      {new Date(ver.created_at).toLocaleString()}
                    </span>
                  </div>
                  <div className="flex items-center gap-1.5 text-slate-500">
                    <User className="w-3.5 h-3.5" />
                    <span className="text-[10px] font-medium">{ver.author}</span>
                  </div>
                </div>
              ))}
            </div>
          </DashboardCard>
        </div>

        {/* Right side: Version preview */}
        <div className="lg:col-span-2">
          {activeVersion ? (
            <DashboardCard 
              title={`Version ${activeVersion.version} Preview`} 
              subtitle={`Created by ${activeVersion.author} on ${new Date(activeVersion.created_at).toLocaleString()}`}
            >
              <div className="space-y-4 pt-2 select-none">
                {/* Meta tags */}
                <div className="flex flex-wrap gap-2 text-[10px]">
                  <span className="font-bold px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-300">
                    Category: {activeVersion.category}
                  </span>
                  {activeVersion.department && (
                    <span className="font-bold px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-300">
                      Dept: {activeVersion.department}
                    </span>
                  )}
                  {activeVersion.tags?.map((t: string) => (
                    <span key={t} className="font-bold px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-400">
                      #{t}
                    </span>
                  ))}
                </div>

                {/* Restoring action bar */}
                <div className="flex justify-between items-center bg-slate-950 p-4 border border-slate-900 rounded-xl">
                  <div className="text-xs text-slate-400">
                    Restoring this snapshot will increment the active document version ledger.
                  </div>
                  <button
                    onClick={() => handleRestore(activeVersion.version)}
                    disabled={restoring}
                    className="px-4 py-1.5 bg-primary text-background font-bold text-xs rounded-xl flex items-center gap-1.5 shadow transition-colors cursor-pointer disabled:opacity-50"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                    <span>Restore Version {activeVersion.version}</span>
                  </button>
                </div>

                {/* Rendered content */}
                <div className="bg-slate-950/60 p-5 border border-slate-900/60 rounded-2xl max-h-[350px] overflow-y-auto font-mono text-xs text-slate-300 leading-relaxed whitespace-pre-wrap">
                  {activeVersion.content}
                </div>
              </div>
            </DashboardCard>
          ) : (
            <div className="glass-panel p-6 rounded-2xl text-center text-xs text-slate-500 italic">
              Select a version snapshot to view preview.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
