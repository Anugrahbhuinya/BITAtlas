// src/features/navigation/components/GraphStatistics.tsx

import React, { useState } from "react";
import { Database, Share2, AlertTriangle, CheckCircle, RefreshCw, Compass, ShieldAlert, Cpu } from "lucide-react";
import type { GraphSummary, GraphNode } from "../types";
import { navigationApi } from "../services/navigationApi";

interface GraphStatisticsProps {
  summary: GraphSummary | null;
  loading: boolean;
  onRebuild: () => void;
  rebuilding: boolean;
  allNodes?: GraphNode[];
}

export const GraphStatistics: React.FC<GraphStatisticsProps> = ({
  summary,
  loading,
  onRebuild,
  rebuilding,
  allNodes = []
}) => {
  const [testStartId, setTestStartId] = useState("");
  const [testDestId, setTestDestId] = useState("");
  const [benchmarkResult, setBenchmarkResult] = useState<{
    timeMs: number;
    distance: number;
    instructionsCount: number;
    accessible: boolean;
    error?: string;
  } | null>(null);
  const [runningBenchmark, setRunningBenchmark] = useState(false);

  if (loading && !summary) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <RefreshCw className="w-8 h-8 text-primary animate-spin mb-3" />
        <p className="text-sm text-on-surface/65 font-medium">Loading graph statistics...</p>
      </div>
    );
  }

  if (!summary) {
    return (
      <div className="text-center py-8 text-on-surface/50 font-medium">
        Failed to load graph summary.
      </div>
    );
  }

  const handleRunBenchmark = async () => {
    if (!testStartId || !testDestId) return;
    setRunningBenchmark(true);
    setBenchmarkResult(null);
    const startTime = performance.now();
    try {
      const res = await navigationApi.calculateRoute(testStartId, testDestId, "shortest");
      const endTime = performance.now();
      setBenchmarkResult({
        timeMs: Math.round(endTime - startTime),
        distance: res.total_distance,
        instructionsCount: res.navigation_instructions.length,
        accessible: res.accessibility_information
      });
    } catch (e: any) {
      setBenchmarkResult({
        timeMs: Math.round(performance.now() - startTime),
        distance: 0,
        instructionsCount: 0,
        accessible: false,
        error: e.response?.data?.detail || "Locations are disconnected."
      });
    } finally {
      setRunningBenchmark(false);
    }
  };

  return (
    <div className="space-y-6 text-left">
      {/* Rebuild Trigger Section */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-surface-variant/15 p-4 rounded-2xl border border-outline-variant/30">
        <div>
          <h4 className="text-sm font-bold text-on-surface">Graph Sync Status</h4>
          <p className="text-xs text-on-surface/60">
            Rebuild the graph to sync latest coordinate details, room additions, or pathway linkages.
          </p>
        </div>
        <button
          onClick={onRebuild}
          disabled={rebuilding}
          className="flex items-center gap-2 px-4 py-2 bg-primary hover:bg-primary/90 text-background rounded-xl font-bold text-xs shadow-md transition disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${rebuilding ? "animate-spin" : ""}`} />
          {rebuilding ? "Rebuilding Graph..." : "Rebuild Graph"}
        </button>
      </div>

      {/* Primary Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Node Count */}
        <div className="bg-surface border border-outline-variant/45 p-4 rounded-2xl flex items-center gap-4 shadow-sm hover:shadow transition">
          <div className="p-3 bg-primary/10 rounded-xl text-primary">
            <Database className="w-6 h-6" />
          </div>
          <div>
            <p className="text-[10px] uppercase font-bold text-on-surface/55 tracking-wider">Total Nodes</p>
            <p className="text-2xl font-black text-on-surface mt-0.5">{summary.total_nodes}</p>
          </div>
        </div>

        {/* Edge Count */}
        <div className="bg-surface border border-outline-variant/45 p-4 rounded-2xl flex items-center gap-4 shadow-sm hover:shadow transition">
          <div className="p-3 bg-secondary/10 rounded-xl text-secondary">
            <Share2 className="w-6 h-6" />
          </div>
          <div>
            <p className="text-[10px] uppercase font-bold text-on-surface/55 tracking-wider">Total Edges</p>
            <p className="text-2xl font-black text-on-surface mt-0.5">{summary.total_edges}</p>
          </div>
        </div>

        {/* Graph Health */}
        <div className="bg-surface border border-outline-variant/45 p-4 rounded-2xl flex items-center gap-4 shadow-sm hover:shadow transition">
          <div className={`p-3 rounded-xl ${summary.is_valid ? "bg-success/15 text-success" : "bg-error/15 text-error"}`}>
            {summary.is_valid ? <CheckCircle className="w-6 h-6" /> : <AlertTriangle className="w-6 h-6" />}
          </div>
          <div>
            <p className="text-[10px] uppercase font-bold text-on-surface/55 tracking-wider">Graph Health</p>
            <p className={`text-md font-extrabold mt-1 ${summary.is_valid ? "text-success" : "text-error"}`}>
              {summary.is_valid ? "Healthy & Consistent" : "Requires Validation"}
            </p>
          </div>
        </div>
      </div>

      {/* Detailed Type Breakdowns */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Node Types list */}
        <div className="bg-surface border border-outline-variant/45 rounded-2xl p-5 shadow-sm">
          <h5 className="font-extrabold text-sm mb-3.5 text-on-surface flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-primary" />
            Nodes by Category
          </h5>
          <div className="space-y-2.5">
            {Object.entries(summary.node_type_counts).map(([type, count]) => (
              <div key={type} className="flex justify-between items-center text-xs border-b border-outline-variant/20 pb-2">
                <span className="font-semibold text-on-surface/75">{type}</span>
                <span className="bg-surface-variant px-2.5 py-0.5 rounded-full font-bold text-on-surface-variant">
                  {count}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Edge Relationships list */}
        <div className="bg-surface border border-outline-variant/45 rounded-2xl p-5 shadow-sm">
          <h5 className="font-extrabold text-sm mb-3.5 text-on-surface flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-secondary" />
            Edges by Relationship
          </h5>
          <div className="space-y-2.5">
            {Object.entries(summary.edge_relationship_counts).map(([rel, count]) => (
              <div key={rel} className="flex justify-between items-center text-xs border-b border-outline-variant/20 pb-2">
                <span className="font-semibold text-on-surface/75 font-mono">{rel}</span>
                <span className="bg-secondary/10 px-2.5 py-0.5 rounded-full font-bold text-secondary">
                  {count}
                </span>
              </div>
            ))}
            {Object.keys(summary.edge_relationship_counts).length === 0 && (
              <p className="text-xs text-on-surface/40 text-center py-6">No edge relationships found.</p>
            )}
          </div>
        </div>
      </div>

      {/* Routing Performance & Diagnostics */}
      {allNodes.length > 0 && (
        <div className="bg-surface border border-outline-variant/45 rounded-2xl p-5 shadow-sm space-y-4">
          <h5 className="font-extrabold text-sm text-on-surface flex items-center gap-2">
            <Cpu className="w-5 h-5 text-primary" />
            Routing Diagnostics & Performance Analyzer
          </h5>
          <p className="text-xs text-on-surface/60">
            Verify graph connectivity and Dijkstra calculation latencies. Select two locations to calculate a path.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 items-end">
            <div className="space-y-1">
              <label className="text-[10px] font-bold text-on-surface/50 uppercase tracking-wider block">Start Node</label>
              <select
                value={testStartId}
                onChange={(e) => setTestStartId(e.target.value)}
                className="w-full p-2.5 bg-surface border border-outline-variant rounded-xl text-xs"
              >
                <option value="">-- Select Start Node --</option>
                {allNodes.map(n => <option key={n.id} value={n.id}>{n.name} ({n.type})</option>)}
              </select>
            </div>

            <div className="space-y-1">
              <label className="text-[10px] font-bold text-on-surface/50 uppercase tracking-wider block">Destination Node</label>
              <select
                value={testDestId}
                onChange={(e) => setTestDestId(e.target.value)}
                className="w-full p-2.5 bg-surface border border-outline-variant rounded-xl text-xs"
              >
                <option value="">-- Select Destination --</option>
                {allNodes.map(n => <option key={n.id} value={n.id}>{n.name} ({n.type})</option>)}
              </select>
            </div>

            <button
              onClick={handleRunBenchmark}
              disabled={runningBenchmark || !testStartId || !testDestId}
              className="py-2.5 bg-primary text-background hover:bg-primary/95 text-xs font-black rounded-xl shadow-md transition disabled:opacity-40"
            >
              {runningBenchmark ? "Calculating..." : "Run Connectivity Test"}
            </button>
          </div>

          {/* Benchmark output */}
          {benchmarkResult && (
            <div className={`p-4 rounded-xl border flex items-start gap-3 text-xs leading-normal font-semibold ${
              benchmarkResult.error 
                ? "bg-error/5 border-error/25 text-error" 
                : "bg-emerald-500/5 border-emerald-500/25 text-emerald-500"
            }`}>
              <ShieldAlert className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <div className="space-y-1">
                <p className="font-extrabold uppercase text-[10px] tracking-wider">Diagnostic Results</p>
                {benchmarkResult.error ? (
                  <p>Pathfinding Failed: {benchmarkResult.error} (Calculated in {benchmarkResult.timeMs}ms)</p>
                ) : (
                  <div className="space-y-0.5 text-on-surface">
                    <p className="text-emerald-500">✓ Graph is connected between selected locations.</p>
                    <p className="text-on-surface/70">Distance: {benchmarkResult.distance.toFixed(1)}m | Instructions: {benchmarkResult.instructionsCount} steps</p>
                    <p className="text-on-surface/70">Calculated in: <span className="font-bold text-primary">{benchmarkResult.timeMs} ms</span></p>
                    <p className="text-on-surface/70">Wheelchair Accessible: {benchmarkResult.accessible ? "Yes" : "No (contains stairs/unpaved paths)"}</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
export default GraphStatistics;
