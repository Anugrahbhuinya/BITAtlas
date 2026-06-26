import { useState, useEffect } from "react";
import adminApi from "../services/api";
import { DashboardCard } from "../components/DashboardCard";
import { CardSkeleton } from "../components/LoadingSkeleton";
import { Cpu, Database, Server, Info } from "lucide-react";

export const AdminSettingsPage = () => {
  const [settings, setSettings] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchSettings = async () => {
    setLoading(true);
    try {
      const response = await adminApi.get("/api/admin/settings");
      setSettings(response.data);
    } catch (e) {
      console.error("Failed to load settings configs", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-xl font-bold text-slate-100">System Settings</h2>
          <p className="text-xs text-slate-400 mt-1">Reading active configurations...</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <CardSkeleton />
          <CardSkeleton />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-slate-100 tracking-tight flex items-center gap-2">
          <span>System Configurations</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Active system parameters and model weights loaded from environment bindings.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Core RAG Model weights config */}
        <DashboardCard
          title="RAG Model Parameters"
          subtitle="Embedding settings and LLM selection targets"
        >
          <div className="space-y-4 pt-2 select-none">
            <div className="p-3 bg-slate-900/60 border border-slate-900 rounded-xl flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Cpu className="w-4 h-4 text-blue-400" />
                <div>
                  <span className="text-[10px] text-slate-500 uppercase block font-mono">LLM Core Model</span>
                  <span className="text-xs font-semibold text-slate-300 mt-0.5 block">{settings?.geminiModel}</span>
                </div>
              </div>
              <span className="text-[9px] font-bold text-blue-400 bg-blue-950/40 border border-blue-500/20 px-2 py-0.5 rounded">
                Active
              </span>
            </div>

            <div className="p-3 bg-slate-900/60 border border-slate-900 rounded-xl flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Cpu className="w-4 h-4 text-violet-400" />
                <div>
                  <span className="text-[10px] text-slate-500 uppercase block font-mono">Embedding Model</span>
                  <span className="text-xs font-semibold text-slate-300 mt-0.5 block">{settings?.embeddingModel}</span>
                </div>
              </div>
              <span className="text-[9px] font-bold text-violet-400 bg-violet-950/40 border border-violet-500/20 px-2 py-0.5 rounded">
                Active
              </span>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="p-3 bg-slate-900/60 border border-slate-900 rounded-xl">
                <span className="text-[10px] text-slate-500 block uppercase font-mono">Chunk size (chars)</span>
                <span className="text-xs font-semibold text-slate-300 font-mono mt-0.5 block">{settings?.chunkSize}</span>
              </div>
              <div className="p-3 bg-slate-900/60 border border-slate-900 rounded-xl">
                <span className="text-[10px] text-slate-500 block uppercase font-mono">Chunk overlap</span>
                <span className="text-xs font-semibold text-slate-300 font-mono mt-0.5 block">{settings?.chunkOverlap}</span>
              </div>
            </div>
          </div>
        </DashboardCard>

        {/* Database & vector collections settings */}
        <DashboardCard
          title="Data Storage Nodes"
          subtitle="Connection endpoints for vector stores and document logs"
        >
          <div className="space-y-4 pt-2 select-none">
            <div className="p-3 bg-slate-900/60 border border-slate-900 rounded-xl">
              <div className="flex items-center gap-3">
                <Database className="w-4 h-4 text-emerald-400" />
                <div>
                  <span className="text-[10px] text-slate-500 uppercase block font-mono">MongoDB Database</span>
                  <span className="text-xs font-semibold text-slate-300 mt-0.5 block truncate max-w-xs">{settings?.mongoDb}</span>
                </div>
              </div>
            </div>

            <div className="p-3 bg-slate-900/60 border border-slate-900 rounded-xl">
              <div className="flex items-center gap-3">
                <Server className="w-4 h-4 text-indigo-400" />
                <div>
                  <span className="text-[10px] text-slate-500 uppercase block font-mono">Chroma Collection</span>
                  <span className="text-xs font-semibold text-slate-300 mt-0.5 block">{settings?.chromaCollection}</span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="p-3 bg-slate-900/60 border border-slate-900 rounded-xl">
                <span className="text-[10px] text-slate-500 block uppercase font-mono">Environment Target</span>
                <span className="text-xs font-semibold text-slate-300 font-mono mt-0.5 block">Development</span>
              </div>
              <div className="p-3 bg-slate-900/60 border border-slate-900 rounded-xl">
                <span className="text-[10px] text-slate-500 block uppercase font-mono">System version</span>
                <span className="text-xs font-semibold text-slate-300 font-mono mt-0.5 block">{settings?.systemVersion}</span>
              </div>
            </div>
          </div>
        </DashboardCard>
      </div>

      {/* Configuration note footer card */}
      <div className="glass-panel p-5 rounded-2xl border border-slate-800/40 flex items-start gap-4">
        <div className="p-2 bg-slate-900 border border-slate-800 rounded-xl text-blue-400 shrink-0">
          <Info className="w-5 h-5" />
        </div>
        <div className="space-y-1">
          <h4 className="text-sm font-semibold text-slate-200">Read-Only Console Restrictions</h4>
          <p className="text-xs text-slate-400 leading-relaxed max-w-2xl">
            Currently, these configurations are loaded in read-only mode to prevent active model drift. Changing core models or database nodes requires edits to the backend environmental variable configuration files and server restarts.
          </p>
        </div>
      </div>
    </div>
  );
};
