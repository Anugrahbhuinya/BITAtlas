import { useState, useEffect } from "react";
import adminApi from "../services/api";
import { DashboardCard } from "../components/DashboardCard";
import { StatsCard } from "../components/StatsCard";
import { CardSkeleton } from "../components/LoadingSkeleton";
import { 
  Database, 
  FileJson, 
  FileText, 
  CheckCircle2, 
  RefreshCw, 
  AlertCircle, 
  HardDrive, 
  Layers, 
  ShieldAlert 
} from "lucide-react";

export const AdminKnowledgePage = () => {
  const [stats, setStats] = useState<any>(null);
  const [health, setHealth] = useState<any>(null);
  const [settings, setSettings] = useState<any>(null);
  const [documents, setDocuments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [statsRes, healthRes, settingsRes, docsRes] = await Promise.all([
        adminApi.get("/api/admin/dashboard"),
        adminApi.get("/api/admin/index-health"),
        adminApi.get("/api/admin/settings"),
        adminApi.get("/api/admin/documents")
      ]);
      setStats(statsRes.data);
      setHealth(healthRes.data);
      setSettings(settingsRes.data);
      setDocuments(docsRes.data.documents || []);
    } catch (e) {
      console.error("Failed to load knowledge base data", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const formatSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-xl font-bold text-slate-100">Knowledge Base</h2>
          <p className="text-xs text-slate-400 mt-1">Measuring vector collections...</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <CardSkeleton />
          <CardSkeleton />
          <CardSkeleton />
        </div>
      </div>
    );
  }

  // Count files by type
  const totalSources = documents.length;
  const jsonSourcesCount = documents.filter(d => d.type === "json").length;
  const pdfSourcesCount = documents.filter(d => d.type === "pdf").length;

  // Determine health style
  const healthState = health?.health_state || "Healthy";
  const healthDetails = health?.details || "Vector storage and metadata are fully synchronized.";
  
  const getHealthUI = () => {
    switch (healthState.toLowerCase()) {
      case "healthy":
        return {
          icon: CheckCircle2,
          color: "text-emerald-400",
          bg: "bg-emerald-500/10 border-emerald-500/20",
          title: "Collection Health: Healthy"
        };
      case "degraded":
        return {
          icon: AlertCircle,
          color: "text-amber-400",
          bg: "bg-amber-500/10 border-amber-500/20",
          title: "Collection Health: Degraded"
        };
      case "critical":
      default:
        return {
          icon: ShieldAlert,
          color: "text-rose-400",
          bg: "bg-rose-500/10 border-rose-500/20",
          title: "Collection Health: Critical"
        };
    }
  };

  const healthUI = getHealthUI();
  const HealthIcon = healthUI.icon;

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-100 tracking-tight flex items-center gap-2">
            <span>Knowledge Base Management</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Overview of static and dynamic document segments compiled into the retrieval engine.
          </p>
        </div>

        <button
          onClick={fetchData}
          className="px-4 py-2 text-xs font-semibold bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300 hover:text-white rounded-xl transition-all cursor-pointer flex items-center gap-2 select-none"
        >
          <RefreshCw className="w-3 h-3" />
          <span>Synchronize Collection</span>
        </button>
      </div>

      {/* Numerical metric cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <StatsCard
          title="Total Knowledge Sources"
          value={totalSources}
          icon={FileText}
          description="Total document datasets indexed"
          colorClass="bg-blue-500/10 border-blue-500/20 text-blue-400"
        />
        <StatsCard
          title="Vector Chunks count"
          value={health?.total_vectors || 0}
          icon={Layers}
          description="Total ChromaDB partitions"
          colorClass="bg-emerald-500/10 border-emerald-500/20 text-emerald-400"
        />
        <StatsCard
          title="Index Size on Disk"
          value={formatSize(health?.chroma_size_bytes || 0)}
          icon={HardDrive}
          description="Chroma SQLite and HNSW size"
          colorClass="bg-amber-500/10 border-amber-500/20 text-amber-400"
        />
      </div>

      {/* Detailed overview layout cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Collection details */}
        <div className="lg:col-span-2 space-y-6">
          <DashboardCard
            title="Index Structuring & Segment Summary"
            subtitle="Details of document types indexed inside vector stores"
          >
            <div className="divide-y divide-slate-800/40 select-none max-h-[450px] overflow-y-auto pr-1 custom-scrollbar">
              {documents.length === 0 ? (
                <div className="py-8 text-center text-xs text-slate-500">
                  No documents currently in knowledge base.
                </div>
              ) : (
                documents.map((doc) => (
                  <div key={doc.id} className="py-3.5 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-xl border ${
                        doc.type === "pdf" 
                          ? "bg-blue-500/10 text-blue-400 border-blue-500/20" 
                          : "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                      }`}>
                        {doc.type === "pdf" ? <FileText className="w-4 h-4" /> : <FileJson className="w-4 h-4" />}
                      </div>
                      <div>
                        <span className="text-xs font-semibold text-slate-200 block truncate max-w-sm" title={doc.filename}>
                          {doc.filename}
                        </span>
                        <span className="text-[10px] text-slate-400">
                          {doc.type.toUpperCase()} &bull; {formatSize(doc.size_bytes)}
                        </span>
                      </div>
                    </div>
                    <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${
                      doc.status.toLowerCase() === "indexed"
                        ? "text-emerald-400 bg-emerald-950/30 border-emerald-500/20"
                        : doc.status.toLowerCase() === "pending"
                        ? "text-amber-400 bg-amber-950/30 border-amber-500/20"
                        : "text-rose-400 bg-rose-950/30 border-rose-500/20"
                    }`}>
                      {doc.status}
                    </span>
                  </div>
                ))
              )}
            </div>
          </DashboardCard>
        </div>

        {/* Database parameters / settings */}
        <div className="space-y-6">
          <DashboardCard
            title="Index Integrity State"
            subtitle="Retrieval collections status verification"
          >
            <div className="space-y-4 pt-2">
              <div className={`p-4 rounded-xl border ${healthUI.bg} flex items-start gap-3`}>
                <HealthIcon className={`w-5 h-5 ${healthUI.color} shrink-0 mt-0.5`} />
                <div>
                  <h4 className="text-xs font-semibold text-slate-200">{healthUI.title}</h4>
                  <p className="text-[10px] text-slate-400 mt-1 leading-relaxed">
                    {healthDetails}
                  </p>
                </div>
              </div>

              {/* Sync diagnostics */}
              {(health?.orphan_vectors_count > 0 || health?.missing_vectors_count > 0) && (
                <div className="p-3 bg-rose-500/5 border border-rose-500/10 rounded-xl space-y-1.5">
                  <span className="text-[10px] font-bold text-rose-400 uppercase tracking-wider block">Index Anomalies</span>
                  {health.orphan_vectors_count > 0 && (
                    <div className="text-[10px] text-slate-300">
                      &bull; {health.orphan_vectors_count} orphan vectors in vector database (no matching document details).
                    </div>
                  )}
                  {health.missing_vectors_count > 0 && (
                    <div className="text-[10px] text-slate-300">
                      &bull; {health.missing_vectors_count} missing vectors in database (defined but missing in index).
                    </div>
                  )}
                </div>
              )}

              <div className="p-4 bg-slate-900/50 rounded-xl border border-slate-900/80 space-y-3">
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-400">Embedding Model</span>
                  <span className="font-semibold text-slate-300 font-mono text-[10px] truncate max-w-[150px]">
                    {settings?.embeddingModel || "BAAI/bge-small-en-v1.5"}
                  </span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-400">Total Chunks</span>
                  <span className="font-semibold text-slate-300 font-mono">
                    {health?.total_vectors || 0} Chunks
                  </span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-400">Collection Name</span>
                  <span className="font-semibold text-slate-300 font-mono">
                    {settings?.chromaCollection || "langchain"}
                  </span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-400">Default Chunk Size</span>
                  <span className="font-semibold text-slate-300 font-mono">
                    {settings?.chunkSize || 500} (overlap {settings?.chunkOverlap || 50})
                  </span>
                </div>
              </div>

              <div className="p-3 bg-blue-500/5 border border-blue-500/10 rounded-xl flex gap-2.5">
                <Database className="w-4 h-4 text-blue-500 mt-0.5 shrink-0" />
                <p className="text-[10px] text-slate-400 leading-relaxed">
                  FastAPI service performs extraction page-by-page using PyPDF, storing the dynamic documents to <code>uploads/pdfs</code> with transactional safety rollbacks.
                </p>
              </div>
            </div>
          </DashboardCard>
        </div>
      </div>
    </div>
  );
};
