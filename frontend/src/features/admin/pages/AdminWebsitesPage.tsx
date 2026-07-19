import { useState, useEffect } from "react";
import adminApi from "../services/api";
import { ConfirmationDialog } from "../components/ConfirmationDialog";
import { TableSkeleton } from "../components/LoadingSkeleton";
import { EmptyState } from "../components/EmptyState";
import { SearchBar } from "../components/SearchBar";
import { useAdminStore } from "../hooks/adminStore";
import { Globe, Trash2, Eye, RefreshCw, Plus, ExternalLink, Filter, SortAsc, Calendar, FileText, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export const AdminWebsitesPage = () => {
  const { showToast } = useAdminStore();
  const [websites, setWebsites] = useState<any[]>([]);
  const [filteredWebsites, setFilteredWebsites] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Sync Stats states
  const [stats, setStats] = useState<any>({
    indexed_websites: 0,
    healthy_websites: 0,
    pending_updates: 0,
    failed_websites: 0,
    today_crawls: 0,
    today_updates: 0,
    avg_crawl_time_ms: 0,
    avg_chunk_count: 0
  });
  const [syncingSiteId, setSyncingSiteId] = useState<string | null>(null);
  const [bulkSyncing, setBulkSyncing] = useState(false);

  // Filter and Sorting states
  const [searchValue, setSearchValue] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [sortBy, setSortBy] = useState("indexed_desc");

  // Dialog Modals states
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [urlInput, setUrlInput] = useState("");
  const [submittingUrl, setSubmittingUrl] = useState(false);

  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [selectedSite, setSelectedSite] = useState<any>(null);

  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [siteToDelete, setSiteToDelete] = useState<any>(null);

  const [reindexDialogOpen, setReindexDialogOpen] = useState(false);
  const [siteToReindex, setSiteToReindex] = useState<any>(null);
  const [reindexingState, setReindexingState] = useState<string | null>(null); // "loading" | null

  // Pagination states
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5;

  const fetchWebsites = async () => {
    setLoading(true);
    try {
      const [websitesResponse, statsResponse] = await Promise.all([
        adminApi.get("/api/admin/websites"),
        adminApi.get("/api/admin/websites/stats")
      ]);
      setWebsites(websitesResponse.data.websites || []);
      setStats(statsResponse.data);
    } catch (e) {
      console.error("Failed to load websites list", e);
      showToast("Failed to load websites list", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleToggleSync = async (siteId: string, currentVal: boolean) => {
    try {
      await adminApi.post(`/api/admin/websites/${siteId}/toggle-sync`, {
        sync_enabled: !currentVal
      });
      showToast(`Auto sync ${!currentVal ? "enabled" : "disabled"}`, "info");
      setWebsites(prev => prev.map(w => (w.id === siteId || w._id === siteId) ? { ...w, sync_enabled: !currentVal } : w));
      // Refresh stats
      const statsResponse = await adminApi.get("/api/admin/websites/stats");
      setStats(statsResponse.data);
    } catch (e: any) {
      console.error(e);
      showToast(`Failed to toggle auto-sync: ${e.response?.data?.detail || e.message}`, "error");
    }
  };

  const handleManualSync = async (siteId: string, url: string) => {
    setSyncingSiteId(siteId);
    showToast(`Checking for updates on ${url}...`, "info");
    try {
      const response = await adminApi.post(`/api/admin/websites/${siteId}/sync`);
      const msg = typeof response.data === "string" ? response.data : response.data.message || "Synchronization completed.";
      showToast(msg, "success");
      await fetchWebsites();
    } catch (e: any) {
      console.error(e);
      showToast(`Sync failed: ${e.response?.data?.detail || e.message}`, "error");
    } finally {
      setSyncingSiteId(null);
    }
  };

  const handleSyncAll = async () => {
    setBulkSyncing(true);
    showToast("Starting synchronization check for all websites...", "info");
    try {
      const response = await adminApi.post("/api/admin/websites/sync-all");
      const { checked, updated, unchanged, failed, duration } = response.data;
      showToast(
        `Checked ${checked} sites. Updated: ${updated}, Unchanged: ${unchanged}, Failed: ${failed}. Duration: ${duration}`,
        "success"
      );
      await fetchWebsites();
    } catch (e: any) {
      console.error(e);
      showToast(`Bulk sync check failed: ${e.response?.data?.detail || e.message}`, "error");
    } finally {
      setBulkSyncing(false);
    }
  };

  useEffect(() => {
    fetchWebsites();
  }, []);

  // Filter & sort logic
  useEffect(() => {
    let result = [...websites];

    // 1. Text Search Filter
    if (searchValue.trim()) {
      const q = searchValue.toLowerCase();
      result = result.filter(
        (site) =>
          site.title?.toLowerCase().includes(q) ||
          site.url?.toLowerCase().includes(q) ||
          site.domain?.toLowerCase().includes(q)
      );
    }

    // 2. Status Filter (Healthy, Pending, Failed, Disabled)
    if (statusFilter !== "all") {
      if (statusFilter === "disabled") {
        result = result.filter((site) => site.sync_enabled === false);
      } else {
        result = result.filter((site) => site.sync_enabled === true && site.sync_status?.toLowerCase() === statusFilter.toLowerCase());
      }
    }

    // 3. Sorting
    result.sort((a, b) => {
      if (sortBy === "indexed_desc") {
        return new Date(b.indexed_at).getTime() - new Date(a.indexed_at).getTime();
      }
      if (sortBy === "indexed_asc") {
        return new Date(a.indexed_at).getTime() - new Date(b.indexed_at).getTime();
      }
      if (sortBy === "title_asc") {
        return (a.title || "").localeCompare(b.title || "");
      }
      if (sortBy === "words_desc") {
        return b.word_count - a.word_count;
      }
      return 0;
    });

    setFilteredWebsites(result);
    setCurrentPage(1); // Reset page on filter/sort change
  }, [websites, searchValue, statusFilter, sortBy]);

  // Client-side URL Validator
  const isValidHttpUrl = (str: string) => {
    let url;
    try {
      url = new URL(str);
    } catch (_) {
      return false;
    }
    return url.protocol === "http:" || url.protocol === "https:";
  };

  const handleAddWebsite = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanUrl = urlInput.trim();
    if (!cleanUrl) {
      showToast("Please enter a URL.", "error");
      return;
    }
    if (!isValidHttpUrl(cleanUrl)) {
      showToast("Please enter a valid URL starting with http:// or https://", "error");
      return;
    }

    setSubmittingUrl(true);
    try {
      const response = await adminApi.post("/api/admin/websites", { url: cleanUrl });
      
      if (response.data.status === "Duplicate") {
        showToast(response.data.message || "This content is already indexed.", "info");
      } else if (response.data.status === "Completed") {
        showToast(`Successfully indexed: ${response.data.title || cleanUrl}`, "success");
      } else {
        showToast(response.data.message || "Ingestion complete.", "info");
      }

      setUrlInput("");
      setAddDialogOpen(false);
      fetchWebsites();
    } catch (err: any) {
      console.error("Failed to add website", err);
      const detail = err.response?.data?.detail || "An error occurred during indexing.";
      showToast(detail, "error");
    } finally {
      setSubmittingUrl(false);
    }
  };

  const handleDelete = async (purge: boolean) => {
    if (!siteToDelete) return;
    const siteId = siteToDelete.id || siteToDelete._id;
    console.log("[DEV DEBUG] Delete Trace: Delete handler receives siteToDelete ID:", siteId, "purge:", purge);
    console.log("[DEV DEBUG] Delete Trace: DELETE URL:", `/api/admin/websites/${siteId}?purge=${purge}`);
    try {
      await adminApi.delete(`/api/admin/websites/${siteId}?purge=${purge}`);
      if (purge) {
        showToast(`Website "${siteToDelete.title}" and its vectors purged successfully.`, "success");
      } else {
        showToast(`Website "${siteToDelete.title}" metadata deleted. Content preserved.`, "success");
      }
      fetchWebsites();
    } catch (e: any) {
      console.error("Failed to delete website", e);
      const detail = e.response?.data?.detail || "Failed to delete website.";
      showToast(detail, "error");
    } finally {
      setSiteToDelete(null);
      setDeleteDialogOpen(false);
    }
  };

  const handleReindexConfirm = async () => {
    if (!siteToReindex) return;
    setReindexingState("loading");
    try {
      const siteId = siteToReindex.id || siteToReindex?._id || (siteToReindex as any)._id;
      const response = await adminApi.post(`/api/admin/websites/${siteId}/reindex`);
      if (response.data.status === "Duplicate") {
        showToast("Reindexing complete: Content has not changed.", "info");
      } else {
        showToast(`Successfully re-indexed: ${response.data.title || siteToReindex.title}`, "success");
      }
      fetchWebsites();
    } catch (e: any) {
      console.error("Failed to reindex website", e);
      const detail = e.response?.data?.detail || "Failed to reindex website.";
      showToast(detail, "error");
    } finally {
      setSiteToReindex(null);
      setReindexingState(null);
      setReindexDialogOpen(false);
    }
  };

  // Pagination Helper
  const totalPages = Math.ceil(filteredWebsites.length / itemsPerPage);
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = filteredWebsites.slice(indexOfFirstItem, indexOfLastItem);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
            <Globe className="w-6 h-6 text-blue-500" />
            Website Knowledge Ingestion
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Ingest, schedule, and synchronize web pages directly into the assistant's retrieval memory bank.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleSyncAll}
            disabled={bulkSyncing}
            className="px-4 py-2.5 text-xs font-semibold bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300 hover:text-white rounded-xl transition-all cursor-pointer flex items-center gap-2 select-none disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${bulkSyncing ? "animate-spin" : ""}`} />
            <span>{bulkSyncing ? "Syncing All..." : "Sync All Pages"}</span>
          </button>
          
          <button
            onClick={() => setAddDialogOpen(true)}
            className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl shadow-lg shadow-blue-600/10 hover:shadow-blue-500/20 font-semibold text-sm transition-all cursor-pointer w-fit sm:w-auto"
          >
            <Plus className="w-4 h-4" />
            <span>Index New Page</span>
          </button>
        </div>
      </div>

      {/* Sync Stats Dashboard Cards */}
      {!loading && stats && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="glass-panel p-4 rounded-xl border border-slate-800/40 relative overflow-hidden flex flex-col justify-between">
            <div>
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Indexed Web Pages</span>
              <h3 className="text-xl font-bold text-slate-200 mt-1">{stats.indexed_websites || 0}</h3>
            </div>
            <p className="text-[10px] text-slate-400 mt-2">Avg: {stats.avg_chunk_count || 0} chunks/page</p>
          </div>

          <div className="glass-panel p-4 rounded-xl border border-slate-800/40 relative overflow-hidden flex flex-col justify-between">
            <div>
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Healthy / Online</span>
              <h3 className="text-xl font-bold text-emerald-400 mt-1">{stats.healthy_websites || 0}</h3>
            </div>
            <p className="text-[10px] text-slate-400 mt-2">Pending sync checks: {stats.pending_updates || 0}</p>
          </div>

          <div className="glass-panel p-4 rounded-xl border border-slate-800/40 relative overflow-hidden flex flex-col justify-between">
            <div>
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Sync Failures</span>
              <h3 className="text-xl font-bold text-rose-400 mt-1">{stats.failed_websites || 0}</h3>
            </div>
            <p className="text-[10px] text-slate-400 mt-2">Connection/crawler errors</p>
          </div>

          <div className="glass-panel p-4 rounded-xl border border-slate-800/40 relative overflow-hidden flex flex-col justify-between">
            <div>
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Checks Run (Today)</span>
              <h3 className="text-xl font-bold text-indigo-400 mt-1">{stats.today_crawls || 0}</h3>
            </div>
            <p className="text-[10px] text-slate-400 mt-2">{stats.today_updates || 0} updates applied. Avg: {((stats.avg_crawl_time_ms || 0)/1000).toFixed(1)}s</p>
          </div>
        </div>
      )}

      {/* Toolbar - Search, Sort, Filters */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 p-4 bg-slate-900/40 rounded-2xl border border-slate-800/40">
        <div className="w-full lg:w-80">
          <SearchBar
            value={searchValue}
            onChange={setSearchValue}
            placeholder="Search by title, URL or domain..."
          />
        </div>
        <div className="flex flex-wrap items-center gap-3">
          {/* Status filter */}
          <div className="flex items-center gap-2">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="text-xs bg-slate-950 border border-slate-800 text-slate-300 rounded-xl px-3 py-2.5 focus:outline-none focus:border-blue-500/60 cursor-pointer"
            >
              <option value="all">All Statuses</option>
              <option value="healthy">Healthy</option>
              <option value="pending">Pending</option>
              <option value="failed">Failed</option>
              <option value="disabled">Disabled</option>
            </select>
          </div>

          {/* Sort selection */}
          <div className="flex items-center gap-2">
            <SortAsc className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="text-xs bg-slate-950 border border-slate-800 text-slate-300 rounded-xl px-3 py-2.5 focus:outline-none focus:border-blue-500/60 cursor-pointer"
            >
              <option value="indexed_desc">Newest Indexed</option>
              <option value="indexed_asc">Oldest Indexed</option>
              <option value="title_asc">Title (A-Z)</option>
              <option value="words_desc">Word Count (High-Low)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Main content grid - Table or skeletons */}
      <div className="glass-panel border border-slate-800/50 rounded-2xl overflow-hidden shadow-xl">
        {loading ? (
          <TableSkeleton cols={7} rows={itemsPerPage} />
        ) : filteredWebsites.length === 0 ? (
          <EmptyState
            title={searchValue || statusFilter !== "all" ? "No matches found" : "No websites indexed yet"}
            description={
              searchValue || statusFilter !== "all"
                ? "Try adjusting your filters or search term."
                : "Add website URLs to expand the assistant knowledge base."
            }
            icon={<Globe className="w-12 h-12 text-slate-500 opacity-60" />}
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-800/70 text-xs font-semibold text-slate-400 uppercase bg-slate-900/20">
                  <th className="p-4 pl-6">Title & Domain</th>
                  <th className="p-4">URL</th>
                  <th className="p-4 text-center">Auto Sync</th>
                  <th className="p-4 text-center">Sync Health</th>
                  <th className="p-4 text-right">Chunks</th>
                  <th className="p-4 text-right">Last Checked</th>
                  <th className="p-4 text-right">Last Changed</th>
                  <th className="p-4 pr-6 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/40 text-sm">
                {currentItems.map((site, index) => (
                  <tr
                    key={site.id || index}
                    className="hover:bg-slate-900/20 transition-colors group"
                  >
                    <td className="p-4 pl-6">
                      <div className="flex flex-col">
                        <span className="font-semibold text-slate-200 group-hover:text-blue-400 transition-colors">
                          {site.title || "Untitled Webpage"}
                        </span>
                        <span className="text-xs text-slate-500 font-mono mt-0.5">
                          {site.domain}
                        </span>
                      </div>
                    </td>
                    <td className="p-4 max-w-[180px] truncate">
                      <a
                        href={site.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-500/80 hover:text-blue-400 inline-flex items-center gap-1 hover:underline"
                      >
                        {site.url}
                        <ExternalLink className="w-3 h-3 shrink-0" />
                      </a>
                    </td>
                    <td className="p-4 text-center">
                      <div className="flex items-center justify-center">
                        <input
                          type="checkbox"
                          checked={site.sync_enabled !== false}
                          onChange={() => handleToggleSync(site.id || site._id, site.sync_enabled !== false)}
                          className="w-4 h-4 text-blue-600 bg-slate-950 border-slate-800 rounded focus:ring-blue-500 cursor-pointer"
                        />
                      </div>
                    </td>
                    <td className="p-4 text-center">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-semibold tracking-wide border uppercase ${
                        site.sync_enabled === false
                          ? "bg-slate-500/10 text-slate-400 border-slate-500/20"
                          : site.sync_status === "Healthy"
                          ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                          : site.sync_status === "Pending"
                          ? "bg-amber-500/10 text-amber-400 border-amber-500/20"
                          : "bg-rose-500/10 text-rose-400 border-rose-500/20"
                      }`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${
                          site.sync_enabled === false
                            ? "bg-slate-500"
                            : site.sync_status === "Healthy"
                            ? "bg-emerald-400"
                            : site.sync_status === "Pending"
                            ? "bg-amber-400 animate-pulse"
                            : "bg-rose-400"
                        }`} />
                        {site.sync_enabled === false
                          ? "Disabled"
                          : site.sync_status || "Healthy"}
                      </span>
                    </td>
                    <td className="p-4 text-right font-mono text-slate-300">
                      {site.chunk_count?.toLocaleString() || 0}
                    </td>
                    <td className="p-4 text-right text-slate-450 text-xs font-mono">
                      {site.last_checked ? new Date(site.last_checked).toLocaleDateString() + " " + new Date(site.last_checked).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : "Never"}
                    </td>
                    <td className="p-4 text-right text-slate-455 text-xs font-mono">
                      {site.last_changed ? new Date(site.last_changed).toLocaleDateString() + " " + new Date(site.last_changed).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : "Never"}
                    </td>
                    <td className="p-4 pr-6 text-right">
                      <div className="flex items-center justify-end gap-1.5 opacity-80 group-hover:opacity-100 transition-opacity">
                        <button
                          disabled={syncingSiteId !== null}
                          onClick={() => handleManualSync(site.id || site._id, site.url)}
                          title="Sync update check now"
                          className="p-2 hover:bg-slate-800 rounded-lg text-slate-400 hover:text-indigo-400 transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          <RefreshCw className={`w-4 h-4 ${syncingSiteId === (site.id || site._id) ? "animate-spin" : ""}`} />
                        </button>
                        <button
                          onClick={() => {
                            setSelectedSite(site);
                            setViewDialogOpen(true);
                          }}
                          title="View metadata details"
                          className="p-2 hover:bg-slate-800 rounded-lg text-slate-400 hover:text-slate-100 transition-colors cursor-pointer"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => {
                            setSiteToReindex(site);
                            setReindexDialogOpen(true);
                          }}
                          title="Force full Re-index"
                          className="p-2 hover:bg-slate-800 rounded-lg text-slate-400 hover:text-slate-100 transition-colors cursor-pointer"
                        >
                          <RefreshCw className="w-4 h-4 text-blue-500" />
                        </button>
                        <button
                          onClick={() => {
                            console.log("[DEV DEBUG] Delete Trace: Website selected:", site.title);
                            console.log("[DEV DEBUG] Delete Trace: Website object:", JSON.stringify(site));
                            console.log("[DEV DEBUG] Delete Trace: Website ID:", site.id || site._id);
                            setSiteToDelete(site);
                            setDeleteDialogOpen(true);
                          }}
                          title="Delete index memory"
                          className="p-2 hover:bg-slate-800/80 rounded-lg text-slate-400 hover:text-rose-400 transition-colors cursor-pointer"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination footer */}
        {!loading && totalPages > 1 && (
          <div className="flex items-center justify-between px-6 py-4 border-t border-slate-800/40 select-none">
            <span className="text-xs text-slate-400">
              Showing {indexOfFirstItem + 1} to {Math.min(indexOfLastItem, filteredWebsites.length)} of{" "}
              {filteredWebsites.length} indexed websites
            </span>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="p-2 bg-slate-900 border border-slate-800 hover:bg-slate-800 rounded-lg text-slate-400 hover:text-slate-200 transition-colors disabled:opacity-40 disabled:hover:bg-slate-900 cursor-pointer disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <button
                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="p-2 bg-slate-900 border border-slate-800 hover:bg-slate-800 rounded-lg text-slate-400 hover:text-slate-200 transition-colors disabled:opacity-40 disabled:hover:bg-slate-900 cursor-pointer disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Add Website Dialog Modal */}
      <AnimatePresence>
        {addDialogOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => !submittingUrl && setAddDialogOpen(false)}
              className="fixed inset-0 bg-slate-950/60 backdrop-blur-md"
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 15 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 15 }}
              className="relative w-full max-w-lg glass-panel rounded-2xl overflow-hidden shadow-2xl p-6 border border-slate-700/20 z-10"
            >
              <div className="flex items-start justify-between mb-4 border-b border-slate-800/40 pb-3">
                <h3 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
                  <Globe className="w-5 h-5 text-blue-500" />
                  Index Website Page
                </h3>
                <button
                  onClick={() => setAddDialogOpen(false)}
                  disabled={submittingUrl}
                  className="p-1 hover:bg-slate-800 rounded-lg text-slate-400 hover:text-slate-200 transition-colors cursor-pointer"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <form onSubmit={handleAddWebsite} className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                    Website URL
                  </label>
                  <input
                    type="text"
                    value={urlInput}
                    onChange={(e) => setUrlInput(e.target.value)}
                    placeholder="https://example.com/page"
                    disabled={submittingUrl}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-slate-100 text-sm placeholder-slate-600 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                  />
                  <p className="text-xs text-slate-500 mt-2">
                    Enter the full URL, starting with http:// or https://. Single page will be crawled (depth = 0).
                  </p>
                </div>

                <div className="flex justify-end gap-3 pt-3 border-t border-slate-800/40 mt-6">
                  <button
                    type="button"
                    onClick={() => setAddDialogOpen(false)}
                    disabled={submittingUrl}
                    className="px-4 py-2 text-sm font-semibold text-slate-400 hover:bg-slate-800 rounded-xl border border-slate-800 transition-colors cursor-pointer"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={submittingUrl}
                    className="flex items-center gap-2 px-5 py-2 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-500 rounded-xl transition-all cursor-pointer shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {submittingUrl ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        <span>Crawling & Indexing...</span>
                      </>
                    ) : (
                      <span>Start Indexing</span>
                    )}
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Website Details View Dialog Modal */}
      <AnimatePresence>
        {viewDialogOpen && selectedSite && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setViewDialogOpen(false)}
              className="fixed inset-0 bg-slate-950/60 backdrop-blur-md"
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 15 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 15 }}
              className="relative w-full max-w-2xl glass-panel rounded-2xl overflow-hidden shadow-2xl p-6 border border-slate-700/20 z-10 flex flex-col max-h-[85vh]"
            >
              <div className="flex items-start justify-between border-b border-slate-800/40 pb-3 shrink-0">
                <h3 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
                  <Globe className="w-5 h-5 text-blue-500" />
                  Website Ingestion Details
                </h3>
                <button
                  onClick={() => setViewDialogOpen(false)}
                  className="p-1 hover:bg-slate-800 rounded-lg text-slate-400 hover:text-slate-200 transition-colors cursor-pointer"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="overflow-y-auto custom-scrollbar my-4 space-y-5 pr-2">
                {/* Meta details */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 bg-slate-900/30 p-4 rounded-xl border border-slate-800/40">
                  <div>
                    <span className="text-xs font-semibold text-slate-500 uppercase block">Title</span>
                    <span className="text-sm font-semibold text-slate-200">{selectedSite.title}</span>
                  </div>
                  <div>
                    <span className="text-xs font-semibold text-slate-500 uppercase block">Domain</span>
                    <span className="text-sm text-slate-300 font-mono">{selectedSite.domain}</span>
                  </div>
                  <div className="sm:col-span-2">
                    <span className="text-xs font-semibold text-slate-500 uppercase block">Full URL</span>
                    <a
                      href={selectedSite.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-blue-400 break-all inline-flex items-center gap-1 hover:underline font-mono mt-0.5"
                    >
                      {selectedSite.url}
                      <ExternalLink className="w-3 h-3 shrink-0" />
                    </a>
                  </div>
                  <div>
                    <span className="text-xs font-semibold text-slate-500 uppercase block">Word Count</span>
                    <span className="text-sm text-slate-200 font-mono">{selectedSite.word_count?.toLocaleString()}</span>
                  </div>
                  <div>
                    <span className="text-xs font-semibold text-slate-500 uppercase block">Vector Chunks</span>
                    <span className="text-sm text-slate-200 font-mono">{selectedSite.chunk_count?.toLocaleString()}</span>
                  </div>
                  <div>
                    <span className="text-xs font-semibold text-slate-500 uppercase block">Language</span>
                    <span className="text-sm text-slate-200 uppercase font-mono">{selectedSite.language || "en"}</span>
                  </div>
                  <div>
                    <span className="text-xs font-semibold text-slate-500 uppercase block">Crawl Timestamp</span>
                    <span className="text-sm text-slate-200">
                      {new Date(selectedSite.last_crawled || selectedSite.indexed_at).toLocaleString()}
                    </span>
                  </div>
                  <div className="sm:col-span-2 space-y-3">
                    <div>
                      <span className="text-xs font-semibold text-slate-500 uppercase block">Raw Content SHA-256 Hash</span>
                      <span className="text-[10px] text-slate-450 font-mono break-all bg-slate-950 p-2 rounded-lg border border-slate-900 block mt-1">
                        {selectedSite.content_hash}
                      </span>
                    </div>
                    <div>
                      <span className="text-xs font-semibold text-slate-500 uppercase block">Normalized Content SHA-256 Hash (ignores date/visitor counters)</span>
                      <span className="text-[10px] text-indigo-400 font-mono break-all bg-slate-950 p-2 rounded-lg border border-slate-900 block mt-1">
                        {selectedSite.normalized_content_hash || "Not computed yet (will run on next sync)"}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Description info */}
                <div>
                  <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5">Description</h4>
                  <p className="text-sm text-slate-300 leading-relaxed bg-slate-900/10 p-3 rounded-lg border border-slate-900">
                    {selectedSite.description || "No meta description extracted."}
                  </p>
                </div>
              </div>

              <div className="flex justify-end pt-3 border-t border-slate-800/40 shrink-0">
                <button
                  type="button"
                  onClick={() => setViewDialogOpen(false)}
                  className="px-5 py-2 text-sm font-semibold text-white bg-slate-800 hover:bg-slate-700 border border-slate-700/30 rounded-xl transition-colors cursor-pointer"
                >
                  Close
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Reindex confirmation loader / blocker */}
      <AnimatePresence>
        {reindexingState === "loading" && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div className="fixed inset-0 bg-slate-950/70 backdrop-blur-md" />
            <div className="relative glass-panel rounded-2xl p-8 border border-slate-700/20 max-w-sm w-full text-center space-y-4 shadow-2xl">
              <RefreshCw className="w-10 h-10 text-blue-500 animate-spin mx-auto" />
              <h3 className="text-lg font-semibold text-slate-100">Reindexing Web Content</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Downloading latest page content, wiping previous vectors, and building a fresh semantic vector index. Please wait...
              </p>
            </div>
          </div>
        )}
      </AnimatePresence>

      {/* Delete Confirmation Dialog */}
      <AnimatePresence>
        {deleteDialogOpen && siteToDelete && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            {/* Backdrop overlay */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => {
                setSiteToDelete(null);
                setDeleteDialogOpen(false);
              }}
              className="fixed inset-0 bg-slate-950/60 backdrop-blur-md"
            />

            {/* Modal body */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              transition={{ type: "spring", duration: 0.3 }}
              className="relative w-full max-w-md glass-panel rounded-2xl overflow-hidden shadow-2xl p-6 z-10 border border-slate-700/30"
            >
              {(() => {
                console.log("[DEV DEBUG] Delete Trace: Modal receives siteToDelete ID:", siteToDelete.id || siteToDelete._id);
                return null;
              })()}
              {/* Header */}
              <div className="flex items-start justify-between gap-4 mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-rose-500/10 rounded-lg border border-rose-500/20">
                    <Trash2 className="w-5 h-5 text-rose-500" />
                  </div>
                  <h3 className="text-lg font-semibold text-slate-100">Delete Website Ingestion</h3>
                </div>
                <button
                  onClick={() => {
                    setSiteToDelete(null);
                    setDeleteDialogOpen(false);
                  }}
                  className="p-1.5 hover:bg-slate-800 rounded-lg text-slate-400 hover:text-slate-200 transition-colors cursor-pointer"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Message */}
              <div className="space-y-3 mb-6">
                <p className="text-sm text-slate-300 leading-relaxed">
                  How do you want to delete the indexed website memory for <strong className="text-slate-150 font-semibold">"{siteToDelete.title}"</strong>?
                </p>
                <div className="text-[11px] space-y-2 bg-slate-950/40 p-3.5 rounded-xl border border-slate-800/60 leading-relaxed">
                  <p className="text-slate-350">
                    <span className="font-bold text-indigo-400">Keep Content:</span> Deletes only the metadata and admin listing. The chatbot can <strong>still answer questions</strong> using this website's knowledge.
                  </p>
                  <p className="text-slate-355">
                    <span className="font-bold text-rose-400">Purge Content:</span> Deletes everything, including ChromaDB vectors. The website content will <strong>no longer be searchable</strong>.
                  </p>
                </div>
              </div>

              {/* Action buttons */}
              <div className="flex flex-wrap justify-end gap-2.5">
                <button
                  onClick={() => {
                    setSiteToDelete(null);
                    setDeleteDialogOpen(false);
                  }}
                  className="px-4 py-2 text-sm font-medium text-slate-400 hover:bg-slate-800 rounded-lg border border-slate-800 transition-colors cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleDelete(false)}
                  className="px-4 py-2 text-sm font-medium text-slate-200 bg-slate-800 hover:bg-slate-700 border border-slate-700/50 rounded-lg transition-colors cursor-pointer"
                >
                  Keep Content
                </button>
                <button
                  onClick={() => handleDelete(true)}
                  className="px-4 py-2 text-sm font-medium text-white bg-rose-600 hover:bg-rose-500 rounded-lg shadow-lg hover:shadow-rose-500/20 transition-all cursor-pointer"
                >
                  Purge Content
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Reindex Confirmation Dialog */}
      <ConfirmationDialog
        isOpen={reindexDialogOpen}
        title="Reindex Website Content"
        message={`Do you want to re-index the content at "${siteToReindex?.title || ""}"? This will fetch the latest HTML contents, purge the current Chroma DB vector chunks, and re-insert the updated embeddings.`}
        confirmLabel="Start Re-indexing"
        cancelLabel="Cancel"
        onConfirm={handleReindexConfirm}
        onCancel={() => {
          setSiteToReindex(null);
          setReindexDialogOpen(false);
        }}
      />
    </div>
  );
};
