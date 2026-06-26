import { useState } from "react";
import { DashboardCard } from "../components/DashboardCard";
import { StatsCard } from "../components/StatsCard";
import {
  TrendingUp,
  Clock,
  Database,
  Layers,
  ArrowUpRight,
  RefreshCw,
} from "lucide-react";

export const AdminAnalyticsPage = () => {
  const [hoveredPoint, setHoveredPoint] = useState<number | null>(null);
  const [hoveredBar, setHoveredBar] = useState<number | null>(null);

  // 1. Mock Dataset for API Traffic (Weekly)
  const trafficData = [
    { day: "Mon", requests: 120, label: "Monday: 120 calls" },
    { day: "Tue", requests: 190, label: "Tuesday: 190 calls" },
    { day: "Wed", requests: 310, label: "Wednesday: 310 calls" },
    { day: "Thu", requests: 280, label: "Thursday: 280 calls" },
    { day: "Fri", requests: 420, label: "Friday: 420 calls" },
    { day: "Sat", requests: 250, label: "Saturday: 250 calls" },
    { day: "Sun", requests: 180, label: "Sunday: 180 calls" },
  ];

  // 2. Mock Dataset for Response Latency (Hourly)
  const latencyData = [
    { hour: "08:00", ms: 890 },
    { hour: "10:00", ms: 940 },
    { hour: "12:00", ms: 1210 },
    { hour: "14:00", ms: 820 },
    { hour: "16:00", ms: 750 },
    { hour: "18:00", ms: 990 },
    { hour: "20:00", ms: 810 },
  ];

  // 3. Document distribution breakdown
  const documentDistribution = [
    { type: "PDF Documents", count: 4, percent: 40, color: "bg-blue-500", svgColor: "#3b82f6" },
    { type: "JSON Sources", count: 5, percent: 50, color: "bg-emerald-500", svgColor: "#10b981" },
    { type: "TXT Files", count: 1, percent: 10, color: "bg-amber-500", svgColor: "#f59e0b" },
  ];

  // SVG dimensions & mapping for Line Chart
  const svgWidth = 550;
  const svgHeight = 220;
  const paddingX = 40;
  const paddingY = 30;

  const maxVal = Math.max(...trafficData.map((d) => d.requests)) * 1.1; // Add 10% breathing room
  const minVal = 0;

  const getX = (index: number) => {
    return paddingX + (index * (svgWidth - paddingX * 2)) / (trafficData.length - 1);
  };

  const getY = (value: number) => {
    return svgHeight - paddingY - ((value - minVal) * (svgHeight - paddingY * 2)) / (maxVal - minVal);
  };

  // Generate path coordinates
  const pathPoints = trafficData.map((d, i) => `${getX(i)},${getY(d.requests)}`);
  const linePath = `M ${pathPoints.join(" L ")}`;
  
  // Closed area path for background gradient fill
  const areaPath = `${linePath} L ${getX(trafficData.length - 1)},${svgHeight - paddingY} L ${getX(0)},${svgHeight - paddingY} Z`;

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-100 tracking-tight flex items-center gap-2">
            <span>Analytics Center</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Statistical operations, traffic reports, and service latency monitoring.
          </p>
        </div>

        <button
          onClick={() => {}}
          className="px-4 py-2 text-xs font-semibold bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300 hover:text-white rounded-xl transition-all cursor-pointer flex items-center gap-2 select-none"
        >
          <RefreshCw className="w-3 h-3" />
          <span>Refresh Metrics</span>
        </button>
      </div>

      {/* Overview stats cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <StatsCard
          title="Total API Calls (Weekly)"
          value="1,750"
          icon={TrendingUp}
          description="Inference operations count"
          trend={{ value: "+18% vs last week", isPositive: true }}
          colorClass="bg-blue-500/10 border-blue-500/20 text-blue-400"
          delay={0.05}
        />
        <StatsCard
          title="Avg Latency"
          value="915 ms"
          icon={Clock}
          description="Response inference time"
          trend={{ value: "-45ms optimization", isPositive: true }}
          colorClass="bg-emerald-500/10 border-emerald-500/20 text-emerald-400"
          delay={0.1}
        />
        <StatsCard
          title="Total Tokens Processed"
          value="48.5K"
          icon={Layers}
          description="Gemini token payload volume"
          colorClass="bg-amber-500/10 border-amber-500/20 text-amber-400"
          delay={0.15}
        />
      </div>

      {/* Interactive SVG Charts section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* SVG Line Chart: Weekly Traffic */}
        <DashboardCard
          title="API Request Volume"
          subtitle="Weekly traffic metrics to chatbot model endpoints"
        >
          <div className="w-full h-[250px] relative mt-2 overflow-x-auto custom-scrollbar select-none">
            <svg
              viewBox={`0 0 ${svgWidth} ${svgHeight}`}
              className="w-full h-full min-w-[500px]"
            >
              <defs>
                {/* Background area gradient fill */}
                <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.25" />
                  <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.0" />
                </linearGradient>
                {/* Glow border stroke gradient */}
                <linearGradient id="lineGrad" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor="#3b82f6" />
                  <stop offset="50%" stopColor="#6366f1" />
                  <stop offset="100%" stopColor="#8b5cf6" />
                </linearGradient>
              </defs>

              {/* Gridlines */}
              {Array.from({ length: 4 }).map((_, i) => {
                const yVal = getY(minVal + (i * (maxVal - minVal)) / 3);
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
              <path d={areaPath} fill="url(#areaGrad)" />

              {/* Glowing Line Stroke */}
              <path
                d={linePath}
                fill="none"
                stroke="url(#lineGrad)"
                strokeWidth="3.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />

              {/* Interactive Node Circles */}
              {trafficData.map((d, i) => (
                <circle
                  key={i}
                  cx={getX(i)}
                  cy={getY(d.requests)}
                  r={hoveredPoint === i ? 6 : 4}
                  fill={hoveredPoint === i ? "#ffffff" : "#3b82f6"}
                  stroke="#0f172a"
                  strokeWidth="2.5"
                  className="transition-all duration-150 cursor-pointer"
                  onMouseEnter={() => setHoveredPoint(i)}
                  onMouseLeave={() => setHoveredPoint(null)}
                />
              ))}

              {/* X Axis labels */}
              {trafficData.map((d, i) => (
                <text
                  key={i}
                  x={getX(i)}
                  y={svgHeight - 8}
                  fill="#94a3b8"
                  fontSize="10"
                  fontFamily="monospace"
                  textAnchor="middle"
                >
                  {d.day}
                </text>
              ))}
            </svg>

            {/* Hover Tooltip Overlay */}
            {hoveredPoint !== null && (
              <div className="absolute top-2 right-2 px-3 py-1.5 bg-slate-900 border border-blue-500/30 rounded-lg text-[10px] text-blue-400 font-semibold font-mono shadow-xl glow-blue transition-all">
                {trafficData[hoveredPoint].label}
              </div>
            )}
          </div>
        </DashboardCard>

        {/* SVG Bar Chart: Latency Monitoring */}
        <DashboardCard
          title="Hourly Response Latency"
          subtitle="Model inference average latency (milliseconds)"
        >
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
              {latencyData.map((d, i) => {
                const barWidth = 32;
                const xCoord = getX(i) - barWidth / 2;
                const maxBarVal = 1500;
                const barHeight = ((d.ms) / maxBarVal) * (svgHeight - paddingY * 2);
                const yCoord = svgHeight - paddingY - barHeight;

                const isHovered = hoveredBar === i;

                return (
                  <g key={i}>
                    {/* Glowing bar column */}
                    <rect
                      x={xCoord}
                      y={yCoord}
                      width={barWidth}
                      height={barHeight}
                      rx="6"
                      fill={isHovered ? "#10b981" : "rgba(16, 185, 129, 0.25)"}
                      stroke={isHovered ? "#34d399" : "rgba(16, 185, 129, 0.4)"}
                      strokeWidth="1.5"
                      className="transition-all duration-200 cursor-pointer"
                      onMouseEnter={() => setHoveredBar(i)}
                      onMouseLeave={() => setHoveredBar(null)}
                    />
                    {/* Time Label */}
                    <text
                      x={getX(i)}
                      y={svgHeight - 8}
                      fill="#94a3b8"
                      fontSize="9"
                      fontFamily="monospace"
                      textAnchor="middle"
                    >
                      {d.hour}
                    </text>
                  </g>
                );
              })}
            </svg>

            {/* Hover Tooltip Overlay */}
            {hoveredBar !== null && (
              <div className="absolute top-2 right-2 px-3 py-1.5 bg-slate-900 border border-emerald-500/30 rounded-lg text-[10px] text-emerald-400 font-semibold font-mono shadow-xl glow-emerald transition-all">
                {latencyData[hoveredBar].hour}: {latencyData[hoveredBar].ms} ms
              </div>
            )}
          </div>
        </DashboardCard>
      </div>

      {/* Bottom row: Document types donut chart & metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* SVG Donut Chart for Document Formats */}
        <DashboardCard
          title="Knowledge Distribution"
          subtitle="Proportion of files processed by type"
          className="lg:col-span-1"
        >
          <div className="flex flex-col items-center justify-center p-2 relative h-[240px]">
            <svg viewBox="0 0 100 100" className="w-36 h-36">
              <circle
                cx="50"
                cy="50"
                r="40"
                fill="transparent"
                stroke="rgba(255, 255, 255, 0.03)"
                strokeWidth="12"
              />
              {/* PDF Segment (40% starting at -90 deg) */}
              <circle
                cx="50"
                cy="50"
                r="40"
                fill="transparent"
                stroke="#3b82f6"
                strokeWidth="12"
                strokeDasharray={`${40 * 2.51} 251`}
                strokeDashoffset="0"
                transform="rotate(-90 50 50)"
              />
              {/* JSON Segment (50% starting at -90 deg + 40% = 54 deg) */}
              <circle
                cx="50"
                cy="50"
                r="40"
                fill="transparent"
                stroke="#10b981"
                strokeWidth="12"
                strokeDasharray={`${50 * 2.51} 251`}
                strokeDashoffset={`${-40 * 2.51}`}
                transform="rotate(-90 50 50)"
              />
              {/* TXT Segment (10% starting at -90 deg + 90% = 234 deg) */}
              <circle
                cx="50"
                cy="50"
                r="40"
                fill="transparent"
                stroke="#f59e0b"
                strokeWidth="12"
                strokeDasharray={`${10 * 2.51} 251`}
                strokeDashoffset={`${-90 * 2.51}`}
                transform="rotate(-90 50 50)"
              />
            </svg>

            {/* Legend breakdown list */}
            <div className="w-full mt-4 flex items-center justify-center gap-3 flex-wrap">
              {documentDistribution.map((doc) => (
                <div key={doc.type} className="flex items-center gap-1.5 text-[10px] text-slate-300">
                  <span className={`w-2.5 h-2.5 rounded-full ${doc.color}`} />
                  <span>{doc.percent}% {doc.type.split(" ")[0]}</span>
                </div>
              ))}
            </div>
          </div>
        </DashboardCard>

        {/* Detailed insights cards */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl border border-slate-800/40 relative overflow-hidden flex flex-col justify-between">
          <div className="absolute top-0 right-0 -mr-16 -mt-16 w-36 h-36 bg-blue-500/5 rounded-full blur-2xl pointer-events-none" />
          
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-slate-100 font-semibold text-sm">
              <Database className="w-4 h-4 text-blue-400" />
              <span>Indexing Infrastructure Health</span>
            </div>
            
            <p className="text-xs text-slate-400 leading-relaxed">
              The retrieval pipelines operate on top of a highly optimized vector dimension space using **BAAI/bge-small-en-v1.5** embeddings. Segment mappings are compiled correctly in a secure SQLite Chroma collection. Latency benchmarks demonstrate excellent query resolution of college notices and campus guidelines within sub-second metrics.
            </p>

            <div className="grid grid-cols-2 gap-4 pt-2">
              <div className="p-3 bg-slate-900/50 rounded-xl border border-slate-900/60">
                <span className="text-[10px] text-slate-500 block uppercase font-mono">Embedding Model</span>
                <span className="text-xs font-semibold text-slate-300 font-mono mt-0.5 block">BAAI/bge-small-en-v1.5</span>
              </div>
              <div className="p-3 bg-slate-900/50 rounded-xl border border-slate-900/60">
                <span className="text-[10px] text-slate-500 block uppercase font-mono">Vector Database</span>
                <span className="text-xs font-semibold text-slate-300 font-mono mt-0.5 block">ChromaDB Persistent</span>
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between text-xs pt-4 mt-4 border-t border-slate-900/60">
            <span className="text-slate-400">Next planned indexing update:</span>
            <span className="font-semibold text-slate-300 flex items-center gap-1">
              <span>Automatic trigger</span>
              <ArrowUpRight className="w-3 h-3 text-slate-400" />
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
