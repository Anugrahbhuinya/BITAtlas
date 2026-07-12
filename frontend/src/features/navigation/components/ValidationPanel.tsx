// src/features/navigation/components/ValidationPanel.tsx

import React, { useState } from "react";
import { AlertCircle, AlertTriangle, CheckCircle2, ShieldAlert, Filter } from "lucide-react";
import type { GraphValidationReport, GraphValidationError } from "../types";

interface ValidationPanelProps {
  report: GraphValidationReport | null;
  loading: boolean;
}

export const ValidationPanel: React.FC<ValidationPanelProps> = ({ report, loading }) => {
  const [severityFilter, setSeverityFilter] = useState<"ALL" | "ERROR" | "WARNING">("ALL");

  if (loading && !report) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-4 border-primary border-t-transparent mb-3" />
        <p className="text-sm text-on-surface/65 font-medium">Running graph integrity checks...</p>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="text-center py-8 text-on-surface/50 font-medium">
        Failed to fetch validation details.
      </div>
    );
  }

  const filteredErrors = report.errors.filter((err) => {
    if (severityFilter === "ALL") return true;
    return err.severity === severityFilter;
  });

  return (
    <div className="space-y-6">
      {/* Overview Card */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        {/* Validation Status */}
        <div className={`p-4 rounded-2xl border flex items-center gap-3.5 ${
          report.is_valid 
            ? "bg-success/10 border-success/35 text-success" 
            : "bg-error/10 border-error/35 text-error"
        }`}>
          {report.is_valid ? (
            <CheckCircle2 className="w-8 h-8 flex-shrink-0" />
          ) : (
            <ShieldAlert className="w-8 h-8 flex-shrink-0" />
          )}
          <div>
            <h4 className="text-xs uppercase font-bold tracking-wider opacity-75">Integrity Status</h4>
            <p className="text-md font-extrabold mt-0.5">
              {report.is_valid ? "Passes Validation" : "Integrity Failure"}
            </p>
          </div>
        </div>

        {/* Error Count */}
        <div className="bg-surface border border-outline-variant/45 p-4 rounded-2xl flex items-center gap-3.5">
          <div className="p-2.5 bg-error/10 text-error rounded-xl">
            <AlertCircle className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-xs uppercase font-bold tracking-wider text-on-surface/55">Total Errors</h4>
            <p className="text-xl font-black text-on-surface mt-0.5">{report.total_errors}</p>
          </div>
        </div>

        {/* Warning Count */}
        <div className="bg-surface border border-outline-variant/45 p-4 rounded-2xl flex items-center gap-3.5">
          <div className="p-2.5 bg-warning/10 text-warning rounded-xl">
            <AlertTriangle className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-xs uppercase font-bold tracking-wider text-on-surface/55">Total Warnings</h4>
            <p className="text-xl font-black text-on-surface mt-0.5">{report.total_warnings}</p>
          </div>
        </div>
      </div>

      {/* Filter and Details List */}
      <div className="bg-surface border border-outline-variant/45 rounded-2xl p-5 shadow-sm">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 border-b border-outline-variant/20 pb-4 mb-4">
          <h4 className="font-extrabold text-sm text-on-surface">Validation Log Details</h4>
          <div className="flex items-center gap-2">
            <Filter className="w-3.5 h-3.5 text-on-surface/50" />
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value as any)}
              className="p-1.5 bg-surface border border-outline-variant rounded-xl text-xs"
            >
              <option value="ALL">All Severities</option>
              <option value="ERROR">Errors Only</option>
              <option value="WARNING">Warnings Only</option>
            </select>
          </div>
        </div>

        {/* List of Validation Issues */}
        <div className="space-y-3.5 max-h-[400px] overflow-y-auto pr-1">
          {filteredErrors.map((err, idx) => (
            <div
              key={idx}
              className={`p-3.5 rounded-xl border flex items-start gap-3 text-xs transition ${
                err.severity === "ERROR"
                  ? "bg-error/5 border-error/25 hover:bg-error/10"
                  : "bg-warning/5 border-warning/25 hover:bg-warning/10"
              }`}
            >
              {err.severity === "ERROR" ? (
                <AlertCircle className="w-4 h-4 text-error flex-shrink-0 mt-0.5" />
              ) : (
                <AlertTriangle className="w-4 h-4 text-warning flex-shrink-0 mt-0.5" />
              )}
              <div className="flex-1 space-y-1">
                <div className="flex flex-wrap items-center gap-2">
                  <span className={`px-2 py-0.5 rounded font-black text-[9px] uppercase ${
                    err.severity === "ERROR" ? "bg-error/15 text-error" : "bg-warning/15 text-warning"
                  }`}>
                    {err.severity}
                  </span>
                  <span className="font-bold text-on-surface/85 capitalize font-mono text-[10px]">
                    Category: {err.type.replace("_", " ")}
                  </span>
                </div>
                <p className="text-on-surface/75 leading-relaxed font-semibold">{err.message}</p>
                {Object.keys(err.details).length > 0 && (
                  <div className="bg-surface/55 p-2 rounded-lg border border-outline-variant/30 mt-2 font-mono text-[10px] text-on-surface/60 max-w-full overflow-x-auto">
                    {JSON.stringify(err.details, null, 2)}
                  </div>
                )}
              </div>
            </div>
          ))}

          {filteredErrors.length === 0 && (
            <div className="text-center py-12 text-on-surface/40 font-medium">
              <CheckCircle2 className="w-8 h-8 text-success/75 mx-auto mb-2.5" />
              No issues detected for the selected filter!
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
