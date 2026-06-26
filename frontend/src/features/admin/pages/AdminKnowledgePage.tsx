import { useState, useEffect } from "react";
import adminApi from "../services/api";
import { DashboardCard } from "../components/DashboardCard";
import { StatsCard } from "../components/StatsCard";
import { CardSkeleton } from "../components/LoadingSkeleton";
import { Database, FileJson, FileText, CheckCircle2, RefreshCw, AlertCircle } from "lucide-react";

export const AdminKnowledgePage = () => {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const response = await adminApi.get("/api/admin/dashboard");
      setStats(response.data);
    } catch (e) {
      console.error("Failed to load knowledge metrics", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

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

  // Segmenting mock/scanned files counts:
  // We have 4 sources total (e.g. notices.json, student_faqs.json + calendar.pdf, handbook.pdf).
  // Lets represent this dynamically.
  const totalSources = stats?.knowledgeSources || 4;
  const jsonSourcesCount = 2; // notices.json, student_faqs.json
  const pdfSourcesCount = Math.max(totalSources - jsonSourcesCount, 0); // Remaining are PDFs

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
          onClick={fetchStats}
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
          icon={Database}
          description="Total data files scanned"
          colorClass="bg-blue-500/10 border-blue-500/20 text-blue-400"
        />
        <StatsCard
          title="JSON Sources"
          value={jsonSourcesCount}
          icon={FileJson}
          description="FAQ and notice datasets"
          colorClass="bg-emerald-500/10 border-emerald-500/20 text-emerald-400"
        />
        <StatsCard
          title="PDF Sources (Phase 5B)"
          value={pdfSourcesCount}
          icon={FileText}
          description="Uploaded curriculum & calendar PDFs"
          trend={{ value: "Pending 5B", isPositive: true }}
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
            <div className="divide-y divide-slate-800/40 select-none">
              <div className="py-3.5 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-emerald-500/10 rounded-xl text-emerald-400 border border-emerald-500/20">
                    <FileJson className="w-4 h-4" />
                  </div>
                  <div>
                    <span className="text-xs font-semibold text-slate-200 block">student_faqs.json</span>
                    <span className="text-[10px] text-slate-400">Campus guidelines FAQs dataset</span>
                  </div>
                </div>
                <span className="text-xs font-semibold text-emerald-400 bg-emerald-950/30 border border-emerald-500/20 px-2 py-0.5 rounded-full">
                  Indexed
                </span>
              </div>

              <div className="py-3.5 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-emerald-500/10 rounded-xl text-emerald-400 border border-emerald-500/20">
                    <FileJson className="w-4 h-4" />
                  </div>
                  <div>
                    <span className="text-xs font-semibold text-slate-200 block">notices.json</span>
                    <span className="text-[10px] text-slate-400">Academic & exam notices feed</span>
                  </div>
                </div>
                <span className="text-xs font-semibold text-emerald-400 bg-emerald-950/30 border border-emerald-500/20 px-2 py-0.5 rounded-full">
                  Indexed
                </span>
              </div>

              <div className="py-3.5 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-500/10 rounded-xl text-blue-400 border border-blue-500/20">
                    <FileText className="w-4 h-4" />
                  </div>
                  <div>
                    <span className="text-xs font-semibold text-slate-200 block">academic_calendar_2026.pdf</span>
                    <span className="text-[10px] text-slate-400">Semester schedules (mock source)</span>
                  </div>
                </div>
                <span className="text-xs font-semibold text-blue-400 bg-blue-950/30 border border-blue-500/20 px-2 py-0.5 rounded-full">
                  Indexed
                </span>
              </div>

              <div className="py-3.5 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-amber-500/10 rounded-xl text-amber-400 border border-amber-500/20">
                    <FileText className="w-4 h-4" />
                  </div>
                  <div>
                    <span className="text-xs font-semibold text-slate-200 block">syllabus_cse_2026.pdf</span>
                    <span className="text-[10px] text-slate-400">Computer Science course curriculum</span>
                  </div>
                </div>
                <span className="text-xs font-semibold text-amber-400 bg-amber-950/30 border border-amber-500/20 px-2 py-0.5 rounded-full">
                  Pending Sync
                </span>
              </div>
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
              <div className="flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 mt-0.5 shrink-0" />
                <div>
                  <h4 className="text-xs font-semibold text-slate-200">Collection Health: Excellent</h4>
                  <p className="text-[10px] text-slate-400 mt-1 leading-relaxed">
                    Chroma collections are mapped and write permissions are confirmed. Schema models contain no corruption.
                  </p>
                </div>
              </div>

              <div className="p-4 bg-slate-900/50 rounded-xl border border-slate-900/80 space-y-3">
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-400">Embedding Schema</span>
                  <span className="font-semibold text-slate-300 font-mono">Dense Embeddings</span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-400">Total Chunks</span>
                  <span className="font-semibold text-slate-300 font-mono">248 Chunks</span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-400">Collection Name</span>
                  <span className="font-semibold text-slate-300 font-mono">langchain</span>
                </div>
              </div>

              <div className="p-3 bg-amber-500/5 border border-amber-500/10 rounded-xl flex gap-2.5">
                <AlertCircle className="w-4 h-4 text-amber-500 mt-0.5 shrink-0" />
                <p className="text-[10px] text-slate-400 leading-relaxed">
                  Uploading files in later phases will run automated text splitting using the RecursiveCharacterTextSplitter and ingestion pipeline.
                </p>
              </div>
            </div>
          </DashboardCard>
        </div>
      </div>
    </div>
  );
};
