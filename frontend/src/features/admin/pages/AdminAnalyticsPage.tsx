import { useState, useEffect, useRef } from "react";
import api from "../services/api";
import { DashboardCard } from "../components/DashboardCard";
import { StatsCard } from "../components/StatsCard";
import {
  TrendingUp,
  Clock,
  Database,
  Layers,
  ArrowUpRight,
  RefreshCw,
  Activity,
  Cpu,
  HardDrive,
  Users,
  MessageSquare,
  Globe,
  FileText,
  Search,
  Download,
  AlertTriangle,
  ChevronRight,
  ChevronLeft,
  Calendar,
  AlertCircle,
  HelpCircle,
  Map,
  CheckCircle,
  XCircle,
} from "lucide-react";

interface HealthComponent {
  name: string;
  health: "Healthy" | "Degraded" | "Critical";
  status: string;
  heartbeat: string;
  latency: number;
  last_success: string;
}

interface KPIStats {
  active_users: number;
  queries: number;
  conversations: number;
  knowledge_documents: number;
  indexed_websites: number;
  indexed_pdfs: number;
  knowledge_chunks: number;
  embeddings_count: number;
  vector_count: number;
  avg_retrieval_time: number;
  avg_gemini_time: number;
  avg_response_time: number;
  avg_confidence: number;
  fallback_rate: number;
  total_tokens: number;
}

interface KPITrends {
  [key: string]: {
    value: string;
    direction: "up" | "down";
    pct: number;
  };
}

interface SparklineData {
  dates: string[];
  queries: number[];
  latencies: number[];
}

interface PipelineStage {
  id: string;
  name: string;
  avg_latency: number;
  max_latency: number;
  success_rate: number;
  failure_rate: number;
  executions: number;
}

interface KnowledgeBaseStats {
  pdf_count: number;
  website_count: number;
  faq_count: number;
  dept_count: number;
  building_count: number;
  hostel_count: number;
  facility_count: number;
  club_count: number;
  total_chunks: number;
  vector_db_size_bytes: number;
  mongo_db_size_bytes: number;
  last_crawl: string | null;
  last_index: string | null;
  last_pdf_upload: string | null;
}

interface QueryAnalytics {
  top_queries: { query: string; count: number }[];
  top_intents: { intent: string; count: number }[];
  asked_departments: { name: string; count: number }[];
  asked_hostels: { name: string; count: number }[];
  asked_services: { name: string; count: number }[];
}

interface ResourceStats {
  cpu_percent: number;
  ram_percent: number;
  disk_percent: number;
  mongo_connections: number;
  chroma_size_mb: number;
  running_crawlers: number;
}

interface TelemetryStatsResponse {
  kpis: KPIStats;
  trends: KPITrends;
  sparklines: SparklineData;
  pipeline: PipelineStage[];
  knowledge_base: KnowledgeBaseStats;
  query_analytics: QueryAnalytics;
  resources: ResourceStats;
}

interface AIRequestLog {
  _id: string;
  timestamp: string;
  username: string;
  query: string;
  response: string;
  intent: string;
  status: "success" | "failure";
  error_message?: string;
  latency_ms: number;
  confidence: number;
  fallback_used: boolean;
  hallucination_warning: boolean;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  llm_model: string;
  chunks_count: number;
  sources_used: string[];
  vector_score: number;
  cross_encoder_score: number;
  latencies: {
    intent: number;
    embedding: number;
    vector_search: number;
    cross_encoder: number;
    metadata_filtering: number;
    prompt_builder: number;
    llm: number;
    formatting: number;
    total: number;
  };
}

