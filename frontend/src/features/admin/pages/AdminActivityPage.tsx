import { useState, useEffect } from "react";
import adminApi from "../services/api";
import { ActivityTimeline } from "../components/ActivityTimeline";
import { SearchBar } from "../components/SearchBar";
import { ListSkeleton } from "../components/LoadingSkeleton";
import { EmptyState } from "../components/EmptyState";
import { Clock, RefreshCw } from "lucide-react";

export const AdminActivityPage = () => {
  const [activities, setActivities] = useState<any[]>([]);
  const [filteredActivities, setFilteredActivities] = useState<any[]>([]);
  const [searchValue, setSearchValue] = useState("");
  const [loading, setLoading] = useState(true);

  const fetchActivities = async () => {
    setLoading(true);
    try {
      const response = await adminApi.get("/api/admin/activity");
      setActivities(response.data.logs || []);
    } catch (e) {
      console.error("Failed to load activity logs", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchActivities();
  }, []);

  useEffect(() => {
    if (!searchValue.trim()) {
      setFilteredActivities(activities);
      return;
    }
    const q = searchValue.toLowerCase();
    const filtered = activities.filter(
      (act) =>
        act.action.toLowerCase().includes(q) ||
        act.username.toLowerCase().includes(q) ||
        (act.details && JSON.stringify(act.details).toLowerCase().includes(q))
    );
    setFilteredActivities(filtered);
  }, [activities, searchValue]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-100 tracking-tight flex items-center gap-2">
            <span>Audit Activity Logs</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Historical trace of admin actions and model queries recorded on-disk.
          </p>
        </div>

        <button
          onClick={fetchActivities}
          className="px-4 py-2 text-xs font-semibold bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300 hover:text-white rounded-xl transition-all cursor-pointer flex items-center gap-2 select-none"
        >
          <RefreshCw className="w-3 h-3" />
          <span>Refresh Audit Logs</span>
        </button>
      </div>

      {/* Toolbar filters */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 bg-slate-900/40 rounded-2xl border border-slate-800/40">
        <div className="w-full sm:w-80">
          <SearchBar
            value={searchValue}
            onChange={setSearchValue}
            placeholder="Search action, user, details..."
          />
        </div>

        <div className="flex items-center gap-2 text-xs text-slate-400">
          <Clock className="w-4 h-4 text-slate-500" />
          <span>Showing {filteredActivities.length} total events</span>
        </div>
      </div>

      {/* Timeline section */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800/40 relative overflow-hidden">
        {loading ? (
          <ListSkeleton items={4} />
        ) : filteredActivities.length === 0 ? (
          <EmptyState
            title="No activity matches search"
            description="Adjust search queries to display actions list"
            onAction={() => setSearchValue("")}
            actionLabel="Reset Search"
          />
        ) : (
          <div className="pt-2 max-w-2xl">
            <ActivityTimeline activities={filteredActivities} limit={100} />
          </div>
        )}
      </div>
    </div>
  );
};
