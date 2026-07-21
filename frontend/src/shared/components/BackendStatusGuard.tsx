import React, { useEffect, useState } from "react";
import { API_BASE_URL, WS_BASE_URL, APP_ENV } from "../../config";
import { AlertCircle, RefreshCw, Terminal, CheckCircle2 } from "lucide-react";

interface BackendStatusGuardProps {
  children: React.ReactNode;
}

export const BackendStatusGuard: React.FC<BackendStatusGuardProps> = ({ children }) => {
  const [checking, setChecking] = useState(true);
  const [isReachable, setIsReachable] = useState<boolean | null>(null);
  const [errorDetails, setErrorDetails] = useState<string | null>(null);

  const verifyBackend = async () => {
    setChecking(true);
    try {
      const response = await fetch(`${API_BASE_URL}/health`, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      });
      if (response.ok) {
        setIsReachable(true);
        setErrorDetails(null);
      } else {
        setIsReachable(false);
        setErrorDetails(`Received status code ${response.status} from health check.`);
      }
    } catch (err: any) {
      setIsReachable(false);
      setErrorDetails(err.message || "Network connection refused.");
    } finally {
      setChecking(false);
    }
  };

  useEffect(() => {
    verifyBackend();
  }, []);

  if (checking) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center text-slate-100 font-sans p-6">
        <div className="relative flex flex-col items-center">
          <RefreshCw className="w-12 h-12 text-blue-500 animate-spin mb-4" />
          <p className="text-sm font-mono tracking-widest uppercase text-slate-400">
            Checking System Environment...
          </p>
        </div>
      </div>
    );
  }

  if (isReachable === false) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center text-slate-100 font-sans p-6">
        {/* Decorative background glow */}
        <div className="absolute top-1/4 left-1/4 w-[400px] h-[400px] bg-red-950/20 rounded-full blur-[120px] pointer-events-none" />
        <div className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] bg-amber-950/10 rounded-full blur-[120px] pointer-events-none" />

        <div className="relative max-w-xl w-full bg-slate-900/60 backdrop-blur-xl border border-red-500/20 rounded-3xl p-8 shadow-2xl shadow-red-950/20 flex flex-col">
          {/* Header */}
          <div className="flex items-center gap-4 mb-6">
            <div className="w-12 h-12 rounded-2xl bg-red-950/40 border border-red-500/30 flex items-center justify-center text-red-400 shrink-0">
              <AlertCircle className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-red-200">
                Backend Connection Failed
              </h1>
              <p className="text-xs text-slate-400 mt-0.5">
                The BITATLAS Operating System could not reach the backend server.
              </p>
            </div>
          </div>

          {/* Environmental parameters */}
          <div className="bg-slate-950/60 border border-slate-800 rounded-2xl p-5 mb-6 flex flex-col gap-3 font-mono text-xs text-slate-300">
            <div className="flex justify-between items-center border-b border-slate-900 pb-2">
              <span className="text-slate-500">API URL:</span>
              <span className="text-slate-200">{API_BASE_URL}</span>
            </div>
            <div className="flex justify-between items-center border-b border-slate-900 pb-2">
              <span className="text-slate-500">WS URL:</span>
              <span className="text-slate-200">{WS_BASE_URL}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-500">Environment:</span>
              <span className="text-slate-200 uppercase tracking-wider">{APP_ENV}</span>
            </div>
          </div>

          {/* Diagnostic status */}
          <div className="mb-6">
            <h2 className="text-xs font-mono uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-2">
              <Terminal className="w-3.5 h-3.5 text-slate-400" />
              Diagnostics Log
            </h2>
            <div className="bg-slate-950/80 rounded-2xl p-4 border border-slate-800 font-mono text-xs text-red-400 max-h-[80px] overflow-y-auto">
              [CRITICAL] {errorDetails || "Connection refused by the host."}
            </div>
          </div>

          {/* Troubleshooting recommendations */}
          <div className="mb-8">
            <h3 className="text-xs font-mono uppercase tracking-wider text-slate-400 mb-3">
              Troubleshooting Recommendations
            </h3>
            <ul className="text-sm text-slate-300 space-y-3.5 leading-relaxed">
              <li className="flex gap-3">
                <span className="w-5 h-5 rounded-full bg-slate-800 flex items-center justify-center text-xs shrink-0 text-slate-400">1</span>
                <span>
                  Check if the backend server is running on port <strong className="text-slate-100">8001</strong>. Run the following command in the <code>backend/</code> directory:
                  <div className="bg-slate-950/80 rounded-lg p-2.5 border border-slate-800 text-xs font-mono mt-2 text-slate-200 select-all cursor-pointer">
                    uvicorn app.main:app --reload --port 8001
                  </div>
                </span>
              </li>
              <li className="flex gap-3">
                <span className="w-5 h-5 rounded-full bg-slate-800 flex items-center justify-center text-xs shrink-0 text-slate-400">2</span>
                <span>Verify that CORS in <code>backend/.env</code> allows connections from origin <code>http://localhost:5180</code>.</span>
              </li>
              <li className="flex gap-3">
                <span className="w-5 h-5 rounded-full bg-slate-800 flex items-center justify-center text-xs shrink-0 text-slate-400">3</span>
                <span>Ensure there are no conflicting processes (such as Docker containers or other projects) using ports 5180 or 8001.</span>
              </li>
            </ul>
          </div>

          {/* Retest Trigger */}
          <button
            onClick={verifyBackend}
            className="w-full py-3.5 bg-red-600/90 hover:bg-red-500 text-white rounded-2xl font-medium transition-all shadow-lg shadow-red-950/30 hover:shadow-red-500/20 active:scale-[0.98] cursor-pointer flex items-center justify-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Retry Connection Check
          </button>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};

export default BackendStatusGuard;
