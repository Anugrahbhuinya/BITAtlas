import React, { useState, useEffect } from "react";
import { 
  Navigation, RefreshCw, X, AlertTriangle, 
  Compass, Accessibility, Flame, Watch, ArrowUpDown, ChevronDown, ChevronUp, MapPin, Play
} from "lucide-react";
import type { GraphNode, Route } from "../types";
import { navigationApi } from "../services/navigationApi";
import { useNavigationAIStore } from "../store/useNavigationAIStore";

interface RoutePanelProps {
  allNodes: GraphNode[];
  selectedStart?: GraphNode | null;
  selectedDestination: GraphNode | null;
  onClear: () => void;
  onRouteCalculated: (route: Route | null, routePathPoints: [number, number][]) => void;
  onStartNavigation?: (startNode: GraphNode, destNode: GraphNode, route: Route, pathPoints: [number, number][]) => void;
}

export const RoutePanel: React.FC<RoutePanelProps> = ({
  allNodes,
  selectedStart,
  selectedDestination,
  onClear,
  onRouteCalculated,
  onStartNavigation
}) => {
  const [startId, setStartId] = useState(selectedStart?.id || "");
  const [destId, setDestId] = useState(selectedDestination?.id || "");
  const [routeType, setRouteType] = useState<"shortest" | "fastest" | "accessible">("shortest");
  
  const [route, setRoute] = useState<Route | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQueryStart, setSearchQueryStart] = useState("");
  const [searchQueryDest, setSearchQueryDest] = useState("");
  
  const [showStartDropdown, setShowStartDropdown] = useState(false);
  const [showDestDropdown, setShowDestDropdown] = useState(false);

  // Collapsible sections
  const [sectionsCollapsed, setSectionsCollapsed] = useState<Record<string, boolean>>({
    summary: false,
    options: false,
    directions: false,
    accessibility: false
  });

  const toggleSection = (sec: string) => {
    setSectionsCollapsed(prev => ({ ...prev, [sec]: !prev[sec] }));
  };

  // Sync start if updated externally
  useEffect(() => {
    if (selectedStart) {
      setStartId(selectedStart.id);
      setSearchQueryStart(selectedStart.name);
    }
  }, [selectedStart]);

  // Sync destination if updated externally
  useEffect(() => {
    if (selectedDestination) {
      setDestId(selectedDestination.id);
      setSearchQueryDest(selectedDestination.name);
    }
  }, [selectedDestination]);

  // Sync location IDs to shared NavigationAI store for chat context injection
  useEffect(() => {
    useNavigationAIStore.getState().setCurrentLocation(startId || null);
  }, [startId]);
  useEffect(() => {
    useNavigationAIStore.getState().setCurrentDestination(destId || null);
  }, [destId]);
  useEffect(() => {
    useNavigationAIStore.getState().setAccessibilityMode(routeType === "accessible");
  }, [routeType]);

  // Fetch route when start, destination, or strategy changes
  useEffect(() => {
    if (!startId || !destId) {
      setRoute(null);
      onRouteCalculated(null, []);
      return;
    }

    const calculatePath = async () => {
      setLoading(true);
      setError(null);
      try {
        const routeRes = await navigationApi.calculateRoute(startId, destId, routeType);
        setRoute(routeRes);
        
        // Extract coordinate points for Leaflet polyline overlay
        // Use path geometry coordinates if present, fallback to node coordinates
        let pathPoints: [number, number][] = [];
        if (routeRes.geometry && routeRes.geometry.length > 0) {
          pathPoints = routeRes.geometry.map((pt: number[]) => [pt[0], pt[1]]);
        } else {
          pathPoints = routeRes.ordered_nodes.map(
            (n) => [n.coordinates.latitude, n.coordinates.longitude]
          );
        }
        onRouteCalculated(routeRes, pathPoints);
      } catch (err: any) {
        setError(err.response?.data?.detail || "Unreachable path between selected points.");
        setRoute(null);
        onRouteCalculated(null, []);
      } finally {
        setLoading(false);
      }
    };

    calculatePath();
  }, [startId, destId, routeType]);

  const filteredStartNodes = allNodes
    .filter(n => n.name.toLowerCase().includes(searchQueryStart.toLowerCase()))
    .slice(0, 5);

  const filteredDestNodes = allNodes
    .filter(n => n.name.toLowerCase().includes(searchQueryDest.toLowerCase()))
    .slice(0, 5);

  const handleSwapLocations = () => {
    const tempId = startId;
    const tempQuery = searchQueryStart;
    
    setStartId(destId);
    setSearchQueryStart(searchQueryDest);
    
    setDestId(tempId);
    setSearchQueryDest(tempQuery);
  };

  // Format walking time
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.round(seconds % 60);
    if (mins > 0) return `${mins} min${mins > 1 ? "s" : ""} ${secs > 0 ? `${secs} sec` : ""}`;
    return `${secs} seconds`;
  };

  // Compute ETA clock arrival
  const getEstimatedArrival = (seconds: number) => {
    const now = new Date();
    now.setSeconds(now.getSeconds() + seconds);
    return now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  // Count number of turns
  const getTurnsCount = (instructions: string[]) => {
    return instructions.filter(step => 
      step.toLowerCase().includes("turn left") || 
      step.toLowerCase().includes("turn right") || 
      step.toLowerCase().includes("make a u-turn")
    ).length;
  };

  // Compute route confidence
  const getRouteConfidence = (r: Route) => {
    let score = 99;
    if (!r.accessibility_information) score -= 10;
    
    // Check if it traverses unpaved roads in pathway types
    const hasDirt = r.ordered_path.some(edge => 
      (edge.metadata?.surface || "").toLowerCase() === "dirt" ||
      (edge.metadata?.surface || "").toLowerCase() === "grass"
    );
    if (hasDirt) score -= 5;

    return `${score}% (${score >= 90 ? "High" : "Moderate"})`;
  };

  return (
    <div className="bg-surface/95 border border-outline-variant/65 rounded-3xl p-5 shadow-2xl flex flex-col gap-4 max-h-[85vh] overflow-y-auto w-full max-w-sm backdrop-blur-md relative select-none z-[1000]">
      {/* Header */}
      <div className="flex justify-between items-center border-b border-outline-variant/35 pb-2.5">
        <div className="flex items-center gap-2 text-primary">
          <Navigation className="w-5 h-5 animate-pulse" />
          <h3 className="text-sm font-black tracking-tight">Smart Routing Engine</h3>
        </div>
        <button
          onClick={onClear}
          className="p-1 rounded-full hover:bg-surface-variant text-on-surface/40 hover:text-on-surface transition"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Selectors and Swap button */}
      <div className="flex gap-2 items-center text-left">
        <div className="flex-1 space-y-3 relative">
          {/* Start Location Input */}
          <div className="relative">
            <label className="text-[10px] font-bold text-on-surface/50 uppercase tracking-wider block mb-1">Start Location</label>
            <input
              type="text"
              value={searchQueryStart}
              onChange={(e) => {
                setSearchQueryStart(e.target.value);
                setShowStartDropdown(true);
              }}
              onFocus={() => setShowStartDropdown(true)}
              disabled={loading}
              placeholder="Search start location..."
              className="w-full p-2 bg-surface-variant/40 hover:bg-surface-variant/75 border border-outline-variant/50 rounded-xl text-xs focus:outline-none focus:border-primary transition duration-150 disabled:opacity-50"
            />
            {showStartDropdown && searchQueryStart && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-surface border border-outline-variant rounded-xl shadow-xl z-[1050] overflow-hidden">
                {filteredStartNodes.map((n) => (
                  <button
                    key={n.id}
                    onClick={() => {
                      setStartId(n.id);
                      setSearchQueryStart(n.name);
                      setShowStartDropdown(false);
                    }}
                    className="w-full text-left p-2.5 hover:bg-primary/10 text-xs font-semibold text-on-surface/85 transition"
                  >
                    {n.name} <span className="text-[9px] opacity-50 font-medium">({n.type})</span>
                  </button>
                ))}
                {filteredStartNodes.length === 0 && (
                  <div className="p-2 text-xs text-on-surface/40">No matching locations</div>
                )}
              </div>
            )}
          </div>

          {/* Destination Location Input */}
          <div className="relative">
            <label className="text-[10px] font-bold text-on-surface/50 uppercase tracking-wider block mb-1">Destination</label>
            <input
              type="text"
              value={searchQueryDest}
              onChange={(e) => {
                setSearchQueryDest(e.target.value);
                setShowDestDropdown(true);
              }}
              onFocus={() => setShowDestDropdown(true)}
              disabled={loading}
              placeholder="Search destination..."
              className="w-full p-2 bg-surface-variant/40 hover:bg-surface-variant/75 border border-outline-variant/50 rounded-xl text-xs focus:outline-none focus:border-primary transition duration-150 disabled:opacity-50"
            />
            {showDestDropdown && searchQueryDest && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-surface border border-outline-variant rounded-xl shadow-xl z-[1050] overflow-hidden">
                {filteredDestNodes.map((n) => (
                  <button
                    key={n.id}
                    onClick={() => {
                      setDestId(n.id);
                      setSearchQueryDest(n.name);
                      setShowDestDropdown(false);
                    }}
                    className="w-full text-left p-2.5 hover:bg-primary/10 text-xs font-semibold text-on-surface/85 transition"
                  >
                    {n.name} <span className="text-[9px] opacity-50 font-medium">({n.type})</span>
                  </button>
                ))}
                {filteredDestNodes.length === 0 && (
                  <div className="p-2 text-xs text-on-surface/40">No matching locations</div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Swap Button */}
        <button
          onClick={handleSwapLocations}
          disabled={loading || !startId || !destId}
          className="p-2.5 bg-surface-variant/35 hover:bg-surface-variant/75 border border-outline-variant/60 rounded-xl text-on-surface/65 hover:text-primary transition shrink-0 self-end mb-0.5 disabled:opacity-30"
          title="Swap Start & Destination"
        >
          <ArrowUpDown className="w-4.5 h-4.5" />
        </button>
      </div>

      {/* Collapsible Options / Strategy Toggles */}
      <div className="border border-outline-variant/35 rounded-2xl overflow-hidden bg-surface-variant/10 text-left">
        <button
          onClick={() => toggleSection("options")}
          className="w-full p-2.5 bg-surface-variant/20 flex justify-between items-center text-[10px] font-extrabold text-on-surface/60 uppercase tracking-wider hover:bg-surface-variant/30 transition"
        >
          <span>Route Strategy</span>
          {sectionsCollapsed.options ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronUp className="w-3.5 h-3.5" />}
        </button>
        
        {!sectionsCollapsed.options && (
          <div className="p-2 grid grid-cols-3 gap-1 border-t border-outline-variant/35">
            <button
              onClick={() => setRouteType("shortest")}
              disabled={loading}
              className={`py-1.5 text-[10px] font-extrabold rounded-lg flex items-center justify-center gap-1 transition ${
                routeType === "shortest" ? "bg-primary text-background shadow-md" : "text-on-surface/60 hover:text-on-surface hover:bg-surface/30"
              }`}
            >
              <Compass className="w-3.5 h-3.5" />
              Shortest
            </button>
            <button
              onClick={() => setRouteType("fastest")}
              disabled={loading}
              className={`py-1.5 text-[10px] font-extrabold rounded-lg flex items-center justify-center gap-1 transition ${
                routeType === "fastest" ? "bg-primary text-background shadow-md" : "text-on-surface/60 hover:text-on-surface hover:bg-surface/30"
              }`}
            >
              <Flame className="w-3.5 h-3.5" />
              Fastest
            </button>
            <button
              onClick={() => setRouteType("accessible")}
              disabled={loading}
              className={`py-1.5 text-[10px] font-extrabold rounded-lg flex items-center justify-center gap-1 transition ${
                routeType === "accessible" ? "bg-primary text-background shadow-md" : "text-on-surface/60 hover:text-on-surface hover:bg-surface/30"
              }`}
            >
              <Accessibility className="w-3.5 h-3.5" />
              Accessible
            </button>
          </div>
        )}
      </div>

      {/* Loading state skeleton list */}
      {loading && (
        <div className="space-y-4 animate-pulse text-left py-4">
          <div className="h-5 bg-surface-variant/60 rounded-lg w-1/3"></div>
          <div className="grid grid-cols-2 gap-2">
            <div className="h-16 bg-surface-variant/40 rounded-2xl"></div>
            <div className="h-16 bg-surface-variant/40 rounded-2xl"></div>
          </div>
          <div className="h-8 bg-surface-variant/30 rounded-xl"></div>
          <div className="space-y-2.5">
            <div className="h-4 bg-surface-variant/20 rounded w-5/6"></div>
            <div className="h-4 bg-surface-variant/20 rounded w-4/6"></div>
            <div className="h-4 bg-surface-variant/20 rounded w-full"></div>
          </div>
        </div>
      )}

      {/* Error / suggestions when no accessible path exists */}
      {error && !loading && (
        <div className="p-4 bg-error/5 border border-error/25 rounded-2xl flex flex-col gap-3 text-left">
          <div className="flex items-start gap-2.5">
            <AlertTriangle className="w-4 h-4 text-error flex-shrink-0 mt-0.5" />
            <div className="space-y-0.5">
              <p className="text-xs font-bold text-error">No Walkable Route Found</p>
              <p className="text-[10px] text-on-surface/65 font-semibold leading-relaxed">{error}</p>
            </div>
          </div>
          <div className="border-t border-outline-variant/30 pt-2.5 space-y-1.5">
            <p className="text-[9px] font-extrabold uppercase text-on-surface/45 tracking-wider">Suggestions</p>
            <ul className="list-disc list-inside text-[10px] text-on-surface/70 space-y-1 leading-normal font-semibold">
              {routeType === "accessible" ? (
                <li>Try switching from <strong>Accessible</strong> to <strong>Shortest</strong> mode as some connection links contain stairs.</li>
              ) : (
                <li>Verify if locations are on opposite sides of unlinked campus blocks.</li>
              )}
              <li>Select building entrance points or local landmarks directly.</li>
            </ul>
          </div>
        </div>
      )}

      {/* Route results */}
      {route && !loading && !error && (
        <div className="space-y-4 text-left">
          {/* Collapsible Route Summary */}
          <div className="border border-outline-variant/35 rounded-2xl overflow-hidden bg-surface-variant/10">
            <button
              onClick={() => toggleSection("summary")}
              className="w-full p-2.5 bg-surface-variant/20 flex justify-between items-center text-[10px] font-extrabold text-on-surface/60 uppercase tracking-wider hover:bg-surface-variant/30 transition"
            >
              <span>Route Metrics</span>
              {sectionsCollapsed.summary ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronUp className="w-3.5 h-3.5" />}
            </button>
            
            {!sectionsCollapsed.summary && (
              <div className="p-3.5 space-y-3.5 border-t border-outline-variant/35">
                {/* Statistics Grid */}
                <div className="grid grid-cols-2 gap-2">
                  <div className="bg-surface-variant/20 p-2.5 rounded-xl border border-outline-variant/35 flex items-center gap-2">
                    <Watch className="w-4 h-4 text-primary flex-shrink-0" />
                    <div>
                      <p className="text-[8px] text-on-surface/50 font-bold uppercase">Duration</p>
                      <p className="text-xs font-black text-on-surface">{formatTime(route.estimated_walking_time)}</p>
                    </div>
                  </div>
                  <div className="bg-surface-variant/20 p-2.5 rounded-xl border border-outline-variant/35 flex items-center gap-2">
                    <Compass className="w-4 h-4 text-primary flex-shrink-0" />
                    <div>
                      <p className="text-[8px] text-on-surface/50 font-bold uppercase">Distance</p>
                      <p className="text-xs font-black text-on-surface">
                        {route.total_distance >= 1000 
                          ? `${(route.total_distance / 1000).toFixed(2)} km` 
                          : `${route.total_distance.toFixed(0)} m`}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Additional metrics info */}
                <div className="grid grid-cols-3 gap-1.5 text-center">
                  <div className="bg-surface/30 p-2 rounded-lg border border-outline-variant/30">
                    <span className="text-[8px] block text-on-surface/40 uppercase font-black">Arrival</span>
                    <span className="text-[10px] font-bold text-on-surface mt-0.5 block">{getEstimatedArrival(route.estimated_walking_time)}</span>
                  </div>
                  <div className="bg-surface/30 p-2 rounded-lg border border-outline-variant/30">
                    <span className="text-[8px] block text-on-surface/40 uppercase font-black">Turns</span>
                    <span className="text-[10px] font-bold text-on-surface mt-0.5 block">{getTurnsCount(route.navigation_instructions)}</span>
                  </div>
                  <div className="bg-surface/30 p-2 rounded-lg border border-outline-variant/30">
                    <span className="text-[8px] block text-on-surface/40 uppercase font-black">Confidence</span>
                    <span className="text-[10px] font-bold text-on-surface mt-0.5 block truncate" title={getRouteConfidence(route)}>
                      {getRouteConfidence(route).split(" ")[0]}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Accessibility Info banner */}
          <div className="border border-outline-variant/35 rounded-2xl overflow-hidden bg-surface-variant/10">
            <button
              onClick={() => toggleSection("accessibility")}
              className="w-full p-2.5 bg-surface-variant/20 flex justify-between items-center text-[10px] font-extrabold text-on-surface/60 uppercase tracking-wider hover:bg-surface-variant/30 transition"
            >
              <span>Accessibility Panel</span>
              {sectionsCollapsed.accessibility ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronUp className="w-3.5 h-3.5" />}
            </button>
            
            {!sectionsCollapsed.accessibility && (
              <div className={`p-3 border-t border-outline-variant/35 flex items-start gap-2.5 text-[10px] font-bold leading-normal ${
                route.accessibility_information
                  ? "bg-emerald-500/5 text-emerald-500"
                  : "bg-amber-500/5 text-amber-500"
              }`}>
                <Accessibility className="w-4 h-4 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-extrabold uppercase text-[9px] tracking-wider mb-0.5">
                    {route.accessibility_information ? "Accessible Path" : "Limited Accessibility"}
                  </p>
                  <p className="font-medium text-on-surface/75">
                    {route.accessibility_information 
                      ? "This route avoids stairs, unpaved surfaces, and steep steps. Suitable for wheelchairs." 
                      : "Caution: This route contains staircases, steep slopes, or unpaved dirt walkways."}
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Instructions List */}
          <div className="border border-outline-variant/35 rounded-2xl overflow-hidden bg-surface-variant/10">
            <button
              onClick={() => toggleSection("directions")}
              className="w-full p-2.5 bg-surface-variant/20 flex justify-between items-center text-[10px] font-extrabold text-on-surface/60 uppercase tracking-wider hover:bg-surface-variant/30 transition"
            >
              <span>Navigation Directions</span>
              {sectionsCollapsed.directions ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronUp className="w-3.5 h-3.5" />}
            </button>
            
            {!sectionsCollapsed.directions && (
              <div className="p-3.5 border-t border-outline-variant/35 max-h-48 overflow-y-auto space-y-2 pr-1 custom-scrollbar">
                {route.navigation_instructions.map((step, idx) => (
                  <div key={idx} className="flex gap-2.5 items-start text-xs text-on-surface/85 leading-relaxed font-semibold">
                    <div className="w-4.5 h-4.5 rounded-full bg-primary/10 text-primary flex items-center justify-center text-[9px] flex-shrink-0 font-black mt-0.5">
                      {idx + 1}
                    </div>
                    <span className="flex-1">{step}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Start Navigation Button */}
      {route && !loading && !error && onStartNavigation && (
        <div className="border-t border-outline-variant/30 pt-3">
          <button
            onClick={() => {
              const startNode = allNodes.find(n => n.id === startId);
              const destNode = allNodes.find(n => n.id === destId);
              if (startNode && destNode && route) {
                let pathPoints: [number, number][] = [];
                if (route.geometry && route.geometry.length > 0) {
                  pathPoints = route.geometry.map((pt: number[]) => [pt[0], pt[1]]);
                } else {
                  pathPoints = route.ordered_nodes.map(
                    (n) => [n.coordinates.latitude, n.coordinates.longitude]
                  );
                }
                onStartNavigation(startNode, destNode, route, pathPoints);
              }
            }}
            className="w-full py-3 bg-primary hover:bg-primary/90 text-background text-xs font-black uppercase tracking-wider rounded-xl transition duration-150 flex items-center justify-center gap-2 active:scale-[0.98] cursor-pointer shadow-lg"
          >
            <Play size={14} className="fill-current" />
            <span>Start Navigation</span>
          </button>
        </div>
      )}
    </div>
  );
};
export default RoutePanel;