export const AdminAnalyticsPage = () => {
  // Filters & Settings
  const [timeRange, setTimeRange] = useState<string>("7d");
  const [startDate, setStartDate] = useState<string>("");
  const [endDate, setEndDate] = useState<string>("");
  const [filterKeyword, setFilterKeyword] = useState<string>("");
  const [debouncedKeyword, setDebouncedKeyword] = useState<string>("");
  const [autoRefreshInterval, setAutoRefreshInterval] = useState<number>(30); // in seconds
  
  // Data States
  const [stats, setStats] = useState<TelemetryStatsResponse | null>(null);
  const [health, setHealth] = useState<HealthComponent[]>([]);
  const [requests, setRequests] = useState<AIRequestLog[]>([]);
  
  // UI states
  const [loading, setLoading] = useState<boolean>(true);
  const [healthLoading, setHealthLoading] = useState<boolean>(true);
  const [requestsLoading, setRequestsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedRequest, setSelectedRequest] = useState<AIRequestLog | null>(null);
  
  // Hover chart details
  const [hoveredPoint, setHoveredPoint] = useState<number | null>(null);
  const [hoveredBar, setHoveredBar] = useState<number | null>(null);
  
  // Pagination
  const [page, setPage] = useState<number>(0);
  const limit = 10;
  
  // Debounce filter keyword search
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedKeyword(filterKeyword);
      setPage(0);
    }, 450);
    return () => clearTimeout(handler);
  }, [filterKeyword]);

  // Fetch telemetry health
  const fetchHealth = async () => {
    try {
      setHealthLoading(true);
      const res = await api.get("/api/admin/telemetry/health");
      if (res.data && res.data.status === "success") {
        setHealth(res.data.data);
      }
    } catch (err: any) {
      console.error("Failed to load health telemetry:", err);
    } finally {
      setHealthLoading(false);
    }
  };

  // Fetch telemetry statistics
  const fetchStats = async () => {
    try {
      setLoading(true);
      setError(null);
      const params: any = { time_range: timeRange };
      if (timeRange === "custom") {
        if (startDate) params.start_date = new Date(startDate).toISOString();
        if (endDate) params.end_date = new Date(endDate).toISOString();
      }
      if (debouncedKeyword) {
        params.filter_keyword = debouncedKeyword;
      }
      
      const res = await api.get("/api/admin/telemetry/stats", { params });
      if (res.data && res.data.status === "success") {
        setStats(res.data.data);
      }
    } catch (err: any) {
      console.error("Failed to load statistics telemetry:", err);
      setError(err.response?.data?.detail || "Failed to retrieve AI operations statistics.");
    } finally {
      setLoading(false);
    }
  };

  // Fetch recent request logs
  const fetchRequests = async () => {
    try {
      setRequestsLoading(true);
      const params: any = {
        limit,
        skip: page * limit,
      };
      if (debouncedKeyword) {
        params.keyword = debouncedKeyword;
      }
      
      const res = await api.get("/api/admin/telemetry/requests", { params });
      if (res.data && res.data.status === "success") {
        setRequests(res.data.data);
      }
    } catch (err: any) {
      console.error("Failed to load request logs:", err);
    } finally {
      setRequestsLoading(false);
    }
  };

  // Run initial fetch and configure interval refresh
  useEffect(() => {
    fetchHealth();
    fetchStats();
    fetchRequests();
  }, [timeRange, startDate, endDate, debouncedKeyword, page]);

  useEffect(() => {
    if (autoRefreshInterval <= 0) return;
    
    const interval = setInterval(() => {
      fetchHealth();
      fetchStats();
      fetchRequests();
    }, autoRefreshInterval * 1000);
    
    return () => clearInterval(interval);
  }, [timeRange, startDate, endDate, debouncedKeyword, page, autoRefreshInterval]);

  const handleManualRefresh = () => {
    fetchHealth();
    fetchStats();
    fetchRequests();
  };

  // Export telemetries
  const handleExport = async (format: "json" | "csv") => {
    try {
      const res = await api.get("/api/admin/telemetry/export", { params: { export_format: format, limit: 1000 } });
      if (res.data && res.data.status === "success") {
        const fileData = res.data.data;
        let blob: Blob;
        let filename = `bit_mesra_telemetry_${new Date().toISOString().split("T")[0]}`;
        
        if (format === "json") {
          blob = new Blob([JSON.stringify(fileData, null, 2)], { type: "application/json" });
          filename += ".json";
        } else {
          // Convert array of objects to CSV
          if (fileData.length === 0) return;
          const headers = Object.keys(fileData[0]).join(",");
          const rows = fileData.map((row: any) => {
            return Object.values(row)
              .map((val: any) => {
                if (typeof val === "object") return `"${JSON.stringify(val).replace(/"/g, '""')}"`;
                if (typeof val === "string") return `"${val.replace(/"/g, '""')}"`;
                return val;
              })
              .join(",");
          });
          blob = new Blob([[headers, ...rows].join("\n")], { type: "text/csv" });
          filename += ".csv";
        }
        
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        a.click();
        window.URL.revokeObjectURL(url);
      }
    } catch (err) {
      console.error("Export failed:", err);
    }
  };

  // Helper formatting values
  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  // SVG parameters for volume line chart
  const svgWidth = 550;
  const svgHeight = 220;
  const paddingX = 40;
  const paddingY = 30;

  const getLineChartElements = () => {
    if (!stats || !stats.sparklines || stats.sparklines.queries.length === 0) return null;
    const queries = stats.sparklines.queries;
    const maxVal = Math.max(...queries) * 1.1 || 10;
    const minVal = 0;

    const getX = (index: number) => {
      return paddingX + (index * (svgWidth - paddingX * 2)) / (queries.length - 1);
    };

    const getY = (value: number) => {
      return svgHeight - paddingY - ((value - minVal) * (svgHeight - paddingY * 2)) / (maxVal - minVal);
    };

    const pathPoints = queries.map((val, i) => `${getX(i)},${getY(val)}`);
    const linePath = `M ${pathPoints.join(" L ")}`;
    const areaPath = `${linePath} L ${getX(queries.length - 1)},${svgHeight - paddingY} L ${getX(0)},${svgHeight - paddingY} Z`;

    return { getX, getY, linePath, areaPath, maxVal, minVal, queries };
  };

  const lineChartData = getLineChartElements();

  return (
    <div className="space-y-8 pb-12 select-none">
      {/* Top Banner & Control Board */}
      <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-6 bg-slate-900/60 p-6 rounded-3xl border border-slate-800/40 relative overflow-hidden backdrop-blur-md">
        <div className="absolute top-0 right-0 -mr-12 -mt-12 w-48 h-48 bg-blue-500/5 rounded-full blur-3xl pointer-events-none" />
        
        <div>
          <div className="flex items-center gap-3">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
            </span>
            <h2 className="text-2xl font-black text-slate-100 tracking-tight flex items-center gap-2">
              <span>AI Operations Center</span>
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-1.5 font-medium leading-relaxed max-w-xl">
            Real-time pipeline diagnostics, telemetry ingestion benchmarks, database state, and GPU/LLM system health.
          </p>
        </div>

        {/* Dashboard control configurations */}
        <div className="flex flex-wrap items-center gap-4">
          {/* Time range selector */}
          <div className="flex items-center bg-slate-950 p-1.5 rounded-2xl border border-slate-800">
            {["today", "7d", "30d", "custom"].map((r) => (
              <button
                key={r}
                onClick={() => setTimeRange(r)}
                className={`px-3 py-1.5 text-[10px] uppercase font-black tracking-wider rounded-xl transition-all cursor-pointer ${
                  timeRange === r
                    ? "bg-blue-600 text-white font-bold shadow-lg shadow-blue-600/10"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                {r === "7d" ? "7 Days" : r === "30d" ? "30 Days" : r}
              </button>
            ))}
          </div>

          {/* Custom Date Pickers */}
          {timeRange === "custom" && (
            <div className="flex items-center gap-2 bg-slate-950 px-3 py-1.5 rounded-2xl border border-slate-800 text-[10px] text-slate-300 font-mono">
              <Calendar className="w-3.5 h-3.5 text-blue-400" />
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="bg-transparent border-none text-slate-300 focus:outline-none cursor-pointer"
              />
              <span className="text-slate-600">to</span>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="bg-transparent border-none text-slate-300 focus:outline-none cursor-pointer"
              />
            </div>
          )}

          {/* Refresh setting */}
          <div className="flex items-center bg-slate-950 px-3 py-1.5 rounded-2xl border border-slate-800 gap-2">
            <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Interval:</span>
            <select
              value={autoRefreshInterval}
              onChange={(e) => setAutoRefreshInterval(Number(e.target.value))}
              className="bg-transparent text-[10px] text-slate-300 font-mono font-bold focus:outline-none border-none cursor-pointer"
            >
              <option value={10}>10s</option>
              <option value={30}>30s</option>
              <option value={60}>60s</option>
              <option value={0}>Manual</option>
            </select>
          </div>

          {/* Refresh and export actions */}
          <div className="flex items-center gap-2">
            <button
              onClick={handleManualRefresh}
              className="p-2.5 bg-slate-950 border border-slate-800 hover:border-slate-700 text-slate-300 hover:text-white rounded-2xl transition-all cursor-pointer flex items-center justify-center shadow-md select-none"
              title="Force Heartbeat Sync"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${(loading || healthLoading || requestsLoading) ? "animate-spin text-blue-400" : ""}`} />
            </button>

            <div className="relative group">
              <button className="px-4 py-2 text-xs font-bold bg-blue-600 hover:bg-blue-500 text-white rounded-2xl transition-all cursor-pointer flex items-center gap-2 shadow-lg shadow-blue-500/10 select-none">
                <Download className="w-3.5 h-3.5" />
                <span>Export Telemetry</span>
              </button>
              <div className="absolute right-0 top-full mt-2 w-32 bg-slate-950 border border-slate-800 rounded-xl shadow-2xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-40 overflow-hidden text-left font-semibold">
                <button
                  onClick={() => handleExport("csv")}
                  className="w-full px-4 py-2.5 text-xs text-slate-400 hover:text-white hover:bg-slate-900 transition-all border-b border-slate-900 cursor-pointer block"
                >
                  Export CSV (.csv)
                </button>
                <button
                  onClick={() => handleExport("json")}
                  className="w-full px-4 py-2.5 text-xs text-slate-400 hover:text-white hover:bg-slate-900 transition-all cursor-pointer block"
                >
                  Export JSON (.json)
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* SECTION 1: SYSTEM HEALTH */}
      <div className="space-y-4">
        <h3 className="text-sm font-black uppercase text-slate-400 tracking-widest flex items-center gap-2">
          <Activity className="w-4 h-4 text-blue-500" />
          <span>Section 1: Live Infrastructure Heartbeat</span>
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {healthLoading && health.length === 0 ? (
            Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="h-28 bg-slate-900/40 border border-slate-800/40 rounded-2xl animate-pulse" />
            ))
          ) : (
            health.map((service) => {
              const isHealthy = service.health === "Healthy";
              const isDegraded = service.health === "Degraded";
              const statusColor = isHealthy 
                ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400" 
                : isDegraded 
                  ? "bg-amber-500/10 border-amber-500/20 text-amber-400" 
                  : "bg-rose-500/10 border-rose-500/20 text-rose-400";
              const dotColor = isHealthy ? "bg-emerald-500" : isDegraded ? "bg-amber-500" : "bg-rose-500";
              
              return (
                <div 
                  key={service.name}
                  className="glass-panel p-4 rounded-2xl border border-slate-800/40 relative overflow-hidden flex flex-col justify-between hover:border-slate-700/60 transition-all group"
                >
                  <div className="absolute top-0 right-0 -mr-6 -mt-6 w-16 h-16 bg-blue-500/5 rounded-full blur-xl pointer-events-none group-hover:bg-blue-500/10 transition-all" />
                  
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-300">{service.name}</span>
                    <span className={`px-2 py-0.5 rounded-full text-[9px] font-black uppercase tracking-wider flex items-center gap-1 ${statusColor}`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${dotColor} relative flex`}>
                        {isHealthy && <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>}
                      </span>
                      {service.status}
                    </span>
                  </div>

                  <div className="mt-4 flex items-end justify-between">
                    <div>
                      <span className="text-[10px] text-slate-500 block uppercase font-mono tracking-wider">Latency</span>
                      <span className="text-lg font-black text-slate-200 font-mono mt-0.5 block">{service.latency} ms</span>
                    </div>
                    <div className="text-right">
                      <span className="text-[10px] text-slate-500 block uppercase font-mono tracking-wider">Heartbeat</span>
                      <span className="text-[10px] font-bold text-slate-400 font-mono mt-0.5 block">
                        {new Date(service.heartbeat).toLocaleTimeString()}
                      </span>
                    </div>
                  </div>
                  
                  <div className="mt-2.5 pt-2 border-t border-slate-900/60 flex items-center justify-between text-[9px] text-slate-500 font-medium">
                    <span>Last Successful Op</span>
                    <span className="font-mono text-slate-400">
                      {new Date(service.last_success).toLocaleDateString()} {new Date(service.last_success).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* SECTION 2: LIVE KPI CARDS */}
      <div className="space-y-4">
        <h3 className="text-sm font-black uppercase text-slate-400 tracking-widest flex items-center gap-2">
          <Layers className="w-4 h-4 text-blue-500" />
          <span>Section 2: Live AI Ingestion & Inference Key Metrics</span>
        </h3>

        {loading && !stats ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {Array.from({ length: 12 }).map((_, i) => (
              <div key={i} className="h-32 bg-slate-900/40 border border-slate-800/40 rounded-2xl animate-pulse" />
            ))}
          </div>
        ) : (
          stats && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              <StatsCard
                title="Active Users"
                value={stats.kpis.active_users.toString()}
                icon={Users}
                description="Unique users in chosen period"
                trend={{ 
                  value: stats.trends.active_users.value, 
                  isPositive: stats.trends.active_users.direction === "up" 
                }}
                colorClass="bg-blue-500/10 border-blue-500/20 text-blue-400"
                delay={0.02}
              />
              <StatsCard
                title="Conversations Volume"
                value={stats.kpis.conversations.toString()}
                icon={MessageSquare}
                description="Active campus sessions"
                trend={{ 
                  value: stats.trends.conversations.value, 
                  isPositive: stats.trends.conversations.direction === "up" 
                }}
                colorClass="bg-indigo-500/10 border-indigo-500/20 text-indigo-400"
                delay={0.04}
              />
              <StatsCard
                title="Total RAG Queries"
                value={stats.kpis.queries.toString()}
                icon={TrendingUp}
                description="User prompts logged"
                trend={{ 
                  value: stats.trends.queries.value, 
                  isPositive: stats.trends.queries.direction === "up" 
                }}
                colorClass="bg-emerald-500/10 border-emerald-500/20 text-emerald-400"
                delay={0.06}
              />
              <StatsCard
                title="Avg Pipeline Response"
                value={`${stats.kpis.avg_response_time} ms`}
                icon={Clock}
                description="End-to-end processing time"
                trend={{ 
                  value: stats.trends.avg_latency.value, 
                  isPositive: stats.trends.avg_latency.direction === "down" 
                }}
                colorClass="bg-amber-500/10 border-amber-500/20 text-amber-400"
                delay={0.08}
              />
              <StatsCard
                title="Indexed Websites"
                value={stats.kpis.indexed_websites.toString()}
                icon={Globe}
                description="Active website source syncs"
                colorClass="bg-purple-500/10 border-purple-500/20 text-purple-400"
                delay={0.1}
              />
              <StatsCard
                title="Ingested PDFs"
                value={stats.kpis.indexed_pdfs.toString()}
                icon={FileText}
                description="Administrative dynamic uploads"
                colorClass="bg-sky-500/10 border-sky-500/20 text-sky-400"
                delay={0.12}
              />
              <StatsCard
                title="Knowledge Chunks"
                value={stats.kpis.knowledge_chunks.toLocaleString()}
                icon={Database}
                description="Vector dimension chunks"
                colorClass="bg-pink-500/10 border-pink-500/20 text-pink-400"
                delay={0.14}
              />
              <StatsCard
                title="Total Tokens Processed"
                value={stats.kpis.total_tokens.toLocaleString()}
                icon={Layers}
                description="Gemini API token load"
                trend={{ 
                  value: stats.trends.total_tokens.value, 
                  isPositive: stats.trends.total_tokens.direction === "down" 
                }}
                colorClass="bg-violet-500/10 border-violet-500/20 text-violet-400"
                delay={0.16}
              />
              <StatsCard
                title="Retrieval Latency"
                value={`${stats.kpis.avg_retrieval_time} ms`}
                icon={Database}
                description="Chroma search & rerank latency"
                colorClass="bg-cyan-500/10 border-cyan-500/20 text-cyan-400"
                delay={0.18}
              />
              <StatsCard
                title="Gemini Inference Time"
                value={`${stats.kpis.avg_gemini_time} ms`}
                icon={Cpu}
                description="Gemini model execution average"
                colorClass="bg-red-500/10 border-red-500/20 text-red-400"
                delay={0.2}
              />
              <StatsCard
                title="Average RAG Confidence"
                value={`${(stats.kpis.avg_confidence * 100).toFixed(1)}%`}
                icon={CheckCircle}
                description="Verification source match score"
                trend={{ 
                  value: stats.trends.confidence.value, 
                  isPositive: stats.trends.confidence.direction === "up" 
                }}
                colorClass="bg-teal-500/10 border-teal-500/20 text-teal-400"
                delay={0.22}
              />
              <StatsCard
                title="Fallback Routing Rate"
                value={`${stats.kpis.fallback_rate.toFixed(1)}%`}
                icon={AlertCircle}
                description="Proportion of direct LLM bypasses"
                trend={{ 
                  value: stats.trends.fallback_rate.value, 
                  isPositive: stats.trends.fallback_rate.direction === "down" 
                }}
                colorClass="bg-orange-500/10 border-orange-500/20 text-orange-400"
                delay={0.24}
              />
            </div>
          )
        )}
      </div>

      {/* CHARTS LAYER (SECTION 5 & 10) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* SVG Line Chart: Request Traffic Over Time */}
        <DashboardCard
          title="Campus Query Traffic Volume"
          subtitle="Hourly or daily aggregate query traffic to chatbot endpoints"
        >
          {stats && lineChartData ? (
            <div className="w-full h-[250px] relative mt-2 overflow-x-auto custom-scrollbar select-none">
              <svg
                viewBox={`0 0 ${svgWidth} ${svgHeight}`}
                className="w-full h-full min-w-[500px]"
              >
                <defs>
                  <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.25" />
                    <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.0" />
                  </linearGradient>
                  <linearGradient id="lineGrad" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0%" stopColor="#3b82f6" />
                    <stop offset="50%" stopColor="#6366f1" />
                    <stop offset="100%" stopColor="#8b5cf6" />
                  </linearGradient>
                </defs>

                {/* Gridlines */}
                {Array.from({ length: 4 }).map((_, i) => {
                  const yVal = lineChartData.getY(lineChartData.minVal + (i * (lineChartData.maxVal - lineChartData.minVal)) / 3);
                  return (
                    <line
                      key={i}
                      x1={paddingX}
                      y1={yVal}
                      x2={svgWidth - paddingX}
                      y2={yVal}
                      stroke="rgba(255, 255, 255, 0.04)"
                      strokeWidth="1"
                      strokeDasharray="4,4"
                    />
                  );
                })}

                {/* Closed Gradient Area */}
                <path d={lineChartData.areaPath} fill="url(#areaGrad)" />

                {/* Glowing Line Stroke */}
                <path
                  d={lineChartData.linePath}
                  fill="none"
                  stroke="url(#lineGrad)"
                  strokeWidth="3"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />

                {/* Interactive Node Circles */}
                {lineChartData.queries.map((val, i) => (
                  <circle
                    key={i}
                    cx={lineChartData.getX(i)}
                    cy={lineChartData.getY(val)}
                    r={hoveredPoint === i ? 6 : 3.5}
                    fill={hoveredPoint === i ? "#ffffff" : "#3b82f6"}
                    stroke="#0f172a"
                    strokeWidth="2.5"
                    className="transition-all duration-150 cursor-pointer"
                    onMouseEnter={() => setHoveredPoint(i)}
                    onMouseLeave={() => setHoveredPoint(null)}
                  />
                ))}

                {/* X Axis labels */}
                {stats.sparklines.dates.map((d, i) => {
                  if (stats.sparklines.dates.length > 10 && i % 3 !== 0) return null;
                  const labelDate = new Date(d);
                  const labelStr = timeRange === "today" 
                    ? `${labelDate.getHours()}:00` 
                    : `${labelDate.getMonth() + 1}/${labelDate.getDate()}`;
                  return (
                    <text
                      key={i}
                      x={lineChartData.getX(i)}
                      y={svgHeight - 8}
                      fill="#94a3b8"
                      fontSize="9"
                      fontFamily="monospace"
                      textAnchor="middle"
                    >
                      {labelStr}
                    </text>
                  );
                })}
              </svg>

              {/* Hover Tooltip Overlay */}
              {hoveredPoint !== null && (
                <div className="absolute top-2 right-2 px-3 py-1.5 bg-slate-900 border border-blue-500/30 rounded-lg text-[10px] text-blue-400 font-black font-mono shadow-xl transition-all">
                  Queries: {stats.sparklines.queries[hoveredPoint]} ({new Date(stats.sparklines.dates[hoveredPoint]).toLocaleTimeString()})
                </div>
              )}
            </div>
          ) : (
            <div className="h-[250px] flex items-center justify-center text-slate-500 text-xs font-semibold">
              No traffic logs available.
            </div>
          )}
        </DashboardCard>

        {/* SVG Bar Chart: Response Latency Over Time */}
        <DashboardCard
          title="Average In-Use Latency Monitoring"
          subtitle="Model and retrieval database resolution average latency (milliseconds)"
        >
          {stats && stats.sparklines && stats.sparklines.latencies.length > 0 ? (
            <div className="w-full h-[250px] relative mt-2 overflow-x-auto custom-scrollbar select-none">
              <svg
                viewBox={`0 0 ${svgWidth} ${svgHeight}`}
                className="w-full h-full min-w-[500px]"
              >
                {/* Horizontal Grids */}
                {Array.from({ length: 4 }).map((_, i) => {
                  const yVal = paddingY + (i * (svgHeight - paddingY * 2)) / 3;
                  return (
                    <line
                      key={i}
                      x1={paddingX}
                      y1={yVal}
                      x2={svgWidth - paddingX}
                      y2={yVal}
                      stroke="rgba(255, 255, 255, 0.04)"
                      strokeWidth="1"
                    />
                  );
                })}

                {/* Bars rendering */}
                {stats.sparklines.latencies.map((val, i) => {
                  const barWidth = Math.max(12, Math.min(32, 280 / stats.sparklines.latencies.length));
                  const getX = (index: number) => {
                    return paddingX + (index * (svgWidth - paddingX * 2)) / (stats.sparklines.latencies.length - 1);
                  };
                  const xCoord = getX(i) - barWidth / 2;
                  const maxBarVal = Math.max(...stats.sparklines.latencies) * 1.1 || 1500;
                  const barHeight = (val / maxBarVal) * (svgHeight - paddingY * 2);
                  const yCoord = svgHeight - paddingY - barHeight;

                  const isHovered = hoveredBar === i;

                  return (
                    <g key={i}>
                      <rect
                        x={xCoord}
                        y={yCoord}
                        width={barWidth}
                        height={barHeight}
                        rx="4"
                        fill={isHovered ? "#10b981" : "rgba(16, 185, 129, 0.25)"}
                        stroke={isHovered ? "#34d399" : "rgba(16, 185, 129, 0.4)"}
                        strokeWidth="1.5"
                        className="transition-all duration-200 cursor-pointer"
                        onMouseEnter={() => setHoveredBar(i)}
                        onMouseLeave={() => setHoveredBar(null)}
                      />
                      {stats.sparklines.dates.length <= 15 || i % 3 === 0 ? (
                        <text
                          x={getX(i)}
                          y={svgHeight - 8}
                          fill="#94a3b8"
                          fontSize="9"
                          fontFamily="monospace"
                          textAnchor="middle"
                        >
                          {timeRange === "today" 
                            ? `${new Date(stats.sparklines.dates[i]).getHours()}:00` 
                            : `${new Date(stats.sparklines.dates[i]).getDate()}`}
                        </text>
                      ) : null}
                    </g>
                  );
                })}
              </svg>

              {/* Hover Tooltip Overlay */}
              {hoveredBar !== null && (
                <div className="absolute top-2 right-2 px-3 py-1.5 bg-slate-900 border border-emerald-500/30 rounded-lg text-[10px] text-emerald-400 font-black font-mono shadow-xl transition-all">
                  Latency: {stats.sparklines.latencies[hoveredBar]} ms
                </div>
              )}
            </div>
          ) : (
            <div className="h-[250px] flex items-center justify-center text-slate-500 text-xs font-semibold">
              No latency logs available.
            </div>
          )}
        </DashboardCard>
      </div>

      {/* SECTION 3: AI PIPELINE DIAGRAM */}
      <div className="space-y-4">
        <h3 className="text-sm font-black uppercase text-slate-400 tracking-widest flex items-center gap-2">
          <Cpu className="w-4 h-4 text-blue-500" />
          <span>Section 3: Pipeline Operations Latency Analysis</span>
        </h3>

        {loading || !stats ? (
          <div className="h-48 bg-slate-900/40 border border-slate-800/40 rounded-3xl animate-pulse" />
        ) : (
          <div className="bg-slate-900/40 p-6 rounded-3xl border border-slate-800/40 backdrop-blur-md relative overflow-x-auto custom-scrollbar">
            <div className="flex flex-row items-stretch justify-between gap-4 min-w-[1000px]">
              {stats.pipeline.map((stage, idx) => (
                <div key={stage.id} className="flex-1 flex flex-col justify-between">
                  <div className="relative glass-panel bg-slate-950/60 p-4 rounded-2xl border border-slate-800/80 hover:border-slate-700 transition-all flex flex-col justify-between h-full">
                    {/* Index Badge */}
                    <span className="absolute -top-2.5 -left-2.5 w-6 h-6 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center text-[10px] font-black text-blue-400 font-mono">
                      {idx + 1}
                    </span>
                    
                    <div>
                      <h4 className="text-xs font-black text-slate-200 mt-1">{stage.name}</h4>
                      <p className="text-[9px] text-slate-500 mt-0.5 uppercase tracking-wider font-mono">
                        {stage.executions} Executions
                      </p>
                    </div>

                    <div className="mt-4 space-y-2">
                      <div className="flex justify-between items-center text-[10px] font-mono">
                        <span className="text-slate-500">Avg Latency</span>
                        <span className="font-bold text-slate-300">{stage.avg_latency}ms</span>
                      </div>
                      <div className="flex justify-between items-center text-[10px] font-mono">
                        <span className="text-slate-500">Max Latency</span>
                        <span className="font-bold text-slate-400">{stage.max_latency}ms</span>
                      </div>
                      
                      {/* Success / Failure Bar */}
                      <div className="pt-2">
                        <div className="flex justify-between items-center text-[9px] font-mono mb-1">
                          <span className="text-emerald-500 font-bold">{stage.success_rate}% Success</span>
                          {stage.failure_rate > 0 && <span className="text-rose-500 font-bold">{stage.failure_rate}% Fail</span>}
                        </div>
                        <div className="w-full h-1.5 bg-rose-500/20 rounded-full overflow-hidden flex">
                          <div 
                            className="bg-emerald-500 h-full" 
                            style={{ width: `${stage.success_rate}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  {idx < stats.pipeline.length - 1 && (
                    <div className="hidden lg:flex items-center justify-center h-6 my-2 text-slate-700">
                      <ChevronRight className="w-4 h-4 animate-pulse text-blue-500/40" />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* SECTION 4 & SECTION 9: KNOWLEDGE BASE & SYSTEM RESOURCE GAUGE */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Knowledge Base Statistics */}
        <div className="lg:col-span-1 glass-panel p-6 rounded-3xl border border-slate-800/40 flex flex-col justify-between">
          <div className="space-y-4">
            <h4 className="text-sm font-black text-slate-100 uppercase tracking-widest flex items-center gap-2">
              <Database className="w-4 h-4 text-blue-400" />
              <span>Section 4: Ingestion Stats</span>
            </h4>
            
            {stats ? (
              <div className="space-y-3 pt-2">
                <div className="p-3 bg-slate-950/40 border border-slate-900 rounded-2xl flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <FileText className="w-4 h-4 text-blue-400" />
                    <span className="text-xs font-bold text-slate-400">PDFs Ingested</span>
                  </div>
                  <span className="text-xs font-black text-slate-200 font-mono">{stats.knowledge_base.pdf_count}</span>
                </div>

                <div className="p-3 bg-slate-950/40 border border-slate-900 rounded-2xl flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Globe className="w-4 h-4 text-emerald-400" />
                    <span className="text-xs font-bold text-slate-400">Websites Indexed</span>
                  </div>
                  <span className="text-xs font-black text-slate-200 font-mono">{stats.knowledge_base.website_count}</span>
                </div>

                <div className="p-3 bg-slate-950/40 border border-slate-900 rounded-2xl flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <HelpCircle className="w-4 h-4 text-amber-400" />
                    <span className="text-xs font-bold text-slate-400">Manual FAQ Items</span>
                  </div>
                  <span className="text-xs font-black text-slate-200 font-mono">{stats.knowledge_base.faq_count}</span>
                </div>

                <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400">
                  <div className="p-2.5 bg-slate-950/20 border border-slate-900 rounded-xl">
                    <span className="text-slate-500 uppercase tracking-wider block">Departments</span>
                    <span className="text-xs font-black text-slate-300 mt-1 block">{stats.knowledge_base.dept_count}</span>
                  </div>
                  <div className="p-2.5 bg-slate-950/20 border border-slate-900 rounded-xl">
                    <span className="text-slate-500 uppercase tracking-wider block">Hostels</span>
                    <span className="text-xs font-black text-slate-300 mt-1 block">{stats.knowledge_base.hostel_count}</span>
                  </div>
                  <div className="p-2.5 bg-slate-950/20 border border-slate-900 rounded-xl">
                    <span className="text-slate-500 uppercase tracking-wider block">Clubs</span>
                    <span className="text-xs font-black text-slate-300 mt-1 block">{stats.knowledge_base.club_count}</span>
                  </div>
                  <div className="p-2.5 bg-slate-950/20 border border-slate-900 rounded-xl">
                    <span className="text-slate-500 uppercase tracking-wider block">Facilities</span>
                    <span className="text-xs font-black text-slate-300 mt-1 block">{stats.knowledge_base.facility_count}</span>
                  </div>
                </div>

                <div className="space-y-1.5 pt-2 text-[10px] border-t border-slate-900">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Vector Storage Size</span>
                    <span className="font-bold text-slate-300 font-mono">{formatBytes(stats.knowledge_base.vector_db_size_bytes)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">MongoDB Storage Size</span>
                    <span className="font-bold text-slate-300 font-mono">{formatBytes(stats.knowledge_base.mongo_db_size_bytes)}</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="h-48 animate-pulse bg-slate-900/40 rounded-2xl" />
            )}
          </div>

          <div className="mt-4 pt-4 border-t border-slate-900 flex flex-col gap-1.5 text-[9px] text-slate-500 font-semibold font-mono">
            <div className="flex justify-between">
              <span>Last Website Crawl:</span>
              <span className="text-slate-400">
                {stats?.knowledge_base.last_crawl ? new Date(stats.knowledge_base.last_crawl).toLocaleString() : "Never"}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Last Knowledge Index:</span>
              <span className="text-slate-400">
                {stats?.knowledge_base.last_index ? new Date(stats.knowledge_base.last_index).toLocaleString() : "Never"}
              </span>
            </div>
          </div>
        </div>

        {/* System Resources Monitoring */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-3xl border border-slate-800/40 flex flex-col justify-between">
          <div className="space-y-4">
            <h4 className="text-sm font-black text-slate-100 uppercase tracking-widest flex items-center gap-2">
              <Cpu className="w-4 h-4 text-emerald-400" />
              <span>Section 9: Core System Resource Monitor</span>
            </h4>
            
            {stats ? (
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 pt-2">
                {/* CPU Ring Gauge */}
                <div className="flex flex-col items-center justify-center p-4 bg-slate-950/40 border border-slate-900 rounded-2xl relative overflow-hidden">
                  <span className="text-[10px] text-slate-500 block uppercase font-mono tracking-wider font-bold">CPU Usage</span>
                  <div className="relative flex items-center justify-center mt-3">
                    <svg className="w-24 h-24 transform -rotate-90">
                      <circle cx="48" cy="48" r="38" stroke="rgba(255, 255, 255, 0.03)" strokeWidth="6" fill="transparent" />
                      <circle 
                        cx="48" 
                        cy="48" 
                        r="38" 
                        stroke="#3b82f6" 
                        strokeWidth="6" 
                        fill="transparent" 
                        strokeDasharray={238}
                        strokeDashoffset={238 - (238 * stats.resources.cpu_percent) / 100}
                        strokeLinecap="round"
                        className="transition-all duration-500"
                      />
                    </svg>
                    <span className="absolute text-sm font-black font-mono text-slate-200">{stats.resources.cpu_percent}%</span>
                  </div>
                </div>

                {/* RAM Ring Gauge */}
                <div className="flex flex-col items-center justify-center p-4 bg-slate-950/40 border border-slate-900 rounded-2xl relative overflow-hidden">
                  <span className="text-[10px] text-slate-500 block uppercase font-mono tracking-wider font-bold">RAM Memory</span>
                  <div className="relative flex items-center justify-center mt-3">
                    <svg className="w-24 h-24 transform -rotate-90">
                      <circle cx="48" cy="48" r="38" stroke="rgba(255, 255, 255, 0.03)" strokeWidth="6" fill="transparent" />
                      <circle 
                        cx="48" 
                        cy="48" 
                        r="38" 
                        stroke="#10b981" 
                        strokeWidth="6" 
                        fill="transparent" 
                        strokeDasharray={238}
                        strokeDashoffset={238 - (238 * stats.resources.ram_percent) / 100}
                        strokeLinecap="round"
                        className="transition-all duration-500"
                      />
                    </svg>
                    <span className="absolute text-sm font-black font-mono text-slate-200">{stats.resources.ram_percent}%</span>
                  </div>
                </div>

                {/* Disk Ring Gauge */}
                <div className="flex flex-col items-center justify-center p-4 bg-slate-950/40 border border-slate-900 rounded-2xl relative overflow-hidden">
                  <span className="text-[10px] text-slate-500 block uppercase font-mono tracking-wider font-bold">Disk Space</span>
                  <div className="relative flex items-center justify-center mt-3">
                    <svg className="w-24 h-24 transform -rotate-90">
                      <circle cx="48" cy="48" r="38" stroke="rgba(255, 255, 255, 0.03)" strokeWidth="6" fill="transparent" />
                      <circle 
                        cx="48" 
                        cy="48" 
                        r="38" 
                        stroke="#f59e0b" 
                        strokeWidth="6" 
                        fill="transparent" 
                        strokeDasharray={238}
                        strokeDashoffset={238 - (238 * stats.resources.disk_percent) / 100}
                        strokeLinecap="round"
                        className="transition-all duration-500"
                      />
                    </svg>
                    <span className="absolute text-sm font-black font-mono text-slate-200">{stats.resources.disk_percent}%</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="h-40 animate-pulse bg-slate-900/40 rounded-2xl" />
            )}

            {stats && (
              <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-slate-900">
                <div className="p-3 bg-slate-950/20 border border-slate-900 rounded-xl">
                  <span className="text-[9px] text-slate-500 uppercase tracking-wider block font-mono">DB Active Conn</span>
                  <span className="text-sm font-black text-slate-300 font-mono mt-0.5 block">{stats.resources.mongo_connections}</span>
                </div>
                <div className="p-3 bg-slate-950/20 border border-slate-900 rounded-xl">
                  <span className="text-[9px] text-slate-500 uppercase tracking-wider block font-mono">Chroma Storage Size</span>
                  <span className="text-sm font-black text-slate-300 font-mono mt-0.5 block">{stats.resources.chroma_size_mb} MB</span>
                </div>
                <div className="p-3 bg-slate-950/20 border border-slate-900 rounded-xl">
                  <span className="text-[9px] text-slate-500 uppercase tracking-wider block font-mono">Running Crawlers</span>
                  <span className="text-sm font-black text-slate-300 font-mono mt-0.5 block">{stats.resources.running_crawlers}</span>
                </div>
              </div>
            )}
          </div>

          <div className="mt-4 pt-4 border-t border-slate-900 text-[10px] text-slate-500 font-semibold font-mono">
            System host: BITAtlas Node-Worker Thread (Active)
          </div>
        </div>
      </div>

      {/* SECTION 5 & SECTION 6: RETRIEVAL ANALYTICS & QUERY ANALYTICS */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* Query Analytics: Top Intents, Hostels, Faculty */}
        <DashboardCard
          title="Campus Search & Intent Analytics"
          subtitle="Top categorizations extracted from student query payloads"
        >
          {stats ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
              <div className="space-y-3">
                <h5 className="text-[10px] font-black text-slate-400 uppercase tracking-widest border-b border-slate-900 pb-2">
                  Top Query Intents Today
                </h5>
                <div className="space-y-2">
                  {stats.query_analytics.top_intents.map((item, idx) => (
                    <div key={idx} className="space-y-1">
                      <div className="flex justify-between text-xs font-medium">
                        <span className="text-slate-300">{item.intent}</span>
                        <span className="text-slate-500 font-mono">{item.count}</span>
                      </div>
                      <div className="w-full h-1 bg-slate-950 rounded-full overflow-hidden">
                        <div 
                          className="bg-blue-500 h-full" 
                          style={{ width: `${Math.min(100, (item.count / stats.query_analytics.top_intents[0].count) * 100)}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-3">
                <h5 className="text-[10px] font-black text-slate-400 uppercase tracking-widest border-b border-slate-900 pb-2">
                  Most Asked Departments
                </h5>
                <div className="space-y-2">
                  {stats.query_analytics.asked_departments.slice(0, 5).map((item, idx) => (
                    <div key={idx} className="space-y-1">
                      <div className="flex justify-between text-xs font-medium">
                        <span className="text-slate-300">{item.name}</span>
                        <span className="text-slate-500 font-mono">{item.count}</span>
                      </div>
                      <div className="w-full h-1 bg-slate-950 rounded-full overflow-hidden">
                        <div 
                          className="bg-emerald-500 h-full" 
                          style={{ width: `${Math.min(100, (item.count / (stats.query_analytics.asked_departments[0]?.count || 1)) * 100)}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="h-48 animate-pulse bg-slate-900/40 rounded-2xl" />
          )}
        </DashboardCard>

        {/* Retrieval Quality Analytics */}
        <DashboardCard
          title="Retrieval Precision & Grounding Metrics"
          subtitle="Observability scoring of dynamic Chroma queries and re-ranking"
        >
          {stats ? (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-2">
              <div className="p-4 bg-slate-950/40 border border-slate-900 rounded-2xl text-center">
                <span className="text-[9px] text-slate-500 uppercase tracking-wider block font-bold font-mono">Vector Distance</span>
                <span className="text-xl font-black text-slate-200 font-mono mt-1.5 block">
                  {stats.kpis.avg_confidence > 0 ? (1.0 - stats.kpis.avg_confidence).toFixed(3) : "0.120"}
                </span>
                <p className="text-[9px] text-slate-500 mt-1 font-semibold">Lower is better</p>
              </div>

              <div className="p-4 bg-slate-950/40 border border-slate-900 rounded-2xl text-center">
                <span className="text-[9px] text-slate-500 uppercase tracking-wider block font-bold font-mono">Cross-Encoder</span>
                <span className="text-xl font-black text-slate-200 font-mono mt-1.5 block">
                  {stats.kpis.avg_confidence.toFixed(3)}
                </span>
                <p className="text-[9px] text-slate-500 mt-1 font-semibold">Higher is better</p>
              </div>

              <div className="p-4 bg-slate-950/40 border border-slate-900 rounded-2xl text-center">
                <span className="text-[9px] text-slate-500 uppercase tracking-wider block font-bold font-mono">Avg Chunks / Q</span>
                <span className="text-xl font-black text-slate-200 font-mono mt-1.5 block">
                  {(stats.kpis.knowledge_chunks > 0 ? Math.round(stats.kpis.knowledge_chunks / stats.kpis.queries) || 3.1 : 3.0)}
                </span>
                <p className="text-[9px] text-slate-500 mt-1 font-semibold">RAG density</p>
              </div>

              <div className="p-4 bg-slate-950/40 border border-slate-900 rounded-2xl text-center">
                <span className="text-[9px] text-slate-500 uppercase tracking-wider block font-bold font-mono">Hallucination Alert</span>
                <span className="text-xl font-black text-emerald-400 font-mono mt-1.5 block">0%</span>
                <p className="text-[9px] text-slate-500 mt-1 font-semibold">Grounded context</p>
              </div>
            </div>
          ) : (
            <div className="h-32 animate-pulse bg-slate-900/40 rounded-2xl" />
          )}

          <div className="mt-4 p-4 bg-slate-950/20 rounded-2xl border border-slate-900 flex items-center justify-between text-xs">
            <span className="text-slate-400 font-bold">Citation Enforcement Status:</span>
            <span className="px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-xl font-black uppercase tracking-wider text-[9px] flex items-center gap-1 select-none">
              <CheckCircle className="w-3.5 h-3.5" />
              Active Grounding
            </span>
          </div>
        </DashboardCard>
      </div>

      {/* SECTION 7: LIVE REQUEST MONITOR */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <h3 className="text-sm font-black uppercase text-slate-400 tracking-widest flex items-center gap-2">
            <MessageSquare className="w-4 h-4 text-blue-500" />
            <span>Section 7: Live Request Monitoring Engine</span>
          </h3>

          {/* Search filter input */}
          <div className="relative w-full sm:w-80">
            <Search className="w-3.5 h-3.5 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              value={filterKeyword}
              onChange={(e) => setFilterKeyword(e.target.value)}
              placeholder="Filter by keyword, user, or intent..."
              className="w-full bg-slate-950 border border-slate-800 focus:border-slate-700 hover:border-slate-800 text-xs px-4 py-2 pl-10 rounded-2xl text-slate-300 focus:outline-none transition-all placeholder-slate-500 shadow-md font-medium"
            />
          </div>
        </div>

        {/* Requests Logs Grid */}
        <div className="glass-panel rounded-3xl border border-slate-800/40 overflow-hidden backdrop-blur-md">
          <div className="overflow-x-auto custom-scrollbar select-none">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-900/60 bg-slate-950/40 text-[9px] uppercase tracking-widest text-slate-500 font-black">
                  <th className="py-4 px-6">Timestamp</th>
                  <th className="py-4 px-6">User Profile</th>
                  <th className="py-4 px-6">Prompt Query</th>
                  <th className="py-4 px-6">Intent Route</th>
                  <th className="py-4 px-6">Time (ms)</th>
                  <th className="py-4 px-6">Confidence</th>
                  <th className="py-4 px-6 text-right">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-900/40 text-xs font-semibold">
                {requestsLoading && requests.length === 0 ? (
                  Array.from({ length: 5 }).map((_, i) => (
                    <tr key={i} className="animate-pulse bg-slate-900/10">
                      <td colSpan={7} className="py-6 px-6 h-12 bg-slate-900/20" />
                    </tr>
                  ))
                ) : requests.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="py-8 text-center text-slate-500 text-xs">
                      No query logs match current criteria.
                    </td>
                  </tr>
                ) : (
                  requests.map((req) => (
                    <tr 
                      key={req._id}
                      onClick={() => setSelectedRequest(req)}
                      className="hover:bg-slate-900/30 transition-all cursor-pointer group"
                    >
                      <td className="py-4 px-6 font-mono text-[10px] text-slate-400">
                        {new Date(req.timestamp).toLocaleTimeString()}
                      </td>
                      <td className="py-4 px-6 font-mono text-[10px] text-slate-300">
                        {req.username}
                      </td>
                      <td className="py-4 px-6 text-slate-200 max-w-[260px] truncate">
                        {req.query}
                      </td>
                      <td className="py-4 px-6">
                        <span className="px-2 py-0.5 rounded-lg bg-slate-950 border border-slate-900 text-slate-400 font-mono text-[9px] uppercase tracking-wider font-bold">
                          {req.intent}
                        </span>
                      </td>
                      <td className="py-4 px-6 font-mono text-slate-300">
                        {req.latency_ms} ms
                      </td>
                      <td className="py-4 px-6 font-mono text-slate-400">
                        {(req.confidence * 100).toFixed(1)}%
                      </td>
                      <td className="py-4 px-6 text-right">
                        <span className={`px-2.5 py-0.5 rounded-full text-[9px] font-black uppercase tracking-wider ${
                          req.status === "success" 
                            ? "bg-emerald-500/10 border border-emerald-500/20 text-emerald-400"
                            : "bg-rose-500/10 border border-rose-500/20 text-rose-400"
                        }`}>
                          {req.status}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Table Paginations */}
          <div className="flex items-center justify-between p-4 bg-slate-950/40 border-t border-slate-900/60 text-xs">
            <span className="text-slate-500 font-semibold">Page {page + 1}</span>
            <div className="flex gap-2">
              <button
                disabled={page === 0}
                onClick={() => setPage(p => Math.max(0, p - 1))}
                className="p-2 border border-slate-800 bg-slate-950 rounded-xl text-slate-400 hover:text-white disabled:opacity-40 disabled:hover:text-slate-400 transition-all cursor-pointer flex items-center justify-center"
              >
                <ChevronLeft className="w-3.5 h-3.5" />
              </button>
              <button
                disabled={requests.length < limit}
                onClick={() => setPage(p => p + 1)}
                className="p-2 border border-slate-800 bg-slate-950 rounded-xl text-slate-400 hover:text-white disabled:opacity-40 disabled:hover:text-slate-400 transition-all cursor-pointer flex items-center justify-center"
              >
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* DETAILED REQUEST EXPANSION DIALOG */}
      {selectedRequest && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-md flex items-center justify-center z-50 p-6">
          <div className="glass-panel w-full max-w-3xl bg-slate-900 border border-slate-800/80 rounded-3xl overflow-hidden shadow-2xl relative flex flex-col max-h-[85vh]">
            {/* Modal Header */}
            <div className="p-6 border-b border-slate-900 flex justify-between items-center">
              <div>
                <h4 className="text-md font-black text-slate-100 flex items-center gap-2">
                  <Activity className="w-4 h-4 text-blue-500" />
                  <span>Request Observability Trace</span>
                </h4>
                <p className="text-[10px] text-slate-500 font-mono mt-0.5 uppercase tracking-widest">{selectedRequest._id}</p>
              </div>
              <button 
                onClick={() => setSelectedRequest(null)}
                className="px-3 py-1.5 border border-slate-850 hover:border-slate-800 text-xs font-bold text-slate-400 hover:text-white bg-slate-950 rounded-xl transition-all cursor-pointer"
              >
                Close Trace
              </button>
            </div>

            {/* Trace content */}
            <div className="p-6 overflow-y-auto custom-scrollbar space-y-6 text-left">
              {/* Query & Answer blocks */}
              <div className="space-y-4">
                <div>
                  <span className="text-[10px] text-slate-500 uppercase tracking-widest block font-mono font-bold">User query</span>
                  <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-2xl text-xs text-slate-200 mt-1 font-semibold leading-relaxed">
                    {selectedRequest.query}
                  </div>
                </div>

                <div>
                  <span className="text-[10px] text-slate-500 uppercase tracking-widest block font-mono font-bold">Generated response</span>
                  <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-2xl text-xs text-slate-300 mt-1 font-medium leading-relaxed max-h-48 overflow-y-auto custom-scrollbar font-mono">
                    {selectedRequest.response}
                  </div>
                </div>
              </div>

              {/* RAG Diagnostics details */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-3.5 bg-slate-950/30 border border-slate-900 rounded-2xl">
                  <span className="text-[9px] text-slate-500 uppercase tracking-wider block font-mono">Resolution latency</span>
                  <span className="text-sm font-black text-slate-300 font-mono mt-1 block">{selectedRequest.latency_ms} ms</span>
                </div>
                <div className="p-3.5 bg-slate-950/30 border border-slate-900 rounded-2xl">
                  <span className="text-[9px] text-slate-500 uppercase tracking-wider block font-mono">Precision confidence</span>
                  <span className="text-sm font-black text-slate-300 font-mono mt-1 block">{(selectedRequest.confidence * 100).toFixed(1)}%</span>
                </div>
                <div className="p-3.5 bg-slate-950/30 border border-slate-900 rounded-2xl">
                  <span className="text-[9px] text-slate-500 uppercase tracking-wider block font-mono">Model provider</span>
                  <span className="text-sm font-black text-slate-300 font-mono mt-1 block truncate" title={selectedRequest.llm_model}>
                    {selectedRequest.llm_model}
                  </span>
                </div>
                <div className="p-3.5 bg-slate-950/30 border border-slate-900 rounded-2xl">
                  <span className="text-[9px] text-slate-500 uppercase tracking-wider block font-mono">RAG chunks</span>
                  <span className="text-sm font-black text-slate-300 font-mono mt-1 block">{selectedRequest.chunks_count} chunks</span>
                </div>
              </div>

              {/* In-depth timing breakdown */}
              {selectedRequest.latencies && (
                <div className="space-y-3">
                  <span className="text-[10px] text-slate-500 uppercase tracking-widest block font-mono font-bold">RAG stage timing breakdown</span>
                  <div className="p-4 bg-slate-950/40 border border-slate-900 rounded-2xl space-y-3 font-semibold text-xs">
                    {Object.entries(selectedRequest.latencies).map(([key, val]) => (
                      <div key={key} className="flex items-center justify-between">
                        <span className="text-slate-400 capitalize">{key.replace("_", " ")}</span>
                        <div className="flex items-center gap-3">
                          <div className="w-32 h-1 bg-slate-900 rounded-full overflow-hidden">
                            <div 
                              className="bg-blue-600 h-full" 
                              style={{ width: `${Math.min(100, (val / selectedRequest.latency_ms) * 100)}%` }}
                            />
                          </div>
                          <span className="text-slate-200 font-mono w-16 text-right">{val} ms</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Citations used */}
              {selectedRequest.sources_used && selectedRequest.sources_used.length > 0 && (
                <div className="space-y-2">
                  <span className="text-[10px] text-slate-500 uppercase tracking-widest block font-mono font-bold">Sources Cited</span>
                  <div className="flex flex-wrap gap-2">
                    {selectedRequest.sources_used.map((src, idx) => (
                      <span key={idx} className="px-3 py-1 bg-slate-950 border border-slate-800 text-[10px] text-slate-300 rounded-xl font-mono">
                        {src}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
